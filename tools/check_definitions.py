"""Check that the Player Rules define each term before using it: first use against first bold appearance.
Usage: python3 tools/check_definitions.py fr|en. Rule and tree: rules/DESIGN.md, Order of definitions."""
import re, sys, pathlib
lang = sys.argv[1]
f = {'fr': 'rules/fr/JOUEURS.md', 'en': 'rules/PLAYERS.md'}[lang]
TERMS = {'fr': """Porteur|Compagnie|Vocation|matériel|Rune|Pierre runique|Pierre vierge|carte|Emplacement|équipement|caractéristique|modificateur|Défense|Points de vie|PV|Vitesse|totaux|carte de Décompte|carte de Porteur|affinité|effet|abilité|test|DD|jet d'attaque|20 naturel|avantage|désavantage|état|Aide|tour|action|réaction|round|interaction gratuite|court repos|long repos|convalescence|Vigilance passive|Obscurité|Invisible|Rang|bonus|mots-clés|type|utilisation|Consommable|Recette|Livre de sorts|Instrument|Bijou|Sac|Réserve de la Compagnie|pièce|Contenant|Bourse|Capturer|Graver|Libérer|temps d'échange|au toucher|Boss|initiative|Surnombre|Engagé|engagé|Encerclé|encerclé|attaque d'opportunité|allonge|Coup critique|coup critique|abri total|abri|Agrippé|À terre|Neutralisé|Meneur|PV temporaires|Inconscient|Blessure|jets contre la mort|stabilis|Emprise|usure|magie d'Intelligence|Pouvoir|points de sort|tours de magie|Surpuissance|Discret|Rune de Pouvoirs|Ardeur|Hymne|Complainte|Réplique|Soin|Forme|Focaliseur|Dés du destin|jalon|saga|quête|épreuve|Trait|Technique|Domaine|Physique|Durée|zone|portée|Désengag|Esquive|Bousculer|Empoigner|résistance|cadre|Méditer|dormante|Réveiller""",
 'en': """Bearer|Party|Calling|gear|Rune|Runestone|blank Runestone|card|Slot|equipment|ability|modifier|Defense|Hit Points|HP|Speed|totals|tally card|Bearer card|affinit|effect|power|check|DC|attack roll|natural 20|advantage|disadvantage|condition|Help|turn|action|reaction|round|free object interaction|short rest|long rest|downtime|passive Awareness|Dark|Invisible|Rank|bonus|Keyword|type|uses|Consumable|Recipe|Spellbook|Instrument|Jewelry|Pack|Party Stash|piece|Container|Purse|Capture|Etch|Release|swap time|to-hit|Boss|initiative|Outnumbered|Engaged|engaged|Surrounded|surrounded|opportunity attack|reach|Critical hit|critical hit|full cover|cover|Grappled|Prone|Incapacitated|Leader|Temporary HP|Unconscious|Wound|death saves|stable|Subdue|decay|INT magic|WIL magic|spell points|cantrip|Upcast|Subtle|WIL deck|Resolve|Anthem|Dirge|Cue|Mend|Form|Focus|Fate dice|milestone|story|quest|trial|Trait|Technique|Domain|Physical|Duration|area|range|Disengag|Dodge|Shove|Grapple|resistance|frame|Tend|Dormant|Wake"""}[lang].split('|')
L = pathlib.Path(f).read_text().split('\n')
a = next(i for i, l in enumerate(L) if l.startswith('## 1. ')); b = next(i for i, l in enumerate(L) if l.startswith('## 11. '))
sec = ''; rows = []
secs = []
for i in range(a, b):
    if L[i].startswith('#'): sec = L[i].lstrip('# ')[:28]
    secs.append(sec)
for t in TERMS:
    ci = t[0].islower()
    pat = re.compile(r'(?<![\w])' + re.escape(t), re.I if ci else 0)
    use = dfn = None
    for i in range(a, b):
        l = L[i]
        if use is None and pat.search(l): use = i
        if dfn is None and (any(pat.search(x) for x in re.findall(r'\*\*(.+?)\*\*', l)) or (l.startswith('#') and pat.search(l)) or (l.startswith('| **') and pat.search(l.split('|')[1]))): dfn = i
        if use is not None and dfn is not None: break
    if dfn is None: rows.append((use or 0, t, 'NEVER BOLD', secs[use - a] if use else '-', ''))
    elif use < dfn: rows.append((use, t, 'USED %d lines early' % (dfn - use), secs[use - a], secs[dfn - a] + ' | ' + L[use][:110]))
for r in sorted(rows): print('%-22s %-22s %-28s -> %s' % (r[1], r[2], r[3], r[4]))
