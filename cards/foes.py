"""Foe cards (GM 2.1): one card per kind of monster, built from base-set cards.

Built into rules/Bearers-Base-Set.pdf by tools/build_cards.py, which adds up the totals and the attacks.
Foe cards are double width (126 × 88 mm): a drawing on the left, the card on the right.
core and carries name base-set cards (they print in italics and can drop). A monster whose body can't drop
uses body=(STR, DEX, INT, WIL, HP, Speed, size) instead of core. own is the monster's plain text: it never drops.
bonus adds plain-text numbers to the strip; extra_dice adds damage dice to every weapon (an int) or to the named weapons
({weapon card name: n}). recharge={card name: 5} turns a carried card's limited uses into Recharge 5–6 for this foe.
powers picks which powers of a carried deck the foe uses (the whole deck drops).
alert and own_fx are the sim's mechanics for own: alert = Keen Nose, own_fx = Powers (SPEC 2.1) for plain-text attacks and powers.
The keywords at the bottom are built from the type (Foe, Boss), the size and senses.
"""


def foe(name, carries, core=None, body=None, own=(), bonus=None, extra_dice=0, recharge=None, powers=(), senses="", boss=False,
        alert=False, own_fx=()):
    return dict(name=name, core=core, body=body, carries=list(carries), own=list(own), bonus=bonus or {},
                extra_dice=extra_dice, recharge=recharge or {}, powers=list(powers), senses=senses, boss=boss, alert=alert, own_fx=list(own_fx))


FOES = [
    foe("Bandit", ["Handaxe", "Pocket Sand", "Leather"], core="Balanced"),
    foe("Archer", ["Longbow", "Dagger", "Steady Aim", "Leather"], core="Nimble"),
    foe("Goblin", ["Sling", "Dagger", "Slippery", "Leather"], body=(-1, 2, 0, -1, 7, 30, "Small"),
        senses="Darkvision 60"),
    foe("Wolf", ["Pack Hunter"], body=(1, 2, -1, -2, 11, 40, "Medium"),
        own=["**Bite:** +4 to hit, 1d6 + 2 Physical.", "**Keen Nose:** alert (passive Awareness +5)."],
        alert=True, own_fx=[dict(name="Bite", use="action", reach=5, target="enemy", atk=dict(flat=4, vs="weapon"),
                                 do=[dict(dmg="1d6+2", type="Physical")])]),
    foe("Cultist", ["Dagger", "Acolyte's Litany", "Iron Will"], core="Envoy", powers=["Bane", "Twist Fate", "Healing Word"]),
    foe("Legionary", ["Pilum", "Gladius", "Shield Wall", "Mail", "Shield"], core="Brute",
        own=["Throws its *Pilum*, then draws its *Gladius*."]),
    foe("Bandit Captain", ["Finesse Blade", "Dagger", "Twin Strike", "Leather", "Coin Pouch"], core="Bandit Captain"),
    foe("Ogre", ["Greatclub", "Javelins", "Sweeping Blow"], core="Ogre",
        own=["**Giant Strength:** +60 HP. Its *Javelins* roll one extra damage die (included). "
             "Its *Sweeping Blow* recharges on a 5–6 instead of 1/S.R."],
        bonus={"HP": 60}, extra_dice={"Javelins": 1}, recharge={"Sweeping Blow": 5}, senses="Darkvision 60"),
    foe("Ogre Chieftain", ["Greatclub", "Cleave", "Second Wind", "Sweeping Blow", "Plate"], body=(5, 0, 0, 1, 70, 40, "Large"),
        own=["**Warlord:** its *Sweeping Blow* recharges on a 5–6 instead of 1/S.R.",
             "**Bellow (Recharge 5–6):** bonus action. Attack (+5) against the WIL Defense of each enemy within 30 ft: "
             "Frightened of the chieftain until the end of its next turn."],
        recharge={"Sweeping Blow": 5}, senses="Darkvision 60", boss=True,
        own_fx=[dict(name="Bellow", use="bonus", recharge=5, target="enemies", reach=30, atk=dict(flat=5, vs="WIL"),
                     do=[dict(cond="Frightened", until="endSourceTurn")], tags=["fear"])]),
]

BLANKS = 4  # blank foe cards for monsters built from scratch (GM 2.2)
