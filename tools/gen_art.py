"""Generate a foe drawing for the cards with the Eachlabs API (https://docs.eachlabs.ai).

Usage: .venv/bin/python tools/gen_art.py "Goblin Shaman" "a hunched goblin with a bone staff and a fetish necklace"
       .venv/bin/python tools/gen_art.py "Goblin Shaman" "..." --model qwen-turbo --count 3
       .venv/bin/python tools/gen_art.py --batch [--only Orc --only Troll]   (foes in tools/art_prompts.py without a drawing)
       .venv/bin/python tools/gen_art.py --redo Bandit --change "bone mask instead of the sack mask"   (edit the drawing)
       .venv/bin/python tools/gen_art.py --items --batch [--only Dagger]   (gear card backs, ITEMS in tools/art_prompts.py)
       .venv/bin/python tools/gen_art.py --items Dagger --count 2   (a name alone takes its subject from tools/art_prompts.py)
Drawings are saved in greyscale (Pillow, in .venv). rules/art/sources.json keeps each drawing's Eachlabs URL, so --redo can
send the current drawing as the reference (the API takes URLs only); the replaced drawing is kept in rules/art/old/.
Output: rules/art/<name>.png (what tools/build_cards.py picks up), or <name>-1.png, -2.png… with --count.
--items draws gear for the card backs instead: ITEM_STYLE in place of STYLE, saved in rules/art/items/.
The key is EACHLABS_API_KEY, from the environment or the git-ignored .env at the repo root.
--model picks the image model (qwen: Qwen Image 3.0 Pro, $0.075; qwen-turbo: Qwen Image 2.1 Turbo, $0.016; qwen-pro21: Qwen Image 2.1 Pro, $0.04;
         seedream: Seedream v5 Lite, $0.035; flux3: Flux 3, $0.041; luma: Luma Uni-1, $0.042; nano: Nano Banana 2).
Every drawing copies the ink style of REF, a Chris Riddell sketch sheet (many small figures, so no one subject gets copied);
--ref replaces it with other images (URLs; local files are sent inline, which the API may refuse), --no-ref drops it.
The house style (STYLE: Chris Riddell pen and ink, white background) is added to every prompt; the card crops to 50 × 67 mm.
"""
import argparse
import base64
import datetime
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "rules" / "art"
ITEM_ART = ART / "items"
SOURCES = ART / "sources.json"  # drawing path under rules/art/ -> Eachlabs URL of the image it came from
API = "https://api.eachlabs.ai/v1"
AVOID = ("colour, grey wash, gradients, photorealistic, realistic anatomy, dense texture, heavy shading, frame, border, text, "
         "signature, malformed weapons, broken objects, extra limbs")
