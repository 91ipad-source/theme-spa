# -*- coding: utf-8 -*-
"""Recomposition, version 2 : le fond est ramene au blanc cote par cote.

CE QUI CLOCHAIT. La version 1 mesurait le fond sur UN SEUL anneau, tout
autour du cadre, et en prenait la mediane. Sur le Proto 2 de survol, le haut
du cadre est a 253-255 (un mur blanc) et le bas a 250 (un sol gris) : la
mediane de l'anneau tombait au-dessus du seuil, aucune correction n'etait
faite, et le sol gris se retrouvait colle au milieu d'une marge blanche —
avec un bord net, vertical, parfaitement visible sur fond blanc.

CE QU'ON FAIT. On mesure les quatre cotes separement et on retient le plus
sombre des quatre (en ignorant ceux que le produit touche). Un sol a 250 sous
un mur a 255 est donc vu, et le point blanc est cale sur lui.

POURQUOI C'EST SANS DANGER. Le releve est au plus de 255/240, soit 6 %. Sur
l'acrylique le plus clair cela deplace un 240 vers 255 ; sur l'habillage
anthracite, un 60 vers 64. Aucune forme, aucun modele, aucun reflet n'est
redessine : c'est le reglage de point blanc d'un labo photo, pas un detourage.
"""
import numpy as np
from PIL import Image

CIBLE = 0.88
SEUIL_FOND = 12


def fond_par_cote(rgb):
    """Le plus sombre des quatre bords, parmi ceux qui sont clairs et neutres."""
    h, w, _ = rgb.shape
    b = max(3, int(min(h, w) * 0.015))
    cotes = [rgb[:b], rgb[-b:], rgb[:, :b], rgb[:, -b:]]
    valeurs = []
    for c in cotes:
        px = c.reshape(-1, 3)
        lum = px.mean(axis=1)
        sat = px.max(axis=1) - px.min(axis=1)
        clair = lum[(sat <= 12) & (lum >= 150)]
        # un cote que le produit mord est ecarte : il n'est pas du fond
        if len(clair) < 0.6 * len(px):
            continue
        valeurs.append(float(np.median(clair)))
    return min(valeurs) if valeurs else None


def boite(rgb):
    contenu = (255 - rgb.min(axis=2)) > SEUIL_FOND
    ys, xs = np.nonzero(contenu)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def recomposer(chemin, sortie, cible=CIBLE):
    im = Image.open(chemin).convert('RGB')
    rgb = np.asarray(im, dtype=np.float32)

    fond = fond_par_cote(rgb)
    releve = None
    if fond is not None and 240 <= fond < 255:
        rgb = np.clip(rgb * (255.0 / fond), 0, 255)
        im = Image.fromarray((rgb + 0.5).astype(np.uint8))
        releve = round(fond, 1)

    x0, y0, x1, y1 = boite(np.asarray(im, dtype=np.int16))
    produit = im.crop((x0, y0, x1, y1))
    pw, ph = produit.size

    cote = max(im.size)
    facteur = (cible * cote) / max(pw, ph)
    nw, nh = max(1, round(pw * facteur)), max(1, round(ph * facteur))
    produit = produit.resize((nw, nh), Image.LANCZOS)

    cadre = Image.new('RGB', (cote, cote), (255, 255, 255))
    cadre.paste(produit, ((cote - nw) // 2, (cote - nh) // 2))
    cadre.save(sortie, optimize=True)

    avant = max(pw / im.size[0], ph / im.size[1])
    return {'avant_pct': round(avant * 100), 'apres_pct': round(max(nw, nh) / cote * 100),
            'facteur': round(facteur, 3), 'cadre': '%dx%d' % (cote, cote),
            'fond_releve': releve}


if __name__ == '__main__':
    import sys
    liste, src, dst = sys.argv[1], sys.argv[2], sys.argv[3]
    noms = [l.split()[0] for l in open(liste)]
    print('%-14s %6s %6s %7s %-11s %s' % ('spa', 'avant', 'apres', 'facteur', 'cadre', 'fond relevé'))
    for n in noms:
        r = recomposer('%s/%s.png' % (src, n), '%s/%s.png' % (dst, n))
        print('%-14s %5d%% %5d%% %7.3f %-11s %s' % (n, r['avant_pct'], r['apres_pct'],
              r['facteur'], r['cadre'], r['fond_releve'] or '—'))
