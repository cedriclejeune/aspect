"""What to draw for each foe card (cards/foes.py) and each gear card's back (cards/base_set.py), sent by tools/gen_art.py --batch
(--items for gear).

Each subject is added before the house style (gen_art.STYLE, or ITEM_STYLE for gear); Qwen takes 800 characters in all, so keep them short.
"""

SUBJECTS = {
    "Bandit": "a fat, squat bandit wearing a cracked mask carved from an animal skull, tied on with twine, a grinning "
              "mouth of real teeth; greasy neck stubble, sweat stains, patched leather jerkin straining over the "
              "belly, flies. Front view, legs wide, leaning forward; right hand raises a notched handaxe by its short "
              "handle, blade up, fully visible; left hand empty, fingers spread; sand trickling from a torn hip pocket "
              "onto the ground",
    "Bandit Archer": "a tall, rake-thin bandit archer with a beautiful but hard angular face, high cheekbones, shaved "
                     "head with one long braid, a scar across the lips; dirty patched leather, muddy boots, grime "
                     "under the nails. Side view, left foot forward, drawing a longbow: left arm straight holding the "
                     "bow at its middle, right hand pulling the string to the cheek, arrow nocked and fully visible; "
                     "dagger in the boot",
    "Goblin": "small, wiry, bald goblin, big pointed ears, sharp grin, patched leather, crouched, whirling a leather sling, "
              "notched dagger",
    "Wolf": "a gaunt, mangy wolf, ribs and hip bones showing, patchy matted fur with burrs and scabby bald patches, a "
            "torn ear, one milky blind eye, foam at the lips. Side view, head held low below the shoulders, hackles "
            "up, lips peeled back over long stained fangs, front legs braced, hind legs coiled to lunge, tail stiff",
    "Cultist": "a tall, gaunt cultist with an eerily beautiful, serene face, shaved head tattooed with small eyes, "
               "lips half sewn shut with thread; filthy hooded robe with an eye sigil stitched on the chest, bare "
               "dirty feet, candle wax dripped on the shoulders. Front view, standing very straight, arms held out "
               "wide; right hand holds a wavy dagger by its hilt, point down, blade fully visible; left hand dangles a "
               "string of knuckle-bone prayer beads",
    "Legionary": "a short, barrel-chested soldier, square jaw, broken nose, clean-shaven, neat and disciplined; "
                 "polished, undented segmented iron armour, clean crested helmet, tidy straps, hobnailed sandals. "
                 "Three-quarter view, crouched behind a tall curved rectangular shield held by its centre grip in the "
                 "left hand; right hand thrusts a short sword forward over the shield rim, blade fully visible; a "
                 "heavy javelin leans against the shield",
    "Bandit Captain": "a vain, wiry bandit captain, long angular face, waxed moustache, one metal tooth, pockmarked cheeks; "
                      "feathered tricorn hat, stained velvet coat over leather, rings on every finger, a fat coin "
                      "purse at the belt. Three-quarter view, fencing stance: right arm extended pointing a thin "
                      "rapier forward, left hand raised behind holding a dagger point up, both blades fully visible",
    "Ogre": "a hulking two-headed ogre: the left head fat and jowly, tusked underbite, a string of drool; the right head "
            "small, bald and angular, sneering at the left. Pot belly crusted with grime, filthy hide loincloth with flies. "
            "Three-quarter view, knees bent; its right arm hangs down holding a knotted tree-trunk club by its thin end, "
            "the thick end resting on the ground beside its foot, the whole club in clear view; javelins tied on its back",
    "Ogre Chieftain": "a towering, muscular ogre warlord, small flat head, jutting tusks, scarred bald scalp, a ring "
                      "through the nose; mismatched plate armour strapped on with rope, a crude crown of antlers and "
                      "bent iron, skulls hanging from the belt, grime in every crease. Front view, chest out, mouth "
                      "wide open bellowing; right hand rests a huge spiked club on its shoulder, holding it by the "
                      "thin end; left fist raised high",
    "Guard": "a pear-shaped, middle-aged town guard, sleepy and bored, droopy moustache, bulbous nose with broken "
             "veins, double chin; rusty mail shirt too short over a stained tunic, dented kettle helmet tipped back. "
             "Front view, slouching with weight on one hip; left hand holds a round shield by its strap, resting on "
             "the ground; right hand leans on two javelins held upright like a walking stick; longsword sheathed at "
             "the hip",
    "Scout": "a slender elf scout with a beautiful, sharp, angular face, high cheekbones, long pointed ears, hair in a "
             "tight braid, a thin scar through one eyebrow; mud-spattered hooded cloak of leaves and rags. Side view, "
             "kneeling on one knee on a rock; left hand holds a longbow upright by its grip; right hand draws an arrow "
             "from a quiver at the hip; shortsword sheathed on the back",
    "Mage": "a tiny, ancient, hunched wizard, huge bald dome head, enormous ears, wild eyebrows, a beard so long it "
            "drags on the ground, crooked spectacles; patched robe with burn holes and soot. Three-quarter view, "
            "standing on tiptoe; left hand holds a fat spellbook open by its spine; right hand raised, fingers spread, "
            "small flames curling from the fingertips; a dagger tucked in the belt",
    "Orc": "a hulking, top-heavy orc on short legs, heavy underbite with two tusks, flat pig nose, war paint scrawled "
           "across the face, topknot; leather harness, a bear pelt over one shoulder. Front view, mid-swing towards "
           "the viewer, roaring, body twisted; both fists together at the end of a long handle, swinging a huge "
           "greataxe in a wide arc, the blade seen edge-on as a thin sharp line coming at us, a curved motion line; "
           "javelins on its back",
    "Hobgoblin": "a lean, upright hobgoblin officer; a low, wide, flat-topped skull like a frog's, only two cold "
                 "narrow eyes set in the face, big ears sticking straight out sideways, waxed moustache and goatee; "
                 "polished mail with a sash, clean boots, ruthlessly tidy. Front view, at attention; left hand holds a "
                 "tall kite shield resting on the ground; right hand holds a longsword upright before its face in "
                 "salute; longbow slung on its back",
    "Skeleton": "a lanky skeleton with an oversized grinning skull, cracked cranium, missing teeth, a loose jaw, "
                "cobwebs between the ribs, a mouse peeking out of the ribcage; scraps of rotten leather armour and a "
                "tattered belt. Three-quarter view, lurching forward mid-stride; right hand holds a rusty notched "
                "shortsword by the hilt, pointing ahead; a shortbow slung over one shoulder",
    "Zombie": "a bloated, swollen zombie, belly split open along ragged stitches, sagging mottled skin, one eye "
              "missing, slack jaw hanging loose, wisps of hair; tattered burial shroud, bare blackened feet, worms and "
              "a cloud of flies. Front view, shambling forward, head lolling to one side, both arms stretched straight "
              "ahead, fingers curled, one foot dragging behind",
    "Kobold": "a scrawny little kobold, lizard snout, small curled horns, a crest of spines, scaly skin, long thin "
              "tail, huge nervous eyes; a tin pot for a helmet, a sack tunic, a necklace of stolen spoons. "
              "Three-quarter view, tiptoeing forward, hunched low; right hand holds an oversized dagger by its hilt, "
              "point forward; left hand holds a sling by its cords, a stone in the pouch",
    "Giant Rat": "a giant rat as big as a dog, fat and greasy, naked scaly tail longer than its body, long stained "
                 "buck teeth, twitching whiskers, beady eyes, fur missing in patches, sores, filth caked on its belly. "
                 "Side view, profile facing left, standing on all four legs, all four paws planted on the ground and "
                 "visible, back arched, head low and sniffing forward, long claws",
    "Giant Spider": "a giant hairy spider with exactly eight long jointed legs, four on each side and no more, a "
                    "bloated round plain hairy abdomen, a cluster of eight glistening eyes, hooked fangs dripping "
                    "venom. Side view, profile facing left, the first pair of legs raised high in threat, the other "
                    "three pairs planted on the ground; behind it a torn web with a small skull caught in it",
    "Troll": "a very tall, lanky, emaciated troll with arms that reach the ground, long hooked nose, tiny eyes, lank "
             "stringy hair, rubbery warty skin, moss and fungus growing on its back; a fresh sword wound on its chest "
             "knitting closed with threads of flesh. Side view, stooped, knuckles dragging, long claws, head thrust "
             "forward, mouth open on jagged teeth",
}

