#!/usr/bin/env python3
# -*- coding: ascii -*-
"""sonde-mobilier.py -- ou se cale le mobilier sur chaque page ?

Arbitrage AH du 22/07/2026 (option B) : le mobilier partage (cartouche de
provenance, bandeau de variante) s'aligne sur la COLONNE EDITORIALE de sa
page, et non sur le menu. Comme les 33 ossatures bespoke n'ont pas la meme
colonne, la valeur ne se devine pas : elle se MESURE, page par page, au
rendu reel.

La sonde CONSTATE et n'ecrit rien dans le site. Elle produit
`resultats/mobilier.json`, que `outils/normalise-v2.py --regle calage-mobilier`
consomme pour poser la variable `--mobilier-largeur`.

Une page qui declare son propre `.wrap` est EXCLUE : sa regle l'emporte par la
cascade, elle a ete ecrite a dessein, et la variable n'y aurait aucun effet.

Usage : RECETTE_BASE=http://127.0.0.1:8791 python sonde-mobilier.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harnais  # noqa: E402

# Le mobilier porte 1.6rem de marge interne de chaque cote (mobilier.css).
PADDING_TOTAL_PX = 51.2
RACINE_PX = 16.0

MESURE = """() => {
  const res = {};
  const wrap = document.querySelector('.wrap');
  res.wrap = wrap ? Math.round(wrap.getBoundingClientRect().width) : null;
  res.wrapMaxWidth = wrap ? getComputedStyle(wrap).maxWidth : null;
  // La colonne editoriale, c'est le BLOC QUI CONTIENT le texte, pas le
  // paragraphe. La distinction n'est pas theorique : 3 pages sur 33 bornent
  // leurs paragraphes (max-width en ch) a l'interieur d'un conteneur plus
  // large et cale a gauche. Mesurer le paragraphe y decalait le mobilier de
  // plus de 100 px -- dans l'autre sens. On mesure donc le parent.
  let col = null;
  for (const p of document.querySelectorAll('section p')) {
    const r = p.getBoundingClientRect();
    if (r.width > 200) {
      const parent = p.parentElement;
      col = parent ? parent.getBoundingClientRect() : r;
      res.paragraphe = Math.round(r.width);
      res.conteneur = parent ? parent.tagName.toLowerCase()
                             + (parent.className ? '.' + String(parent.className).split(' ')[0] : '')
                             : null;
      break;
    }
  }
  res.colonne = col ? Math.round(col.width) : null;
  res.colonneGauche = col ? Math.round(col.left) : null;
  const c = document.querySelector('.cartouche');
  res.cartoucheGauche = c ? Math.round(c.getBoundingClientRect().left) : null;
  res.scrollWidth = document.documentElement.scrollWidth;
  res.innerWidth = window.innerWidth;
  return res;
}"""


def page_declare_son_wrap(chemin_html):
    import io
    import re
    with io.open(chemin_html, "r", encoding="utf-8") as f:
        t = f.read()
    return bool(re.search(r"\.wrap\s*\{", t))


def main():
    sync = harnais.playwright_ou_arret()
    pages = harnais.pages_films()
    resultats = []
    with sync() as p:
        nav = p.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        for chemin in pages:
            page.goto(harnais.url(chemin), wait_until="networkidle")
            page.wait_for_timeout(120)
            m = page.evaluate(MESURE)
            nom = os.path.basename(chemin)
            propre = page_declare_son_wrap(
                os.path.join(harnais.DOSSIER_FILMS, nom))
            entree = {
                "page": nom,
                "declare_son_wrap": propre,
                "colonne_px": m["colonne"],
                "wrap_px": m["wrap"],
                "decalage_px": (None if m["cartoucheGauche"] is None
                                or m["colonneGauche"] is None
                                else m["cartoucheGauche"] - m["colonneGauche"]),
                "debordement_px": m["scrollWidth"] - m["innerWidth"],
            }
            # Depuis le correctif structurel du 22/07 20h34, le mobilier porte
            # sa propre classe : qu'une page declare ou non son `.wrap`
            # d'ossature ne le concerne plus, et n'exclut donc plus du calage.
            # Le champ reste mesure, a titre informatif.
            if not m["colonne"]:
                entree["largeur_proposee_rem"] = None
                entree["motif"] = "colonne editoriale non mesurable"
            else:
                rem = (m["colonne"] + PADDING_TOTAL_PX) / RACINE_PX
                entree["largeur_proposee_rem"] = round(rem, 1)
            resultats.append(entree)
            print("%-32s colonne=%-5s wrap=%-5s decalage=%-5s -> %s" % (
                nom, entree["colonne_px"], entree["wrap_px"],
                entree["decalage_px"],
                entree["largeur_proposee_rem"] or entree.get("motif")))
        nav.close()
    harnais.ecrire_json("mobilier.json", resultats)
    a_caler = [r for r in resultats if r["largeur_proposee_rem"]]
    print("")
    print("pages mesurees          : %d" % len(resultats))
    print("pages a caler           : %d" % len(a_caler))
    print("pages hors calage       : %d" % (len(resultats) - len(a_caler)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
