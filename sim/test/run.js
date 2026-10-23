// Engine tests: `node sim/test/run.js`. No packages. Runs against the fixture cards and, if present, sim/cards.js.
"use strict";
const path = require("path");
const Eng = require("../engine.js");
require("../effects.js");
const FIX = require("./fixture-cards.js");
let REAL = null;
try { REAL = require(path.join(__dirname, "..", "cards.js")); } catch (e) { REAL = null; }

const tests = [];
const T = (name, fn) => tests.push({ name, fn });
function eq(a, b, msg) { const A = JSON.stringify(a), B = JSON.stringify(b); if (A !== B) throw new Error(`${msg || "eq"}: got ${A}, want ${B}`); }
function ok(v, msg) { if (!v) throw new Error(msg || "expected true"); }

// ---------- helpers ----------
let CARDS = FIX;
const B = (o) => Object.assign({ core: "C-I-01", armor: null, hands: [], carried: [], jewelry: [], items: [], aspects: [] }, o);
const pc = (id, pos, build, o) => Object.assign({ id, side: "pc", name: id, pos, build: B(build), react: "ask" }, o);
const foe = (id, pos, build, o) => Object.assign({ id, side: "foe", name: id, pos, build: B(build), react: "never" }, o);
const orc = (id, pos, o) => Object.assign({ id, side: "foe", name: id, pos, build: Eng.fromFoe(CARDS.foes.find((f) => f.name === "Orc"), CARDS), react: "never" }, o);
function fight(creatures, o) {
  o = o || {};
  return Eng.createFight({ version: 1, name: "test", seed: o.seed || 7, map: { w: o.w || 14, h: o.h || 14, cells: o.cells || {} }, surprise: o.surprise || null, creatures }, o.cards || CARDS);
}
// Runs a command, answering prompts from `script` (number = die roll, { c } = choice). `fill` answers leftover rolls.
function run(f, cmd, script, fill) {
  script = (script || []).slice();
  let r = f.do(cmd);
  if (!r.ok && /^Engine error/.test(r.error)) throw new Error(r.error);
  if (!r.ok) throw new Error(`refused ${JSON.stringify(cmd)}: ${r.error}`);
  const prompts = [];
  while (f.pending) {
    prompts.push(f.pending);
    let a = script.length ? script.shift() : f.pending.kind === "roll" && fill != null ? fill : undefined;
    if (a === undefined) throw new Error(`unanswered prompt: ${f.pending.text}`);
    if (typeof a === "number" && f.pending.kind !== "roll") throw new Error(`expected a choice for: ${f.pending.text}`);
    if (typeof a !== "number" && f.pending.kind === "roll") throw new Error(`expected a roll for: ${f.pending.text}`);
    r = f.do(typeof a === "number" ? { type: "answer", roll: a } : { type: "answer", choice: a.c });
    if (!r.ok) throw new Error(r.error);
  }
  if (script.length) throw new Error(`unused answers ${JSON.stringify(script)} after ${JSON.stringify(cmd)}`);
  return { events: r.events, prompts };
}
const refused = (f, cmd) => { const r = f.do(cmd); ok(!r.ok, `should refuse ${JSON.stringify(cmd)}`); return r.error; };
// Manual dice; side initiative pc first (or foe first).
function start(f, first, extra) { f.setManualDice(true); run(f, { type: "start" }, first === "foe" ? [1, 19] : [19, 1].concat(extra || [])); }
const C = (f, id) => f.state.creatures[id];
const evs = (r, t) => r.events.filter((e) => e.t === t);

