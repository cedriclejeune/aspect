# Bearers Combat Sim — Contract

Every agent builds against this file. Don't change it on your own: if you need a schema or API change, stop and report what you need and why. Rules live in `rules/PLAYERS.md` (P) and `rules/GM.md` (GM). `rules/DESIGN.md` explains intent.

## 0. Goal and constraints
- A browser page for playtesting combat. One human plays both sides. It opens from disk (`file://`): **no server, no ES modules, no fetch, no build step**. Plain `<script>` tags only. No external libraries.
- **Headless engine:** `sim/engine.js` never touches the DOM or `window` and also runs under Node 18 (`node sim/test/run.js`).
- **One source of truth for cards:** `cards/base_set.py` and `cards/foes.py`. `tools/export_sim.py` writes `sim/cards.js` from them. Never hand-edit `sim/cards.js`.
- **Rulings:** where the rules are unclear or silent, pick the most plausible reading, mark the code with `// RULING R<n>: ...`, and add a line to `sim/RULINGS.md` (`R<n> · topic · ruling · rule ref`). Number rulings by agent: A uses R100+, B R200+, C R300+, D R400+.
- Write code that reads like the surrounding code. Keep comments sparse and to the point.

## 1. File ownership
| Owner | Files |
|---|---|
| A: Card data | `cards/base_set.py`, `cards/foes.py`, `tools/export_sim.py`, `tools/check_cards.py`, `tools/build_cards.py` (only to call the export), `sim/cards.js` (generated) |
| B: Engine core | `sim/engine.js`, `sim/test/**` |
| C: UI | `sim/index.html`, `sim/ui.js`, `sim/style.css`, `sim/dev/**`, `sim/scenarios/**` |
| D: Card effects (phase 2) | `sim/effects.js`, `sim/test/effects/**` |
| Lead | `sim/SPEC.md`, `sim/README.md`, `sim/RULINGS.md` (anyone may *append*), git |

Page load order: `cards.js`, `engine.js`, `effects.js`, `ui.js`.

## 2. `sim/cards.js`
```js
globalThis.BEARERS_CARDS = { /* JSON below */ };
if (typeof module !== "undefined") module.exports = globalThis.BEARERS_CARDS;
```
```jsonc
{
  "version": 1,
  "cards": { "<id>": Card },           // every card with an ID (P 12.1), keyed by ID, e.g. "W-I-02"
  "decks": { "<cover id>": Deck },
  "foes": [Foe],
  "frames": [{ "key": "hand", "name": "Hand", "perPlayer": 2 }],  // starting Slot counts: armor 1, hand 2, jewelry 1, item 2, aspect 3
  "starter": { "Armor": ["<id>"], "Hands": [], "Jewelry": [], "Items": [], "Aspects": [] }
}
```
**Card**
```jsonc
{
  "id": "W-I-05", "name": "Finesse Blade", "rank": "I",
  "kind": "core" | "gear" | "aspect",
  "type": "Weapon",                    // first keyword: Core Armor Weapon Shield Instrument Jewelry Consumable Recipe Purse Spellbook Trait Technique Knack Divine Glamour Nature
  "kw": ["Weapon", "Finesse"],         // keywords split on " · "
  "text": ["..."],                     // printed text, markdown ** and *
  "strip": { "STR": 1, "STRd": 1, "SPD": 5 },   // integers. Core: absolute values; other cards: bonuses. Keys STR DEX INT WIL STRd DEXd INTd WILd HP SPD
  "group": "starter" | "loot",
  "size": "Medium",                    // Cores only
  "req": { "STR": 1 },                 // Req X +N, if any
  "noisy": 3,                          // if any
  "uses": 3,                           // Recipe flasks, if any
  "atk": WeaponAtk,                    // Weapons only
  "fx": [Power],                       // mechanics; [] = no combat effect (Knacks, Guild Signet...)
  "deck": "<cover id>"                 // on deck covers only
}
```
**WeaponAtk**: `{ "hit": 2, "dice": "1d8", "two": "1d10" | null, "abil": ["STR"] | ["STR","DEX"] | ["DEX"], "type": "Physical", "finesse": bool, "light": bool, "heavy": bool, "reach": bool, "twoHanded": bool, "loading": bool, "thrown": [20,60] | null, "range": [150,600] | null }`

