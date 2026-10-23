/*
 * Bearers combat engine (sim/SPEC.md sections 4–6). Headless: no DOM, no window, no modules.
 * Runs in Node 18 (`require("./engine.js")`) and in a page from file:// (`globalThis.BearersEngine`).
 *
 * API
 *   Eng.totals(build, cards)       → { STR … SPD, size, errors }   tally card (P 12.3)
 *   Eng.validate(build, cards)     → [string]   Slot limits, types, Requirements, copies ("Warning: …" lines don't block)
 *   Eng.fromFoe(foe, cards)        → Build      (Shield first in Hand, other weapons in carries order, rest carried)
 *   Eng.createFight(scenario, cards) → Fight
 *   Eng.replay(exported, cards)    → Fight      re-runs every exported command with its recorded answers
 *   Eng.registerHook(name, h)      hook plug-in point (below)
 *   Eng.summaryCsv(summary)        → CSV text, one row per creature
 *   Eng.geometry                   distance / sight / engagement helpers (read-only use by the UI)
 *
 *   fight.state                    plain JSON (SPEC 4.1); never write it
 *   fight.legal(actorId)           → [template]: { type, actor, label, ...fields }. Fields still missing
 *                                    (target, targets, point, path, text) are what the UI collects;
 *                                    `candidates` lists target ids that pass the checks right now.
 *   fight.preview(cmd)             → { ok, error, info }  info keys: toHit, defense, vs, dice, adv, dis, why,
 *                                    outnumbered { us, them, n, list }, cover, distance, damage, cost, left,
 *                                    provokes, targets, use
 *   fight.do(cmd)                  → { ok, error, events, pending }
 *   fight.pending                  null | Prompt { id, kind: "reaction"|"choice"|"roll", text, trigger, options, sides }
 *   fight.undo()                   → false when there is nothing to undo; cancels a pending prompt first
 *   fight.setManualDice(bool)      every die becomes a "roll" prompt
 *   fight.events, fight.summary(), fight.summaryRows(), fight.export()
 *
 * Commands: SPEC 4.2, plus these extras: act "revert" (leave a Form, free) and act "prone" (drop prone, free);
 *   move `safe: true` spends movement granted by a `move: "safe"` effect (no opportunity attacks);
 *   act "endCond" + `cond: "<condition id>"` (an action that ends a condition with `endAction`, Pierce: pull the pilum free);
 *   interact `drop: "<card id>"` (free); power `pool: "extra"` pays from the extra spell point / Resolve pool;
 *   power/shove `mode: "push"|"prone"` for shove effects; adjust `temp`, `exhaustion`.
 *
 * Answers and re-runs (SPEC 4.2 recommended design)
 *   Every external input (a reaction choice, a manual die) is an *answer*, consumed in order by the running
 *   command. When resolution needs an answer that isn't there yet, it throws NeedInput: the engine restores the
 *   snapshot taken before the command, sets `pending`, and waits. `do({ type: "answer", choice, roll })` appends
 *   the answer and re-runs the whole command from the snapshot. The RNG lives in state.rng, so the re-run rolls
 *   the same dice and reaches the same question, now answered, and goes on. A command is committed (events,
 *   undo snapshot, command log with its answers) only when it finishes. Undo restores the snapshot before the
 *   last committed command. Export = scenario + [{ cmd, answers, manual }]; replay feeds them back in order.
 *   Rule checks run before the first question, so an answer never turns into a rule error.
 *
 * Hooks (SPEC 5): Eng.registerHook(name, { onUse, onTrigger, modifyAttack, modifyDamage, passive })
 *   onUse(ctx)        a power with `hook` is used (costs already paid). Without a hook: "<card>: not automated".
 *   onTrigger(ctx)    a trigger/reaction power with `hook` fires (ctx.trigger = { on, attacker, target, hit, crit, weapon }).
 *   modifyAttack(ctx) while an attack is built: ctx.attack = { bonus, adv, dis, why[], def, defs, weapon, melee,
 *                     ranged, opportunity }; ctx.role = "attacker" | "target". Pure: no rolls, no state changes
 *                     (it also runs for preview). Called for the attacker's passive hooks (a weapon's own only
 *                     when attacking with it) and the target's passive hooks.
 *   modifyDamage(ctx) before damage is rolled: ctx.damage = { parts: [{ dice, type }], flat, crit, type }; push
 *                     parts or change flat. Same callers as modifyAttack.
 *   passive(ctx)      once at `start`, for each passive hook power.
 *   plan(ctx)         optional, for a power with `hook`: pure, runs when the power is planned (preview, legal, use).
 *                     Returns an error text (refused) or { targets: [creature], info } (its own targets; info is
 *                     merged into the preview). ctx.cmd is the command.
 *   ctx = { fight, state, cards, actor, target, targets, point, power, entry, cmd, attack, damage, trigger,
 *           role, roll(dice) → total, d20(adv, dis) → { dice, kept }, emit(event), ask(prompt) → answer,
 *           dealDamage(t, n, type, opts), heal(t, n), addCond(t, name, opts), removeCond(t, name),
 *           addMod(t, mod), apply(effects, target), distance(a, b), engaged(a, b), creature(id), creatures(),
 *           weapon(id) → weapon spec of a held weapon, weaponReach(w), sees(a, b) → clear line, attackInfo(t, src) (pure),
 *           areaWeaponAttack(w, targets, { label, attackAction }) one weapon roll against each target, half on a miss }
 *   Creatures in ctx are live state objects; change them only through the helpers.
 */
