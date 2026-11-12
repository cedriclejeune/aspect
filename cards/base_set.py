"""The base set: every card and Slot frame for a 4-player test game.

Built into rules/Bearers-Base-Set.pdf by tools/build_cards.py.
Strip keys: STR DEX INT WIL (modifiers), STRd DEXd INTd WILd (Defenses), HP, SPD.
Text uses **bold** and *italic*; each list item is one paragraph.
"""
import re

PLAYERS = 4


def card(name, rank, kind, kw, text=(), strip=None, copies=1, group="starter", sym=None, **extra):
    """sym: the abilities whose symbols it prints (P 3.1); a Calling with one of them can equip it. None = all four."""
    return dict(name=name, rank=rank, kind=kind, kw=kw, text=list(text), strip=strip or {},
                copies=copies, group=group, sym=list(sym or ["STR", "DEX", "INT", "WIL"]), **extra)


ABILS = ["STR", "DEX", "INT", "WIL"]
ALL = ABILS  # all four symbols lit: anyone can equip it (P 3.1)


def body(mods, hp, spd):
    """A body's own ten values (a Calling, a Form, a foe): modifiers, Defenses (10 + modifier), HP and Speed."""
    s, d, i, w = mods
    return {"STR": f"{s:+d}", "DEX": f"{d:+d}", "INT": f"{i:+d}", "WIL": f"{w:+d}",
            "STRd": str(10 + s), "DEXd": str(10 + d), "INTd": str(10 + i), "WILd": str(10 + w),
            "HP": str(hp), "SPD": str(spd)}


def calling(name, pair, hp, spd, *perks):
    """A Calling (P 2.4): +2 in its two abilities, +0 in the others, Medium, its own HP and Speed, and its perks.
    Every perk scales with both of the Calling's abilities (DESIGN 4): uses, dice and distances are half an ability,
    rounded down (*½ WIL*), bonuses the whole modifier (*+STR*); a Calling with two perks splits them between its two."""
    return card(name, "", "calling", "Calling", list(perks), body([2 if a in pair else 0 for a in ABILS], hp, spd), sym=list(pair))


CALLINGS = [
    calling("Duelist", ("STR", "DEX"), 12, 35,
            "**Footwork:** once per turn, after you hit with a melee attack, move 5 ft × ½ DEX. This movement doesn't provoke opportunity attacks.",
            "**Riposte (½ STR/S.R.):** reaction, when a melee attack misses you: make one melee weapon attack against the attacker."),
    calling("Templar", ("STR", "WIL"), 14, 30,
            "**Oath (½ WIL/S.R.):** reaction, when an attack hits an ally within 5 ft: you take its damage instead, reduced by 2 × STR."),
    calling("Spellblade", ("STR", "INT"), 13, 30,
            "**Battle Caster:** a weapon you hold counts as an empty Hand for casting from a Spellbook.",
            "**Spell Strike (½ STR/S.R.):** when you hit with a melee weapon attack: +INT damage."),
    calling("Infiltrator", ("DEX", "INT"), 10, 35, "**Unseen:** your checks to sneak, pick locks and spot traps add both DEX and INT."),
    calling("Performer", ("DEX", "WIL"), 10, 35,
            "**Presence:** your checks to perform, persuade and deceive add both DEX and WIL."),
    calling("Sage", ("INT", "WIL"), 9, 35, "**Learned:** ½ INT extra spell points. Your checks to recall lore add both INT and WIL."),
    # the second Calling of each pair: same +2 / +2, another perk, HP and Speed
    calling("Brawler", ("STR", "DEX"), 14, 30,
            "**Scrapper:** +STR to hit with Grapples and Shoves.",
            "**Slip Free:** your Escape attacks add 2 × DEX instead of STR or DEX."),
    calling("Patriot", ("STR", "WIL"), 12, 35,
            "**Righteous Fury (½ WIL/S.R.):** when you hit with a weapon attack: +½ STR d6 Radiant damage."),
    calling("Tactician", ("STR", "INT"), 12, 35,
            "**Command (½ STR/S.R.):** action. An ally within 30 ft who can hear you takes the Attack action at once, with +INT to hit."),
    calling("Ranger", ("DEX", "INT"), 11, 35,
            "**Quarry (½ INT/S.R.):** when you hit a creature with a ranged attack, it's marked: you and your allies have +½ DEX on attacks against it until the start of your next turn."),
    calling("Trickster", ("DEX", "WIL"), 9, 35,
            "**Sure Thing:** on your checks to sneak, pick locks, pick pockets and disarm traps, a d20 that shows less than 10 counts as a 10. When you hit a creature that can't see you: +½ DEX or ½ WIL d6 damage, whichever is higher."),
    calling("Hermit", ("INT", "WIL"), 11, 30, "**Solitude:** ½ WIL extra Resolve. Your checks to forage and endure add both INT and WIL."),
]


ARMOR = [
    # HP by weight and Rank (DESIGN 4): light +2/+4, medium +4/+8, heavy +6/+12 at Rank I/II
    card("Leather", "I", "gear", "Armor", [], {"STRd": "+2", "DEXd": "+1", "HP": "+2", "SPD": "+5"}, copies=2),
    card("Mail", "I", "gear", "Armor", [], {"STRd": "+3", "HP": "+4"}, copies=2, sym=["STR", "DEX"]),
    card("Plate", "II", "gear", "Armor · Noisy 3", [], {"STRd": "+4", "HP": "+12", "SPD": "−10"}, group="loot", sym=["STR"]),
]


def weapon_atk(dice, kw, attack, sym, dtype="Physical"):
    """Structured attack of a weapon, read from its own args (SPEC 2, WeaponAtk)."""
    parts = kw.split(" · ")
    pair = lambda key: next(([int(a), int(b)] for p in parts if p.startswith(key) for a, b in [re.findall(r"\d+", p)]), None)
    two = re.search(r"Versatile \((\d+d\d+)\)", kw)
    ranged = pair("Range")
    return dict(hit=int(attack.replace("−", "-")), dice=dice.split(" / ")[0], two=two[1] if two else None,
                abil=list(sym), type=dtype, brutal="Brutal" in parts, crushing="Crushing" in parts, flurry="Flurry" in parts,
                light="Light" in parts, heavy="Heavy" in parts, reach="Reach" in parts,
                twoHanded="Two-Handed" in parts, loading="Loading" in parts, thrown=pair("Thrown"), range=ranged)


