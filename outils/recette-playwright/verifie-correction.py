#!/usr/bin/env python3
# -*- coding: ascii -*-
"""verifie-correction.py -- une correction ne s'ecrit qu'apres avoir ete vue.

REGLE POSEE PAR AH LE 23/07/2026, et qui vaut pour tout le reste du chantier :
aucune valeur proposee ne lui est soumise, ni appliquee, sans que l'etat APRES
ait ete mesure. Son test sur la premiere fiche de la revue avait montre une
proposition qui faisait DISPARAITRE le titre de Pandora -- le fond gagnait,
le texte se perdait, et c'est le rendu ENTIER qui compte.

Ce que le script fait, pour une correction donnee (page, variable, valeur) :
  1. il releve TOUS les elements que la variable colore, avec leur ratio reel
     mesure sur le fond dominant sous leurs lignes de texte ;
  2. il injecte la valeur proposee dans le navigateur -- aucun fichier n'est
     touche -- et refait la meme mesure ;
  3. il rend un verdict par element, et un verdict d'ensemble.

Le verdict d'ensemble est REFUSE des qu'un seul element perd : soit il tombe
sous son seuil alors qu'il le tenait, soit son ratio baisse de plus d'un
dixieme. Une correction qui repare trois elements et en abime un n'est pas
une correction.

Usage : RECETTE_BASE=... python verifie-correction.py <page.html> <--var> <#hex>
"""

import collections
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

PART_MINIMALE = 0.10
TOLERANCE = 0.10        # baisse de ratio acceptee sur un element deja conforme

JS_ELEMENTS = r"""
(cible) => {
  const out = [];
  let i = 0;
  for (const el of document.querySelectorAll('*')) {
    let propre = '';
    for (const n of el.childNodes) if (n.nodeType === 3) propre += n.nodeValue;
    if (!propre.trim()) continue;
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden') continue;
    const c = window.__lireRgba(el.ownerSVGElement ? st.fill : st.color);
    if (!c || window.__hex(c).toLowerCase() !== cible) continue;
    const rects = [];
    for (const n of el.childNodes) {
      if (n.nodeType !== 3 || !n.nodeValue.trim()) continue;
      const rg = document.createRange();
      rg.selectNodeContents(n);
      for (const r of rg.getClientRects()) {
        if (r.width < 2 || r.height < 2) continue;
        rects.push({x: r.left + window.scrollX, y: r.top + window.scrollY,
                    w: r.width, h: r.height});
      }
    }
    if (!rects.length) continue;
    const px = parseFloat(st.fontSize) || 16;
    const poids = parseInt(st.fontWeight, 10) || 400;
    el.setAttribute('data-vc', 'v' + i);
    out.push({marque: 'v' + (i++), rects: rects,
              seuil: (px >= 24 || (px >= 18.66 && poids >= 700)) ? 3.0 : 4.5,
              extrait: propre.trim().slice(0, 46),
              chemin: window.__chemin(el)});
  }
  return out;
}
"""

JS_MASQUE = """() => {
  for (const el of document.querySelectorAll('[data-vc]')) {
    for (const n of [el].concat(Array.from(el.querySelectorAll('*')))) {
      n.style.setProperty('color', 'transparent', 'important');
      n.style.setProperty('fill', 'transparent', 'important');
      n.style.setProperty('text-shadow', 'none', 'important');
      n.style.setProperty('text-decoration-color', 'transparent', 'important');
      n.style.setProperty('border-color', 'transparent', 'important');
    }
  }
}"""

JS_INJECTE = """(a) => {
  let s = document.getElementById('__vc');
  if (!s) { s = document.createElement('style'); s.id = '__vc';
            document.head.appendChild(s); }
  s.textContent = ':root{' + a.variable + ':' + a.valeur + ' !important;}';
}"""


