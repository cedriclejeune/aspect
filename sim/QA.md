# Sim QA report (agent E)

Branch `combat-sim`, 2026-10-22. Engine as of the `ed8465d` working tree, with `effects.js` (close_order, brace, pierce) once it appeared. Scripts live in `/tmp/claude-1000/qa/` (scratch): `harness.js` (scripted policy + invariant checks), `run.js` / `run2.js` / `run3.js` / `agg.js` (fight sets), `t_*.js` (targeted repros).

**Method.** About 250 complete fights, all driven through `f.do`. The scripted policy: move to the nearest conscious enemy, attack with the best weapon, sometimes use a power (Bless, Bane, Magic Missile, Web, Grease, Fire Bolt, Bite, Bellow, potions, Second Wind, Steady Aim, Shield Bash, Pocket Sand), off-hand attacks, and the Boss half turn. Prompts get a random option or a decline. After every command the harness checks these invariants:
- engine exceptions;
- HP and resource bounds;
- dead creatures acting;
- legal() offering attacks to Incapacitated creatures;
- Outnumbered (attack and power previews) against an independent P 6.5 implementation;
- Disengage cost against the P 6.5 table;
- condition and mod ages (more than 12 rounds);
- maintain rolls at turn start;
- uses at fight start;
- summary totals against the event log;
- export → replay determinism.

None of these checks fired in normal play (0 exceptions, 0 refusals of policy commands, 0 Outnumbered or Disengage mismatches, 0 summary mismatches, replay identical). Every bug below came from reading the log or from a targeted script.