// ---------- totals / validate / fromFoe ----------
T("totals: Core + Mail + Shield; empty Armor +10 Speed", () => {
  const t = Eng.totals(B({ armor: "A-I-02", hands: ["W-I-05", "S-I-01"] }), CARDS);
  eq([t.STRd, t.DEXd, t.SPD, t.HP, t.size], [18, 13, 30, 14, "Medium"]);
  eq(Eng.totals(B({}), CARDS).SPD, 40);
});
T("totals: unmet Requirement adds nothing and is reported", () => {
  const t = Eng.totals(B({ core: "C-I-03", armor: "A-I-02" }), CARDS);
  eq(t.STRd, 10); ok(t.errors.length === 1);
});
T("validate: Hands, Slot types, duplicates, Heavy warning", () => {
  const v = Eng.validate(B({ core: "C-I-03", hands: ["W-I-08", "S-I-01"], jewelry: ["W-I-01"], aspects: ["T-I-03", "T-I-03"] }), CARDS);
  ok(v.some((s) => /Hands: 3/.test(s)), "hands"); ok(v.some((s) => /doesn't fit a jewelry/.test(s)), "slot");
  ok(v.some((s) => /two copies/.test(s)), "dup"); ok(v.some((s) => /Heavy/.test(s)), "heavy");
  eq(Eng.validate(B({ armor: "A-I-02", hands: ["W-I-05", "S-I-01"] }), CARDS), []);
});
T("fromFoe matches the printed foe totals", () => {
  for (const f of CARDS.foes) {
    const t = Eng.totals(Eng.fromFoe(f, CARDS), CARDS);
    for (const k of Object.keys(f.totals)) eq(t[k], f.totals[k], `${f.name} ${k}`);
  }
});

// ---------- engagement ----------
T("Outnumbered: 3 vs 1 gives 2 advantage, also to an archer; a second orc makes it 1 (P 6.5)", () => {
  const f = fight([pc("a", [4, 5], { hands: ["W-I-05"] }), pc("b", [6, 5]), pc("c", [5, 4]), pc("arch", [5, 11], { core: "C-I-02", hands: ["W-I-09"] }), orc("o1", [5, 5]), orc("o2", [3, 5])]);
  const G = Eng.geometry, st = f.state;
  eq(G.outnumbered(st, C(f, "a"), C(f, "o1")).n, 1, "with o2 engaged: 3 vs 2");
  eq(G.outnumbered(st, C(f, "arch"), C(f, "o1")).n, 1, "archer gets the same dice");
  run(f, { type: "adjust", actor: "o2", dead: true });
  eq(G.outnumbered(st, C(f, "a"), C(f, "o1")).n, 2);
  start(f);
  run(f, { type: "beginTurn", actor: "a" });
  const pv = f.preview({ type: "attack", actor: "a", weapon: "W-I-05", target: "o1" });
  ok(pv.ok, pv.error); eq([pv.info.dice, pv.info.adv, pv.info.outnumbered.us, pv.info.outnumbered.them], [3, 2, 3, 1]);
});
T("Outnumbered: lone attacker at range vs unengaged target: no dice", () => {
  const f = fight([pc("arch", [1, 1], { core: "C-I-02", hands: ["W-I-09"] }), orc("o1", [8, 8])]);
  eq(Eng.geometry.outnumbered(f.state, C(f, "arch"), C(f, "o1")).n, 0);
});
T("Engagement ignores Incapacitated creatures and sizes two apart", () => {
  const f = fight([pc("a", [4, 5]), orc("o1", [5, 5])]);
  ok(Eng.geometry.engaged(C(f, "a"), C(f, "o1")));
  run(f, { type: "adjust", actor: "a", cond: "Stunned" });
  ok(!Eng.geometry.engaged(C(f, "a"), C(f, "o1")));
});
T("Disengage costs by engaged enemies; 4 = surrounded (P 6.5)", () => {
  const costs = [];
  for (let n = 1; n <= 4; n++) {
    const spots = [[4, 5], [6, 5], [5, 4], [5, 6]].slice(0, n).map((p, i) => orc("o" + i, p));
    const f = fight([pc("a", [5, 5])].concat(spots));
    start(f);
    run(f, { type: "beginTurn", actor: "a" });
    const pv = f.preview({ type: "act", actor: "a", action: "disengage" });
    costs.push(pv.ok ? pv.info.cost : "surrounded");
  }
  eq(costs, ["free", "bonus", "action", "surrounded"]);
});
T("Opportunity attack when leaving reach; Disengage prevents it", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-05"] }), orc("o1", [6, 5], { react: "auto" })]);
  start(f, "foe");
  run(f, { type: "beginTurn", actor: "o1" }); run(f, { type: "endTurn", actor: "o1" });
  run(f, { type: "beginTurn", actor: "a" });
  eq(f.preview({ type: "move", actor: "a", path: [[4, 5], [3, 5]] }).info.provokes, ["o1"]);
  const r = run(f, { type: "move", actor: "a", path: [[4, 5], [3, 5]] }, [1]); // orc's OA rolls a natural 1
  ok(evs(r, "reaction").length === 1, "OA taken"); ok(C(f, "o1").turn.reaction, "reaction spent");
  f.undo();
  run(f, { type: "act", actor: "a", action: "disengage" });
  const r2 = run(f, { type: "move", actor: "a", path: [[4, 5], [3, 5]] });
  eq(evs(r2, "reaction").length, 0);
});
T("Movement: difficult terrain, Prone crawl, stand up costs half speed", () => {
  const f = fight([pc("a", [1, 1]), orc("o1", [12, 12])], { cells: { "2,1": "difficult" } });
  start(f);
  run(f, { type: "beginTurn", actor: "a" });
  eq(f.preview({ type: "move", actor: "a", path: [[2, 1], [3, 1]] }).info.cost, 15);
  run(f, { type: "act", actor: "a", action: "prone" });
  eq(f.preview({ type: "move", actor: "a", path: [[1, 2]] }).info.cost, 10);
  eq(f.preview({ type: "move", actor: "a", stand: true, path: [[1, 2]] }).info.cost, 25);
});

// ---------- turn structure ----------
T("First-mover rule: round 1 first side gets movement or action", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-05"] }), orc("o1", [6, 5])]);
  start(f);
  run(f, { type: "beginTurn", actor: "a" });
  ok(C(f, "a").turn.firstMover);
  run(f, { type: "move", actor: "a", path: [[5, 6]] });
  ok(/movement or action/.test(refused(f, { type: "attack", actor: "a", weapon: "W-I-05", target: "o1" })));
  run(f, { type: "endTurn", actor: "a" });
  run(f, { type: "beginTurn", actor: "o1" });
  ok(!C(f, "o1").turn.firstMover, "second side takes full turns");
});
T("Ambush: the other side surprised, first side takes full turns", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-05"] }), orc("o1", [6, 5])], { surprise: "foe" });
  f.setManualDice(true);
  run(f, { type: "start" }, [19, 1, 1]); // foe rolls 2d20 (disadvantage)
  ok(f.state.ambush && f.state.first === "pc");
  run(f, { type: "beginTurn", actor: "a" });
  ok(!C(f, "a").turn.firstMover);
});
T("Initiative: d20 + average DEX rounded down, ties re-rolled", () => {
  const f = fight([pc("a", [1, 1], { core: "C-I-02" }), pc("b", [2, 1]), orc("o1", [9, 9])]);
  f.setManualDice(true);
  const r = run(f, { type: "start" }, [10, 11, 15, 3]); // pc 10+2=12 vs foe 11+1=12: tie, re-roll
  eq(evs(r, "initiative").filter((e) => e.total != null).map((e) => e.total), [12, 12, 17, 4]);
  eq(f.state.first, "pc");
});
T("Boss half turn: during the other side, once per round, movement or one action (GM 3)", () => {
  const chief = { id: "boss", side: "foe", name: "Chief", pos: [8, 8], build: Eng.fromFoe(CARDS.foes.find((x) => x.name === "Chief"), CARDS), react: "never" };
  const f = fight([pc("a", [1, 1]), pc("b", [1, 3]), chief]);
  start(f);
  run(f, { type: "beginTurn", actor: "a" }); run(f, { type: "endTurn", actor: "a" });
  ok(f.legal("boss").some((t) => t.type === "beginTurn" && t.half), "legal offers a half turn");
  run(f, { type: "beginTurn", actor: "boss", half: true });
  ok(C(f, "boss").turn.half);
  run(f, { type: "move", actor: "boss", path: [[7, 7]] });
  ok(/half turn/.test(refused(f, { type: "act", actor: "boss", action: "dodge" })));
  run(f, { type: "endTurn", actor: "boss" });
  ok(/already used/.test(refused(f, { type: "beginTurn", actor: "boss", half: true })));
  eq(f.state.side, "pc", "half turn doesn't end the side");
  run(f, { type: "beginTurn", actor: "b" }); run(f, { type: "endTurn", actor: "b" });
  eq(f.state.side, "foe");
  ok(/other side/.test(refused(f, { type: "beginTurn", actor: "boss", half: true })));
});
T("Rounds: sides alternate, round counter and reactions reset", () => {
  const f = fight([pc("a", [1, 1]), orc("o1", [9, 9])]);
  start(f);
  for (const id of ["a", "o1"]) { run(f, { type: "beginTurn", actor: id }); run(f, { type: "endTurn", actor: id }); }
  eq([f.state.round, f.state.side], [2, "pc"]);
});

