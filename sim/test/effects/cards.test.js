// Card-effect tests on the real sim/cards.js (agent D): one test per card with combat mechanics and per deck
// power or Form. Each uses the card through f.do commands, as the UI does, and checks the printed numbers.
// Loaded by sim/test/run.js: module.exports(T, H) registers the tests with the runner's helpers.
"use strict";
module.exports = function register(T, H) {
  const { Eng, eq, ok, run, refused, start, C, evs } = H;
  const CARDS = () => H.cards();
  const B = (o) => Object.assign({ body: { STR: 3, DEX: 1, INT: 0, WIL: 0, HP: 14, SPD: 30 }, armor: null, hands: [], carried: [], jewelry: [], items: [], aspects: [] }, o);
  const pc = (id, pos, build, o) => Object.assign({ id, side: "pc", name: id, pos, build: B(build), react: "ask" }, o);
  const foe = (id, pos, build, o) => Object.assign({ id, side: "foe", name: id, pos, build: B(build), react: "never" }, o);
  const tmpl = (id, name, pos, o) => Object.assign({ id, side: "foe", name: id, pos, build: Eng.fromFoe(CARDS().foes.find((f) => f.name === name), CARDS()), react: "never" }, o);
  const fight = (cs, o) => { o = o || {}; return Eng.createFight({ version: 1, name: "fx", seed: 3, map: { w: o.w || 30, h: o.h || 14, cells: o.cells || {} }, surprise: null, creatures: cs }, CARDS()); };
  const skip = (f, id, script, endScript) => { run(f, { type: "beginTurn", actor: id }, script); if (f.state.active === id) run(f, { type: "endTurn", actor: id }, endScript); };
  const go = (f, id, script) => run(f, { type: "beginTurn", actor: id }, script);
  const end = (f, id, script) => run(f, { type: "endTurn", actor: id }, script);
  // Foes go first; every foe skips its turn, then `id` (a pc) begins a full turn.
  const pcTurn = (f, id) => { start(f, "foe"); for (const c of Object.values(f.state.creatures)) if (c.side === "foe" && !c.dead) skip(f, c.id); go(f, id); };
  // pcs go first and skip; then foe `id` begins.
  const foeTurn = (f, id) => { start(f); for (const c of Object.values(f.state.creatures)) if (c.side === "pc" && !c.dead) skip(f, c.id); go(f, id); };
  const has = (c, name) => c.conds.some((k) => k.name === name);
  const pv = (f, cmd) => { const r = f.preview(cmd); ok(r.ok, `preview refused ${JSON.stringify(cmd)}: ${r.error}`); return r.info; };
  const tpl = (f, id, pred) => f.legal(id).find(pred);
  const power = (f, actor, pid, o) => Object.assign({ type: "power", actor, power: pid }, o);
  const atk = (actor, weapon, target, o) => Object.assign({ type: "attack", actor, weapon, target }, o);
  const dmgs = (r) => evs(r, "damage").map((e) => e.n);

  // ---------- strip-only cards ----------
  T("[fx] Leather, Mail, Plate, Shield, Wiry, Sellsword, Acrobat: tally card; a dropped Shield stops counting", () => {
    const t = (b) => Eng.totals(B(b), CARDS());
    const l = t({ armor: "A-I-01" }); eq([l.STRd, l.DEXd, l.SPD], [15, 12, 35]);
    eq(t({ armor: "A-I-02" }).STRd, 16);
    const p = t({ armor: "A-II-01", aspects: ["T-II-04"] }); eq([p.STRd, p.SPD], [13 + 4 + 1, 20], "Plate: Req STR +2 met by Brute STR 3");
    const w = t({ aspects: ["T-II-02", "T-II-05"] }); eq([w.STR, w.STRd, w.SPD, w.DEX, w.DEXd], [4, 14, 45, 2, 12]);
    const f = fight([pc("a", [5, 5], { hands: ["W-I-05", "S-I-01"] }), foe("x", [6, 5], { hands: ["W-I-05"] })]);
    eq([C(f, "a").totals.STRd, C(f, "a").totals.DEXd], [15, 13]);
    pcTurn(f, "a");
    eq(pv(f, atk("a", "W-I-05", "x")).damage, "1d8+3 Physical", "Shield in the other Hand: no Versatile die");
    run(f, { type: "interact", actor: "a", drop: "S-I-01" });
    eq([C(f, "a").totals.STRd, C(f, "a").totals.DEXd], [13, 11]);
    eq(pv(f, atk("a", "W-I-05", "x")).damage, "1d10+3 Physical");
    run(f, { type: "interact", actor: "a", draw: "S-I-01" });
    eq(C(f, "a").totals.STRd, 15, "picked up again");
  });

  // ---------- weapon riders ----------
  T("[fx] Finesse Blade Sap: −2 on the target's next attack, spent by it or gone at the start of your next turn", () => {
    const f = fight([pc("a", [5, 5], { body: { STR: 0, DEX: 3, INT: 1, WIL: 0, HP: 11, SPD: 35 }, hands: ["W-I-04"] }), foe("x", [6, 5], { hands: ["W-I-05"] })]);
    pcTurn(f, "a");
    eq(pv(f, atk("a", "W-I-04", "x")).toHit, 5, "DEX 3 (Finesse) + 2");
    const r = run(f, atk("a", "W-I-04", "x"), [8, 4]); // 13 vs 13
    eq(dmgs(r), [7], "1d6 + DEX");
    end(f, "a");
    go(f, "x");
    eq(pv(f, atk("x", "W-I-05", "a")).toHit, 3, "Brute STR 3 + 2 − 2");
    run(f, atk("x", "W-I-05", "a"), [1]);
    ok(!C(f, "x").mods.length, "spent by the attack");
    // unused: gone when a's next turn starts
    const g = fight([pc("a", [5, 5], { body: { STR: 0, DEX: 3, INT: 1, WIL: 0, HP: 11, SPD: 35 }, hands: ["W-I-04"] }), foe("x", [6, 5], { hands: ["W-I-05"] })]);
    pcTurn(g, "a");
    run(g, atk("a", "W-I-04", "x"), [15, 1]);
    end(g, "a");
    skip(g, "x");
    ok(C(g, "x").mods.length === 1, "still there after x's turn without attacking");
    go(g, "a");
    ok(!C(g, "x").mods.length, "ends at the start of a's next turn");
  });

  T("[fx] Greatclub Crushing and Ogre Giant Strength: +60 HP, the extra die on the Javelins only; a crit knocks Prone", () => {
    const f = fight([pc("a", [5, 5]), tmpl("o", "Ogre", [6, 5])]);
    eq([C(f, "o").maxHp, C(f, "o").size], [95, "Large"]);
    eq(C(f, "o").build.extraDice, { "W-I-11": 1 }, "per weapon: Javelins");
    foeTurn(f, "o");
    const info = pv(f, atk("o", "W-I-13", "a"));
    eq([info.toHit, info.damage], [6, "1d10+4 Physical"]);
    const r = run(f, atk("o", "W-I-13", "a"), [15, 1]); // Greatclub 1d10 + 4: no extra die
    eq(dmgs(r), [5]); ok(!has(C(f, "a"), "Prone"));
    f.undo();
    const r2 = run(f, atk("o", "W-I-13", "a"), [20, 1, 1]); // crit: 2d10 + 4
    eq(dmgs(r2), [6]); ok(has(C(f, "a"), "Prone"), "Crushing");
    f.undo();
    run(f, { type: "interact", actor: "o", stow: "W-I-13", draw: "W-I-11" });
    const r3 = run(f, atk("o", "W-I-11", "a", { thrown: true }), [15, 15, 1, 1]); // thrown within 5 ft: disadvantage; Javelins 2d6 + 4
    eq(dmgs(r3), [6]);
  });

  T("[fx] Per-weapon extra dice: only the named weapon rolls them; a number still means every weapon", () => {
    const mk = (extraDice) => {
      const b = Eng.fromFoe(CARDS().foes.find((x) => x.name === "Ogre"), CARDS());
      b.extraDice = extraDice;
      return fight([pc("a", [5, 5]), { id: "o", side: "foe", name: "o", pos: [6, 5], build: b, react: "never" }]);
    };
    const f = mk({ "W-I-13": 2 });
    foeTurn(f, "o");
    eq(dmgs(run(f, atk("o", "W-I-13", "a"), [15, 1, 1, 1])), [7], "Greatclub named: 3d10 + 4");
    f.undo();
    run(f, { type: "interact", actor: "o", stow: "W-I-13", draw: "W-I-11" });
    eq(dmgs(run(f, atk("o", "W-I-11", "a", { thrown: true }), [15, 15, 1])), [5], "Javelins not named: 1d6 + 4");
    const g = mk(1);
    foeTurn(g, "o");
    eq(dmgs(run(g, atk("o", "W-I-13", "a"), [15, 1, 1])), [6], "a number: every weapon, 2d10 + 4");
  });

  T("[rules] Prone target: one advantage die at any range, melee or ranged (P 8)", () => {
    const f = fight([pc("a", [2, 5], { body: { STR: 0, DEX: 3, INT: 1, WIL: 0, HP: 11, SPD: 35 }, hands: ["W-I-10"] }), pc("b", [9, 6]), foe("x", [8, 5], { hands: ["W-I-05"] })]);
    pcTurn(f, "a");
    run(f, { type: "adjust", actor: "x", cond: "Prone" });
    const far = pv(f, atk("a", "W-I-10", "x"));
    eq([far.distance, far.adv, far.dis], [30, 1, 0], "Sling from 30 ft: advantage (was disadvantage beyond 5 ft)");
    ok(far.why.some((w) => /Target \(Prone\)/.test(w)));
    const r = run(f, atk("a", "W-I-10", "x"), [3, 18, 1]);
    eq(evs(r, "roll")[0].dice.length, 2, "rolled 2d20");
    end(f, "a");
    go(f, "b");
    eq(pv(f, atk("b", "unarmed", "x")).adv, 1, "melee within 5 ft: advantage");
  });

  T("[fx] Gladius Close Order: +1d4 while an ally is engaged with the same creature", () => {
    const f = fight([pc("a", [5, 5], { hands: ["W-I-14"] }), pc("b", [7, 5]), foe("x", [6, 5])]);
    pcTurn(f, "a");
    const r = run(f, atk("a", "W-I-14", "x"), [15, 15, 2, 3]); // Outnumbered 2 vs 1; 1d6 + 1d4 + 3
    eq(dmgs(r), [8]); ok(evs(r, "note").some((e) => /Close Order/.test(e.text)));
    f.undo();
    run(f, { type: "adjust", actor: "b", cond: "Stunned" });
    const r2 = run(f, atk("a", "W-I-14", "x"), [15, 2]); // b is Incapacitated: not engaged
    eq(dmgs(r2), [5]);
  });

  T("[fx] Boarspear Brace: +1d8 on its opportunity attacks only", () => {
    const f = fight([pc("a", [5, 5], { hands: ["W-II-01"] }), foe("x", [6, 5])]);
    foeTurn(f, "x");
    const r = run(f, { type: "move", actor: "x", path: [[7, 5], [8, 5]] }, [{ c: 0 }, 10, 2, 5]); // 1d10 + 1d8 + 3
    eq(dmgs(r), [10]); ok(evs(r, "note").some((e) => /Brace/.test(e.text)));
    const g = fight([pc("a", [5, 5], { hands: ["W-II-01"] }), foe("x", [6, 5])]);
    pcTurn(g, "a");
    eq(pv(g, atk("a", "W-II-01", "x")).toHit, 6);
    eq(dmgs(run(g, atk("a", "W-II-01", "x"), [10, 2])), [5], "own turn: 1d10 + 3");
  });

  T("[fx] Pilum Pierce: the target's Shield gives no bonus until it spends an action to pull the pilum free", () => {
    const f = fight([pc("a", [1, 5], { hands: ["W-II-02"] }), foe("x", [6, 5], { hands: ["W-I-05", "S-I-01"] }), foe("y", [6, 8])]);
    pcTurn(f, "a");
    eq(pv(f, atk("a", "W-II-02", "x", { thrown: true })).defense, 15, "Shield +2");
    const r = run(f, atk("a", "W-II-02", "x", { thrown: true }), [10, 3]); // 16 vs 15
    eq(dmgs(r), [6]);
    ok(has(C(f, "x"), "Pierced")); eq([C(f, "x").totals.STRd, C(f, "x").totals.DEXd], [13, 11]);
    end(f, "a");
    go(f, "x");
    const t = tpl(f, "x", (t) => t.type === "act" && t.action === "endCond");
    ok(t, "legal offers pulling the pilum free"); ok(/pilum/i.test(t.label));
    const cmd = Object.assign({}, t); delete cmd.label;
    run(f, cmd);
    ok(!has(C(f, "x"), "Pierced")); eq(C(f, "x").totals.STRd, 15); eq(C(f, "x").turn.acts, 1, "costs an action");
    // no Shield in hand: nothing to pierce
    const g = fight([pc("a", [1, 5], { hands: ["W-II-02"] }), foe("y", [6, 5])]);
    pcTurn(g, "a");
    run(g, atk("a", "W-II-02", "y", { thrown: true }), [15, 3]);
    ok(!has(C(g, "y"), "Pierced"));
  });

  // ---------- jewelry ----------
  T("[fx] Ring of Warding: reaction 2/S.R., +2 to the targeted Defense; ask prompts, auto only when it flips", () => {
    const f = fight([pc("a", [5, 5], { jewelry: ["J-I-01"] }), foe("x", [6, 5], { hands: ["W-I-05"] }), foe("y", [5, 6], { hands: ["W-I-05"] })]);
    foeTurn(f, "x");
    // a: STR Defense 13. x: +5, Outnumbered 2 vs 1.
    const r = run(f, atk("x", "W-I-05", "a"), [9, 9, { c: 0 }]); // 14 vs 13 → 15
    ok(evs(r, "miss").length, "turned into a miss"); eq(C(f, "a").uses["J-I-01#0"], 1);
    end(f, "x"); go(f, "y");
    const r2 = run(f, atk("y", "W-I-05", "a"), [9, 9, 4]);
    eq(r2.prompts.filter((p) => p.kind === "reaction").length, 0, "reaction already used this round");
    eq(dmgs(r2), [7]);
    const g = fight([pc("a", [5, 5], { jewelry: ["J-I-01"] }, { react: "auto" }), foe("x", [6, 5], { hands: ["W-I-05"] })]);
    foeTurn(g, "x");
    run(g, atk("x", "W-I-05", "a"), [11, 1]); // 16 vs 13: +2 can't flip
    eq(C(g, "a").uses["J-I-01#0"], 2, "auto doesn't waste it");
    g.undo();
    run(g, atk("x", "W-I-05", "a"), [10, 1]); // 15 vs 13 → 15 would still hit
    eq(C(g, "a").uses["J-I-01#0"], 2);
    g.undo();
    const r3 = run(g, atk("x", "W-I-05", "a"), [9]);
    ok(evs(r3, "miss").length); eq(C(g, "a").uses["J-I-01#0"], 1);
  });

  T("[fx] Ring of Sparks: 2d6 Lightning to a creature within 5 ft that hits you, 1/S.R.", () => {
    const f = fight([pc("a", [5, 5], { jewelry: ["J-II-01"] }), foe("x", [6, 5], { hands: ["W-I-05"] }), foe("s", [4, 5], { body: { STR: 0, DEX: 3, INT: 1, WIL: 0, HP: 11, SPD: 35 }, hands: ["W-I-10"] }), foe("far", [12, 5], { body: { STR: 0, DEX: 3, INT: 1, WIL: 0, HP: 11, SPD: 35 }, hands: ["W-I-10"] })]);
    foeTurn(f, "x");
    const r = run(f, atk("x", "W-I-05", "a"), [15, 15, { c: 0 }, 2, 3, 1]); // Outnumbered 2 vs 1
    eq(C(f, "x").hp, 14 - 5); eq(evs(r, "damage").find((e) => e.target === "x").type, "Lightning");
    eq(C(f, "a").uses["J-II-01#0"], 0);
    f.undo();
    end(f, "x"); go(f, "far");
    const r2 = run(f, atk("far", "W-I-10", "a"), [15, 1]); // 35 ft away
    eq(r2.prompts.filter((p) => p.kind === "reaction").length, 0, "not within 5 ft");
    end(f, "far"); go(f, "s");
    const r3 = run(f, atk("s", "W-I-10", "a"), [15, { c: 0 }, 2, 3, 1]); // a sling shot from 5 ft also counts
    eq(C(f, "s").hp, 11 - 5, "Sparks on a ranged hit from within 5 ft");
    ok(r3);
  });

  T("[fx] Boots of the Long Stride: reaction 1/S.R., a free Move", () => {
    const f = fight([pc("a", [1, 5], { jewelry: ["J-I-05"] }), foe("x", [20, 5])]);
    pcTurn(f, "a");
    ok(tpl(f, "a", (t) => t.power === "J-I-05#0"));
    run(f, power(f, "a", "J-I-05#0"));
    eq(C(f, "a").turn.speed, 40); ok(C(f, "a").turn.reaction); eq(C(f, "a").turn.acts, 2);
    run(f, { type: "move", actor: "a", path: Array.from({ length: 16 }, (_, i) => [2 + i, 5]) });
    eq([C(f, "a").pos, C(f, "a").turn.acts], [[17, 5], 1], "80 ft: the Boots' Move and one Move action");
    end(f, "a"); skip(f, "x"); go(f, "a");
    ok(/no uses/.test(refused(f, power(f, "a", "J-I-05#0"))));
  });

  T("[fx] Holy Amulet: Cues reach 90 ft; 1 extra Resolve added to the Litany's pool (P 10.6)", () => {
    const mk = (jewelry) => fight([pc("p", [1, 5], { body: { STR: 0, DEX: 1, INT: 0, WIL: 3, HP: 10, SPD: 30 }, jewelry, aspects: ["D-I-01"] }), pc("a", [18, 5], { hands: ["W-I-05"] }), foe("x", [19, 5])]);
    const f = mk(["J-I-04"]);
    eq(C(f, "p").resolve["D-I-01"], 7, "3 + WIL 3 + 1");
    pcTurn(f, "p"); end(f, "p"); go(f, "a");
    const r = run(f, atk("a", "W-I-05", "x"), [3, { c: 0 }, 17, 4]); // 85 ft: Twist Fate rerolls the 3
    ok(evs(r, "reaction").some((e) => e.power === "D-I-01#twist-fate"));
    const g = mk([]);
    pcTurn(g, "p"); end(g, "p"); go(g, "a");
    const r2 = run(g, atk("a", "W-I-05", "x"), [3]);
    eq(r2.prompts.filter((p) => p.kind === "reaction").length, 0, "60 ft without the amulet");
    // a WIL +0 bearer (Resolve 3 + 1) spends Bless (1) and Cure Wounds (2), then a Cue spends the last one
    const h = fight([pc("p", [2, 5], { jewelry: ["J-I-04"], aspects: ["D-I-01"] }), pc("a", [3, 5], { hands: ["W-I-05"] }), foe("x", [4, 5])]);
    pcTurn(h, "p");
    run(h, power(h, "p", "D-I-01#bless"));
    run(h, power(h, "p", "D-I-01#cure-wounds", { targets: ["a"] }), [1, 1]);
    eq(C(h, "p").resolve["D-I-01"], 1);
    end(h, "p"); go(h, "a");
    run(h, atk("a", "W-I-05", "x"), [3, 1, { c: 0 }, 17, 4]); // Bless d4 rolls with the attack
    eq(C(h, "p").resolve["D-I-01"], 0);
  });

  T("[fx] Traveler's Lute: Anthems reach 60 ft; 1 extra Resolve", () => {
    const mk = (hands) => fight([pc("e", [1, 5], { body: { STR: 0, DEX: 1, INT: 0, WIL: 3, HP: 10, SPD: 30 }, hands, aspects: ["G-I-01"] }), pc("a", [11, 5]), foe("x", [25, 5])]);
    const f = mk(["M-I-01"]);
    eq(C(f, "e").resolve["G-I-01"], 7, "3 + WIL 3 + 1");
    pcTurn(f, "e");
    run(f, power(f, "e", "G-I-01#rally"));
    ok(C(f, "a").mods.some((m) => m.n === 2), "50 ft away");
    const g = mk([]);
    pcTurn(g, "e");
    run(g, power(g, "e", "G-I-01#rally"));
    ok(!C(g, "a").mods.length, "30 ft without the lute");
  });
  // ---------- items ----------
  T("[fx] Potion of Healing / Greater Potion: action, drink or give within 5 ft, 2d4 + 2 / 4d4 + 4; the stack runs out", () => {
    const f = fight([pc("a", [5, 5], { items: [{ id: "P-I-01", n: 2 }, { id: "P-II-01", n: 1 }] }), pc("b", [6, 5]), pc("c", [8, 5]), foe("x", [20, 5])]);
    for (const id of ["a", "b", "c"]) run(f, { type: "adjust", actor: id, hp: 1 });
    pcTurn(f, "a");
    const L = tpl(f, "a", (t) => t.power === "P-I-01#0");
    ok(L.candidates.includes("a") && L.candidates.includes("b") && !L.candidates.includes("c"), "self or within 5 ft");
    const r = run(f, power(f, "a", "P-I-01#0", { targets: ["b"] }), [3, 4]);
    eq(evs(r, "heal")[0].n, 9); eq(C(f, "b").hp, 10); eq(C(f, "a").turn.acts, 1);
    eq(C(f, "a").items.find((i) => i.id === "P-I-01").n, 1);
    run(f, { type: "move", actor: "a", path: [[5, 4]] });
    ok(/No actions left/.test(refused(f, power(f, "a", "P-II-01#0", { targets: ["a"] }))));
    end(f, "a"); skip(f, "b"); skip(f, "c"); skip(f, "x"); go(f, "a");
    const r2 = run(f, power(f, "a", "P-II-01#0", { targets: ["a"] }), [1, 2, 3, 4]);
    eq(evs(r2, "heal")[0].n, 13 - 1 + 1, "4d4 + 4 = 14, capped at max HP 14"); eq(C(f, "a").hp, 14);
    ok(!C(f, "a").items.some((i) => i.id === "P-II-01"), "empty stack leaves the Item Slot");
  });

  T("[fx] Pocket Sand: bonus action, DEX or WIL + 2 vs DEX Defense within 5 ft; −2 on its attacks until the end of its next turn", () => {
    const f = fight([pc("a", [5, 5], { body: { STR: 0, DEX: 3, INT: 1, WIL: 0, HP: 11, SPD: 35 }, items: [{ id: "P-I-03", n: 1 }] }), foe("x", [6, 5], { hands: ["W-I-05"] }), foe("y", [9, 5])]);
    pcTurn(f, "a");
    ok(!tpl(f, "a", (t) => t.power === "P-I-03#0").candidates.includes("y"), "within 5 ft");
    const i = pv(f, power(f, "a", "P-I-03#0", { targets: ["x"] }));
    eq([i.toHit, i.defense], [5, 11]);
    run(f, power(f, "a", "P-I-03#0", { targets: ["x"] }), [6]); // 11 vs 11
    ok(C(f, "x").mods.some((m) => m.n === -2 && m.kind === "attack"));
    ok(!C(f, "a").items.some((it) => it.id === "P-I-03"), "used up");
    end(f, "a"); skip(f, "y"); go(f, "x");
    eq(pv(f, atk("x", "W-I-05", "a")).toHit, 3);
    run(f, atk("x", "W-I-05", "a"), [1]);
    ok(C(f, "x").mods.some((m) => m.n === -2), "every attack, not just the next");
    end(f, "x");
    ok(!C(f, "x").mods.length, "ends with x's turn");
  });

  T("[fx] Alchemist's Fire: 3 flasks, bonus action, 30 ft, one attack vs each creature within 5 ft of impact, half on a miss", () => {
    const f = fight([pc("a", [1, 5], { body: { STR: 0, DEX: 3, INT: 1, WIL: 0, HP: 11, SPD: 35 }, items: [{ id: "R-II-01" }] }), foe("x", [6, 5]), foe("y", [7, 6], { body: { STR: 0, DEX: 3, INT: 1, WIL: 0, HP: 11, SPD: 35 }, armor: "A-I-01" }), foe("z", [9, 5])]);
    eq(C(f, "a").items[0].n, 3);
    pcTurn(f, "a");
    ok(/out of range/.test(refused(f, power(f, "a", "R-II-01#0", { point: [8, 5] }))), "35 ft");
    const i = pv(f, power(f, "a", "R-II-01#0", { point: [6, 6] }));
    eq([i.toHit, i.targets], [6, ["x", "y"]]);
    const r = run(f, power(f, "a", "R-II-01#0", { point: [6, 6] }), [7, 4, 5]); // 13: hits x (DEX 11), misses y (DEX 14)
    eq(evs(r, "roll").length, 1, "one roll");
    eq(evs(r, "damage").map((e) => [e.target, e.n, e.type]), [["x", 9, "Fire"], ["y", 4, "Fire"]]);
    eq(C(f, "a").items[0].n, 2);
    for (let k = 0; k < 2; k++) { end(f, "a"); for (const id of ["x", "y", "z"]) skip(f, id); go(f, "a"); run(f, power(f, "a", "R-II-01#0", { point: [6, 9] })); }
    eq(C(f, "a").items, [{ id: "R-II-01", n: 0 }], "a Recipe keeps its Slot at 0 flasks");
    end(f, "a"); for (const id of ["x", "y", "z"]) skip(f, id); go(f, "a");
    ok(/none left/.test(refused(f, power(f, "a", "R-II-01#0", { point: [6, 9] }))));
  });

  // ---------- traits ----------
  T("[fx] Iron Will: +2 WIL Defense against fear (Dread, Bellow), not against Jeer", () => {
    const f = fight([pc("e", [1, 5], { body: { STR: 0, DEX: 1, INT: 0, WIL: 3, HP: 10, SPD: 30 }, aspects: ["G-I-01"] }), foe("x", [6, 5], { aspects: ["T-I-03"] }), foe("y", [6, 7])]);
    pcTurn(f, "e");
    eq(pv(f, power(f, "e", "G-I-01#dread", { targets: ["x"] })).defense, 12);
    eq(pv(f, power(f, "e", "G-I-01#dread", { targets: ["y"] })).defense, 10);
    eq(pv(f, power(f, "e", "G-I-01#jeer", { targets: ["x"] })).defense, 10, "Jeer isn't fear");
    run(f, power(f, "e", "G-I-01#dread", { targets: ["x"] }), [6]); // 11 vs 12
    ok(!has(C(f, "x"), "Frightened"));
    const g = fight([pc("a", [3, 5], { aspects: ["T-I-03"] }), pc("b", [3, 8]), tmpl("boss", "Ogre Chieftain", [5, 5])]);
    foeTurn(g, "boss");
    run(g, power(g, "boss", "foe-ogre-chieftain#0"), [6]); // 11: b's WIL 10 yes, a's 12 no
    ok(!has(C(g, "a"), "Frightened")); ok(has(C(g, "b"), "Frightened"));
  });

  T("[fx] Second Wind: bonus action 1/S.R., regain 1d10 + 3", () => {
    const f = fight([pc("a", [1, 5], { aspects: ["T-II-01"] }), foe("x", [20, 5])]);
    run(f, { type: "adjust", actor: "a", hp: 2 });
    pcTurn(f, "a");
    const r = run(f, power(f, "a", "T-II-01#0"), [6]);
    eq([evs(r, "heal")[0].n, C(f, "a").hp, C(f, "a").uses["T-II-01#0"]], [9, 11, 0]);
    end(f, "a"); skip(f, "x"); go(f, "a");
    ok(!tpl(f, "a", (t) => t.power === "T-II-01#0"), "no use left: no button");
  });

  T("[fx] Night Eyes: sees in the Dark within 120 ft", () => {
    const cells = {}; for (let x = 6; x < 30; x++) for (let y = 0; y < 14; y++) cells[x + "," + y] = "dark";
    const mk = (aspects) => fight([pc("a", [1, 5], { body: { STR: 0, DEX: 3, INT: 1, WIL: 0, HP: 11, SPD: 35 }, hands: ["W-I-09"], aspects }), foe("x", [21, 5]), foe("y", [27, 5])], { cells });
    const f = mk(["T-II-03"]);
    pcTurn(f, "a");
    ok(!pv(f, atk("a", "W-I-09", "x")).why.some((w) => /can't see/.test(w)), "100 ft: seen");
    ok(pv(f, atk("a", "W-I-09", "y")).why.some((w) => /can't see/.test(w)), "130 ft: beyond darkvision");
    const g = mk([]);
    pcTurn(g, "a");
    ok(pv(g, atk("a", "W-I-09", "x")).why.some((w) => /can't see/.test(w)));
  });

  T("[fx] Pack Hunter (Wolf): 1/S.R., a hit on a creature an ally is engaged with knocks it Prone; Wolf Bite +4, 1d6 + 2", () => {
    const f = fight([pc("a", [5, 5]), tmpl("w1", "Wolf", [6, 5], { react: "ask" }), tmpl("w2", "Wolf", [4, 5])]);
    eq(C(f, "w1").maxHp, 11);
    foeTurn(f, "w1");
    const i = pv(f, power(f, "w1", "foe-wolf#0", { targets: ["a"] }));
    eq([i.toHit, i.defense, i.damage], [4, 13, "1d6+2 Physical"]);
    const r = run(f, power(f, "w1", "foe-wolf#0", { targets: ["a"] }), [9, 9, 3, { c: 0 }]); // Outnumbered 2 vs 1
    eq(dmgs(r), [5]); ok(has(C(f, "a"), "Prone")); eq(C(f, "w1").uses["T-I-05#0"], 0);
    f.undo();
    const r2 = run(f, power(f, "w1", "foe-wolf#0", { targets: ["a"] }), [9, 9, 3, { c: null }]);
    ok(!has(C(f, "a"), "Prone"), "declined"); ok(r2);
    run(f, { type: "adjust", actor: "w2", dead: true }, [15]); // half the pack is down: w1's morale check holds
    f.undo(); f.undo();
    // alone: no trigger
    const g = fight([pc("a", [5, 5]), tmpl("w1", "Wolf", [6, 5], { react: "auto" })]);
    foeTurn(g, "w1");
    run(g, power(g, "w1", "foe-wolf#0", { targets: ["a"] }), [9, 3]);
    ok(!has(C(g, "a"), "Prone")); eq(C(g, "w1").uses["T-I-05#0"], 1);
  });

  T("[fx] Hedge Witch: 1 extra spell point added to the Spellbook's pool (P 10.2)", () => {
    const f = fight([pc("w", [1, 5], { body: { STR: 0, DEX: 1, INT: 3, WIL: 0, HP: 9, SPD: 30 }, items: [{ id: "B-I-01" }], aspects: ["T-II-06"] }), foe("x", [8, 5]), foe("y", [8, 9])]);
    eq(C(f, "w").sp["B-I-01"], 5);
    pcTurn(f, "w");
    run(f, power(f, "w", "B-I-01#web", { point: [8, 6] }), [1]);
    end(f, "w"); for (const id of ["x", "y"]) skip(f, id);
    go(f, "w");
    run(f, power(f, "w", "B-I-01#misty-step", { point: [1, 9] }));
    eq(C(f, "w").sp["B-I-01"], 1);
    end(f, "w"); for (const id of ["x", "y"]) skip(f, id);
    go(f, "w");
    run(f, power(f, "w", "B-I-01#magic-missile", { targets: ["x"] }), [1, 1]);
    eq(C(f, "w").sp["B-I-01"], 0, "the extra point paid for it");
    end(f, "w"); for (const id of ["x", "y"]) skip(f, id);
    go(f, "w");
    ok(/spell points/.test(refused(f, power(f, "w", "B-I-01#magic-missile", { targets: ["x"] }))));
  });

  T("[fx] Spellguard Staff: counts as an empty Hand for casting", () => {
    const f = fight([pc("w", [1, 5], { body: { STR: 0, DEX: 1, INT: 3, WIL: 0, HP: 9, SPD: 30 }, hands: ["W-I-12", "S-I-01"], items: [{ id: "B-I-01" }] }), pc("v", [1, 8], { body: { STR: 0, DEX: 1, INT: 3, WIL: 0, HP: 9, SPD: 30 }, hands: ["W-I-05", "S-I-01"], items: [{ id: "B-I-01" }] }), foe("x", [8, 5])]);
    pcTurn(f, "w");
    ok(f.preview(power(f, "w", "B-I-01#fire-bolt", { targets: ["x"] })).ok);
    end(f, "w"); go(f, "v");
    ok(/empty Hand/.test(refused(f, power(f, "v", "B-I-01#fire-bolt", { targets: ["x"] }))));
  });
  // ---------- techniques ----------
  T("[fx] Cleave: 1/S.R., a melee drop gives one more melee attack, even after the Attack action", () => {
    const f = fight([pc("a", [5, 5], { hands: ["W-I-05"], aspects: ["Q-I-01"] }), foe("x", [6, 5]), foe("y", [5, 6])]);
    run(f, { type: "adjust", actor: "x", hp: 1 });
    pcTurn(f, "a");
    const r = run(f, atk("a", "W-I-05", "x"), [15, 15, 1, { c: 0 }, 15]); // 1 vs 2: disadvantage; Cleave asks (optional: it has uses); y's morale holds
    ok(C(f, "x").dead); eq(r.prompts.filter((p) => /Cleave/.test(p.text)).length, 1);
    eq(C(f, "a").uses["Q-I-01#0"], 0);
    eq(C(f, "a").turn.acts, 1, "the Attack action is spent");
    eq(pv(f, atk("a", "W-I-05", "y")).use, "extra");
    run(f, atk("a", "W-I-05", "y"), [15, 1]);
    eq(pv(f, atk("a", "W-I-05", "y")).use, "action", "only one extra attack; the next takes the second action");
  });

  T("[fx] Steady Aim: reaction 2/S.R., +2 on the next ranged attack this turn only", () => {
    const f = fight([pc("a", [5, 5], { body: { STR: 0, DEX: 3, INT: 1, WIL: 0, HP: 11, SPD: 35 }, hands: ["W-I-10", "W-I-01"], aspects: ["Q-I-02"] }), foe("x", [6, 5]), foe("y", [12, 5])]);
    pcTurn(f, "a");
    const base = pv(f, atk("a", "W-I-10", "y")).toHit;
    run(f, power(f, "a", "Q-I-02#0"));
    eq(C(f, "a").uses["Q-I-02#0"], 1);
    eq(pv(f, atk("a", "W-I-10", "y")).toHit, base + 2);
    eq(pv(f, atk("a", "W-I-01", "x")).toHit, 7, "melee dagger: DEX 3 + 4, no bonus");
    end(f, "a");
    ok(!C(f, "a").mods.length, "this turn only");
    for (const id of ["x", "y"]) skip(f, id);
    go(f, "a");
    run(f, power(f, "a", "Q-I-02#0"));
    run(f, atk("a", "W-I-10", "y"), [1, 1]); // You: long range, enemy within 5 ft; Crowd: nobody around y
    ok(!C(f, "a").mods.length, "spent by the ranged attack");
  });

  T("[fx] Shield Bash: reaction 1/S.R. after the Attack action while holding a Shield: Shove within 5 ft", () => {
    const f = fight([pc("a", [5, 5], { hands: ["W-I-05", "S-I-01"], aspects: ["Q-I-03"] }), foe("x", [6, 5]), foe("y", [5, 6])]);
    pcTurn(f, "a");
    ok(/Attack action first/.test(refused(f, power(f, "a", "Q-I-03#0", { targets: ["x"], mode: "prone" }))));
    run(f, atk("a", "W-I-05", "x"), [1, 1]);
    const t = tpl(f, "a", (t) => t.power === "Q-I-03#0");
    ok(t && t.candidates.includes("x") && t.candidates.includes("y"));
    run(f, power(f, "a", "Q-I-03#0", { targets: ["y"], mode: "prone" }), [8, 8]); // unarmed STR + 2 vs 13; Outnumbered 2 vs 1 against a
    ok(has(C(f, "y"), "Prone")); ok(C(f, "a").turn.reaction); eq(C(f, "a").uses["Q-I-03#0"], 0);
    const g = fight([pc("a", [5, 5], { hands: ["W-I-05"], aspects: ["Q-I-03"] }), foe("x", [6, 5])]);
    pcTurn(g, "a");
    run(g, atk("a", "W-I-05", "x"), [1]);
    ok(/needs a Shield/.test(refused(g, power(g, "a", "Q-I-03#0", { targets: ["x"] }))));
  });

  T("[fx] Battle Hymn: 2/S.R. on a weapon hit, up to 3 allies within 30 ft who hear get +2 on their next attack", () => {
    const f = fight([pc("a", [5, 5], { hands: ["W-I-05"], aspects: ["Q-I-04"] }), pc("b", [3, 5], { hands: ["W-I-10"] }), pc("c", [5, 8]), pc("d", [1, 5]), pc("e", [5, 1]), pc("far", [12, 12]), pc("deaf", [6, 7]), foe("x", [6, 5])]);
    run(f, { type: "adjust", actor: "deaf", cond: "Deafened" });
    pcTurn(f, "a");
    const r = run(f, atk("a", "W-I-05", "x"), [15, 1, { c: 0 }]);
    eq(r.prompts.filter((p) => /Battle Hymn/.test(p.text)).length, 1);
    const got = ["b", "c", "d", "e", "far", "deaf"].filter((id) => C(f, id).mods.some((m) => m.n === 2 && m.next));
    eq(got, ["b", "c", "d"], "the 3 nearest who can hear");
    eq(C(f, "a").uses["Q-I-04#0"], 1);
    end(f, "a"); go(f, "b");
    eq(pv(f, atk("b", "W-I-10", "x")).toHit, 1 + 2 + 2);
    run(f, atk("b", "W-I-10", "x"), [1]);
    ok(!C(f, "b").mods.length, "spent");
    ok(C(f, "c").mods.length === 1);
    end(f, "b"); for (const id of ["c", "d", "e", "far", "deaf"]) skip(f, id); skip(f, "x"); go(f, "a");
    ok(C(f, "c").mods.length === 1, "lasts through a's next turn");
    end(f, "a");
    ok(!C(f, "c").mods.length, "gone at the end of a's next turn");
  });

  T("[fx] Rallying Cry: bonus action 1/S.R., up to 3 allies within 30 ft +2 on attacks for 1 minute", () => {
    const f = fight([pc("a", [5, 5], { aspects: ["Q-I-05"] }), pc("b", [6, 5]), pc("c", [7, 5]), pc("d", [8, 5]), pc("e", [9, 5]), foe("x", [20, 5])]);
    pcTurn(f, "a");
    run(f, power(f, "a", "Q-I-05#0"));
    eq(["b", "c", "d", "e"].filter((id) => C(f, id).mods.some((m) => m.n === 2)), ["b", "c", "d"]);
    eq(C(f, "a").uses["Q-I-05#0"], 0);
    for (let k = 1; k < 10; k++) { end(f, "a"); for (const id of ["b", "c", "d", "e"]) skip(f, id); skip(f, "x"); go(f, "a"); }
    ok(C(f, "b").mods.length === 1, "still on at a's 9th turn start");
    end(f, "a"); for (const id of ["b", "c", "d", "e"]) skip(f, id); skip(f, "x"); go(f, "a");
    ok(!C(f, "b").mods.length, "1 minute: ends at a's 10th turn start");
  });

  T("[fx] Shield Wall: reaction 1/S.R. while holding a Shield, +2 to an adjacent ally's targeted Defense", () => {
    const mk = (hands) => fight([pc("a", [5, 5]), pc("s", [5, 6], { hands, aspects: ["Q-I-06"] }), foe("x", [6, 5], { hands: ["W-I-05"] })]);
    const f = mk(["S-I-01"]);
    foeTurn(f, "x");
    const r = run(f, atk("x", "W-I-05", "a"), [8, 8, { c: 0 }]); // 1 vs 2: disadvantage; 13 vs 13 → 15
    ok(evs(r, "miss").length); eq(C(f, "s").uses["Q-I-06#0"], 0); ok(C(f, "s").turn.reaction);
    const g = mk(["W-I-05"]);
    foeTurn(g, "x");
    const r2 = run(g, atk("x", "W-I-05", "a"), [8, 8, 1]);
    eq(r2.prompts.filter((p) => p.kind === "reaction").length, 0, "no Shield, no Shield Wall");
  });

  // ---------- Callings (P 2.4, 3.1) ----------
  const calling = (id, o) => Object.assign({ calling: id, body: null }, o);
  T("[fx] Callings: symbols gate equipping; +2 / +2 and the Calling's HP and Speed", () => {
    const t = Eng.totals(B(calling("L-02", { hands: ["W-I-05", "S-I-01"], armor: "A-I-02" })), CARDS());
    eq([t.STR, t.WIL, t.DEX, t.STRd, t.DEXd, t.HP, t.SPD, t.errors], [2, 2, 0, 17, 12, 18, 30, []]);
    eq(Eng.validate(B(calling("L-02", { hands: ["W-I-09"] })), CARDS()), [], "a basic weapon lights all four: a Templar can wield a Longbow");
    ok(Eng.validate(B(calling("L-02", { hands: ["W-I-15"] })), CARDS()).some((v) => /symbols/.test(v)), "Templar can't wield a Shortbow (loot, DEX)");
    eq(Eng.totals(B(calling("L-02", { hands: ["W-I-15"] })), CARDS()).errors.length, 1);
  });
  T("[fx] Duelist Footwork: 5 ft of safe movement after a melee hit, once per turn", () => {
    const f = fight([pc("d", [5, 5], calling("L-01", { hands: ["W-I-03"] })), foe("x", [6, 5])]);
    pcTurn(f, "d");
    run(f, atk("d", "W-I-03", "x"), [18, 3]);
    eq(C(f, "d").turn.safeFt, 5); ok(f.legal("d").some((m) => m.type === "move" && m.safe));
    run(f, atk("d", "W-I-03", "x"), [18, 3]);
    eq(C(f, "d").turn.safeFt, 5, "once per turn");
  });
  T("[fx] Templar Oath: reaction 1/S.R., takes an adjacent ally's hit", () => {
    const f = fight([pc("a", [5, 5]), pc("t", [5, 6], calling("L-02"), { react: "auto" }), foe("x", [6, 5], { hands: ["W-I-05"] })]);
    foeTurn(f, "x");
    run(f, atk("x", "W-I-05", "a"), [15, 15, 6]); // 6 + 3 = 9
    eq([C(f, "a").hp, C(f, "t").hp, C(f, "t").uses["L-02#0"]], [14, 14 - 9, 0]);
  });
  T("[fx] Performer Crowd Work: reaction 1/S.R., +2 to an ally's roll within 30 ft", () => {
    const f = fight([pc("p", [1, 5], calling("L-05"), { react: "auto" }), pc("a", [7, 5], { hands: ["W-I-05"] }), foe("x", [8, 5], { hands: ["W-I-05"] })]);
    pcTurn(f, "a");
    const r = run(f, atk("a", "W-I-05", "x"), [7, 1]); // 12 vs 13 → 14: hits
    ok(evs(r, "reaction").some((e) => e.power === "L-05#0")); eq(dmgs(r), [4]); eq(C(f, "p").uses["L-05#0"], 0);
  });
  T("[fx] Spellblade Battle Caster casts with both Hands full; Sage Learned: +1 spell point", () => {
    const hands = { hands: ["W-I-05", "S-I-01"], items: [{ id: "B-I-01" }] };
    const f = fight([pc("s", [1, 5], calling("L-03", hands)), pc("g", [1, 7], calling("L-06", { items: [{ id: "B-I-01" }] })), foe("x", [9, 5])]);
    pcTurn(f, "s");
    ok(f.legal("s").some((m) => m.power && m.power.startsWith("B-I-01")), "Spellblade casts holding a Longsword and a Shield");
    eq([C(f, "s").sp["B-I-01"], C(f, "g").sp["B-I-01"]], [4, 5]);
    const g = fight([pc("s", [1, 5], hands), foe("x", [9, 5])]);
    pcTurn(g, "s");
    ok(!g.legal("s").some((m) => m.power && m.power.startsWith("B-I-01")), "a body with both Hands full can't cast");
  });

  T("[fx] Brawler Scrapper: +2 to hit with Shoves; Hermit Solitude: +1 Resolve", () => {
    const f = fight([pc("b", [5, 5], calling("L-07")), pc("h", [1, 1], calling("L-12", { aspects: ["G-I-01"] })), foe("x", [6, 5])]);
    pcTurn(f, "b");
    const r = f.preview({ type: "shove", actor: "b", target: "x", mode: "push" });
    eq(r.info.toHit, 2 + 2 + 2, "STR + 2 + Scrapper");
    eq(C(f, "h").resolve["G-I-01"], 3 + 2 + 1);
  });
  T("[fx] Zealot Righteous Fury: 1/S.R., +1d6 Radiant on a weapon hit", () => {
    const f = fight([pc("z", [5, 5], calling("L-08", { hands: ["W-I-05"] }), { react: "auto" }), foe("x", [6, 5])]);
    pcTurn(f, "z");
    const r = run(f, atk("z", "W-I-05", "x"), [18, 4, 3]);
    eq(dmgs(r), [6, 3]); eq(C(f, "z").uses["L-08#0"], 0);
  });
  T("[fx] Trickster Feint: reaction 1/S.R., −2 to an attack that hits you", () => {
    const f = fight([pc("k", [5, 5], calling("L-11"), { react: "auto" }), foe("x", [6, 5], { hands: ["W-I-05"] })]);
    foeTurn(f, "x");
    const r = run(f, atk("x", "W-I-05", "k"), [8]); // 8 + 5 = 13 vs DEX Defense 12 → 14: miss
    ok(evs(r, "miss").length); eq(C(f, "k").uses["L-11#0"], 0);
  });

  T("[fx] Twin Strike: one extra attack, once per turn", () => {
    const f = fight([pc("a", [5, 5], { hands: ["W-I-05"], aspects: ["Q-II-01"] }), foe("x", [6, 5])]);
    pcTurn(f, "a");
    run(f, atk("a", "W-I-05", "x"), [1]);
    eq(pv(f, atk("a", "W-I-05", "x")).use, "attack");
    run(f, atk("a", "W-I-05", "x"), [1]);
    eq(pv(f, atk("a", "W-I-05", "x")).use, "action");
    run(f, atk("a", "W-I-05", "x"), [1]);
    ok(/No actions left/.test(refused(f, atk("a", "W-I-05", "x"))), "3 attacks in all");
  });

  T("[fx] Slippery: reaction 2/S.R., move half your Speed without opportunity attacks", () => {
    const f = fight([pc("a", [5, 5], { aspects: ["Q-I-07"] }), foe("x", [6, 5], { hands: ["W-I-05"] }, { react: "ask" })]);
    pcTurn(f, "a");
    run(f, power(f, "a", "Q-I-07#0"));
    eq(C(f, "a").turn.safeFt, 20);
    ok(tpl(f, "a", (t) => t.type === "move" && t.safe));
    const r = run(f, { type: "move", actor: "a", safe: true, path: [[4, 5], [3, 5], [2, 5], [1, 5]] });
    eq(r.prompts.length, 0, "no opportunity attack"); eq(C(f, "a").pos, [1, 5]); eq([C(f, "a").turn.safeFt, C(f, "a").turn.moved], [0, 0]);
    f.undo();
    ok(/Needs 25 ft/.test(refused(f, { type: "move", actor: "a", safe: true, path: [[4, 5], [3, 5], [2, 5], [1, 5], [0, 5]] })));
    const r2 = run(f, { type: "move", actor: "a", path: [[4, 5]] }, [{ c: null }]);
    eq(r2.prompts.length, 1, "a normal move provokes");
  });
  // ---------- Conjurer's Book ----------
  const wiz = (o) => Object.assign({ body: { STR: 0, DEX: 1, INT: 3, WIL: 0, HP: 9, SPD: 30 }, items: [{ id: "B-I-01" }] }, o);
  T("[fx] Fire Bolt: cantrip, 120 ft, INT + 2 vs DEX, 1d10 Fire; no spell points, not the turn's spell", () => {
    const f = fight([pc("w", [1, 5], wiz()), foe("x", [20, 5]), foe("far", [26, 5])], { w: 40 });
    pcTurn(f, "w");
    const i = pv(f, power(f, "w", "B-I-01#fire-bolt", { targets: ["x"] }));
    eq([i.toHit, i.defense, i.damage, i.cost], [5, 11, "1d10 Fire", null]);
    ok(/out of range \(120 ft\)/.test(refused(f, power(f, "w", "B-I-01#fire-bolt", { targets: ["far"] }))), "125 ft");
    const r = run(f, power(f, "w", "B-I-01#fire-bolt", { targets: ["x"] }), [6, 7]);
    eq(evs(r, "damage").map((e) => [e.n, e.type]), [[7, "Fire"]]); eq(C(f, "w").sp["B-I-01"], 4);
    ok(f.preview(power(f, "w", "B-I-01#misty-step", { point: [1, 9] })).ok, "a spell after a cantrip");
  });

  T("[fx] Mage Hand: listed, no combat effect, no cost", () => {
    const f = fight([pc("w", [1, 5], wiz()), foe("x", [20, 5])]);
    pcTurn(f, "w");
    const r = run(f, power(f, "w", "B-I-01#mage-hand"));
    eq(evs(r, "damage").length + evs(r, "cond").length, 0); eq(C(f, "w").turn.acts, 1); eq(C(f, "w").sp["B-I-01"], 4);
  });

  T("[fx] Magic Missile: 3 darts, one attack per target vs DEX, 1d4 + 1 Radiant per dart, half on a miss, +1 dart per upcast level", () => {
    const f = fight([pc("w", [1, 5], wiz()), foe("x", [8, 5]), foe("y", [8, 8])]);
    pcTurn(f, "w");
    eq(pv(f, power(f, "w", "B-I-01#magic-missile", { targets: ["x"] })).cost, "1 spell point");
    ok(/3 darts/.test(refused(f, power(f, "w", "B-I-01#magic-missile", { targets: ["x", "x", "y", "y"] }))));
    ok(/Max spell level 2/.test(refused(f, power(f, "w", "B-I-01#magic-missile", { targets: ["x"], level: 3 }))));
    const r = run(f, power(f, "w", "B-I-01#magic-missile", { targets: ["x", "x", "x", "y"], level: 2 }), [10, 1, 2, 3, 2, 3]);
    eq(evs(r, "roll").length, 2, "one roll per target");
    eq(evs(r, "damage").map((e) => [e.target, e.n, e.type]), [["x", 9, "Radiant"], ["y", 2, "Radiant"]], "x: 3 darts (2+3+4); y misses: half of 4");
    eq(C(f, "w").sp["B-I-01"], 2);
    ok(f.preview(power(f, "w", "B-I-01#misty-step", { point: [1, 9] })).ok, "no limit on spells per turn");
  });

  T("[fx] Shield: reaction, +5 STR and DEX Defense against the triggering attack and until the start of your next turn", () => {
    const f = fight([pc("w", [5, 5], wiz()), foe("x", [6, 5], { hands: ["W-I-05"] }), foe("y", [4, 5], { body: { STR: 0, DEX: 3, INT: 1, WIL: 0, HP: 11, SPD: 35 }, hands: ["W-I-01"] })]);
    foeTurn(f, "x");
    const r = run(f, atk("x", "W-I-05", "w"), [9, 9, { c: 0 }]); // 14 vs 11 → 16; Outnumbered 2 vs 1
    ok(evs(r, "miss").length); eq(C(f, "w").sp["B-I-01"], 3);
    end(f, "x"); go(f, "y");
    eq(pv(f, atk("y", "W-I-01", "w")).defense, 16, "still on");
    end(f, "y"); go(f, "w");
    ok(!C(f, "w").mods.length, "ends at the start of w's turn");
    const g = fight([pc("w", [5, 5], wiz({ hands: ["W-I-05", "S-I-01"] })), foe("x", [6, 5], { hands: ["W-I-05"] })]);
    foeTurn(g, "x");
    const r2 = run(g, atk("x", "W-I-05", "w"), [12, 1]);
    eq(r2.prompts.filter((p) => p.kind === "reaction").length, 0, "no empty Hand, no Shield");
  });

  T("[fx] Grease: 10-ft cube, difficult terrain, attack vs DEX of each creature in it and of one entering or ending its turn there; 1 minute", () => {
    const f = fight([pc("w", [1, 5], wiz()), foe("x", [8, 5]), foe("y", [9, 6]), foe("z", [12, 5], { hands: ["W-I-05"] })]);
    pcTurn(f, "w");
    const i = pv(f, power(f, "w", "B-I-01#grease", { point: [8, 5] }));
    eq([i.cells, i.targets], [["8,5", "9,5", "8,6", "9,6"], ["x", "y"]]);
    const r = run(f, power(f, "w", "B-I-01#grease", { point: [8, 5] }), [6]); // 11: x (DEX 11) Prone, y too
    eq(evs(r, "roll").length, 1); ok(has(C(f, "x"), "Prone") && has(C(f, "y"), "Prone"));
    eq(C(f, "w").sp["B-I-01"], 3);
    end(f, "w");
    run(f, { type: "beginTurn", actor: "x" });
    run(f, { type: "move", actor: "x", stand: true, path: [] });
    run(f, { type: "endTurn", actor: "x" }, [1]); // ends its turn there: attacked again, misses
    skip(f, "y", [], [1]); // Prone, ends its turn there: attacked
    go(f, "z");
    eq(pv(f, { type: "move", actor: "z", path: [[11, 5], [10, 5], [9, 5]] }).cost, 20, "the greased square costs double");
    const r2 = run(f, { type: "move", actor: "z", path: [[11, 5], [10, 5], [9, 5]] }, [1]); // enters: attacked
    eq(evs(r2, "roll").length, 1);
    eq(run(f, { type: "endTurn", actor: "z" }).prompts.length, 0, "once per turn");
    for (let k = 1; k <= 10; k++) {
      go(f, "w"); eq(f.state.zones.length, k < 10 ? 1 : 0, "turn " + k); end(f, "w");
      for (const id of ["x", "y", "z"]) skip(f, id, [], k < 10 ? [1] : []);
    }
  });

  T("[fx] Misty Step: reaction, 2 spell points, teleport up to 30 ft to a free square you can see, no opportunity attacks", () => {
    const f = fight([pc("w", [5, 5], wiz()), foe("x", [6, 5], { hands: ["W-I-05"] }, { react: "ask" })], { cells: { "1,1": "wall" } });
    pcTurn(f, "w");
    ok(/at most 30 ft/.test(refused(f, power(f, "w", "B-I-01#misty-step", { point: [12, 5] }))));
    ok(/isn't free/.test(refused(f, power(f, "w", "B-I-01#misty-step", { point: [6, 5] }))));
    const r = run(f, power(f, "w", "B-I-01#misty-step", { point: [5, 11] }));
    eq(r.prompts.length, 0, "no opportunity attack"); eq(C(f, "w").pos, [5, 11]); ok(C(f, "w").turn.reaction); eq(C(f, "w").sp["B-I-01"], 2);
  });

  T("[fx] Web: 20-ft cube, Restrained for 2 turns on a hit vs DEX, no maintain roll, entering triggers it, fire burns it away", () => {
    const f = fight([pc("w", [1, 5], wiz()), foe("x", [8, 5]), foe("y", [9, 7]), foe("z", [13, 5])]);
    pcTurn(f, "w");
    const i = pv(f, power(f, "w", "B-I-01#web", { point: [8, 5] }));
    eq(i.cells.length, 16); eq(i.targets, ["x", "y"]);
    run(f, power(f, "w", "B-I-01#web", { point: [8, 5] }), [6]); // 11 vs DEX 11
    ok(C(f, "x").conds.some((k) => k.name === "Restrained" && !k.lasting));
    eq(C(f, "w").sp["B-I-01"], 2);
    end(f, "w");
    const r = go(f, "x");
    eq(evs(r, "maintain").length, 0); ok(has(C(f, "x"), "Restrained"));
    end(f, "x");
    skip(f, "y");
    ok(has(C(f, "y"), "Restrained"), "still held after its 1st turn");
    go(f, "z");
    run(f, { type: "move", actor: "z", path: [[12, 5], [11, 5], [10, 5], [9, 5]] }, [10]); // enters at 10,5
    ok(has(C(f, "z"), "Restrained"), "entering"); eq(C(f, "z").pos, [10, 5], "Restrained: speed 0, the move stops");
    end(f, "z");
    // fire: Fire Bolt on x burns its square and frees it
    go(f, "w");
    run(f, power(f, "w", "B-I-01#fire-bolt", { targets: ["x"] }), [10, 10, 1]); // Restrained target: advantage
    ok(!f.state.zones[0].cells.includes("8,5"), "square burned"); ok(!has(C(f, "x"), "Restrained"), "freed");
    end(f, "w"); skip(f, "x"); skip(f, "y");
    ok(!has(C(f, "y"), "Restrained"), "ends with its 2nd turn");
  });
  // ---------- Wanderer's Repertoire ----------
  const bard = (o) => Object.assign({ body: { STR: 0, DEX: 1, INT: 0, WIL: 3, HP: 10, SPD: 30 }, aspects: ["G-I-01"] }, o);
  T("[fx] Jeer: Dirge at will, WIL + 2 vs WIL, −2 on the target's next attack until the end of its next turn; needs your voice", () => {
    const f = fight([pc("e", [1, 5], bard(), { react: "never" }), pc("a", [7, 5]), foe("x", [8, 5], { hands: ["W-I-05"] }), foe("far", [14, 5])]);
    pcTurn(f, "e");
    const i = pv(f, power(f, "e", "G-I-01#jeer", { targets: ["x"] }));
    eq([i.toHit, i.defense, i.cost], [5, 10, null]);
    ok(/out of range \(60 ft\)/.test(refused(f, power(f, "e", "G-I-01#jeer", { targets: ["far"] }))), "65 ft");
    run(f, power(f, "e", "G-I-01#jeer", { targets: ["x"] }), [5]);
    eq(C(f, "e").resolve["G-I-01"], 6);
    end(f, "e"); skip(f, "a"); skip(f, "far"); go(f, "x");
    eq(pv(f, atk("x", "W-I-05", "a")).toHit, 3);
    run(f, atk("x", "W-I-05", "a"), [1]);
    ok(!C(f, "x").mods.length, "next attack only");
    const g = fight([pc("e", [1, 5], bard()), foe("x", [8, 5])]);
    run(g, { type: "adjust", actor: "e", cond: "Stunned" });
    start(g); go(g, "e");
    eq(g.state.active, null, "Stunned: the turn ends on its own");
    ok(!g.legal("e").some((t) => t.power === "G-I-01#jeer"));
  });

  T("[fx] Rally: Anthem, 1 Resolve, up to 3 allies within 30 ft +2 on attacks for 1 minute", () => {
    const f = fight([pc("e", [1, 5], bard()), pc("a", [3, 5]), pc("b", [4, 5]), pc("c", [5, 5]), pc("d", [6, 5]), foe("x", [20, 5])]);
    pcTurn(f, "e");
    run(f, power(f, "e", "G-I-01#rally"));
    eq(["a", "b", "c", "d"].filter((id) => C(f, id).mods.some((m) => m.n === 2 && m.kind === "attack")), ["a", "b", "c"]);
    eq(C(f, "e").resolve["G-I-01"], 5); eq(C(f, "e").turn.acts, 1);
    eq(C(f, "a").mods[0].until.rounds, 10);
  });

  T("[fx] Hold the Line: Anthem, 1 Resolve, every ally within 30 ft +2 STR and DEX Defense for 1 minute", () => {
    const f = fight([pc("e", [1, 5], bard()), pc("a", [3, 5]), pc("b", [4, 5]), pc("c", [5, 5]), pc("d", [6, 5]), pc("far", [9, 5]), foe("x", [7, 5], { hands: ["W-I-05"] })]);
    pcTurn(f, "e");
    run(f, power(f, "e", "G-I-01#hold-the-line"));
    eq(["a", "b", "c", "d", "far"].filter((id) => C(f, id).mods.length), ["a", "b", "c", "d"], "no count limit; 40 ft is out");
    ok(!C(f, "e").mods.length, "allies, not the singer");
    end(f, "e"); for (const id of ["a", "b", "c", "d", "far"]) skip(f, id);
    go(f, "x");
    eq(pv(f, atk("x", "W-I-05", "d")).defense, 15);
  });

  T("[fx] Cutting Words: Cue, reaction, 1 Resolve, −2 to an enemy's attack roll within 60 ft", () => {
    const f = fight([pc("e", [1, 5], bard()), pc("a", [7, 5]), foe("x", [8, 5], { hands: ["W-I-05"] })]);
    foeTurn(f, "x");
    const r = run(f, atk("x", "W-I-05", "a"), [9, { c: 0 }]); // 14 vs 13 → 12
    ok(evs(r, "reaction").some((e) => e.power === "G-I-01#cutting-words")); ok(evs(r, "miss").length);
    eq(C(f, "e").resolve["G-I-01"], 5); ok(C(f, "e").turn.reaction);
    f.undo();
    C(f, "e").react = "auto";
    const r2 = run(f, atk("x", "W-I-05", "a"), [12, 1]); // 17 vs 13: −2 can't flip, auto keeps it
    eq(evs(r2, "reaction").length, 0);
  });

  T("[fx] Steady Now: Cue, +2 to an ally's roll, or to the Defense an enemy's attack targets", () => {
    const f = fight([pc("e", [1, 5], bard()), pc("a", [7, 5], { hands: ["W-I-05"] }), foe("x", [8, 5], { hands: ["W-I-05"] })]);
    pcTurn(f, "a");
    const r = run(f, atk("a", "W-I-05", "x"), [7, { c: 0 }, 1]); // 12 vs 13 → 14: hits
    ok(evs(r, "reaction").some((e) => e.power === "G-I-01#steady-now")); eq(dmgs(r), [4]);
    end(f, "a"); skip(f, "e"); go(f, "x");
    const r2 = run(f, atk("x", "W-I-05", "a"), [8, { c: 0 }]); // 13 vs 13 → Defense 15
    ok(evs(r2, "miss").length, "orDefense"); eq(C(f, "e").resolve["G-I-01"], 4);
  });

  T("[fx] Dread: Dirge, 2 Resolve, Frightened of you for 2 turns; no moving closer, −1d20 on attacks", () => {
    const f = fight([pc("e", [1, 5], bard()), pc("a", [8, 4]), foe("x", [9, 5], { hands: ["W-I-05"] })]);
    pcTurn(f, "e");
    run(f, power(f, "e", "G-I-01#dread", { targets: ["x"] }), [7]); // 12 vs 10
    ok(C(f, "x").conds.some((k) => k.name === "Frightened" && !k.lasting)); eq(C(f, "e").resolve["G-I-01"], 4);
    end(f, "e"); skip(f, "a");
    const r = go(f, "x");
    eq(evs(r, "maintain").length, 0); ok(has(C(f, "x"), "Frightened"));
    ok(/Frightened/.test(refused(f, { type: "move", actor: "x", path: [[8, 6]] })), "no step closer to e");
    ok(f.preview({ type: "move", actor: "x", path: [[10, 5]] }).ok);
    ok(pv(f, atk("x", "W-I-05", "a")).why.some((w) => /Frightened/.test(w)), "disadvantage while e is in sight");
    end(f, "x");
    for (const id of ["e", "a", "x"]) skip(f, id);
    ok(!has(C(f, "x"), "Frightened"), "ends with its 2nd turn");
  });

  // ---------- Acolyte's Litany ----------
  const priest = (o) => Object.assign({ body: { STR: 0, DEX: 1, INT: 0, WIL: 3, HP: 10, SPD: 30 }, aspects: ["D-I-01"] }, o);
  T("[fx] Guidance: checks only, never prompts on an attack", () => {
    const f = fight([pc("p", [1, 5], priest()), pc("a", [7, 5], { hands: ["W-I-05"] }), foe("x", [8, 5])]);
    pcTurn(f, "a");
    const r = run(f, atk("a", "W-I-05", "x"), [1, { c: null }]); // Twist Fate asks; Guidance doesn't
    ok(r.prompts.some((q) => q.kind === "reaction"));
    ok(!r.prompts.some((q) => q.options && q.options.some((o) => o.power === "D-I-01#guidance")));
  });

  T("[fx] Bless: Anthem, 1 Resolve, up to 3 allies within 30 ft add 1d4 to attack rolls for 1 minute", () => {
    const f = fight([pc("p", [1, 5], priest(), { react: "never" }), pc("a", [7, 5], { hands: ["W-I-05"] }), foe("x", [8, 5])]);
    pcTurn(f, "p");
    run(f, power(f, "p", "D-I-01#bless"));
    ok(C(f, "a").mods.some((m) => m.dice === "1d4")); eq(C(f, "p").resolve["D-I-01"], 5);
    end(f, "p"); go(f, "a");
    const r = run(f, atk("a", "W-I-05", "x"), [7, 3, 1]); // 7 + 5 + 3 = 15 vs 13
    eq(evs(r, "roll")[0].total, 15); eq(dmgs(r), [4]);
    ok(C(f, "a").mods.length === 1, "every attack for the Duration");
  });

  T("[fx] R500: the same power doesn't stack — a second Bless on an ally replaces the first", () => {
    const f = fight([pc("p", [1, 5], priest()), pc("q", [1, 6], priest()), pc("a", [7, 5]), foe("x", [20, 5])]);
    pcTurn(f, "p");
    run(f, power(f, "p", "D-I-01#bless"));
    end(f, "p"); go(f, "q");
    run(f, power(f, "q", "D-I-01#bless"));
    eq(C(f, "a").mods.filter((m) => m.dice === "1d4").length, 1);
  });

  T("[fx] Bane: Dirge, 1 Resolve, the target subtracts 1d4 from its attack rolls for 1 minute", () => {
    const f = fight([pc("p", [1, 5], priest(), { react: "never" }), pc("a", [7, 5]), foe("x", [8, 5], { hands: ["W-I-05"] })]);
    pcTurn(f, "p");
    run(f, power(f, "p", "D-I-01#bane", { targets: ["x"] }), [6]); // 11 vs WIL 10
    ok(C(f, "x").mods.some((m) => m.dice === "-1d4")); eq(C(f, "p").resolve["D-I-01"], 5);
    end(f, "p"); skip(f, "a");
    go(f, "x"); // no maintain roll
    const r = run(f, atk("x", "W-I-05", "a"), [10, 4]); // 10 + 5 − 4 = 11 vs 13
    eq(evs(r, "roll")[0].total, 11); ok(evs(r, "miss").length);
    end(f, "x");
    for (const id of ["p", "a", "x"]) skip(f, id);
    eq(C(f, "x").mods.filter((m) => m.dice === "-1d4").map((m) => m.until.rounds), [9], "1 minute, counted on p's turns");
  });

  T("[fx] Twist Fate: Cue, 1 Resolve, reroll a creature's attack once; auto never rerolls", () => {
    const f = fight([pc("p", [1, 5], priest()), pc("a", [7, 5]), foe("x", [8, 5], { hands: ["W-I-05"] })]);
    foeTurn(f, "x");
    const r = run(f, atk("x", "W-I-05", "a"), [18, { c: 0 }, 2]); // reroll the enemy's hit
    ok(evs(r, "miss").length); eq(C(f, "p").resolve["D-I-01"], 5);
    eq(r.prompts.filter((q) => q.kind === "reaction").length, 1, "once");
    f.undo();
    C(f, "p").react = "auto";
    const r2 = run(f, atk("x", "W-I-05", "a"), [18, 1]);
    eq(evs(r2, "reaction").length, 0);
  });

  T("[fx] Healing Word: Mend, action, 2 Resolve, 60 ft, 2d4 + WIL; reaches an Unconscious ally", () => {
    const f = fight([pc("p", [1, 5], priest()), pc("a", [12, 5]), pc("far", [14, 5]), foe("x", [20, 5])]);
    run(f, { type: "adjust", actor: "a", hp: 0 });
    pcTurn(f, "p");
    ok(/out of range/.test(refused(f, power(f, "p", "D-I-01#healing-word", { targets: ["far"] }))), "65 ft");
    const r = run(f, power(f, "p", "D-I-01#healing-word", { targets: ["a"] }), [1, 2]);
    eq(evs(r, "heal")[0].n, 6); ok(!has(C(f, "a"), "Unconscious")); eq(C(f, "p").resolve["D-I-01"], 4); eq(C(f, "p").turn.acts, 1);
  });

  T("[fx] Cure Wounds: Mend, action, 2 Resolve, touch, 2d8 + WIL", () => {
    const f = fight([pc("p", [1, 5], priest()), pc("a", [2, 5]), pc("b", [3, 5]), foe("x", [20, 5])]);
    run(f, { type: "adjust", actor: "a", hp: 1 });
    pcTurn(f, "p");
    ok(/out of range \(5 ft\)/.test(refused(f, power(f, "p", "D-I-01#cure-wounds", { targets: ["b"] }))));
    const r = run(f, power(f, "p", "D-I-01#cure-wounds", { targets: ["a"] }), [4, 5]);
    eq(evs(r, "heal")[0].n, 12); eq(C(f, "p").turn.acts, 1);
  });

  // ---------- Wildheart's Remembrance ----------
  const druid = (o) => Object.assign({ body: { STR: 0, DEX: 1, INT: 0, WIL: 3, HP: 10, SPD: 30 }, armor: "A-I-01", hands: ["W-I-05"], aspects: ["N-I-01"] }, o);
  T("[fx] Hawk: Form, action, 1 Resolve: Tiny, Fly 60, 4 HP, Talons +2 1d4 + DEX; no voice", () => {
    const f = fight([pc("d", [1, 5], druid({ aspects: ["N-I-01", "D-I-01"] })), foe("x", [12, 5])]);
    pcTurn(f, "d");
    run(f, power(f, "d", "N-I-01#hawk"));
    const d = C(f, "d");
    const move = () => f.legal("d").find((t) => t.type === "move").left;
    eq([d.size, d.totals.STR, d.totals.DEX, d.totals.STRd, d.totals.DEXd, d.form.hp, move(), d.resolve["N-I-01"]], ["Tiny", -2, 3, 8, 13, 4, 60, 5]);
    eq(d.turn.acts, 1);
    end(f, "d"); skip(f, "x"); go(f, "d");
    run(f, { type: "move", actor: "d", path: [[2, 5], [3, 5], [4, 5], [5, 5], [6, 5], [7, 5], [8, 5], [9, 5], [10, 5], [11, 5]] });
    const i = pv(f, atk("d", "natural", "x"));
    eq([i.toHit, i.damage], [5, "1d4+3 Physical"]);
    ok(!f.legal("d").some((t) => t.power && t.power.startsWith("D-I-01")), "no Divine while shifted");
  });

  T("[fx] Wolf: Form, 2 Resolve: Medium, 8 HP, Speed 40, Bite +2 1d6 + DEX; damage beyond its HP carries over", () => {
    const f = fight([pc("d", [5, 5], druid()), foe("x", [6, 5], { hands: ["W-I-05"] })]);
    pcTurn(f, "d");
    run(f, power(f, "d", "N-I-01#wolf"));
    const d = C(f, "d");
    eq([d.size, d.totals.STR, d.totals.DEX, d.form.hp, f.legal("d").find((t) => t.type === "move").left, d.resolve["N-I-01"]], ["Medium", 1, 3, 8, 40, 4]);
    eq(pv(f, atk("d", "natural", "x")).damage, "1d6+3 Physical");
    end(f, "d"); go(f, "x");
    const r = run(f, atk("x", "W-I-05", "d"), [15, 10]); // 13 damage: 8 off the Form, 5 carry over
    ok(evs(r, "revert").length); eq([C(f, "d").form, C(f, "d").hp], [null, 12 - 5]); // 10 + Leather's 2 HP
  });

  T("[fx] Bear: Form, 3 Resolve: Large, Hide STR Defense 15, 12 HP, Claws +2 1d8 + STR; revert is free; Form to Form", () => {
    const f = fight([pc("d", [5, 5], druid()), foe("x", [7, 5])]);
    pcTurn(f, "d");
    run(f, power(f, "d", "N-I-01#bear"));
    const d = C(f, "d");
    eq([d.size, d.totals.STRd, d.totals.DEXd, d.form.hp, d.resolve["N-I-01"]], ["Large", 15, 11, 12, 3]);
    const i = pv(f, atk("d", "natural", "x"));
    eq([i.toHit, i.damage], [5, "1d8+3 Physical"]);
    run(f, { type: "act", actor: "d", action: "revert" });
    eq([C(f, "d").size, C(f, "d").totals.STRd, C(f, "d").form], ["Medium", 12, null]);
    end(f, "d"); skip(f, "x"); go(f, "d");
    run(f, power(f, "d", "N-I-01#wolf"));
    ok(f.preview(power(f, "d", "N-I-01#hawk")).ok, "Form to Form with the second action");
    end(f, "d"); skip(f, "x"); go(f, "d");
    ok(/not enough Resolve/.test(refused(f, power(f, "d", "N-I-01#bear"))), "3 + 2 spent of 6: 1 left");
    run(f, power(f, "d", "N-I-01#hawk"));
    eq([C(f, "d").form.name, C(f, "d").form.hp, C(f, "d").resolve["N-I-01"]], ["Hawk", 4, 0]);
  });

  T("[fx] Mossbalm: Mend, action, 2 Resolve, touch, 2d8 + WIL; no voice needed, not while shifted", () => {
    const f = fight([pc("d", [1, 5], druid()), pc("a", [2, 5]), foe("x", [20, 5])]);
    run(f, { type: "adjust", actor: "a", hp: 1 });
    pcTurn(f, "d");
    const r = run(f, power(f, "d", "N-I-01#mossbalm", { targets: ["a"] }), [2, 3]);
    eq(evs(r, "heal")[0].n, 8); eq(C(f, "d").resolve["N-I-01"], 4);
    run(f, power(f, "d", "N-I-01#hawk"));
    ok(!f.legal("d").some((t) => t.power === "N-I-01#mossbalm"), "shifted");
  });

  // ---------- Ogre Chieftain ----------
  T("[fx] Ogre Chieftain Bellow: reaction, Recharge 5–6, +5 vs WIL of each enemy within 30 ft, Frightened until the end of its next turn; on a half turn too", () => {
    const f = fight([pc("a", [3, 5]), pc("b", [3, 8]), pc("c", [14, 12]), tmpl("boss", "Ogre Chieftain", [5, 5])]);
    eq([C(f, "boss").maxHp, C(f, "boss").totals.SPD], [70, 30]);
    start(f);
    go(f, "a"); end(f, "a");
    run(f, { type: "beginTurn", actor: "boss", half: true });
    ok(f.legal("boss").some((t) => t.power === "foe-ogre-chieftain#0"), "its reaction works on a half turn");
    end(f, "boss");
    skip(f, "b"); skip(f, "c");
    run(f, { type: "beginTurn", actor: "boss" }); // ready at the start of the fight: no recharge roll
    const r = run(f, power(f, "boss", "foe-ogre-chieftain#0"), [6]); // 11 vs WIL 10
    eq(evs(r, "roll").length, 1); ok(has(C(f, "a"), "Frightened") && has(C(f, "b"), "Frightened")); ok(!has(C(f, "c"), "Frightened"), "out of 30 ft");
    eq(C(f, "boss").uses["foe-ogre-chieftain#0"], 0);
    eq([C(f, "boss").turn.reaction, C(f, "boss").turn.acts], [true, 2], "it spends its reaction, not an action");
    const e = end(f, "boss", [5]); // Recharge rolled at the end of its turn: a 5, ready again
    ok(evs(e, "roll").some((x) => x.kind === "recharge")); eq(C(f, "boss").uses["foe-ogre-chieftain#0"], 1);
  });

};
