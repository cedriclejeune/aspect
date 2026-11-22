"""Build the printable base set (cards and Slot frames) from cards/base_set.py.

Usage: .venv/bin/python tools/build_cards.py [--lang fr]
--lang fr: the French base set (cards/fr.py) in rules/fr/Porteurs-Set-de-base.pdf and rules/fr/Porteurs-Set-de-base-Lecture.pdf.
Output: rules/Bearers-Base-Set.pdf to print and rules/Bearers-Base-Set-Reading.pdf to read on screen
(and build/base-set.html, build/base-set-reading.html for inspection)
Cards are 63 × 88 mm, 9 per Letter page; Bearer, tally and foe cards 126 × 88 mm and two-sided, 4 per landscape page (a foe's back: its drawing and name, turned a quarter); Slot frames are 67 × 98 mm, 8 per landscape page.
Each card and frame is laid out at that size, then printed at PRINT_SCALE (95 %), centred in its place: the cut, at the full size, leaves a margin all round.
A card with a drawing is two-sided: gear and gold from rules/art/items/, Callings, Runes, deck cards and Wounds from
rules/art/cards/ (a Form named after a foe, and the Runes in FOE_DRAWING, use the foe's drawing). The drawing goes in place of the
text on the front, the text on the back, on facing pages printed two-sided (each back page mirrors its front page's
columns). The reading PDF shows those cards once, double width: drawing and text side by side.
Card geometry matches the tally card (P 12.3): title band 13 %, keywords 10 %, bonus strip 20 % wide.
Cards are black and white ("Ledger"): stat symbols are ink PNGs from rules/symbols/ink/ (made by tools/ink_symbols.py),
the four ability symbols sit in the top corner (the ones a card doesn't print greyed out, P 4.1), and a foe's drawing is
rules/art/<name>.png when there is one. The look by family (DESIGN 4): every card type has its symbol at the bottom left and
faint behind the text, and the family in grey under the name (Calling, Equipment, Item, Rune · its type, Spell, Power); a Calling
has a black band, Equipment a double rule under it, an Item a hatched band, a Rune its symbol before its name, and a deck
card its cover's symbol at the foot of its index. Type symbols are ink PNGs from rules/symbols/ink/, or until one is drawn
(tools/gen_symbols.py), its sketch from rules/symbols/sketch/.
Foe cards (GM 2.1) come from cards/foes.py: their totals and attacks are added up from the cards they name.
"""
import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "cards"))
import base_set as bs  # noqa: E402
import foes  # noqa: E402
import card_art  # noqa: E402
import illustrations as ill  # noqa: E402
from build_pdf import FONTS  # noqa: E402
from PIL import Image  # noqa: E402

