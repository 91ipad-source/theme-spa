# -*- coding: utf-8 -*-
"""Mesurer la couleur du fond d'une photo de produit.

Ce module ne contient plus qu'une fonction. Il en portait trois autres, qui
tentaient de blanchir le fond par des regles de luminance ; elles sont
racontees — et enterrees — en tete de « traiter.py ».
"""
import numpy as np
from PIL import Image


def mesurer_fond(rgb):
    """La couleur du fond, lue sur l'anneau de bord, pixels neutres seulement.

    L'anneau fait 1,5 % du cote. On n'y retient que les pixels gris (moins de
    douze niveaux d'ecart entre canaux) et clairs (au-dessus de 150) : le
    reste est du produit qui mord le cadre.

    Rend None si ces pixels-la font moins du quart de l'anneau. On ne sait
    alors pas ce qu'est le fond, et une photo de detail n'en montre de toute
    facon pas.

    ATTENTION, LE PIEGE EST CONNU : un gros plan de cuve en acrylique blanc
    presente un anneau clair et neutre, et cette fonction rend alors la
    couleur de l'ACRYLIQUE en croyant mesurer un fond. « traiter.py » s'en
    protege apres coup, en verifiant que le produit ne touche pas le cadre.
    """
    h, w, _ = rgb.shape
    b = max(3, int(min(h, w) * 0.015))
    anneau = np.concatenate([rgb[:b].reshape(-1, 3), rgb[-b:].reshape(-1, 3),
                             rgb[:, :b].reshape(-1, 3), rgb[:, -b:].reshape(-1, 3)])
    lum = anneau.mean(axis=1)
    sat = anneau.max(axis=1) - anneau.min(axis=1)
    clair = anneau[(sat <= 12) & (lum >= 150)]
    if len(clair) < 0.25 * len(anneau):
        return None
    return float(np.median(clair.mean(axis=1)))
