"""Copy GLOSSARY.md into the Glossary chapter of both handbooks, so they stay identical.

Usage: python3 tools/sync_glossary.py [--check] [--lang fr]
Each "**Term**:" entry and its definition (never the _Avoid_ line) becomes one table row, sorted A–Z,
between the <!-- glossary:start --> and <!-- glossary:end --> markers of rules/PLAYERS.md and rules/GM.md.
--lang fr does the same from rules/fr/GLOSSAIRE.md into rules/fr/JOUEURS.md and rules/fr/MJ.md.
--check only reports whether a handbook is out of date (exit 1 if so). The PDF build runs the sync.
"""
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = {
    # glossary, books, intro line, table header
    "en": (ROOT / "GLOSSARY.md", [ROOT / "rules" / "PLAYERS.md", ROOT / "rules" / "GM.md"],
           "Each game term has one meaning, in both books.", "| Term | Meaning |"),
    "fr": (ROOT / "rules" / "fr" / "GLOSSAIRE.md", [ROOT / "rules" / "fr" / "JOUEURS.md", ROOT / "rules" / "fr" / "MJ.md"],
           "Chaque terme de jeu a un seul sens, dans les deux livres.", "| Terme | Sens |"),
}
BOOKS = LANGS["en"][1]
BLOCK = re.compile(r"(<!-- glossary:start -->\n).*?(<!-- glossary:end -->)", re.S)


def _key(term):
    """A–Z order that ignores accents (É sorts with E)."""
    return unicodedata.normalize("NFD", term.lower()).encode("ascii", "ignore").decode()


def entries(lang="en"):
    text = LANGS[lang][0].read_text(encoding="utf-8")
    return sorted(re.findall(r"^\*\*(.+?)\*\*:\n(.+)$", text, flags=re.M), key=lambda e: _key(e[0]))


def table(lang="en"):
    _, _, intro, head = LANGS[lang]
    rows = "".join(f"| **{term}** | {meaning} |\n" for term, meaning in entries(lang))
    return f"{intro}\n\n{head}\n|---|---|\n" + rows


def sync(check=False, lang="en"):
    stale = []
    for book in LANGS[lang][1]:
        text = book.read_text(encoding="utf-8")
        if not BLOCK.search(text):
            sys.exit(f"{book.name}: glossary markers not found")
        new = BLOCK.sub(lambda m: m.group(1) + "\n" + table(lang) + "\n" + m.group(2), text)
        if new != text:
            stale.append(book.name)
            if not check:
                book.write_text(new, encoding="utf-8")
    return stale


if __name__ == "__main__":
    check = "--check" in sys.argv
    lang = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "en"
    stale = sync(check, lang)
    if stale:
        print(("Out of date: " if check else "Updated: ") + ", ".join(stale))
    sys.exit(1 if check and stale else 0)