def weapon(name, abil, dice, kw, effect=None, attack="+2", rank="I", copies=1, group="starter", dtype="Physical", sym=None):
    """abil is the weapon's roll: you attack and deal damage with the higher of them (STR / DEX; INT / WIL for staves and wands).
    A basic (starter) weapon lights all four symbols so anyone can wield it; a loot weapon lights only its abil (DESIGN 4).
    sym overrides that (the Spellguard Staff is a starter that lights only INT · WIL).
    The range of a Range or Thrown weapon is printed in its attack line, so the card doesn't print that keyword (DESIGN 4)."""
    reach = next((f"{p.split()[0].lower()} {p.split()[1]} ft, " for p in kw.split(" · ") if p.startswith(("Range ", "Thrown "))), "")
    text = [f"{attack} to hit, {reach}{dice} + {' or '.join(abil)} {dtype}." + (f" {effect}" if effect else "")]
    sym = sym or (ALL if group == "starter" else abil)
    return card(name, rank, "gear", "Weapon" + (f" · {kw}" if kw else ""), text, copies=copies, group=group, sym=sym,
                atk=weapon_atk(dice, kw, attack, abil, dtype))


HANDS = [
    card("Shield", "I", "gear", "Shield", ["Takes one Hand."], {"STRd": "+2", "DEXd": "+2"}, copies=2, sym=["STR", "WIL"]),
    weapon("Dagger", ["DEX"], "1d4", "Light · Thrown 20/60 · Flurry"),
    weapon("Shortsword", ["STR", "DEX"], "1d6", "Light · Flurry"),
    weapon("Handaxe", ["STR", "DEX"], "1d6", "Light · Thrown 20/60"),
    weapon("Finesse Blade", ["DEX"], "1d6", "", "**Sap:** when you hit, the target has −2 on its next attack roll before the start of your next turn."),
    weapon("Longsword", ["STR"], "1d8 / 1d10", "Versatile (1d10)"),
    weapon("Battleaxe", ["STR", "DEX"], "1d8 / 1d10", "Versatile (1d10)"),
    weapon("Greatsword", ["STR"], "2d6", "Heavy · Two-Handed"),
    weapon("Glaive", ["STR"], "1d10", "Heavy · Reach · Two-Handed"),
    weapon("Longbow", ["DEX"], "1d8", "Range 150/600 · Two-Handed"),
    weapon("Sling", ["DEX"], "1d6", "Light · Range 30/120"),
    weapon("Javelins", ["STR", "DEX"], "1d6", "Thrown 30/120"),
    weapon("Spellguard Staff", ["INT", "WIL"], "1d6 / 1d8", "Versatile (1d8)", "While you hold it, it counts as an empty Hand for casting from a Spellbook.", sym=["INT", "WIL"]),
    card("Traveler's Lute", "I", "gear", "Instrument · Focus", ["1 extra Resolve (short rest).", "Your Anthems reach 60 ft instead of 30 ft."], sym=["WIL"]),
    weapon("Greatclub", ["STR"], "1d10", "Heavy · Two-Handed · Crushing", group="loot"),
    weapon("Gladius", ["STR", "DEX"], "1d6", "Light", "**Close Order:** +1d4 damage while an ally is engaged with the same creature.", group="loot"),
    weapon("Boarspear", ["STR"], "1d8 / 1d10", "Versatile (1d10)", "**Brace:** your opportunity attacks with it deal +1d8 damage.", attack="+3", rank="II", group="loot"),
    weapon("Pilum", ["STR", "DEX"], "1d6", "Thrown 30/120", "**Pierce:** on a hit, a Shield the target holds gives no bonus until it spends an action to pull the pilum free.", attack="+3", rank="II", group="loot"),
    weapon("Shortbow", ["DEX"], "1d6", "Range 80/320 · Two-Handed", group="loot"),
    weapon("Greataxe", ["STR"], "1d12", "Heavy · Two-Handed · Brutal", group="loot"),
    # identity cards (DESIGN 4, symbol parity): one symbol each, like the heavy weapons for STR
    weapon("Fine Bow", ["DEX"], "1d10", "Range 150/600 · Two-Handed", group="loot"),
    weapon("Wand", ["INT"], "1d8", "Range 60/120", group="loot", dtype="Lightning"),
]

JEWELRY = [
    card("Ring of Warding", "I", "gear", "Jewelry", ["**Reaction (2/S.R.)**, when an attack hits you: +2 to the targeted Defense against that attack, possibly turning it into a miss."]),
    card("Guild Signet", "I", "gear", "Jewelry", ["**Action (1/L.R.)**, in a settlement where the guild operates: a contact finds you within 1 hour. They share one fact the guild would know, or hide you for a night."]),
    card("Holy Amulet", "I", "gear", "Jewelry · Focus", ["1 extra Resolve (short rest).", "Your Cues reach 90 ft instead of 60 ft."], group="loot", sym=["WIL"]),
    card("Boots of the Long Stride", "I", "gear", "Jewelry", ["**Reaction (1/S.R.):** Move."]),
    card("Ring of Sparks", "II", "gear", "Jewelry", ["**Reaction (1/S.R.)**, when a creature within 5 ft hits you: it takes 2d6 Lightning."], group="loot"),
    card("Dancer's Bells", "I", "gear", "Jewelry · Focus", ["1 extra Resolve (short rest).", "Your Dirges reach 90 ft instead of 60 ft."], sym=["WIL"]),
]

ITEMS = [
    card("Potion of Healing", "I", "gear", "Consumable", ["**Action:** drink it, or give it to a creature within 5 ft. It regains 2d4 + 2 HP."], copies=6),
    card("Coin Pouch", "I", "gear", "Container", ["Holds up to **100 gp**."], copies=PLAYERS),
    card("Writ of Favor", "I", "gear", "Consumable", ["A sealed letter from a noble house, a guild or a temple. Show it to one of its members: they grant one reasonable request (shelter, an audience, safe passage, a loan up to 100 gp)."]),
    card("Greater Potion of Healing", "II", "gear", "Consumable", ["**Action:** drink it, or give it to a creature within 5 ft. It regains 4d4 + 4 HP."], copies=2, group="loot"),
    card("Restorative Salve", "II", "gear", "Consumable", ["**Action:** spread it on a creature within 5 ft. Heal one of its Wounds."], group="loot"),
    card("Pocket Sand", "I", "gear", "Consumable", ["**Reaction:** throw it at a creature within 5 ft. Attack (DEX or WIL + 2) against its DEX Defense: on a hit, it has −2 on attacks until the end of its next turn."], group="loot"),
    card("Alchemist's Fire Recipe", "II", "gear", "Recipe · 3 flasks", ["**Reaction:** throw a flask up to 30 ft. Make one attack (DEX or INT + 3) against the DEX Defense of each creature within 5 ft of the impact: 2d6 Fire on a hit, half on a miss."], group="loot", uses=3),
    card("Runestone Bandolier", "I", "gear", "Container", ["While it's in your Pack, your Pack holds up to 5 Runestones instead of 3."]),
]


def domain(name, acts, rank="I", bonus="+2", group="starter", sym=None):
    """A Domain (GM 4.3): one bonus on the checks of four activities. A Rune's kind stays "aspect" in the data (sim/)."""
    return card(name, rank, "aspect", "Domain", [f"{bonus} on checks to {acts}."], group=group, sym=sym)


