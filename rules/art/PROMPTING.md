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
- **Backup:** `qwen-ms` (Model Studio, the default) falls back to `qwen` on Eachlabs when Model Studio fails or is out of budget,
  if `EACHLABS_API_KEY` is set. It is the same Qwen Image 3.0 model, and it gets the same prompt, reference and avoid list, so every rule here still applies.
  A local reference such as a mini's render goes inline, and Eachlabs may refuse it. `--no-backup` stops instead.
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
- **References:** Model Studio takes local files inline. On Eachlabs they must be web links (no upload; inline may be refused).

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
- **Be specific about the character, simple about the pose.** Give the pose one clear action and a familiar stance,
  and keep the limbs in view. Poses like "at attention", "slouching", "kneeling" and "standing firm, feet apart" came out
  clean every time. Crowded poses broke: "crouched behind a shield, sword thrust over the rim, javelin leaning on it"
  lost a leg behind the shield and gave an odd grip. The same legionary as "standing firm on both legs, shield on its
  left arm, short sword in its right hand" came out right first time.
- **A stick held in both hands in front of the body replaced a leg.** The Shattered Knee orc lost its right leg behind
  the walking stick. "Standing on both legs, both legs and both feet in clear view", the stick in one hand
  "planted beside the right foot, outside the legs" fixed it in a fresh drawing.
- **"Wild-eyed" and shouting faces can come out with blank white eyes,** which read as undead. An edit
  ("small dark pupils looking forward, fierce and alive") fixed it.
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
- **An undescribed face comes out handsome.** "Grizzled" and "a crooked smirk" still gave a pretty-boy mercenary.
  Name two or three physical irregularities: face shape (weak chin, lantern jaw, long narrow face), features (bulbous nose,
  jug ears, eyes too close), wear (pockmarks, missing teeth, a scar pulling the lip), asymmetry (one ear torn off).
  For young characters, show youth through awkwardness (acne scars, a big Adam's apple, a cowlick), not "young".
  `AVOID` also lists "handsome, pretty, idealised face, model looks, smooth skin".
- **Figures of speech are drawn literally.** "A sharp fox face" gave a fox's head, "beak-nosed", "a beak of a nose" and even "a hooked nose" (the Archery archer) a
  bird's beak, "scooped by a fingertip" a finger with no hand, "a long horse face" a horse's head, "a black eye" an eye drawn solid black and "squinting along an arrow" an arrow pointing into the eye. Describe the shape instead: "a long thin pointed nose".
- **Say which end of a stuck arrow shows.** "Arrows stuck in it" gave arrows pointing out of the shield, fletching in the wood,
  and on the Templar arrows on the inner face she sees. Write "points buried in the wood, fletched ends sticking out",
  and for a held shield "its outer face toward us, the arm hidden behind it".
- **A plain "mace" can come out as a lumpy rag head that reads as a torch.** Give the head: "a solid metal ball ringed with sharp flanges".
- **Drop decorative eyes.** "A crude painted eye" on the shield came out as a realistic eyeball in a socket.
- **Raised fingers read as gestures.** Two splinted fingers held up came out as a rude gesture; show an injured hand
  held flat, palm out.
- **Mostly white, even in the dark.** "Standing in darkness drawn as dense hatching" and "a long black coat" gave large
  solid black areas that break the style; give darkness as a few strokes at the edges.
- **Masks are a great source of variety.** "A cracked mask carved from an animal skull, tied on with twine" and
  "a stitched burlap sack mask with ragged eye holes" both read instantly.
- **To show an item without anyone holding it, say where it is and what it's doing:**
  "sand trickling from a torn hip pocket onto the ground" works, and "left hand empty, fingers spread" stops the hand
  from inventing something to hold.
- **"A black robe" comes out as one solid black shape** (*Hold Person*). Write "a plain pale robe drawn in outline".
- **Avoid "a few small solid black fills".** It caused a stray black rectangle on clothing twice.
  The wording now is "solid black only in the deepest shadows".

## Characters (the players' Bearers)

The campaign's Bearers are drawn from their 3D-printed minis (Eldritch Foundry STL exports in `Campagnes/<campaign>/Models/`),
so the Bearer card portrait matches the mini on the table.

- **Render first:** `tools/render_minis.py` turns each mini's `*_char_mm.stl` (the figure without its base) into a grey-clay
  picture, `rules/art/characters/<name>-supplied.png` (front) and `<name>-three-quarter.png`. Flat clay with a dark outline
  where surfaces overlap reads best as a figure to copy. If a mini's "front" shows its side, set `TURN` in the script.
- **Two references, two jobs:** image 1 is the render (copy the figure: build, face, clothes, gear, pose), image 2 the sketch
  sheet (copy only the ink). `CHARACTER_REF` says so outright, like `REF_STYLE` does for one reference.
- **Not grotesque:** `CHARACTER_STYLE` is `STYLE` without "grotesque caricature, oversized hands and feet". The players'
  Bearers keep the ink and the grime, not the foes' caricature.
- **Say what the render shows:** the render has no colour or texture, so the subject names what matters (Far Reacher wears a
  whole wolf pelt as a hood; he is not wolf-headed) and adds the grime the clay can't show.
- **Model Studio** (`--model qwen-ms`) takes the local render inline. Eachlabs needs web links and may refuse it.
- **Print:** `tools/build_cards.py --bearers C1` puts each drawing in its Bearer card's portrait box (the grey render until the
  drawing exists), trimmed to the figure.

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

