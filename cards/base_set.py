"""The base set: every card and Slot frame for a 4-player test game.

Built into rules/Bearers-Base-Set.pdf by tools/build_cards.py.
Strip keys: STR DEX INT WIL (modifiers), STRd DEXd INTd WILd (Defenses), HP, SPD.
Text uses **bold** and *italic*; each list item is one paragraph.
"""
import re

PLAYERS = 4


def card(name, rank, kind, kw, text=(), strip=None, copies=1, group="starter", **extra):
    return dict(name=name, rank=rank, kind=kind, kw=kw, text=list(text), strip=strip or {},
                copies=copies, group=group, **extra)


def core(name, rank, mods, hp, spd, size="Medium", text=(), group="starter"):
    s, d, i, w = mods
    strip = {"STR": f"{s:+d}", "DEX": f"{d:+d}", "INT": f"{i:+d}", "WIL": f"{w:+d}",
             "STRd": str(10 + s), "DEXd": str(10 + d), "INTd": str(10 + i), "WILd": str(10 + w),
             "HP": str(hp), "SPD": str(spd)}
    return card(name, rank, "core", f"Core · {size}", text, strip, group=group)


CORES = [
    core("Brute", "I", (3, 1, 0, 0), 14, 30),
    core("Nimble", "I", (0, 3, 1, 0), 11, 35),
    core("Scholar", "I", (0, 1, 3, 0), 9, 30),
    core("Envoy", "I", (0, 1, 0, 3), 10, 30),
    core("Balanced", "I", (2, 1, 1, 0), 12, 30),
    core("Ogre", "II", (4, 0, 0, 0), 35, 35, "Large", group="loot"),
    core("Bandit Captain", "II", (2, 3, 0, 1), 30, 30, group="loot"),
]

ARMOR = [
    card("Leather", "I", "gear", "Armor", ["Supple hide, oiled and stitched."], {"STRd": "+2", "DEXd": "+1", "SPD": "+5"}, copies=2),
    card("Mail", "I", "gear", "Armor · Req STR +1", ["Riveted rings over a padded coat."], {"STRd": "+3"}, copies=2),
    card("Plate", "II", "gear", "Armor · Noisy 3 · Req STR +2", ["Full steel, fitted to you."], {"STRd": "+4", "SPD": "−10"}, group="loot"),
]


def weapon_atk(dice, kw, attack):
    """Structured attack of a weapon, read from its own args (SPEC 2, WeaponAtk)."""
    parts = kw.split(" · ")
    pair = lambda key: next(([int(a), int(b)] for p in parts if p.startswith(key) for a, b in [re.findall(r"\d+", p)]), None)
    two = re.search(r"Versatile \((\d+d\d+)\)", kw)
    ranged = pair("Range")
    finesse = "Finesse" in parts
    return dict(hit=int(attack.replace("−", "-")), dice=dice.split(" / ")[0], two=two[1] if two else None,
                abil=["DEX"] if ranged else ["STR", "DEX"] if finesse else ["STR"], type="Physical",
                finesse=finesse, light="Light" in parts, heavy="Heavy" in parts, reach="Reach" in parts,
                twoHanded="Two-Handed" in parts, loading="Loading" in parts, thrown=pair("Thrown"), range=ranged)


def weapon(name, dice, kw, effect=None, attack="+2", rank="I", copies=1, group="starter"):
    attr = "STR or DEX" if "Finesse" in kw else "DEX" if "Range" in kw else "STR"
    text = [f"{attack} to hit, {dice} + {attr} Physical." + (f" {effect}" if effect else "")]
    return card(name, rank, "gear", f"Weapon · {kw}", text, copies=copies, group=group, atk=weapon_atk(dice, kw, attack))


