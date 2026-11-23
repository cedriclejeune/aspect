"""Render a campaign's 3D-printed minis (Eldritch Foundry STL exports) as grey-clay pictures, the reference images that
tools/gen_art.py --characters redraws in the house ink style.

Usage: .venv/bin/python tools/render_minis.py                       (every mini in Campagnes/C1/Models/)
       .venv/bin/python tools/render_minis.py --campaign C1 --only Hilda --view front --view three-quarter
       .venv/bin/python tools/render_minis.py --turn 45              (turn every mini 45° more, if "front" shows its side)
Reads Campagnes/<campaign>/Models/<Name>/*_char_mm.stl (the figure without its base) and writes
rules/art/characters/<name>-supplied.png (the front view, what gen_art.py sends) and <name>-<view>.png for the other views.
Pure numpy and Pillow (already in .venv): the triangles are sampled into points and depth-sorted, then lit like clay.
"""
import argparse
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "rules" / "art" / "characters"
VIEWS = {"front": 0, "three-quarter": 35, "side": 90, "back": 180}  # turn about the vertical axis, degrees
TILT = 8  # the camera looks slightly down, as at a figure on the table
TURN = {}  # per-mini correction when its STL doesn't face −Y, e.g. {"Kramus": 20}
CLAY, BG = 0.82, 255


def slug_of(name):
    return name.lower().replace(" ", "-")  # as tools/gen_art.py names its files


def load_stl(path):
    """Binary STL → (n, 3, 3) float array of triangle corners, in mm, Z up."""
    data = path.read_bytes()
    n = int(np.frombuffer(data, "<u4", 1, 80)[0])
    if 84 + 50 * n != len(data):
        sys.exit(f"{path}: not a binary STL (ASCII STL isn't read; re-export as binary)")
    rec = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    return np.frombuffer(data, rec, n, 84)["v"].astype(np.float64)


def turned(tri, deg, tilt=TILT):
    a, t = math.radians(deg), math.radians(tilt)
    rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, math.cos(t), -math.sin(t)], [0, math.sin(t), math.cos(t)]])
    return tri @ (rx @ rz).T  # camera on −Y looking at +Y: x right, z up, y depth (smaller = nearer)


