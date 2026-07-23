#!/usr/bin/env python3
# -*- coding: ascii -*-
"""bilan-contraste.py -- ecrit le TABLEAU AA DEFINITIF (P-39) dans docs/.

Lecture seule sur les mesures, aucune palette touchee : le tableau porte les
arbitrages qui attendent AH en 065-5, il n'en execute aucun.

Deux vues, parce qu'elles n'appellent pas la meme decision :
  - les 71 ecarts DECLARES par le comptage statique du prototype, chacun
    CONFIRME ou ECARTE au rendu reel (c'est la demande du mandat 4.3) ;
  - le RECENSEMENT independant des 34 pages, qui voit ce que le comptage
    statique ne pouvait pas voir et fait le tableau definitif.

Usage : python bilan-contraste.py [--sortie CHEMIN]
"""

import argparse
import os
import sys

import harnais

ENTETE_NATURE = {
    "texte courant (seuil 4,5:1)":
        "Texte courant sur fond uniforme. Seuil 4,5:1. Le coeur de la lisibilite.",
    "grand texte (seuil 3:1)":
        "Grand texte (>= 24 px, ou >= 18,66 px en gras). Seuil 3:1.",
    "fond en degrade : echoue sur une PARTIE du fond":
        "Le fond est un degrade : le texte PASSE sur certaines zones et ECHOUE "
        "sur d'autres. Le ratio donne est le pire cas du degrade.",
    "opacite < 1":
        "L'echec vient d'une opacite inferieure a 1 : la couleur pleine "
        "passerait. L'arbitrage porte sur l'opacite, pas sur la palette.",
    "identite de couleur (ratio 1,00)":
        "Texte de la couleur exacte de son fond. A verifier : effet voulu "
        "(caviardage) ou defaut.",
}


def nature(l):
    if l.get("partiel"):
        return "fond en degrade : echoue sur une PARTIE du fond"
    if l["ratio"] <= 1.01:
        return "identite de couleur (ratio 1,00)"
    if l["opacite"] < 1:
        return "opacite < 1"
    if l["seuil"] == 3.0:
        return "grand texte (seuil 3:1)"
    return "texte courant (seuil 4,5:1)"