ASPECTS = [
    card("Springheel", "I", "aspect", "Trait", ["Your jump distances are doubled, and you never need a running start."], {"HP": "+2"}, sym=["STR", "DEX"]),
    card("Stone Blood", "I", "aspect", "Trait", ["+2 STR Defense against poison and disease."], {"HP": "+2"}, sym=["STR", "INT"]),
    card("Iron Will", "I", "aspect", "Trait", ["+2 WIL Defense against fear and mind control."], {"HP": "+2"}, sym=["INT", "WIL"]),
    card("Clear Mind", "I", "aspect", "Trait", ["+2 INT Defense against illusions and confusion."], {"HP": "+2"}, sym=["INT", "WIL"]),
    card("Cleave", "I", "aspect", "Technique", ["**1/S.R.**, when your melee attack drops a creature to 0 HP: make one melee attack against another creature within your reach."], sym=["STR", "DEX"]),
    card("Steady Aim", "I", "aspect", "Technique", ["**Reaction (2/S.R.):** your next ranged attack this turn has +2 to hit."], sym=["DEX", "INT"]),
    card("Shield Bash", "I", "aspect", "Technique", ["**Reaction (1/S.R.)**, when you take the Attack action while holding a Shield: Shove a creature within 5 ft."], sym=["STR", "WIL"]),
    card("Battle Hymn", "I", "aspect", "Technique", ["**2/S.R.**, when you hit with a weapon attack: up to 3 allies within 30 ft who can hear you have +2 to STR and DEX Defense until the start of your next turn."], sym=["DEX", "WIL"]),
    card("Rallying Cry", "I", "aspect", "Technique · Anthem", ["*Rally* as a loose Anthem.", "**Action (1/S.R.):** Duration 1 minute. Up to 3 allies within 30 ft have +2 on attacks."], sym=["STR", "WIL"]),
    card("Shield Wall", "I", "aspect", "Technique", ["**Reaction (1/S.R.)**, when an attack hits an ally within 5 ft while you hold a Shield: +2 to the targeted Defense against that attack, possibly turning it into a miss."], group="loot", sym=["STR", "WIL"]),
    domain("Larceny", "sneak, climb or pick locks", sym=["DEX", "INT"]),
    domain("Minstrel", "persuade, haggle, gather rumors or perform", sym=["INT", "WIL"]),
    domain("Navigation", "swim, climb, navigate or gather rumors", sym=["STR", "INT"]),
    domain("Backstreets", "pick pockets, sneak, read intentions or gather rumors", sym=["DEX", "WIL"]),
    domain("Hunt", "track, notice, sneak or handle animals", sym=["DEX", "INT"]),
    domain("Healing", "treat wounds, recall lore, read intentions or persuade", sym=["INT", "WIL"]),
    domain("Tavern", "read intentions, gather rumors, intimidate or lift", sym=["INT", "WIL"]),
    domain("Forge", "lift, break, haggle or recall lore", sym=["STR", "INT"]),
    domain("Peaks", "climb, endure, navigate or balance", sym=["DEX", "INT"]),
    # loot
    card("Twin Strike", "II", "aspect", "Technique", ["Once per turn, when you take the Attack action, make one extra attack."], group="loot", sym=["STR", "DEX"]),
    card("Second Wind", "II", "aspect", "Trait", ["**Action (1/S.R.):** regain 1d10 + 3 HP."], {"HP": "+4"}, group="loot", sym=["STR", "WIL"]),
    card("Sinew", "II", "aspect", "Trait", [], {"HP": "+4", "STR": "+1", "STRd": "+1", "SPD": "+5"}, group="loot", sym=["STR", "DEX"]),
    card("Night Eyes", "II", "aspect", "Trait · Darkvision 120", [], {"HP": "+4"}, group="loot", sym=["DEX", "INT"]),
    card("Bravado", "II", "aspect", "Trait", ["+3 on checks to intimidate, endure, haggle or gather rumors."], {"HP": "+4", "STR": "+1", "STRd": "+1"}, group="loot", sym=["STR", "WIL"]),
    card("Tumbling", "II", "aspect", "Trait", ["+3 on checks to tumble, balance, jump or perform."], {"HP": "+4", "DEX": "+1", "DEXd": "+1"}, group="loot", sym=["DEX", "WIL"]),
    card("Herbalist", "II", "aspect", "Trait", ["1 extra spell point (long rest).", "+3 on checks to handle animals, recall lore, treat wounds or deceive."], {"HP": "+4"}, group="loot", sym=["INT", "WIL"]),
    card("Sweeping Blow", "II", "aspect", "Technique", ["**1/S.R.**, when you take the Attack action with a Heavy or Reach weapon: make one attack roll against each enemy within your reach instead. Half damage on a miss."], group="loot", sym=["STR"]),
    card("Defiance", "II", "aspect", "Trait", ["**1/S.R.**, when damage drops you to 0 HP without killing you outright: you drop to 1 HP instead."], {"HP": "+4"}, group="loot", sym=["STR", "WIL"]),
    card("Wolfpack", "II", "aspect", "Trait", ["**1/S.R.**, when you hit a creature one of your allies is engaged with: it falls Prone."], {"HP": "+4"}, group="loot", sym=["DEX", "INT"]),
    # Rank I loot Traits and Domains that humanoid foes drop (DESIGN 4: species has no card)
    card("Grit", "I", "aspect", "Trait", ["**Stubborn (1/S.R.):** when you fail a check, add +2 to that roll, possibly turning it into a success."], {"HP": "+2"}, group="loot"),
    card("Dusk Eyes", "I", "aspect", "Trait · Darkvision 60", [], {"HP": "+2"}, group="loot", sym=["DEX", "INT"]),
    card("Bedrock", "I", "aspect", "Trait", ["+2 STR Defense against poison, Shoves and Grapples."], {"HP": "+2"}, group="loot", sym=["STR", "WIL"]),
    card("Luck", "I", "aspect", "Trait", ["**Lucky (1/S.R.):** when you roll a 1 on a d20, reroll it."], {"HP": "+2"}, group="loot", sym=["DEX", "WIL"]),
    domain("Campaign", "intimidate, endure, lift or march", group="loot", sym=["STR", "WIL"]),
    domain("Discipline", "march, navigate, stand firm or read intentions", group="loot", sym=["INT", "WIL"]),
]


# A Rune card prints "Rune of" in small above its name (DESIGN 1b); these few take "the".
RUNE_OF_THE = ['Minstrel', 'Herbalist', 'Wolfpack']


def rune_of(name):
    return "Rune of the" if name in RUNE_OF_THE else "Rune of"


# ---------- Wounds (P 7.6): one shared deck, drawn at random at each fall to 0 HP ----------
def wound(name, text=(), strip=None, blocks=None, fx=()):
    """fx: what the sim plays of its penalty (sim/cards.js); checks and rests aren't simulated."""
    kw = f"Wound · Crippling · {blocks}" if blocks else "Wound"
    text = list(text) or [f"Blocks one of your **{blocks} Slots** until it heals."]
    return card(name, "", "wound", kw, text, strip, group="wound", fx=list(fx))


