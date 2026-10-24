// Morale (P 6.11, RULING R800): a Leader falling, and half of the foe group down or fled, make each remaining
// non-Boss foe roll d20 + WIL vs 10; a failure flees (leaves the fight, counts as defeated).
// Loaded by sim/test/run.js: module.exports(T, H) registers the tests with the runner's helpers.
"use strict";
module.exports = function register(T, H) {
  const { Eng, eq, ok, run, start, C, evs } = H;
  const CARDS = () => H.cards();
  const B = (o) => Object.assign({ core: "C-I-01", armor: null, hands: [], carried: [], jewelry: [], items: [], aspects: [] }, o);
  const pc = (id, pos, build, o) => Object.assign({ id, side: "pc", name: id, pos, build: B(build), react: "never" }, o);
  const tmpl = (id, name, pos, o) => Object.assign({ id, side: "foe", name: id, pos, build: Eng.fromFoe(CARDS().foes.find((f) => f.name === name), CARDS()), react: "never" }, o);
  const fight = (cs) => Eng.createFight({ version: 1, name: "morale", seed: 4, map: { w: 24, h: 14, cells: {} }, surprise: null, creatures: cs }, CARDS());
  const morale = (r) => evs(r, "roll").filter((e) => e.kind === "morale");
  const drop = (f, id, script) => run(f, { type: "adjust", actor: id, hp: 0 }, script);

  T("[morale] the Bandit Captain and the Ogre Chieftain are Leaders; fromFoe copies the flag", () => {
    const foes = CARDS().foes.filter((f) => f.leader).map((f) => f.name);
    eq(foes, ["Bandit Captain", "Ogre Chieftain"]);
    ok(Eng.fromFoe(CARDS().foes.find((f) => f.name === "Bandit Captain"), CARDS()).leader);
    ok(!Eng.fromFoe(CARDS().foes.find((f) => f.name === "Bandit"), CARDS()).leader);
  });

  T("[morale] the Leader falls: each remaining foe rolls WIL vs 10; a failure flees and counts as defeated", () => {
    const f = fight([pc("a", [2, 2], { hands: ["W-I-05"] }), tmpl("cap", "Bandit Captain", [20, 2]), tmpl("b1", "Bandit", [20, 5]),
      tmpl("b2", "Bandit", [20, 8]), tmpl("b3", "Bandit", [20, 11]), tmpl("b4", "Bandit", [18, 11])]);
    start(f);
    // WIL +0: 9 fails, 10 holds, 15 holds, 1 fails; then 3 of 5 are down or fled: the half trigger, at once (12, 12 hold)
    const r = drop(f, "cap", [9, 10, 15, 1, 12, 12]);
    eq(evs(r, "morale").map((e) => e.why), ["a Leader falls", "half of the group is down"]);
    eq(morale(r).map((e) => [e.actor, e.total, e.vs]), [["b1", 9, 10], ["b2", 10, 10], ["b3", 15, 10], ["b4", 1, 10], ["b2", 12, 10], ["b3", 12, 10]]);
    eq(evs(r, "flee").map((e) => e.actor), ["b1", "b4"]);
    ok(C(f, "b1").fled && C(f, "b1").dead && C(f, "b1").hp > 0, "fled: out of the fight with its HP");
    ok(C(f, "b1").hands.length && !f.state.ground.some((g) => g.owner === "b1"), "it takes its gear");
    ok(!C(f, "b2").fled);
    const s = f.summary().creatures;
    eq([s.b1.fled, s.b2.fled, s.a.kills], [true, false, 0]);
    ok(Eng.summaryCsv(f.summary()).split("\n")[0].endsWith(",fled"));
  });

  T("[morale] fleeing counts toward half the group; each trigger fires once per fight", () => {
    const f = fight([pc("a", [2, 2]), tmpl("cap", "Bandit Captain", [20, 2]), tmpl("b1", "Bandit", [20, 5]), tmpl("b2", "Bandit", [20, 8]), tmpl("b3", "Bandit", [20, 11])]);
    start(f);
    // Leader falls (1 of 4): b1 flees (2 of 4 = half): b2 and b3 check again
    const r = drop(f, "cap", [2, 12, 12, 12, 13]);
    eq(evs(r, "morale").map((e) => e.why), ["a Leader falls", "half of the group is down"]);
    eq(morale(r).map((e) => e.actor), ["b1", "b2", "b3", "b2", "b3"]);
    eq([f.state.morale.leader, f.state.morale.half], [true, true]);
    const r2 = drop(f, "b2");
    eq(morale(r2).length, 0, "no trigger left");
    eq(f.state.phase, "fight");
  });

  T("[morale] half the group down without a Leader; a lone Bandit's failure ends the fight", () => {
    const f = fight([pc("a", [2, 2]), tmpl("w1", "Wolf", [20, 2]), tmpl("w2", "Wolf", [20, 5]), tmpl("w3", "Wolf", [20, 8])]);
    start(f);
    eq(morale(drop(f, "w1")).length, 0, "1 of 3: below half");
    const r = drop(f, "w2", [11]); // 2 of 3 (half rounded up): w3 rolls 11 − 2 = 9: flees
    eq(morale(r).map((e) => [e.actor, e.total]), [["w3", 9]]);
    ok(C(f, "w3").fled);
    eq([f.state.phase, f.state.winner], ["over", "pc"], "no able foe remains");
  });

  T("[morale] a Boss never checks; the Chieftain is a Leader", () => {
    const f = fight([pc("a", [2, 2]), tmpl("boss", "Ogre Chieftain", [18, 2]), tmpl("b1", "Bandit", [20, 8]), tmpl("b2", "Bandit", [20, 11])]);
    start(f);
    const r = drop(f, "b1"); // 1 of 3: nothing
    eq(morale(r).length, 0);
    const r2 = drop(f, "b2"); // 2 of 3: half, but the Boss doesn't check
    eq(evs(r2, "morale").length, 1); eq(morale(r2).length, 0);
    const g = fight([pc("a", [2, 2]), tmpl("boss", "Ogre Chieftain", [18, 2]), tmpl("b1", "Bandit", [20, 8]), tmpl("b2", "Bandit", [20, 11]), tmpl("b3", "Bandit", [18, 11])]);
    start(g);
    const r3 = drop(g, "boss", [10, 10, 10]); // the Leader falls: the three Bandits check
    eq(morale(r3).map((e) => e.actor), ["b1", "b2", "b3"]);
  });

  T("[morale] a foe that flees on its own turn ends it; the UI-facing state stays consistent", () => {
    const f = fight([pc("a", [10, 5], { hands: ["W-I-05"] }, { react: "auto" }), tmpl("cap", "Bandit Captain", [20, 2]), tmpl("b1", "Bandit", [11, 5])]);
    start(f, "foe");
    run(f, { type: "adjust", actor: "cap", hp: 1 });
    run(f, { type: "beginTurn", actor: "b1" });
    run(f, { type: "adjust", actor: "cap", hp: 0 }, [3]); // the Captain falls during b1's turn: b1 fails and flees
    ok(C(f, "b1").fled);
    eq(f.state.phase, "over", "only fled and fallen foes left");
    eq(f.state.active, null);
  });
};
