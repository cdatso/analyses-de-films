#!/usr/bin/env python3
# -*- coding: ascii -*-
"""recompresse-affiches.py -- nature 5 du retrofit : le poste de poids du site.

P-36 : aucune affiche ne depasse 300 Ko. Cinq la depassent au 22/07/2026, dont
`pandora.jpg` a 1 660 Ko -- et c'est elle qui produit P-37 (les deux pages du
diptyque a 1 937 Ko a la premiere visite, seuil 900).

Doctrine de la recompression, dans cet ordre :
  1. d'abord la QUALITE seule (rien n'est redimensionne tant que ce n'est pas
     necessaire) ;
  2. si le seuil n'est pas tenu, on reduit la plus grande dimension par paliers
     -- l'affiche est rendue a 272 px de large au maximum dans la fiche
     technique ; un fichier de 900 px reste trois fois plus fin que son rendu.
  3. le fichier n'est reecrit que s'il PASSE sous le seuil : une recompression
     qui n'y parvient pas ne laisse pas une image degradee derriere elle.

Le format et le mode sont preserves ; aucune conversion (pas de WebP : le
parc de navigateurs n'est pas le sujet de ce mandat, et un changement de
format changerait les noms de fichiers cites par 33 pages).

Usage : python recompresse-affiches.py [--depot CHEMIN] [--seuil KO] [--simuler]
Codes : 0 succes -- 1 une affiche au moins reste au-dessus du seuil.
"""

import argparse
import io
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.stderr.write("ARRET : Pillow absent. Le mandat interdit toute "
                     "installation -- signaler a AH.\n")
    raise SystemExit(3)

QUALITES = [88, 85, 82]
PALIERS = [None, 1200, 1000, 900, 800]


def octets(chemin):
    return os.path.getsize(chemin)


def essai(im, qualite, palier):
    """Encode en memoire et rend (taille, image effectivement encodee)."""
    copie = im
    if palier and max(im.size) > palier:
        ratio = float(palier) / max(im.size)
        taille = (int(round(im.size[0] * ratio)),
                  int(round(im.size[1] * ratio)))
        copie = im.resize(taille, Image.LANCZOS)
    tampon = io.BytesIO()
    copie.save(tampon, format="JPEG", quality=qualite, optimize=True,
               progressive=True)
    return tampon.getvalue(), copie.size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depot", default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    ap.add_argument("--seuil", type=int, default=300, help="en Ko (P-36)")
    ap.add_argument("--simuler", action="store_true")
    args = ap.parse_args()

    seuil = args.seuil * 1024
    dossier = os.path.join(args.depot, "assets", "posters")
    if not os.path.isdir(dossier):
        sys.stderr.write("Introuvable : %s\n" % dossier)
        return 2

    noms = sorted(n for n in os.listdir(dossier)
                  if n.lower().endswith((".jpg", ".jpeg")))
    lourdes = [n for n in noms if octets(os.path.join(dossier, n)) > seuil]
    if not lourdes:
        print("aucune affiche au-dessus de %d Ko -- rien a faire" % args.seuil)
        return 0

    print("seuil P-36 : %d Ko -- %d affiche(s) au-dessus, sur %d"
          % (args.seuil, len(lourdes), len(noms)))
    print("")
    print("%-30s %10s %10s %14s %14s %s"
          % ("affiche", "avant", "apres", "dimensions", "-> apres", "reglage"))
    print("-" * 104)

    echecs, total_avant, total_apres = [], 0, 0
    for nom in lourdes:
        chemin = os.path.join(dossier, nom)
        avant = octets(chemin)
        im = Image.open(chemin)
        dim_avant = im.size
        retenu = None
        for palier in PALIERS:
            for qualite in QUALITES:
                donnees, dim = essai(im, qualite, palier)
                if len(donnees) <= seuil:
                    retenu = (donnees, dim, qualite, palier)
                    break
            if retenu:
                break
        if not retenu:
            echecs.append(nom)
            print("%-30s %8.1f Ko %10s %14s %14s %s"
                  % (nom, avant / 1024.0, "ECHEC", "%dx%d" % dim_avant,
                     "-", "aucun reglage ne tient le seuil"))
            continue
        donnees, dim, qualite, palier = retenu
        if not args.simuler:
            with open(chemin, "wb") as f:
                f.write(donnees)
        total_avant += avant
        total_apres += len(donnees)
        print("%-30s %8.1f Ko %8.1f Ko %14s %14s q=%d%s"
              % (nom, avant / 1024.0, len(donnees) / 1024.0,
                 "%dx%d" % dim_avant, "%dx%d" % dim, qualite,
                 "" if palier is None else " palier=%d" % palier))

    print("")
    print("total avant : %8.1f Ko" % (total_avant / 1024.0))
    print("total apres : %8.1f Ko  (%.1f %% du poids d'origine)"
          % (total_apres / 1024.0,
             100.0 * total_apres / total_avant if total_avant else 0))
    if args.simuler:
        print("SIMULATION : aucun fichier reecrit")
    if echecs:
        sys.stderr.write("AFFICHES ENCORE AU-DESSUS DU SEUIL : %s\n"
                         % ", ".join(echecs))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
