"""What to draw for each foe card (cards/foes.py) and each card back in the base set (cards/base_set.py), sent by
tools/gen_art.py --batch: SUBJECTS for foes, ITEMS (--items) for gear and gold, CARDS (--cards) for Callings, Aspects, deck
cards and Wounds. *Orcish Blood*, *Hobgoblin Discipline* and the Wolf Form use the foe's drawing (build_cards.FOE_DRAWING).

Each subject is added before the house style (gen_art.STYLE, or ITEM_STYLE for ITEMS); Qwen takes 800 characters in all, so keep them short.
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
                 "polished segmented iron armour, clean crested helmet, tidy straps, hobnailed sandals. Three-quarter "
                 "view, standing firm on both legs, feet apart; a tall curved Roman scutum on its left arm, from "
                 "shoulder to shin, with a round central boss; a short sword in its right hand; a heavy javelin slung "
                 "on its back",
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
             "tight braid, a thin scar through one eyebrow; a neat, well-made hooded cloak with clean hems over a "
             "fitted leather tunic, soft boots. Three-quarter view, standing alert on both legs; left hand holds a "
             "longbow upright at its side, one straight taut string from tip to tip; quiver at the hip; shortsword "
             "sheathed on the back",
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
                 "polished mail with a sash, clean boots, ruthlessly tidy. Front view, standing at attention on both "
                 "legs; left hand rests on a tall kite shield standing on the ground; right hand holds a longsword "
                 "point down; longbow slung across its back",
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
    "Giant Spider": "a giant hairy spider with exactly eight long jointed legs, four on its left and four on its right, "
                    "every leg whole and clearly separate, none hidden; each ends in a single sharp hooked tip. "
                    "A bloated round plain hairy abdomen, a cluster of eight glistening eyes, hooked fangs dripping venom. "
                    "Seen from above at a slant, the legs spread wide around the body like the spokes of a wheel; "
                    "behind it a torn web with a small skull caught in it",
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
               "Only the jerkin, nothing below its hem: no trousers, no boots. Front view, the whole jerkin in clear view",
    "Mail": "a heavy mail shirt of interlocking iron rings, each ring a small open circle drawn in fine line on white, standing upright as if "
            "worn by no one, short sleeves, a plain round neck, rings rusted and a few burst open, a straight even hem with no tatters. "
            "Front view, the whole shirt in clear view",
    "Plate": "a full suit of dented plate armour standing empty, helmet visor raised, one pauldron hanging by a single "
             "rivet, scratches and hammered-out dents, arms at its sides. Front view, standing straight, legs apart, "
             "the whole suit in clear view",
    "Shield": "a round wooden shield standing on its edge, iron rim bent in one place, planks split, two arrows "
              "stuck in it, points buried in the wood, fletched ends sticking out, a frayed strap. Front view, flat face to the viewer, "
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
                 "wire, one notch in the blade. Front view, the whole sword in clear view",
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
    "Spellguard Staff": "a tall gnarled wooden staff floating upright, a slim shaft ending in a plain metal-capped butt, the top split into three twisted "
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
    "Pilum": "a heavy throwing spear standing upright and perfectly straight, a long thin straight iron shank topped "
             "by a small pyramid point, the shank joined to a thick wooden shaft by a square wooden block bound with "
             "iron collars. Side view, the whole pilum in clear view",
    "Shortbow": "a short curved bow standing upright, recurved tips of horn, the string taut, grip wrapped in leather, "
                "one arrow lying flat on the ground beside it. Front view, the whole bow and arrow in clear view",
    "Fine Bow": "an elegant composite recurve bow standing upright, laminated layers of horn and wood, deeply "
                "recurved tips, the string tied to both tips and pulled taut, a fine carved grip wrapped in silk cord. Front view, the whole bow "
                "in clear view",
    "Wand": "a very thin, pencil-slim wand of black wood floating upright, tapering to a fine point at the top, a "
            "tiny copper ring at the base, a few small sparks crackling at the point. Front view, the whole wand in "
            "clear view, small in the middle of the empty white page",
    "Greataxe": "a huge double-bladed greataxe standing on the end of its long handle, head at the top, both crescent "
                "blades chipped, a skull-shaped rivet in the middle, handle bound with leather. Front view, the whole "
                "axe in clear view",
    # Instrument, Jewelry, Spellbook
    "Traveler's Lute": "a well-travelled round-bellied lute standing upright, neck at the top, worn and scuffed wood, "
                       "one small neat patch on the soundboard, all strings intact, mismatched pegs. Front view, the "
                       "whole lute in clear view, nothing behind it",
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
    "Restorative Salve": "a small round flat tin of ointment lying open, its lid propped against it on edge, the thick "
                         "salve inside scooped by a fingertip, a sprig of bitter herbs tied on the lid with string. "
                         "Three-quarter view from above, the whole tin and lid in clear view",
    # Gold
    "1 gp": "one worn metal coin standing upright on its edge, a crude crowned head stamped on its face, the rim nicked "
            "and bent. Close up, front view, the whole coin in clear view",
    "10 gp": "a short stack of five worn metal coins, and three more lying flat on the ground beside it, spaced apart, "
             "crude stamped faces, nicked rims. Front view, every coin in clear view",
    "50 gp": "a small cloth money bag standing upright, tied shut with string, a patch sewn on its side, four coins "
             "lying flat on the ground beside it, spaced apart. Front view, the whole bag in clear view",
    "100 gp": "a fat leather purse standing upright, bulging, drawstring knotted twice, the seams straining, a coin "
              "peeking out of a split seam, two coins lying flat beside it, spaced apart. Front view, the whole purse "
              "in clear view",
    "500 gp": "a small iron-banded wooden strongbox standing open, its lid raised on its hinges, coins heaped level with "
              "the rim, a heavy padlock hanging open from the hasp. Three-quarter view, the whole box in clear view",
    "1,000 gp": "three heavy metal ingots lying side by side, spaced apart, each stamped with a crown, chipped edges, "
                "a fat purse standing beside them. Three-quarter view, every ingot in clear view",
}

ANIMALS = {"Hawk", "Bear"}  # drawn with gen_art.ANIMAL_STYLE: a real animal, not a caricature figure

CARDS = {  # Callings, Aspects, deck covers, deck cards and Wounds: one figure acting the card out, drawn with --cards
    # Callings: who the Bearer is, acting out the perk
    "Duelist": "a wiry elf woman duelist with a sharp narrow face, long pointed ears, a high ponytail and a thin "
               "scar on the chin, a padded doublet with slashed sleeves, tall scuffed boots. Side view, in a deep "
               "lunge on the front foot, a straight sword thrust forward in the right hand, the whole blade in clear "
               "view, left arm raised behind for balance",
    "Templar": "a short, very broad dwarf woman templar with a square jaw, a broken nose and two thick braids, a "
               "plain surcoat with a sun sigil over mail. Front view, standing with feet planted, a big round shield "
               "raised on the left arm, its outer face toward us, the arm hidden behind it, three arrows "
               "stuck in that face, right hand pressed flat on the chest as if "
               "swearing an oath",
    "Spellblade": "a tall, gaunt hobgoblin man spellblade with a flat nose, a jutting jaw and a shaved head tattooed "
                  "with runes, a long coat over a breastplate. Three-quarter view, a longsword held up in the right "
                  "hand, the whole blade in clear view with small sparks crackling along it, left hand holding an open "
                  "book against the hip",
    "Infiltrator": "a skinny, long-limbed young wood elf woman, wild tangled hair, a fitted leather jerkin, a long "
              "hooded cloak of overlapping leaves, laced leggings, soft wrapped leather boots, a slim knife belt. Side view, tip-toeing, arms out for balance, hands empty",
    "Sage": "a stooped, pot-bellied old scholar with a bald head, huge round spectacles and ink-stained fingers, a "
               "long scruffy robe, a quill tucked behind the ear. Front view, standing, carrying a tall stack of "
               "books against the chest with both arms, the whole stack in clear view",
    "Performer": "a lanky, grinning halfling man street performer with a huge nose, curly hair, a feathered cap, a "
                 "patchwork jerkin and big hairy bare feet. Front view, balanced on one foot on a small barrel, arms "
                 "flung wide, a juggling ball in each hand and a third in the air above the head",
    "Brawler": "a squat, bull-necked orc woman brawler with small tusks, cauliflower ears, a flattened nose and a "
               "shaved head, a torn sleeveless shirt, rag-wrapped fists. Three-quarter view, crouched low, both arms "
               "wide, hands open and reaching forward as if to grab",
    "Patriot": "a young, lean, charismatic peasant orator, bright fierce eyes, a big open-mouthed shout, a short "
               "snug knitted wool tuque, its top folded over, a hooded wool coat, a woven sash with a zigzag arrow pattern "
               "tied at the waist, fringed ends hanging. Front view from below, standing atop a street barricade of "
               "barrels and planks, sword raised high in the right hand, left arm flung out, leaflets flying from it",
    "Tactician": "a stout, grey-haired halfling woman tactician with round spectacles, a tight bun and a buttoned "
                 "officer's coat, big hairy bare feet. Three-quarter view, standing on a crate, a rolled map tucked "
                 "under the left arm, right arm stretched out pointing forward with a short baton",
    "Ranger": "a weathered, lanky hobgoblin woman ranger with a long face, a jutting jaw and a cropped mohawk, a "
              "hooded leaf-patched cloak, a quiver on the back. Front view, kneeling on one knee, drawing a "
              "longbow, the whole bow and arrow in clear view",
    "Trickster": "a thin, sly elf man trickster with a pointed chin, long pointed ears, a crooked grin and slicked "
                 "hair, a jester-like patched coat. Side view, leaning far back out of the way, a thrown dagger flying "
                 "past the nose, both hands raised in mock surprise",
    "Hermit": "a gaunt old dwarf man hermit with a huge tangled white beard down to the knees, wild eyebrows, bare "
              "feet and a robe of sewn furs and leaves. Front view, standing, leaning on a gnarled staff in the "
              "right hand, a small owl on the left shoulder",
    # species Traits
    "Human Grit": "a stubborn middle-aged farmer with a weathered square face, a crooked nose and thinning hair, sleeves "
             "rolled up, a patched apron, muddy boots. Front view, standing, a pitchfork held upright in the right "
             "hand, its prongs up, its butt on the ground, left hand on the hip",
    "Elven Blood": "a slender, very tall elf with an ageless beautiful narrow face, long pointed ears, long straight hair, "
           "large calm eyes, a simple long cloak with leaves stitched at the hem. Side view, standing very still, "
           "left hand shading the eyes, gazing into the distance, right hand empty",
    "Dwarven Blood": "a short, very broad dwarf, a huge braided beard down to the belt, a bulbous nose, bushy eyebrows, a "
             "leather apron over mail, thick boots. Front view, standing with feet planted, a tankard held in the "
             "right hand, left hand gripping the belt",
    "Halfling Luck": "a small, round-cheeked, cheerful halfling with curly hair, a button nose and big hairy bare feet, a "
                "waistcoat with one button missing. Three-quarter view, standing, flipping a coin up with the right "
                "thumb, the coin in the air, left hand in a pocket",
    # Aspects
    "Springheel": "a gangly, knobbly-kneed youth with springy hair and a gap-toothed grin, a ragged tunic, oversized "
                  "boots. Side view, in mid-leap high above the ground, legs tucked, arms flung up, a short shadow on "
                  "the ground far below",
    "Stone Blood": "a fat, bald royal taster with a triple chin and a smug face, a fancy collar stained with spills, "
                   "a skull-and-crossbones tag on a cup. Front view, standing, drinking from a goblet tipped up to "
                   "the lips with the right hand, left hand on the belly",
    "Iron Will": "a small, scrawny old woman with a stern wrinkled face, a hooked nose, hair in a tight bun, a plain "
                 "shawl. Front view, standing very straight, arms folded, glaring ahead, a huge shadowy hand with "
                 "long claws reaching towards her from the side and stopping short",
    "Clear Mind": "a calm, thin monk with a shaved head, a long serene face and closed eyes, a simple rough robe. "
                  "Front view, standing with hands clasped, swirling wisps of mist and broken mirror shards "
                  "drifting around and passing harmlessly to either side",
    "Cleave": "a burly soldier with a scarred face and a shaved head, a dented breastplate, a torn cloak. Three-quarter "
              "view, mid-swing, a broad sword sweeping level across the body in both hands, the whole sword in clear "
              "view, a dropped helmet rolling on the ground",
    "Steady Aim": "a lean, weathered hunter with a long drooping moustache and one eye squinting shut, a fur "
                  "hood, a quiver at the hip. Side view. Aiming a crossbow at unseen target.",
    "Shield Bash": "a stocky, snub-nosed veteran with a bristly beard and a battered helmet, patched mail. Side view, "
                   "lunging forward, a round shield on the left arm thrust out rim first, the right hand clenched "
                   "back by the hip, the whole shield in clear view",
    "Battle Hymn": "a barrel-chested warrior with a wild beard and a horned helmet, mouth wide open singing, veins "
                   "on the neck. Three-quarter view, standing, a short sword raised high in the right hand, left fist "
                   "beating the chest, music notes drawn in the air",
    "Rallying Cry": "a gaunt, hollow-cheeked standard-bearer with a bandaged head, a torn tabard. Front view, "
                    "standing on both legs, shouting, a tall pole with a tattered trefoiled banner held upright"
                    " in the right hand, the pole's butt on the ground, left arm thrown forward",
    "Shield Wall": "two soldiers standing shoulder to shoulder, one tall and thin, one short and fat, both with "
                   "squashed helmets. Front view, both standing firm, feet apart, their two tall rectangular shields "
                   "held side by side, rims overlapping, eyes peeking over the top",
    "Cat Burglar": "a skinny, hunched burglar with a long pointed nose, a striped shirt, a burglars mask over "
                   "the eyes, a sack over the shoulder. Side view, tiptoeing on the toes of both feet, a "
                   "lockpick held up in the right hand, left hand raised with one finger to the lips. Two hands"
                   " only.",
    "Renowned": "a pompous, beaming hero with a big chin and a perfect wavy hairdo, a medal-covered sash, a cape. "
                "Front view, standing, chest puffed out, both hands on the hips, a scatter of tossed flowers lying "
                "on the ground at the feet",
    "Sailor": "a squat, bow-legged old halfling woman sailor with a pipe, a leathery wrinkled face, a grey "
              "braid under a knit cap, a striped shirt, tattooed forearms, big hairy bare feet. Front view, "
              "standing, a coil of rope over the left shoulder, right hand holding the pipe, an anchor tattoo"
              " on the arm",
    "Street Urchin": "a tiny, grubby street urchin with a gap-toothed grin, huge eyes, a cap too big and a coat "
                     "with ragged sleeves, bare feet. Three-quarter view, tiptoeing away, a fat stolen purse held "
                     "behind the back in the right hand, left hand waving innocently",
    "Hunter": "a rangy woodsman with a hooked nose and a scruffy beard, a fur hat, a hide coat, a hunting knife at the "
              "belt. Side view, crouched low on both feet, one hand touching a large paw print on the ground, the "
              "other holding a longbow upright, the whole bow in clear view",
    "Physician": "a plump, kindly physician with a round bald head, small spectacles and a big moustache, a long "
                 "apron with many pockets. Front view, standing, rolling a bandage between both hands, a leather "
                 "satchel open on the ground beside the feet",
    "Barkeep": "a hulking goliath woman barkeep, a grey-skinned giant-kin with a bald head marked with dark "
               "stony patches, a heavy jaw, big hoop earrings, a broad bosom and huge forearms, a stained "
               "apron, a rag over the shoulder. Front view, standing, polishing a tankard with a rag in both "
               "hands, one eyebrow raised, squinting suspiciously",
    "Smith": "a stocky dwarf woman smith with thick braided hair tied back, singed sideburns, a sooty face, a"
             " burn scar on the cheek and bulging arms, a heavy leather apron, thick gloves. Three-quarter "
             "view, standing and forging on an anvil, hammer raised",
    "Mountaineer": "a wiry, weathered elf woman mountaineer with long pointed ears, a sunburnt, wind-chapped "
                   "face, a beaked nose, crow's feet and frost in her eyebrows, a fur-lined hood, a rope "
                   "coiled across the chest, spiked boots. Side view, climbing a big solid cliff face of rock"
                   " drawn as a wall at one side of the picture, both hands gripping one pick driven into the"
                   " rock, both spiked boots dug into the rock below, body pressed close to the cliff",
    "Twin Strike": "a lithe, sharp-featured duellist with a thin moustache, a hooked nose, hollow cheeks and a "
                   "long ponytail, a slashed doublet. Front view, standing, feet apart, arms held out low to "
                   "the sides, a slim sword in each hand pointing down at the ground, both blades fully visible",
    "Second Wind": "a battered, muscular, bruised woman fighter with a square heavy jaw, a flattened boxer's nose, a "
                   "swollen black eye and a split lip, a chipped front tooth, sweaty hair plastered to the brow, a torn shirt, "
                   "one boot missing. Three-quarter view, getting up off one knee, one hand pushing on the knee, the other "
                   "wiping the mouth, a determined grin",
    "Wiry": "an extremely thin, ropy labourer with stringy muscles, a long neck and a beak of a nose, a sleeveless "
            "vest, rolled trousers. Front view, standing, carrying a heavy sack on one shoulder with one hand, "
            "unbothered, left hand empty",
    "Night Eyes": "a pale, hunched cave-dweller with enormous round staring eyes, a pinched little face and huge "
                  "ears, a ragged hooded cloak. Front view, standing in darkness drawn as dense hatching around the "
                  "edges, the figure itself left clear, peering ahead",
    "Sellsword": "a grizzled, broken-nosed woman mercenary of fifty with a lantern jaw, a pockmarked weathered face, "
                 "cropped hair and one ear torn off to a stump, a crooked smirk showing missing teeth; mismatched scavenged "
                 "armour, a coin purse at the belt. Front view, standing, a longsword resting on the right shoulder, left "
                 "hand held out, palm up, waiting to be paid",
    "Acrobat": "a lanky acrobat with a long jaw and a waxed moustache, a striped leotard, soft slippers. Front view, "
               "doing a handstand on both hands, legs straight up in the air, the whole body in clear view",
    "Pack Hunter": "a wiry human woman hunter with shaggy matted hair, a long bony face, filed pointed teeth and a scar "
                   "across the nose, a fur cloak with a wolf's head hood. Side view, crouched low on both feet, ready to "
                   "pounce, human hands with five fingers spread and curled; beside her, a separate real wolf on four legs "
                   "crouched in the same pose",
    "Slippery": "a slick, androgynous rogue with a long sinuous body, a greasy smile, a thin pencil moustache "
                "and slicked-back hair, a tight coat, dodging arrows like Neo in the Matrix: side view, bending"
                " far backwards from the knees, two arms flung out to the sides, two legs with both feet "
                "planted flat on the ground, three arrows streaking past just above the body",
    "Hedge Witch": "a hunched, warty old hedge witch with a long chin, wild hair stuck with twigs, a patched shawl, a "
                   "crow on the shoulder. Front view, standing, stirring a small cauldron on the ground with a long "
                   "spoon held in both hands, herbs hanging from the belt",
    "Sweeping Blow": "a giant, slab-shouldered half-ogre with a tiny head and a tusked underbite, a fur loincloth. "
                     "Front view, mid-swing, a long two-handed maul held level in both hands, sweeping round, three "
                     "small helmets flying off to the side",
    "Relentless": "a bruised, bloodied brawler with a battered pear-shaped face, a cauliflower ear, a nose "
                  "broken flat and bent to one side, one eye swollen shut, a missing front tooth, a shaved head"
                  " with a fresh stitched cut; a torn shirt, bandaged fists. Front view, standing unsteadily, "
                  "one arm hanging, the other fist raised, a grim lopsided grin",
    # Deck covers
    "Wanderer's Repertoire": "a skinny, long-haired wandering bard with a big nose and a feathered hat, a patched "
                             "coat, a pack on the back. Three-quarter view, walking, a lute held across the chest, "
                             "strumming with the right hand, the whole lute in clear view",
    "Acolyte's Litany": "a young, round-faced acolyte with a bowl haircut and a plain hooded robe, a rope belt."
                        " Front view, standing, eyes closed in prayer, holding a small open prayer book in both"
                        " hands, a few beads hanging from the fingers, with two hands",
    "Wildheart's Remembrance": "a lean, wild-haired druid with leaves and feathers tangled in the hair, a gaunt "
                               "beautiful face, a cloak of patched furs, bare feet. Front view, standing, a knobbly "
                               "wooden staff in the right hand, a hawk perched on the left forearm",
    # Conjurer's Book
    "Fire Bolt": "a round stout female apprentice conjurer with singed eyebrows, a smoking frizzy fringe and a "
                 "too-big pointed hat on its head. Side view, standing, right arm thrust out, a bolt of fire "
                 "flying from the palm drawn as curling ink flames, left hand clutching the hat",
    "Mage Hand": "a short, plump conjurer with a bald head and a neat beard, a long robe. Front view, standing,"
                 " one hand raised and wiggling the fingers, a large ghostly outlined hand floating beside it "
                 "holding a key by its ring, the other hand is by its side.",
    "Magic Missile": "a tall old woman wizard with a long thin pointed nose, wrinkled sunken cheeks, a long "
                     "forked beard and a starry robe. Three-quarter view, standing, pointing forward with the "
                     "right hand, three small glowing darts drawn as bright outlined arrows flying out in a fan",
    "Shield": "a startled, skinny conjurer with wide eyes and hair standing on end, a patched robe. Front view, "
              "standing, both hands thrown up, a flat round disc of force drawn as a clean outline in front of the "
              "hands, a dagger bouncing off it",
    "Grease": "a pompous fat guard with a big moustache and a helmet, a breastplate. Side view, slipping on a puddle "
              "of grease, both feet in the air, arms flailing, the helmet flying off",
    "Misty Step": "a lanky, hooded conjurer with a hooked nose. Side view, stepping out of a swirl of mist drawn in "
                  "light curling lines, one foot still inside the mist, the other planted on the ground ahead",
    "Web": "a small, angry goblin tangled in a thick sticky web, the strands drawn as clean lines stretched in every "
           "direction, arms stuck out, one foot lifted, a dagger caught in the web beside it",
    # Wanderer's Repertoire
    "Jeer": "a scrawny jester with a long pointed nose and a floppy cap with bells. Side view, standing, thumbs in "
            "both ears, fingers waggling, tongue stuck out",
    "Rally": "a round-bellied drummer with puffed cheeks and a bushy moustache, a soldier's coat. Front view, "
             "marching, a drum hung at the waist, beating it with a stick in each hand",
    "Hold the Line": "a stout, square-jawed sergeant with a big moustache and a battered helmet, beating a slow "
                     "rhythm. Front view, standing firm, feet apart, a tall rectangular shield planted on the ground "
                     "in front, banging it with a short sword held in the right hand",
    "Cutting Words": "a sharp-faced, sneering poet with a thin moustache, a ruff collar and a feathered cap. "
                     "Three-quarter view, standing, one hand on the hip, the other pointing a long quill like a "
                     "dagger, mouth open mid-insult",
    "Steady Now": "a calm, jolly, plump old orc minstrel like a Santa Claus, with two big lower tusks, "
                  "pointed ears out of the hood, a broad flat nose, a kind wrinkled face, a long curly white "
                  "beard, a patched fur-trimmed hooded cloak. Front view, standing, one hand resting on an "
                  "unseen shoulder at his side, the other holding a small flute down at his side",
    "Dread": "a gaunt, hollow-eyed mourner with a long sad face and a tall black hat, a long black coat. Front view, "
             "standing, playing a slow tune on a fiddle held under the chin, the whole fiddle and bow in clear view",
    "Rousing Verse": "a cheerful, chubby bard with round cheeks, curly hair and a feathered beret. "
                     "Front view, standing on a small wooden crate, one arm flung up, singing, a scroll of verse "
                     "unrolling from the other hand",
    # Acolyte's Litany
    "Guidance": "a stooped, kindly old priest with a long white beard and a hooded robe. Three-quarter view, "
                "standing, eyes closed in prayer, his left hand resting on the shoulder of a kneeling, armoured, grizzled "
                "adult warrior, his right hand holding a lit candle up high. The warrior kneels with head bowed and "
                "both hands clasped on the hilt of a sword planted point-down",
    "Bless": "a broad, smiling priestess with a round face and a wimple, a simple robe with a sun stitched on it. "
             "Front view, standing, both arms raised wide, palms up, rays drawn as simple lines above the hands",
    "Bane": "a thin, scowling inquisitor with a pointed chin and narrow eyes, a tall hood and a long robe. Front view, "
            "standing, pointing at the ground with a long bony finger, a small storm cloud drawn above the "
            "pointing hand",
    "Twist Fate": "a sly old fortune teller with a hooked nose, hoop earrings and a headscarf, many rings. Front "
                  "view, standing, tossing two large dice from the right hand, the dice tumbling in the air, the "
                  "left hand holding a single thread",
    "Healing Word": "a young, earnest monk with a bowl haircut and big ears, a plain robe. Front view, standing, "
                    "cupping both hands round the mouth, calling out, a small simple sun shape drawn in the air in "
                    "front of the mouth",
    "Cure Wounds": "a gentle, heavy-set healer with a broad face and a shaved head, rolled sleeves. Three-quarter "
                   "view, kneeling on one knee, both hands laid on the bandaged arm of a wounded soldier sitting "
                   "beside it",
    # Wildheart's Remembrance
    "Hawk": "a lean, fierce hawk with a hooked beak, staring eye. Side view, in flight, wings spread wide",
    "Mossbalm": "a gaunt druid with leaves in the hair, a patched fur cloak. Three-quarter view, kneeling on one "
                "knee, pressing a thick clump of moss onto the leg of a sitting wounded hunter beside it with both "
                "hands",
    "Bear": "a huge, heavy bear with a scarred muzzle and small eyes, shaggy matted fur. Front view, standing "
            "up on its hind legs, front paws raised with long claws spread, mouth open in a roar",
    # Wounds
    "Twisted Ankle": "a gangly, miserable elf adventurer with a long chin and hollow cheeks, a patched cloak."
                     " Side view, walking with two wooden crutches under the arms, one foot on the ground, "
                     "the other foot thickly bandaged at the ankle and held just off the ground",
    "Bruised Ribs": "a stocky, wincing fighter with a broken-toothed grimace and a torn shirt. Front view, standing "
                    "bent slightly to one side, both hands pressed against the ribs, eyes squeezed shut",
    "Pulled Muscle": "a portly, middle-aged draconic adventurer with small scales on his face, bald head and "
                     "arms, slit reptile pupils, two swept-back dragon horns, a ridge of spines down the back"
                     " of the head, a big moustache, one thick scaly dragon tail, a tunic. Three-quarter "
                     "view, standing stiffly bent forward at the waist, grimacing. His right hand pressed to "
                     "the small of his back; his left hand braced flat on top of his left knee, the arm "
                     "straight. Two arms and hands only",
    "Concussion": "a dazed, cross-eyed brawler with a lump on the head, a dented helmet tipped sideways. Front "
                  "view, standing wobbling, arms half raised for balance, little stars and birds circling the head",
    "Shaken": "a skinny, twitchy adventurer with bulging eyes and hair standing on end, a rumpled cloak. Front view, "
              "standing hunched, clutching a dagger to the chest with both hands, glancing over one shoulder",
    "Deep Cut": "a big, weathered northern warrior with a braided beard, long hair in two thick braids, a "
                "broken nose, a fur collar and iron arm rings. Front view, standing on both feet, head bowed "
                "to look down at his belly, wincing. His left hand lifts the hem of his tunic up to his "
                "chest, his right hand pressed flat on his hip. Across his bare belly runs one long diagonal "
                "gash closed with big crossing stitches, the stitches clearly drawn",
    "Black Eye": "a sour, pudgy bullywug archer, a squat frog-man with a wide mouth and warty skin, a scowl, "
                 "a hood pushed back. One eye is punched: the eyelids puffed up and swollen almost shut, a "
                 "ring of bruise around it drawn with dense hatching, the eye itself a normal eye. Three-"
                 "quarter view, standing, drawing a bow with an arrow nocked, aiming off to the side of the "
                 "picture, squinting hard with the good eye, the arrow well away from the face",
    "Broken Nose": "a 60ish once-handsome, pompous noble with a big bandaged broken nose, a frilly collar. "
                   "Front view, standing, hands raised, trying to speak",
    "Torn Tendon": "a lanky, gangly adventurer with drooping mournful eyes, a long chin, sunken cheeks and a "
                   "scruffy beard, a coil of rope on one shoulder. Side view, standing at the foot of a short"
                   " stone wall, looking up at the top of it with a sigh, one hand resting on the stones, the"
                   " other leaning on a walking stick. The bad foot is held just off the ground, the ankle "
                   "splinted with two straight sticks tied on with strips of cloth",
    "Weak Grip": "a gaunt, trembling warrior with a long chin and a battered helmet. Front view, standing, a sword "
                 "slipping out of a shaking right hand, the blade tipping towards the ground, the whole sword in "
                 "clear view",
    "Cracked Jaw": "a glum bard with a cracked jaw tied up with a bandage knotted on top of the head, "
                   "covering the mouth, no hat. Front view, standing, arms hanging down, one hand holding a "
                   "single lute by its neck so it hangs at his side, unplayed, mouth shut tight. Only one "
                   "lute",
    "Nightmares": "a haggard, sleepless adventurer with dark rings under the eyes and wild hair, a blanket round the "
                  "shoulders. Front view, sitting up on a bedroll on the ground, staring ahead, a small shadowy "
                  "creature drawn at the edge of the blanket",
    "Broken Arm": "a sulking, square-faced troll fighter with the right arm in a sling of knotted cloth going"
                  " over the left shoulder, the arm bound to a wooden splint. Front view, standing, a sword "
                  "hanging from the belt, left hand empty",
    "Broken Fingers": "a grumpy, round-faced gnome with a big nose, a tight cap. Front view, standing, "
                      "holding up one hand showing its middle finger bandaged",
    "Swollen Hand": "a vain, bejewelled noble with a pointed beard, a ruff collar. Front view, standing, holding up "
                    "a huge puffy swollen hand, a ring stuck tight on one fat finger, the other hand tugging at it",
    "Cracked Ribs": "a hunched, wincing porter with a heavy bandage wound round the chest, a pack lying dropped on "
                    "the ground beside it. Front view, standing bent forward, one arm wrapped round the chest",
    "Wrenched Back": "a stout old adventurer with a bushy beard, bent double at the waist, frozen in place, both hands "
                     "on the small of the back, a full backpack lying dropped on the ground beside it. Side view",
    "Shattered Knee": "a grizzled old orc soldier with a scarred face, the left leg in a long splint from hip to "
                      "ankle. Front view, standing on both legs, both legs and both feet in clear view, the splinted "
                      "leg held stiff, leaning on a walking stick in the right hand planted on the ground beside the "
                      "right foot, outside the legs, left hand on the hip",
    "Skull Fracture": "a dazed, bookish adventurer with a bandage wrapped round the head and cracked spectacles, a "
                      "robe. Front view, standing, holding an open book upside down in both hands, frowning at it",
    "Internal Bleeding": "a pale, sweating, gaunt hobgoblin messenger with a flat nose, a jutting jaw and long "
                         "pointed ears, the face twisted in pain, eyes squeezed shut, teeth gritted, a satchel on the "
                         "shoulder. Three-quarter view, hunched forward, knees buckling, both arms wrapped tightly "
                         "around the belly, both hands clutching the sides",
}


SYMBOLS = {  # card symbols, drawn with gen_art.py --symbols (SYMBOL_STYLE) into rules/symbols/qwen/; tools/ink_symbols.py
    # turns them into rules/symbols/ink/ and puts the four ability emblems on a shield for the Defense symbols
    "str": "a clenched fist raised, seen from the front, knuckles forward, thumb wrapped across the fingers, short wrist",
    "dex": "a single feather, tilted, quill at the bottom left, tip at the top right, a solid black vane split by a white shaft",
    "int": "a wide open eye, almond shaped, a large solid black iris with a white highlight, no eyebrow",
    "wil": "an eight-pointed star with long sharp rays, a solid black dot in a white ring at its centre",
    "hp": "a plump heart shape, solid black, one small white highlight at the top left",
    "spd": "a tall riding boot seen from the side, toe pointing right, low heel, three short speed lines behind it on the left",
    "trait": "a young sprout, a short thick stem with two broad leaves opening left and right",
    "technique": "two straight swords crossed in an X, points up, simple crossguards and round pommels at the bottom",
    "knack": "an old iron key, diagonal, ring bow at the top left, bit with two teeth at the bottom right",
}
