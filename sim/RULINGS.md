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
| R106 | Steady Aim | "Next ranged attack this turn": `mod attack +2`, `next`, `until endSourceTurn`, `params.ranged`. | P 3.4 |
| R107 | Web burning | Fire burns a 5-ft square a round: `zone.burns` plus `zone.burnFt: 5`. Lasting Restrained, Duration 1 hour. | P 10.4 |
| R108 | Instrument reach | Traveler's Lute / Holy Amulet carry the base reach in `params.default` (30 / 60 ft) so every printed number lives in the data. | P 10.6 |
| R109 | Mage Hand | A power with `do: []`: listed in the deck, no combat effect. | P 10.3 |
| R110 | Foe senses | Foe cards keep the printed string ("Darkvision 60"); the export turns it into `senses.darkvision`. Wolf's Keen Nose is `alert: true`. | GM 2.1 |
