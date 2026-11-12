"""French text of the combat cheat sheet (tools/build_cheatsheet.py --lang fr).

Hand-written like the English one: when a combat rule changes in rules/fr/JOUEURS.md, update it here too.
"""

FRONT = """
<section class="page dense">
<header><h1>Actions et réactions</h1><span class="tag">PORTEURS · Aide-mémoire de combat</span></header>

<div class="economy">
  <div><b>Deux actions</b>Deux actions quelconques de la liste ci-dessous, dans n'importe quel ordre. Deux fois la même, c'est permis : Déplacement deux fois, Attaque deux fois. Pas d'actions bonus.</div>
  <div><b>Gratuit</b>Une interaction avec un objet (dégainer, ouvrir, ramasser). Parler brièvement.</div>
  <div class="react"><b>Réaction</b>Une par round, au tour de n'importe qui quand son déclencheur survient, ou à votre tour si elle n'en a pas. Récupérée au début de votre tour.</div>
</div>

<div class="cols">
<h2>Actions <small>6.3</small></h2>
<table>
<tr><th>Action</th><th>Effet</th></tr>
<tr><td>Déplacement</td><td>Déplacez-vous jusqu'à votre Vitesse. Vous pouvez le couper autour de votre autre action.</td></tr>
<tr><td>Attaque</td><td>Une attaque d'arme ou à mains nues (davantage avec des Runes comme <em>Double frappe</em>). Toute attaque peut devenir <strong>Empoigner</strong> ou <strong>Bousculer</strong>.</td></tr>
<tr><td>Incantation</td><td>Lancez un sort à 1 action, ou utilisez un pouvoir de votre matériel ou de vos Runes qui demande une action (Hymne, Complainte, muer en une Forme).</td></tr>
<tr><td>Désengagement</td><td>Votre déplacement ne provoque pas d'attaque d'opportunité ce tour-ci. <strong>Pas si vous êtes Encerclé.</strong></td></tr>
<tr><td>Esquive</td><td>Jusqu'à votre prochain tour : <strong>+3 à toutes vos Défenses</strong>. Perdu si Neutralisé ou Vitesse 0.</td></tr>
<tr><td>Aide</td><td>Avant votre prochain tour, un allié a <strong>+3</strong> à son prochain test pour une tâche, ou à sa prochaine attaque contre une créature à 2 m de vous.</td></tr>
<tr><td>Se cacher</td><td>Test d'AGI pour se cacher. Hors de vue obligatoire (abri total ou Obscurité). Échec sous 15 ou sous la Vigilance passive d'un observateur. Réussite : <strong>Invisible</strong> pour eux.</td></tr>
<tr><td>Utiliser</td><td>Utilisez une babiole, ou un matériel qui demande une action : boire ou donner une potion.</td></tr>
<tr><td>Se relever</td><td>Quitter l'état À terre.</td></tr>
<tr><td>Se tenir prêt</td><td>Choisissez un déclencheur et une action ou un déplacement. Quand il survient, dépensez votre <strong>réaction</strong> pour le faire.</td></tr>
<tr><td>Fouiller</td><td>Test d'INT pour trouver quelque chose de caché.</td></tr>
<tr><td>Se souvenir</td><td>Test d'INT pour se rappeler des connaissances.</td></tr>
<tr><td>Premiers soins</td><td>Test d'INT DD 10 : stabiliser une créature mourante.</td></tr>
<tr><td>S'échapper</td><td>Attaque à mains nues (FOR ou AGI + 2) contre la plus haute Défense de FOR / AGI de celui qui vous agrippe. Touché : vous êtes libre.</td></tr>
<tr><td>Maintenir<br><small>deux actions</small></td><td>Prolongez une Emprise : la prochaine répétition qui touche n'ajoute pas d'usure.</td></tr>
<tr><td>Autre</td><td>Tout ce que vous décrivez d'autre. Le MJ tranche.</td></tr>
</table>

<div class="box"><b>Empoigner et Bousculer <small>6.10</small></b>
Remplace une attaque. Cible à votre allonge, au plus <strong>une taille de plus</strong>. Faites une <strong>attaque à mains nues (FOR + 2)</strong> contre sa plus haute Défense de FOR ou d'AGI.
<ul>
<li><strong>Empoigner</strong> (main libre) : la cible est <strong>Agrippée</strong>. Vous pouvez la traîner : chaque mètre coûte 1 m de plus sauf si elle a 2 tailles de moins ou plus.</li>
<li><strong>Bousculer :</strong> repoussez-la de 2 m, ou mettez-la <strong>À terre</strong>.</li>
</ul></div>

<h2>Réactions</h2>
<p>Une par round. Elle fonctionne au tour de <strong>n'importe qui</strong>, y compris le vôtre.</p>
<table>
<tr><th>Réaction</th><th>Déclencheur → Effet</th></tr>
<tr><td>Attaque<br>d'opportunité</td><td>Une créature que vous <strong>voyez</strong> quitte votre allonge <strong>en se déplaçant</strong> → une attaque au corps à corps contre elle. Être poussé, se téléporter ou se Désengager ne provoque pas. <small>6.5</small></td></tr>
<tr><td>Attaque de<br>l'autre main</td><td>Vous attaquez avec une arme <strong>Légère</strong> → une attaque avec une <em>autre</em> arme Légère dans l'autre main. Pas de modificateur de caractéristique aux dégâts (sauf s'il est négatif). Les deux dans des Emplacements de Main. <small>6.9</small></td></tr>
<tr><td>Action<br>préparée</td><td>Le déclencheur nommé avec Se tenir prêt survient → effectuez l'action ou le déplacement préparé.</td></tr>
<tr><td>Sort</td><td>Un sort au temps d'incantation d'une réaction (p. ex. <em>Bouclier</em> du <em>Livre du conjurateur</em>). Demande une Main vide.</td></tr>
<tr><td>Réplique</td><td>Magie de VOL : modifiez le jet d'une créature à 24 m ou moins qui vous entend, <strong>après le jet</strong>, avant que le MJ dise s'il réussit.</td></tr>
<tr><td>Matériel et Runes</td><td>Tout pouvoir marqué <strong>Réaction</strong>. Avec déclencheur : <em>Anneau de protection</em> (une attaque vous touche → +2 à cette Défense). Sans, à votre tour : <em>Feu grégeois</em> (lancer une fiole).</td></tr>
</table>

<div class="box gold"><b>Gratuit (sans action)</b>
<ul>
<li>Une interaction avec un objet par tour.</li>
<li>Parler brièvement.</li>
<li>Se jeter À terre.</li>
<li>Mettre fin à un sort que vous avez lancé.</li>
<li>Revenir d'une Forme (à votre tour).</li>
</ul></div>

<h2>Déplacement <small>6.4</small></h2>
<table>
<tr><th>Mouvement</th><th>Coût</th></tr>
<tr><td>Case</td><td>2 m, diagonales comprises</td></tr>
<tr><td>Terrain difficile</td><td>+1 m par m (gravats, broussailles, l'espace d'une créature)</td></tr>
<tr><td>Se relever</td><td>Une action</td></tr>
<tr><td>Ramper</td><td>+1 m par m</td></tr>
<tr><td>Grimper / nager</td><td>+1 m par m sans vitesse d'escalade / de nage</td></tr>
<tr><td>Traîner un agrippé</td><td>+1 m par m (sauf 2 tailles de moins ou plus)</td></tr>
<tr><td>Saut en longueur</td><td>4 m + 0,8 m × FOR (moitié sans 4 m d'élan)</td></tr>
<tr><td>Saut en hauteur</td><td>1,2 m + 0,4 m × FOR (moitié sans élan)</td></tr>
</table>
<ul>
<li>Traversez un <strong>allié</strong> (terrain difficile), ou un <strong>ennemi</strong> seulement s'il a 2 tailles de plus ou de moins.</li>
<li>Vous ne pouvez pas finir votre tour dans l'espace d'une autre créature.</li>
</ul>

<div class="box"><b>Limites à votre tour</b>
<ul>
<li><strong>Premier round, premier camp :</strong> une action au lieu de deux (réaction conservée). Ignoré en <strong>embuscade</strong>.</li>
<li><strong>Neutralisé</strong> (aussi Étourdi, Inconscient) : ni actions ni réactions.</li>
<li><strong>Encerclé</strong> (3+ ennemis engagés avec vous) : pas de Désengagement.</li>
<li><strong>Agrippé / Entravé / Étourdi :</strong> Vitesse 0.</li>
<li>Arme à <strong>Chargement</strong> : un tir par action ou réaction.</li>
<li><strong>Livre de sorts :</strong> une Main vide pour lancer.</li>
<li><strong>Magie de VOL :</strong> demande votre voix (sauf un pouvoir <strong>Visuel</strong>, ou pour muer en une Forme). Pas si Neutralisé, sous l'eau ou en Forme.</li>
<li><strong>Sous Emprise :</strong> vous perdez votre tour jusqu'à ce qu'une répétition rate.</li>
</ul></div>
</div>
<footer>Les numéros de section renvoient aux Règles du joueur de Porteurs. Le particulier l'emporte sur le général : un matériel ou une Rune qui dit le contraire l'emporte.</footer>
</section>
"""

