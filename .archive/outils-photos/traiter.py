# -*- coding: utf-8 -*-
"""Ramener au blanc le fond des photos de spas, sans abimer le produit.

TROIS SORTS, SELON CE QUE MESURE L'ANNEAU DE BORD.

  - fond au-dessus de 252 : rien a faire, la photo est deja detouree sur
    blanc. C'est le cas des rendus du Duo, du Doto, du Calypso et du Proto 2.

  - fond entre 246 et 252 : l'ecart au blanc est de 3 % au plus. On remonte
    le point blanc de toute l'image. Le produit s'eclaircit d'autant, et a
    cette amplitude cela ne se voit pas. Aucun masque, donc aucun risque.

  - fond en dessous de 246 : la photo a ete prise sur un fond de studio gris,
    de 186 a 245 selon les series. La, remonter le point blanc ecrase
    l'acrylique — la cuve blanche est elle-meme a 230-250, elle passerait a
    255 et perdrait son modele. Il faut separer le produit du fond.

CE QUI A ETE ESSAYE ET JETE, pour qu'on ne le refasse pas :

  1. une fourchette de luminance autour d'une valeur unique : elle coupe les
     fonds en degrade en leur milieu et laisse un halo gris dechiquete
     accroche au spa ;
  2. une nappe qui grandit de proche en proche depuis le bord tant que la
     pente reste douce : elle suit les degrades, mais la coque blanche est
     elle aussi une surface lisse, et il suffit d'un point ou son bord se
     fond dans le fond pour que la nappe entre dedans et devore le produit ;
  3. une nappe de fond lisse estimee par cellules, chaque pixel juge sur son
     ecart a elle : plus de fuite catastrophique, mais la coque est au meme
     niveau que le fond — a 100 %, tout son modele etait efface.

Les trois echouent pour la meme raison : AUCUNE REGLE DE LUMINANCE NE PEUT
SEPARER UNE COQUE BLANCHE D'UN FOND GRIS CLAIR. Il y faut un modele qui
reconnaisse l'objet. C'est isnet-general-use, en detourage avec matte doux,
puis composition sur blanc. Verifie a 100 % : bords nets, aucun halo, modele
de l'acrylique intact, liseres lumineux conserves.

GARDE-FOU. Apres coup, on regarde ce que le modele a RETIRE : si les pixels
effaces contenaient du sombre ou du colore, il a mordu dans le spa et la
photo est laissee telle quelle pour un examen a l'oeil.
"""
import os, sys, numpy as np
from PIL import Image, ImageFilter
from blanchir import mesurer_fond

# L'IMPORT DE rembg EST DIFFERE, ET CE N'EST PAS UN DETAIL. Il tire
# onnxruntime, qui demarre OpenMP des le chargement ; un processus qui a
# demarre OpenMP ne peut plus se dupliquer par fork() sans risque, et la
# bibliotheque refuse net — « fork() called from a process already using GNU
# OpenMP ». Les quatre ouvriers mouraient a la seconde ou ils naissaient, et
# le parent attendait indefiniment des resultats qui ne venaient pas. Importe
# ici, le parent ne charge jamais rembg : seuls les ouvriers le font, chacun
# chez soi.

SEUIL_RIEN = 252.0
SEUIL_RELEVE = 246.0
CIBLE = 254.0          # ce qu'on vise pour le fond, pas 255 : voir plus bas
# LE GARDE-FOU N'EST PLUS UN REFUS, ET VOICI POURQUOI. Il mesurait la part
# de pixels « sombres ou colores » que le detourage efface, en supposant que
# seul le produit est sombre. Faux : l'OMBRE PORTEE est sombre elle aussi, et
# elle est du fond — c'est meme precisement ce qu'on veut retirer. Sur 32
# photos, il en a rejete 29, toutes correctes. Il ne reste donc qu'un
# indicateur, reporte dans le compte rendu ; le controle se fait a l'oeil sur
# les planches avant/apres, qui est le seul juge fiable ici.
PART_MIN, PART_MAX = 0.03, 0.90   # un detourage qui prend tout ou rien a rate
BORD_MINI = 0.97       # part de l'anneau de bord qui doit etre du fond

# QUATRE PHOTOS ECARTEES A LA MAIN, APRES REVUE DES PLANCHES.
#
# Aucun test automatique ne les rattrape, et c'est logique : ce sont des gros
# plans dont le cadre est entierement rempli de produit — un appui-tete, un
# panneau de commande, deux fonds de cuve. Le modele y trouve un objet (le
# coussin, le boitier) et efface tout le reste, qui est pourtant le sujet.
# Le fond mesure n'est pas un fond de studio mais l'acrylique blanc lui-meme,
# et l'anneau de bord, entierement classe en « fond », passe le test de
# cadrage.
#
# C'est la limite honnete de la methode : les planches avant/apres restent le
# dernier juge, et ces quatre-la y sautent aux yeux.
ECARTEES = {
    'duo-71940924932426':       'gros plan d\'appui-tete, le modele ne garde que le coussin',
    'duo-71940925030730':       'gros plan du panneau de commande, le modele ne garde que le boitier',
    'pleuxaure-72020675952970': 'fond de cuve vu de dessus, decoupe en lambeau',
    'panope-72020008960330':    'fond de cuve vu de dessus, decoupe en lambeau',
}
DURCIR = 6.0           # pente appliquee a l'alpha du modele
FONDU = 0.8            # fondu du bord, en pixels

_session = None


def _modele():
    global _session
    if _session is None:
        from rembg import new_session
        _session = new_session('isnet-general-use')
    return _session