WOUNDS = [
    # light: one penalty
    wound("Twisted Ankle", ["You hobble."], {"SPD": "−10"}),
    wound("Bruised Ribs", ["Every breath hurts."], {"STRd": "−2"}),
    wound("Pulled Muscle", ["You can't twist away in time."], {"DEXd": "−2"}),
    wound("Concussion", ["The world swims a little."], {"INTd": "−2"}),
    wound("Shaken", ["You flinch at every shadow."], {"WILd": "−2"}),
    wound("Deep Cut", ["Stitched, not healed."], {"HP": "−5"}),
    wound("Black Eye", ["−2 on ranged attacks and on checks to notice."], fx=[dict(use="passive", hitMod=-2, only="ranged")]),
    wound("Broken Nose", ["−2 on WIL checks."]),
    wound("Torn Tendon", ["−2 on checks to climb, jump or swim."]),
    wound("Weak Grip", ["−2 on melee attacks."], fx=[dict(use="passive", hitMod=-2, only="melee")]),
    wound("Cracked Jaw", ["1 less Resolve and 1 less spell point."], fx=[dict(use="passive", extraSp=-1, extraResolve=-1)]),
    wound("Nightmares", ["A short rest heals only a quarter of your missing HP (rounded up)."]),
    # Crippling: blocks a Gear Slot
    wound("Broken Arm", blocks="Hand"),
    wound("Broken Fingers", blocks="Hand"),
    wound("Swollen Hand", blocks="Jewelry"),
    wound("Cracked Ribs", blocks="Item"),
    wound("Wrenched Back", blocks="Item"),
    # grave
    wound("Shattered Knee", ["You may never run the same again."], {"SPD": "−10", "DEXd": "−2"}),
    wound("Skull Fracture", ["−2 on INT checks."], {"INTd": "−2", "WILd": "−2"}),
    wound("Internal Bleeding", ["You lose blood every time you move too fast."], {"HP": "−10"}),
]


# ---------- decks: a cover card, then one card per spell or power ----------
# Every WIL deck has the same structure, whatever its type (P 10.6, DESIGN 3): a cover that prints Attack, Resolve
# and one flavor line, then its powers. The type only decides which powers it holds (Litany, Repertoire: Anthem, Dirge,
# Cue, Mend; Instinct: Form, Mend). All of them need the voice but a Form.
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
    "Misty Step": dict(use="reaction", target="self", do=[dict(move="teleport", ft=30)]),
    "Web": dict(use="action", reach=60, target="point", area=dict(shape="cube", size=20), atk=dict(abil="deck", vs="DEX"),
                zone=dict(terrain="difficult", on=["enter"], burns=True, burnFt=5), do=[dict(cond="Restrained", until="targetTurns2")],
                dur="1 hour"),
    "Jeer": dict(use="action", reach=60, target="enemy", need=VOICE, atk=dict(abil="deck", vs="WIL"),
                 do=[dict(mod="attack", n=-2, next=True, until="endTargetTurn")]),
    "Rally": dict(use="action", reach=30, target="allies", count=3, need=VOICE, dur="1 minute",
                  do=[dict(mod="attack", n=2, until="dur")]),
    "Hold the Line": dict(use="action", reach=30, target="allies", need=VOICE, dur="1 minute",
                          do=[dict(mod="def", n=2, defs=["STR", "DEX"], until="dur")]),
    "Cutting Words": dict(use="reaction", on="rollNear", reach=60, target="enemy", need=VOICE,
                          do=[dict(mod="roll", n=-2)], params=dict(rollKinds=["attack", "check"])),
    "Steady Now": dict(use="reaction", on="rollNear", reach=60, target="ally", need=VOICE,
                       do=[dict(mod="roll", n=2)], params=dict(orDefense=True)),
    "Dread": dict(use="action", reach=60, target="enemy", need=VOICE, atk=dict(abil="deck", vs="WIL"),
                  do=[dict(cond="Frightened", until="targetTurns2")], tags=["fear"]),
    "Guidance": dict(use="reaction", on="rollNear", reach=60, target="ally", need=VOICE,
                     do=[dict(mod="roll", dice="1d4")], params=dict(rollKinds=["check"])),
    "Bless": dict(use="action", reach=30, target="allies", count=3, need=VOICE, dur="1 minute",
                  do=[dict(mod="attack", dice="1d4", until="dur")]),
    "Bane": dict(use="action", reach=60, target="enemy", need=VOICE, atk=dict(abil="deck", vs="WIL"),
                 dur="1 minute", do=[dict(mod="attack", dice="-1d4", until="dur")]),
    "Twist Fate": dict(use="reaction", on="rollNear", reach=60, target="creature", need=VOICE,
                       do=[dict(reroll=True)], params=dict(rollKinds=["attack", "check"])),
    "Healing Word": dict(use="action", reach=60, target="creature", need=VOICE, do=[dict(heal="2d4+WIL")]),
    "Rousing Verse": dict(use="action", reach=60, target="creature", need=VOICE, do=[dict(heal="2d4+WIL")]),
    "Cure Wounds": dict(use="action", reach=5, target="creature", need=VOICE, do=[dict(heal="2d8+WIL")]),
    "Mossbalm": dict(use="action", reach=5, target="creature", need=VOICE, do=[dict(heal="2d8+WIL")]),
    "Hawk": dict(use="action", target="self", form=dict(
        strip={"STR": -2, "DEX": 3, "STRd": 8, "DEXd": 13, "HP": 4, "SPD": 10}, size="Tiny", fly=60, climb=0,
        weapon=dict(name="Talons", hit=2, dice="1d4", abil=["DEX"], type="Physical"))),
    "Wolf": dict(use="action", target="self", form=dict(
        strip={"STR": 1, "DEX": 3, "STRd": 11, "DEXd": 13, "HP": 8, "SPD": 40}, size="Medium", fly=0, climb=0,
        weapon=dict(name="Bite", hit=2, dice="1d6", abil=["DEX"], type="Physical"))),
    "Bear": dict(use="action", target="self", form=dict(
        strip={"STR": 3, "DEX": 1, "STRd": 15, "DEXd": 11, "HP": 12, "SPD": 30}, size="Large", fly=0, climb=30,
        weapon=dict(name="Claws", hit=2, dice="1d8", abil=["STR"], type="Physical"))),
}


def spell(name, level, text, kw):
    cost = 0 if level == "Cantrip" else int(level[0])
    fx = dict(name=name, kind="Cantrip" if cost == 0 else "Spell", cost=cost, **POWER_FX[name])
    return dict(name=name, level=level, cost=cost, text=list(text), kw=kw, strip={}, fx=fx)


