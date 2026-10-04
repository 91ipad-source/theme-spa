# -*- coding: utf-8 -*-
"""Mesurer la part du cadre occupee par le produit, et le bord du collage.

A LIRE D'ABORD : ces mesures se font sur les fichiers RECUPERES DU CDN, pas
sur les fichiers locaux. Les fichiers locaux sont corrects par construction ;
ce qui compte, c'est ce que le visiteur telecharge.

    python3 mesurer.py part   liste.txt dossier    -> la part du cadre
    python3 mesurer.py fond   liste.txt dossier    -> une couture visible ?

« liste.txt » : une ligne par photo, « nom url ». « dossier » : ou sont les
fichiers deja telecharges (nom.png).
"""
import sys
import numpy as np
from PIL import Image

SEUIL_FOND = 12   # ecart au blanc a partir duquel un pixel est du produit


def boite(a):
    contenu = (255 - a.min(axis=2)) > SEUIL_FOND
    ys, xs = np.nonzero(contenu)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def part(noms, dossier):
    print('%-14s %-11s %8s %8s' % ('spa', 'cadre', 'produit', 'part'))
    parts = []
    for n in noms:
        im = Image.open('%s/%s.png' % (dossier, n)).convert('RGB')
        x0, y0, x1, y1 = boite(np.asarray(im, dtype=np.int16))
        w, h = x1 - x0, y1 - y0
        p = max(w, h) / max(im.size)
        parts.append(p)
        print('%-14s %-11s %8s %7.1f%%' % (n, '%dx%d' % im.size, '%dx%d' % (w, h), p * 100))
    print('\nplus petit : %.1f %%   plus grand : %.1f %%   ecart : %.1f point'
          % (min(parts) * 100, max(parts) * 100, (max(parts) - min(parts)) * 100))


def fond(noms, dossier):
    """Tout pixel clair MAIS pas blanc est peint en rouge.

    C'est le seul controle qui ait servi a quelque chose. Les mesures
    chiffrees de « saut au bord du rectangle » donnent toutes le meme
    resultat, parce que le maximum tombe toujours sur le contour du produit
    lui-meme, pas sur la couture. L'oeil, lui, tranche en une seconde :
    un fond propre reste blanc, une plaque grise apparait en rouge franc.
    """
    for n in noms:
        a = np.asarray(Image.open('%s/%s.png' % (dossier, n)).convert('RGB'), dtype=np.int16)
        lum = a.mean(axis=2)
        sat = a.max(axis=2) - a.min(axis=2)
        masque = (lum >= 238) & (lum <= 253.5) & (sat <= 10)
        v = a.astype(np.uint8).copy()
        v[masque] = [220, 30, 60]
        Image.fromarray(v).save('%s/%s-fond.png' % (dossier, n))
        print('%-14s %5.1f %% du cadre en clair-non-blanc -> %s-fond.png' % (n, masque.mean() * 100, n))


if __name__ == '__main__':
    quoi, liste, dossier = sys.argv[1], sys.argv[2], sys.argv[3]
    noms = [l.split()[0] for l in open(liste) if l.strip()]
    {'part': part, 'fond': fond}[quoi](noms, dossier)
