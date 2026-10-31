"""French translation of the base set (cards/base_set.py) and the foe cards (cards/foes.py).

tools/build_cards.py --lang fr calls localize() after importing both: every card keeps its English name in
c["key"] (drawings in rules/art/ and the foe cards look cards up by it) and gets its French name, text, keywords
and lore. A missing translation stops the build with the list of untranslated strings.
Distances: 5 ft = 1,5 m (French fifth-edition convention). Terms follow rules/fr/GLOSSAIRE.md.
"""
import re

ABBR = {"STR": "FOR", "DEX": "DEX", "INT": "INT", "WIL": "VOL"}

NAMES = {
    # Callings
    "Duelist": "Duelliste", "Templar": "Templier", "Spellblade": "Lame-mage", "Infiltrator": "Infiltrateur",
    "Performer": "Artiste", "Sage": "Sage", "Brawler": "Bagarreur", "Zealot": "Zélote", "Tactician": "Tacticien",
    "Ranger": "Rôdeur", "Trickster": "Filou", "Hermit": "Ermite",
    # armor and hands
    "Leather": "Cuir", "Mail": "Mailles", "Plate": "Plates", "Shield": "Bouclier", "Dagger": "Dague",
    "Shortsword": "Épée courte", "Handaxe": "Hachette", "Finesse Blade": "Lame fine", "Longsword": "Épée longue",
    "Battleaxe": "Hache d'armes", "Greatsword": "Épée à deux mains", "Glaive": "Coutille", "Longbow": "Arc long",
    "Sling": "Fronde", "Javelins": "Javelines", "Spellguard Staff": "Bâton de garde-sort",
    "Traveler's Lute": "Luth du voyageur", "Greatclub": "Massue", "Gladius": "Gladius", "Boarspear": "Épieu",
    "Pilum": "Pilum", "Shortbow": "Arc court", "Greataxe": "Grande hache",
    # jewelry and items
    "Ring of Warding": "Anneau de protection", "Guild Signet": "Chevalière de guilde",
    "Shard Bandolier": "Bandoulière à Éclats", "Holy Amulet": "Amulette sacrée",
    "Boots of the Long Stride": "Bottes de grande foulée", "Ring of Sparks": "Anneau d'étincelles",
    "Dancer's Bells": "Grelots de danseur", "Potion of Healing": "Potion de soins", "Coin Pouch": "Bourse de cuir",
    "Writ of Favor": "Lettre de faveur", "Greater Potion of Healing": "Potion de soins supérieurs",
    "Restorative Salve": "Onguent réparateur", "Pocket Sand": "Sable de poche",
    "Alchemist's Fire Recipe": "Recette de feu grégeois",
    # Aspects
    "Springheel": "Talons-ressorts", "Stone Blood": "Sang de pierre", "Iron Will": "Volonté de fer",
    "Clear Mind": "Esprit clair", "Cleave": "Enchaînement", "Steady Aim": "Visée stable",
    "Shield Bash": "Coup de bouclier", "Battle Hymn": "Hymne de bataille", "Rallying Cry": "Cri de ralliement",
    "Shield Wall": "Mur de boucliers", "Cat Burglar": "Monte-en-l'air", "Renowned": "Renommé", "Sailor": "Marin",
    "Street Urchin": "Gamin des rues", "Hunter": "Chasseur", "Physician": "Médecin", "Barkeep": "Tavernier",
    "Smith": "Forgeron", "Mountaineer": "Montagnard", "Twin Strike": "Double frappe", "Second Wind": "Second souffle",
    "Wiry": "Nerveux", "Night Eyes": "Yeux de nuit", "Sellsword": "Lame à louer", "Acrobat": "Acrobate",
    "Pack Hunter": "Chasseur de meute", "Slippery": "Insaisissable", "Hedge Witch": "Sorcière des haies",
    "Sweeping Blow": "Coup balayant", "Relentless": "Implacable", "Human Grit": "Ténacité humaine",
    "Elven Blood": "Sang elfique", "Dwarven Blood": "Sang nain", "Halfling Luck": "Chance halfeline",
    "Orcish Blood": "Sang orque", "Hobgoblin Discipline": "Discipline hobgobeline",
    # Wounds
    "Twisted Ankle": "Cheville tordue", "Bruised Ribs": "Côtes contusionnées", "Pulled Muscle": "Claquage",
    "Concussion": "Commotion", "Shaken": "Ébranlé", "Deep Cut": "Entaille profonde", "Black Eye": "Œil au beurre noir",
    "Broken Nose": "Nez cassé", "Torn Tendon": "Tendon déchiré", "Weak Grip": "Poigne faible",
    "Cracked Jaw": "Mâchoire fêlée", "Nightmares": "Cauchemars", "Broken Arm": "Bras cassé",
    "Broken Fingers": "Doigts cassés", "Swollen Hand": "Main enflée", "Cracked Ribs": "Côtes fêlées",
    "Wrenched Back": "Dos bloqué", "Shattered Knee": "Genou brisé", "Skull Fracture": "Fracture du crâne",
    "Internal Bleeding": "Hémorragie interne",
    # decks: covers, spells, powers, Forms
    "Conjurer's Book": "Livre du conjurateur", "Wanderer's Repertoire": "Répertoire du vagabond",
    "Acolyte's Litany": "Litanie de l'acolyte", "Wildheart's Remembrance": "Souvenance du cœur sauvage",
    "Fire Bolt": "Trait de feu", "Mage Hand": "Main de mage", "Magic Missile": "Projectile magique",
    "Grease": "Graisse", "Misty Step": "Foulée brumeuse", "Web": "Toile d'araignée", "Jeer": "Raillerie",
    "Rally": "Ralliement", "Hold the Line": "Tenez la ligne", "Cutting Words": "Mots cinglants",
    "Steady Now": "Du calme", "Dread": "Effroi", "Rousing Verse": "Vers exaltant", "Guidance": "Assistance",
    "Bless": "Bénédiction", "Bane": "Fléau", "Twist Fate": "Tordre le destin", "Healing Word": "Mot de guérison",
    "Cure Wounds": "Soins", "Hawk": "Faucon", "Wolf": "Loup", "Mossbalm": "Baume de mousse", "Bear": "Ours",
    # foes
    "Bandit": "Bandit", "Bandit Archer": "Archer bandit", "Goblin": "Gobelin", "Cultist": "Cultiste",
    "Legionary": "Légionnaire", "Bandit Captain": "Capitaine bandit", "Ogre": "Ogre", "Ogre Chieftain": "Chef ogre",
    "Guard": "Garde", "Scout": "Éclaireur", "Mage": "Mage", "Orc": "Orque", "Hobgoblin": "Hobgobelin",
    "Skeleton": "Squelette", "Zombie": "Zombie", "Kobold": "Kobold", "Giant Rat": "Rat géant",
    "Giant Spider": "Araignée géante", "Troll": "Troll",
}

LEVELS = {"Cantrip": "Tour de magie", "1st": "1er", "2nd": "2e", "Anthem": "Hymne", "Dirge": "Complainte",
          "Cue": "Réplique", "Mend": "Soin", "Form": "Forme"}

