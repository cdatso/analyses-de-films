#!/usr/bin/env python3
# -*- coding: ascii -*-
"""retrofit-registre.py -- nature 3 du retrofit : le registre au schema v2.

Ce que ce script pose, et RIEN d'autre -- uniquement ce qui se derive sans
jugement (annexe B de SPEC-SITE-V2) :

  volet            'critique' -- les 30 pages retrofitees sont des Critiques ;
                   la seule Etude du corpus est le contrechamp, deja migre ;
  datePublication  premiere apparition du fichier sur main (git log
                   --diff-filter=A), jamais une estimation (diagnostic D-5) ;
  producteur       la valeur JOURNALISEE si elle existe, sinon la mention
                   explicite 'non specifie' (P-18 : jamais vide, jamais devinee) ;
  genreBase        tete du champ `genre` deprecie, SI cette tete appartient au
                   vocabulaire ferme (P-10). Sinon : rien -- l'entree est
                   signalee, pas devinee.

Ce que ce script NE POSE PAS, et pourquoi :

  technique        2 entrees sur 33 seulement portent leur technique dans le
                   texte libre ('(muet)', '(N&B)'). Pour les 31 autres, savoir
                   si un film est en noir et blanc n'est pas une derivation :
                   c'est une connaissance du film. Le champ rejoint donc la
                   table de taxonomie soumise a AH (ARRET n.1) ;
  pays, courant,   non derivables (le pays n'est nulle part un champ --
  deleuze          diagnostic D-3). Travail de modele SOUS RELECTURE D'AH ;
  genre            conserve pour l'instant : il reste la SOURCE du remplissage
                   de technique et des 2 genreBase ambigus. Son retrait (P-50)
                   vient apres le gate de taxonomie, pas avant.

Usage : python retrofit-registre.py [--depot CHEMIN] [--simuler]
Codes : 0 succes -- 1 assert en echec -- 2 fichier introuvable.
"""

import argparse
import io
import os
import re
import subprocess
import sys
import unicodedata

VOCABULAIRE_GENRE = ["comedie", "documentaire", "drame", "fantastique",
                     "fresque", "melodrame", "polar", "thriller", "tragedie",
                     "western"]

# Les 3 entrees migrees par le prototype : leur bloc v2 est deja pose.
DEJA_MIGREES = ["pandora", "pandora-contrechamp", "rouges-et-blancs"]

ENTETE_V2 = ("    // --- schema v2 (annexe B) -- retrofit BKL-065-5, "
             "22/07/2026 ---")


def echec(msg):
    sys.stderr.write("ASSERT EN ECHEC : %s\n" % msg)
    sys.exit(1)


def sans_accent(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


def date_git(depot, slug):
    sortie = subprocess.check_output(
        ["git", "-C", depot, "log", "main", "--diff-filter=A",
         "--format=%ad", "--date=format:%Y-%m-%d %H:%M", "--",
         "films/%s.html" % slug],
        stderr=subprocess.STDOUT).decode("ascii", "replace")
    lignes = [l.strip() for l in sortie.splitlines() if l.strip()]
    if not lignes:
        echec("%s : aucune date d'ajout dans l'historique de main" % slug)
    return lignes[-1]


def genre_base(genre_libre):
    """Tete du genre libre, si et seulement si elle est au vocabulaire."""
    if not genre_libre:
        return None
    tete = sans_accent(genre_libre).split()[0]
    return tete if tete in VOCABULAIRE_GENRE else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depot", default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    ap.add_argument("--simuler", action="store_true")
    args = ap.parse_args()

    chemin = os.path.join(args.depot, "assets", "films-data.js")
    if not os.path.isfile(chemin):
        sys.stderr.write("Introuvable : %s\n" % chemin)
        return 2
    with io.open(chemin, "r", encoding="utf-8") as f:
        src = f.read()

    objets = re.compile(r"(\n  \{\n)(.*?)(\n  \})", re.S)
    traitees, ignorees, sans_genrebase = [], [], []

    def traite(m):
        ouvre, corps, ferme = m.group(1), m.group(2), m.group(3)
        ms = re.search(r"slug:\s*'([^']+)'", corps)
        if not ms:
            echec("objet sans slug dans le registre")
        slug = ms.group(1)
        if slug in DEJA_MIGREES:
            ignorees.append((slug, "migree par le prototype"))
            return m.group(0)
        if "datePublication" in corps:
            ignorees.append((slug, "deja retrofitee"))
            return m.group(0)

        mg = re.search(r"\n    genre:\s*'([^']*)'", corps)
        genre_libre = mg.group(1) if mg else ""
        gb = genre_base(genre_libre)
        if gb is None:
            sans_genrebase.append((slug, genre_libre))

        champs = ["    volet: 'critique',",
                  "    datePublication: '%s'," % date_git(args.depot, slug)]
        if gb:
            champs.append("    genreBase: '%s'," % gb)
        if "producteur:" not in corps:
            # P-18 : la mention est EXPLICITE, elle n'est pas un vide.
            champs.append("    producteur: 'non sp\xe9cifi\xe9',")

        # Le dernier champ pose ne porte pas de virgule finale.
        champs[-1] = champs[-1].rstrip(",")
        # Le champ qui precedait devient non final : il en gagne une.
        corps2 = corps
        if not corps2.rstrip().endswith(","):
            corps2 = corps2.rstrip() + ","
        nouveau = corps2 + "\n" + ENTETE_V2 + "\n" + "\n".join(champs)
        traitees.append(slug)
        return ouvre + nouveau + ferme

    resultat = objets.sub(traite, src)

    if not traitees:
        echec("aucune entree retrofitee -- registre deja a jour ?")
    if resultat == src:
        echec("le registre n'a pas change")

    if not args.simuler:
        with io.open(chemin, "w", encoding="utf-8", newline="\n") as f:
            f.write(resultat)

    print("entrees retrofitees : %d%s" % (
        len(traitees), "  [SIMULATION]" if args.simuler else ""))
    print("entrees ignorees    : %d" % len(ignorees))
    for slug, motif in ignorees:
        print("   %-30s %s" % (slug, motif))
    if sans_genrebase:
        print("")
        print("genreBase NON POSE (tete hors vocabulaire) : %d"
              % len(sans_genrebase))
        for slug, g in sans_genrebase:
            print("   %-30s genre libre = %r" % (slug, g))
        print("   -> ces entrees rejoignent la table soumise a AH (ARRET n.1)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
