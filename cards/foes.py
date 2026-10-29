"""Foe cards (GM 2.1): one card per kind of monster, built from base-set cards.

Built into rules/Bearers-Base-Set.pdf by tools/build_cards.py, which adds up the totals and the attacks.
Foe cards are double width (126 × 88 mm): a drawing on the left, the card on the right.
core and carries name base-set cards (they print in italics and can drop). A monster whose body can't drop
uses body=(STR, DEX, INT, WIL, HP, Speed, size) instead of core. own is the monster's plain text: it never drops.
bonus adds plain-text numbers to the strip; extra_dice adds damage dice to every weapon (an int) or to the named weapons
({weapon card name: n}). recharge={card name: 5} turns a carried card's limited uses into Recharge 5–6 for this foe.
powers picks which powers of a carried deck the foe uses (the whole deck drops).
alert and own_fx are the sim's mechanics for own: alert = Keen Nose, own_fx = Powers (SPEC 2.1) for plain-text attacks and powers.
leader=True marks a foe that leads its group (keyword Leader, Morale P 6.11).
The keywords at the bottom are built from the type (Foe, Boss), Leader, the size and senses.
"""


def foe(name, carries, core=None, body=None, own=(), bonus=None, extra_dice=0, recharge=None, powers=(), senses="", boss=False,
        leader=False, alert=False, own_fx=()):
    return dict(name=name, core=core, body=body, carries=list(carries), own=list(own), bonus=bonus or {},
                extra_dice=extra_dice, recharge=recharge or {}, powers=list(powers), senses=senses, boss=boss, leader=leader, alert=alert,
                own_fx=list(own_fx))


UNDEAD = "**Undead:** resists Poison and Necrotic, vulnerable to Radiant. Never checks Morale."
UNDEAD_FX = dict(name="Undead", use="passive", resist=["Poison", "Necrotic"], vuln=["Radiant"], fearless=True)