// ---------- attacks ----------
T("Critical hit doubles all damage dice, modifier once", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-05", "S-I-01"] }), orc("o1", [6, 5])]);
  start(f, "foe");
  run(f, { type: "beginTurn", actor: "o1" }); run(f, { type: "endTurn", actor: "o1" });
  run(f, { type: "beginTurn", actor: "a" });
  const r = run(f, { type: "attack", actor: "a", weapon: "W-I-05", target: "o1" }, [20, 3, 4]);
  ok(evs(r, "crit").length === 1);
  eq(evs(r, "damage")[0].n, 3 + 4 + 3);
  eq(C(f, "o1").hp, 14 - 10);
});
T("Versatile die with the other Hand empty", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-05"] }), orc("o1", [6, 5])]);
  start(f, "foe");
  run(f, { type: "beginTurn", actor: "o1" }); run(f, { type: "endTurn", actor: "o1" });
  run(f, { type: "beginTurn", actor: "a" });
  eq(f.preview({ type: "attack", actor: "a", weapon: "W-I-05", target: "o1" }).info.damage, "1d10+3 Physical");
  const r = run(f, { type: "attack", actor: "a", weapon: "W-I-05", target: "o1" }, [15, 10]);
  eq(evs(r, "damage")[0].n, 13);
});
T("Advantage dice: sources add d20s, cancel, keep highest/lowest; natural 1 on the kept die", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-05"] }), orc("o1", [6, 5])]);
  start(f, "foe");
  run(f, { type: "adjust", actor: "o1", cond: "Prone" });
  run(f, { type: "adjust", actor: "o1", cond: "Restrained" });
  run(f, { type: "adjust", actor: "a", cond: "Poisoned" });
  run(f, { type: "beginTurn", actor: "o1" }); run(f, { type: "endTurn", actor: "o1" });
  run(f, { type: "beginTurn", actor: "a" });
  const pv = f.preview({ type: "attack", actor: "a", weapon: "W-I-05", target: "o1" });
  eq([pv.info.adv, pv.info.dis, pv.info.dice, pv.info.keep], [2, 1, 2, "highest"]);
  const r = run(f, { type: "attack", actor: "a", weapon: "W-I-05", target: "o1" }, [1, 1]);
  ok(evs(r, "miss").length === 1, "natural 1 on kept die misses");
});
T("Twin Strike: two attacks per Attack action; two-weapon fighting with Light weapons", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-01", "W-I-03"], aspects: ["Q-II-01"] }), orc("o1", [6, 5], { build: Object.assign(Eng.fromFoe(CARDS.foes[0], CARDS), { bonus: { HP: 100 } }) })]);
  start(f, "foe");
  run(f, { type: "beginTurn", actor: "o1" }); run(f, { type: "endTurn", actor: "o1" });
  run(f, { type: "beginTurn", actor: "a" });
  run(f, { type: "attack", actor: "a", weapon: "W-I-01", target: "o1" }, [2]);
  run(f, { type: "attack", actor: "a", weapon: "W-I-01", target: "o1" }, [2]);
  ok(/Light weapon/.test(refused(f, { type: "attack", actor: "a", weapon: "W-I-01", target: "o1", offhand: true })));
  const r = run(f, { type: "attack", actor: "a", weapon: "W-I-03", target: "o1", offhand: true }, [19, 4]);
  eq(evs(r, "damage")[0].n, 4, "no ability modifier off-hand");
  ok(/Action already used|Bonus/.test(refused(f, { type: "attack", actor: "a", weapon: "W-I-01", target: "o1" })));
});
T("Thrown weapon lands at the target, picked up with the interaction; Javelins stay in hand", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-01", "W-I-11"] }), orc("o1", [8, 5])]);
  start(f, "foe");
  run(f, { type: "beginTurn", actor: "o1" }); run(f, { type: "endTurn", actor: "o1" });
  run(f, { type: "beginTurn", actor: "a" });
  run(f, { type: "attack", actor: "a", weapon: "W-I-01", target: "o1", thrown: true }, [2]);
  eq(C(f, "a").hands, ["W-I-11"]); eq(f.state.ground[0], { card: "W-I-01", pos: [8, 5], owner: "a" });
  ok(!f.preview({ type: "attack", actor: "a", weapon: "W-I-01", target: "o1" }).ok);
  ok(!f.preview({ type: "interact", actor: "a", draw: "W-I-01" }).ok, "not within 5 ft");
  run(f, { type: "endTurn", actor: "a" });
  run(f, { type: "beginTurn", actor: "o1" }); run(f, { type: "endTurn", actor: "o1" });
  run(f, { type: "beginTurn", actor: "a" });
  run(f, { type: "move", actor: "a", path: [[6, 5], [7, 5]] });
  run(f, { type: "interact", actor: "a", draw: "W-I-01" });
  eq([C(f, "a").hands, f.state.ground], [["W-I-11", "W-I-01"], []]);
});
T("Javelins: unlimited throws; ranged with an enemy within 5 ft and long range give disadvantage", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-11"] }), orc("o1", [6, 5]), orc("o2", [5, 13], { pos: [5, 13] })], { h: 40 });
  start(f, "foe");
  for (const id of ["o1", "o2"]) { run(f, { type: "beginTurn", actor: id }); run(f, { type: "endTurn", actor: id }); }
  run(f, { type: "beginTurn", actor: "a" });
  const pv = f.preview({ type: "attack", actor: "a", weapon: "W-I-11", target: "o2", thrown: true });
  // long range, an enemy within 5 ft, and Outnumbered 0 vs 1 (o1 is engaged with a's side)
  eq([pv.info.dis, pv.info.dice, pv.info.keep], [3, 4, "lowest"]);
  run(f, { type: "attack", actor: "a", weapon: "W-I-11", target: "o2", thrown: true }, [2, 2, 2, 2]);
  eq(C(f, "a").hands, ["W-I-11"]);
  ok(/beyond long range/.test(f.preview({ type: "attack", actor: "a", weapon: "W-I-11", target: "o2", thrown: true }).error) === false);
});
T("Cover +2 to all Defenses; full cover can't be targeted", () => {
  const f = fight([pc("a", [1, 5], { core: "C-I-02", hands: ["W-I-09"] }), orc("o1", [8, 5]), orc("o2", [8, 9])], { cells: { "5,5": "cover", "5,9": "wall", "5,8": "wall", "5,10": "wall" } });
  start(f);
  run(f, { type: "beginTurn", actor: "a" });
  const pv = f.preview({ type: "attack", actor: "a", weapon: "W-I-09", target: "o1" });
  eq([pv.info.cover, pv.info.defense], [2, 17]);
  const p2 = f.preview({ type: "attack", actor: "a", weapon: "W-I-09", target: "o2" });
  ok(!p2.ok && /full cover/.test(p2.error), p2.error);
});
T("Dark: unseen target gives disadvantage, Darkvision cancels it, an unseen attacker has advantage", () => {
  const dark = {}; for (let x = 7; x < 14; x++) for (let y = 0; y < 14; y++) dark[x + "," + y] = "dark";
  const f = fight([pc("a", [1, 5], { core: "C-I-02", hands: ["W-I-09"] }), pc("b", [1, 7], { core: "C-I-02", hands: ["W-I-09"], aspects: ["T-II-03"] }), orc("o1", [9, 5])], { cells: dark });
  start(f);
  run(f, { type: "beginTurn", actor: "a" });
  const pa = f.preview({ type: "attack", actor: "a", weapon: "W-I-09", target: "o1" });
  eq([pa.info.adv, pa.info.dis], [0, 1]);
  run(f, { type: "endTurn", actor: "a" });
  run(f, { type: "beginTurn", actor: "b" });
  const pb = f.preview({ type: "attack", actor: "b", weapon: "W-I-09", target: "o1" });
  eq([pb.info.adv, pb.info.dis], [0, 0]);
  run(f, { type: "endTurn", actor: "b" });
  run(f, { type: "beginTurn", actor: "o1" });
  const f2 = fight([pc("a", [8, 5], { hands: ["W-I-05"], aspects: ["T-II-03"] }), orc("o1", [9, 5])], { cells: dark });
  start(f2);
  run(f2, { type: "beginTurn", actor: "a" });
  const p3 = f2.preview({ type: "attack", actor: "a", weapon: "W-I-05", target: "o1" });
  eq([p3.info.adv, p3.info.dis], [1, 0], "orc can't see a in the Dark");
});
T("Reach weapon: 10 ft; resistance halves", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-08"] }), orc("o1", [7, 5], { build: Object.assign(Eng.fromFoe(CARDS.foes[0], CARDS), { resist: ["Physical"] }) })]);
  start(f, "foe");
  run(f, { type: "beginTurn", actor: "o1" }); run(f, { type: "endTurn", actor: "o1" });
  run(f, { type: "beginTurn", actor: "a" });
  const r = run(f, { type: "attack", actor: "a", weapon: "W-I-08", target: "o1" }, [15, 7]);
  eq(evs(r, "damage")[0].n, 5);
});
T("Shove prone and push; grapple then escape", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-05"] }), orc("o1", [6, 5])]);
  start(f, "foe");
  run(f, { type: "beginTurn", actor: "o1" }); run(f, { type: "endTurn", actor: "o1" });
  run(f, { type: "beginTurn", actor: "a" });
  run(f, { type: "shove", actor: "a", target: "o1", mode: "push" }, [18]);
  eq(C(f, "o1").pos, [7, 5]);
  run(f, { type: "endTurn", actor: "a" });
  run(f, { type: "beginTurn", actor: "o1" }); run(f, { type: "move", actor: "o1", path: [[6, 5]] }); run(f, { type: "endTurn", actor: "o1" });
  run(f, { type: "beginTurn", actor: "a" });
  run(f, { type: "grapple", actor: "a", target: "o1" }, [18]);
  ok(C(f, "o1").conds.some((k) => k.name === "Grappled"));
  run(f, { type: "endTurn", actor: "a" });
  run(f, { type: "beginTurn", actor: "o1" });
  eq(C(f, "o1").turn.speed, 0, "Grappled: speed 0");
  run(f, { type: "escape", actor: "o1", target: "a" }, [19]);
  ok(!C(f, "o1").conds.some((k) => k.name === "Grappled"));
});

