#!/usr/bin/env python3
# -*- coding: ascii -*-
"""requalifie-degrades.py -- le fond DOMINANT sous chaque ligne de texte.

CE QUI A RENDU CE SCRIPT NECESSAIRE. Le test visuel d'AH du 23/07 sur la
premiere fiche de la revue : la valeur proposee pour `--platre-dim` faisait
DISPARAITRE le titre de Pandora. Verification : les 5 elements concernes sont
peints sur le HAUT de la couverture (bleu nuit, ratio 8 a 11) ; le "pire cas"
de 1,55 venait du sable, arret de degrade situe a 74 % de la hauteur, que ces
textes ne touchent jamais. Il n'y avait aucun defaut a corriger.

Vingt-trois des vingt-sept lots restants reposent sur ce meme pire cas
theorique. Ce script les re-qualifie sur le fond REEL.

POURQUOI LE FOND DOMINANT, ET NON LE PIRE PIXEL. Une premiere sonde retenait
le pixel le plus defavorable du rectangle de ligne. Elle s'est revelee bruitee
-- cas temoin : une pastille dont le texte vaut 10,03 y etait comptee 1,09,
quelques pixels etrangers suffisant a fausser le verdict. On retient donc les
couleurs qui COUVRENT REELLEMENT le fond de la ligne (au moins 10 % de ses
pixels) et l'on prend la pire d'entre elles. Une nuance qui occupe moins d'un
dixieme du cadre n'est pas le fond sur lequel le texte se lit.

Verdicts rendus :
  CONFORME   le texte tient le seuil sur son fond reel -- rien a corriger,
             le lot sort de la revue ;
  ECART      le defaut existe la ou le texte se trouve ;
  A VOIR     le fond varie trop sous la ligne pour trancher mecaniquement.

Aucune ecriture dans le site. Produit `resultats/requalification.json`.

Usage : RECETTE_BASE=http://127.0.0.1:8791 python requalifie-degrades.py
"""

import collections
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harnais  # noqa: E402

try:
    from PIL import Image
except ImportError:
    sys.stderr.write("ARRET : Pillow absent (aucune installation, mandat).\n")
    raise SystemExit(3)

PART_MINIMALE = 0.10     # une couleur sous ce seuil n'est pas "le fond"

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
    el.setAttribute('data-rq', 'r' + i);
    out.push({marque: 'r' + (i++), rects: rects,
              seuil: (px >= 24 || (px >= 18.66 && poids >= 700)) ? 3.0 : 4.5,
              extrait: propre.trim().slice(0, 44),
              chemin: window.__chemin(el)});
  }
  return out;
}
"""

JS_MASQUE = """() => {
  for (const el of document.querySelectorAll('[data-rq]')) {
    for (const n of [el].concat(Array.from(el.querySelectorAll('*')))) {
      n.style.setProperty('color', 'transparent', 'important');
      n.style.setProperty('fill', 'transparent', 'important');
      n.style.setProperty('text-shadow', 'none', 'important');
      n.style.setProperty('text-decoration-color', 'transparent', 'important');
      n.style.setProperty('border-color', 'transparent', 'important');
    }
  }
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


def main():
    chemin = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "resultats", "usage-variables.json")
    with io.open(chemin, "r", encoding="utf-8") as f:
        lots = [x for x in json.load(f)
                if x["lourd"] and any("degrade" in n for n in x["natures"])]

    par_page = {}
    for x in lots:
        par_page.setdefault(x["page"], []).append(x)

    verdicts = []
    sync = harnais.playwright_ou_arret()
    with sync() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        for nom_page in sorted(par_page):
            page.set_viewport_size({"width": 1280, "height": 900})
            page.goto(harnais.url("films/" + nom_page), wait_until="load",
                      timeout=30000)
            page.wait_for_timeout(120)
            h = page.evaluate("() => Math.min("
                              "document.documentElement.scrollHeight, 20000)")
            page.set_viewport_size({"width": 1280, "height": int(h)})
            page.evaluate(harnais.JS_FOND_EFFECTIF)
            page.wait_for_timeout(150)

            for lot in par_page[nom_page]:
                elements = page.evaluate(JS_ELEMENTS, lot["valeur"].lower())
                if not elements:
                    verdicts.append({"page": nom_page,
                                     "variable": lot["variable"],
                                     "verdict": "INTROUVABLE",
                                     "detail": "la couleur n'est plus rendue"})
                    continue
                page.evaluate(JS_MASQUE)
                page.wait_for_timeout(70)
                image = Image.open(io.BytesIO(
                    page.screenshot())).convert("RGB")
                page.reload(wait_until="load")
                page.evaluate(harnais.JS_FOND_EFFECTIF)
                page.wait_for_timeout(130)

                lt = lum(*[int(lot["valeur"][i:i + 2], 16) for i in (1, 3, 5)])
                pire_global, detail = 99.0, []
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
                    # Seules les couleurs qui COUVRENT la ligne comptent.
                    dominantes = [(c, n) for c, n in compte.items()
                                  if n / float(total) >= PART_MINIMALE]
                    if not dominantes:
                        dominantes = [compte.most_common(1)[0]]
                    pire = min(ratio(lt, lum(*c)) for c, _ in dominantes)
                    pire_global = min(pire_global, pire)
                    detail.append({
                        "chemin": e["chemin"][-46:], "extrait": e["extrait"],
                        "ratio_reel": round(pire, 2), "seuil": e["seuil"],
                        "fonds_dominants": ["#%02x%02x%02x" % c
                                            for c, _ in sorted(
                                                dominantes,
                                                key=lambda kv: -kv[1])[:3]],
                    })
                seuil = min(d["seuil"] for d in detail) if detail else 4.5
                if pire_global >= seuil:
                    verdict = "CONFORME"
                elif pire_global < seuil * 0.9:
                    verdict = "ECART"
                else:
                    verdict = "A VOIR"
                verdicts.append({
                    "page": nom_page, "variable": lot["variable"],
                    "valeur": lot["valeur"], "propose": lot["propose"],
                    "elements": lot["elements"],
                    "ratio_annonce": lot["pire_ratio"],
                    "ratio_reel": round(pire_global, 2),
                    "seuil": seuil, "verdict": verdict, "detail": detail,
                })
                print("  %-26s %-20s annonce %.2f -> reel %.2f  %s"
                      % (nom_page[:-5], lot["variable"], lot["pire_ratio"],
                         pire_global, verdict))
        ctx.close()
        nav.close()

    harnais.ecrire_json("requalification.json", verdicts)
    c = collections.Counter(v["verdict"] for v in verdicts)
    print("")
    for k in ("CONFORME", "ECART", "A VOIR", "INTROUVABLE"):
        if c[k]:
            print("%-12s : %2d lot(s)" % (k, c[k]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
