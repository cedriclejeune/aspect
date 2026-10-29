// Four starters against a bandit ambush on a ruined road.
globalThis.BEARERS_SCENARIOS.push({
  version: 1, name: "Road ambush: 4 starters vs bandits", seed: 1201, surprise: null,
  map: { w: 16, h: 12, rows: [
    "................",
    "...##......+....",
    "...#.......+....",
    "................",
    ".......~~.......",
    "......~~~~......",
    ".......~~.....#.",
    "..............#.",
    "....+.........#.",
    "....+...........",
    "..........##....",
    "................",
  ] },
  creatures: BEARERS_PARTY([[2, 5], [1, 7], [1, 4], [2, 8]]).concat([
    { id: "foe1", side: "foe", name: "Bandit 1", foe: "Bandit", pos: [11, 4], react: "auto" },
    { id: "foe2", side: "foe", name: "Bandit 2", foe: "Bandit", pos: [11, 6], react: "auto" },
    { id: "foe3", side: "foe", name: "Bandit 3", foe: "Bandit", pos: [12, 8], react: "auto" },
    { id: "foe4", side: "foe", name: "Bandit Archer 1", foe: "Bandit Archer", pos: [13, 1], react: "auto" },
    { id: "foe5", side: "foe", name: "Bandit Archer 2", foe: "Bandit Archer", pos: [15, 9], react: "auto" },
  ]),
});