# model name -> (text-to-image slug, edit slug, input builder[, reference input]); slugs and inputs from GET /v1/models/<slug>
MODELS = {
    "nano": ("nano-banana-2-text-to-image", "nano-banana-2-edit",
             lambda prompt, count: {"prompt": prompt, "aspect_ratio": "3:4", "resolution": "2K", "num_images": count,
                                    "output_format": "png"}),
    "qwen": ("alibaba-qwen-image-3-0-pro-text-to-image", "alibaba-qwen-image-3-0-pro-image-edit",
             lambda prompt, count: {"prompt": prompt, "size": "1728*2368", "n": count, "prompt_extend": False,
                                    "negative_prompt": AVOID}),
    "qwen-turbo": ("alibaba-qwen-image-2-1-turbo-text-to-image", "alibaba-qwen-image-2-1-turbo-image-edit",  # no negative prompt
                   lambda prompt, count: {"prompt": f"{prompt} Avoid: {AVOID}.", "size": "960*1280", "n": count,
                                          "prompt_extend": False}),
    "qwen-pro21": ("alibaba-qwen-image-2-1-pro-text-to-image", "alibaba-qwen-image-2-1-pro-image-edit",  # $0.04
                   lambda prompt, count: {"prompt": prompt, "size": "1728*2368", "n": count, "prompt_extend": False,
                                          "negative_prompt": AVOID}),
    "seedream": ("bytedance-seedream-v5-lite-text-to-image", "bytedance-seedream-v5-lite-edit",  # $0.035
                 lambda prompt, count: {"prompt": f"{prompt} Avoid: {AVOID}.", "aspect_ratio": "3:4", "resolution": "2K",
                                        "num_images": count, "output_format": "png"}, "image"),
    "flux3": ("flux-3-text-to-image", "flux-3-edit",  # $0.041 at 1k, one image per call
              lambda prompt, count: {"prompt": f"{prompt} Avoid: {AVOID}.", "aspect_ratio": "3:4", "resolution": "1k",
                                     "grounding": False}),
    "luma": ("luma-uni-1-text-to-image", "luma-uni-1-text-to-image",  # $0.042, one image per call; no 3:4
             lambda prompt, count: {"prompt": f"{prompt} Avoid: {AVOID}.", "aspect_ratio": "2:3", "output_format": "png"},
             "reference_image_urls"),
}
STYLE = """Style:
- pen and ink, Chris Riddell
- black line on white, no grey
- varied contour lines, sparse hatching in shadows only
- mostly untouched white paper
- grotesque caricature, oversized hands and feet
- one full-body figure alone, short ground shadow
- white background, no frame, no text"""
ITEM_STYLE = """Style:
- pen and ink, Chris Riddell
- black line on white, no grey
- varied contour lines, sparse hatching in shadows only
- mostly untouched white paper
- well-used object, slightly exaggerated proportions
- one object alone, centred, large in the frame, clear simple outline
- white background, no frame, no text"""
REF_STYLE = "Copy only the ink style of the reference, not its subjects or labels."
EDIT = "Edit the reference drawing. Make these changes: {change}. Keep everything else exactly as it is."
REF = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSJcSel0OCyTLDZmaKmoofuv9kZqkJggSAfbPhz7CLysw&s=10"


def key():
    if os.environ.get("EACHLABS_API_KEY"):
        return os.environ["EACHLABS_API_KEY"]
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            name, _, value = line.partition("=")
            if name.strip() == "EACHLABS_API_KEY" and value.strip():
                return value.strip().strip("'\"")
    sys.exit("No EACHLABS_API_KEY: put EACHLABS_API_KEY=... in .env at the repo root.")


def call(method, path, body=None, tries=30):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {key()}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 429 and tries > 1:  # small balances may only run 2 predictions at once
            print("Rate limited, retrying in 10 s…")
            time.sleep(10)
            return call(method, path, body, tries - 1)
        raise RuntimeError(f"Eachlabs {method} {path}: HTTP {e.code} {e.read().decode(errors='replace')}")
    except (urllib.error.URLError, ConnectionError, TimeoutError) as e:  # dropped connection
        if tries > 1 and method == "GET":
            time.sleep(5)
            return call(method, path, body, tries - 1)
        raise RuntimeError(f"Eachlabs {method} {path}: {e}")


def ref_url(ref):
    if ref.startswith(("http://", "https://")):
        return ref
    p = Path(ref)
    return f"data:{mimetypes.guess_type(p)[0] or 'image/png'};base64,{base64.b64encode(p.read_bytes()).decode()}"


def generate(model, prompt, refs, count):
    text, edit, build, *ref_key = MODELS[model]
    inp = build(prompt, count)
    if refs:
        inp[ref_key[0] if ref_key else "image_urls"] = [ref_url(r) for r in refs]
    pid = call("POST", "/prediction", {"model": edit if refs else text, "version": "1.0.0", "input": inp})["predictionID"]
    print(f"Prediction {pid} started", flush=True)
    deadline = time.time() + 300
    while True:
        time.sleep(2)
        p = call("GET", f"/prediction/{pid}")
        if p["status"] in ("success", "failed", "cancelled", "error"):
            break
        if time.time() > deadline:
            raise RuntimeError(f"Prediction {pid} still {p['status']} after 5 minutes; giving up (it may still finish and bill).")
    if p["status"] != "success":
        raise RuntimeError(f"Prediction {pid} {p['status']}: {p.get('logs') or p.get('output')}")
    cost = (p.get("metrics") or {}).get("cost")
    print(f"Prediction {pid} done" + (f" (${cost})" if cost is not None else ""))
    out = p["output"]
    return out if isinstance(out, list) else [out]