BACK = """
<section class="page dense">
<header><h1>Règles de combat</h1><span class="tag">PORTEURS · Aide-mémoire de combat</span></header>
<div class="cols">

<h2>Déroulement du combat <small>6.1</small></h2>
<ul>
<li><strong>Surprise :</strong> un camp qui approche sans être remarqué surprend l'autre et agit en premier, sans jet.</li>
<li><strong>Initiative de camp :</strong> sinon chaque camp lance <strong>d20 + la meilleure AGI</strong> de ses membres. Relancez les égalités. Un camp entièrement Invisible : avantage.</li>
<li><strong>Round</strong> (~6 s) : le premier camp joue tous ses tours, puis l'autre camp.</li>
<li>Les <strong>Boss</strong> jouent aussi un <strong>demi-tour</strong> (une action) pendant le camp des personnages.</li>
<li>Au sein d'un camp, agissez dans l'ordre convenu, un tour complet à la fois.</li>
<li><strong>Règle du premier à agir :</strong> au round 1 seulement, le premier camp a une action chacun. <strong>Embuscade</strong> (autre camp surpris) : tours complets.</li>
</ul>

<h2>Faire une attaque <small>6.6</small></h2>
<p>C'est <strong>toujours l'attaquant qui lance</strong>, contre une <strong>Défense</strong> (10 + caractéristique + bonus). Les armes visent la <strong>plus haute Défense de FOR / AGI</strong> ; les autres effets nomment la leur.</p>
<table>
<tr><th>Jet</th><th>Formule</th></tr>
<tr><td>Arme</td><td>d20 + la caractéristique qu'elle nomme (la plus haute des deux : FOR / AGI, bâton ou baguette INT / VOL) + au toucher</td></tr>
<tr><td>Sort</td><td>d20 + INT + attaque de sort du livre</td></tr>
<tr><td>Magie de VOL</td><td>d20 + VOL + Attaque imprimée</td></tr>
<tr><td>Mains nues</td><td>+2 au toucher · 1 + FOR Physique</td></tr>
<tr><td>Improvisée</td><td>+0 au toucher · 1d4 + FOR Physique</td></tr>
</table>
<ul>
<li><strong>Touché</strong> si total ≥ Défense. <strong>20 nat. :</strong> touche toujours, critique. <strong>1 nat. :</strong> rate toujours.</li>
<li><strong>Dégâts :</strong> dé de l'arme + le même modificateur. <strong>Critique :</strong> dés de dégâts deux fois, modificateurs une fois.</li>
<li><strong>Zone :</strong> un seul jet contre la Défense de chaque cible, seule la question Vous. Échec = moitié des dégâts.</li>
</ul>

<h2>Les trois questions <small>5.2</small></h2>
<p>À poser avant chaque attaque. Chacune donne <strong>un dé au plus</strong> ; les raisons contraires s'annulent au sein d'une question.</p>
<table>
<tr><th>Question</th><th>Avantage</th><th>Désavantage</th></tr>
<tr><td>Vous</td><td>Vous n'êtes pas vu</td><td>Longue portée, cible non vue, ennemi à 2 m de votre arc, vous êtes À terre, Entravé, Empoisonné…</td></tr>
<tr><td>Cible</td><td>Elle est À terre, Entravée ou Étourdie</td><td>—</td></tr>
<tr><td>Foule</td><td>Votre camp est en surnombre</td><td>Son camp est en surnombre</td></tr>
</table>
<ul>
<li>Tests et sauvegardes : seule la question <strong>Vous</strong> s'applique.</li>
<li>Chaque désavantage annule un avantage. Lancez <strong>1 + ce qui reste</strong> : gardez le plus haut (av.) ou le plus bas (désav.). 20 / 1 naturels lus sur le dé gardé.</li>
<li><strong>Avantage aux dégâts :</strong> avant de lancer, reportez les dés d'avantage restants sur les dégâts. Chacun relance tous les dégâts ; gardez le meilleur. Le désavantage reste sur l'attaque.</li>
<li>Matériel, Runes, Aide et Esquive donnent des bonus <strong>fixes</strong> (+3 / −3), pas des dés.</li>
</ul>
<div class="adv">
<span>4,5<i>4d20 ↓</i></span><span>5,5<i>3d20 ↓</i></span><span>7,2<i>2d20 ↓</i></span>
<span><b>10,5</b><i>1d20</i></span><span>13,8<i>2d20 ↑</i></span><span>15,5<i>3d20 ↑</i></span><span>16,5<i>4d20 ↑</i></span>
</div>

<h2>Engagement <small>6.5</small></h2>
<ul>
<li><strong>Engagé :</strong> à 2 m d'un ennemi, aucun des deux Neutralisé, au plus une taille d'écart.</li>
<li><strong>Surnombre</strong> (Foule) : comptez autour de la <em>cible</em>. Votre camp = vos créatures engagées avec elle. Son camp = la cible (si votre camp l'engage) + ses alliés à 2 m. Plus nombreux = 1 dé d'av., moins = 1 dé de désav. Mêmes dés pour chaque attaquant, au contact ou à distance.</li>
<li><strong>Encerclé :</strong> 3+ ennemis engagés avec vous → pas de Désengagement.</li>
</ul>

<h2>Abri <small>6.8</small></h2>
<ul>
<li><strong>Abri :</strong> +2 aux Défenses de FOR et d'AGI.</li>
<li><strong>Abri total :</strong> ne peut être visé ; bloque la vue et les zones ; permet de se cacher et d'approcher sans être vu.</li>
</ul>

<h2>États <small>8</small></h2>
<table>
<tr><th>État</th><th>Effets</th></tr>
<tr><td>Aveuglé</td><td>Rate les tests de vue. Attaques contre vous : av. ; les vôtres : désav.</td></tr>
<tr><td>Charmé</td><td>Ne peut pas blesser celui qui charme. Il a l'av. aux tests de VOL contre vous.</td></tr>
<tr><td>Effrayé</td><td>Désav. aux tests et attaques tant que la source est en vue. Ne peut s'en approcher.</td></tr>
<tr><td>Agrippé</td><td>Vitesse 0. Désav. aux attaques sauf contre celui qui agrippe. Fin s'il est Neutralisé ou si vous quittez son allonge.</td></tr>
<tr><td>Neutralisé</td><td>Ni actions, ni réactions, ni parole. Engagé avec personne.</td></tr>
<tr><td>Invisible</td><td>Ne peut être vu. Attaques contre vous : désav. ; les vôtres : av.</td></tr>
<tr><td>Empoisonné</td><td>Désav. aux attaques et aux tests de caractéristique.</td></tr>
<tr><td>À terre</td><td>Ramper ou se relever seulement. Vos attaques : désav. Attaques contre vous : un dé d'av., à toute distance.</td></tr>
<tr><td>Entravé</td><td>Vitesse 0. Attaques contre vous : av. ; les vôtres : désav.</td></tr>
<tr><td>Étourdi</td><td>Neutralisé, Vitesse 0. Attaques contre vous : av. <em>Pétrifié : + résiste à tout.</em></td></tr>
<tr><td>Inconscient</td><td>Étourdi + À terre, lâche ce qu'il tient. <strong>Tout coup à 2 m est un critique.</strong></td></tr>
</table>
<p>Les états ne se cumulent pas avec eux-mêmes.</p>

<div class="box"><b>Emprise <small>8</small></b>
<ul>
<li><strong>Touché :</strong> la cible perd son prochain tour.</li>
<li><strong>Répétition</strong> au début de chacun de ses tours, gratuite : même bonus contre la même Défense, seulement les dés d'usure. Touché : elle perd aussi ce tour. Raté : elle se libère.</li>
<li><strong>Usure :</strong> chaque répétition qui touche, et chaque fois que la source subit des dégâts, ajoute 1 dé de désavantage.</li>
<li><strong>Fin</strong> sur un échec, si la source est Neutralisée ou meurt, ou si elle le choisit. Blesser une cible Charmée la libère.</li>
</ul></div>

<h2>Dégâts <small>7.2–7.3</small></h2>
<ul>
<li>La <strong>résistance</strong> divise par deux, la <strong>vulnérabilité</strong> double (dans cet ordre, après les autres modificateurs). Deux résistances = une.</li>
<li><strong>PV temporaires :</strong> perdus en premier, ne se cumulent pas (gardez le plus haut), ne sont pas des soins, durent jusqu'à un long repos.</li>
</ul>

<h2>Tomber à 0 PV <small>7.4</small></h2>
<ul>
<li><strong>Mort instantanée</strong> si les dégâts restants ≥ votre maximum de PV.</li>
<li>Sinon <strong>Inconscient</strong> ; jet contre la mort (d20, sans modificateur) au début de chaque tour. Vous subissez une <strong>Blessure</strong> (7.6).</li>
</ul>
<table>
<tr><th>Jet contre la mort</th><th>Résultat</th></tr>
<tr><td>10+</td><td>1 réussite</td></tr>
<tr><td>9 ou moins</td><td>1 échec</td></tr>
<tr><td>20 nat.</td><td>Récupérez 1 PV</td></tr>
<tr><td>1 nat.</td><td>2 échecs</td></tr>
<tr><td>Touché à 0 PV</td><td>1 échec (2 si critique) ; mort si dégâts ≥ PV max</td></tr>
</table>
<p><strong>3 réussites :</strong> stabilisé (1 PV après 1d4 heures). <strong>3 échecs :</strong> mort. <strong>Tout soin</strong> vous réveille et remet le compte à zéro. Les <strong>Premiers soins</strong> (INT DD 10, action) stabilisent.</p>

<h2>Magie en combat <small>10</small></h2>
<ul>
<li><strong>Livre de sorts :</strong> une Main vide pour lancer. Une seule réserve de <strong>points de sort</strong> (tous les livres + INT) paie les sorts de n'importe quel livre (coût 1/2/3/4/6/8 selon le niveau, tours de magie gratuits). Évident sauf si Discret.</li>
<li><strong>Magie de VOL</strong> (Divin, Glamour, Nature) : mêmes règles, payée sur une seule réserve d'<strong>Ardeur</strong> (tous les paquets + VOL, revient au court repos). Toujours évidente.</li>
<li><strong>Formes :</strong> le matériel ne compte plus ; les PV de la Forme partent d'abord, l'excédent se reporte.</li>
</ul>

<div class="box gold"><b>Moral <small>6.11</small></b>
Quand le <strong>Meneur</strong> d'un groupe d'Adversaires tombe, et quand la moitié du groupe est hors de combat : un <strong>test de VOL (DD 10)</strong> avec sa meilleure VOL. Échec : le groupe fuit ou se rend. Les Boss n'en font jamais.</div>

<h2>Après le combat <small>7.5</small></h2>
<ul>
<li><strong>Court repos</strong> (1 h, 2 par long repos) : récupérez la moitié des PV manquants ; les utilisations C.R. et l'Ardeur reviennent ; enfiler ou ôter une Armure.</li>
<li><strong>Long repos</strong> (8 h) : tous les PV, utilisations, Ardeur et points de sort ; échanger des Runes.</li>
<li><strong>Convalescence</strong> (3 jours en lieu sûr) : comme un long repos, et guérit toutes les Blessures.</li>
</ul>
</div>
<footer>Règles d'or : la règle du plaisir · personne n'est laissé de côté · le particulier l'emporte sur le général · arrondir à l'inférieur · tout se cumule · le MJ tranche.</footer>
</section>
"""
