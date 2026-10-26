# Foe art: image prompt rules

What we learned making foe drawings with `tools/gen_art.py` (Eachlabs API). The subjects live in `tools/art_prompts.py`;
the style, reference and avoid list live in `tools/gen_art.py`.

## The look

Chris Riddell (Edge Chronicles) pen and ink: pure black line on white paper, sparse hatching in the shadows only,
lots of untouched white, grotesque caricature (big hands and feet, warts, lumpy bodies), a short hatched shadow
on the ground. Grimy and lived-in, never clean or heroic.

## Model

- **Qwen Image 3.0 Pro** (`--model qwen`, $0.075 per image) is the one we use. It has the most character and the cleanest ink.
- Cheaper models we tried on the same goblin:
  - Seedream v5 Lite ($0.035): lively and close, but weapons came out wrong.
  - Qwen 2.1 Pro ($0.04): clean, but the figure was small in the frame, with a white sticker outline.
  - Qwen 2.1 Turbo ($0.016): tamer, with thin lines and a small figure; good enough for trying out poses.
  - Flux 3 ($0.048): grey fills, a comic-book look and a cream background.
  - Luma Uni-1: its content filter refused the prompt (no charge).
- Nano Banana 2 (the first default) gave a realistic, grey, densely rendered look: too far from Riddell.

## The prompt

Every prompt is built as: **subject**, then **style list**, then **reference line**.

- **Style as a short bullet list.** With a reference image carrying the style, short works as well as long and leaves room for the subject.
- **Qwen's limit is 800 characters in total.** The style and reference lines take about 360, which leaves **about 436 for the subject**.
  The script checks every prompt's length before spending anything.
- **The avoid list** (`AVOID`) goes in Qwen's separate negative prompt, which Qwen respects better than "no X" in the main prompt.
  It lists colour, grey wash, gradients, photorealism, dense texture, heavy shading, frames, text,
  malformed weapons, broken objects and extra limbs.
- **Turn off Qwen's automatic prompt rewriting** (`prompt_extend: false`) so the style text arrives word for word.

## The reference image

- **A reference image moves the style more than any wording.** Without one, "Chris Riddell" alone still came out grey and realistic.
- **Use a sheet of many small figures, not one creature.** A single-creature reference (a furry troll) got its *subject* copied:
  we asked for a goblin and got the troll's mane, pose and hand-on-head.
  The multi-figure sketch sheet (`REF` in `gen_art.py`) gives the style without a subject to copy.
- **Say "copy only the ink style of the reference, not its subjects or labels"**, or the sheet's name banners
  and extra creatures creep in.
- **References must be web links.** Eachlabs has no upload feature; a local file is sent inline, which may be refused.

## Writing a subject

- **Be specific, in this order:** body type → face(s) → grime and skin → clothes and gear → exact pose → what each hand holds.
- **Vary the cast on purpose:** skinny and fat, ugly and beautiful, masked and bare-faced, round and angular faces.
  The style already pushes everything towards grotesque, so ask for contrast explicitly.
- **Grime by name:** grime crusts, boils, warts, matted hair, drool, flies, filthy or shredded cloth. Each one shows up.
- **For a held object, give its geometry, not just the action.** Say which end is in the hand, where the other end is,
  and ask for "the whole X in clear view".
  - "Grips a club whose end drags behind" gave a club gripped partway along, with a mystery stub above the fist.
  - "Holding the club by its thin end, the thick end resting on the ground beside its foot, the whole club in clear view"
    gave a club that makes sense.
- **Simple, readable outlines.** Weapons hanging down, resting on a shoulder or held out to the side read better
  than ones angled behind the body. Hidden parts are where the model invents nonsense.
- **Details come through reliably; expressions and camera angles less so.** Two heads, drool, flies and javelins always appeared.
  "Sneering at the left head" and "three-quarter view" took a second try.
  If one matters, say it more strongly or describe it physically ("turned sideways", "seen from the side").
- **Contrasting features need their own clause each:** "the left head fat and jowly…; the right head small, bald and angular…".
- **No colour words in the description.** "Yellow fangs", "yellow buck teeth" and "gold tooth" came out tinted
  yellow or gold, and the rat got a pink nose, despite "colour" being on the avoid list.
  Use "stained", "metal" or "dull" instead. Even neutral words can leak a little: "twine" and "sweat stains" gave faint
  brown touches on the bandit.
- **Masks are a great source of variety.** "A cracked mask carved from an animal skull, tied on with twine" and
  "a stitched burlap sack mask with ragged eye holes" both read instantly.
- **To show an item without anyone holding it, say where it is and what it's doing:**
  "sand trickling from a torn hip pocket onto the ground" works, and "left hand empty, fingers spread" stops the hand
  from inventing something to hold.
- **Avoid "a few small solid black fills".** It caused a stray black rectangle on clothing twice.
  The wording now is "solid black only in the deepest shadows".

## Symbols (stat icons)

A first round of 13 proposals is in `rules/symbols/qwen/`, with contact sheets.
It was made from square 2048 × 2048 images, the same reference and an icon version of the style list.
- **The foe style fights legibility at icon size.** The reference and "sparse hatching, mostly untouched white" give
  thin, mostly white drawings, and "bold clear silhouette that reads at 5 mm" was ignored.
  At about 5 mm they look pale beside the solid black brush symbols. For icons, drop "mostly untouched white paper",
  ask for "thick heavy outlines, filled solid black shapes", or use a bold reference.
  Thickening the lines afterwards (cropping to the ink, a min filter, a threshold) helps but doesn't fully fix it.