def slug_of(name):
    return name.lower().replace(" ", "-")  # the file name tools/build_cards.py looks for


def sources():
    return json.loads(SOURCES.read_text()) if SOURCES.exists() else {}


def table(items):
    """(subjects, style, folder) for foes or, with items, gear card backs."""
    import art_prompts
    return (art_prompts.ITEMS, ITEM_STYLE, ITEM_ART) if items else (art_prompts.SUBJECTS, STYLE, ART)


def prompt_for(subject, model, refs, edit=None, style=STYLE):
    if edit:  # edit = the changes, said outright: a subject that just leaves something out changes nothing
        prompt = f"{EDIT.format(change=edit)}\nDescription: {subject}."  # the drawing itself carries the style
    else:
        prompt = f"{subject}.\n{style}" + (f"\n{REF_STYLE}" if refs else "")
    if model == "qwen" and len(prompt) > 800:
        raise ValueError(f"Prompt is {len(prompt)} characters; Qwen takes 800. Shorten the subject by {len(prompt) - 800}.")
    return prompt


def make(name, subject, model, refs, count=1, edit=None, items=False):
    """Draw one foe, or one gear card back with items; returns the saved files."""
    _, style, folder = table(items)
    slug = slug_of(name)
    targets = [folder / f"{slug}.png"] if count == 1 else [folder / f"{slug}-{i}.png" for i in range(1, count + 1)]
    folder.mkdir(parents=True, exist_ok=True)
    saved = []
    for url, t in zip(generate(model, prompt_for(subject, model, refs, edit, style), refs, count), targets):
        for attempt in range(3):
            try:
                urllib.request.urlretrieve(url, t)
                break
            except (urllib.error.URLError, ConnectionError, TimeoutError):
                if attempt == 2:
                    raise RuntimeError(f"Could not download {url}; fetch it by hand into {t}")
                time.sleep(5)
        Image.open(t).convert("L").save(t)  # the models slip in colour now and then; the cards are black and white
        SOURCES.write_text(json.dumps(sources() | {t.relative_to(ART).as_posix(): url}, indent=1, sort_keys=True) + "\n")
        print("Saved", t.relative_to(ROOT), flush=True)
        saved.append(t)
    return saved


def batch(names, model, refs, force, items=False):
    SUBJECTS, style, folder = table(items)
    unknown = [n for n in names if n not in SUBJECTS]
    if unknown:
        sys.exit(f"Not in tools/art_prompts.py: {', '.join(unknown)}")
    todo = {n: SUBJECTS[n] for n in names or SUBJECTS}
    skip = [n for n in todo if not force and (folder / f"{slug_of(n)}.png").exists()]
    if skip:
        print(f"Skipping (drawing exists, --force to redo): {', '.join(skip)}")
    todo = {n: s for n, s in todo.items() if n not in skip}
    for s in todo.values():
        prompt_for(s, model, refs, style=style)  # check every length before spending anything
    failed = []
    for i, (n, s) in enumerate(todo.items()):
        if i:
            time.sleep(60)  # small balances may run 2 jobs at once, and Eachlabs keeps a slot busy a while after one ends
        try:
            make(n, s, model, refs, items=items)
        except Exception as e:
            failed.append(n)
            print(f"{n} failed: {e}", flush=True)
    print(f"Done: {len(todo) - len(failed)} drawn" + (f", failed: {', '.join(failed)}" if failed else ""))