HANDS = [
    card("Shield", "I", "gear", "Shield", ["Takes one Hand."], {"STRd": "+2", "DEXd": "+2"}, copies=2),
    weapon("Dagger", "1d4", "Finesse · Light · Thrown 20/60", attack="+4"),
    weapon("Shortsword", "1d4", "Finesse · Light", attack="+3"),
    weapon("Handaxe", "1d6", "Light · Thrown 20/60"),
    weapon("Finesse Blade", "1d6", "Finesse", "**Sap:** when you hit, the target has −2 on its next attack roll before the start of your next turn."),
    weapon("Longsword", "1d8 / 1d10", "Versatile (1d10)"),
    weapon("Battleaxe", "1d8 / 1d10", "Versatile (1d10)"),
    weapon("Greatsword", "2d6", "Heavy · Two-Handed"),
    weapon("Glaive", "1d10", "Heavy · Reach · Two-Handed"),
    weapon("Longbow", "1d8", "Range 150/600 · Two-Handed"),
    weapon("Sling", "1d6", "Light · Range 30/120"),
    weapon("Javelins", "1d6", "Thrown 30/120"),
    weapon("Spellguard Staff", "1d8 / 1d10", "Versatile (1d10)", "While you hold it, it counts as an empty Hand for casting from a Spellbook."),
    card("Traveler's Lute", "I", "gear", "Instrument · Focus", ["1 extra Resolve (short rest).", "Your Anthems reach 60 ft instead of 30 ft."]),
    weapon("Greatclub", "1d10", "Heavy · Two-Handed", "**Crushing:** on a critical hit, the target is knocked Prone.", group="loot"),
    weapon("Gladius", "1d6", "Light", "**Close Order:** +1d4 damage while an ally is engaged with the same creature.", group="loot"),
    weapon("Boarspear", "1d8 / 1d10", "Versatile (1d10)", "**Brace:** your opportunity attacks with it deal +1d8 damage.", attack="+3", rank="II", group="loot"),
    weapon("Pilum", "1d6", "Thrown 30/120", "**Pierce:** on a hit, a Shield the target holds gives no bonus until it spends an action to pull the pilum free.", attack="+3", rank="II", group="loot"),
]

JEWELRY = [
    card("Ring of Warding", "I", "gear", "Jewelry", ["**Reaction (2/S.R.)**, when an attack hits you: +2 to the targeted Defense against that attack, possibly turning it into a miss."]),
    card("Guild Signet", "I", "gear", "Jewelry", ["**Action (1/L.R.)**, in a settlement where the guild operates: a contact finds you within 1 hour. They share one fact the guild would know, or hide you for a night."]),
    card("Shard Bandolier", "I", "gear", "Jewelry", ["Leather straps padded for crystal. You can carry 2 more Shards in your Pack (5 in all). They still count toward its 8 pieces."]),
    card("Holy Amulet", "I", "gear", "Jewelry · Focus", ["1 extra Resolve (short rest).", "Your Cues reach 90 ft instead of 60 ft."]),
    card("Boots of the Long Stride", "I", "gear", "Jewelry", ["**Bonus action (1/S.R.):** Dash."]),
    card("Ring of Sparks", "II", "gear", "Jewelry", ["**Reaction (1/S.R.)**, when a creature within 5 ft hits you: it takes 2d6 Lightning."], group="loot"),
]

ITEMS = [
    card("Potion of Healing", "I", "gear", "Consumable", ["**Bonus action:** drink it, or give it to a creature within 5 ft. It regains 2d4 + 2 HP."], copies=6),
    card("Coin Pouch", "I", "gear", "Purse", ["Holds up to **100 gp**."], copies=PLAYERS),
    card("Writ of Favor", "I", "gear", "Consumable", ["A sealed letter from a noble house, a guild or a temple. Show it to one of its members: they grant one reasonable request (shelter, an audience, safe passage, a loan up to 100 gp)."]),
    card("Greater Potion of Healing", "II", "gear", "Consumable", ["**Bonus action:** drink it, or give it to a creature within 5 ft. It regains 4d4 + 4 HP."], copies=2, group="loot"),
    card("Pocket Sand", "I", "gear", "Consumable", ["**Bonus action:** throw it at a creature within 5 ft. Attack (DEX or WIL + 2) against its DEX Defense: on a hit, it has −2 on attacks until the end of its next turn."], group="loot"),
    card("Alchemist's Fire Recipe", "II", "gear", "Recipe · 3 flasks", ["**Bonus action:** throw a flask up to 30 ft. Make one attack (DEX or INT + 3) against the DEX Defense of each creature within 5 ft of the impact: 2d6 Fire on a hit, half on a miss."], group="loot", uses=3),
]


