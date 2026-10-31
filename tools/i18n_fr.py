"""French strings for the drawn figures (tools/illustrations.py) and the PDF builders.

illustrations.set_lang("fr") makes every SVG text go through ILLUSTRATIONS (exact match; an all-caps string
matches its key in capitals). Strings not listed stay as they are, so numbers and already-French text pass through.
Distances follow the French convention of the fifth-edition translation: 5 ft = 1,5 m (see FEET).
"""

# feet → metres, French style (1 square = 1,5 m)
def feet(n):
    """30 → "9", 35 → "10,5", 2.5 → "0,75"."""
    m = round(float(n) * 0.3, 2)
    s = f"{m:g}".replace(".", ",")
    return s


def signed_feet(v):
    """A strip value in feet ("+5", "−10", "35") → metres ("+1,5", "−3", "10,5")."""
    v = str(v)
    sign = v[0] if v[0] in "+−-" else ""
    num = v[1:] if sign else v
    return (sign.replace("-", "−")) + feet(num)


ILLUSTRATIONS = {
    # figure labels
    "Trial": "Épreuve", "Gather": "Ramasser", "Rest &amp; Rebuild": "Repos et reconstruction",
    "DUELIST": "DUELLISTE", "Calling: STR · DEX": "Vocation : FOR · DEX", "HP · Speed · perk": "PV · Vitesse · atout",
    "Armor": "Armure", "Hands": "Mains", "Jewelry": "Bijou", "Items": "Objets", "Aspects": "Aspects",
    "Leather": "Cuir", "Finesse Blade": "Lame fine", "Dagger": "Dague", "Ring of Warding": "Anneau de protection",
    "Potion ×1": "Potion ×1", "empty": "vide", "Cat Burglar": "Monte-en-l'air", "Springheel": "Talons-ressorts",
    "Iron Will": "Volonté de fer", "Stash": "Réserve", "unequipped cards": "cartes non équipées",
    "swap at rests": "échangées aux repos",
    "Duelist": "Duelliste", "Calling": "Vocation", "Symbols": "Symboles", "its two abilities": "ses deux caractéristiques",
    "Own values": "Valeurs propres", "+2 in its two abilities": "+2 à ses deux caractéristiques", "HP, Speed": "PV, Vitesse",
    "Keyword": "Mot-clé", "Name": "Nom", "Perk": "Atout",
    "**Reaction (1/S.R.)**,": "**Réaction (1/R.C.)**,", "when an attack hits you:": "quand une attaque vous touche :",
    "reduce its damage by 5.": "réduisez ses dégâts de 5.", "Warden's Plate": "Plates du gardien",
    "Armor · Noisy 3": "Armure · Bruyante 3", "Type": "Type", "Property": "Propriété", "Rank": "Rang", "I to V": "de I à V",
    "who can equip it": "qui peut l'équiper", "Bonus strip": "Bande de bonus", "abilities": "caractéristiques",
    "Defenses (in a shield)": "Défenses (dans un bouclier)", "Keywords": "Mots-clés", "type first": "le type d'abord",
    "Effect": "Effet",
    "Tally": "Décompte", "TALLY": "DÉCOMPTE", "CURRENT HP": "PV ACTUELS", "TEMP HP": "PV TEMP.", "DEATH SAVES": "JETS CONTRE LA MORT",
    "Totals": "Totaux", "four modifiers": "quatre modificateurs", "four Defenses": "quatre Défenses",
    "HP maximum, Speed": "PV maximum, Vitesse", "Current HP": "PV actuels", "cross out, rewrite": "barrer, réécrire",
    "Temp HP": "PV temporaires", "Death saves": "Jets contre la mort", "successes, failures": "réussites, échecs",
    "IN PLAY: SPREAD OUT BY SLOT": "EN JEU : ÉTALÉES PAR EMPLACEMENT", "CALLING": "VOCATION", "ARMOR": "ARMURE",
    "HANDS": "MAINS", "JEWELRY": "BIJOU", "ITEM": "OBJET", "ASPECTS": "ASPECTS",
    "Templar": "Templier", "Mail": "Mailles", "Shield": "Bouclier", "Versatile Weapon": "Arme polyvalente",
    "Weapon · Versatile": "Arme · Polyvalente", "Jewelry · Reaction": "Bijou · Réaction", "Potion of Healing": "Potion de soins",
    "Consumable": "Consommable", "Trait": "Trait", "Barkeep": "Tavernier", "Knack": "Savoir-faire",
    "ADDING UP: TALLY, CALLING, THEN EACH CARD ON TOP": "ADDITION : DÉCOMPTE, VOCATION, PUIS CHAQUE CARTE PAR-DESSUS",
    "Spring.": "Talons", "Each row reads left to right,": "Chaque ligne se lit de gauche à droite,",
    "like a written sum:": "comme une addition écrite :", "STR Defense": "Défense de FOR",
    "+2 Shield + 3 Armor": "+2 Bouclier + 3 Armure", "+ 12 Calling = 17": "+ 12 Vocation = 17", "HP": "PV",
    "+2 + 2 Traits + 4 Armor + 14 = 22": "+2 + 2 Traits + 4 Armure + 14 = 22",
    "Cards with an empty strip": "Les cartes à la bande vide", "stay out of the stack.": "restent hors de la pile.",
    "Hand": "Main", "Swap: 10 minutes": "Échange : 10 minutes", "Swap: free interaction": "Échange : interaction gratuite",
    "Empty: **+10 ft Speed**.": "Vide : **+3 m de Vitesse**.", "Weapon": "Arme", "Slot": "Emplacement",
    "symbol and name": "symbole et nom", "Swap time": "Temps d'échange", "Slit": "Fente",
    "the card's corner tucks under it": "le coin de la carte s'y glisse", "on the frame's edge": "sur le bord du cadre",
    "opposite corner": "coin opposé", "Empty: it shows what the Slot does": "Vide : il montre ce que fait l'Emplacement",
    "Framed: the card is equipped": "Encadrée : la carte est équipée", "cut": "couper", "+10": "+3",
    "Small edge": "Petit avantage", "Defining": "Déterminant", "Strong": "Puissant", "Bends rules": "Plie les règles",
    "Breaks rules": "Brise les règles",
    "Side A": "Camp A", "won initiative": "a gagné l'initiative", "Side B": "Camp B", "Round 1": "Round 1",
    "Round 2": "Round 2", "Round 3": "Round 3", "Move OR Action": "Déplacement OU Action", "Full turns": "Tours complets",
    "A Boss on Side A also takes a half turn (one action) during Side B, the characters' side.": "Un Boss du camp A joue aussi un demi-tour (une action) pendant le camp B, celui des personnages.",
    "Within a side, creatures act in any order they agree on.": "Au sein d'un camp, les créatures agissent dans l'ordre dont elles conviennent.",
    "Ambush: if the other side is surprised, Side A takes full turns in round 1.": "Embuscade : si l'autre camp est surpris, le camp A joue des tours complets au round 1.",
    "Opportunity attack": "Attaque d'opportunité", "E leaves F's reach (gold): F may use": "E quitte l'allonge de F (en or) : F peut utiliser",
    "its reaction to make one melee attack.": "sa réaction pour faire une attaque au corps à corps.", "Cover": "Abri",
    "T behind the wall's edge: cover, +2 STR and DEX Defense.": "T derrière le bout du mur : abri, +2 Défenses de FOR et de DEX.",
    "H fully hidden by the wall: can't be targeted.": "H entièrement caché par le mur : ne peut être visé.",
    "Successes": "Réussites", "Failures": "Échecs", "3 = stable": "3 = stabilisé", "3 = death": "3 = mort",
    "d20, no modifiers, at the start of each turn at 0 HP: 10+ succeeds.": "d20, sans modificateur, au début de chaque tour à 0 PV : 10+ réussit.",
    "Natural 20: regain 1 HP. Natural 1: two failures.": "20 naturel : récupérez 1 PV. 1 naturel : deux échecs.",
    "Damage at 0 HP: one failure (two on a critical hit). Any healing: back up.": "Dégâts à 0 PV : un échec (deux sur un critique). Tout soin : debout.",
    "Plate": "Plates", "+2 STR · +1 DEX": "+2 FOR · +1 DEX", "+2 HP · +5 ft": "+2 PV · +1,5 m", "+3 STR": "+3 FOR",
    "+4 HP": "+4 PV", "+4 STR": "+4 FOR", "+12 HP · −10 ft": "+12 PV · −3 m", "+2 STR · +2 DEX": "+2 FOR · +2 DEX",
    "one Hand": "une Main",
    "Cone": "Cône", "Cube": "Cube", "Cylinder": "Cylindre", "Emanation": "Émanation", "Line": "Ligne", "Sphere": "Sphère",
}

