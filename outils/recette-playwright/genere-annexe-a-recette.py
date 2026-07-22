#!/usr/bin/env python3
# -*- coding: ascii -*-
"""genere-annexe-a-recette.py -- annexe A REGENEREE, vers docs/.

Mandat BKL-065-4-recette, point 4.7 (arbitrage E-1 du 22/07 11h54 : l'annexe A
de la spec est perimee, 34 URLs reels contre 33 listes).

Difference avec `_scratch\\genere-annexe-a.py`, dont ce script reprend la
logique a l'identique : l'original ECRIT DANS `SPEC-SITE-V2.md`. Le mandat
interdit d'ouvrir la spec en ecriture (autorisations 8). C'est donc la
DESTINATION qui est adaptee -- jamais la spec, dont l'integration reste la
main du greffe.

Lit le depot en SEULE LECTURE (systeme de fichiers + git). Ecrit un seul
fichier, dans docs/.

Usage : python genere-annexe-a-recette.py [--sortie CHEMIN]
Code de sortie : 0 genere - 2 le depot n'a pas pu etre lu.
"""

import argparse
import io
import os
import re
import subprocess
import sys

import harnais

BASE = "https://www.cdatso.be/analyses-de-films/"


def git(*args):
    r = subprocess.run(["git", "-C", harnais.DEPOT] + list(args),
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sortie", default=os.path.join(
        harnais.DOSSIER_DOCS, "recette-v2-annexe-A-regeneree.md"))
    args = ap.parse_args()

    # GARDE-FOU : ce script ne doit jamais pouvoir ecrire dans la spec.
    interdit = os.path.normcase(os.path.abspath(args.sortie))
    assert "spec-site-v2" not in interdit, \
        "REFUS : la spec n'est pas une destination autorisee (mandat 8)"
    assert interdit.startswith(os.path.normcase(os.path.abspath(
        harnais.DOSSIER_DOCS))), "REFUS : la sortie doit rester dans docs/"

    dossier = os.path.join(harnais.DEPOT, "films")
    if not os.path.isdir(dossier):
        sys.stderr.write("films/ introuvable sous %s\n" % harnais.DEPOT)
        return 2

    pages = sorted(f for f in os.listdir(dossier) if f.endswith(".html"))
    with io.open(os.path.join(harnais.DEPOT, "assets", "films-data.js"),
                 encoding="utf-8") as f:
        registre = f.read()
    slugs_var = set(re.findall(r"slug:\s*'([^']+)'[^}]*?variantOf:",
                               registre, re.S))

    head = git("rev-parse", "--short", "HEAD")
    branche = git("rev-parse", "--abbrev-ref", "HEAD")
    horodatage = git("log", "-1", "--format=%ad", "--date=format:%Y-%m-%d %H:%M")

    lignes = []
    for f in pages:
        slug = f[:-5]
        d = git("log", "--diff-filter=A", "--format=%ad",
                "--date=format:%Y-%m-%d %H:%M", "--", "films/" + f).split("\n")
        date = d[-1] if d and d[-1] else "(inconnue)"
        lignes.append((slug, "Etude" if slug in slugs_var else "Critique", date))

    etudes = sum(1 for _s, v, _d in lignes if v == "Etude")
    total = len(lignes) + 1

    t = []
    t.append("# Annexe A regeneree - Inventaire des URLs publies")
    t.append("")
    t.append("**Item** : BKL-065-4-recette - **Genere** (jamais recopie) depuis")
    t.append("le depot du site, branche `%s`, HEAD `%s` (dernier commit du %s)."
             % (branche, head, horodatage))
    t.append("")
    t.append("> **Ce fichier n'est PAS l'annexe A de la spec.** Le mandat")
    t.append("> interdit d'ecrire dans `SPEC-SITE-V2.md` : l'integration de")
    t.append("> cette annexe regeneree est la main du greffe. Le present")
    t.append("> document est la mesure, pas la consignation.")
    t.append("")
    t.append("Script rejouable : `outils/recette-playwright/"
             "genere-annexe-a-recette.py`.")
    t.append("")
    t.append("Base : `%s`" % BASE)
    t.append("")
    t.append("Cette liste **est** la checklist de **P-32** (aucun URL publie ne")
    t.append("casse) : chaque ligne doit repondre 200 apres migration,")
    t.append("controlee une par une, sans echantillonnage.")
    t.append("")
    t.append("| # | URL (relatif a la base) | Volet | Publiee le |")
    t.append("|---|---|---|---|")
    t.append("| 1 | `index.html` | - | (accueil) |")
    for i, (slug, volet, date) in enumerate(lignes, start=2):
        t.append("| %d | `films/%s.html` | %s | %s |" % (i, slug, volet, date))
    t.append("")
    t.append("**Total : %d URLs publies** (%d analyses + l'accueil), dont %d "
             "Etude(s) et %d Critique(s)."
             % (total, len(lignes), etudes, len(lignes) - etudes))
    t.append("")
    t.append("## Ce qui a change depuis l'annexe A de la spec v1.1")
    t.append("")
    t.append("| | Annexe A de la spec | Mesure de ce jour |")
    t.append("|---|---|---|")
    t.append("| URLs listes | 33 | **%d** |" % total)
    t.append("")
    t.append("*L'ecart de l'arbitrage E-1 (22/07 11h54) est confirme sur")
    t.append("mesure : le corpus a grossi apres la mesure `ae06e77`. Les 6")
    t.append("pages du menu v2 (`critiques.html`, `etudes.html`,")
    t.append("`qui-sommes-nous.html`, `comment-ca-marche.html`,")
    t.append("`demander-une-analyse.html`) ne figurent pas dans cet inventaire :")
    t.append("elles ne sont pas des URLs PUBLIES a ce jour, elles n'existent")
    t.append("que sur `v2-proto`. Elles rejoindront la liste a la bascule.*")
    t.append("")

    with io.open(args.sortie, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(t) + "\n")

    print("Annexe A regeneree : %s" % args.sortie)
    print("  URLs : %d (%d analyses + accueil) -- %d Etude(s), %d Critique(s)"
          % (total, len(lignes), etudes, len(lignes) - etudes))
    print("  branche %s, HEAD %s" % (branche, head))
    print("  SPEC-SITE-V2.md : NON OUVERTE (mandat 8)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
