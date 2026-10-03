# -*- coding: utf-8 -*-
"""Rapatrier les photos des spas depuis le CDN Shopify, dans « avant/ ».

Les identifiants et les noms de fichiers sont dans « medias.py ». Ils datent
du 3 octobre 2026 : si une photo a ete remplacee depuis, son nom a change et
le telechargement echouera — c'est le bon comportement, mieux vaut une erreur
qu'une vieille version silencieusement reprise.
"""
import os, subprocess
from concurrent.futures import ThreadPoolExecutor
import medias


def tirer(args):
    fiche, (mid, nom) = args
    cible = 'avant/%s-%s.png' % (fiche, mid)
    if os.path.exists(cible) and os.path.getsize(cible) > 1000:
        return cible
    subprocess.run(['curl', '-sS', '-f', '-o', cible, medias.BASE + nom], check=True)
    return cible


if __name__ == '__main__':
    os.makedirs('avant', exist_ok=True)
    taches = [(f, m) for f, ms in medias.MEDIAS.items() for m in ms]
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(tirer, taches))
    print(len(os.listdir('avant')), 'photos dans avant/')