`node sim/test/run.js`: 1 failing test in `sim/test/effects/cards.test.js:373` at the time of the run (agent D's work in progress).

## 1. Bugs

| # | Sev | Repro | Expected (rule) | Actual |
|---|---|---|---|---|
| B1 | High | `t_spot3.js`: Cleric casts Bless, Mage casts Grease, then both die (`adjust dead`). Play 12 more rounds. | Bless, Grease and any "until"/Duration end after their time (P 9.3 "set duration"; Bless 1 minute = 10 rounds). | At round 14 the Fighter still has Bless (`rounds: 10` left) and the Grease zone still exists. Durations count the **source's** turn starts (R206, R236, Help R237), and a dead source has no more turns, so they never end. This also hits Bellow's "until the end of its next turn" and `endSourceTurn` mods. |
| B2 | High | Same script: after the Mage dies, the Fighter moves into the Grease: `move path [[3,5],[4,4],[5,4],[6,4]]`. | The zone attacks with the source's bonus (R243) or has ended. | `preview` says ok, but `do` refuses the move: `"Not a living creature"`. `attackInfo` fails on a dead attacker inside `triggerZone`, so a dead caster's zone blocks movement into its squares. |
| B3 | High | `t_spot3.js`: the Ogre Chieftain's Bellow hits Weakwill (half turn, round 1). The Chieftain dies. Play 5 rounds. | Frightened ends at the end of the Chieftain's next turn (Bellow text), or when its source is gone (P 8 "until its source ends it or its duration expires"). | At round 7 Weakwill is still Frightened, and `move` toward the corpse is refused ("can't move closer to Boss"). `canSee` doesn't check whether the target is dead, so the corpse also counts as "in sight" for the Frightened disadvantage. Same root cause as B1, plus `sweep` only clears Lasting and Grappled conditions. |
| B4 | High | Harness `4 vs Ogre Chieftain`, seed 1, round 2: Isolde casts Web on the Chieftain's square (allies adjacent). Round 3: Isolde walks into her own Web. | Web: "on a hit, it is **Restrained** (Lasting)". P 8: a lasting effect "holds a creature until it breaks free (a web…)". | Under R238, Bram, Wren, Aldo and later Isolde herself are Restrained with `until` = 600 turn starts (1 hour). They get no maintain roll and have no escape action, while the enemies in the same Web can break free. See ruling R238 below. |
| B5 | Med | `t_spot.js`: the Chieftain makes an opportunity attack on Bram's move (`turn.reaction = true`), then `beginTurn foe1 half:true`. | Reaction: one per round, regained "at the start of **your turn**" (P 6.2). A half turn is "its movement or one action" (GM 3). Recharge rolls "at the start of the monster's turn" (GM 2.1). | `startTurn` runs `freshTurn` on the half turn, so the Boss gets its reaction back, loses an active Dodge, and also rolls Recharge 5–6 (an extra recharge chance each round). No ruling covers this (R227 doesn't mention it). |
| B6 | Med | `t_bless.js`: Aldo casts Bless in round 1 and again in round 2. Also the harness Ogre fight, seed 4: Bane cast twice on the Ogre. | Needs a ruling. P 8: conditions don't stack with themselves. DESIGN 5: "buffs stack" across cards. Nothing covers re-casting the same power on the same target. | Bram has two Bless mods (+2d4). The Ogre has two −1d4 Bane mods under one Lasting record (its attack in round 2: 6 − 2d4). One Resolve per cast, so it is cheap to stack. |
| B7 | Low | Sample Boss scenario, seed 1, round 3: Wolf 2's Bite hits Unconscious Bram from 5 ft. | P 8: any hit from within 5 ft on an Unconscious creature is a critical hit. | The engine treats it as a crit (doubled dice, 2 death-save failures), but the event says "Bite **hits** Bram" and `stats.crits` isn't incremented (`doPower` single-target branch: the crit is recomputed after the hit/crit event and the stats update). |
| B8 | Low | Sample Boss scenario, seed 1, round 3: "Wolf 1 picks up Longsword", "Wolf 2 picks up Shield". | Beasts have no Hands. `fromFoe` gives every foe `slots.hand: 2`. | `legal()` offers "Pick up" and "Draw" to Wolves, which can then wield dropped weapons. |
| B9 | Low | `t_spot3.js`: `adjust {actor: pc1, hp: 0}` on a Bearer. | 0 HP means Unconscious and death saves (P 7.4). | HP 0 with no Unconscious, `down: false`. The reverse case (0 → above 0) is handled. |
| B10 | Low | Harness Chieftain fight, seed 1, round 3: Fire Bolt hits the Large Chieftain inside the Web. | Web: "Fire burns a **5-ft square** away each round." | `burnZones` removes every square under the burned creature (4 for a Large one) on every Fire hit, with no per-round cap; `zone.burnFt` is unused. Creatures in burned squares stay Restrained. |
| B11 | Low | Code read: `hitReactions`, `meleeHitSelf5`. | Ring of Sparks: "when a creature within 5 ft hits you" (any attack). | Fires only on melee attacks: a ranged or spell hit from 5 ft doesn't trigger it. |
| B12 | Low | `boss` demo screenshot; `planBegin`. | GM 3: the half turn comes "between any two characters' turns". | "Boss half turn" is offered before the first character's turn of the round. |
| B13 | Low | Code read: Cleave (`d.attack` → `turn.bonusMelee++`). | "make one melee attack against **another** creature within your reach", at the moment the drop happens. | The extra attack can target anyone, a downed Bearer included (the Chieftain has Cleave), and can be spent later in the turn after moving. |
| B14 | Low | `run3.js` seed 1: "Legionary 2 attacks with Pilum → Bram: … +4", with `why` = [Restrained, +3 STR, +3 to hit]. | The log should explain the total. | Dice mods (Bless +1d4, Bane −1d4, Help in some cases) are rolled into `bonus` but never listed in `why` or in the preview "Why". |
| B15 | Low | Harness Chieftain fight, seed 1, round 3: "Isolde Web → Isolde: 19 +13". | Needs a ruling. | A zone attacking its own caster or her allies uses her Bless and consumes her Battle Hymn "next attack" +2. |
| B16 | Low | Area attacks (`doPower`, area branch). | P 6.6: individual target situations don't apply to an area roll. | The roll uses `attackInfo` on `targets[0]` only, so the attacker's "can't see the target" disadvantage depends on which creature happens to be listed first. |
| B17 | Low | Event text. | — | "Druid spends 3 Resolves." should read "3 Resolve". |

**Notes (not bugs).**
- Summary `dmgDealt` and `dmgTaken` count raw damage, including overkill and damage absorbed by temporary HP or a Form. HP changed through `adjust` isn't counted at all (summary demo: Bandit 2 has End HP 0 and Dmg taken 0).
- Foes pick up Bearers' dropped gear and use it (a Cultist with Aldo's Shortsword). The rules allow this.

