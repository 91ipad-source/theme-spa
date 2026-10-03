# -*- coding: utf-8 -*-
"""Les planches de controle : avant / apres, fiche par fiche, sur fond blanc.

LE FOND DE LA PLANCHE EST BLANC PUR, ET C'EST TOUT L'INTERET. Une photo sur
fond gris posee sur du blanc se denonce d'elle-meme : le rectangle se voit.
C'est exactement ce que le visiteur a sous les yeux dans la grille du site.
"""
import os
from PIL import Image, ImageDraw, ImageFont
import medias

TITRES = {
    'duo': 'Spa Duo — 2 places', 'doto': 'Spa Doto — 3 places',
    'proto2': 'Spa Proto 2 — 5 places', 'calypso-web': 'Spa Calypso Web — 3 places',
    'calypso': 'Spa Calypso — 3 places', 'europe': 'Spa Europe Infrared — 5 places',
    'pleuxaure': 'Spa Pleuxaure — 5 places', 'panope': 'Spa Panopé — 5 places',
    'panope-full': 'Spa Panopé FULL — 5 places', 'doro-plus': 'Spa Doro Plus — 7 places',
}
SORTS = {}
try:
    import json
    for cle, sort, fond, part in json.load(open('rapport.json')):
        SORTS[cle] = (sort, fond)
except Exception:
    pass


def police(taille):
    for c in ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        if os.path.exists(c):
            return ImageFont.truetype(c, taille)
    return ImageFont.load_default()


V, MARGE, ENTETE, LEGENDE = 260, 14, 54, 26


def planche(fiche):
    ms = medias.MEDIAS[fiche]
    n = len(ms)
    larg = 2 * V + 3 * MARGE
    haut = ENTETE + n * (V + LEGENDE + MARGE) + MARGE
    img = Image.new('RGB', (larg, haut), (255, 255, 255))
    d = ImageDraw.Draw(img)
    f_titre, f_petit = police(20), police(13)
    d.text((MARGE, 16), TITRES[fiche], font=f_titre, fill=(15, 58, 90))
    d.text((MARGE, ENTETE - 16), 'AVANT', font=f_petit, fill=(120, 140, 155))
    d.text((MARGE * 2 + V, ENTETE - 16), 'APRÈS', font=f_petit, fill=(120, 140, 155))

    y = ENTETE
    for mid, _ in ms:
        cle = '%s-%s' % (fiche, mid)
        for j, dossier in enumerate(('avant', 'apres')):
            im = Image.open('%s/%s.png' % (dossier, cle)).convert('RGB').resize((V, V), Image.LANCZOS)
            x = MARGE + j * (V + MARGE)
            img.paste(im, (x, y))
            d.rectangle([x, y, x + V - 1, y + V - 1], outline=(225, 233, 239))
        sort, fond = SORTS.get(cle, ('?', None))
        d.text((MARGE, y + V + 6), '%s — fond mesuré %s' % (sort, fond), font=f_petit,
               fill=(15, 58, 90) if sort != 'inchange' else (150, 165, 178))
        y += V + LEGENDE + MARGE
    img.save('planche-%s.png' % fiche)
    return 'planche-%s.png' % fiche


if __name__ == '__main__':
    for f in medias.MEDIAS:
        print(planche(f))
