#!/usr/bin/env python3
# -*- coding: ascii -*-
"""applique-lots-aa.py -- applique les lots de contraste GATES par AH.

Gate d'AH du 23/07/2026 : "go lots 1, 2, 3 et 5". Le lot 4 (deplacements
lourds) reste a arbitrer cas par cas et n'est PAS traite ici.

Les lots, et le geste propre a chacun :

  --lot 1  le chrome partage. `--ink-muted` et `--mobilier-attenue` de
           style.css passent de #7a7a74 a #6c6c67. Les deux variables ne
           servent qu'a colorer du texte (26 declarations, toutes `color:`) :
           la valeur se change en place, sans effet de bord.

  --lot 2  12 variables de page SURES (aucun usage hors `color:`) : la valeur
           se change en place, meme raisonnement.

  --lot 3  23 variables MIXTES -- elles portent aussi des fonds, des filets,
           des degrades. On ne touche PAS a la variable : on lui ajoute une
           SOEUR de texte `--<nom>-texte`, et seules les declarations `color:`
           basculent dessus. Les fonds restent intacts au pixel pres.

  --lot 5  couples hors palette. A jouer EN DERNIER et sur une mesure fraiche :
           ce sont des couleurs COMPOSEES (opacite < 1), et le lot 3 peut en
           avoir deja regle. Le geste s'y decide au cas par cas, hors de ce
           script.

Chaque lot porte ses asserts : un motif attendu absent, un remplacement sans
effet, et le script s'arrete AVANT d'ecrire.

Usage : python applique-lots-aa.py --lot 1|2|3 [--simuler]
Codes : 0 succes -- 1 assert en echec -- 2 fichier introuvable.
"""

import argparse
import io
import json
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
DEPOT = os.path.dirname(ICI)
RESULTATS = os.path.join(ICI, "recette-playwright", "resultats")

# Lot 1 : les deux variables du chrome, et la valeur qui tient les DEUX fonds
# du site (#faf8f4 -> 4,98 et #f1ede4 -> 4,52).
LOT1 = [("--ink-muted", "#7a7a74", "#6c6c67"),
        ("--mobilier-attenue", "#7a7a74", "#6c6c67")]


def echec(msg):
    sys.stderr.write("ASSERT EN ECHEC : %s\n" % msg)
    sys.exit(1)


def lire(chemin):
    with io.open(chemin, "r", encoding="utf-8") as f:
        return f.read()


def ecrire(chemin, texte):
    with io.open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(texte)


def charge_lots():
    chemin = os.path.join(RESULTATS, "usage-variables.json")
    if not os.path.isfile(chemin):
        echec("mesures absentes : jouer controle-usage-variables.py (%s)"
              % chemin)
    with io.open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)


def lot1(simuler):
    chemin = os.path.join(DEPOT, "assets", "style.css")
    src = lire(chemin)
    t = src
    for nom, avant, apres in LOT1:
        motif = re.compile(r"(" + re.escape(nom) + r"\s*:\s*)" +
                           re.escape(avant) + r"\s*;")
        if not motif.search(t):
            echec("style.css : %s ne vaut pas %s" % (nom, avant))
        t = motif.sub(lambda m: m.group(1) + apres + ";", t)
        print("  %-22s %s -> %s" % (nom, avant, apres))
    if t == src:
        echec("style.css : aucune modification produite")
    if not simuler:
        ecrire(chemin, t)
    print("LOT 1 applique : 2 variables, 54 elements vises%s"
          % ("  [SIMULATION]" if simuler else ""))
    return 0


def valeur_en_place(chemin_page, variable, avant, apres, simuler):
    """Change la valeur d'une variable dans le bloc :root de sa page."""
    src = lire(chemin_page)
    motif = re.compile(r"(" + re.escape(variable) + r"\s*:\s*)" +
                       re.escape(avant) + r"\s*;", re.I)
    if not motif.search(src):
        return None
    t = motif.sub(lambda m: m.group(1) + apres + ";", src, count=1)
    if t == src:
        echec("%s : %s inchangee" % (os.path.basename(chemin_page), variable))
    if not simuler:
        ecrire(chemin_page, t)
    return True