# keywords, one at a time ("Range 150/600" and "Thrown 20/60" convert their feet)
KEYWORDS = {
    "Calling": "Vocation", "Armor": "Armure", "Weapon": "Arme", "Shield": "Bouclier", "Instrument": "Instrument",
    "Focus": "Focaliseur", "Jewelry": "Bijou", "Consumable": "Consommable", "Purse": "Bourse", "Recipe": "Recette",
    "3 flasks": "3 fioles", "Spellbook": "Livre de sorts", "Spell": "Sort", "Cantrip": "Tour de magie",
    "Trait": "Trait", "Technique": "Technique", "Knack": "Savoir-faire", "Divine": "Divin", "Glamour": "Glamour",
    "Nature": "Nature", "Anthem": "Hymne", "Dirge": "Complainte", "Cue": "Réplique", "Mend": "Soin", "Form": "Forme",
    "Wound": "Blessure", "Crippling": "Invalidante", "Hand": "Main", "Item": "Objet", "Heavy": "Lourde",
    "Light": "Légère", "Reach": "Allonge", "Two-Handed": "Deux mains", "Versatile (1d10)": "Polyvalente (1d10)",
    "Restrained": "Entravé", "Targets DEX": "Vise DEX", "Duration 1 minute": "Durée 1 minute",
    "Duration 1 round": "Durée 1 round", "Gold": "Or", "Foe": "Adversaire", "Boss": "Boss", "Leader": "Meneur",
    "Tiny": "Très petit", "Small": "Petit", "Medium": "Moyen", "Large": "Grand",
}


def feet(n):
    """30 → "9", 35 → "10,5" (5 ft = 1,5 m)."""
    return f"{round(float(n) * 0.3, 2):g}".replace(".", ",")


def keyword(k):
    if k in KEYWORDS:
        return KEYWORDS[k]
    m = re.fullmatch(r"(Range|Thrown|Darkvision|Cube|Noisy) ([\d/]+)", k)
    if m:
        word = {"Range": "Portée", "Thrown": "Lancer", "Darkvision": "Vision dans le noir", "Cube": "Cube",
                "Noisy": "Bruyante"}[m[1]]
        nums = m[2] if m[1] == "Noisy" else "/".join(feet(n) for n in m[2].split("/"))
        return f"{word} {nums}"
    raise KeyError(k)


def keywords(kw):
    return " · ".join(keyword(k) for k in kw.split(" · ")) if kw else kw


ACTIVITIES = {
    "sneak, climb or pick locks": "se faufiler, grimper ou crocheter les serrures",
    "persuade, haggle, gather rumors or perform": "persuader, marchander, recueillir des rumeurs ou se produire",
    "swim, climb, navigate or gather rumors": "nager, grimper, s'orienter ou recueillir des rumeurs",
    "pick pockets, sneak, read intentions or gather rumors": "faire les poches, se faufiler, deviner les intentions ou recueillir des rumeurs",
    "track, notice, sneak or handle animals": "pister, remarquer, se faufiler ou dresser les animaux",
    "treat wounds, recall lore, read intentions or persuade": "soigner les blessures, se souvenir de connaissances, deviner les intentions ou persuader",
    "read intentions, gather rumors, intimidate or lift": "deviner les intentions, recueillir des rumeurs, intimider ou soulever",
    "lift, break, haggle or recall lore": "soulever, briser, marchander ou se souvenir de connaissances",
    "climb, endure, navigate or balance": "grimper, endurer, s'orienter ou garder l'équilibre",
    "intimidate, endure, haggle or gather rumors": "intimider, endurer, marchander ou recueillir des rumeurs",
    "tumble, balance, jump or perform": "faire des acrobaties, garder l'équilibre, sauter ou se produire",
    "intimidate, endure, lift or march": "intimider, endurer, soulever ou marcher longtemps",
    "march, navigate, stand firm or read intentions": "marcher longtemps, s'orienter, tenir bon ou deviner les intentions",
}