(function (root, factory) {
  const api = factory();
  root.BearersEngine = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  // ---------- constants ----------
  const ABILS = ["STR", "DEX", "INT", "WIL"];
  const KEYS = ["STR", "DEX", "INT", "WIL", "STRd", "DEXd", "INTd", "WILd", "HP", "SPD"];
  const SIZE_N = { Tiny: 0, Small: 1, Medium: 2, Large: 3, Huge: 4, Gargantuan: 5 };
  const SPACE = { Tiny: 1, Small: 1, Medium: 1, Large: 2, Huge: 3, Gargantuan: 4 };
  const ASPECT_TYPES = ["Trait", "Technique", "Knack", "Divine", "Glamour", "Nature"];
  const SLOT_TYPES = { armor: ["Armor"], hand: ["Weapon", "Shield", "Instrument"], jewelry: ["Jewelry"],
    item: ["Spellbook", "Recipe", "Purse", "Consumable"], aspect: ASPECT_TYPES };
  const DEFAULT_SLOTS = { hand: 2, jewelry: 1, item: 2, aspect: 3 };
  const INCAP = ["Incapacitated", "Stunned", "Unconscious", "Petrified"];
  const SPEED0 = ["Grappled", "Restrained", "Stunned", "Unconscious", "Petrified"];
  const DUR = { "1 round": 1, "1 minute": 10, "10 minutes": 100, "1 hour": 600, "8 hours": 4800 };
  const HOOKS = {};

  // ---------- helpers ----------
  const clone = (o) => (o === undefined ? undefined : JSON.parse(JSON.stringify(o)));
  const signed = (n) => (n >= 0 ? "+" : "−") + Math.abs(n);
  const key = (x, y) => x + "," + y;
  const other = (side) => (side === "pc" ? "foe" : "pc");
  class RuleError extends Error {}
  function NeedInput(prompt) { this.prompt = prompt; }
  const fail = (msg) => { throw new RuleError(msg); };
  const num = (v) => (typeof v === "number" ? v : parseInt(String(v).replace("−", "-"), 10) || 0);

  // ---------- dice ----------
  function rngNext(rng) {
    let t = (rng.s = (rng.s + 0x6D2B79F5) | 0);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }
  function die(X, sides, why) {
    if (X.preview) fail("preview can't roll");
    if (X.manual) {
      const r = ask(X, { kind: "roll", sides, die: sides, text: `Roll 1d${sides}${why ? " (" + why + ")" : ""}` });
      return r;
    }
    return 1 + Math.floor(rngNext(X.st.rng) * sides);
  }
  // "2d8+WIL", "1d4 + 1", "-1d4", "1" → { dice: [{ n, sides, sign }], flat }
  function parseDice(expr, mods) {
    const out = { dice: [], flat: 0 };
    const s = String(expr == null ? "0" : expr).replace(/\s+/g, "").replace(/−/g, "-");
    for (const tok of s.match(/[+-]?[^+-]+/g) || []) {
      const sign = tok[0] === "-" ? -1 : 1, body = tok.replace(/^[+-]/, "");
      const m = body.match(/^(\d*)d(\d+)$/);
      if (m) out.dice.push({ n: m[1] ? +m[1] : 1, sides: +m[2], sign });
      else if (ABILS.includes(body)) out.flat += sign * ((mods && mods[body]) || 0);
      else out.flat += sign * (parseInt(body, 10) || 0);
    }
    return out;
  }
  function rollDice(X, expr, o) {
    o = o || {};
    const p = typeof expr === "string" || typeof expr === "number" ? parseDice(expr, o.mods) : expr;
    const rolls = [];
    let total = p.flat;
    p.dice.forEach((d, i) => {
      let n = d.n + (i === 0 && o.extra ? o.extra : 0);
      if (o.crit) n *= 2;
      for (let k = 0; k < n; k++) { const r = die(X, d.sides, o.why); rolls.push(d.sign * r); total += d.sign * r; }
    });
    return { total, rolls };
  }
  function rollD20(X, adv, dis, why) {
    const net = adv - dis, n = 1 + Math.abs(net), dice = [];
    for (let i = 0; i < n; i++) dice.push(die(X, 20, why));
    const kept = net > 0 ? Math.max(...dice) : net < 0 ? Math.min(...dice) : dice[0];
    return { dice, kept, adv, dis };
  }
  function ask(X, prompt) {
    if (X.preview) fail("preview can't ask");
    if (X.i < X.answers.length) {
      const a = X.answers[X.i++];
      return prompt.kind === "roll" ? a.roll : a.choice;
    }
    throw new NeedInput(prompt);
  }

  // ---------- cards and builds ----------
  function normBuild(b) {
    b = Object.assign({ core: null, body: null, armor: null, hands: [], carried: [], jewelry: [], items: [], aspects: [],
      slots: {}, bonus: {}, extraDice: 0, ownFx: [], powers: [], boss: false, senses: {}, alert: false, foe: null }, clone(b || {}));
    b.slots = Object.assign({}, DEFAULT_SLOTS, b.slots);
    b.items = b.items.map((it) => (typeof it === "string" ? { id: it, n: 1 } : it));
    return b;
  }
  const typeOf = (c) => c.type || (c.kw && c.kw[0]);
  const sizeOfCard = (c) => c.size || (c.kw || []).find((k) => SIZE_N[k] !== undefined) || "Medium";
  function equippedIds(b) {
    return [b.armor, ...(b.hands || []), ...(b.jewelry || []), ...(b.items || []).map((it) => (typeof it === "string" ? it : it.id)), ...(b.aspects || [])].filter(Boolean);
  }
  function blank() { const t = {}; KEYS.forEach((k) => (t[k] = 0)); return t; }
  function addStrip(t, s) { for (const k of KEYS) if (s && s[k] != null) t[k] += num(s[k]); }
  function bodyStrip(body) {
    const t = blank();
    ABILS.forEach((a) => { t[a] = body[a] || 0; t[a + "d"] = 10 + (body[a] || 0); });
    t.HP = body.HP || 0; t.SPD = body.SPD || 0;
    return t;
  }
  function coreStrip(build, cards) {
    if (build.core) { const c = cards.cards[build.core]; return c ? { strip: Object.assign(blank(), c.strip), size: sizeOfCard(c), card: c } : null; }
    if (build.body) return { strip: bodyStrip(build.body), size: build.body.size || "Medium" };
    return null;
  }
  // RULING R203: a Requirement counts the Core and every other equipped card's positive bonuses
  // (penalties and the card's own bonus don't count, P 3.1); an unmet card adds nothing to the totals.
  function meetsReq(card, core, list, bonus) {
    for (const [ab, need] of Object.entries(card.req || {})) {
      let v = core[ab] || 0;
      for (const o of list) if (o !== card && o.strip && num(o.strip[ab]) > 0) v += num(o.strip[ab]);
      if (bonus && num(bonus[ab]) > 0) v += num(bonus[ab]);
      if (v < need) return false;
    }
    return true;
  }
  function totals(build, cards) {
    build = normBuild(build);
    const errors = [];
    const base = coreStrip(build, cards);
    const t = base ? Object.assign({}, base.strip) : blank();
    if (!base) errors.push(build.core ? `Unknown Core ${build.core}` : "No Core or body");
    const list = [];
    for (const id of equippedIds(build)) {
      const c = cards.cards[id];
      if (!c) errors.push(`Unknown card ${id}`); else if (c.kind !== "core") list.push(c);
    }
    for (const c of list) {
      if (!meetsReq(c, base ? base.strip : t, list, build.bonus)) { errors.push(`${c.name}: Requirement not met (${Object.entries(c.req).map(([a, n]) => a + " +" + n).join(", ")})`); continue; }
      addStrip(t, c.strip);
    }
    // RULING R201: foe templates (build.foe set) don't get the empty Armor Slot's +10 Speed: foe cards print
    // their totals without it (Ogre: Speed 35), and fromFoe must match them.
    if (!build.armor && !build.foe) t.SPD += 10;
    addStrip(t, build.bonus);
    t.size = base ? base.size : "Medium";
    t.errors = errors;
    return t;
  }
  // Fresh tally card for a Form (P 10.7, 12.3): Form STR, DEX, HP, Speed, Size + Core INT and WIL + Aspects.
  function formTotals(build, cards, form) {
    const base = coreStrip(build, cards);
    const t = blank();
    addStrip(t, form.strip);
    if (base) ["INT", "WIL", "INTd", "WILd"].forEach((k) => (t[k] = base.strip[k]));
    if (!form.strip.STRd) t.STRd += 10 + t.STR;
    if (!form.strip.DEXd) t.DEXd += 10 + t.DEX;
    for (const id of build.aspects || []) { const c = cards.cards[id]; if (c) addStrip(t, c.strip); }
    t.SPD = Math.max(t.SPD, form.fly || 0);
    t.size = form.size || "Medium";
    t.errors = [];
    return t;
  }
  // Totals from the gear in hand now (a dropped Shield stops counting); a condition with `card` (Pierce)
  // switches that card's bonuses off.
  function retally(F, c) {
    const off = c.conds.filter((k) => k.card).map((k) => k.card);
    const t = totals(Object.assign({}, c.build, { hands: c.hands.filter((id) => !off.includes(id)) }), F.cards);
    c.own = t;
    if (!c.form) { c.totals = t; c.size = t.size; }
  }
  function validate(build, cards) {
    build = normBuild(build);
    const out = totals(build, cards).errors.slice();
    const s = build.slots;
    const get = (id) => cards.cards[id];
    const check = (id, slot) => { const c = get(id); if (c && !SLOT_TYPES[slot].includes(typeOf(c))) out.push(`${c.name} (${typeOf(c)}) doesn't fit a ${slot} Slot`); };
    if (build.armor) check(build.armor, "armor");
    build.hands.forEach((id) => check(id, "hand"));
    build.jewelry.forEach((id) => check(id, "jewelry"));
    build.items.forEach((it) => check(it.id, "item"));
    build.aspects.forEach((id) => check(id, "aspect"));
    const hands = build.hands.reduce((n, id) => n + (get(id) && get(id).atk && get(id).atk.twoHanded ? 2 : 1), 0);
    if (hands > s.hand) out.push(`Hands: ${hands} used, ${s.hand} Slots`);
    if (build.jewelry.length > s.jewelry) out.push(`Jewelry: ${build.jewelry.length} cards, ${s.jewelry} Slots`);
    if (build.items.length > s.item) out.push(`Items: ${build.items.length} stacks, ${s.item} Slots`);
    if (build.aspects.length > s.aspect) out.push(`Aspects: ${build.aspects.length} cards, ${s.aspect} Slots`);
    for (const it of build.items) {
      const c = get(it.id); if (!c) continue;
      if (typeOf(c) === "Consumable" && (it.n || 1) > 3) out.push(`${c.name}: a stack holds at most 3`);
      if (typeOf(c) !== "Consumable" && typeOf(c) !== "Recipe" && (it.n || 1) > 1) out.push(`${c.name}: one per Item Slot`);
    }
    build.carried.forEach((id) => { const c = get(id); if (c && !SLOT_TYPES.hand.includes(typeOf(c))) out.push(`${c.name}: only Hand gear can be carried for a quick swap`); if (!c) out.push(`Unknown card ${id}`); });
    const seen = {};
    for (const id of equippedIds(build)) { if (seen[id]) out.push(`${(get(id) || { name: id }).name}: two copies can't be equipped (P 3.6)`); seen[id] = 1; }
    const t = totals(build, cards);
    for (const id of build.hands.concat(build.carried)) {
      const c = get(id);
      if (c && c.atk && c.atk.heavy) {
        const ab = c.atk.range ? "DEX" : "STR";
        if (t[ab] < 1) out.push(`Warning: ${c.name} is Heavy: −3 on attacks without ${ab} +1`);
      }
    }
    return out;
  }
  // RULING R202: fromFoe puts Armor, Jewelry, Items and Aspects in their Slots; a Shield always goes in a Hand,
  // other Hand gear fills the remaining Hands in `carries` order and the rest is carried (Legionary: Pilum +
  // Shield in hand, Gladius carried; Ogre: Greatclub in hand, Javelins carried). Slots grow to fit.
  function fromFoe(foe, cards) {
    const b = normBuild({ core: foe.core || null, body: foe.body ? clone(foe.body) : null, bonus: clone(foe.bonus || {}),
      extraDice: foe.extraDice || 0, ownFx: clone(foe.ownFx || []), powers: (foe.powers || []).slice(), boss: !!foe.boss,
      senses: clone(foe.senses || {}), alert: !!foe.alert, foe: foe.name });
    const hand = [];
    for (const id of foe.carries || []) {
      const c = cards.cards[id]; if (!c) continue;
      const ty = typeOf(c);
      if (ty === "Armor") b.armor = id;
      else if (SLOT_TYPES.hand.includes(ty)) hand.push(c);
      else if (ty === "Jewelry") b.jewelry.push(id);
      else if (SLOT_TYPES.item.includes(ty)) b.items.push({ id, n: ty === "Recipe" ? c.uses || 1 : 1 });
      else if (ASPECT_TYPES.includes(ty)) b.aspects.push(id);
    }
    const shields = hand.filter((c) => typeOf(c) === "Shield");
    let free = Math.max(0, b.slots.hand - shields.length);
    for (const c of hand) {
      if (typeOf(c) === "Shield") continue;
      const need = c.atk && c.atk.twoHanded ? 2 : 1;
      if (need <= free) { b.hands.push(c.id); free -= need; } else b.carried.push(c.id);
    }
    shields.forEach((c) => b.hands.push(c.id));
    // RULING R408: a foe built on a body (a beast) that carries no Hand gear has no Hand Slots: it can't pick up,
    // draw or wield gear, nor grapple with a hand (Wolf).
    if (foe.body && !hand.length) b.slots.hand = 0;
    b.slots.jewelry = Math.max(b.slots.jewelry, b.jewelry.length);
    b.slots.item = Math.max(b.slots.item, b.items.length);
    b.slots.aspect = Math.max(b.slots.aspect, b.aspects.length);
    return b;
  }

  // ---------- powers ----------
  function deckAbil(deck) { return deck && deck.kind === "spellbook" ? "INT" : "WIL"; }
  // Every power a creature has: { p, card, deck, src } ; `all` includes carried weapons (for uses).
  function powerList(cards, c, all) {
    const b = c.build, out = [];
    const fromCard = (src, id) => {
      const cd = cards.cards[id]; if (!cd) return;
      (cd.fx || []).forEach((p) => out.push({ p, card: id, deck: null, src }));
      const deck = cards.decks && cards.decks[cd.deck || id];
      if (deck) deck.powers.filter((p) => !(b.powers && b.powers.length) || b.powers.includes(p.name))
        .forEach((p) => out.push({ p, card: id, deck: cd.deck || id, src }));
    };
    const shifted = !!c.form && !all;
    if (!shifted) {
      if (b.core) fromCard("core", b.core);
      if (b.armor) fromCard("armor", b.armor);
      (all ? c.hands.concat(c.carried) : c.hands).forEach((id) => fromCard("hand", id));
      b.jewelry.forEach((id) => fromCard("jewelry", id));
      c.items.forEach((it) => fromCard("item", it.id));
    }
    b.aspects.forEach((id) => fromCard("aspect", id));
    (b.ownFx || []).forEach((p, i) => out.push({ p: p.id ? p : Object.assign({ id: "own#" + i }, p), card: null, deck: null, src: "own" }));
    return out;
  }
  function powersOf(F, c) { return powerList(F.cards, c, false); }
  function findPower(F, c, pid) { return powersOf(F, c).find((e) => e.p.id === pid); }
  function passives(F, c) { return powersOf(F, c).filter((e) => e.p.use === "passive"); }
  function passiveMax(F, c, k) { return passives(F, c).reduce((m, e) => Math.max(m, e.p[k] || 0), 0); }
  function passiveSum(F, c, k) { return passives(F, c).reduce((m, e) => m + (e.p[k] || 0), 0); }
  function deckOf(F, entry) { return entry && entry.deck ? F.cards.decks[entry.deck] : null; }
  function cardName(F, entry) { return (entry.card && F.cards.cards[entry.card] && F.cards.cards[entry.card].name) || entry.p.name || entry.p.id; }

  function parseUses(u) { const m = String(u || "").match(/(\d+)/); return m ? +m[1] : 0; }
  function maxResolve(F, c, deckId) { const d = F.cards.decks[deckId]; return Math.max(1, (d.resolve || 0) + (c.totals.WIL || 0)); }
  function refreshPools(F, c) {
    for (const id of Object.keys(c.resolve)) c.resolve[id] = Math.max(0, maxResolve(F, c, id) - (c.spentResolve[id] || 0));
  }

  // ---------- geometry ----------
  const space = (c) => SPACE[c.size] || 1;
  function rectAt(c, pos) { const s = space(c); return { x0: pos[0], y0: pos[1], x1: pos[0] + s - 1, y1: pos[1] + s - 1 }; }
  const rect = (c) => rectAt(c, c.pos);
  function cellsOfRect(r) { const out = []; for (let y = r.y0; y <= r.y1; y++) for (let x = r.x0; x <= r.x1; x++) out.push([x, y]); return out; }
  const cellsOf = (c, pos) => cellsOfRect(rectAt(c, pos || c.pos));
  function rectDist(a, b) {
    const gx = Math.max(0, b.x0 - a.x1, a.x0 - b.x1), gy = Math.max(0, b.y0 - a.y1, a.y0 - b.y1);
    return 5 * Math.max(gx, gy);
  }
  const dist = (a, b) => rectDist(rect(a), rect(b));
  const distToCell = (a, p) => rectDist(rect(a), { x0: p[0], y0: p[1], x1: p[0], y1: p[1] });
  function cellType(st, x, y) {
    const v = st.map.cells && st.map.cells[key(x, y)];
    return Array.isArray(v) ? v : v ? [v] : [];
  }
  const inBounds = (st, x, y) => x >= 0 && y >= 0 && x < st.map.w && y < st.map.h;
  const isWall = (st, x, y) => !inBounds(st, x, y) || cellType(st, x, y).includes("wall");
  const isDark = (st, x, y) => cellType(st, x, y).includes("dark");
  function isDifficult(st, x, y) {
    if (cellType(st, x, y).includes("difficult")) return true;
    return st.zones.some((z) => z.terrain === "difficult" && z.cells.includes(key(x, y)));
  }
  // Cells a segment between two cell centers passes through (endpoints excluded).
  function lineCells(a, b) {
    const ax = a[0] + 0.5 + 1e-7, ay = a[1] + 0.5 + 2e-7, bx = b[0] + 0.5 - 1e-7, by = b[1] + 0.5 - 2e-7;
    const n = Math.max(Math.abs(b[0] - a[0]), Math.abs(b[1] - a[1])) * 6 + 1, out = {};
    for (let i = 1; i < n; i++) {
      const x = Math.floor(ax + ((bx - ax) * i) / n), y = Math.floor(ay + ((by - ay) * i) / n);
      out[key(x, y)] = [x, y];
    }
    delete out[key(a[0], a[1])]; delete out[key(b[0], b[1])];
    return Object.values(out);
  }
  // RULING R204: line of sight runs center to center between any square of each creature; walls block it,
  // "cover" squares on every clear line give cover (+2), creatures never give cover. No clear line = full cover.
  function sightCells(st, from, to, skip) {
    let los = false, cover = true;
    for (const p of from) for (const q of to) {
      const mid = lineCells(p, q).filter((c) => !skip[key(c[0], c[1])]);
      if (mid.some((c) => isWall(st, c[0], c[1]))) continue;
      los = true;
      if (!mid.some((c) => cellType(st, c[0], c[1]).includes("cover"))) cover = false;
    }
    return { los, cover: los && cover };
  }
  function sight(st, a, b) {
    const ca = cellsOf(a), cb = cellsOf(b), skip = {};
    ca.concat(cb).forEach((c) => (skip[key(c[0], c[1])] = 1));
    return sightCells(st, ca, cb, skip);
  }
  function sightToCell(st, a, p) {
    const ca = cellsOf(a), skip = {};
    ca.concat([p]).forEach((c) => (skip[key(c[0], c[1])] = 1));
    return sightCells(st, ca, [p], skip);
  }
  // RULING R205: a creature is in Dark when every square it occupies is Dark.
  const inDark = (st, c) => cellsOf(c).every((p) => isDark(st, p[0], p[1]));

  // ---------- creature state helpers ----------
  const has = (c, name) => c.conds.some((k) => k.name === name);
  const condsNamed = (c, name) => c.conds.filter((k) => k.name === name);
  const incap = (c) => c.dead || c.conds.some((k) => INCAP.includes(k.name));
  const stunnedLike = (c) => c.conds.some((k) => ["Stunned", "Unconscious", "Petrified"].includes(k.name));
  const proneLike = (c) => has(c, "Prone") || has(c, "Unconscious");
  const conscious = (c) => !c.dead && c.hp > 0;
  const living = (st) => Object.values(st.creatures).filter((c) => !c.dead);
  function speedOf(c) {
    if (c.conds.some((k) => SPEED0.includes(k.name))) return 0;
    return Math.max(0, c.totals.SPD - 5 * (c.exhaustion || 0));
  }
  function darkvision(F, c) { return Math.max((c.build.senses && c.build.senses.darkvision) || 0, passiveMax(F, c, "darkvision")); }
  function canSee(F, obs, tgt) {
    const st = F.state;
    if (obs.dead || has(obs, "Blinded")) return false;
    if (obs === tgt) return true;
    if (has(tgt, "Invisible")) return false;
    if (!sight(st, obs, tgt).los) return false;
    if (inDark(st, tgt) && darkvision(F, obs) < dist(obs, tgt)) return false;
    return true;
  }
  const sizeGap = (a, b) => Math.abs((SIZE_N[a.size] || 2) - (SIZE_N[b.size] || 2));
  // P 6.5: a is engaged with enemy b when within 5 ft, a isn't Incapacitated, sizes at most one apart.
  function engaged(a, b) {
    return a.side !== b.side && !a.dead && !b.dead && !incap(a) && dist(a, b) <= 5 && sizeGap(a, b) <= 1;
  }
  // P 6.5 Outnumbered, with DESIGN 5 "compares sides".
  // RULING R223: read as written: an Incapacitated creature engages no one, so it never counts for its own side
  // (attacking a lone Stunned or Unconscious target gives Outnumbered 1 vs 0).
  function outnumbered(st, attacker, target) {
    const all = living(st), mine = all.filter((c) => c.side === attacker.side);
    const us = mine.filter((c) => engaged(c, target)).map((c) => c.id);
    const them = all.filter((c) => c.side === target.side && mine.some((m) => engaged(c, m))).map((c) => c.id);
    return { us: us.length, them: them.length, n: us.length - them.length, list: { us, them } };
  }
  const engagedEnemies = (st, c) => living(st).filter((e) => e.side !== c.side && engaged(e, c));
  function handsUsed(F, c) { return c.hands.reduce((n, id) => n + (F.cards.cards[id] && F.cards.cards[id].atk && F.cards.cards[id].atk.twoHanded ? 2 : 1), 0); }
  const freeHand = (F, c) => !c.form && handsUsed(F, c) < c.build.slots.hand;
  function canCastBook(F, c) {
    if (c.form) return false;
    return freeHand(F, c) || c.hands.some((id) => (F.cards.cards[id].fx || []).some((p) => p.use === "passive" && p.castingHand));
  }
  const canSpeak = (c) => !incap(c) && !c.form;
  const holdsShield = (F, c) => !c.form && c.hands.some((id) => typeOf(F.cards.cards[id]) === "Shield");

  // ---------- fight state ----------
  function freshTurn(prev) {
    return { moved: 0, speed: 0, action: false, bonus: false, reaction: prev ? prev.reaction : false, interact: false,
      spellCast: false, disengaged: false, dodging: prev ? prev.dodging : false, firstMover: false, half: false,
      attacksLeft: 0, attackAction: false, lightWeapon: null, safeFt: 0, bonusMelee: 0, loaded: false };
  }
  function initCreature(F, sc) {
    const cards = F.cards;
    const build = normBuild(sc.build || (sc.foe ? fromFoe(cards.foes.find((f) => f.name === sc.foe), cards) : {}));
    const t = totals(build, cards);
    const c = { id: sc.id, side: sc.side, name: sc.name || sc.id, pos: sc.pos.slice(), size: t.size, totals: t, own: t,
      hp: t.HP, maxHp: t.HP, temp: 0, form: null, dead: false, down: false, stable: false, death: { ok: 0, fail: 0 },
      conds: [], mods: [], turn: freshTurn(), hands: build.hands.slice(), carried: build.carried.slice(),
      items: build.items.map((it) => { const cd = cards.cards[it.id]; return { id: it.id, n: it.n != null ? it.n : cd && typeOf(cd) === "Recipe" ? cd.uses || 1 : 1 }; }),
      uses: {}, sp: {}, resolve: {}, spentResolve: {}, extra: { sp: 0, resolve: 0 }, highMagic: {},
      react: sc.react || "ask", boss: !!build.boss, build, exhaustion: 0, spellTurn: -1, rechargeUsed: {}, turnUsed: {} };
    for (const e of powerList(cards, c, true)) {
      if (e.p.uses) c.uses[e.p.id] = parseUses(e.p.uses);
      if (e.p.recharge) c.uses[e.p.id] = 1;
    }
    for (const it of c.items) { const d = cards.decks && cards.decks[it.id]; if (d && d.kind === "spellbook") c.sp[it.id] = d.sp || 0; }
    for (const id of build.aspects) { const d = cards.decks && cards.decks[id]; if (d && d.kind !== "spellbook") { c.resolve[id] = 0; c.spentResolve[id] = 0; } }
    refreshPools(F, c);
    const pass = powerList(cards, c, false).filter((e) => e.p.use === "passive");
    c.extra.sp = pass.reduce((n, e) => n + (e.p.extraSp || 0), 0);
    c.extra.resolve = pass.reduce((n, e) => n + (e.p.extraResolve || 0), 0);
    return c;
  }
  function initState(F, sc) {
    const st = { version: 1, round: 0, side: null, first: null, phase: "setup", winner: null, active: null, done: [],
      halfTurn: {}, map: clone(sc.map || { w: 12, h: 12, cells: {} }), zones: [], creatures: {}, ground: [],
      surprise: sc.surprise || null, ambush: false, turnNo: 0, nextId: 1,
      rng: { seed: sc.seed != null ? sc.seed : 1, s: (sc.seed != null ? sc.seed : 1) | 0 }, stats: {} };
    st.map.cells = st.map.cells || {};
    F.state = st;
    for (const s of sc.creatures || []) {
      const c = initCreature(F, s);
      st.creatures[c.id] = c;
      if (c.boss) st.halfTurn[c.id] = false;
      st.stats[c.id] = { name: c.name, side: c.side, dmgDealt: 0, dmgTaken: 0, healed: 0, attacks: 0, hits: 0, crits: 0,
        kills: 0, downs: 0, roundsAlive: 0, spent: { sp: 0, resolve: 0, uses: 0, consumables: 0 }, endHp: c.hp };
    }
    return st;
  }

  // ---------- events ----------
  function emit(X, ev) {
    ev.round = X.st.round;
    X.events.push(ev);
    return ev;
  }
  const nm = (X, id) => (X.st.creatures[id] ? X.st.creatures[id].name : id);
  const stat = (X, id) => X.st.stats[id] || (X.st.stats[id] = { spent: {} });

  // ---------- durations ----------
  // until: { ev: "start"|"end", who, skip, rounds } | { lasting: id } | null
  function mkUntil(X, spec, src, tgt, p) {
    const active = X.st.active;
    switch (spec) {
      case "endTargetTurn": return { ev: "end", who: tgt.id, skip: active === tgt.id && !X.st.halfActive ? 1 : 0 };
      case "startSourceTurn": return { ev: "start", who: src.id, skip: 0 };
      case "endSourceTurn": return { ev: "end", who: src.id, skip: active === src.id && !X.st.halfActive ? 1 : 0 };
      // RULING R236: endSourceTurn applied during the source's own turn lasts to the end of its NEXT turn; the extra
  // value "endThisTurn" means the current one.
  // Extension: end of the source's current turn (Steady Aim "this turn").
      case "endThisTurn": return { ev: "end", who: src.id, skip: 0 };
      case "dur": return durUntil(p && p.dur, src);
      default: return null;
    }
  }
  // RULING R206: a Duration counts the source's turn starts: "1 minute" ends at the start of the source's 10th
  // turn after it began (1 round = 1 turn start). Boss half turns never count for durations.
  function durUntil(dur, src) { const n = DUR[dur]; return n ? { ev: "start", who: src.id, rounds: n } : null; }
  function tick(X, ev, who) {
    const st = X.st;
    const due = (u) => {
      if (!u || u.ev !== ev || u.who !== who) return false;
      if (u.rounds != null) { u.rounds--; return u.rounds <= 0; }
      if (u.skip > 0) { u.skip--; return false; }
      return true;
    };
    for (const c of Object.values(st.creatures)) {
      for (const m of c.mods.slice()) if (due(m.until)) { c.mods.splice(c.mods.indexOf(m), 1); emit(X, { t: "condEnd", target: c.id, mod: true, text: `${c.name}: ${m.power || m.kind} ends.` }); }
      for (const k of c.conds.slice()) if (due(k.until)) removeCond(X, c, k, "duration ends");
    }
    for (const z of st.zones.slice()) if (due(z.until)) { st.zones.splice(st.zones.indexOf(z), 1); emit(X, { t: "condEnd", text: `${z.name} ends.` }); }
  }

  // ---------- conditions and mods ----------
  function addCond(X, t, name, o) {
    o = o || {};
    if (t.dead) return null;
    if (name === "Exhaustion") {
      t.exhaustion = Math.min(6, (t.exhaustion || 0) + (o.levels || 1));
      emit(X, { t: "cond", target: t.id, cond: name, level: t.exhaustion, text: `${t.name}: Exhaustion ${t.exhaustion}.` });
      if (t.exhaustion >= 6) die_(X, t, "Exhaustion 6", o.source);
      return null;
    }
    // RULING R207: a condition doesn't stack with itself: the same condition from the same source replaces
    // the old one; from another source both are kept (their effect still counts once).
    const old = t.conds.find((k) => k.name === name && k.source === (o.source || null));
    if (old) removeCond(X, t, old, null, true);
    const k = { id: "k" + X.st.nextId++, name, source: o.source || null, until: o.until || null, lasting: !!o.lasting,
      subdue: !!o.subdue, rolls: 0, hurt: 0, hits: 0, bite: !!o.subdue, abil: o.abil || null, vs: o.vs || null,
      flat: !!o.flat, power: o.power || null, effect: !!o.effect, card: o.card || null, endAction: o.endAction || null };
    t.conds.push(k);
    if (k.card) retally(X.F, t);
    emit(X, { t: "cond", target: t.id, actor: k.source, cond: name, lasting: k.lasting, text: `${t.name} is ${name}${k.source && k.source !== t.id ? " (" + nm(X, k.source) + ")" : ""}${k.lasting ? ", Lasting" : ""}.` });
    if (INCAP.includes(name) || SPEED0.includes(name)) { t.turn.dodging = false; }
    if (name === "Unconscious" || name === "Stunned" || name === "Petrified") dropHeld(X, t, name === "Unconscious");
    return k;
  }
  function dropHeld(X, t, drop) {
    if (!drop || t.form || !t.hands.length) return;
    for (const id of t.hands) X.st.ground.push({ card: id, pos: t.pos.slice(), owner: t.id });
    emit(X, { t: "note", target: t.id, text: `${t.name} drops ${t.hands.map((id) => X.F.cards.cards[id].name).join(", ")}.` });
    t.hands = [];
    retally(X.F, t);
  }
  function removeCond(X, t, k, why, silent) {
    const i = t.conds.indexOf(k);
    if (i < 0) return;
    t.conds.splice(i, 1);
    t.mods = t.mods.filter((m) => !(m.until && m.until.lasting === k.id));
    if (k.card) retally(X.F, t);
    if (!silent) emit(X, { t: "condEnd", target: t.id, cond: k.name, text: `${t.name} is no longer ${k.name}${why ? " (" + why + ")" : ""}.` });
  }
  function addMod(X, t, m) {
    const mod = Object.assign({ kind: "attack", n: 0, dice: null, next: false, until: null, source: null, power: null }, m);
    // RULING R500: the same power doesn't stack with itself (P 3.6): a new use replaces the old one, refreshing it.
    if (mod.power && !(mod.until && mod.until.lasting)) t.mods = t.mods.filter((o) => !(o.power === mod.power && o.kind === mod.kind && !(o.until && o.until.lasting)));
    t.mods.push(mod);
    const what = mod.kind === "def" ? `${(mod.defs || ["all"]).join("/")} Defense` : mod.kind;
    emit(X, { t: "cond", target: t.id, actor: mod.source, mod: mod.kind, text: `${t.name}: ${mod.n ? signed(mod.n) : ""}${mod.dice ? (mod.n ? " " : "") + mod.dice : ""} ${what}${mod.next ? " (next roll)" : ""}${mod.power ? " — " + mod.power : ""}.` });
    return mod;
  }

  // ---------- defenses ----------
  // defs of an attack: "weapon" → { STR, DEX } (the higher counts); otherwise the named one.
  function defList(vs) { return !vs || vs === "weapon" ? ["STR", "DEX"] : [vs]; }
  function defense(F, t, ab, o) {
    o = o || {};
    let v = t.totals[ab + "d"];
    for (const m of t.mods) if (m.kind === "def" && (!m.defs || m.defs.includes(ab) || (m.defs.includes("targeted") && o.targeted))) v += m.n || 0;
    if (t.turn.dodging && !incap(t) && speedOf(t) > 0) v += 3;
    if (o.cover) v += 2;
    if (o.tags && o.tags.length) for (const e of passives(F, t)) if (e.p.defVs && e.p.defVs[ab] && (e.p.tags || []).some((g) => o.tags.includes(g))) v += e.p.defVs[ab];
    return v;
  }
  function defsOf(F, t, vs, o) {
    const out = {};
    for (const ab of defList(vs)) out[ab] = defense(F, t, ab, Object.assign({ targeted: true }, o));
    return out;
  }
  const best = (defs) => Math.max(...Object.values(defs));

  // ---------- weapons ----------
  function weaponOf(F, a, wid) {
    if (wid === "unarmed") return { id: "unarmed", name: "Unarmed strike", hit: 2, dice: "1", abil: ["STR"], type: "Physical" };
    if (wid === "improvised") return { id: "improvised", name: "Improvised weapon", hit: 0, dice: "1d4", abil: ["STR"], type: "Physical" };
    if (wid === "natural") {
      if (!a.form || !a.form.weapon) fail("No natural weapon");
      return Object.assign({ id: "natural", natural: true, type: "Physical" }, a.form.weapon);
    }
    if (a.form) fail("Your gear is merged into your Form");
    if (!a.hands.includes(wid)) fail("That weapon isn't in your Hands");
    const cd = F.cards.cards[wid];
    if (!cd || !cd.atk) fail(`${cd ? cd.name : wid} isn't a weapon`);
    return Object.assign({ id: wid, name: cd.name, card: wid }, cd.atk);
  }
  const bestAbil = (c, list) => list.reduce((b, ab) => (c.totals[ab] > c.totals[b] ? ab : b), list[0]);
  function meleeWeapons(F, c) {
    if (c.form) return c.form.weapon ? ["natural"] : ["unarmed"];
    const ws = c.hands.filter((id) => { const cd = F.cards.cards[id]; return cd && cd.atk && !cd.atk.range; });
    return ws.concat(["unarmed"]);
  }
  const weaponReach = (w) => (w.reach ? 10 : 5);
  function meleeReach(F, c) { return Math.max(...meleeWeapons(F, c).map((w) => weaponReach(weaponOf(F, c, w)))); }

  // ---------- attack building (pure: used by preview) ----------
  // src: { w } weapon spec, or { entry } power; plus thrown, offhand, opportunity, area, unarmedAbil
  function attackInfo(F, a, t, src) {
    const st = F.state;
    const info = { bonus: 0, adv: 0, dis: 0, why: [], parts: [], diceMods: [], nextMods: [] };
    const add = (n, why) => { if (n > 0) info.adv += n; else info.dis -= n; info.why.push(`${n > 0 ? "+" : "−"}${Math.abs(n)}d20 ${why}`); };
    const flat = (n, why) => { if (!n) return; info.bonus += n; info.parts.push(`${signed(n)} ${why}`); };
    const d = dist(a, t);
    info.distance = d;
    // RULING R405: a zone's later attacks (a creature entering it or ending its turn there) use only its source's
    // attack bonus: the source isn't making an attack then, so its own mods and situations don't apply, and a
    // dead source's zone still attacks.
    const zone = !!src.zone;
    if ((a.dead && !zone) || t.dead) fail("Not a living creature");
    if (condsNamed(a, "Charmed").some((k) => k.source === t.id)) fail(`${a.name} is Charmed by ${t.name}`);
    const sg = sight(st, a, t);
    // RULING R231: Unconscious and Stunned creatures still "see" for unseen/advantage purposes; only Blinded,
    // Dark, Invisible and walls hide (Unconscious already gives Stunned + Prone).
    if (!sg.los && !src.area) fail(`${t.name} has full cover`);
    let ranged = false, melee = false, vs = "weapon";
    if (src.w) {
      const w = src.w;
      if (src.thrown && !w.thrown) fail(`${w.name} can't be thrown`);
      const rng = w.range || (src.thrown ? w.thrown : null);
      if (rng) {
        ranged = true;
        if (d > rng[1]) fail(`${t.name} is beyond long range (${rng[1]} ft)`);
        if (d > rng[0]) add(-1, "long range");
      } else {
        melee = true;
        if (d > weaponReach(w)) fail(`${t.name} is out of reach (${weaponReach(w)} ft)`);
      }
      const ab = src.abil ? bestAbil(a, src.abil) : bestAbil(a, w.abil || ["STR"]);
      info.abil = ab;
      flat(a.totals[ab], ab);
      flat(w.hit || 0, "to hit");
      if (w.heavy && a.totals[ranged ? "DEX" : "STR"] < 1) flat(-3, "Heavy");
      info.weapon = w;
    } else {
      const p = src.entry.p, deck = deckOf(F, src.entry);
      if (!src.area) {
        const reach = powerReach(F, a, src.entry);
        if (d > reach) fail(`${t.name} is out of range (${reach} ft)`);
      }
      vs = p.atk.vs || "weapon";
      // RULING R224: a power attack with a range above 5 ft is a ranged attack (enemy within 5 ft: disadvantage);
      // long range doesn't apply to powers.
      ranged = !src.area && powerReach(F, a, src.entry) > 5;
      melee = !ranged && !src.area && vs === "weapon";
      info.abil = atkAbil(F, a, src.entry);
      if (p.atk.flat != null) flat(p.atk.flat, "attack");
      else if (p.atk.abil === "deck") { flat(a.totals[deckAbil(deck)], deckAbil(deck)); flat(deck ? deck.atk || 0 : 0, "deck"); }
      else { flat(a.totals[info.abil], info.abil); flat(p.atk.hit || 0, "to hit"); }
    }
    info.ranged = ranged; info.melee = melee; info.vs = vs;
    // RULING R234: Exhaustion's −2 per level applies to attack and maintain rolls, not to death saves or side initiative.
    if (a.exhaustion) flat(-2 * a.exhaustion, "Exhaustion");
    for (const m of zone ? [] : a.mods) {
      if (m.kind !== "attack" && m.kind !== "roll") continue;
      if (m.only === "ranged" && !ranged) continue;
      if (m.only === "melee" && !melee) continue;
      if (m.near) { const h = st.creatures[m.near]; if (!h || dist(h, t) > 5) continue; }
      if (m.n) flat(m.n, m.power || m.kind);
      if (m.dice) { info.diceMods.push(m.dice); info.parts.push(`${/^[-−]/.test(m.dice) ? "−" + m.dice.slice(1) : "+" + m.dice} ${m.power || m.kind}`); }
      if (m.next) info.nextMods.push(m);
    }
    // situations (P 5.2): each source once. An area roll skips the target's situations (P 6.6).
    if (zone) {
      info.cover = 0; info.ranged = false; info.melee = false; info.vs = vs; info.tags = src.entry.p.tags || [];
      info.defs = defsOf(F, t, vs, { tags: info.tags }); info.def = best(info.defs);
      info.dice = 1; info.keep = null;
      return info;
    }
    if (!src.area && !canSee(F, a, t)) add(-1, "can't see the target");
    if (!src.area && !canSee(F, t, a)) add(1, "unseen");
    if (has(a, "Prone")) add(-1, "Prone");
    if (has(a, "Restrained")) add(-1, "Restrained");
    if (has(a, "Poisoned")) add(-1, "Poisoned");
    if (condsNamed(a, "Frightened").some((k) => { const s = st.creatures[k.source]; return s && canSee(F, a, s); })) add(-1, "Frightened");
    if (condsNamed(a, "Grappled").some((k) => k.source !== t.id)) add(-1, "Grappled");
    if (ranged && living(st).some((e) => e.side !== a.side && !incap(e) && dist(e, a) <= 5 && canSee(F, e, a))) add(-1, "enemy within 5 ft");
    if (!src.area) {
      // RULING R208: Unconscious counts as Stunned and Prone (two sources); Petrified as Stunned.
      if (proneLike(t)) add(d <= 5 ? 1 : -1, d <= 5 ? "target Prone" : "target Prone, beyond 5 ft");
      if (has(t, "Restrained")) add(1, "target Restrained");
      if (stunnedLike(t)) add(1, "target Stunned");
      const o = outnumbered(st, a, t);
      info.outnumbered = o;
      if (o.n) add(o.n, `Outnumbered ${o.us} vs ${o.them}`);
    }
    info.cover = sg.cover && !src.area ? 2 : 0;
    info.tags = src.entry ? src.entry.p.tags || [] : [];
    info.defs = defsOf(F, t, vs, { cover: !!info.cover, tags: info.tags });
    info.def = best(info.defs);
    runHooks(F, null, a, t, "modifyAttack", { attack: info, weapon: src.w, entry: src.entry });
    info.dice = 1 + Math.abs(info.adv - info.dis);
    info.keep = info.adv > info.dis ? "highest" : info.adv < info.dis ? "lowest" : null;
    return info;
  }
  function atkAbil(F, a, entry) {
    const p = entry.p;
    if (!p.atk) return null;
    if (p.atk.flat != null) return null;
    if (p.atk.abil === "deck") return deckAbil(deckOf(F, entry));
    return bestAbil(a, p.atk.abil || ["STR"]);
  }
  function powerReach(F, c, entry) {
    const p = entry.p;
    let r = p.reach != null ? p.reach : p.target === "self" ? 0 : 5;
    for (const e of passives(F, c)) {
      const dflt = e.p.params && e.p.params.default;
      if (p.kind === "Anthem" && e.p.anthemReach && (dflt == null || p.reach == null || p.reach === dflt)) r = Math.max(r, e.p.anthemReach);
      if (p.kind === "Cue" && e.p.cueReach && (dflt == null || p.reach == null || p.reach === dflt)) r = Math.max(r, e.p.cueReach);
    }
    return r;
  }

  // ---------- hooks ----------
  function makeCtx(F, X, extra) {
    const ctx = Object.assign({ fight: F, state: F.state, cards: F.cards }, extra);
    const need = () => { if (!X) fail("hook can't change state in preview"); return X; };
    ctx.roll = (dice) => rollDice(need(), dice, { mods: ctx.actor && ctx.actor.totals }).total;
    ctx.d20 = (adv, dis) => rollD20(need(), adv || 0, dis || 0);
    ctx.emit = (ev) => emit(need(), ev);
    ctx.ask = (prompt) => ask(need(), prompt);
    ctx.dealDamage = (t, n, type, o) => applyDamage(need(), t, n, type, Object.assign({ source: ctx.actor && ctx.actor.id }, o));
    ctx.heal = (t, n) => heal(need(), t, n, ctx.actor);
    ctx.addCond = (t, name, o) => addCond(need(), t, name, Object.assign({ source: ctx.actor && ctx.actor.id }, o));
    ctx.removeCond = (t, name) => condsNamed(t, name).forEach((k) => removeCond(need(), t, k));
    ctx.addMod = (t, m) => addMod(need(), t, Object.assign({ source: ctx.actor && ctx.actor.id }, m));
    ctx.apply = (effects, target) => applyDo(need(), ctx.actor, ctx.entry, effects, target, { hit: true });
    ctx.distance = dist; ctx.engaged = engaged;
    ctx.weapon = (id) => weaponOf(F, ctx.actor, id);
    ctx.weaponReach = weaponReach;
    ctx.sees = (a, b) => sight(F.state, a, b).los;
    ctx.attackInfo = (t, src) => attackInfo(F, ctx.actor, t, src);
    ctx.areaWeaponAttack = (w, targets, o) => areaWeaponAttack(need(), ctx.actor, w, targets, o);
    ctx.creature = (id) => F.state.creatures[id];
    ctx.creatures = () => Object.values(F.state.creatures);
    return ctx;
  }
  // Calls handler `fn` of the passive hooks of attacker a (its used weapon's only) and of target t.
  function runHooks(F, X, a, t, fn, extra) {
    const go = (c, role) => {
      for (const e of passives(F, c)) {
        if (!e.p.hook || !HOOKS[e.p.hook] || !HOOKS[e.p.hook][fn]) continue;
        if (e.src === "hand" && role === "attacker" && (!extra.weapon || extra.weapon.card !== e.card)) continue;
        HOOKS[e.p.hook][fn](makeCtx(F, X, Object.assign({ actor: c, target: role === "attacker" ? t : a, role, power: e.p, entry: e }, extra)));
      }
    };
    go(a, "attacker");
    if (t) go(t, "target");
  }

  // ---------- rolling an attack ----------
  // Returns { hit, crit, nat, total, def, defs }. t null for area rolls (compare later per target).
  function rollAttack(X, a, t, info, o) {
    o = o || {};
    const F = X.F;
    let r = rollD20(X, info.adv, info.dis, "attack");
    let extra = 0;
    for (const dm of info.diceMods) extra += rollDice(X, dm, {}).total;
    for (const m of info.nextMods) { const i = a.mods.indexOf(m); if (i >= 0) a.mods.splice(i, 1); }
    const res = { roll: r, bonus: info.bonus + extra, defs: Object.assign({}, info.defs), rerolled: false, a, t };
    res.total = r.kept + res.bonus;
    const label = o.label || "attack";
    emit(X, { t: "roll", actor: a.id, target: t ? t.id : null, kind: "attack", dice: r.dice, kept: r.kept, bonus: res.bonus,
      total: res.total, vs: t ? best(res.defs) : null, adv: info.adv, dis: info.dis, why: info.why.concat(info.parts),
      text: `${a.name} ${label}${t ? " → " + t.name : ""}: ${r.dice.length > 1 ? "[" + r.dice.join(", ") + "] keeps " : ""}${r.kept} ${signed(res.bonus)} = ${res.total}${t ? " vs " + best(res.defs) : ""}` });
    stat(X, a.id).attacks++;
    cuePhase(X, res, "attack");
    if (t) decide(res);
    return res;
  }
  function decide(res) {
    const nat = res.roll.kept;
    res.nat = nat; res.crit = nat === 20;
    res.def = best(res.defs);
    res.hit = nat === 20 || (nat !== 1 && res.total >= res.def);
    return res;
  }
  const flipped = (res, dTotal, dDef) => res.roll.kept !== 20 && res.roll.kept !== 1 && (res.total + dTotal >= best(res.defs) + dDef) !== (res.total >= best(res.defs));

  // RULING R226: Cues fire on attack rolls only (the sim makes no ability checks); "auto" uses a flat Cue only when
  // it flips the outcome and never uses Reroll; a Cue on "ally" never targets the user's own roll.
  // Cues (rollNear): after the roll, before the hit is announced (P 10.6).
  function cuePhase(X, res, kind) {
    const F = X.F, st = X.st, roller = res.a, used = {};
    for (;;) {
      const opts = [];
      for (const c of living(st)) {
        if (used[c.id] || c.turn.reaction || incap(c)) continue;
        for (const e of powersOf(F, c)) {
          const p = e.p;
          if (p.use !== "reaction" || p.on !== "rollNear") continue;
          const kinds = (p.params && p.params.rollKinds) || ["attack", "check"];
          if (!kinds.includes(kind)) continue;
          if (!canPay(F, c, e, p.cost || 0).ok || !needsOk(F, c, e)) continue;
          if (dist(c, roller) > powerReach(F, c, e)) continue;
          if (has(roller, "Deafened")) continue;
          const fx = p.do || [];
          const reroll = fx.some((d) => d.reroll);
          const rollMod = fx.find((d) => d.mod === "roll");
          const ally = roller.side === c.side;
          let mode = null, delta = 0;
          if (reroll) { if (!res.rerolled && (p.target === "creature" || (p.target === "ally") === ally)) mode = "reroll"; }
          else if (rollMod) {
            delta = rollMod.n || 0;
            if (p.target === "enemy" && !ally) mode = "roll";
            else if (p.target === "ally" && ally && roller !== c) mode = "roll";
            // RULING R209: a Cue with params.orDefense (Steady Now) used on an enemy's attack adds its number to
            // the targeted ally's Defense instead.
            else if (p.target === "ally" && !ally && p.params && p.params.orDefense && res.t && res.t.side === c.side) mode = "def";
            else if (p.target === "creature") mode = "roll";
          }
          if (!mode) continue;
          // auto decides only when the change is known to flip the outcome in its side's favour; never rerolls.
          let flips = false;
          if (res.t && mode === "roll" && !rollMod.dice) flips = flipped(res, delta, 0) && (ally ? res.total < best(res.defs) : res.total >= best(res.defs));
          if (res.t && mode === "def") flips = flipped(res, 0, delta) && res.total >= best(res.defs);
          opts.push({ actor: c.id, power: p.id, label: `${c.name}: ${p.name}${mode === "def" ? " (Defense)" : ""}`, e, c, mode, delta, flips });
        }
      }
      if (!opts.length) return;
      let pick = opts.find((o) => o.c.react === "auto" && o.flips);
      if (!pick) {
        const asks = opts.filter((o) => o.c.react === "ask");
        if (!asks.length) return;
        const ch = ask(X, { kind: "reaction", text: `${roller.name} rolled ${res.total}${res.t ? " vs " + res.t.name + " (Defense " + best(res.defs) + ")" : ""}. Use a Cue?`,
          trigger: { on: "rollNear", roller: roller.id, target: res.t ? res.t.id : null, total: res.total }, options: asks.map((o) => ({ actor: o.actor, power: o.power, label: o.label })) });
        if (ch == null) return;
        pick = asks[ch];
      }
      used[pick.actor] = 1;
      const c = pick.c, p = pick.e.p;
      c.turn.reaction = true;
      pay(X, c, pick.e, p.cost || 0, {});
      emit(X, { t: "reaction", actor: c.id, target: roller.id, power: p.id, text: `${c.name} uses ${p.name} on ${roller.name}'s roll.` });
      if (p.hook) { hookTrigger(X, c, pick.e, { on: "rollNear", roll: res }); continue; }
      if (pick.mode === "reroll") {
        const r = rollD20(X, res.roll.adv, res.roll.dis, "reroll");
        res.total += r.kept - res.roll.kept; res.roll = r; res.rerolled = true;
        emit(X, { t: "roll", actor: roller.id, kind, reroll: true, dice: r.dice, kept: r.kept, bonus: res.bonus, total: res.total, adv: r.adv, dis: r.dis, why: [], text: `${roller.name} rerolls: ${r.kept} → ${res.total}` });
      } else {
        const rm = p.do.find((d) => d.mod === "roll");
        let delta = rm.n || 0;
        if (rm.dice) delta += rollDice(X, rm.dice, {}).total;
        if (pick.mode === "def") { for (const k of Object.keys(res.defs)) res.defs[k] += delta; }
        else { res.total += delta; res.bonus += delta; }
        emit(X, { t: "note", actor: c.id, text: `${pick.mode === "def" ? res.t.name + "'s Defense" : roller.name + "'s roll"} ${signed(delta)} → ${pick.mode === "def" ? best(res.defs) : res.total}.` });
      }
    }
  }

  // Defensive and retaliation reactions when an attack hits (hitSelf, hitAlly5, meleeHitSelf5).
  function hitReactions(X, res, melee) {
    const F = X.F, st = X.st, a = res.a, t = res.t, used = {};
    for (;;) {
      if (!res.hit) return;
      const opts = [];
      for (const c of living(st)) {
        if (used[c.id] || c.turn.reaction || incap(c)) continue;
        for (const e of powersOf(F, c)) {
          const p = e.p;
          if (p.use !== "reaction") continue;
          const ok = (p.on === "hitSelf" && c === t) || (p.on === "hitAlly5" && c !== t && c.side === t.side && dist(c, t) <= 5) ||
            // RULING R400: "a creature within 5 ft hits you" (Ring of Sparks) counts any attack from within 5 ft,
            // a ranged one or a spell too, as printed and as SPEC 2.1 defines meleeHitSelf5.
            (p.on === "meleeHitSelf5" && c === t && a !== t && dist(a, t) <= 5);
          if (!ok) continue;
          if (!canPay(F, c, e, p.cost || 0).ok || !needsOk(F, c, e)) continue;
          if (deckOf(F, e) && deckOf(F, e).kind === "spellbook" && (!canCastBook(F, c) || (p.cost > 0 && c.spellTurn === st.turnNo))) continue;
          let up = 0;
          const dm = (p.do || []).find((d) => d.mod === "def");
          if (dm) { const keys = Object.keys(res.defs); up = Math.max(...keys.map((k) => (!dm.defs || dm.defs.includes(k) || dm.defs.includes("targeted") ? res.defs[k] + dm.n : res.defs[k]))) - best(res.defs); }
          const defensive = !!dm, flips = defensive && res.roll.kept !== 20 && res.total < best(res.defs) + up;
          opts.push({ actor: c.id, power: p.id, label: `${c.name}: ${p.name}`, e, c, defensive, flips });
        }
      }
      if (!opts.length) return;
      // RULING R210: "auto" uses a defensive reaction only when it turns the hit into a miss, and otherwise a
      // retaliation reaction (Ring of Sparks); it never spends one that changes nothing.
      let pick = opts.find((o) => o.c.react === "auto" && o.flips) || opts.find((o) => o.c.react === "auto" && !o.defensive);
      if (!pick) {
        const asks = opts.filter((o) => o.c.react === "ask");
        if (!asks.length) return;
        const ch = ask(X, { kind: "reaction", text: `${a.name} hits ${t.name} (${res.total} vs ${best(res.defs)}). React?`,
          trigger: { on: "hit", attacker: a.id, target: t.id, total: res.total, def: best(res.defs) }, options: asks.map((o) => ({ actor: o.actor, power: o.power, label: o.label })) });
        if (ch == null) return;
        pick = asks[ch];
      }
      used[pick.actor] = 1;
      const c = pick.c, p = pick.e.p;
      c.turn.reaction = true;
      pay(X, c, pick.e, p.cost || 0, {});
      if (deckOf(F, pick.e) && deckOf(F, pick.e).kind === "spellbook" && p.cost > 0) c.spellTurn = st.turnNo;
      emit(X, { t: "reaction", actor: c.id, target: a.id, power: p.id, text: `${c.name} uses ${p.name}.` });
      if (p.hook) { hookTrigger(X, c, pick.e, { on: p.on, attacker: a, target: t, hit: true, res }); decide(res); continue; }
      for (const d of p.do || []) {
        if (d.mod === "def") {
          const holder = p.on === "hitAlly5" ? t : c;
          for (const k of Object.keys(res.defs)) if (!d.defs || d.defs.includes(k) || d.defs.includes("targeted")) res.defs[k] += d.n;
          if (d.until) addMod(X, holder, { kind: "def", n: d.n, defs: d.defs, until: mkUntil(X, d.until, c, holder, p), source: c.id, power: p.name });
        } else applyDo(X, c, pick.e, [d], d.dmg ? a : c, { hit: true });
      }
      decide(res);
      emit(X, { t: res.hit ? "hit" : "miss", actor: a.id, target: t.id, text: res.hit ? `Still a hit (${res.total} vs ${best(res.defs)}).` : `Now a miss (${res.total} vs ${best(res.defs)}).` });
    }
  }

  // ---------- resources ----------
  const bossOnce = (st, c, p) => c.boss && st.active === c.id && (["action", "bonus", "free"].includes(p.use) || !!(p.uses || p.cost || p.recharge));
  function canPay(F, c, e, cost, o) {
    o = o || {};
    const p = e.p;
    if (p.uses && !(c.uses[p.id] > 0)) return { ok: false, why: `${p.name}: no uses left` };
    if (p.recharge && !(c.uses[p.id] > 0)) return { ok: false, why: `${p.name}: not recharged` };
    if (p.recharge && c.boss && c.rechargeUsed[p.id] === F.state.round) return { ok: false, why: `${p.name}: already used this round (GM 3)` };
    // RULING R603 (designer-approved, GM 3 text to follow): a Boss can't use the same power on its turn and on its
    // half turn in the same round. Any power used while it is the active creature counts (card powers, deck powers,
    // own powers, limited triggers like Cleave); reactions on others' turns and free unlimited triggers don't. Uses
    // within one turn are limited only by the power.
    const tu = bossOnce(F.state, c, p) && c.turnUsed && c.turnUsed[p.id];
    if (tu && tu.round === F.state.round && tu.half !== !!c.turn.half) return { ok: false, why: `${p.name}: already used on its ${tu.half ? "half turn" : "turn"} this round` };
    const deck = deckOf(F, e);
    if (deck && cost > 0) {
      if (deck.kind === "spellbook") {
        if ((c.sp[e.deck] || 0) >= cost && o.pool !== "extra") return { ok: true, pool: "own" };
        if (c.extra.sp >= cost) return { ok: true, pool: "extra" };
        return { ok: false, why: `${p.name}: not enough spell points` };
      }
      if ((c.resolve[e.deck] || 0) >= cost && o.pool !== "extra") return { ok: true, pool: "own" };
      if (c.extra.resolve >= cost) return { ok: true, pool: "extra" };
      return { ok: false, why: `${p.name}: not enough Resolve` };
    }
    if (e.src === "item") {
      const it = c.items.find((i) => i.id === e.card);
      const cd = F.cards.cards[e.card];
      if (cd && ["Consumable", "Recipe"].includes(typeOf(cd)) && !(it && it.n > 0)) return { ok: false, why: `${cd.name}: none left` };
    }
    return { ok: true, pool: null };
  }
  // RULING R211: a cost is paid wholly from the deck's own pool, or wholly from the extra pool when the own pool
  // can't cover it (or the command says pool: "extra").
  function pay(X, c, e, cost, o) {
    const F = X.F, p = e.p, s = stat(X, c.id);
    const r = canPay(F, c, e, cost, o);
    if (p.uses) { c.uses[p.id]--; s.spent.uses++; emit(X, { t: "resource", actor: c.id, what: "uses", n: -1, power: p.id, text: `${c.name}: ${p.name} ${c.uses[p.id]} use(s) left.` }); }
    if (p.recharge) { c.uses[p.id] = 0; c.rechargeUsed[p.id] = X.st.round; }
    if (bossOnce(X.st, c, p)) (c.turnUsed = c.turnUsed || {})[p.id] = { round: X.st.round, half: !!c.turn.half };
    const deck = deckOf(F, e);
    if (deck && cost > 0) {
      const sp = deck.kind === "spellbook";
      if (r.pool === "extra") c.extra[sp ? "sp" : "resolve"] -= cost;
      else if (sp) c.sp[e.deck] -= cost;
      else { c.spentResolve[e.deck] = (c.spentResolve[e.deck] || 0) + cost; refreshPools(F, c); }
      s.spent[sp ? "sp" : "resolve"] += cost;
      emit(X, { t: "resource", actor: c.id, what: sp ? "sp" : "resolve", n: -cost, text: `${c.name} spends ${cost} ${sp ? "spell point" + (cost > 1 ? "s" : "") : "Resolve"}${r.pool === "extra" ? " (extra pool)" : ""}.` });
    }
    if (e.src === "item") {
      const cd = F.cards.cards[e.card], it = c.items.find((i) => i.id === e.card);
      if (cd && ["Consumable", "Recipe"].includes(typeOf(cd)) && it) {
        it.n--; s.spent.consumables++;
        // RULING R212: an empty Consumable stack leaves its Item Slot; a Recipe keeps its Slot at 0 flasks.
        if (it.n <= 0 && typeOf(cd) === "Consumable") c.items.splice(c.items.indexOf(it), 1);
        emit(X, { t: "resource", actor: c.id, what: "item", n: -1, card: e.card, text: `${c.name} uses ${cd.name} (${Math.max(0, it.n)} left).` });
      }
    }
  }
  function needsOk(F, c, e, why) {
    const p = e.p, deck = deckOf(F, e);
    const needs = (p.need || []).slice();
    if (deck && (deck.kind === "divine" || deck.kind === "glamour")) needs.push("voice");
    if (["Anthem", "Dirge", "Cue"].includes(p.kind)) needs.push("voice");
    for (const n of needs) {
      if (n === "voice" && !canSpeak(c)) return why ? `${p.name} needs your voice` : false;
      if (n === "shield" && !holdsShield(F, c)) return why ? `${p.name} needs a Shield in hand` : false;
      if (n === "emptyHand" && !freeHand(F, c)) return why ? `${p.name} needs an empty Hand` : false;
      if (n === "attackAction" && !c.turn.attackAction) return why ? `${p.name}: take the Attack action first` : false;
    }
    // P 10.7: no Divine, Glamour or Mend while shifted.
    if (c.form && (p.kind === "Mend" || (deck && (deck.kind === "divine" || deck.kind === "glamour")))) return why ? `${p.name}: not while shifted` : false;
    if (deck && deck.kind === "spellbook" && !canCastBook(F, c)) return why ? `${p.name} needs an empty Hand to hold the book` : false;
    return why ? null : true;
  }

  // ---------- damage, healing, death ----------
  // RULING R239: resistances and vulnerabilities come from build.resist / build.vuln (or a passive `resist`/`vuln`
  // list); Petrified resists everything (SPEC has no field for them).
  function hasResist(F, t, type) {
    if (has(t, "Petrified")) return true;
    return (t.build.resist || []).includes(type) || passives(F, t).some((e) => (e.p.resist || []).includes(type));
  }
  function hasVuln(F, t, type) { return (t.build.vuln || []).includes(type) || passives(F, t).some((e) => (e.p.vuln || []).includes(type)); }
  // o: { source, crit, melee }
  function applyDamage(X, t, n, type, o) {
    o = o || {};
    const F = X.F;
    if (t.dead || n <= 0) return 0;
    type = type || "Physical";
    let resisted = null;
    if (hasResist(F, t, type)) { n = Math.floor(n / 2); resisted = "resisted"; }
    if (hasVuln(F, t, type)) { n *= 2; resisted = resisted ? "both" : "vulnerable"; }
    const src = o.source ? X.st.creatures[o.source] : null;
    const total = n;
    if (src) stat(X, src.id).dmgDealt += n;
    stat(X, t.id).dmgTaken += n;
    emit(X, { t: "damage", actor: o.source || null, target: t.id, n, type, resisted, text: `${t.name} takes ${n} ${type}${resisted ? " (" + resisted + ")" : ""}.` });
    // hurt source of lasting effects (P 8)
    for (const c of Object.values(X.st.creatures)) for (const k of c.conds) if (k.lasting && k.source === t.id) k.hurt++;
    if (src && src.side !== t.side) for (const k of t.conds.slice()) if (k.lasting && k.subdue && k.name === "Charmed") removeCond(X, t, k, "harmed");
    if (t.form) {
      const take = Math.min(t.form.hp, n);
      t.form.hp -= take; n -= take;
      if (t.form.hp <= 0) revert(X, t, "its Form drops to 0 HP");
      if (n <= 0) return total;
    }
    if (t.temp > 0) { const take = Math.min(t.temp, n); t.temp -= take; n -= take; if (n <= 0) return total; }
    if (t.hp === 0) {
      if (n >= t.maxHp) { die_(X, t, "massive damage at 0 HP", o.source); return total; }
      t.death.fail += o.crit ? 2 : 1;
      emit(X, { t: "deathSave", target: t.id, ok: t.death.ok, fail: t.death.fail, text: `${t.name} takes damage at 0 HP: ${t.death.fail} failure(s).` });
      t.stable = false;
      if (t.death.fail >= 3) die_(X, t, "three failed death saves", o.source);
      return total;
    }
    t.hp -= n;
    if (t.hp <= 0) {
      const over = -t.hp;
      t.hp = 0;
      stat(X, t.id).downs++;
      // RULING R213: foes die at 0 HP unless their build sets `important: true` (GM 2.1 "you may let important
      // ones fall unconscious"); they then follow the Bearer rules.
      if (t.side === "foe" && !t.build.important) die_(X, t, "falls", o.source);
      else if (over >= t.maxHp) die_(X, t, "instant death", o.source);
      else {
        t.down = true; t.death = { ok: 0, fail: 0 }; t.stable = false;
        emit(X, { t: "down", actor: o.source || null, target: t.id, text: `${t.name} falls Unconscious.` });
        addCond(X, t, "Unconscious", { source: null });
        addCond(X, t, "Prone", { source: null });
      }
    }
    return total;
  }
  // RULING R235: the dead drop what they hold; dead bodies never block movement or end-of-move squares.
  function die_(X, t, why, source) {
    if (t.dead) return;
    t.dead = true; t.down = true; t.hp = 0;
    if (source && X.st.creatures[source] && source !== t.id) stat(X, source).kills++;
    emit(X, { t: "death", actor: source || null, target: t.id, text: `${t.name} dies (${why}).` });
    for (const k of t.conds.slice()) removeCond(X, t, k, null, true);
    t.mods = [];
    if (t.hands.length && !t.form) { for (const id of t.hands) X.st.ground.push({ card: id, pos: t.pos.slice(), owner: t.id }); t.hands = []; }
    sweep(X);
  }
  function heal(X, t, n, src) {
    if (t.dead || n <= 0) return 0;
    let got;
    // RULING R214: healing a shifted creature restores the Form's HP pool (its own HP waits, P 10.7).
    if (t.form) { got = Math.min(n, t.form.maxHp - t.form.hp); t.form.hp += got; }
    else {
      got = Math.min(n, t.maxHp - t.hp);
      const was0 = t.hp === 0;
      t.hp += got;
      if (was0 && got > 0) {
        t.down = false; t.stable = false; t.death = { ok: 0, fail: 0 };
        condsNamed(t, "Unconscious").forEach((k) => removeCond(X, t, k, "healed"));
      }
    }
    if (src) stat(X, src.id || src).healed += got;
    emit(X, { t: "heal", actor: src ? src.id || src : null, target: t.id, n: got, text: `${t.name} regains ${got} HP (${t.form ? t.form.hp + "/" + t.form.maxHp + " Form" : t.hp + "/" + t.maxHp}).` });
    return got;
  }
  function deathSave(X, c) {
    const r = die(X, 20, "death save");
    let text;
    if (r === 20) { c.hp = 0; heal(X, c, 1, null); text = "natural 20: regains 1 HP"; }
    else if (r === 1) { c.death.fail += 2; text = "natural 1: two failures"; }
    else if (r >= 10) { c.death.ok++; text = "success"; }
    else { c.death.fail++; text = "failure"; }
    emit(X, { t: "deathSave", actor: c.id, target: c.id, roll: r, ok: c.death.ok, fail: c.death.fail, text: `${c.name} death save: ${r}, ${text} (${c.death.ok} ✓ / ${c.death.fail} ✗).` });
    if (c.death.fail >= 3) die_(X, c, "three failed death saves");
    else if (c.death.ok >= 3) { c.stable = true; emit(X, { t: "stable", target: c.id, text: `${c.name} is stable.` }); }
  }

  // ---------- Forms ----------
  // RULING R403: shifting or reverting on your turn changes the movement you have left by the change in Speed
  // (ft already moved stay spent; a Dash keeps its bonus).
  function respeed(X, c, before) { if (X.st.active === c.id) c.turn.speed += speedOf(c) - before; }
  function shift(X, c, e) {
    const F = X.F, fm = e.p.form;
    const ft = formTotals(c.build, F.cards, fm);
    const probe = { size: ft.size, pos: c.pos };
    if (!fits(X.st, probe, c.pos, c.id)) fail(`No room for a ${ft.size} Form here`);
    const before = speedOf(c);
    c.form = { power: e.p.id, name: e.p.name, strip: clone(fm.strip), hp: ft.HP, maxHp: ft.HP, totals: ft, weapon: fm.weapon || null, fly: fm.fly || 0, climb: fm.climb || 0, until: { ev: "start", who: c.id, rounds: 600 } };
    c.totals = ft; c.size = ft.size;
    respeed(X, c, before);
    refreshPools(F, c);
    emit(X, { t: "shift", actor: c.id, power: e.p.id, text: `${c.name} shifts into ${e.p.name} (${ft.HP} HP, ${ft.size}).` });
  }
  function revert(X, c, why) {
    if (!c.form) return;
    const name = c.form.name;
    const before = speedOf(c);
    c.form = null; c.totals = c.own; c.size = c.own.size;
    respeed(X, c, before);
    refreshPools(X.F, c);
    emit(X, { t: "revert", actor: c.id, text: `${c.name} reverts from ${name}${why ? " (" + why + ")" : ""}.` });
  }

  // ---------- occupancy and movement ----------
  function occupants(st, c, pos) {
    const r = rectAt(c, pos);
    return living(st).filter((o) => o.id !== c.id && rectDist(r, rect(o)) === 0 && overlap(r, rect(o)));
  }
  function overlap(a, b) { return a.x0 <= b.x1 && b.x0 <= a.x1 && a.y0 <= b.y1 && b.y0 <= a.y1; }
  function fits(st, c, pos, selfId) {
    const r = rectAt(c, pos);
    for (const p of cellsOfRect(r)) if (isWall(st, p[0], p[1])) return false;
    return !living(st).some((o) => o.id !== selfId && overlap(r, rect(o)));
  }
  // RULING R230: a Form's Fly speed replaces its walking speed (no altitude) and ignores difficult terrain.
  const flying = (c) => c.form && c.form.fly > 0;
  function stepCost(st, c, pos, crawling, dragging) {
    let cost = 5;
    const cells = cellsOf(c, pos);
    const diff = (!flying(c) && cells.some((p) => isDifficult(st, p[0], p[1]))) || occupants(st, c, pos).length > 0;
    if (diff) cost += 5;
    if (crawling) cost += 5;
    if (dragging) cost += 5;
    return cost;
  }
  function grappledBy(st, c) { return living(st).filter((o) => condsNamed(o, "Grappled").some((k) => k.source === c.id)); }
  function planMove(F, c, cmd) {
    const st = F.state;
    if (st.active !== c.id) fail(`It isn't ${c.name}'s turn`);
    if (incap(c)) fail(`${c.name} is Incapacitated`);
    const safe = !!cmd.safe;
    if (!safe && c.turn.firstMover && c.turn.action) fail(c.turn.half ? "A half turn is movement or one action" : "First round: movement or action, not both");
    const path = cmd.path || [];
    const base = speedOf(c);
    let budget = safe ? c.turn.safeFt : c.turn.speed - c.turn.moved;
    let prone = has(c, "Prone"), standCost = 0;
    if (cmd.stand) {
      if (!prone) fail(`${c.name} isn't Prone`);
      if (base === 0) fail("Speed 0: can't stand up");
      standCost = base / 2; prone = false; // RULING R241: exactly half speed, no rounding (35 ft → 17.5 ft)
    }
    if (path.length && base === 0) fail(`${c.name}'s speed is 0`);
    // RULING R228: a grappler drags its grappled creatures into the square it leaves; +5 ft per square unless
    // they are two sizes smaller (P 6.10).
    const drag = grappledBy(st, c);
    const dragging = drag.some((g) => (SIZE_N[c.size] || 2) - (SIZE_N[g.size] || 2) < 2);
    // RULING R229: Frightened: no step may bring the creature closer to a fear source it can see.
    const fear = condsNamed(c, "Frightened").map((k) => st.creatures[k.source]).filter((s) => s && canSee(F, c, s));
    let pos = c.pos.slice(), cost = standCost;
    const steps = [], provokes = [];
    for (const q of path) {
      if (Math.max(Math.abs(q[0] - pos[0]), Math.abs(q[1] - pos[1])) !== 1) fail(`Path step ${q} isn't next to ${pos}`);
      for (const p of cellsOf(c, q)) if (isWall(st, p[0], p[1])) fail(`Square ${p} is blocked`);
      for (const o of occupants(st, c, q)) if (o.side !== c.side && sizeGap(o, c) < 2) fail(`${o.name}'s space blocks the way`);
      const from = pos;
      for (const s of fear) if (rectDist(rectAt(c, q), rect(s)) < rectDist(rectAt(c, from), rect(s))) fail(`${c.name} is Frightened and can't move closer to ${s.name}`);
      const sc = stepCost(st, c, q, prone, dragging);
      cost += sc;
      if (!safe && !c.turn.disengaged) {
        for (const e of living(st)) {
          if (e.side === c.side || incap(e) || e.turn.reaction || !canSee(F, e, c)) continue;
          const r = meleeReach(F, e);
          if (rectDist(rect(e), rectAt(c, from)) <= r && rectDist(rect(e), rectAt(c, q)) > r && !provokes.some((p) => p.enemy === e.id)) provokes.push({ step: steps.length, enemy: e.id });
        }
      }
      steps.push({ from, to: q.slice(), cost: sc });
      pos = q;
    }
    if (path.length && !fits(st, c, pos, c.id)) fail("Can't end the move in another creature's space");
    if (cost > budget) fail(`Needs ${cost} ft, ${budget} ft left`);
    return { steps, cost, standCost, provokes, left: budget - cost, safe };
  }
  function doMove(X, c, cmd) {
    const F = X.F, st = X.st;
    const plan = planMove(F, c, cmd);
    const spend = (n) => { if (plan.safe) c.turn.safeFt -= n; else c.turn.moved += n; };
    if (cmd.stand) { condsNamed(c, "Prone").forEach((k) => removeCond(X, c, k, "stands up")); spend(plan.standCost); }
    const start = c.pos.slice();
    for (const s of plan.steps) {
      // opportunity attacks from creatures whose reach it leaves now
      if (!plan.safe && !c.turn.disengaged) {
        for (const e of living(st)) {
          if (e.side === c.side || incap(e) || e.turn.reaction || !canSee(F, e, c)) continue;
          const r = meleeReach(F, e);
          if (rectDist(rect(e), rectAt(c, s.from)) <= r && rectDist(rect(e), rectAt(c, s.to)) > r) opportunity(X, e, c);
          if (c.dead || incap(c) || speedOf(c) === 0) break;
        }
        if (c.dead || incap(c) || speedOf(c) === 0) { emit(X, { t: "note", actor: c.id, text: `${c.name}'s movement stops.` }); break; }
      }
      const wasProne = has(c, "Prone");
      const zonesBefore = zonesAt(st, c);
      c.pos = s.to.slice();
      spend(s.cost);
      for (const g of grappledBy(st, c)) { if (fits(st, g, s.from, g.id)) g.pos = s.from.slice(); }
      for (const z of zonesAt(st, c)) if (!zonesBefore.includes(z) && (z.on || []).includes("enter")) triggerZone(X, z, c, "enters");
      sweep(X);
      // RULING R215: movement stops when a zone or reaction leaves the mover Prone, at speed 0 or down.
      if (c.dead || incap(c) || speedOf(c) === 0 || (!wasProne && has(c, "Prone"))) { emit(X, { t: "note", actor: c.id, text: `${c.name}'s movement stops.` }); break; }
    }
    if (plan.steps.length && c.turn.bonusMelee) { c.turn.bonusMelee = 0; emit(X, { t: "note", actor: c.id, text: `${c.name} moves: the extra attack is lost.` }); }
    if (plan.steps.length) emit(X, { t: "move", actor: c.id, from: start, to: c.pos.slice(), path: cmd.path, text: `${c.name} moves to ${c.pos.join(",")} (${plan.cost - plan.standCost} ft).` });
    if (!plan.safe) c.turn.moveUsed = true;
  }
  function opportunity(X, e, c) {
    const F = X.F;
    const ws = meleeWeapons(F, e);
    let w;
    if (e.react === "never") return;
    // RULING R240: "auto" opportunity attacks use the first melee weapon in hand (else unarmed / natural weapon).
    if (e.react === "auto") w = ws[0];
    else {
      const ch = ask(X, { kind: "reaction", text: `${c.name} leaves ${e.name}'s reach. Opportunity attack?`, trigger: { on: "leaveReach", actor: e.id, target: c.id },
        options: ws.map((id) => ({ actor: e.id, power: null, weapon: id, label: `${e.name}: ${weaponOf(F, e, id).name}` })) });
      if (ch == null) return;
      w = ws[ch];
    }
    e.turn.reaction = true;
    emit(X, { t: "reaction", actor: e.id, target: c.id, text: `${e.name} makes an opportunity attack.` });
    weaponAttack(X, e, c, weaponOf(F, e, w), { opportunity: true });
  }
  function zonesAt(st, c) { const ks = cellsOf(c).map((p) => key(p[0], p[1])); return st.zones.filter((z) => z.cells.some((k) => ks.includes(k))); }

  // ---------- weapon attacks ----------
  function weaponAttack(X, a, t, w, o) {
    const F = X.F;
    o = o || {};
    const info = attackInfo(F, a, t, { w, thrown: o.thrown, abil: o.abil });
    const res = rollAttack(X, a, t, info, { label: `${o.opportunity ? "opportunity attack" : "attacks"} with ${w.name}` });
    if (res.hit) hitReactions(X, res, info.melee);
    if (!res.hit) { emit(X, { t: "miss", actor: a.id, target: t.id, text: `${a.name} misses ${t.name}.` }); return res; }
    const crit = res.crit || (has(t, "Unconscious") && dist(a, t) <= 5);
    res.crit = crit;
    stat(X, a.id).hits++;
    if (crit) stat(X, a.id).crits++;
    emit(X, { t: crit ? "crit" : "hit", actor: a.id, target: t.id, text: `${a.name} ${crit ? "critically hits" : "hits"} ${t.name}.` });
    markSubdueHit(t);
    if (o.grapple || o.shove || o.escape) return res;
    const engagedNow = allyEngaged(X.st, a, t);
    // damage
    // riders come from the weapon card itself: a thrown weapon has already left the Hand (Pilum)
    const riders = w.card ? (F.cards.cards[w.card].fx || []).map((p) => ({ p, card: w.card, deck: null, src: "hand" })).filter((e) => e.p.use === "trigger" &&
      (e.p.on === "hit" || (e.p.on === "crit" && crit) || (e.p.on === "opportunity" && o.opportunity))) : [];
    const dice = w.two && otherHandEmpty(F, a, w) ? w.two : w.dice;
    const mod = a.totals[info.abil];
    const dmg = { parts: [{ dice, type: w.type || "Physical", extra: w.card || w.natural ? a.build.extraDice || 0 : 0 }],
      flat: o.offhand && mod > 0 ? 0 : mod, crit, type: w.type || "Physical" };
    for (const m of a.mods) if (m.kind === "dmg") { dmg.flat += m.n || 0; if (m.dice) dmg.parts.push({ dice: m.dice, type: dmg.type }); }
    for (const r of riders) if (!r.p.hook) for (const d of r.p.do || []) if (d.dmg) dmg.parts.push({ dice: d.dmg, type: d.type || dmg.type });
    runHooks(F, X, a, t, "modifyDamage", { damage: dmg, weapon: w, attack: info });
    // a rider hook may add damage too (Brace)
    for (const r of riders) { const h = r.p.hook && HOOKS[r.p.hook]; if (h && h.modifyDamage) h.modifyDamage(makeCtx(F, X, { actor: a, target: t, role: "attacker", power: r.p, entry: r, damage: dmg, weapon: w, attack: info, trigger: { on: r.p.on, attacker: a, target: t, hit: true, crit, weapon: w } })); }
    dealParts(X, a, t, dmg, info.melee);
    // weapon riders (non-damage), then triggers
    for (const r of riders) {
      if (r.p.hook) { const h = HOOKS[r.p.hook]; if (!h || h.onTrigger || !h.modifyDamage) hookTrigger(X, a, r, { on: r.p.on, attacker: a, target: t, hit: true, crit, weapon: w }); continue; }
      applyDo(X, a, r, (r.p.do || []).filter((d) => !d.dmg), t, { hit: true });
    }
    afterHit(X, a, t, { weapon: true, melee: info.melee, crit, engaged: engagedNow });
    return res;
  }
  // An area weapon attack (Sweeping Blow): one attack roll compared to each target's Defense, as an area roll (P 6.6:
  // no Outnumbered or target situations, no cover); one damage roll shared by all; half damage on a miss.
  // o: { label, attackAction: true (takes the Attack action: its triggers fire, no further attacks with it) }
  // RULING R600: a shared roll crits only on a natural 20 (an Unconscious target doesn't turn it into a crit); the
  // crit doubles the dice for every target. On a miss, half of the whole damage (the per-target bonuses too); weapon
  // riders and hit triggers (Crushing, weaponHit, meleeDrop) apply per target hit.
  function areaWeaponAttack(X, a, w, targets, o) {
    const F = X.F, st = X.st;
    o = o || {};
    targets = targets.filter((t) => !t.dead);
    if (o.attackAction) {
      a.turn.attackAction = true; a.turn.attacksLeft = 0;
      fireTriggers(X, a, "attackAction", { target: targets[0] });
    }
    if (!targets.length) { emit(X, { t: "note", actor: a.id, text: "No enemy within reach." }); return; }
    const res = rollAttack(X, a, null, attackInfo(F, a, targets[0], { w, area: true }), { label: o.label || `sweeps with ${w.name}` });
    const shared = {};
    const dice = w.two && otherHandEmpty(F, a, w) ? w.two : w.dice;
    for (const t of targets) {
      if (t.dead) continue;
      const info = attackInfo(F, a, t, { w, area: true });
      const r = Object.assign({}, res, { t, defs: info.defs });
      decide(r);
      if (r.hit) hitReactions(X, r, true);
      const crit = r.hit && r.crit;
      emit(X, { t: r.hit ? (crit ? "crit" : "hit") : "miss", actor: a.id, target: t.id, text: `${a.name} ${r.hit ? (crit ? "critically hits" : "hits") : "misses"} ${t.name} (${r.total} vs ${best(r.defs)})${r.hit ? "" : ": half damage"}.` });
      if (r.hit) { stat(X, a.id).hits++; markSubdueHit(t); if (crit) stat(X, a.id).crits++; }
      const engagedNow = r.hit && allyEngaged(st, a, t);
      const riders = r.hit && w.card ? (F.cards.cards[w.card].fx || []).map((p) => ({ p, card: w.card, deck: null, src: "hand" })).filter((e) => e.p.use === "trigger" &&
        (e.p.on === "hit" || (e.p.on === "crit" && crit))) : [];
      const dmg = { parts: [{ key: "w", dice, type: w.type || "Physical", extra: w.card || w.natural ? a.build.extraDice || 0 : 0 }],
        flat: a.totals[info.abil], crit, type: w.type || "Physical" };
      a.mods.forEach((m, i) => { if (m.kind === "dmg") { dmg.flat += m.n || 0; if (m.dice) dmg.parts.push({ key: "m" + i, dice: m.dice, type: dmg.type }); } });
      for (const rd of riders) if (!rd.p.hook) (rd.p.do || []).forEach((d, i) => { if (d.dmg) dmg.parts.push({ key: rd.p.id + i, dice: d.dmg, type: d.type || dmg.type }); });
      runHooks(F, X, a, t, "modifyDamage", { damage: dmg, weapon: w, attack: info });
      for (const rd of riders) { const h = rd.p.hook && HOOKS[rd.p.hook]; if (h && h.modifyDamage) h.modifyDamage(makeCtx(F, X, { actor: a, target: t, role: "attacker", power: rd.p, entry: rd, damage: dmg, weapon: w, attack: info, trigger: { on: rd.p.on, attacker: a, target: t, hit: true, crit, weapon: w } })); }
      dealParts(X, a, t, dmg, true, { shared, half: !r.hit });
      if (!r.hit) continue;
      for (const rd of riders) {
        if (rd.p.hook) { const h = HOOKS[rd.p.hook]; if (!h || h.onTrigger || !h.modifyDamage) hookTrigger(X, a, rd, { on: rd.p.on, attacker: a, target: t, hit: true, crit, weapon: w }); continue; }
        applyDo(X, a, rd, (rd.p.do || []).filter((d) => !d.dmg), t, { hit: true });
      }
      afterHit(X, a, t, { weapon: true, melee: true, crit, engaged: engagedNow });
    }
  }
  // RULING R233: a Versatile weapon uses its bigger die whenever the wielder's other Hand Slot is empty.
  function otherHandEmpty(F, a, w) { return !a.form && w.card && handsUsed(F, a) < a.build.slots.hand; }
  // o: { shared: {} rolls of the parts with a `key`, reused across targets (area weapon attack); half: true on a miss }
  function dealParts(X, a, t, dmg, melee, o) {
    o = o || {};
    let total = dmg.flat;
    const byType = {};
    for (const p of dmg.parts) {
      const keep = o.shared && p.key != null;
      const r = keep && o.shared[p.key] ? o.shared[p.key] : rollDice(X, p.dice, { crit: dmg.crit, extra: p.extra, mods: a.totals, why: "damage" });
      if (keep) o.shared[p.key] = r;
      if (p.type === dmg.type || !p.type) total += r.total; else byType[p.type] = (byType[p.type] || 0) + r.total;
    }
    const cut = (n) => Math.max(0, o.half ? Math.floor(n / 2) : n);
    applyDamage(X, t, cut(total), dmg.type, { source: a.id, crit: dmg.crit, melee });
    for (const [ty, n] of Object.entries(byType)) applyDamage(X, t, cut(n), ty, { source: a.id, crit: dmg.crit, melee });
  }
  // hitEngaged is judged when the hit lands, before damage.
  const allyEngaged = (st, a, t) => living(st).some((c) => c.side === a.side && c !== a && engaged(c, t));
  function markSubdueHit(t) { for (const k of t.conds) if (k.lasting && k.subdue) k.hits++; }
  // Triggers after a hit lands: meleeDrop, weaponHit, hitEngaged.
  function afterHit(X, a, t, o) {
    const st = X.st;
    if (o.weapon) fireTriggers(X, a, "weaponHit", { target: t });
    if (o.engaged) fireTriggers(X, a, "hitEngaged", { target: t });
    if (o.melee && (t.hp === 0 || t.dead)) fireTriggers(X, a, "meleeDrop", { target: t });
  }
  function fireTriggers(X, c, on, ctx) {
    const F = X.F;
    if (c.dead || incap(c)) return;
    for (const e of powersOf(F, c)) {
      const p = e.p;
      if (p.use !== "trigger" || p.on !== on) continue;
      if (!canPay(F, c, e, p.cost || 0).ok || !needsOk(F, c, e)) continue;
      const optional = p.uses || p.cost || p.recharge;
      // RULING R216: a trigger with limited uses or a cost is optional (react mode decides: ask prompts,
      // auto uses it, never skips); a free trigger always applies.
      if (optional) {
        if (c.react === "never") continue;
        if (c.react === "ask") {
          const ch = ask(X, { kind: "choice", text: `${c.name}: use ${p.name}?`, trigger: { on, actor: c.id, target: ctx.target && ctx.target.id }, options: [{ actor: c.id, power: p.id, label: `Use ${p.name}` }] });
          if (ch == null) continue;
        }
      }
      pay(X, c, e, p.cost || 0, {});
      emit(X, { t: "power", actor: c.id, power: p.id, target: ctx.target && ctx.target.id, text: `${c.name}: ${p.name}.` });
      if (p.hook) { hookTrigger(X, c, e, Object.assign({ on }, ctx)); continue; }
      for (const t of triggerTargets(X, c, e, ctx)) applyDo(X, c, e, p.do || [], t, { hit: true });
    }
  }
  function triggerTargets(X, c, e, ctx) {
    const p = e.p;
    if (p.target === "self") return [c];
    if (p.target === "allies" || p.target === "ally") return autoAllies(X.F, c, e, p.target === "ally" ? 1 : p.count);
    return ctx.target ? [ctx.target] : [c];
  }
  // RULING R217: "ally"/"allies" never include the user. When a trigger buffs allies, the nearest ones in reach
  // that can hear (not Deafened) are chosen automatically, up to `count`.
  function autoAllies(F, c, e, count) {
    const r = powerReach(F, c, e);
    const list = living(F.state).filter((o) => o.side === c.side && o !== c && dist(c, o) <= r && !has(o, "Deafened")).sort((x, y) => dist(c, x) - dist(c, y));
    return count ? list.slice(0, count) : list;
  }
  function hookTrigger(X, c, e, trig) {
    const h = HOOKS[e.p.hook];
    if (h && h.onTrigger) h.onTrigger(makeCtx(X.F, X, { actor: c, power: e.p, entry: e, trigger: trig, target: trig.target }));
    else emit(X, { t: "note", actor: c.id, power: e.p.id, text: `${cardName(X.F, e)}: not automated.` });
  }

  // ---------- effects ----------
  // Apply power effects `list` to target t. o: { hit, half, crit, rolled: {} shared rolls (area), level, darts }
  function applyDo(X, user, e, list, t, o) {
    o = o || {};
    const F = X.F, p = e ? e.p : {};
    for (let i = 0; i < list.length; i++) {
      const d = list[i];
      if (!o.hit && !(d.dmg && p.half)) continue;
      if (d.dmg) {
        let n;
        const shared = o.rolled && o.rolled[i];
        if (shared != null) n = shared;
        else {
          n = 0;
          for (let k = 0; k < (o.darts || 1); k++) n += rollDice(X, d.dmg, { crit: o.crit, mods: user.totals, why: "damage" }).total;
          if (o.rolled) o.rolled[i] = n;
        }
        if (!o.hit) n = Math.floor(n / 2);
        applyDamage(X, t, n, d.type || "Physical", { source: user.id, crit: o.crit });
        if (d.type === "Fire") burnZones(X, cellsOf(t));
      } else if (d.heal) heal(X, t, Math.max(0, rollDice(X, d.heal, { mods: user.totals, why: "healing" }).total), user);
      else if (d.temp) { const n = rollDice(X, d.temp, { mods: user.totals }).total; if (n > t.temp) { t.temp = n; emit(X, { t: "temp", target: t.id, n, text: `${t.name} has ${n} temporary HP.` }); } }
      else if (d.cond) {
        // RULING R238: a Lasting effect is Lasting on anyone it holds, allies and its own source included: maintain
        // rolls each turn, as for enemies (P 8 "holds a creature until it breaks free").
        const lasting = !!p.lasting;
        let until = d.until ? mkUntil(X, d.until, user, t, p) : null;
        if (!until && !lasting && p.dur && p.dur !== "instant") until = durUntil(p.dur, user);
        const flat = p.atk && p.atk.flat != null;
        addCond(X, t, d.cond, { source: user.id, until, lasting, subdue: lasting && !!p.subdue, abil: atkAbil(F, user, e) || "WIL", vs: p.atk ? p.atk.vs || "weapon" : null, flat, power: p.name });
      } else if (d.mod) {
        let until = null;
        if (d.until === "lasting") {
          // lasting mod (Bane): held by a Lasting effect record named after the power
          let k = t.conds.find((c) => c.effect && c.power === p.name && c.source === user.id);
          // RULING R500: another source's copy of the same power ends; the newest one holds.
          t.conds.filter((c) => c.effect && c.power === p.name && c !== k).forEach((c) => removeCond(X, t, c, "replaced"));
          if (!k) k = addCond(X, t, p.name, { source: user.id, lasting: true, subdue: !!p.subdue, abil: atkAbil(F, user, e) || "WIL", vs: p.atk ? p.atk.vs || "weapon" : null, flat: p.atk && p.atk.flat != null, power: p.name, effect: true });
          until = { lasting: k.id };
        } else if (d.until) until = mkUntil(X, d.until, user, t, p);
        if (d.mod === "roll" && !d.until) continue; // Cue roll changes are handled in cuePhase
        addMod(X, t, { kind: d.mod, n: d.n || 0, dice: d.dice || null, defs: d.defs || null, next: !!d.next, until, source: user.id, power: p.name || null,
          only: p.params && p.params.ranged ? "ranged" : p.params && p.params.melee ? "melee" : null });
      } else if (d.dash) { user.turn.speed += speedOf(user); emit(X, { t: "note", actor: user.id, text: `${user.name} dashes (+${speedOf(user)} ft).` }); }
      else if (d.move === "safe") {
        const ft = d.ft === "half" ? speedOf(user) / 2 : d.ft || 0;
        user.turn.safeFt += ft;
        emit(X, { t: "note", actor: user.id, text: `${user.name} may move ${ft} ft without provoking (move with safe: true).` });
      } else if (d.move === "teleport") {
        const pt = o.point;
        if (pt) { user.pos = pt.slice(); emit(X, { t: "move", actor: user.id, to: pt, teleport: true, text: `${user.name} teleports to ${pt.join(",")}.` }); sweep(X); }
      } else if (d.shove) {
        shoveAttack(X, user, t, o.mode || "push");
      } else if (d.attack) {
        // RULING R409: Cleave's attack is made at once: against another creature than the one that dropped,
        // before moving (moving forfeits it).
        user.turn.bonusMelee++; user.turn.extraNot = t ? t.id : null;
        emit(X, { t: "note", actor: user.id, text: `${user.name} may make one extra ${d.attack} attack.` });
      } else if (d.reroll) { /* Cues only */ }
    }
  }
  // RULING R402: fire burns a burning zone (Web) away one 5-ft square per round (zone.burnFt): the square of the
  // impact point or of the burned creature, else the first one the fire touches. A creature no longer standing in
  // any square of the zone is free of the effect it held.
  function burnZones(X, cells, center) {
    const ks = cells.map((p) => key(p[0], p[1]));
    if (center) ks.unshift(key(center[0], center[1]));
    for (const z of X.st.zones) {
      if (!z.burns) continue;
      if (!z.burnt || z.burnt.round !== X.st.round) z.burnt = { round: X.st.round, n: 0 };
      const cap = Math.max(1, Math.round((z.burnFt || 5) / 5));
      const gone = [];
      for (const k of ks) if (z.burnt.n + gone.length < cap && z.cells.includes(k) && !gone.includes(k)) gone.push(k);
      if (!gone.length) continue;
      z.burnt.n += gone.length;
      z.cells = z.cells.filter((k) => !gone.includes(k));
      emit(X, { t: "note", text: `Fire burns ${gone.length * 5} ft of ${z.name} away (${gone.join(" ")}).` });
      for (const c of living(X.st)) {
        if (cellsOf(c).some((p) => z.cells.includes(key(p[0], p[1])))) continue;
        for (const k of c.conds.slice()) if (k.source === z.source && k.power === z.name) removeCond(X, c, k, "the fire frees it");
      }
    }
    X.st.zones = X.st.zones.filter((z) => !z.burns || z.cells.length);
  }

  // ---------- areas ----------
  function areaCells(st, p, pt) {
    const out = [];
    if (!p.area) return out;
    if (p.area.shape === "cube") {
      // RULING R218: a cube of side N covers N/5 squares a side, centered on the chosen square (an even side
      // extends right and down: a 10-ft cube is the chosen square and the ones right, below and diagonal).
      const n = Math.max(1, Math.round(p.area.size / 5)), lo = Math.floor((n - 1) / 2);
      for (let y = pt[1] - lo; y < pt[1] - lo + n; y++) for (let x = pt[0] - lo; x < pt[0] - lo + n; x++) if (inBounds(st, x, y)) out.push([x, y]);
    } else {
      // sphere (and anything else round): every square within the radius of the chosen square (5-ft diagonals).
      const r = Math.round(p.area.size / 5);
      for (let y = pt[1] - r; y <= pt[1] + r; y++) for (let x = pt[0] - r; x <= pt[0] + r; x++) if (inBounds(st, x, y)) out.push([x, y]);
    }
    // full cover from the point blocks the area (P 10.5)
    return out.filter((c) => !isWall(st, c[0], c[1]) && (c[0] === pt[0] && c[1] === pt[1] || sightCells(st, [pt], [c], { [key(pt[0], pt[1])]: 1, [key(c[0], c[1])]: 1 }).los));
  }
  function inCells(c, cells) { const ks = cells.map((p) => key(p[0], p[1])); return cellsOf(c).some((p) => ks.includes(key(p[0], p[1]))); }

  // ---------- powers ----------
  function planPower(F, c, cmd) {
    const st = F.state;
    const e = findPower(F, c, cmd.power);
    if (!e) fail(`${c.name} can't use that power${c.form ? " while shifted" : ""}`);
    const p = e.p, deck = deckOf(F, e);
    if (!["action", "bonus", "free"].includes(p.use)) fail(`${p.name} is ${p.use === "passive" ? "always on" : "used when its trigger happens"}`);
    if (st.active !== c.id) fail(`It isn't ${c.name}'s turn`);
    if (incap(c)) fail(`${c.name} is Incapacitated`);
    if (p.use === "action" && !canAct(c)) fail(actionWhy(c));
    if (p.use === "bonus" && (c.turn.bonus || c.turn.half)) fail(c.turn.half ? "No bonus action on a half turn" : "Bonus action already used");
    let cost = p.cost || 0;
    if (deck && deck.kind === "spellbook" && p.kind === "Spell") {
      const lvl = cmd.level != null ? cmd.level : cost;
      if (lvl < cost) fail(`${p.name} is level ${cost}`);
      if (lvl > (deck.maxLevel || 6)) fail(`Max spell level ${deck.maxLevel}`);
      if (lvl >= 5 && c.highMagic[e.deck]) fail("High magic: one 5th or 6th level spell per long rest");
      cost = lvl;
      if (cost > 0 && c.spellTurn === st.turnNo) fail("One spell per turn (P 10.2)");
    }
    const pc = canPay(F, c, e, cost, { pool: cmd.pool });
    if (!pc.ok) fail(pc.why);
    const nw = needsOk(F, c, e, true);
    if (nw) fail(nw);
    const reach = powerReach(F, c, e);
    let targets = [], cells = null, point = cmd.point || null;
    const pick = (ids) => (ids || []).map((id) => { const t = st.creatures[id]; if (!t || t.dead) fail(`No creature ${id}`); return t; });
    const inReach = (t) => {
      if (dist(c, t) > reach) fail(`${t.name} is out of range (${reach} ft)`);
      if (t !== c && !sight(st, c, t).los) fail(`${t.name} has full cover`);
      if (condsNamed(c, "Charmed").some((k) => k.source === t.id) && (p.atk || (p.do || []).some((d) => d.dmg || d.cond))) fail(`${c.name} is Charmed by ${t.name}`);
    };
    const tg = p.target || (p.area ? "point" : "self");
    // a hook power may pick its own targets and add preview info (Sweeping Blow): plan(ctx) → error text | { targets, info }
    const hp = p.hook && HOOKS[p.hook] && HOOKS[p.hook].plan ? HOOKS[p.hook].plan(makeCtx(F, null, { actor: c, power: p, entry: e, cmd })) : null;
    if (typeof hp === "string") fail(hp);
    if (hp) targets = hp.targets;
    else if (tg === "self") targets = [c];
    else if (tg === "creature" || tg === "ally" || tg === "enemy") {
      targets = pick(cmd.targets && cmd.targets.slice(0, 1));
      if (!targets.length) fail("Pick a target");
      const t = targets[0];
      if (tg === "ally" && (t.side !== c.side || t === c)) fail("Pick an ally");
      if (tg === "enemy" && t.side === c.side) fail("Pick an enemy");
      inReach(t);
    } else if (tg === "allies" || tg === "enemies") {
      const pool = living(st).filter((o) => (tg === "allies" ? o.side === c.side && o !== c : o.side !== c.side) && dist(c, o) <= reach && (o === c || sight(st, c, o).los));
      if (cmd.targets && cmd.targets.length) { targets = pick(cmd.targets); targets.forEach((t) => { if (!pool.includes(t)) fail(`${t.name} isn't a valid target`); }); }
      else targets = pool.sort((x, y) => dist(c, x) - dist(c, y));
      if (p.count && targets.length > p.count) { if (cmd.targets && cmd.targets.length) fail(`At most ${p.count} targets`); targets = targets.slice(0, p.count); }
    } else if (tg === "darts") {
      const n = (p.count || 1) + (p.upcast && p.upcast.darts ? (cost - (p.cost || 0)) * p.upcast.darts : 0);
      targets = pick(cmd.targets);
      if (!targets.length) fail("Pick targets for the darts");
      if (targets.length > n) fail(`${n} darts`);
      targets.forEach(inReach);
    } else if (tg === "point") {
      if (!point) fail("Pick a point");
      if (distToCell(c, point) > reach) fail(`Point out of range (${reach} ft)`);
      if (!sightToCell(st, c, point).los) fail("No clear path to that point");
      cells = areaCells(st, p, point);
      targets = living(st).filter((o) => inCells(o, cells));
    }
    const tp = (p.do || []).find((d) => d.move === "teleport");
    if (tp) {
      if (!point) fail("Pick where to teleport");
      const ft = tp.ft === "half" ? speedOf(c) / 2 : tp.ft;
      if (distToCell(c, point) > ft) fail(`Teleport at most ${ft} ft`);
      if (!fits(st, c, point, c.id)) fail("That space isn't free");
      if (!canSeeCell(F, c, point)) fail("You must see the destination");
    }
    if (p.kind === "Form") {
      const ft = formTotals(c.build, F.cards, p.form);
      if (!fits(st, { size: ft.size, pos: c.pos }, c.pos, c.id)) fail(`No room for a ${ft.size} Form here`);
    }
    if ((p.do || []).some((d) => d.shove)) targets.forEach((t) => { if (sizeGap(t, c) > 1 && SIZE_N[t.size] > SIZE_N[c.size]) fail(`${t.name} is too big to shove`); });
    const info = { use: p.use, cost: cost ? `${cost} ${deck && deck.kind === "spellbook" ? "spell point" + (cost > 1 ? "s" : "") : "Resolve"}` : null,
      targets: targets.map((t) => t.id), range: reach, cells: cells ? cells.map((q) => key(q[0], q[1])) : null };
    if (hp && hp.info) Object.assign(info, hp.info);
    if (p.atk && targets.length) {
      const area = !!p.area || tg === "allies" || tg === "enemies";
      const first = attackInfo(F, c, targets[0], { entry: e, area });
      Object.assign(info, { toHit: first.bonus, dice: first.dice, adv: first.adv, dis: first.dis, why: first.why.concat(first.parts), vs: p.atk.vs || "weapon",
        defense: targets.length === 1 ? first.def : targets.map((t) => `${t.name} ${attackInfo(F, c, t, { entry: e, area }).def}`).join(", "),
        outnumbered: area ? null : first.outnumbered, cover: area ? null : first.cover });
    }
    const dm = (p.do || []).find((d) => d.dmg || d.heal);
    if (dm) info.damage = dm.dmg ? `${dm.dmg} ${dm.type || ""}`.trim() : `heal ${dm.heal}`;
    return { e, p, deck, cost, targets, cells, point, info, tg, pool: cmd.pool };
  }
  function canSeeCell(F, c, pt) {
    const st = F.state;
    if (has(c, "Blinded")) return false;
    if (!sightToCell(st, c, pt).los) return false;
    return !isDark(st, pt[0], pt[1]) || darkvision(F, c) >= distToCell(c, pt);
  }
  function doPower(X, c, cmd) {
    const F = X.F, st = X.st;
    const pl = planPower(F, c, cmd);
    const { e, p, deck, cost, targets } = pl;
    if (p.use === "action") useAction(c);
    if (p.use === "bonus") c.turn.bonus = true;
    pay(X, c, e, cost, { pool: pl.pool });
    if (deck && deck.kind === "spellbook" && p.kind === "Spell" && cost > 0) { c.spellTurn = st.turnNo; c.turn.spellCast = true; if (cost >= 5) c.highMagic[e.deck] = true; }
    emit(X, { t: "power", actor: c.id, power: p.id, targets: targets.map((t) => t.id), point: pl.point, level: cost, text: `${c.name} uses ${p.name}${targets.length && pl.tg !== "self" ? " on " + targets.map((t) => t.name).join(", ") : ""}.` });
    if (p.hook) {
      const h = HOOKS[p.hook];
      if (h && h.onUse) h.onUse(makeCtx(F, X, { actor: c, power: p, entry: e, targets, target: targets[0], point: pl.point, cmd }));
      else emit(X, { t: "note", actor: c.id, power: p.id, text: `${cardName(F, e)}: not automated.` });
      return;
    }
    if (p.kind === "Form") { shift(X, c, e); return; }
    if (p.zone) {
      const z = { id: "z" + st.nextId++, name: p.name, cells: pl.cells.map((q) => key(q[0], q[1])), power: p.id, source: c.id,
        until: durUntil(p.dur, c), terrain: p.zone.terrain || null, on: p.zone.on || [], burns: !!p.zone.burns, burnFt: p.zone.burnFt || 0,
        p: clone(p), entry: { card: e.card, deck: e.deck, src: e.src }, hitTurn: {} };
      st.zones.push(z);
    }
    const level = cost;
    if (!p.atk) {
      for (const t of targets) applyDo(X, c, e, p.do || [], t, { hit: true, point: pl.point, mode: cmd.mode, level });
      if (!targets.length) applyDo(X, c, e, (p.do || []).filter((d) => d.dash || d.move), c, { hit: true, point: pl.point });
      return;
    }
    // RULING R225: an attack power on "allies"/"enemies" without an area (Bellow: each enemy within 30 ft) rolls
    // once like an area (P 6.6). Darts roll once per target creature.
    const area = !!p.area || pl.tg === "allies" || pl.tg === "enemies";
    if (p.area && pl.cells && ((p.tags || []).includes("fire") || (p.do || []).some((d) => d.type === "Fire"))) burnZones(X, pl.cells, pl.point);
    if (area) {
      // P 6.6: one roll for every target; no Outnumbered or target situations.
      if (!targets.length) { emit(X, { t: "note", actor: c.id, text: "No creature in the area." }); return; }
      const info = attackInfo(F, c, targets[0], { entry: e, area: true });
      const res = rollAttack(X, c, null, info, { label: p.name });
      const rolled = {};
      for (const t of targets) {
        const ti = attackInfo(F, c, t, { entry: e, area: true });
        const r = Object.assign({}, res, { t, defs: ti.defs });
        decide(r);
        if (r.hit) hitReactions(X, r, false);
        emit(X, { t: r.hit ? (r.crit ? "crit" : "hit") : "miss", actor: c.id, target: t.id, text: `${p.name} ${r.hit ? "hits" : "misses"} ${t.name} (${r.total} vs ${best(r.defs)}).` });
        if (r.hit) { stat(X, c.id).hits++; markSubdueHit(t); if (r.crit) stat(X, c.id).crits++; }
        const eng = r.hit && allyEngaged(st, c, t);
        applyDo(X, c, e, p.do || [], t, { hit: r.hit, crit: r.crit, rolled, mode: cmd.mode });
        if (r.hit) afterHit(X, c, t, { engaged: eng });
      }
      return;
    }
    const counts = {};
    targets.forEach((t) => (counts[t.id] = (counts[t.id] || 0) + 1));
    for (const id of Object.keys(counts)) {
      const t = st.creatures[id];
      if (t.dead) continue;
      const info = attackInfo(F, c, t, { entry: e });
      const r = rollAttack(X, c, t, info, { label: p.name });
      if (r.hit) hitReactions(X, r, info.melee);
      const crit = r.hit && (r.crit || (has(t, "Unconscious") && dist(c, t) <= 5));
      emit(X, { t: r.hit ? (crit ? "crit" : "hit") : "miss", actor: c.id, target: t.id, text: `${p.name} ${r.hit ? (crit ? "critically hits" : "hits") : "misses"} ${t.name}.` });
      if (r.hit) { stat(X, c.id).hits++; markSubdueHit(t); if (crit) stat(X, c.id).crits++; }
      const eng = r.hit && allyEngaged(st, c, t);
      applyDo(X, c, e, p.do || [], t, { hit: r.hit, crit, darts: counts[id], mode: cmd.mode });
      // RULING R219: a power attack against "weapon" Defense within 5 ft (a foe's Bite) is a melee weapon attack
      // for triggers (weaponHit, hitEngaged, meleeDrop, Ring of Sparks).
      if (r.hit) afterHit(X, c, t, { weapon: info.vs === "weapon", melee: info.melee, engaged: eng });
    }
  }
  function triggerZone(X, z, t, why) {
    const st = X.st, F = X.F;
    // RULING R220: a zone attacks a creature at most once per turn (entering, then ending the turn there).
    if (z.hitTurn[t.id] === st.turnNo) return;
    z.hitTurn[t.id] = st.turnNo;
    // RULING R243: a zone keeps attacking with its source's current bonus, even while the source is down.
    const s = st.creatures[z.source];
    if (!s) return;
    const e = { p: z.p, card: z.entry.card, deck: z.entry.deck, src: z.entry.src };
    emit(X, { t: "power", actor: s.id, target: t.id, power: z.power, text: `${t.name} ${why} ${z.name}.` });
    if (!z.p.atk) { applyDo(X, s, e, z.p.do || [], t, { hit: true }); return; }
    const info = attackInfo(F, s, t, { entry: e, area: true, zone: true });
    const r = rollAttack(X, s, t, info, { label: z.name });
    if (r.hit) hitReactions(X, r, false);
    emit(X, { t: r.hit ? "hit" : "miss", actor: s.id, target: t.id, text: `${z.name} ${r.hit ? "catches" : "misses"} ${t.name}.` });
    if (r.hit) markSubdueHit(t);
    applyDo(X, s, e, z.p.do || [], t, { hit: r.hit, crit: r.crit });
  }

  // ---------- shove, grapple, escape ----------
  function shoveAttack(X, a, t, mode) {
    const F = X.F;
    const w = weaponOf(F, a, "unarmed");
    const res = weaponAttack(X, a, t, w, { shove: true });
    if (!res.hit) return;
    if (mode === "prone") { addCond(X, t, "Prone", { source: a.id }); return; }
    const ra = rect(a), rt = rect(t);
    const dx = rt.x0 > ra.x1 ? 1 : rt.x1 < ra.x0 ? -1 : 0, dy = rt.y0 > ra.y1 ? 1 : rt.y1 < ra.y0 ? -1 : 0;
    const to = [t.pos[0] + dx, t.pos[1] + dy];
    if ((dx || dy) && fits(X.st, t, to, t.id)) { t.pos = to; emit(X, { t: "move", actor: t.id, to, pushed: true, text: `${t.name} is pushed 5 ft.` }); sweep(X); }
    else emit(X, { t: "note", target: t.id, text: `${t.name} can't be pushed there.` });
  }

  // ---------- turns ----------
  const canAct = (c) => !c.turn.action && !incap(c) && !(c.turn.firstMover && c.turn.moveUsed);
  function actionWhy(c) {
    if (incap(c)) return `${c.name} is Incapacitated`;
    if (c.turn.action) return "Action already used";
    return c.turn.half ? "A half turn is movement or one action" : "First round: movement or action, not both (P 6.1)";
  }
  function useAction(c) { c.turn.action = true; }
  function startTurn(X, c, half) {
    const F = X.F, st = X.st;
    st.turnNo++;
    st.active = c.id; st.halfActive = !!half;
    // RULING R407: a Boss half turn isn't "your turn" for the reaction (P 6.2), Dodge ("until your next turn") or
    // Recharge 5–6 ("at the start of the monster's turn"): it keeps its spent reaction and its Dodge, and rolls no
    // Recharge.
    c.turn = freshTurn(half ? c.turn : { reaction: false, dodging: false });
    emit(X, { t: "turn", actor: c.id, half: !!half, text: `${c.name}${half ? " takes a half turn" : "'s turn"}.` });
    if (!half) tick(X, "start", c.id);
    let lose = false;
    if (c.hp === 0 && !c.dead && !c.stable && !c.form) deathSave(X, c);
    if (c.dead) return { lose: true };
    // Recharge 5–6 (GM 2.1)
    if (!half) for (const e of powerList(F.cards, c, true)) {
      if (e.p.recharge && !(c.uses[e.p.id] > 0)) {
        const r = die(X, 6, "recharge");
        if (r >= e.p.recharge) c.uses[e.p.id] = 1;
        emit(X, { t: "roll", actor: c.id, kind: "recharge", dice: [r], kept: r, bonus: 0, total: r, why: [], text: `${c.name} ${e.p.name} recharge: ${r}${r >= e.p.recharge ? ", ready" : ""}.` });
      }
    }
    // Lasting effects on c: first bite or maintain roll (P 8); Bosses also on their half turn.
    for (const k of c.conds.slice()) {
      if (!k.lasting || !c.conds.includes(k)) continue;
      if (k.subdue && k.bite) { k.bite = false; lose = true; emit(X, { t: "maintain", actor: k.source, target: c.id, text: `${c.name} loses this ${half ? "half " : ""}turn to ${k.power || k.name} (first bite).` }); continue; }
      if (half && !c.boss) continue;
      maintain(X, c, k);
    }
    sweep(X);
    if (c.form && c.form.until && !half) { c.form.until.rounds--; if (c.form.until.rounds <= 0) revert(X, c, "1 hour passes"); }
    c.turn.speed = speedOf(c);
    const fm = st.round === 1 && c.side === st.first && !st.ambush && !half;
    // RULING R227: a Boss half turn works like the first-mover rule (movement or one action) with no bonus action;
    // Duration and "until" timers ignore half turns, maintain rolls and first bite don't (P 8, GM 3).
    c.turn.firstMover = fm || !!half;
    c.turn.half = !!half;
    return { lose: lose || incap(c) };
  }
  function bareMods(F, c) {
    const base = coreStrip(c.build, F.cards), out = {};
    ABILS.forEach((a) => (out[a] = base ? base.strip[a] || 0 : c.totals[a]));
    if (c.form && c.form.strip) ["STR", "DEX"].forEach((a) => (out[a] = c.form.strip[a] || 0));
    return out;
  }
  function maintain(X, t, k) {
    const st = X.st, F = X.F, s = st.creatures[k.source];
    if (!s || s.dead || incap(s)) { removeCond(X, t, k, "its source can't hold it"); return; }
    const dis = k.hurt + k.hits + (k.subdue ? k.rolls : 0);
    // RULING R221: maintain rolls use the source's bare modifier for the effect's ability, with no Rank, gear or
    // Aspect bonus (P 8): its Core's (or foe body's), or its Form's STR and DEX while shifted. Foes and flat-bonus
    // effects use their highest bare modifier. Exhaustion applies; nothing else does.
    const bare = bareMods(F, s);
    const mod = s.side === "foe" || k.flat || !k.abil ? Math.max(...ABILS.map((a) => bare[a])) : bare[k.abil];
    const r = rollD20(X, 0, dis, "maintain");
    const total = r.kept + mod - 2 * (s.exhaustion || 0);
    const def = best(defsOf(F, t, k.vs || "weapon", {}));
    const ok = r.kept === 20 || (r.kept !== 1 && total >= def);
    emit(X, { t: "maintain", actor: s.id, target: t.id, dice: r.dice, kept: r.kept, bonus: mod, total, vs: def, dis, text: `${s.name} maintains ${k.power || k.name} on ${t.name}: ${r.dice.length > 1 ? "[" + r.dice.join(", ") + "] keeps " : ""}${r.kept} ${signed(mod)} = ${total} vs ${def}${dis ? " (" + dis + " disadvantage)" : ""}: ${ok ? "holds" : "breaks"}.` });
    k.rolls++; k.hurt = 0; k.hits = 0;
    if (!ok) removeCond(X, t, k, "breaks free");
  }
  function endTurn(X, c) {
    const st = X.st;
    const half = st.halfActive;
    if (!half) for (const z of zonesAt(st, c)) if ((z.on || []).includes("endTurn") && !c.dead) triggerZone(X, z, c, "ends its turn in");
    if (!half) tick(X, "end", c.id);
    for (const m of c.mods.slice()) if (m.until && m.until.ev === "end" && m.until.who === c.id && m.until.thisTurn) c.mods.splice(c.mods.indexOf(m), 1);
    emit(X, { t: "turn", actor: c.id, end: true, text: `${c.name} ends ${half ? "its half turn" : "its turn"}.` });
    st.active = null; st.halfActive = false;
    if (half) st.halfTurn[c.id] = true; else if (!st.done.includes(c.id)) st.done.push(c.id);
    advance(X);
  }
  function advance(X) {
    const st = X.st;
    if (st.phase !== "fight") return;
    const pending = living(st).filter((c) => c.side === st.side && !st.done.includes(c.id));
    if (pending.length) return;
    if (st.side === st.first) { st.side = other(st.first); st.done = []; if (!living(st).some((c) => c.side === st.side)) advance(X); return; }
    newRound(X);
  }
  function newRound(X) {
    const st = X.st;
    st.round++; st.side = st.first; st.done = [];
    for (const id of Object.keys(st.halfTurn)) st.halfTurn[id] = false;
    for (const c of living(st)) stat(X, c.id).roundsAlive++;
    emit(X, { t: "round", text: `Round ${st.round}.` });
    // RULING R404: a dead source takes no more turns, so each new round counts as its turn start and end for the
    // Durations and "until" timers it left (Bless, Grease, Help, Bellow's Frightened).
    for (const c of Object.values(st.creatures)) if (c.dead) { tick(X, "start", c.id); tick(X, "end", c.id); }
  }
  function sweep(X) {
    const st = X.st;
    for (const t of Object.values(st.creatures)) {
      if (t.dead) continue;
      for (const k of t.conds.slice()) {
        if (!t.conds.includes(k)) continue;
        const s = k.source && st.creatures[k.source];
        if (k.lasting && (!s || s.dead || incap(s))) removeCond(X, t, k, "its source can't hold it");
        // RULING R406: fear and charm need a living source (P 8 "while the source of fear is in sight").
        else if (["Frightened", "Charmed"].includes(k.name) && s && s.dead) removeCond(X, t, k, "its source is dead");
        else if (k.name === "Grappled" && s && (s.dead || incap(s) || dist(s, t) > 5)) removeCond(X, t, k, "grapple ends");
      }
      if (t.turn.dodging && (incap(t) || speedOf(t) === 0)) t.turn.dodging = false;
    }
  }
  function checkOver(X) {
    const st = X.st;
    if (st.phase !== "fight") return;
    const up = (side) => Object.values(st.creatures).some((c) => c.side === side && conscious(c));
    const pc = up("pc"), foe = up("foe");
    if (pc && foe) return;
    st.phase = "over"; st.winner = pc ? "pc" : foe ? "foe" : null; st.active = null;
    emit(X, { t: "over", winner: st.winner, text: st.winner ? `The fight is over: ${st.winner === "pc" ? "the Bearers" : "the foes"} win.` : "The fight is over: no one stands." });
  }

  // ---------- commands ----------
  function actor(F, cmd) {
    const c = F.state.creatures[cmd.actor];
    if (!c) fail(`No creature ${cmd.actor}`);
    return c;
  }
  function inFight(F) { if (F.state.phase !== "fight") fail(F.state.phase === "setup" ? "Roll initiative first (start)" : "The fight is over"); }
  function myTurn(F, c) { inFight(F); if (F.state.active !== c.id) fail(`It isn't ${c.name}'s turn`); if (c.dead) fail(`${c.name} is dead`); }

  // Attack slot: the Attack action (with its extra attacks) or an extra melee attack (Cleave).
  function planAttackSlot(F, c, cmd, melee) {
    if (incap(c)) fail(`${c.name} is Incapacitated`);
    if (cmd.offhand) {
      if (c.turn.bonus || c.turn.half) fail("Bonus action already used");
      if (!c.turn.lightWeapon) fail("Two-weapon fighting: attack with a Light weapon first (P 6.9)");
      return "offhand";
    }
    if (c.turn.attacksLeft > 0) return "attack";
    if (c.turn.bonusMelee > 0 && melee) return "extra";
    if (!canAct(c)) fail(actionWhy(c));
    return "action";
  }
  function attacksPerAction(F, c) { return Math.max(1, passiveMax(F, c, "attacks")); }
  function planAttack(F, c, cmd) {
    myTurn(F, c);
    const t = F.state.creatures[cmd.target];
    if (!t) fail("Pick a target");
    const w = weaponOf(F, c, cmd.weapon || "unarmed");
    const melee = !w.range && !cmd.thrown;
    const slot = planAttackSlot(F, c, cmd, melee);
    if (slot === "extra" && c.turn.extraNot === t.id) fail("The extra attack must target another creature");
    if (cmd.offhand) {
      if (!w.light || !w.card) fail("The off-hand weapon must be Light");
      if (w.card === c.turn.lightWeapon) fail("Use a different Light weapon in your other Hand");
    }
    if (w.loading && c.turn.loaded && slot !== "offhand") fail(`${w.name} is Loading: one shot per action`);
    const info = attackInfo(F, c, t, { w, thrown: cmd.thrown });
    const dice = w.two && otherHandEmpty(F, c, w) ? w.two : w.dice;
    const mod = c.totals[info.abil];
    info.damage = `${dice}${cmd.offhand && mod > 0 ? "" : mod ? signed(mod) : ""} ${w.type || "Physical"}`;
    info.toHit = info.bonus;
    info.defense = info.def;
    return { t, w, slot, info };
  }
  function doAttack(X, c, cmd) {
    const F = X.F, st = X.st;
    const { t, w, slot } = planAttack(F, c, cmd);
    if (slot === "action") {
      useAction(c); c.turn.attackAction = true; c.turn.attacksLeft = attacksPerAction(F, c);
      fireTriggers(X, c, "attackAction", { target: t });
    }
    if (slot === "action" || slot === "attack") c.turn.attacksLeft--;
    if (slot === "extra") c.turn.bonusMelee--;
    if (slot === "offhand") c.turn.bonus = true;
    if (w.loading && slot !== "offhand") c.turn.loaded = true;
    if (w.light && w.card && slot !== "offhand") c.turn.lightWeapon = w.card;
    // RULING R222: a thrown weapon lands in the target's square and leaves the Hand; Javelins are a bundle and
    // stay in hand (unlimited throws).
    if (cmd.thrown && w.card && !/javelin/i.test(w.name)) {
      c.hands.splice(c.hands.indexOf(w.card), 1);
      st.ground.push({ card: w.card, pos: t.pos.slice(), owner: c.id });
      retally(F, c);
    }
    let mod;
    if (slot === "offhand") mod = { offhand: true };
    weaponAttack(X, c, t, w, Object.assign({ thrown: cmd.thrown }, mod));
  }
  function planShove(F, c, cmd, kind) {
    myTurn(F, c);
    const t = F.state.creatures[cmd.target];
    if (!t || t.dead) fail("Pick a target");
    if (kind === "escape") {
      const k = condsNamed(c, "Grappled").find((k) => k.source === t.id);
      if (!k) fail(`${c.name} isn't grappled by ${t.name}`);
      if (!canAct(c)) fail(actionWhy(c));
      const info = attackInfo(F, c, t, { w: weaponOf(F, c, "unarmed"), abil: ["STR", "DEX"] });
      return { t, slot: "escapeAction", info: Object.assign(info, { toHit: info.bonus, defense: info.def }) };
    }
    const slot = planAttackSlot(F, c, cmd, true);
    if (slot === "offhand") fail("Shove and Grapple replace an attack of the Attack action");
    if (SIZE_N[t.size] - SIZE_N[c.size] > 1) fail(`${t.name} is more than one size larger`);
    if (kind === "grapple" && !freeHand(F, c)) fail("Grappling needs a free Hand");
    const info = attackInfo(F, c, t, { w: weaponOf(F, c, "unarmed") });
    return { t, slot, info: Object.assign(info, { toHit: info.bonus, defense: info.def }) };
  }
  function doShove(X, c, cmd, kind) {
    const F = X.F;
    const { t, slot } = planShove(F, c, cmd, kind);
    if (slot === "escapeAction") {
      useAction(c);
      const res = weaponAttack(X, c, t, weaponOf(F, c, "unarmed"), { escape: true, abil: ["STR", "DEX"] });
      if (res.hit) condsNamed(c, "Grappled").filter((k) => k.source === t.id).forEach((k) => removeCond(X, c, k, "escapes"));
      return;
    }
    if (slot === "action") { useAction(c); c.turn.attackAction = true; c.turn.attacksLeft = attacksPerAction(F, c); fireTriggers(X, c, "attackAction", { target: t }); }
    if (slot === "action" || slot === "attack") c.turn.attacksLeft--;
    if (slot === "extra") c.turn.bonusMelee--;
    if (kind === "shove") shoveAttack(X, c, t, cmd.mode || "push");
    else {
      const res = weaponAttack(X, c, t, weaponOf(F, c, "unarmed"), { grapple: true });
      if (res.hit) addCond(X, t, "Grappled", { source: c.id });
    }
  }
  function planAct(F, c, cmd) {
    myTurn(F, c);
    const a = cmd.action;
    if (a === "revert") { if (!c.form) fail(`${c.name} isn't shifted`); return { cost: "free" }; }
    if (a === "prone") { if (has(c, "Prone")) fail("Already Prone"); return { cost: "free" }; }
    if (incap(c)) fail(`${c.name} is Incapacitated`);
    if (a === "disengage") {
      const n = engagedEnemies(F.state, c).length;
      if (n >= 4) fail(`${c.name} is surrounded (${n} enemies engaged): can't Disengage`);
      const cost = n <= 1 ? "free" : n === 2 ? "bonus" : "action";
      if (cost === "bonus" && (c.turn.bonus || c.turn.half)) fail("Disengage costs a bonus action (2 enemies engaged): already used");
      if (cost === "action" && !canAct(c)) fail(actionWhy(c));
      return { cost, engaged: n };
    }
    if (a === "endCond") {
      // A condition that ends when its holder spends an action (Pierce: pull the pilum free).
      const k = c.conds.find((x) => x.id === cmd.cond && x.endAction);
      if (!k) fail("Nothing to end that way");
      if (!canAct(c)) fail(actionWhy(c));
      return { cost: "action", k };
    }
    if (!["dash", "dodge", "help"].includes(a)) fail(`Unknown action ${a}`);
    if (!canAct(c)) fail(actionWhy(c));
    if (a === "help") {
      const t = F.state.creatures[cmd.target];
      if (!t || t.dead || t.side !== c.side || t === c) fail("Help an ally");
      return { cost: "action", t };
    }
    return { cost: "action" };
  }
  function doAct(X, c, cmd) {
    const pl = planAct(X.F, c, cmd);
    if (pl.cost === "action") useAction(c);
    if (pl.cost === "bonus") c.turn.bonus = true;
    const a = cmd.action;
    if (a === "dash") { c.turn.speed += speedOf(c); emit(X, { t: "note", actor: c.id, text: `${c.name} dashes.` }); }
    else if (a === "disengage") { c.turn.disengaged = true; emit(X, { t: "note", actor: c.id, text: `${c.name} disengages (${pl.cost === "free" ? "free" : pl.cost}).` }); }
    else if (a === "dodge") { c.turn.dodging = true; emit(X, { t: "note", actor: c.id, text: `${c.name} dodges (+3 Defenses).` }); }
    else if (a === "help") {
      // RULING R237: Help is a +3 mod on the ally's next attack against a creature within 5 ft of the helper, until
      // the start of the helper's next turn.
      addMod(X, pl.t, { kind: "attack", n: 3, next: true, near: c.id, until: { ev: "start", who: c.id, skip: 0 }, source: c.id, power: "Help" });
    } else if (a === "endCond") removeCond(X, c, c.conds.find((x) => x.id === cmd.cond), pl.k.endAction.toLowerCase());
    else if (a === "revert") revert(X, c, null);
    else if (a === "prone") addCond(X, c, "Prone", { source: null });
  }
  function planInteract(F, c, cmd) {
    myTurn(F, c);
    if (c.form) fail("Your gear is merged into your Form");
    if ((cmd.draw || cmd.stow) && c.turn.interact) fail("Free object interaction already used");
    let hands = c.hands.slice();
    if (cmd.drop) { if (!hands.includes(cmd.drop)) fail("Not in hand"); hands.splice(hands.indexOf(cmd.drop), 1); }
    if (cmd.stow) { if (!hands.includes(cmd.stow)) fail("Not in hand"); hands.splice(hands.indexOf(cmd.stow), 1); }
    let from = null;
    if (cmd.draw) {
      if (c.carried.includes(cmd.draw)) from = "carried";
      else {
        const g = F.state.ground.find((g) => g.card === cmd.draw && distToCell(c, g.pos) <= 5);
        if (!g) fail("That weapon isn't carried or within 5 ft");
        from = "ground";
      }
      const cd = F.cards.cards[cmd.draw];
      const used = hands.reduce((n, id) => n + (F.cards.cards[id].atk && F.cards.cards[id].atk.twoHanded ? 2 : 1), 0);
      if (used + (cd.atk && cd.atk.twoHanded ? 2 : 1) > c.build.slots.hand) fail("No free Hand");
    }
    return { from };
  }
  function doInteract(X, c, cmd) {
    const st = X.st, F = X.F;
    const { from } = planInteract(F, c, cmd);
    const name = (id) => F.cards.cards[id].name;
    if (cmd.drop) { c.hands.splice(c.hands.indexOf(cmd.drop), 1); st.ground.push({ card: cmd.drop, pos: c.pos.slice(), owner: c.id }); emit(X, { t: "note", actor: c.id, text: `${c.name} drops ${name(cmd.drop)}.` }); }
    if (cmd.stow) { c.hands.splice(c.hands.indexOf(cmd.stow), 1); c.carried.push(cmd.stow); }
    if (cmd.draw) {
      if (from === "carried") c.carried.splice(c.carried.indexOf(cmd.draw), 1);
      else st.ground.splice(st.ground.findIndex((g) => g.card === cmd.draw && distToCell(c, g.pos) <= 5), 1);
      c.hands.push(cmd.draw);
    }
    if (cmd.draw || cmd.stow || cmd.drop) retally(F, c);
    if (cmd.draw || cmd.stow) c.turn.interact = true;
    if (cmd.draw || cmd.stow) emit(X, { t: "note", actor: c.id, text: `${c.name}${cmd.stow ? " stows " + name(cmd.stow) : ""}${cmd.stow && cmd.draw ? " and" : ""}${cmd.draw ? (from === "ground" ? " picks up " : " draws ") + name(cmd.draw) : ""}.` });
  }
  function doStart(X) {
    const st = X.st, F = X.F;
    if (st.phase !== "setup") fail("The fight has already started");
    const sides = ["pc", "foe"].filter((s) => living(st).some((c) => c.side === s));
    if (sides.length < 2) fail("Both sides need creatures");
    let r;
    for (let guard = 0; guard < 50; guard++) {
      r = {};
      for (const s of sides) {
        const m = living(st).filter((c) => c.side === s);
        const avg = Math.floor(m.reduce((n, c) => n + c.totals.DEX, 0) / m.length);
        const adv = m.every((c) => has(c, "Invisible")) ? 1 : 0, dis = st.surprise === s ? 1 : 0;
        const d = rollD20(X, adv, dis, "initiative");
        r[s] = d.kept + avg;
        emit(X, { t: "initiative", actor: s, dice: d.dice, kept: d.kept, bonus: avg, total: r[s], text: `Initiative (${s === "pc" ? "Bearers" : "foes"}): ${d.dice.length > 1 ? "[" + d.dice.join(", ") + "] keeps " : ""}${d.kept} ${signed(avg)} = ${r[s]}${dis ? " (surprised)" : ""}.` });
      }
      if (r.pc !== r.foe) break;
    }
    st.first = r.pc > r.foe ? "pc" : "foe";
    st.ambush = !!st.surprise && st.surprise !== st.first;
    st.phase = "fight"; st.round = 0;
    emit(X, { t: "initiative", winner: st.first, text: `Initiative: ${st.first === "pc" ? "the Bearers" : "the foes"} go first${st.ambush ? " (ambush: full turns)" : ""}.` });
    for (const c of living(st)) for (const e of powersOf(F, c)) if (e.p.use === "passive" && e.p.hook) {
      const h = HOOKS[e.p.hook];
      if (h && h.passive) h.passive(makeCtx(F, X, { actor: c, power: e.p, entry: e }));
      else if (!h) emit(X, { t: "note", actor: c.id, power: e.p.id, text: `${c.name}: ${cardName(F, e)}: not automated.` });
    }
    newRound(X);
  }
  function planBegin(F, c, cmd) {
    const st = F.state;
    inFight(F);
    if (st.active) fail(`${st.creatures[st.active].name} is acting`);
    if (c.dead) fail(`${c.name} is dead`);
    if (cmd.half) {
      if (!c.boss) fail("Only a Boss takes a half turn");
      if (c.side === st.side) fail("A Boss's half turn comes during the other side's turns (GM 3)");
      if (st.halfTurn[c.id]) fail("Half turn already used this round");
      // GM 3: between two characters' turns (with a single character left, any time on its side)
      if (!st.done.length && living(st).filter((o) => o.side === st.side).length > 1) fail("The half turn comes between two characters' turns: let one act first");
    } else {
      if (c.side !== st.side) fail(`It's the ${st.side === "pc" ? "Bearers'" : "foes'"} side`);
      if (st.done.includes(c.id)) fail(`${c.name} has already acted this round`);
    }
    return {};
  }
  // RULING R232: every living creature takes a turn, even at 0 HP (death save) or Incapacitated; those turns end
  // on their own. A side ends when all its living creatures have acted.
  function doBegin(X, c, cmd) {
    planBegin(X.F, c, cmd);
    const r = startTurn(X, c, !!cmd.half);
    if (r.lose && X.st.active === c.id) { emit(X, { t: "note", actor: c.id, text: `${c.name} can't act.` }); endTurn(X, c); }
  }
  function doAdjust(X, cmd) {
    const c = actor(X.F, cmd);
    const bits = [];
    if (cmd.hp != null) {
      const was = c.hp;
      c.hp = Math.max(0, Math.min(c.maxHp, cmd.hp));
      if (c.hp > 0 && c.down) { c.down = false; c.death = { ok: 0, fail: 0 }; condsNamed(c, "Unconscious").forEach((k) => removeCond(X, c, k)); }
      bits.push(`HP ${c.hp}`);
      // 0 HP by hand follows the usual rules: a foe dies (R213), anyone else falls Unconscious (P 7.4)
      if (c.hp === 0 && was > 0 && !c.dead) {
        if (c.side === "foe" && !c.build.important) die_(X, c, "adjusted to 0 HP");
        else { c.down = true; c.death = { ok: 0, fail: 0 }; c.stable = false; addCond(X, c, "Unconscious", { source: null }); addCond(X, c, "Prone", { source: null }); }
      }
    }
    if (cmd.temp != null) { c.temp = Math.max(0, cmd.temp); bits.push(`temp ${c.temp}`); }
    if (cmd.exhaustion != null) { c.exhaustion = Math.max(0, Math.min(6, cmd.exhaustion)); bits.push(`Exhaustion ${c.exhaustion}`); }
    if (cmd.remove === true && cmd.cond) { condsNamed(c, cmd.cond).forEach((k) => removeCond(X, c, k, "adjusted")); bits.push(`−${cmd.cond}`); }
    else if (cmd.cond) { addCond(X, c, cmd.cond, { source: cmd.source || null }); bits.push(`+${cmd.cond}`); }
    if (typeof cmd.remove === "string") { condsNamed(c, cmd.remove).forEach((k) => removeCond(X, c, k, "adjusted")); bits.push(`−${cmd.remove}`); }
    if (cmd.dead) { die_(X, c, "adjusted"); bits.push("dead"); }
    emit(X, { t: "adjust", actor: c.id, text: `Adjust (manual): ${c.name} ${bits.join(", ")}.` });
  }
  function exec(X, cmd) {
    const F = X.F;
    switch (cmd.type) {
      case "start": doStart(X); break;
      case "beginTurn": doBegin(X, actor(F, cmd), cmd); break;
      case "move": { const c = actor(F, cmd); myTurn(F, c); doMove(X, c, cmd); break; }
      case "attack": doAttack(X, actor(F, cmd), cmd); break;
      case "act": doAct(X, actor(F, cmd), cmd); break;
      case "shove": case "grapple": case "escape": doShove(X, actor(F, cmd), cmd, cmd.type); break;
      case "power": { const c = actor(F, cmd); myTurn(F, c); doPower(X, c, cmd); break; }
      case "interact": doInteract(X, actor(F, cmd), cmd); break;
      case "note": emit(X, { t: "note", actor: cmd.actor || null, text: `${cmd.actor ? nm(X, cmd.actor) + ": " : ""}${cmd.text || "(other action)"}` }); break;
      case "endTurn": { const c = actor(F, cmd); if (X.st.active !== c.id) fail(`It isn't ${c.name}'s turn`); endTurn(X, c); break; }
      case "adjust": doAdjust(X, cmd); break;
      default: fail(`Unknown command ${cmd.type}`);
    }
    sweep(X);
    checkOver(X);
    for (const c of Object.values(X.st.creatures)) X.st.stats[c.id].endHp = c.hp;
  }
  function planOf(F, cmd) {
    switch (cmd.type) {
      case "start": if (F.state.phase !== "setup") fail("Already started"); return {};
      case "beginTurn": return planBegin(F, actor(F, cmd), cmd);
      case "move": { const c = actor(F, cmd); myTurn(F, c); const p = planMove(F, c, cmd); return { cost: p.cost, left: p.left, provokes: p.provokes.map((x) => x.enemy) }; }
      case "attack": { const p = planAttack(F, actor(F, cmd), cmd); return previewInfo(p.info, p.slot); }
      case "act": return planAct(F, actor(F, cmd), cmd);
      case "shove": case "grapple": case "escape": { const p = planShove(F, actor(F, cmd), cmd, cmd.type); return previewInfo(p.info, p.slot); }
      case "power": { const c = actor(F, cmd); myTurn(F, c); return planPower(F, c, cmd).info; }
      case "interact": planInteract(F, actor(F, cmd), cmd); return {};
      case "endTurn": { const c = actor(F, cmd); if (F.state.active !== c.id) fail("Not this creature's turn"); return {}; }
      case "note": case "adjust": return {};
      default: fail(`Unknown command ${cmd.type}`);
    }
  }
  function previewInfo(i, slot) {
    return { toHit: i.bonus, abil: i.abil, defense: i.def, vs: i.vs === "weapon" ? "higher of STR/DEX" : i.vs, dice: i.dice, keep: i.keep, adv: i.adv, dis: i.dis,
      why: i.why.concat(i.parts), outnumbered: i.outnumbered, cover: i.cover, distance: i.distance, damage: i.damage, use: slot };
  }

  // ---------- Fight ----------
  function Fight(scenario, cards) {
    this.cards = cards;
    this.scenario = clone(scenario);
    this.events = [];
    this.commands = [];
    this.history = [];
    this.pending = null;
    this._pend = null;
    this.manual = false;
    initState(this, this.scenario);
  }
  Fight.prototype._run = function (cmd, answers, manual) {
    const snap = JSON.stringify(this.state);
    const X = { F: this, st: this.state, answers, i: 0, events: [], manual };
    try { exec(X, cmd); }
    catch (err) {
      this.state = JSON.parse(snap);
      if (err instanceof NeedInput) {
        this.pending = Object.assign({ id: `${this.commands.length}:${answers.length}`, options: [] }, err.prompt);
        this._pend = { cmd, answers, manual };
        return { ok: true, events: [], pending: this.pending };
      }
      this.pending = null; this._pend = null;
      if (err instanceof RuleError) return { ok: false, error: err.message, events: [] };
      // An engine bug: refuse the command rather than break the page; the state is untouched.
      if (typeof console !== "undefined") console.error(err);
      return { ok: false, error: "Engine error: " + err.message, events: [] };
    }
    this.pending = null; this._pend = null;
    this.history.push({ snap, nEvents: this.events.length });
    this.commands.push({ cmd: clone(cmd), answers: clone(answers), manual });
    this.events.push(...X.events);
    return { ok: true, events: X.events, pending: null };
  };
  Fight.prototype.do = function (cmd) {
    if (!cmd || !cmd.type) return { ok: false, error: "No command", events: [] };
    if (this.pending) {
      if (cmd.type !== "answer") return { ok: false, error: "Answer the pending prompt first", events: [], pending: this.pending };
      const p = this.pending;
      let a;
      if (p.kind === "roll") {
        const r = Math.round(Number(cmd.roll));
        if (!(r >= 1 && r <= p.sides)) return { ok: false, error: `Enter a number from 1 to ${p.sides}`, events: [], pending: p };
        a = { roll: r };
      } else {
        const ch = cmd.choice;
        if (ch != null && !(Number.isInteger(ch) && ch >= 0 && ch < p.options.length)) return { ok: false, error: "No such option", events: [], pending: p };
        a = { choice: ch == null ? null : ch };
      }
      const pend = this._pend;
      return this._run(pend.cmd, pend.answers.concat([a]), pend.manual);
    }
    if (cmd.type === "answer") return { ok: false, error: "Nothing to answer", events: [] };
    return this._run(clone(cmd), [], this.manual);
  };
  Fight.prototype.undo = function () {
    if (this.pending) { this.pending = null; this._pend = null; return true; }
    const h = this.history.pop();
    if (!h) return false;
    this.state = JSON.parse(h.snap);
    this.events.length = h.nEvents;
    this.commands.pop();
    return true;
  };
  Fight.prototype.setManualDice = function (on) { this.manual = !!on; };
  Fight.prototype.preview = function (cmd) {
    try { return { ok: true, error: null, info: planOf(this, cmd) || {} }; }
    catch (err) { if (err instanceof RuleError) return { ok: false, error: err.message, info: null }; throw err; }
  };
  Fight.prototype.legal = function (id) {
    const st = this.state, F = this, out = [];
    if (this.pending) return [{ type: "answer", label: "Answer the prompt" }];
    if (st.phase === "setup") return [{ type: "start", label: "Roll initiative" }];
    if (st.phase === "over") return [];
    const c = st.creatures[id];
    if (!c) return out;
    const ok = (cmd) => this.preview(cmd).ok;
    if (!st.active) {
      if (ok({ type: "beginTurn", actor: id })) out.push({ type: "beginTurn", actor: id, label: c.hp === 0 ? "Begin turn (death save)" : "Begin turn" });
      if (c.boss && ok({ type: "beginTurn", actor: id, half: true })) out.push({ type: "beginTurn", actor: id, half: true, label: "Boss half turn" });
      out.push({ type: "adjust", actor: id, label: "Adjust" });
      return out;
    }
    if (st.active !== id) return [{ type: "adjust", actor: id, label: "Adjust" }];
    if (c.dead) return [{ type: "endTurn", actor: id, label: "End turn" }];
    const foes = living(st).filter((o) => o.side !== c.side), all = living(st);
    const cands = (base, pool) => (pool || foes).filter((o) => ok(Object.assign({}, base, { target: o.id }))).map((o) => o.id);
    if (!incap(c) && speedOf(c) > 0 && c.turn.speed - c.turn.moved > 0 && !(c.turn.firstMover && c.turn.action)) out.push({ type: "move", actor: id, label: "Move", left: c.turn.speed - c.turn.moved });
    if (c.turn.safeFt > 0) out.push({ type: "move", actor: id, safe: true, label: `Move without provoking (${c.turn.safeFt} ft)` });
    if (has(c, "Prone") && ok({ type: "move", actor: id, stand: true, path: [] })) out.push({ type: "move", actor: id, stand: true, path: [], label: "Stand up" });
    const weapons = c.form ? ["natural"] : c.hands.filter((w) => F.cards.cards[w] && F.cards.cards[w].atk);
    for (const w of weapons.concat(c.form ? [] : ["unarmed", "improvised"])) {
      const name = w === "natural" ? c.form.weapon.name : w === "unarmed" ? "Unarmed strike" : w === "improvised" ? "Improvised weapon" : F.cards.cards[w].name;
      const base = { type: "attack", actor: id, weapon: w };
      const cs = cands(base);
      if (cs.length) out.push(Object.assign({ label: name, candidates: cs }, base));
      if (w !== "natural" && F.cards.cards[w] && F.cards.cards[w].atk && F.cards.cards[w].atk.thrown) {
        const cs2 = cands(Object.assign({ thrown: true }, base));
        if (cs2.length) out.push(Object.assign({ label: name + " (thrown)", candidates: cs2, thrown: true }, base));
      }
      if (c.turn.lightWeapon && !c.turn.bonus) {
        const cs3 = cands(Object.assign({ offhand: true }, base));
        if (cs3.length) out.push(Object.assign({ label: name + " (off-hand, bonus action)", candidates: cs3, offhand: true }, base));
      }
    }
    for (const a of ["dash", "disengage", "dodge"]) {
      if (a === "disengage" && !engagedEnemies(st, c).length) continue; // nothing to disengage from
      const pv = this.preview({ type: "act", actor: id, action: a }); if (pv.ok) out.push({ type: "act", actor: id, action: a, label: a[0].toUpperCase() + a.slice(1) + (pv.info.cost !== "action" ? ` (${pv.info.cost})` : "") }); }
    for (const k of c.conds) if (k.endAction && ok({ type: "act", actor: id, action: "endCond", cond: k.id })) out.push({ type: "act", actor: id, action: "endCond", cond: k.id, label: `${k.endAction} (action)` });
    const allies = all.filter((o) => o.side === c.side && o !== c);
    const hc = cands({ type: "act", actor: id, action: "help" }, allies);
    if (hc.length) out.push({ type: "act", actor: id, action: "help", label: "Help", candidates: hc });
    for (const [type, mode, label] of [["shove", "push", "Shove (push 5 ft)"], ["shove", "prone", "Shove (Prone)"], ["grapple", null, "Grapple"], ["escape", null, "Escape grapple"]]) {
      const base = { type, actor: id };
      if (mode) base.mode = mode;
      const cs = cands(base, type === "escape" ? all : foes);
      if (cs.length) out.push(Object.assign({ label, candidates: cs }, base));
    }
    for (const e of powersOf(F, c)) {
      const p = e.p;
      if (!["action", "bonus", "free"].includes(p.use)) continue;
      // probe with no targets: only the rule checks that don't depend on the target
      const pv = this.preview({ type: "power", actor: id, power: p.id, targets: [], point: null });
      if (!pv.ok && !/^(Pick|No clear|Point out)/.test(pv.error)) continue;
      const t = { type: "power", actor: id, power: p.id, label: p.name + (p.use === "bonus" ? " (bonus)" : "") };
      if (["creature", "ally", "enemy", "allies", "enemies", "darts"].includes(p.target)) {
        t.candidates = all.filter((o) => ok({ type: "power", actor: id, power: p.id, targets: [o.id] })).map((o) => o.id);
        if (!t.candidates.length && !["allies", "enemies"].includes(p.target)) continue;
      }
      out.push(t);
    }
    if (c.form) out.push({ type: "act", actor: id, action: "revert", label: "Revert (free)" });
    // RULING R242: carried weapons (Build.carried, SPEC 3) swap with the free object interaction, like a draw.
    if (!c.form && !c.turn.interact) {
      for (const w of c.carried) if (ok({ type: "interact", actor: id, draw: w })) out.push({ type: "interact", actor: id, draw: w, label: "Draw " + F.cards.cards[w].name });
      for (const w of c.carried) for (const h of c.hands) if (ok({ type: "interact", actor: id, draw: w, stow: h }) && !ok({ type: "interact", actor: id, draw: w })) out.push({ type: "interact", actor: id, draw: w, stow: h, label: `Swap ${F.cards.cards[h].name} for ${F.cards.cards[w].name}` });
      for (const g of st.ground) if (distToCell(c, g.pos) <= 5 && ok({ type: "interact", actor: id, draw: g.card })) out.push({ type: "interact", actor: id, draw: g.card, label: "Pick up " + F.cards.cards[g.card].name });
      for (const h of c.hands) out.push({ type: "interact", actor: id, stow: h, label: "Stow " + F.cards.cards[h].name });
    }
    if (!has(c, "Prone")) out.push({ type: "act", actor: id, action: "prone", label: "Drop prone (free)" });
    out.push({ type: "note", actor: id, label: "Other" }, { type: "endTurn", actor: id, label: "End turn" }, { type: "adjust", actor: id, label: "Adjust" });
    return out;
  };
  Fight.prototype.summary = function () {
    const st = this.state, out = { rounds: st.round, winner: st.winner, seed: st.rng.seed, creatures: {} };
    for (const [id, s] of Object.entries(st.stats)) out.creatures[id] = Object.assign(clone(s), { endHp: st.creatures[id] ? st.creatures[id].hp : 0 });
    return out;
  };
  Fight.prototype.summaryRows = function () { return summaryRows(this.summary()); };
  Fight.prototype.export = function () {
    return { version: 1, scenario: clone(this.scenario), commands: clone(this.commands), events: clone(this.events), summary: this.summary() };
  };
  const COLS = ["id", "name", "side", "dmgDealt", "dmgTaken", "healed", "attacks", "hits", "crits", "kills", "downs", "roundsAlive", "sp", "resolve", "uses", "consumables", "endHp"];
  function summaryRows(sum) {
    const rows = [COLS.slice()];
    for (const [id, s] of Object.entries(sum.creatures)) rows.push(COLS.map((k) => (k === "id" ? id : ["sp", "resolve", "uses", "consumables"].includes(k) ? s.spent[k] : s[k])));
    return rows;
  }
  function summaryCsv(sum) {
    return summaryRows(sum).map((r) => r.map((v) => { const s = String(v == null ? "" : v); return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; }).join(",")).join("\n") + "\n";
  }
  function createFight(scenario, cards) { return new Fight(scenario, cards); }
  function replay(exp, cards) {
    const f = createFight(exp.scenario, cards);
    for (const c of exp.commands || []) {
      const r = f._run(clone(c.cmd), clone(c.answers || []), !!c.manual);
      if (!r.ok || f.pending) throw new Error(`Replay failed at ${JSON.stringify(c.cmd)}: ${r.error || "needs more answers"}`);
    }
    return f;
  }

  return {
    version: 1, totals, validate, fromFoe, createFight, replay, summaryCsv, summaryRows,
    registerHook(name, h) { HOOKS[name] = h; },
    hooks: HOOKS,
    geometry: { dist, distToCell, sight, canSee: (f, a, b) => canSee(f, a, b), engaged, outnumbered, areaCells, cellsOf, inDark, lineCells },
    formTotals, parseDice,
  };
});