def knack(name, acts, rank="I", bonus="+2", group="starter"):
    return card(name, rank, "aspect", "Knack", [f"{bonus} on checks to {acts}."], group=group)


ASPECTS = [
    card("Springheel", "I", "aspect", "Trait", ["Your jump distances are doubled, and you never need a running start."]),
    card("Stone Blood", "I", "aspect", "Trait", ["+2 STR Defense against poison."]),
    card("Iron Will", "I", "aspect", "Trait", ["+2 WIL Defense against fear and mind control."]),
    card("Clear Mind", "I", "aspect", "Trait", ["+2 INT Defense against illusions and confusion."]),
    card("Cleave", "I", "aspect", "Technique", ["**1/S.R.**, when your melee attack drops a creature to 0 HP: make one melee attack against another creature within your reach."]),
    card("Steady Aim", "I", "aspect", "Technique", ["**Bonus action (2/S.R.):** your next ranged attack this turn has +2 to hit."]),
    card("Shield Bash", "I", "aspect", "Technique", ["**Bonus action (1/S.R.)**, when you take the Attack action while holding a Shield: Shove a creature within 5 ft."]),
    card("Battle Hymn", "I", "aspect", "Technique", ["**2/S.R.**, when you hit with a weapon attack: up to 3 allies within 30 ft who can hear you have +2 on their next attack before the end of your next turn."]),
    card("Rallying Cry", "I", "aspect", "Technique · Anthem", ["*Rally* as a loose Anthem.", "**Bonus action (1/S.R.):** Duration 1 minute. Up to 3 allies within 30 ft have +2 on attacks."]),
    card("Shield Wall", "I", "aspect", "Technique", ["**Reaction (1/S.R.)**, when an attack hits an ally within 5 ft while you hold a Shield: +2 to the targeted Defense against that attack, possibly turning it into a miss."], group="loot"),
    knack("Cat Burglar", "sneak, climb or pick locks"),
    card("Renowned", "I", "aspect", "Knack", ["Choose a city, guild or order when you gain this. +2 on WIL checks with its people."]),
    knack("Sailor", "swim, climb, navigate or gather rumors"),
    knack("Street Urchin", "pick pockets, sneak, read intentions or gather rumors"),
    knack("Hunter", "track, notice, sneak or handle animals"),
    knack("Physician", "treat wounds, recall lore, read intentions or persuade"),
    knack("Barkeep", "read intentions, gather rumors, intimidate or lift"),
    knack("Smith", "lift, break, haggle or recall lore"),
    knack("Mountaineer", "climb, endure, navigate or balance"),
    # loot
    card("Twin Strike", "II", "aspect", "Technique", ["When you take the Attack action, you make two attacks instead of one."], group="loot"),
    card("Second Wind", "II", "aspect", "Trait", ["**Bonus action (1/S.R.):** regain 1d10 + 3 HP."], group="loot"),
    card("Wiry", "II", "aspect", "Trait", ["Lean, ropy strength."], {"STR": "+1", "STRd": "+1", "SPD": "+5"}, group="loot"),
    card("Night Eyes", "II", "aspect", "Trait · Darkvision 60", ["You see in the Dark within 60 ft as if it were Bright."], group="loot"),
    card("Sellsword", "II", "aspect", "Trait", ["+3 on checks to intimidate, endure, haggle or gather rumors."], {"STR": "+1", "STRd": "+1"}, group="loot"),
    card("Acrobat", "II", "aspect", "Trait", ["+3 on checks to tumble, balance, jump or perform."], {"DEX": "+1", "DEXd": "+1"}, group="loot"),
    card("Pack Hunter", "I", "aspect", "Trait", ["**1/S.R.**, when you hit a creature one of your allies is engaged with: it falls Prone."], group="loot"),
    card("Slippery", "I", "aspect", "Technique", ["**Bonus action (2/S.R.):** move up to half your Speed. This movement doesn't provoke opportunity attacks."], group="loot"),
    card("Hedge Witch", "II", "aspect", "Trait", ["1 extra spell point (long rest).", "+3 on checks to handle animals, recall lore, treat wounds or deceive."], group="loot"),
]


