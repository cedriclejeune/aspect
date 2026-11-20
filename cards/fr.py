"""French translation of the base set (cards/base_set.py) and the foe cards (cards/foes.py).

tools/build_cards.py --lang fr calls localize() after importing both: every card keeps its English name in
c["key"] (drawings in rules/art/ and the foe cards look cards up by it) and gets its French name, text, keywords
and lore. A missing translation stops the build with the list of untranslated strings.
Distances: 5 ft = 2 m (1 square = 2 m). Terms follow rules/fr/GLOSSAIRE.md.
"""
import re

ABBR = {"STR": "FOR", "DEX": "AGI", "INT": "INT", "WIL": "VOL"}

NAMES = {
    # Callings
    "Duelist": "Duelliste", "Templar": "Templier", "Spellblade": "Lame-mage", "Infiltrator": "Infiltrateur",
    "Performer": "Artiste", "Sage": "Sage", "Brawler": "Bagarreur", "Patriot": "Patriote", "Tactician": "Tacticien",
    "Ranger": "Rôdeur", "Trickster": "Filou", "Hermit": "Ermite",
    # armor and hands
    "Leather": "Cuir", "Mail": "Mailles", "Plate": "Plates", "Shield": "Bouclier", "Dagger": "Dague",
    "Shortsword": "Épée courte", "Handaxe": "Hachette", "Finesse Blade": "Lame fine", "Longsword": "Épée longue",
    "Battleaxe": "Hache d'armes", "Greatsword": "Épée à deux mains", "Glaive": "Glaive sur lance", "Longbow": "Arc long",
    "Sling": "Fronde", "Javelins": "Javelots", "Spellguard Staff": "Bâton de garde-sort",
    "Traveler's Lute": "Luth du voyageur", "Greatclub": "Massue", "Gladius": "Gladius", "Boarspear": "Lance de chasse",
    "Pilum": "Pilum", "Shortbow": "Arc court", "Greataxe": "Grande hache",
    "Fine Bow": "Arc composite", "Wand": "Baguette", "Hide": "Peaux", "Studded Leather": "Cuir clouté",
    "Whip": "Fouet", "Hand Crossbow": "Arbalète de poing", "Crossbow": "Arbalète", "Druid's Staff": "Bâton druidique",
    # jewelry and items
    "Ring of Warding": "Anneau de protection", "Guild Signet": "Chevalière de guilde",
    "Runestone Bandolier": "Bandoulière runique", "Holy Amulet": "Amulette sacrée",
    "Boots of the Long Stride": "Bottes de grande foulée", "Ring of Sparks": "Anneau d'étincelles",
    "Dancer's Bells": "Grelots de danseur", "Potion of Healing": "Potion de soins", "Coin Pouch": "Bourse à cordon",
    "Writ of Favor": "Lettre d'introduction", "Greater Potion of Healing": "Potion de soins supérieurs",
    "Restorative Salve": "Onguent réparateur", "Pocket Sand": "Sable de poche",
    "Alchemist's Fire Recipe": "Recette de feu grégeois", "Druid's Totem": "Totem druidique",
    "Arcane Crystal": "Cristal arcanique", "Healer's Kit": "Trousse de soins",
    # Runes
    "Springheel": "Bond", "Stone Blood": "Sang de pierre", "Iron Will": "Volonté de fer",
    "Clear Mind": "Esprit clair", "Cleave": "Enchaînement", "Steady Aim": "Visée juste",
    "Shield Bash": "Coup de bouclier", "Battle Hymn": "Hymne de bataille", "Rallying Cry": "Cri de ralliement",
    "Shield Wall": "Mur de boucliers", "Larceny": "Larcin", "Minstrel": "Ménestrel", "Navigation": "Navigation",
    "Backstreets": "Ruelles", "Hunt": "Traque", "Healing": "Guérison", "Tavern": "Taverne",
    "Forge": "Forge", "Peaks": "Cimes", "Twin Strike": "Double frappe", "Second Wind": "Second souffle",
    "Sinew": "Nerf", "Night Eyes": "Yeux de nuit", "Bravado": "Bravade", "Tumbling": "Voltige",
    "Wolfpack": "Meute", "Herbalist": "Herboriste",
    "Sweeping Blow": "Coup balayant", "Defiance": "Acharnement", "Grit": "Ténacité",
    "Dusk Eyes": "Yeux de crépuscule", "Bedrock": "Socle", "Luck": "Chance",
    "Campaign": "Campagne", "Discipline": "Discipline",
    "Archery": "Archerie", "Bulwark": "Rempart", "Dueling": "Duel", "Great Weapons": "Armes lourdes",
    "Quick Throw": "Lancer vif", "Rage": "Rage", "Cunning": "Ruse", "Unarmored Guard": "Garde sans armure",
    "Martial Arts": "Arts martiaux", "Expertise": "Expertise", "Arcane Recovery": "Recouvrement arcanique",
    "Library": "Bibliothèque", "Court": "Cour", "Frontier": "Contrées sauvages", "Deceit": "Duperie",
    "Asceticism": "Ascèse",
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
    "Acolyte's Litany": "Litanie de l'acolyte", "Wildheart's Instinct": "Instinct du cœur sauvage",
    "Fire Bolt": "Trait de feu", "Mage Hand": "Main de mage", "Magic Missile": "Projectile magique",
    "Grease": "Graisse", "Misty Step": "Foulée brumeuse", "Web": "Toile d'araignée", "Jeer": "Raillerie",
    "Rally": "Ralliement", "Hold the Line": "Tenez la ligne", "Cutting Words": "Réplique cinglante",
    "Steady Now": "Du calme", "Dread": "Effroi", "Rousing Verse": "Vers exaltant", "Guidance": "Assistance",
    "Bless": "Bénédiction", "Bane": "Fléau", "Twist Fate": "Altération du destin", "Healing Word": "Mot de guérison",
    "Cure Wounds": "Soins", "Hawk": "Faucon", "Wolf": "Loup", "Mossbalm": "Baume de mousse", "Bear": "Ours",
    "Evoker's Book": "Livre de l'évocateur", "Abjurer's Book": "Livre de l'abjurateur",
    "Illusionist's Book": "Livre de l'illusionniste", "Enchanter's Book": "Livre de l'enchanteur",
    "Occultist's Pact": "Pacte de l'occultiste",
    "Ray of Frost": "Rayon de givre", "Shocking Grasp": "Poigne électrique", "Burning Hands": "Mains brûlantes",
    "Thunderwave": "Vague tonnante", "Chromatic Orb": "Orbe chromatique", "Scorching Ray": "Rayon ardent",
    "Shatter": "Fracassement", "Blade Ward": "Protection contre les lames", "Mending": "Réparation",
    "Mage Armor": "Armure de mage", "Absorb Elements": "Absorption des éléments",
    "Protection from Evil": "Protection contre le mal", "Aid": "Aide", "Arcane Lock": "Verrou magique",
    "Minor Illusion": "Illusion mineure", "Disguise Self": "Déguisement", "Silent Image": "Image silencieuse",
    "Color Spray": "Couleurs dansantes", "Mirror Image": "Image miroir", "Invisibility": "Invisibilité",
    "Mind Sliver": "Éclat psychique", "Heroism": "Héroïsme", "Sleep": "Sommeil", "Charm Person": "Charme-personne", "Compel": "Injonction",
    "Hideous Laughter": "Fou rire", "Hold Person": "Immobilisation de personne",
    "Necromancer's Book": "Livre du nécromancien", "Chill Touch": "Contact glacial", "Toll the Dead": "Glas",
    "Raise Dead": "Relever les morts", "False Life": "Simulacre de vie", "Ray of Sickness": "Rayon empoisonné",
    "Vampiric Touch": "Caresse du vampire", "Blindness": "Cécité",
    "Eldritch Blast": "Décharge occulte", "Enfeeble": "Affaiblissement", "Hellish Rebuke": "Représailles infernales",
    "Hex": "Maléfice",
    # foes
    "Bandit": "Bandit", "Bandit Archer": "Archer bandit", "Goblin": "Gobelin", "Cultist": "Cultiste",
    "Legionary": "Légionnaire", "Bandit Captain": "Capitaine bandit", "Ogre": "Ogre", "Ogre Chieftain": "Chef ogre",
    "Guard": "Garde", "Scout": "Éclaireur", "Mage": "Mage", "Orc": "Orque", "Hobgoblin": "Hobgobelin",
    "Skeleton": "Squelette", "Zombie": "Zombie", "Kobold": "Kobold", "Giant Rat": "Rat géant",
    "Giant Spider": "Araignée géante", "Troll": "Troll",
    "Stirge": "Stirge", "Giant Centipede": "Mille-pattes géant", "Boar": "Sanglier", "Flying Sword": "Épée volante",
    "Goblin Boss": "Chef gobelin", "Gnoll": "Gnoll", "Shadow": "Ombre", "Dire Wolf": "Loup sanguinaire", "Ghoul": "Goule",
    "Bugbear": "Gobelours", "Animated Armor": "Armure animée", "Harpy": "Harpie", "Brown Bear": "Ours brun",
    "Gelatinous Cube": "Cube gélatineux", "Owlbear": "Ours-hibou",
    # Rank II WIL decks (from festive-hypatia)
    "Herald's Repertoire": 'Répertoire du héraut',
    "Vicar's Litany": 'Litanie du vicaire',
    "Prowler's Instinct": 'Instinct du maraudeur',
    "Supplicant's Pact": 'Pacte du suppliant',
    'Heckle': 'Huées',
    'Unbowed': 'Insoumis',
    'Rebuttal': 'Riposte verbale',
    'Rout': 'Déroute',
    'Mending Air': 'Air apaisant',
    'Ill Omen': 'Mauvais présage',
    'Providence': 'Providence',
    'Kneel': 'À genoux',
    'Zeal': 'Ferveur',
    'Restoring Touch': 'Toucher réparateur',
    'Chorus of Mercy': 'Chœur de miséricorde',
    'Spider': 'Araignée',
    'Panther': 'Panthère',
    'Sapblood': 'Sang de sève',
    'Aurochs': 'Aurochs',
    'Wild Growth': 'Croissance sauvage',
    'Hex Bolt': 'Trait maudit',
    'Malediction': 'Malédiction',
    'Torment': 'Tourment',
    'Wither': 'Flétrissure',
    'Eclipse': 'Éclipse',
}

LEVELS = {"Cantrip": "Tour de magie", "1st": "1er", "2nd": "2e", "Anthem": "Hymne", "Dirge": "Complainte",
          "Cue": "Réplique", "Mend": "Soin", "Form": "Forme"}

# keywords, one at a time ("Range 150/600" and "Thrown 20/60" convert their feet)
KEYWORDS = {
    "Calling": "Vocation", "Armor": "Armure", "Weapon": "Arme", "Shield": "Bouclier", "Instrument": "Instrument",
    "Focus": "Focaliseur", "Jewelry": "Bijou", "Consumable": "Consommable", "Container": "Contenant", "Recipe": "Recette",
    "3 flasks": "3 fioles", "Spellbook": "Livre de sorts", "Spell": "Sort", "Cantrip": "Tour de magie",
    "Trait": "Trait", "Technique": "Technique", "Domain": "Domaine", "Divine": "Divin", "Glamour": "Glamour",
    "Nature": "Nature", "Pact": "Pacte", "Anthem": "Hymne", "Dirge": "Complainte", "Cue": "Réplique", "Mend": "Soin", "Form": "Forme",
    "Wound": "Blessure", "Loading": "Chargement", "Targets STR": "Vise FOR", "Targets INT": "Vise INT", "Targets WIL": "Vise VOL",
    "Subdue": "Emprise", "Unconscious": "Inconscient", "Charmed": "Charmé", "Incapacitated": "Neutralisé", "Stunned": "Étourdi",
    "Blinded": "Aveuglé", "Invisible": "Invisible", "Duration 8 hours": "Durée 8 heures", "Duration 10 minutes": "Durée 10 minutes",
    "Duration 1 hour": "Durée 1 heure", "Crippling": "Invalidante", "Hand": "Main", "Item": "Objet", "Heavy": "Lourde",
    "Light": "Légère", "Reach": "Allonge", "Two-Handed": "Deux mains", "Versatile (1d10)": "Polyvalente (1d10)",
    "Versatile (1d8)": "Polyvalente (1d8)", "Brutal": "Brutale", "Crushing": "Écrasante", "Flurry": "Rafale", "Loading": "Chargement",
    "Restrained": "Entravé", "Targets DEX": "Vise AGI", "Duration 1 minute": "Durée 1 minute",
    "Duration 1 round": "Durée 1 round", "Gold": "Or", "Foe": "Adversaire", "Boss": "Boss", "Leader": "Meneur",
    "Tiny": "Très petit", "Small": "Petit", "Medium": "Moyen", "Large": "Grand",
}


