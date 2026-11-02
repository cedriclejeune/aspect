// Classic foes and the cards added with them: Relentless, Regeneration, Undead, Dancer's Bells, Rousing Verse.
// Loaded by sim/test/run.js: module.exports(T, H) registers the tests with the runner's helpers.
"use strict";
module.exports = function register(T, H) {
  const { Eng, eq, ok, run, start, C, evs } = H;
  const CARDS = () => H.cards();
  const B = (o) => Object.assign({ body: { STR: 3, DEX: 1, INT: 0, WIL: 0, HP: 14, SPD: 30 }, armor: null, hands: [], carried: [], jewelry: [], items: [], aspects: [] }, o);
  const pc = (id, pos, build, o) => Object.assign({ id, side: "pc", name: id, pos, build: B(build), react: "never" }, o);
  const tmpl = (id, name, pos, o) => Object.assign({ id, side: "foe", name: id, pos, build: Eng.fromFoe(CARDS().foes.find((f) => f.name === name), CARDS()), react: "never" }, o);
  const fight = (cs) => Eng.createFight({ version: 1, name: "monsters", seed: 5, map: { w: 30, h: 14, cells: {} }, surprise: null, creatures: cs }, CARDS());
  const skip = (f, id) => { run(f, { type: "beginTurn", actor: id }); if (f.state.active === id) run(f, { type: "endTurn", actor: id }); };
  const pcTurn = (f, id) => { start(f, "foe"); for (const c of Object.values(f.state.creatures)) if (c.side === "foe" && !c.dead) skip(f, c.id); run(f, { type: "beginTurn", actor: id }); };
  const atk = (actor, weapon, target) => ({ type: "attack", actor, weapon, target });

  T("[foes] Relentless: the Zombie drops to 1 HP once per fight, then falls", () => {
    const f = fight([pc("a", [5, 5], { hands: ["W-I-16"] }), tmpl("z", "Zombie", [6, 5])]); // Greataxe 1d12 + 3
    pcTurn(f, "a");
    run(f, atk("a", "W-I-16", "z"), [15, 12]);
    const r = run(f, atk("a", "W-I-16", "z"), [15, 12]);
    ok(evs(r, "note").some((e) => /Relentless/.test(e.text)));
    eq([C(f, "z").hp, C(f, "z").dead], [1, false]);
    run(f, { type: "endTurn", actor: "a" }); skip(f, "z"); run(f, { type: "beginTurn", actor: "a" });
    run(f, atk("a", "W-I-16", "z"), [15, 1]);
    eq(C(f, "z").hp, 0, "the second hit kills it");
    ok(C(f, "z").dead);
    const g = fight([pc("a", [5, 5], { hands: ["W-I-16"] }), tmpl("z", "Zombie", [6, 5])]);
    pcTurn(g, "a");
    run(g, atk("a", "W-I-16", "z"), [15, 12]);
    eq([C(g, "z").hp, C(g, "z").dead], [5, false], "15 of 20");
  });

  T("[foes] Regeneration: the Troll regains 10 HP at the start of its turn, not after Fire", () => {
    const f = fight([pc("a", [5, 5], { hands: ["W-I-16"] }), tmpl("t", "Troll", [6, 5])]);
    pcTurn(f, "a");
    run(f, atk("a", "W-I-16", "t"), [15, 12]);
    eq(C(f, "t").hp, 65);
    run(f, { type: "endTurn", actor: "a" });
    run(f, { type: "beginTurn", actor: "t" });
    eq(C(f, "t").hp, 75);
    // Fire stops it for one turn
    const g = fight([pc("a", [5, 5], { body: { STR: 0, DEX: 3, INT: 1, WIL: 0, HP: 11, SPD: 35 }, items: [{ id: "R-II-01" }] }), tmpl("t", "Troll", [10, 5])]);
    pcTurn(g, "a");
    run(g, { type: "power", actor: "a", power: "R-II-01#0", point: [10, 5] }, [15, 6, 6]);
    eq(C(g, "t").hp, 68, "2d6 Fire");
    run(g, { type: "endTurn", actor: "a" });
    run(g, { type: "beginTurn", actor: "t" });
    eq(C(g, "t").hp, 68, "no regeneration after Fire");
    run(g, { type: "endTurn", actor: "t" });
    skip(g, "a");
    run(g, { type: "beginTurn", actor: "t" });
    eq(C(g, "t").hp, 78, "back the turn after");
  });

  T("[foes] Undead: resists Poison, vulnerable to Radiant, never checks Morale", () => {
    const sk = Eng.fromFoe(CARDS().foes.find((f) => f.name === "Skeleton"), CARDS());
    const und = sk.ownFx.find((p) => p.name === "Undead");
    eq([und.resist, und.vuln, und.fearless], [["Poison", "Necrotic"], ["Radiant"], true]);
    const f = fight([pc("a", [2, 2]), tmpl("s1", "Skeleton", [20, 2]), tmpl("s2", "Skeleton", [20, 5])]);
    start(f);
    const r = run(f, { type: "adjust", actor: "s1", hp: 0 });
    eq(evs(r, "roll").filter((e) => e.kind === "morale").length, 0, "half down, no one left to check");
    eq(evs(r, "flee").length, 0);
  });

  T("[fx] Dancer's Bells: Dirges reach 90 ft; 1 extra Resolve. Rousing Verse heals 2d4 + WIL at 60 ft", () => {
    const f = fight([pc("e", [1, 5], { body: { STR: 0, DEX: 1, INT: 0, WIL: 3, HP: 10, SPD: 30 }, jewelry: ["J-I-05"], aspects: ["G-I-01"] }), pc("a", [12, 5]), tmpl("x", "Bandit", [18, 5])]);
    eq(C(f, "e").resolve, 7, "3 + WIL 3 + 1");
    pcTurn(f, "e");
    ok(f.preview({ type: "power", actor: "e", power: "G-I-01#jeer", targets: ["x"] }).ok, "85 ft: in reach with the Bells");
    run(f, { type: "adjust", actor: "a", hp: 4 });
    const r = run(f, { type: "power", actor: "e", power: "G-I-01#rousing-verse", targets: ["a"] }, [2, 3]);
    eq(evs(r, "heal").map((e) => e.n), [8], "2d4 (2 + 3) + WIL 3");
    eq(C(f, "e").resolve, 5);
    const g = fight([pc("e", [1, 5], { body: { STR: 0, DEX: 1, INT: 0, WIL: 3, HP: 10, SPD: 30 }, aspects: ["G-I-01"] }), tmpl("x", "Bandit", [18, 5])]);
    pcTurn(g, "e");
    ok(!g.preview({ type: "power", actor: "e", power: "G-I-01#jeer", targets: ["x"] }).ok, "60 ft without them");
  });
};