# ---------- decks: a cover card, then one card per spell or power ----------
# ---------- mechanics of decks (SPEC 2.1): name → Power, id/name/kind/cost are filled in by spell() / power() ----------
VOICE = ["voice"]
POWER_FX = {
    "Fire Bolt": dict(use="action", reach=120, target="enemy", atk=dict(abil="deck", vs="DEX"),
                      do=[dict(dmg="1d10", type="Fire")], tags=["fire"]),
    "Mage Hand": dict(use="action", reach=30, dur="1 minute", do=[]),
    "Magic Missile": dict(use="action", reach=120, target="darts", count=3, atk=dict(abil="deck", vs="DEX"), half=True,
                          do=[dict(dmg="1d4+1", type="Radiant")], upcast=dict(darts=1)),
    "Shield": dict(use="reaction", on="hitSelf", target="self", dur="1 round",
                   do=[dict(mod="def", n=5, defs=["STR", "DEX"], until="startSourceTurn")]),
    "Grease": dict(use="action", reach=60, target="point", area=dict(shape="cube", size=10), atk=dict(abil="deck", vs="DEX"),
                   zone=dict(terrain="difficult", on=["enter", "endTurn"]), do=[dict(cond="Prone")], dur="1 minute"),
    "Misty Step": dict(use="bonus", target="self", do=[dict(move="teleport", ft=30)]),
    "Web": dict(use="action", reach=60, target="point", area=dict(shape="cube", size=20), atk=dict(abil="deck", vs="DEX"),
                zone=dict(terrain="difficult", on=["enter"], burns=True, burnFt=5), do=[dict(cond="Restrained")],
                lasting=True, dur="1 hour"),
    "Jeer": dict(use="action", reach=60, target="enemy", need=VOICE, atk=dict(abil="deck", vs="WIL"),
                 do=[dict(mod="attack", n=-2, next=True, until="endTargetTurn")]),
    "Rally": dict(use="bonus", reach=30, target="allies", count=3, need=VOICE, dur="1 minute",
                  do=[dict(mod="attack", n=2, until="dur")]),
    "Hold the Line": dict(use="bonus", reach=30, target="allies", need=VOICE, dur="1 minute",
                          do=[dict(mod="def", n=2, defs=["STR", "DEX"], until="dur")]),
    "Cutting Words": dict(use="reaction", on="rollNear", reach=60, target="enemy", need=VOICE,
                          do=[dict(mod="roll", n=-2)], params=dict(rollKinds=["attack", "check"])),
    "Steady Now": dict(use="reaction", on="rollNear", reach=60, target="ally", need=VOICE,
                       do=[dict(mod="roll", n=2)], params=dict(orDefense=True)),
    "Dread": dict(use="action", reach=60, target="enemy", need=VOICE, atk=dict(abil="deck", vs="WIL"),
                  do=[dict(cond="Frightened")], lasting=True, tags=["fear"]),
    "Guidance": dict(use="reaction", on="rollNear", reach=60, target="ally", need=VOICE,
                     do=[dict(mod="roll", dice="1d4")], params=dict(rollKinds=["check"])),
    "Bless": dict(use="bonus", reach=30, target="allies", count=3, need=VOICE, dur="1 minute",
                  do=[dict(mod="attack", dice="1d4", until="dur")]),
    "Bane": dict(use="action", reach=60, target="enemy", need=VOICE, atk=dict(abil="deck", vs="WIL"),
                 do=[dict(mod="attack", dice="-1d4", until="lasting")], lasting=True),
    "Twist Fate": dict(use="reaction", on="rollNear", reach=60, target="creature", need=VOICE,
                       do=[dict(reroll=True)], params=dict(rollKinds=["attack", "check"])),
    "Healing Word": dict(use="bonus", reach=60, target="creature", need=VOICE, do=[dict(heal="2d4+WIL")]),
    "Cure Wounds": dict(use="action", reach=5, target="creature", need=VOICE, do=[dict(heal="2d8+WIL")]),
    "Mossbalm": dict(use="action", reach=5, target="creature", do=[dict(heal="2d8+WIL")]),
    "Hawk": dict(use="bonus", target="self", form=dict(
        strip={"STR": -2, "DEX": 3, "STRd": 8, "DEXd": 13, "HP": 4, "SPD": 10}, size="Tiny", fly=60, climb=0,
        weapon=dict(name="Talons", hit=2, dice="1d4", abil=["DEX"], type="Physical"))),
    "Wolf": dict(use="bonus", target="self", form=dict(
        strip={"STR": 1, "DEX": 3, "STRd": 11, "DEXd": 13, "HP": 8, "SPD": 40}, size="Medium", fly=0, climb=0,
        weapon=dict(name="Bite", hit=2, dice="1d6", abil=["DEX"], type="Physical"))),
    "Bear": dict(use="bonus", target="self", form=dict(
        strip={"STR": 3, "DEX": 1, "STRd": 15, "DEXd": 11, "HP": 12, "SPD": 30}, size="Large", fly=0, climb=30,
        weapon=dict(name="Claws", hit=2, dice="1d8", abil=["STR"], type="Physical"))),
}


