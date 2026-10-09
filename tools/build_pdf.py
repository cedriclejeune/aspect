"""Build the illustrated PDF rulebook from rules/RULES.md.

Usage: .venv/bin/python tools/build_pdf.py
Output: rules/Aspects-Core-Rules.pdf (and build/rules.html for inspection)
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

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "rules" / "RULES.md"
BUILD = ROOT / "build"
OUT = ROOT / "rules" / "Aspects-Core-Rules.pdf"

# Figure placed right after the heading whose text starts with the key.
FIGURES = {
    "The Core Loop": (ill.core_loop, "The core loop. Every session turns this wheel a few times.", "wide"),
    "2.3 Rank Bonus": (ill.rank_ladder, "Higher Ranks give bigger bonuses and are worth more when Shattered.", "wide"),
    "3. Aspects & Slots": (ill.character_anatomy, "Mira's build: a Core, five Slots, a Stash and a Pack.", "wide"),
    "3.1 Reading an Aspect": (ill.aspect_card_anatomy, "Every Aspect fits on a card.", "mid"),
    "4.1 Shattering": (ill.shatter, "Shattering: Aspects worth 5 points open the sixth Slot.", "wide"),
    "6.1 Order of Combat": (ill.initiative_timeline, "Side initiative: the winners open with half a turn, then sides alternate full turns.", "full"),
    "6.5 Opportunity Attacks": (ill.combat_grid, "Reach, opportunity attacks and cover on the grid.", "wide"),
    "7.4 Dropping to 0 HP": (ill.death_saves, "The death save track.", "wide"),
    "9.1 Armor Class": (ill.armor_tiers, "The three armor tiers and the shield.", "wide"),
    "10.6 Areas of Effect": (ill.areas_of_effect, "Areas of effect. The black dot marks the point of origin.", "wide"),
}

CSS = """
@page { size: Letter; margin: 0.8in 0.85in 0.9in 0.85in; background: #f6efdd;
  @bottom-center { content: counter(page); font-family: Cinzel, serif; font-size: 9pt; color: #7a6648; }
  @top-right { content: "ASPECTS · Core Rules"; font-family: Cinzel, serif; font-size: 8pt; color: #b07d2b; } }
@page :first { margin: 0; @bottom-center { content: none; } @top-right { content: none; } }
@page toc { @bottom-center { content: none; } }
html { background: #f6efdd; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: 'EB Garamond', Georgia, serif; font-size: 11.2pt; line-height: 1.38; color: #2b1d12; margin: 0; }
h1, h2, h3, h4 { font-family: Cinzel, serif; color: #8a1c1c; line-height: 1.15; break-after: avoid; }
h2 { font-size: 24pt; margin: 0 0 4pt; break-before: page; text-align: center; letter-spacing: .04em; }
h2 + .ornament { text-align: center; margin: 0 0 14pt; }
h2 + .ornament svg { width: 2.6in; }
h3 { font-size: 13.5pt; margin: 16pt 0 5pt; border-bottom: 1.5px solid #b07d2b; padding-bottom: 2pt; }
p { margin: 0 0 6pt; }
ul, ol { margin: 0 0 7pt; padding-left: 18pt; }
li { margin: 0 0 2.5pt; }
strong { color: #3a1f10; }
a { color: inherit; text-decoration: none; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.5pt; }
table { width: 100%; border-collapse: collapse; margin: 6pt 0 10pt; font-size: 10pt; break-inside: avoid; }
th { font-family: Cinzel, serif; font-size: 8.8pt; background: #8a1c1c; color: #f6efdd; text-align: left; padding: 4pt 6pt; }
td { padding: 3.2pt 6pt; border-bottom: 1px solid #e0cfa6; vertical-align: top; }
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
figure.wide svg { width: 88%; } figure.mid svg { width: 70%; } figure.full svg { width: 100%; }
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
        elif re.match(r"^[A-Z'’ ]{3,}·", lead):
            cls = "card monster" if "CR " in lead else "card"
        else:
            cls = "callout"
        return f'<blockquote class="{cls}">{inner}</blockquote>'

    body = re.sub(r"<blockquote>(.*?)</blockquote>", repl, body, flags=re.S)
    # Sample Aspects: lay consecutive cards out in two columns
    return re.sub(
        r'(<h3[^>]*>3\.2 Sample Aspects</h3>)\s*((?:<blockquote class="card">.*?</blockquote>\s*)+)',
        lambda m: m.group(1) + '<div class="cards">' + m.group(2) + "</div>",
        body,
        flags=re.S,
    )


def build_html():
    md_text = SRC.read_text(encoding="utf-8")
    # Drop the Markdown title block and Contents list: the PDF has its own cover and TOC.
    md_text = md_text.split("## 1. Introduction", 1)[1]
    md_text = "## 1. Introduction" + md_text
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
        for key in FIGURES:
            if plain.startswith(key):
                out += figure(key)
        return out

    body = re.sub(r"<h([234])>(.*?)</h\1>", heading, body)
    body = classify_blockquotes(body)
    body = body.replace('<h2 id="attribution">Attribution</h2>', '<h2 id="attribution">Attribution</h2><div class="attribution">', 1)
    if '<div class="attribution">' in body:
        body += "</div>"

    toc_html = "".join(f'<li><a href="#{hid}">{text}</a></li>' for hid, text in toc)
    cover = (
        f'<section class="cover">{ill.cover_emblem()}<h1>ASPECTS</h1>'
        '<p class="sub">Core Rules</p>'
        '<p class="tag">A classless, level-less game of loot and reinvention.<br>Compatible with fifth edition.</p>'
        '<p class="foot">Version 0.1 · Draft</p></section>'
    )
    return (
        f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Aspects · Core Rules</title>{FONTS}'
        f"<style>{CSS}</style></head><body>{cover}"
        f'<section class="toc"><h2>Contents</h2><div class="ornament">{ill.ornament()}</div><ol>{toc_html}</ol></section>'
        f"{body}</body></html>"
    )


def main():
    BUILD.mkdir(exist_ok=True)
    html_path = BUILD / "rules.html"
    html_path.write_text(build_html(), encoding="utf-8")
    subprocess.run(
        [
            "chromium", "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
            "--virtual-time-budget=20000", f"--print-to-pdf={OUT}", html_path.as_uri(),
        ],
        check=True, capture_output=True,
    )
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
