// The starter party used by the sample scenarios: four Rank I Bearers built from the starter list (P 13.1).
// Scenario files register themselves on BEARERS_SCENARIOS; a creature with "foe": "<name>" and no build
// gets its build from that foe card (Eng.fromFoe) when the scenario loads.
globalThis.BEARERS_SCENARIOS = globalThis.BEARERS_SCENARIOS || [];
globalThis.BEARERS_PARTY = function (spots) {
  const pc = (id, name, b) => ({ id, side: "pc", name, react: "ask", build: Object.assign({
    calling: null, body: null, armor: null, hands: [], carried: [], jewelry: [], items: [], aspects: [],
    slots: { hand: 2, jewelry: 1, item: 2, aspect: 3 }, bonus: {}, extraDice: 0, ownFx: [], powers: [],
    boss: false, senses: {}, alert: false, foe: null }, b) });
  const party = [ // Templar, Infiltrator, Sage, Performer
    pc("pc1", "Bram", { calling: "L-02", armor: "A-I-02", hands: ["W-I-05", "S-I-01"], jewelry: ["J-I-01"],
      items: [{ id: "P-I-01", n: 1 }], aspects: ["Q-I-03", "Q-I-01", "T-I-03"] }),
    pc("pc2", "Wren", { calling: "L-04", armor: "A-I-01", hands: ["W-I-09"], carried: ["W-I-02"], jewelry: ["J-I-05"],
      items: [{ id: "P-I-01", n: 1 }], aspects: ["Q-I-02", "K-I-05", "T-I-04"] }),
    pc("pc3", "Isolde", { calling: "L-06", armor: "A-I-01", hands: ["W-I-12"], jewelry: ["J-I-01"],
      items: [{ id: "B-I-01", n: 1 }, { id: "P-I-01", n: 1 }], aspects: ["T-I-04", "T-I-02", "K-I-06"] }),
    pc("pc4", "Aldo", { calling: "L-05", armor: "A-I-01", hands: ["W-I-02"], jewelry: ["J-I-04"],
      items: [{ id: "P-I-01", n: 1 }], aspects: ["D-I-01", "Q-I-04", "T-I-03"] }),
  ];
  party.forEach((c, i) => (c.pos = spots[i]));
  return party;
};
