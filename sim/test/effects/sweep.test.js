// Sweeping Blow (Q-II-02, hook "sweep"): the Attack action as one area roll against each enemy within reach.
// Loaded by sim/test/run.js: module.exports(T, H) registers the tests with the runner's helpers.
"use strict";
module.exports = function register(T, H) {
  const { Eng, eq, ok, run, refused, start, C, evs } = H;
  const CARDS = () => H.cards();
  const B = (o) => Object.assign({ core: "C-I-01", armor: null, hands: [], carried: [], jewelry: [], items: [], aspects: [] }, o);
  const pc = (id, pos, build, o) => Object.assign({ id, side: "pc", name: id, pos, build: B(build), react: "never" }, o);
  const tmpl = (id, name, pos, o) => Object.assign({ id, side: "foe", name: id, pos, build: Eng.fromFoe(CARDS().foes.find((f) => f.name === name), CARDS()), react: "never" }, o);
  const fight = (cs) => Eng.createFight({ version: 1, name: "sweep", seed: 3, map: { w: 20, h: 14, cells: {} }, surprise: null, creatures: cs }, CARDS());
  const skip = (f, id) => { run(f, { type: "beginTurn", actor: id }); if (f.state.active === id) run(f, { type: "endTurn", actor: id }); };
  // pcs go first and skip; then `id` begins.
  const foeTurn = (f, id) => { start(f); for (const c of Object.values(f.state.creatures)) if (c.side === "pc" && !c.dead) skip(f, c.id); run(f, { type: "beginTurn", actor: id }); };
  const pcTurn = (f, id) => { start(f, "foe"); for (const c of Object.values(f.state.creatures)) if (c.side === "foe" && !c.dead) skip(f, c.id); run(f, { type: "beginTurn", actor: id }); };
  const has = (c, name) => c.conds.some((k) => k.name === name);
  const SWEEP = "Q-II-02#0";
  const sweep = (actor, o) => Object.assign({ type: "power", actor, power: SWEEP }, o);
  const dmgOf = (r, id) => evs(r, "damage").filter((e) => e.target === id).map((e) => e.n);
  // Ogre at 6,5 (2×2) with Bearers of STR Defense 13 (a), 16 (b, Mail), 17 (c, Plate) around it and d out of reach.
  const ring = () => fight([pc("a", [5, 5]), pc("b", [8, 5], { armor: "A-I-02" }), pc("c", [6, 7], { armor: "A-II-01" }), pc("d", [12, 10]), tmpl("o", "Ogre", [6, 5])]);

  T("[sweep] Ogre carries Sweeping Blow; one roll, no Outnumbered dice, compared to each Defense in reach", () => {
    const f = ring();
    ok(Eng.validate(f.state.creatures.o.build, CARDS()).every((e) => /^Warning/.test(e)), "Ogre build valid");
    foeTurn(f, "o");
    const plain = f.preview({ type: "attack", actor: "o", weapon: "W-I-13", target: "a" }).info;
    eq(plain.dis, 2, "a normal attack: Outnumbered 1 vs 3");
    const t = f.legal("o").find((x) => x.power === SWEEP);
    ok(t && !t.target && !t.targets, "offered as a power with no target to pick");
    const info = f.preview(sweep("o")).info;
    eq([info.toHit, info.dice, info.dis, info.targets, info.defense], [6, 1, 0, ["a", "b", "c"], "a 13, b 16, c 17"]);
    const r = run(f, sweep("o"), [10, 3, 4]); // 16: hits a and b, misses c; one damage roll 2d10 + 4 = 11
    eq(evs(r, "roll").length, 1, "one attack roll");
    eq(evs(r, "roll")[0].dice.length, 1, "no Outnumbered dice");
    eq([dmgOf(r, "a"), dmgOf(r, "b"), dmgOf(r, "c"), dmgOf(r, "d")], [[11], [11], [5], []], "half (rounded down) on a miss");
    const s = f.summary().creatures.o;
    eq([s.attacks, s.hits], [1, 2]);
  });

  T("[sweep] a natural 20 crits every target: shared doubled dice, Crushing knocks each one Prone", () => {
    const f = ring();
    foeTurn(f, "o");
    const r = run(f, sweep("o"), [20, 1, 1, 1, 1]); // 4d10 + 4 = 8
    eq([dmgOf(r, "a"), dmgOf(r, "b"), dmgOf(r, "c")], [[8], [8], [8]]);
    ok(["a", "b", "c"].every((id) => has(C(f, id), "Prone")) && !has(C(f, "d"), "Prone"));
    f.undo();
    const r2 = run(f, sweep("o"), [1, 5, 5]); // a natural 1 misses all: half of 14
    eq([dmgOf(r2, "a"), dmgOf(r2, "b"), dmgOf(r2, "c")], [[7], [7], [7]]);
  });

  T("[sweep] uses the whole Attack action; only a held Heavy or Reach melee weapon; Reach sweeps 10 ft", () => {
    const f = ring();
    foeTurn(f, "o");
    run(f, sweep("o"), [10, 3, 4]);
    ok(!C(f, "o").turn.attacksLeft && C(f, "o").turn.attackAction);
    refused(f, { type: "attack", actor: "o", weapon: "W-I-13", target: "a" });
    refused(f, sweep("o"));
    // attack first, then no sweep
    const g = ring();
    foeTurn(g, "o");
    run(g, { type: "attack", actor: "o", weapon: "W-I-13", target: "a" }, [1, 1, 1]);
    ok(!g.legal("o").some((x) => x.power === SWEEP), "the action is spent");
    // Twin Strike + Glaive (Heavy, Reach): one roll, no second attack; an enemy 10 ft away is in the sweep
    const T2 = () => fight([pc("p", [5, 5], { hands: ["W-I-08"], aspects: ["Q-II-01", "Q-II-02"] }), tmpl("x", "Bandit", [6, 5]), tmpl("y", "Bandit", [7, 5]), tmpl("z", "Bandit", [5, 8])]);
    const h = T2();
    pcTurn(h, "p");
    eq(h.preview(sweep("p")).info.targets, ["x", "y"], "x at 5 ft, y at 10 ft; z at 15 ft is out");
    run(h, sweep("p"), [2, 1]);
    refused(h, { type: "attack", actor: "p", weapon: "W-I-08", target: "x" });
    // Longsword: not offered, refused
    const k = fight([pc("p", [5, 5], { hands: ["W-I-05"], aspects: ["Q-II-02"] }), tmpl("x", "Bandit", [6, 5]), tmpl("y", "Bandit", [5, 6])]);
    pcTurn(k, "p");
    ok(!k.legal("p").some((x) => x.power === SWEEP));
    ok(/Heavy or Reach/.test(refused(k, sweep("p"))));
  });

  T("[sweep] allies and enemies at 0 HP are left out unless named; no enemy in reach: not offered", () => {
    const f = fight([pc("a", [5, 5]), pc("b", [8, 5]), tmpl("o", "Ogre", [6, 5]), tmpl("g", "Bandit", [6, 7])]);
    foeTurn(f, "o");
    run(f, { type: "adjust", actor: "b", hp: 0 });
    eq(f.preview(sweep("o")).info.targets, ["a"], "the Bandit ally and b at 0 HP are out");
    eq(f.preview(sweep("o", { targets: ["a", "b"] })).info.targets, ["a", "b"]);
    ok(!f.preview(sweep("o", { targets: ["g"] })).ok, "an ally can't be named");
    const g = fight([pc("a", [12, 5]), tmpl("o", "Ogre", [6, 5])]);
    foeTurn(g, "o");
    ok(!g.legal("o").some((x) => x.power === SWEEP));
  });
};
