#!/usr/bin/env python3
# -*- coding: ascii -*-
"""sonde-fond-peint.py -- le fond REELLEMENT peint derriere chaque texte.

Pourquoi cette sonde existe. Sur un fond en degrade, `sonde-contraste.py`
retient comme pire cas le plus defavorable des ARRETS DE COULEUR declares.
C'est prudent, et c'est trop prudent : un degrade qui va du bleu nuit au sable
sur toute la hauteur d'une couverture voit son arret "sable" retenu contre un
texte qui, lui, ne descend jamais si bas. On corrigerait alors un defaut que
personne ne peut voir -- et on abimerait une identite pour rien.

La mesure juste ne se lit pas dans le CSS, elle se lit A L'ECRAN. Le procede :
  1. les glyphes des textes candidats passent en `color:transparent` -- ils
     disparaissent SANS emporter le fond propre de leur element ;
  2. une capture est prise ; elle montre donc les fonds nus ;
  3. pour chaque element, on lit les pixels de son cadre exact et on en tire
     la luminance la PLUS DEFAVORABLE au texte qu'il portait ;
  4. le ratio se calcule contre ce fond-la, celui que l'oeil rencontre.

La sonde ne corrige rien. Elle dit lesquels des ecarts de degrade sont reels.

Usage : RECETTE_BASE=http://127.0.0.1:8791 python sonde-fond-peint.py
"""

import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harnais  # noqa: E402

try:
    from PIL import Image
except ImportError:
    sys.stderr.write("ARRET : Pillow absent (aucune installation, mandat).\n")
    raise SystemExit(3)

SEUIL_COURANT, SEUIL_GRAND = 4.5, 3.0

JS_CANDIDATS = r"""
(seuils) => {
  const TOUT = true;   // audit complet : on mesure meme les conformes
  const out = [];
  let i = 0;
  for (const el of document.querySelectorAll('*')) {
    let propre = '';
    for (const n of el.childNodes) if (n.nodeType === 3) propre += n.nodeValue;
    if (!propre.trim()) continue;
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    if (r.bottom < 0 || r.right < 0) continue;

    let opacite = 1;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const o = parseFloat(getComputedStyle(n).opacity);
      if (!isNaN(o)) opacite *= o;
    }
    if (opacite === 0) continue;

    const fond = window.__fondEffectif(el);
    // DANS UN SVG, LA COULEUR DU TEXTE EST `fill`, PAS `color`. Lire `color`
    // y renvoie une valeur heritee du document qui n'est JAMAIS peinte : les
    // cartels de `rouges-et-blancs`, remplis en #c9c4b4 clair sur un champ
    // sombre (ratio reel 10,09), etaient ainsi comptes a 1,11 et declares
    // illisibles. Un faux positif qui aurait fait "corriger" un texte sain.
    const estSVG = el.ownerSVGElement || el.tagName === 'svg';
    const brut = window.__lireRgba(estSVG ? st.fill : st.color);
    if (!brut || brut.a === 0) continue;
    const alpha = brut.a * opacite;
    const texte = alpha >= 0.999 ? brut
                : window.__composer({r: brut.r, g: brut.g, b: brut.b, a: alpha}, fond);

    const cand = window.__fondsCandidats(el);
    let pire = Infinity;
    for (const f of cand.fonds) {
      const r2 = window.__ratio(texte, f);
      if (r2 < pire) pire = r2;
    }
    const px = parseFloat(st.fontSize) || 16;
    const poids = parseInt(st.fontWeight, 10) || 400;
    const seuil = (px >= 24 || (px >= 18.66 && poids >= 700))
                ? seuils.grand : seuils.courant;
    if (!TOUT && pire >= seuil) continue;     // deja conforme au pire theorique

    el.setAttribute('data-sonde', 'p' + (i++));
    out.push({
      marque: 'p' + (i - 1),
      texte: window.__hex(texte),
      ratio_theorique: Math.round(pire * 100) / 100,
      seuil: seuil,
      rect: {x: r.left + window.scrollX, y: r.top + window.scrollY,
             w: r.width, h: r.height},
      extrait: propre.trim().slice(0, 40),
      chemin: window.__chemin(el),
    });
  }
  return out;
}
"""