FOES = [
    foe("Bandit", ["Handaxe", "Pocket Sand", "Leather"], core="Balanced"),
    foe("Bandit Archer", ["Longbow", "Dagger", "Steady Aim", "Leather"], core="Nimble"),
    foe("Goblin", ["Sling", "Dagger", "Slippery", "Leather"], body=(-1, 2, 0, -1, 7, 30, "Small"),
        senses="Darkvision 60"),
    foe("Wolf", ["Pack Hunter"], body=(1, 2, -1, -2, 11, 40, "Medium"),
        own=["**Bite:** +4 to hit, 1d6 + 2 Physical.", "**Keen Nose:** alert (passive Awareness +5)."],
        alert=True, own_fx=[dict(name="Bite", use="action", reach=5, target="enemy", atk=dict(flat=4, vs="weapon"),
                                 do=[dict(dmg="1d6+2", type="Physical")])]),
    foe("Cultist", ["Dagger", "Acolyte's Litany", "Iron Will"], core="Envoy", powers=["Bane", "Twist Fate", "Healing Word"]),
    foe("Legionary", ["Pilum", "Gladius", "Shield Wall", "Mail", "Shield"], core="Brute",
        own=["Throws its *Pilum*, then draws its *Gladius*."]),
    foe("Bandit Captain", ["Finesse Blade", "Dagger", "Twin Strike", "Leather", "Coin Pouch"], core="Bandit Captain",
        leader=True),
    foe("Ogre", ["Greatclub", "Javelins", "Sweeping Blow"], core="Ogre",
        own=["**Giant Strength:** +60 HP. Its *Javelins* roll one extra damage die (included). "
             "Its *Sweeping Blow* recharges on a 5–6 instead of 1/S.R."],
        bonus={"HP": 60}, extra_dice={"Javelins": 1}, recharge={"Sweeping Blow": 5}, senses="Darkvision 60"),
    foe("Ogre Chieftain", ["Greatclub", "Cleave", "Second Wind", "Sweeping Blow", "Plate"], body=(5, 0, 0, 1, 70, 40, "Large"),
        own=["**Warlord:** its *Sweeping Blow* recharges on a 5–6 instead of 1/S.R.",
             "**Bellow (Recharge 5–6):** reaction. Attack (+5) against the WIL Defense of each enemy within 30 ft: "
             "Frightened of the chieftain until the end of its next turn."],
        recharge={"Sweeping Blow": 5}, senses="Darkvision 60", boss=True, leader=True,
        own_fx=[dict(name="Bellow", use="reaction", recharge=5, target="enemies", reach=30, atk=dict(flat=5, vs="WIL"),
                     do=[dict(cond="Frightened", until="endSourceTurn")], tags=["fear"])]),
    # basic humanoids, built on the species Cores
    foe("Guard", ["Longsword", "Shield", "Javelins", "Mail"], core="Human"),
    foe("Scout", ["Longbow", "Shortsword", "Hunter", "Leather"], core="Elf", senses="Darkvision 60", alert=True,
        own=["**Keen Eyes:** alert (passive Awareness +5)."]),
    foe("Mage", ["Conjurer's Book", "Dagger", "Clear Mind"], core="Scholar", powers=["Fire Bolt", "Magic Missile", "Shield"]),
    foe("Orc", ["Greataxe", "Javelins", "Relentless", "Leather"], core="Orc", senses="Darkvision 60"),
    foe("Hobgoblin", ["Longsword", "Shield", "Longbow", "Mail", "Battle Hymn"], core="Hobgoblin", senses="Darkvision 60"),
    # classic monsters
    foe("Skeleton", ["Shortsword", "Shortbow", "Leather"], body=(0, 2, -2, -2, 10, 30, "Medium"), senses="Darkvision 60",
        own=[UNDEAD], own_fx=[UNDEAD_FX]),
    foe("Zombie", ["Relentless"], body=(1, -2, -4, -2, 20, 20, "Medium"), senses="Darkvision 60",
        own=[UNDEAD, "**Slam:** +3 to hit, 1d8 + 1 Physical."],
        own_fx=[UNDEAD_FX, dict(name="Slam", use="action", reach=5, target="enemy", atk=dict(flat=3, vs="weapon"),
                                do=[dict(dmg="1d8+1", type="Physical")])]),
    foe("Kobold", ["Dagger", "Sling", "Pack Hunter"], body=(-2, 2, -1, -1, 5, 30, "Small"), senses="Darkvision 60"),
    foe("Giant Rat", ["Pack Hunter"], body=(-2, 2, -4, -2, 5, 30, "Small"), senses="Darkvision 60", alert=True,
        own=["**Bite:** +4 to hit, 1d4 + 2 Physical.", "**Keen Nose:** alert (passive Awareness +5)."],
        own_fx=[dict(name="Bite", use="action", reach=5, target="enemy", atk=dict(flat=4, vs="weapon"),
                     do=[dict(dmg="1d4+2", type="Physical")])]),
    foe("Giant Spider", ["Cat Burglar"], body=(2, 3, -4, -2, 26, 30, "Large"), senses="Darkvision 60", alert=True,
        own=["**Spider Climb:** climbs walls and ceilings at full Speed. **Web Sense:** alert (passive Awareness +5).",
             "**Bite:** +5 to hit, 1d8 + 3 Physical plus 1d8 Poison.",
             "**Web (Recharge 5–6):** action, range 30 ft. Attack (+3) against DEX Defense: **Restrained** for 2 turns."],
        own_fx=[dict(name="Bite", use="action", reach=5, target="enemy", atk=dict(flat=5, vs="weapon"),
                     do=[dict(dmg="1d8+3", type="Physical"), dict(dmg="1d8", type="Poison")]),
                dict(name="Web", use="action", recharge=5, reach=30, target="enemy", atk=dict(flat=3, vs="DEX"),
                     do=[dict(cond="Restrained", until="targetTurns2")])]),
    foe("Troll", ["Night Eyes", "Stone Blood"], body=(4, 1, -1, -2, 80, 30, "Large"), senses="Darkvision 60", alert=True,
        own=["**Claws:** +6 to hit, 2d6 + 4 Physical.",
             "**Regeneration:** regains 10 HP at the start of its turn, unless it took Fire or Poison damage since its last turn.",
             "**Keen Nose:** alert (passive Awareness +5)."],
        own_fx=[dict(name="Claws", use="action", reach=5, target="enemy", atk=dict(flat=6, vs="weapon"),
                     do=[dict(dmg="2d6+4", type="Physical")]),
                dict(name="Regeneration", use="passive", regen=10, stopBy=["Fire", "Poison"])]),
]

BLANKS = 4  # blank foe cards for monsters built from scratch (GM 2.2)