def feet(n):
    """30 → "12", 35 → "14" (5 ft = 2 m)."""
    return f"{round(float(n) * 0.4, 2):g}".replace(".", ",")


def keyword(k):
    if k in KEYWORDS:
        return KEYWORDS[k]
    m = re.fullmatch(r"(Range|Thrown|Darkvision|Cube|Sphere|Noisy) ([\d/]+)", k)
    if m:
        word = {"Range": "Portée", "Thrown": "Lancer", "Darkvision": "Vision nocturne", "Cube": "Cube", "Sphere": "Sphère",
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
    "recall lore, notice, search or haggle": "se souvenir de connaissances, remarquer, fouiller ou marchander",
    "persuade, read intentions, recall lore or perform": "persuader, deviner les intentions, se souvenir de connaissances ou se produire",
    "track, navigate, endure or notice": "pister, s'orienter, endurer ou remarquer",
    "deceive, hide, pick pockets or perform": "tromper, se cacher, faire les poches ou se produire",
    "endure, notice, treat wounds or read intentions": "endurer, remarquer, soigner les blessures ou deviner les intentions",
}

TEXT = {
    # Calling perks
    "**Battle Caster:** a weapon you hold counts as an empty Hand for casting from a Spellbook.":
        "**Incantateur de guerre :** une arme que vous tenez compte comme une Main vide pour lancer des sorts depuis un Livre de sorts.",
    "**Footwork:** once per turn, after you hit with a melee attack, move 5 ft × ½ DEX. This movement doesn't provoke opportunity attacks.":
        "**Jeu de jambes :** une fois par tour, après avoir touché au corps à corps, déplacez-vous de 2 m × ½ AGI. Ce déplacement ne provoque pas d'attaque d'opportunité.",
    "**Riposte (½ STR/S.R.):** reaction, when a melee attack misses you: make one melee weapon attack against the attacker.":
        "**Riposte (½ FOR/C.R.) :** réaction, quand une attaque au corps à corps vous rate : faites une attaque d'arme au corps à corps contre l'attaquant.",
    "**Oath (½ WIL/S.R.):** reaction, when an attack hits an ally within 5 ft: you take its damage instead, reduced by 2 × STR.":
        "**Serment (½ VOL/C.R.) :** réaction, quand une attaque touche un allié à 2 m ou moins : vous subissez ses dégâts à sa place, réduits de 2 × FOR.",
    "**Spell Strike (½ STR/S.R.):** when you hit with a melee weapon attack: +INT damage.":
        "**Frappe ensorcelée (½ FOR/C.R.) :** quand vous touchez avec une attaque d'arme au corps à corps : +INT dégâts.",
    "**Unseen:** your checks to sneak, pick locks and spot traps add both DEX and INT.":
        "**Inaperçu :** vos tests pour se faufiler, crocheter les serrures et repérer les pièges ajoutent l'AGI et l'INT.",
    "**Presence:** your checks to perform, persuade and deceive add both DEX and WIL.":
        "**Présence :** vos tests pour se produire, persuader et tromper ajoutent l'AGI et la VOL.",
    "**Weak Spot (½ WIL/L.R.):** when you cast a spell at a single creature, it targets the creature's lowest Defense instead of the one the spell names, with +½ INT to hit. Your checks to recall lore add both INT and WIL.":
        "**Point faible (½ VOL/L.R.) :** quand vous lancez un sort contre une seule créature, il vise sa Défense la plus basse au lieu de celle que nomme le sort, avec +½ INT au toucher. Vos tests pour se souvenir de connaissances ajoutent l'INT et la VOL.",
    "**Scrapper:** +STR to hit with Grapples and Shoves.":
        "**Teigneux :** +FOR au toucher pour Empoigner et Bousculer.",
    "**Slip Free:** your Escape attacks add 2 × DEX instead of STR or DEX.":
        "**Dégagement :** vos attaques pour S'échapper ajoutent 2 × AGI au lieu de FOR ou AGI.",
    "**Righteous Fury (½ WIL/S.R.):** when you hit with a weapon attack: +½ STR d6 Radiant damage.":
        "**Juste colère (½ VOL/C.R.) :** quand vous touchez avec une attaque d'arme : +½ FOR d6 dégâts Radiants.",
    "**Command (½ STR/S.R.):** action. An ally within 30 ft who can hear you takes the Attack action at once, with +INT to hit.":
        "**Commandement (½ FOR/C.R.) :** action. Un allié à 12 m ou moins qui peut vous entendre effectue aussitôt l'action Attaque, avec +INT au toucher.",
    "**Quarry (½ INT/S.R.):** when you hit a creature with a ranged attack, it's marked: you and your allies have +½ DEX on attacks against it until the start of your next turn.":
        "**Proie (½ INT/C.R.) :** quand vous touchez une créature avec une attaque à distance, elle est marquée : vous et vos alliés avez +½ AGI aux attaques contre elle jusqu'au début de votre prochain tour.",
    "**Sure Thing:** on your checks to sneak, pick locks, pick pockets and disarm traps, a d20 that shows less than 10 counts as a 10. When you hit a creature that can't see you: +½ DEX or ½ WIL d6 damage, whichever is higher.":
        "**Coup sûr :** pour vos tests pour se faufiler, crocheter les serrures, faire les poches et désamorcer les pièges, un d20 qui affiche moins de 10 compte comme un 10. Quand vous touchez une créature qui ne vous voit pas : +½ AGI ou ½ VOL d6 dégâts, la plus haute des deux.",
    "**Omen:** when you finish a long rest, roll ½ WIL d20 and set them aside. Before a creature within 10 ft × INT makes an attack roll or a check, you may replace its d20 with one of them, which is spent. Dice left over are lost at your next long rest. Your checks to forage and endure add both INT and WIL.":
        "**Présage :** à la fin d'un long repos, lancez ½ VOL d20 et mettez-les de côté. Avant qu'une créature à 4 m × INT ou moins fasse un jet d'attaque ou un test, vous pouvez remplacer son d20 par l'un d'eux, qui est dépensé. Les dés restants sont perdus à votre long repos suivant. Vos tests pour cueillir et endurer ajoutent l'INT et la VOL.",
    # hands
    "Takes one Hand.": "Occupe une Main.",
    "**Sap:** when you hit, the target has −2 on its next attack roll before the start of your next turn.":
        "**Saignée :** quand vous touchez, la cible a −2 à son prochain jet d'attaque avant le début de votre prochain tour.",
    "**Close Shot:** an enemy within 5 ft doesn't give you disadvantage on your attacks with it.":
        "**Tir rapproché :** un ennemi à 2 m ou moins ne vous donne pas de désavantage à vos attaques avec lui.",
    "+2 to your spell attacks and WIL deck attacks.":
        "+2 à vos attaques de sort et de pouvoir.",
    "1 extra Resolve (short rest).": "1 Ardeur supplémentaire (court repos).",
    "Your Anthems reach 60 ft instead of 30 ft.": "Vos Hymnes portent à 24 m au lieu de 12 m.",
    "**Crushing:** on a critical hit, the target is knocked Prone.": "**Écrasement :** sur un coup critique, la cible est mise À terre.",
    "**Close Order:** +1d4 damage while an ally is engaged with the same creature.":
        "**Ordre serré :** +1d4 dégâts tant qu'un allié est engagé avec la même créature.",
    "**Brace:** your opportunity attacks with it deal +1d8 damage.": "**Tenez bon !** Vos attaques d'opportunité avec lui infligent +1d8 dégâts.",
    "**Pierce:** on a hit, a Shield the target holds gives no bonus until it spends an action to pull the pilum free.":
        "**Perforation :** si l'attaque touche, un Bouclier que tient la cible ne donne plus de bonus jusqu'à ce qu'elle dépense une action pour arracher le pilum.",
    # jewelry
    "**Reaction (2/S.R.)**, when an attack hits you: +2 to the targeted Defense against that attack, possibly turning it into a miss.":
        "**Réaction (2/C.R.)**, quand une attaque vous touche : +2 à la Défense visée contre cette attaque, ce qui peut la transformer en échec.",
    "**Action (1/L.R.)**, in a settlement where the guild operates: a contact finds you within 1 hour. They share one fact the guild would know, or hide you for a night.":
        "**Action (1/L.R.)**, dans une localité où la guilde opère : un contact vous trouve dans l'heure. Il vous révèle un fait que la guilde connaîtrait, ou vous cache pour une nuit.",
    "While it's in your Pack, your Pack holds up to 5 Runestones instead of 3.":
        "Tant qu'elle est dans votre Sac, il contient jusqu'à 5 Pierres runiques au lieu de 3.",
    "Your Cues reach 90 ft instead of 60 ft.": "Vos Répliques portent à 36 m au lieu de 24 m.",
    "**Reaction (1/S.R.):** Move.": "**Réaction (1/C.R.) :** Déplacement.",
    "**Reaction (1/S.R.)**, when a creature within 5 ft hits you: it takes 2d6 Lightning.":
        "**Réaction (1/C.R.)**, quand une créature à 2 m ou moins vous touche : elle subit 2d6 Foudre.",
    "Your Dirges reach 90 ft instead of 60 ft.": "Vos Complaintes portent à 36 m au lieu de 24 m.",
    "1 extra Resolve (short rest). Your Mends restore 2 extra HP.": "1 Ardeur supplémentaire (court repos). Vos Soins rendent 2 PV de plus.",
    "When you shift into a Form, it gains 2 temporary HP.": "Quand vous prenez une Forme, elle gagne 2 PV temporaires.",
    "**Action:** tend a creature within 5 ft. It regains 1d4 HP.": "**Action :** soignez une créature à 2 m ou moins. Elle récupère 1d4 PV.",
    # items
    "**Action:** drink it, or give it to a creature within 5 ft. It regains 2d4 + 2 HP.":
        "**Action :** buvez-la, ou donnez-la à une créature à 2 m ou moins. Elle récupère 2d4 + 2 PV.",
    "Holds up to **100 gp**.": "Contient jusqu'à **100 po**.",
    "A sealed letter from a noble house, a guild or a temple. Show it to one of its members: they grant one reasonable request (shelter, an audience, safe passage, a loan up to 100 gp).":
        "Une lettre scellée d'une maison noble, d'une guilde ou d'un temple. Montrez-la à l'un de ses membres : il accède à une demande raisonnable (un abri, une audience, un sauf-conduit, un prêt jusqu'à 100 po).",
    "**Action:** drink it, or give it to a creature within 5 ft. It regains 4d4 + 4 HP.":
        "**Action :** buvez-la, ou donnez-la à une créature à 2 m ou moins. Elle récupère 4d4 + 4 PV.",
    "**Action:** spread it on a creature within 5 ft. Heal one of its Wounds.":
        "**Action :** étalez-le sur une créature à 2 m ou moins. Guérissez l'une de ses Blessures.",
    "**Reaction:** throw it at a creature within 5 ft. Attack (DEX or WIL + 2) against its DEX Defense: on a hit, it has −2 on attacks until the end of its next turn.":
        "**Réaction :** lancez-le sur une créature à 2 m ou moins. Attaque (AGI ou VOL + 2) contre sa Défense d'AGI : si elle touche, la créature a −2 aux attaques jusqu'à la fin de son prochain tour.",
    "**Reaction:** throw a flask up to 30 ft. Make one attack (DEX or INT + 3) against the DEX Defense of each creature within 5 ft of the impact: 2d6 Fire on a hit, half on a miss.":
        "**Réaction :** lancez une fiole jusqu'à 12 m. Faites une attaque (AGI ou INT + 3) contre la Défense d'AGI de chaque créature à 2 m ou moins du point d'impact : 2d6 Feu si elle touche, la moitié en cas d'échec.",
    # Runes
    "Your jump distances are doubled, and you never need a running start.":
        "Vos distances de saut sont doublées, et vous n'avez jamais besoin d'élan.",
    "+2 STR Defense against poison and disease.": "+2 à la Défense de FOR contre le poison et la maladie.",
    "+2 WIL Defense against fear and mind control.": "+2 à la Défense de VOL contre la peur et le contrôle mental.",
    "+2 INT Defense against illusions and confusion.": "+2 à la Défense d'INT contre les illusions et la confusion.",
    "**1/S.R.**, when your melee attack drops a creature to 0 HP: make one melee attack against another creature within your reach.":
        "**1/C.R.**, quand votre attaque au corps à corps fait tomber une créature à 0 PV : faites une attaque au corps à corps contre une autre créature à votre allonge.",
    "**Reaction (2/S.R.):** your next ranged attack this turn has +2 to hit.":
        "**Réaction (2/C.R.) :** votre prochaine attaque à distance de ce tour a +2 au toucher.",
    "**Reaction (1/S.R.)**, when you take the Attack action while holding a Shield: Shove a creature within 5 ft.":
        "**Réaction (1/C.R.)**, quand vous effectuez l'action Attaque en tenant un Bouclier : Bousculez une créature à 2 m ou moins.",
    "**2/S.R.**, when you hit with a weapon attack: up to 3 allies within 30 ft who can hear you have +2 to STR and DEX Defense until the start of your next turn.":
        "**2/C.R.**, quand vous touchez avec une attaque d'arme : jusqu'à 3 alliés à 12 m ou moins qui peuvent vous entendre ont +2 aux Défenses de FOR et d'AGI jusqu'au début de votre prochain tour.",
    "*Rally* as a loose Anthem.": "*Ralliement* comme Hymne isolé.",
    "**Action (1/S.R.):** Duration 1 minute. Up to 3 allies within 30 ft have +2 on attacks.":
        "**Action (1/C.R.) :** Durée 1 minute. Jusqu'à 3 alliés à 12 m ou moins ont +2 aux attaques.",
    "**Reaction (1/S.R.)**, when an attack hits an ally within 5 ft while you hold a Shield: +2 to the targeted Defense against that attack, possibly turning it into a miss.":
        "**Réaction (1/C.R.)**, quand une attaque touche un allié à 2 m ou moins pendant que vous tenez un Bouclier : +2 à la Défense visée contre cette attaque, ce qui peut la transformer en échec.",
    "Once per turn, when you take the Attack action, make one extra attack.":
        "Une fois par tour, quand vous effectuez l'action Attaque, faites une attaque supplémentaire.",
    "**Action (1/S.R.):** regain 1d10 + 3 HP.": "**Action (1/C.R.) :** récupérez 1d10 + 3 PV.",
    "**1/S.R.**, when you hit a creature one of your allies is engaged with: it falls Prone.":
        "**1/C.R.**, quand vous touchez une créature avec laquelle l'un de vos alliés est engagé : elle tombe À terre.",
    "**Reaction (2/S.R.):** move up to half your Speed. This movement doesn't provoke opportunity attacks.":
        "**Réaction (2/C.R.) :** déplacez-vous jusqu'à la moitié de votre Vitesse. Ce déplacement ne provoque pas d'attaque d'opportunité.",
    "1 extra spell point (long rest).": "1 point de sort supplémentaire (long repos).",
    "+3 on checks to handle animals, recall lore, treat wounds or deceive.":
        "+3 aux tests pour dresser les animaux, se souvenir de connaissances, soigner les blessures ou tromper.",
    "+3 on checks to intimidate, endure, haggle or gather rumors.":
        "+3 aux tests pour intimider, endurer, marchander ou recueillir des rumeurs.",
    "+3 on checks to tumble, balance, jump or perform.":
        "+3 aux tests pour faire des acrobaties, garder l'équilibre, sauter ou se produire.",
    "**1/S.R.**, when you take the Attack action with a Heavy or Reach weapon: make one attack roll against each enemy within your reach instead. Half damage on a miss.":
        "**1/C.R.**, quand vous effectuez l'action Attaque avec une arme Lourde ou à Allonge : faites à la place un jet d'attaque contre chaque ennemi à votre allonge. Moitié des dégâts en cas d'échec.",
    "**1/S.R.**, when damage drops you to 0 HP without killing you outright: you drop to 1 HP instead.":
        "**1/C.R.**, quand des dégâts vous font tomber à 0 PV sans vous tuer sur le coup : vous tombez à 1 PV à la place.",
    "**Stubborn (1/S.R.):** when you fail a check, add +2 to that roll, possibly turning it into a success.":
        "**Têtu (1/C.R.) :** quand vous ratez un test, ajoutez +2 à ce jet, ce qui peut le transformer en réussite.",
    "+2 STR Defense against poison.": "+2 à la Défense de FOR contre le poison.",
    "+2 STR Defense against poison, Shoves and Grapples.": "+2 à la Défense de FOR contre le poison, Bousculer et Empoigner.",
    "**Lucky (1/S.R.):** when you roll a 1 on a d20, reroll it.": "**Veinard (1/C.R.) :** quand vous faites 1 sur un d20, relancez-le.",
    "Long range gives your ranged weapon attacks no disadvantage.": "La longue portée ne donne pas de désavantage à vos attaques d'arme à distance.",
    "+1 STR Defense while you wear Armor.": "+1 à la Défense de FOR tant que vous portez une Armure.",
    "While you hold a one-handed melee weapon and your other Hand is empty: +1 STR and DEX Defense against melee attacks.":
        "Tant que vous tenez une arme de corps à corps à une main et que votre autre Main est vide : +1 aux Défenses de FOR et d'AGI contre les attaques au corps à corps.",
    "When a damage die of your Two-Handed weapon shows 1 or 2, reroll it once.":
        "Quand un dé de dégâts de votre arme à Deux mains affiche 1 ou 2, relancez-le une fois.",
    "You draw a Thrown weapon as part of the attack that throws it, and your Thrown ranges are doubled.":
        "Vous dégainez une arme de Lancer pendant l'attaque qui la lance, et vos portées de Lancer sont doublées.",
    "**Reaction (2/L.R.)**, when you roll initiative or a creature hits you: for 1 minute, you Resist Physical damage and can't cast spells or use WIL magic.":
        "**Réaction (2/L.R.)**, quand vous lancez l'initiative ou qu'une créature vous touche : pendant 1 minute, vous Résistez aux dégâts Physiques et ne pouvez ni lancer de sorts ni utiliser la magie de VOL.",
    "Once per turn, if you end your movement out of sight, you can Hide without spending an action.":
        "Une fois par tour, si vous terminez votre déplacement hors de vue, vous pouvez vous Cacher sans dépenser d'action.",
    "+2 STR Defense while your Armor Slot is empty.": "+2 à la Défense de FOR tant que votre Emplacement d'Armure est vide.",
    "Your unarmed strikes deal 1d6 + STR or DEX Physical.": "Vos attaques à mains nues infligent 1d6 + FOR ou AGI Physique.",
    "**1/S.R.**, when you fail a check one of your Domains covers: reroll it.":
        "**1/C.R.**, quand vous ratez un test que couvre l'un de vos Domaines : relancez-le.",
    "**1/L.R.**, during a short rest: regain 2 spell points.": "**1/L.R.**, pendant un court repos : récupérez 2 points de sort.",
    # Wounds
    "You hobble.": "Vous boitez.", "Every breath hurts.": "Chaque respiration fait mal.",
    "You can't twist away in time.": "Vous ne pivotez plus assez vite.", "The world swims a little.": "Le monde tangue un peu.",
    "You flinch at every shadow.": "Vous sursautez à chaque ombre.", "Stitched, not healed.": "Recousue, pas guérie.",
    "−2 on ranged attacks and on checks to notice.": "−2 aux attaques à distance et aux tests pour remarquer.",
    "−2 on WIL checks.": "−2 aux tests de VOL.", "−2 on checks to climb, jump or swim.": "−2 aux tests pour grimper, sauter ou nager.",
    "−2 on melee attacks.": "−2 aux attaques au corps à corps.",
    "1 less Resolve and 1 less spell point.": "1 Ardeur de moins et 1 point de sort de moins.",
    "A short rest heals only a quarter of your missing HP (rounded up).":
        "Un court repos ne soigne qu'un quart de vos PV manquants (arrondi au supérieur).",
    "You may never run the same again.": "Vous ne courrez peut-être plus jamais comme avant.",
    "−2 on INT checks.": "−2 aux tests d'INT.", "You lose blood every time you move too fast.": "Vous perdez du sang dès que vous bougez trop vite.",
    # deck covers
    "Spell attack: **INT + 2**": "Attaque de sort : **INT + 2**", "Spell points: **4** (long rest)": "Points de sort : **4** (long repos)",
    "Spell points: **+2** (long rest)": "Points de sort : **+2** (long repos)", "Resolve: **+3** (short rest)": "Ardeur : **+3** (court repos)",
    "Max spell level: **2nd**": "Niveau de sort max : **2e**", "Casting needs an empty Hand.": "L'incantation demande une Main vide.",
    "Attack: **WIL + 2**": "Attaque : **VOL + 2**", "Resolve: **3 + WIL** (short rest)": "Ardeur : **3 + VOL** (court repos)",
    "Songs, poems and dances.": "Chants, poèmes et danses.", "Prayers.": "Prières.",
    "Beasts your body knows.": "Des bêtes que votre corps connaît.", "Gifts of a patron.": "Les dons d'un protecteur.",
    # spells and powers
    "**Action**, range 120 ft.": "**Action**, portée 48 m.",
    "Spell attack against DEX Defense: **1d10 Fire**. A flammable object it hits catches fire.":
        "Attaque de sort contre la Défense d'AGI : **1d10 Feu**. Un objet inflammable touché prend feu.",
    "**Action**, range 30 ft, Duration 1 minute.": "**Action**, portée 12 m, Durée 1 minute.",
    "A spectral hand lifts, carries or works an object up to 10 lb. It can't attack. Move it with your reaction.":
        "Une main spectrale soulève, porte ou manipule un objet de 5 kg au plus. Elle ne peut pas attaquer. Déplacez-la avec votre réaction.",
    "Three darts at one to three creatures. One spell attack against the DEX Defense of each target: **1d4 + 1 Radiant** per dart on a hit, half on a miss.":
        "Trois fléchettes sur une à trois créatures. Une attaque de sort contre la Défense d'AGI de chaque cible : **1d4 + 1 Radiant** par fléchette si elle touche, la moitié en cas d'échec.",
    "**Upcast:** +1 dart per level above 1st.": "**Surpuissance :** +1 fléchette par niveau au-delà du 1er.",
    "**Reaction**, when an attack hits you.": "**Réaction**, quand une attaque vous touche.",
    "+5 to your STR and DEX Defense until the start of your next turn, against the triggering attack too.":
        "+5 à vos Défenses de FOR et d'AGI jusqu'au début de votre prochain tour, y compris contre l'attaque déclencheuse.",
    "**Action**, range 60 ft, Duration 1 minute.": "**Action**, portée 24 m, Durée 1 minute.",
    "A 10-ft cube of slick grease: difficult terrain. Spell attack against the DEX Defense of each creature in it, and of each one that enters it or ends its turn there: on a hit, it falls **Prone**.":
        "Un cube de 4 m de graisse glissante : terrain difficile. Attaque de sort contre la Défense d'AGI de chaque créature à l'intérieur, et de chacune qui y entre ou y termine son tour : si elle touche, la créature tombe **À terre**.",
    "**Reaction.**": "**Réaction.**",
    "Teleport up to 30 ft to an unoccupied space you can see.": "Téléportez-vous jusqu'à 12 m vers un espace inoccupé que vous voyez.",
    "**Action**, range 60 ft, Duration 1 hour.": "**Action**, portée 24 m, Durée 1 heure.",
    "A 20-ft cube of webs: difficult terrain. Spell attack against the DEX Defense of each creature in it, and of each one that enters it: on a hit, it is **Restrained** for 2 turns. Fire burns a 5-ft square away each round.":
        "Un cube de 8 m de toiles : terrain difficile. Attaque de sort contre la Défense d'AGI de chaque créature à l'intérieur, et de chacune qui y entre : si elle touche, la créature est **Entravée** pendant 2 tours. Le feu en brûle une case de 2 m par round.",
    "**Action.** Attack against WIL Defense: until the end of the target's next turn, it has −2 on its next attack.":
        "**Action.** Attaque contre la Défense de VOL : jusqu'à la fin du prochain tour de la cible, elle a −2 à sa prochaine attaque.",
    "**Action**, Duration 1 minute.": "**Action**, Durée 1 minute.",
    "Up to 3 allies within 30 ft have +2 on attacks.": "Jusqu'à 3 alliés à 12 m ou moins ont +2 aux attaques.",
    "Allies within 30 ft have +2 to STR and DEX Defense.": "Les alliés à 12 m ou moins ont +2 aux Défenses de FOR et d'AGI.",
    "**Reaction**, after a creature within 60 ft rolls.": "**Réaction**, après le jet d'une créature à 24 m ou moins.",
    "−2 to an enemy's attack roll or check.": "−2 au jet d'attaque ou au test d'un ennemi.",
    "+2 to an ally's roll, or to the Defense an attack targets.": "+2 au jet d'un allié, ou à la Défense que vise une attaque.",
    "**Action.** Attack against WIL Defense: the target is **Frightened** of you for 2 turns.":
        "**Action.** Attaque contre la Défense de VOL : la cible est **Effrayée** par vous pendant 2 tours.",
    "**Action**, range 60 ft.": "**Action**, portée 24 m.",
    "A creature regains 2d4 + WIL HP.": "Une créature récupère 2d4 + VOL PV.",
    "**Reaction**, after an ally within 60 ft rolls a check.": "**Réaction**, après le test d'un allié à 24 m ou moins.",
    "Add 1d4 to it.": "Ajoutez-y 1d4.",
    "Up to 3 allies within 30 ft add 1d4 to their attack rolls.": "Jusqu'à 3 alliés à 12 m ou moins ajoutent 1d4 à leurs jets d'attaque.",
    "Attack against WIL Defense: the target subtracts 1d4 from its attack rolls.":
        "Attaque contre la Défense de VOL : la cible soustrait 1d4 à ses jets d'attaque.",
    "**Reroll:** make it reroll an attack roll or a check.": "**Relance :** faites-lui relancer un jet d'attaque ou un test.",
    "**Action**, touch.": "**Action**, contact.", "A creature regains 2d8 + WIL HP.": "Une créature récupère 2d8 + VOL PV.",
    "**Tiny** · Fly 60 ft.": "**Très petit** · Vol 24 m.", "Talons: +2 to hit, 1d4 + DEX Physical.": "Serres : +2 au toucher, 1d4 + AGI Physique.",
    "+2 on checks to notice.": "+2 aux tests pour remarquer.", "**Medium**.": "**Moyen**.",
    "Bite: +2 to hit, 1d6 + DEX Physical.": "Morsure : +2 au toucher, 1d6 + AGI Physique.",
    "+2 on checks to track.": "+2 aux tests pour pister.", "**Large** · Climb 30 ft.": "**Grand** · Escalade 12 m.",
    "Hide: +2 STR Defense (included).": "Cuir épais : +2 Défense de FOR (compris).",
    "Claws: +2 to hit, 1d8 + STR Physical.": "Griffes : +2 au toucher, 1d8 + FOR Physique.",
    # Evoker's Book
    "Spell attack against DEX Defense: **1d8 Cold**, and its Speed drops by 10 ft until the start of your next turn.":
        "Attaque de sort contre la Défense d'AGI : **1d8 Froid**, et sa Vitesse baisse de 4 m jusqu'au début de votre prochain tour.",
    "Spell attack against DEX Defense: **1d8 Lightning**, and it can't take reactions until the start of its next turn.":
        "Attaque de sort contre la Défense d'AGI : **1d8 Foudre**, et elle ne peut pas réagir jusqu'au début de son prochain tour.",
    "**Action**, range 15 ft.": "**Action**, portée 6 m.",
    "Flames fill a 10-ft cube. Spell attack against the DEX Defense of each creature in it: **3d6 Fire**, half on a miss.":
        "Des flammes emplissent un cube de 4 m. Attaque de sort contre la Défense d'AGI de chaque créature à l'intérieur : **3d6 Feu**, la moitié en cas d'échec.",
    "**Action**, range 30 ft.": "**Action**, portée 12 m.",
    "A 10-ft cube of thunder. Spell attack against the STR Defense of each creature in it: **2d8 Lightning** and it falls **Prone**; on a miss, half damage and it stays standing.":
        "Un cube de 4 m de tonnerre. Attaque de sort contre la Défense de FOR de chaque créature à l'intérieur : **2d8 Foudre** et elle tombe **À terre** ; en cas d'échec, la moitié des dégâts et elle reste debout.",
    "**Action**, range 90 ft.": "**Action**, portée 36 m.",
    "Spell attack against DEX Defense: **3d8** Fire, Cold, Lightning or Poison, your choice.":
        "Attaque de sort contre la Défense d'AGI : **3d8** Feu, Froid, Foudre ou Poison, au choix.",
    "Three rays at one to three creatures. One spell attack against the DEX Defense of each target: **2d6 Fire** per ray on a hit.":
        "Trois rayons sur une à trois créatures. Une attaque de sort contre la Défense d'AGI de chaque cible : **2d6 Feu** par rayon qui touche.",
    "A 10-ft sphere of ringing sound. Spell attack against the STR Defense of each creature in it: **3d8 Lightning**, half on a miss.":
        "Une sphère de 4 m de son strident. Attaque de sort contre la Défense de FOR de chaque créature à l'intérieur : **3d8 Foudre**, la moitié en cas d'échec.",
    # Abjurer's Book
    "**Action.**": "**Action.**",
    "You Resist Physical damage until the start of your next turn.": "Vous Résistez aux dégâts Physiques jusqu'au début de votre prochain tour.",
    "Repair one break or tear in an object.": "Réparez une cassure ou une déchirure d'un objet.",
    "**Action**, touch, Duration 8 hours.": "**Action**, contact, Durée 8 heures.",
    "A creature that wears no Armor has +3 STR Defense.": "Une créature qui ne porte pas d'Armure a +3 à sa Défense de FOR.",
    "You Resist Fire, Cold, Lightning and Poison until the start of your next turn, against the triggering attack too.":
        "Vous Résistez au Feu, au Froid, à la Foudre et au Poison jusqu'au début de votre prochain tour, y compris contre l'attaque déclencheuse.",
    "**Action**, touch, Duration 10 minutes.": "**Action**, contact, Durée 10 minutes.",
    "Undead, fiends, fey and elementals have −2 on attacks against the creature, and can't Charm or Frighten it.":
        "Les morts-vivants, fiélons, fées et élémentaires ont −2 aux attaques contre la créature, et ne peuvent ni la Charmer ni l'Effrayer.",
    "Up to 3 creatures gain 5 temporary HP.": "Jusqu'à 3 créatures gagnent 5 PV temporaires.",
    "A door, a window or a chest stays shut to all but you and those you name, until dispelled.":
        "Une porte, une fenêtre ou un coffre reste fermé à tous sauf à vous et à ceux que vous nommez, jusqu'à dissipation.",
    # Illusionist's Book
    "**Action**, range 30 ft, Duration 1 minute.": "**Action**, portée 12 m, Durée 1 minute.",
    "A sound, or the image of an object that fits in a 5-ft cube. A creature that studies it with an action sees through it.":
        "Un son, ou l'image d'un objet qui tient dans un cube de 2 m. Une créature qui l'examine avec une action perce l'illusion.",
    "**Action**, Duration 1 hour.": "**Action**, Durée 1 heure.",
    "You look like someone else of about your size, clothes and gear included. A creature that touches you, or studies you with an action, sees through it.":
        "Vous ressemblez à quelqu'un d'autre de votre taille environ, vêtements et équipement compris. Une créature qui vous touche, ou vous examine avec une action, perce l'illusion.",
    "**Action**, range 60 ft, Duration 10 minutes.": "**Action**, portée 24 m, Durée 10 minutes.",
    "A silent image that fits in a 15-ft cube. Move it with an action. A creature that studies it with an action sees through it.":
        "Une image muette qui tient dans un cube de 6 m. Déplacez-la avec une action. Une créature qui l'examine avec une action perce l'illusion.",
    "A burst of colors fills a 10-ft cube. Spell attack against the INT Defense of each creature in it: it is **Blinded** until the end of its next turn.":
        "Un éclat de couleurs emplit un cube de 4 m. Attaque de sort contre la Défense d'INT de chaque créature à l'intérieur : elle est **Aveuglée** jusqu'à la fin de son prochain tour.",
    "Three illusory copies of you: +3 to your STR and DEX Defense. Each time an attack misses you, a copy vanishes and the bonus drops by 1.":
        "Trois copies illusoires de vous : +3 à vos Défenses de FOR et d'AGI. Chaque fois qu'une attaque vous rate, une copie disparaît et le bonus baisse de 1.",
    "**Action**, touch, Duration 1 hour.": "**Action**, contact, Durée 1 heure.",
    "A creature is **Invisible**. It ends when the creature attacks or casts a spell.":
        "Une créature est **Invisible**. Le sort prend fin quand elle attaque ou lance un sort.",
    # Necromancer's Book
    "Spell attack against DEX Defense: **1d8 Necrotic**, and it can't regain HP until the start of your next turn.":
        "Attaque de sort contre la Défense d'AGI : **1d8 Nécrotique**, et elle ne peut pas regagner de PV avant le début de votre prochain tour.",
    "Spell attack against WIL Defense: **1d8 Necrotic**, or **1d12 Necrotic** if it is missing any HP.":
        "Attaque de sort contre la Défense de VOL : **1d8 Nécrotique**, ou **1d12 Nécrotique** s'il lui manque des PV.",
    "**Action**, range 10 ft, Duration 1 hour.": "**Action**, portée 4 m, Durée 1 heure.",
    "The corpse of a Small or Medium creature rises as a **Skeleton** (its foe card) on your side. It acts right after you: you choose its moves and actions. It dies instead of falling **Unconscious**. A corpse rises once; cast again and your previous Skeleton collapses.":
        "Le cadavre d'une créature Petite ou Moyenne se relève en **Squelette** (sa carte d'adversaire) dans votre camp. Il agit juste après vous : vous choisissez ses déplacements et ses actions. Il meurt au lieu de tomber **Inconscient**. Un cadavre ne se relève qu'une fois ; lancez le sort à nouveau et votre Squelette précédent s'effondre.",
    "You gain 1d4 + 4 temporary HP.": "Vous gagnez 1d4 + 4 PV temporaires.",
    "Spell attack against STR Defense: **2d8 Poison**, and it is **Poisoned** until the end of its next turn.":
        "Attaque de sort contre la Défense de FOR : **2d8 Poison**, et elle est **Empoisonnée** jusqu'à la fin de son prochain tour.",
    "Spell attack against DEX Defense: **3d6 Necrotic**, and you regain HP equal to half the damage dealt.":
        "Attaque de sort contre la Défense d'AGI : **3d6 Nécrotique**, et vous regagnez autant de PV que la moitié des dégâts infligés.",
    "Spell attack against WIL Defense: it is **Blinded** for 2 turns.":
        "Attaque de sort contre la Défense de VOL : elle est **Aveuglée** pendant 2 tours.",
    # Enchanter's Book
    "Spell attack against INT Defense: **1d6 Necrotic**, and it subtracts 1d4 from its next attack roll before the end of your next turn.":
        "Attaque de sort contre la Défense d'INT : **1d6 Nécrotique**, et elle soustrait 1d4 à son prochain jet d'attaque avant la fin de votre prochain tour.",
    "**Action**, touch, Duration 1 minute.": "**Action**, contact, Durée 1 minute.",
    "A creature can't be **Frightened**, and gains 2 temporary HP at the start of each of its turns.":
        "Une créature ne peut pas être **Effrayée**, et gagne 2 PV temporaires au début de chacun de ses tours.",
    "Spell attack against WIL Defense: **Subdue · Unconscious**. It wakes up when it takes damage, or when someone spends an action to shake it.":
        "Attaque de sort contre la Défense de VOL : **Emprise · Inconscient**. Elle se réveille quand elle subit des dégâts, ou quand quelqu'un dépense une action pour la secouer.",
    "Spell attack against the WIL Defense of a humanoid: **Subdue · Charmed**. When it ends, the creature knows it was charmed.":
        "Attaque de sort contre la Défense de VOL d'un humanoïde : **Emprise · Charmé**. Quand l'effet prend fin, la créature sait qu'elle a été charmée.",
    "Spell attack against WIL Defense: one word it obeys on its next turn. *Drop:* it drops what it holds. *Grovel:* it falls **Prone**. *Flee:* it spends its turn moving away from you.":
        "Attaque de sort contre la Défense de VOL : un mot auquel elle obéit à son prochain tour. *Lâche :* elle lâche ce qu'elle tient. *À genoux :* elle tombe **À terre**. *Fuis :* elle passe son tour à s'éloigner de vous.",
    "Spell attack against WIL Defense: it collapses with laughter. **Subdue · Incapacitated**.":
        "Attaque de sort contre la Défense de VOL : elle s'effondre de rire. **Emprise · Neutralisé**.",
    "Spell attack against the WIL Defense of a humanoid: it is paralyzed. **Subdue · Stunned**.":
        "Attaque de sort contre la Défense de VOL d'un humanoïde : elle est paralysée. **Emprise · Étourdi**.",
    # Occultist's Pact
    "**Action.** Attack against WIL Defense: **1d10 Necrotic**.": "**Action.** Attaque contre la Défense de VOL : **1d10 Nécrotique**.",
    "Attack against WIL Defense: the target subtracts 1d6 from its damage rolls.":
        "Attaque contre la Défense de VOL : la cible soustrait 1d6 à ses jets de dégâts.",
    "−2 to an enemy's attack roll, and it takes **1d10 Fire**.": "−2 au jet d'attaque d'un ennemi, et il subit **1d10 Feu**.",
    "**Action.** Attack against WIL Defense: the target is **Poisoned** for 2 turns.":
        "**Action.** Attaque contre la Défense de VOL : la cible est **Empoisonnée** pendant 2 tours.",
    # foes' own text
    "**Bite:** +4 to hit, 1d6 + 2 Physical.": "**Morsure :** +4 au toucher, 1d6 + 2 Physique.",
    "**Thick Hide:** +1 STR Defense (included).": "**Cuir épais :** +1 à la Défense de FOR (inclus).",
    "**Keen Nose:** alert (passive Awareness +5).": "**Flair :** alerte (Vigilance passive +5).",
    "**Nimble (2/S.R.):** reaction. Move up to half its Speed without provoking opportunity attacks.": "**Leste (2/C.R.) :** réaction. Il se déplace de la moitié de sa Vitesse sans provoquer d'attaque d'opportunité.",
    "Throws its *Pilum*, then draws its *Gladius*.": "Lance son *Pilum*, puis dégaine son *Gladius*.",
    "**Giant Strength:** +60 HP. Its *Javelins* roll one extra damage die (included). Its *Sweeping Blow* recharges on a 5–6 instead of 1/S.R.":
        "**Force de géant :** +60 PV. Ses *Javelots* lancent un dé de dégâts supplémentaire (compris). Son *Coup balayant* se recharge sur 5–6 au lieu de 1/C.R.",
    "**Warlord:** its *Sweeping Blow* recharges on a 5–6 instead of 1/S.R.":
        "**Seigneur de guerre :** son *Coup balayant* se recharge sur 5–6 au lieu de 1/C.R.",
    "**Bellow (Recharge 5–6):** reaction. Attack (+5) against the WIL Defense of each enemy within 30 ft: Frightened of the chieftain until the end of its next turn.":
        "**Beuglement (Recharge 5–6) :** réaction. Attaque (+5) contre la Défense de VOL de chaque ennemi à 12 m ou moins : Effrayé par le chef jusqu'à la fin de son prochain tour.",
    "**Keen Eyes:** alert (passive Awareness +5).": "**Œil perçant :** alerte (Vigilance passive +5).",
    "**Undead:** resists Poison and Necrotic, vulnerable to Radiant. Never checks Morale.":
        "**Mort-vivant :** résiste au Poison et au Nécrotique, vulnérable au Radiant. Ne teste jamais son Moral.",
    "**Slam:** +3 to hit, 1d8 + 1 Physical.": "**Coup :** +3 au toucher, 1d8 + 1 Physique.",
    "**Bite:** +4 to hit, 1d4 + 2 Physical.": "**Morsure :** +4 au toucher, 1d4 + 2 Physique.",
    "**Spider Climb:** climbs walls and ceilings at full Speed. **Web Sense:** alert (passive Awareness +5).":
        "**Pattes d'araignée :** grimpe aux murs et aux plafonds à pleine Vitesse. **Sens de la toile :** alerte (Vigilance passive +5).",
    "**Bite:** +5 to hit, 1d8 + 3 Physical plus 1d8 Poison.": "**Morsure :** +5 au toucher, 1d8 + 3 Physique plus 1d8 Poison.",
    "**Web (Recharge 5–6):** action, range 30 ft. Attack (+3) against DEX Defense: **Restrained** for 2 turns.":
        "**Toile (Recharge 5–6) :** action, portée 12 m. Attaque (+3) contre la Défense d'AGI : **Entravé** pendant 2 tours.",
    "**Claws:** +6 to hit, 2d6 + 4 Physical.": "**Griffes :** +6 au toucher, 2d6 + 4 Physique.",
    "**Regeneration:** regains 10 HP at the start of its turn, unless it took Fire or Poison damage since its last turn.":
        "**Régénération :** récupère 10 PV au début de son tour, sauf s'il a subi des dégâts de Feu ou de Poison depuis son dernier tour.",
    # beginner monsters' own text
    "**Construct:** resists Poison and Necrotic. Never checks Morale.":
        "**Créature artificielle :** résiste au Poison et au Nécrotique. Ne teste jamais son Moral.",
    "**Flyer:** flies at its full Speed.": "**Volant :** vole à pleine Vitesse.",
    "**Proboscis:** +5 to hit, 1d4 + 3 Physical, and it latches on: the target is **Grappled** by it.":
        "**Trompe :** +5 au toucher, 1d4 + 3 Physique, et elle s'accroche : la cible est **Agrippée** par elle.",
    "**Wall Crawler:** climbs walls and ceilings at full Speed.":
        "**Grimpeur :** grimpe aux murs et aux plafonds à pleine Vitesse.",
    "**Bite:** +4 to hit, 1d4 + 2 Physical, and the target is **Poisoned** until the end of the centipede's next turn.":
        "**Morsure :** +4 au toucher, 1d4 + 2 Physique, et la cible est **Empoisonnée** jusqu'à la fin du prochain tour du mille-pattes.",
    "**Tusks:** +3 to hit, 1d6 + 1 Physical.": "**Défenses :** +3 au toucher, 1d6 + 1 Physique.",
    "**Charge:** when it hits right after a Move straight at the target, the target falls **Prone**.":
        "**Charge :** s'il touche juste après un Déplacement en ligne droite vers la cible, celle-ci tombe **À terre**.",
    "**Steel Body:** +5 STR Defense (included).": "**Corps d'acier :** +5 à la Défense de FOR (inclus).",
    "**Meat Shield:** when an attack hits it, it may pull an adjacent goblin in the way: the goblin is hit instead.":
        "**Bouclier de chair :** quand une attaque le touche, il peut tirer devant lui un gobelin adjacent : c'est le gobelin qui est touché.",
    "**Rend:** +4 to hit, 1d6 + 2 Physical.": "**Lacération :** +4 au toucher, 1d6 + 2 Physique.",
    "**Incorporeal:** resists Physical. Moves through creatures and objects.":
        "**Intangible :** résiste au Physique. Traverse les créatures et les objets.",
    "**Draining Touch:** +4 to hit, 2d6 + 2 Necrotic. The target's damage rolls lose 1d4 for 2 turns.":
        "**Contact affaiblissant :** +4 au toucher, 2d6 + 2 Nécrotique. Les jets de dégâts de la cible perdent 1d4 pendant 2 tours.",
    "**Bite:** +5 to hit, 1d10 + 3 Physical.": "**Morsure :** +5 au toucher, 1d10 + 3 Physique.",
    "**Claws:** +4 to hit, 2d4 + 2 Physical.": "**Griffes :** +4 au toucher, 2d4 + 2 Physique.",
    "**Paralyzing Touch (Recharge 5–6):** action. Attack (+3) against the STR Defense of a creature within 5 ft: **Subdue · Stunned** (paralyzed).":
        "**Contact paralysant (Recharge 5–6) :** action. Attaque (+3) contre la Défense de FOR d'une créature à 2 m ou moins : **Emprise · Étourdi** (paralysé).",
    "**Grab:** +4 to hit, 2d6 + 2 Physical, and the target is **Grappled** by it.":
        "**Empoignade :** +4 au toucher, 2d6 + 2 Physique, et la cible est **Agrippée** par lui.",
    "**Abduct:** it moves at full Speed while dragging a creature it grapples.":
        "**Rapt :** il se déplace à pleine Vitesse en traînant une créature qu'il agrippe.",
    "**Slam:** +4 to hit, 1d6 + 2 Physical.": "**Coup :** +4 au toucher, 1d6 + 2 Physique.",
    "**False Appearance:** while it stays still, it looks like an empty suit of armor.":
        "**Faux-semblant :** tant qu'elle reste immobile, elle ressemble à une armure vide.",
    "**Claws:** +3 to hit, 2d4 + 1 Physical.": "**Griffes :** +3 au toucher, 2d4 + 1 Physique.",
    "**Luring Song (Recharge 5–6):** action. Attack (+3) against the WIL Defense of each enemy within 60 ft who can hear it: **Subdue · Charmed**.":
        "**Chant envoûtant (Recharge 5–6) :** action. Attaque (+3) contre la Défense de VOL de chaque ennemi à 24 m ou moins qui peut l'entendre : **Emprise · Charmé**.",
    "**Bite:** +5 to hit, 1d8 + 3 Physical.": "**Morsure :** +5 au toucher, 1d8 + 3 Physique.",
    "**Claw:** +5 to hit, 1d4 + 3 Physical, and the target falls **Prone**.":
        "**Griffe :** +5 au toucher, 1d4 + 3 Physique, et la cible tombe **À terre**.",
    "**Ooze:** resists Poison. Never checks Morale. **Transparent:** easy to miss until it moves.":
        "**Vase :** résiste au Poison. Ne teste jamais son Moral. **Transparent :** passe facilement inaperçu tant qu'il ne bouge pas.",
    "**Soft Body:** −5 STR Defense (included).": "**Corps mou :** −5 à la Défense de FOR (inclus).",
    "**Pseudopod:** +4 to hit, 3d6 Poison.": "**Pseudopode :** +4 au toucher, 3d6 Poison.",
    "**Engulf (Recharge 5–6):** action. Attack (+4) against the DEX Defense of a creature within 5 ft: 3d6 Poison, and it is **Restrained** inside the cube for 2 turns.":
        "**Engloutissement (Recharge 5–6) :** action. Attaque (+4) contre la Défense d'AGI d'une créature à 2 m ou moins : 3d6 Poison, et elle est **Entravée** dans le cube pendant 2 tours.",
    "**Beak:** +7 to hit, 1d10 + 5 Physical.": "**Bec :** +7 au toucher, 1d10 + 5 Physique.",
    "**Claws:** +7 to hit, 2d8 + 5 Physical.": "**Griffes :** +7 au toucher, 2d8 + 5 Physique.",
    # Rank II WIL decks (from festive-hypatia)
    '**Learned:** ½ INT extra spell points. Your checks to recall lore add both INT and WIL.': "**Érudit :** ½ INT points de sort supplémentaires. Vos tests pour se souvenir de connaissances ajoutent l'INT et la VOL.",
    '**Solitude:** ½ WIL extra Resolve. Your checks to forage and endure add both INT and WIL.': "**Solitude :** ½ VOL Ardeur supplémentaire. Vos tests pour cueillir et endurer ajoutent l'INT et la VOL.",
    'While you hold it, it counts as an empty Hand for casting from a Spellbook.': 'Tant que vous le tenez, il compte comme une Main vide pour lancer des sorts depuis un Livre de sorts.',
    'Attack: **WIL + 3**': 'Attaque : **VOL + 3**',
    'Resolve: **+4** (short rest)': 'Ardeur : **+4** (court repos)',
    'Proclamations, war songs and taunts.': 'Proclamations, chants de guerre et provocations.',
    'Psalms and judgments.': 'Psaumes et jugements.',
    'Hunters of the deep woods.': 'Les chasseurs des bois profonds.',
    'Gifts of a patron who keeps count.': "Les dons d'un patron qui tient les comptes.",
    "Attack against WIL Defense: until the end of the target's next turn, it has −3 on its next attack.": "Attaque contre la Défense de VOL : jusqu'à la fin du prochain tour de la cible, elle a −3 à sa prochaine attaque.",
    'Allies within 30 ft have +3 to WIL Defense.': 'Les alliés à 12 m ou moins ont +3 à la Défense de VOL.',
    "−3 to an enemy's attack roll or check.": "−3 au jet d'attaque ou au test d'un ennemi.",
    '**Action.** One attack against the WIL Defense of each enemy within 30 ft: **Frightened** of you until the end of your next turn.': "**Action.** Une attaque contre la Défense de VOL de chaque ennemi à 12 m ou moins : **Effrayé** par vous jusqu'à la fin de votre prochain tour.",
    'A creature regains 3d4 + WIL HP.': 'Une créature récupère 3d4 + VOL PV.',
    '**Reaction**, after an enemy within 60 ft rolls a check.': "**Réaction**, après le test d'un ennemi à 24 m ou moins.",
    'Subtract 1d4 from it.': 'Soustrayez-y 1d4.',
    '**Reaction**, after a creature within 60 ft rolls an attack.': "**Réaction**, après le jet d'attaque d'une créature à 24 m ou moins.",
    "Add 1d4 to an ally's attack roll, or to the Defense an enemy's attack targets.": "Ajoutez 1d4 au jet d'attaque d'un allié, ou à la Défense que vise l'attaque d'un ennemi.",
    'Attack against WIL Defense: the target falls **Prone**.': 'Attaque contre la Défense de VOL : la cible tombe **À terre**.',
    'Up to 3 allies within 30 ft add 1d4 to their damage rolls.': "Jusqu'à 3 alliés à 12 m ou moins ajoutent 1d4 à leurs jets de dégâts.",
    'A creature regains 3d8 + WIL HP.': 'Une créature récupère 3d8 + VOL PV.',
    'Up to 3 allies regain 2d4 + WIL HP.': "Jusqu'à 3 alliés récupèrent 2d4 + VOL PV.",
    '**Tiny** · Climb 20 ft, on walls and ceilings.': '**Très petit** · Escalade 8 m, sur les murs et les plafonds.',
    'Bite: +3 to hit, 1d4 + DEX Poison.': 'Morsure : +3 au toucher, 1d4 + AGI Poison.',
    '+3 on checks to sneak.': '+3 aux tests pour se faufiler.',
    '**Medium** · Climb 30 ft.': '**Moyen** · Escalade 12 m.',
    'Claws: +3 to hit, 1d8 + DEX Physical.': 'Griffes : +3 au toucher, 1d8 + AGI Physique.',
    '+3 on checks to jump.': '+3 aux tests pour sauter.',
    '**Large**.': '**Grand**.',
    'Hide: +3 STR Defense (included).': 'Cuir épais : +3 Défense de FOR (compris).',
    'Horns: +3 to hit, 1d10 + STR Physical.': 'Cornes : +3 au toucher, 1d10 + FOR Physique.',
    'Up to 3 allies regain 2d6 + WIL HP.': "Jusqu'à 3 alliés récupèrent 2d6 + VOL PV.",
    'Attack against WIL Defense: **1d10 Necrotic**.': 'Attaque contre la Défense de VOL : **1d10 Nécrotique**.',
    'Attack against WIL Defense: the target has −3 to all its Defenses.': 'Attaque contre la Défense de VOL : la cible a −3 à toutes ses Défenses.',
    'Attack against WIL Defense: **2d6 Necrotic**, and until the end of its next turn, −3 on its next attack.': "Attaque contre la Défense de VOL : **2d6 Nécrotique**, et jusqu'à la fin de son prochain tour, −3 à sa prochaine attaque.",
    'Attack against WIL Defense: **3d8 Necrotic**, half on a miss.': "Attaque contre la Défense de VOL : **3d8 Nécrotique**, la moitié en cas d'échec.",
    'Attack against WIL Defense: **2d6 Necrotic**, and the target is **Blinded** for 2 turns.': 'Attaque contre la Défense de VOL : **2d6 Nécrotique**, et la cible est **Aveuglée** pendant 2 tours.',
}