**Deck**
```jsonc
{
  "cover": "B-I-01", "kind": "spellbook" | "glamour" | "divine" | "nature",
  "atk": 2,                            // Spell attack / Attack bonus (absent for nature)
  "sp": 4, "maxLevel": 2,              // spellbook
  "resolve": 3,                        // WIL decks: printed Resolve (pool = resolve + WIL, min 1)
  "fate": "1d4",                       // divine
  "powers": [Power]                    // one per spell / power card, in deck order
}
```
**Foe**
```jsonc
{
  "name": "Ogre", "core": "C-II-01" | null,
  "body": { "STR": 5, "DEX": 0, "INT": 0, "WIL": 1, "HP": 110, "SPD": 40, "size": "Large" } | null,
  "carries": ["W-I-13", "..."],        // card IDs it equips (Slots inferred from type)
  "bonus": { "HP": 33 }, "extraDice": 1,
  "powers": ["Bane", "Twist Fate"],    // deck powers it uses ([] = all)
  "senses": { "darkvision": 60 }, "alert": false, "boss": false,
  "own": ["plain text"], "ownFx": [Power],   // plain-text powers as mechanics
  "totals": { "STR": 4, "...": 0 }     // as printed on the foe card (for cross-checking)
}
```

### 2.1 Power (`fx` entries and deck powers)
Every key is optional except `use`. Engine code (B) handles the generic keys; anything with `hook` is a named special case (implemented by D).
```jsonc
{
  "id": "Q-I-02#0",                    // card ID + "#" + index; deck powers: cover ID + "#" + slug ("B-I-01#fire-bolt")
  "name": "Steady Aim",                // deck powers: power name; card fx: card name unless the card has several
  "kind": "Cantrip" | "Spell" | "Anthem" | "Dirge" | "Cue" | "Mend" | "Form" | null,
  "cost": 1,                           // spell points (spell level) or Resolve
  "use": "action" | "bonus" | "reaction" | "trigger" | "passive" | "free",
  "uses": "2/SR" | "1/LR",             // limited uses (reset at the start of each fight, GM 2.1)
  "recharge": 5,                       // Recharge 5–6
  "on": Trigger,                       // reaction and trigger only
  "need": ["shield"],                  // shield | emptyHand | voice | attackAction | melee | ranged | weapon
  "reach": 30,                         // range in ft from the user (5 = touch or within 5 ft)
  "target": "self" | "creature" | "ally" | "enemy" | "allies" | "enemies" | "point" | "darts",
  "count": 3,                          // max targets for allies/enemies/darts; absent = all in reach
  "area": { "shape": "cube" | "sphere", "size": 10 },   // cube: side; sphere: radius around the point
  "zone": { "terrain": "difficult", "on": ["enter", "endTurn"], "burns": true },   // area persists (Grease, Web)
  "atk": { "abil": ["DEX", "WIL"] | "deck", "hit": 2, "flat": 5, "vs": "DEX" },  // "deck" = deck's ability + atk; flat = total bonus (foe plain text)
  "half": true,                        // half damage on a miss
  "do": [Effect],
  "dur": "instant" | "1 round" | "1 minute" | "1 hour",
  "lasting": true,                     // effect is Lasting (maintain rolls, P 8)
  "subdue": false,
  "tags": ["fear"],                    // fear, mind control, poison, illusion, fire...
  "upcast": { "darts": 1 },
  "form": Form,                        // kind Form only
  "hook": "twin_strike",               // special handling (D)
  "params": { }                        // hook parameters, numbers taken from the card
}
```
**Trigger** (`on`):
| value | when |
|---|---|
| `hitSelf` | an attack hits you (before damage) |
| `hitAlly5` | an attack hits an ally within 5 ft of you |
| `meleeHitSelf5` | a creature within 5 ft hits you |
| `rollNear` | a creature within `reach` rolls an attack or check (Cues; before the hit is announced) |
| `weaponHit` | you hit with a weapon attack |
| `hit` / `crit` | an attack **with this weapon** hits / crits (weapon riders) |
| `meleeDrop` | your melee attack drops a creature to 0 HP |
| `attackAction` | you take the Attack action |
| `hitEngaged` | you hit a creature one of your allies is engaged with |
| `opportunity` | your opportunity attack with this weapon |

**Effect** (`do` entries)
```jsonc
{ "dmg": "1d10", "type": "Fire" }            // dice may add a flat or ability: "1d4+1", "2d8+WIL"
{ "heal": "2d4+2" }
{ "cond": "Prone" }                          // P 8 condition; with power.lasting → lasting effect
{ "mod": "attack" | "def" | "roll" | "dmg", "n": -2, "dice": "-1d4", "defs": ["STR","DEX"],
  "next": true,                              // only the next roll
  "until": Until }
{ "reroll": true }
{ "move": "teleport" | "safe", "ft": 30 | "half" }   // safe = no opportunity attacks
{ "dash": true }
{ "shove": true }
{ "attack": "melee" }                        // make one extra attack (Cleave)
```
**Until**: `endTargetTurn` (end of the target's next turn) · `startSourceTurn` (start of the source's next turn) · `endSourceTurn` (end of the source's next turn) · `dur` (the power's duration) · `lasting`.