# ATTENTION : `visibility:hidden` serait un PIEGE ici -- il masque l'element
# ENTIER, son propre fond compris. On mesurerait alors ce qui se trouve
# DERRIERE le bloc et non le fond sur lequel le texte repose : un cartel a
# fond saumon pose sur une couverture sombre serait mesure contre la
# couverture, et declare illisible alors qu'il ne l'est pas.
# `color:transparent` ne retire que les GLYPHES : le fond de l'element reste
# peint, et la mise en page ne bouge pas d'un pixel.
# Et la DESCENDANCE avec : un `<em>` ou un `<strong>` a l'interieur garde sa
# propre couleur, ses glyphes resteraient peints dans le cadre mesure et
# seraient pris pour du fond. Le masquage couvre donc tout le sous-arbre.
JS_MASQUE = """() => {
  for (const el of document.querySelectorAll('[data-sonde]')) {
    for (const n of [el, ...el.querySelectorAll('*')]) {
      n.style.setProperty('color', 'transparent', 'important');
      n.style.setProperty('text-shadow', 'none', 'important');
      n.style.setProperty('-webkit-text-stroke-color', 'transparent',
                          'important');
    }
  }
}"""


def luminance_rgb(r, g, b):
    def c(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * c(r) + 0.7152 * c(g) + 0.0722 * c(b)


def ratio_l(l1, l2):
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def main():
    sync = harnais.playwright_ou_arret()
    fiches = []
    with sync() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        for chemin in harnais.pages_films():
            nom = chemin.split("/")[-1]
            page.goto(harnais.url(chemin), wait_until="load", timeout=30000)
            page.evaluate(harnais.JS_FOND_EFFECTIF)
            page.wait_for_timeout(130)
            candidats = page.evaluate(JS_CANDIDATS,
                                      {"courant": SEUIL_COURANT,
                                       "grand": SEUIL_GRAND})
            if not candidats:
                continue
            page.evaluate(JS_MASQUE)
            page.wait_for_timeout(60)
            brut = page.screenshot(full_page=True)
            image = Image.open(io.BytesIO(brut)).convert("RGB")
            for c in candidats:
                r = c["rect"]
                x0, y0 = max(0, int(r["x"])), max(0, int(r["y"]))
                x1 = min(image.width, int(r["x"] + r["w"]))
                y1 = min(image.height, int(r["y"] + r["h"]))
                if x1 <= x0 or y1 <= y0:
                    continue
                zone = image.crop((x0, y0, x1, y1))
                # Sous-echantillonnage : la luminance d'un fond varie
                # lentement, inutile de lire chaque pixel.
                zone.thumbnail((60, 60))
                lums = [luminance_rgb(*p) for p in zone.getdata()]
                l_texte = luminance_rgb(
                    *[int(c["texte"][i:i + 2], 16) for i in (1, 3, 5)])
                pire = min(ratio_l(l_texte, lf) for lf in lums)
                fiches.append({
                    "page": nom, "chemin": c["chemin"],
                    "texte": c["texte"], "seuil": c["seuil"],
                    "ratio_theorique": c["ratio_theorique"],
                    "ratio_peint": round(pire, 2),
                    "conforme_au_reel": pire >= c["seuil"],
                    "extrait": c["extrait"],
                })
        ctx.close()
        nav.close()

    harnais.ecrire_json("fond-peint.json", fiches)
    reels = [f for f in fiches if not f["conforme_au_reel"]]
    faux = [f for f in fiches if f["conforme_au_reel"]]
    print("elements en degrade declares en echec : %d" % len(fiches))
    print("  ECARTS REELS (mesure sur pixels peints) : %d" % len(reels))
    print("  conformes en realite (pire cas theorique jamais rencontre) : %d"
          % len(faux))
    print("")
    print("--- ecarts reels ---")
    for f in sorted(reels, key=lambda x: x["ratio_peint"]):
        print("  %-28s %s  theorique %.2f -> peint %.2f (seuil %.1f)  %s"
              % (f["page"][:-5], f["texte"], f["ratio_theorique"],
                 f["ratio_peint"], f["seuil"], f["extrait"][:26]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
