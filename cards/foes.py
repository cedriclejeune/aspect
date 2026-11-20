"""Foe cards (GM 2.1): one card per kind of monster, built from base-set cards.

Built into rules/Bearers-Base-Set.pdf by tools/build_cards.py, which adds up the totals and the attacks.
Foe cards are double width (126 × 88 mm): a drawing on the left, the card on the right.
body=(STR, DEX, INT, WIL, HP, Speed, size) is the monster's own plain-text body: it never drops. Its HP leaves out the HP
its Armor and Traits print (the build adds those). carries names base-set cards (they print in italics and can drop).
own is the monster's plain text: it never drops.
bonus adds plain-text numbers to the strip; extra_dice adds damage dice to every weapon (an int) or to the named weapons
({weapon card name: n}). recharge={card name: 5} turns a carried card's limited uses into Recharge 5–6 for this foe.
powers picks which powers of a carried deck the foe uses (the whole deck drops).
alert and own_fx are the sim's mechanics for own: alert = Keen Nose, own_fx = Powers (SPEC 2.1) for plain-text attacks and powers.
leader=True marks a foe that leads its group (keyword Leader, Morale GM 2.4).
The keywords at the bottom are built from the type (Foe, Boss), Leader, the size and senses.
"""


def foe(name, carries, body, own=(), bonus=None, extra_dice=0, recharge=None, powers=(), senses="", boss=False,
        leader=False, alert=False, own_fx=()):
    return dict(name=name, body=body, carries=list(carries), own=list(own), bonus=bonus or {},
                extra_dice=extra_dice, recharge=recharge or {}, powers=list(powers), senses=senses, boss=boss, leader=leader, alert=alert,
                own_fx=list(own_fx))


UNDEAD = "**Undead:** resists Poison and Necrotic, vulnerable to Radiant. Never checks Morale."
UNDEAD_FX = dict(name="Undead", use="passive", resist=["Poison", "Necrotic"], vuln=["Radiant"], fearless=True)
CONSTRUCT = "**Construct:** resists Poison and Necrotic. Never checks Morale."
CONSTRUCT_FX = dict(name="Construct", use="passive", resist=["Poison", "Necrotic"], fearless=True)
FLYER = "**Flyer:** flies at its full Speed."