CONJURER = dict(
    cover=card("Conjurer's Book", "I", "gear", "Spellbook", [
        "Spell attack: **INT + 2**", "Spell points: **+2** (long rest)", "Max spell level: **2nd**",
        "Casting needs an empty Hand."], sym=["INT"]),
    color="gear", stats=dict(kind="spellbook", atk=2, sp=2, maxLevel=2),
    cards=[
        spell("Fire Bolt", "Cantrip", ["**Action**, range 120 ft.", "Spell attack against DEX Defense: **1d10 Fire**. A flammable object it hits catches fire."], "Cantrip · Targets DEX · Range 120"),
        spell("Mage Hand", "Cantrip", ["**Action**, range 30 ft, Duration 1 minute.", "A spectral hand lifts, carries or works an object up to 10 lb. It can't attack. Move it with your reaction."], "Cantrip · Duration 1 minute"),
        spell("Magic Missile", "1st", ["**Action**, range 120 ft.", "Three darts at one to three creatures. One spell attack against the DEX Defense of each target: **1d4 + 1 Radiant** per dart on a hit, half on a miss.", "**Upcast:** +1 dart per level above 1st."], "Spell · Targets DEX · Range 120"),
        spell("Shield", "1st", ["**Reaction**, when an attack hits you.", "+5 to your STR and DEX Defense until the start of your next turn, against the triggering attack too."], "Spell · Duration 1 round"),
        spell("Grease", "1st", ["**Action**, range 60 ft, Duration 1 minute.", "A 10-ft cube of slick grease: difficult terrain. Spell attack against the DEX Defense of each creature in it, and of each one that enters it or ends its turn there: on a hit, it falls **Prone**."], "Spell · Cube 10 · Targets DEX"),
        spell("Misty Step", "2nd", ["**Reaction.**", "Teleport up to 30 ft to an unoccupied space you can see."], "Spell"),
        spell("Web", "2nd", ["**Action**, range 60 ft, Duration 1 hour.", "A 20-ft cube of webs: difficult terrain. Spell attack against the DEX Defense of each creature in it, and of each one that enters it: on a hit, it is **Restrained** for 2 turns. Fire burns a 5-ft square away each round."], "Spell · Cube 20 · Targets DEX · Restrained"),
    ],
)


def power(name, kind, cost, text, strip=None):
    fx = dict(name=name, kind=kind, cost=cost, **POWER_FX[name])
    return dict(name=name, level=kind, cost=cost, text=list(text), kw=kind, strip=strip or {}, fx=fx)


REPERTOIRE = dict(
    cover=card("Wanderer's Repertoire", "I", "aspect", "Glamour", [
        "Attack: **WIL + 2**", "Resolve: **+3** (short rest)", "Songs, poems and dances."], sym=["WIL"]),
    color="aspect", stats=dict(kind="glamour", atk=2, resolve=3),
    cards=[
        power("Jeer", "Dirge", 0, ["**Action.** Attack against WIL Defense: until the end of the target's next turn, it has −2 on its next attack."]),
        power("Rally", "Anthem", 1, ["**Action**, Duration 1 minute.", "Up to 3 allies within 30 ft have +2 on attacks."]),
        power("Hold the Line", "Anthem", 1, ["**Action**, Duration 1 minute.", "Allies within 30 ft have +2 to STR and DEX Defense."]),
        power("Cutting Words", "Cue", 1, ["**Reaction**, after a creature within 60 ft rolls.", "−2 to an enemy's attack roll or check."]),
        power("Steady Now", "Cue", 1, ["**Reaction**, after a creature within 60 ft rolls.", "+2 to an ally's roll, or to the Defense an attack targets."]),
        power("Dread", "Dirge", 2, ["**Action.** Attack against WIL Defense: the target is **Frightened** of you for 2 turns."]),
        power("Rousing Verse", "Mend", 2, ["**Action**, range 60 ft.", "A creature regains 2d4 + WIL HP."]),
    ],
)

LITANY = dict(
    cover=card("Acolyte's Litany", "I", "aspect", "Divine", [
        "Attack: **WIL + 2**", "Resolve: **+3** (short rest)", "Prayers."], group="loot", sym=["WIL"]),
    color="aspect", stats=dict(kind="divine", atk=2, resolve=3),
    cards=[
        power("Guidance", "Cue", 0, ["**Reaction**, after an ally within 60 ft rolls a check.", "Add 1d4 to it."]),
        power("Bless", "Anthem", 1, ["**Action**, Duration 1 minute.", "Up to 3 allies within 30 ft add 1d4 to their attack rolls."]),
        power("Bane", "Dirge", 1, ["**Action**, Duration 1 minute.", "Attack against WIL Defense: the target subtracts 1d4 from its attack rolls."]),
        power("Twist Fate", "Cue", 1, ["**Reaction**, after a creature within 60 ft rolls.", "**Reroll:** make it reroll an attack roll or a check."]),
        power("Healing Word", "Mend", 2, ["**Action**, range 60 ft.", "A creature regains 2d4 + WIL HP."]),
        power("Cure Wounds", "Mend", 2, ["**Action**, touch.", "A creature regains 2d8 + WIL HP."]),
    ],
)

def form(s, d, hp, spd, hide=0):
    """A Form's strip (P 10.7): its own STR, DEX, HP and Speed, printed like a Calling."""
    return {"STR": f"{s:+d}".replace("-", "−"), "DEX": f"{d:+d}".replace("-", "−"),
            "STRd": str(10 + s + hide), "DEXd": str(10 + d), "HP": str(hp), "SPD": str(spd)}


INSTINCT = dict(
    cover=card("Wildheart's Instinct", "I", "aspect", "Nature", [
        "Attack: **WIL + 2**", "Resolve: **+3** (short rest)", "Beasts your body knows."], group="loot", sym=["WIL"]),
    color="aspect", stats=dict(kind="nature", atk=2, resolve=3),
    cards=[
        power("Hawk", "Form", 1, ["**Tiny** · Fly 60 ft.", "Talons: +2 to hit, 1d4 + DEX Physical.", "+2 on checks to notice."], form(-2, 3, 4, 10)),
        power("Wolf", "Form", 2, ["**Medium**.", "Bite: +2 to hit, 1d6 + DEX Physical.", "+2 on checks to track."], form(1, 3, 8, 40)),
        power("Mossbalm", "Mend", 2, ["**Action**, touch.", "A creature regains 2d8 + WIL HP."]),
        power("Bear", "Form", 3, ["**Large** · Climb 30 ft.", "Hide: +2 STR Defense (included).", "Claws: +2 to hit, 1d8 + STR Physical."], form(3, 1, 12, 30, hide=2)),
    ],
)

DECKS = [CONJURER, REPERTOIRE, LITANY, INSTINCT]

GOLD = [(1, 8), (10, 8), (50, 6), (100, 4), (500, 2), (1000, 1)]  # (value, copies)
TALLIES = 8

