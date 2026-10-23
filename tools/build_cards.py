"""Build the printable base set (cards and Slot frames) from cards/base_set.py.

Usage: .venv/bin/python tools/build_cards.py
Output: rules/Bearers-Base-Set.pdf (and build/base-set.html for inspection)
Cards are 63 × 88 mm, 9 per Letter page; foe cards 126 × 88 mm, 3 per page; Slot frames are 67 × 98 mm, 8 per landscape page.
Card geometry matches the tally card (P 12.3): title band 13 %, keywords 10 %, bonus strip 20 % wide.
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

BUILD = ROOT / "build"
OUT = ROOT / "rules" / "Bearers-Base-Set.pdf"

ROWS = ["STR", "DEX", "INT", "WIL", "STRd", "DEXd", "INTd", "WILd", "HP", "SPD"]
SYM = [("STR", False), ("DEX", False), ("INT", False), ("WIL", False),
       ("STR", True), ("DEX", True), ("INT", True), ("WIL", True), ("HP", False), ("SPD", False)]
COLOR = {"core": ill.CRIMSON, "gear": ill.GOLD, "aspect": ill.ASPECT_GREEN, "foe": ill.INK}
RANK_COLOR = {"I": "#9a8a6a", "II": ill.GOLD, "III": ill.CRIMSON, "IV": "#4b2a6b", "V": ill.INK}

CSS = f"""
@page {{ size: Letter; margin: 0; }}
@page frames {{ size: Letter landscape; margin: 0; }}
html {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ margin: 0; font-family: 'EB Garamond', Georgia, serif; color: {ill.INK}; }}
.sheet {{ width: 215.9mm; height: 279.4mm; display: grid; grid-template-columns: repeat(3, 63mm); grid-auto-rows: 88mm;
  gap: 2mm; justify-content: center; align-content: center; break-after: page; overflow: hidden; }}
