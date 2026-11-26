#!/usr/bin/env python3
"""Character model sheets from a 3D mini: eight turntable views of an STL, redrawn in the flat colour animation style.

Run from the aspect repo root (uses tools/render_minis.py for the clay renders and tools/gen_art.py for the Model Studio key).

  guides <model.stl | mini name> <out dir> [--turn DEG] [--campaign C1]
        render the eight clay views (front, front-3/4 R, right side, back-3/4 R, back, back-3/4 L, left side, front-3/4 L)
        and lay them out as guide.png, two rows of four, the layout of the finished sheet
  sheet <out dir> <prompt.txt | "text"> [--design IMG] [--style IMG]
        draw sheet.png: guide.png redrawn as a flat colour model sheet. The prompt says what the clay can't show
        (colours, materials, face, hair). --design adds a colour picture of the character to copy the colours from
  edit  <sheet.png> <prompt.txt | "text"> <out.png>
        change the design in all eight views at once (new weapon, no beard...), keeping the layout and style
  act   <sheet.png> <prompt.txt | "text"> <out.png> [--wide]
        the character from the sheet acting out the prompt, drawn once, full body on white (--wide: landscape)

Every call is one Qwen Image 3.0 request on Model Studio (at most 3 images; colour kept; prompt_extend off).
Each step writes the prompt it sent next to its image as .txt, so a result can be traced and redone.
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_art as g  # noqa: E402
import render_minis as rm  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
STYLE_REF = str(ROOT / "rules/art/characters/style-refs/style-board.png")
CHARS = ROOT / "rules/art/characters/model-sheets.json"
OUT = Path("/mnt/project-files/studio/model-sheets")
SIZE = "2688*1536"
COLS, ROWS = 4, 2
# turntable order, read left to right then the second row; the angle turns the mini about its vertical axis
VIEWS = [("FRONT", 0), ("FRONT 3/4 RIGHT", 45), ("RIGHT SIDE", 90), ("BACK 3/4 RIGHT", 135),
         ("BACK", 180), ("BACK 3/4 LEFT", 225), ("LEFT SIDE", 270), ("FRONT 3/4 LEFT", 315)]
NEG = ("open mouth, teeth, pencil, watercolour, paper texture, grey clay, 3D render, photorealistic, text, labels, numbers, "
       "watermark, hatching, sketchy lines, gradients, extra limbs, extra weapons, background scenery, grid lines, frames")
NEG_ACT = ("character sheet, several copies of the same character, duplicate character, text, labels, panel border, "
           "photorealistic, 3D render, hatching, pencil texture, sketchy lines, gradients, extra limbs, extra weapons")
FLAT = "flat 2D animation style: clean thin even dark outlines, flat colour fills, one hard-edged shadow tone, no texture"


def text_of(p):
    if p.endswith(".txt") and "\n" not in p:
        return Path(p).read_text().strip()
    return p.strip()


def call(prompt, refs, out, size=SIZE, neg=NEG):
    body = {"model": g.MS_MODELS["qwen-ms"],
            "input": {"messages": [{"role": "user", "content": [{"image": g.ref_url(str(r))} for r in refs] + [{"text": prompt}]}]},
            "parameters": {"size": size, "n": 1, "negative_prompt": neg, "prompt_extend": False, "watermark": False}}
    req = urllib.request.Request(g.key("MODELSTUDIO_URL", g.MS_API), method="POST", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {g.key('DASHSCOPE_API_KEY')}", "Content-Type": "application/json"})
    print(f"Drawing {out} ({len(prompt)} characters, {len(refs)} images)…", flush=True)
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                res = json.load(r)
            break
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 5:  # a few requests at once hit the rate quota
                print("Rate limited, retrying in 20 s…", flush=True)
                time.sleep(20)
                continue
            raise SystemExit(f"Model Studio HTTP {e.code}: {e.read().decode(errors='replace')}")
    url = [c["image"] for ch in res["output"]["choices"] for c in ch["message"]["content"] if "image" in c][0]
    urllib.request.urlretrieve(url, out)
    Path(out).with_suffix(".txt").write_text(prompt + "\n\nImages: " + ", ".join(map(str, refs)) + "\nNegative: " + neg + "\n")
    print("Saved", out, flush=True)


def find_stl(arg, campaign):
    p = Path(arg)
    if p.suffix.lower() == ".stl":
        return p
    found = rm.minis(campaign)
    if arg not in found:
        sys.exit(f"No STL for {arg} in Campagnes/{campaign}/Models/ (found: {', '.join(found)})")
    return found[arg]


def guides(model, out, turn=0, campaign="C1", height=1400):
    """Eight clay renders at the same scale, feet on one line, in a 2688×1536 grid like the sheet to come."""
    out = Path(out)
    (out / "views").mkdir(parents=True, exist_ok=True)
    tri = rm.load_stl(find_stl(model, campaign))
    print(f"{len(tri):,} triangles", flush=True)
    W, H = (int(v) for v in SIZE.split("*"))
    cw, ch = W // COLS, H // ROWS
    sheet = Image.new("L", (W, H), 255)
    renders = []
    for name, deg in VIEWS:
        t = rm.turned(tri, deg + turn)
        renders.append((name, t, rm.render(t, height)))
    # one scale for all eight: the tallest figure fills 88% of a cell's height (renders are cropped to the figure + 6% margin)
    for i, (name, t, img) in enumerate(renders):
        img.save(out / "views" / f"{i + 1}-{name.lower().replace(' ', '-').replace('/', '')}.png")
    figs = [img.crop(Image.eval(img, lambda v: 255 - v).point(lambda v: 255 if v > 8 else 0).getbbox()) for _, _, img in renders]
    tall = max(f.height for f in figs)
    widest = max(f.width for f in figs)
    k = min(ch * .88 / tall, cw * .94 / widest)
    for i, f in enumerate(figs):
        f = f.resize((max(1, int(f.width * k)), max(1, int(f.height * k))), Image.LANCZOS)
        cx, cy = (i % COLS) * cw, (i // COLS) * ch
        foot = cy + int(ch * .95)
        sheet.paste(f, (cx + (cw - f.width) // 2, foot - f.height))
    sheet.save(out / "guide.png")
    labelled = sheet.convert("RGB")
    d = ImageDraw.Draw(labelled)
    for i, (name, _) in enumerate(VIEWS):
        d.text(((i % COLS) * cw + 12, (i // COLS) * ch + 8), f"{i + 1} {name}", fill=(200, 40, 40))
    labelled.save(out / "guide-labelled.png")
    print("Saved", out / "guide.png", flush=True)


def sheet(out, prompt, design=None, style=STYLE_REF, dest="sheet.png"):
    """With a design sheet (already in the flat style) it goes in as image 2 and carries the style too: a third image
    (the style board) made Qwen paste the design sheet over the grid or leave figures grey."""
    out = Path(out)
    refs = [out / "guide.png", design or style]
    p = ("Character model sheet for 2D animation. Image 1 shows eight grey clay renders of one 3D miniature, the same figure "
         "turned on a turntable. Repaint all eight grey figures in place as the coloured character, in the "
         f"{FLAT}, like image 2. Keep each figure's pose, size, position and angle from image 1 exactly; every view must be "
         "fully coloured, none left grey. " +
         ("Image 2 is the character's design sheet: take the face, hair, clothes, gear and colours from it, and not its "
          "layout or poses. " if design else "Image 2 gives the style only; copy none of its people or scenery. ") +
         "Two rows of four, plain white background, mouth closed, exactly one figure per view, no text. "
         "Character: " + text_of(prompt))
    call(p, refs, out / dest)


def build(name, redo_guides=False):
    """One character from model-sheets.json: clay guides if missing, then the sheet, then the eight view cells."""
    c = json.loads(CHARS.read_text())[name]
    out = OUT / name.lower().replace(" ", "-")
    if redo_guides or not (out / "guide.png").exists():
        guides(name, out)
    design = c.get("design")
    sheet(out, c["look"], str(ROOT / design) if design and not design.startswith("/") else design)
    cells(out / "sheet.png")


def cell_box(i, size):
    W, H = size
    cw, ch = W // COLS, H // ROWS
    return ((i % COLS) * cw, (i // COLS) * ch, (i % COLS + 1) * cw, (i // COLS + 1) * ch)


def cells(src):
    """Cut a sheet into its eight views (<sheet>-views/1.webp … 8.webp) for the viewer."""
    im = Image.open(src).convert("RGB")
    d = Path(src).with_name(Path(src).stem + "-views")
    d.mkdir(exist_ok=True)
    for i in range(8):
        im.crop(cell_box(i, im.size)).save(d / f"{i + 1}.webp", quality=88)
    print("Cut", d, flush=True)


def fix(src, view, note, out, use=("clay",)):
    """Redraw one view of a sheet (1-8) and paste it back. Image 2 is the clay of that view (the angle), image 3 another
    view of the same sheet (the colours: with the clay alone, skin and hands stayed grey)."""
    i = int(view) - 1
    im = Image.open(src).convert("RGB")
    box = cell_box(i, im.size)
    stem = Path(out).with_suffix("")
    tmp = Path(f"{stem}.view{i + 1}.png")
    im.crop(box).save(tmp)
    refs = [tmp]
    guide = Path(src).parent / "guide.png"
    if "clay" in use and guide.exists():
        g = Image.open(guide).convert("RGB")
        gt = Path(f"{stem}.clay{i + 1}.png")
        g.crop(cell_box(i, g.size)).save(gt)
        refs.append(gt)
    angle = len(refs) == 2
    if "colour" in use:  # only for views left grey: the other view's pose and gear leak in (a third sword)
        j = 0 if i else 7  # the front view, or the front three-quarter when fixing the front
        ct = Path(f"{stem}.colour{j + 1}.png")
        im.crop(cell_box(j, im.size)).save(ct)
        refs.append(ct)
    p = (f"Edit image 1, one view ({VIEWS[i][0].lower()}) of a character model sheet. Change only this: " + text_of(note) +
         f". Keep the character, the {FLAT}, size, position and white background as they are" +
         (", and keep the figure turned exactly like the grey figure in image 2, which only shows the angle, not colours." if angle else ".") +
         (f" Image {len(refs)} is only a colour guide, the same character from another angle: match its colours, every part "
          "fully coloured, skin, face and hands included, but copy none of its pose, angle or gear: the figure keeps exactly "
          "what it holds now, one of each item." if "colour" in use else "") + " One figure, no text.")
    new = Path(f"{stem}.patch.png")
    call(p, refs, new, size="1344*1536")
    patch = Image.open(new).convert("RGB").resize((box[2] - box[0], box[3] - box[1]), Image.LANCZOS)
    im.paste(patch, box[:2])
    im.save(out)
    print("Saved", out, flush=True)


def pose(src, action, out):
    """A new eight-view sheet of the character in a pose, same layout and angles as the neutral sheet."""
    p = ("Image 1 is an eight-view model sheet of one character: two rows of four turntable views, in this order: front, "
         "front three-quarter, side, back three-quarter, back, back three-quarter, other side, front three-quarter. "
         "Draw a new sheet of the same character with the same layout, the same eight angles in the same places and "
         f"the same design, colours, gear and {FLAT}, white background, but in this pose in every view: " +
         text_of(action) + " The pose is identical in all eight views, only the camera turns. "
         "Exactly one figure per view, one of each weapon, no text.")
    call(p, [src], out)


def edit(src, prompt, out):
    """The clay guide next to the sheet goes in as image 2: without it Qwen turns some views (a side became a back)."""
    guide = Path(src).parent / "guide.png"
    refs = [src] + ([guide] if guide.exists() else [])
    p = ("Edit image 1, an eight-view character model sheet (two rows of four turntable views of one character). Keep the "
         f"exact layout, the white background and the {FLAT}. " +
         ("Keep each figure turned exactly as the grey figure in the same place in image 2, which only shows the angles. "
          if len(refs) > 1 else "Keep each view's angle exactly. ") +
         "Make only these changes, consistently in every view where they show: " + text_of(prompt) +
         " Keep everything else as it is. No text.")
    call(p, refs, out)


def act(src, prompt, out, wide=False):
    p = ("Image 1 is a model sheet showing one character from eight angles. Draw that character exactly once, full body, "
         f"same design, colours and proportions, in the {FLAT}, on a plain white background. Action: " + text_of(prompt) +
         " Expressive pose, clear silhouette. Only one character, carrying only the gear from the sheet, one of each "
         "(one weapon stays one weapon). No text.")
    call(p, [src], out, size=SIZE if wide else "1536*2048", neg=NEG_ACT)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("guides"); a.add_argument("model"); a.add_argument("out")
    a.add_argument("--turn", type=float, default=0); a.add_argument("--campaign", default="C1")
    a = sub.add_parser("sheet"); a.add_argument("out"); a.add_argument("prompt")
    a.add_argument("--design"); a.add_argument("--style", default=STYLE_REF)
    a = sub.add_parser("build"); a.add_argument("name"); a.add_argument("--redo-guides", action="store_true")
    a = sub.add_parser("cells"); a.add_argument("sheet")
    a = sub.add_parser("fix"); a.add_argument("sheet"); a.add_argument("view", type=int, choices=range(1, 9))
    a.add_argument("note"); a.add_argument("out")
    a.add_argument("--use", default="clay", help="extra references, comma-separated: clay (the angle), colour (another "
                   "view, for parts left grey), or none")
    a = sub.add_parser("pose"); a.add_argument("sheet"); a.add_argument("action"); a.add_argument("out")
    a = sub.add_parser("edit"); a.add_argument("sheet"); a.add_argument("prompt"); a.add_argument("out")
    a = sub.add_parser("act"); a.add_argument("sheet"); a.add_argument("prompt"); a.add_argument("out")
    a.add_argument("--wide", action="store_true")
    a = ap.parse_args()
    if a.cmd == "guides":
        guides(a.model, a.out, a.turn, a.campaign)
    elif a.cmd == "sheet":
        sheet(a.out, a.prompt, a.design, a.style)
    elif a.cmd == "build":
        build(a.name, a.redo_guides)
    elif a.cmd == "cells":
        cells(a.sheet)
    elif a.cmd == "fix":
        fix(a.sheet, a.view, a.note, a.out, tuple(a.use.split(",")))
    elif a.cmd == "pose":
        pose(a.sheet, a.action, a.out)
    elif a.cmd == "edit":
        edit(a.sheet, a.prompt, a.out)
    else:
        act(a.sheet, a.prompt, a.out, a.wide)


if __name__ == "__main__":
    main()
