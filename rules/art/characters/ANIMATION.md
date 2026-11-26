# Animation references: prompts

The prompts behind the colour reference sheets, storyboards and test videos for the campaign's Bearers (November 2026).
The images sit next to this file; the videos are kept out of git.

**Style references.** "Images 2 and 3" in the prompts below are two stills supplied by the user as the target look,
kept in `style-refs/`: `close-ups.png` (a pair of flat cel-shaded character close-ups) and `forest.png` (a forest
landscape with two hikers): flat colour, clean dark outlines, one hard shadow tone, muted natural palette.
`poster.png` is a third still in the same look. `style-board.png` puts the poster and the forest side by side, so the
three fit in one image slot (Model Studio takes at most 3 images per request). `face-selleck.png` is the face
inspiration for Far Reacher's redesign.

**Image model.** Qwen Image 3.0 on Alibaba Model Studio (`DASHSCOPE_API_KEY`), `prompt_extend: false`, colour kept
(not through `tools/gen_art.py`, which saves greyscale). At most 3 images per request. Lessons learned are in
[../PROMPTING.md](../PROMPTING.md).

## Reference sheets

### Hilda: `hilda-turnaround-flat.png`

Images: 1 the front view cropped from an earlier sheet (Hilda in colour), 2 and 3 the style references. Size 2688×1536.

> Character turnaround sheet for 2D animation. Character design from image 1 only; redraw her entirely in the flat cel-shaded style of images 2 and 3: clean thin even dark outlines, flat colour fills, one hard-edged shadow tone, no texture, no hatching. Plain white background, four full-body views in a row, same height, feet on one line, neutral pose, hands empty, mouth closed, gentle smile. VIEW 1 FRONT: round freckled face, both ginger braids hanging over her chest, red knitted beanie, green tunic with laced collar and zigzag bands, brown belt with buckle, brown pouch on her right hip, small Nordic axe head-down on her left hip, rocks of the pack showing above her head, frying pan hanging from the pack beside her right arm, bare hairy feet. VIEW 2 LEFT PROFILE, facing left: the big brown pack sticks out far behind her back, grey rocks heaped on top; the axe on her hip; one braid. VIEW 3 BACK: the pack covers her whole back, rocks on top, frying pan on the pack's right side, axe handle at her left hip, beanie from behind, heels. VIEW 4 RIGHT PROFILE, facing right: the pack sticks out far behind her, frying pan on its side; the pouch on her hip; one braid. No text.

Negative prompt: `open mouth, teeth, rope, double-headed axe, pencil, watercolour, paper texture, storybook, fox, animal, text, labels, watermark, photorealistic, 3D render, pencil texture, hatching, sketchy lines, gradients, extra limbs, background scenery`

### Far Reacher: `far-reacher-turnaround.png`

Images: 1 `far-reacher.png` (his ink portrait, for the design), 2 and 3 the style references. Size 2688×1536.
The colours (grey wolf, blue-grey tunic, brown leather) are a choice: the portrait is black and white.

> Character turnaround sheet for 2D animation. Character design from image 1 only; redraw him entirely in the flat cel-shaded style of images 2 and 3: clean even dark outlines, flat colour, one hard shadow tone. Plain white background, four full-body views in a row, same height, feet on one line, standing upright, neutral, mouth closed. A lean bearded warrior, stern, dark brown beard and moustache, wearing a whole grey wolf pelt: the wolf head as a hood over his brow, the pelt as a long cloak to his calves. Dull blue-grey tunic, wide brown belt, tan trousers with leg wraps, brown boots. VIEW 1 FRONT: wolf face above his face, sword in his right hand pointing down beside his right leg, round wooden shield with iron rim, studs and central boss on his left forearm, three small skulls hanging at his right hip. VIEW 2 LEFT PROFILE, facing left: wolf snout pointing left, the shield seen from the side on his left arm, cloak hanging behind. VIEW 3 BACK: the grey pelt covers his whole back, wolf ears on top, the pelt's tail hanging down, shield rim at his left side, sword tip at his right side. VIEW 4 RIGHT PROFILE, facing right: sword in his right hand pointing down, skulls at his hip, cloak behind. Only one man. No text.