- **Shields push the emblem out.** "A shield with an emblem" gives a detailed bevelled shield with a small emblem that
  vanishes at card size. Ask for a plain flat shield with a large emblem filling it, or combine the two in code.
- **Small extras fade or vanish,** such as speed lines or a centre disc. A detail that matters needs its own clause,
  described physically: "a solid black dot in the centre".
- **Saying which way things face works every time:** knuckles forward, boot toe right, swords pointing up.
- **Square results sometimes have a faint line at the edges.** Trim a few pixels off each side.

## Output

- Portrait 3:4 at 1728 × 2368. The card's picture panel (50 × 67 mm) crops the top and bottom slightly; keep the figure whole with a margin.
- Saved as `rules/art/<foe-name>.png`, which `tools/build_cards.py` picks up automatically.
  `--force` is needed to replace an existing drawing.
  Bandit, Bandit Archer and Ogre began as supplied drawings; test against them under another name (`"Ogre Test"`).
- **Every drawing is saved in greyscale** (Pillow, in `.venv`), because the models slip in faint colour now and then.
- `rules/art/sources.json` records each drawing's Eachlabs web link, which a redo uses as its reference.
- Results vary from run to run. When hands or weapons matter, `--count 2` or `--count 3` and pick the best.

## Redoing a drawing

When a drawing needs changes, **edit it instead of starting over**: the pose, face and composition you liked survive.

1. Update the foe's subject in `tools/art_prompts.py`, so the description stays true for later.
2. Run `.venv/bin/python tools/gen_art.py --redo "Giant Rat" --change "remove the bone; ..."`. This:
   - sends the **current drawing as the reference**, by its web link from `sources.json`, instead of the sketch sheet;
   - sends the prompt "Edit the reference drawing. Make these changes: … Keep everything else exactly as it is.",
     then the description, but **not the style list**: the drawing carries the style;
   - keeps the replaced drawing in `rules/art/old/`.

What we learned:
- **The change must be said outright.** A description that just leaves something out changes nothing:
  the rat came back with its bone and pose identical. "Remove the bone lying on the ground" worked.
- **Edits keep the pose almost exactly.** That's good for small fixes, but it can't easily add a limb the pose hides:
  "give the rat its missing hind leg" left the far hind leg behind the body in a three-quarter view.
  For a change of pose or angle, generate afresh instead of editing.
- **What edits do well:** surfaces and objects.
  - Rusty armour became polished.
  - A small axe head became a big crescent blade.
  - A skull pattern was removed from the spider's abdomen, and a small skull added to its web.
- **What they don't:** pose, grip and limb count.
  - The orc kept its one-handed short-handled axe.
  - The spider kept its extra legs.
- **"Both hands overhead" doesn't come through.** Qwen drew the orc's greataxe one-handed three times, even with
  "one hand near the butt and one halfway up". Choose a pose where two hands are natural instead,
  such as the weapon held across the body at chest height.
- **Fresh drawings can fix limb counts;** edits can't. The side-view spider prompt with "exactly eight legs, four on each
  side and no more" came out close to eight, but the raised legs got hand-like claws.
- **A second reference image (`--ref`) works for a feature,** but the model may copy it too literally.
  "Flatten the head like image 2" gave the hobgoblin the flat skull and side ears, but also a second pair of
  frog eyes on top, taken from the reference, while keeping its own. Say what to replace, not only what to copy.

## Gear drawings

Gear cards get their drawing on the **card back**. Subjects are `ITEMS` in `tools/art_prompts.py`, drawn with `--items`:
`ITEM_STYLE` replaces the figure lines of the style ("one object alone, centred, large in the frame, clear simple outline")
and drawings are saved in `rules/art/items/`.

- **Whole and in clear view.** Nothing buried, stuck in the ground, piled, coiled or in a heap, and nothing in front of the object.
  Blades float upright point down or lie flat; hafted weapons stand on their butt.
- **A second object lies apart**, flat on the ground beside the first (a scabbard, an arrow, coins spaced apart).

## Running it

- **Key:** `EACHLABS_API_KEY` in the git-ignored `.env`.
- **Python:** run with `.venv/bin/python`, which has Pillow.
- **One foe:** `.venv/bin/python tools/gen_art.py "Name" "subject"`.
- **All foes:** `.venv/bin/python tools/gen_art.py --batch` (skips drawn foes; `--only Orc` repeats per foe).
- **Redo:** `.venv/bin/python tools/gen_art.py --redo Bandit` (see above).
- **Concurrency:** while the account balance is $10 or less, Eachlabs runs at most **2 jobs at once** (HTTP 429).
  A slot stays busy for a while after a job finishes, so a batch of two-at-a-time jobs got refused over and over.
  The batch runs **one job at a time with a 60 s pause after each**, and the script retries on 429 for up to 5 minutes.
  Topping up the balance above $10 lifts the limit.
- **One-off `status: error` "input rejected as invalid":** the same prompt worked on the rerun. Retry once before rewording.
- **Errors:** a refused job comes back with status `error` (missing from the docs), and its message is in `output`.
  The script stops on it and gives up on any job after 5 minutes.
- **Dropped connections:** they happen; the script retries status checks and downloads.
  A job that dropped may still finish and bill.