def spell(name, level, text, kw):
    cost = 0 if level == "Cantrip" else int(level[0])
    fx = dict(name=name, kind="Cantrip" if cost == 0 else "Spell", cost=cost, **POWER_FX[name])
    return dict(name=name, level=level, cost=cost, text=list(text), kw=kw, strip={}, fx=fx)


CONJURER = dict(
    cover=card("Conjurer's Book", "I", "gear", "Spellbook", [
        "Spell attack: **INT + 2**", "Spell points: **4** (long rest)", "Max spell level: **2nd**",
        "Casting needs an empty Hand."]),
    color="gear", stats=dict(kind="spellbook", atk=2, sp=4, maxLevel=2),
    cards=[
        spell("Fire Bolt", "Cantrip", ["**Action**, range 120 ft.", "Spell attack against DEX Defense: **1d10 Fire**. A flammable object it hits catches fire."], "Cantrip · Targets DEX · Range 120"),
        spell("Mage Hand", "Cantrip", ["**Action**, range 30 ft, Duration 1 minute.", "A spectral hand lifts, carries or works an object up to 10 lb. It can't attack. Move it as a bonus action."], "Cantrip · Duration 1 minute"),
        spell("Magic Missile", "1st", ["**Action**, range 120 ft.", "Three darts at one to three creatures. One spell attack against the DEX Defense of each target: **1d4 + 1 Radiant** per dart on a hit, half on a miss.", "**Upcast:** +1 dart per level above 1st."], "Spell · Targets DEX · Range 120"),
        spell("Shield", "1st", ["**Reaction**, when an attack hits you.", "+5 to your STR and DEX Defense until the start of your next turn, against the triggering attack too."], "Spell · Duration 1 round"),
        spell("Grease", "1st", ["**Action**, range 60 ft, Duration 1 minute.", "A 10-ft cube of slick grease: difficult terrain. Spell attack against the DEX Defense of each creature in it, and of each one that enters it or ends its turn there: on a hit, it falls **Prone**."], "Spell · Cube 10 · Targets DEX"),
        spell("Misty Step", "2nd", ["**Bonus action.**", "Teleport up to 30 ft to an unoccupied space you can see."], "Spell"),
        spell("Web", "2nd", ["**Action**, range 60 ft, Duration 1 hour.", "A 20-ft cube of webs: difficult terrain. Spell attack against the DEX Defense of each creature in it, and of each one that enters it: on a hit, it is **Restrained** (Lasting). Fire burns a 5-ft square away each round."], "Spell · Cube 20 · Targets DEX · Lasting · Restrained"),
    ],
)


def power(name, kind, cost, text, strip=None):
    fx = dict(name=name, kind=kind, cost=cost, **POWER_FX[name])
    return dict(name=name, level=kind, cost=cost, text=list(text), kw=kind, strip=strip or {}, fx=fx)


