#!/usr/bin/env python3
# -*- coding: ascii -*-
"""applique-lot4.py -- ecrit les corrections que la revue a montrees.

Gate d'AH du 23/07/2026 : "go pour le tout (en bloc)", apres revue visuelle
des 16 fiches.

LES REGLES SONT LUES DANS LA REVUE ELLE-MEME, pas recalculees. Recalculer,
c'est risquer d'appliquer autre chose que ce qui a ete regarde -- la revue est
le document qu'AH a vu, elle fait donc foi. Chaque fiche y porte le CSS exact
en toutes lettres, et c'est lui qu'on ecrit.

Deux gestes selon la forme de la regle :
  `:root{--x:VAL}`       -> la valeur de la variable change dans le bloc :root
                            de la page ; le `!important` de la revue disparait,
                            il n'y servait qu'a passer devant la feuille ;
  `SELECTEUR{color:VAL}` -> une regle est ajoutee en FIN de feuille de page.
                            En fin de feuille, elle l'emporte a specificite
                            egale sans avoir besoin d'`!important`.

Usage : python applique-lot4.py [--simuler]
"""

import argparse
import io
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
DEPOT = os.path.dirname(ICI)
REVUE = os.path.join(os.path.dirname(os.path.dirname(DEPOT)),
                     "_scratch", "revue-lot4", "index.html")

MARQUE = "/* Contraste AA -- lot 4, revue visuelle validee par AH le 23/07 */"


def echec(msg):
    sys.stderr.write("ASSERT EN ECHEC : %s\n" % msg)
    sys.exit(1)


def lire(c):
    with io.open(c, "r", encoding="utf-8") as f:
        return f.read()


def ecrire(c, t):
    with io.open(c, "w", encoding="utf-8", newline="\n") as f:
        f.write(t)


def lit_revue():
    """Rend [(page, css)] dans l'ordre ou la revue les presente."""
    t = lire(REVUE)
    corps = t[t.index("<main>"):]
    sortie, page = [], None
    for m in re.finditer(r"<h2>([^<]+)</h2>|<code>([^<]*\{[^<]*\})</code>",
                         corps):
        if m.group(1):
            page = m.group(1).strip() + ".html"
        elif page:
            sortie.append((page, m.group(2)))
    return sortie