LORE = {
    "Horn, sinew and years of an archer's patience. Only steady fingers can draw it.":
        "De la corne, du tendon et des années de patience d'archer. Seuls des doigts sûrs peuvent le bander.",
    "A rod of black wood capped with copper. It hums in a thinking hand and crackles when pointed.":
        "Une tige de bois noir coiffée de cuivre. Elle bourdonne dans une main qui réfléchit et crépite quand on la pointe.",
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
    "Glyphs run along its grain. The wood remembers the shape of a casting hand.": "Des glyphes courent le long du fil. Le bois se souvient de la forme d'une main qui incante.",
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
    "Leather straps padded for stone. Runestones knock softly against each other as you walk.": "Des sangles de cuir rembourrées pour la pierre. Les Pierres runiques s'entrechoquent doucement à chaque pas.",
    "A blessed token on a worn cord. Prayers spoken over it seem to travel further.": "Un médaillon béni sur un cordon usé. Les prières dites sur lui semblent porter plus loin.",
    "Soft boots that never wear out. Every few steps, one lands farther than it should.": "Des bottes souples qui ne s'usent jamais. Tous les quelques pas, l'un d'eux tombe plus loin qu'il ne devrait.",
    "Copper wire coiled around a blue stone. It bites whoever lays a hand on its wearer.": "Un fil de cuivre enroulé autour d'une pierre bleue. Il mord quiconque porte la main sur son porteur.",
    "A string of tiny bells for the ankle. Their jingle gets under an enemy's skin.": "Un chapelet de clochettes pour la cheville. Leur tintement agace l'ennemi jusqu'à l'os.",
    # items
    "Red and faintly warm, it tastes of iron and cherries. Shake before drinking.": "Rouge et un peu tiède, elle a un goût de fer et de cerise. Agiter avant de boire.",
    "A drawstring purse of good leather. Its weight is the only friend some people have.": "Du bon cuir, un cordon solide. Son poids est le seul ami de certains.",
    "Heavy paper, a heavy seal. A debt someone important promised to repay.": "Papier épais, sceau pesant. Une dette qu'un personnage important a promis d'honorer.",
    "Deep crimson and almost hot to hold. Wounds close while you're still swallowing.": "D'un pourpre profond, presque brûlante en main. Les plaies se ferment avant la dernière gorgée.",
    "Bitter herbs, river clay and a healer's patience, sealed in a tin.": "Herbes amères, argile de rivière et patience de guérisseur, scellées dans une boîte en fer.",
    "The oldest trick there is. It still works.": "Le plus vieux tour qui soit. Il marche encore.",
    "Three corked flasks and the knowledge to fill them. Keep them away from the campfire.": "Trois fioles bouchées et le savoir pour les remplir. À tenir loin du feu de camp.",
    # Runes
    "The ground lets go of you a little sooner, and takes you back a little later.": "Le sol vous lâche un peu plus tôt, et vous reprend un peu plus tard.",
    "Blood gone thick and slow as stone. Poison sinks into it and goes no further.": "Un sang devenu épais et lent comme la pierre. Le poison s'y enfonce et ne va pas plus loin.",
    "A resolve that stares down terrors and does not blink.": "Une résolution qui toise l'épouvante sans ciller.",
    "A mind that sees through mist and mirrors. Illusions slide off it like rain.": "Un esprit qui voit à travers brumes et miroirs. Les illusions glissent dessus comme la pluie.",
    "One foe falls, and the blade is already moving to the next.": "Un ennemi tombe, et la lame file déjà vers le suivant.",
    "A breath held between heartbeats, until the arrow flies.": "Un souffle retenu entre deux battements, jusqu'à ce que la flèche parte.",
    "Shields aren't only for hiding behind. The rim is a weapon too.": "Un bouclier ne sert pas qu'à se cacher. Son rebord est aussi une arme.",
    "A chant that rises with every strike, until the whole line sings along.": "Un chant qui monte à chaque coup, jusqu'à ce que toute la ligne le reprenne.",
    "One voice that turns a rout into a charge. It carries farther than a voice should.": "Une seule voix qui change une déroute en charge. Elle porte plus loin qu'une voix ne devrait.",
    "The rule of the front rank: your shield guards the friend beside you.": "La règle du premier rang : votre bouclier garde l'ami à vos côtés.",
    "Why use a door when a window will do?": "Pourquoi prendre la porte quand une fenêtre suffit ?",
    "A name that opens doors. Everyone has heard the stories, true or not.": "Un nom qui ouvre les portes. Tout le monde connaît les histoires, vraies ou non.",
    "Salt on the lips, knots in the fingers, and a tale for every port.": "Du sel sur les lèvres, des nœuds dans les doigts, et une histoire pour chaque port.",
    "Every alley has a shortcut, every crowd a loose purse, every corner a whisper.": "Chaque ruelle a son raccourci, chaque foule sa bourse mal fermée, chaque coin son murmure.",
    "Broken twigs, bent grass, the hush before a deer bolts. The wild speaks, and you listen.": "Brindilles cassées, herbe couchée, le silence avant qu'un cerf ne détale. La nature parle, et vous écoutez.",
    "Steady hands, a calm voice, and the right herb for the right fever.": "Des mains sûres, une voix calme, et la bonne herbe pour la bonne fièvre.",
    "The whole room at a glance: who lies, who drinks, who will start the fight.": "Toute la salle d'un coup d'œil : qui ment, qui boit, qui lancera la bagarre.",
    "The forge's wisdom: the weight of iron, the price of iron, where iron breaks.": "La sagesse de la forge : le poids du fer, le prix du fer, l'endroit où le fer se brise.",
    "Thin air and sheer cliffs feel like home. The mountain doesn't win.": "L'air rare et les falaises abruptes ont un goût de chez-soi. La montagne ne gagne pas.",
    "A feint and a cut, so fast they sound like one blow.": "Une feinte et une taille, si rapides qu'on n'entend qu'un coup.",
    "When others lie down, you get back up. Pain is a problem for later.": "Quand les autres se couchent, vous vous relevez. La douleur, ce sera pour plus tard.",
    "Lean, ropy strength. Not much meat on it, and it never tires.": "Une force sèche et noueuse. Jamais bien épaisse, jamais fatiguée.",
    "Eyes made for the dark. Shadows turn to shapes, then to detail.": "Des yeux faits pour le noir. Les ombres deviennent des formes, puis des détails.",
    "A hard stare and a hand on the hilt. It knows the price of everything, and of everyone.": "Un regard dur et une main sur la garde. Elle connaît le prix de tout, et de chacun.",
    "Flips, falls and landings that make a crowd gasp.": "Saltos, chutes et réceptions qui coupent le souffle à la foule.",
    "It knows the moment a friend has the prey, and when to pull it down.": "Elle sait quand un compagnon tient la proie, et quand la faire tomber.",
    "A way of being somewhere else when the blow arrives.": "Une façon d'être ailleurs quand le coup arrive.",
    "Roots, leaves and old charms, and what each one is good for.": "Racines, feuilles et vieux charmes, et ce à quoi chacun est bon.",
    "The wide arc of a giant's swing. Everyone in reach learns to fear it.": "Le large arc d'un coup de géant. Tous ceux à portée apprennent à le craindre.",
    "It will not stay down. Death has to ask twice.": "Elle refuse de rester à terre. La mort doit demander deux fois.",
    "Stubborn to the bone. What skill can't do, trying again will.": "Une tête dure jusqu'à l'os. Ce que l'adresse ne fait pas, un nouvel essai le fera.",
    "Eyes that never quite lose the starlight. For them, dusk lasts all night.": "Des yeux qui ne perdent jamais tout à fait la lueur des étoiles. Pour eux, le crépuscule dure toute la nuit.",
    "Feet like roots in rock. It shrugs off the shove, the grip and the poison.": "Des pieds comme des racines dans le roc. Elle encaisse la poussée, la prise et le poison.",
    "Fate likes whoever carries it, and nobody knows why.": "Le destin aime qui la porte, et personne ne sait pourquoi.",
    "Made for war and for the long march after it. Strike hard, carry it all home.": "Faite pour la guerre et la longue marche qui suit. Frapper fort, tout rapporter.",
    "March in step, hold the post, read the order before it is given.": "Marcher au pas, tenir le poste, lire l'ordre avant qu'il soit donné.",
    # deck covers
    "Spells copied in a careful hand, the margins full of warnings. The ink still smells of ozone.": "Des sorts recopiés d'une main soigneuse, les marges pleines d'avertissements. L'encre sent encore l'ozone.",
    "Songs of roadside fires and tavern corners, made for someone who never stays long.": "Des chansons de feux de route et de coins de taverne, faites pour qui ne reste jamais longtemps.",
    "Prayers worn smooth by a thousand voices. The faith comes with them.": "Des prières polies par mille voix. La foi vient avec.",
    "Fur, feather and claw. The body knows these shapes, and longs for them.": "Poil, plume et griffe. Le corps connaît ces formes, et s'en languit.",
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
    'Thick pelts, cured and laced. It smells of the animal for a while, then of you.': "D'épaisses fourrures, tannées et lacées. Elles sentent la bête un moment, puis vous.",
    'Leather stiffened with rivets. It turns a blade and still lets you crouch.': 'Un cuir raidi de rivets. Il détourne une lame et vous laisse encore vous accroupir.',
    "A length of braided leather with a crack like a breaking branch. It keeps a foe at arm's length, and more.": "Une longueur de cuir tressé qui claque comme une branche qui casse. Elle tient l'ennemi à bout de bras, et plus loin.",
    'Small enough for a sleeve, loud enough to end an argument.': 'Assez petite pour une manche, assez bruyante pour clore une dispute.',
    'A heavy steel bow on a wooden stock. Slow to wind, and nothing stops the bolt.': "Un lourd arc d'acier sur un fût de bois. Lente à armer, et rien n'arrête le carreau.",
    'A living branch that never quite stopped growing. Wounds close faster in its shade.': "Une branche vivante qui n'a jamais tout à fait cessé de pousser. Les plaies se ferment plus vite à son ombre.",
    'Bone, feather and a knot of fur on a thong. The beasts you become wear it too.': 'Os, plume et nœud de fourrure sur une lanière. Les bêtes que vous devenez le portent aussi.',
    'A clear stone that holds a little light after dark. A tired mind can borrow from it.': 'Une pierre claire qui garde un peu de lumière après la nuit tombée. Un esprit las peut y puiser.',
    'Linen, thread, a bone needle and a pot of salve. Enough to keep a friend breathing.': "Du lin, du fil, une aiguille d'os et un pot d'onguent. De quoi garder un ami en vie.",
    'Wind, distance, the arc of the shot. Far is just another kind of near.': "Le vent, la distance, l'arc du tir. Loin n'est qu'une autre façon d'être près.",
    'Armor worn like a second skin, every plate where the blow will land.': 'Une armure portée comme une seconde peau, chaque pièce là où le coup tombera.',
    'One blade, one open hand, and a body that turns sideways to every thrust.': "Une lame, une main libre, et un corps qui s'efface devant chaque estoc.",
    'A big weapon forgives nothing, and gives nothing back but strength.': 'Une grande arme ne pardonne rien, et ne rend que de la force.',
    'The knife leaves the belt and the hand in the same motion.': "Le couteau quitte la ceinture et la main d'un seul geste.",
    'A red haze that eats pain and spits out fury. Thinking can wait.': 'Un voile rouge qui dévore la douleur et crache la fureur. Réfléchir attendra.',
    'A step into shadow, and the room forgets you were there.': "Un pas dans l'ombre, et la salle oublie que vous étiez là.",
    'No steel, no leather: just a body that is never where the blow arrives.': "Ni acier ni cuir : juste un corps qui n'est jamais là où le coup arrive.",
    'Hands and feet trained until they hit like hammers.': "Des mains et des pieds entraînés jusqu'à frapper comme des marteaux.",
    'What it knows well, it knows twice.': "Ce qu'elle sait bien, elle le sait deux fois.",
    'An hour of quiet study, and a little of the spent magic comes back.': "Une heure d'étude au calme, et un peu de la magie dépensée revient.",
    'Dust, candle wax and a thousand spines. The answer is in a book somewhere.': 'Poussière, cire de bougie et mille reliures. La réponse est quelque part dans un livre.',
    'Bows, titles and smiles with knives behind them. It knows the steps of that dance.': 'Révérences, titres et sourires avec des couteaux derrière. Elle connaît les pas de cette danse.',
    'Far from roads and roofs, where the land does the talking.': 'Loin des routes et des toits, là où la terre fait la conversation.',
    "A borrowed name, a false smile, a hand in someone's pocket.": "Un nom d'emprunt, un faux sourire, une main dans la poche d'un autre.",
    'Hunger, cold and silence, endured until they taught something.': "La faim, le froid et le silence, endurés jusqu'à ce qu'ils enseignent quelque chose.",
    'Every page is scorched at the corners. Raw power, written down and barely held.': 'Chaque page est roussie aux coins. De la puissance brute, couchée sur papier et à peine contenue.',
    'Wards, seals and locks, in a hand that never smudges. Nothing gets in.': "Protections, sceaux et verrous, d'une main qui ne bave jamais. Rien n'entre.",
    'Its pages show something else to every reader. Only the owner sees the spells.': 'Ses pages montrent autre chose à chaque lecteur. Seul son propriétaire y voit les sorts.',
    'Soft words for hard minds. Its margins are full of names.': 'Des mots doux pour les esprits durs. Ses marges sont pleines de noms.',
    'A promise made in the dark, to something that keeps its promises too.': 'Une promesse faite dans le noir, à quelque chose qui tient aussi les siennes.',
    'A pale beam that leaves frost on the skin and lead in the legs.': 'Un rayon pâle qui laisse du givre sur la peau et du plomb dans les jambes.',
    'A handshake that nobody forgets, or finishes.': "Une poignée de main que personne n'oublie, ni ne termine.",
    'Thumbs together, fingers spread, and a sheet of flame leaps out.': 'Pouces joints, doigts écartés, et une nappe de flammes jaillit.',
    'A clap of thunder from an open palm. Everyone close ends up on the floor.': "Un coup de tonnerre d'une paume ouverte. Tous ceux qui sont près finissent par terre.",
    'A sphere that shifts color in flight, and decides on the way what it will be.': "Une sphère qui change de couleur en vol, et décide en chemin de ce qu'elle sera.",
    'Three lines of fire, drawn in the air like strokes of a pen.': "Trois traits de feu, tracés dans l'air comme des coups de plume.",
    'A single ringing note that cracks stone, glass and bone.': "Une seule note stridente qui fend la pierre, le verre et l'os.",
    'A shimmer over the skin. Edges skid off it.': 'Un miroitement sur la peau. Les lames glissent dessus.',
    'A torn strap, a cracked cup, a broken link: whole again, without a seam.': 'Une sangle déchirée, une coupe fêlée, un maillon brisé : entiers à nouveau, sans couture.',
    'A skin of force, light as silk and harder than mail.': 'Une peau de force, légère comme la soie et plus dure que la maille.',
    'The fire hits, and the ward drinks it.': 'Le feu frappe, et la protection le boit.',
    'A circle drawn on the air. The dead and the damned find it hard to cross.': "Un cercle tracé dans l'air. Les morts et les damnés ont du mal à le franchir.",
    'A surge of vigor that leaves allies taller than they were.': "Un sursaut de vigueur qui laisse les alliés plus grands qu'avant.",
    "A sigil on the lock. It won't open for you, whoever you are.": "Un sigle sur la serrure. Elle ne s'ouvrira pas pour vous, qui que vous soyez.",
    "A creak behind the door, a crate that isn't there.": "Un grincement derrière la porte, une caisse qui n'est pas là.",
    'A new face, new clothes, the same voice. Practice the voice.': 'Un nouveau visage, de nouveaux habits, la même voix. Travaillez la voix.',
    'A whole scene painted on the air, perfect until someone pokes it.': "Toute une scène peinte dans l'air, parfaite jusqu'à ce que quelqu'un la touche du doigt.",
    'A burst of dazzling colors. When the eyes come back, the fight has moved on.': 'Un éclat de couleurs éblouissantes. Quand la vue revient, le combat a continué sans vous.',
    'Three of you, then two, then one. Which one is real? Guess.': 'Trois de vous, puis deux, puis un. Lequel est le vrai ? Devinez.',
    "The light bends around you. Don't sneeze.": "La lumière se courbe autour de vous. N'éternuez pas.",
    'A cold splinter of thought, driven between the eyes.': 'Un éclat de pensée glacé, planté entre les yeux.',
    'Courage, poured in like warm wine.': 'Du courage, versé comme un vin chaud.',
    "Bound in grey hide, cold to the touch. The dead read it too, in their way.": "Relié de peau grise, froid au toucher. Les morts le lisent aussi, à leur manière.",
    "A ghostly hand, and the warmth goes out of the wound.": "Une main de spectre, et la chaleur quitte la plaie.",
    "One bell, heard only by the one it rings for.": "Une cloche, que seul entend celui pour qui elle sonne.",
    "Old bones remember how to stand.": "Les vieux os se souviennent comment tenir debout.",
    "Borrowed breath, cold in the chest.": "Un souffle d'emprunt, froid dans la poitrine.",
    "A green beam, and a stomach that turns.": "Un rayon vert, et l'estomac qui se retourne.",
    "What it loses, you keep.": "Ce qu'elle perd, vous le gardez.",
    "A whisper, and the world goes dark.": "Un murmure, et le monde s'éteint.",
    'A heavy warmth behind the eyes. Just for a moment.': 'Une lourde chaleur derrière les yeux. Juste un instant.',
    'A friendly voice, a reasonable request. Why would anyone refuse?': 'Une voix amicale, une demande raisonnable. Pourquoi refuser ?',
    'One word, spoken like a command from a king.': "Un seul mot, prononcé comme l'ordre d'un roi.",
    'Everything is suddenly, hopelessly funny.': 'Tout devient soudain, désespérément drôle.',
    'Every muscle locks. Only the eyes still move.': 'Chaque muscle se fige. Seuls les yeux bougent encore.',
    'A crackling beam of something that was never meant to be in this world.': "Un rayon crépitant de quelque chose qui n'aurait jamais dû être en ce monde.",
    'A black ray that turns muscle to wet rope.': 'Un rayon noir qui change le muscle en corde mouillée.',
    'Strike the occultist, and the flames of a patron answer.': "Frappez l'occultiste, et les flammes d'un protecteur répondent.",
    'A muttered curse. Food sours, hands shake, the stomach turns.': "Une malédiction marmonnée. La nourriture tourne, les mains tremblent, l'estomac se soulève.",
    # Rank II WIL decks (from festive-hypatia)
    'Cried from the walls before the battle, and from the field after it. The enemy hears both.': "Crié du haut des remparts avant la bataille, et sur le champ après. L'ennemi entend les deux.",
    'The prayers of a parish priest who has buried too many. Gentle for the flock, heavy for the wolf.': "Les prières d'un curé de paroisse qui a trop enterré. Douces pour le troupeau, lourdes pour le loup.",
    'Shapes that hunt at dusk, and the patience to wait for it.': "Des formes qui chassent au crépuscule, et la patience de l'attendre.",
    'Signed in ink that was never ink. The patron gives freely, and remembers everything.': "Signé d'une encre qui n'a jamais été de l'encre. Le patron donne sans compter, et se souvient de tout.",
    'Loud, rude and impossible to ignore. The swing goes wide out of pure spite.': 'Bruyantes, grossières, impossibles à ignorer. Le coup part de travers par pur dépit.',
    "A herald's cry: the banner still stands, and so do you.": 'Le cri du héraut : la bannière tient debout, et vous aussi.',
    'One word, flung across the field at the worst possible moment.': 'Un mot, lancé à travers le champ au pire moment possible.',
    "The herald announces the enemy's defeat a little early. Some of them believe it.": "Le héraut annonce la défaite de l'ennemi un peu tôt. Certains y croient.",
    'A slow refrain that carries further than it should. Breathing comes easier.': "Un refrain lent qui porte plus loin qu'il ne devrait. On respire mieux.",
    "A crow on the sill, a candle that gutters. The enemy's luck turns sour.": "Un corbeau sur le rebord, une bougie qui vacille. La chance de l'ennemi tourne à l'aigre.",
    'A hand on the shoulder that nobody put there.': "Une main sur l'épaule que personne n'y a posée.",
    'Spoken once, with the full weight of the altar behind it. Knees obey before minds do.': "Prononcé une fois, avec tout le poids de l'autel derrière. Les genoux obéissent avant l'esprit.",
    'A psalm of judgment. Every blow lands like a verdict.': 'Un psaume de jugement. Chaque coup tombe comme un verdict.',
    'Palms pressed to the wound, and a prayer older than the parish.': 'Les paumes pressées sur la plaie, et une prière plus vieille que la paroisse.',
    'A short psalm, sung once. Everyone who hears it breathes a little easier.': "Un court psaume, chanté une fois. Tous ceux qui l'entendent respirent un peu mieux.",
    'Eight legs, a patient heart, and every crack in the wall a road.': 'Huit pattes, un cœur patient, et chaque fissure du mur est une route.',
    'A black shape in the branches. The last thing the deer never saw.': "Une forme noire dans les branches. La dernière chose que le cerf n'a jamais vue.",
    'Amber sap, warm as blood, sealing the wound like bark over a cut.': "Une sève ambrée, chaude comme le sang, qui scelle la plaie comme l'écorce une entaille.",
    'A wild bull from before the plough. It does not stop for walls.': "Un taureau sauvage d'avant la charrue. Il ne s'arrête pas devant un mur.",
    'Green shoots burst through the ground and wrap the wounded in soft leaves.': 'Des pousses vertes percent le sol et enveloppent les blessés de feuilles tendres.',
    'A crackling shard of something that should not be here. It leaves frost on the bones.': 'Un éclat crépitant de quelque chose qui ne devrait pas être là. Il laisse du givre sur les os.',
    'A name whispered to the patron. From then on, everything finds a way through.': 'Un nom murmuré au patron. Dès lors, tout trouve un passage.',
    'A voice inside the skull, reciting every fear in order.': "Une voix dans le crâne, qui récite chaque peur dans l'ordre.",
    'Skin grays, lips crack, and the life drains toward a hungry dark.': "La peau grisonne, les lèvres se fendent, et la vie s'écoule vers un noir affamé.",
    'A shadow falls over the eyes. The patron watches; the victim cannot.': 'Une ombre tombe sur les yeux. Le patron regarde ; la victime ne le peut plus.',
}