// ---------- HP and death ----------
T("Death saves: falling to 0, natural 1, damage at 0, crit within 5 ft on Unconscious, death", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-05"] }), pc("b", [1, 1]), orc("o1", [6, 5])]);
  start(f, "foe");
  run(f, { type: "adjust", actor: "a", hp: 2 });
  run(f, { type: "beginTurn", actor: "o1" });
  run(f, { type: "attack", actor: "o1", weapon: "W-I-05", target: "a" }, [18, 4]);
  ok(C(f, "a").down && C(f, "a").conds.some((k) => k.name === "Unconscious"));
  eq(C(f, "a").hands, [], "drops what it holds");
  run(f, { type: "endTurn", actor: "o1" });
  run(f, { type: "beginTurn", actor: "a" }, [1]);
  eq(C(f, "a").death.fail, 2);
  eq(f.state.active, null, "unconscious turn ends on its own");
  run(f, { type: "beginTurn", actor: "b" }); run(f, { type: "endTurn", actor: "b" });
  run(f, { type: "beginTurn", actor: "o1" });
  const pv = f.preview({ type: "attack", actor: "o1", weapon: "W-I-05", target: "a" });
  eq(pv.info.adv, 3, "Prone within 5 ft + Stunned + Outnumbered 1 vs 0");
  const r = run(f, { type: "attack", actor: "o1", weapon: "W-I-05", target: "a" }, [5, 6, 7, 8], 1);
  ok(evs(r, "crit").length === 1, "hit within 5 ft is a crit");
  ok(C(f, "a").dead);
});
T("Death save natural 20 regains 1 HP; healing wakes; instant death", () => {
  const f = fight([pc("a", [5, 5]), pc("b", [5, 6], { items: [{ id: "P-I-01", n: 2 }] }), orc("o1", [12, 12])]);
  start(f);
  run(f, { type: "adjust", actor: "a", hp: 0 });
  run(f, { type: "adjust", actor: "a", cond: "Unconscious" });
  run(f, { type: "beginTurn", actor: "a" }, [20]);
  eq(C(f, "a").hp, 1); ok(!C(f, "a").conds.some((k) => k.name === "Unconscious"));
  run(f, { type: "endTurn", actor: "a" });
  run(f, { type: "beginTurn", actor: "b" });
  run(f, { type: "power", actor: "b", power: "P-I-01#0", targets: ["a"] }, [1, 1]);
  eq(C(f, "a").hp, 5); eq(C(f, "b").items[0].n, 1);
  const g = fight([pc("a", [5, 5]), orc("o1", [6, 5])]);
  start(g, "foe");
  run(g, { type: "adjust", actor: "a", hp: 1 });
  run(g, { type: "beginTurn", actor: "o1" });
  run(g, { type: "attack", actor: "o1", weapon: "W-I-05", target: "a" }, [20, 8, 8]);
  ok(C(g, "a").dead, "19 damage at 1 HP: 18 left ≥ 14 max");
  eq(g.state.phase, "over"); eq(g.state.winner, "foe");
});
T("Temporary HP absorbs first; foes die at 0", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-05", "S-I-01"] }), orc("o1", [6, 5])]);
  start(f, "foe");
  run(f, { type: "adjust", actor: "o1", temp: 5 });
  run(f, { type: "beginTurn", actor: "o1" }); run(f, { type: "endTurn", actor: "o1" });
  run(f, { type: "beginTurn", actor: "a" });
  run(f, { type: "attack", actor: "a", weapon: "W-I-05", target: "o1" }, [18, 8]);
  eq([C(f, "o1").temp, C(f, "o1").hp], [0, 8]);
  run(f, { type: "adjust", actor: "o1", hp: 1 });
  f.state.creatures.a.turn.attacksLeft = 0;
});