## 2. Rulings audit

| # | Verdict | Note |
|---|---|---|
| R100 | Fills a real gap (reasonable) | No Dirge range is printed; 60 ft matches Cues. |
| R101 | Matches the rules | P 9.5: Divine and Glamour need the voice; a Mend target needn't hear; "Nature needs no voice". The Glamour dance (sight instead of hearing) isn't modeled. |
| R102 | Fills a real gap (reasonable) | Matches the card texts (Guidance: "after an ally … rolls a check"). |
| R103 | Matches the rules | Consistent with P 9.6 natural weapons ("higher of STR and DEX Defense, like a weapon"). |
| R104 | Matches the rules | Card: "+2 to the targeted Defense against that attack". |
| R105 | Matches the rules | Card: "it takes 2d6 Lightning". But see B11: the trigger is narrower than the card. |
| R106 | Matches the rules (stale text) | The ruling says `until endSourceTurn`, but the data correctly uses `endThisTurn` ("this turn"). Update the R106 line. |
| R107 | Fills a real gap, partly implemented | `burnFt` is ignored (B10). |
| R108 | Fills a real gap (reasonable) | Data detail only. |
| R109 | Matches the rules | — |
| R110 | Fills a real gap (reasonable) | — |
| R201 | Contradicts the rules | P 12.3: "An empty Armor Slot adds +10 Speed"; GM 2.1: foes follow the "same rules as Bearers". It matches the printed foe totals (Ogre 35 ft, Wolf 40 ft), so either the foe cards or the rule is wrong. Designer call. |
| R202 | Fills a real gap (reasonable) | Matches the Legionary note "throws its Pilum, then draws its Gladius". |
| R203 | Matches the rules | P 4.1: "You can equip it only if your Calling shares at least one of its lit affinities." (was the Requirement rule before Callings) |
| R204 | Fills a real gap (reasonable) | P 6.7 says nothing on how to draw lines or on creatures as cover. |
| R205 | Fills a real gap (reasonable) | — |
| R206 | Fills a real gap, but with a hole | Counting the source's turn starts never ends a Duration once the source dies (B1, B3). |
| R207 | Matches the rules | P 8: "Conditions don't stack with themselves". |
| R208 | Matches the rules | P 8 (Unconscious = Stunned and Prone) and P 6.6 (each source adds one die). |
| R209 | Matches the rules | Steady Now: "or to the Defense an attack targets". |
| R210 | Matches the rules (SPEC 4.2) | — |
| R211 | Retired: the rules now define one pool each (P 9.2, 9.5) | — |
| R212 | Matches the rules | P 4.2: "Consumables are gone once used"; Recipes refill. |
| R213 | Matches the rules | GM 2.1: "At 0 HP, they usually die. You may let important ones fall unconscious." |
| R214 | Fills a real gap (reasonable) | P 9.6 doesn't say how healing works while shifted. |
| R215 | Fills a real gap (reasonable) | — |
| R216 | Fills a real gap (reasonable) | — |
| R217 | Fills a real gap (reasonable) | "Allies" in Bless and Battle Hymn plausibly excludes the user. |
| R218 | Fills a real gap (reasonable) | — |
| R219 | Fills a real gap (reasonable) | — |
| R220 | Fills a real gap (reasonable) | Grease text: "enters it or ends its turn there". |
| R221 | Contradicts the rules | P 8: "d20 + its ability modifier, with **no Rank, gear or Aspect bonus**"; DESIGN 5: "maintain rolls use the bare modifier". R221 uses the tally-card total, which includes gear and Aspect bonuses to the modifier. Base-set starters aren't affected yet (none raises WIL or INT). |
| R222 | Fills a real gap (reasonable) | — |
| R223 | Matches the rules (literal) | P 6.5 counts "its side" only when it is engaged, and an Incapacitated creature isn't engaged. Design question: a lone Stunned target then gives +1 Outnumbered die on top of Stunned. |
| R224 | Matches the rules | P 6.6 (enemy within 5 ft); P 11.3 ("a single number is a spell's maximum range"). |
| R225 | Fills a real gap (reasonable) | Bellow's "each enemy within 30 ft" read as an area roll; Magic Missile: "One spell attack against … each target". |
| R226 | Fills a real gap (reasonable) | P 9.5 lets Cues change any roll (maintain rolls and death saves too). The sim covers attack rolls only; worth noting in the UI. |
| R227 | Matches the rules (GM 3, P 8) | It doesn't cover the reaction reset, Dodge loss and extra Recharge roll on half turns (B5). |
| R228 | Matches the rules | P 6.9. |
| R229 | Fills a real gap (reasonable) | P 8 can be read either way on whether "while in sight" also limits the movement ban. Needs a dead-source check (B3). |
| R230 | Fills a real gap (reasonable) | — |
| R231 | Fills a real gap (reasonable) | — |
| R232 | Matches the rules | P 7.4: death saves "at the start of each of your turns". |
| R233 | Fills a real gap (reasonable) | P 11.3 "held in two hands". The sim assumes a two-handed grip whenever a Hand is free. |
| R234 | Fills a real gap, borderline | P 8: "−2 to all d20 tests". The death-save exclusion follows P 7.4 "no modifiers"; leaving out side initiative (a d20 test) is a stretch, but it is a side roll. |
| R235 | Fills a real gap (reasonable) | A body isn't "a creature's space" (P 6.4). |
| R236 | Matches the rules | Bellow: "until the end of its next turn". |
| R237 | Matches the rules | P 6.3 Help. |
| R238 | Contradicts the rules | Web prints "**Restrained** (Lasting)" for each creature in it, and P 8 says "A lasting effect holds a creature until it breaks free (a web…)". P 9.3's "spell on enemies" split leaves an ally stuck for the full 1 hour with no roll (B4). Suggestion: a lasting effect on an ally is still Lasting (maintain rolls), or the ally can end it as a willing target. |
| R239 | Fills a real gap (reasonable) | P 8: Petrified = resistance to all damage. |
| R240 | Fills a real gap (reasonable) | — |
| R241 | Matches the rules | P 6.4: "Standing up costs half your speed". |
| R242 | Fills a real gap (reasonable) | P 4.5: Hand swap = free object interaction. |
| R243 | Fills a real gap, but broken | When the source is **dead** (not just down), entering the zone is refused (B2). |

