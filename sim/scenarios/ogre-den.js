// An ogre and its goblins in a dark cave; the party walks in from the light.
globalThis.BEARERS_SCENARIOS.push({
  version: 1, name: "Ogre den: ogre and goblins in the dark", seed: 4242, surprise: "pc",
  map: { w: 18, h: 12, rows: [
    "##################",
    "#......::::::::::#",
    "#.....:::::::::::#",
    "#....::::##::::::#",
    "......:::##:::+::#",
    "......:::::::::::#",
    "......:::::::::::#",
    "#.....::~~~::::::#",
    "#.....::~~~::##::#",
    "#......::::::##::#",
    "#........::::::::#",
    "##################",
  ] },
  creatures: BEARERS_PARTY([[2, 4], [1, 6], [1, 5], [2, 7]]).concat([
    { id: "foe1", side: "foe", name: "Ogre", foe: "Ogre", pos: [13, 5], react: "auto" },
    { id: "foe2", side: "foe", name: "Goblin 1", foe: "Goblin", pos: [10, 2], react: "auto" },
    { id: "foe3", side: "foe", name: "Goblin 2", foe: "Goblin", pos: [14, 3], react: "auto" },
    { id: "foe4", side: "foe", name: "Goblin 3", foe: "Goblin", pos: [11, 9], react: "auto" },
  ]),
});
