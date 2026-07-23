#!/usr/bin/env python3
# -*- coding: ascii -*-
"""dedouble-contexte.py -- une variable, deux contextes de fond.

Gate d'AH du 23/07/2026 : "go pour la passe dedoublement".

LE PROBLEME. Une variable de texte se pose parfois sur un fond clair ET sur un
fond sombre dans la meme page. Pour un fond de luminance Lf, le texte convient
s'il est assez sombre (L <= (Lf+0.05)/s-0.05) OU assez clair
(L >= s*(Lf+0.05)-0.05). Quand la page melange un fond a L=0,85 et un fond a
L=0,01, aucune des deux strategies ne tient sur les deux : il n'existe
mathematiquement aucune valeur unique. Iterer ne converge pas, la correction
oscille d'un fond a l'autre.

LA SOLUTION, ET POURQUOI ELLE NE REECRIT AUCUNE REGLE. En CSS, une variable se
REDEFINIT dans un sous-arbre. Il suffit donc de declarer, sur l'element qui
porte le fond minoritaire, la valeur adaptee a ce fond : tous les
`color: var(--x)` de ce sous-arbre la prennent par cascade, sans qu'un seul
selecteur de texte soit touche. C'est la palette qui devient contextuelle, ce
qui est precisement ce qu'une palette bespoke devrait etre.

DEUX PRECAUTIONS.
  1. La redefinition porte sur TOUT le sous-arbre : si la variable sert aussi
     de fond ou de filet, elle les deplacerait la aussi. Les variables MIXTES
     recoivent donc d'abord une soeur de texte (meme geste qu'au lot 3), et
     c'est la soeur qu'on redefinit.
  2. Le contexte MAJORITAIRE garde la valeur de `:root`. On ne redefinit que
     la minorite -- le diff reste petit et lisible.

Usage : python dedouble-contexte.py [--simuler]
Codes : 0 succes -- 1 assert en echec -- 2 mesures absentes.
"""

import argparse
import colorsys
import io
import json
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
DEPOT = os.path.dirname(ICI)
RESULTATS = os.path.join(ICI, "recette-playwright", "resultats")

MARQUE = "/* Palette contextuelle (AA, retrofit 065-5) */"


def echec(msg):
    sys.stderr.write("ASSERT EN ECHEC : %s\n" % msg)
    sys.exit(1)


def lire(c):
    with io.open(c, "r", encoding="utf-8") as f:
        return f.read()


def ecrire(c, t):
    with io.open(c, "w", encoding="utf-8", newline="\n") as f:
        f.write(t)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(c))))
                                   for c in rgb)


