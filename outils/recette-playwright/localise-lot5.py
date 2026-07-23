#!/usr/bin/env python3
# -*- coding: ascii -*-
"""localise-lot5.py -- retrouver les 7 couples "hors palette" du lot 5.

Ces couleurs n'existent nulle part dans les pages : ce sont des couleurs
COMPOSEES. Un texte a 0,82 d'opacite sur un fond creme ne rend pas sa couleur
declaree mais un melange des deux -- et c'est ce melange que la sonde mesure,
a juste titre, puisque c'est ce que l'oeil voit.

Corriger demande donc de remonter du rendu a la DECLARATION : quel element,
quelle couleur ecrite, quelle opacite. Le script ne corrige rien ; il rend la
fiche de chaque cas pour que la correction porte au bon endroit.

Usage : RECETTE_BASE=http://127.0.0.1:8791 python localise-lot5.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harnais  # noqa: E402

# Les 7 couples du lot 5, tels que soumis a AH.
CIBLES = [
    ("shutter-island.html", "#aa4c41", "#ece3ca"),
    ("au-fil-de-leau.html", "#c39f5e", "#415343"),
    ("le-doulos.html", "#576b77", "#ece5d5"),
    ("le-golem.html", "#80796c", "#171310"),
    ("rosetta.html", "#d96d30", "#d8d5c9"),
    ("sur-la-route-domaha.html", "#be653f", "#f1e9d8"),
    ("waterloo.html", "#958b77", "#3f321b"),
]

JS = r"""
(cible) => {
  const sortie = [];
  for (const el of document.querySelectorAll('*')) {
    let propre = '';
    for (const n of el.childNodes) if (n.nodeType === 3) propre += n.nodeValue;
    if (!propre.trim()) continue;
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;

    let opacite = 1;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const o = parseFloat(getComputedStyle(n).opacity);
      if (!isNaN(o)) opacite *= o;
    }
    const fond = window.__fondEffectif(el);
    const brut = window.__lireRgba(st.color);
    if (!brut) continue;
    const alpha = brut.a * opacite;
    const texte = alpha >= 0.999 ? brut
                : window.__composer({r: brut.r, g: brut.g, b: brut.b, a: alpha}, fond);
    if (window.__hex(texte).toLowerCase() !== cible.texte) continue;

    sortie.push({
      chemin: window.__chemin(el),
      balise: el.tagName.toLowerCase(),
      classe: (typeof el.className === 'string' ? el.className : '') || '',
      couleur_declaree: st.color,
      opacite_element: parseFloat(st.opacity),
      opacite_effective: Math.round(opacite * 1000) / 1000,
      fond_effectif: window.__hex(fond),
      px: parseFloat(st.fontSize),
      extrait: propre.trim().slice(0, 50),
    });
  }
  return sortie;
}
"""


def main():
    sync = harnais.playwright_ou_arret()
    fiches = []
    with sync() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        for nom, texte, fond in CIBLES:
            page.goto(harnais.url("films/" + nom), wait_until="load",
                      timeout=30000)
            page.evaluate(harnais.JS_FOND_EFFECTIF)
            page.wait_for_timeout(110)
            trouves = page.evaluate(JS, {"texte": texte})
            print("=== %s  texte rendu %s sur %s : %d element(s)"
                  % (nom, texte, fond, len(trouves)))
            for t in trouves:
                print("    %-34s declaree=%-22s opac=%.2f  %s"
                      % (t["chemin"][-34:], t["couleur_declaree"],
                         t["opacite_effective"], t["extrait"][:34]))
                fiches.append(dict(t, page=nom, texte_rendu=texte, fond=fond))
        ctx.close()
        nav.close()
    harnais.ecrire_json("lot5-localisation.json", fiches)
    print("")
    print("elements localises : %d" % len(fiches))
    return 0


if __name__ == "__main__":
    sys.exit(main())