def applique(page_nom, css, simuler):
    chemin = os.path.join(DEPOT, "films", page_nom)
    if not os.path.isfile(chemin):
        echec("page introuvable : %s" % chemin)
    src = lire(chemin)

    m = re.match(r"^:root\{(--[a-z0-9-]+):(#[0-9a-f]{6})\s*!important;\}$",
                 css.strip())
    if m:
        variable, valeur = m.group(1), m.group(2)
        # LA REVUE MONTRAIT LE TEXTE ; ELLE NE MONTRAIT PAS LES FONDS.
        # Quatre de ces variables portent aussi un fond, un filet ou un
        # degrade : en changer la valeur repeindrait tout cela, hors du cadre
        # capture et donc hors de ce qu'AH a valide. Le rendu du TEXTE qu'il a
        # approuve s'obtient a l'identique par une soeur de texte, sans
        # toucher au reste. Meme mecanique qu'au lot 3.
        autres = [x.group(1) for x in re.finditer(
            r"([a-z-]+)\s*:\s*[^;{}]*var\(\s*" + re.escape(variable)
            + r"\s*[,)]", src) if x.group(1) != "color"]
        if re.search(r"gradient\([^;]*var\(\s*" + re.escape(variable)
                     + r"\s*[,)]", src):
            autres.append("gradient")
        if autres:
            soeur = variable + "-texte"
            t = src
            if soeur not in t:
                mr = re.search(r":root\s*\{", t)
                if not mr:
                    echec("%s : pas de bloc :root" % page_nom)
                fin_root = t.find("}", mr.end())
                bloc = t[mr.end():fin_root]
                md = re.search(r"(" + re.escape(variable)
                               + r"\s*:\s*#[0-9a-fA-F]{3,6}\s*;)", bloc)
                if not md:
                    echec("%s : %s introuvable dans :root"
                          % (page_nom, variable))
                bloc = (bloc[:md.end()] + "\n    " + soeur + ":" + valeur + ";"
                        + bloc[md.end():])
                t = t[:mr.end()] + bloc + t[fin_root:]
            else:
                t = re.sub(r"(" + re.escape(soeur) + r"\s*:\s*)#[0-9a-fA-F]{3,6}\s*;",
                           lambda x: x.group(1) + valeur + ";", t, count=1)
            usage = re.compile(r"(^|[{;]\s*)(color\s*:\s*)var\(\s*"
                               + re.escape(variable) + r"\s*\)", re.M)
            n = len(usage.findall(t))
            if n == 0 and soeur not in src:
                echec("%s : aucune declaration color: var(%s)"
                      % (page_nom, variable))
            t = usage.sub(lambda x: x.group(1) + x.group(2) + "var(" + soeur
                          + ")", t)
            if t == src:
                echec("%s : soeur non posee" % page_nom)
            if not simuler:
                ecrire(chemin, t)
            return ("%s -> %s  [SOEUR : %s garde ses %s]"
                    % (soeur, valeur, variable, ", ".join(sorted(set(autres)))))
        # La substitution porte sur le bloc :root, et sur lui seul : une
        # redefinition contextuelle posee par une passe anterieure ne doit pas
        # etre mordue (lecon du 23/07, ancrage de dedouble-contexte.py).
        mr = re.search(r":root\s*\{", src)
        if not mr:
            echec("%s : pas de bloc :root" % page_nom)
        debut = mr.end()
        fin = src.find("}", debut)
        bloc = src[debut:fin]
        md = re.search(r"(" + re.escape(variable) + r"\s*:\s*)#[0-9a-fA-F]{3,6}\s*;",
                       bloc)
        if not md:
            echec("%s : %s introuvable dans :root" % (page_nom, variable))
        nouveau = bloc[:md.start()] + md.group(1) + valeur + ";" \
            + bloc[md.end():]
        t = src[:debut] + nouveau + src[fin:]
        detail = "%s -> %s" % (variable, valeur)
    else:
        m = re.match(r"^(.+?)\{color:(#[0-9a-f]{6})\s*!important;\}$",
                     css.strip())
        if not m:
            echec("%s : regle non reconnue -- %r" % (page_nom, css))
        selecteur, valeur = m.group(1).strip(), m.group(2)
        if selecteur + "{" in src.replace(" ", ""):
            pass  # le selecteur existe deja ailleurs : la regle finale prime
        fin = src.rfind("</style>")
        if fin < 0:
            echec("%s : pas de </style>" % page_nom)
        regle = ("\n  %s\n  %s{ color:%s; }\n"
                 % (MARQUE, selecteur, valeur))
        if regle.strip() in src:
            return None
        t = src[:fin] + regle + src[fin:]
        detail = "%s -> %s" % (selecteur, valeur)

    if t == src:
        echec("%s : aucune modification produite" % page_nom)
    if not simuler:
        ecrire(chemin, t)
    return detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--simuler", action="store_true")
    args = ap.parse_args()

    regles = lit_revue()
    if not regles:
        echec("aucune regle lue dans la revue (%s)" % REVUE)
    print("regles lues dans la revue : %d" % len(regles))
    print("")
    faits = 0
    for page_nom, css in regles:
        detail = applique(page_nom, css, args.simuler)
        if detail is None:
            print("  %-28s deja appliquee" % page_nom[:-5])
            continue
        faits += 1
        print("  %-28s %s" % (page_nom[:-5], detail))
    print("")
    print("corrections ecrites : %d%s"
          % (faits, "  [SIMULATION]" if args.simuler else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
