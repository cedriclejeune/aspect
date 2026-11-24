"""Generate a foe drawing for the cards with the Eachlabs API (https://docs.eachlabs.ai), or Alibaba Model Studio.

Usage: .venv/bin/python tools/gen_art.py "Goblin Shaman" "a hunched goblin with a bone staff and a fetish necklace"
       .venv/bin/python tools/gen_art.py "Goblin Shaman" "..." --model qwen-turbo --count 3
       .venv/bin/python tools/gen_art.py --batch [--only Orc --only Troll]   (foes in tools/art_prompts.py without a drawing)
       .venv/bin/python tools/gen_art.py --redo Bandit --change "bone mask instead of the sack mask"   (edit the drawing)
       .venv/bin/python tools/gen_art.py --items --batch [--only Dagger]   (gear card backs, ITEMS in tools/art_prompts.py)
       .venv/bin/python tools/gen_art.py --items Dagger --count 2   (a name alone takes its subject from tools/art_prompts.py)
       .venv/bin/python tools/gen_art.py --cards --batch   (Callings, Runes, deck cards and Wounds: CARDS, in rules/art/cards/)
       .venv/bin/python tools/gen_art.py --characters --batch [--only Hilda]   (the campaign's Bearers: CHARACTERS, from the
         grey renders of their minis made by tools/render_minis.py, in rules/art/characters/)
       .venv/bin/python tools/gen_art.py --symbols --batch --force [--only str]   (card symbols: SYMBOLS, in rules/symbols/qwen/;
         then run tools/ink_symbols.py)
Drawings are saved in greyscale (Pillow, in .venv). --redo sends the current drawing as the reference: inline to Model Studio,
as its Eachlabs URL (kept in rules/art/sources.json) to Eachlabs; the replaced drawing is kept in rules/art/old/.
Output: rules/art/<name>.png (what tools/build_cards.py picks up), or <name>-1.png, -2.png… with --count.
--items draws gear and gold for the card backs instead: ITEM_STYLE in place of STYLE, saved in rules/art/items/.
--cards draws the other card backs (one figure, STYLE), saved in rules/art/cards/.
--characters draws the campaign's Bearers for their Bearer card portraits (tools/build_cards.py --bearers): image 1 is the
grey render of the character's mini (rules/art/characters/<name>-supplied.png, from tools/render_minis.py), whose figure is
copied; the style reference follows as image 2. CHARACTER_STYLE is STYLE without the foes' grotesque caricature. Model Studio (--model qwen-ms) takes the local render inline; Eachlabs may not.
--symbols draws the card symbols (SYMBOL_STYLE, square, no style reference: the sketch sheet made them thin and pale),
saved in rules/symbols/qwen/ with their links in its sources.json; the replaced drawings go to rules/symbols/qwen/old/.
Keys come from the environment or the git-ignored .env at the repo root: EACHLABS_API_KEY for Eachlabs, DASHSCOPE_API_KEY
for Model Studio (and MODELSTUDIO_URL to use another workspace than MS_API).
--model picks the image model (qwen: Qwen Image 3.0 Pro, $0.075; qwen-ms, the default: Qwen Image 3.0 on Model Studio,
         working since 2026-11-17 and preferred over Eachlabs; qwen-turbo: Qwen Image 2.1 Turbo, $0.016; qwen-pro21: Qwen Image 2.1 Pro, $0.04;
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
CARD_ART = ART / "cards"
CHARACTER_ART = ART / "characters"
SYMBOL_ART = ROOT / "rules" / "symbols" / "qwen"
SOURCES = ART / "sources.json"  # drawing path under rules/art/ -> Eachlabs URL of the image it came from
API = "https://api.eachlabs.ai/v1"
MS_API = "https://ws-lz48fh0uf1m4zk5e.ap-southeast-1.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
MS_MODELS = {"qwen-ms": "qwen-image-3.0"}  # model name -> Model Studio model; it draws and edits (reference images in the message)
AVOID = ("colour, grey wash, gradients, photorealistic, realistic anatomy, dense texture, heavy shading, frame, border, text, "
         "signature, malformed weapons, broken objects, extra limbs, handsome, pretty, idealised face, model looks, smooth skin")
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
CHARACTER_STYLE = STYLE.replace("- grotesque caricature, oversized hands and feet",  # the players' Bearers: same ink, not
                                 "- characterful, lived-in, not grotesque")              # the foes' caricature
ANIMAL_STYLE = """Style:
- pen and ink, Chris Riddell
- black line on white, no grey
- varied contour lines, sparse hatching in shadows only
- mostly untouched white paper
- a real animal, true to its anatomy, scruffy and characterful
- one whole animal alone, no people, short ground shadow
- white background, no frame, no text"""
ITEM_STYLE = """Style:
- pen and ink, Chris Riddell
- black line on white, no grey
- varied contour lines, sparse hatching in shadows only
- mostly untouched white paper
- well-used object, slightly exaggerated proportions
- one object alone, centred, large in the frame, clear simple outline
- white background, no frame, no text"""
SYMBOL_STYLE = """Style:
- a bold ink icon, hand-drawn with a thick brush pen
- black on white, no grey
- thick heavy outlines, large areas filled solid black
- few inner lines, drawn in white across the black
- one simple object alone, centred, filling the frame
- a clear silhouette that reads at 5 mm
- white background, no frame, no text, no shading"""
SYMBOL_AVOID = ("colour, grey, gradients, shading, hatching, cross-hatching, thin lines, sketchy lines, fine detail, "
                "photorealistic, 3D, bevel, frame, border, text, letters, signature, several objects")
REF_STYLE = "Copy only the ink style of the reference, not its subjects or labels."
CHARACTER_REF = ("Image 1 is a grey 3D model: redraw that figure, keeping its build, face, clothes, gear and pose. "
                 "From image 2 copy only the ink style.")
EDIT = "Edit the reference drawing. Make these changes: {change}. Keep everything else exactly as it is."
REF = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSJcSel0OCyTLDZmaKmoofuv9kZqkJggSAfbPhz7CLysw&s=10"


def key(var="EACHLABS_API_KEY", default=None):
    if os.environ.get(var):
        return os.environ[var]
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            name, _, value = line.partition("=")
            if name.strip() == var and value.strip():
                return value.strip().strip("'\"")
    return default or sys.exit(f"No {var}: put {var}=... in .env at the repo root.")


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


def ms_ref(ref):
    """Model Studio can't fetch REF's link, so it gets a copy of the sheet, downloaded once into the git-ignored build/."""
    if ref != REF:
        return ref
    copy = ROOT / "build" / "ref-sheet.jpg"
    if not copy.exists():
        copy.parent.mkdir(exist_ok=True)
        urllib.request.urlretrieve(REF, copy)
    return str(copy)


def generate_ms(model, prompt, refs, count, square=False, tries=10):
    """Model Studio answers in the same call (no prediction to poll); its image links expire after 24 hours."""
    refs = [ms_ref(r) for r in refs]
    body = {"model": MS_MODELS[model],
            "input": {"messages": [{"role": "user", "content": [{"image": ref_url(r)} for r in refs] + [{"text": prompt}]}]},
            "parameters": {"size": "2048*2048" if square else "1728*2368", "n": count,
                           "negative_prompt": SYMBOL_AVOID if square else AVOID, "prompt_extend": False, "watermark": False}}
    req = urllib.request.Request(key("MODELSTUDIO_URL", MS_API), method="POST", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key('DASHSCOPE_API_KEY')}", "Content-Type": "application/json"})
    print(f"Drawing with {MS_MODELS[model]} on Model Studio…", flush=True)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            out = json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 429 and tries > 1:
            print("Rate limited, retrying in 10 s…")
            time.sleep(10)
            return generate_ms(model, prompt, refs, count, square, tries - 1)
        raise RuntimeError(f"Model Studio: HTTP {e.code} {e.read().decode(errors='replace')}")
    except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
        raise RuntimeError(f"Model Studio: {e} (a call that timed out may still finish and bill)")
    if "output" not in out:
        raise RuntimeError(f"Model Studio {out.get('code')}: {out.get('message')}")
    print(f"Done (request {out.get('request_id')})")
    return [c["image"] for ch in out["output"]["choices"] for c in ch["message"]["content"] if "image" in c]


def generate(model, prompt, refs, count, square=False):
    if model in MS_MODELS:
        return generate_ms(model, prompt, refs, count, square)
    text, edit, build, *ref_key = MODELS[model]
    inp = build(prompt, count)
    if square:  # the symbols: square, and their own negative prompt
        for k, v in (("size", "2048*2048"), ("aspect_ratio", "1:1")):
            if k in inp:
                inp[k] = v
        if "negative_prompt" in inp:
            inp["negative_prompt"] = SYMBOL_AVOID
        else:
            inp["prompt"] = inp["prompt"].replace(f"Avoid: {AVOID}.", f"Avoid: {SYMBOL_AVOID}.")
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


def sources(folder=ART):
    f = SYMBOL_ART / "sources.json" if folder == SYMBOL_ART else SOURCES
    return json.loads(f.read_text()) if f.exists() else {}


def save_source(folder, path, url):
    f, base = (SYMBOL_ART / "sources.json", SYMBOL_ART) if folder == SYMBOL_ART else (SOURCES, ART)
    f.write_text(json.dumps(sources(folder) | {path.relative_to(base).as_posix(): url}, indent=1, sort_keys=True) + "\n")


def table(items):
    """(subjects, style, folder) for foes, or with items "items" or "cards" the card backs."""
    import art_prompts
    return {"items": (art_prompts.ITEMS, ITEM_STYLE, ITEM_ART),
            "cards": (art_prompts.CARDS, STYLE, CARD_ART),
            "characters": (art_prompts.CHARACTERS, CHARACTER_STYLE, CHARACTER_ART),
            "symbols": (art_prompts.SYMBOLS, SYMBOL_STYLE, SYMBOL_ART)}.get(items, (art_prompts.SUBJECTS, STYLE, ART))


def style_of(name, style):
    """ANIMAL_STYLE for the beasts in art_prompts.ANIMALS: the figure lines (caricature, big hands and feet) turned the hawk
    into a man-bird."""
    import art_prompts
    return ANIMAL_STYLE if name in art_prompts.ANIMALS else style


def prompt_for(subject, model, refs, edit=None, style=STYLE, character=False):
    if edit:  # edit = the changes, said outright: a subject that just leaves something out changes nothing
        prompt = f"{EDIT.format(change=edit)}\nDescription: {subject}."  # the drawing itself carries the style
    elif character:  # image 1 the mini's render, image 2 the style reference
        prompt = f"{subject}.\n{style}\n{CHARACTER_REF}"
    else:
        prompt = f"{subject}.\n{style}" + (f"\n{REF_STYLE}" if refs else "")
    if model in ("qwen", "qwen-ms") and len(prompt) > 800:
        raise ValueError(f"Prompt is {len(prompt)} characters; Qwen takes 800. Shorten the subject by {len(prompt) - 800}.")
    return prompt


def make(name, subject, model, refs, count=1, edit=None, items=False):
    """Draw one foe, or one gear card back with items; returns the saved files."""
    _, style, folder = table(items)
    style = style_of(name, style)
    slug = slug_of(name)
    targets = [folder / f"{slug}.png"] if count == 1 else [folder / f"{slug}-{i}.png" for i in range(1, count + 1)]
    folder.mkdir(parents=True, exist_ok=True)
    saved = []
    if items == "symbols" and not edit:  # keep the drawings being replaced
        for t in targets:
            if t.exists():
                keep = folder / "old" / f"{t.stem}-{datetime.datetime.now():%Y%m%d-%H%M%S}.png"
                keep.parent.mkdir(exist_ok=True)
                keep.write_bytes(t.read_bytes())
    square = items == "symbols"
    character = items == "characters" and not edit
    if character:
        refs = [str(render_of(name)), *refs]
    for url, t in zip(generate(model, prompt_for(subject, model, refs, edit, style, character), refs, count, square), targets):
        for attempt in range(3):
            try:
                urllib.request.urlretrieve(url, t)
                break
            except (urllib.error.URLError, ConnectionError, TimeoutError):
                if attempt == 2:
                    raise RuntimeError(f"Could not download {url}; fetch it by hand into {t}")
                time.sleep(5)
        Image.open(t).convert("L").save(t)  # the models slip in colour now and then; the cards are black and white
        if model not in MS_MODELS:  # Model Studio links expire after a day: not worth keeping
            save_source(folder, t, url)
        print("Saved", t.relative_to(ROOT), flush=True)
        saved.append(t)
    return saved


def render_of(name):
    """The grey render of a character's mini, the figure gen_art.py --characters redraws."""
    p = CHARACTER_ART / f"{slug_of(name)}-supplied.png"
    if not p.exists():
        raise RuntimeError(f"No {p.relative_to(ROOT)}: run tools/render_minis.py --only '{name}' first")
    return p


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
    for n, s in todo.items():  # check every length (and each character's render) before spending anything
        prompt_for(s, model, refs, style=style_of(n, style), character=items == "characters")
        if items == "characters":
            render_of(n)
    failed = []
    for i, (n, s) in enumerate(todo.items()):
        if i and model not in MS_MODELS:
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
    known = sources(folder)
    base = SYMBOL_ART if folder == SYMBOL_ART else ART
    for n in names:
        if n not in SUBJECTS or not (folder / f"{slug_of(n)}.png").exists():
            sys.exit(f"{n}: needs a subject in tools/art_prompts.py and a drawing in {folder.relative_to(ROOT)}/")
        prompt_for(SUBJECTS[n], model, ["x"], edit=change)  # check every length before spending anything
    for n in names:
        old = folder / f"{slug_of(n)}.png"
        # a local file goes inline: fine on Model Studio, Eachlabs may refuse it
        ref = (None if model in MS_MODELS else known.get(old.relative_to(base).as_posix())) or str(old)
        keep = base / "old" / f"{old.stem}-{datetime.datetime.now():%Y%m%d-%H%M%S}.png"
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
    ap.add_argument("--model", choices=[*MODELS, *MS_MODELS], default="qwen-ms", help="image model (default qwen-ms)")
    kind = ap.add_mutually_exclusive_group()
    kind.add_argument("--items", action="store_const", const="items", dest="kind",
                      help="gear and gold card backs (ITEMS, ITEM_STYLE, rules/art/items/) instead of foes")
    kind.add_argument("--symbols", action="store_const", const="symbols", dest="kind",
                      help="the card symbols (SYMBOLS, SYMBOL_STYLE, no style reference, rules/symbols/qwen/)")
    kind.add_argument("--cards", action="store_const", const="cards", dest="kind",
                      help="the other card backs: Callings, Runes, deck cards, Wounds (CARDS, rules/art/cards/)")
    kind.add_argument("--characters", action="store_const", const="characters", dest="kind",
                      help="the campaign's Bearers from their minis' renders (CHARACTERS, rules/art/characters/)")
    ap.add_argument("--force", action="store_true", help="overwrite an existing drawing")
    a = ap.parse_args()
    refs = [] if a.no_ref or (a.kind == "symbols" and not a.ref) else a.ref or [REF]
    if a.redo:
        if not a.change:
            ap.error("--redo needs --change: say what to change ('remove the bone; add the missing hind leg')")
        return redo(a.redo, a.model, a.change, a.ref, a.kind)
    if a.batch:
        return batch(a.only, a.model, refs, a.force, a.kind)
    subjects, _, folder = table(a.kind)
    subject = a.subject or subjects.get(a.name)  # a name alone draws its subject from tools/art_prompts.py
    if not (a.name and subject):
        ap.error("give a name and a subject (or a name from tools/art_prompts.py), or --batch")

    slug = slug_of(a.name)
    targets = [folder / f"{slug}.png"] if a.count == 1 else [folder / f"{slug}-{i}.png" for i in range(1, a.count + 1)]
    if not a.force and any(t.exists() for t in targets):
        sys.exit(f"{', '.join(str(t.relative_to(ROOT)) for t in targets if t.exists())} exists; pass --force to overwrite.")
    try:
        make(a.name, subject, a.model, refs, a.count, items=a.kind)
    except (RuntimeError, ValueError) as e:
        sys.exit(str(e))
    if a.count > 1:
        print(f"Rename the one you keep to {folder.relative_to(ROOT)}/{slug}.png for the card to use it.")

if __name__ == "__main__":
    main()