A second round (`gen_art.py --symbols`, SYMBOL_STYLE: "bold ink icon, thick brush pen, thick heavy outlines, large areas
filled solid black", no reference image, square) gave bold symbols that read at card size. Knack is still from the first round.
- **Dropping the sketch-sheet reference is what made them bold.** With it, every icon came back as a thin pen drawing.
- **Bold drawings need little thickening.** tools/ink_symbols.py's full min filter closed their white highlights and veins; they use grow 5.

## Output

- Portrait 3:4 at 1728 × 2368. The card's picture panel (50 × 67 mm) crops the top and bottom slightly; keep the figure whole with a margin.
- Saved as `rules/art/<foe-name>.png`, which `tools/build_cards.py` picks up automatically.
  `--force` is needed to replace an existing drawing.
  Bandit, Bandit Archer and Ogre began as supplied drawings; test against them under another name (`"Ogre Test"`).
- **Every drawing is saved in greyscale** (Pillow, in `.venv`), because the models slip in faint colour now and then.
- `rules/art/sources.json` records each Eachlabs drawing's web link, which an Eachlabs redo uses as its reference.
  Model Studio links expire after 24 hours, so a Model Studio redo sends the drawing file itself.
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
- **Reshaping an object: remove it, then add the new one.** Three edits asking to turn the Patriot's long stocking
  cap into a short folded tuque left it almost unchanged. "Remove the hat entirely", then a second edit
  "put a short knitted wool tuque on his head…", worked. Several edits in a row fade the lines: darken afterwards
  (a gamma curve in Pillow).
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

- **Key:** `EACHLABS_API_KEY` in the git-ignored `.env`. `--model qwen-ms` uses Qwen Image 3.0 on Alibaba Model Studio
  instead (`DASHSCOPE_API_KEY`, and `MODELSTUDIO_URL` for another workspace than `MS_API`), but in October 2026 the account
  got "AccessDenied.Unpurchased" for both `qwen-image-3.0` and `-pro` until the model was activated in the console.
  `qwen-image-3.0` then drew the ogre test as well as Eachlabs' 3.0 Pro (club grip right). Model Studio can't fetch
  `REF`'s Google link ("url error"), so the script downloads the sheet once into `build/` and sends it inline.
  `qwen-mt-image-2.0` is not a generator: it translates the text in an existing image.
- **Python:** run with `.venv/bin/python`, which has Pillow.
- **One foe:** `.venv/bin/python tools/gen_art.py "Name" "subject"`.
- **All foes:** `.venv/bin/python tools/gen_art.py --batch` (skips drawn foes; `--only Orc` repeats per foe).
- **Redo:** `.venv/bin/python tools/gen_art.py --redo Bandit` (see above).
- **Animals:** names in `ANIMALS` (`tools/art_prompts.py`) get `ANIMAL_STYLE`, without the figure lines
  ("grotesque caricature, oversized hands and feet", "one full-body figure"): with them the hawk came out as a man
  growing out of a bird.
- **Other card backs:** `--cards --batch` draws `CARDS` (Callings, Runes, deck cards, Wounds: one figure acting the card
  out, the foe `STYLE`) into `rules/art/cards/`; gold is in `ITEMS`, drawn with `--items`.
- **Concurrency (Eachlabs):** while the account balance is $10 or less, Eachlabs runs at most **2 jobs at once** (HTTP 429).
  A slot stays busy for a while after a job finishes, so a batch of two-at-a-time jobs got refused over and over.
  The batch runs **one job at a time with a 60 s pause after each**, and the script retries on 429 for up to 5 minutes.
  Topping up the balance above $10 lifts the limit.
- **One-off `status: error` "input rejected as invalid":** the same prompt worked on the rerun. Retry once before rewording.
- **Errors:** a refused job comes back with status `error` (missing from the docs), and its message is in `output`.
  The script stops on it and gives up on any job after 5 minutes.
- **Model Studio for whole batches (2026-11-12):** when Eachlabs ran out of credit (HTTP 402, nothing billed), the 60 starter
  expansion drawings were made with `--model qwen-ms` (Qwen Image 3.0), no pause between jobs, about 40 s each. One read
  timed out and was simply rerun. Redos work there too (`--cards --redo X --change ... --model qwen-ms`).
- **Dropped connections:** they happen; the script retries status checks and downloads.
  A job that dropped may still finish and bill.
