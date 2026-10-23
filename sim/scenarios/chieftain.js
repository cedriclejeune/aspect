// The Ogre Chieftain Boss with its wolves and a cultist, on an open hilltop.
globalThis.BEARERS_SCENARIOS.push({
  version: 1, name: "Boss: the Ogre Chieftain", seed: 777, surprise: null,
  map: { w: 18, h: 14, rows: [
    "..................",
    "..................",
    ".....++......##...",
    "..................",
    "........~~~.......",
    ".......~~~~~......",
    ".......~~~~~......",
    "........~~~.......",
    "..................",
    "...##.........++..",
    "..................",
    "..................",
    "..................",
    "..................",
  ] },
  creatures: BEARERS_PARTY([[3, 6], [2, 8], [2, 5], [3, 9]]).concat([
    { id: "foe1", side: "foe", name: "Ogre Chieftain", foe: "Ogre Chieftain", pos: [13, 6], react: "ask" },
    { id: "foe2", side: "foe", name: "Wolf 1", foe: "Wolf", pos: [11, 4], react: "auto" },
    { id: "foe3", side: "foe", name: "Wolf 2", foe: "Wolf", pos: [11, 9], react: "auto" },
    { id: "foe4", side: "foe", name: "Cultist", foe: "Cultist", pos: [16, 7], react: "auto" },
  ]),
});