# Slot frames (base_set.FRAMES): name, swap time, reminder
FRAME_TEXT = {
    "Armor": "Armure", "Hand": "Main", "Jewelry": "Bijou", "Item": "Objet", "Rune": "Rune",
    "Third Hand": "Troisième Main", "Second Jewel": "Second Bijou", "Great Backpack": "Grand Sac à dos", "Runestone": "Pierre runique",
    "Swap: 10 minutes": "Échange : 10 minutes", "Swap: free interaction": "Échange : interaction gratuite",
    "Swap: free, once per turn": "Échange : gratuit, 1 fois par tour", "Swap: free · Spellbook: 1 action": "Échange : gratuit · Livre : 1 action",
    "Swap: long rest": "Échange : long repos", "Pack (3 at most) or Party Stash": "Sac (3 au plus) ou Réserve",
    "Empty: **+10 ft Speed**.": "Vide : **+4 m de Vitesse**.",
    "One Weapon, Shield or Instrument.": "Une Arme, un Bouclier ou un Instrument.",
    "Empty: grapple, or hold a Spellbook to cast.": "Vide : empoigner, ou tenir un Livre de sorts pour lancer.",
    "Rings, amulets, circlets, cloaks, gloves, boots.": "Anneaux, amulettes, diadèmes, capes, gants, bottes.",
    "A Spellbook, a Recipe, or up to 3 identical Consumables.": "Un Livre de sorts, une Recette, ou jusqu'à 3 Consommables identiques.",
    "A Trait, Technique, Domain or WIL deck.": "Un Trait, une Technique, un Domaine ou un paquet de VOL.",
    "Extra Gear Slot: a spectral arm, a familiar, a living tail.": "Emplacement de Matériel supplémentaire : un bras spectral, un familier, une queue vivante.",
    "Never lost, traded or stored.": "Jamais perdu, échangé ni rangé.", "Extra Gear Slot.": "Emplacement de Matériel supplémentaire.",
    "Holds one Rune, or nothing.": "Contient une Rune, ou rien.",
    "**Capture:** 1 action · **Etch:** long rest · **Release:** free": "**Capturer :** 1 action · **Graver :** long repos · **Libérer :** gratuit",
}

