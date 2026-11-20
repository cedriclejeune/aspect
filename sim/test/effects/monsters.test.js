// Classic foes and the cards added with them: Relentless, Regeneration, Undead, Dancer's Bells, Rousing Verse;
// the beginner monsters: latching, poison, paralysis, charm, incorporeal, engulf, constructs.
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
  const foeTurn = (f, id) => { start(f); for (const c of Object.values(f.state.creatures)) if (c.side === "pc" && !c.dead) skip(f, c.id); run(f, { type: "beginTurn", actor: id }); };
  const has = (c, name) => c.conds.some((k) => k.name === name);
  const power = (actor, pid, o) => Object.assign({ type: "power", actor, power: pid }, o);
  const dmgs = (r) => evs(r, "damage").map((e) => e.n);

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

  T("[foes] Stirge: Proboscis +5, 1d4 + 3, and the target is Grappled by it", () => {
    const f = fight([pc("a", [5, 5]), tmpl("s", "Stirge", [6, 5])]);
    eq(C(f, "s").maxHp, 5);
    foeTurn(f, "s");
    const r = run(f, power("s", "foe-stirge#0", { targets: ["a"] }), [15, 2]);
    eq(dmgs(r), [5]);
    ok(C(f, "a").conds.some((k) => k.name === "Grappled" && k.source === "s"));
  });

  T("[foes] Giant Centipede: Bite poisons until the end of the centipede's next turn", () => {
    const f = fight([pc("a", [5, 5]), tmpl("c", "Giant Centipede", [6, 5])]);
    foeTurn(f, "c");
    const r = run(f, power("c", "foe-giant-centipede#0", { targets: ["a"] }), [15, 3]);
    eq(dmgs(r), [5]); ok(has(C(f, "a"), "Poisoned"));
    run(f, { type: "endTurn", actor: "c" });
    ok(has(C(f, "a"), "Poisoned"), "still during the next round");
  });

  T("[foes] Ghoul: Paralyzing Touch is Subdue · Stunned against STR Defense, Recharge 5–6", () => {
    const f = fight([pc("a", [5, 5]), tmpl("g", "Ghoul", [6, 5])]);
    foeTurn(f, "g");
    run(f, power("g", "foe-ghoul#2", { targets: ["a"] }), [12]); // 12 + 3 = 15 vs STR Defense 13
    const k = C(f, "a").conds.find((k) => k.name === "Stunned");
    ok(k && k.subdue, "Subdue · Stunned");
    eq(C(f, "g").uses["foe-ghoul#2"], 0);
  });

  T("[foes] Harpy: Luring Song charms each enemy within 60 ft who is hit (Subdue · Charmed)", () => {
    const f = fight([pc("a", [5, 5]), pc("b", [5, 9], { body: { STR: 0, DEX: 1, INT: 0, WIL: 3, HP: 10, SPD: 30 } }), pc("far", [29, 13]), tmpl("h", "Harpy", [12, 5])]);
    foeTurn(f, "h");
    run(f, power("h", "foe-harpy#1"), [8]); // one roll: 11 vs WIL Defense 10 (a) and 13 (b)
    ok(C(f, "a").conds.some((k) => k.name === "Charmed" && k.subdue));
    ok(!has(C(f, "b"), "Charmed"), "11 misses WIL Defense 13");
    ok(!has(C(f, "far"), "Charmed"), "out of reach");
  });

  T("[foes] Shadow: resists Physical; Draining Touch 2d6 + 2 Necrotic", () => {
    const f = fight([pc("a", [5, 5], { hands: ["W-I-16"] }), tmpl("s", "Shadow", [6, 5])]);
    pcTurn(f, "a");
    run(f, atk("a", "W-I-16", "s"), [15, 9]); // 9 + 3 = 12, halved
    eq(C(f, "s").hp, 10);
    const g = fight([pc("a", [5, 5]), tmpl("s", "Shadow", [6, 5])]);
    foeTurn(g, "s");
    const r = run(g, power("s", "foe-shadow#2", { targets: ["a"] }), [15, 3, 4]);
    eq(dmgs(r), [9]);
  });

  T("[foes] Gelatinous Cube: STR Defense 10; Engulf 3d6 Poison and Restrained", () => {
    const f = fight([pc("a", [5, 5]), tmpl("q", "Gelatinous Cube", [6, 5])]);
    eq([C(f, "q").maxHp, C(f, "q").totals.STRd], [63, 10]);
    foeTurn(f, "q");
    const r = run(f, power("q", "foe-gelatinous-cube#2", { targets: ["a"] }), [15, 1, 2, 3]);
    eq(dmgs(r), [6]); ok(has(C(f, "a"), "Restrained"));
  });

  T("[foes] Constructs never check Morale and resist Poison; the Flying Sword wields its Longsword", () => {
    for (const n of ["Flying Sword", "Animated Armor"]) {
      const b = Eng.fromFoe(CARDS().foes.find((f) => f.name === n), CARDS());
      const c = b.ownFx.find((p) => p.name === "Construct");
      eq([c.resist, c.fearless], [["Poison", "Necrotic"], true], n);
    }
    const f = fight([pc("a", [5, 5]), tmpl("s", "Flying Sword", [6, 5])]);
    eq(C(f, "s").totals.STRd, 18, "Longsword: +1 STR Defense");
    ok(C(f, "s").hands.includes("W-I-05") || JSON.stringify(C(f, "s").build || {}).includes("W-I-05"));
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