REPERTOIRE = dict(
    cover=card("Wanderer's Repertoire", "I", "aspect", "Glamour", [
        "Attack: **WIL + 2**", "Resolve: **3 + WIL** (short rest)", "Songs, poems and dances."]),
    color="aspect", stats=dict(kind="glamour", atk=2, resolve=3),
    cards=[
        power("Jeer", "Dirge", 0, ["**Action.** Attack against WIL Defense: until the end of the target's next turn, it has −2 on its next attack."]),
        power("Rally", "Anthem", 1, ["**Bonus action**, Duration 1 minute.", "Up to 3 allies within 30 ft have +2 on attacks."]),
        power("Hold the Line", "Anthem", 1, ["**Bonus action**, Duration 1 minute.", "Allies within 30 ft have +2 to STR and DEX Defense."]),
        power("Cutting Words", "Cue", 1, ["**Reaction**, after a creature within 60 ft rolls.", "−2 to an enemy's attack roll or check."]),
        power("Steady Now", "Cue", 1, ["**Reaction**, after a creature within 60 ft rolls.", "+2 to an ally's roll, or to the Defense an attack targets."]),
        power("Dread", "Dirge", 2, ["**Action.** Attack against WIL Defense: the target is **Frightened** of you (Lasting)."]),
    ],
)

LITANY = dict(
    cover=card("Acolyte's Litany", "I", "aspect", "Divine", [
        "Attack: **WIL + 2**", "Resolve: **3 + WIL** (short rest)", "Prayers. Fate dice: **d4**."]),
    color="aspect", stats=dict(kind="divine", atk=2, resolve=3, fate="1d4"),
    cards=[
        power("Guidance", "Cue", 0, ["**Reaction**, after an ally within 60 ft rolls a check.", "Add 1d4 to it."]),
        power("Bless", "Anthem", 1, ["**Bonus action**, Duration 1 minute.", "Up to 3 allies within 30 ft add 1d4 to their attack rolls."]),
        power("Bane", "Dirge", 1, ["**Action.** Attack against WIL Defense: the target subtracts 1d4 from its attack rolls (Lasting)."]),
        power("Twist Fate", "Cue", 1, ["**Reaction**, after a creature within 60 ft rolls.", "**Reroll:** make it reroll an attack roll or a check."]),
        power("Healing Word", "Mend", 2, ["**Bonus action**, range 60 ft.", "A creature regains 2d4 + WIL HP."]),
        power("Cure Wounds", "Mend", 2, ["**Action**, touch.", "A creature regains 2d8 + WIL HP."]),
    ],
)

def form(s, d, hp, spd, hide=0):
    """A Form's strip (P 10.7): its own STR, DEX, HP and Speed, printed like a Core."""
    return {"STR": f"{s:+d}".replace("-", "−"), "DEX": f"{d:+d}".replace("-", "−"),
            "STRd": str(10 + s + hide), "DEXd": str(10 + d), "HP": str(hp), "SPD": str(spd)}


REMEMBRANCE = dict(
    cover=card("Wildheart's Remembrance", "I", "aspect", "Nature", [
        "Resolve: **3 + WIL** (short rest)", "Beasts your body remembers. Shift: bonus action."]),
    color="aspect", stats=dict(kind="nature", resolve=3),
    cards=[
        power("Hawk", "Form", 1, ["**Tiny** · Fly 60 ft.", "Talons: +2 to hit, 1d4 + DEX Physical.", "+2 on checks to notice."], form(-2, 3, 4, 10)),
        power("Wolf", "Form", 2, ["**Medium**.", "Bite: +2 to hit, 1d6 + DEX Physical.", "+2 on checks to track."], form(1, 3, 8, 40)),
        power("Mossbalm", "Mend", 2, ["**Action**, touch.", "A creature regains 2d8 + WIL HP."]),
        power("Bear", "Form", 3, ["**Large** · Climb 30 ft.", "Hide: +2 STR Defense (included).", "Claws: +2 to hit, 1d8 + STR Physical."], form(3, 1, 12, 30, hide=2)),
    ],
)

DECKS = [CONJURER, REPERTOIRE, LITANY, REMEMBRANCE]

