// Hand-written test cards in the sim/cards.js format (SPEC 2). Independent of the generated data.
(function () {
  const W = (hit, dice, o) => Object.assign({ hit, dice, two: null, abil: ["STR"], type: "Physical", finesse: false, light: false, heavy: false,
    reach: false, twoHanded: false, loading: false, thrown: null, range: null }, o);
  const calling = (id, name, m, hp, spd, size) => ({ id, name, rank: "", kind: "calling", type: "Calling", kw: ["Calling"], text: [],
    strip: { STR: m[0], DEX: m[1], INT: m[2], WIL: m[3], STRd: 10 + m[0], DEXd: 10 + m[1], INTd: 10 + m[2], WILd: 10 + m[3], HP: hp, SPD: spd },
    group: "starter", size: size || "Medium", fx: [] });
  const gear = (id, name, type, o) => Object.assign({ id, name, rank: "I", kind: "gear", type, kw: [type], text: [], strip: {}, group: "starter", fx: [] }, o);
  const asp = (id, name, type, fx, o) => Object.assign({ id, name, rank: "I", kind: "aspect", type, kw: [type], text: [], strip: {}, group: "starter", fx }, o);
  const list = [
    calling("C-I-01", "Brute", [3, 1, 0, 0], 14, 30),
    calling("C-I-02", "Nimble", [0, 3, 1, 0], 11, 35),
    calling("C-I-03", "Scholar", [0, 1, 3, 0], 9, 30),
    calling("C-I-04", "Envoy", [0, 1, 0, 3], 10, 30),
    calling("C-II-01", "Ogre", [4, 0, 0, 0], 35, 35, "Large"),
    gear("A-I-01", "Leather", "Armor", { strip: { STRd: 2, DEXd: 1, SPD: 5 } }),
    gear("A-I-02", "Mail", "Armor", { strip: { STRd: 3 } }),
    gear("S-I-01", "Shield", "Shield", { strip: { STRd: 2, DEXd: 2 } }),
    gear("W-I-01", "Dagger", "Weapon", { atk: W(4, "1d4", { abil: ["STR", "DEX"], finesse: true, light: true, thrown: [20, 60] }) }),
    gear("W-I-03", "Handaxe", "Weapon", { atk: W(2, "1d6", { light: true, thrown: [20, 60] }) }),
    gear("W-I-04", "Finesse Blade", "Weapon", { atk: W(2, "1d6", { abil: ["STR", "DEX"], finesse: true }),
      fx: [{ id: "W-I-04#0", name: "Sap", use: "trigger", on: "hit", do: [{ mod: "attack", n: -2, next: true, until: "startSourceTurn" }] }] }),
    gear("W-I-05", "Longsword", "Weapon", { atk: W(2, "1d8", { two: "1d10" }) }),
    gear("W-I-08", "Glaive", "Weapon", { atk: W(2, "1d10", { heavy: true, reach: true, twoHanded: true }) }),
    gear("W-I-09", "Longbow", "Weapon", { atk: W(2, "1d8", { abil: ["DEX"], twoHanded: true, range: [150, 600] }) }),
    gear("W-I-11", "Javelins", "Weapon", { atk: W(2, "1d6", { thrown: [30, 120] }) }),
    gear("W-I-13", "Greatclub", "Weapon", { atk: W(2, "1d10", { heavy: true, twoHanded: true }), fx: [{ id: "W-I-13#0", name: "Crushing", use: "trigger", on: "crit", do: [{ cond: "Prone" }] }] }),
    gear("W-I-14", "Gladius", "Weapon", { atk: W(2, "1d6", { light: true }), fx: [{ id: "W-I-14#0", name: "Close Order", use: "passive", hook: "close_order", params: { dmg: "1d4" } }] }),
    gear("J-I-01", "Ring of Warding", "Jewelry", { fx: [{ id: "J-I-01#0", name: "Ring of Warding", use: "reaction", uses: "2/SR", on: "hitSelf", target: "self", do: [{ mod: "def", n: 2, defs: ["targeted"], next: true }] }] }),
    gear("J-II-01", "Ring of Sparks", "Jewelry", { fx: [{ id: "J-II-01#0", name: "Ring of Sparks", use: "reaction", uses: "1/SR", on: "meleeHitSelf5", target: "enemy", do: [{ dmg: "2d6", type: "Lightning" }] }] }),
    gear("P-I-01", "Potion of Healing", "Consumable", { fx: [{ id: "P-I-01#0", name: "Potion of Healing", use: "action", reach: 5, target: "creature", do: [{ heal: "2d4+2" }] }] }),
    gear("B-I-01", "Test Book", "Spellbook", { deck: "B-I-01" }),
    asp("Q-II-01", "Twin Strike", "Technique", [{ id: "Q-II-01#0", name: "Twin Strike", use: "passive", attacks: 2 }]),
    asp("T-I-03", "Iron Will", "Trait", [{ id: "T-I-03#0", name: "Iron Will", use: "passive", defVs: { WIL: 2 }, tags: ["fear", "mind control"] }]),
    asp("T-II-03", "Night Eyes", "Trait", [{ id: "T-II-03#0", name: "Night Eyes", use: "passive", darkvision: 60 }]),
    asp("T-X-01", "Mystery", "Trait", [{ id: "T-X-01#0", name: "Mystery", use: "action", target: "self", hook: "mystery" }]),
    asp("G-I-01", "Test Repertoire", "Glamour", [], { deck: "G-I-01" }),
    asp("N-I-01", "Test Remembrance", "Nature", [], { deck: "N-I-01" }),
  ];
  const cards = {};
  list.forEach((c) => (cards[c.id] = c));
  const data = {
    version: 1, cards,
    decks: {
      "B-I-01": { cover: "B-I-01", kind: "spellbook", atk: 2, sp: 2, maxLevel: 2, powers: [
        { id: "B-I-01#fire-bolt", name: "Fire Bolt", kind: "Cantrip", cost: 0, use: "action", reach: 120, target: "enemy", atk: { abil: "deck", vs: "DEX" }, do: [{ dmg: "1d10", type: "Fire" }], tags: ["fire"] },
        { id: "B-I-01#shield", name: "Shield", kind: "Spell", cost: 1, use: "reaction", on: "hitSelf", target: "self", dur: "1 round", do: [{ mod: "def", n: 5, defs: ["STR", "DEX"], until: "startSourceTurn" }] },
        { id: "B-I-01#magic-missile", name: "Magic Missile", kind: "Spell", cost: 1, use: "action", reach: 120, target: "darts", count: 3, atk: { abil: "deck", vs: "DEX" }, half: true, do: [{ dmg: "1d4+1", type: "Radiant" }], upcast: { darts: 1 } },
        { id: "B-I-01#web", name: "Web", kind: "Spell", cost: 2, use: "action", reach: 60, target: "point", area: { shape: "cube", size: 10 }, atk: { abil: "deck", vs: "DEX" }, zone: { terrain: "difficult", on: ["enter"], burns: true, burnFt: 5 }, do: [{ cond: "Restrained", until: "targetTurns2" }], dur: "1 hour" },
        { id: "B-I-01#hold", name: "Hold", kind: "Spell", cost: 2, use: "action", reach: 60, target: "enemy", atk: { abil: "deck", vs: "WIL" }, do: [{ cond: "Stunned" }], lasting: true, subdue: true },
      ] },
      "G-I-01": { cover: "G-I-01", kind: "glamour", atk: 2, resolve: 3, powers: [
        { id: "G-I-01#steady-now", name: "Steady Now", kind: "Cue", cost: 1, use: "reaction", on: "rollNear", reach: 60, target: "ally", need: ["voice"], do: [{ mod: "roll", n: 2 }], params: { orDefense: true } },
        { id: "G-I-01#dread", name: "Dread", kind: "Dirge", cost: 2, use: "action", reach: 60, target: "enemy", need: ["voice"], atk: { abil: "deck", vs: "WIL" }, do: [{ cond: "Frightened", until: "targetTurns2" }], tags: ["fear"] },
      ] },
      "N-I-01": { cover: "N-I-01", kind: "nature", resolve: 3, powers: [
        { id: "N-I-01#bear", name: "Bear", kind: "Form", cost: 3, use: "action", target: "self", form: { strip: { STR: 3, DEX: 1, STRd: 15, DEXd: 11, HP: 12, SPD: 30 }, size: "Large", fly: 0, climb: 30, weapon: { name: "Claws", hit: 2, dice: "1d8", abil: ["STR"], type: "Physical" } } },
      ] },
    },
    foes: [
      { name: "Orc", body: { STR: 3, DEX: 1, INT: 0, WIL: 0, HP: 14, SPD: 30, size: "Medium" }, carries: ["W-I-05", "A-I-01"], bonus: {}, extraDice: 0, powers: [], senses: {}, alert: false, boss: false, own: [], ownFx: [],
        totals: { STR: 3, DEX: 1, INT: 0, WIL: 0, STRd: 15, DEXd: 12, INTd: 10, WILd: 10, HP: 14, SPD: 35 } },
      { name: "Ogre", body: { STR: 4, DEX: 0, INT: 0, WIL: 0, HP: 35, SPD: 35, size: "Large" }, carries: ["W-I-13", "W-I-11"], bonus: { HP: 33 }, extraDice: 1, powers: [], senses: { darkvision: 60 }, alert: false, boss: false, own: [], ownFx: [],
        totals: { STR: 4, DEX: 0, INT: 0, WIL: 0, STRd: 14, DEXd: 10, INTd: 10, WILd: 10, HP: 68, SPD: 35 } },
      { name: "Chief", body: { STR: 5, DEX: 0, INT: 0, WIL: 1, HP: 110, SPD: 40, size: "Large" }, carries: ["W-I-13"], bonus: {}, extraDice: 1, powers: [], senses: {}, alert: false, boss: true, own: [],
        ownFx: [{ id: "foe-chief#0", name: "Bellow", use: "action", recharge: 5, target: "enemies", reach: 30, atk: { flat: 5, vs: "WIL" }, do: [{ cond: "Frightened", until: "endSourceTurn" }], tags: ["fear"] }],
        totals: { STR: 5, DEX: 0, INT: 0, WIL: 1, STRd: 15, DEXd: 10, INTd: 10, WILd: 11, HP: 110, SPD: 40 } },
    ],
    frames: [{ key: "armor", name: "Armor", perPlayer: 1 }, { key: "hand", name: "Hand", perPlayer: 2 }, { key: "jewelry", name: "Jewelry", perPlayer: 1 }, { key: "item", name: "Item", perPlayer: 2 }, { key: "aspect", name: "Aspect", perPlayer: 3 }],
    starter: { Armor: [], Hands: [], Jewelry: [], Items: [], Aspects: [] },
  };
  module.exports = data;
})();