// ---------- lasting / subdue ----------
T("Lasting effect (Web): maintain roll with the bare modifier breaks on a miss", () => {
  const f = fight([pc("w", [1, 5], { core: "C-I-03", items: [{ id: "B-I-01", n: 1 }] }), orc("o1", [6, 5])]);
  start(f);
  run(f, { type: "beginTurn", actor: "w" });
  const pv = f.preview({ type: "power", actor: "w", power: "B-I-01#web", point: [6, 5] });
  ok(pv.ok, pv.error); eq(pv.info.targets, ["o1"]); eq(pv.info.cells.length, 4);
  run(f, { type: "power", actor: "w", power: "B-I-01#web", point: [6, 5] }, [15]);
  ok(C(f, "o1").conds.some((k) => k.name === "Restrained" && k.lasting));
  eq(C(f, "w").sp["B-I-01"], 2);
  run(f, { type: "endTurn", actor: "w" });
  const r = run(f, { type: "beginTurn", actor: "o1" }, [8]); // 8 + INT 3 = 11 < DEX Defense 12
  ok(evs(r, "maintain").length === 1);
  ok(!C(f, "o1").conds.some((k) => k.name === "Restrained"), "breaks free");
});
T("Lasting effect: hurt source rolls with disadvantage; ends if the source is Incapacitated", () => {
  const f = fight([pc("w", [1, 5], { core: "C-I-03", items: [{ id: "B-I-01", n: 1 }] }), orc("o1", [6, 5]), orc("o2", [1, 6])]);
  start(f);
  run(f, { type: "beginTurn", actor: "w" });
  run(f, { type: "power", actor: "w", power: "B-I-01#web", point: [6, 5] }, [15]);
  run(f, { type: "endTurn", actor: "w" });
  run(f, { type: "beginTurn", actor: "o2" });
  run(f, { type: "attack", actor: "o2", weapon: "W-I-05", target: "w" }, [18, { c: null }, 1]);
  run(f, { type: "endTurn", actor: "o2" });
  const r = run(f, { type: "beginTurn", actor: "o1" }, [15, 15]);
  eq(evs(r, "maintain")[0].dice.length, 2, "1 disadvantage die");
  run(f, { type: "adjust", actor: "w", cond: "Stunned" });
  ok(!C(f, "o1").conds.some((k) => k.name === "Restrained"));
});
T("Subdue: first bite, weakening, hits add disadvantage", () => {
  const f = fight([pc("w", [1, 5], { core: "C-I-03", items: [{ id: "B-I-01", n: 1 }] }), pc("a", [5, 5], { hands: ["W-I-05"] }), orc("o1", [6, 5])]);
  start(f);
  run(f, { type: "beginTurn", actor: "w" });
  run(f, { type: "power", actor: "w", power: "B-I-01#hold", targets: ["o1"] }, [12]);
  ok(C(f, "o1").conds.some((k) => k.name === "Stunned" && k.subdue));
  run(f, { type: "endTurn", actor: "w" });
  run(f, { type: "beginTurn", actor: "a" }); run(f, { type: "endTurn", actor: "a" });
  const r1 = run(f, { type: "beginTurn", actor: "o1" });
  eq(evs(r1, "maintain").length, 1); ok(/first bite/.test(evs(r1, "maintain")[0].text));
  eq(f.state.active, null, "loses its turn");
  run(f, { type: "beginTurn", actor: "w" }); run(f, { type: "endTurn", actor: "w" });
  run(f, { type: "beginTurn", actor: "a" });
  run(f, { type: "attack", actor: "a", weapon: "W-I-05", target: "o1" }, [10, 10, 10, 1]); // Stunned + Outnumbered 1 vs 0
  run(f, { type: "endTurn", actor: "a" });
  const r2 = run(f, { type: "beginTurn", actor: "o1" }, [15, 15]);
  eq(evs(r2, "maintain")[0].dice.length, 2, "first maintain roll: 1 die per hit");
  for (const id of ["w", "a"]) { run(f, { type: "beginTurn", actor: id }); run(f, { type: "endTurn", actor: id }); }
  const r3 = run(f, { type: "beginTurn", actor: "o1" }, [15, 15]);
  eq(evs(r3, "maintain")[0].dice.length, 2, "second maintain roll: weakening");
});
T("Dirge vs WIL with fear tag: Iron Will adds +2 WIL Defense", () => {
  const f = fight([pc("e", [1, 5], { core: "C-I-04", aspects: ["G-I-01"] }), foe("x", [6, 5], { aspects: ["T-I-03"] })]);
  start(f);
  run(f, { type: "beginTurn", actor: "e" });
  const pv = f.preview({ type: "power", actor: "e", power: "G-I-01#dread", targets: ["x"] });
  eq([pv.info.toHit, pv.info.defense], [5, 12]);
  run(f, { type: "power", actor: "e", power: "G-I-01#dread", targets: ["x"] }, [10]); // own Cue is for allies only
  ok(C(f, "x").conds.some((k) => k.name === "Frightened" && k.lasting));
  eq(C(f, "e").resolve["G-I-01"], 4);
});

// ---------- reactions, prompts, undo, replay ----------
T("Reaction prompt: Ring of Warding turns a hit into a miss; undo; decline", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-05"], jewelry: ["J-I-01"] }), orc("o1", [6, 5])]);
  start(f, "foe");
  run(f, { type: "beginTurn", actor: "o1" });
  // a's weapon Defense: STR 13 (no armor). Orc +5: roll 8 → 13 hits by 0.
  const r = run(f, { type: "attack", actor: "o1", weapon: "W-I-05", target: "a" }, [8, { c: 0 }]);
  ok(evs(r, "miss").length >= 1, "now a miss"); eq(C(f, "a").uses["J-I-01#0"], 1); ok(C(f, "a").turn.reaction);
  ok(f.undo());
  eq(C(f, "a").uses["J-I-01#0"], 2);
  eq(f.state.creatures.a.hp, 14);
  const r2 = run(f, { type: "attack", actor: "o1", weapon: "W-I-05", target: "a" }, [8, { c: null }, 5]);
  ok(evs(r2, "damage").length === 1); eq(C(f, "a").hp, 14 - 8);
});
T("Pending prompt: other commands refused, bad answers refused, undo cancels it", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-05"], jewelry: ["J-I-01"] }), orc("o1", [6, 5])]);
  start(f, "foe");
  run(f, { type: "beginTurn", actor: "o1" });
  f.do({ type: "attack", actor: "o1", weapon: "W-I-05", target: "a" });
  eq(f.pending.kind, "roll"); eq(f.pending.die, 20);
  ok(!f.do({ type: "answer", roll: 21 }).ok);
  f.do({ type: "answer", roll: 8 });
  eq(f.pending.kind, "reaction");
  ok(!f.do({ type: "endTurn", actor: "o1" }).ok);
  ok(!f.do({ type: "answer", choice: 5 }).ok);
  ok(f.undo()); eq(f.pending, null);
  eq(C(f, "a").hp, 14);
});
T("Auto react: Shield spell only when it flips the hit; reaction auto never wasted", () => {
  const f = fight([pc("w", [5, 5], { core: "C-I-03", items: [{ id: "B-I-01", n: 1 }] }, { react: "auto" }), orc("o1", [6, 5])]);
  start(f, "foe");
  run(f, { type: "beginTurn", actor: "o1" });
  const r = run(f, { type: "attack", actor: "o1", weapon: "W-I-05", target: "w" }, [10]); // 15 vs DEX 11: Shield +5 → 16
  ok(evs(r, "miss").length >= 1); eq(C(f, "w").sp["B-I-01"], 3);
  ok(C(f, "w").mods.some((m) => m.kind === "def" && m.n === 5), "Shield lasts until w's next turn");
});
T("Cue (Steady Now) auto: +2 Defense on an ally flips a hit", () => {
  const f = fight([pc("e", [3, 5], { core: "C-I-04", aspects: ["G-I-01"] }, { react: "auto" }), pc("a", [5, 5], { hands: ["W-I-05"] }), orc("o1", [6, 5])]);
  start(f, "foe");
  run(f, { type: "beginTurn", actor: "o1" });
  const r = run(f, { type: "attack", actor: "o1", weapon: "W-I-05", target: "a" }, [9]); // 14 vs 13
  ok(evs(r, "miss").length >= 1, "13+2 = 15 > 14");
  eq(C(f, "e").resolve["G-I-01"], 5);
});
T("Retaliation reaction: Ring of Sparks damages the attacker", () => {
  const f = fight([pc("a", [5, 5], { jewelry: ["J-II-01"] }, { react: "auto" }), orc("o1", [6, 5])]);
  start(f, "foe");
  run(f, { type: "beginTurn", actor: "o1" });
  run(f, { type: "attack", actor: "o1", weapon: "W-I-05", target: "a" }, [15, 3, 3, 1]);
  eq(C(f, "o1").hp, 14 - 6);
});
T("Weapon rider (Sap) applies on hit and is spent by the next attack", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-04"] }), orc("o1", [6, 5])]);
  start(f, "foe");
  run(f, { type: "beginTurn", actor: "o1" }); run(f, { type: "endTurn", actor: "o1" });
  run(f, { type: "beginTurn", actor: "a" });
  run(f, { type: "attack", actor: "a", weapon: "W-I-04", target: "o1" }, [15, 1]);
  ok(C(f, "o1").mods.some((m) => m.n === -2 && m.next));
  run(f, { type: "endTurn", actor: "a" });
  run(f, { type: "beginTurn", actor: "o1" });
  eq(f.preview({ type: "attack", actor: "o1", weapon: "W-I-05", target: "a" }).info.toHit, 3);
});
T("Deterministic replay of an exported fight (random dice, prompts)", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-05"], jewelry: ["J-I-01"] }), pc("w", [2, 5], { core: "C-I-03", items: [{ id: "B-I-01", n: 1 }] }), orc("o1", [6, 5]), orc("o2", [9, 9])], { seed: 99 });
  run(f, { type: "start" });
  let guard = 0;
  while (f.state.phase === "fight" && guard++ < 60) {
    const st = f.state;
    if (!st.active) { const id = Object.values(st.creatures).find((c) => !c.dead && c.side === st.side && !st.done.includes(c.id)).id; run(f, { type: "beginTurn", actor: id }, [], null); continue; }
    const c = st.creatures[st.active];
    const tgt = Object.values(st.creatures).find((o) => !o.dead && o.side !== c.side);
    const opts = [];
    if (c.id === "w") opts.push({ type: "power", actor: "w", power: "B-I-01#fire-bolt", targets: [tgt.id] });
    opts.push({ type: "attack", actor: c.id, weapon: c.hands[0] || "unarmed", target: tgt.id });
    for (const o of opts) if (f.preview(o).ok) { f.do(o); while (f.pending) f.do({ type: "answer", choice: f.pending.options.length ? 0 : null }); break; }
    if (f.state.active) run(f, { type: "endTurn", actor: f.state.active });
  }
  const exp = JSON.parse(JSON.stringify(f.export()));
  const g = Eng.replay(exp, CARDS);
  eq(JSON.stringify(g.state), JSON.stringify(f.state));
  eq(g.events.map((e) => e.text), f.events.map((e) => e.text));
  ok(exp.summary.creatures.a.attacks > 0);
  ok(Eng.summaryCsv(exp.summary).split("\n")[0].startsWith("id,name,side,dmgDealt"));
});
T("Manual-dice replay keeps answers", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-05"] }), orc("o1", [6, 5])]);
  start(f, "foe");
  run(f, { type: "beginTurn", actor: "o1" });
  run(f, { type: "attack", actor: "o1", weapon: "W-I-05", target: "a" }, [15, 6]);
  const g = Eng.replay(f.export(), CARDS);
  eq(C(g, "a").hp, 14 - 9);
});