**Passive keys** (`use: "passive"`): `attacks: 2` · `defVs: { "WIL": 2 }` + `tags` · `extraResolve: 1` · `extraSp: 1` · `anthemReach: 60` · `cueReach: 90` · `castingHand: true` · `darkvision: 60` · `hook` + `params` (Close Order, Brace, Pierce...).

**Form**: `{ "strip": { "STR": -2, "DEX": 3, "STRd": 8, "DEXd": 13, "HP": 4, "SPD": 10 }, "size": "Tiny", "fly": 60, "climb": 0, "weapon": { "name": "Talons", "hit": 2, "dice": "1d4", "abil": ["DEX"], "type": "Physical" } }`

## 3. Scenario (saved and exported JSON)
```jsonc
{
  "version": 1, "name": "4 starters vs bandits", "seed": 12345,
  "map": { "w": 16, "h": 12, "cells": { "3,4": "wall", "5,5": "difficult", "6,2": "cover", "7,7": "dark" } },
  "surprise": null | "pc" | "foe",            // which side is surprised
  "creatures": [ {
    "id": "pc1", "side": "pc" | "foe", "name": "Bram",
    "build": Build, "pos": [2, 3],              // top-left square; Large = 2×2
    "react": "ask" | "auto" | "never"
  } ]
}
```
**Build**
```jsonc
{
  "core": "C-I-01" | null, "body": { ... } | null,      // body as in Foe
  "armor": "A-I-02" | null,
  "hands": ["W-I-06", "S-I-01"],                         // in hand at the start; extra carried weapons in "carried"
  "carried": ["W-II-02"],                                // weapons on the belt (swap with the free interaction)
  "jewelry": ["J-I-01"], "items": [{ "id": "P-I-01", "n": 1 }], "aspects": ["Q-I-05"],
  "slots": { "hand": 2, "jewelry": 1, "item": 2, "aspect": 3 },
  "bonus": {}, "extraDice": 0, "ownFx": [], "powers": [], "boss": false, "senses": {}, "alert": false,
  "foe": "Ogre" | null                                   // template it came from, if any
}
```