PAGES_PROTO = set(p.split("/")[-1] for p in harnais.PAGES_PROTOTYPE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sortie", default=os.path.join(
        harnais.DOSSIER_DOCS, "recette-v2-tableau-AA.md"))
    args = ap.parse_args()

    d = harnais.lire_json("contraste.json")
    declares, recensement = d["declares"], d["recensement"]

    lignes = []
    for page, lst in recensement.items():
        for l in lst:
            l = dict(l)
            l["page"] = page
            l["nature"] = nature(l)
            l["migree"] = page in PAGES_PROTO
            lignes.append(l)

    par_nature = {}
    for l in lignes:
        par_nature.setdefault(l["nature"], []).append(l)

    proto = [l for l in lignes if l["migree"]]
    autres = [l for l in lignes if not l["migree"]]

    o = []
    a = o.append
    a("# Tableau AA definitif -- P-39 au rendu reel")
    a("")
    a("**Item** : BKL-065-4-recette - **Branche** : `v2-proto` - **Contrat** :")
    a("`SPEC-SITE-V2.md` v1.1, prescription **P-39** (4,5:1 texte courant,")
    a("3:1 grand texte).")
    a("")
    a("**Ce document COMPTE et n'a rien corrige.** Chaque ligne est un")
    a("arbitrage qui attend AH en **BKL-065-5** : corriger la palette, ou")
    a("documenter l'exception. Aucun fichier du site n'a ete modifie.")
    a("")
    a("## Methode, et en quoi elle differe du comptage du prototype")
    a("")
    a("Le comptage de 065-3 (`outils/controle-contraste.py`) lisait le CSS")
    a("**sans arbre de document** : il ne pouvait pas savoir sur quel fond un")
    a("texte se pose. Il assumait de sous-estimer et distinguait deux classes,")
    a("**E1** (couple ecrit dans la meme regle, *certain*) et **E2** (couleur en")
    a("echec sur tous les fonds declares, *probable*).")
    a("")
    a("La presente mesure est prise dans Chromium, sur la page composee :")
    a("")
    a("- le fond effectif se lit en **remontant les ancetres** jusqu'a une")
    a("  couche opaque, les couches semi-transparentes etant composees ;")
    a("- les fonds en **degrade** sont traites par leurs arrets de couleur, et")
    a("  le verdict porte sur le **pire** d'entre eux (une couche a")
    a("  `background-image` couvre ce qui est dessous : le fond de page cesse")
    a("  d'etre un candidat) ;")
    a("- l'**opacite effective** est le produit de celles de l'element et de")
    a("  ses ancetres ;")
    a("- le seuil applicable vient de la **taille et de la graisse reelles** ;")
    a("- les textes `aria-hidden`, hors cadre ou de dimension nulle sont exclus.")
    a("")
    a("*Controle du perimetre : aucune page du corpus n'emploie d'image bitmap")
    a("en fond (`background: url(...)`) -- tout fond est une couleur ou un")
    a("degrade, donc entierement decidable aux styles calcules. Aucune ligne de")
    a("ce tableau n'est laissee indeterminee.*")
    a("")

    a("## 1. Les 71 ecarts declares par le prototype, confrontes au rendu reel")
    a("")
    a("| Classe | Declares | CONFIRMES | ECARTES |")
    a("|---|---|---|---|")
    for classe, libelle in (("E1", "certains"), ("E2", "probables")):
        lst = [e for e in declares if e["classe"] == classe]
        conf = len([e for e in lst if e["verdict"] == "CONFIRME"])
        a("| **%s** (%s) | %d | **%d** | %d |"
          % (classe, libelle, len(lst), conf, len(lst) - conf))
    tot = len(declares)
    totc = len([e for e in declares if e["verdict"] == "CONFIRME"])
    a("| **Total** | **%d** | **%d** | **%d** |" % (tot, totc, tot - totc))
    a("")
    a("Motifs des mises a l'ecart :")
    a("")
    a("| Motif | Nombre | Lecture |")
    a("|---|---|---|")
    motifs = {}
    for e in declares:
        if e["verdict"].startswith("ECARTE"):
            motifs[e["verdict"]] = motifs.get(e["verdict"], 0) + 1
    lecture = {
        "ECARTE (regle sans element rendu)":
            "la regle CSS existe mais ne s'applique a aucun element de la page",
        "ECARTE (aucun texte porte par la regle)":
            "les elements vises ne portent aucun texte -- il n'y a rien a lire",
        "ECARTE (passe au rendu reel)":
            "le couple reel differe de celui suppose : le contraste passe",
    }
    for m, n in sorted(motifs.items(), key=lambda x: -x[1]):
        a("| %s | %d | %s |" % (m.replace("ECARTE ", ""), n,
                                lecture.get(m, "")))
    a("")
    a("### Detail des ecarts declares")
    a("")
    a("| Page | Classe | Selecteur | Ratio statique | Ratio reel | Verdict |")
    a("|---|---|---|---|---|---|")
    for e in sorted(declares, key=lambda x: (x["page"], x["classe"])):
        rr = e.get("ratio_reel")
        a("| `%s` | %s | `%s` | %.2f | %s | %s |"
          % (e["page"], e["classe"], e["selecteur"][:44], e["ratio_statique"],
             ("%.2f" % rr) if rr is not None else "-", e["verdict"]))
    a("")

    a("## 2. Recensement independant au rendu reel -- le tableau definitif")
    a("")
    a("| Mesure | Valeur |")
    a("|---|---|")
    a("| Pages balayees | %d |" % len(recensement))
    a("| **Couples sous le seuil** | **%d** |" % len(lignes))
    a("| Pages concernees | %d / %d |"
      % (len([p for p, v in recensement.items() if v]), len(recensement)))
    a("| dont pages **migrees en v2** (les 9 du prototype) | %d couples |"
      % len(proto))
    a("| dont pages **non migrees** (retrofit 065-5) | %d couples |" % len(autres))
    a("")
    a("*Lecture : le comptage statique en annoncait %d en se declarant borne"
      % len(declares))
    a("basse. Le rendu reel en mesure **%d**. L'ecart ne vient pas d'une"
      % len(lignes))
    a("aggravation du site mais de ce que le premier outil ne pouvait pas voir :")
    a("l'appariement d'un texte avec son fond reel.*")
    a("")
    a("### Par nature d'ecart")
    a("")
    a("| Nature | Nombre | Ce que l'arbitrage doit trancher |")
    a("|---|---|---|")
    for n in sorted(par_nature, key=lambda k: -len(par_nature[k])):
        a("| %s | **%d** | %s |" % (n, len(par_nature[n]),
                                    ENTETE_NATURE.get(n, "")))
    a("")
    a("### Par page")
    a("")
    a("| Page | Migree v2 | Couples sous le seuil | Pire ratio |")
    a("|---|---|---|---|")
    for page in sorted(recensement, key=lambda n: -len(recensement[n])):
        lst = recensement[page]
        if not lst:
            continue
        a("| `%s` | %s | %d | %.2f |"
          % (page, "oui" if page in PAGES_PROTO else "non", len(lst),
             min(x["ratio"] for x in lst)))
    a("")
    a("### Detail complet -- une ligne par couple, page par page")
    a("")
    a("Colonnes : `ratio` = pire cas mesure - `seuil` = exigence applicable -")
    a("`opac.` = opacite effective - `px` = taille reelle.")
    a("")
    for page in sorted(recensement):
        lst = recensement[page]
        if not lst:
            continue
        a("#### `%s` -- %d couple(s)%s"
          % (page, len(lst), " *(migree v2)*" if page in PAGES_PROTO else ""))
        a("")
        a("| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |")
        a("|---|---|---|---|---|---|---|---|")
        for l in sorted(lst, key=lambda x: x["ratio"]):
            extrait = l["extrait"].replace("|", "/")
            a("| `%s` | `%s` | `%s` | **%.2f** | %.1f | %.2f | %.0f | %s |"
              % (l["chemin"][-46:], l["texte"], l["fond"], l["ratio"],
                 l["seuil"], l["opacite"], l["px"], extrait))
        a("")

    texte = "\n".join(o) + "\n"
    with open(args.sortie, "w", encoding="utf-8", newline="\n") as f:
        f.write(texte)

    print("Tableau AA ecrit : %s" % args.sortie)
    print("  ecarts declares reconcilies : %d (%d confirmes, %d ecartes)"
          % (tot, totc, tot - totc))
    print("  recensement independant     : %d couples sur %d pages"
          % (len(lignes), len([p for p, v in recensement.items() if v])))
    print("  dont pages migrees v2       : %d" % len(proto))
    print("  dont pages non migrees      : %d" % len(autres))
    for n in sorted(par_nature, key=lambda k: -len(par_nature[k])):
        print("     %-52s %d" % (n, len(par_nature[n])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
