# -*- coding: utf-8 -*-
"""Temps 2 du televersement : poster les octets a l'adresse signee.

Les adresses signees sont lues dans un fichier texte, une ligne par photo :
  nom <TAB> cle <TAB> signature <TAB> politique
Rien n'est code en dur ici : le meme script sert pour chaque lot.
"""
import subprocess, sys

URL = "https://shopify-staged-uploads.storage.googleapis.com/"
DATE = sys.argv[2]
DOSSIER = sys.argv[3]
COMMUN = [("Content-Type", "image/png"), ("success_action_status", "201"), ("acl", "private"),
          ("x-goog-date", DATE),
          ("x-goog-credential",
           "merchant-assets@shopify-tiers.iam.gserviceaccount.com/%s/auto/storage/goog4_request" % DATE[:8]),
          ("x-goog-algorithm", "GOOG4-RSA-SHA256")]

for ligne in open(sys.argv[1]):
    if not ligne.strip():
        continue
    nom, cle, sig, pol = ligne.rstrip("\n").split("\t")
    cmd = ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", "-X", "POST", URL]
    for k, v in COMMUN:
        cmd += ["-F", "%s=%s" % (k, v)]
    cmd += ["-F", "key=" + cle, "-F", "x-goog-signature=" + sig, "-F", "policy=" + pol,
            "-F", "file=@%s/%s.png" % (DOSSIER, nom)]
    code = subprocess.check_output(cmd).decode().strip()
    print("%-14s %s" % (nom, code))
    if code != "201":
        raise SystemExit("envoi refuse : " + nom)