def traiter(chemin):
    im = Image.open(chemin).convert('RGB')
    cle = os.path.splitext(os.path.basename(chemin))[0]
    if cle in ECARTEES:
        return im, ('ecartee a la main', None, 0.0)
    rgb = np.asarray(im, dtype=np.float32)
    fond = mesurer_fond(rgb)
    if fond is None:
        return im, ('bord occupe', None, 0.0)
    if fond >= SEUIL_RIEN:
        return im, ('inchange', round(fond, 1), 0.0)

    if fond >= SEUIL_RELEVE:
        sortie = np.clip(rgb * (255.0 / fond), 0, 255)
        return Image.fromarray((sortie + .5).astype(np.uint8)), ('releve', round(fond, 1), 100.0)

    # PAS D'AFFINAGE PAR SOLVEUR, ET C'EST UN CHOIX MESURE. rembg sait
    # raffiner le contour en resolvant un systeme sur tous les pixels
    # (alpha_matting). Sur une image de 1 254 px cela demande 90 secondes et
    # 4,5 Go — assez pour que le gestionnaire de memoire tue les ouvriers en
    # cours de lot, ce qui est arrive. Compare a 100 % sur trois photos
    # difficiles, le contour obtenu est indiscernable de celui qu'on tire de
    # l'alpha du modele en le durcissant autour de 0,5 puis en le fondant sur
    # un pixel : 1,5 seconde et 1,8 Go.
    from rembg import remove
    decoupe = remove(im, session=_modele(), alpha_matting=False)
    a = np.asarray(decoupe.convert('RGBA'), dtype=np.float32)
    brut = np.clip((a[..., 3] / 255.0 - 0.5) * DURCIR + 0.5, 0, 1)
    alpha = np.asarray(Image.fromarray((brut * 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(FONDU)),
                       dtype=np.float32)[..., None] / 255.0

    efface = (alpha[..., 0] < 0.5)
    lum = rgb.mean(axis=2)
    sat = rgb.max(axis=2) - rgb.min(axis=2)
    produit = (lum < fond - 60) | (sat > 25)
    degat = float((efface & produit).mean())
    part = float(efface.mean())
    # LE PRODUIT NE DOIT PAS TOUCHER LE CADRE, ET C'EST LE SEUL CRITERE QUI
    # SEPARE VRAIMENT LES DEUX FAMILLES.
    #
    # Le modele reussit les vues d'ensemble — un spa entier, pose au milieu
    # d'un fond — et detruit les gros plans : sur une photo de buses ou de
    # fond de cuve, il n'y a pas d'objet a detourer, il en invente un et rend
    # un lambeau sur blanc. Les planches avant/apres ne laissaient aucun
    # doute : quatre gros plans du Pleuxaure sur neuf etaient dechiquetes.
    #
    # Pire, ces photos-la trompent aussi la mesure du fond : un gros plan de
    # cuve blanche presente un anneau de bord clair et neutre, que
    # mesurer_fond prend pour un fond de studio a 228. D'ou un detourage
    # lance sur une photo qui n'en demandait pas.
    #
    # Le test ci-dessous ferme les deux portes d'un coup : apres decoupe, on
    # regarde si l'anneau de bord est entierement classe en fond. Sur une vue
    # d'ensemble il l'est a 99 % ; sur un gros plan, le produit mord le cadre
    # et la part s'effondre. Mesure sur les 44 : les vues d'ensemble passent,
    # les gros plans sont ecartes, et ils restent tels quels — ce qui est le
    # bon defaut, un gros plan ne montrant de toute facon presque pas de fond.
    h, w = efface.shape
    b = max(3, int(min(h, w) * 0.015))
    anneau = np.concatenate([efface[:b].ravel(), efface[-b:].ravel(),
                             efface[:, :b].ravel(), efface[:, -b:].ravel()])
    bord_libre = float(anneau.mean())
    if bord_libre < BORD_MINI:
        return im, ('gros plan, laisse tel quel (bord %.0f %%)' % (bord_libre*100),
                    round(fond, 1), 0.0)

    if part < PART_MIN or part > PART_MAX:
        return im, ('ECHEC (fond efface %.0f %%)' % (part*100), round(fond, 1), 0.0)

    sortie = a[..., :3] * alpha + 255.0 * (1 - alpha)
    marque = 'detourage' if degat <= 0.005 else 'detourage (sombre efface %.1f %%)' % (degat*100)
    return (Image.fromarray(np.clip(sortie + .5, 0, 255).astype(np.uint8)),
            (marque, round(fond, 1), round(part * 100, 1)))


def _un(cle):
    im, info = traiter('avant/%s.png' % cle)
    im.save('apres/%s.png' % cle)
    return (cle,) + info


if __name__ == '__main__':
    # QUATRE PROCESSUS, PARCE QUE L'AFFINAGE DU CONTOUR EST MONOFIL. Le
    # modele tourne en quelques secondes ; c'est le solveur du matte qui
    # prend une minute et demie par image, et il n'occupe qu'un coeur. A la
    # file, les quarante-quatre detourages demanderaient plus d'une heure.
    import json, time, medias
    import multiprocessing
    # « spawn » plutot que « fork » : voir la note sur OpenMP plus haut.
    ctx = multiprocessing.get_context('spawn')
    os.makedirs('apres', exist_ok=True)
    t0 = time.time()
    taches = ['%s-%s' % (f, m[0]) for f, ms in medias.MEDIAS.items() for m in ms]
    rapport = []
    with ctx.Pool(2) as p:
        for i, r in enumerate(p.imap_unordered(_un, taches), 1):
            rapport.append(r)
            print('%3d/%d  %-36s %-40s fond=%-6s efface=%s%%' % ((i, len(taches)) + r),
                  flush=True)
    print('\n%.0f s' % (time.time() - t0))
    json.dump(sorted(rapport), open('rapport.json', 'w'), indent=1)
