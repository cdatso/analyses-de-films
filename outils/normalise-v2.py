#!/usr/bin/env python3
# -*- coding: ascii -*-
"""normalise-v2.py -- les normalisations ponctuelles du retrofit BKL-065-5.

La nature 4 du mandat rassemble ce qui n'est pas une transformation de masse :
des defauts NOMMES, un par un, chacun avec sa regle, son perimetre et son
critere de verification. Rien d'automatique a l'aveugle -- une regle ne
s'applique qu'aux fichiers qu'elle nomme, et echoue bruyamment si le motif
attendu a disparu.

Regles disponibles (--regle) :
  collision-waterloo : la page nomme `cartouche` son en-tete de COUVERTURE
                       (header.cartouche + .cartouche-inner), nom qui entre en
                       collision avec le composant de mobilier `.cartouche`
                       (P-15/P-16). Sans renommage, les regles du mobilier
                       (chasse fixe, filets de volet, marges) s'appliqueraient
                       a la couverture du film. Renomme la classe BESPOKE,
                       jamais le composant partage. Zero effet editorial.

Usage : python normalise-v2.py --regle <nom> [--depot CHEMIN] [--simuler]
Codes : 0 succes -- 1 assert en echec -- 2 fichier introuvable.
"""

import argparse
import io
import os
import sys


def echec(msg):
    sys.stderr.write("ASSERT EN ECHEC : %s\n" % msg)
    sys.exit(1)


def lire(chemin):
    with io.open(chemin, "r", encoding="utf-8") as f:
        return f.read()


def ecrire(chemin, texte):
    with io.open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(texte)


def collision_waterloo(depot, simuler):
    chemin = os.path.join(depot, "films", "waterloo.html")
    if not os.path.isfile(chemin):
        sys.stderr.write("Introuvable : %s\n" % chemin)
        return 2
    src = lire(chemin)

    # Les 5 occurrences constatees le 22/07/2026. Si l'une manque, la page a
    # change depuis le constat : on s'arrete plutot que de renommer a moitie.
    attendus = [
        ("header.cartouche{", "header.carte-titre{"),
        ("header.cartouche::after{", "header.carte-titre::after{"),
        (".cartouche-inner{", ".carte-titre-inner{"),
        ('<header class="cartouche">', '<header class="carte-titre">'),
        ('<div class="cartouche-inner">', '<div class="carte-titre-inner">'),
    ]
    t = src
    for avant, apres in attendus:
        if avant not in t:
            echec("waterloo.html : motif attendu absent -- %r" % avant)
        t = t.replace(avant, apres)

    # Le composant de mobilier ne doit plus etre nomme nulle part dans la
    # page : c'est TOUT l'objet de la regle.
    if "cartouche" in t:
        restants = [l for l in t.splitlines() if "cartouche" in l]
        echec("waterloo.html : %d ligne(s) nomment encore 'cartouche' : %s"
              % (len(restants), restants[:3]))
    if t == src:
        echec("waterloo.html : aucune modification produite")

    if not simuler:
        ecrire(chemin, t)
    print("waterloo.html  collision header.cartouche -> header.carte-titre  "
          "(%d occurrences)  %d -> %d octets%s"
          % (len(attendus), len(src), len(t),
             "  [SIMULATION]" if simuler else ""))
    return 0


REGLES = {"collision-waterloo": collision_waterloo}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--regle", required=True, choices=sorted(REGLES))
    ap.add_argument("--depot", default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    ap.add_argument("--simuler", action="store_true")
    args = ap.parse_args()
    return REGLES[args.regle](args.depot, args.simuler)


if __name__ == "__main__":
    sys.exit(main())