# ---------- Slot frames ----------
# (key, name, swap time, empty-Slot reminder, copies)
FRAMES = [
    ("armor", "Armor", "Swap: 10 minutes", ["Empty: **+10 ft Speed**."], PLAYERS),
    ("hand", "Hand", "Swap: free interaction", ["One Weapon, Shield or Instrument.", "Empty: grapple, or hold a Spellbook to cast."], 2 * PLAYERS),
    ("jewelry", "Jewelry", "Swap: free, once per turn", ["Rings, amulets, circlets, cloaks, gloves, boots."], PLAYERS),
    ("item", "Item", "Swap: free · Spellbook: 1 action", ["A Spellbook, a Recipe, or up to 3 identical Consumables."], 2 * PLAYERS),
    ("aspect", "Rune", "Swap: long rest", ["A Trait, Technique, Domain, Divine, Glamour or Nature."], 4 * PLAYERS),  # 3 each + 1 milestone
    ("hand", "Third Hand", "Swap: free interaction", ["Extra Gear Slot: a spectral arm, a familiar, a living tail.", "Never lost, traded or stored."], 1),
    ("jewelry", "Second Jewel", "Swap: free, once per turn", ["Extra Gear Slot.", "Never lost, traded or stored."], 1),
    ("item", "Great Backpack", "Swap: free · Spellbook: 1 action", ["Extra Gear Slot.", "Never lost, traded or stored."], 1),
    ("shard", "Runestone", "Pack (3 at most) or Party Stash", ["Holds one Rune, or nothing.", "**Capture:** 1 action · **Etch:** long rest · **Release:** free"], 5 * PLAYERS),  # 3 each + 2 each in the Stash
]

STARTER_LIST = {  # GM's Guide 4.2 table, generated from the cards above
    "Armor": [c["name"] for c in ARMOR if c["group"] == "starter"],
    "Hands": [c["name"] for c in HANDS if c["group"] == "starter"],
    "Jewelry": [c["name"] for c in JEWELRY if c["group"] == "starter"],
    "Items": [d["cover"]["name"] for d in DECKS if d["cover"]["kind"] == "gear" and d["cover"]["group"] == "starter"]
             + [c["name"] for c in ITEMS if c["group"] == "starter"],
    "Runes": [c["name"] for c in ASPECTS if c["group"] == "starter"]
               + [d["cover"]["name"] for d in DECKS if d["cover"]["kind"] == "aspect" and d["cover"]["group"] == "starter"],
}

