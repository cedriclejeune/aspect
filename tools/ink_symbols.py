"""Build the card symbols in rules/symbols/ink/ from Qwen's drawings in rules/symbols/qwen/ (tools/build_cards.py uses them).

Usage: .venv/bin/python tools/ink_symbols.py
Each drawing is cropped to its ink and its lines thickened; the four Defense symbols are a shield drawn here with the stat's
emblem centred on it. Black ink on transparency, like the earlier brush set in rules/symbols/brush/.
"""
import math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps

SRC = Path(__file__).resolve().parent.parent / "rules" / "symbols" / "qwen"
OUT = SRC.parent / "ink"
N = 600  # brush symbols are this order of size; the card prints them at 4.8 mm


def bold(name, grow=11, cut=150, fill=0.9, scale=2):
    im = Image.open(SRC / f"{name}.png").convert("L")
    w, h = im.size
    k = int(w * .03)
    im = im.crop((k, k, w - k, h - k))  # faint edge lines
    x0, y0, x1, y1 = ImageOps.invert(im).point(lambda v: 255 if v > 60 else 0).getbbox()
    side = int(max(x1 - x0, y1 - y0) / fill)
    sq = Image.new("L", (side, side), 255)
    sq.paste(im.crop((x0, y0, x1, y1)), ((side - (x1 - x0)) // 2, (side - (y1 - y0)) // 2))
    sq = sq.resize((scale * N, scale * N), Image.LANCZOS)  # thicken at scale × size: the filter grows the lines 1/scale as much
    sq = sq.filter(ImageFilter.MinFilter(grow)).point(lambda v: 0 if v < cut else 255)
    return sq.resize((N, N), Image.LANCZOS).point(lambda v: 0 if v < 128 else 255)


def shield(emblem):
    """A plain heater shield with a wobbly ink outline, the emblem large in the middle."""
    random.seed(1)
    pts = []
    for i in range(41):  # top edge, slightly bowed
        t = i / 40
        pts.append((90 + 420 * t, 70 + 18 * math.sin(math.pi * t)))
    def side(t):  # straight down for the top third, then curving in to the point
        u = max(0.0, (t - 0.3) / 0.7)
        return 210 * (1 - math.cos(u * math.pi / 2)) ** 0.8
    for i in range(1, 41):  # right side
        t = i / 40
        pts.append((510 - side(t), 70 + 480 * t))
    for i in range(1, 40):  # left side back up
        t = 1 - i / 40
        pts.append((90 + side(t), 70 + 480 * t))
    pts = [(x + random.uniform(-3, 3), y + random.uniform(-3, 3)) for x, y in pts]
    im = Image.new("L", (N, N), 255)
    d = ImageDraw.Draw(im)
    d.line(pts + [pts[0]], fill=0, width=34, joint="curve")
    # centre the emblem's ink on the shield's centre of area (shoelace formula)
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        c = x0 * y1 - x1 * y0
        a += c; cx += (x0 + x1) * c; cy += (y0 + y1) * c
    cx, cy = cx / (3 * a), cy / (3 * a)
    e = emblem.resize((290, 290), Image.LANCZOS).point(lambda v: 0 if v < 128 else 255)
    x0, y0, x1, y1 = ImageOps.invert(e).getbbox()
    e = e.crop((x0, y0, x1, y1))
    im.paste(Image.new("L", e.size, 0), (round(cx - e.width / 2), round(cy - e.height / 2)), ImageOps.invert(e))
    return im


def save(im, path):
    """Black ink on transparency, like the brush symbols."""
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.putalpha(ImageOps.invert(im.convert("L")))
    out.save(path)


# the feather gets a fifth of the others' thickening (scale 10 instead of 2)
plain = {"str": {}, "dex": {"grow": 15, "scale": 10}, "int": {}, "wil": {"grow": 15}, "hp": {}, "spd": {},
         "trait": {}, "technique": {"grow": 13}, "knack": {}}
done = {n: bold(n, **o) for n, o in plain.items()}
for n, im in done.items():
    save(im, OUT / f"{n}.png")
for n in ("str", "dex", "int", "wil"):
    save(shield(done[n]), OUT / f"{n}-def.png")
print(sorted(p.name for p in OUT.glob("*.png")))
