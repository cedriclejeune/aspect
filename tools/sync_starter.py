"""Write the starter list (every Rank I starter card, with its text) into the Player Rules, chapter 13.3.

Usage: python3 tools/sync_starter.py [--check] [--lang fr]
Generated from cards/base_set.py (and cards/fr.py in French), between the <!-- starter:start --> and
<!-- starter:end --> markers of rules/PLAYERS.md or rules/fr/JOUEURS.md. Never hand-edit the block.
--check only reports whether the book is out of date (exit 1 if so). The PDF build runs the sync.
"""
import importlib
import importlib.util
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "cards"), str(ROOT / "tools")]
BLOCK = re.compile(r"(<!-- starter:start -->\n).*?(<!-- starter:end -->)", re.S)

WORDS = {
    "en": dict(
        book=ROOT / "rules" / "PLAYERS.md",
        intro="Every Rank I card you can start with (13.1). *All*: the four affinities are lit. "
              "A deck card (Spellbook, WIL deck) lists the spells or powers it holds.",
        head="| Card | Affinities | Keywords | Bonuses | Effects and powers |",
        slots={"Armor": "Armor", "Hands": "Hands", "Jewelry": "Jewelry", "Items": "Items", "Runes": "Runes"},
        all="all", abil={"STR": "STR", "DEX": "DEX", "INT": "INT", "WIL": "WIL"},
        defense="+{n} {a} Defense", hp="+{n} HP", spd="{n} ft Speed", mod="{n} {a}",
        spells="Spells", powers="Powers", level={"Cantrip": "cantrips", "1st": "1st level", "2nd": "2nd level"},
        drop=r" · (?:Thrown|Range) [\d/]+", order=["Trait", "Technique", "Domain"],
    ),
    "fr": dict(
        book=ROOT / "rules" / "fr" / "JOUEURS.md",
        intro="Toutes les cartes de Rang I parmi lesquelles vous choisissez à la création (13.1). *Toutes* : "
              "les quatre affinités sont allumées. Un paquet (Livre de sorts, paquet de Volonté) liste ses sorts ou ses pouvoirs.",
        head="| Carte | Affinités | Mots-clés | Bonus | Effets et abilités |",
        slots={"Armor": "Armure", "Hands": "Mains", "Jewelry": "Bijou", "Items": "Objets", "Runes": "Runes"},
        all="toutes", abil={"STR": "FOR", "DEX": "AGI", "INT": "INT", "WIL": "VOL"},
        defense="+{n} Défense {de}{a}", hp="+{n} PV", spd="{n} m de Vitesse", mod="{n} {a}",
        spells="Sorts", powers="Pouvoirs", level={"Tour de magie": "tours de magie", "1er": "1er niveau", "2e": "2e niveau"},
        drop=r" · (?:Lancer|Portée) [\d/]+", order=["Trait", "Technique", "Domaine"],
    ),
}


def _key(s):
    return unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()


def _fresh(name):
    """A private copy of cards/<name>.py, so localizing it never touches the build's own modules."""
    spec = importlib.util.spec_from_file_location(f"_starter_{name}", ROOT / "cards" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load(lang):
    """A fresh copy of the base set, in French if asked."""
    bs = _fresh("base_set")
    if lang == "fr":
        _fresh("fr").localize(bs, _fresh("foes"))
    return bs


def bonuses(strip, W, lang):
    out = []
    for k in ["STR", "DEX", "INT", "WIL"]:
        if k in strip:
            out.append(W["mod"].format(n=strip[k], a=W["abil"][k]))
    for k in ["STR", "DEX", "INT", "WIL"]:
        if k + "d" in strip:
            a = W["abil"][k]
            de = ("d'" if a[0] in "AEIOU" else "de ") if lang == "fr" else ""
            out.append(W["defense"].format(n=strip[k + "d"].lstrip("+"), a=a, de=de))
    if "HP" in strip:
        out.append(W["hp"].format(n=strip["HP"].lstrip("+")))
    if "SPD" in strip:
        v = strip["SPD"]
        if lang == "fr":
            import i18n_fr
            v = i18n_fr.signed_feet(v)
        out.append(W["spd"].format(n=v))
    return ", ".join(out) or "—"


def deck_line(deck, W):
    """The spells or powers a deck holds, grouped by level (Spellbook) or listed with their kind (WIL deck)."""
    cards = deck["cards"]
    if deck["stats"]["kind"] == "spellbook":
        groups = {}
        for p in cards:
            groups.setdefault(W["level"].get(p["level"], p["level"]), []).append(f"*{p['name']}*")
        return f"**{W['spells']} :** " + " ; ".join(f"{lvl} : {', '.join(n)}" for lvl, n in groups.items()) + "."
    return f"**{W['powers']} :** " + ", ".join(f"*{p['name']}* ({p['level']})" for p in cards) + "."


def table(lang="en"):
    W = WORDS[lang]
    bs = load(lang)
    by_name = {c["name"]: c for c in bs.CARDS}
    decks = {d["cover"]["name"]: d for d in bs.DECKS}
    out = [W["intro"], ""]
    for slot, names in bs.STARTER_LIST.items():
        cards = [by_name[n] for n in names]
        typ = lambda c: c["kw"].split(" · ")[0]
        if slot in ("Runes",):
            rank = lambda c: W["order"].index(typ(c)) if typ(c) in W["order"] else len(W["order"])
            cards.sort(key=lambda c: (rank(c), _key(c["name"])))
        elif slot in ("Hands", "Mains"):
            cards.sort(key=lambda c: (c.get("atk") is None, _key(c["name"])))
        heading = W["slots"].get(slot, slot)
        out += [f"#### {heading}", "", W["head"], "|---|---|---|---|---|"]
        for c in cards:
            sym = W["all"] if len(c["sym"]) == 4 else " · ".join(W["abil"][a] for a in c["sym"])
            kw = re.sub(W["drop"], "", c["kw"])
            kw = re.sub(r" \(\d+d\d+\)", "", kw)
            text = " ".join(c["text"])
            if c["name"] in decks:  # a cover prints one fact per line: keep them apart
                text = " · ".join(t.rstrip(".") for t in c["text"]) + f". {deck_line(decks[c['name']], W)}"
            text = text.replace("|", "/") or "—"
            out.append(f"| **{c['name']}** | {sym} | {kw} | {bonuses(c['strip'], W, lang)} | {text} |")
        out.append("")
    body = "\n".join(out)
    if lang == "en":
        body = body.replace(" :** ", ":** ").replace(" ; ", "; ").replace(" : ", ": ")
    return body


def sync(check=False, lang="en"):
    """Rewrite the block; return the book's name if it changed (or would change, with check)."""
    book = WORDS[lang]["book"]
    text = book.read_text(encoding="utf-8")
    if not BLOCK.search(text):
        raise SystemExit(f"No <!-- starter:start --> / <!-- starter:end --> markers in {book}")
    new = BLOCK.sub(lambda m: m[1] + table(lang) + m[2], text)
    if new == text:
        return []
    if not check:
        book.write_text(new, encoding="utf-8")
    return [book.name]


if __name__ == "__main__":
    lang = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "en"
    changed = sync(check="--check" in sys.argv, lang=lang)
    for name in changed:
        print(("Out of date: " if "--check" in sys.argv else "Synced the starter list into ") + name)
    sys.exit(1 if changed and "--check" in sys.argv else 0)