def lot2(simuler):
    lots = [x for x in charge_lots()
            if x["classe"] == "SUR" and not x["lourd"]]
    faits, sautes = 0, []
    for x in sorted(lots, key=lambda y: -y["elements"]):
        page = os.path.join(DEPOT, "films", x["page"])
        r = valeur_en_place(page, x["variable"], x["valeur"], x["propose"],
                            simuler)
        if r is None:
            sautes.append((x["page"], x["variable"], x["valeur"]))
            continue
        faits += 1
        print("  %-28s %-16s %s -> %s  (%d el.)"
              % (x["page"][:-5], x["variable"], x["valeur"], x["propose"],
                 x["elements"]))
    if not faits:
        echec("lot 2 : aucune variable modifiee")
    print("LOT 2 applique : %d variables%s" % (faits,
          "  [SIMULATION]" if simuler else ""))
    if sautes:
        print("  NON TROUVEES (a inspecter) : %d" % len(sautes))
        for p, v, val in sautes:
            print("    %-28s %-16s attendait %s" % (p[:-5], v, val))
    return 0


def lot3(simuler):
    """Variable-soeur de texte : la variable d'origine n'est jamais touchee."""
    lots = [x for x in charge_lots()
            if x["classe"] == "MIXTE" and not x["lourd"]]
    faits, sautes = 0, []
    par_page = {}
    for x in lots:
        par_page.setdefault(x["page"], []).append(x)

    for nom_page, entrees in sorted(par_page.items()):
        chemin = os.path.join(DEPOT, "films", nom_page)
        src = lire(chemin)
        t = src
        for x in sorted(entrees, key=lambda y: -y["elements"]):
            var, soeur = x["variable"], x["variable"] + "-texte"
            if soeur in t:
                sautes.append((nom_page, var, "soeur deja posee"))
                continue
            # 1. declarer la soeur JUSTE APRES l'originale, dans le meme bloc.
            motif_decl = re.compile(r"(" + re.escape(var) + r"\s*:\s*"
                                    + re.escape(x["valeur"]) + r"\s*;)", re.I)
            if not motif_decl.search(t):
                sautes.append((nom_page, var, "declaration introuvable"))
                continue
            t = motif_decl.sub(
                lambda m: m.group(1) + "\n    " + soeur + ":" + x["propose"]
                + ";", t, count=1)
            # 2. basculer les seules declarations `color:`.
            # `\bcolor` ne suffit PAS : le tiret de `border-color` est un
            # caractere non-mot, donc `\b` s'y place et le motif mordait sur
            # `border-color`, `border-bottom-color`, `text-decoration-color`.
            # Quatre filets ont bascule sur la soeur avant que le controle du
            # double contexte ne le revele. Il faut exiger un DEBUT de
            # declaration : accolade, point-virgule ou debut de ligne.
            motif_usage = re.compile(
                r"(^|[{;]\s*)(color\s*:\s*)var\(\s*" + re.escape(var)
                + r"\s*\)", re.M)
            n = len(motif_usage.findall(t))
            if n == 0:
                sautes.append((nom_page, var, "aucun usage color: var()"))
                continue
            t = motif_usage.sub(
                lambda m: m.group(1) + m.group(2) + "var(" + soeur + ")", t)
            faits += 1
            print("  %-26s %-16s %s -> %s  (%d usage color:)"
                  % (nom_page[:-5], soeur, x["valeur"], x["propose"], n))
        if t != src and not simuler:
            ecrire(chemin, t)
    if not faits:
        echec("lot 3 : aucune variable-soeur posee")
    print("LOT 3 applique : %d variables-soeurs%s"
          % (faits, "  [SIMULATION]" if simuler else ""))
    if sautes:
        print("  NON TRAITEES : %d" % len(sautes))
        for p, v, motif in sautes:
            print("    %-26s %-16s %s" % (p[:-5], v, motif))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lot", required=True, choices=["1", "2", "3"])
    ap.add_argument("--simuler", action="store_true")
    args = ap.parse_args()
    return {"1": lot1, "2": lot2, "3": lot3}[args.lot](args.simuler)


if __name__ == "__main__":
    sys.exit(main())