.sheet.foes {{ grid-template-columns: 126mm; }}
.sheet.frames {{ page: frames; width: 279.4mm; height: 215.9mm; grid-template-columns: repeat(4, 67mm); grid-auto-rows: 98mm; gap: 0; }}
.sheet.frames svg {{ width: 67mm; height: 98mm; display: block; }}
.intro {{ width: 215.9mm; height: 279.4mm; box-sizing: border-box; padding: 22mm 24mm; break-after: page; background: {ill.PARCH}; }}
.intro h1 {{ font-family: Cinzel, serif; color: {ill.CRIMSON}; font-size: 30pt; margin: 0; letter-spacing: .08em; }}
.intro h2 {{ font-family: Cinzel, serif; color: {ill.CRIMSON}; font-size: 13pt; margin: 14pt 0 4pt; border-bottom: 1.5px solid {ill.GOLD}; }}
.intro p, .intro li {{ font-size: 11pt; line-height: 1.35; margin: 0 0 4pt; }}
.intro table {{ border-collapse: collapse; font-size: 10pt; width: 100%; }}
.intro td {{ padding: 2pt 6pt; border-bottom: 1px solid #e0cfa6; vertical-align: top; }}
.intro td:first-child {{ font-family: Cinzel, serif; font-size: 9pt; white-space: nowrap; }}

.card {{ position: relative; width: 63mm; height: 88mm; box-sizing: border-box; border: .35mm solid {ill.INK}; border-radius: 3mm;
  background: #fbf6e9; overflow: hidden; }}
.band {{ position: absolute; left: 0; right: 0; top: 0; height: 11.44mm; background: var(--c); color: {ill.PARCH};
  display: flex; align-items: center; padding: 0 9.5mm 0 2.2mm; box-sizing: border-box; border-bottom: .35mm solid {ill.INK};
  font-family: Cinzel, serif; font-weight: 700; line-height: 1.05; }}
.band .gem {{ position: absolute; right: 1.4mm; top: 1.6mm; width: 8.2mm; height: 8.2mm; }}
.band .lvl {{ position: absolute; right: 2mm; top: 2.2mm; font-size: 6.2pt; font-family: 'EB Garamond', serif; font-style: italic; font-weight: 400; }}
.strip {{ position: absolute; right: 0; top: 11.44mm; width: 12.6mm; height: 67.76mm; background: {ill.SHADE};
  border-left: .25mm solid {ill.INK}; display: grid; grid-template-rows: repeat(10, 1fr); }}
.strip div {{ display: flex; align-items: center; justify-content: space-between; padding: 0 .7mm; border-top: .12mm solid {ill.MUTED}; }}
.strip div:first-child {{ border-top: 0; }}
.strip svg {{ width: 4.6mm; height: 4.6mm; }}
.strip .off svg {{ opacity: .25; }}
.strip b {{ font-family: Cinzel, serif; font-size: 7.4pt; color: {ill.CRIMSON}; }}
.strip.own b {{ color: {ill.INK}; }}
.body {{ position: absolute; left: 0; right: 12.6mm; top: 11.44mm; bottom: 8.8mm; padding: 2mm 2.2mm; box-sizing: border-box;
  display: flex; flex-direction: column; justify-content: center; gap: 1.4mm; }}
.body p {{ margin: 0; line-height: 1.2; }}
.body .art {{ display: flex; justify-content: center; opacity: .9; }}
.wide .body {{ right: 0; }}
.deck .body {{ left: 8mm; }}
.index {{ position: absolute; left: 0; top: 11.44mm; bottom: 8.8mm; width: 8mm; border-right: .25mm solid {ill.GOLD};
  background: rgba(176,125,43,.08); display: flex; flex-direction: column; align-items: center; padding-top: 1.6mm; gap: 2mm; }}
.index .cost {{ width: 6mm; height: 6mm; border-radius: 50%; background: var(--c); color: {ill.PARCH}; display: flex;
  align-items: center; justify-content: center; font-family: Cinzel, serif; font-weight: 700; font-size: 9pt; }}
.index .name {{ writing-mode: vertical-rl; transform: rotate(180deg); font-family: Cinzel, serif; font-size: 6.4pt; color: {ill.MUTED};
  white-space: nowrap; }}
.kw {{ position: absolute; left: 0; right: 0; bottom: 0; height: 8.8mm; border-top: .35mm solid {ill.GOLD}; display: flex;
  align-items: center; justify-content: center; padding: 0 3mm; box-sizing: border-box; text-align: center;
  font-style: italic; font-size: 7.6pt; line-height: 1.1; }}
.set {{ position: absolute; left: 1.6mm; bottom: .9mm; font-family: Cinzel, serif; font-size: 4.6pt; color: {ill.MUTED}; letter-spacing: .05em; }}
.coin {{ display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2mm; }}
.coin svg {{ width: 30mm; height: 30mm; }}
.tally svg {{ width: 63mm; height: 88mm; display: block; }}
.tally {{ border: 0; border-radius: 0; background: none; }}
.card.foe {{ width: 126mm; }}
.foe .pic {{ position: absolute; left: 0; top: 11.44mm; bottom: 8.8mm; width: 50mm; border-right: .25mm solid {ill.GOLD};
  background: rgba(176,125,43,.06); display: flex; align-items: center; justify-content: center; }}
.foe .pic svg {{ width: 42mm; height: 42mm; }}
.foe .body {{ left: 50mm; justify-content: flex-start; gap: .9mm; }}
.foe .tag {{ position: absolute; right: 2mm; top: 3.4mm; font-size: 6.4pt; font-family: 'EB Garamond', serif; font-style: italic; font-weight: 400; }}
.foe .ids {{ font-size: 6.4pt; color: {ill.MUTED}; }}
.blank .line {{ border-bottom: .2mm solid {ill.MUTED}; height: 4.2mm; font-size: 6pt; color: {ill.MUTED}; font-style: italic; }}
"""


def md(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)


def fit(text, room):
    """Font size (pt) for the effect text: shrink as it grows."""
    n = sum(len(t) for t in text) + 25 * (len(text) - 1)
    return 9.4 if n < 90 else 8.8 if n < 170 else 8.2 if n < 250 else 7.7 if n < 330 else 7.2


def art_block(svg, text):
    """The card's drawing, smaller as its text grows."""
    if not svg:
        return ""
    n = sum(len(t) for t in text)
    size = 30 if n == 0 else 24 if n < 90 else 19 if n < 170 else 15 if n < 250 else 12
    sized = svg.replace("<svg ", f'<svg style="width:{size}mm;height:{size}mm;overflow:visible" ', 1)
    return f'<div class="art" style="height:{size}mm">{sized}</div>'


def rank_gem(rank):
    return ill._svg(40, 40, ill.gem(20, 20, 18, RANK_COLOR[rank], rank, 12 if len(rank) < 3 else 10), f"Rank {rank}").replace("<svg ", '<svg class="gem" ', 1)


def strip(values, own=False):
    rows = []
    for key, (sym, shield) in zip(ROWS, SYM):
        v = values.get(key)
        rows.append(f'<div class="{"" if v or own else "off"}">{ill.stat_symbol(sym, shield)}{f"<b>{v}</b>" if v else ""}</div>')
    return f'<div class="strip{" own" if own else ""}">{"".join(rows)}</div>'


def band(name, color, right):
    size = 9.2 if len(name) <= 14 else 8 if len(name) <= 18 else 7
    return f'<div class="band" style="--c:{color};font-size:{size}pt">{html.escape(name.upper())}{right}</div>'


def item_card(c, group):
    color = COLOR[c["kind"]]
    paras = "".join(f"<p>{md(t)}</p>" for t in c["text"])
    art_html = art_block(card_art.art(c["name"]), c["text"])
    return (f'<div class="card">{band(c["name"], color, rank_gem(c["rank"]))}'
            f'{strip(c["strip"], own=c["kind"] == "core")}'
            f'<div class="body" style="font-size:{fit(c["text"], "")}pt">{art_html}{paras}</div>'
            f'<div class="kw">{md(c["kw"])}</div><div class="set">{group} · {c["id"]}</div></div>')


def deck_card(s, deck):
    cover = deck["cover"]
    color = COLOR[deck["color"]]
    has_strip = bool(s["strip"]) or s["level"] == "Form"
    paras = art_block(card_art.art(s["name"], deck=True), s["text"]) + "".join(f"<p>{md(t)}</p>" for t in s["text"])
    level = f'<span class="lvl">{s["level"]}</span>'
    return (f'<div class="card deck{"" if has_strip else " wide"}">{band(s["name"], color, level)}'
            f'<div class="index" style="--c:{color}"><div class="cost">{s["cost"]}</div><div class="name">{html.escape(cover["name"])}</div></div>'
            f'{strip(s["strip"]) if has_strip else ""}'
            f'<div class="body" style="font-size:{fit(s["text"], "deck")}pt">{paras}</div>'
            f'<div class="kw">{md(s["kw"])}</div></div>')


def total(values):
    """Add up strip values ("+2", "−10", "14") row by row."""
    out = {}
    for strip_ in values:
        for k, v in strip_.items():
            out[k] = out.get(k, 0) + int(str(v).replace("−", "-"))
    return out


def signed(n):
    return f"+{n}" if n >= 0 else f"−{-n}"


def more_dice(dice, n):
    return re.sub(r"(\d+)d(\d+)", lambda m: f"{int(m[1]) + n}d{m[2]}", dice)


ABIL = r"(STR|DEX|INT|WIL)"


def resolve(text, mods):
    """Write a foe's numbers into card text: "WIL + 2" → "+5", "3 + WIL" → "6", "2d4 + WIL" → "2d4 + 3"."""
    text = re.sub(rf"(\d+d\d+) \+ {ABIL}\b", lambda m: f"{m[1]} + {mods[m[2]]}", text)
    text = re.sub(rf"\b{ABIL}(?: or {ABIL})? \+ (\d+)\b",
                  lambda m: signed(max(mods[a] for a in (m[1], m[2]) if a) + int(m[3])), text)
    return re.sub(rf"\b(\d+) \+ {ABIL}\b", lambda m: str(int(m[1]) + mods[m[2]]), text)


def foe_attack(c, mods, extra_dice):
    """A weapon card's line on a foe card: the foe's modifier added in, plain-text dice included."""
    m = re.match(r"([+−-]\d+) to hit, (.+?) \+ (STR or DEX|STR|DEX) (\w+)\.\s*(.*)", c["text"][0])
    hit, dice, attr, dtype, effect = m.groups()
    mod = max(mods[a] for a in attr.split(" or "))
    reach = next((k for k in c["kw"].split(" · ") if k.startswith(("Thrown", "Range"))), "")
    dmg_mod = f" + {mod}" if mod >= 0 else f" − {-mod}"
    line = (f'*{c["name"]}*: {signed(int(hit.replace("−", "-")) + mod)} to hit, {reach + ", " if reach else ""}'
            f'{more_dice(dice, extra_dice)}{dmg_mod} {dtype}.')
    return line + (f" {effect}" if effect else "")


def foe_lines(f):
    """Totals and text of a foe card, from the cards it names (cards/foes.py)."""
    if f["core"]:
        core = bs.BY_NAME[f["core"]]
        size = core["kw"].split(" · ")[-1]
        head = [f'*{core["name"]}* Core']
    else:
        *mods_, hp, spd, size = f["body"]
        core = bs.core(f["name"], "", mods_, hp, spd, size)
        head = []
    cards = [bs.BY_NAME[n] for n in f["carries"]]
    sums = total([core["strip"]] + [c["strip"] for c in cards] + [f["bonus"]])
    mods = {k: sums.get(k, 0) for k in ("STR", "DEX", "INT", "WIL")}
    values = {k: signed(v) if k in mods else str(v) for k, v in sums.items()}
    lines = head + f["own"]
    also = []
    for c in cards:
        kind = c["kw"].split(" · ")[0]
        deck = next((d for d in bs.DECKS if d["cover"] is c), None)
        if kind == "Weapon":
            lines.append(foe_attack(c, mods, f["extra_dice"]))
        elif kind in ("Armor", "Shield", "Purse"):
            also.append(f'*{c["name"]}*')
        elif deck:
            lines.append(f'*{c["name"]}*: ' + " · ".join(resolve(t, mods) for t in c["text"][:2]))
            lines += [f'**{p["name"]}** ({p["cost"]}): ' + resolve(" ".join(p["text"]), mods)
                      for p in deck["cards"] if p["name"] in f["powers"]]
        else:
            lines.append(f'*{c["name"]}*: ' + resolve(" ".join(c["text"]), mods))
    if also:
        lines.append("Also carries " + ", ".join(also) + ".")
    drops = [c for c in ([core] if f["core"] else []) + cards]
    kw = " · ".join(["Foe"] + (["Boss"] if f["boss"] else []) + [size] + ([f["senses"]] if f["senses"] else []))
    return values, lines, kw, "Drops: " + " · ".join(f'*{c["name"]}*{" Core" if c["kind"] == "core" else ""} ({c["id"]})' for c in drops)


def foe_card(f):
    values, lines, kw, ids = foe_lines(f)
    tag = f'<span class="tag">{"Boss" if f["boss"] else "Foe"}</span>'
    art = card_art.foe_art(f["name"]) or ""
    paras = "".join(f"<p>{md(t)}</p>" for t in lines)
    return (f'<div class="card foe">{band(f["name"], COLOR["foe"], tag)}<div class="pic">{art}</div>{strip(values, own=True)}'
            f'<div class="body" style="font-size:{fit(lines, "") + 1}pt">{paras}<p class="ids">{md(ids)}</p></div>'
            f'<div class="kw">{kw}</div><div class="set">FOE</div></div>')


def blank_foe_card():
    rows = "".join(f'<div class="line">{t}</div>' for t in ("Core", "Attacks", "", "", "Powers", "", "", "", "Drops", "", ""))
    return (f'<div class="card foe blank">{band("", COLOR["foe"], "<span class=tag>Foe</span>")}<div class="pic"></div>{strip({}, own=True)}'
            f'<div class="body">{rows}</div><div class="kw">Foe · size · senses</div><div class="set">FOE</div></div>')


def gold_card(value):
    coin = ill._svg(40, 40, f'<circle cx="20" cy="20" r="17" fill="{ill.GOLD}" stroke="{ill.INK}" stroke-width="1.6"/>'
                    f'<circle cx="20" cy="20" r="13" fill="none" stroke="{ill.PARCH}" stroke-width=".8"/>'
                    + ill._text(20, 24.5, f"{value:,}", 12 if value < 1000 else 9.5, ill.HEAD, ill.PARCH), "gold")
    return (f'<div class="card wide">{band(f"{value:,} gp", ill.GOLD, "")}'
            f'<div class="body coin">{coin}<p style="font-size:8pt;text-align:center"><i>In a Purse, it takes no room. Loose, it is a bag of coins: 1 piece.</i></p></div>'
            f'<div class="kw">Gold</div></div>')


def tally_card():
    return f'<div class="card tally">{ill._svg(300, 419, ill.tally_small(0, 0, 300, 419, {}), "Tally card")}</div>'


def sheets(cards, cls="", per=9):
    return "".join(f'<section class="sheet {cls}">{"".join(cards[i:i + per])}</section>' for i in range(0, len(cards), per))


def build_cards():
    out = []

    dropped = [n for f in foes.FOES for n in {f["core"], *f["carries"]}]  # one extra copy per foe card naming it

    def add(c):
        out.extend([item_card(c, c["group"].upper())] * (c["copies"] + dropped.count(c["name"])))
    for c in bs.CORES + bs.ARMOR + bs.HANDS + bs.JEWELRY + bs.ITEMS:
        add(c)
    for c in bs.ASPECTS:
        add(c)
    for deck in bs.DECKS:
        out.append(item_card(deck["cover"], "STARTER"))
        out.extend(deck_card(s, deck) for s in deck["cards"])
    for value, n in bs.GOLD:
        out.extend([gold_card(value)] * n)
    out.extend([tally_card()] * bs.TALLIES)
    return out


def build_foes():
    """Double-width foe cards, filled with the single cards' grid: one per row (the third column stays empty)."""
    return [foe_card(f) for f in foes.FOES] + [blank_foe_card()] * foes.BLANKS


def build_frames():
    out = []
    for key, name, swap, reminder, n in bs.FRAMES:
        out.extend([ill.slot_frame(key, name, swap, reminder)] * n)
    return out


def intro(n_cards, n_frames):
    rows = "".join(f"<tr><td>{k}</td><td>{', '.join(v)}</td></tr>" for k, v in bs.STARTER_LIST.items())
    frames = ", ".join(f"{n} {name}" for _, name, _, _, n in bs.FRAMES)
    return f"""<section class="intro"><h1>BEARERS</h1><p style="font-family:Cinzel,serif;letter-spacing:.2em">Base Set · {bs.PLAYERS} players</p>
<h2>Printing</h2>
<ul><li>Print at <b>100 %</b> (no fit-to-page) on cardstock. Cards are 63 × 88 mm; foe cards are double width (126 × 88 mm); Slot frames are 67 × 98 mm.</li>
<li>Cut out each card and frame. On each frame, cut the two <b style="color:{ill.CRIMSON}">red slits</b> with a craft knife.</li>
<li>Tuck a card's top-right and bottom-left corners under the slits to equip it (Player Rules 12.2).</li></ul>
<h2>Contents</h2>
<p>{n_cards} cards: 7 Cores, the starter list below, a pool of Rank I–II loot (marked LOOT at the bottom left), four decks, gold, {bs.TALLIES} tally cards.</p>
<p>For the GM: {len(foes.FOES)} foe cards and {foes.BLANKS} blank ones (marked FOE: keep them apart from the loot pool).</p>
<p>Each card shows its ID at the bottom left (<i>W-II-02</i>: type, Rank, number). Foe cards list the IDs of the cards they drop; every card a foe drops has one extra copy, so the loot pool still holds it after players take their starting gear.</p>
<p>{n_frames} frames: {frames}.</p>
<h2>Starter list</h2><table>{rows}</table>
<h2>Each player takes</h2>
<p>A Core, then gear and Aspects from the starter list (Player Rules 13.2), 9 Slot frames (Armor, 2 Hand, Jewelry, 2 Item, 3 Aspect), 3 Shard frames, a Potion of Healing, a Coin Pouch with 50 gp and a tally card. The Party Stash starts with 2 Shard frames per player. Keep the milestone Aspect frames and the extra Gear Slot frames for the GM to hand out.</p>
</section>"""


def main():
    BUILD.mkdir(exist_ok=True)
    cards, frames, foe_cards = build_cards(), build_frames(), build_foes()
    doc = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Bearers · Base Set</title>{FONTS}'
           f"<style>{CSS}</style></head><body>{intro(len(cards), len(frames))}{sheets(cards)}{sheets(foe_cards, 'foes', 3)}{sheets(frames, 'frames', 8)}</body></html>")
    page = BUILD / "base-set.html"
    page.write_text(doc, encoding="utf-8")
    subprocess.run(["chromium", "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                    "--virtual-time-budget=20000", f"--print-to-pdf={OUT}", page.as_uri()], check=True, capture_output=True)
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(cards)} cards, {len(foe_cards)} foe cards, {len(frames)} frames")


if __name__ == "__main__":
    main()
