// Morale (P 6.11, RULING R800): a Leader falling, and half of the foe group down or fled, make the group roll once:
// d20 + the best WIL among its remaining non-Boss foes vs 10; on a failure they all flee (leave the fight, count as
// defeated).
// Loaded by sim/test/run.js: module.exports(T, H) registers the tests with the runner's helpers.
"use strict";
module.exports = function register(T, H) {
  const { Eng, eq, ok, run, start, C, evs } = H;
  const CARDS = () => H.cards();
  const B = (o) => Object.assign({ body: { STR: 3, DEX: 1, INT: 0, WIL: 0, HP: 14, SPD: 30 }, armor: null, hands: [], carried: [], jewelry: [], items: [], aspects: [] }, o);
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

  T("[morale] the Leader falls: one group roll with the best WIL; a failure: they all flee and count as defeated", () => {
    const f = fight([pc("a", [2, 2], { hands: ["W-I-05"] }), tmpl("cap", "Bandit Captain", [20, 2]), tmpl("b1", "Bandit", [20, 5]),
      tmpl("b2", "Bandit", [20, 8]), tmpl("b3", "Bandit", [20, 11]), tmpl("b4", "Bandit", [18, 11])]);
    start(f);
    const r = drop(f, "cap", [12]); // WIL +0: 12 holds
    eq(evs(r, "morale").map((e) => e.why), ["a Leader falls"]);
    eq(morale(r).map((e) => [e.actor, e.total, e.vs]), [["b1", 12, 10]]);
    eq(evs(r, "flee").length, 0);
    eq(morale(drop(f, "b1")).length, 0, "2 of 5: below half");
    const r2 = drop(f, "b2", [9]); // 3 of 5 (half rounded up): 9 fails
    eq(evs(r2, "morale").map((e) => e.why), ["half of the group is down"]);
    eq(evs(r2, "flee").map((e) => e.actor), ["b3", "b4"]);
    ok(C(f, "b3").fled && C(f, "b3").dead && C(f, "b3").hp > 0, "fled: out of the fight with its HP");
    ok(C(f, "b3").hands.length && !f.state.ground.some((g) => g.owner === "b3"), "it takes its gear");
    const s = f.summary().creatures;
    eq([s.b3.fled, s.b1.fled, s.a.kills], [true, false, 0]);
    ok(Eng.summaryCsv(f.summary()).split("\n")[0].endsWith(",fled"));
  });

  T("[morale] the group rolls with its best WIL; each trigger fires once per fight", () => {
    const f = fight([pc("a", [2, 2]), tmpl("cap", "Bandit Captain", [20, 2]), tmpl("b1", "Bandit", [20, 5]), tmpl("c1", "Cultist", [20, 8]), tmpl("b3", "Bandit", [20, 11])]);
    start(f);
    const r = drop(f, "cap", [7]); // the Cultist's WIL +3: 10 holds
    eq(morale(r).map((e) => [e.actor, e.bonus, e.total]), [["c1", 3, 10]]);
    const r1 = drop(f, "b1", [7]); // 2 of 4 = half
    eq(evs(r1, "morale").map((e) => e.why), ["half of the group is down"]);
    eq([f.state.morale.leader, f.state.morale.half], [true, true]);
    const r2 = drop(f, "b3");
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
    const r3 = drop(g, "boss", [10]); // the Leader falls: the three Bandits check once, as a group
    eq(morale(r3).map((e) => e.actor), ["b1"]);
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