TEXT = {
    # Calling perks
    "**Footwork:** once per turn, after you hit with a melee attack, move 5 ft. This movement doesn't provoke opportunity attacks.":
        "**Jeu de jambes :** une fois par tour, après avoir touché au corps à corps, déplacez-vous de 1,5 m. Ce déplacement ne provoque pas d'attaque d'opportunité.",
    "**Oath (1/S.R.):** reaction, when an attack hits an ally within 5 ft: you take its damage instead.":
        "**Serment (1/R.C.) :** réaction, quand une attaque touche un allié à 1,5 m ou moins : vous subissez ses dégâts à sa place.",
    "**Battle Caster:** a weapon you hold counts as an empty Hand for casting from a Spellbook.":
        "**Incantateur de guerre :** une arme que vous tenez compte comme une Main vide pour lancer des sorts depuis un Livre de sorts.",
    "**Unseen:** +2 on checks to sneak, pick locks and spot traps.":
        "**Inaperçu :** +2 aux tests pour se faufiler, crocheter les serrures et repérer les pièges.",
    "**Crowd Work (1/S.R.):** reaction, after an ally within 30 ft rolls an attack or a check: +2 to that roll.":
        "**Complicité du public (1/R.C.) :** réaction, après qu'un allié à 9 m ou moins a fait une attaque ou un test : +2 à ce jet.",
    "**Learned:** 1 extra spell point on a Spellbook you hold. +2 on checks to recall lore.":
        "**Érudit :** 1 point de sort supplémentaire sur un Livre de sorts que vous tenez. +2 aux tests pour se souvenir de connaissances.",
    "**Scrapper:** +2 to hit with Grapples and Shoves.": "**Teigneux :** +2 au toucher pour Empoigner et Bousculer.",
    "**Righteous Fury (1/S.R.):** when you hit with a weapon attack: +1d6 Radiant damage.":
        "**Juste colère (1/R.C.) :** quand vous touchez avec une attaque d'arme : +1d6 dégâts Radiants.",
    "**Command (1/S.R.):** action. An ally within 30 ft who can hear you uses its reaction to make one weapon attack.":
        "**Commandement (1/R.C.) :** action. Un allié à 9 m ou moins qui peut vous entendre utilise sa réaction pour faire une attaque d'arme.",
    "**Quarry (1/S.R.):** when you hit with a ranged attack: +2 on your attacks against that target until the end of your next turn.":
        "**Proie (1/R.C.) :** quand vous touchez avec une attaque à distance : +2 à vos attaques contre cette cible jusqu'à la fin de votre prochain tour.",
    "**Feint (1/S.R.):** reaction, when an attack hits you: −2 to that attack roll, possibly turning it into a miss.":
        "**Feinte (1/R.C.) :** réaction, quand une attaque vous touche : −2 à ce jet d'attaque, ce qui peut le transformer en échec.",
    "**Solitude:** 1 extra Resolve on a Divine, Glamour or Nature deck you have. +2 on checks to forage and endure.":
        "**Solitude :** 1 Ardeur supplémentaire sur un paquet Divin, de Glamour ou de Nature que vous avez. +2 aux tests pour cueillir et endurer.",
    # hands
    "Takes one Hand.": "Occupe une Main.",
    "**Sap:** when you hit, the target has −2 on its next attack roll before the start of your next turn.":
        "**Saignée :** quand vous touchez, la cible a −2 à son prochain jet d'attaque avant le début de votre prochain tour.",
    "While you hold it, it counts as an empty Hand for casting from a Spellbook.":
        "Tant que vous le tenez, il compte comme une Main vide pour lancer des sorts depuis un Livre de sorts.",
    "1 extra Resolve (short rest).": "1 Ardeur supplémentaire (repos court).",
    "Your Anthems reach 60 ft instead of 30 ft.": "Vos Hymnes portent à 18 m au lieu de 9 m.",
    "**Crushing:** on a critical hit, the target is knocked Prone.": "**Écrasement :** sur un coup critique, la cible est mise À terre.",
    "**Close Order:** +1d4 damage while an ally is engaged with the same creature.":
        "**Ordre serré :** +1d4 dégâts tant qu'un allié est engagé avec la même créature.",
    "**Brace:** your opportunity attacks with it deal +1d8 damage.": "**En arrêt :** vos attaques d'opportunité avec lui infligent +1d8 dégâts.",
    "**Pierce:** on a hit, a Shield the target holds gives no bonus until it spends an action to pull the pilum free.":
        "**Perforation :** si l'attaque touche, un Bouclier que tient la cible ne donne plus de bonus jusqu'à ce qu'elle dépense une action pour arracher le pilum.",
    # jewelry
    "**Reaction (2/S.R.)**, when an attack hits you: +2 to the targeted Defense against that attack, possibly turning it into a miss.":
        "**Réaction (2/R.C.)**, quand une attaque vous touche : +2 à la Défense visée contre cette attaque, ce qui peut la transformer en échec.",
    "**Action (1/L.R.)**, in a settlement where the guild operates: a contact finds you within 1 hour. They share one fact the guild would know, or hide you for a night.":
        "**Action (1/R.L.)**, dans une localité où la guilde opère : un contact vous trouve dans l'heure. Il vous révèle un fait que la guilde connaîtrait, ou vous cache pour une nuit.",
    "You can carry 2 more Shards in your Pack (5 in all). They still count toward its 8 pieces.":
        "Vous pouvez porter 2 Éclats de plus dans votre Sac (5 en tout). Ils comptent toujours dans ses 8 pièces.",
    "Your Cues reach 90 ft instead of 60 ft.": "Vos Répliques portent à 27 m au lieu de 18 m.",
    "**Reaction (1/S.R.):** Move.": "**Réaction (1/R.C.) :** Déplacement.",
    "**Reaction (1/S.R.)**, when a creature within 5 ft hits you: it takes 2d6 Lightning.":
        "**Réaction (1/R.C.)**, quand une créature à 1,5 m ou moins vous touche : elle subit 2d6 Foudre.",
    "Your Dirges reach 90 ft instead of 60 ft.": "Vos Complaintes portent à 27 m au lieu de 18 m.",
    # items
    "**Action:** drink it, or give it to a creature within 5 ft. It regains 2d4 + 2 HP.":
        "**Action :** buvez-la, ou donnez-la à une créature à 1,5 m ou moins. Elle récupère 2d4 + 2 PV.",
    "Holds up to **100 gp**.": "Contient jusqu'à **100 po**.",
    "A sealed letter from a noble house, a guild or a temple. Show it to one of its members: they grant one reasonable request (shelter, an audience, safe passage, a loan up to 100 gp).":
        "Une lettre scellée d'une maison noble, d'une guilde ou d'un temple. Montrez-la à l'un de ses membres : il accède à une demande raisonnable (un abri, une audience, un sauf-conduit, un prêt jusqu'à 100 po).",
    "**Action:** drink it, or give it to a creature within 5 ft. It regains 4d4 + 4 HP.":
        "**Action :** buvez-la, ou donnez-la à une créature à 1,5 m ou moins. Elle récupère 4d4 + 4 PV.",
    "**Action:** spread it on a creature within 5 ft. Heal one of its Wounds.":
        "**Action :** étalez-le sur une créature à 1,5 m ou moins. Guérissez l'une de ses Blessures.",
    "**Reaction:** throw it at a creature within 5 ft. Attack (DEX or WIL + 2) against its DEX Defense: on a hit, it has −2 on attacks until the end of its next turn.":
        "**Réaction :** lancez-le sur une créature à 1,5 m ou moins. Attaque (DEX ou VOL + 2) contre sa Défense de DEX : si elle touche, la créature a −2 aux attaques jusqu'à la fin de son prochain tour.",
    "**Reaction:** throw a flask up to 30 ft. Make one attack (DEX or INT + 3) against the DEX Defense of each creature within 5 ft of the impact: 2d6 Fire on a hit, half on a miss.":
        "**Réaction :** lancez une fiole jusqu'à 9 m. Faites une attaque (DEX ou INT + 3) contre la Défense de DEX de chaque créature à 1,5 m ou moins du point d'impact : 2d6 Feu si elle touche, la moitié en cas d'échec.",
    # Aspects
    "Your jump distances are doubled, and you never need a running start.":
        "Vos distances de saut sont doublées, et vous n'avez jamais besoin d'élan.",
    "+2 STR Defense against poison and disease.": "+2 à la Défense de FOR contre le poison et la maladie.",
    "+2 WIL Defense against fear and mind control.": "+2 à la Défense de VOL contre la peur et le contrôle mental.",
    "+2 INT Defense against illusions and confusion.": "+2 à la Défense d'INT contre les illusions et la confusion.",
    "**1/S.R.**, when your melee attack drops a creature to 0 HP: make one melee attack against another creature within your reach.":
        "**1/R.C.**, quand votre attaque au corps à corps fait tomber une créature à 0 PV : faites une attaque au corps à corps contre une autre créature à votre allonge.",
    "**Reaction (2/S.R.):** your next ranged attack this turn has +2 to hit.":
        "**Réaction (2/R.C.) :** votre prochaine attaque à distance de ce tour a +2 au toucher.",
    "**Reaction (1/S.R.)**, when you take the Attack action while holding a Shield: Shove a creature within 5 ft.":
        "**Réaction (1/R.C.)**, quand vous effectuez l'action Attaque en tenant un Bouclier : Bousculez une créature à 1,5 m ou moins.",
    "**2/S.R.**, when you hit with a weapon attack: up to 3 allies within 30 ft who can hear you have +2 on their next attack before the end of your next turn.":
        "**2/R.C.**, quand vous touchez avec une attaque d'arme : jusqu'à 3 alliés à 9 m ou moins qui peuvent vous entendre ont +2 à leur prochaine attaque avant la fin de votre prochain tour.",
    "*Rally* as a loose Anthem.": "*Ralliement* comme Hymne isolé.",
    "**Action (1/S.R.):** Duration 1 minute. Up to 3 allies within 30 ft have +2 on attacks.":
        "**Action (1/R.C.) :** Durée 1 minute. Jusqu'à 3 alliés à 9 m ou moins ont +2 aux attaques.",
    "**Reaction (1/S.R.)**, when an attack hits an ally within 5 ft while you hold a Shield: +2 to the targeted Defense against that attack, possibly turning it into a miss.":
        "**Réaction (1/R.C.)**, quand une attaque touche un allié à 1,5 m ou moins pendant que vous tenez un Bouclier : +2 à la Défense visée contre cette attaque, ce qui peut la transformer en échec.",
    "Once per turn, when you take the Attack action, make one extra attack.":
        "Une fois par tour, quand vous effectuez l'action Attaque, faites une attaque supplémentaire.",
    "**Action (1/S.R.):** regain 1d10 + 3 HP.": "**Action (1/R.C.) :** récupérez 1d10 + 3 PV.",
    "**1/S.R.**, when you hit a creature one of your allies is engaged with: it falls Prone.":
        "**1/R.C.**, quand vous touchez une créature avec laquelle l'un de vos alliés est engagé : elle tombe À terre.",
    "**Reaction (2/S.R.):** move up to half your Speed. This movement doesn't provoke opportunity attacks.":
        "**Réaction (2/R.C.) :** déplacez-vous jusqu'à la moitié de votre Vitesse. Ce déplacement ne provoque pas d'attaque d'opportunité.",
    "1 extra spell point (long rest).": "1 point de sort supplémentaire (repos long).",
    "+3 on checks to handle animals, recall lore, treat wounds or deceive.":
        "+3 aux tests pour dresser les animaux, se souvenir de connaissances, soigner les blessures ou tromper.",
    "+3 on checks to intimidate, endure, haggle or gather rumors.":
        "+3 aux tests pour intimider, endurer, marchander ou recueillir des rumeurs.",
    "+3 on checks to tumble, balance, jump or perform.":
        "+3 aux tests pour faire des acrobaties, garder l'équilibre, sauter ou se produire.",
    "**1/S.R.**, when you take the Attack action with a Heavy or Reach weapon: make one attack roll against each enemy within your reach instead. Half damage on a miss.":
        "**1/R.C.**, quand vous effectuez l'action Attaque avec une arme Lourde ou à Allonge : faites à la place un jet d'attaque contre chaque ennemi à votre allonge. Moitié des dégâts en cas d'échec.",
    "**1/S.R.**, when damage drops you to 0 HP without killing you outright: you drop to 1 HP instead.":
        "**1/R.C.**, quand des dégâts vous font tomber à 0 PV sans vous tuer sur le coup : vous tombez à 1 PV à la place.",
    "**Stubborn (1/S.R.):** when you fail a check, add +2 to that roll, possibly turning it into a success.":
        "**Têtu (1/R.C.) :** quand vous ratez un test, ajoutez +2 à ce jet, ce qui peut le transformer en réussite.",
    "+2 STR Defense against poison.": "+2 à la Défense de FOR contre le poison.",
    "**Lucky (1/S.R.):** when you roll a 1 on a d20, reroll it.": "**Veinard (1/R.C.) :** quand vous faites 1 sur un d20, relancez-le.",
    # Wounds
    "You hobble.": "Vous boitez.", "Every breath hurts.": "Chaque respiration fait mal.",
    "You can't twist away in time.": "Vous ne pivotez plus assez vite.", "The world swims a little.": "Le monde tangue un peu.",
    "You flinch at every shadow.": "Vous sursautez à chaque ombre.", "Stitched, not healed.": "Recousue, pas guérie.",
    "−2 on ranged attacks and on checks to notice.": "−2 aux attaques à distance et aux tests pour remarquer.",
    "−2 on WIL checks.": "−2 aux tests de VOL.", "−2 on checks to climb, jump or swim.": "−2 aux tests pour grimper, sauter ou nager.",
    "−2 on melee attacks.": "−2 aux attaques au corps à corps.",
    "1 less Resolve and 1 less spell point.": "1 Ardeur de moins et 1 point de sort de moins.",
    "A short rest heals only a quarter of your missing HP (rounded up).":
        "Un repos court ne soigne qu'un quart de vos PV manquants (arrondi au supérieur).",
    "You may never run the same again.": "Vous ne courrez peut-être plus jamais comme avant.",
    "−2 on INT checks.": "−2 aux tests d'INT.", "You lose blood every time you move too fast.": "Vous perdez du sang dès que vous bougez trop vite.",
    # deck covers
    "Spell attack: **INT + 2**": "Attaque de sort : **INT + 2**", "Spell points: **4** (long rest)": "Points de sort : **4** (repos long)",
    "Max spell level: **2nd**": "Niveau de sort max : **2e**", "Casting needs an empty Hand.": "L'incantation demande une Main vide.",
    "Attack: **WIL + 2**": "Attaque : **VOL + 2**", "Resolve: **3 + WIL** (short rest)": "Ardeur : **3 + VOL** (repos court)",
    "Songs, poems and dances.": "Chants, poèmes et danses.", "Prayers. Fate dice: **d4**.": "Prières. Dés du destin : **d4**.",
    "Beasts your body remembers. Shift: action.": "Des bêtes dont votre corps se souvient. Muer : action.",
    # spells and powers
    "**Action**, range 120 ft.": "**Action**, portée 36 m.",
    "Spell attack against DEX Defense: **1d10 Fire**. A flammable object it hits catches fire.":
        "Attaque de sort contre la Défense de DEX : **1d10 Feu**. Un objet inflammable touché prend feu.",
    "**Action**, range 30 ft, Duration 1 minute.": "**Action**, portée 9 m, Durée 1 minute.",
    "A spectral hand lifts, carries or works an object up to 10 lb. It can't attack. Move it with your reaction.":
        "Une main spectrale soulève, porte ou manipule un objet de 5 kg au plus. Elle ne peut pas attaquer. Déplacez-la avec votre réaction.",
    "Three darts at one to three creatures. One spell attack against the DEX Defense of each target: **1d4 + 1 Radiant** per dart on a hit, half on a miss.":
        "Trois fléchettes sur une à trois créatures. Une attaque de sort contre la Défense de DEX de chaque cible : **1d4 + 1 Radiant** par fléchette si elle touche, la moitié en cas d'échec.",
    "**Upcast:** +1 dart per level above 1st.": "**Surpuissance :** +1 fléchette par niveau au-delà du 1er.",
    "**Reaction**, when an attack hits you.": "**Réaction**, quand une attaque vous touche.",
    "+5 to your STR and DEX Defense until the start of your next turn, against the triggering attack too.":
        "+5 à vos Défenses de FOR et de DEX jusqu'au début de votre prochain tour, y compris contre l'attaque déclencheuse.",
    "**Action**, range 60 ft, Duration 1 minute.": "**Action**, portée 18 m, Durée 1 minute.",
    "A 10-ft cube of slick grease: difficult terrain. Spell attack against the DEX Defense of each creature in it, and of each one that enters it or ends its turn there: on a hit, it falls **Prone**.":
        "Un cube de 3 m de graisse glissante : terrain difficile. Attaque de sort contre la Défense de DEX de chaque créature à l'intérieur, et de chacune qui y entre ou y termine son tour : si elle touche, la créature tombe **À terre**.",
    "**Reaction.**": "**Réaction.**",
    "Teleport up to 30 ft to an unoccupied space you can see.": "Téléportez-vous jusqu'à 9 m vers un espace inoccupé que vous voyez.",
    "**Action**, range 60 ft, Duration 1 hour.": "**Action**, portée 18 m, Durée 1 heure.",
    "A 20-ft cube of webs: difficult terrain. Spell attack against the DEX Defense of each creature in it, and of each one that enters it: on a hit, it is **Restrained** for 2 turns. Fire burns a 5-ft square away each round.":
        "Un cube de 6 m de toiles : terrain difficile. Attaque de sort contre la Défense de DEX de chaque créature à l'intérieur, et de chacune qui y entre : si elle touche, la créature est **Entravée** pendant 2 tours. Le feu en brûle une case de 1,5 m par round.",
    "**Action.** Attack against WIL Defense: until the end of the target's next turn, it has −2 on its next attack.":
        "**Action.** Attaque contre la Défense de VOL : jusqu'à la fin du prochain tour de la cible, elle a −2 à sa prochaine attaque.",
    "**Action**, Duration 1 minute.": "**Action**, Durée 1 minute.",
    "Up to 3 allies within 30 ft have +2 on attacks.": "Jusqu'à 3 alliés à 9 m ou moins ont +2 aux attaques.",
    "Allies within 30 ft have +2 to STR and DEX Defense.": "Les alliés à 9 m ou moins ont +2 aux Défenses de FOR et de DEX.",
    "**Reaction**, after a creature within 60 ft rolls.": "**Réaction**, après le jet d'une créature à 18 m ou moins.",
    "−2 to an enemy's attack roll or check.": "−2 au jet d'attaque ou au test d'un ennemi.",
    "+2 to an ally's roll, or to the Defense an attack targets.": "+2 au jet d'un allié, ou à la Défense que vise une attaque.",
    "**Action.** Attack against WIL Defense: the target is **Frightened** of you for 2 turns.":
        "**Action.** Attaque contre la Défense de VOL : la cible est **Effrayée** par vous pendant 2 tours.",
    "**Action**, range 60 ft.": "**Action**, portée 18 m.",
    "A creature regains 2d4 + WIL HP.": "Une créature récupère 2d4 + VOL PV.",
    "**Reaction**, after an ally within 60 ft rolls a check.": "**Réaction**, après le test d'un allié à 18 m ou moins.",
    "Add 1d4 to it.": "Ajoutez-y 1d4.",
    "Up to 3 allies within 30 ft add 1d4 to their attack rolls.": "Jusqu'à 3 alliés à 9 m ou moins ajoutent 1d4 à leurs jets d'attaque.",
    "Attack against WIL Defense: the target subtracts 1d4 from its attack rolls.":
        "Attaque contre la Défense de VOL : la cible soustrait 1d4 à ses jets d'attaque.",
    "**Reroll:** make it reroll an attack roll or a check.": "**Relance :** faites-lui relancer un jet d'attaque ou un test.",
    "**Action**, touch.": "**Action**, contact.", "A creature regains 2d8 + WIL HP.": "Une créature récupère 2d8 + VOL PV.",
    "**Tiny** · Fly 60 ft.": "**Très petit** · Vol 18 m.", "Talons: +2 to hit, 1d4 + DEX Physical.": "Serres : +2 au toucher, 1d4 + DEX Physique.",
    "+2 on checks to notice.": "+2 aux tests pour remarquer.", "**Medium**.": "**Moyen**.",
    "Bite: +2 to hit, 1d6 + DEX Physical.": "Morsure : +2 au toucher, 1d6 + DEX Physique.",
    "+2 on checks to track.": "+2 aux tests pour pister.", "**Large** · Climb 30 ft.": "**Grand** · Escalade 9 m.",
    "Hide: +2 STR Defense (included).": "Cuir épais : +2 Défense de FOR (compris).",
    "Claws: +2 to hit, 1d8 + STR Physical.": "Griffes : +2 au toucher, 1d8 + FOR Physique.",
    # foes' own text
    "**Bite:** +4 to hit, 1d6 + 2 Physical.": "**Morsure :** +4 au toucher, 1d6 + 2 Physique.",
    "**Keen Nose:** alert (passive Awareness +5).": "**Flair :** alerte (Vigilance passive +5).",
    "Throws its *Pilum*, then draws its *Gladius*.": "Lance son *Pilum*, puis dégaine son *Gladius*.",
    "**Giant Strength:** +60 HP. Its *Javelins* roll one extra damage die (included). Its *Sweeping Blow* recharges on a 5–6 instead of 1/S.R.":
        "**Force de géant :** +60 PV. Ses *Javelines* lancent un dé de dégâts supplémentaire (compris). Son *Coup balayant* se recharge sur 5–6 au lieu de 1/R.C.",
    "**Warlord:** its *Sweeping Blow* recharges on a 5–6 instead of 1/S.R.":
        "**Seigneur de guerre :** son *Coup balayant* se recharge sur 5–6 au lieu de 1/R.C.",
    "**Bellow (Recharge 5–6):** reaction. Attack (+5) against the WIL Defense of each enemy within 30 ft: Frightened of the chieftain until the end of its next turn.":
        "**Beuglement (Recharge 5–6) :** réaction. Attaque (+5) contre la Défense de VOL de chaque ennemi à 9 m ou moins : Effrayé par le chef jusqu'à la fin de son prochain tour.",
    "**Keen Eyes:** alert (passive Awareness +5).": "**Œil perçant :** alerte (Vigilance passive +5).",
    "**Undead:** resists Poison and Necrotic, vulnerable to Radiant. Never checks Morale.":
        "**Mort-vivant :** résiste au Poison et au Nécrotique, vulnérable au Radiant. Ne teste jamais son Moral.",
    "**Slam:** +3 to hit, 1d8 + 1 Physical.": "**Coup :** +3 au toucher, 1d8 + 1 Physique.",
    "**Bite:** +4 to hit, 1d4 + 2 Physical.": "**Morsure :** +4 au toucher, 1d4 + 2 Physique.",
    "**Spider Climb:** climbs walls and ceilings at full Speed. **Web Sense:** alert (passive Awareness +5).":
        "**Pattes d'araignée :** grimpe aux murs et aux plafonds à pleine Vitesse. **Sens de la toile :** alerte (Vigilance passive +5).",
    "**Bite:** +5 to hit, 1d8 + 3 Physical plus 1d8 Poison.": "**Morsure :** +5 au toucher, 1d8 + 3 Physique plus 1d8 Poison.",
    "**Web (Recharge 5–6):** action, range 30 ft. Attack (+3) against DEX Defense: **Restrained** for 2 turns.":
        "**Toile (Recharge 5–6) :** action, portée 9 m. Attaque (+3) contre la Défense de DEX : **Entravé** pendant 2 tours.",
    "**Claws:** +6 to hit, 2d6 + 4 Physical.": "**Griffes :** +6 au toucher, 2d6 + 4 Physique.",
    "**Regeneration:** regains 10 HP at the start of its turn, unless it took Fire or Poison damage since its last turn.":
        "**Régénération :** récupère 10 PV au début de son tour, sauf s'il a subi des dégâts de Feu ou de Poison depuis son dernier tour.",
}