DAMAGE = {"Physical": "Physique", "Lightning": "Foudre", "Poison": "Poison"}

STARTER_KEYS = {"Armor": "Armure", "Hands": "Mains", "Jewelry": "Bijou", "Items": "Objets", "Runes": "Runes"}


def ability_words(s):
    """STR / WIL → FOR / VOL wherever they stand as words."""
    return re.sub(r"\b(STR|WIL)\b", lambda m: ABBR[m[1]], s)


def text(t, missing):
    """One paragraph of card text in French (generated weapon, Domain and Wound lines are rebuilt)."""
    if t in TEXT:
        return TEXT[t]
    m = re.fullmatch(r"([+−-]\d+) to hit, (?:(thrown|range) (\d+)/(\d+) ft, )?(.+?) \+ ((?:STR|DEX|INT|WIL)(?: or (?:STR|DEX|INT|WIL))*)"
                     r" (Physical|Lightning)\.(?: (.*))?", t)
    if m:
        reach = f"{ {'thrown': 'lancer', 'range': 'portée'}[m[2]]} {feet(m[3])}/{feet(m[4])} m, " if m[2] else ""
        abil = " ou ".join(ABBR[a] for a in m[6].split(" or "))
        rest = f" {text(m[8], missing)}" if m[8] else ""
        return f"{m[1]} au toucher, {reach}{m[5]} + {abil} {DAMAGE[m[7]]}.{rest}"
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


