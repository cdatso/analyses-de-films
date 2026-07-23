#!/usr/bin/env python3
# -*- coding: ascii -*-
"""analyse-lots-aa.py -- remonte des couples de couleurs aux VARIABLES.

Le regroupement par couple de couleurs (sonde-contraste-lots.py) ramene 242
elements a 116 couples : c'est deja mieux que 242 decisions, mais toujours
trop pour des gates. Il reste un cran a monter.

Ces couleurs ne sont pas dispersees dans les pages : chaque page bespoke
declare sa palette dans son bloc `:root`, sous forme de VARIABLES nommees
(`--gris`, `--sable`, `--encre-douce`...). Un meme `--gris` alimente le
sommaire, les legendes, le pied de page et les cartels : corriger LA VARIABLE
corrige tous ses couples a la fois, sans toucher a une seule regle.

Le lot pertinent est donc : UNE VARIABLE, DANS UNE PAGE. La decision porte sur
un mot ("cette nuance de gris descend de 3 %"), pas sur une liste d'elements.

Ce script ne modifie rien. Il produit `resultats/lots-aa.json` et le tableau
que la session soumet a AH.

Usage : python analyse-lots-aa.py   (apres sonde-contraste-lots.py)
"""

import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harnais  # noqa: E402

# Un deplacement de clarte au-dela de ce seuil ne se voit plus comme un
# ajustement mais comme un CHANGEMENT DE COULEUR : il ne se traite pas dans
# le meme lot, et se signale a part.
SEUIL_LOURD = 0.15


def variables_de_page(chemin):
    """Rend {valeur hex minuscule : [noms de variables]} pour une page."""
    with io.open(chemin, "r", encoding="utf-8") as f:
        t = f.read()
    trouve = {}
    for m in re.finditer(r"(--[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\s*;", t):
        nom, val = m.group(1), m.group(2).lower()
        if len(val) == 4:  # #abc -> #aabbcc
            val = "#" + "".join(c * 2 for c in val[1:])
        trouve.setdefault(val[:7], []).append(nom)
    return trouve


def main():
    resultats = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "resultats", "contraste-lots.json")
    if not os.path.isfile(resultats):
        sys.stderr.write("ARRET : jouer d'abord sonde-contraste-lots.py\n")
        return 2
    with io.open(resultats, "r", encoding="utf-8") as f:
        couples = json.load(f)

    # Palette de chaque page, lue une fois.
    palettes = {}
    for chemin in harnais.pages_films():
        nom = chemin.split("/")[-1]
        palettes[nom] = variables_de_page(
            os.path.join(harnais.DOSSIER_FILMS, nom))

    # Un lot = (page, variable de la couleur de TEXTE). Le fond n'est pas
    # touche : deplacer un fond change l'identite de la page bien plus qu'un
    # texte, et la spec protege l'identite bespoke (A-1).
    lots = {}
    orphelins = []
    for c in couples:
        for page, n_elements in c["pages"].items():
            noms = palettes.get(page, {}).get(c["texte"], [])
            if not noms:
                orphelins.append({"page": page, "texte": c["texte"],
                                  "fond": c["fond"],
                                  "elements": n_elements,
                                  "ratio": c["pire_ratio"],
                                  "propose": c["propose"],
                                  "nature": c["nature"]})
                continue
            variable = sorted(noms)[0]
            cle = (page, variable, c["texte"])
            lot = lots.setdefault(cle, {
                "page": page, "variable": variable, "valeur": c["texte"],
                "fonds": [], "elements": 0, "pire": 99.0,
                "natures": set(), "propositions": []})
            lot["elements"] += n_elements
            lot["pire"] = min(lot["pire"], c["pire_ratio"])
            lot["natures"].add(c["nature"])
            lot["fonds"].append(c["fond"])
            if c["propose"]:
                lot["propositions"].append(
                    (c["propose"], c["deplacement_clarte"] or 0.0, c["fond"]))

    # La valeur retenue pour une variable doit tenir TOUS ses fonds : on garde
    # la proposition la plus exigeante, pas la plus douce.
    sortie = []
    for (page, variable, valeur), lot in lots.items():
        if not lot["propositions"]:
            continue
        propose, deplacement, fond_dur = max(lot["propositions"],
                                             key=lambda p: p[1])
        sortie.append({
            "page": page, "variable": variable, "valeur": valeur,
            "propose": propose, "deplacement": round(deplacement, 3),
            "elements": lot["elements"], "fonds": sorted(set(lot["fonds"])),
            "fond_dimensionnant": fond_dur,
            "pire_ratio": lot["pire"],
            "natures": sorted(lot["natures"]),
            "lourd": deplacement > SEUIL_LOURD,
        })

    sortie.sort(key=lambda x: (x["lourd"], -x["elements"]))
    harnais.ecrire_json("lots-aa.json", {"lots": sortie,
                                         "orphelins": orphelins})

    legers = [x for x in sortie if not x["lourd"]]
    lourds = [x for x in sortie if x["lourd"]]
    print("LOTS (une variable de palette dans une page) : %d" % len(sortie))
    print("  ajustements FINS  (deplacement <= %.2f) : %d lot(s), %d element(s)"
          % (SEUIL_LOURD, len(legers), sum(x["elements"] for x in legers)))
    print("  deplacements LOURDS (> %.2f)            : %d lot(s), %d element(s)"
          % (SEUIL_LOURD, len(lourds), sum(x["elements"] for x in lourds)))
    print("  couples hors palette (valeur ecrite en dur) : %d"
          % len(orphelins))
    print("")
    print("--- les 12 lots les plus rentables ---")
    for x in sortie[:12]:
        print("  %-28s %-16s %s -> %s  %2d el.  ratio %.2f"
              % (x["page"][:-5], x["variable"], x["valeur"], x["propose"],
                 x["elements"], x["pire_ratio"]))
    print("")
    print("--- deplacements lourds (a arbitrer un par un) ---")
    for x in lourds:
        print("  %-28s %-16s %s -> %s  dL=%.2f  %d el."
              % (x["page"][:-5], x["variable"], x["valeur"], x["propose"],
                 x["deplacement"], x["elements"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