# Gear: one object alone on the card back, whole and in clear view. Nothing buried, stuck in the ground, piled, coiled,
# wrapped around it or in front of it; any second object lies apart from it.
ITEMS = {
    # Armor and Shield
    "Leather": "a battered leather jerkin standing upright as if worn by no one, scuffed and cracked at the elbows, a "
               "patched hole over the heart, mismatched buckles down the front, one broken strap hanging at the side. "
               "Front view, the whole jerkin in clear view",
    "Mail": "a mail shirt standing upright as if worn by no one, sleeves hanging straight down, rings rusted and a few "
            "burst open, a torn padded collar, a ragged hem. Front view, the whole shirt in clear view",
    "Plate": "a full suit of dented plate armour standing empty, helmet visor raised, one pauldron hanging by a single "
             "rivet, scratches and hammered-out dents, arms at its sides. Front view, standing straight, legs apart, "
             "the whole suit in clear view",
    "Shield": "a round wooden shield standing on its edge, iron rim bent in one place, planks split, an arrowhead "
              "stuck in it, a crude painted eye half scraped off, a frayed strap. Front view, flat face to the viewer, "
              "the whole shield in clear view",
    # Weapons
    "Dagger": "a plain dagger floating upright, point down, blade nicked along the edge, cord-wrapped grip worn "
              "shiny, crossguard slightly bent, a round pommel. Front view, the whole dagger in clear view",
    "Shortsword": "a short broad-bladed sword lying flat on the ground, blade chipped near the tip, leather grip "
                  "unravelling, a dented round pommel. Side view, horizontal, the whole sword in clear view",
    "Handaxe": "a handaxe standing upright on the end of its short handle, bearded blade at the top, blade nicked, "
               "stained wooden handle cracked and bound with wire. Side view, the whole axe in clear view",
    "Finesse Blade": "a thin elegant sword floating upright, point down, a swept basket hilt of curling metal wire, a "
                     "tassel hanging from the pommel, blade long and needle-thin. Front view, the whole sword in "
                     "clear view",
    "Longsword": "a long straight sword floating upright, point down, long cross-shaped hilt, leather grip wound with "
                 "wire, one notch in the blade, a battered scabbard lying flat on the ground beside it. Front view, "
                 "the whole sword and scabbard in clear view",
    "Battleaxe": "a heavy battleaxe standing on the end of its long handle, head at the top, one broad crescent blade, "
                 "chipped, a spike on the back, handle wrapped in strips of hide. Side view, upright, the whole axe in "
                 "clear view",
    "Greatsword": "a huge two-handed sword floating upright, point down, long grip wrapped in rough leather, wide "
                  "crossguard with drooping ends, blade with a notched edge. Front view, the whole sword in clear view",
    "Glaive": "a glaive standing upright, a long wooden pole with a broad single-edged curved blade on top, a hook on "
              "the back of the blade, a ragged cloth strip tied below the head, iron butt cap. Side view, the whole "
              "glaive in clear view",
    "Longbow": "a tall strung longbow standing upright, bow stave of knotted yew, string straight and taut, grip "
               "wrapped in leather, one fletched arrow lying flat on the ground beside it. Front view, the whole bow "
               "and arrow in clear view",
    "Sling": "a leather sling hanging straight down from a finger loop at the top, two long braided cords, a worn "
             "cupped pouch at the bottom, one round stone lying on the ground beside it. Front view, the whole sling "
             "in clear view",
    "Javelins": "three javelins standing upright side by side, spaced apart, leaf-shaped iron heads at the top, "
                "wooden shafts scuffed, one shaft cracked and bound, butts resting on the ground. Front view, all "
                "three javelins in clear view",
    "Spellguard Staff": "a tall gnarled wooden staff standing upright on its own, the top split into three twisted "
                        "branches cradling a cloudy crystal, carved runes spiralling down the shaft. Front view, the "
                        "whole staff and crystal in clear view",
    "Greatclub": "a huge knotted tree-trunk club standing upright on its thick end, the thick end studded with old "
                 "nails, the thin end at the top wrapped with filthy rag as a grip, bark peeling. Side view, the whole "
                 "club in clear view",
    "Gladius": "a short wide stabbing sword floating upright, point down, straight blade with a long tapering point, "
               "rounded wooden guard and ball pommel, grip with finger ridges. Front view, the whole sword in clear "
               "view",
    "Boarspear": "a boar spear standing upright, a broad leaf-shaped iron head at the top with a short crossbar just "
                 "below it, a tuft of coarse bristle caught on the crossbar, thick ash shaft. Side view, the whole "
                 "spear in clear view",
    "Pilum": "a heavy throwing spear standing upright, a long thin iron shank topped by a small pyramid point, the "
             "shank slightly bent from use, fixed to a short wooden shaft with a round lead weight. Side view, the "
             "whole pilum in clear view",
    "Shortbow": "a short curved bow standing upright, recurved tips of horn, the string taut, grip wrapped in leather, "
                "one arrow lying flat on the ground beside it. Front view, the whole bow and arrow in clear view",
    "Greataxe": "a huge double-bladed greataxe standing on the end of its long handle, head at the top, both crescent "
                "blades chipped, a skull-shaped rivet in the middle, handle bound with leather. Front view, the whole "
                "axe in clear view",
    # Instrument, Jewelry, Spellbook
    "Traveler's Lute": "a battered round-bellied lute standing upright, neck at the top, cracked soundboard patched "
                       "with a nailed board, one string snapped and hanging loose, mismatched pegs. Front view, the "
                       "whole lute in clear view",
    "Ring of Warding": "a thick ring standing upright on its edge, a small shield engraved on its face, worn smooth, "
                       "one tiny crack across the band. Close up, front view, the whole ring in clear view",
    "Guild Signet": "a heavy signet ring standing upright on its edge, a set of scales carved on its flat face, "
                    "scratches on the band; a round wax seal with the same scales lying flat beside it. Close up, the "
                    "whole ring and seal in clear view",
    "Shard Bandolier": "a leather bandolier laid out flat in a wide open U, five stitched pockets spaced along it, a "
                       "jagged crystal shard standing out of each, buckle tarnished, stitching coming loose. Seen from "
                       "the front, the whole bandolier in clear view",
    "Holy Amulet": "a round amulet hanging from a leather cord, the cord in a clean V above it, a sunburst carved on "
                   "its face, a small chip missing from the rim. Front view, the whole amulet and cord in clear view",
    "Boots of the Long Stride": "a pair of tall worn leather riding boots standing side by side, spaced apart, small "
                                "wings carved into the heel spurs, soles patched, mud on the toes. Side view, both "
                                "boots in clear view",
    "Ring of Sparks": "a ring of twisted metal wire standing upright on its edge, a jagged lightning bolt set on its "
                      "face, tiny zigzag sparks jumping off it into the air. Close up, front view, the whole ring in "
                      "clear view",
    "Dancer's Bells": "five small round bells hanging from a frayed ribbon strung in a gentle arc, spaced apart, the "
                      "bells dented and mismatched, one tilted to show its clapper. Front view, the whole ribbon and "
                      "every bell in clear view",
    "Conjurer's Book": "a thick spellbook standing upright, closed, cracked leather cover with an eye carved on it, "
                       "metal corner caps, a strap and buckle holding it shut. Front view, cover to the viewer, the "
                       "whole book in clear view",
    # Items
    "Potion of Healing": "a small round-bellied glass potion bottle standing upright, a wax-sealed cork, a heart "
                         "scratched on the glass, liquid inside, a drip running down the side. Front view, the whole "
                         "bottle in clear view",
    "Coin Pouch": "a plump leather coin pouch standing upright, tied shut with a drawstring at the top, patched seams, "
                  "three coins lying flat on the ground beside it, spaced apart. Front view, the whole pouch in clear "
                  "view",
    "Writ of Favor": "a parchment letter hanging open, unrolled flat, a heavy wax seal hanging from its bottom edge on "
                     "a ribbon, rows of cramped handwriting squiggles, one corner torn. Front view, the whole letter "
                     "in clear view",
    "Greater Potion of Healing": "a tall square-sided glass potion bottle standing upright, a long neck, a carved glass "
                                 "stopper wired shut, a heart etched on the glass, bubbles rising in the liquid. Front "
                                 "view, the whole bottle in clear view",
    "Pocket Sand": "a small open cloth pouch standing upright, patched and stained, its mouth open at the top, a puff "
                   "of sand grains blowing out of it into the air. Front view, the whole pouch in clear view",
    "Alchemist's Fire Recipe": "three small clay flasks standing upright side by side, spaced apart, a rag wick in each "
                               "neck, one wick lit with a small curl of flame and smoke. Front view, all three flasks "
                               "in clear view",
}
