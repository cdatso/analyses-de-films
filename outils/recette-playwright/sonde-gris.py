#!/usr/bin/env python3
# -*- coding: ascii -*-
"""sonde-gris.py -- P-22 : la distinction de volet ne repose jamais sur la
seule couleur.

Le prototype avait etabli la regle par construction (le cartouche NOMME le
regime, l'Etude porte son appareil theorique) mais laissait le rendu en
niveaux de gris "non verifiable".

Deux preuves, l'une mecanique et l'autre visuelle :
  1. FORME -- les proprietes de bordure du marqueur de volet (P-21) sont
     lues aux styles calcules sur une page de chaque volet. Si `border-style`
     et `border-width` different, la distinction survit a la suppression de
     toute couleur : c'est une difference de FORME.
  2. IMAGE -- captures du cartouche des deux volets avec `filter:
     grayscale(1)` applique a la page : ce que voit un lecteur qui ne
     distingue pas les couleurs.

Cette sonde ne modifie aucun fichier du site ; elle ecrit des PNG dans
docs/recette-v2-captures/.
"""

import os
import sys

import harnais

PAIRE = [
    ("critique", "films/pandora.html"),
    ("etude", "films/pandora-contrechamp.html"),
]

JS_MARQUEUR = r"""
() => {
  const c = document.querySelector('.cartouche');
  if (!c) return {erreur: 'cartouche absent'};
  const st = getComputedStyle(c);
  const porteur = c.closest('[data-volet]');
  return {
    volet_declare: porteur ? porteur.getAttribute('data-volet') : null,
    borderTopStyle: st.borderTopStyle,
    borderTopWidth: st.borderTopWidth,
    borderTopColor: st.borderTopColor,
    borderBottomStyle: st.borderBottomStyle,
    borderBottomWidth: st.borderBottomWidth,
    variable_volet: getComputedStyle(porteur || document.documentElement)
                      .getPropertyValue('--volet').trim(),
    regime_en_toutes_lettres: (c.querySelector('.regime') || {}).textContent || null,
  };
}
"""


def main():
    sync_playwright = harnais.playwright_ou_arret()
    dossier = os.path.join(harnais.DOSSIER_DOCS, "recette-v2-captures")
    assert os.path.isdir(harnais.DOSSIER_DOCS), "docs/ introuvable"
    if not os.path.isdir(dossier):
        os.makedirs(dossier)

    mesures = {}
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(viewport={"width": 900, "height": 900})
        page = ctx.new_page()
        for volet, cible in PAIRE:
            page.goto(harnais.url(cible), wait_until="load", timeout=30000)
            page.wait_for_timeout(200)
            mesures[volet] = page.evaluate(JS_MARQUEUR)

            # Capture du cartouche en niveaux de gris.
            page.add_style_tag(content="html { filter: grayscale(1) !important; }")
            page.wait_for_timeout(150)
            el = page.query_selector(".cartouche")
            if el:
                el.screenshot(path=os.path.join(
                    dossier, "gris-cartouche-%s.png" % volet))
            page.screenshot(path=os.path.join(
                dossier, "gris-page-%s.png" % volet), full_page=False)
        ctx.close()
        nav.close()

    harnais.ecrire_json("gris.json", mesures)

    print("P-22 -- distinction de volet hors couleur")
    print("")
    for volet, m in mesures.items():
        if "erreur" in m:
            print("  %s : %s" % (volet, m["erreur"]))
            continue
        print("  volet declare      : %s" % m["volet_declare"])
        print("    --volet          : %s" % m["variable_volet"])
        print("    bordure haute    : %s %s (%s)" % (
            m["borderTopStyle"], m["borderTopWidth"], m["borderTopColor"]))
        print("    bordure basse    : %s %s" % (
            m["borderBottomStyle"], m["borderBottomWidth"]))
        print("    regime en clair  : %s" % (
            (m["regime_en_toutes_lettres"] or "").strip()[:60]))
        print("")

    a, b = mesures.get("critique", {}), mesures.get("etude", {})
    forme = (a.get("borderTopStyle"), a.get("borderTopWidth")) != \
            (b.get("borderTopStyle"), b.get("borderTopWidth"))
    texte = (a.get("regime_en_toutes_lettres") or "") != \
            (b.get("regime_en_toutes_lettres") or "")
    print("  difference de FORME (style/epaisseur)  : %s" % ("OUI" if forme else "NON"))
    print("  difference en TOUTES LETTRES           : %s" % ("OUI" if texte else "NON"))
    print("  VERDICT P-22 : %s" % (
        "OK -- la distinction survit a la perte de la couleur"
        if (forme and texte) else "ECART -- la couleur porte seule la distinction"))
    print("")
    print("captures en niveaux de gris versees dans %s" % dossier)
    return 0


if __name__ == "__main__":
    sys.exit(main())
