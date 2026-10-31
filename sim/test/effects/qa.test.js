// Regression tests for the QA report (sim/QA.md, agent E): one per engine bug fixed, real cards.
"use strict";
module.exports = function register(T, H) {
  const { Eng, eq, ok, run, refused, start, C, evs } = H;
  const CARDS = () => H.cards();
  const B = (o) => Object.assign({ body: { STR: 3, DEX: 1, INT: 0, WIL: 0, HP: 14, SPD: 30 }, armor: null, hands: [], carried: [], jewelry: [], items: [], aspects: [] }, o);
  const pc = (id, pos, build, o) => Object.assign({ id, side: "pc", name: id, pos, build: B(build), react: "never" }, o);
  const foe = (id, pos, build, o) => Object.assign({ id, side: "foe", name: id, pos, build: B(build), react: "never" }, o);
  const tmpl = (id, name, pos, o) => Object.assign({ id, side: "foe", name: id, pos, build: Eng.fromFoe(CARDS().foes.find((f) => f.name === name), CARDS()), react: "never" }, o);
  const fight = (cs, o) => { o = o || {}; return Eng.createFight({ version: 1, name: "qa", seed: 5, map: { w: 30, h: 14, cells: o.cells || {} }, surprise: null, creatures: cs }, CARDS()); };
  const skip = (f, id, script, endScript) => { run(f, { type: "beginTurn", actor: id }, script); if (f.state.active === id) run(f, { type: "endTurn", actor: id }, endScript); };
  const has = (c, name) => c.conds.some((k) => k.name === name);
  // Every living creature of the active side skips its turn.
  const side = (f) => { const s = f.state.side; for (const c of Object.values(f.state.creatures)) if (c.side === s && !c.dead && !f.state.done.includes(c.id) && f.state.side === s) skip(f, c.id); };

  T("[qa B1] Durations keep counting after their source dies (Bless, Grease)", () => {
    const f = fight([pc("p", [1, 1], { body: { STR: 0, DEX: 1, INT: 0, WIL: 3, HP: 10, SPD: 30 }, aspects: ["D-I-01"] }), pc("w", [1, 3], { body: { STR: 0, DEX: 1, INT: 3, WIL: 0, HP: 9, SPD: 30 }, items: [{ id: "B-I-01" }] }), pc("a", [2, 1]), foe("x", [20, 10])]);
    start(f);
    run(f, { type: "beginTurn", actor: "p" }); run(f, { type: "power", actor: "p", power: "D-I-01#bless" }); run(f, { type: "endTurn", actor: "p" });
    run(f, { type: "beginTurn", actor: "w" }); run(f, { type: "power", actor: "w", power: "B-I-01#grease", point: [8, 8] }); run(f, { type: "endTurn", actor: "w" });
    run(f, { type: "adjust", actor: "p", dead: true }); run(f, { type: "adjust", actor: "w", dead: true });
    ok(C(f, "a").mods.length && f.state.zones.length);
    let r = 0;
    while (f.state.round < 13 && r++ < 40) side(f);
    ok(!C(f, "a").mods.length, "Bless ended"); eq(f.state.zones.length, 0, "Grease ended");
  });

  T("[qa B2/B15] A zone attacks with its source's bare bonus (no Bless), and still attacks after the caster dies", () => {
    const f = fight([pc("p", [1, 3], { body: { STR: 0, DEX: 1, INT: 0, WIL: 3, HP: 10, SPD: 30 }, aspects: ["D-I-01"] }), pc("w", [1, 5], { body: { STR: 0, DEX: 1, INT: 3, WIL: 0, HP: 9, SPD: 30 }, items: [{ id: "B-I-01" }] }), foe("x", [12, 5])]);
    start(f);
    run(f, { type: "beginTurn", actor: "p" }); run(f, { type: "power", actor: "p", power: "D-I-01#bless" }); run(f, { type: "endTurn", actor: "p" });
    ok(C(f, "w").mods.some((m) => m.dice === "1d4"));
    run(f, { type: "beginTurn", actor: "w" }); run(f, { type: "power", actor: "w", power: "B-I-01#grease", point: [8, 5] }); run(f, { type: "endTurn", actor: "w" });
    run(f, { type: "beginTurn", actor: "x" });
    const r = run(f, { type: "move", actor: "x", path: [[11, 5], [10, 5], [9, 5]] }, [5]); // no Bless d4 rolled
    eq(evs(r, "roll")[0].bonus, 5, "INT 3 + 2");
    run(f, { type: "endTurn", actor: "x" });
    run(f, { type: "adjust", actor: "w", dead: true });
    skip(f, "p");
    run(f, { type: "beginTurn", actor: "x" });
    const r2 = run(f, { type: "move", actor: "x", path: [[10, 5], [9, 5]] }, [1]);
    eq(evs(r2, "roll").length, 1, "a dead caster's zone still attacks");
  });

  T("[qa B3] Frightened ends when its source dies", () => {
    const f = fight([pc("a", [3, 5]), pc("b", [3, 9]), tmpl("boss", "Ogre Chieftain", [5, 5])]);
    start(f, "foe");
    run(f, { type: "beginTurn", actor: "boss" }); run(f, { type: "power", actor: "boss", power: "foe-ogre-chieftain#0" }, [10]);
    ok(has(C(f, "a"), "Frightened"));
    run(f, { type: "adjust", actor: "boss", dead: true });
    ok(!has(C(f, "a"), "Frightened"));
  });

  T("[qa B4] Web holds an ally (and its caster) too, for 2 of their turns, with no maintain roll", () => {
    const f = fight([pc("w", [7, 5], { body: { STR: 0, DEX: 1, INT: 3, WIL: 0, HP: 9, SPD: 30 }, items: [{ id: "B-I-01" }] }), pc("a", [8, 6]), foe("x", [9, 5])]);
    start(f);
    run(f, { type: "beginTurn", actor: "w" }); run(f, { type: "power", actor: "w", power: "B-I-01#web", point: [8, 5] }, [15]);
    for (const id of ["w", "a", "x"]) ok(C(f, id).conds.some((k) => k.name === "Restrained" && !k.lasting), id);
    run(f, { type: "endTurn", actor: "w" });
    const r = run(f, { type: "beginTurn", actor: "a" });
    eq(evs(r, "maintain").length, 0); ok(has(C(f, "a"), "Restrained"));
  });

  T("[qa B5] Half turn: no Recharge roll, the reaction stays spent", () => {
    const f = fight([pc("a", [3, 5]), pc("b", [3, 12]), tmpl("boss", "Ogre Chieftain", [4, 5], { react: "auto" })]);
    start(f, "foe");
    run(f, { type: "beginTurn", actor: "boss" }); run(f, { type: "power", actor: "boss", power: "foe-ogre-chieftain#0" }, [1]); run(f, { type: "endTurn", actor: "boss" }, [2]);
    eq(C(f, "boss").uses["foe-ogre-chieftain#0"], 0, "a 2 at the end of its turn: not back");
    run(f, { type: "beginTurn", actor: "a" });
    ok(C(f, "boss").turn.reaction, "Bellow took its reaction");
    run(f, { type: "endTurn", actor: "a" });
    const r = run(f, { type: "beginTurn", actor: "boss", half: true });
    eq(evs(r, "roll").length, 0, "no Recharge roll"); ok(C(f, "boss").turn.reaction, "reaction still spent");
    eq(evs(run(f, { type: "endTurn", actor: "boss" }), "roll").length, 0, "nor at the end of the half turn");
  });

  T("[qa B7] A power hit within 5 ft on an Unconscious creature is logged and counted as a crit", () => {
    const f = fight([pc("a", [5, 5]), pc("b", [20, 12]), tmpl("w", "Wolf", [6, 5])]);
    run(f, { type: "adjust", actor: "a", hp: 0 });
    start(f, "foe");
    run(f, { type: "beginTurn", actor: "w" });
    const r = run(f, { type: "power", actor: "w", power: "foe-wolf#0", targets: ["a"] }, [15, 15, 2, 2]); // Target: Prone and Stunned count once; no Outnumbered against a downed target (R223): 2d20
    ok(evs(r, "crit").length === 1); eq(f.summary().creatures.w.crits, 1); eq(C(f, "a").death.fail, 2);
  });

  T("[qa B8] Beasts without Hand gear have no Hands: no pick up, no draw", () => {
    const f = fight([pc("a", [5, 5], { hands: ["W-I-05"] }), pc("b", [20, 12]), tmpl("w", "Wolf", [6, 5])]);
    eq(C(f, "w").build.slots.hand, 0);
    run(f, { type: "adjust", actor: "a", hp: 0 });
    start(f, "foe");
    run(f, { type: "beginTurn", actor: "w" });
    ok(f.state.ground.length === 1, "a dropped its sword");
    ok(!f.legal("w").some((t) => t.type === "interact"));
    ok(/No free Hand/.test(refused(f, { type: "interact", actor: "w", draw: "W-I-05" })));
  });

  T("[qa B9] Adjusting a Bearer to 0 HP makes it Unconscious; a foe dies", () => {
    const f = fight([pc("a", [5, 5]), foe("x", [9, 5]), foe("y", [12, 5])]);
    run(f, { type: "adjust", actor: "a", hp: 0 });
    ok(has(C(f, "a"), "Unconscious") && C(f, "a").down);
    run(f, { type: "adjust", actor: "x", hp: 0 });
    ok(C(f, "x").dead);
  });

  T("[qa B10] Fire burns one 5-ft square of Web a round, even on a Large creature", () => {
    const f = fight([pc("w", [1, 5], { body: { STR: 0, DEX: 1, INT: 3, WIL: 0, HP: 9, SPD: 30 }, items: [{ id: "B-I-01" }] }), pc("v", [1, 8], { body: { STR: 0, DEX: 1, INT: 3, WIL: 0, HP: 9, SPD: 30 }, items: [{ id: "B-I-01" }] }), tmpl("o", "Ogre", [8, 5])]);
    start(f);
    run(f, { type: "beginTurn", actor: "w" }); run(f, { type: "power", actor: "w", power: "B-I-01#web", point: [8, 5] }, [15]); run(f, { type: "endTurn", actor: "w" });
    run(f, { type: "beginTurn", actor: "v" });
    run(f, { type: "power", actor: "v", power: "B-I-01#fire-bolt", targets: ["o"] }, [15, 15, 1]);
    eq(f.state.zones[0].cells.length, 15); ok(has(C(f, "o"), "Restrained"), "still in 3 webbed squares");
  });

  T("[qa B11] Ring of Sparks answers a ranged hit from within 5 ft", () => {
    const f = fight([pc("a", [5, 5], { jewelry: ["J-II-01"] }, { react: "auto" }), foe("s", [6, 5], { body: { STR: 0, DEX: 3, INT: 1, WIL: 0, HP: 11, SPD: 35 }, hands: ["W-I-10"] })]);
    start(f, "foe");
    run(f, { type: "beginTurn", actor: "s" });
    run(f, { type: "attack", actor: "s", weapon: "W-I-10", target: "a" }, [18, 18, 3, 3, 1]);
    eq(C(f, "s").hp, 11 - 6);
  });

  T("[qa B12] The Boss half turn comes between two characters' turns", () => {
    const f = fight([pc("a", [3, 5]), pc("b", [3, 12]), tmpl("boss", "Ogre Chieftain", [8, 5])]);
    start(f);
    ok(/between two/.test(refused(f, { type: "beginTurn", actor: "boss", half: true })));
    ok(!f.legal("boss").some((t) => t.half));
    run(f, { type: "beginTurn", actor: "a" }); run(f, { type: "endTurn", actor: "a" });
    ok(f.legal("boss").some((t) => t.half));
  });

  T("[qa B13] Cleave: another creature, at once (moving forfeits it)", () => {
    const f = fight([pc("a", [5, 5], { hands: ["W-I-05"], aspects: ["Q-I-01"] }, { react: "auto" }), foe("x", [6, 5]), foe("y", [5, 6])]);
    run(f, { type: "adjust", actor: "x", hp: 1 });
    start(f, "foe");
    for (const id of ["x", "y"]) skip(f, id);
    run(f, { type: "beginTurn", actor: "a" });
    run(f, { type: "attack", actor: "a", weapon: "W-I-05", target: "x" }, [15, 15, 1, 15]); // 1 vs 2: disadvantage; y's morale holds
    ok(C(f, "x").dead); eq(C(f, "a").turn.bonusMelee, 1);
    run(f, { type: "move", actor: "a", path: [[4, 5]] });
    eq(C(f, "a").turn.bonusMelee, 0, "moving forfeits it");
  });

  T("[qa B14] Dice mods (Bless, Bane) are listed in the attack's why", () => {
    const f = fight([pc("p", [1, 5], { body: { STR: 0, DEX: 1, INT: 0, WIL: 3, HP: 10, SPD: 30 }, aspects: ["D-I-01"] }), pc("a", [5, 5], { hands: ["W-I-05"] }), foe("x", [6, 5])]);
    start(f);
    run(f, { type: "beginTurn", actor: "p" }); run(f, { type: "power", actor: "p", power: "D-I-01#bless" }); run(f, { type: "endTurn", actor: "p" });
    run(f, { type: "beginTurn", actor: "a" });
    ok(f.preview({ type: "attack", actor: "a", weapon: "W-I-05", target: "x" }).info.why.some((w) => /\+1d4 Bless/.test(w)));
  });

  T("[qa B16] An area roll doesn't depend on which target is listed first", () => {
    const cells = { "8,5": "dark" };
    const f = fight([pc("a", [3, 5], { body: { STR: 0, DEX: 3, INT: 1, WIL: 0, HP: 11, SPD: 35 }, items: [{ id: "R-II-01" }] }), foe("x", [8, 5]), foe("y", [8, 6])], { cells });
    start(f);
    run(f, { type: "beginTurn", actor: "a" });
    const i = f.preview({ type: "power", actor: "a", power: "R-II-01#0", point: [8, 6] }).info;
    ok(!i.why.some((w) => /can't see/.test(w)), JSON.stringify(i.why)); eq(i.dice, 1);
  });

  T("[qa B17] Resolve has no plural", () => {
    const f = fight([pc("d", [5, 5], { body: { STR: 0, DEX: 1, INT: 0, WIL: 3, HP: 10, SPD: 30 }, aspects: ["N-I-01"] }), foe("x", [12, 5])]);
    start(f);
    run(f, { type: "beginTurn", actor: "d" });
    eq(f.preview({ type: "power", actor: "d", power: "N-I-01#bear" }).info.cost, "3 Resolve");
    const r = run(f, { type: "power", actor: "d", power: "N-I-01#bear" });
    ok(r.events.some((e) => e.text === "d spends 3 Resolve."));
  });
};