LORE = {
    # Callings
    "Footwork drilled until it needs no thought. The blade goes where the eyes already are.": "Un jeu de jambes répété jusqu'à ne plus y penser. La lame va où les yeux sont déjà.",
    "A vow, a shield arm and a spine that does not bend. Others stand behind this one.": "Un serment, un bras de bouclier et une échine qui ne plie pas. Les autres se tiennent derrière.",
    "Steel in one hand, a spell on the tongue. Taught that the two were never separate.": "L'acier dans une main, un sort sur la langue. On lui a appris que les deux n'ont jamais fait qu'un.",
    "Locks, ledges and the patience of a held breath. Nobody remembers seeing them leave.": "Serrures, corniches et la patience d'un souffle retenu. Personne ne se souvient de l'avoir vu partir.",
    "Quick feet and a quicker smile. Every room is a stage, every fight an audience.": "Le pied vif et le sourire plus vif encore. Chaque salle est une scène, chaque combat un public.",
    "A mind that kept every page it ever read, and a voice that makes the pages speak.": "Un esprit qui a gardé chaque page lue, et une voix qui fait parler les pages.",
    "Taverns, docks and pit fights. Swords are for people who can't hold on.": "Tavernes, quais et combats de fosse. Les épées, c'est pour ceux qui ne savent pas tenir prise.",
    "A fire that won't go out, and a cause worth burning for. Doubt is for other people.": "Un feu qui ne s'éteint pas, et une cause qui vaut qu'on brûle pour elle. Le doute, c'est pour les autres.",
    "Every fight is a board, every ally a piece. They see the move three turns before it lands.": "Chaque combat est un échiquier, chaque allié une pièce. Le coup se voit trois tours à l'avance.",
    "Weeks alone on a trail, and an arrow that never wastes its flight.": "Des semaines seul sur une piste, et une flèche qui ne gâche jamais son vol.",
    "Never where you swing. Always where you look away. The grin is the last thing you see.": "Jamais là où l'on frappe. Toujours là où l'on détourne les yeux. Le sourire est la dernière chose qu'on voit.",
    "Years in a cave or a forest, talking to stones and stars. Something out there answered.": "Des années dans une grotte ou une forêt, à parler aux pierres et aux étoiles. Quelque chose a répondu.",
    # armor
    "Supple hide, oiled and stitched. It creaks a little, but it lets you run.": "Une peau souple, huilée et cousue. Elle grince un peu, mais elle laisse courir.",
    "Riveted rings over a padded coat. Heavy on the shoulders, light on the conscience.": "Des anneaux rivetés sur un gambison. Lourd aux épaules, léger pour la conscience.",
    "Full steel, fitted to you. You hear yourself coming, and so does everyone else.": "De l'acier de pied en cap, ajusté sur vous. On vous entend venir, vous comme les autres.",
    # hands
    "Oak boards, an iron rim, a dented boss. Every scar on it is a blow you never felt.": "Des planches de chêne, un cerclage de fer, un umbo cabossé. Chaque cicatrice est un coup que vous n'avez pas senti.",
    "Every traveler carries one. It cuts bread, rope and, when it must, throats.": "Tout voyageur en porte une. Elle tranche le pain, la corde et, s'il le faut, les gorges.",
    "A short, honest blade for tight alleys and crowded fights.": "Une lame courte et franche pour les ruelles étroites et les mêlées serrées.",
    "A woodcutter's tool that learned a second trade. It flies true when thrown.": "Un outil de bûcheron qui a appris un second métier. Lancée, elle vole droit.",
    "A slim duelist's sword. A nick here, a cut there, and the foe's arm grows slow.": "Une fine épée de duelliste. Une entaille ici, une coupure là, et le bras adverse s'alourdit.",
    "The knight's blade: one hand for the shield, two hands when the shield breaks.": "La lame du chevalier : une main pour le bouclier, deux quand le bouclier se brise.",
    "A bearded head on an ash haft. It splits shields as easily as firewood.": "Un fer barbu sur un manche de frêne. Il fend les boucliers comme du petit bois.",
    "As tall as a child and twice as loud. You don't parry it; you get out of its way.": "Grande comme un enfant et deux fois plus bruyante. On ne la pare pas : on s'écarte.",
    "A blade on a long pole. It keeps the enemy at a distance, where it should be.": "Une lame au bout d'une longue hampe. Elle tient l'ennemi à distance, là où il doit être.",
    "Yew, horn and patience. A trained archer drops a charging boar before it closes.": "If, corne et patience. Un archer entraîné abat un sanglier qui charge avant qu'il n'arrive.",
    "A strip of leather and a pouch of stones. Shepherds have killed giants with less.": "Une lanière de cuir et une bourse de pierres. Des bergers ont tué des géants avec moins.",
    "A bundle of light spears, made to be thrown first and asked about later.": "Une botte de lances légères, faites pour être lancées d'abord et discutées ensuite.",
    "Runes run along its grain. The wood remembers the shape of a casting hand.": "Des runes courent le long du fil. Le bois se souvient de la forme d'une main qui incante.",
    "Its varnish is worn where a hundred hands have strummed it. The tunes carry far.": "Son vernis est usé là où cent mains l'ont gratté. Ses airs portent loin.",
    "A tree limb with ambitions. What it hits stays down for a while.": "Une branche qui a de l'ambition. Ce qu'elle frappe reste à terre un moment.",
    "A soldier's sword, short and wide, made for fighting shoulder to shoulder.": "Une épée de soldat, courte et large, faite pour combattre coude à coude.",
    "Its crossbar stops a charging beast on the point. Hunters set it, then wait.": "Sa traverse arrête sur la pointe une bête qui charge. Le chasseur la cale, puis attend.",
    "A soft iron shank bends on impact, so the spear can't be thrown back, and the shield can't be raised.": "Sa tige de fer doux plie à l'impact : impossible de le renvoyer, impossible de lever le bouclier.",
    "Light enough to shoot from the saddle or from the treetops.": "Assez léger pour tirer de la selle ou du haut des arbres.",
    "A crescent of iron on a heavy haft. One swing, one problem fewer.": "Un croissant de fer sur un lourd manche. Un coup, un problème de moins.",
    # jewelry
    "A band of cold silver. It tightens around the finger just before the blow lands.": "Un anneau d'argent froid. Il se resserre sur le doigt juste avant que le coup ne porte.",
    "Press it into wax and doors open. Lose it, and someone comes asking why.": "Pressez-la dans la cire et les portes s'ouvrent. Perdez-la, et quelqu'un viendra demander pourquoi.",
    "Leather straps padded for crystal. Shards clink softly against each other as you walk.": "Des sangles de cuir rembourrées pour le cristal. Les Éclats tintent doucement à chaque pas.",
    "A blessed token on a worn cord. Prayers spoken over it seem to travel further.": "Un médaillon béni sur un cordon usé. Les prières dites sur lui semblent porter plus loin.",
    "Soft boots that never wear out. Every few steps, one lands farther than it should.": "Des bottes souples qui ne s'usent jamais. Tous les quelques pas, l'un d'eux tombe plus loin qu'il ne devrait.",
    "Copper wire coiled around a blue stone. It bites whoever lays a hand on its wearer.": "Un fil de cuivre enroulé autour d'une pierre bleue. Il mord quiconque porte la main sur son porteur.",
    "A string of tiny bells for the ankle. Their jingle gets under an enemy's skin.": "Un chapelet de clochettes pour la cheville. Leur tintement agace l'ennemi jusqu'à l'os.",
    # items
    "Red and faintly warm, it tastes of iron and cherries. Shake before drinking.": "Rouge et un peu tiède, elle a un goût de fer et de cerise. Agiter avant de boire.",
    "A drawstring purse of good leather. Its weight is the only friend some people have.": "Une bourse à cordon de bon cuir. Son poids est le seul ami de certains.",
    "Heavy paper, a heavy seal. A debt someone important promised to repay.": "Papier épais, sceau pesant. Une dette qu'un personnage important a promis d'honorer.",
    "Deep crimson and almost hot to hold. Wounds close while you're still swallowing.": "D'un pourpre profond, presque brûlante en main. Les plaies se ferment avant la dernière gorgée.",
    "Bitter herbs, river clay and a healer's patience, sealed in a tin.": "Herbes amères, argile de rivière et patience de guérisseur, scellées dans une boîte en fer.",
    "The oldest trick there is. It still works.": "Le plus vieux tour qui soit. Il marche encore.",
    "Three corked flasks and the knowledge to fill them. Keep them away from the campfire.": "Trois fioles bouchées et le savoir pour les remplir. À tenir loin du feu de camp.",
    # aspects
    "It came from someone who never learned to walk, only to bound.": "Il vient de quelqu'un qui n'a jamais appris à marcher, seulement à bondir.",
    "Taken from a taster at a poisoner's court. Nothing in a cup ever hurt them again.": "Pris à un goûteur d'une cour d'empoisonneurs. Plus rien dans une coupe ne lui a jamais fait de mal.",
    "The resolve of someone who stared down terrors and did not blink.": "La résolution de quelqu'un qui a toisé l'épouvante sans ciller.",
    "A mind that sees through mist and mirrors. Illusions slide off it like rain.": "Un esprit qui voit à travers brumes et miroirs. Les illusions glissent dessus comme la pluie.",
    "A soldier's reflex: when one foe falls, the blade is already moving to the next.": "Un réflexe de soldat : quand un ennemi tombe, la lame file déjà vers le suivant.",
    "A hunter's breath, held between heartbeats, until the arrow flies.": "Le souffle d'un chasseur, retenu entre deux battements, jusqu'à ce que la flèche parte.",
    "Shields aren't only for hiding behind. A veteran knows the rim is a weapon too.": "Un bouclier ne sert pas qu'à se cacher. Un vétéran sait que son rebord est aussi une arme.",
    "A warrior's chant that rose with every strike, until the whole line sang along.": "Le chant d'un guerrier, qui montait à chaque coup jusqu'à ce que toute la ligne le reprenne.",
    "One voice that turns a rout into a charge. It remembers every battlefield it saved.": "Une seule voix qui change une déroute en charge. Elle se souvient de chaque champ de bataille qu'elle a sauvé.",
    "Learned in the front rank, where your shield guards the friend beside you.": "Appris au premier rang, là où votre bouclier garde l'ami à vos côtés.",
    "The habits of someone who never used a door if a window would do.": "Les habitudes de quelqu'un qui n'a jamais pris une porte quand une fenêtre suffisait.",
    "A name that opens doors. Everyone has heard the stories, true or not.": "Un nom qui ouvre les portes. Tout le monde connaît les histoires, vraies ou non.",
    "Salt in the blood, knots in the fingers, and a tavern story for every port.": "Du sel dans le sang, des nœuds dans les doigts, et une histoire de taverne pour chaque port.",
    "Taught by gutters and hunger. Nobody sees a child in the crowd until their purse is gone.": "Formé par le caniveau et la faim. Personne ne voit l'enfant dans la foule avant que sa bourse ait disparu.",
    "Broken twigs, bent grass, the hush before a deer bolts. The wild speaks; this one listens.": "Brindilles cassées, herbe couchée, le silence avant qu'un cerf ne détale. La nature parle ; celui-ci écoute.",
    "Steady hands and a calm voice, honed over a thousand sickbeds.": "Des mains sûres et une voix calme, affûtées au chevet de mille malades.",
    "Years behind the bar teach a lot: who lies, who drinks, who will start the fight.": "Des années derrière le comptoir en apprennent beaucoup : qui ment, qui boit, qui lancera la bagarre.",
    "The forge's wisdom: the weight of iron, the price of iron, where iron breaks.": "La sagesse de la forge : le poids du fer, le prix du fer, l'endroit où le fer se brise.",
    "Thin air and sheer cliffs were a home to them. The mountain never won.": "L'air rare et les falaises abruptes étaient sa maison. La montagne n'a jamais gagné.",
    "A blade master's rhythm: a feint and a cut, so fast they sound like one blow.": "Le rythme d'un maître d'armes : une feinte et une taille, si rapides qu'on n'entend qu'un coup.",
    "When others lie down, this one gets back up. Pain is a problem for later.": "Quand les autres se couchent, celui-ci se relève. La douleur, ce sera pour plus tard.",
    "Lean, ropy strength. There was never much meat on them, but they never tired.": "Une force sèche et noueuse. Jamais bien épais, jamais fatigué.",
    "Eyes from something that lived in the dark. Shadows turn to shapes, then to detail.": "Les yeux d'une chose qui vivait dans le noir. Les ombres deviennent des formes, puis des détails.",
    "Hard years selling a blade to whoever paid. You learn the price of everything, and of everyone.": "De dures années à vendre sa lame au plus offrant. On apprend le prix de tout, et de chacun.",
    "From a traveling troupe: flips, falls and a crowd that gasped every night.": "D'une troupe ambulante : saltos, chutes et une foule qui retenait son souffle chaque soir.",
    "Taken from a wolf. It knows the moment a friend has the prey, and when to pull it down.": "Pris à un loup. Il sait quand un compagnon tient la proie, et quand la faire tomber.",
    "A knack for being somewhere else when the blow arrives.": "Un don pour être ailleurs quand le coup arrive.",
    "Herb lore and old charms from a cottage at the edge of the woods.": "Science des herbes et vieux charmes d'une chaumière à l'orée du bois.",
    "The wide arc of a giant's swing. Everyone in reach learns to fear it.": "Le large arc d'un coup de géant. Tous ceux à portée apprennent à le craindre.",
    "Something that would not stay down. Death had to ask twice, and it never asked again.": "Quelque chose qui refusait de rester à terre. La mort a dû demander deux fois, et n'a plus jamais redemandé.",
    "Short-lived, stubborn and everywhere. Whatever they lack, they make up for by trying again.": "Brève vie, tête dure, et partout. Ce qui leur manque, ils le compensent en réessayant.",
    "Long years in a slender frame, and eyes that never quite lost the starlight.": "De longues années dans un corps élancé, et des yeux qui n'ont jamais tout à fait perdu la lueur des étoiles.",
    "Stone-born and slow to fall. Their blood shrugs off what would fell a lesser body.": "Né de la pierre et lent à tomber. Ce sang encaisse ce qui abattrait un corps plus faible.",
    "Small, cheerful and impossibly lucky. Fate seems to like them, and nobody knows why.": "Petits, joyeux et d'une chance insolente. Le destin semble les aimer, et personne ne sait pourquoi.",
    "Made for war and for the long march after it. The dark holds no secrets from those eyes.": "Fait pour la guerre et la longue marche qui suit. Le noir n'a pas de secrets pour ces yeux.",
    "Drilled from birth: a good soldier, a good scout, a good officer. Discipline is in the bones.": "Dressé dès la naissance : bon soldat, bon éclaireur, bon officier. La discipline est dans les os.",
    # deck covers
    "Spells copied in a careful hand, the margins full of warnings. The ink still smells of ozone.": "Des sorts recopiés d'une main soigneuse, les marges pleines d'avertissements. L'encre sent encore l'ozone.",
    "Songs gathered at roadside fires and in tavern corners, sung by someone who never stayed long.": "Des chansons glanées aux feux de route et aux coins des tavernes, chantées par quelqu'un qui ne restait jamais longtemps.",
    "Prayers learned by heart in a quiet temple. The faith came with them.": "Des prières apprises par cœur dans un temple paisible. La foi est venue avec.",
    "The memory of fur, feather and claw. The body knows these shapes, and longs for them.": "Le souvenir du poil, de la plume et de la griffe. Le corps connaît ces formes, et s'en languit.",
    # deck cards
    "The first spell every conjurer learns, and the one they burn their eyebrows with.": "Le premier sort de tout conjurateur, et celui avec lequel il se brûle les sourcils.",
    "An unseen hand for the jar on the high shelf, or the key on the guard's belt.": "Une main invisible pour le pot sur l'étagère du haut, ou la clé à la ceinture du garde.",
    "Darts of pure light that seek their mark. They rarely miss entirely.": "Des fléchettes de pure lumière qui cherchent leur cible. Elles la manquent rarement tout à fait.",
    "A shimmer of force, conjured in the instant before the blade lands.": "Un miroitement de force, invoqué l'instant avant que la lame ne frappe.",
    "Slick as an eel and twice as rude. Dignity is the first casualty.": "Glissant comme une anguille et deux fois plus grossier. La dignité est la première victime.",
    "A breath of silver mist, and you stand somewhere else.": "Un souffle de brume argentée, et vous voilà ailleurs.",
    "Thick, sticky strands fill the passage. Whatever is caught in it struggles in vain.": "D'épais fils collants emplissent le passage. Ce qui s'y prend se débat en vain.",
    "A well-timed insult can throw off any swing.": "Une insulte bien placée peut dévier n'importe quel coup.",
    "A marching song that puts steel in tired arms.": "Un chant de marche qui met de l'acier dans les bras las.",
    "A slow, steady beat. Feet planted, shields up, nobody runs.": "Un rythme lent et régulier. Pieds ancrés, boucliers levés, personne ne fuit.",
    "Mockery, sharp as a knife, right as the foe commits.": "Une moquerie, tranchante comme un couteau, à l'instant où l'ennemi s'engage.",
    "A calm word in the moment that matters.": "Un mot calme au moment qui compte.",
    "A lament for the foe's own funeral. Some listeners believe it.": "Une lamentation pour les propres funérailles de l'ennemi. Certains y croient.",
    "A verse about the heroes who got back up. The listener does too.": "Un couplet sur les héros qui se sont relevés. L'auditeur aussi se relève.",
    "A quiet word of faith that steadies hand and mind.": "Un mot de foi murmuré qui affermit la main et l'esprit.",
    "A blessing that sends allies forward with surer hands.": "Une bénédiction qui pousse les alliés en avant d'une main plus sûre.",
    "A curse that makes every blow of the enemy hesitate.": "Une malédiction qui fait hésiter chaque coup de l'ennemi.",
    "The threads of chance, plucked and pulled. The dice tumble again.": "Les fils du hasard, pincés et tirés. Les dés roulent à nouveau.",
    "A single holy word, called across the battlefield. Wounds answer.": "Un seul mot sacré, lancé à travers le champ de bataille. Les plaies répondent.",
    "Hands laid on the wound; warmth spreads, and the flesh knits.": "Des mains posées sur la plaie ; la chaleur se répand, et la chair se referme.",
    "Wind under wings, the world far below, every mouse in the field plain to see.": "Le vent sous les ailes, le monde loin en dessous, chaque souris du champ bien visible.",
    "Four swift legs and a nose that reads the forest like a book.": "Quatre pattes rapides et un museau qui lit la forêt comme un livre.",
    "Green moss pressed into the wound. The forest remembers how to heal.": "De la mousse verte pressée dans la plaie. La forêt se souvient de comment guérir.",
    "Thick fur, a heavy hide and claws like knives. Few things argue with a bear.": "Une fourrure épaisse, un cuir lourd et des griffes comme des couteaux. Peu de choses discutent avec un ours.",
}