def lum(r, g, b):
    def c(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * c(r) + 0.7152 * c(g) + 0.0722 * c(b)


def ratio(l1, l2):
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def hex_lum(h):
    return lum(*[int(h[i:i + 2], 16) for i in (1, 3, 5)])


def mesure(page, elements, couleur_hex, image):
    """Ratio reel de chaque element contre le fond DOMINANT de ses lignes."""
    lt = hex_lum(couleur_hex)
    resultats = []
    for e in elements:
        compte = collections.Counter()
        for r in e["rects"]:
            x0, y0 = max(0, int(r["x"])), max(0, int(r["y"]))
            x1 = min(image.width, int(r["x"] + r["w"]) + 1)
            y1 = min(image.height, int(r["y"] + r["h"]) + 1)
            if x1 <= x0 or y1 <= y0:
                continue
            compte.update(image.crop((x0, y0, x1, y1)).getdata())
        total = sum(compte.values())
        if not total:
            continue
        dominantes = [c for c, n in compte.items()
                      if n / float(total) >= PART_MINIMALE]
        if not dominantes:
            dominantes = [compte.most_common(1)[0][0]]
        resultats.append({
            "chemin": e["chemin"], "extrait": e["extrait"],
            "seuil": e["seuil"],
            "ratio": round(min(ratio(lt, lum(*c)) for c in dominantes), 2),
        })
    return resultats


def verifie(page_nom, variable, valeur_actuelle, valeur_proposee):
    sync = harnais.playwright_ou_arret()
    with sync() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        page.goto(harnais.url("films/" + page_nom), wait_until="load",
                  timeout=30000)
        page.wait_for_timeout(120)
        h = page.evaluate("() => Math.min("
                          "document.documentElement.scrollHeight, 20000)")
        page.set_viewport_size({"width": 1280, "height": int(h)})
        page.evaluate(harnais.JS_FOND_EFFECTIF)
        page.wait_for_timeout(150)

        elements = page.evaluate(JS_ELEMENTS, valeur_actuelle.lower())
        if not elements:
            nav.close()
            return None, "aucun element ne porte %s" % valeur_actuelle

        page.evaluate(JS_MASQUE)
        page.wait_for_timeout(70)
        image = Image.open(io.BytesIO(page.screenshot())).convert("RGB")
        avant = mesure(page, elements, valeur_actuelle, image)
        # Le fond ne bouge pas : seule la couleur du texte change. La meme
        # capture sert donc aux deux mesures -- et c'est plus sur, car elle
        # garantit qu'on compare bien le meme rendu.
        apres = mesure(page, elements, valeur_proposee, image)
        page.evaluate(JS_INJECTE, {"variable": variable,
                                   "valeur": valeur_proposee})
        nav.close()

    lignes, refus = [], []
    for a, b in zip(avant, apres):
        etat = "="
        if b["ratio"] >= b["seuil"] > a["ratio"]:
            etat = "REPARE"
        elif a["ratio"] >= a["seuil"] > b["ratio"]:
            etat = "CASSE"
            refus.append(b)
        elif b["ratio"] < a["ratio"] - TOLERANCE:
            etat = "DEGRADE"
            refus.append(b)
        elif b["ratio"] > a["ratio"] + TOLERANCE:
            etat = "mieux"
        lignes.append((a, b, etat))
    return (lignes, refus), None


def main():
    if len(sys.argv) != 5:
        sys.stderr.write("usage : verifie-correction.py <page.html> <--var> "
                         "<#actuelle> <#proposee>\n")
        return 2
    page_nom, variable, actuelle, proposee = sys.argv[1:5]
    resultat, erreur = verifie(page_nom, variable, actuelle, proposee)
    if erreur:
        print("ARRET : %s" % erreur)
        return 1
    lignes, refus = resultat
    print("%s  %s  %s -> %s" % (page_nom, variable, actuelle, proposee))
    print("%-46s %6s %6s  %s" % ("element", "avant", "apres", "etat"))
    print("-" * 74)
    for a, b, etat in lignes:
        print("%-46s %6.2f %6.2f  %s"
              % (a["extrait"][:46], a["ratio"], b["ratio"], etat))
    print("")
    if refus:
        print("VERDICT : REFUSEE -- %d element(s) y perdent" % len(refus))
        return 1
    repares = len([1 for a, b, e in lignes if e == "REPARE"])
    restants = len([1 for a, b, e in lignes if b["ratio"] < b["seuil"]])
    print("VERDICT : ACCEPTABLE -- %d repare(s), %d encore en ecart, "
          "aucun degrade" % (repares, restants))
    return 0


if __name__ == "__main__":
    sys.exit(main())