## 4. Engine API (`sim/engine.js`)
UMD: `globalThis.BearersEngine = {...}` and `module.exports` under Node.
```js
const Eng = BearersEngine;
Eng.totals(build, cards)        // → { STR, DEX, INT, WIL, STRd, DEXd, INTd, WILd, HP, SPD, size, errors: [] }  (tally card, P 12.3; empty Armor Slot +10 SPD)
Eng.validate(build, cards)      // → [string]  Slot limits, types per Slot, Requirements (P 3.1), no duplicate copies (P 3.6)
Eng.fromFoe(foe, cards)         // → Build
const f = Eng.createFight(scenario, cards)   // → Fight
f.state                         // plain JSON, serializable; the UI reads it, never writes it
f.legal(actorId)                // → [Command templates] the UI turns into buttons
f.preview(cmd)                  // → { ok, error, info }  e.g. dice count, to-hit, Defense, Outnumbered breakdown, path cost, provoked OAs
f.do(cmd)                       // → { ok, error, events: [Event] }   applies a command or answers a prompt
f.pending                       // null | Prompt — while set, only { type: "answer" } is accepted
f.undo()                        // back one command (unlimited)
f.events                        // full event log
f.summary()                     // → Summary (section 6)
f.export()                      // → { scenario, commands, events, summary }  replays deterministically
Eng.replay(exported, cards)     // → Fight
```
### 4.1 State (read-only for the UI)
```jsonc
{
  "round": 1, "side": "pc" | "foe", "first": "pc", "phase": "setup" | "fight" | "over", "winner": null,
  "active": "pc1" | null, "done": ["pc2"],          // turns taken this side-turn
  "halfTurn": { "foe1": false },                     // Boss half turn used this round
  "map": { ... }, "zones": [ { "id", "cells": ["x,y"], "power", "source", "until" } ],
  "creatures": { "<id>": {
    "id", "side", "name", "pos": [x,y], "size", "totals": {...}, "hp", "maxHp", "temp",
    "form": null | { "power", "hp", "maxHp", "totals" },
    "dead": false, "down": false, "stable": false, "death": { "ok": 0, "fail": 0 },
    "conds": [ { "name": "Prone", "source": "foe1", "until": "...", "lasting": true, "subdue": false, "rolls": 0, "hurt": 0 } ],
    "mods": [ { "kind": "attack", "n": 2, "dice": null, "next": true, "until": "...", "source": "pc3", "power": "..." } ],
    "turn": { "moved": 0, "speed": 30, "action": false, "bonus": false, "reaction": false, "interact": false, "spellCast": false, "disengaged": false, "dodging": false, "firstMover": false },
    "hands": [...], "carried": [...], "items": [...],
    "uses": { "<power id>": 1 }, "sp": { "<deck id>": 4 }, "resolve": { "<deck id>": 6 }, "extra": { "sp": 0, "resolve": 0 },
    "react": "ask"
  } },
  "rng": { "seed": 1, "s": 1 }
}
```
### 4.2 Commands (`{ type, actor, ... }`)
| type | fields | rule |
|---|---|---|
| `start` | — | side initiative: d20 + average DEX (rounded down), surprise = disadvantage, re-roll ties (P 6.1) |
| `beginTurn` | `actor` | pick who acts next on the active side; `half: true` for a Boss half turn on the other side (GM 3) |
| `move` | `actor, path: [[x,y],...]` | cost, difficult terrain, Prone crawl, stand up (`stand: true`), provoked OAs (P 6.4–6.5) |
| `attack` | `actor, weapon: "<card id>" \| "unarmed" \| "improvised" \| "natural", target, thrown: bool` | P 6.6–6.9; two-weapon bonus attack: `offhand: true` |
| `act` | `actor, action: "dash" \| "disengage" \| "dodge" \| "help", target?` | P 6.3 |
| `shove` / `grapple` / `escape` | `actor, target, mode: "push" \| "prone"` | P 6.10 |
| `power` | `actor, power: "<power id>", targets: [id], point: [x,y], level` | spells, deck powers, card powers |
| `interact` | `actor, draw: "<card id>", stow: "<card id>"` | free object interaction: swap a carried weapon in hand, pick up a thrown one |
| `note` | `actor, text` | free-text "Other" action, logged |
| `endTurn` | `actor` | end-of-turn effects; the side ends when every able creature has acted |
| `answer` | `choice: <option index> \| null, roll: n` | answers `f.pending` |
| `adjust` | `actor, hp?, cond?, remove?` | manual override, logged as such |

**Prompt** `{ "id", "kind": "reaction" | "choice" | "roll", "text", "trigger": {...}, "options": [ { "actor", "power", "label" } ] }`. Reactions the creature's `react` mode decides automatically don't prompt: `auto` takes opportunity attacks and uses defensive reactions only when they turn a hit into a miss; `never` declines.

**Manual dice:** `f.setManualDice(true)` → each die roll becomes a `roll` prompt (`answer.roll`).

**Implementation note (recommended):** make every external input (reaction choices, manual rolls) an *answer* consumed in order. When resolution needs one that isn't there yet, raise `pending`, restore the snapshot taken before the command, and re-run the command with the answers so far once it comes. Because the RNG lives in `state.rng`, the re-run rolls the same dice. Undo = restore the snapshot before the last command.

### 4.3 Events
`{ "t": type, "round", "actor", "target", "text": "human-readable log line", ...data }`. Types: `round`, `turn`, `initiative`, `move`, `roll` (`dice: [..], kept, bonus, total, vs, adv, dis, why: [...]`), `hit`, `miss`, `crit`, `damage` (`n, type, resisted`), `heal`, `temp`, `cond`, `condEnd`, `maintain`, `down`, `death`, `deathSave`, `stable`, `power`, `reaction`, `resource` (`what, n`), `shift`, `revert`, `note`, `adjust`, `over`.

## 5. Effects plug-in (`sim/effects.js`, phase 2)
`BearersEngine.registerHook(name, { onUse?, onTrigger?, modifyAttack?, modifyDamage?, passive? })`. B defines the hook points and the context object (`ctx.fight, ctx.actor, ctx.power, ctx.attack, ctx.roll(dice), ctx.emit(event), ctx.ask(prompt)`) and documents them at the top of `engine.js`. Unknown hooks log `"<card>: not automated"` and offer a manual note.

## 6. Summary
```jsonc
{ "rounds": 4, "winner": "pc", "seed": 1,
  "creatures": { "<id>": { "name", "side", "dmgDealt", "dmgTaken", "healed", "attacks", "hits", "crits", "kills", "downs", "roundsAlive", "spent": { "sp": 0, "resolve": 0, "uses": 0, "consumables": 0 }, "endHp" } } }
```
CSV export: one row per creature with those columns.