Negative prompt: `open mouth, teeth, rope, double-headed axe, pencil, watercolour, paper texture, storybook, fox, animal, text, labels, watermark, photorealistic, 3D render, pencil texture, hatching, sketchy lines, gradients, extra limbs, background scenery`

Then one targeted edit (image 1 the sheet alone) to remove a second blade in the back view:

> Edit the character turnaround sheet in image 1. Make only this change: in the third view (the back view), remove the extra sword blade that pokes out from under the wolf-pelt cloak on the left side of that figure, near his left boot; fill that spot with the pelt's ragged hem and the white background. He holds only one sword, in his right hand, on the right side of the back view. Keep everything else exactly as it is: same four views, same style, colours, poses and framing.

## Storyboards and start frames

### Hilda and the cairn: `hilda-cairn/1.png`–`5.png`

Images: 1 `hilda-turnaround-flat.png`, 2 the forest still, 3 the close-ups. Size 2688×1536. Each frame is the shared
opening, then `SHOT n: `, the shot, and ` No text, no panel border.`

Shared opening:

> Storyboard frame for a 2D animated short, wide shot, side view. Image 1 is a character sheet of Hilda: draw her once, same design (short stocky halfling, freckles, ginger braids, red knitted beanie, green zigzag tunic, belt, pouch on right hip, small Nordic axe on left hip, bare hairy feet, big brown pack heaped with grey rocks, frying pan on the pack). Style and colours of images 2 and 3: flat 2D animation, clean outlines, flat colour, one hard shadow tone. Setting: a windswept grassy northern hilltop, pale sky, a stone cairn of stacked flat stones a head taller than her. 

1. She stands before the cairn, smiling, holding up a smooth flat stone in both hands, looking up at the top of the cairn.
2. She rises on the tips of her toes, heels off the ground, arms stretched high, setting the flat stone on the top of the cairn; the heavy pack leans on her back.
3. She loses her balance: tilting backwards on one foot, arms flailing, eyes wide, mouth open in surprise; the heavy pack pulls her back, the cairn wobbles, its top stones tipping toward her.
4. Everything falls on her: the cairn collapses onto her and the rocks spill out of her pack over her head, stones in mid-air all around her, she is falling backwards, arms over her head.
5. Aftermath: she sits on the ground buried to the waist under a heap of stones, beanie askew, dazed, a single flat stone balanced on top of her head, the frying pan beside her.

Negative prompt: `character sheet, several Hildas, duplicate character, fox, text, labels, panel border, photorealistic, 3D render, hatching, extra limbs`

Frames 2 and 5 came out with two Hildas.

The vector animatic (`hilda-cairn/animatic.py`, 1920×1080, 24 fps, 8 s) is drawn in code, no prompt.

### Far Reacher in the forest: `far-reacher-forest/start.png`

Images: 1 `far-reacher-turnaround.png`, 2 the forest still, 3 the close-ups. Size 2688×1536.

> Opening frame of a 2D animated short, wide shot. Image 1 is a character sheet of Far Reacher: draw him once, same design (lean bearded warrior in a whole grey wolf pelt, wolf head as a hood, long pelt cloak, blue-grey tunic, brown belt, small skulls at his right hip, round wooden shield with iron rim on his left arm, sword in his right hand pointing down, leg wraps, brown boots). Style of images 2 and 3: flat 2D animation, clean dark outlines, flat colours, one hard shadow tone. Night in a dark, dense forest of tall twisted trunks, roots and ferns, cold blue-green moonlight in thin shafts, faint mist on the ground, deep black shadows between the trees. He stands small in the middle of the frame, three-quarter view, lost and uneasy, looking over his shoulder, breath steaming. No eyes or creatures yet. No text, no panel border.

