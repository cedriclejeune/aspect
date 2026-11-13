"""Draw the card-type symbols that are still missing, in the style of the stat symbols in rules/symbols/qwen/.

Usage: .venv/bin/python tools/gen_symbols.py                 (every missing symbol)
       .venv/bin/python tools/gen_symbols.py --only spellbook --only nature --count 2
       .venv/bin/python tools/gen_symbols.py --force --only shield    (redraw one that exists)
Then:  .venv/bin/python tools/ink_symbols.py                 (crops and thickens them into rules/symbols/ink/)

Same API and model as the existing symbols (Eachlabs, Qwen Image 3.0 Pro, about $0.075 each; key EACHLABS_API_KEY, see
tools/gen_art.py). Each drawing is square 2048 × 2048. The references are three existing symbols (trait, technique, knack)
by their Eachlabs links, so the new ones copy that ink style; the icon style follows the lessons in rules/art/PROMPTING.md
("Symbols"): thick outlines and solid shapes, the facing said outright, no small extras.
Output: rules/symbols/qwen/<type>.png in greyscale, its link in rules/symbols/qwen/sources.json. With --count N,
<type>-1.png… to choose from: rename the chosen one to <type>.png before running tools/ink_symbols.py.
"""
import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_art import AVOID, call  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "rules" / "symbols" / "qwen"
SOURCES = OUT / "sources.json"
MODEL = "alibaba-qwen-image-3-0-pro-image-edit"  # the edit model takes the reference images
REFS = ["trait.png", "technique.png", "knack.png"]  # existing symbols whose style the new ones copy

STYLE = """Style:
- pen and ink, Chris Riddell, like the reference icons
- black line on white, no grey
- thick heavy outlines, filled solid black shapes
- one object alone, centred, large, whole, with a margin
- bold simple silhouette that reads at 5 mm
- white background, no frame, no text, no letters
Copy only the ink style of the reference images, not their subjects."""

# card type (file name) -> subject. Each must not look like a stat symbol (fist, feather, eye, star, heater shield, heart, boot).
SUBJECTS = {
    "calling": "A banner on a tall upright wooden pole, the cloth hanging to the right with a swallowtail end, "
               "one large plain star on the cloth",
    "armor": "A metal breastplate seen from the front, with shoulder guards and a belt at the waist, no person in it",
    "weapon": "One straight sword pointing straight up, a plain cross guard and a round pommel at the bottom",
    "shield": "A round buckler seen from the front, a large raised boss in the centre and a ring of rivets near the rim",
    "jewelry": "A plain thick ring seen at a slight angle, one large faceted gemstone set on top",
    "instrument": "A lute seen from the front, neck pointing straight up, a round sound hole in the body",
    "consumable": "A round-bellied glass potion flask with a cork stopper, half full of dark liquid",
    "purse": "A leather drawstring coin pouch tied at the neck, three coins lying at its base",
    "recipe": "A parchment scroll held open, rolled at the top and bottom, a few short horizontal ink strokes on it, "
              "no letters",
    "spellbook": "A thick closed leather-bound book seen from the front, metal corner caps, "
                 "a large four-pointed star on the cover",
    "divine": "A plain chalice seen from the side, a small flame rising from the cup",
    "glamour": "A smiling theatre mask seen from the front, empty almond-shaped eye holes, ribbons hanging at both sides",
    "nature": "An animal paw print: one large rounded pad with four oval toe pads above it, all filled solid black",
    "occult": "A single open eye inside a downward-pointing triangle, a small cross below the eye",
}


def sources():
    return json.loads(SOURCES.read_text()) if SOURCES.exists() else {}


def draw(name, count):
    prompt = f"{SUBJECTS[name]}.\n{STYLE}"
    if len(prompt) > 800:
        sys.exit(f"{name}: prompt is {len(prompt)} characters; Qwen takes 800.")
    known = sources()
    refs = [known[r] for r in REFS]
    inp = {"prompt": prompt, "size": "2048*2048", "n": count, "prompt_extend": False, "negative_prompt": AVOID,
           "image_urls": refs}
    pid = call("POST", "/prediction", {"model": MODEL, "version": "1.0.0", "input": inp})["predictionID"]
    print(f"{name}: prediction {pid} started", flush=True)
    deadline = time.time() + 300
    while True:
        time.sleep(2)
        p = call("GET", f"/prediction/{pid}")
        if p["status"] in ("success", "failed", "cancelled", "error"):
            break
        if time.time() > deadline:
            raise RuntimeError(f"{name}: prediction {pid} still {p['status']} after 5 minutes")
    if p["status"] != "success":
        raise RuntimeError(f"{name}: prediction {pid} {p['status']}: {p.get('logs') or p.get('output')}")
    urls = p["output"] if isinstance(p["output"], list) else [p["output"]]
    targets = [OUT / f"{name}.png"] if count == 1 else [OUT / f"{name}-{i}.png" for i in range(1, count + 1)]
    for url, t in zip(urls, targets):
        urllib.request.urlretrieve(url, t)
        Image.open(t).convert("L").save(t)  # the cards are black and white
        SOURCES.write_text(json.dumps(sources() | {t.name: url}, indent=1, sort_keys=True) + "\n")
        print("Saved", t.relative_to(ROOT), flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", action="append", default=[], help="a type from SUBJECTS (repeatable)")
    ap.add_argument("--count", type=int, default=1, help="drawings per type, to choose from")
    ap.add_argument("--force", action="store_true", help="redraw a symbol that already exists")
    a = ap.parse_args()
    unknown = [n for n in a.only if n not in SUBJECTS]
    if unknown:
        sys.exit(f"Unknown: {', '.join(unknown)}. Types: {', '.join(SUBJECTS)}")
    todo = [n for n in (a.only or SUBJECTS) if a.force or not (OUT / f"{n}.png").exists()]
    if not todo:
        sys.exit("Nothing to draw (--force to redraw).")
    failed = []
    for i, n in enumerate(todo):
        if i:
            time.sleep(60)  # small balances run 2 jobs at once, and a slot stays busy a while after one ends
        try:
            draw(n, a.count)
        except Exception as e:
            failed.append(n)
            print(f"{n} failed: {e}", flush=True)
    print(f"Done: {len(todo) - len(failed)} drawn" + (f", failed: {', '.join(failed)}" if failed else ""))


if __name__ == "__main__":
    main()