def redo(names, model, change, extra_refs=(), items=False):
    """Edit each foe's current drawing (image 1) with the changes; extra_refs follow as image 2, 3… for the change to point at."""
    SUBJECTS, _, folder = table(items)
    known = sources()
    for n in names:
        if n not in SUBJECTS or not (folder / f"{slug_of(n)}.png").exists():
            sys.exit(f"{n}: needs a subject in tools/art_prompts.py and a drawing in {folder.relative_to(ROOT)}/")
        prompt_for(SUBJECTS[n], model, ["x"], edit=change)  # check every length before spending anything
    for n in names:
        old = folder / f"{slug_of(n)}.png"
        ref = known.get(old.relative_to(ART).as_posix()) or str(old)  # a local file goes inline, which the API may refuse
        keep = ART / "old" / f"{old.stem}-{datetime.datetime.now():%Y%m%d-%H%M%S}.png"
        keep.parent.mkdir(exist_ok=True)
        keep.write_bytes(old.read_bytes())
        try:
            make(n, SUBJECTS[n], model, [ref, *extra_refs], edit=change, items=items)
            print(f"Previous drawing kept as {keep.relative_to(ROOT)}")
        except (RuntimeError, ValueError) as e:
            print(f"{n} failed: {e}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", nargs="?", help="foe name as on its card, e.g. 'Ogre Chieftain'")
    ap.add_argument("subject", nargs="?", help="what to draw")
    ap.add_argument("--batch", action="store_true", help="draw the foes in tools/art_prompts.py that have no drawing yet")
    ap.add_argument("--only", action="append", default=[], help="with --batch: just this foe; repeatable")
    ap.add_argument("--redo", action="append", default=[], metavar="FOE",
                    help="edit this foe's drawing (with --change); repeatable")
    ap.add_argument("--change", help="with --redo: the changes to make, as instructions, e.g. 'remove the bone'; "
                    "--ref images are sent as image 2, 3… for it to point at")
    ap.add_argument("--ref", action="append", default=[], help="style reference image instead of REF (URL or file); repeatable")
    ap.add_argument("--no-ref", action="store_true", help="no style reference: text-to-image from the prompt alone")
    ap.add_argument("--count", type=int, default=1, choices=range(1, 5), help="variants to make (1-4)")
    ap.add_argument("--model", choices=MODELS, default="qwen", help="image model (default qwen)")
    ap.add_argument("--items", action="store_true", help="gear card backs (ITEMS, ITEM_STYLE, rules/art/items/) instead of foes")
    ap.add_argument("--force", action="store_true", help="overwrite an existing drawing")
    a = ap.parse_args()
    refs = [] if a.no_ref else a.ref or [REF]
    if a.redo:
        if not a.change:
            ap.error("--redo needs --change: say what to change ('remove the bone; add the missing hind leg')")
        return redo(a.redo, a.model, a.change, a.ref, a.items)
    if a.batch:
        return batch(a.only, a.model, refs, a.force, a.items)
    subjects, _, folder = table(a.items)
    subject = a.subject or subjects.get(a.name)  # a name alone draws its subject from tools/art_prompts.py
    if not (a.name and subject):
        ap.error("give a name and a subject (or a name from tools/art_prompts.py), or --batch")

    slug = slug_of(a.name)
    targets = [folder / f"{slug}.png"] if a.count == 1 else [folder / f"{slug}-{i}.png" for i in range(1, a.count + 1)]
    if not a.force and any(t.exists() for t in targets):
        sys.exit(f"{', '.join(str(t.relative_to(ROOT)) for t in targets if t.exists())} exists; pass --force to overwrite.")
    try:
        make(a.name, subject, a.model, refs, a.count, items=a.items)
    except (RuntimeError, ValueError) as e:
        sys.exit(str(e))
    if a.count > 1:
        print(f"Rename the one you keep to {folder.relative_to(ROOT)}/{slug}.png for the card to use it.")

if __name__ == "__main__":
    main()
