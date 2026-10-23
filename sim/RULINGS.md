# Sim rulings

Interpretations the sim makes where the rules are unclear or silent. Each one is marked in code with `// RULING R<n>`. Approve, fix or fold into the rulebooks.

| # | Topic | Ruling | Rule |
|---|---|---|---|
| R100 | Dirge range | Dirges (Jeer, Dread, Bane) reach 60 ft and need the caster's voice; the text gives no range. Cues and Anthems use the printed 60 / 30 ft. | P 10.6 |
| R101 | Divine / Glamour voice | Every Divine and Glamour power, Mends included, carries `need: ["voice"]`. Nature (Mossbalm) does not. | P 10.6 |
| R102 | Cue targets | Cutting Words targets an enemy, Steady Now and Guidance an ally, Twist Fate any creature. Guidance affects checks only. Steady Now's "or the Defense an attack targets" is `params.orDefense`. | P 10.6 |
| R103 | Natural weapon vs Defense | Foe plain-text attacks (Wolf Bite) use `vs: "weapon"` = the higher of STR and DEX Defense, with `flat` as the total bonus. | P 6.6, 10.7 |
| R104 | Ring of Warding / Shield Wall | The +2 is a `mod def` with `defs: ["targeted"]` (whichever Defense the attack targets) and `next: true` (this attack only). | P 3.4 |
| R105 | Ring of Sparks | The 2d6 Lightning goes to the creature that hit you (target `enemy` = the trigger's attacker). | P 3.4 |
| R106 | Steady Aim | "Next ranged attack this turn": `mod attack +2`, `next`, `until endThisTurn`, `params.ranged`. | P 3.4 |
| R107 | Web burning | Fire burns a 5-ft square a round: `zone.burns` plus `zone.burnFt: 5`. Lasting Restrained, Duration 1 hour. | P 10.4 |
| R108 | Instrument reach | Traveler's Lute / Holy Amulet carry the base reach in `params.default` (30 / 60 ft) so every printed number lives in the data. | P 10.6 |
| R109 | Mage Hand | A power with `do: []`: listed in the deck, no combat effect. | P 10.3 |
| R110 | Foe senses | Foe cards keep the printed string ("Darkvision 60"); the export turns it into `senses.darkvision`. Wolf's Keen Nose is `alert: true`. | GM 2.1 |
| R201 | Foe Speed | Builds from a foe template (`build.foe`) skip the empty Armor Slot's +10 Speed: foe cards print totals without it (Ogre 35 ft). | P 12.3, GM 2.1 |
| R202 | fromFoe Hands | A Shield always goes in a Hand; other Hand gear fills the rest in `carries` order, the remainder is carried (Legionary: Pilum + Shield, Gladius carried). Slots grow to fit. | GM 2.1 |
| R203 | Requirements | Count the Core plus every other equipped card's positive bonuses; an unmet card adds nothing to the totals and is reported. | P 3.1 |
| R204 | Line of sight, cover | Center-to-center lines between any squares of both creatures; walls block; "cover" squares on every clear line give +2; creatures never give cover; no clear line = full cover. | P 6.8 |
| R205 | In Dark | A creature is in Dark when every square it occupies is Dark. | P 5.5 |
| R206 | Durations | A Duration counts the source's turn starts (1 minute = its 10th turn start after casting). Boss half turns don't count. | P 10.4 |
| R207 | Condition stacking | The same condition from the same source replaces the old one; from another source both are kept, the effect counts once. | P 8 |
| R208 | Unconscious target | Counts as Stunned and Prone: two advantage sources within 5 ft. Petrified counts as Stunned. | P 5.2, P 8 |
| R209 | Steady Now on a foe's roll | A Cue with `orDefense` used on an enemy's attack adds its number to the targeted ally's Defense. | P 3.4 |
| R210 | Auto reactions | "auto" uses a defensive reaction only when it turns the hit into a miss, otherwise a retaliation reaction (Ring of Sparks); never one that changes nothing. | SPEC 4.2 |
| R211 | Extra pools | A cost is paid wholly from the deck's own pool, or wholly from the extra pool when the own pool can't cover it (or `pool: "extra"`). | P 10.2, P 10.6 |
| R212 | Empty stacks | An empty Consumable stack leaves its Item Slot; a Recipe keeps its Slot at 0 flasks. | P 3.2 |
| R213 | Foes at 0 HP | Foes die at 0 HP unless the build sets `important: true`; then they follow the Bearer rules (Unconscious, death saves). | GM 2.1 |
| R214 | Healing a Form | Healing a shifted creature restores the Form's HP pool; its own HP waits. | P 10.7 |
| R215 | Interrupted moves | Movement stops when a zone or reaction leaves the mover Prone, at speed 0, Incapacitated or down. | P 6.4 |
| R216 | Optional triggers | A trigger with limited uses or a cost is optional (react mode: ask prompts, auto uses it, never skips); a free trigger (weapon rider) always applies. | P 11.2 |
| R217 | "Allies" | "ally"/"allies" never include the user (Rally, Bless, Battle Hymn). Trigger buffs on allies pick the nearest in reach that can hear, up to `count`. | P 10.6 |
| R218 | Cube placement | A cube of side N covers N/5 squares a side, centered on the chosen square (an even side extends right and down). Spheres use 5-ft diagonals (radius 5 = 3×3). Full cover from the point blocks squares. | P 10.5 |
| R219 | Natural attack powers | A power attack against "weapon" Defense within 5 ft (Wolf's Bite) is a melee weapon attack for triggers (weaponHit, hitEngaged, meleeDrop, Ring of Sparks). | P 6.6 |
| R220 | Zone triggers | A zone attacks a given creature at most once per turn (entering, then ending the turn there). | P 10.5 |
| R221 | Maintain modifier | Maintain rolls use the source's bare modifier for the effect's ability (deck ability, or the better of the two printed): its Core's or foe body's, or its Form's STR and DEX while shifted; no Rank, gear or Aspect bonus. Foes and flat-bonus effects use their highest bare modifier. Exhaustion applies, nothing else. | P 8 |
| R222 | Thrown weapons | A thrown weapon leaves the Hand and lands in the target's square (pick it up within 5 ft with the free interaction). Javelins are a bundle: they stay in hand. | P 6.7 |
| R223 | Outnumbered vs Incapacitated | Read as written: an Incapacitated creature engages no one, so a lone Stunned or Unconscious target gives its attackers Outnumbered 1 vs 0. | P 6.5 |
| R224 | Ranged powers | A power attack with a range above 5 ft is a ranged attack (enemy within 5 ft: disadvantage); long range doesn't apply to powers. | P 6.7 |
| R225 | Multi-target attacks | An attack power on "allies"/"enemies" without an area (Bellow) rolls once for all, like an area. Darts (Magic Missile) roll once per target creature, damage per dart. | P 6.6 |
| R226 | Cues | Cues fire on attack rolls only (the sim makes no ability checks); "auto" uses a flat Cue only when it flips the outcome and never uses Reroll; an "ally" Cue never targets the user's own roll. | P 10.6 |
| R227 | Boss half turn | Works like the first-mover rule (movement or one action), no bonus action. Durations ignore half turns; maintain rolls and first bite don't. | GM 3, P 8 |
| R228 | Dragging a grapple | The grappler drags its grappled creatures into the square it leaves; +5 ft per square unless they are two sizes smaller. | P 6.10 |
| R229 | Frightened movement | No step may bring the creature closer to a fear source it can see. | P 8 |
| R230 | Flying Forms | A Form's Fly speed replaces its walking speed (no altitude) and ignores difficult terrain. | P 10.7, P 11.5 |
| R231 | Who sees | Unconscious and Stunned creatures still count as seeing for unseen advantage; only Blinded, Dark, Invisible and walls hide. | P 5.2, P 8 |
| R232 | Turns at 0 HP | Every living creature takes a turn, even at 0 HP (its death save) or Incapacitated; those turns end on their own. A side ends when all its living creatures have acted. | P 6.1, P 7.4 |
| R233 | Versatile | A Versatile weapon uses its bigger die whenever the wielder's other Hand Slot is empty. | P 11.3 |
| R234 | Exhaustion | −2 per level on attack and maintain rolls; not on death saves ("no modifiers") or side initiative. | P 8 |
| R235 | The dead | The dead drop what they hold; dead bodies never block movement. | P 6.4 |
| R236 | "End of the source's next turn" | `endSourceTurn` set during the source's own turn lasts to the end of its next turn; extra value `endThisTurn` = the current turn (Steady Aim should use it). | P 3.4 |
| R237 | Help | +3 on the ally's next attack against a creature within 5 ft of the helper, until the start of the helper's next turn. | P 6.3 |
| R238 | Lasting on allies | A Lasting effect is Lasting on anyone it holds, allies and its own source included (Web): maintain rolls each turn, as for enemies. | P 8, P 10.4 |
| R239 | Resistances | Come from `build.resist` / `build.vuln` (or a passive `resist`/`vuln` list); Petrified resists everything. | P 7.2 |
| R240 | Auto opportunity attacks | "auto" uses the first melee weapon in hand (else unarmed or the Form's natural weapon). | P 6.5 |
| R241 | Standing up | Costs exactly half speed, no rounding (35 ft → 17.5 ft). | P 6.4 |
| R242 | Carried weapons | `Build.carried` weapons swap into a Hand with the free object interaction, like drawing. | P 3.5, SPEC 3 |
| R243 | Zones after their source falls | A zone keeps attacking with its source's current bonus, even while the source is down. | P 10.5 |
| R400 | Ring of Sparks trigger | "When a creature within 5 ft hits you" counts any attack from within 5 ft (ranged, spell or melee). | P 3.4 |
| R401 | Pierce | Any hit with the Pilum (thrown or in melee) pierces a Shield the target holds: a "Pierced" condition switches the Shield's bonuses off until the target spends an action to pull the pilum free (`act` action `endCond`). No Shield in hand, no effect. | P 3.4 |
| R402 | Fire on a Web | Fire burns one 5-ft square of a burning zone a round (`zone.burnFt`): the impact point's or the burned creature's square, else the first one the fire touches. A creature no longer standing in any square of the zone is free of it. | P 10.4 |
| R403 | Speed when shifting | Shifting or reverting on your turn changes the movement left by the change in Speed; feet already moved stay spent. | P 10.7 |
| R404 | Dead sources | A dead source takes no more turns: each new round counts as its turn start and end for the Durations and timers it left. | P 10.4 |
| R405 | Zone attacks | A zone's later attacks (entering, ending a turn there) use only its source's attack bonus: the source's mods (Bless, Battle Hymn) and situations don't apply, and a dead source's zone still attacks. | P 10.5 |
| R406 | Fear and charm | Frightened and Charmed end when their source dies. | P 8 |
| R407 | Boss half turn | A half turn doesn't restore the reaction, end a Dodge or roll Recharge 5–6; it comes only between two characters' turns (any time if one character is left). | GM 3, P 6.2 |
| R408 | Beasts' Hands | A foe built on a body that carries no Hand gear has no Hand Slots (Wolf): no picking up, drawing or wielding gear. | GM 2.1 |
| R409 | Cleave | The extra attack targets another creature than the one that dropped and is lost if the attacker moves first. | P 3.4 |
