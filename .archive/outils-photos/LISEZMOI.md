# Remettre au blanc le fond des photos de spas

> Pour l'échelle des produits dans leur cadre — un autre problème, un
> autre outil, celui-là bel et bien appliqué — voir `echelle/`.

> **L'AFFAIRE EST CLOSE — 4 octobre 2026.** Cédric a refait les photos
> lui-même : 43 nouvelles images sur blanc pur, remplaçant celles des fiches
> Doto, Calypso Web, Pleuxaure, Panopé et Panopé FULL. Mesuré sur les 43 :
> fond à 254 partout, y compris sur les gros plans que cet outil ne savait
> pas traiter. **Cet outil n'a donc jamais été appliqué.** Il reste ici pour
> le jour où le problème se représentera sur une nouvelle série de photos —
> et surtout pour la leçon en tête de `traiter.py`, qui vaut pour n'importe
> quel détourage.
>
> `medias.py` liste les fichiers du 3 octobre. Les 43 remplacés n'existent
> plus sous ces noms : `telecharger.py` échouera dessus, ce qui est le bon
> comportement. Relire la liste depuis l'API avant de s'en resservir.

Au 3 octobre 2026, les 89 photos des dix spas venaient de deux sources :
des **rendus détourés sur blanc pur** (Duo, Doto, Calypso, Proto 2) et de
**vraies photos de studio sur fond gris** (Calypso Web, Pleuxaure, Panopé,
Panopé FULL). Côte à côte dans la grille de l'accueil, le rectangle gris se
voit et la vignette paraît sale à côté de ses voisines.

Ces quatre fichiers ramènent tous les fonds au blanc. Ils ne touchent pas à
la boutique : ils lisent le CDN et écrivent en local.

## Ce qu'il faut installer

    pip install scipy rembg onnxruntime

`rembg` télécharge son modèle (`isnet-general-use`, 179 Mo) au premier appel.

## L'ordre des opérations

    python3 telecharger.py     # le CDN → avant/
    python3 traiter.py         # avant/ → apres/   (80 s, 2 processus)
    python3 planches.py        # les planches de contrôle avant/après

**Les planches sont le dernier juge.** Aucun test automatique n'a suffi ; on
les regarde, une par fiche, avant de téléverser quoi que ce soit.

## Les trois sorts, et les quatre exceptions

| sort | photos | règle |
|---|---|---|
| inchangée | 33 | fond déjà au-dessus de 252 |
| relevée | 12 | fond entre 246 et 252 : point blanc global, 3 % au plus |
| détourée | 21 | fond en dessous de 246 : modèle de détourage, puis blanc |
| gros plan | 15 | le produit touche le cadre : laissée telle quelle |
| échec | 4 | le modèle efface plus de 90 % : laissée telle quelle |
| écartée | 4 | jugée à l'œil sur les planches, voir `ECARTEES` |

L'en-tête de `traiter.py` raconte les trois méthodes essayées et jetées avant
celle-ci, et pourquoi chacune échoue. À lire avant d'en réinventer une.

## Remplacer les fichiers dans Shopify

Par `fileUpdate` et son `originalSource`, en trois temps : `stagedUploadsCreate`
rend une adresse signée, on y poste le fichier, puis `fileUpdate` pointe le
fichier **existant** vers cette adresse. Le média garde son identifiant, son
rang dans la fiche et son texte alternatif — ce qu'une suppression suivie
d'un ajout perdrait.

## Les dix affiches publicitaires

Supprimées des fiches le 3 octobre 2026 : d'anciennes affiches du fournisseur,
avec le nom du modèle et les dimensions incrustés dans l'image. Ce texte n'est
lu ni par Google ni par les lecteurs d'écran, et il répète ce que la fiche dit
déjà. Les fichiers restent accessibles par leur adresse CDN, listée dans
l'historique Git de ce dossier.

## Ce dossier n'est pas envoyé à Shopify

Shopify ne synchronise que `assets`, `blocks`, `config`, `layout`, `locales`,
`sections`, `snippets` et `templates`. Un dossier commençant par un point est
ignoré.

## Les textes alternatifs, et pourquoi ils se perdent

Les 43 nouvelles photos sont arrivées **sans texte alternatif** : remplacer
une photo par une autre ne transporte rien, et Shopify n'en invente pas. Elles
ont été réécrites une par une le 4 octobre, à partir de planches de contrôle,
dans la forme des autres : `Spa <Nom> ROCA Spa <N> places, <ce qu'on voit>`.

C'est le piège à retenir pour la prochaine fois : **téléverser une série de
photos efface silencieusement tout le travail de texte alternatif**, qui ne se
voit nulle part dans l'administration tant qu'on ne l'ouvre pas photo par
photo. La requête qui les contrôle toutes d'un coup :

    { products(first: 15, query: "product_type:Spa AND status:active") {
        nodes { handle media(first: 25) { nodes { ... on MediaImage { alt } } } } } }

## La règle du survol

Dawn affiche la **deuxième** photo d'une fiche au survol de sa vignette. Une
vue de trois quarts y est plus parlante qu'une cuve vue de dessus : on y lit
la hauteur, l'habillage et l'encombrement. Les dix fiches la respectaient au
3 octobre ; le remplacement des photos a remis le Panopé dans l'ordre du
téléversement, et il a été reclassé le 4.

**Le Spa Europe Infrared fait exception** : sa vue de trois quarts en eau
(`SpaEuropeImage22sept.2026_15_27_02_2.png`) a été retirée de la fiche le
3 ou 4 octobre, et aucune autre de ses photos n'en est une. Son survol montre
donc une vue de face. Le fichier reste servi par le CDN ; il suffirait de le
rattacher à la fiche et de le mettre en deuxième position.
