"""Export every card as flat, easy-to-read tables: cards/tables/*.csv and cards/tables/cards.json.

Usage: .venv/bin/python tools/export_tables.py
Generated from cards/base_set.py and cards/foes.py (through tools/export_sim.py, for the foe totals). Never hand-edit
the tables: change the sources and run this (tools/build_cards.py runs it too).

Files:
- cards.csv: one row per card (Callings, gear, Runes, deck covers, Wounds) with its ten strip numbers.
- powers.csv: one row per spell or power in a deck (Spellbook, Glamour, Divine, Nature).
- foes.csv: one row per foe card with its body, its totals and the cards it carries.
- cards.json: the same three tables as lists of objects.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import export_sim  # noqa: E402

bs, foes = export_sim.bs, export_sim.foes
OUT = ROOT / "cards" / "tables"
STRIP = ["STR", "DEX", "INT", "WIL", "STRd", "DEXd", "INTd", "WILd", "HP", "SPD"]


def clean(s):
    """Card text without the **bold** and *italic* marks."""
    return str(s).replace("**", "").replace("*", "")


def card_rows():
    rows = []
    for c in bs.CARDS + bs.WOUNDS:
        kw = c["kw"].split(" · ")
        atk = c.get("atk")
        rows.append({
            "id": c.get("id", ""), "name": c["name"], "type": kw[0], "rank": c["rank"], "group": c["group"],
            "symbols": "all" if len(c["sym"]) == 4 else " ".join(c["sym"]), "copies": c["copies"],
            **{k: str(c["strip"].get(k, "")).replace("−", "-") for k in STRIP},
            "to_hit": f"+{atk['hit']}" if atk else "", "damage": (atk["dice"] + (f" / {atk['two']}" if atk["two"] else "")) if atk else "",
            "keywords": " · ".join(kw[1:]), "text": clean(" ".join(c["text"])), "lore": c.get("lore", ""),
        })
    return rows


def power_rows():
    rows = []
    for d in bs.DECKS:
        for p in d["cards"]:
            rows.append({"deck_id": d["cover"]["id"], "deck": d["cover"]["name"], "name": p["name"],
                         "kind": p["level"], "cost": p["cost"], "keywords": p["kw"], "text": clean(" ".join(p["text"])),
                         **{k: str(p["strip"].get(k, "")).replace("−", "-") for k in STRIP}})
    return rows


def foe_rows():
    rows = []
    for f, src in zip(export_sim.build()["foes"], foes.FOES):
        b, t = f["body"], f["totals"]
        tags = ["Boss"] * f["boss"] + ["Leader"] * f["leader"]
        rows.append({"name": f["name"], "size": b["size"], "tags": " ".join(tags), "senses": src["senses"],
                     **{f"body_{k}": b[k] for k in ("STR", "DEX", "INT", "WIL", "HP", "SPD")},
                     **{k: t[k] for k in STRIP},
                     "carries": "; ".join(f"{n} ({bs.BY_NAME[n]['id']})" for n in src["carries"]),
                     "own": clean(" ".join(src["own"]))})
    return rows


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tables = {"cards": card_rows(), "powers": power_rows(), "foes": foe_rows()}
    for name, rows in tables.items():
        write_csv(OUT / f"{name}.csv", rows)
    (OUT / "cards.json").write_text(json.dumps(tables, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}: " + ", ".join(f"{len(r)} {n}" for n, r in tables.items()))


if __name__ == "__main__":
    main()
