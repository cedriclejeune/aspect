"""Balance report for the base set: what each Calling can equip and use, symbol parity, and Rank-sizing checks.

Usage: python3 tools/balance_report.py [--strict]
Reads cards/base_set.py only (no packages needed). Prints tables; with --strict, exits non-zero when a check fails.

"Equippable" follows P 3.1 (the Calling has one of the card's lit symbols). "Usable" also drops cards whose effect
needs gear or Runes the Calling can never equip: a Focus without a Divine, Glamour or Nature deck, a Shield
Technique without a Shield, a Heavy or Reach Technique without such a weapon.
"""
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cards"))
import base_set as bs  # noqa: E402

ABILS = bs.ABILS
RANK_BONUS = {"I": 2, "II": 3, "III": 4, "IV": 5, "V": 6}
TRAIT_HP = {"I": 2, "II": 4, "III": 7, "IV": 10, "V": 14}
SLOT = {"Armor": "Armor", "Weapon": "Hand", "Shield": "Hand", "Instrument": "Hand", "Jewelry": "Jewelry",
        "Consumable": "Item", "Recipe": "Item", "Container": "Pack", "Spellbook": "Item"}
WIL_DECKS = ("Divine", "Glamour", "Nature")
# GM 4.3 activity table: the ability each activity belongs to (plus the extra words used on base-set cards)
ACTIVITY = {
    "STR": ["climb", "swim", "jump", "lift", "break", "endure", "march"],
    "DEX": ["sneak", "hide", "balance", "tumble", "pick locks", "pick pockets"],
    "INT": ["notice", "search", "read intentions", "recall lore", "track", "navigate", "treat wounds"],
    "WIL": ["persuade", "deceive", "perform", "intimidate", "haggle", "gather rumors", "handle animals", "stand firm"],
}

ACTIVITY_EXCEPTIONS = {"Minstrel"}  # GM 4.3: the pure WIL social Domain
ROLL_EXCEPTIONS = {"Pocket Sand", "Alchemist's Fire Recipe"}  # anyone can throw them, at +0 without the ability (accepted)

CARDS = [c for c in bs.CARDS if c["kind"] != "calling"]
CALLINGS = bs.CALLINGS
PAIRS = []
for c in CALLINGS:
    if tuple(c["sym"]) not in PAIRS:
        PAIRS.append(tuple(c["sym"]))


def ctype(c):
    return c["kw"].split(" · ")[0]


def slot(c):
    return SLOT.get(ctype(c), "Rune")


def fits(c, pair):
    return bool(set(c["sym"]) & set(pair))


def usable(c, pair):
    """Equippable and not dead weight for this pair of abilities."""
    if not fits(c, pair):
        return False
    pool = [x for x in CARDS if fits(x, pair)]
    if "Focus" in c["kw"]:
        return any(ctype(x) in WIL_DECKS for x in pool)
    text = " ".join(c["text"])
    if "Shield" in text and ctype(c) == "Technique":
        return any(ctype(x) == "Shield" for x in pool)
    if "Heavy or Reach weapon" in text:
        return any(re.search(r"\b(Heavy|Reach)\b", x["kw"]) for x in pool if ctype(x) == "Weapon")
    return True


def table(head, rows):
    w = [max(len(str(r[i])) for r in [head] + rows) for i in range(len(head))]
    line = lambda r: "  ".join(str(v).ljust(w[i]) for i, v in enumerate(r))
    print(line(head))
    print("  ".join("-" * x for x in w))
    for r in rows:
        print(line(r))
    print()


def callings_report():
    print("## Cards each Calling can equip (P 3.1) and use\n")
    rows, totals = [], []
    for pair in PAIRS:
        names = " / ".join(c["name"] for c in CALLINGS if tuple(c["sym"]) == pair)
        eq = [c for c in CARDS if fits(c, pair)]
        us = [c for c in CARDS if usable(c, pair)]
        st = sum(c["group"] == "starter" for c in us)
        lo = sum(c["group"] == "loot" for c in us)
        asp = collections.Counter(c["rank"] for c in us if slot(c) == "Rune")
        hands = sum(slot(c) == "Hand" for c in us)
        rows.append(["·".join(pair), names, len(eq), len(us), st, lo, hands, asp.get("I", 0), asp.get("II", 0)])
        totals.append(len(us))
    table(["Pair", "Callings", "Equip", "Usable", "Starter", "Loot", "Hand", "Rune I", "Rune II"], rows)
    print(f"Usable spread: {min(totals)}–{max(totals)} of {len(CARDS)} cards "
          f"({max(totals) - min(totals)} apart, {100 * (max(totals) - min(totals)) / max(totals):.0f}%)\n")
    return max(totals) - min(totals)


def symbols_report():
    print("## Symbol parity\n")
    single = collections.Counter(c["sym"][0] for c in CARDS if len(c["sym"]) == 1)
    lit = collections.Counter(a for c in CARDS if len(c["sym"]) < 4 for a in c["sym"])
    table(["Ability", "Single-symbol cards", "Cards lighting it (not all-four)"],
          [[a, single.get(a, 0), lit.get(a, 0)] for a in ABILS])
    home = collections.Counter(tuple(sorted(c["sym"], key=ABILS.index)) for c in CARDS if len(c["sym"]) == 2)
    table(["Pair", "Two-symbol cards"], [["·".join(p), home.get(p, 0)] for p in PAIRS])
    print("A pair loses the cards of its opposite pair and the single-symbol cards of its two missing abilities,\n"
          "so equal access needs equal single-symbol counts per ability and equal two-symbol counts per pair.\n")