BUILD = ROOT / "build"
def _arg(name, default):
    return float(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


# The two-sided pages' backs (cards and the landscape wide cards alike) move this far (mm, as seen on the back: + right, + down) to make up for a printer whose
# duplex unit prints the back off its front. Measured with rules/fr/calibrage-recto-verso.pdf; --back-dx, --back-dy override.
BACK_SHIFT = (_arg("--back-dx", -2.0), _arg("--back-dy", 0.25))  # the Xerox, measured with the calibration sheet
PRINT_SCALE = .95  # cards and frames print this much smaller, centred where the Cricut cut files (tools/cut_svg.py) cut them
OUT = ROOT / "rules" / "Bearers-Base-Set.pdf"
READING = ROOT / "rules" / "Bearers-Base-Set-Reading.pdf"
SYMBOLS = ROOT / "rules" / "symbols" / "ink"
ART = ROOT / "rules" / "art"
ITEM_ART = ART / "items"
CARD_ART = ART / "cards"

ROWS = ["STR", "DEX", "INT", "WIL", "STRd", "DEXd", "INTd", "WILd", "HP", "SPD"]
SYM_FILE = {"STR": "str", "DEX": "dex", "INT": "int", "WIL": "wil", "STRd": "str-def", "DEXd": "dex-def", "INTd": "int-def",
            "WILd": "wil-def", "HP": "hp", "SPD": "spd"}
SKETCHES = ROOT / "rules" / "symbols" / "sketch"  # stand-ins until tools/gen_symbols.py draws the ink symbol
TYPE_SYMBOL = {t: t.lower() for t in ("Calling", "Armor", "Weapon", "Shield", "Jewelry", "Instrument", "Consumable", "Container",
                                      "Recipe", "Spellbook", "Trait", "Technique", "Divine", "Glamour", "Nature", "Pact")}
TYPE_SYMBOL["Domain"] = "knack"  # the symbol file keeps the name the type had before it became Domain
FAMILY = {"Calling": "calling", **dict.fromkeys(("Armor", "Weapon", "Shield", "Jewelry", "Instrument"), "equip"),
          **dict.fromkeys(("Consumable", "Container", "Recipe", "Spellbook", "Runestone"), "item"),
          **dict.fromkeys(("Trait", "Technique", "Domain", "Divine", "Glamour", "Nature", "Pact"), "aspect")}  # "aspect": the Rune family
SUBTITLE = {"calling": "Calling", "equip": "Equipment", "item": "Item", "aspect": "Rune", "spell": "Spell", "power": "Power"}  # GLOSSARY: gear is equipment or items
DESCRIPTIVE = set()  # keywords that describe without a rule: printed grey on the second keyword line (none yet)

# Words the builder writes itself (the cards' own text comes from cards/base_set.py, or cards/fr.py in French).
UI = {
    "en": dict(lang="en", to_hit="to hit", or_="or", abil={"STR": "STR", "DEX": "DEX", "INT": "INT", "WIL": "WIL"},
               ranged=("Thrown", "Range"), uses=r"\d+/[SL]\.R\.", recharge="Recharge {n}–6", also="Also carries ",
               drops="Drops: ", foe="Foe", boss="Boss", leader="Leader", set_foe="FOE", gp="gp", gold="Gold",
               groups={}, coin="In a Purse, it takes no room. Loose, it is a bag of coins: 1 piece.",
               blank=("Body", "Attacks", "Powers", "Drops"), blank_kw="Foe · size · senses",
               sizes={}, senses=lambda x: x, sub=SUBTITLE),
    "fr": dict(lang="fr", to_hit="au toucher", or_="ou", abil={"STR": "FOR", "DEX": "AGI", "INT": "INT", "WIL": "VOL"},
               ranged=("Lancer", "Portée"), uses=r"\d+/R\.[CL]\.", recharge="Recharge {n}–6", also="Porte aussi ",
               drops="Butin : ", foe="Adversaire", boss="Boss", leader="Meneur", set_foe="ADVERSAIRE", gp="po", gold="Or",
               groups={"STARTER": "DÉPART", "LOOT": "BUTIN", "WOUND": "BLESSURE"},
               coin="Dans une Bourse, il ne prend pas de place. En vrac, c'est un sac de pièces : 1 pièce.",
               blank=("Corps", "Attaques", "Pouvoirs", "Butin"), blank_kw="Adversaire · taille · sens",
               sizes={"Tiny": "Très petit", "Small": "Petit", "Medium": "Moyen", "Large": "Grand"}, senses=None,
               sub={"calling": "Vocation", "equip": "Équipement", "item": "Objet", "aspect": "Rune", "spell": "Sort", "power": "Pouvoir"}),
}
T = UI["en"]

CSS = f"""
@page {{ size: Letter; margin: 0; }}
@page frames {{ size: Letter landscape; margin: 0; }}
html {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ margin: 0; font-family: 'EB Garamond', Georgia, serif; color: {ill.INK}; }}
.sheet {{ width: 215.9mm; height: 279.4mm; display: grid; grid-template-columns: repeat(3, 63mm); grid-auto-rows: 88mm;
  gap: 2mm; justify-content: center; align-content: center; break-after: page; overflow: hidden; }}
.sheet.foes {{ grid-template-columns: 126mm; }}
.sheet.wide4 {{ page: frames; width: 279.4mm; height: 215.9mm; grid-template-columns: repeat(2, 126mm); }}
.sheet.frames {{ page: frames; width: 279.4mm; height: 215.9mm; grid-template-columns: repeat(4, 67mm); grid-auto-rows: 98mm; gap: 0; }}
.sheet.frames svg {{ width: 67mm; height: 98mm; display: block; }}
.sheet > .card:not(.gap), .sheet.frames > svg {{ transform: scale({PRINT_SCALE}); }}  /* centred in the unchanged cut, for a margin all round */
.sheet.back > * {{ translate: {BACK_SHIFT[0]}mm {BACK_SHIFT[1]}mm; }}
.intro {{ width: 215.9mm; height: 279.4mm; box-sizing: border-box; padding: 22mm 24mm; break-after: page; background: {ill.PARCH}; }}
.intro h1 {{ font-family: Cinzel, serif; color: {ill.CRIMSON}; font-size: 30pt; margin: 0; letter-spacing: .08em; }}
.intro h2 {{ font-family: Cinzel, serif; color: {ill.CRIMSON}; font-size: 13pt; margin: 14pt 0 4pt; border-bottom: 1.5px solid {ill.GOLD}; }}
.intro p, .intro li {{ font-size: 11pt; line-height: 1.35; margin: 0 0 4pt; }}
.intro table {{ border-collapse: collapse; font-size: 10pt; width: 100%; }}
.intro td {{ padding: 2pt 6pt; border-bottom: 1px solid #e0cfa6; vertical-align: top; }}
.intro td:first-child {{ font-family: Cinzel, serif; font-size: 9pt; white-space: nowrap; }}

.card {{ position: relative; width: 63mm; height: 88mm; box-sizing: border-box; border: .35mm solid #000; border-radius: 3mm;
  background: #fff; color: #000; overflow: hidden; }}
.band {{ position: absolute; left: 0; right: 0; top: 0; height: 11.44mm; background: #fff; color: #000;
  display: flex; align-items: center; padding: 0 10mm 0 2.4mm; box-sizing: border-box; border-bottom: .7mm solid #000;
  font-family: Cinzel, serif; font-weight: 700; line-height: 1.05; letter-spacing: .04em; }}
.band .rank {{ position: absolute; right: 1.6mm; top: 50%; transform: translateY(-50%); width: 7.1mm; height: 9.4mm; }}
.band .rank svg {{ width: 100%; height: 100%; display: block; }}
.band.syms {{ padding-right: 18.4mm; }}
.band .sym4 {{ position: absolute; right: 10mm; top: 50%; transform: translateY(-50%); display: grid; grid-template-columns: 3.5mm 3.5mm;
  gap: .3mm; }}
.band .sym4 img {{ width: 3.5mm; height: 3.5mm; display: block; }}
.band .sym4 .off {{ opacity: .18; }}
.band.norank {{ padding-right: 10mm; }}
.band.norank .sym4 {{ right: 2mm; }}
.band .lvl {{ position: absolute; right: 2mm; top: 50%; transform: translateY(-50%); font-size: 6.6pt; font-family: 'EB Garamond', serif; font-style: italic; font-weight: 400; letter-spacing: 0; }}
.strip {{ position: absolute; right: 0; top: 11.44mm; bottom: 8.8mm; width: 12.6mm; background: #fff;
  border-left: .3mm solid #000; display: grid; grid-template-rows: repeat(10, 1fr); }}
.strip div {{ display: flex; align-items: center; justify-content: space-between; padding: 0 .7mm; border-top: .12mm solid #b5b5b5; }}
.strip div:first-child {{ border-top: 0; }}
.strip div:nth-child(5), .strip div:nth-child(9) {{ border-top: .3mm solid #000; }}
.strip img {{ width: 4.8mm; height: 4.8mm; }}
.strip .off img {{ opacity: .28; }}
.strip b {{ font-family: Cinzel, serif; font-size: 7.4pt; color: #000; }}
.body {{ position: absolute; left: 0; right: 12.6mm; top: 11.44mm; bottom: 8.8mm; padding: 2mm 2.2mm; box-sizing: border-box;
  display: flex; flex-direction: column; justify-content: center; gap: 1.4mm; }}
.body p {{ margin: 0; line-height: 1.2; }}
.body .art {{ display: flex; justify-content: center; opacity: .9; }}
.body .main {{ flex: 1 0 auto; display: flex; flex-direction: column; justify-content: center; gap: 1.4mm; }}
.body .lore {{ font-size: 7.4pt; font-style: italic; line-height: 1.15; color: #555; text-align: center; }}
.wide .body {{ right: 0; }}
.deck .body {{ left: 8mm; }}
.index {{ position: absolute; left: 0; top: 11.44mm; bottom: 8.8mm; width: 8mm; border-right: .25mm solid #000;
  background: #fff; display: flex; flex-direction: column; align-items: center; padding-top: 1.6mm; gap: 2mm; }}
.index .cost {{ width: 6mm; height: 6mm; border-radius: 50%; background: #000; color: #fff; display: flex;
  align-items: center; justify-content: center; font-family: Cinzel, serif; font-weight: 700; font-size: 9pt; }}
.index .name {{ writing-mode: vertical-rl; transform: rotate(180deg); font-family: Cinzel, serif; font-size: 6.4pt; color: #555;
  white-space: nowrap; }}
.kw {{ position: absolute; left: 0; right: 0; bottom: 0; height: 8.8mm; border-top: .3mm solid #000; display: flex;
  align-items: center; justify-content: flex-start; gap: 1.4mm; padding: 0 19mm 0 2.4mm; box-sizing: border-box;
  font-style: italic; font-weight: 600; font-size: 7.6pt; line-height: 1.1; }}
.kw img {{ width: 4.4mm; height: 4.4mm; flex: none; }}
.band .ttl {{ display: flex; flex-direction: column; min-width: 0; gap: .35mm; }}
.band .pre {{ font-family: 'EB Garamond', serif; font-weight: 600; font-size: 6.4pt; line-height: 1; letter-spacing: .02em;
  margin-bottom: .1mm; }}
.band .sub {{ font-family: 'EB Garamond', serif; font-style: italic; font-weight: 600; letter-spacing: .02em; color: #000;
  font-size: 7.4pt; line-height: 1.05; }}
.band .bsym {{ width: 4.6mm; height: 4.6mm; flex: none; margin-right: 1.2mm; }}
.band .bsym img {{ width: 100%; height: 100%; display: block; }}
.f-calling .band {{ background: #000; color: #fff; }}
.f-calling .band .sub {{ color: #fff; }}
.f-calling .band .sym4 img {{ filter: invert(1); }}
.f-calling .band .sym4 .off {{ opacity: .5; }}
.f-equip .band {{ border-bottom: 1.3mm double #000; }}
.f-item .band, .deck.src-item .index {{ background: repeating-linear-gradient(135deg, #fff 0 .9mm, #e6e6e6 .9mm 1.15mm); }}
.body .wm {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; pointer-events: none; }}
.body .wm img {{ width: 30mm; height: 30mm; opacity: .075; }}
.body .main, .body .lore {{ position: relative; }}
.index .isym {{ margin-top: auto; margin-bottom: 1.6mm; width: 5mm; height: 5mm; flex: none; }}
.index .isym img {{ width: 100%; height: 100%; display: block; }}
.kw .kl {{ flex: 1; min-width: 0; display: flex; flex-direction: column; justify-content: center; gap: .4mm; max-height: 100%; }}
.kw .k1, .kw .k2 {{ display: block; overflow: hidden; line-height: 1.12; }}
.kw .kn {{ white-space: nowrap; }}
.kw .k1 {{ font-size: 8.2pt; max-height: 8.2mm; }}
.kw .kl:has(.k2) .k1 {{ max-height: 4.6mm; }}
.kw .k2 {{ font-size: 6.8pt; opacity: .55; max-height: 3.8mm; }}
.set {{ position: absolute; right: 2mm; bottom: 3.3mm; font-family: Cinzel, serif; font-weight: 600; font-size: 4.6pt; color: #000; letter-spacing: .05em; }}
.coin {{ display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2mm; }}
.coin svg {{ width: 30mm; height: 30mm; }}
.card.tally {{ width: 126mm; }}
.tally svg {{ width: 126mm; height: 88mm; display: block; }}
.tally {{ border: 0; border-radius: 0; background: none; }}
.card.foe {{ width: 126mm; }}
.foe .pic {{ position: absolute; left: 0; top: 11.44mm; bottom: 8.8mm; width: 50mm; border-right: .3mm solid #000;
  background: #fff; display: flex; align-items: center; justify-content: center; overflow: hidden; }}
.foe .pic img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.foe .pic svg {{ width: 42mm; height: 42mm; }}
.foe .body {{ left: 50mm; justify-content: flex-start; gap: .9mm; }}
.foe.back {{ overflow: hidden; }}
.foe.back .rot {{ position: absolute; left: 0; top: 87.3mm; width: 87.3mm; height: 125.3mm; transform-origin: 0 0; transform: rotate(-90deg); }}
.foe.back .pic {{ width: auto; right: 0; bottom: 0; border-right: 0; border-radius: 0 0 3mm 3mm; padding: 2mm; box-sizing: border-box; }}
.foe.back .pic img {{ object-fit: contain; }}
.foe.back .pic svg {{ width: 76mm; height: 76mm; }}
.foe .tag {{ position: absolute; right: 2mm; top: 3.4mm; font-size: 6.4pt; font-family: 'EB Garamond', serif; font-style: italic; font-weight: 400; }}
.foe .ids {{ font-size: 6.4pt; color: #555; }}
.card .art {{ position: absolute; left: 0; right: 12.6mm; top: 11.44mm; bottom: 8.8mm; padding: 1.4mm; box-sizing: border-box;
  display: flex; align-items: center; justify-content: center; }}
.card .art img {{ width: 100%; height: 100%; object-fit: contain; display: block; }}
.card.read {{ width: 126mm; }}
.read .art {{ right: auto; width: 63mm; border-right: .3mm solid #000; }}
.read .body {{ left: 63mm; }}
.card .art.full {{ right: 0; }}
.pair {{ display: flex; gap: 0; width: 126mm; }}
.pair .card + .card {{ border-left: 0; border-top-left-radius: 0; border-bottom-left-radius: 0; }}
.pair .card:first-child {{ border-top-right-radius: 0; border-bottom-right-radius: 0; }}
.gap {{ visibility: hidden; }}
.blank .line {{ border-bottom: .2mm solid #999; height: 4.2mm; font-size: 6pt; color: {ill.MUTED}; font-style: italic; }}
"""


def md(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)


def fit(text, room):
    """Font size (pt) for the effect text: shrink as it grows."""
    n = sum(len(t) for t in text) + 25 * (len(text) - 1)
    return 9.4 if n < 90 else 8.8 if n < 170 else 8.2 if n < 250 else 7.7 if n < 330 else 7.2


def print_image(src):
    """A drawing as a print-sized copy (BUILD/img): 760 px wide is about 380 ppi on a 50 mm card picture, and a
    grayscale JPEG keeps the PDF light. The source PNG is left as it is."""
    out = BUILD / "img" / src.relative_to(ART).with_suffix(".jpg")
    if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
        out.parent.mkdir(parents=True, exist_ok=True)
        im = Image.open(src).convert("L")
        im.thumbnail((760, 1600), Image.LANCZOS)
        im.save(out, quality=85, optimize=True)
    return out.as_uri()


def symbol(name, alt=""):
    return f'<img src="{(SYMBOLS / f"{name}.png").as_uri()}" alt="{alt}">'


def printed(kw):
    """The keywords as the card prints them: never what the card's text already says (DESIGN 4). A range (Range N/M,
    Thrown N/M, a spell's Range N) is in the attack or casting line, and a Versatile weapon's bigger die is in its damage."""
    parts = [p for p in kw.split(" · ") if not p.startswith(("Range ", "Thrown ", "Portée ", "Lancer "))]
    return " · ".join(re.sub(r"^(Versatile|Polyvalente) \(.*\)$", r"\1", p) for p in parts)


def en_type(kind):
    """The English name of a card type (the French build prints "Arme", the tables are keyed by "Weapon")."""
    return T.get("type_en", {}).get(kind, kind)


def type_symbol(kind):
    """The card type's symbol: the ink drawing, or its sketch until one is drawn; "" for a type without one."""
    name = TYPE_SYMBOL.get(en_type(kind))
    path = next((p for p in (SYMBOLS / f"{name}.png", SKETCHES / f"{name}.svg") if name and p.exists()), None)
    return f'<img src="{path.as_uri()}" alt="">' if path else ""


def keywords(kw, sub=None):
    """The keyword line: the type's symbol at the left, then two lines: the type and rule keywords, then the descriptive
    ones in grey. The type is left out when the subtitle already says it (a Calling). FIT_LORE shrinks each line to fit."""
    parts = printed(kw).split(" · ")
    sym = type_symbol(parts[0])
    if parts[0] == sub:
        parts = parts[1:]
    rule, desc = [p for p in parts if p not in DESCRIPTIVE], [p for p in parts if p in DESCRIPTIVE]
    join = lambda ps: " · ".join(f'<span class="kn">{md(p)}</span>' for p in ps)  # a wrapped line breaks between keywords only
    lines = f'<span class="k1">{join(rule)}</span>' + (f'<span class="k2">{join(desc)}</span>' if desc else "")
    return f'<div class="kw">{sym}<span class="kl">{lines}</span></div>'


def family(kind):
    """(family, subtitle) of a card type."""
    fam = FAMILY.get(en_type(kind), "")
    return fam, T["sub"].get(fam)


def watermark(kind):
    sym = type_symbol(kind)
    return f'<div class="wm">{sym}</div>' if sym else ""


def lore(c):
    """The lore line (DESIGN 4), printed at the bottom of the effect area if space permits (FIT_LORE)."""
    return f'<p class="lore">{md(c["lore"])}</p>' if c.get("lore") else ""


FIT_LORE = """<script>document.fonts.ready.then(() => {
  const fits = e => e.scrollWidth <= e.clientWidth + 1 && e.scrollHeight <= e.clientHeight + 1;
  const size = (e, pt) => { e.style.fontSize = pt + 'pt'; return pt; };
  document.querySelectorAll('.kw .k1, .kw .k2').forEach(e => {  // one line, smaller; then two lines, smaller still
    const two = e.classList.contains('k2');
    let pt = size(e, two ? 6.8 : 8.2); e.style.whiteSpace = 'nowrap';
    while (!fits(e) && pt > (two ? 5.6 : 6.4)) pt = size(e, +(pt - .2).toFixed(1));
    if (fits(e)) return;
    e.style.whiteSpace = 'normal'; pt = size(e, two ? 5.8 : 6.6);
    while (!fits(e) && pt > (two ? 4.6 : 5.2)) pt = size(e, +(pt - .2).toFixed(1));
  });
  document.querySelectorAll('.body .lore').forEach(l => {
    const b = l.parentNode, over = () => b.scrollHeight > b.clientHeight + 1;  // shrink before giving up
    for (let pt = 7.4; over() && pt > 6.4; ) { pt = +(pt - .2).toFixed(1); l.style.fontSize = pt + 'pt'; }
    if (over()) l.remove();
  });
  document.querySelectorAll('.intro').forEach(s => {  // the intro stays on its one page (the French text runs longer)
    const parts = [...s.querySelectorAll('p, li, td, h2')].map(e => [e, parseFloat(getComputedStyle(e).fontSize)]);
    for (let k = 1; s.scrollHeight > s.clientHeight + 1 && k > .75; ) {
      k = +(k - .02).toFixed(2);
      parts.forEach(([e, px]) => { e.style.fontSize = px * k + 'px'; });
    }
  });
});</script>"""


def rank_mark(rank):
    """The Rank carved as a branch rune in a stone (one branch per Rank, P 4.1)."""
    return (f'<span class="rank"><svg viewBox="0 0 21 28" role="img" aria-label="Rank {rank}">{ill.rank_rune(rank, "#000", "#fff")}</svg></span>'
            if rank else "")


def strip(values, own=False):
    rows = []
    for key in ROWS:
        v = values.get(key)
        if v and key == "SPD" and T["lang"] == "fr":
            import i18n_fr
            v = i18n_fr.signed_feet(v)
        rows.append(f'<div class="{"" if v or own else "off"}">{symbol(SYM_FILE[key], key)}{f"<b>{v}</b>" if v else ""}</div>')
    return f'<div class="strip{" own" if own else ""}">{"".join(rows)}</div>'


def sym4(sym):
    """The four ability symbols in a 2 × 2 grid, those the card doesn't print greyed out (P 4.1)."""
    return '<span class="sym4">' + "".join(
        f'<span class="{"" if a in sym else "off"}">{symbol(SYM_FILE[a], a if a in sym else "")}</span>'
        for a in ("STR", "DEX", "INT", "WIL")) + "</span>"


def band(name, right, sym=None, sub=None, lead="", pre=""):
    """sub: the family in grey under the name; lead: a symbol before the name (a Rune's type); pre: small words above
    the name (a Rune's "Rune of the", DESIGN 1b)."""
    size = 9.2 if len(name) <= 14 else 8 if len(name) <= 18 else 7
    if sym:
        size = min(size, 8.4 if len(name) <= 12 else 7.4 if len(name) <= 16 else 6.6)
    title = html.escape(name.upper())
    if sub:
        pre = f'<span class="pre">{html.escape(pre)}</span>' if pre else ""
        title = f'<span class="ttl">{pre}<span class="nm">{title}</span><span class="sub">{sub}</span></span>'
    lead = f'<span class="bsym">{lead}</span>' if lead else ""
    return (f'<div class="band{" syms" if sym else ""}{" norank" if sym and not right else ""}" style="font-size:{size}pt">{lead}{title}'
            f'{sym4(sym) if sym else ""}{right}</div>')


def slug(name):
    return name.lower().replace(" ", "-")


FOE_DRAWING = {"Campaign": "orc", "Discipline": "hobgoblin"}  # Runes drawn as a foe that carries them


def drawing(name, kind):
    """The card's drawing, or None: gear and gold in rules/art/items/, the rest in rules/art/cards/ (a deck card named
    after a foe, and a Rune in FOE_DRAWING, use the foe's drawing in rules/art/)."""
    if name in FOE_DRAWING and (ART / f"{FOE_DRAWING[name]}.png").exists():
        return ART / f"{FOE_DRAWING[name]}.png"
    folders = [ITEM_ART] if kind in ("gear", "gold") else [CARD_ART] + ([ART] if kind == "deck" else [])
    return next((f / f"{slug(name)}.png" for f in folders if (f / f"{slug(name)}.png").exists()), None)


def item_drawing(c):
    return drawing(c.get("key", c["name"]), c["kind"])


RUNE_NAMES = {c["name"] for c in bs.ASPECTS}  # deck covers (Repertoire, Litany, Instinct) print no "Rune of"


def rune_of(c):
    """'Rune of the' / 'Rune du' printed above a Rune card's name, or "" for a deck cover."""
    key = c.get("key", c["name"])
    if key not in RUNE_NAMES:
        return ""
    if T["lang"] == "fr":
        import fr
        return fr.rune_de(c["name"])
    return bs.rune_of(key)


def item_card(c, group, face="text"):
    """face: "text" (the card as rules text), "art" (the front of a two-sided card: its drawing in place of the text),
    "read" (double width, drawing and text side by side)."""
    paras = "".join(f"<p>{md(t)}</p>" for t in c["text"])
    kind = c["kw"].split(" · ")[0]
    fam, sub = family(kind)
    typed = kind if fam == "aspect" else sub  # the type the subtitle already says: left out of the keyword line
    if fam == "aspect":
        sub = f"{sub} · {kind}"  # a Rune's type line: "Rune · Trait"
    art = f'<div class="art"><img src="{print_image(item_drawing(c))}" alt=""></div>' if face != "text" else ""
    body = "" if face == "art" else (f'<div class="body" style="font-size:{fit(c["text"], "")}pt">{watermark(kind)}'
                                     f'<div class="main">{paras}</div>{lore(c)}</div>')
    sym = c["sym"] if c["kind"] in ("gear", "aspect", "calling") else None
    lead = type_symbol(kind) if fam == "aspect" else ""
    pre = rune_of(c) if fam == "aspect" else ""
    if pre:
        sub = kind  # "Rune of the" above the name already says Rune: the line under it gives the type alone
    return (f'<div class="card f-{fam}{" read" if face == "read" else ""}">{band(c["name"], rank_mark(c["rank"]), sym, sub, lead, pre)}{art}'
            f'{strip(c["strip"], own=c["kind"] == "calling")}{body}'
            f'{keywords(c["kw"], typed)}<div class="set">{T["groups"].get(group, group)}{" · " + c["id"] if c.get("id") else ""}</div></div>')


def deck_card(s, deck, face="text"):
    """face: "text", "art" (the drawing in place of the index and text) or "read" (the two side by side)."""
    if face == "read":
        return f'<div class="pair">{deck_card(s, deck, "art")}{deck_card(s, deck)}</div>'
    cover = deck["cover"]
    source = cover["kw"].split(" · ")[0]  # the cover's type: its symbol marks the deck's cards
    sub = T["sub"]["spell" if en_type(source) == "Spellbook" else "power"]
    has_strip = bool(s["strip"]) or s["level"] == "Form"
    level = f'<span class="lvl">{s["level"]}</span>'
    if face == "art":
        return (f'<div class="card">{band(s["name"], level, sub=sub)}<div class="art{"" if has_strip else " full"}">'
                f'<img src="{print_image(drawing(s.get("key", s["name"]), "deck"))}" alt=""></div>'
                f'{strip(s["strip"]) if has_strip else ""}{keywords(s["kw"])}</div>')
    paras = "".join(f"<p>{md(t)}</p>" for t in s["text"])
    src = " src-item" if FAMILY.get(en_type(source)) == "item" else ""
    isym = type_symbol(source)
    return (f'<div class="card deck{src}{"" if has_strip else " wide"}">{band(s["name"], level, sub=sub)}'
            f'<div class="index"><div class="cost">{s["cost"]}</div><div class="name">{html.escape(cover["name"])}</div>'
            f'{f"<span class=isym>{isym}</span>" if isym else ""}</div>'
            f'{strip(s["strip"]) if has_strip else ""}'
            f'<div class="body" style="font-size:{fit(s["text"], "deck")}pt">{watermark(source)}<div class="main">{paras}</div>{lore(s)}</div>'
            f'{keywords(s["kw"])}</div>')


def total(values):
    """Add up strip values ("+2", "−10", "14") row by row."""
    out = {}
    for strip_ in values:
        for k, v in strip_.items():
            out[k] = out.get(k, 0) + int(str(v).replace("−", "-").rstrip("*"))  # "+1*": a conditional bonus, counted
    return out


def signed(n):
    return f"+{n}" if n >= 0 else f"−{-n}"


def more_dice(dice, n):
    return re.sub(r"(\d+)d(\d+)", lambda m: f"{int(m[1]) + n}d{m[2]}", dice)


def _abil():
    """The four ability abbreviations as printed (FOR/AGI/VOL in French), and a lookup back to the English keys."""
    back = {v: k for k, v in T["abil"].items()}
    return "(" + "|".join(back) + ")", back


def resolve(text, mods):
    """Write a foe's numbers into card text: "WIL + 2" → "+5", "3 + WIL" → "6", "2d4 + WIL" → "2d4 + 3"."""
    ABIL, back = _abil()
    m_ = lambda a: mods[back[a]]
    text = re.sub(rf"(\d+d\d+) \+ {ABIL}\b", lambda m: f"{m[1]} + {m_(m[2])}", text)
    text = re.sub(rf"\b{ABIL}(?: {T['or_']} {ABIL})? \+ (\d+)\b",
                  lambda m: signed(max(m_(a) for a in (m[1], m[2]) if a) + int(m[3])), text)
    return re.sub(rf"\b(\d+) \+ {ABIL}\b", lambda m: str(int(m[1]) + m_(m[2])), text)


def pool(text, mods):
    """A deck cover's pool on a foe card, as its tally total (P 12.3): "Resolve: **+3**" → "Resolve: **6**" (+ WIL, min 1)."""
    return re.sub(r"(Spell points|Resolve): \*\*\+(\d+)\*\*",
                  lambda m: f"{m[1]}: **{max(1, int(m[2]) + mods['INT' if m[1] == 'Spell points' else 'WIL'])}**", text)


def foe_attack(c, mods, extra_dice):
    """A weapon card's line on a foe card: the foe's modifier added in, plain-text dice included."""
    ab, back = _abil()
    ab = ab[1:-1]
    m = re.match(rf"([+−-]\d+) {T['to_hit']}, (.+?) \+ ((?:{ab})(?: {T['or_']} (?:{ab}))*) (\w+)\.\s*(.*)", c["text"][0])
    hit, dice, attr, dtype, effect = m.groups()
    mod = max(mods[back[a]] for a in attr.split(f" {T['or_']} "))
    dmg_mod = f" + {mod}" if mod >= 0 else f" − {-mod}"
    colon = " :" if T["lang"] == "fr" else ":"
    line = (f'*{c["name"]}*{colon} {signed(int(hit.replace("−", "-")) + mod)} {T["to_hit"]}, '
            f'{more_dice(dice, extra_dice)}{dmg_mod} {dtype}.')
    return line + (f" {effect}" if effect else "")


def foe_lines(f):
    """Totals and text of a foe card, from the cards it names (cards/foes.py)."""
    *mods_, hp, spd, size = f["body"]
    cards = [bs.BY_NAME[n] for n in f["carries"]]
    sums = total([bs.body(mods_, hp, spd)] + [c["strip"] for c in cards] + [f["bonus"]])
    mods = {k: sums.get(k, 0) for k in ("STR", "DEX", "INT", "WIL")}
    values = {k: signed(v) if k in mods else str(v) for k, v in sums.items()}
    lines = list(f["own"])
    also = []
    colon = " :" if T["lang"] == "fr" else ":"
    for c in cards:
        key = c.get("key", c["name"])
        kind = c["kw"].split(" · ")[0]
        deck = next((d for d in bs.DECKS if d["cover"] is c), None)
        n = f["recharge"].get(key)
        if kind in ("Weapon", "Arme"):
            extra = f["extra_dice"]
            lines.append(foe_attack(c, mods, extra.get(key, 0) if isinstance(extra, dict) else extra))
        elif kind in ("Armor", "Shield", "Container", "Armure", "Bouclier", "Contenant"):
            also.append(f'*{c["name"]}*')
        elif deck:
            lines.append(f'*{c["name"]}*{colon} ' + " · ".join(resolve(pool(t, mods), mods) for t in c["text"][:2]))
            lines += [f'**{p["name"]}** ({p["cost"]}){colon} ' + resolve(" ".join(p["text"]), mods)
                      for p in deck["cards"] if p.get("key", p["name"]) in f["powers"]]
        else:
            text = resolve(" ".join(c["text"]), mods)
            if n:  # the foe's plain text turns the card's limited uses into Recharge n–6
                text = re.sub(T["uses"], T["recharge"].format(n=n), text, count=1)
            lines.append(f'*{c["name"]}*{colon} ' + text)
    if also:
        lines.append(T["also"] + ", ".join(also) + ".")
    senses = f["senses"]
    if senses and T["lang"] == "fr":
        import fr
        senses = fr.keyword(senses)
    kw = " · ".join([T["foe"]] + ([T["boss"]] if f["boss"] else []) + ([T["leader"]] if f["leader"] else [])
                    + [T["sizes"].get(size, size)] + ([senses] if senses else []))
    return values, lines, kw, T["drops"] + " · ".join(f'*{c["name"]}* ({c["id"]})' for c in cards)


def foe_card(f):
    values, lines, kw, ids = foe_lines(f)
    tag = f'<span class="tag">{T["boss"] if f["boss"] else T["foe"]}</span>'
    drawing = ART / f'{f["name"].lower().replace(" ", "-")}.png'
    art = f'<img src="{print_image(drawing)}" alt="">' if drawing.exists() else card_art.foe_art(f["name"]) or ""
    paras = "".join(f"<p>{md(t)}</p>" for t in lines)
    size = 7.4 if sum(len(t) for t in lines) + 25 * (len(lines) - 1) > 760 else fit(lines, "") + 1  # the longest foe cards
    name = f["name"]
    if T["lang"] == "fr":
        import fr
        name = fr.NAMES[name]
    return (f'<div class="card foe">{band(name, tag)}<div class="pic">{art}</div>{strip(values, own=True)}'
            f'<div class="body" style="font-size:{size}pt">{paras}<p class="ids">{md(ids)}</p></div>'
            f'<div class="kw">{kw}</div><div class="set">{T["set_foe"]}</div></div>')


def foe_back(f):
    """A foe card's back: its name in the title band and its drawing, large, turned a quarter so the drawing gets
    the card's length."""
    drawing = ART / f'{f["name"].lower().replace(" ", "-")}.png'
    art = f'<img src="{print_image(drawing)}" alt="">' if drawing.exists() else card_art.foe_art(f["name"]) or ""
    name = f["name"]
    if T["lang"] == "fr":
        import fr
        name = fr.NAMES[name]
    return f'<div class="card foe back"><div class="rot">{band(name, "")}<div class="pic">{art}</div></div></div>'


def blank_foe_card():
    b, a, p, d = T["blank"]
    tag = f'<span class=tag>{T["foe"]}</span>'
    rows = "".join(f'<div class="line">{t}</div>' for t in (b, a, "", "", p, "", "", "", d, "", ""))
    return (f'<div class="card foe blank">{band("", tag)}<div class="pic"></div>{strip({}, own=True)}'
            f'<div class="body">{rows}</div><div class="kw">{T["blank_kw"]}</div><div class="set">{T["set_foe"]}</div></div>')


def money(value):
    """1,000 gp (1 000 po in French)."""
    return f"{value:,} gp" if T["lang"] == "en" else f"{value:,}".replace(",", "\u202f") + " po"


def gold_card(value, face="text"):
    if face == "read":
        return f'<div class="pair">{gold_card(value, "art")}{gold_card(value)}</div>'
    if face == "art":
        return (f'<div class="card">{band(money(value), "")}<div class="art full">'
                f'<img src="{print_image(drawing(f"{value:,} gp", "gold"))}" alt=""></div>{keywords(T["gold"])}</div>')
    coin = ill._svg(40, 40, '<circle cx="20" cy="20" r="17" fill="#000" stroke="#000" stroke-width="1.6"/>'
                    '<circle cx="20" cy="20" r="13.5" fill="none" stroke="#fff" stroke-width=".8"/>'
                    + ill._text(20, 24.5, money(value).split(" ")[0] if T["lang"] == "en" else money(value)[:-3], 12 if value < 1000 else 9.5, ill.HEAD, "#fff"), "gold")
    return (f'<div class="card wide">{band(money(value), "")}'
            f'<div class="body coin">{coin}<p style="font-size:8pt;text-align:center"><i>{T["coin"]}</i></p></div>'
            f'{keywords(T["gold"])}</div>')


def tally_card():
    return f'<div class="card tally">{ill._svg(600, 419, ill.tally_small(0, 0, 600, 419, {}, ledger=True), "Tally card")}</div>'


def bearer_card(back=False):
    return f'<div class="card tally">{ill._svg(600, 419, ill.bearer_small(0, 0, 600, 419, back), "Bearer card")}</div>'


def sheets(cards, cls="", per=9):
    return "".join(f'<section class="sheet {cls}">{"".join(cards[i:i + per])}</section>' for i in range(0, len(cards), per))


def duplex(pairs):
    """Two-sided cards as a front page and a back page, 9 a sheet. Flipped on the long edge, each row's columns swap
    sides, so the back page lists each row in reverse."""
    gap = '<div class="card gap"></div>'
    out = []
    for i in range(0, len(pairs), 9):
        chunk = pairs[i:i + 9] + [(gap, gap)] * (9 - len(pairs[i:i + 9]))
        backs = [b for r in range(0, 9, 3) for _, b in reversed(chunk[r:r + 3])]
        out.append(sheets([f for f, _ in chunk]) + sheets(backs, "back"))
    return "".join(out)


def build_cards(reading=False):
    """The single cards, and the two-sided ones as (front, back) pairs; reading: those as double-width cards instead."""
    out, pairs, wide = [], [], []

    dropped = {n for f in foes.FOES for n in f["carries"]}  # one extra copy of each card a foe drops

    def put(drawn, face, n):
        """face(f): the card's "text", "art" or "read" face."""
        if not drawn:
            out.extend([face("text")] * n)
        elif reading:
            wide.append(face("read"))  # once: the reading PDF is a catalogue, not a print run
        else:
            pairs.extend([(face("art"), face("text"))] * n)

    def add(c, n=None, group=None):
        group = group or c["group"].upper()
        put(item_drawing(c), lambda f: item_card(c, group, f), n or c["copies"] + (c.get("key", c["name"]) in dropped))
    for c in bs.CALLINGS + bs.ARMOR + bs.HANDS + bs.JEWELRY + bs.ITEMS:
        add(c)
    for c in bs.ASPECTS:
        add(c)
    for deck in bs.DECKS:
        add(deck["cover"], 1)
        for s in deck["cards"]:
            put(drawing(s.get("key", s["name"]), "deck"), lambda f, s=s, deck=deck: deck_card(s, deck, f), 1)
    for value, n in bs.GOLD:
        put(drawing(f"{value:,} gp", "gold"), lambda f, value=value: gold_card(value, f), n)
    for w in bs.WOUNDS:
        add(w, 1, "WOUND")
    return out, wide if reading else pairs


def build_foes():
    """Double-width foe cards as (front, back) pairs: the stats, then the drawing and name."""
    blank_back = '<div class="card foe back"><div class="rot">' + band("", "") + '<div class="pic"></div></div></div>'
    return [(foe_card(f), foe_back(f)) for f in foes.FOES] + [(blank_foe_card(), blank_back)] * foes.BLANKS


def build_tallies():
    """Double-width tally cards, the same on both faces, as (front, back) pairs."""
    return [(tally_card(), tally_card())] * bs.TALLIES


def build_bearers():
    """Double-width Bearer cards, one per player (P 2.5): who on the front, what drives them on the back."""
    return [(bearer_card(), bearer_card(back=True))] * bs.PLAYERS


def duplex_wide(pairs):
    """Two-sided double-width cards as a front page and a back page, 4 a landscape sheet. Flipped on the short edge,
    each row's two cards swap sides."""
    gap = '<div class="card gap"></div>'
    out = []
    for i in range(0, len(pairs), 4):
        chunk = pairs[i:i + 4] + [(gap, gap)] * (4 - len(pairs[i:i + 4]))
        backs = [chunk[k][1] for k in (1, 0, 3, 2)]
        out.append(sheets([f for f, _ in chunk], "wide4", 4) + sheets(backs, "wide4 back", 4))
    return "".join(out)


def build_frames():
    out = []
    for key, name, swap, reminder, n in bs.FRAMES:
        out.extend([ill.slot_frame(key, name, swap, reminder)] * n)
    return out


def intro(n_cards, n_frames, n_duplex, wide):
    rows = "".join(f"<tr><td>{k}</td><td>{', '.join(v)}</td></tr>" for k, v in bs.STARTER_LIST.items())
    frames = ", ".join(f"{n} {name}" for _, name, _, _, n in bs.FRAMES)
    return f"""<section class="intro"><h1>BEARERS</h1><p style="font-family:Cinzel,serif;letter-spacing:.2em">Base Set · {bs.PLAYERS} players</p>
<h2>Printing</h2>
<ul><li>Print at <b>100 %</b> (no fit-to-page) on cardstock. Pages 2–{n_duplex + 1} are two-sided cards: print them double-sided, flipping on the long edge. Pages {wide[0]}–{wide[1]} (landscape: Bearer, tally and foe cards) are two-sided too, flipping on the short edge. Print the rest single-sided.</li>
<li>Cards print at 60 × 84 mm, each centred in a 63 × 88 mm space; Bearer, tally and foe cards are double width (120 × 84 mm) and two-sided, 4 to a landscape page; Slot frames print at 64 × 93 mm.</li>
<li>Cut out each card and frame. On each frame, cut the two <b style="color:{ill.CRIMSON}">red slits</b> with a craft knife.</li>
<li>Tuck a card's top-right and bottom-left corners under the slits to equip it (Player Rules 12.2).</li></ul>
<h2>Contents</h2>
<p>{n_cards} cards: {len(bs.CALLINGS)} Callings, the starter list below, a pool of Rank I–II loot (marked LOOT at the bottom left), four decks, gold, {bs.PLAYERS} Bearer cards, {bs.TALLIES} tally cards and the {len(bs.WOUNDS)}-card Wound deck (marked WOUND: shuffle it and keep it beside the table, Player Rules 7.6).</p>
<p>For the GM: {len(foes.FOES)} foe cards and {foes.BLANKS} blank ones (marked FOE: keep them apart from the loot pool).</p>
<p>Each card shows its ID at the bottom right (<i>W-II-02</i>: type, Rank, number). Foe cards list the IDs of the cards they drop; every card a foe drops has one extra copy, so the loot pool still holds it after players take their starting gear.</p>
<p>{n_frames} frames: {frames}.</p>
<h2>Starter list</h2><table>{rows}</table>
<h2>Each player takes</h2>
<p>A Calling, then gear and Runes from the starter list that it can equip (Player Rules 13.1), 9 Slot frames (Armor, 2 Hand, Jewelry, 2 Item, 3 Rune), 3 Runestone frames, a Potion of Healing, a Coin Pouch with 50 gp, a Bearer card and a tally card. The Party Stash starts with 2 Runestone frames per player. Keep the milestone Rune frames and the extra Gear Slot frames for the GM to hand out.</p>
</section>"""


def render(name, title, body, pdf):
    doc = (f'<!doctype html><html lang="{T["lang"]}"><head><meta charset="utf-8"><title>{title}</title>{FONTS}'
           f"<style>{CSS}</style></head><body>{body}{FIT_LORE}</body></html>")
    page = BUILD / name
    page.write_text(doc, encoding="utf-8")
    subprocess.run(["chromium", "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                    "--virtual-time-budget=20000", f"--print-to-pdf={pdf}", page.as_uri()], check=True, capture_output=True)


def use_french():
    """The French base set: cards/fr.py translates the cards in place, the figures and words switch to French."""
    global T, OUT, READING, intro
    import fr
    fr.localize(bs, foes)
    ill.set_lang("fr")
    T = UI["fr"]
    T["type_en"] = {v: k for k, v in fr.KEYWORDS.items()}
    OUT = ROOT / "rules" / "fr" / "Porteurs-Set-de-base.pdf"
    READING = ROOT / "rules" / "fr" / "Porteurs-Set-de-base-Lecture.pdf"
    intro = intro_fr


def intro_fr(n_cards, n_frames, n_duplex, wide):
    rows = "".join(f"<tr><td>{k}</td><td>{', '.join(v)}</td></tr>" for k, v in bs.STARTER_LIST.items())
    frames = ", ".join(f"{n} {name}" for _, name, _, _, n in bs.FRAMES)
    return f"""<section class="intro"><h1>PORTEURS</h1><p style="font-family:Cinzel,serif;letter-spacing:.2em">Set de base · {bs.PLAYERS} joueurs</p>
<h2>Impression</h2>
<ul><li>Imprimez à <b>100 %</b> (sans ajustement à la page) sur du papier cartonné. Les pages 2 à {n_duplex + 1} sont des cartes recto verso : imprimez-les en recto verso, retournement sur le bord long. Les pages {wide[0]} à {wide[1]} (en paysage : cartes de Porteur, de Décompte et d'Adversaire) sont aussi recto verso, retournement sur le bord court. Imprimez le reste en recto seul.</li>
<li>Les cartes s'impriment en 60 × 84 mm, chacune centrée dans un espace de 63 × 88 mm ; les cartes de Porteur, de Décompte et d'Adversaire sont double largeur (120 × 84 mm) et recto verso, 4 par page paysage ; les cadres d'Emplacement s'impriment en 64 × 93 mm.</li>
<li>Découpez chaque carte et chaque cadre. Sur chaque cadre, incisez les deux <b style="color:{ill.CRIMSON}">fentes rouges</b> au cutter.</li>
<li>Glissez les coins supérieur droit et inférieur gauche d'une carte sous les fentes pour l'équiper (Règles du joueur 12.2).</li></ul>
<h2>Contenu</h2>
<p>{n_cards} cartes : {len(bs.CALLINGS)} Vocations, la liste de départ ci-dessous, une réserve de butin de Rang I–II (marquée BUTIN en bas à gauche), quatre paquets, de l'or, {bs.PLAYERS} cartes de Porteur, {bs.TALLIES} cartes de Décompte et le paquet de {len(bs.WOUNDS)} Blessures (marqué BLESSURE : mélangez-le et gardez-le à côté de la table, Règles du joueur 7.6).</p>
<p>Pour le MJ : {len(foes.FOES)} cartes d'Adversaire et {foes.BLANKS} vierges (marquées ADVERSAIRE : gardez-les à l'écart de la réserve de butin).</p>
<p>Chaque carte indique son code en bas à droite (<i>W-II-02</i> : type, Rang, numéro). Les cartes d'Adversaire listent les codes des cartes qu'elles lâchent ; chaque carte lâchée par un Adversaire a un exemplaire supplémentaire, pour que la réserve de butin la contienne encore après que les joueurs ont pris leur matériel de départ.</p>
<p>{n_frames} cadres : {frames}.</p>
<h2>Liste de départ</h2><table>{rows}</table>
<h2>Chaque joueur prend</h2>
<p>Une Vocation, puis du matériel et des Runes de la liste de départ qu'elle peut équiper (Règles du joueur 13.1), 9 cadres d'Emplacement (Armure, 2 Mains, Bijou, 2 Objets, 3 Runes), 3 cadres de Pierre runique, une Potion de soins, une Bourse à cordon avec 50 po, une carte de Porteur et une carte de Décompte. La Réserve de la Compagnie commence avec 2 cadres de Pierre runique par joueur. Gardez les cadres de Rune de jalon et les cadres d'Emplacement de Matériel supplémentaire pour que le MJ les distribue.</p>
</section>"""


def main():
    BUILD.mkdir(exist_ok=True)
    french = "--lang" in sys.argv and sys.argv[sys.argv.index("--lang") + 1] == "fr"
    if french:
        use_french()
    suffix = "-fr" if french else ""
    title = "Porteurs · Set de base" if french else "Bearers · Base Set"
    (cards, pairs), frames, foe_cards, tallies = build_cards(), build_frames(), build_foes(), build_bearers() + build_tallies()
    n_duplex = 2 * -(-len(pairs) // 9)
    first = n_duplex + 2 + -(-len(cards) // 9)  # the landscape two-sided pages follow the single cards
    wide = (first, first - 1 + 2 * -(-len(tallies) // 4) + 2 * -(-len(foe_cards) // 4))
    n_own = len(tallies)  # Bearer and tally cards
    render(f"base-set{suffix}.html", title,
           intro(len(cards) + len(pairs) + n_own, len(frames), n_duplex, wide) + duplex(pairs) + sheets(cards)
           + duplex_wide(tallies) + duplex_wide(foe_cards) + sheets(frames, "frames", 8), OUT)
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(cards) + len(pairs) + n_own} cards ({len(pairs) + n_own} two-sided), "
          f"{len(foe_cards)} foe cards, {len(frames)} frames")
    _, wide = build_cards(reading=True)
    render(f"base-set-reading{suffix}.html", title + (" (lecture)" if french else " (reading)"),
           sheets(wide, "foes", 3) + sheets(cards) + sheets([bearer_card(), bearer_card(back=True), tally_card()] + [f for f, _ in foe_cards], "wide4", 4), READING)
    print(f"Wrote {READING.relative_to(ROOT)}: {len(wide)} double-width two-sided cards, then the rest")
    if french:  # the simulator reads the English cards only
        return
    import export_sim
    import export_tables
    export_sim.main()
    export_tables.main()


if __name__ == "__main__":
    main()
