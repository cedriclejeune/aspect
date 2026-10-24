"""Check that the printed text of every card with mechanics agrees with its structured data (sim/cards.js source).

Usage: .venv/bin/python tools/check_cards.py
Reports a number in the printed text that the data lacks, and dice in the data that the text lacks.
Exits non-zero on any problem.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import export_sim  # noqa: E402

# Pure flavour: removed from the text before its numbers are read.
IGNORE = [
    r"\d+ (?:round|minute|hour|night)s?",   # durations that only the dur key spells ("1 minute", "within 1 hour")
    r"\d+ lb",                              # object weight
    r"to 0 HP",                            # drop threshold
    r"\d+ gp",                              # gold amounts
    r"\+\d+ on checks to [^.]*",            # Knack-style check bonuses
    r"passive Awareness \+\d+",             # Keen Nose
    r"[Rr]echarges?(?: on a)? (\d)–\d",     # "Recharge 5–6", "recharges on a 5–6": the data holds 5
    r"instead of \d/[SL]\.R\.",            # the printed limit a recharge override replaces
]
SKIP_KEYS = {"id", "name", "text", "kw", "deck", "cover"}
DICE = re.compile(r"\b(\d*)d(\d+)\b")


def strings(data):
    """Every string and number in the data, except ids and printed text."""
    if isinstance(data, dict):
        for k, v in data.items():
            if k not in SKIP_KEYS:
                yield from strings(v)
    elif isinstance(data, (list, tuple)):
        for v in data:
            yield from strings(v)
    else:
        yield str(data)


def dice_in(text):
    return {f"{m[1] or 1}d{m[2]}" for m in DICE.finditer(text)}


def text_numbers(text):
    for pat in IGNORE:
        text = re.sub(pat, lambda m: f"Recharge {m[1]}" if "echarge" in m.re.pattern else "", text)
    return dice_in(text), {int(n) for n in re.findall(r"\d+", DICE.sub("", text))}


def compare(label, text, data):
    blob = " ".join(strings(data))
    d_text, n_text = text_numbers(text)
    d_data = dice_in(blob)
    n_data = {int(n) for n in re.findall(r"\d+", blob)}
    problems = [f"{label}: number {n} in the text is not in the data" for n in sorted(n_text - n_data)]
    problems += [f"{label}: dice {d} in the text is not in the data" for d in sorted(d_text - d_data)]
    problems += [f"{label}: dice {d} in the data is not in the text" for d in sorted(d_data - d_text)]
    return problems


def main():
    data = export_sim.build()
    problems, checked = [], 0
    for c in data["cards"].values():
        deck = data["decks"].get(c["id"])
        if not (c["fx"] or c.get("atk") or deck):
            continue
        stats = {k: v for k, v in (deck or {}).items() if k != "powers"}
        checked += 1
        problems += compare(f'{c["id"]} {c["name"]}', " ".join(c["text"] + c["kw"]),
                            {k: v for k, v in c.items() if k != "strip"} | {"deck_stats": stats})
    for cover, deck in data["decks"].items():
        for src, p in zip(next(d for d in export_sim.bs.DECKS if d["cover"]["id"] == cover)["cards"], deck["powers"]):
            checked += 1
            problems += compare(f'{p["id"]} {p["name"]}', " ".join(src["text"] + [src["kw"]]), p)
    for f, src in zip(data["foes"], export_sim.foes.FOES):
        if f["own"]:
            checked += 1
            problems += compare(f'foe {f["name"]}', " ".join(f["own"]),
                                {"bonus": f["bonus"], "extraDice": f["extraDice"], "recharge": f.get("recharge", {}), "ownFx": f["ownFx"]})
    for p in problems:
        print(p)
    print(f"{checked} cards and powers checked, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