GOLD = [(1, 8), (10, 8), (50, 6), (100, 4), (500, 2), (1000, 1)]  # (value, copies)
TALLIES = 6

# ---------- Slot frames ----------
# (key, name, swap time, empty-Slot reminder, copies)
FRAMES = [
    ("armor", "Armor", "Swap: 10 minutes", ["Empty: **+10 ft Speed**."], PLAYERS),
    ("hand", "Hand", "Swap: free interaction", ["One Weapon, Shield or Instrument.", "Empty: grapple, or hold a Spellbook to cast."], 2 * PLAYERS),
    ("jewelry", "Jewelry", "Swap: free, once per turn", ["Rings, amulets, circlets, cloaks, gloves, boots."], PLAYERS),
    ("item", "Item", "Swap: free · Spellbook: 1 action", ["A Spellbook, a Recipe, a Purse, or up to 3 identical Consumables."], 2 * PLAYERS),
    ("aspect", "Aspect", "Swap: long rest", ["A Trait, Technique, Knack, Divine, Glamour or Nature."], 4 * PLAYERS),  # 3 each + 1 milestone
    ("hand", "Third Hand", "Swap: free interaction", ["Extra Gear Slot: a spectral arm, a familiar, a living tail.", "Never lost, traded or stored."], 1),
    ("jewelry", "Second Jewel", "Swap: free, once per turn", ["Extra Gear Slot.", "Never lost, traded or stored."], 1),
    ("item", "Great Backpack", "Swap: free · Spellbook: 1 action", ["Extra Gear Slot.", "Never lost, traded or stored."], 1),
    ("shard", "Shard", "Pack (3 at most) or Party Stash", ["Holds one Aspect or Core, or nothing.", "**Capture:** 1 action · **Absorb:** long rest · **Release:** free"], 5 * PLAYERS),  # 3 each + 2 each in the Stash
]

STARTER_LIST = {  # GM's Guide 4.2 table, generated from the cards above
    "Armor": [c["name"] for c in ARMOR if c["group"] == "starter"],
    "Hands": [c["name"] for c in HANDS if c["group"] == "starter"],
    "Jewelry": [c["name"] for c in JEWELRY if c["group"] == "starter"],
    "Items": [CONJURER["cover"]["name"]] + [c["name"] for c in ITEMS if c["group"] == "starter"],
    "Aspects": [c["name"] for c in ASPECTS if c["group"] == "starter"] + [d["cover"]["name"] for d in (REPERTOIRE, LITANY, REMEMBRANCE)],
}

# ---------- card IDs (P 12.1): type letter, Rank, number in order of appearance ----------
# Add new cards at the end of their type and Rank so existing IDs never change.
TYPE_LETTER = {"Core": "C", "Armor": "A", "Weapon": "W", "Shield": "S", "Instrument": "M", "Jewelry": "J",
               "Consumable": "P", "Recipe": "R", "Purse": "U", "Spellbook": "B", "Trait": "T", "Technique": "Q",
               "Knack": "K", "Divine": "D", "Glamour": "G", "Nature": "N"}
CARDS = CORES + ARMOR + HANDS + JEWELRY + ITEMS + ASPECTS + [d["cover"] for d in DECKS]