// ---------- powers ----------
T("Spells: empty Hand needed, one spell per turn, spell points, darts with upcast", () => {
  const f = fight([pc("w", [1, 5], { core: "C-I-03", hands: ["W-I-05", "S-I-01"], items: [{ id: "B-I-01", n: 1 }] }), orc("o1", [6, 5]), orc("o2", [6, 7])]);
  start(f);
  run(f, { type: "beginTurn", actor: "w" });
  ok(/empty Hand/.test(refused(f, { type: "power", actor: "w", power: "B-I-01#fire-bolt", targets: ["o1"] })));
  run(f, { type: "interact", actor: "w", drop: "S-I-01" });
  const pv = f.preview({ type: "power", actor: "w", power: "B-I-01#magic-missile", targets: ["o1", "o1", "o2", "o2"], level: 2 });
  ok(pv.ok, pv.error);
  ok(/3 darts/.test(refused(f, { type: "power", actor: "w", power: "B-I-01#magic-missile", targets: ["o1", "o1", "o2", "o2"] })));
  const r = run(f, { type: "power", actor: "w", power: "B-I-01#magic-missile", targets: ["o1", "o1", "o2", "o2"], level: 2 }, [15, 2, 2, 2, 1, 1]);
  eq(evs(r, "damage").map((e) => e.n), [6, 2], "o1: 2 darts of 2+1; o2 misses: half of (1+1)+(1+1)");
  eq(C(f, "w").sp["B-I-01"], 2);
});
T("Area: one roll against each creature; half damage on a miss", () => {
  const cards = JSON.parse(JSON.stringify(CARDS));
  cards.cards["R-II-01"] = { id: "R-II-01", name: "Fire Flask", rank: "II", kind: "gear", type: "Recipe", kw: ["Recipe"], text: [], strip: {}, uses: 3,
    fx: [{ id: "R-II-01#0", name: "Fire Flask", use: "bonus", reach: 30, target: "point", area: { shape: "sphere", size: 5 }, atk: { abil: ["DEX", "INT"], hit: 3, vs: "DEX" }, half: true, do: [{ dmg: "2d6", type: "Fire" }] }] };
  const f = fight([pc("a", [1, 5], { core: "C-I-02", items: [{ id: "R-II-01" }] }), orc("o1", [6, 5]), orc("o2", [7, 6]), orc("o3", [10, 10])], { cards });
  start(f);
  run(f, { type: "beginTurn", actor: "a" });
  const r = run(f, { type: "power", actor: "a", power: "R-II-01#0", point: [6, 6] }, [6, 3, 4]); // 6+6 = 12: hits DEX 12 both
  eq(evs(r, "roll").length, 1); eq(evs(r, "damage").map((e) => e.n), [7, 7]);
  eq(C(f, "a").items[0].n, 2);
});
T("Anthem on allies (count, Duration), Bless-like dice mods roll on the attack", () => {
  const cards = JSON.parse(JSON.stringify(CARDS));
  cards.decks["G-I-01"].powers.push({ id: "G-I-01#rally", name: "Rally", kind: "Anthem", cost: 1, use: "bonus", reach: 30, target: "allies", count: 3, need: ["voice"], dur: "1 minute", do: [{ mod: "attack", n: 2, until: "dur" }] });
  const f = fight([pc("e", [1, 5], { core: "C-I-04", aspects: ["G-I-01"] }), pc("a", [3, 5]), pc("b", [12, 12]), orc("o1", [13, 0])], { cards });
  start(f);
  run(f, { type: "beginTurn", actor: "e" });
  run(f, { type: "power", actor: "e", power: "G-I-01#rally" });
  ok(C(f, "a").mods.some((m) => m.n === 2)); ok(!C(f, "b").mods.length, "out of reach"); ok(!C(f, "e").mods.length, "allies exclude the user");
  const m = C(f, "a").mods[0];
  eq(m.until.rounds, 10);
});
T("Forms: shift with fresh totals, own HP pool, overflow carries over, gear off, revert free", () => {
  const f = fight([pc("d", [5, 5], { core: "C-I-04", armor: "A-I-01", hands: ["W-I-05"], aspects: ["N-I-01"] }), orc("o1", [8, 5])]);
  start(f);
  run(f, { type: "beginTurn", actor: "d" });
  run(f, { type: "power", actor: "d", power: "N-I-01#bear" });
  const d = C(f, "d");
  eq([d.size, d.totals.STR, d.totals.STRd, d.totals.WIL, d.form.hp, d.resolve["N-I-01"]], ["Large", 3, 15, 3, 12, 3]);
  ok(!f.preview({ type: "attack", actor: "d", weapon: "W-I-05", target: "o1" }).ok, "gear merged");
  run(f, { type: "move", actor: "d", path: [[6, 5]] });
  ok(f.preview({ type: "attack", actor: "d", weapon: "natural", target: "o1" }).ok === false, "first-mover: moved, no action");
  run(f, { type: "endTurn", actor: "d" });
  run(f, { type: "beginTurn", actor: "o1" });
  run(f, { type: "attack", actor: "o1", weapon: "W-I-05", target: "d" }, [18, 8]);
  eq([C(f, "d").form.hp, C(f, "d").hp], [1, 10], "11 damage comes off the Form");
  run(f, { type: "endTurn", actor: "o1" });
  run(f, { type: "beginTurn", actor: "d" });
  if (C(f, "d").form) run(f, { type: "act", actor: "d", action: "revert" });
  eq([C(f, "d").size, C(f, "d").totals.STRd], ["Medium", 12]);
  const g = fight([pc("d", [5, 5], { core: "C-I-04", aspects: ["N-I-01"] }), orc("o1", [7, 5])]);
  start(g);
  run(g, { type: "beginTurn", actor: "d" });
  run(g, { type: "power", actor: "d", power: "N-I-01#bear" });
  run(g, { type: "endTurn", actor: "d" });
  run(g, { type: "beginTurn", actor: "o1" });
  run(g, { type: "attack", actor: "o1", weapon: "W-I-05", target: "d" }, [20, 8, 8]); // 19 damage: 12 to Form, 7 carry over
  eq([C(g, "d").form, C(g, "d").hp], [null, 10 - 7]);
});
T("Hooks: registered onUse runs with ctx; unknown hook logs not automated", () => {
  const f = fight([pc("a", [5, 5], { aspects: ["T-X-01"] }), orc("o1", [12, 12])]);
  start(f);
  run(f, { type: "beginTurn", actor: "a" });
  const r = run(f, { type: "power", actor: "a", power: "T-X-01#0" });
  ok(evs(r, "note").some((e) => /not automated/.test(e.text)));
  f.undo();
  let seen = null;
  Eng.registerHook("mystery", { onUse(ctx) { seen = ctx.actor.id; ctx.heal(ctx.actor, 1); ctx.emit({ t: "note", text: "mystery " + ctx.roll("1d4") }); } });
  const r2 = run(f, { type: "power", actor: "a", power: "T-X-01#0" }, [3]);
  eq(seen, "a"); ok(evs(r2, "note").some((e) => e.text === "mystery 3"));
  delete Eng.hooks.mystery;
});
T("Boss Recharge rolls at turn start; Bellow is one roll against each enemy in 30 ft", () => {
  const chief = { id: "boss", side: "foe", name: "Chief", pos: [5, 5], build: Eng.fromFoe(CARDS.foes.find((x) => x.name === "Chief"), CARDS), react: "never" };
  const f = fight([pc("a", [3, 5]), pc("b", [5, 9], { aspects: ["T-I-03"] }), pc("c", [13, 13]), chief]);
  start(f, "foe");
  run(f, { type: "beginTurn", actor: "boss" });
  const r = run(f, { type: "power", actor: "boss", power: "foe-chief#0" }, [6]);
  eq(evs(r, "roll").length, 1);
  ok(C(f, "a").conds.some((k) => k.name === "Frightened"), "11 vs 10"); ok(!C(f, "b").conds.length, "Iron Will: 11 vs 10+2"); ok(!C(f, "c").conds.length);
  eq(C(f, "boss").uses["foe-chief#0"], 0);
  run(f, { type: "endTurn", actor: "boss" });
  ok(C(f, "a").conds.some((k) => k.name === "Frightened"), "until end of the chief's NEXT turn");
  for (const id of ["a", "b", "c"]) { run(f, { type: "beginTurn", actor: id }); run(f, { type: "endTurn", actor: id }); }
  run(f, { type: "beginTurn", actor: "boss" }, [5]);
  eq(C(f, "boss").uses["foe-chief#0"], 1, "recharged on a 5");
  run(f, { type: "endTurn", actor: "boss" });
  ok(!C(f, "a").conds.some((k) => k.name === "Frightened"));
});
T("legal(): templates and candidates", () => {
  const f = fight([pc("a", [5, 5], { hands: ["W-I-05"], items: [{ id: "P-I-01", n: 1 }] }), orc("o1", [6, 5])]);
  eq(f.legal("a")[0].type, "start");
  start(f, "foe");
  ok(f.legal("o1").some((t) => t.type === "beginTurn"));
  run(f, { type: "beginTurn", actor: "o1" }); run(f, { type: "endTurn", actor: "o1" });
  run(f, { type: "beginTurn", actor: "a" });
  const L = f.legal("a");
  const atk = L.find((t) => t.type === "attack" && t.weapon === "W-I-05");
  eq(atk.candidates, ["o1"]);
  ok(L.some((t) => t.type === "power" && t.power === "P-I-01#0"));
  ok(L.some((t) => t.type === "endTurn"));
});

