# Donner à tous les spas la même place dans leur cadre

**Appliqué le 4 octobre 2026**, sur les dix vignettes du catalogue puis sur
les dix photos de survol. Contrairement à l'outil de détourage du dossier
parent, celui-ci a bien servi.

## Le constat

Mesure du 4 octobre sur les dix photos de vignette : le spa occupait de
**76 % à 100 %** de son cadre selon le modèle. Le Doro Plus touchait les
quatre bords, le Pleuxaure flottait avec une large marge — et il paraissait
plus petit qu'un 3 places alors que c'est un 5 places.

Dans une grille, l'œil ne lit pas cet écart comme une différence de cadrage.
Il le lit comme une différence de taille du produit.

Les photos de survol, elles, étaient entre **94,5 % et 100 %**. Au survol, le
spa ne se remplaçait donc pas : il grossissait, et pas du même coup d'une
carte à l'autre.

## Ce qu'on fait, et ce qu'on ne fait pas

La photo est mise à l'échelle **uniformément** — le même facteur en largeur
et en hauteur — puis recentrée sur un carré blanc. Aucun étirement, aucun
recadrage dans le produit, aucun détourage. Un spa plat reste plat.

La cible est 88 % du cadre pour le plus grand côté du produit.

## Le résultat, mesuré sur le CDN

| | avant | après |
|---|---|---|
| vignettes — plus petite | 76 % | 88,0 % |
| vignettes — plus grande | 100 % | 88,0 % |
| survol — plus petite | 94,5 % | 88,0 % |
| survol — plus grande | 100 % | 88,0 % |

Fichiers 5 à 39 % plus légers. Deux vignettes qui n'étaient pas carrées
(Pleuxaure 1272 × 1236, Panopé FULL 1271 × 1238) sortent carrées : le thème
leur rognait une dizaine de pixels à l'affichage, ce rognage disparaît.

## La leçon : mesurer le fond **côté par côté**

La première version mesurait le fond sur **un seul anneau**, tout autour du
cadre, et en prenait la médiane. Sur la photo de survol du Proto 2, le haut
du cadre est un mur à 253-255 et le bas un sol à 246 : la médiane de l'anneau
tombait au-dessus du seuil, aucune correction n'était faite, et le sol gris
se retrouvait collé au milieu d'une marge blanche — avec un bord net,
vertical, parfaitement visible.

Un fond légèrement gris qui va jusqu'au bord du cadre ne se voit pas. Le même
fond gris **entouré de blanc** se voit immédiatement. Recomposer une photo
rend donc visible un défaut de fond qui ne l'était pas : il faut corriger le
fond **avant** de recomposer, jamais après.

D'où `fond_par_cote()` : on mesure les quatre bords séparément et on retient
le plus sombre, en écartant ceux que le produit mord. Un sol à 246 sous un
mur à 255 est alors vu, et le point blanc est calé sur lui.

Le relevé est au plus de 255/240, soit 6 %. Vérifié à 100 % sur le marbre du
Proto 2 : les volutes, les jets, les LED et l'appuie-tête sont intacts. C'est
le réglage de point blanc d'un labo photo, pas un détourage.

## L'autre leçon : les mesures chiffrées de « couture » ne servent à rien

J'ai écrit trois métriques pour détecter le bord du rectangle collé. Les
trois donnaient le même chiffre sur les dix photos, propres comme sales :
le maximum tombe toujours sur le contour du produit lui-même, qui borde le
rectangle là où le produit touche. Une médiane, elle, noie le défaut.

Ce qui tranche en une seconde, c'est `mesurer.py fond` : peindre en rouge
tout pixel clair mais pas blanc. Une plaque grise apparaît en rouge franc,
un fond propre reste blanc, et le mouchetis autour du produit est l'ombre
portée — normal.

## Les fichiers

- `recomposer.py` — met à l'échelle et recentre. `python3 recomposer.py liste.txt source destination`
- `mesurer.py` — `part` (l'occupation du cadre) ou `fond` (la détection visuelle). Sur les fichiers du CDN.
- `poster.py` — temps 2 du téléversement : poster les octets à l'adresse signée.

## Remplacer une photo sans perdre son identité

Trois temps. Le média garde son identifiant, sa position dans la fiche et son
texte alternatif — contrairement à un téléversement depuis l'admin, qui crée
un nouveau média et **efface tous les textes alternatifs de la série**.

1. `stagedUploadsCreate` (API Admin) → une adresse signée par photo ;
2. POST multipart vers cette adresse — c'est du Google Cloud Storage, aucun
   jeton Shopify n'intervient ; c'est ce que fait `poster.py` ;
3. `fileUpdate(files: [{id, originalSource}])` avec l'identifiant du média
   et l'URL renvoyée au temps 1.

Après le temps 3, `image` reste `null` quelques dizaines de secondes : le
traitement n'est pas fini. Re-interroger jusqu'à obtenir une URL avec un
nouveau `?v=`, puis **re-télécharger depuis le CDN et re-mesurer**. Tant
qu'on n'a pas fait ça, on n'a rien vérifié.