# ---------- mechanics of cards (SPEC 2.1): card name → list of Powers; ids are added by tools/export_sim.py ----------
TWO_SHIELD_MOD = [dict(mod="def", n=2, defs=["targeted"], next=True)]  # +2 to the Defense the attack targets, this attack only
CARD_FX = {
    # weapon riders
    "Finesse Blade": [dict(use="trigger", on="hit", do=[dict(mod="attack", n=-2, next=True, until="startSourceTurn")])],
    "Spellguard Staff": [dict(use="passive", castingHand=True)],
    "Greatclub": [dict(use="trigger", on="crit", do=[dict(cond="Prone")])],
    "Gladius": [dict(use="passive", hook="close_order", params=dict(dmg="1d4"))],
    "Boarspear": [dict(use="trigger", on="opportunity", hook="brace", params=dict(dmg="1d8"))],
    "Pilum": [dict(use="trigger", on="hit", hook="pierce")],
    # gear
    "Traveler's Lute": [dict(use="passive", extraResolve=1, anthemReach=60, params=dict(default=30))],
    "Holy Amulet": [dict(use="passive", extraResolve=1, cueReach=90, params=dict(default=60))],
    "Ring of Warding": [dict(use="reaction", uses="2/SR", on="hitSelf", target="self", do=TWO_SHIELD_MOD)],
    "Ring of Sparks": [dict(use="reaction", uses="1/SR", on="meleeHitSelf5", target="enemy",
                            do=[dict(dmg="2d6", type="Lightning")])],
    "Boots of the Long Stride": [dict(use="bonus", uses="1/SR", target="self", do=[dict(dash=True)])],
    "Potion of Healing": [dict(use="bonus", reach=5, target="creature", do=[dict(heal="2d4+2")])],
    "Greater Potion of Healing": [dict(use="bonus", reach=5, target="creature", do=[dict(heal="4d4+4")])],
    "Pocket Sand": [dict(use="bonus", reach=5, target="enemy", atk=dict(abil=["DEX", "WIL"], hit=2, vs="DEX"),
                         do=[dict(mod="attack", n=-2, until="endTargetTurn")])],
    "Alchemist's Fire Recipe": [dict(use="bonus", reach=30, target="point", area=dict(shape="sphere", size=5),
                                     atk=dict(abil=["DEX", "INT"], hit=3, vs="DEX"), half=True,
                                     do=[dict(dmg="2d6", type="Fire")], tags=["fire"])],
    # aspects
    "Iron Will": [dict(use="passive", defVs=dict(WIL=2), tags=["fear", "mind control"])],
    "Stone Blood": [dict(use="passive", defVs=dict(STR=2), tags=["poison"])],
    "Clear Mind": [dict(use="passive", defVs=dict(INT=2), tags=["illusion", "confusion"])],
    "Cleave": [dict(use="trigger", uses="1/SR", on="meleeDrop", do=[dict(attack="melee")])],
    "Steady Aim": [dict(use="bonus", uses="2/SR", target="self", params=dict(ranged=True),
                        do=[dict(mod="attack", n=2, next=True, until="endThisTurn")])],
    "Shield Bash": [dict(use="bonus", uses="1/SR", need=["shield", "attackAction"], reach=5, target="enemy",
                         do=[dict(shove=True)])],
    "Battle Hymn": [dict(use="trigger", uses="2/SR", on="weaponHit", target="allies", count=3, reach=30, need=VOICE,
                         do=[dict(mod="attack", n=2, next=True, until="endSourceTurn")])],
    "Rallying Cry": [dict(kind="Anthem", use="bonus", uses="1/SR", reach=30, target="allies", count=3, need=VOICE,
                          dur="1 minute", do=[dict(mod="attack", n=2, until="dur")])],
    "Shield Wall": [dict(use="reaction", uses="1/SR", on="hitAlly5", need=["shield"], target="ally", do=TWO_SHIELD_MOD)],
    "Twin Strike": [dict(use="passive", attacks=2)],
    "Second Wind": [dict(use="bonus", uses="1/SR", target="self", do=[dict(heal="1d10+3")])],
    "Night Eyes": [dict(use="passive", darkvision=60)],
    "Pack Hunter": [dict(use="trigger", uses="1/SR", on="hitEngaged", do=[dict(cond="Prone")])],
    "Slippery": [dict(use="bonus", uses="2/SR", target="self", do=[dict(move="safe", ft="half")])],
    "Hedge Witch": [dict(use="passive", extraSp=1)],
}
for _name in CARD_FX:
    assert _name in {c["name"] for c in CARDS}, _name
for _c in CARDS:
    _c["fx"] = CARD_FX.get(_c["name"], [])

_count = {}
for _c in CARDS:
    _key = (TYPE_LETTER[_c["kw"].split(" · ")[0]], _c["rank"])
    _count[_key] = _count.get(_key, 0) + 1
    _c["id"] = f"{_key[0]}-{_key[1]}-{_count[_key]:02d}"
BY_NAME = {c["name"]: c for c in CARDS}