# ---------- lore (DESIGN 4): a line at the bottom of each card, printed if space permits ----------
LORE = {
    # Callings
    "Duelist": "Footwork drilled until it needs no thought. The blade goes where the eyes already are.",
    "Templar": "A vow, a shield arm and a spine that does not bend. Others stand behind this one.",
    "Spellblade": "Steel in one hand, a spell on the tongue. Taught that the two were never separate.",
    "Infiltrator": "Locks, ledges and the patience of a held breath. Nobody remembers seeing them leave.",
    "Performer": "Quick feet and a quicker smile. Every room is a stage, every fight an audience.",
    "Sage": "A mind that kept every page it ever read, and a voice that makes the pages speak.",
    "Brawler": "Taverns, docks and pit fights. Swords are for people who can't hold on.",
    "Patriot": "A fire that won't go out, and a cause worth burning for. Doubt is for other people.",
    "Tactician": "Every fight is a board, every ally a piece. They see the move three turns before it lands.",
    "Ranger": "Weeks alone on a trail, and an arrow that never wastes its flight.",
    "Trickster": "Never where you swing. Always where you look away. The grin is the last thing you see.",
    "Hermit": "Years in a cave or a forest, talking to stones and stars. Something out there answered.",
    # armor
    "Leather": "Supple hide, oiled and stitched. It creaks a little, but it lets you run.",
    "Mail": "Riveted rings over a padded coat. Heavy on the shoulders, light on the conscience.",
    "Plate": "Full steel, fitted to you. You hear yourself coming, and so does everyone else.",
    # hands
    "Shield": "Oak boards, an iron rim, a dented boss. Every scar on it is a blow you never felt.",
    "Dagger": "Every traveler carries one. It cuts bread, rope and, when it must, throats.",
    "Shortsword": "A short, honest blade for tight alleys and crowded fights.",
    "Handaxe": "A woodcutter's tool that learned a second trade. It flies true when thrown.",
    "Finesse Blade": "A slim duelist's sword. A nick here, a cut there, and the foe's arm grows slow.",
    "Longsword": "The knight's blade: one hand for the shield, two hands when the shield breaks.",
    "Battleaxe": "A bearded head on an ash haft. It splits shields as easily as firewood.",
    "Greatsword": "As tall as a child and twice as loud. You don't parry it; you get out of its way.",
    "Glaive": "A blade on a long pole. It keeps the enemy at a distance, where it should be.",
    "Longbow": "Yew, horn and patience. A trained archer drops a charging boar before it closes.",
    "Sling": "A strip of leather and a pouch of stones. Shepherds have killed giants with less.",
    "Javelins": "A bundle of light spears, made to be thrown first and asked about later.",
    "Spellguard Staff": "Glyphs run along its grain. The wood remembers the shape of a casting hand.",
    "Traveler's Lute": "Its varnish is worn where a hundred hands have strummed it. The tunes carry far.",
    "Greatclub": "A tree limb with ambitions. What it hits stays down for a while.",
    "Gladius": "A soldier's sword, short and wide, made for fighting shoulder to shoulder.",
    "Boarspear": "Its crossbar stops a charging beast on the point. Hunters set it, then wait.",
    "Pilum": "A soft iron shank bends on impact, so the spear can't be thrown back, and the shield can't be raised.",
    "Shortbow": "Light enough to shoot from the saddle or from the treetops.",
    "Greataxe": "A crescent of iron on a heavy haft. One swing, one problem fewer.",
    "Fine Bow": "Horn, sinew and years of an archer's patience. Only steady fingers can draw it.",
    "Wand": "A rod of black wood capped with copper. It hums in a thinking hand and crackles when pointed.",
    # jewelry
    "Ring of Warding": "A band of cold silver. It tightens around the finger just before the blow lands.",
    "Guild Signet": "Press it into wax and doors open. Lose it, and someone comes asking why.",
    "Runestone Bandolier": "Leather straps padded for stone. Runestones knock softly against each other as you walk.",
    "Holy Amulet": "A blessed token on a worn cord. Prayers spoken over it seem to travel further.",
    "Boots of the Long Stride": "Soft boots that never wear out. Every few steps, one lands farther than it should.",
    "Ring of Sparks": "Copper wire coiled around a blue stone. It bites whoever lays a hand on its wearer.",
    "Dancer's Bells": "A string of tiny bells for the ankle. Their jingle gets under an enemy's skin.",
    # items
    "Potion of Healing": "Red and faintly warm, it tastes of iron and cherries. Shake before drinking.",
    "Coin Pouch": "A drawstring purse of good leather. Its weight is the only friend some people have.",
    "Writ of Favor": "Heavy paper, a heavy seal. A debt someone important promised to repay.",
    "Greater Potion of Healing": "Deep crimson and almost hot to hold. Wounds close while you're still swallowing.",
    "Restorative Salve": "Bitter herbs, river clay and a healer's patience, sealed in a tin.",
    "Pocket Sand": "The oldest trick there is. It still works.",
    "Alchemist's Fire Recipe": "Three corked flasks and the knowledge to fill them. Keep them away from the campfire.",
    # Runes: a line about the power, never about a former owner (DESIGN 4)
    "Springheel": "The ground lets go of you a little sooner, and takes you back a little later.",
    "Stone Blood": "Blood gone thick and slow as stone. Poison sinks into it and goes no further.",
    "Iron Will": "A resolve that stares down terrors and does not blink.",
    "Clear Mind": "A mind that sees through mist and mirrors. Illusions slide off it like rain.",
    "Cleave": "One foe falls, and the blade is already moving to the next.",
    "Steady Aim": "A breath held between heartbeats, until the arrow flies.",
    "Shield Bash": "Shields aren't only for hiding behind. The rim is a weapon too.",
    "Battle Hymn": "A chant that rises with every strike, until the whole line sings along.",
    "Rallying Cry": "One voice that turns a rout into a charge. It carries farther than a voice should.",
    "Shield Wall": "The rule of the front rank: your shield guards the friend beside you.",
    "Larceny": "Why use a door when a window will do?",
    "Minstrel": "A name that opens doors. Everyone has heard the stories, true or not.",
    "Navigation": "Salt on the lips, knots in the fingers, and a tale for every port.",
    "Backstreets": "Every alley has a shortcut, every crowd a loose purse, every corner a whisper.",
    "Hunt": "Broken twigs, bent grass, the hush before a deer bolts. The wild speaks, and you listen.",
    "Healing": "Steady hands, a calm voice, and the right herb for the right fever.",
    "Tavern": "The whole room at a glance: who lies, who drinks, who will start the fight.",
    "Forge": "The forge's wisdom: the weight of iron, the price of iron, where iron breaks.",
    "Peaks": "Thin air and sheer cliffs feel like home. The mountain doesn't win.",
    "Twin Strike": "A feint and a cut, so fast they sound like one blow.",
    "Second Wind": "When others lie down, you get back up. Pain is a problem for later.",
    "Sinew": "Lean, ropy strength. Not much meat on it, and it never tires.",
    "Night Eyes": "Eyes made for the dark. Shadows turn to shapes, then to detail.",
    "Bravado": "A hard stare and a hand on the hilt. It knows the price of everything, and of everyone.",
    "Tumbling": "Flips, falls and landings that make a crowd gasp.",
    "Wolfpack": "It knows the moment a friend has the prey, and when to pull it down.",
    "Herbalist": "Roots, leaves and old charms, and what each one is good for.",
    "Sweeping Blow": "The wide arc of a giant's swing. Everyone in reach learns to fear it.",
    "Defiance": "It will not stay down. Death has to ask twice.",
    "Grit": "Stubborn to the bone. What skill can't do, trying again will.",
    "Dusk Eyes": "Eyes that never quite lose the starlight. For them, dusk lasts all night.",
    "Bedrock": "Feet like roots in rock. It shrugs off the shove, the grip and the poison.",
    "Luck": "Fate likes whoever carries it, and nobody knows why.",
    "Campaign": "Made for war and for the long march after it. Strike hard, carry it all home.",
    "Discipline": "March in step, hold the post, read the order before it is given.",
    # deck covers
    "Conjurer's Book": "Spells copied in a careful hand, the margins full of warnings. The ink still smells of ozone.",
    "Wanderer's Repertoire": "Songs of roadside fires and tavern corners, made for someone who never stays long.",
    "Acolyte's Litany": "Prayers worn smooth by a thousand voices. The faith comes with them.",
    "Wildheart's Instinct": "Fur, feather and claw. The body knows these shapes, and longs for them.",
}
POWER_LORE = {  # deck cards: their names may repeat a gear card's (Shield)
    "Fire Bolt": "The first spell every conjurer learns, and the one they burn their eyebrows with.",
    "Mage Hand": "An unseen hand for the jar on the high shelf, or the key on the guard's belt.",
    "Magic Missile": "Darts of pure light that seek their mark. They rarely miss entirely.",
    "Shield": "A shimmer of force, conjured in the instant before the blade lands.",
    "Grease": "Slick as an eel and twice as rude. Dignity is the first casualty.",
    "Misty Step": "A breath of silver mist, and you stand somewhere else.",
    "Web": "Thick, sticky strands fill the passage. Whatever is caught in it struggles in vain.",
    "Jeer": "A well-timed insult can throw off any swing.",
    "Rally": "A marching song that puts steel in tired arms.",
    "Hold the Line": "A slow, steady beat. Feet planted, shields up, nobody runs.",
    "Cutting Words": "Mockery, sharp as a knife, right as the foe commits.",
    "Steady Now": "A calm word in the moment that matters.",
    "Dread": "A lament for the foe's own funeral. Some listeners believe it.",
    "Rousing Verse": "A verse about the heroes who got back up. The listener does too.",
    "Guidance": "A quiet word of faith that steadies hand and mind.",
    "Bless": "A blessing that sends allies forward with surer hands.",
    "Bane": "A curse that makes every blow of the enemy hesitate.",
    "Twist Fate": "The threads of chance, plucked and pulled. The dice tumble again.",
    "Healing Word": "A single holy word, called across the battlefield. Wounds answer.",
    "Cure Wounds": "Hands laid on the wound; warmth spreads, and the flesh knits.",
    "Hawk": "Wind under wings, the world far below, every mouse in the field plain to see.",
    "Wolf": "Four swift legs and a nose that reads the forest like a book.",
    "Mossbalm": "Green moss pressed into the wound. The forest remembers how to heal.",
    "Bear": "Thick fur, a heavy hide and claws like knives. Few things argue with a bear.",
}
for _deck in DECKS:
    for _p in _deck["cards"]:
        _p["lore"] = POWER_LORE[_p["name"]]

# ---------- card IDs (P 12.1): type letter, Rank, number in order of appearance ----------
# A Domain keeps the letter K it had as a Knack, so no ID changes.
# Add new cards at the end of their type and Rank so existing IDs never change.
TYPE_LETTER = {"Calling": "L", "Armor": "A", "Weapon": "W", "Shield": "S", "Instrument": "M", "Jewelry": "J",
               "Consumable": "P", "Recipe": "R", "Container": "C", "Spellbook": "B", "Trait": "T", "Technique": "Q",
               "Domain": "K", "Divine": "D", "Glamour": "G", "Nature": "N"}
CARDS = CALLINGS + ARMOR + HANDS + JEWELRY + ITEMS + ASPECTS + [d["cover"] for d in DECKS]

