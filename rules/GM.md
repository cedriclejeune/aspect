# BEARERS — Game Master's Guide
*Version 0.1 (draft). Read the Player Rules first: this book only adds what the GM needs to run the world. References like "(P 6.5)" point to the Player Rules.*

---

## Contents
1. [Running the Game](#1-running-the-game)
2. [Monsters](#2-monsters)
3. [Bosses](#3-bosses)
4. [Loot & Rewards](#4-loot--rewards)
5. [Building Encounters](#5-building-encounters)
6. [Bearers in the World](#6-bearers-in-the-world)
7. [Glossary](#7-glossary)
8. [Attribution](#attribution)

---

## 1. Running the Game

### 1.1 Difficulty Classes
| Task | DC |
|---|---|
| Very easy | 5 |
| Easy | 10 |
| Medium | 15 |
| Hard | 20 |
| Very hard | 25 |
| Nearly impossible | 30 |

### 1.2 Travel
Split a journey into **legs**. Each leg, the party makes one **group INT check** (P 5.1). Success means a smooth leg; failure brings an event (getting lost, an encounter, bad weather, exhaustion). Travel pace is in P 5.6.

### 1.3 Hazards
- **Falling:** **1d6 Physical damage per 10 ft** fallen (max 20d6). The creature lands Prone unless it takes no damage.
- **Holding breath:** **1 + STR** minutes (minimum 30 seconds). After that, the creature gains **1 Exhaustion** at the end of each of its turns until it can breathe.
- **Underwater:**
  - **Half speed**, unless the creature has a swim speed.
  - **No spells and no weapons:** only **unarmed** attacks (Grapple and Shove included). Monsters' natural attacks (bites, claws, tails) count as unarmed. **Aquatic** weapons, Aspects and spells work.
  - **No Divine or Glamour** (P 10.6): nobody can hear you. Nature Forms work.
  - **No Fire damage:** Fire damage is reduced to 0.
- **Extreme heat or cold, starvation, thirst:** a STR check (DC 10–15) each hour or day, as you see fit; on a failure, gain 1 Exhaustion.

### 1.4 Objects
Objects have one Defense and HP set by the GM (e.g. wooden door Defense 15, 18 HP; stone wall Defense 17, 50+ HP). Objects are immune to Poison and Necrotic damage and to conditions.

---

### 1.5 Trials
A trial is any problem with a clear outcome: a fight, a negotiation, a heist, a hazard, a chase. Before it starts, decide three things:
- **The goal:** what the party wants, and what stands in the way.
- **The ways through:** at least two. A fight is one of them, never the only one. Players will find the ways you didn't plan, so judge them fairly: a clever plan can replace a roll, and a roll can replace a fight.
- **The reward:** the loot from 4.1, whatever the outcome.

Use a **check** (1.1) for a short task, a **fight** (2 and 3) when someone means to stop the party by force, and a **conversation** when a character can be persuaded, bribed or fooled.

**Trial difficulty** sets the DC of the check or the target of the conversation. Use the party's average effective level (5):

| Trial | Level 1–4 | Level 5–8 | Level 9–12 |
|---|---|---|---|
| **Routine** (a lock, a bribe, a rumor) | DC 10 | DC 15 | DC 20 |
| **Tough** (a guard captain, a heist, a chase) | DC 15 | DC 20 | DC 25 |
| **Climactic** (a court, a vault, a rival Bearer) | DC 20 | DC 25 | DC 30 |

A **tough** or **climactic** trial has at least two ways through, so a failed approach leaves another open. *Provisional until the balance pass.*

### 1.6 Quests & Stories
The play loop (P 1) exists to move the party through the story. Build it from the top down:
- **Story:** what's at stake for the whole campaign arc, and who or what drives it (often a Boss, 3). A story is **3–5 quests** and ends on a climactic trial. Ending it grants every character a milestone (4.2).
- **Quest:** a goal the party takes on, with a hook and a clear end: *clear the mine*, *escort the envoy*, *find the stolen relic*. A quest is **3–5 trials** (1.5), usually one of them tough, linked by exploration and travel (1.2). Each quest should change something in the story: a clue, an ally, a rival weakened, a door opened.
- **Offer quests, don't force them.** Give the party two or three leads and let them choose. A quest they refuse or fail can return later, harder.
- **Quest rewards** are your call, on top of the trials' loot (4.1): a Party Stash upgrade, a favor, rare gear or a rare Aspect. Give one when the quest was long or the party went out of its way.

### 1.7 Rulings
- **Polymorph on a shifted Bearer** (P 10.7): the polymorph replaces the Form. When the polymorph ends, the Bearer reverts to their own body; the Form is lost.

---

## 2. Monsters

### 2.1 Foe Cards
You run each kind of monster from its **foe card**: its Core, its totals and everything it does, already added up. A foe card is **double width** (126 × 88 mm): a drawing on the left, the card on the right, its bonus strip on the right edge like any card. Identical monsters share one foe card; track each one's HP by a numbered token on the map. Keep foe cards hidden: players learn what a monster carried when it falls.

- **Italics name a real card.** An *italic* name is a card from the loot pool, exactly as a Bearer would have it: a Core, gear or an Aspect. The foe card prints its ID (*W-I-03*) so you can find its copy. **Only italic cards drop** (4.1).
- **Plain text is the monster's own:** anatomy and innate powers (a dragon's breath, an ooze's acid body, giant strength). It never drops. It may change how the monster's italic cards perform (an ogre swings a *Greatclub* harder than a Bearer); the card that drops is always the normal one.
- **Totals are final.** A foe card's totals already include everything: an unarmored foe doesn't add the empty Armor Slot's +10 Speed.
- **Same rules as Bearers.** A monster has one action, a bonus action only if a card gives it one, and a reaction. It attacks with its modifier + the weapon's to-hit bonus, and swaps gear like a Bearer. Its uses (S.R. and L.R.) come back at the start of each fight.
- **Keywords** along the bottom, type first: *Foe* (or *Foe · Boss*), then size and senses (*Foe · Large · Darkvision 60*). Challenge Rating (CR) and XP value (5) aren't printed: judge them yourself while foe difficulty is reworked.
- **Passive Awareness:** 10 + INT, **+5 for alert creatures** (guards, scouts, predators, most beasts).
- **Effect bonus:** a plain-text effect that attacks (a breath, a poison, a grapple) uses this bonus by CR:

| CR | 0–1 | 2–3 | 4–5 | 6–7 | 8–10 | 11+ |
|---|---|---|---|---|---|---|
| **Effect bonus** | +3 | +4 | +5 | +6 | +7 | +8 |

- **Recharge 5–6:** the power comes back when the monster rolls 5 or 6 on a d6 at the start of its turn.
- Monsters act on their side's initiative like everyone else. **At 0 HP**, they usually die. You may let important ones fall unconscious.

> **OGRE** · *Ogre Core* (C-II-01)
> STR +4 · DEX +0 · INT +0 · WIL +0 · Defenses STR 14 · DEX 10 · INT 10 · WIL 10 · HP 68 · Speed 35 ft
> **Giant Strength:** +33 HP; its weapons roll one extra damage die (included below).
> *Greatclub* (W-I-13): +6 to hit, 2d10 + 4 Physical. **Crushing:** on a critical hit, the target is knocked Prone.
> *Javelins* (W-I-11): +6 to hit, Thrown 30/120, 2d6 + 4 Physical.
> *Foe · Large · Darkvision 60*

> **LEGIONARY** · *Brute* Core (C-I-01)
> STR +3 · DEX +1 · INT +0 · WIL +0 · Defenses STR 18 · DEX 13 · INT 10 · WIL 10 · HP 14 · Speed 30 ft
> Throws its *Pilum*, then draws its *Gladius*.
> *Pilum* (W-II-02): +6 to hit, Thrown 30/120, 1d6 + 3 Physical. **Pierce:** on a hit, a Shield the target holds gives no bonus until it spends an action to pull the pilum free.
> *Gladius* (W-I-14): +5 to hit, 1d6 + 3 Physical. **Close Order:** +1d4 damage while an ally is engaged with the same creature.
> *Shield Wall* (Q-I-06): **Reaction (1/S.R.)**, when an attack hits an ally within 5 ft while you hold a Shield: +2 to the targeted Defense against that attack, possibly turning it into a miss.
> Also carries *Mail* (A-I-02) and *Shield* (S-I-01).
> *Foe · Medium*

### 2.2 Customizing and Building Foes
- **Add a card.** Slide any card from the loot pool **behind** a foe card, so that only its bonus strip shows on the right. Its bonuses add across, row by row, like a Bearer's stack (P 12.3). Read its effect from the card when you need it. It's italic now: it can drop.
- **Build from scratch.** Fill in a **blank foe card**: pick a Core and cards from the loot pool, add up the totals once, write the attacks, and list the italic cards with their IDs. Keep it and reuse it. For a one-off monster, just lay it out like a Bearer: a Core, its cards and a tally card.
- **Plain text sparingly.** Give a monster its own powers only for what no card could be: anatomy, a curse, a god's touch. Everything else is a card the party could win.
- **The base set** has 9 foe cards to start from (Bandit, Archer, Goblin, Wolf, Cultist, Legionary, Bandit Captain, Ogre, and the Ogre Chieftain Boss) and 4 blank ones.
- **How strong a foe is** (how many cards, which Ranks) is still judged by its CR and your call (5).

## 3. Bosses
- A **Boss** has the **Boss** tag on its foe card. It takes a **half turn** once per round, during the characters' side: **its movement or one action**, between any two characters' turns, whenever you choose.
- On its half turn, it can use any power it could use on its turn; only the power's own uses and Recharge limit it.
- **Its Core and signature powers are plain text:** they never drop. Its gear and Aspects are italic, so give it cards you're willing to hand over: usually **at most one Rank above** the party's best gear and Aspects.
- Some Bosses grant an **extra Gear Slot** (P 3.3) when defeated.

---

## 4. Loot & Rewards

### 4.1 Drops
- **Each trial the party overcomes rewards 1–3 pieces of loot per character** (gear, Aspects or Cores). In a fight, they come from the **italic cards** on the defeated monsters' foe cards (2.1), your choice or random: six legionaries don't mean six pila. Other trials give them as their outcome: a payment, a gift, a favor, a hidden stash. Bosses add their best gear and Aspects and may grant an extra Gear Slot. A monster's Aspects and Core linger for 1 minute after it falls (P 3.8): the party keeps only what it has empty Shards and actions for.
- **A drop is the very card** named on the foe card: pull a copy from the loot pool by its ID and hand it over. The foe card stays with you, ready for the next fight. Make about **half** of the cards you give monsters **Core-free** (no roll, no modifier), so any character might want them.
- **Spread strong Cores across the party.** HP comes only from the Core, so one player with a much better Core than the others unbalances encounters.
- **Most drops are ordinary:** a goblin's Core, a bandit's crossbow, a guard's mail. They're rarely worth equipping, but they fill the Party Stash with options for future builds.
- **Rank V** gear and Aspects drop only from Bosses, and rarely.
- **Share Aspects between styles.** At every Rank, give fighting Techniques, Traits for casters, and Divine, Glamour and Nature Aspects (or Traits and Focus gear that boost them) about equal shares. Every build then grows at the same pace from its Aspect Slots.
- **A budget per trial, not per corpse.** Give the same 1–3 pieces of loot per character however the party gets through: a fight leaves gear on the bodies and Aspects lingering over them; a deal brings a payment, a gift (6.3) or a favor (*Writ of Favor*, *Guild Signet*, P 3.4); stealth or trickery reaches the treasure the monsters guarded. Players then never lose loot for avoiding a fight.

### 4.2 Rewards
- **Starter list** (P 13.2): offer Rank I gear and Aspects for every style, including a Litany (Divine), a Repertoire (Glamour), a Remembrance (Nature) and a Focus. The base set's list:

| Slot | Starter gear and Aspects (Rank I) |
|---|---|
| **Armor** | *Leather*, *Mail* |
| **Hands** | *Shield*, *Dagger*, *Shortsword*, *Handaxe*, *Finesse Blade*, *Longsword*, *Battleaxe*, *Greatsword*, *Glaive*, *Longbow*, *Sling*, *Javelins*, *Spellguard Staff*, *Traveler's Lute* |
| **Jewelry** | *Ring of Warding*, *Guild Signet*, *Shard Bandolier*, *Holy Amulet*, *Boots of the Long Stride* |
| **Items** | *Conjurer's Book*, *Potion of Healing*, *Coin Pouch*, *Writ of Favor* |
| **Aspects** | *Springheel*, *Stone Blood*, *Iron Will*, *Clear Mind*, *Cleave*, *Steady Aim*, *Shield Bash*, *Battle Hymn*, *Rallying Cry*, *Cat Burglar*, *Renowned*, *Sailor*, *Street Urchin*, *Hunter*, *Physician*, *Barkeep*, *Smith*, *Mountaineer*, *Wanderer's Repertoire*, *Acolyte's Litany*, *Wildheart's Remembrance* |

- **Extra Gear Slots** are Boss rewards only. Never more than one of each per character. At the table, hand the player its Slot frame (P 12.2).
- **Empty Shards** count as one piece of the loot budget when they drop. Give one when the party keeps losing Aspects it wanted. A *Shard Bandolier* (P 3.8) is a good early Jewelry reward.
- **Party Stash upgrades** (Pack Mule, Cart, Wagon) are quest rewards (1.6) or Boss rewards. Give the next one when the party starts leaving good loot behind.
- **Milestones** (P 4.1): grant one to everyone at the **end of each story** (1.6), and hand each player a new Aspect frame (P 12.2). A full campaign is about **five stories** (3 → 8 Aspects). Everyone advances together. *Provisional until the balance pass.*

### 4.3 Building Traits and Knacks
Use this to size the Traits and Knacks you hand out as loot.

Traits and Knacks are built from four sources:
- **Bonus:** +1 to an ability modifier (and to its Defense, P 2.3). Costs **1**.
- **Perk:** a small edge for one kind of build (table below). Costs **1**.
- **Strong perk:** a bigger edge. Costs **2**.
- **Activity:** a bonus on checks for one narrow activity (*sneak*, *climb*, *persuade*). Costs **¼**. **At most 4 per Aspect.**

**An Aspect's Rank is its budget:** Rank I spends 1, Rank II 2, up to Rank V 5. The ability maximum (+5) still applies.
- **A bonus is never alone:** it comes with a second bonus, a perk or activities. There is no "+1 STR" Aspect.
- **Mix the builds:** an Aspect's activities come from **at least two abilities**.
- **Rank I has no bonus or perk:** up to 4 activities (a Knack), or one narrow edge of the same weight (*Iron Will*, *Springheel*). Bonuses and perks start at Rank II.

| Rank (budget) | I (1) | II (2) | III (3) | IV (4) | V (5) |
|---|---|---|---|---|---|
| **STR perk:** HP maximum | +3 | +5 | +8 | +12 | +15 |
| **DEX perk:** Speed | +5 ft | +5 ft | +10 ft | +10 ft | +15 ft |
| **INT perk:** spell points | +1 | +1 | +2 | +2 | +3 |
| **WIL perk:** extra Resolve (P 10.6) | +1 | +1 | +2 | +2 | +3 |
| **Activity bonus** | +2 | +3 | +4 | +5 | +6 |

Perk spell points can be spent on any equipped Spellbook, and perk Resolve on any of your Divine, Glamour or Nature powers (P 10.2, 10.6).

**Strong perks:**
- **Doubled perk:** twice a perk from the table.
- **A sense or a movement:** Darkvision 60 ft, a climb or swim speed (P 11.5).
- **A resistance:** Resist one damage type other than Physical.
- **A small power:** a bonus action or reaction, 1/S.R. (*Second Wind*, Rank II).
- **Levitation:** **bonus action (1/S.R.):** for 1 minute you float, rising or sinking up to 20 ft per turn.
- **A cantrip:** cast one cantrip at will, as from a Spellbook with this Trait's Spell attack bonus (an empty Hand needed).

**Activities by ability:**

| d6 | STR | DEX | INT | WIL |
|---|---|---|---|---|
| 1 | Climb | Sneak | Notice | Persuade |
| 2 | Swim | Hide | Search | Deceive |
| 3 | Jump | Balance | Read intentions | Perform |
| 4 | Lift | Tumble | Recall lore | Intimidate |
| 5 | Break | Pick locks | Track or navigate | Haggle |
| 6 | Endure (pain, cold, a march) | Pick pockets | Treat wounds | Gather rumors or handle animals |

**Three families** (a Trait keeps its name at every Rank):

| Rank | II | III | IV | V |
|---|---|---|---|---|
| **Cross Trait** (lead + second's perk) | +1 & perk | +1/+1 & perk | +2/+1 & perk | +2/+2 & perk |
| **Dual Trait** (two bonuses) | +1/+1 | +2/+1 | +2/+2 | +3/+2 |
| **Gifted Trait** (lead + strong perk) | strong perk | +1 & strong perk | +1/+1 & strong perk | +2/+1 & strong perk |

**Cross Traits** (lead · second, the perk's build): *Wiry* STR · DEX · *Battle Scholar* STR · INT · *Commanding Frame* STR · WIL · *Climber's Grip* DEX · STR · *Keen Eye* DEX · INT · *Showman* DEX · WIL · *Tomb Delver* INT · STR · *Arcane Fingers* INT · DEX · *Learned Voice* INT · WIL · *Crusader's Faith* WIL · STR · *Court Dancer* WIL · DEX · *Oracle's Sight* WIL · INT.

**Dual Traits:** *Brawler's Footwork* STR · DEX · *Siege Engineer* STR · INT · *Warlord's Bearing* STR · WIL · *Duelist's Reading* DEX · INT · *Swashbuckler* DEX · WIL · *Silver Tongue* INT · WIL.

**Gifted Traits** (lead, strong perk): *Night Eyes* INT, Darkvision 60 ft · *Feather Step* DEX, Levitation · *Salamander Blood* STR, Resist Fire · *Spark of Talent* INT, a cantrip · *Second Wind* STR, a small power.

*Examples: Wiry (II): +1 STR, +5 ft Speed. Whipcord (III): +1 STR, +1 DEX, +10 ft Speed. Siege Engineer (IV): +2 STR, +2 INT. Night Eyes (III): +1 INT, Darkvision 60 ft.*

### 4.4 Concept Traits and Knacks
Named Traits and Knacks with a clear idea, ready to drop. Activities get the bonus of their Rank (table above).

| Rank I (Knack, +2) | Activities |
|---|---|
| *Cat Burglar* | Sneak, climb, pick locks |
| *Sailor* | Swim, climb, navigate, gather rumors |
| *Street Urchin* | Pick pockets, sneak, read intentions, gather rumors |
| *Hunter* | Track, notice, sneak, handle animals |
| *Physician* | Treat wounds, recall lore, read intentions, persuade |
| *Barkeep* | Read intentions, gather rumors, intimidate, lift |
| *Smith* | Lift, break, haggle, recall lore |
| *Mountaineer* | Climb, endure, navigate, balance |

| Rank II (+3) | Bonus & perk | Activities |
|---|---|---|
| *Sellsword* | +1 STR | Intimidate, endure, haggle, gather rumors |
| *Acrobat* | +1 DEX | Tumble, balance, jump, perform |
| *Diplomat* | +1 WIL | Persuade, deceive, read intentions, recall lore |
| *Hedge Witch* | +1 spell point | Handle animals, recall lore, treat wounds, deceive |
| *Ranger* | +5 ft Speed | Track, notice, navigate, sneak |
| *Bouncer* | +5 HP | Lift, intimidate, read intentions, endure |

| Rank III (+4) | Bonuses & perks | Activities |
|---|---|---|
| *Guild Thief* | +1 DEX, +1 INT | Sneak, pick locks, pick pockets, notice |
| *War Priest* | +1 WIL, +8 HP | Intimidate, persuade, treat wounds, endure |
| *Beastmaster* | +1 WIL, +10 ft Speed | Handle animals, track, notice, swim |
| *Deep Diver* | Swim speed (strong) | Endure, notice, recall lore, navigate |
| *Spy* | +1 WIL, +1 DEX | Deceive, sneak, read intentions, pick locks |

| Rank IV (+5) | Bonuses & perks | Activities |
|---|---|---|
| *Shadow Dancer* | +1 DEX, Levitation (strong) | Sneak, tumble, balance, deceive |
| *Sage of the Old Roads* | +1 INT, +1 WIL, +2 spell points | Recall lore, navigate, persuade, read intentions |
| *Ironhide* | +1 STR, Resist Poison (strong) | Endure, lift, break, intimidate |

| Rank V (+6) | Bonuses & perks | Activities |
|---|---|---|
| *Legend of the Arena* | +2 STR, +1 WIL, +15 HP | Intimidate, perform, lift, endure |
| *Thousand Faces* | +1 WIL, +1 DEX; small power (strong): **bonus action (1/S.R.):** take the look of a humanoid you have seen, for 1 hour | Deceive, perform, read intentions, pick pockets |

### 4.5 Random Traits and Knacks
To make a new Trait or Knack at any Rank:
1. **Pair** (d6): 1 STR · DEX · 2 STR · INT · 3 STR · WIL · 4 DEX · INT · 5 DEX · WIL · 6 INT · WIL. Roll again: on 1–3 the first ability **leads**, on 4–6 the second.
2. **Shape** (d6, by Rank). Bonuses go to the lead first. A perk is the **second** ability's perk.

| d6 | Rank I (1) | Rank II (2) | Rank III (3) | Rank IV (4) | Rank V (5) |
|---|---|---|---|---|---|
| 1–3 | 4 activities | +1/+1 | +2/+1 | +2/+2 | +3/+2 |
| 4 | 4 activities | +1 & perk | +1/+1 & perk | +2/+1 & perk | +2/+2 & perk |
| 5 | 3 activities | +1 & 4 activities | +1 & strong perk | +1/+1 & strong perk | +2/+1 & strong perk |
| 6 | 3 activities | strong perk | +1 & perk & 4 activities | +1/+1 & perk & 4 activities | +1/+1 & strong perk & 4 activities |

3. **Activities:** half from each ability of the pair (d6 table above).
4. **Strong perk** (d6): 1 doubled perk (the second's) · 2 a sense or movement (Darkvision 60 ft, climb or swim speed) · 3 a resistance (d6: Fire, Cold, Lightning, Poison, Necrotic, Radiant) · 4 a small power you invent · 5 Levitation · 6 a cantrip.
5. **Name it** after the idea the result suggests, and give it its type: **Knack** if it has only activities, otherwise **Trait**.

*Example: Rank III. Pair 4 (DEX · INT), INT leads. Shape 6: +1 INT, DEX's perk (+10 ft Speed) and 4 activities: notice, recall lore, balance, pick locks. Name: Tinker-Thief.*

---

## 5. Building Encounters
*This section sizes fights. Non-combat trials use the difficulty table in 1.5 and rewards from 4.1.*

**Effective level** (1–12) is a GM yardstick for encounters, not a character stat: estimate it from the character's Core, gear, Aspects and Slots. A new character is level 1; a character with a Rank IV Core, Rank IV gear, 8 Rank IV Aspects and all three extra Gear Slots is level 12. Use the party's average.

**XP budget per character:**

| Level | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Low** | 50 | 100 | 150 | 250 | 500 | 600 | 750 | 1,000 | 1,300 | 1,600 | 1,900 | 2,200 |
| **Moderate** | 75 | 150 | 225 | 375 | 750 | 1,000 | 1,300 | 1,700 | 2,000 | 2,300 | 2,900 | 3,700 |
| **High** | 100 | 200 | 400 | 500 | 1,100 | 1,400 | 1,700 | 2,100 | 2,600 | 3,100 | 4,100 | 4,700 |

Multiply by the number of characters, then spend the budget on monsters' XP values.
- **Low:** one or two scary moments, no casualties. **Moderate:** could go badly. **High:** potentially lethal.
- More than two monsters per character? Make most of them fragile.
- A monster with a CR above the party's level can drop a character in one hit.
- *Values are provisional until the balance pass.*

---

## 6. Bearers in the World
The Player Rules fix only the basics (P 1): Bearers absorb Cores and Aspects, gear is gear, and a Bearer's look and personality never change (a Form changes the shape only for a while). Everything below is a suggestion: take what fits your world.

### 6.1 Shards in the World
Aspects have no body of their own; Shards do. Decide how both fit your world before play: it changes what NPCs know, what can be stolen and what the Shard trade looks like. Two suggestions:

| | **Only Bearers** see Aspects and touch Shards | **Everyone** sees lingering Aspects and can handle Shards |
|---|---|---|
| **To others** | A Shard is a dull, heavy stone. A Bearer kneeling over a corpse looks strange. | A lingering Aspect is a glow over the body; a full Shard shines: a curiosity worth money. |
| **Theft** | Only another Bearer can steal from the Pack or the Party Stash. | Anyone can: thieves, bandits, a greedy innkeeper. |
| **Trade** | A secret market between Bearers. | An open market: merchants, collectors, guilds, laws. |
| **Society** | Bearers can hide the gift easily; non-Bearers may doubt Shards exist. | The gift is hard to hide, and people know what Bearers hunt. |

You can mix them: everyone can see Shards, but only Bearers can touch them, or the reverse.

### 6.2 Bearers in Society
Bearers are rare, and people don't agree on what they are. Give each region one or two stances, so travel changes how NPCs react:
- **Hunted:** a church calls them abominations that steal souls. Bearers hide, and the gift is a secret worth blackmail.
- **Hired:** a crown, a guild or a mercenary company pays them to clear monsters, and licenses them like any dangerous trade.
- **Revered:** villages see them as chosen protectors, and expect them to act like it.
- **Feared:** common folk avoid them, inns turn them away, prices go up.

Other hooks:
- **A mark.** A sign betrays the gift: eyes that glow while a Shard settles, a scar that warms near Shards. Towns then become a choice between hiding it and showing it.
- **The Shard trade.** Unused Shards are worth money, to other Bearers or to everyone (6.1). Markets, smugglers and thieves follow, and the Party Stash becomes worth stealing.
- **Rival Bearers.** Recurring enemies with the same gift, hunting the same Shards. Rank V Aspects become a race between Bearers.

### 6.3 Bearers at the Table
- **Origin.** Ask each player whether their character sees the gift as a blessing or a curse, and how it came: at birth, through a ritual, a pact, or by surviving a catastrophe. Use the answers as story hooks.
- **Echoes.** An Aspect keeps a trace of its old owner: a memory, a voice, a reflex. Faint at Rank I, loud at Rank V, where it may want things. The character's personality doesn't change: they hear the echo and react as themselves. Describe an echo when a new Core or Aspect settles.
- **Gifts.** A living, willing being can pour one of its Aspects into a Bearer's empty Shard: a master teaches a technique, a noble grants a favor, a fey seals a pact. A gift needs no capture action and doesn't fade. Use gifts to reward encounters solved by talk, stealth or trickery (4.1).
- **A monster's own powers** (plain text on its foe card, 2.1) are part of its body or its nature, not Aspects: they don't linger when it falls, so no Shard can catch them.

---

## 7. Glossary
<!-- glossary:start -->

Each game term has one meaning, in both books.

| Term | Meaning |
|---|---|
| **Ability** | One of four measures every creature has: Strength (STR), Dexterity (DEX), Intelligence (INT) and Will (WIL), each written as a modifier. |
| **Absorb** | Moving a Shard's Aspect into an Aspect Slot, or its Core into your body, during a long rest. |
| **Action** | Using it takes your action. |
| **Anthem** | A Divine or Glamour power. Bonus action: a buff for allies who hear you, for a Duration. |
| **Aquatic** | A weapon keyword: works underwater, where other weapons and spells don't. |
| **Area** | Cone, Cube, Cylinder, Emanation, Line or Sphere N: an area of that shape and size. Roll once against every creature in it. Half damage on a miss. |
| **Armor** | The type of gear worn on the body; it fits the Armor Slot. Takes 10 minutes to don or doff. Never in the Pack. |
| **Aspect** | A Trait, Technique, Knack, Divine, Glamour or Nature absorbed from another being. It has no body: outside a Bearer it lives in a Shard. Only Bearers can use it. |
| **Aspect Slot** | A Slot that holds one Aspect. You start with 3 and can reach 8. |
| **Attack roll** | A roll of d20 + modifiers against a Defense, made by whoever harms or hinders: weapons, spells, Divine, Glamour and Nature powers, traps, poisons. |
| **Bearer** | A humanoid who can absorb the Aspects and the Core of other beings. Every player character is one. |
| **Blindsight N** | Perceive everything within N ft without sight. |
| **Bonus action** | Using it takes your bonus action. |
| **Boss** | A strong monster with special abilities, including a half turn during the characters' side. |
| **Cantrip** | A spell that costs nothing. Cast at will. |
| **Capture** | Pouring a lingering Aspect or Core into an empty Shard. |
| **Card** | The physical component for a Core, a piece of gear, an Aspect, a spell or an amount of gold. |
| **Card ID** | The code in a card's bottom-left corner: type letter, Rank and number (W-II-02). |
| **Challenge Rating (CR)** | A monster's danger, used with its XP value to size fights. |
| **Check** | A roll of d20 + ability modifier + bonuses against a Difficulty Class (DC). |
| **Climb N** | A climb speed: climbing costs no extra movement. |
| **Consumable** | An item gone once used. Up to 3 identical Consumables share one Item Slot. |
| **Core** | Your body: four ability modifiers, HP maximum, Speed and Size. You always have exactly one. It is neither an Aspect nor gear. |
| **Cue** | A Divine or Glamour power. Reaction: changes a roll after it's made, before its result. |
| **Darkvision N** | Treat Dark as Bright within N ft. |
| **Defense** | The number an attack must reach: 10 + an ability modifier + bonuses. Every creature has a STR, DEX, INT and WIL Defense. |
| **Dirge** | A Divine or Glamour power. Action: an attack against WIL Defense. |
| **Divine** | An Aspect type: WIL magic of prayer. Its deck, a **Litany**, holds a fixed list of powers that alter fate and heal, and a pool of Resolve. |
| **Drop** | Gear, an Aspect or a Core that a trial yields as loot; to drop is to yield it. |
| **Duration** | A set length of time an effect lasts, printed on it. |
| **Effective level** | The GM's estimate of a character's power, from 1 to 12, used to size fights and trial DCs. Not a character stat. |
| **Equipment** | Gear you wear or wield: armor, weapons, shields, Instruments and Jewelry. |
| **Extra Gear Slot** | A permanent extra Hand, Jewelry or Item Slot, granted only by defeating a Boss: Third Hand, Second Jewel or Great Backpack. |
| **Finesse** | A weapon keyword: use STR or DEX for attack and damage. |
| **Fly N** | A fly speed: you move through the air. If you're knocked Prone or Incapacitated while flying, you fall. |
| **Focus** | A keyword on equipment that strengthens your Divine, Glamour or Nature Aspects: an Instrument, a holy amulet, a druid's staff. |
| **Foe card** | The GM's card for one kind of monster: its Core, totals and powers. Cards named in italics on it can drop; plain text never does. |
| **Form** | One beast body in a Remembrance (Nature), printed like a Core: STR, DEX, HP, Speed and Size. While you are shifted into it, it replaces your body; your mind and Aspects stay. |
| **Game Master (GM)** | The player who describes the world, runs monsters and adjudicates rules. |
| **Gear** | Every real object a Bearer can equip or store: equipment and items. Anyone can use gear. |
| **Gear Slot** | An Armor, Hand, Jewelry or Item Slot. |
| **Glamour** | An Aspect type: WIL magic of performance and command. Its deck, a **Repertoire**, holds a fixed list of powers that lift allies and break enemies, and a pool of Resolve. |
| **Heavy** | A weapon keyword: needs STR +1 (melee) or DEX +1 (ranged), or −3 on attacks. |
| **Instrument** | Equipment held in a Hand that is neither a weapon nor a shield: a lute, a drum, a horn. |
| **Item** | Gear you carry and use: Spellbooks, Recipes, Consumables, Purses and Shards. |
| **Jewelry** | The type of worn gear that fits the Jewelry Slot: rings, amulets, circlets, cloaks, gloves, boots. |
| **Keyword** | A word with one fixed meaning that gear and Aspects list, type first. |
| **Knack** | An Aspect type: a bonus on checks for one narrow activity. |
| **Lasting effect** | An effect on a creature that ends when the creature breaks free, not after a set time. |
| **Leather, Mail, Plate** | The three armors, from lightest to heaviest. |
| **Light** | A weapon keyword: allows two-weapon fighting. |
| **Lingering** | The state of a defeated creature's Aspects and Core for 1 minute, before they fade for good. |
| **Loading** | A weapon keyword: one shot per action, bonus action or reaction, even with extra attacks. |
| **Maintain roll** | The source's roll, at the start of each of the target's turns, to keep a lasting effect going. |
| **Mend** | A Divine or Nature power that restores HP to a creature in range, even one who can't hear you. |
| **Milestone** | One new Aspect Slot for every character, granted when the party completes a story. |
| **Nature** | An Aspect type: WIL magic of the wild. Its deck, a **Remembrance**, holds a fixed list of Forms and healing powers, and a pool of Resolve. |
| **Noisy N** | −N on checks to sneak. |
| **Object** | A small non-magical thing that isn't gear: a key, a letter, treasure, rope, a torch. Carried freely, with no limit. |
| **Pack** | Your personal bag: up to 8 pieces of gear you carry but haven't equipped, at most 3 of them Shards. |
| **Party** | The group of Bearers played together. |
| **Party Stash** | The group's mule, cart or wagon: gear the party owns but nobody carries. |
| **Piece** | One unit of gear, as the Pack, the Party Stash and loot count it. A stack of up to 3 identical Consumables is one piece. |
| **Play loop** | The repeating cycle of play: face a trial, gather the loot, rest and rebuild when needed. |
| **Purse** | An item that holds your gold, up to a maximum set by its Rank. |
| **Quest** | A goal the party takes on, a few trials long. |
| **Range N/M** | A ranged attack. Beyond N: disadvantage. Beyond M: impossible. A single number is a spell's maximum range. |
| **Rank** | The fixed power of a piece of gear, an Aspect or a Core, from I to V. Characters have none. |
| **Reach** | A weapon keyword: your reach is 10 ft instead of 5 ft. |
| **Reaction** | Using it takes your reaction, when the trigger in its text happens. |
| **Recharge 5–6** | A monster power that comes back on a 5 or 6 on a d6 at the start of the monster's turn. |
| **Recipe** | An item: a stack that refills at each long rest. Unused items vanish when it refills. |
| **Release** | Emptying a Shard. Its Aspect or Core is gone for good. |
| **Requirement** | A minimum ability modifier needed to equip gear or an Aspect (*Req STR +2*). |
| **Reroll** | The roll is made again (all its d20s) and the new result counts. A roll can be rerolled only once. |
| **Resist (type)** | Take half damage of that type. |
| **Resolve** | The points a Divine, Glamour or Nature Aspect spends on its powers. Each has its own pool; extra Resolve from Traits can be spent on any of them. It returns on a short rest. |
| **Shard** | A bulky crystal vessel that holds one Aspect or Core, or nothing. An item, but never in a Slot. |
| **Shield** | The type of held gear that raises your Defenses; it fits a Hand Slot. |
| **Shift** | To take on a Form from your Remembrance; to revert is to return to your own body. Being polymorphed is never shifting. |
| **Size** | Tiny, Small, Medium or Large, printed on a Core or a Form. |
| **Slot** | A space that holds one piece of gear or one Aspect of the matching type: Armor, Hand, Jewelry, Item or Aspect. |
| **Slot frame** | The table component for one Slot: a holder with two corner slits that a card tucks into. A framed card is equipped. A Shard is a Shard frame. |
| **Spell** | One card of a Spellbook, never on its own. Its level is its cost in spell points. |
| **Spell level** | A spell's power and its cost in spell points, from 1st to 6th. |
| **Spellbook** | An item holding a fixed list of spells and a pool of spell points. All spellcasting uses INT. |
| **Story** | The campaign's big arc, made of quests. Completing one grants a milestone. |
| **Subdue** | The keyword of a lasting effect that takes a creature out of the fight. The effect names its state (Stunned, Charmed, banished…); Subdue adds first bite and weakening. |
| **Subtle** | Nobody notices you casting it. |
| **Swim N** | A swim speed: swimming costs no extra movement, and full speed underwater. |
| **Tally card** | The one card you write on: your ten totals, current and temporary HP, and death saves. |
| **Targets X** | The attack is against the target's X Defense (STR, DEX, INT or WIL). |
| **Technique** | An Aspect type: something a being trained (a fighting move). |
| **Thrown N/M** | A weapon keyword: it can be thrown as a ranged attack, using the modifier of its melee use. Beyond N ft: disadvantage. Beyond M ft: impossible (*Thrown 20/60*). |
| **Totals** | Your ten running numbers: four ability modifiers, four Defenses, HP maximum and Speed. |
| **Trait** | An Aspect type: something a being is (a body, a blood, a blessing). |
| **Trial** | One problem with a clear outcome: a fight, a negotiation, a heist, a hazard, a chase. Each one pays out loot, however it ends. |
| **Truesight N** | As Darkvision, and see invisible creatures and through illusions and shapechanges. |
| **Two-Handed** | Takes two Hand Slots. |
| **Type** | The first keyword of gear or an Aspect. It names the Slot it fits. |
| **Use** | The action that uses an object, or gear that takes an action. |
| **Uses** | A limited number of activations of one power, written on it (*2/S.R.*, *1/L.R.*), that come back on a short or long rest. |
| **Versatile** | A weapon keyword: uses the bigger damage die when held in two hands. |
| **Vulnerable (type)** | Take double damage of that type. |
| **Weapon** | The type of held gear you attack with; it fits a Hand Slot. It prints its to-hit bonus and damage (*+2 to hit, 1d8 + STR Physical*). |

<!-- glossary:end -->

---

## Attribution
This work includes material from the System Reference Document 5.2.1 ("SRD 5.2.1") by Wizards of the Coast LLC, available at https://www.dndbeyond.com/srd. The SRD 5.2.1 is licensed under the Creative Commons Attribution 4.0 International License, available at https://creativecommons.org/licenses/by/4.0/legalcode.