**Spot-check of rules without a ruling** (engine.js):
- P 6.6 attack procedure: matches (ability, to-hit, higher of STR/DEX Defense, natural 20/1 on the kept die, crit doubles all damage dice, off-hand without a positive modifier).
- P 6.6 advantage: matches (one die per source, net count, Outnumbered as n dice, area rolls skip target situations; see B16).
- P 6.5 Outnumbered and Disengage: match in every preview checked during the fights. Opportunity attacks fire on leaving reach, not on pushes or Disengage.
- P 7.4 death saves: match (10+, natural 20 → 1 HP, natural 1 → two failures, damage at 0 HP = 1 failure or 2 on a crit, massive damage, healing resets).
- P 8 Lasting and Subdue: match (`t_spot2.js`): first bite skips the maintain roll; weakening adds 1, then 2 disadvantage dice; a hit adds 1; the hurt source counts; a Boss's first bite lands on whichever comes first, turn or half turn.
- P 9.6 Forms: match (fresh tally card, gear merged, separate HP pool, Bless and Mend blocked).
- GM 3 Boss half turn: movement or one action, no bonus action; same Recharge power not twice in a round. See B5 and B12.
- P 6.1 first mover: matches (move then attack refused in round 1, bonus action kept, the second side gets full turns, ambush when the other side is surprised).

## 3. UI (headless Chromium, 1440×900)

`?demo=selftest`: title **SELFTEST PASS**. Every demo renders without a blank page.

