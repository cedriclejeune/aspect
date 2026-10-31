"""Build the illustrated PDF rulebooks from rules/PLAYERS.md and rules/GM.md.

Usage: .venv/bin/python tools/build_pdf.py
Output: rules/Bearers-Player-Rules.pdf, rules/Bearers-GM-Guide.pdf (and build/*.html for inspection)
rules/DESIGN.md is internal and never built. The Glossary chapters are first synced from GLOSSARY.md.
Needs: the `markdown` package and Chromium (headless printing).
"""
import html
import re
import subprocess
import sys
from pathlib import Path

import markdown

sys.path.insert(0, str(Path(__file__).parent))
import illustrations as ill  # noqa: E402
import sync_glossary  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"

# Figure placed right after the heading whose text starts with the key (Player Rules only),
# or wherever the Markdown has a <!-- figure: key --> line.
FIGURES = {
    "Story, Quests & Trials": (ill.play_loop, "Chain trials straight from Gather; rest (dotted) when the party needs it. A few trials make a quest; a few quests make a story.", "wide"),
    "calling": (ill.calling_card, "A Calling card: its own values in the strip. Your totals go on the tally card (12.3).", "full"),
    "card": (ill.card_elements, "Where each element sits on a card.", "wide"),
    "rank": (ill.rank_ladder, "Rank I is a small edge; Rank V breaks the rules.", "side"),
    "3.2 Your Slots": (ill.character_anatomy, "A starting Duelist: Calling, Armor, two Hands, Jewelry, two Items and three Aspects.", "wide"),
    "tally": (ill.tally_card, "The tally card, the one card you write on.", "full"),
    "frame": (ill.frame_figure, "An empty Armor frame, and a Hand frame holding a weapon by two corner slits.", "wide"),
    "totals": (ill.keeping_totals, "Bram's cards in play beside his tally card (top), and stacked on it to add up (bottom).", "full"),
    "6.1 Order of Combat": (ill.initiative_timeline, "Side initiative: the winners open with half a turn, then sides alternate full turns.", "full"),
    "6.5 Engagement": (ill.combat_grid, "Reach, opportunity attacks and cover on the grid.", "wide"),
    "7.4 Falling to 0 HP": (ill.death_saves, "The death save track.", "wide"),
    "9.1 Armor": (ill.armor_tiers, "Leather, Mail, Plate and the shield, with their Defense bonuses.", "wide"),
    "10.5 Areas of Effect": (ill.areas_of_effect, "Areas of effect. The black dot marks the point of origin.", "wide"),
}

