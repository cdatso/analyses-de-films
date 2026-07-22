#!/usr/bin/env python3
# -*- coding: ascii -*-
"""sonde-geometrie.py -- P-38 (aucun defilement horizontal) et captures T6.

C'est la ligne que le prototype ne pouvait pas verifier : son moteur ne
composait pas d'image, `clientWidth` valait 0. Chromium compose : la mesure
devient possible.

Critere P-38 : a 320 px, `scrollWidth` du document ne depasse pas
`clientWidth`. Quand il depasse, la sonde NOMME les elements fautifs (ceux
dont le bord droit sort du cadre) -- constater, pas corriger.

Largeurs : 320 (le seuil de la spec), 375 et 768 (mandat 4.6).
Captures : accueil + une page de chaque volet, versees en docs/.

Cette sonde ne modifie aucun fichier du site ; elle ecrit des PNG dans
docs/recette-v2-captures/ et son resultat brut dans resultats/.
"""

import os
import sys

import harnais

LARGEURS = [320, 375, 768]
TOLERANCE = 1          # px : sous-pixel de composition, pas un debordement

# Mandat 4.6 : accueil + une page de chaque volet.
PAGES_CAPTUREES = [
    "index.html",
    "films/pandora.html",              # volet Critiques
    "films/pandora-contrechamp.html",  # volet Etudes
]

JS_DEBORDEMENT = r"""
(tolerance) => {
  const d = document.scrollingElement || document.documentElement;
  const cadre = d.clientWidth;
  const fautifs = [];
  for (const el of document.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    const st = getComputedStyle(el);
    if (st.position === 'fixed') continue;
    if (r.right > cadre + tolerance) {
      fautifs.push({
        chemin: window.__chemin(el),
        droite: Math.round(r.right),
        largeur: Math.round(r.width),
        debord: Math.round(r.right - cadre),
      });
    }
  }
  fautifs.sort((a, b) => b.debord - a.debord);
  return {
    clientWidth: cadre,
    scrollWidth: d.scrollWidth,
    debordement: d.scrollWidth - cadre,
    fautifs: fautifs.slice(0, 8),
    nb_fautifs: fautifs.length,
  };
}
"""


def dossier_captures():
    chemin = os.path.join(harnais.DOSSIER_DOCS, "recette-v2-captures")
    assert os.path.isdir(harnais.DOSSIER_DOCS), "docs/ introuvable"
    if not os.path.isdir(chemin):
        os.makedirs(chemin)
    return chemin


def main():
    sync_playwright = harnais.playwright_ou_arret()
    cibles = harnais.pages_toutes()
    resultats = {}
    captures = []
    dossier = dossier_captures()

    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        for largeur in LARGEURS:
            ctx = nav.new_context(viewport={"width": largeur, "height": 800},
                                  device_scale_factor=1)
            page = ctx.new_page()
            for cible in cibles:
                page.goto(harnais.url(cible), wait_until="load", timeout=30000)
                page.evaluate(harnais.JS_FOND_EFFECTIF)
                page.wait_for_timeout(150)
                mesure = page.evaluate(JS_DEBORDEMENT, TOLERANCE)
                resultats.setdefault(cible, {})[str(largeur)] = mesure

                if cible in PAGES_CAPTUREES:
                    # Poids des captures : une analyse illustree fait ~2 Mo en
                    # PNG pleine page, pour un depot de 7,8 Mo. D'ou deux
                    # choix, declares plutot que subis :
                    #   - JPEG q=50 (la preuve visuelle n'a pas besoin du
                    #     sans-perte, le depot si) ;
                    #   - PLEINE PAGE a 320 px seulement -- c'est la largeur
                    #     ou vit le critere de P-38 ; a 375 et 768 px, le
                    #     premier ecran suffit, le defilement horizontal etant
                    #     de toute facon mesure sur TOUTE la page, pour les
                    #     39 pages, par la sonde elle-meme.
                    pleine = (largeur == 320)
                    nom = "%s-%dpx%s.jpg" % (
                        cible.replace("/", "_").replace(".html", ""), largeur,
                        "-pleine-page" if pleine else "-premier-ecran")
                    page.screenshot(path=os.path.join(dossier, nom),
                                    full_page=pleine, type="jpeg", quality=50)
                    captures.append(nom)
            ctx.close()
        nav.close()

    harnais.ecrire_json("geometrie.json", resultats)

    print("P-38 -- defilement horizontal (tolerance %d px)" % TOLERANCE)
    print("")
    proto = harnais.PAGES_PROTOTYPE
    for largeur in LARGEURS:
        en_ecart = [c for c in cibles
                    if resultats[c][str(largeur)]["debordement"] > TOLERANCE]
        proto_ecart = [c for c in en_ecart if c in proto]
        print("  %4d px : %d page(s) en debordement sur %d  |  prototype : %d / 9"
              % (largeur, len(en_ecart), len(cibles), len(proto_ecart)))
        for c in en_ecart[:12]:
            m = resultats[c][str(largeur)]
            marque = "PROTOTYPE" if c in proto else "non migree"
            print("      %-40s +%d px (%s)" % (c, m["debordement"], marque))
            for f in m["fautifs"][:2]:
                print("          %s  (+%d px)" % (f["chemin"], f["debord"]))
    print("")
    print("clientWidth mesure a 320 px sur index.html : %d"
          % resultats["index.html"]["320"]["clientWidth"])
    print("captures versees : %d dans %s" % (len(captures), dossier))
    return 0


if __name__ == "__main__":
    sys.exit(main())