def luminance(rgb):
    def c(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (c(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = luminance(a), luminance(b)
    if la < lb:
        la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)


def corrige(texte_hex, fond_hex, seuil):
    t, f = hex_rgb(texte_hex), hex_rgb(fond_hex)
    if ratio(t, f) >= seuil:
        return texte_hex
    h, l, s = colorsys.rgb_to_hls(*[c / 255.0 for c in t])
    for sens in (1, -1):
        # On tente d'abord le sens naturel (s'eloigner du fond), puis l'autre.
        pas = sens * (0.002 if luminance(f) < luminance(t) else -0.002)
        l2 = l
        for _ in range(600):
            l2 += pas
            if not 0.0 <= l2 <= 1.0:
                break
            cand = tuple(c * 255.0 for c in colorsys.hls_to_rgb(h, l2, s))
            if ratio(cand, f) >= seuil:
                return rgb_hex(cand)
    for extreme in ((255, 255, 255), (0, 0, 0)):
        if ratio(extreme, f) >= seuil:
            return rgb_hex(extreme)
    return None


def est_mixte(texte_page, variable):
    for m in re.finditer(r"([a-z-]+)\s*:\s*[^;{}]*var\(\s*"
                         + re.escape(variable) + r"\s*[,)]", texte_page):
        if m.group(1) != "color":
            return True
    return bool(re.search(r"gradient\([^;]*var\(\s*" + re.escape(variable)
                          + r"\s*[,)]", texte_page))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--simuler", action="store_true")
    args = ap.parse_args()

    chemin = os.path.join(RESULTATS, "double-contexte.json")
    if not os.path.isfile(chemin):
        echec("mesures absentes : jouer sonde-double-contexte.py")
    with io.open(chemin, "r", encoding="utf-8") as f:
        cas = [x for x in json.load(f) if not x["possible"]]

    faits, sautes = 0, []
    par_page = {}
    for x in cas:
        par_page.setdefault(x["page"], []).append(x)

    for nom_page, entrees in sorted(par_page.items()):
        fichier = os.path.join(DEPOT, "films", nom_page)
        src = lire(fichier)
        t = src
        regles = []
        for x in entrees:
            var = x["variable"]
            # Le contexte MAJORITAIRE (le plus d'elements) garde :root.
            fonds = sorted(x["fonds"].items(),
                           key=lambda kv: -kv[1]["elements"])
            majoritaire, f_majo = fonds[0]
            minoritaires = [(h, f) for h, f in fonds[1:] if f["echecs"]]

            # CAS INVERSE : c'est le contexte MAJORITAIRE qui echoue (souvent
            # le fond du body, qu'aucun selecteur ne peut cibler autrement que
            # par la racine). On corrige alors :root POUR LUI, et on rend sa
            # valeur d'origine aux contextes ou elle marchait -- meme
            # mecanique, sens oppose.
            # Un fond dont aucun porteur n'est nommable est le fond de la PAGE
            # elle-meme : le seul selecteur qui l'atteint est la racine. Il
            # commande donc :root, qu'il soit majoritaire ou non.
            def sans_porteur(f):
                return not [p for p in f["porteurs"] if p and p != "body"]

            racine_cible = None
            if f_majo["echecs"] > 0:
                racine_cible = (majoritaire, f_majo)
            else:
                for h, f in minoritaires:
                    if sans_porteur(f):
                        racine_cible = (h, f)
                        break
            inverse = racine_cible is not None
            if not minoritaires and not inverse:
                sautes.append((nom_page, var, "aucun contexte en echec"))
                continue

            cible = var
            if est_mixte(t, var):
                soeur = var + "-texte"
                if soeur not in t:
                    decl = re.compile(r"(" + re.escape(var) + r"\s*:\s*"
                                      + re.escape(x["valeur"]) + r"\s*;)", re.I)
                    if not decl.search(t):
                        sautes.append((nom_page, var, "declaration absente"))
                        continue
                    t = decl.sub(lambda m: m.group(1) + "\n    " + soeur + ":"
                                 + x["valeur"] + ";", t, count=1)
                    usage = re.compile(r"(^|[{;]\s*)(color\s*:\s*)var\(\s*"
                                       + re.escape(var) + r"\s*\)", re.M)
                    if not usage.search(t):
                        sautes.append((nom_page, var, "aucun color: var()"))
                        continue
                    t = usage.sub(lambda m: m.group(1) + m.group(2)
                                  + "var(" + soeur + ")", t)
                cible = soeur

            if inverse:
                # 1. la racine se corrige pour le contexte qui la commande ;
                fond_racine, f_racine = racine_cible
                racine = corrige(x["valeur"], fond_racine, f_racine["seuil"])
                if not racine:
                    sautes.append((nom_page, var,
                                   "aucune valeur ne tient sur %s"
                                   % fond_racine))
                    continue
                # La substitution doit porter sur la declaration de :root, et
                # sur elle SEULE. Sans cet ancrage, elle mordait sur la
                # premiere occurrence rencontree -- y compris une regle
                # contextuelle posee par une passe precedente, dont la valeur
                # aurait ete remplacee par celle du contexte oppose. Le bloc
                # :root est isole d'abord ; le remplacement s'y fait, puis le
                # bloc est reinsere a sa place.
                m_root = re.search(r":root\s*\{", t)
                if not m_root:
                    sautes.append((nom_page, var, "pas de bloc :root"))
                    continue
                debut = m_root.end()
                fin_root = t.find("}", debut)
                bloc_root = t[debut:fin_root]
                decl = re.compile(r"(" + re.escape(cible) + r"\s*:\s*)"
                                  + re.escape(x["valeur"]) + r"\s*;", re.I)
                if not decl.search(bloc_root):
                    sautes.append((nom_page, var,
                                   "%s ne vaut pas %s dans :root"
                                   % (cible, x["valeur"])))
                    continue
                t = (t[:debut]
                     + decl.sub(lambda m: m.group(1) + racine + ";",
                                bloc_root, count=1)
                     + t[fin_root:])
                print("  %-26s %-20s :root %s -> %s (pour %s)"
                      % (nom_page[:-5], cible, x["valeur"], racine,
                         fond_racine))
                faits += 1
                # 2. les contextes ou l'ancienne valeur marchait la gardent.
                for fond_hex, f in fonds:
                    if fond_hex == fond_racine:
                        continue
                    if f["echecs"]:
                        continue
                    porteurs = [p for p in f["porteurs"] if p and p != "body"]
                    if not porteurs:
                        continue
                    regles.append((", ".join(porteurs), cible, x["valeur"],
                                   fond_hex, f["elements"]))
                continue

            for fond_hex, f in minoritaires:
                porteurs = [p for p in f["porteurs"] if p and p != "body"]
                if not porteurs:
                    sautes.append((nom_page, var,
                                   "fond %s sans porteur nommable" % fond_hex))
                    continue
                valeur = corrige(x["valeur"], fond_hex, f["seuil"])
                if not valeur:
                    sautes.append((nom_page, var,
                                   "aucune valeur ne tient sur %s" % fond_hex))
                    continue
                # IDEMPOTENCE. Sans ce garde-fou, une seconde execution
                # reecrit les memes selecteurs avec des valeurs a un
                # centieme pres : le bloc de palette contextuelle doublerait
                # a chaque passe. On ne redefinit jamais deux fois le meme
                # couple (selecteur, variable).
                selecteur = ", ".join(porteurs)
                if re.search(re.escape(selecteur) + r"\s*\{\s*"
                             + re.escape(cible) + r"\s*:", t):
                    sautes.append((nom_page, var,
                                   "deja redefinie sur %s" % selecteur))
                    continue
                regles.append((selecteur, cible, valeur, fond_hex,
                               f["elements"]))
                faits += 1

        if regles:
            bloc = ["", "  " + MARQUE,
                    "  /* Ces variables colorent du texte sur DEUX fonds"
                    " inconciliables : aucune",
                    "     valeur unique ne tient les deux (voir"
                    " sonde-double-contexte.py). La valeur",
                    "     de :root sert le contexte majoritaire ; ici, le"
                    " contexte minoritaire. */"]
            for sel, cible, valeur, fond_hex, n in regles:
                bloc.append("  %s{ %s:%s; }   /* sur %s, %d element(s) */"
                            % (sel, cible, valeur, fond_hex, n))
            fin = t.rfind("</style>")
            if fin < 0:
                echec("%s : pas de </style>" % nom_page)
            t = t[:fin] + "\n".join(bloc) + "\n" + t[fin:]
            for sel, cible, valeur, fond_hex, n in regles:
                print("  %-26s %-20s %s sur %s (%s)"
                      % (nom_page[:-5], cible, valeur, fond_hex, sel[:26]))

        if t != src and not args.simuler:
            ecrire(fichier, t)

    print("")
    print("redefinitions contextuelles : %d%s"
          % (faits, "  [SIMULATION]" if args.simuler else ""))
    if sautes:
        print("non traitees : %d" % len(sautes))
        for p, v, motif in sautes:
            print("   %-26s %-18s %s" % (p[:-5], v, motif))
    return 0


if __name__ == "__main__":
    sys.exit(main())
