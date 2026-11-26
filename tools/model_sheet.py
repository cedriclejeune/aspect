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
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_art as g  # noqa: E402
import render_minis as rm  # noqa: E402

STYLE_REF = "/mnt/project-files/studio/flat/sheets/style-bg.png"
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
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            res = json.load(r)
    except urllib.error.HTTPError as e:
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


def sheet(out, prompt, design=None, style=STYLE_REF):
    out = Path(out)
    refs = [out / "guide.png", style] + ([design] if design else [])
    p = ("Character model sheet for 2D animation. Image 1 shows eight grey clay renders of one 3D miniature, the same figure "
         "turned on a turntable. Redraw every figure in place, same pose, proportions, clothes and gear, as the same coloured "
         f"character, in the {FLAT}, like image 2. " + ("Copy the colours and face from image 3. " if design else "") +
         "Keep the two rows of four, the sizes and the angles exactly: front, front three-quarter, side, back three-quarter, "
         "back, back three-quarter, other side, front three-quarter. Plain white background, mouth closed, no text. "
         "Character: " + text_of(prompt))
    call(p, refs, out / "sheet.png")


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
    a = sub.add_parser("edit"); a.add_argument("sheet"); a.add_argument("prompt"); a.add_argument("out")
    a = sub.add_parser("act"); a.add_argument("sheet"); a.add_argument("prompt"); a.add_argument("out")
    a.add_argument("--wide", action="store_true")
    a = ap.parse_args()
    if a.cmd == "guides":
        guides(a.model, a.out, a.turn, a.campaign)
    elif a.cmd == "sheet":
        sheet(a.out, a.prompt, a.design, a.style)
    elif a.cmd == "edit":
        edit(a.sheet, a.prompt, a.out)
    else:
        act(a.sheet, a.prompt, a.out, a.wide)


if __name__ == "__main__":
    main()