# ---------- mechanics of cards (SPEC 2.1): card name → list of Powers; ids are added by tools/export_sim.py ----------
TWO_SHIELD_MOD = [dict(mod="def", n=2, defs=["targeted"], next=True)]  # +2 to the Defense the attack targets, this attack only
CARD_FX = {
    # weapon riders
    "Finesse Blade": [dict(use="trigger", on="hit", do=[dict(mod="attack", n=-2, next=True, until="startSourceTurn")])],
    "Spellguard Staff": [dict(use="passive", castingHand=True)],
    "Gladius": [dict(use="passive", hook="close_order", params=dict(dmg="1d4"))],
    "Boarspear": [dict(use="trigger", on="opportunity", hook="brace", params=dict(dmg="1d8"))],
    "Pilum": [dict(use="trigger", on="hit", hook="pierce")],
    # gear
    "Traveler's Lute": [dict(use="passive", extraResolve=1, anthemReach=60, params=dict(default=30))],
    "Holy Amulet": [dict(use="passive", extraResolve=1, cueReach=90, params=dict(default=60))],
    "Dancer's Bells": [dict(use="passive", extraResolve=1, dirgeReach=90, params=dict(default=60))],
    "Ring of Warding": [dict(use="reaction", uses="2/SR", on="hitSelf", target="self", do=TWO_SHIELD_MOD)],
    "Ring of Sparks": [dict(use="reaction", uses="1/SR", on="meleeHitSelf5", target="enemy",
                            do=[dict(dmg="2d6", type="Lightning")])],
    "Boots of the Long Stride": [dict(use="reaction", uses="1/SR", target="self", do=[dict(dash=True)])],
    "Potion of Healing": [dict(use="action", reach=5, target="creature", do=[dict(heal="2d4+2")])],
    "Greater Potion of Healing": [dict(use="action", reach=5, target="creature", do=[dict(heal="4d4+4")])],
    "Pocket Sand": [dict(use="reaction", reach=5, target="enemy", atk=dict(abil=["DEX", "WIL"], hit=2, vs="DEX"),
                         do=[dict(mod="attack", n=-2, until="endTargetTurn")])],
    "Alchemist's Fire Recipe": [dict(use="reaction", reach=30, target="point", area=dict(shape="sphere", size=5),
                                     atk=dict(abil=["DEX", "INT"], hit=3, vs="DEX"), half=True,
                                     do=[dict(dmg="2d6", type="Fire")], tags=["fire"])],
    # Runes
    "Iron Will": [dict(use="passive", defVs=dict(WIL=2), tags=["fear", "mind control"])],
    "Stone Blood": [dict(use="passive", defVs=dict(STR=2), tags=["poison", "disease"])],
    "Clear Mind": [dict(use="passive", defVs=dict(INT=2), tags=["illusion", "confusion"])],
    "Cleave": [dict(use="trigger", uses="1/SR", on="meleeDrop", do=[dict(attack="melee")])],
    "Steady Aim": [dict(use="reaction", uses="2/SR", target="self", params=dict(ranged=True),
                        do=[dict(mod="attack", n=2, next=True, until="endThisTurn")])],
    "Shield Bash": [dict(use="reaction", uses="1/SR", need=["shield", "attackAction"], reach=5, target="enemy",
                         do=[dict(shove=True)])],
    "Battle Hymn": [dict(use="trigger", uses="2/SR", on="weaponHit", target="allies", count=3, reach=30, need=VOICE,
                         do=[dict(mod="def", n=2, defs=["STR", "DEX"], until="startSourceTurn")])],
    "Rallying Cry": [dict(kind="Anthem", use="action", uses="1/SR", reach=30, target="allies", count=3, need=VOICE,
                          dur="1 minute", do=[dict(mod="attack", n=2, until="dur")])],
    "Shield Wall": [dict(use="reaction", uses="1/SR", on="hitAlly5", need=["shield"], target="ally", do=TWO_SHIELD_MOD)],
    "Twin Strike": [dict(use="passive", attacks=2)],
    "Second Wind": [dict(use="action", uses="1/SR", target="self", do=[dict(heal="1d10+3")])],
    "Night Eyes": [dict(use="passive", darkvision=120)],
    "Defiance": [dict(use="passive", uses="1/SR", relentless=True)],
    # Rank I loot Traits
    "Dusk Eyes": [dict(use="passive", darkvision=60)],
    "Bedrock": [dict(use="passive", defVs=dict(STR=2), tags=["poison", "shove", "grapple"])],
    "Luck": [dict(use="passive", uses="1/SR", lucky=True, reroll="1d20")],
    # Calling perks (scaling values: "STR", "-DEX", "½WIL", "2×STR", "5×½DEX" read the creature's current modifiers)
    "Duelist": [dict(use="trigger", on="meleeHit", target="self", do=[dict(move="safe", ft="5×½DEX", once=True)]),
                dict(use="reaction", uses="½STR/SR", on="meleeMissSelf", target="enemy", riposte=True)],
    "Templar": [dict(use="reaction", uses="½WIL/SR", on="hitAlly5", target="ally", oath=True, oathCut="2×STR")],
    "Spellblade": [dict(use="passive", castingHand=True),
                   dict(use="trigger", uses="½STR/SR", on="meleeWeaponHit", do=[dict(dmg="INT")])],
    "Sage": [dict(use="passive", extraSp="½INT")],
    "Brawler": [dict(use="passive", grabHit="STR"), dict(use="passive", escapeAbil="2×DEX")],
    "Patriot": [dict(use="trigger", uses="½WIL/SR", on="weaponHit", do=[dict(dmg="½STR d6", type="Radiant")])],
    "Tactician": [dict(use="action", uses="½STR/SR", reach=30, target="ally", need=VOICE, do=[dict(command=True, hit="INT")])],
    # Quarry's mark: −½ DEX to every Defense of the target, so you and your allies hit it more (RULING R714)
    "Ranger": [dict(use="trigger", uses="½INT/SR", on="rangedHit", do=[dict(mod="def", n="-½DEX", until="startSourceTurn")])],
    "Trickster": [dict(use="trigger", on="hitUnseen", do=[dict(dmg="½DEX|WIL d6")])],
    "Hermit": [dict(use="passive", extraResolve="½WIL")],
    "Wolfpack": [dict(use="trigger", uses="1/SR", on="hitEngaged", do=[dict(cond="Prone")])],
    "Herbalist": [dict(use="passive", extraSp=1)],
    # an Attack action of its own: one roll against each enemy in the weapon's reach (sim/effects.js)
    "Sweeping Blow": [dict(use="action", uses="1/SR", target="enemies", hook="sweep", params=dict(props=["heavy", "reach"]))],
}
for _name in CARD_FX:
    assert _name in {c["name"] for c in CARDS}, _name
for _c in CARDS:
    _c["fx"] = CARD_FX.get(_c["name"], [])
    _c["lore"] = LORE[_c["name"]]
assert set(LORE) == {c["name"] for c in CARDS}, set(LORE) ^ {c["name"] for c in CARDS}

_count = {}
for _c in CARDS:
    _key = (TYPE_LETTER[_c["kw"].split(" · ")[0]], _c["rank"])
    _count[_key] = _count.get(_key, 0) + 1
    _c["id"] = f"{_key[0]}-{_key[1] + '-' if _key[1] else ''}{_count[_key]:02d}"  # a Calling has no Rank: L-01
BY_NAME = {c["name"]: c for c in CARDS}