# What a Rune card prints in small above its name: Rune du / de la / de l' / des (DESIGN 1b)
RUNE_DE = {
    'Bond': 'du',
    'Sang de pierre': 'du',
    'Volonté de fer': 'de la',
    'Esprit clair': "de l'",
    'Enchaînement': "de l'",
    'Visée juste': 'de la',
    'Coup de bouclier': 'du',
    'Hymne de bataille': "de l'",
    'Cri de ralliement': 'du',
    'Mur de boucliers': 'du',
    'Larcin': 'du',
    'Ménestrel': 'du',
    'Navigation': 'de la',
    'Ruelles': 'des',
    'Traque': 'de la',
    'Guérison': 'de la',
    'Taverne': 'de la',
    'Forge': 'de la',
    'Cimes': 'des',
    'Double frappe': 'de la',
    'Second souffle': 'du',
    'Nerf': 'du',
    'Yeux de nuit': 'des',
    'Bravade': 'de la',
    'Voltige': 'de la',
    'Herboriste': "de l'",
    'Coup balayant': 'du',
    'Acharnement': "de l'",
    'Meute': 'de la',
    'Ténacité': 'de la',
    'Yeux de crépuscule': 'des',
    'Socle': 'du',
    'Chance': 'de la',
    'Campagne': 'de la',
    'Discipline': 'de la',
    'Archerie': "de l'",
    'Rempart': 'du',
    'Duel': 'du',
    'Armes lourdes': 'des',
    'Lancer vif': 'du',
    'Rage': 'de la',
    'Ruse': 'de la',
    'Garde sans armure': 'de la',
    'Arts martiaux': 'des',
    'Expertise': "de l'",
    'Recouvrement arcanique': 'du',
    'Bibliothèque': 'de la',
    'Cour': 'de la',
    'Contrées sauvages': 'des',
    'Duperie': 'de la',
    'Ascèse': "de l'",
}


def rune_de(name):
    return "Rune " + RUNE_DE[name]