// ---------- real cards ----------
function realTests() {
  T("[real] fromFoe matches every printed foe card", () => {
    for (const f of REAL.foes) {
      const b = Eng.fromFoe(f, REAL), t = Eng.totals(b, REAL);
      for (const k of Object.keys(f.totals)) eq(t[k], f.totals[k], `${f.name} ${k}`);
      eq(Eng.validate(b, REAL).filter((s) => !/^Warning/.test(s)), [], f.name);
    }
  });
  T("[real] random fights run to the end without errors and replay identically", () => {
    const party = [
      { id: "pc1", core: "C-I-01", armor: "A-I-02", hands: ["W-I-05", "S-I-01"], jewelry: ["J-I-01"], items: [{ id: "P-I-01", n: 1 }], aspects: ["Q-I-03", "Q-I-01", "T-I-03"] },
      { id: "pc2", core: "C-I-02", armor: "A-I-01", hands: ["W-I-09"], carried: ["W-I-02"], jewelry: ["J-I-05"], items: [{ id: "P-I-01", n: 1 }], aspects: ["Q-I-02", "K-I-05", "T-I-04"] },
      { id: "pc3", core: "C-I-03", armor: "A-I-01", hands: ["W-I-12"], jewelry: ["J-I-01"], items: [{ id: "B-I-01", n: 1 }, { id: "P-I-01", n: 1 }], aspects: ["T-I-04", "T-I-02", "K-I-06"] },
      { id: "pc4", core: "C-I-04", armor: "A-I-01", hands: ["W-I-02"], jewelry: ["J-I-04"], items: [{ id: "P-I-01", n: 1 }], aspects: ["D-I-01", "Q-I-04", "T-I-03"] },
      { id: "pc5", core: "C-I-04", armor: null, hands: ["M-I-01"], jewelry: [], items: [], aspects: ["G-I-01", "N-I-01", "Q-I-05"] },
    ];
    for (const b of party) eq(Eng.validate(b, REAL).filter((s) => !/^Warning/.test(s)), [], b.id);
    let seedN = 0;
    for (const foes of [["Bandit", "Archer", "Goblin", "Wolf"], ["Cultist", "Legionary", "Bandit Captain"], ["Ogre", "Goblin", "Goblin"], ["Ogre Chieftain", "Wolf", "Cultist"]]) {
      for (let k = 0; k < 3; k++) {
        const seed = 1000 + seedN++;
        let rs = seed;
        const rnd = (n) => { rs = (rs * 1103515245 + 12345) % 2147483648; return (rs >>> 8) % n; };
        const cs = party.map((b, i) => ({ id: b.id, side: "pc", name: b.id, pos: [2 + (i % 2), 2 + i * 2], build: b, react: ["ask", "auto", "never"][(i + k) % 3] }));
        foes.forEach((name, i) => cs.push({ id: "f" + i, side: "foe", name, pos: [10 + (i % 2) * 2, 2 + i * 3], build: Eng.fromFoe(REAL.foes.find((x) => x.name === name), REAL), react: ["auto", "ask"][(i + k) % 2] }));
        const f = Eng.createFight({ version: 1, name: "r", seed, map: { w: 16, h: 16, cells: { "7,7": "wall", "8,8": "difficult", "6,4": "cover", "12,12": "dark" } }, surprise: k === 1 ? "foe" : null, creatures: cs }, REAL);
        run(f, { type: "start" });
        let guard = 0;
        while (f.state.phase === "fight" && guard++ < 1500) {
          const st = f.state;
          const id = st.active || Object.keys(st.creatures).find((i) => f.legal(i).some((t) => t.type === "beginTurn"));
          const L = f.legal(id).filter((t) => t.type !== "adjust" && t.type !== "note");
          const ends = L.filter((t) => t.type === "endTurn");
          const acts = L.filter((t) => t.type !== "endTurn");
          const hits = acts.filter((t) => t.candidates && t.candidates.length && !c0(st, id, t));
          let tpl = hits.length && rnd(10) < 7 ? hits[rnd(hits.length)] : acts.length && rnd(5) ? acts[rnd(acts.length)] : ends[0] || L[0];
          if (!tpl) throw new Error("no legal command for " + id);
          const cmd = Object.assign({}, tpl); delete cmd.label; delete cmd.candidates; delete cmd.left;
          if (cmd.type === "move" && !cmd.stand) {
            const c = st.creatures[id], path = [];
            const near = Object.values(st.creatures).filter((o) => !o.dead && o.side !== c.side).sort((x, y) => Eng.geometry.dist(c, x) - Eng.geometry.dist(c, y))[0];
            let p = c.pos;
            for (let s = 0; s < 1 + rnd(4); s++) { p = near && rnd(4) ? [p[0] + Math.sign(near.pos[0] - p[0]), p[1] + Math.sign(near.pos[1] - p[1])] : [p[0] + rnd(3) - 1, p[1] + rnd(3) - 1]; path.push(p); }
            cmd.path = path;
          }
          if (tpl.candidates && tpl.candidates.length) { const t = tpl.candidates[rnd(tpl.candidates.length)]; if (cmd.type === "power") cmd.targets = [t]; else cmd.target = t; }
          if (cmd.type === "power") { const pp = (REAL.cards[cmd.power.split("#")[0]] || {}).fx; const deck = REAL.decks[cmd.power.split("#")[0]]; const p = (deck ? deck.powers : pp || []).find((x) => x.id === cmd.power) || {}; if (p.target === "point" || (p.do || []).some((d) => d.move === "teleport")) cmd.point = [rnd(16), rnd(16)]; if (p.target === "darts") cmd.targets = (cmd.targets || []).concat(cmd.targets || []); }
          const r = f.do(cmd);
          while (f.pending) { const n = f.pending.options.length; f.do({ type: "answer", choice: n && rnd(2) ? rnd(n) : null }); }
          if (!r.ok && /^Engine error/.test(r.error)) throw new Error(`${JSON.stringify(cmd)}: ${r.error}`);
          if (!r.ok && cmd.type === "endTurn") throw new Error("endTurn refused: " + r.error);
          if (!r.ok && !["move", "power", "attack"].includes(cmd.type)) throw new Error(`legal template refused: ${JSON.stringify(cmd)}: ${r.error}`);
        }
        ok(f.state.phase === "over" || guard >= 1500, "fight ran");
        if (process.env.VERBOSE) { const n = {}; f.events.forEach((e) => (n[e.t] = (n[e.t] || 0) + 1)); console.log(`    ${foes.join("+")} seed ${seed}: ${f.state.phase} r${f.state.round} ${f.state.winner}`, JSON.stringify(n)); }
        const g = Eng.replay(JSON.parse(JSON.stringify(f.export())), REAL);
        eq(JSON.stringify(g.state), JSON.stringify(f.state), "replay");
      }
    }
  });
}