# figure keys (heading starts) and captions for the French Player Rules (tools/build_pdf.py FIGURES)
FIGURE_KEYS = {
    "Story, Quests & Trials": "Saga, quêtes et épreuves",
    "3.2 Your Slots": "3.2 Vos Emplacements",
    "6.1 Order of Combat": "6.1 Déroulement du combat",
    "6.5 Engagement": "6.5 Engagement",
    "7.4 Falling to 0 HP": "7.4 Tomber à 0 PV",
    "9.1 Armor": "9.1 Armure",
    "10.5 Areas of Effect": "10.5 Zones d'effet",
}
CAPTIONS = {
    "Story, Quests & Trials": "Enchaînez les épreuves directement après le ramassage ; reposez-vous (pointillés) quand la Compagnie en a besoin. Quelques épreuves font une quête ; quelques quêtes font une saga.",
    "calling": "Une carte de Vocation : ses propres valeurs dans la bande. Vos totaux vont sur la carte de Décompte (12.3).",
    "card": "Où se trouve chaque élément d'une carte.",
    "rank": "Le Rang I est un petit avantage ; le Rang V brise les règles.",
    "3.2 Your Slots": "Un Duelliste débutant : Vocation, Armure, deux Mains, Bijou, deux Objets et trois Aspects.",
    "tally": "La carte de Décompte, la seule carte sur laquelle on écrit.",
    "frame": "Un cadre d'Armure vide, et un cadre de Main qui tient une arme par deux fentes en coin.",
    "totals": "Les cartes de Bram en jeu à côté de sa carte de Décompte (en haut), et empilées dessus pour l'addition (en bas).",
    "6.1 Order of Combat": "Initiative de camp : les vainqueurs ouvrent avec un demi-tour, puis les camps alternent des tours complets.",
    "6.5 Engagement": "Allonge, attaques d'opportunité et abri sur la grille.",
    "7.4 Falling to 0 HP": "La piste des jets contre la mort.",
    "9.1 Armor": "Cuir, Mailles, Plates et le bouclier, avec leurs bonus de Défense.",
    "10.5 Areas of Effect": "Zones d'effet. Le point noir marque le point d'origine.",
}
