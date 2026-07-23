#!/usr/bin/env python3
# -*- coding: ascii -*-
"""controle-usage-variables.py -- une variable ne se corrige pas a l'aveugle.

Le lot "une variable de palette" n'est SUR que si la variable ne sert qu'a
colorer du TEXTE. Beaucoup n'en sont pas la : dans une palette bespoke, la
meme nuance sert souvent de fond ici, de filet la, de texte ailleurs.
Assombrir `--platre` de 60 % pour rattraper un cartel, c'est repeindre la
couverture du film.

Le script classe donc chaque variable en echec :

  SUR       la variable n'apparait QUE comme `color:` -- la corriger ne
            deplace que du texte, et le lot peut etre gate en bloc ;
  MIXTE     la variable sert aussi de fond, de bordure ou de degrade -- la
            corriger deborderait de l'ecart. Traitement LOCAL (une regle
            dediee au texte fautif) ou exception documentee ;
  A VOIR    usage non determine par l'analyse statique.

Aucune ecriture. Produit `resultats/usage-variables.json`.

Usage : python controle-usage-variables.py  (apres analyse-lots-aa.py)
"""

import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harnais  # noqa: E402

# Proprietes ou une variable ne colore PAS du texte.
NON_TEXTE = ("background", "border", "outline", "box-shadow", "fill",
             "stroke", "gradient", "text-shadow", "caret-color",
             "text-decoration-color", "column-rule", "accent-color")


def usages(page_html, variable):
    """Rend (n_color, n_autre, exemples) pour une variable dans une page."""
    with io.open(page_html, "r", encoding="utf-8") as f:
        t = f.read()
    n_color, n_autre, exemples = 0, 0, []
    motif = re.compile(r"([a-z-]+)\s*:\s*([^;{}]*var\(\s*"
                       + re.escape(variable) + r"\s*[,)][^;{}]*)")
    for m in motif.finditer(t):
        prop, valeur = m.group(1), m.group(2)
        if prop == "color":
            n_color += 1
        else:
            n_autre += 1
            if len(exemples) < 3:
                exemples.append(prop)
        del valeur
    # Un degrade cite la variable sans que la propriete soit nommee juste
    # avant : on le cherche a part.
    for m in re.finditer(r"(linear|radial|conic)-gradient\([^;]*var\(\s*"
                         + re.escape(variable) + r"\s*[,)]", t):
        n_autre += 1
        if "gradient" not in exemples:
            exemples.append("gradient")
        del m
    return n_color, n_autre, exemples


def main():
    chemin = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "resultats", "lots-aa.json")
    if not os.path.isfile(chemin):
        sys.stderr.write("ARRET : jouer d'abord analyse-lots-aa.py\n")
        return 2
    with io.open(chemin, "r", encoding="utf-8") as f:
        donnees = json.load(f)

    sortie = []
    for lot in donnees["lots"]:
        page = os.path.join(harnais.DOSSIER_FILMS, lot["page"])
        n_color, n_autre, ex = usages(page, lot["variable"])
        if n_color and not n_autre:
            classe = "SUR"
        elif n_autre:
            classe = "MIXTE"
        else:
            classe = "A VOIR"
        e = dict(lot)
        e.update({"usages_color": n_color, "usages_autres": n_autre,
                  "exemples_autres": ex, "classe": classe})
        sortie.append(e)

    harnais.ecrire_json("usage-variables.json", sortie)

    for classe in ("SUR", "MIXTE", "A VOIR"):
        v = [x for x in sortie if x["classe"] == classe]
        print("%-7s : %2d lot(s), %3d element(s)"
              % (classe, len(v), sum(x["elements"] for x in v)))
    print("")
    surs = [x for x in sortie if x["classe"] == "SUR"]
    fins = [x for x in surs if not x["lourd"]]
    print("Lots SURS et a deplacement FIN : %d lots, %d elements"
          % (len(fins), sum(x["elements"] for x in fins)))
    print("")
    print("--- MIXTES : la variable sert aussi ailleurs ---")
    for x in sorted([y for y in sortie if y["classe"] == "MIXTE"],
                    key=lambda y: -y["elements"]):
        print("  %-26s %-16s %d texte / %d autre(s) : %s"
              % (x["page"][:-5], x["variable"], x["usages_color"],
                 x["usages_autres"], ", ".join(x["exemples_autres"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
