"""Cricut cut files for the printed base set: one SVG per kind of page, page-sized, in rules/cricut/.

Usage: .venv/bin/python tools/cut_svg.py [--lang fr] [--dx MM] [--dy MM]
Reads build/base-set[-fr].html (run tools/build_cards.py first) and lays out the cut lines as the sheets' CSS does:
cards (63 × 88 mm, 3 mm corners) and foe and tally cards (126 × 88 mm) centred on the page, 2 mm apart; Slot frames
67 × 98 mm edge to edge (each shared edge cut once), with their two corner slits. Cards are cut 1 mm outside their
full-size border, frames on their full-size edge; both print at 95 % (PRINT_SCALE), so the cut leaves a margin round each.
Two-sided pages are cut from the front, so the back pages get no file.
Each file is a single path (one layer in Design Space, nothing to Attach), with a 0.5 mm square at two opposite page
corners, so Design Space keeps the cuts where they are on the page.
Also writes rules/cricut/calibrage-impression.pdf (rulers to print, needs Inkscape) and calibrage.svg (a slit across each
ruler's 0): the number where a slit crosses its ruler is the --dx or --dy to give.
Landscape pages are cut turned a quarter clockwise (the page's top to the right), so every file is 215.9 mm wide.
--dx, --dy shift every cut (and the far corner mark); with the paper placed 1 in from the mat's corner, add 25.4 to each (in mm, + is right and down) to make up for a printer that prints off-centre.
"""
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "rules" / "cricut"
PORTRAIT, LANDSCAPE = (215.9, 279.4), (279.4, 215.9)
MARGIN = 1  # cards are cut this far outside their border, so a slightly off cut never bites into it
PRINT_SCALE = .95  # tools/build_cards.py: cards and frames print 95 % of their size, centred where they are cut
SLITS = (((550, 68), (667, 185)), ((13, 855), (130, 972)))  # tools/illustrations.py frame_body, in 0.1 mm


class Sheets(HTMLParser):
    """Each page: its class and the classes of its direct children."""
    def __init__(self):
        super().__init__()
        self.pages, self.depth, self.open = [], 0, None

    def handle_starttag(self, tag, attrs):
        if tag in ("img", "br", "hr", "meta", "link", "input"):
            return
        self.depth += 1
        cls = dict(attrs).get("class", "") or ""
        if tag == "section":
            self.pages.append((cls.split(), []))
            self.open = self.depth
        elif self.open is not None and self.depth == self.open + 1:
            self.pages[-1][1].append((tag, cls.split()))

    def handle_endtag(self, tag):
        if tag in ("img", "br", "hr", "meta", "link", "input"):
            return
        if self.open == self.depth:
            self.open = None
        self.depth -= 1