FOES = [
    foe("Bandit", ["Handaxe", "Pocket Sand", "Leather"], body=(2, 1, 1, 0, 10, 30, "Medium")),
    foe("Bandit Archer", ["Longbow", "Dagger", "Steady Aim", "Leather"], body=(0, 3, 1, 0, 9, 35, "Medium")),
    foe("Goblin", ["Sling", "Dagger", "Leather"], body=(-1, 2, 0, -1, 5, 30, "Small"),
        senses="Darkvision 60",
        own=["**Nimble (2/S.R.):** reaction. Move up to half its Speed without provoking opportunity attacks."],
        own_fx=[dict(name="Nimble", use="reaction", uses="2/SR", target="self", do=[dict(move="safe", ft="half")])]),
    foe("Wolf", ["Wolfpack"], body=(1, 2, -1, -2, 7, 40, "Medium"),
        own=["**Bite:** +4 to hit, 1d6 + 2 Physical.", "**Keen Nose:** alert (passive Awareness +5)."],
        alert=True, own_fx=[dict(name="Bite", use="action", reach=5, target="enemy", atk=dict(flat=4, vs="weapon"),
                                 do=[dict(dmg="1d6+2", type="Physical")])]),
    foe("Cultist", ["Dagger", "Acolyte's Litany", "Iron Will"], body=(0, 1, 0, 3, 8, 30, "Medium"), powers=["Bane", "Twist Fate", "Healing Word"]),
    foe("Legionary", ["Pilum", "Gladius", "Shield Wall", "Mail", "Shield"], body=(3, 1, 0, 0, 10, 30, "Medium"),
        own=["Throws its *Pilum*, then draws its *Gladius*."]),
    foe("Bandit Captain", ["Finesse Blade", "Dagger", "Twin Strike", "Leather", "Coin Pouch"], body=(2, 3, 0, 1, 28, 30, "Medium"),
        leader=True),
    foe("Ogre", ["Greatclub", "Javelins", "Sweeping Blow"], body=(4, 0, 0, 0, 35, 35, "Large"),
        own=["**Giant Strength:** +60 HP. Its *Javelins* roll one extra damage die (included). "
             "Its *Sweeping Blow* recharges on a 5–6 instead of 1/S.R."],
        bonus={"HP": 60}, extra_dice={"Javelins": 1}, recharge={"Sweeping Blow": 5}, senses="Darkvision 60"),
    foe("Ogre Chieftain", ["Greatclub", "Cleave", "Second Wind", "Sweeping Blow", "Plate"], body=(5, 0, 0, 1, 54, 40, "Large"),
        own=["**Warlord:** its *Sweeping Blow* recharges on a 5–6 instead of 1/S.R.",
             "**Bellow (Recharge 5–6):** reaction. Attack (+5) against the WIL Defense of each enemy within 30 ft: "
             "Frightened of the chieftain until the end of its next turn."],
        recharge={"Sweeping Blow": 5}, senses="Darkvision 60", boss=True, leader=True,
        own_fx=[dict(name="Bellow", use="reaction", recharge=5, target="enemies", reach=30, atk=dict(flat=5, vs="WIL"),
                     do=[dict(cond="Frightened", until="endSourceTurn")], tags=["fear"])]),
    # basic humanoids: a Rank I Rune each
    foe("Guard", ["Longsword", "Shield", "Javelins", "Mail", "Grit"], body=(1, 1, 1, 1, 6, 30, "Medium")),
    foe("Scout", ["Longbow", "Shortsword", "Hunt", "Leather", "Dusk Eyes"], body=(0, 2, 1, 0, 6, 35, "Medium"), senses="Darkvision 60", alert=True,
        own=["**Keen Eyes:** alert (passive Awareness +5)."]),
    foe("Mage", ["Conjurer's Book", "Dagger", "Clear Mind"], body=(0, 1, 3, 0, 7, 30, "Medium"), powers=["Fire Bolt", "Magic Missile", "Shield"]),
    foe("Orc", ["Greataxe", "Javelins", "Defiance", "Leather", "Campaign"], body=(3, 0, 0, 0, 8, 30, "Medium"), senses="Darkvision 60"),
    foe("Hobgoblin", ["Longsword", "Shield", "Longbow", "Mail", "Battle Hymn", "Discipline"], body=(1, 1, 1, 0, 8, 30, "Medium"), senses="Darkvision 60"),
    # classic monsters
    foe("Skeleton", ["Shortsword", "Shortbow", "Leather"], body=(0, 2, -2, -2, 8, 30, "Medium"), senses="Darkvision 60",
        own=[UNDEAD], own_fx=[UNDEAD_FX]),
    foe("Zombie", ["Defiance"], body=(1, -2, -4, -2, 16, 20, "Medium"), senses="Darkvision 60",
        own=[UNDEAD, "**Slam:** +3 to hit, 1d8 + 1 Physical."],
        own_fx=[UNDEAD_FX, dict(name="Slam", use="action", reach=5, target="enemy", atk=dict(flat=3, vs="weapon"),
                                do=[dict(dmg="1d8+1", type="Physical")])]),
    foe("Kobold", ["Dagger", "Sling", "Wolfpack"], body=(-2, 2, -1, -1, 1, 30, "Small"), senses="Darkvision 60"),
    foe("Giant Rat", ["Wolfpack"], body=(-2, 2, -4, -2, 1, 30, "Small"), senses="Darkvision 60", alert=True,
        own=["**Bite:** +4 to hit, 1d4 + 2 Physical.", "**Keen Nose:** alert (passive Awareness +5)."],
        own_fx=[dict(name="Bite", use="action", reach=5, target="enemy", atk=dict(flat=4, vs="weapon"),
                     do=[dict(dmg="1d4+2", type="Physical")])]),
    foe("Giant Spider", ["Larceny"], body=(2, 3, -4, -2, 26, 30, "Large"), senses="Darkvision 60", alert=True,
        own=["**Spider Climb:** climbs walls and ceilings at full Speed. **Web Sense:** alert (passive Awareness +5).",
             "**Bite:** +5 to hit, 1d8 + 3 Physical plus 1d8 Poison.",
             "**Web (Recharge 5–6):** action, range 30 ft. Attack (+3) against DEX Defense: **Restrained** for 2 turns."],
        own_fx=[dict(name="Bite", use="action", reach=5, target="enemy", atk=dict(flat=5, vs="weapon"),
                     do=[dict(dmg="1d8+3", type="Physical"), dict(dmg="1d8", type="Poison")]),
                dict(name="Web", use="action", recharge=5, reach=30, target="enemy", atk=dict(flat=3, vs="DEX"),
                     do=[dict(cond="Restrained", until="targetTurns2")])]),
    foe("Troll", ["Night Eyes", "Stone Blood"], body=(4, 1, -1, -2, 74, 30, "Large"), senses="Darkvision 120", alert=True,
        own=["**Claws:** +6 to hit, 2d6 + 4 Physical.",
             "**Regeneration:** regains 10 HP at the start of its turn, unless it took Fire or Poison damage since its last turn.",
             "**Keen Nose:** alert (passive Awareness +5).", "**Thick Hide:** +1 STR Defense (included)."],
        bonus={"STRd": 1},
        own_fx=[dict(name="Claws", use="action", reach=5, target="enemy", atk=dict(flat=6, vs="weapon"),
                     do=[dict(dmg="2d6+4", type="Physical")]),
                dict(name="Regeneration", use="passive", regen=10, stopBy=["Fire", "Poison"])]),
    # classic monsters for new parties (SRD 5.2.1, CR 1/8 to 3)
    foe("Stirge", ["Dusk Eyes"], body=(-3, 3, -1, -2, 3, 40, "Tiny"), senses="Darkvision 60",
        own=[FLYER, "**Proboscis:** +5 to hit, 1d4 + 3 Physical, and it latches on: the target is **Grappled** by it."],
        own_fx=[dict(name="Proboscis", use="action", reach=5, target="enemy", atk=dict(flat=5, vs="weapon"),
                     do=[dict(dmg="1d4+3", type="Physical"), dict(cond="Grappled")])]),
    foe("Giant Centipede", ["Stone Blood"], body=(1, 2, -2, -4, 7, 30, "Small"),
        own=["**Wall Crawler:** climbs walls and ceilings at full Speed.",
             "**Bite:** +4 to hit, 1d4 + 2 Physical, and the target is **Poisoned** until the end of the centipede's next turn."],
        own_fx=[dict(name="Bite", use="action", reach=5, target="enemy", atk=dict(flat=4, vs="weapon"), tags=["poison"],
                     do=[dict(dmg="1d4+2", type="Physical"), dict(cond="Poisoned", until="endSourceTurn")])]),
    foe("Boar", ["Defiance"], body=(1, 0, -1, -3, 9, 40, "Medium"), alert=True,
        own=["**Tusks:** +3 to hit, 1d6 + 1 Physical.",
             "**Charge:** when it hits right after a Move straight at the target, the target falls **Prone**.",
             "**Keen Nose:** alert (passive Awareness +5)."],
        own_fx=[dict(name="Tusks", use="action", reach=5, target="enemy", atk=dict(flat=3, vs="weapon"),
                     do=[dict(dmg="1d6+1", type="Physical")])]),
    foe("Flying Sword", ["Longsword"], body=(2, 2, -3, -5, 14, 50, "Small"),
        own=[CONSTRUCT, FLYER, "**Steel Body:** +5 STR Defense (included)."],
        bonus={"STRd": 5}, own_fx=[CONSTRUCT_FX]),
    foe("Goblin Boss", ["Shortsword", "Shield", "Mail", "Rallying Cry"], body=(0, 2, 0, 0, 17, 30, "Small"),
        senses="Darkvision 60", leader=True,
        own=["**Nimble (2/S.R.):** reaction. Move up to half its Speed without provoking opportunity attacks.",
             "**Meat Shield:** when an attack hits it, it may pull an adjacent goblin in the way: the goblin is hit instead."],
        own_fx=[dict(name="Nimble", use="reaction", uses="2/SR", target="self", do=[dict(move="safe", ft="half")])]),
    foe("Gnoll", ["Shortbow", "Leather", "Cleave"], body=(2, 1, 0, -2, 25, 30, "Medium"), senses="Darkvision 60",
        own=["**Rend:** +4 to hit, 1d6 + 2 Physical."],
        own_fx=[dict(name="Rend", use="action", reach=5, target="enemy", atk=dict(flat=4, vs="weapon"),
                     do=[dict(dmg="1d6+2", type="Physical")])]),
    foe("Shadow", ["Night Eyes"], body=(1, 2, 0, -1, 12, 40, "Medium"), senses="Darkvision 120",
        own=[UNDEAD, "**Incorporeal:** resists Physical. Moves through creatures and objects.",
             "**Draining Touch:** +4 to hit, 2d6 + 2 Necrotic. The target's damage rolls lose 1d4 for 2 turns."],
        own_fx=[UNDEAD_FX, dict(name="Incorporeal", use="passive", resist=["Physical"]),
                dict(name="Draining Touch", use="action", reach=5, target="enemy", atk=dict(flat=4, vs="weapon"),
                     do=[dict(dmg="2d6+2", type="Necrotic"), dict(mod="dmg", dice="-1d4", until="targetTurns2")])]),
    foe("Dire Wolf", ["Wolfpack"], body=(3, 2, 1, -2, 18, 50, "Large"), senses="Darkvision 60", alert=True,
        own=["**Bite:** +5 to hit, 1d10 + 3 Physical.", "**Keen Nose:** alert (passive Awareness +5)."],
        own_fx=[dict(name="Bite", use="action", reach=5, target="enemy", atk=dict(flat=5, vs="weapon"),
                     do=[dict(dmg="1d10+3", type="Physical")])]),
    foe("Ghoul", ["Springheel"], body=(1, 2, 0, -2, 20, 30, "Medium"), senses="Darkvision 60",
        own=[UNDEAD, "**Claws:** +4 to hit, 2d4 + 2 Physical.",
             "**Paralyzing Touch (Recharge 5–6):** action. Attack (+3) against the STR Defense of a creature within 5 ft: "
             "**Subdue · Stunned** (paralyzed)."],
        own_fx=[UNDEAD_FX, dict(name="Claws", use="action", reach=5, target="enemy", atk=dict(flat=4, vs="weapon"),
                                do=[dict(dmg="2d4+2", type="Physical")]),
                dict(name="Paralyzing Touch", use="action", recharge=5, reach=5, target="enemy", atk=dict(flat=3, vs="STR"),
                     do=[dict(cond="Stunned")], subdue=True, lasting=True)]),
    foe("Bugbear", ["Battleaxe", "Javelins", "Leather", "Backstreets"], body=(2, 2, 0, -1, 31, 30, "Medium"),
        senses="Darkvision 60",
        own=["**Grab:** +4 to hit, 2d6 + 2 Physical, and the target is **Grappled** by it.",
             "**Abduct:** it moves at full Speed while dragging a creature it grapples."],
        own_fx=[dict(name="Grab", use="action", reach=5, target="enemy", atk=dict(flat=4, vs="weapon"),
                     do=[dict(dmg="2d6+2", type="Physical"), dict(cond="Grappled")])]),
    foe("Animated Armor", ["Plate"], body=(2, 0, -4, -5, 21, 35, "Medium"),
        own=[CONSTRUCT, "**Slam:** +4 to hit, 1d6 + 2 Physical.",
             "**False Appearance:** while it stays still, it looks like an empty suit of armor."],
        own_fx=[CONSTRUCT_FX, dict(name="Slam", use="action", reach=5, target="enemy", atk=dict(flat=4, vs="weapon"),
                                   do=[dict(dmg="1d6+2", type="Physical")])]),
    foe("Harpy", ["Minstrel"], body=(1, 1, 0, 1, 38, 40, "Medium"),
        own=[FLYER, "**Claws:** +3 to hit, 2d4 + 1 Physical.",
             "**Luring Song (Recharge 5–6):** action. Attack (+3) against the WIL Defense of each enemy within 60 ft "
             "who can hear it: **Subdue · Charmed**."],
        own_fx=[dict(name="Claws", use="action", reach=5, target="enemy", atk=dict(flat=3, vs="weapon"),
                     do=[dict(dmg="2d4+1", type="Physical")]),
                dict(name="Luring Song", use="action", recharge=5, reach=60, target="enemies", atk=dict(flat=3, vs="WIL"),
                     do=[dict(cond="Charmed")], subdue=True, lasting=True, tags=["mind control"])]),
    foe("Brown Bear", ["Sinew"], body=(2, 1, 1, -2, 18, 35, "Large"), senses="Darkvision 60", alert=True,
        own=["**Bite:** +5 to hit, 1d8 + 3 Physical.", "**Claw:** +5 to hit, 1d4 + 3 Physical, and the target falls **Prone**.",
             "**Keen Nose:** alert (passive Awareness +5)."],
        own_fx=[dict(name="Bite", use="action", reach=5, target="enemy", atk=dict(flat=5, vs="weapon"),
                     do=[dict(dmg="1d8+3", type="Physical")]),
                dict(name="Claw", use="action", reach=5, target="enemy", atk=dict(flat=5, vs="weapon"),
                     do=[dict(dmg="1d4+3", type="Physical"), dict(cond="Prone")])]),
    foe("Gelatinous Cube", ["Potion of Healing", "Coin Pouch"], body=(5, -4, -2, -5, 63, 15, "Large"),
        own=["**Ooze:** resists Poison. Never checks Morale. **Transparent:** easy to miss until it moves.",
             "**Soft Body:** −5 STR Defense (included).",
             "**Pseudopod:** +4 to hit, 3d6 Poison.",
             "**Engulf (Recharge 5–6):** action. Attack (+4) against the DEX Defense of a creature within 5 ft: "
             "3d6 Poison, and it is **Restrained** inside the cube for 2 turns."],
        bonus={"STRd": -5},
        own_fx=[dict(name="Ooze", use="passive", resist=["Poison"], fearless=True),
                dict(name="Pseudopod", use="action", reach=5, target="enemy", atk=dict(flat=4, vs="weapon"),
                     do=[dict(dmg="3d6", type="Poison")]),
                dict(name="Engulf", use="action", recharge=5, reach=5, target="enemy", atk=dict(flat=4, vs="DEX"),
                     do=[dict(dmg="3d6", type="Poison"), dict(cond="Restrained", until="targetTurns2")])]),
    foe("Owlbear", ["Bravado", "Second Wind"], body=(4, 1, 1, -2, 51, 40, "Large"), senses="Darkvision 60",
        boss=True, alert=True,
        own=["**Beak:** +7 to hit, 1d10 + 5 Physical.", "**Claws:** +7 to hit, 2d8 + 5 Physical.",
             "**Keen Eyes:** alert (passive Awareness +5)."],
        own_fx=[dict(name="Beak", use="action", reach=5, target="enemy", atk=dict(flat=7, vs="weapon"),
                     do=[dict(dmg="1d10+5", type="Physical")]),
                dict(name="Claws", use="action", reach=5, target="enemy", atk=dict(flat=7, vs="weapon"),
                     do=[dict(dmg="2d8+5", type="Physical")])]),
]

BLANKS = 4  # blank foe cards for monsters built from scratch (GM 2.2)
