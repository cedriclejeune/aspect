// DEV STUB: a crude fake of the SPEC section 4 engine API, so the UI can be built and screenshotted
// before sim/engine.js exists. Its rules are rough on purpose; never trust a number it gives.
(function () {
  "use strict";
  const ABIL = ["STR", "DEX", "INT", "WIL"];
  const ROWS = ["STR", "DEX", "INT", "WIL", "STRd", "DEXd", "INTd", "WILd", "HP", "SPD"];
  const clone = (o) => JSON.parse(JSON.stringify(o));
  const PENDING = { pending: true };

  function totals(build, cards) {
    const t = { STR: 0, DEX: 0, INT: 0, WIL: 0, STRd: 10, DEXd: 10, INTd: 10, WILd: 10, HP: 0, SPD: 30, size: "Medium", errors: [] };
    const core = build.core && cards.cards[build.core];
    if (core) { ROWS.forEach((k) => (t[k] = core.strip[k] || 0)); t.size = core.size || "Medium"; }
    else if (build.body) {
      ABIL.forEach((k) => { t[k] = build.body[k] || 0; t[k + "d"] = 10 + (build.body[k] || 0); });
      t.HP = build.body.HP || 0; t.SPD = build.body.SPD || 30; t.size = build.body.size || "Medium";
    } else t.errors.push("No Core or body");
    for (const id of equipped(build)) {
      const c = cards.cards[id];
      if (!c) { t.errors.push("Unknown card " + id); continue; }
      ROWS.forEach((k) => (t[k] += c.strip[k] || 0));
    }
    if (!build.armor) t.SPD += 10;
    ROWS.forEach((k) => (t[k] += (build.bonus || {})[k] || 0));
    return t;
  }

  function equipped(b) {
    return [b.armor, ...(b.hands || []), ...(b.jewelry || []), ...(b.items || []).map((i) => i.id), ...(b.aspects || [])].filter(Boolean);
  }

  function validate(build, cards) {
    const err = [], slots = Object.assign({ hand: 2, jewelry: 1, item: 2, aspect: 3 }, build.slots || {});
    const type = (id) => (cards.cards[id] || {}).type;
    const hands = (build.hands || []).reduce((n, id) => n + ((cards.cards[id] || {}).atk && cards.cards[id].atk.twoHanded ? 2 : 1), 0);
    if (hands > slots.hand) err.push(`Hands: ${hands} used, ${slots.hand} Slots`);
    if ((build.jewelry || []).length > slots.jewelry) err.push(`Jewelry: ${build.jewelry.length} cards, ${slots.jewelry} Slots`);
    if ((build.items || []).length > slots.item) err.push(`Items: ${build.items.length} stacks, ${slots.item} Slots`);
    if ((build.aspects || []).length > slots.aspect) err.push(`Aspects: ${build.aspects.length} cards, ${slots.aspect} Slots`);
    if (build.armor && type(build.armor) !== "Armor") err.push(`${build.armor} is not Armor`);
    const t = totals(build, cards);
    for (const id of equipped(build)) {
      const c = cards.cards[id];
      for (const [k, n] of Object.entries((c && c.req) || {}))
        if (t[k] - (c.strip[k] || 0) < n) err.push(`${c.name}: Req ${k} +${n} (you have ${t[k] - (c.strip[k] || 0)})`);
    }
    const ids = equipped(build).filter((id) => type(id) !== "Consumable");
    ids.forEach((id, i) => { if (ids.indexOf(id) !== i) err.push(`Two copies of ${cards.cards[id].name}`); });
    return err;
  }

  function fromFoe(foe, cards) {
    const b = { core: foe.core, body: foe.body ? clone(foe.body) : null, armor: null, hands: [], carried: [], jewelry: [], items: [], aspects: [],
      slots: { hand: 2, jewelry: 1, item: 2, aspect: 3 }, bonus: clone(foe.bonus || {}), extraDice: foe.extraDice || 0, ownFx: clone(foe.ownFx || []),
      powers: clone(foe.powers || []), boss: !!foe.boss, senses: clone(foe.senses || {}), alert: !!foe.alert, foe: foe.name };
    for (const id of foe.carries) {
      const c = cards.cards[id]; if (!c) continue;
      if (c.type === "Armor") b.armor = id;
      else if (["Weapon", "Shield", "Instrument"].includes(c.type)) {
        const used = b.hands.reduce((n, h) => n + (cards.cards[h].atk && cards.cards[h].atk.twoHanded ? 2 : 1), 0);
        if (used + (c.atk && c.atk.twoHanded ? 2 : 1) <= 2) b.hands.push(id); else b.carried.push(id);
      } else if (c.type === "Jewelry") b.jewelry.push(id);
      else if (c.kind === "aspect") b.aspects.push(id);
      else b.items.push({ id, n: 1 });
    }
    return b;
  }

  // ---------- fight ----------
  function Fight(scenario, cards) {
    this.cards = cards;
    this.scenario = clone(scenario);
    this.events = []; this.pending = null; this.manual = false;
    this.commands = []; this.undoStack = []; this.answers = []; this.cmd = null;
    const s = { round: 0, side: "pc", first: "pc", phase: "setup", winner: null, active: null, done: [], halfTurn: {},
      map: clone(scenario.map), surprise: scenario.surprise || null, zones: [], creatures: {}, rng: { seed: scenario.seed || 1, s: scenario.seed || 1 }, stats: {}, init: null };
    for (const c of scenario.creatures) {
      const t = totals(c.build, cards);
      const uses = {}, sp = {}, resolve = {};
      for (const id of equipped(c.build)) {
        const card = cards.cards[id];
        (card.fx || []).forEach((p) => { if (p.uses) uses[p.id] = parseInt(p.uses); });
        const deck = card.deck && cards.decks[card.deck];
        if (deck && deck.sp) sp[deck.cover] = deck.sp;
        if (deck && deck.resolve) resolve[deck.cover] = Math.max(1, deck.resolve + t.WIL);
      }
      s.creatures[c.id] = { id: c.id, side: c.side, name: c.name, pos: c.pos || [0, 0], size: t.size, totals: t, hp: t.HP, maxHp: t.HP, temp: 0,
        form: null, dead: false, down: false, stable: false, death: { ok: 0, fail: 0 }, conds: [], mods: [], turn: freshTurn(t),
        hands: clone(c.build.hands || []), carried: clone(c.build.carried || []), items: clone(c.build.items || []),
        uses, sp, resolve, extra: { sp: 0, resolve: 0 }, react: c.react || "ask", boss: !!c.build.boss, build: clone(c.build) };
      s.stats[c.id] = { dmgDealt: 0, dmgTaken: 0, healed: 0, attacks: 0, hits: 0, crits: 0, kills: 0, downs: 0, roundsAlive: 0,
        spent: { sp: 0, resolve: 0, uses: 0, consumables: 0 } };
    }
    this.state = s;
  }
  function freshTurn(t) {
    return { moved: 0, speed: t.SPD, action: false, bonus: false, reaction: false, interact: false, spellCast: false, disengaged: false, dodging: false, firstMover: false };
  }

  const P = Fight.prototype;
  P.setManualDice = function (on) { this.manual = !!on; };

  P.rand = function () {
    let t = (this.state.rng.s = (this.state.rng.s + 0x6d2b79f5) | 0);
    t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  P.die = function (n, why) {
    if (this.manual) {
      const a = this.ask({ kind: "roll", text: `Roll a d${n}` + (why ? ` (${why})` : ""), die: n, options: [] });
      return Math.max(1, Math.min(n, a.roll | 0));
    }
    return 1 + Math.floor(this.rand() * n);
  };
  P.dice = function (expr, c, crit) {
    let total = 0; const rolls = [];
    String(expr).replace(/\s/g, "").split(/(?=[+-])/).forEach((term) => {
      const sign = term[0] === "-" ? -1 : 1, body = term.replace(/^[+-]/, "");
      const m = body.match(/^(\d*)d(\d+)$/);
      if (m) for (let i = 0; i < (+m[1] || 1) * (crit ? 2 : 1); i++) { const r = this.die(+m[2], "damage"); rolls.push(r); total += sign * r; }
      else if (ABIL.includes(body)) total += sign * (c ? c.totals[body] : 0);
      else total += sign * (+body || 0);
    });
    return { total: Math.max(0, total), rolls };
  };
  P.ask = function (prompt) {
    if (this.answers.length > this.used) return this.answers[this.used++];
    prompt.id = "p" + (this.used + 1);
    this.pendingPrompt = prompt;
    throw PENDING;
  };
  P.emit = function (e) {
    e.round = this.state.round; this.out.push(e);
  };

  P.do = function (cmd) {
    if (this.pending && cmd.type !== "answer") return { ok: false, error: "Answer the prompt first", events: [] };
    if (cmd.type === "answer") {
      if (!this.pending) return { ok: false, error: "Nothing to answer", events: [] };
      this.answers.push(cmd);
      this.commands.push(cmd);
      return this.run(this.cmd);
    }
    const err = this.check(cmd);
    if (err) return { ok: false, error: err, events: [] };
    this.snap = { state: clone(this.state), events: this.events.length };
    this.answers = []; this.cmd = cmd;
    this.commands.push(cmd);
    return this.run(cmd);
  };
  P.run = function (cmd) {
    this.state = clone(this.snap.state); this.out = []; this.used = 0; this.pending = null;
    try { this.exec(cmd); } catch (e) {
      if (e !== PENDING) throw e;
      this.state = clone(this.snap.state);
      this.pending = this.pendingPrompt;
      return { ok: true, events: [], pending: this.pending };
    }
    this.events.push(...this.out);
    this.undoStack.push({ state: this.snap.state, events: this.snap.events, commands: this.commands.length - 1 - this.answers.length });
    this.cmd = null;
    return { ok: true, events: this.out };
  };
  P.undo = function () {
    if (this.pending) { this.state = clone(this.snap.state); this.pending = null; this.commands.length -= this.answers.length + 1; this.cmd = null; return true; }
    const u = this.undoStack.pop(); if (!u) return false;
    this.state = u.state; this.events.length = u.events; this.commands.length = u.commands;
    return true;
  };

  P.check = function (cmd) {
    const s = this.state, c = s.creatures[cmd.actor];
    if (cmd.type === "start") return s.phase === "setup" ? null : "Already started";
    if (cmd.type === "adjust") return c ? null : "No such creature";
    if (s.phase !== "fight") return "The fight hasn't started";
    if (cmd.type === "beginTurn") return s.active ? "Someone is already acting" : null;
    if (cmd.type === "move" || cmd.type === "attack" || cmd.type === "power") {
      if (s.active !== cmd.actor) return "Not this creature's turn";
      const r = this.preview(cmd); return r.ok ? null : r.error;
    }
    if (cmd.type !== "note" && s.active !== cmd.actor) return "Not this creature's turn";
    return null;
  };

  // ---------- geometry ----------
  const key = (p) => p[0] + "," + p[1];
  P.span = function (c) { return c.size === "Large" ? 2 : c.size === "Huge" ? 3 : 1; };
  P.cellsOf = function (c, pos) {
    const n = this.span(c), out = [], p = pos || c.pos;
    for (let dx = 0; dx < n; dx++) for (let dy = 0; dy < n; dy++) out.push([p[0] + dx, p[1] + dy]);
    return out;
  };
  P.dist = function (a, b, pa) {
    let best = 99;
    for (const p of this.cellsOf(a, pa)) for (const q of this.cellsOf(b)) best = Math.min(best, Math.max(Math.abs(p[0] - q[0]), Math.abs(p[1] - q[1])));
    return best * 5;
  };
  P.alive = function (c) { return !c.dead && !c.down; };
  P.foesOf = function (c) { return Object.values(this.state.creatures).filter((o) => o.side !== c.side && this.alive(o)); };
  P.engaged = function (a, b) { return this.alive(a) && this.alive(b) && this.dist(a, b) <= 5; };

  P.outnumbered = function (att, tgt) {
    const all = Object.values(this.state.creatures);
    const us = all.filter((o) => o.side === att.side && this.engaged(o, tgt));
    const them = all.filter((o) => o.side === tgt.side && all.some((e) => e.side === att.side && this.engaged(o, e)));
    return { us: us.map((o) => o.id), them: them.map((o) => o.id), n: us.length - them.length };
  };

  P.weapon = function (c, w) {
    if (w === "unarmed") return { name: "Unarmed strike", hit: 2, dice: "1", abil: ["STR"], type: "Physical" };
    if (w === "improvised") return { name: "Improvised weapon", hit: 0, dice: "1d4", abil: ["STR"], type: "Physical" };
    const card = this.cards.cards[w];
    return card && card.atk ? Object.assign({ name: card.name }, card.atk) : null;
  };
  P.attackInfo = function (c, t, wpn, thrown) {
    const abil = wpn.abil.reduce((a, k) => (c.totals[k] > c.totals[a] ? k : a), wpn.abil[0]);
    const mod = c.totals[abil];
    const ranged = !!(wpn.range || thrown);
    const d = this.dist(c, t);
    const reach = wpn.reach ? 10 : 5;
    const range = wpn.range || (thrown && wpn.thrown);
    if (!ranged && d > reach) return { ok: false, error: `Out of reach (${d} ft)` };
    if (ranged && d > range[1]) return { ok: false, error: `Beyond long range (${d} ft)` };
    const on = this.outnumbered(c, t), why = [];
    let adv = Math.max(0, on.n), dis = Math.max(0, -on.n);
    if (on.n) why.push(`Outnumbered ${on.us.length} vs ${on.them.length}`);
    if (ranged && d > range[0]) { dis++; why.push("long range"); }
    if (ranged && this.foesOf(c).some((o) => this.dist(c, o) <= 5)) { dis++; why.push("enemy within 5 ft"); }
    if (t.conds.some((x) => x.name === "Prone")) { adv++; why.push("target Prone (adv)"); }
    if (c.conds.some((x) => ["Prone", "Poisoned", "Restrained", "Blinded"].includes(x.name))) { dis++; why.push("attacker hampered"); }
    const cover = this.cellsOf(t).some((p) => this.state.map.cells[key(p)] === "cover") && d > 5 ? 2 : 0;
    const bonus = mod + wpn.hit + c.mods.filter((m) => m.kind === "attack").reduce((n, m) => n + (m.n || 0), 0);
    const def = Math.max(t.totals.STRd, t.totals.DEXd) + cover + (t.turn.dodging ? 3 : 0);
    const net = adv - dis;
    return { ok: true, info: { weapon: wpn.name, abil, toHit: bonus, defense: def, cover, distance: d,
      dice: net === 0 ? "1d20" : `${1 + Math.abs(net)}d20 keep ${net > 0 ? "highest" : "lowest"}`, adv, dis, why,
      outnumbered: { us: on.us.length, them: on.them.length }, damage: `${wpn.dice}${mod ? (mod > 0 ? "+" : "") + mod : ""}` } };
  };

  P.findPower = function (c, id) {
    const [src] = id.split("#");
    const card = this.cards.cards[src];
    const fx = card && (card.fx || []).find((p) => p.id === id);
    if (fx) return fx;
    const deck = this.cards.decks[src];
    if (deck) return deck.powers.find((p) => p.id === id);
    return (c.build.ownFx || []).find((p) => p.id === id);
  };
  P.areaCells = function (pw, pt) {
    const out = [], n = pw.area.size / 5;
    if (pw.area.shape === "cube") { for (let x = 0; x < n; x++) for (let y = 0; y < n; y++) out.push(key([pt[0] + x, pt[1] + y])); }
    else for (let x = -n; x <= n; x++) for (let y = -n; y <= n; y++) if (Math.max(Math.abs(x), Math.abs(y)) <= n) out.push(key([pt[0] + x, pt[1] + y]));
    return out;
  };

  P.preview = function (cmd) {
    const s = this.state, c = s.creatures[cmd.actor];
    if (!c) return { ok: false, error: "No actor" };
    if (cmd.type === "move") {
      const path = cmd.path || [];
      if (!path.length) return { ok: false, error: "Empty path" };
      let cost = 0, prev = c.pos;
      const oas = [];
      for (const p of path) {
        if (Math.max(Math.abs(p[0] - prev[0]), Math.abs(p[1] - prev[1])) !== 1) return { ok: false, error: "Path must go square by square" };
        const cell = s.map.cells[key(p)];
        if (cell === "wall") return { ok: false, error: "A wall blocks the path" };
        cost += cell === "difficult" || s.zones.some((z) => z.cells.includes(key(p))) ? 10 : 5;
        if (!c.turn.disengaged) for (const o of this.foesOf(c)) if (o.react !== "never" && !o.turn.reaction && this.dist(c, o, prev) <= 5 && this.dist(c, o, p) > 5 && !oas.includes(o.id)) oas.push(o.id);
        prev = p;
      }
      const left = c.turn.speed - c.turn.moved;
      if (cost > left) return { ok: false, error: `Costs ${cost} ft, ${left} ft left`, info: { cost, left } };
      return { ok: true, info: { cost, left: left - cost, provokes: oas.map((id) => s.creatures[id].name) } };
    }
    if (cmd.type === "attack" || cmd.type === "shove" || cmd.type === "grapple") {
      const t = s.creatures[cmd.target];
      if (!t) return { ok: false, error: "Pick a target" };
      if (t.side === c.side) return { ok: false, error: "That's an ally" };
      const w = cmd.type === "attack" ? this.weapon(c, cmd.weapon) : this.weapon(c, "unarmed");
      if (!w) return { ok: false, error: "Unknown weapon" };
      return this.attackInfo(c, t, w, cmd.thrown);
    }
    if (cmd.type === "power") {
      const pw = this.findPower(c, cmd.power);
      if (!pw) return { ok: false, error: "Unknown power" };
      const info = { power: pw.name, use: pw.use };
      if (pw.cost) info.cost = pw.cost + (pw.kind === "Spell" || pw.kind === "Cantrip" ? " spell points" : " Resolve");
      if (pw.target === "point") {
        if (!cmd.point) return { ok: false, error: "Pick a point", info };
        info.cells = this.areaCells(pw, cmd.point);
        info.targets = Object.values(s.creatures).filter((o) => this.cellsOf(o).some((p) => info.cells.includes(key(p)))).map((o) => o.name);
      } else if (["creature", "ally", "enemy", "darts"].includes(pw.target)) {
        if (!(cmd.targets || []).length) return { ok: false, error: "Pick a target", info };
        const t = s.creatures[cmd.targets[0]];
        info.distance = this.dist(c, t);
        if (pw.reach && info.distance > pw.reach) return { ok: false, error: `Out of range (${info.distance} ft > ${pw.reach} ft)`, info };
        if (pw.atk) { info.vs = pw.atk.vs + " Defense " + this.defVs(t, pw.atk.vs); info.toHit = this.powerBonus(c, pw); }
      }
      return { ok: true, info };
    }
    return { ok: true, info: {} };
  };
  P.defVs = function (t, vs) { return vs === "weapon" ? Math.max(t.totals.STRd, t.totals.DEXd) : t.totals[vs + "d"]; };
  P.powerBonus = function (c, pw) {
    if (pw.atk.flat != null) return pw.atk.flat;
    if (pw.atk.abil === "deck") { const deck = this.cards.decks[pw.id.split("#")[0]]; return (deck.kind === "spellbook" ? c.totals.INT : c.totals.WIL) + (deck.atk || 0); }
    return Math.max(...pw.atk.abil.map((k) => c.totals[k])) + (pw.atk.hit || 0);
  };

  P.legal = function (actorId) {
    const s = this.state, out = [];
    if (s.phase === "setup") return [{ type: "start", label: "Roll initiative" }];
    if (s.phase === "over") return [];
    const c = s.creatures[actorId];
    if (!c) return out;
    if (!s.active) {
      if (c.side === s.side && !s.done.includes(c.id) && !c.dead) out.push({ type: "beginTurn", actor: c.id, label: "Begin turn" });
      if (c.boss && c.side !== s.side && !s.halfTurn[c.id] && this.alive(c)) out.push({ type: "beginTurn", actor: c.id, half: true, label: "Boss half turn" });
      return out;
    }
    if (s.active !== c.id) return out;
    const t = c.turn;
    if (t.moved < t.speed) out.push({ type: "move", actor: c.id, label: "Move" });
    if (!t.action) {
      for (const w of c.hands) { const card = this.cards.cards[w]; if (card && card.atk) {
        out.push({ type: "attack", actor: c.id, weapon: w, label: card.name });
        if (card.atk.thrown) out.push({ type: "attack", actor: c.id, weapon: w, thrown: true, label: card.name + " (thrown)" });
      } }
      out.push({ type: "attack", actor: c.id, weapon: "unarmed", label: "Unarmed strike" });
      for (const a of ["dash", "disengage", "dodge", "help"]) out.push({ type: "act", actor: c.id, action: a, label: a[0].toUpperCase() + a.slice(1) });
      out.push({ type: "shove", actor: c.id, mode: "push", label: "Shove (push 5 ft)" }, { type: "shove", actor: c.id, mode: "prone", label: "Shove (Prone)" });
      out.push({ type: "grapple", actor: c.id, label: "Grapple" });
    }
    for (const pw of this.powersOf(c)) {
      if (pw.use === "passive" || pw.use === "reaction" || pw.use === "trigger") continue;
      if ((pw.use === "action" && t.action) || (pw.use === "bonus" && t.bonus)) continue;
      if (pw.uses && !(c.uses[pw.id] > 0)) continue;
      out.push({ type: "power", actor: c.id, power: pw.id, label: pw.name });
    }
    if (!t.interact) for (const w of c.carried) out.push({ type: "interact", actor: c.id, draw: w, stow: c.hands[0] || null, label: "Draw " + this.cards.cards[w].name });
    out.push({ type: "note", actor: c.id, label: "Other" }, { type: "endTurn", actor: c.id, label: "End turn" });
    return out;
  };
  P.powersOf = function (c) {
    const out = [];
    for (const id of equipped(c.build)) {
      const card = this.cards.cards[id];
      out.push(...(card.fx || []));
      const deck = card.deck && this.cards.decks[card.deck];
      if (deck) out.push(...deck.powers.filter((p) => !(c.build.powers || []).length || c.build.powers.includes(p.name)));
    }
    return out.concat(c.build.ownFx || []);
  };

  // ---------- resolution ----------
  P.exec = function (cmd) {
    const s = this.state, c = s.creatures[cmd.actor];
    switch (cmd.type) {
      case "start": {
        const avg = (side) => { const m = Object.values(s.creatures).filter((o) => o.side === side); return Math.floor(m.reduce((n, o) => n + o.totals.DEX, 0) / (m.length || 1)); };
        let a, b;
        do {
          a = this.d20(s.surprise === "pc" ? -1 : 0, "pc initiative") + avg("pc");
          b = this.d20(s.surprise === "foe" ? -1 : 0, "foe initiative") + avg("foe");
        } while (a === b);
        s.first = s.side = a > b ? "pc" : "foe"; s.phase = "fight"; s.round = 1; s.init = { pc: a, foe: b };
        this.emit({ t: "initiative", text: `Initiative: characters ${a}, foes ${b}. ${a > b ? "Characters" : "Foes"} go first.`, pc: a, foe: b });
        this.emit({ t: "round", text: `Round 1 — ${s.side === "pc" ? "characters" : "foes"}' side` });
        break;
      }
      case "beginTurn": {
        s.active = c.id;
        if (!cmd.half) c.turn = freshTurn(c.totals);
        c.turn.half = !!cmd.half;
        if (cmd.half) s.halfTurn[c.id] = true;
        c.mods = c.mods.filter((m) => m.until !== "startSourceTurn");
        this.emit({ t: "turn", actor: c.id, text: `${c.name} begins ${cmd.half ? "a half turn" : "its turn"}.` });
        break;
      }
      case "move": {
        const pv = this.preview(cmd);
        const oas = Object.values(s.creatures).filter((o) => pv.info.provokes.includes(o.name));
        for (const o of oas) {
          if (o.react === "ask") {
            const a = this.ask({ kind: "reaction", text: `${c.name} leaves ${o.name}'s reach. Opportunity attack?`, trigger: { t: "leave", actor: c.id },
              options: [{ actor: o.id, power: "opportunity", label: `${o.name}: opportunity attack` }] });
            if (a.choice == null) continue;
          }
          o.turn.reaction = true;
          this.emit({ t: "reaction", actor: o.id, target: c.id, text: `${o.name} makes an opportunity attack.` });
          this.strike(o, c, this.weapon(o, o.hands.find((w) => this.weapon(o, w)) || "unarmed"));
        }
        c.turn.moved += pv.info.cost; c.pos = cmd.path[cmd.path.length - 1];
        this.emit({ t: "move", actor: c.id, text: `${c.name} moves ${pv.info.cost} ft.`, path: cmd.path });
        break;
      }
      case "attack": {
        const t = s.creatures[cmd.target];
        if (cmd.offhand) c.turn.bonus = true; else c.turn.action = true;
        this.strike(c, t, this.weapon(c, cmd.weapon), cmd.thrown);
        if (cmd.thrown) { c.hands = c.hands.filter((w) => w !== cmd.weapon); }
        break;
      }
      case "shove": case "grapple": {
        const t = s.creatures[cmd.target]; c.turn.action = true;
        const r = this.strike(c, t, this.weapon(c, "unarmed"), false, true);
        if (r && cmd.type === "grapple") this.addCond(t, "Grappled", c.id);
        else if (r && cmd.mode === "prone") this.addCond(t, "Prone", c.id);
        else if (r) this.emit({ t: "shift", actor: c.id, target: t.id, text: `${t.name} is pushed 5 ft.` });
        break;
      }
      case "act": {
        c.turn.action = true;
        if (cmd.action === "dash") c.turn.speed += c.totals.SPD;
        if (cmd.action === "disengage") c.turn.disengaged = true;
        if (cmd.action === "dodge") c.turn.dodging = true;
        this.emit({ t: "note", actor: c.id, text: `${c.name} takes the ${cmd.action[0].toUpperCase() + cmd.action.slice(1)} action.` });
        break;
      }
      case "power": this.usePower(c, cmd); break;
      case "interact": {
        c.turn.interact = true;
        c.carried = c.carried.filter((w) => w !== cmd.draw);
        if (cmd.stow) { c.hands = c.hands.filter((w) => w !== cmd.stow); c.carried.push(cmd.stow); }
        c.hands.push(cmd.draw);
        this.emit({ t: "note", actor: c.id, text: `${c.name} draws ${this.cards.cards[cmd.draw].name}.` });
        break;
      }
      case "note": this.emit({ t: "note", actor: cmd.actor, text: `${c ? c.name + ": " : ""}${cmd.text || "(other action)"}` }); break;
      case "endTurn": {
        s.active = null;
        if (!c.turn.half) s.done.push(c.id);
        this.emit({ t: "turn", actor: c.id, text: `${c.name} ends ${c.turn.half ? "its half turn" : "its turn"}.` });
        const left = Object.values(s.creatures).filter((o) => o.side === s.side && !o.dead && !s.done.includes(o.id));
        if (!left.length) {
          if (s.side !== s.first) { s.round++; s.halfTurn = {}; Object.values(s.creatures).forEach((o) => { if (!o.dead) s.stats[o.id].roundsAlive++; }); }
          s.side = s.side === "pc" ? "foe" : "pc"; s.done = [];
          this.emit({ t: "round", text: `Round ${s.round} — ${s.side === "pc" ? "characters" : "foes"}' side` });
        }
        break;
      }
      case "adjust": {
        if (cmd.hp != null) { c.hp = Math.max(0, Math.min(c.maxHp, cmd.hp)); c.down = c.hp === 0; }
        if (cmd.cond && !cmd.remove) this.addCond(c, cmd.cond, null);
        if (cmd.cond && cmd.remove) c.conds = c.conds.filter((x) => x.name !== cmd.cond);
        this.emit({ t: "adjust", actor: c.id, text: `Adjust ${c.name}: ${cmd.hp != null ? "HP " + c.hp : ""}${cmd.cond ? (cmd.remove ? " −" : " +") + cmd.cond : ""}` });
        break;
      }
    }
    this.checkOver();
  };

  P.d20 = function (adv, why) {
    const n = 1 + Math.abs(adv), dice = [];
    for (let i = 0; i < n; i++) dice.push(this.die(20, why));
    return adv >= 0 ? Math.max(...dice) : Math.min(...dice);
  };
  P.strike = function (c, t, wpn, thrown, noDamage) {
    const pv = this.attackInfo(c, t, wpn, thrown);
    if (!pv.ok) { this.emit({ t: "note", actor: c.id, text: `${c.name} can't attack: ${pv.error}` }); return false; }
    const i = pv.info, net = i.adv - i.dis, dice = [];
    for (let k = 0; k < 1 + Math.abs(net); k++) dice.push(this.die(20, "attack"));
    const kept = net >= 0 ? Math.max(...dice) : Math.min(...dice);
    const total = kept + i.toHit;
    let def = i.defense;
    const st = this.state.stats;
    st[c.id].attacks++;
    this.emit({ t: "roll", actor: c.id, target: t.id, dice, kept, bonus: i.toHit, total, vs: def, adv: i.adv, dis: i.dis, why: i.why,
      text: `${c.name} attacks ${t.name} with ${wpn.name}: ${total} vs Defense ${def}.` });
    let hit = kept === 20 || (kept !== 1 && total >= def);
    if (hit && kept !== 20) {
      const opts = this.powersOf(t).filter((p) => p.use === "reaction" && p.on === "hitSelf" && !t.turn.reaction && (!p.uses || t.uses[p.id] > 0));
      if (opts.length && t.react !== "never") {
        let pick = null;
        if (t.react === "ask") {
          const a = this.ask({ kind: "reaction", text: `${c.name} hits ${t.name} (${total} vs ${def}). Use a reaction?`, trigger: { t: "hitSelf", actor: c.id, target: t.id },
            options: opts.map((p) => ({ actor: t.id, power: p.id, label: `${t.name}: ${p.name}` })) });
          pick = a.choice == null ? null : opts[a.choice];
        } else if (total < def + 2) pick = opts[0];
        if (pick) {
          t.turn.reaction = true; if (pick.uses) { t.uses[pick.id]--; st[t.id].spent.uses++; }
          def += (pick.do[0] && pick.do[0].n) || 0;
          this.emit({ t: "reaction", actor: t.id, text: `${t.name} uses ${pick.name}: Defense ${def}.` });
          hit = total >= def;
        }
      }
    }
    if (!hit) { this.emit({ t: "miss", actor: c.id, target: t.id, text: `Miss.` }); return false; }
    const crit = kept === 20;
    st[c.id].hits++; if (crit) st[c.id].crits++;
    this.emit({ t: crit ? "crit" : "hit", actor: c.id, target: t.id, text: crit ? "Critical hit!" : "Hit." });
    if (noDamage) return true;
    const mod = c.totals[i.abil];
    const r = this.dice(wpn.dice, c, crit);
    this.damage(c, t, Math.max(0, r.total + mod), wpn.type, r.rolls);
    return true;
  };
  P.damage = function (c, t, n, type, rolls) {
    const st = this.state.stats;
    t.hp = Math.max(0, t.hp - n);
    st[c.id].dmgDealt += n; st[t.id].dmgTaken += n;
    this.emit({ t: "damage", actor: c.id, target: t.id, n, type, dice: rolls, text: `${t.name} takes ${n} ${type} (${t.hp}/${t.maxHp} HP).` });
    if (t.hp === 0 && !t.down) {
      if (t.side === "foe") { t.dead = true; st[c.id].kills++; this.emit({ t: "death", target: t.id, text: `${t.name} dies.` }); }
      else { t.down = true; st[c.id].downs++; this.addCond(t, "Unconscious", null); this.emit({ t: "down", target: t.id, text: `${t.name} falls unconscious.` }); }
    }
  };
  P.addCond = function (t, name, src) {
    if (t.conds.some((x) => x.name === name)) return;
    t.conds.push({ name, source: src, until: null, lasting: false, subdue: false, rolls: 0, hurt: 0 });
    this.emit({ t: "cond", target: t.id, cond: name, text: `${t.name} is ${name}.` });
  };
  P.usePower = function (c, cmd) {
    const pw = this.findPower(c, cmd.power), s = this.state, st = s.stats[c.id];
    if (pw.use === "action") c.turn.action = true;
    if (pw.use === "bonus") c.turn.bonus = true;
    if (pw.uses) { c.uses[pw.id]--; st.spent.uses++; }
    const deck = this.cards.decks[pw.id.split("#")[0]];
    if (pw.cost && deck) {
      const pool = deck.sp ? c.sp : c.resolve;
      pool[deck.cover] -= pw.cost; deck.sp ? (st.spent.sp += pw.cost) : (st.spent.resolve += pw.cost);
      this.emit({ t: "resource", actor: c.id, what: deck.sp ? "sp" : "resolve", n: -pw.cost, text: `${c.name} spends ${pw.cost} ${deck.sp ? "spell points" : "Resolve"}.` });
    }
    this.emit({ t: "power", actor: c.id, power: pw.id, text: `${c.name} uses ${pw.name}.` });
    let targets = (cmd.targets || []).map((id) => s.creatures[id]);
    if (pw.target === "self") targets = [c];
    if (pw.target === "point" && cmd.point) { const cells = this.areaCells(pw, cmd.point); targets = Object.values(s.creatures).filter((o) => this.alive(o) && this.cellsOf(o).some((p) => cells.includes(key(p)))); }
    if (pw.zone && cmd.point) s.zones.push({ id: "z" + (s.zones.length + 1), cells: this.areaCells(pw, cmd.point), power: pw.id, source: c.id, until: pw.dur || null });
    const roll = pw.atk ? this.d20(0, pw.name) : 0;
    for (const t of targets) {
      let hit = true;
      if (pw.atk) {
        const total = roll + this.powerBonus(c, pw), def = this.defVs(t, pw.atk.vs);
        hit = roll === 20 || (roll !== 1 && total >= def);
        this.emit({ t: "roll", actor: c.id, target: t.id, dice: [roll], kept: roll, bonus: this.powerBonus(c, pw), total, vs: def, why: [], text: `${pw.name} vs ${t.name}: ${total} vs ${pw.atk.vs} Defense ${def} — ${hit ? "hit" : "miss"}.` });
      }
      for (const e of pw.do || []) {
        if (e.dmg && (hit || pw.half)) { const r = this.dice(e.dmg, c); this.damage(c, t, hit ? r.total : Math.floor(r.total / 2), e.type, r.rolls); }
        if (e.heal) { const r = this.dice(e.heal, c); const n = Math.min(r.total, t.maxHp - t.hp); t.hp += n; if (t.hp > 0) { t.down = false; t.conds = t.conds.filter((x) => x.name !== "Unconscious"); } st.healed += n;
          this.emit({ t: "heal", actor: c.id, target: t.id, n, text: `${t.name} regains ${n} HP (${t.hp}/${t.maxHp}).` }); }
        if (e.cond && hit) this.addCond(t, e.cond, c.id);
        if (e.mod && hit) { t.mods.push({ kind: e.mod, n: e.n || 0, dice: e.dice || null, next: !!e.next, until: e.until || null, source: c.id, power: pw.id });
          this.emit({ t: "note", target: t.id, text: `${t.name}: ${e.mod} ${e.n ? (e.n > 0 ? "+" : "") + e.n : e.dice}.` }); }
        if (e.dash) c.turn.speed += c.totals.SPD;
      }
    }
    if (pw.form) { c.form = { power: pw.id, hp: pw.form.strip.HP, maxHp: pw.form.strip.HP, totals: pw.form.strip }; this.emit({ t: "shift", actor: c.id, text: `${c.name} shifts into ${pw.name} form.` }); }
  };
  P.checkOver = function () {
    const s = this.state;
    if (s.phase !== "fight") return;
    const up = (side) => Object.values(s.creatures).some((o) => o.side === side && this.alive(o));
    if (!up("pc") || !up("foe")) {
      s.phase = "over"; s.winner = up("pc") ? "pc" : up("foe") ? "foe" : null; s.active = null;
      this.emit({ t: "over", text: `The fight is over: ${s.winner === "pc" ? "the characters win" : s.winner === "foe" ? "the foes win" : "no one stands"}.` });
    }
  };

  P.summary = function () {
    const s = this.state, creatures = {};
    for (const c of Object.values(s.creatures)) creatures[c.id] = Object.assign({ name: c.name, side: c.side }, clone(s.stats[c.id]), { endHp: c.hp });
    return { rounds: s.round, winner: s.winner, seed: this.scenario.seed, creatures };
  };
  P.export = function () { return { scenario: clone(this.scenario), commands: clone(this.commands), events: clone(this.events), summary: this.summary() }; };

  function replay(exp, cards) {
    const f = new Fight(exp.scenario, cards);
    for (const cmd of exp.commands) f.do(cmd);
    return f;
  }

  globalThis.BearersEngine = { stub: true, totals, validate, fromFoe, createFight: (sc, cards) => new Fight(sc, cards), replay };
})();