def calling_stats():
    print("## Callings\n")
    rows = []
    for c in CALLINGS:
        hp, spd = int(c["strip"]["HP"]), int(c["strip"]["SPD"])
        rows.append([c["name"], "·".join(c["sym"]), hp, spd, hp + (spd - 30) * 2 // 5, c["text"][0].split(":**")[0].strip("*")])
    table(["Calling", "Pair", "HP", "Speed", "HP + 2 per 5 ft", "Perk"], rows)


def weapons_report(defense=13, mod=2):
    print(f"## Weapons: expected damage per attack (+{mod} ability, Defense {defense}; a crit adds the dice once more, twice if Brutal)\n")
    rows = []

    def ev(hit, avg, brutal):
        p = max(0.05, min(0.95, (21 - (defense - hit - mod)) / 20))
        return p * (avg + mod) + 0.05 * avg * (2 if brutal else 1)

    for c in CARDS:
        a = c.get("atk")
        if not a:
            continue
        for dice in [a["dice"]] + ([a["two"]] if a["two"] else []):
            n, d = map(int, dice.split("d"))
            avg = n * (d + 1) / 2
            first = ev(a["hit"], avg, a.get("brutal"))
            later = f"{ev(a['hit'] + 2, avg, a.get('brutal')):.2f}" if a.get("flurry") else ""
            rows.append([c["name"], c["rank"], "·".join(c["sym"]), f"+{a['hit']}", dice + (f" {a['type']}" if a["type"] != "Physical" else ""), f"{first:.2f}", later,
                         " ".join(k for k in ("light", "heavy", "reach", "twoHanded", "loading", "brutal", "crushing", "flurry") if a.get(k))
                         + (" thrown" if a["thrown"] else "") + (" ranged" if a["range"] else "")
                         + (" two-handed grip" if dice == a["two"] else "")])
    table(["Weapon", "Rank", "Symbols", "Hit", "Dice", "EV", "EV later (Flurry)", "Properties"], rows)


def checks():
    """Rank-sizing and symbol rules from DESIGN 3–4 and GM 4.3. Returns the list of problems."""
    out = []
    for c in CARDS:
        t, r, text = ctype(c), c["rank"], " ".join(c["text"])
        if t == "Weapon" and c["atk"]["hit"] != RANK_BONUS[r]:
            out.append(f"{c['name']}: to hit +{c['atk']['hit']}, Rank {r} bonus is +{RANK_BONUS[r]} (DESIGN 4: size every number by Rank)")
        if t == "Trait" and c["strip"].get("HP") != f"+{TRAIT_HP[r]}":
            out.append(f"{c['name']}: Trait HP {c['strip'].get('HP')}, Rank {r} prints +{TRAIT_HP[r]}")
        if t in ("Domain", "Technique") and "HP" in c["strip"]:
            out.append(f"{c['name']}: a {t} prints no HP")
        if SLOT.get(t) in ("Jewelry", "Item", "Pack") and t != "Spellbook" and "Focus" not in c["kw"] and len(c["sym"]) != 4:
            out.append(f"{c['name']}: {t} should light all four symbols")
        m = re.search(r"\+(\d) on checks to ([^.]*)", text)
        if m:
            if int(m[1]) != RANK_BONUS[r]:
                out.append(f"{c['name']}: check bonus +{m[1]}, Rank {r} is +{RANK_BONUS[r]}")
            acts = re.split(r", | or ", m[2])
            abil = {a for a in ABILS for x in acts if x in ACTIVITY[a]}
            unknown = [x for x in acts if not any(x in ACTIVITY[a] for a in ABILS)]
            if unknown:
                out.append(f"{c['name']}: activities not in the GM 4.3 table: {', '.join(unknown)}")
            if len(abil) < 2 and c["name"] not in ACTIVITY_EXCEPTIONS:
                out.append(f"{c['name']}: activities from {len(abil)} ability ({', '.join(abil)}), GM 4.3 wants two")
            if len(c["sym"]) < 4 and not abil & set(c["sym"]):
                out.append(f"{c['name']}: no activity matches its symbols {c['sym']}")
        for roll in re.findall(r"\(([A-Z]{3}) or ([A-Z]{3}) \+ \d\)", text):
            missing = [a for a in c["sym"] if a not in roll]
            if missing and len(c["sym"]) < 4:
                out.append(f"{c['name']}: rolls {' or '.join(roll)}, but lit {', '.join(missing)} can't roll")
            if len(c["sym"]) == 4 and c["name"] not in ROLL_EXCEPTIONS:
                out.append(f"{c['name']}: all four lit but it rolls only {' or '.join(roll)} "
                           f"(Callings without either roll +0)")
    return out


def main():
    spread = callings_report()
    symbols_report()
    calling_stats()
    weapons_report()
    problems = checks()
    print("## Checks\n")
    for p in problems:
        print("- " + p)
    print(f"\n{len(problems)} notes")
    if "--strict" in sys.argv and (problems or spread > 8):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