CSS = """
@page { size: Letter; margin: 0.8in 0.85in 0.9in 0.85in; background: #f6efdd;
  @bottom-center { content: counter(page); font-family: Cinzel, serif; font-size: 9pt; color: #7a6648; }
  @top-right { content: "BEARERS · %HEADER%"; font-family: Cinzel, serif; font-size: 8pt; color: #b07d2b; } }
@page :first { margin: 0; @bottom-center { content: none; } @top-right { content: none; } }
@page toc { @bottom-center { content: none; } }
html { background: #f6efdd; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: 'EB Garamond', Georgia, serif; font-size: 11.2pt; line-height: 1.38; color: #2b1d12; margin: 0; }
h1, h2, h3, h4 { font-family: Cinzel, serif; color: #8a1c1c; line-height: 1.15; break-after: avoid; }
h2 { font-size: 24pt; margin: 0 0 4pt; break-before: page; text-align: center; letter-spacing: .04em; }
h2 + .ornament { text-align: center; margin: 0 0 14pt; }
hr { display: none; }  /* chapters already start a new page; a divider can spill onto a blank one */
h2 + .ornament svg { width: 2.6in; }
h3 { font-size: 13.5pt; margin: 16pt 0 5pt; border-bottom: 1.5px solid #b07d2b; padding-bottom: 2pt; }
p { margin: 0 0 6pt; }
ul, ol { margin: 0 0 7pt; padding-left: 18pt; }
li { margin: 0 0 2.5pt; }
strong { color: #3a1f10; }
a { color: inherit; text-decoration: none; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.5pt; }
table { width: 100%; border-collapse: collapse; margin: 6pt 0 10pt; font-size: 10pt; break-inside: avoid; }
table:has(tbody tr:nth-child(25)) { break-inside: auto; }  /* long tables (the Glossary) may span pages */
tr { break-inside: avoid; }
th { font-family: Cinzel, serif; font-size: 8.8pt; background: #8a1c1c; color: #f6efdd; text-align: left; padding: 4pt 6pt; }
td { padding: 3.2pt 6pt; border-bottom: 1px solid #e0cfa6; vertical-align: top; }
img.sym, .sym { display: inline-block; width: 1.7em; height: 1.7em; vertical-align: -0.55em; }
.sym svg { width: 100%; height: 100%; }
td:has(> .sym:only-child) { width: 1.7em; padding-right: 0; }
td:has(> .sym:only-child) .sym { vertical-align: top; margin-top: -1pt; }
td:first-child:has(> .sym:only-child) + td { white-space: nowrap; }
tr:nth-child(even) td { background: rgba(176,125,43,.09); }
blockquote { margin: 8pt 0 10pt; break-inside: avoid; }
blockquote p { margin: 0 0 3pt; }
blockquote.card { background: #fbf6e9; border: 2px solid #2b1d12; border-radius: 9px; padding: 0 12pt 8pt;
  box-shadow: 4px 4px 0 #e6d8b5; max-width: 4.6in; }
blockquote.card p:first-child { background: #b07d2b; color: #fbf6e9; margin: 0 -12pt 6pt; padding: 5pt 12pt;
  border-radius: 7px 7px 0 0; font-family: Cinzel, serif; font-size: 10pt; }
blockquote.card p:first-child strong { color: #fbf6e9; font-size: 11.5pt; }
blockquote.card.monster { max-width: none; }
blockquote.card.monster p:first-child { background: #8a1c1c; }
blockquote.example { border-left: 4px solid #8a1c1c; background: rgba(138,28,28,.06); padding: 6pt 12pt; font-style: italic; }
blockquote.callout { text-align: center; font-family: Cinzel, serif; font-size: 12pt; color: #8a1c1c; padding: 6pt 0;
  border-top: 1px solid #b07d2b; border-bottom: 1px solid #b07d2b; }
.cards { display: grid; grid-template-columns: 1fr 1fr; gap: 0 14pt; }
.cards blockquote.card { max-width: none; margin: 0 0 12pt; }
figure { margin: 10pt auto 12pt; text-align: center; break-inside: avoid; }
figure svg { width: 100%; height: auto; }
figure.wide svg { width: 88%; } figure.mid svg { width: 70%; } figure.small svg { width: 50%; }
figure:not(.side) { clear: both; }
figure.side { float: right; width: 28%; margin: 4pt 0 6pt 14pt; } figure.side svg { width: 100%; } figure.full svg { width: 100%; }
figcaption { font-style: italic; font-size: 9.8pt; color: #7a6648; margin-top: 3pt; }
.cover { height: 11in; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;
  background: radial-gradient(ellipse at center, #fbf6e9 0%, #f0e3c4 70%, #e3cf9f 100%); break-after: page; }
.cover h1 { font-size: 64pt; letter-spacing: .14em; margin: 18pt 0 0; color: #8a1c1c; }
.cover .sub { font-family: Cinzel, serif; font-size: 16pt; color: #2b1d12; letter-spacing: .2em; margin: 6pt 0 0; }
.cover .tag { font-style: italic; font-size: 14pt; color: #7a6648; margin: 18pt 0 0; }
.cover svg { width: 4.2in; }
.cover .foot { font-family: Cinzel, serif; font-size: 9pt; color: #7a6648; margin-top: 60pt; letter-spacing: .1em; }
.toc { page: toc; break-after: page; }
.toc h2 { break-before: auto; margin-top: 40pt; }
.toc ol { list-style: none; padding: 0; max-width: 4.2in; margin: 0 auto; counter-reset: none; }
.toc li { font-family: Cinzel, serif; font-size: 13pt; padding: 7pt 0; border-bottom: 1px dotted #b07d2b; }
.attribution { font-size: 9pt; color: #7a6648; }
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&'
         'family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=block" rel="stylesheet">')


def slug(text):
    """GitHub-style heading anchors, so the Markdown table of contents links still work."""
    text = re.sub(r"<[^>]+>", "", html.unescape(text)).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


BOOKS = [
    # (source, output, cover subtitle, running header, figures)
    ("PLAYERS.md", "Bearers-Player-Rules.pdf", "Player Rules", "Player Rules", FIGURES),
    ("GM.md", "Bearers-GM-Guide.pdf", "Game Master's Guide", "GM's Guide", {}),
]


def figure(key):
    fn, caption, size = FIGURES[key]
    return f'<figure class="{size}">{fn()}<figcaption>{caption}</figcaption></figure>'


def classify_blockquotes(body):
    def repl(m):
        inner = m.group(1)
        first = re.search(r"<p>(.*?)</p>", inner, re.S)
        lead = re.sub(r"<[^>]+>", "", first.group(1)) if first else ""
        if lead.startswith("Example"):
            cls = "example"
        elif re.match(r"^[A-Z'’ ]{3,}(·|\n|$)", lead):
            cls = "card monster" if "CR " in lead else "card"
        else:
            cls = "callout"
        return f'<blockquote class="{cls}">{inner}</blockquote>'

    body = re.sub(r"<blockquote>(.*?)</blockquote>", repl, body, flags=re.S)
    # Sample Cards: lay consecutive cards out in two columns
    return re.sub(
        r'(<h3[^>]*>[\d.]+ Sample Cards</h3>)\s*((?:<blockquote class="card">.*?</blockquote>\s*)+)',
        lambda m: m.group(1) + '<div class="cards">' + m.group(2) + "</div>",
        body,
        flags=re.S,
    )


SYMBOLS = {f"{k.lower()}{'-def' if d else ''}": (k, d) for k in ill.STAT_SYMBOLS for d in (False, True)
           if not d or k in ("STR", "DEX", "INT", "WIL")}


def write_symbols():
    """rules/symbols/*.svg, so the Markdown previews show the stat symbols too."""
    out = ROOT / "rules" / "symbols"
    out.mkdir(exist_ok=True)
    for name, (key, shield) in SYMBOLS.items():
        (out / f"{name}.svg").write_text(ill.stat_symbol(key, shield), encoding="utf-8")


def inline_symbols(body):
    """Swap each <img src="symbols/x.svg"> for the inline SVG, so the PDF needs no files."""
    def repl(m):
        key, shield = SYMBOLS[m.group(1)]
        return f'<span class="sym">{ill.stat_symbol(key, shield)}</span>'
    return re.sub(r'<img[^>]*src="symbols/([\w-]+)\.svg"[^>]*>', repl, body)


def build_html(src, subtitle, header, figures):
    md_text = src.read_text(encoding="utf-8")
    # Drop the Markdown title block and Contents list: the PDF has its own cover and TOC.
    md_text = "## 1. " + md_text.split("## 1. ", 1)[1]
    # Each line of a blockquote becomes its own paragraph (card header, stats, effect...).
    md_text = re.sub(r"^(>.*)\n(?=>)", r"\1\n>\n", md_text, flags=re.M)
    # Keep consecutive blockquotes (sample cards) as separate cards.
    md_text = re.sub(r"^(>.*)\n\n(?=>)", r"\1\n\n<div></div>\n\n", md_text, flags=re.M)
    # Python-Markdown needs a blank line before a list and 4-space indents for nested items.
    md_text = re.sub(r"^([^\s\-|>#].*)\n(?=(?:- |\d+\. ))", r"\1\n\n", md_text, flags=re.M)
    md_text = re.sub(r"^ {2,3}- ", "    - ", md_text, flags=re.M)
    body = markdown.markdown(md_text, extensions=["tables", "sane_lists"])

    toc = []

    def heading(m):
        level, text = m.group(1), m.group(2)
        hid = slug(text)
        out = f'<h{level} id="{hid}">{text}</h{level}>'
        if level == "2":
            toc.append((hid, text))
            out += f'<div class="ornament">{ill.ornament()}</div>'
        plain = html.unescape(re.sub(r"<[^>]+>", "", text))
        for key in figures:
            if plain.startswith(key):
                out += figure(key)
        return out

    body = re.sub(r"<h([234])>(.*?)</h\1>", heading, body)
    body = re.sub(r"<!-- figure: (.+?) -->", lambda m: figure(m.group(1)), body)
    body = classify_blockquotes(body)
    body = inline_symbols(body)
    body = body.replace('<h2 id="attribution">Attribution</h2>', '<h2 id="attribution">Attribution</h2><div class="attribution">', 1)
    if '<div class="attribution">' in body:
        body += "</div>"

    toc_html = "".join(f'<li><a href="#{hid}">{text}</a></li>' for hid, text in toc)
    cover = (
        f'<section class="cover">{ill.cover_emblem()}<h1>BEARERS</h1>'
        f'<p class="sub">{subtitle}</p>'
        '<p class="tag">What Lingers Matters</p>'
        '<p class="foot">Version 0.1 · Draft</p></section>'
    )
    return (
        f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Bearers · {subtitle}</title>{FONTS}'
        f"<style>{CSS.replace('%HEADER%', header)}</style></head><body>{cover}"
        f'<section class="toc"><h2>Contents</h2><div class="ornament">{ill.ornament()}</div><ol>{toc_html}</ol></section>'
        f"{body}</body></html>"
    )


def main():
    for name in sync_glossary.sync():
        print(f"Synced the glossary into {name}")
    BUILD.mkdir(exist_ok=True)
    write_symbols()
    for src, out, subtitle, header, figures in BOOKS:
        out = ROOT / "rules" / out
        html_path = BUILD / (Path(src).stem.lower() + ".html")
        html_path.write_text(build_html(ROOT / "rules" / src, subtitle, header, figures), encoding="utf-8")
        subprocess.run(
            [
                "chromium", "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                "--virtual-time-budget=20000", f"--print-to-pdf={out}", html_path.as_uri(),
            ],
            check=True, capture_output=True,
        )
        print(f"Wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
