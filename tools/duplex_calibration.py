"""A two-page duplex calibration sheet: how far the printer puts a back page off its front.

Usage: .venv/bin/python tools/duplex_calibration.py
Writes rules/duplex-calibration.pdf and rules/fr/calibrage-recto-verso.pdf (Letter, print two-sided on the long edge,
like the card pages). The front has a cross at five points; the back has two rulers at each point, its mirror image.
Held up to a light, back facing you, each cross's vertical line meets the dx ruler at the --back-dx to give
tools/build_cards.py, its horizontal line the dy ruler at the --back-dy (mm, as seen on the back: + right, + down).
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H = 215.9, 279.4
POINTS = ((35, 35), (W - 35, 35), (W / 2, H / 2), (35, H - 45), (W - 35, H - 45))
TEXT = {
    "en": ("Duplex calibration · front", "Duplex calibration · back",
           "Print two-sided, flip on the long edge, at 100 % with the card pages' settings. Hold the sheet up to a light, "
           "this side facing you: read where each cross's vertical line meets its dx ruler, its horizontal line its dy ruler.",
           "Then rebuild: tools/build_cards.py --back-dx DX --back-dy DY (or set BACK_SHIFT). The five readings should agree."),
    "fr": ("Calibrage recto verso · recto", "Calibrage recto verso · verso",
           "Imprimez en recto verso, retournement sur le bord long, à 100 %, avec les mêmes réglages que les pages de cartes. "
           "Tenez la feuille devant une lumière, ce côté vers vous : lisez où la ligne verticale de chaque croix croise "
           "sa règle dx, et sa ligne horizontale sa règle dy.",
           "Ces deux chiffres (en mm) sont le décalage à donner aux versos : tools/build_cards.py --back-dx DX --back-dy DY. "
           "Les cinq lectures doivent concorder."),
}


def cross(x, y):
    return (f'<line x1="{x - 22}" y1="{y}" x2="{x + 22}" y2="{y}"/><line x1="{x}" y1="{y - 22}" x2="{x}" y2="{y + 22}"/>'
            f'<circle cx="{x}" cy="{y}" r="2" fill="none"/>')


def rulers(x, y):
    """A dx ruler below the point and a dy ruler left of it, 14 mm off, so the cross's lines run across them: a tick
    every 0.5 mm, a long one every mm, ±8 mm, labelled every 4 mm."""
    out, rx, ry = [f'<circle cx="{x}" cy="{y}" r="2" fill="none"/>'], x - 14, y + 14
    for k in range(-16, 17):
        d, n, w = k / 2, (5 if k % 8 == 0 else 3.5 if k % 2 == 0 else 2), .3 if k == 0 else .15
        out.append(f'<line x1="{x + d}" y1="{ry - n / 2}" x2="{x + d}" y2="{ry + n / 2}" stroke-width="{w}"/>')
        out.append(f'<line x1="{rx - n / 2}" y1="{y + d}" x2="{rx + n / 2}" y2="{y + d}" stroke-width="{w}"/>')
        if k % 8 == 0:
            out.append(f'<text x="{x + d}" y="{ry + 6}" text-anchor="middle">{d:+g}</text>'.replace('>+0<', '>0<'))
            out.append(f'<text x="{rx - 3.5}" y="{y + d + 1}" text-anchor="end">{d:+g}</text>'.replace('>+0<', '>0<'))
    out.append(f'<text x="{x + 10}" y="{ry + 1}" font-weight="bold">dx</text>')
    out.append(f'<text x="{rx}" y="{y - 10}" font-weight="bold" text-anchor="middle">dy</text>')
    return "".join(out)


def page(title, body, notes, top):
    y0 = 70 if top else H - 95
    lines = "".join(f'<text x="{W / 2}" y="{y0 + 10 + 5.5 * i}" text-anchor="middle" font-size="3.4">{t}</text>'
                    for i, t in enumerate(notes))
    return (f'<section><svg viewBox="0 0 {W} {H}" width="{W}mm" height="{H}mm" stroke="#000" font-family="sans-serif" '
            f'font-size="2.8"><text x="{W / 2}" y="{y0}" text-anchor="middle" font-size="6" stroke="none">{title}</text>'
            f'<g stroke="none">{lines}</g><g stroke-width=".3">{body}</g></svg></section>')


def wrap(text, n=95):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) > n:
            lines.append(cur)
            cur = ""
        cur += (" " if cur else "") + w
    return lines + [cur]


def build(lang, out):
    front_t, back_t, how, then = TEXT[lang]
    front = page(front_t, "".join(cross(x, y) for x, y in POINTS), wrap(how), True)
    back = page(back_t, "".join(rulers(W - x, y) for x, y in POINTS), wrap(how) + [""] + wrap(then), False)
    doc = ('<!doctype html><html><head><meta charset="utf-8"><style>@page { size: Letter; margin: 0; } body { margin: 0; } '
           'section { width: 215.9mm; height: 279.4mm; break-after: page; } svg { display: block; } '
           'text { stroke: none; }</style></head>'
           f'<body>{front}{back}</body></html>')
    page_html = ROOT / "build" / f"duplex-calibration-{lang}.html"
    page_html.parent.mkdir(exist_ok=True)
    page_html.write_text(doc, encoding="utf-8")
    subprocess.run(["chromium", "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                    f"--print-to-pdf={out}", page_html.as_uri()], check=True, capture_output=True)
    print(f"Wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    build("en", ROOT / "rules" / "duplex-calibration.pdf")
    build("fr", ROOT / "rules" / "fr" / "calibrage-recto-verso.pdf")