// Card-effect tests (agent D): sim/test/effects/*.test.js, real cards only.
function effectTests() {
  const fs = require("fs"), dir = path.join(__dirname, "effects");
  const H = { Eng, eq, ok, run, refused, start, C, evs, cards: () => CARDS };
  for (const f of fs.readdirSync(dir).filter((n) => n.endsWith(".test.js")).sort()) require(path.join(dir, f))(T, H);
}

// Bot helper: skip help and buffs on allies when looking for "hit something" templates.
function c0(st, id, t) { return t.type === "act" || t.candidates.every((x) => st.creatures[x].side === st.creatures[id].side); }

// ---------- runner ----------
function runAll(label, cards) {
  CARDS = cards;
  let pass = 0, failN = 0;
  for (const t of tests) {
    try { t.fn(); pass++; }
    catch (e) { failN++; console.log(`  FAIL [${label}] ${t.name}\n       ${e.stack.split("\n").slice(0, 3).join("\n       ")}`); }
  }
  return { pass, fail: failN };
}
const fixtureTests = tests.length;
let res = runAll("fixture", FIX);
console.log(`fixture cards: ${res.pass}/${fixtureTests} passed`);
let total = res;
if (REAL) {
  tests.length = 0;
  realTests();
  effectTests();
  const r2 = runAll("cards.js", REAL);
  console.log(`sim/cards.js:  ${r2.pass}/${tests.length} passed`);
  total = { pass: res.pass + r2.pass, fail: res.fail + r2.fail };
} else console.log("sim/cards.js not found: real-card tests skipped");
console.log(total.fail ? `${total.fail} FAILED` : `all ${total.pass} tests passed`);
process.exit(total.fail ? 1 : 0);