def render(tri, size=1400, density=3.0, seed=7):
    """Orthographic grey-clay render, returned as a greyscale image cropped to the figure with a margin, 3:4."""
    lo, hi = tri.reshape(-1, 3).min(0), tri.reshape(-1, 3).max(0)
    scale = size * .92 / max(hi[2] - lo[2], (hi[0] - lo[0]) * 4 / 3)
    W, H = int(size * .75), size
    px = (tri[..., 0] - (lo[0] + hi[0]) / 2) * scale + W / 2
    py = (hi[2] - tri[..., 2]) * scale + size * .04
    depth = tri[..., 1]

    e1, e2 = tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]
    nrm = np.cross(e1, e2)
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
    nrm[nrm[:, 1] > 0] *= -1  # face the camera: the exports aren't always wound the same way
    key, fill = np.array([-.55, -.6, .58]), np.array([.7, -.4, .1])
    key, fill = key / np.linalg.norm(key), fill / np.linalg.norm(fill)
    shade = .28 + .62 * np.clip(nrm @ key, 0, 1) + .18 * np.clip(nrm @ fill, 0, 1)

    area = np.abs((px[:, 1] - px[:, 0]) * (py[:, 2] - py[:, 0]) - (px[:, 2] - px[:, 0]) * (py[:, 1] - py[:, 0])) / 2
    k = np.ceil(area * density).astype(np.int64) + 1
    idx = np.repeat(np.arange(len(tri)), k)
    rng = np.random.default_rng(seed)
    r1, r2 = np.sqrt(rng.random(len(idx))), rng.random(len(idx))
    w0, w1, w2 = 1 - r1, r1 * (1 - r2), r1 * r2
    sx = w0 * px[idx, 0] + w1 * px[idx, 1] + w2 * px[idx, 2]
    sy = w0 * py[idx, 0] + w1 * py[idx, 1] + w2 * py[idx, 2]
    sd = w0 * depth[idx, 0] + w1 * depth[idx, 1] + w2 * depth[idx, 2]
    xi, yi = sx.astype(np.int64), sy.astype(np.int64)
    ok = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H)
    pix, sd, idx = (yi * W + xi)[ok], sd[ok], idx[ok]
    order = np.lexsort((sd, pix))  # by pixel, then nearest first
    pix, sd, idx = pix[order], sd[order], idx[order]
    first = np.ones(len(pix), bool)
    first[1:] = pix[1:] != pix[:-1]

    lum = np.full(W * H, np.nan)
    zbuf = np.full(W * H, np.inf)
    lum[pix[first]] = shade[idx[first]]
    zbuf[pix[first]] = sd[first]
    lum, zbuf = lum.reshape(H, W), zbuf.reshape(H, W)

    hit = ~np.isnan(lum)
    # a pixel the near surface missed shows a far one through it: if it sits well behind most of its neighbours, take theirs
    zf = np.where(hit, zbuf, np.inf)
    zs = np.stack([np.roll(np.roll(zf, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1)])
    ls = np.stack([np.roll(np.roll(np.nan_to_num(lum), dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1)])
    zmed = np.median(zs, axis=0)
    leak = hit & np.isfinite(zmed) & (zf > zmed + 1.0)
    with np.errstate(invalid="ignore"):  # inf − inf off the figure: those pixels aren't leaks anyway
        pick = np.argmin(np.nan_to_num(np.abs(zs - zmed), nan=np.inf), axis=0)
    lum = np.where(leak, np.take_along_axis(ls, pick[None], 0)[0], lum)
    zbuf = np.where(leak, zmed, zbuf)
    img = Image.fromarray(np.where(hit, np.clip(lum * CLAY, 0, 1) * 255, BG).astype(np.uint8))
    mask = Image.fromarray((hit * 255).astype(np.uint8))
    img = Image.composite(img.filter(ImageFilter.MedianFilter(3)), img, mask.filter(ImageFilter.MaxFilter(3)))  # pinholes

    # a dark outline where the depth jumps, so the silhouette and overlaps read like ink lines
    z = np.where(hit, zbuf, zbuf[hit].max() + 50 if hit.any() else 0)
    jump = np.zeros_like(hit)
    step = 1.0  # depth is in mm: a surface 1 mm in front of its neighbour makes an edge
    jump[1:, :] |= np.abs(z[1:, :] - z[:-1, :]) > step
    jump[:, 1:] |= np.abs(z[:, 1:] - z[:, :-1]) > step
    a = np.asarray(img, dtype=np.float64)
    a[jump] *= .35
    img = Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.SMOOTH)

    box = mask.getbbox()
    if box:
        x0, y0, x1, y1 = box
        m = int((y1 - y0) * .06)
        h = (y1 - y0) + 2 * m
        w = max(int(h * .75), (x1 - x0) + 2 * m)
        h = int(w * 4 / 3)
        canvas = Image.new("L", (w, h), BG)
        canvas.paste(img.crop((x0, y0, x1, y1)), ((w - (x1 - x0)) // 2, (h - (y1 - y0)) // 2))
        img = canvas
    return img


def minis(campaign):
    folder = ROOT / "Campagnes" / campaign / "Models"
    found = {}
    for d in sorted(p for p in folder.glob("*") if p.is_dir()):
        stl = sorted(d.glob("*_char_mm.stl")) or sorted(d.glob("*_unified_mm.stl")) or sorted(d.glob("*.stl"))
        if stl:
            found[d.name] = stl[0]
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--campaign", default="C1", help="folder under Campagnes/ (default C1)")
    ap.add_argument("--only", action="append", default=[], help="just this mini (its folder name); repeatable")
    ap.add_argument("--view", action="append", choices=list(VIEWS), help="views to render (default front and three-quarter)")
    ap.add_argument("--turn", type=float, default=0, help="extra turn for every mini, degrees")
    ap.add_argument("--size", type=int, default=1400, help="render height in pixels (default 1400)")
    a = ap.parse_args()
    found = minis(a.campaign)
    names = a.only or list(found)
    missing = [n for n in names if n not in found]
    if missing:
        sys.exit(f"No STL for {', '.join(missing)} in Campagnes/{a.campaign}/Models/ (found: {', '.join(found) or 'none'})")
    OUT.mkdir(parents=True, exist_ok=True)
    for n in names:
        tri = load_stl(found[n])
        print(f"{n}: {len(tri):,} triangles", flush=True)
        for view in a.view or ["front", "three-quarter"]:
            img = render(turned(tri, VIEWS[view] + TURN.get(n, 0) + a.turn), a.size)
            t = OUT / (f"{slug_of(n)}-supplied.png" if view == "front" else f"{slug_of(n)}-{view}.png")
            img.save(t)
            print("Saved", t.relative_to(ROOT), flush=True)


if __name__ == "__main__":
    main()