| # | Demo | Issue |
|---|---|---|
| U1 | summary | The Cue prompt modal ("Wren rolled 16 vs Bandit 1. Use a Cue?") covers the **Summary** tab. A pending prompt shows on every tab. |
| U2 | summary | Bandits show End HP 0 or 1 with Dmg taken 0 and Rounds alive 1. The demo sets HP through `adjust`, which the summary doesn't count, so the table looks wrong. |
| U3 | boss | "Boss half turn" is available before any character has acted (B12). |
| U4 | prompt | The actor header reads "Bandit 1First mover: move or action": the pill touches the name. |
| U5 | area | The preview table mixes a lowercase key ("range 60") with capitalized ones, and the range has no "ft". |
| U6 | prompt / summary | The Cue prompt shows the roll but not the target's Defense, so the single player can't judge whether the Cue matters (the engine has the number). |
| U7 | builder | Bearers get the foe-only "Conjurer's Book: powers used (all)" checkboxes. Unchecking them would let a Bearer drop spells from a fixed book (P 9.1). |
| U8 | fight / attack | "Disengage (free)" shows even with no enemy engaged. It is noise in the action bar. |

## 4. Balance data

20 seeds per fight. Party: Bram, Wren, Isolde, Aldo (`scenarios/party.js`); 2-Bearer fights use Bram and Wren. The policy is crude: no focus fire, no retreat, random reactions, and Web/Grease aimed at an enemy's square even with allies nearby. Treat these numbers as engine data, not tuning advice. DPR = damage per round dealt by that side (raw, overkill included).

| Fight | PC win | Rounds avg (min–max) | PC DPR | Foe DPR | PC downs / fight | PC deaths (total) | Fights where foes dealt 0 | First Bearer down |
|---|---|---|---|---|---|---|---|---|
| 4 vs 3 Bandits + 2 Archers (road map) | 18/20 | 5.8 (3–11) | 12.9 | 5.3 | 1.1 | 1 | 0 | Bram 4, Wren 3, Aldo 1 |
| 4 vs 4 Wolves | 19/20 | 3.7 (2–8) | 17.1 | 4.0 | 0.8 | 3 | 4 | Aldo 6, Bram 3, Wren 3 |
| 4 vs Ogre | 20/20 | 4.0 (3–7) | 19.1 | 2.0 | 0.3 | 1 | 10 | Aldo 5, Bram 1 |
| 4 vs Ogre Chieftain (Boss, alone) | 17/20 | 6.5 (5–9) | 17.5 | 4.0 | 1.1 | 7 | 12 | Bram 6, Aldo 1 |
| Sample "Boss: the Ogre Chieftain" (+2 Wolves, Cultist) | 4/20 | 7.0 (4–16) | 9.6 | 17.0 | 3.3 | 38 | 0 | Bram 9, Aldo 9, Wren 1 |
| 2 (Bram, Wren) vs 6 Goblins | 0/20 | 2.5 (2–4) | 2.6 | 16.6 | 2.3 | 8 | 0 | Bram 19, Wren 1 |
| 4 vs 3 Legionaries + Bandit Captain + Cultist | 1/20 | 4.5 (2–8) | 5.2 | 22.9 | 4.7 | 33 | 0 | Bram 9, Aldo 8, Wren 3 |

Observations recorded as data:
- Solo Large foes are surrounded by up to 4 Bearers and attack with up to 3 Outnumbered disadvantage dice (1 vs 4). The Ogre dealt 0 damage in 10/20 fights and the solo Chieftain in 12/20. With minions present (sample Boss scenario), the Chieftain side wins 16/20.
- Bellow (+5 vs WIL) rarely lands on Bram or Aldo (Iron Will: +2 WIL Defense against fear); it hits Isolde and Wren (WIL Defense 10).
- Goblins fight two-weapon (Sling + Dagger, both Light), so each Goblin makes 2 attacks a turn. Bram is focused and drops in round 1–2 in 19/20 fights.
- Twist Fate (1 Resolve) is used on most rolls when it is offered; Aldo's 6+1 Resolve usually runs out by round 3.
- Shipped samples: Road ambush, 6 of 8 seeds won by the Bearers; Ogre den, 6 of 8.
