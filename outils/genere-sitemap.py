#!/usr/bin/env python3
# -*- coding: ascii -*-
"""genere-sitemap.py -- le sitemap outille, avec un mode --verifier.

GATE AH du 06/08/2026 (option (1)-B, ANNEXE-REPONSES-AH-2026-08-06.md, Q-1) :
un generateur SEUL, appele par la skill a l'etape 10.0 -- jamais par le hook.
L'option (1)-C (5e controle du hook) a ete ecartee par decision, pas par une
borne ; sa reouverture exige un gate distinct.

sitemap.xml n'a pas de marqueurs internes comme les listes statiques : c'est
le fichier ENTIER qui est engendre, en-tete de commentaire compris. Cet
en-tete est donc repris tel quel (constante ENTETE) -- il decrit la derniere
regeneration reelle et ne se met pas a jour tout seul ; le faire varier ici
casserait la comparaison a l'octet que --verifier doit rendre.

Point de friction (BKL-CIN-089, L2) : la liste d'exclusions. Regle
d'inclusion -- tous les *.html du depot, hors des repertoires .git,
_scratch, outils, assets, docs. Implicite, elle ferait signaler une
publication valide comme une derive.

Ordre de sortie : reproduit celui du fichier existant -- racine, puis
films/, puis en/ (PRIORITE_REPERTOIRES) -- alphabetique a l'interieur de
chaque repertoire. Tout autre repertoire non exclu (structure future) est
ajoute ensuite, trie par son propre nom : rien n'est tu, meme hors de
l'ordre connu.

Usage : python genere-sitemap.py [--depot CHEMIN] [--verifier]
Codes : 0 conforme -- 1 derive -- 2 fichier introuvable.
"""

import argparse
import io
import os
import sys

BASE_URL = "https://www.cdatso.be/analyses-de-films/"

# Repertoires hors publication (BKL-CIN-089, mandat S3-L2) : .git est le
# depot lui-meme, _scratch le vivier du vif, outils/docs/assets ne portent
# aucune page publiee. outils/observation-C2-carte-seule.html est le seul
# HTML non publie du depot -- verifie present le 10/08/2026, couvert par
# cette exclusion.
EXCLUS = set(["_scratch", ".git", "outils", "assets", "docs"])

# Ordre reproduit du sitemap existant (voir docstring). Un repertoire
# nouveau, non exclu et absent d'ici, est inclus quand meme -- ajoute apres
# ceux-ci, trie par nom.
PRIORITE_REPERTOIRES = ["", "films", "en"]

ENTETE = ("""<?xml version="1.0" encoding="UTF-8"?>
<!-- Sitemap du site analyses-de-films.
     Genere depuis le contenu reel du depot le 10/08/2026, par
     outils/genere-sitemap.py, qui vit dans ce depot et que la skill appelle
     a l'etape 10.0 -- jamais recopie a la main.
     Les URL y sont ABSOLUES : seule exception admise a P-33, avec les balises
     hreflang/alternates, nommee et bornee par P-59 (spec v1.8). -->
""")


def lire(chemin):
    with io.open(chemin, "r", encoding="utf-8") as f:
        return f.read()


def ecrire(chemin, texte):
    with io.open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(texte)


def repertoires_html(depot):
    """Rend {repertoire relatif ('' pour la racine) : [noms *.html]}."""
    par_repertoire = {}
    for racine, sousrepertoires, fichiers in os.walk(depot):
        rel = os.path.relpath(racine, depot)
        rel = "" if rel == "." else rel.replace(os.sep, "/")
        sommet = rel.split("/")[0] if rel else ""
        if sommet in EXCLUS:
            sousrepertoires[:] = []
            continue
        sousrepertoires[:] = sorted(d for d in sousrepertoires if d not in EXCLUS)
        noms = sorted(f for f in fichiers if f.endswith(".html"))
        if noms:
            par_repertoire[rel] = noms
    return par_repertoire


def ordre(par_repertoire):
    connus = [r for r in PRIORITE_REPERTOIRES if r in par_repertoire]
    autres = sorted(r for r in par_repertoire if r not in PRIORITE_REPERTOIRES)
    for rep in connus + autres:
        for nom in par_repertoire[rep]:
            yield rep, nom


def genere(depot):
    par_repertoire = repertoires_html(depot)
    lignes = []
    for rep, nom in ordre(par_repertoire):
        chemin = nom if rep == "" else rep + "/" + nom
        lignes.append(u"  <url><loc>%s%s</loc></url>" % (BASE_URL, chemin))
    corps = u"<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
    corps += u"\n".join(lignes) + u"\n</urlset>\n"
    return unicode_str(ENTETE) + corps


def unicode_str(s):
    return s if isinstance(s, type(u"")) else u"%s" % s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depot", default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    ap.add_argument("--verifier", action="store_true")
    args = ap.parse_args()

    cible = os.path.join(args.depot, "sitemap.xml")
    if not os.path.isdir(args.depot):
        sys.stderr.write("Introuvable : %s\n" % args.depot)
        return 2

    contenu = genere(args.depot)
    n = contenu.count(u"<loc>")

    if args.verifier:
        if not os.path.isfile(cible):
            sys.stderr.write("Introuvable : %s\n" % cible)
            return 2
        disque = lire(cible)
        etat = "conforme" if disque == contenu else "DERIVE"
        code = 0 if disque == contenu else 1
        print("%-24s %-9s %d entrees" % ("sitemap.xml", etat, n))
        print("")
        if code == 0:
            print("Aucune derive entre le gabarit du script et sitemap.xml du depot.")
        else:
            print("DERIVE : sitemap.xml ne correspond plus au contenu reel du depot. Regenerer.")
        return code
    else:
        if os.path.isfile(cible) and lire(cible) == contenu:
            print("%-24s %d entrees (deja conforme, rien ecrit)" % ("sitemap.xml", n))
        else:
            ecrire(cible, contenu)
            print("%-24s %d entrees ecrites" % ("sitemap.xml", n))
        return 0


if __name__ == "__main__":
    sys.exit(main())