# Slot frames (base_set.FRAMES): name, swap time, reminder
FRAME_TEXT = {
    "Armor": "Armure", "Hand": "Main", "Jewelry": "Bijou", "Item": "Objet", "Aspect": "Aspect",
    "Third Hand": "Troisième Main", "Second Jewel": "Second Bijou", "Great Backpack": "Grand Sac à dos", "Shard": "Éclat",
    "Swap: 10 minutes": "Échange : 10 minutes", "Swap: free interaction": "Échange : interaction gratuite",
    "Swap: free, once per turn": "Échange : gratuit, 1 fois par tour", "Swap: free · Spellbook: 1 action": "Échange : gratuit · Livre : 1 action",
    "Swap: long rest": "Échange : repos long", "Pack (3 at most) or Party Stash": "Sac (3 au plus) ou Réserve",
    "Empty: **+10 ft Speed**.": "Vide : **+3 m de Vitesse**.",
    "One Weapon, Shield or Instrument.": "Une Arme, un Bouclier ou un Instrument.",
    "Empty: grapple, or hold a Spellbook to cast.": "Vide : empoigner, ou tenir un Livre de sorts pour lancer.",
    "Rings, amulets, circlets, cloaks, gloves, boots.": "Anneaux, amulettes, diadèmes, capes, gants, bottes.",
    "A Spellbook, a Recipe, a Purse, or up to 3 identical Consumables.": "Un Livre de sorts, une Recette, une Bourse, ou jusqu'à 3 Consommables identiques.",
    "A Trait, Technique, Knack, Divine, Glamour or Nature.": "Un Trait, une Technique, un Savoir-faire, un Divin, un Glamour ou une Nature.",
    "Extra Gear Slot: a spectral arm, a familiar, a living tail.": "Emplacement de Matériel supplémentaire : un bras spectral, un familier, une queue vivante.",
    "Never lost, traded or stored.": "Jamais perdu, échangé ni rangé.", "Extra Gear Slot.": "Emplacement de Matériel supplémentaire.",
    "Holds one Aspect, or nothing.": "Contient un Aspect, ou rien.",
    "**Capture:** 1 action · **Absorb:** long rest · **Release:** free": "**Capturer :** 1 action · **Absorber :** repos long · **Libérer :** gratuit",
}

