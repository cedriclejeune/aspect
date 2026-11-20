# Découpe à la Cricut

Fichiers de coupe pour `rules/fr/Porteurs-Set-de-base.pdf` (et l'édition anglaise, même mise en page). Refaits par `tools/cut_svg.py` après `tools/build_cards.py`.

| Fichier | Pages du PDF | Coupe |
|---|---|---|
| `cartes.svg` | 2, 4, 6 … 46 | 9 cartes (coupées à 65 × 90 mm), coins arrondis |
| `cartes-2.svg` | 48 | les 8 dernières cartes |
| `larges.svg` | 50, 52 … 64 | 4 cartes larges (cartes de Décompte, Adversaires) — page couchée, posée debout |
| `cadres.svg` | 66 à 72 | 8 cadres d’Emplacement (coupés à 67 × 98 mm) et leurs 2 fentes — page couchée, posée debout |
| `cadres-2.svg` | 73 | les 7 derniers cadres — page couchée, posée debout |

On coupe le **recto** de chaque feuille recto verso ; les pages de verso n'ont pas de fichier.

## Marche à suivre

1. **Imprimer** à 100 % (« taille réelle », sans « ajuster à la page »), recto verso.
2. Dans Design Space : **Téléverser** le SVG. Vérifier sa taille : **233,95 × 298,45 mm**, pour tous les fichiers.
3. Le fichier arrive en **un seul calque** : les coupes gardent leur place, rien à joindre. Ne pas **Désassembler** le calque. Les deux petits carrés de coin servent à garder la position : celui du haut tombe sur le tapis, hors de la feuille, celui du bas dans le coin de la feuille.
4. **Réaliser**, sur un tapis de **12 × 24 po**. Dans l'aperçu du tapis, laisser le dessin dans le coin en haut à gauche.
5. Poser la feuille recto vers le haut, son coin en haut à gauche sur les lignes **1 po** du haut et de gauche du tapis, bien d'équerre. Matériau : papier cartonné.
   - Pages de cartes : debout, le haut de la page vers le haut du tapis.
   - Pages en paysage (`larges`, `cadres`) : debout aussi, le **haut de l'impression tourné vers la droite**.

## Calibrage

Les fichiers actuels sont corrigés pour la Cricut de Cédric. Feuille dans le coin du tapis, la coupe tombait 7,35 mm trop à droite et 6,35 mm trop bas ; la feuille est posée 1 po (25,4 mm) plus loin du coin, d'où

```
.venv/bin/python tools/cut_svg.py --lang fr --dx 18.05 --dy 19.05
```

Pour recalibrer (autre imprimante, autre façon de poser la feuille) : imprimer `calibrage-impression.pdf` à 100 %, couper `calibrage.svg` dessus de la même façon que les cartes, et lire le chiffre où chaque fente croise sa règle **dx** ou **dy**. Ce chiffre est la correction à ajouter aux valeurs ci-dessus. Les trois paires de règles (haut gauche, milieu, bas droite) doivent donner la même lecture ; sinon, l'impression n'est pas à 100 % ou la feuille est de travers.

Les cartes et les cadres s'impriment à **95 %** de leur taille (cartes 60 × 84 mm, larges 120 × 84 mm, cadres 64 × 93 mm), centrés là où la coupe passe. La coupe, elle, reste à la taille d'origine : 1 mm en dehors d'une carte de 63 × 88 mm (126 × 88 mm pour les larges), sur le bord d'un cadre de 67 × 98 mm. Il reste ainsi environ 2,6 mm de marge blanche autour de chaque carte et 1,7 mm autour de chaque cadre : un petit écart de la Cricut ne mord pas dans la bordure. Les fentes des cadres suivent la réduction. Le facteur est `PRINT_SCALE`, dans `tools/build_cards.py` et `tools/cut_svg.py`.

## Recto verso

L'imprimante décale le verso par rapport au recto. Les versos des pages de cartes (pages 2 à 67) sont donc décalés de **2 mm vers la gauche** (vus côté verso) pour compenser : c'est le réglage `BACK_SHIFT` de `tools/build_cards.py`. Les pages en paysage (retournement sur le bord court) ne sont pas décalées.

Pour remesurer (autre imprimante) : imprimer `rules/fr/calibrage-recto-verso.pdf` en recto verso, bord long, avec les mêmes réglages que les cartes. Tenir la feuille devant une lumière, verso vers soi, et lire où chaque croix croise ses règles **dx** et **dy** : ces chiffres sont le décalage à donner.

```
.venv/bin/python tools/build_cards.py --lang fr --back-dx DX --back-dy DY
```