Negative prompt: `character sheet, several men, duplicate character, glowing eyes, daylight, fox, text, labels, panel border, photorealistic, 3D render, hatching, extra limbs`

## Videos

### Hilda 1: Wan 3.0, reference sheet (`hilda-cairn/hilda-cairn.mp4`)

`wan3.0-video-prime` on Model Studio (`video-generation/video-synthesis`, async), 480P, 16:9, 5 s.
Input `media`: `reference_image` = `hilda-turnaround-flat.png` (as JPEG).

> 2D flat cel-shaded animation, clean outlines, flat colours, in the style of the reference character sheet. Hilda, the short stocky halfling woman of the reference sheet (red knitted beanie, ginger braids, green tunic with zigzag hem, big brown pack heaped with grey rocks, frying pan on the pack, small axe on her left hip, bare hairy feet), stands on a windswept grassy hilltop beside a stone cairn of stacked flat stones as tall as she is. Side view, static camera. She rises on the tips of her toes and sets a flat stone on top of the cairn, smiles, then wobbles, arms flailing, loses her balance and falls backwards; the cairn collapses onto her and the rocks spill out of her pack. She ends sitting on the ground buried to the waist in stones, dazed, the flat stone landing on her head. Comedic timing. Only one Hilda.

Result: the design held, but the cairn fell behind her and she turned to the camera mid-wobble.

### Hilda 2: Wan 3.0, reference sheet + animatic (file no longer kept)

Same, plus `reference_video` = the animatic retimed to 5 s at 480p. Prompt: the one above, followed by:

> Follow the motion, timing and staging of the reference video exactly, but draw it in the style of the reference sheet.

Result: the motion followed the animatic exactly, but so did the look (blocky shapes).

### Hilda 3: Seedance 2.5, start frame (`hilda-cairn/hilda-cairn-seedance.mp4`)

Runway API (`seedance2_5`, `image_to_video`, key `seedance` in `.env`), 1280:720, 5 s, 150 credits ($1.50).
`promptImage` = storyboard frame 1 (`hilda-cairn/1.png`, 1280×720 JPEG).

> 2D flat cel-shaded animation, static camera, side view. The halfling woman rises on the tips of her toes, stretches up and sets the flat stone on top of the cairn, smiles proudly. Then she wobbles on tiptoe, arms flailing, the heavy pack of rocks pulls her backwards, the top of the cairn sways with her. She falls backwards: the cairn collapses onto her and the rocks spill out of her pack over her head. She ends sitting on the ground buried to the waist in stones, dazed, and the flat stone lands last on top of her head. Comedic timing. Keep her design and the drawing style exactly as in the image.

Result: the best of the three: the whole action, the style and the design held. She ends buried to the neck.

### Far Reacher: Seedance 2.5, start frame (`far-reacher-forest/far-reacher-forest.mp4`)

Runway API, `seedance2_5`, 854:480, 5 s, 100 credits ($1.00). `promptImage` = `far-reacher-forest/start.png`.

> 2D flat cel-shaded animation, clean dark outlines, flat colours, one hard shadow tone. Night, a dark, dense forest of tall twisted trunks, roots and ferns, cold blue-green moonlight in thin shafts, faint mist on the ground. Far Reacher, the lean bearded warrior wearing a whole grey wolf pelt (the wolf head as a hood, the pelt as a long cloak), round wooden shield on his left arm, sword in his right hand, walks slowly forward, lost. He stops, turns his head left and right, uneasy, breath steaming, gripping his sword tighter. Around him in the darkness, pairs of glowing eyes open one after another between the trees and in the undergrowth, yellow and pale green, more and more of them, all watching him. He freezes and raises his shield a little. Slow push-in of the camera toward him. Tense, quiet, eerie mood. Only one man, no creatures visible except their eyes.

Result: eyes open and multiply around him, push-in, shield raised. All eyes came out yellow.