STARTER_KEYS = {"Armor": "Armure", "Hands": "Mains", "Jewelry": "Bijou", "Items": "Objets", "Aspects": "Aspects"}


def ability_words(s):
    """STR / WIL → FOR / VOL wherever they stand as words."""
    return re.sub(r"\b(STR|WIL)\b", lambda m: ABBR[m[1]], s)


def text(t, missing):
    """One paragraph of card text in French (generated weapon, Knack and Wound lines are rebuilt)."""
    if t in TEXT:
        return TEXT[t]
    m = re.fullmatch(r"([+−-]\d+) to hit, (.+?) \+ ((?:STR|DEX|INT|WIL)(?: or (?:STR|DEX|INT|WIL))*) Physical\.(?: (.*))?", t)
    if m:
        abil = " ou ".join(ABBR[a] for a in m[3].split(" or "))
        rest = f" {text(m[4], missing)}" if m[4] else ""
        return f"{m[1]} au toucher, {m[2]} + {abil} Physique.{rest}"
    m = re.fullmatch(r"(\+\d) on checks to (.+)\.", t)
    if m and m[2] in ACTIVITIES:
        return f"{m[1]} aux tests pour {ACTIVITIES[m[2]]}."
    m = re.fullmatch(r"Blocks one of your \*\*(\w+) Slots\*\* until it heals\.", t)
    if m:
        slot = {"Hand": "Main", "Jewelry": "Bijou", "Item": "Objet"}[m[1]]
        return f"Bloque l'un de vos **Emplacements de {slot}** jusqu'à sa guérison."
    missing.append(t)
    return t


