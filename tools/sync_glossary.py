"""Copy GLOSSARY.md into the Glossary chapter of both handbooks, so they stay identical.

Usage: python3 tools/sync_glossary.py [--check]
Each "**Term**:" entry and its definition (never the _Avoid_ line) becomes one table row, sorted A–Z,
between the <!-- glossary:start --> and <!-- glossary:end --> markers of rules/PLAYERS.md and rules/GM.md.
--check only reports whether a handbook is out of date (exit 1 if so). The PDF build runs the sync.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = [ROOT / "rules" / "PLAYERS.md", ROOT / "rules" / "GM.md"]
BLOCK = re.compile(r"(<!-- glossary:start -->\n).*?(<!-- glossary:end -->)", re.S)


def entries():
    text = (ROOT / "GLOSSARY.md").read_text(encoding="utf-8")
    return sorted(re.findall(r"^\*\*(.+?)\*\*:\n(.+)$", text, flags=re.M), key=lambda e: e[0].lower())


def table():
    rows = "".join(f"| **{term}** | {meaning} |\n" for term, meaning in entries())
    return "Each game term has one meaning, in both books.\n\n| Term | Meaning |\n|---|---|\n" + rows


def sync(check=False):
    stale = []
    for book in BOOKS:
        text = book.read_text(encoding="utf-8")
        if not BLOCK.search(text):
            sys.exit(f"{book.name}: glossary markers not found")
        new = BLOCK.sub(lambda m: m.group(1) + "\n" + table() + "\n" + m.group(2), text)
        if new != text:
            stale.append(book.name)
            if not check:
                book.write_text(new, encoding="utf-8")
    return stale


if __name__ == "__main__":
    check = "--check" in sys.argv
    stale = sync(check)
    if stale:
        print(("Out of date: " if check else "Updated: ") + ", ".join(stale))
    sys.exit(1 if check and stale else 0)