def grid(n, cols, w, h, gap, page):
    """Top-left corners of n grid cells, the grid centred on the page as by justify- and align-content: center."""
    rows = -(-n // cols)
    x0 = (page[0] - (cols * w + (cols - 1) * gap)) / 2
    y0 = (page[1] - (rows * h + (rows - 1) * gap)) / 2
    return [(x0 + (i % cols) * (w + gap), y0 + (i // cols) * (h + gap)) for i in range(n)]


SHIFT = [0.0, 0.0]  # --dx, --dy
TURN = [0.0]  # a landscape page's height while it is laid out turned a quarter clockwise (its top to the right), else 0


def turn(x, y):
    return (TURN[0] - y, x) if TURN[0] else (x, y)


def pt(x, y):
    """A shifted point, kept on the page: a cut past its top or left edge would move the whole file in Design Space."""
    x, y = turn(x, y)
    return f"{max(0, x + SHIFT[0]):.3f} {max(0, y + SHIFT[1]):.3f}"


def line(ax, ay, bx, by):
    return f"M{pt(ax, ay)} L{pt(bx, by)}"


def card_cut(x, y, w, h):
    """A rounded rectangle MARGIN outside the card's edge, as path data."""
    r, (dx, dy) = 3 + MARGIN, SHIFT
    if TURN[0]:
        x, y, w, h = TURN[0] - y - h, x, h, w
    x0, y0 = max(0, x - MARGIN + dx), max(0, y - MARGIN + dy)  # kept on the page, like pt()
    x1, y1 = x + w + MARGIN + dx, y + h + MARGIN + dy
    arc = f"A{r:.3f} {r:.3f} 0 0 1"
    p = lambda a, b: f"{a:.3f} {b:.3f}"
    return (f"M{p(x0 + r, y0)} L{p(x1 - r, y0)} {arc} {p(x1, y0 + r)} L{p(x1, y1 - r)} {arc} {p(x1 - r, y1)} "
            f"L{p(x0 + r, y1)} {arc} {p(x0, y1 - r)} L{p(x0, y0 + r)} {arc} {p(x0 + r, y0)} Z")


def frame_cuts(cells):
    """Frames sit edge to edge: each edge is cut once, not once per frame."""
    edges, out = {}, []
    for x, y in cells:
        for a, b in (((x, y), (x + 67, y)), ((x, y + 98), (x + 67, y + 98)), ((x, y), (x, y + 98)), ((x + 67, y), (x + 67, y + 98))):
            edges[tuple(round(v, 3) for v in a + b)] = None
    out += [line(*e) for e in edges]
    k = lambda v, size: size / 2 + (v / 10 - size / 2) * PRINT_SCALE  # the frame prints scaled about its centre
    for x, y in cells:
        for (ax, ay), (bx, by) in SLITS:
            out.append(line(x + k(ax, 67), y + k(ay, 98), x + k(bx, 67), y + k(by, 98)))
    return out


def layout(cls, children):
    """(page size, cut shapes) of a sheet, or None for a page with nothing to cut."""
    if "sheet" not in cls:
        return None
    TURN[0] = LANDSCAPE[1] if "frames" in cls or "wide4" in cls else 0  # cut standing, to fit the mat's width
    if "frames" in cls:
        return PORTRAIT, frame_cuts(grid(len(children), 4, 67, 98, 0, LANDSCAPE))
    wide = "wide4" in cls
    page, cols, w = (LANDSCAPE, 2, 126) if wide else (PORTRAIT, 3, 63)
    cells = grid(len(children), cols, w, 88, 2, page)
    return PORTRAIT, [card_cut(x, y, w, 88) for (x, y), (_, c) in zip(cells, children) if "gap" not in c]


def svg(page, shapes):
    """All the cuts as one path, so Design Space takes them as one layer and keeps them in place on the page."""
    W, H = page
    marks = f"M0 0 h.5 v.5 h-.5 Z M{pt(W - .5, H - .5)} h.5 v.5 h-.5 Z"  # the second one on the paper's far corner
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">'
            f'<path fill="none" stroke="#000" stroke-width=".2" d="{marks} {" ".join(shapes)}"/></svg>\n')


GAUGES = ((30, 30), (100, 140), (170, 250))  # calibration gauges: top left, middle, bottom right of a portrait page


def calibration():
    """A page to print (rulers) and its cut file (a slit across each ruler's 0). Each tick is labelled with the
    correction it calls for: where the slit crosses the ruler is the --dx or --dy to give."""
    ink, cuts = [], []
    for gx, gy in GAUGES:
        for axis in "xy":
            ox, oy = (gx, gy) if axis == "x" else (gx + 26, gy - 10)
            for k in range(-16, 17):  # a tick every 0.5 mm, ±8 mm
                d, n = k / 2, 3 if k % 2 == 0 else 1.6
                a, b = ((ox + d, oy), (ox + d, oy + n)) if axis == "x" else ((ox, oy + d), (ox - n, oy + d))
                ink.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke-width="{.25 if k else .4}"/>')
                if k % 4 == 0:
                    v = f"{-d:+g}" if k else "0"
                    tx, ty = (ox + d, oy + (5.6 if k % 8 == 0 else 8.4)) if axis == "x" else (ox + 1.2, oy + d + .7)
                    ink.append(f'<text x="{tx}" y="{ty}" font-size="2" text-anchor="{"middle" if axis == "x" else "start"}"'
                               f' stroke="none">{v}</text>')
            label = (ox - 12.5, oy + 2.2) if axis == "x" else (ox - 4.5, oy - 9.5)
            ink.append(f'<text x="{label[0]}" y="{label[1]}" font-size="2.6" font-weight="bold" stroke="none">'
                       f'{"dx" if axis == "x" else "dy"}</text>')
            cuts.append(line(ox, oy - 3, ox, oy + 3.5) if axis == "x" else line(ox - 3.5, oy, ox + 3, oy))
    W, H = PORTRAIT
    text = ('<text x="108" y="60" font-size="5" text-anchor="middle" font-weight="bold" stroke="none">Calibrage Cricut</text>'
            '<text x="108" y="68" font-size="3.2" text-anchor="middle" stroke="none">Imprimer à 100 %, couper calibrage.svg,'
            ' lire le chiffre où passe chaque fente.</text>')
    page = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">'
            f'<rect width="{W}" height="{H}" fill="#fff"/><g stroke="#000" fill="#000" font-family="sans-serif">'
            f'{text}{"".join(ink)}</g></svg>\n')
    return page, svg(PORTRAIT, cuts)


def main():
    args = sys.argv[1:]
    opt = lambda k, d: type(d)(args[args.index(k) + 1]) if k in args else d
    lang, dx, dy = opt("--lang", "en"), opt("--dx", 0.0), opt("--dy", 0.0)
    SHIFT[:] = dx, dy
    parser = Sheets()
    parser.feed((ROOT / "build" / f"base-set{'-fr' if lang == 'fr' else ''}.html").read_text())
    files, last = {}, None  # svg text → (name, page numbers)
    for num, (cls, children) in enumerate(parser.pages, 1):
        cut = layout(cls, children)
        two_sided = "frames" not in cls
        back = cut and two_sided and last == (tuple(cls), "front")
        last = (tuple(cls), "back" if back else "front") if cut else None
        if not cut or back:
            continue
        text = svg(*cut)
        kind = "cadres" if "frames" in cls else "larges" if "wide4" in cls else "cartes"
        if text not in files:
            same = sum(1 for n, _ in files.values() if n.startswith(kind))
            files[text] = (kind if not same else f"{kind}-{same + 1}", [])
        files[text][1].append(num)
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    for text, (name, nums) in files.items():
        (OUT / f"{name}.svg").write_text(text)
        print(f"rules/cricut/{name}.svg: pages {', '.join(map(str, nums))}")
    TURN[0] = 0
    page, cut = calibration()
    (OUT / "calibrage.svg").write_text(cut)
    (BUILD := ROOT / "build").mkdir(exist_ok=True)
    (BUILD / "calibrage-impression.svg").write_text(page)
    subprocess.run(["inkscape", str(BUILD / "calibrage-impression.svg"), "--export-type=pdf",
                    f"--export-filename={OUT / 'calibrage-impression.pdf'}"], check=True, capture_output=True)
    print("rules/cricut/calibrage-impression.pdf, to print; rules/cricut/calibrage.svg, its cuts")


if __name__ == "__main__":
    main()
