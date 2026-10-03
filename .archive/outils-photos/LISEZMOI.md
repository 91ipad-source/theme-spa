# Remettre au blanc le fond des photos de spas

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