def localize(bs, foes):
    """Turn the base set and the foe cards French, in place. Each card keeps its English name in "key"."""
    missing = []

    def name(n):
        if n not in NAMES:
            missing.append(n)
        return NAMES.get(n, n)

    def card(c):
        c["key"] = c["name"]
        c["name"] = name(c["name"])
        c["text"] = [text(t, missing) for t in c["text"]]
        try:
            c["kw"] = keywords(c["kw"])
        except KeyError as e:
            missing.append(f"keyword {e}")
        if c.get("lore"):
            if c["lore"] in LORE:
                c["lore"] = LORE[c["lore"]]
            else:
                missing.append(c["lore"])

    for c in bs.CARDS + bs.WOUNDS:
        card(c)
    for d in bs.DECKS:
        for p in d["cards"]:
            card(p)
            p["level"] = LEVELS[p["level"]]
    bs.FRAMES[:] = [(k, FRAME_TEXT[n], FRAME_TEXT[s], [FRAME_TEXT[r] for r in rem], cnt) for k, n, s, rem, cnt in bs.FRAMES]
    starter = {STARTER_KEYS[k]: [NAMES[n] for n in v] for k, v in bs.STARTER_LIST.items()}
    bs.STARTER_LIST.clear()
    bs.STARTER_LIST.update(starter)
    for f in foes.FOES:
        f["own"] = [text(t, missing) for t in f["own"]]
        name(f["name"])
    if missing:
        raise SystemExit("Untranslated (cards/fr.py):\n  " + "\n  ".join(dict.fromkeys(missing)))
