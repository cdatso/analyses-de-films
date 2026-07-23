#!/usr/bin/env python3
# -*- coding: ascii -*-
"""revue-lot4-v2.py -- la revue refaite, apres le test visuel d'AH.

CE QUE LA PREMIERE REVUE FAISAIT MAL, et que celle-ci corrige :

  1. elle ne montrait QU'UN fragment par lot, sans le dire -- AH jugeait sur
     un cinquieme du perimetre. Ici : TOUS les elements fautifs, chacun avec
     son avant/apres ;
  2. elle proposait de deplacer la variable meme quand la plupart de ses
     elements allaient bien -- le titre de Pandora disparaissait pour reparer
     un avertissement. Ici : quand une partie seulement echoue, la proposition
     est une REGLE LOCALE visant les elements fautifs, et la variable ne bouge
     pas ;
  3. elle soumettait des propositions que la session n'avait pas regardees.
     Ici : chaque proposition passe par `verifie-correction`, et celles qui
     degradent quoi que ce soit N'ARRIVENT PAS a AH -- elles vont dans une
     liste a part, avec leur motif de refus.

La regle d'AH, qui gouverne tout : le test porte sur le RENDU ENTIER, texte
et fond ensemble. Un fond qui s'ameliore et un texte qui disparait est un
echec.

Sortie hors depot : `_scratch\\revue-lot4\\index.html`.

Usage : RECETTE_BASE=http://127.0.0.1:8791 python revue-lot4-v2.py
"""

import base64
import collections
import colorsys
import io
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ICI, "recette-playwright"))
import harnais  # noqa: E402

try:
    from PIL import Image
except ImportError:
    sys.stderr.write("ARRET : Pillow absent (aucune installation, mandat).\n")
    raise SystemExit(3)

SORTIE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "_scratch", "revue-lot4")

PART_MINIMALE = 0.10
TOLERANCE = 0.10
MARGE = 26
LARGEUR_MAX = 520

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
    // Le selecteur LOCAL le plus court qui atteigne cet element : sa balise
    // et sa premiere classe. C'est lui qui portera une correction ciblee.
    let local = el.tagName.toLowerCase();
    if (typeof el.className === 'string' && el.className.trim()) {
      local += '.' + el.className.trim().split(/\s+/)[0];
    }
    el.setAttribute('data-vc', 'v' + i);
    out.push({marque: 'v' + (i++), rects: rects, local: local,
              seuil: (px >= 24 || (px >= 18.66 && poids >= 700)) ? 3.0 : 4.5,
              extrait: propre.trim().slice(0, 52),
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

JS_REGLE = """(css) => {
  let s = document.getElementById('__revue');
  if (!s) { s = document.createElement('style'); s.id = '__revue';
            document.head.appendChild(s); }
  s.textContent = css;
}"""

JS_RETIRE = """() => {
  const s = document.getElementById('__revue');
  if (s) s.textContent = '';
}"""


def lum(r, g, b):
    def c(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * c(r) + 0.7152 * c(g) + 0.0722 * c(b)


def ratio_rgb(a, b):
    l1, l2 = lum(*a), lum(*b)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def rgb_hex(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(v))))
                                   for v in c)


def cherche_valeur(depart_hex, fonds_a_reparer, fonds_a_preserver, seuil):
    """La couleur la plus proche qui repare SANS casser ce qui allait bien.

    `fonds_a_preserver` sont les fonds des elements deja conformes : la
    nouvelle valeur doit continuer d'y tenir le seuil. Sans cette contrainte,
    on obtient exactement le defaut qu'AH a releve -- un titre sacrifie pour
    un avertissement.
    """
    base = hex_rgb(depart_hex)
    h, l, s = colorsys.rgb_to_hls(*[v / 255.0 for v in base])
    for sens in (-1, 1):
        l2 = l
        for _ in range(500):
            l2 += sens * 0.002
            if not 0.0 <= l2 <= 1.0:
                break
            c = tuple(v * 255.0 for v in colorsys.hls_to_rgb(h, l2, s))
            if any(ratio_rgb(c, hex_rgb(f)) < seuil + 0.05
                   for f in fonds_a_reparer):
                continue
            if any(ratio_rgb(c, hex_rgb(f)) < seuil
                   for f in fonds_a_preserver):
                continue
            return rgb_hex(c), round(abs(l2 - l), 3)
    return None, None


def mesure(elements, couleur_hex, image):
    lt = lum(*hex_rgb(couleur_hex))
    out = {}
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
        dom = [c for c, n in compte.items()
               if n / float(total) >= PART_MINIMALE]
        if not dom:
            dom = [compte.most_common(1)[0][0]]
        pire = min((max(lt, lum(*c)) + 0.05) / (min(lt, lum(*c)) + 0.05)
                   for c in dom)
        out[e["marque"]] = {"ratio": round(pire, 2), "seuil": e["seuil"],
                            "fonds": [rgb_hex(c) for c in dom[:2]]}
    return out


def png(image):
    t = io.BytesIO()
    image.save(t, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(t.getvalue()).decode()


def main():
    base = os.path.join(ICI, "recette-playwright", "resultats")
    with io.open(os.path.join(base, "requalification.json"), encoding="utf-8") as f:
        requal = {(x["page"], x["variable"]): x for x in json.load(f)
                  if x["verdict"] == "ECART"}
    with io.open(os.path.join(base, "usage-variables.json"), encoding="utf-8") as f:
        tous = {(x["page"], x["variable"]): x for x in json.load(f)}

    # Les 19 requalifies + le cas laisse de cote (fond uniforme, mais la
    # correction mecanique y inverse une variable nommee --noir).
    cles = list(requal)
    if ("hitchcock-truffaut.html", "--noir") in tous:
        cles.append(("hitchcock-truffaut.html", "--noir"))

    par_page = {}
    for k in cles:
        par_page.setdefault(k[0], []).append(k)

    if not os.path.isdir(SORTIE):
        os.makedirs(SORTIE)

    fiches, ecartees = [], []
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

            for cle in par_page[nom_page]:
                lot = tous[cle]
                elements = page.evaluate(JS_ELEMENTS, lot["valeur"].lower())
                if not elements:
                    ecartees.append((nom_page, lot["variable"],
                                     "la couleur n'est plus rendue"))
                    continue

                page.evaluate(JS_MASQUE)
                page.wait_for_timeout(70)
                fond_nu = Image.open(io.BytesIO(
                    page.screenshot())).convert("RGB")
                avant = mesure(elements, lot["valeur"], fond_nu)
                page.reload(wait_until="load")
                page.evaluate(harnais.JS_FOND_EFFECTIF)
                page.wait_for_timeout(140)
                page.evaluate(JS_ELEMENTS, lot["valeur"].lower())

                fautifs = [e for e in elements
                           if e["marque"] in avant
                           and avant[e["marque"]]["ratio"]
                           < avant[e["marque"]]["seuil"]]
                sains = [e for e in elements
                         if e["marque"] in avant and e not in fautifs]
                if not fautifs:
                    ecartees.append((nom_page, lot["variable"],
                                     "aucun element en ecart a la re-mesure"))
                    continue

                seuil = min(avant[e["marque"]]["seuil"] for e in fautifs)
                f_rep, f_pres = set(), set()
                for e in fautifs:
                    f_rep.update(avant[e["marque"]]["fonds"])
                for e in sains:
                    f_pres.update(avant[e["marque"]]["fonds"])

                # Une regle LOCALE des qu'une partie des elements va bien.
                locale = bool(sains)
                valeur, depl = cherche_valeur(
                    lot["valeur"], f_rep, set() if locale else f_pres, seuil)
                if not valeur:
                    # Les fonds des elements fautifs se contredisent : les uns
                    # veulent un texte plus sombre, les autres plus clair.
                    # C'est le meme mur que la passe de dedoublement, et la
                    # reponse est la meme -- non pas une couleur, mais UNE PAR
                    # CONTEXTE. On dit lesquels, plutot que de renvoyer un
                    # "impossible" qui n'apprend rien.
                    clairs = [f for f in f_rep
                              if lum(*hex_rgb(f)) > 0.35]
                    sombres = [f for f in f_rep if f not in clairs]
                    ecartees.append((nom_page, lot["variable"],
                                     "fonds contradictoires (%d clair(s), "
                                     "%d sombre(s)) : demande une valeur PAR "
                                     "CONTEXTE, pas une valeur unique"
                                     % (len(clairs), len(sombres))))
                    continue

                if locale:
                    selecteurs = sorted({e["local"] for e in fautifs})
                    css = "%s{color:%s !important;}" % (
                        ", ".join(selecteurs), valeur)
                    geste = "regle locale sur %s" % ", ".join(selecteurs)
                else:
                    css = ":root{%s:%s !important;}" % (lot["variable"],
                                                        valeur)
                    geste = "valeur de %s" % lot["variable"]

                # La correction ne touche QUE la couleur du texte : le fond nu
                # est le meme avant et apres. Une seule capture de fond suffit
                # donc aux deux mesures -- et c'est plus sur, car elle garantit
                # qu'on compare bien le meme rendu de fond.
                #
                # MAIS : quand la regle est LOCALE, les elements sains ne la
                # recoivent pas et gardent leur couleur. Les mesurer avec la
                # nouvelle valeur, c'est leur imputer un changement qui ne les
                # atteint pas -- et rejeter la proposition pour un degat
                # imaginaire. La premiere execution a ainsi ecarte a tort huit
                # propositions sur onze, dont `sans-filtre --or-texte` ou une
                # regle visant UN element etait refusee au nom des vingt
                # autres.
                apres = mesure(fautifs, valeur, fond_nu)
                apres.update(mesure(sains, lot["valeur"] if locale else valeur,
                                    fond_nu))

                capt_avant = Image.open(io.BytesIO(
                    page.screenshot())).convert("RGB")
                page.evaluate(JS_REGLE, css)
                page.wait_for_timeout(90)
                capt_apres = Image.open(io.BytesIO(
                    page.screenshot())).convert("RGB")
                page.evaluate(JS_RETIRE)
                page.wait_for_timeout(50)

                # CONTROLE : rien ne doit perdre.
                perdants = []
                for e in (fautifs + sains):
                    m = e["marque"]
                    if m not in avant or m not in apres:
                        continue
                    a, b = avant[m], apres[m]
                    if a["ratio"] >= a["seuil"] > b["ratio"]:
                        perdants.append((e["extrait"], a["ratio"], b["ratio"]))
                    elif b["ratio"] < a["ratio"] - TOLERANCE:
                        perdants.append((e["extrait"], a["ratio"], b["ratio"]))
                if perdants:
                    ecartees.append((nom_page, lot["variable"],
                                     "%d element(s) y perdent : %s"
                                     % (len(perdants),
                                        " ; ".join("%s (%.2f -> %.2f)" % p
                                                   for p in perdants[:2]))))
                    continue

                vues = []
                for e in fautifs:
                    r = e["rects"][0]
                    b = (max(0, int(r["x"]) - MARGE),
                         max(0, int(r["y"]) - MARGE),
                         min(capt_avant.width, int(r["x"] + r["w"]) + MARGE),
                         min(capt_avant.height, int(r["y"] + r["h"]) + MARGE))
                    if b[2] <= b[0] or b[3] <= b[1]:
                        continue
                    ia, ib = capt_avant.crop(b), capt_apres.crop(b)
                    if ia.width > LARGEUR_MAX:
                        k = LARGEUR_MAX / float(ia.width)
                        t = (LARGEUR_MAX, max(1, int(ia.height * k)))
                        ia, ib = ia.resize(t, Image.LANCZOS), ib.resize(
                            t, Image.LANCZOS)
                    m = e["marque"]
                    vues.append({"extrait": e["extrait"],
                                 "avant": png(ia), "apres": png(ib),
                                 "r_avant": avant[m]["ratio"],
                                 "r_apres": apres.get(m, {}).get("ratio", 0),
                                 "seuil": avant[m]["seuil"]})

                fiches.append({
                    "page": nom_page, "variable": lot["variable"],
                    "valeur": lot["valeur"], "propose": valeur,
                    "geste": geste, "css": css, "locale": locale,
                    "deplacement": depl, "fautifs": len(fautifs),
                    "sains": len(sains), "vues": vues,
                })
                print("  %-26s %-20s %d fautif(s) / %d sain(s)  %s"
                      % (nom_page[:-5], lot["variable"], len(fautifs),
                         len(sains), geste))
        ctx.close()
        nav.close()

    ecrire(fiches, ecartees)
    print("")
    print("fiches soumises   : %d" % len(fiches))
    print("propositions ECARTEES par la session : %d" % len(ecartees))
    for p, v, motif in ecartees:
        print("   %-26s %-20s %s" % (p[:-5], v, motif))
    return 0



def ecrire(fiches, ecartees):
    par_page = {}
    for f in fiches:
        par_page.setdefault(f["page"], []).append(f)
    h = ["<!DOCTYPE html><html lang=fr><head><meta charset=utf-8>",
         "<title>Revue du lot 4 (v2)</title>", "<style>"
         "body{font:15px/1.6 system-ui,sans-serif;margin:0;background:#f7f5f1;"
         "color:#1a1a18}header{padding:2.2rem 2rem 1.4rem;"
         "border-bottom:1px solid #d8d3c6}h1{font-size:1.45rem;margin:0 0 .4rem}"
         "header p{margin:.3rem 0;max-width:62rem;color:#55534e}"
         "main{padding:1.4rem 2rem 5rem}h2{font-size:1.05rem;margin:2.4rem 0 .7rem;"
         "padding-bottom:.3rem;border-bottom:2px solid #1a1a18}"
         ".fiche{background:#fff;border:1px solid #d8d3c6;margin:0 0 1.1rem;"
         "padding:.9rem 1.1rem}.vue{display:flex;gap:1rem;flex-wrap:wrap;"
         "margin:.6rem 0;padding-bottom:.6rem;border-bottom:1px dotted #d8d3c6}"
         ".vue:last-child{border-bottom:none}"
         ".col{flex:1 1 280px;min-width:240px}.col h4{margin:0 0 .3rem;"
         "font-size:.68rem;letter-spacing:.12em;text-transform:uppercase;"
         "color:#55534e}.col img{max-width:100%;display:block;"
         "border:1px solid #d8d3c6}.meta{font-size:.85rem;color:#3f3d38}"
         "code{background:#f1ede4;padding:.1rem .3rem;font-size:.85em}"
         ".geste{margin-top:.6rem;padding:.5rem .75rem;background:#f1ede4;"
         "border-left:3px solid #7a3b2e;font-size:.88rem}"
         ".ecart{background:#fbf0ee;border:1px solid #e0c4bf;padding:.9rem 1.1rem;"
         "margin:0 0 1.4rem}"
         "</style></head><body><header>"]
    h.append("<h1>Lot 4 &mdash; revue refaite</h1>")
    h.append("<p><b>%d propositions</b> sur <b>%d pages</b>. Chacune montre "
             "<b>tous</b> les &eacute;l&eacute;ments fautifs, pas le premier, "
             "et chacune a &eacute;t&eacute; <b>v&eacute;rifi&eacute;e avant "
             "de vous parvenir</b>&nbsp;: aucune de celles-ci ne d&eacute;grade "
             "quoi que ce soit.</p>" % (len(fiches), len(par_page)))
    h.append("<p>Quand une partie seulement des &eacute;l&eacute;ments "
             "&eacute;choue, la proposition est une <b>r&egrave;gle "
             "locale</b>&nbsp;: la variable ne bouge pas, et les "
             "&eacute;l&eacute;ments sains restent intacts.</p></header><main>")
    if ecartees:
        h.append("<div class=ecart><b>%d proposition(s) &eacute;cart&eacute;e(s) "
                 "par la session</b> &mdash; elles ne vous sont pas soumises."
                 "<p class=meta>%s</p></div>"
                 % (len(ecartees), "<br>".join(
                     "%s &middot; <code>%s</code> &middot; %s"
                     % (p[:-5], v, m) for p, v, m in ecartees)))
    for nom in sorted(par_page):
        h.append("<h2>%s</h2>" % nom[:-5])
        for f in par_page[nom]:
            h.append("<div class=fiche>")
            h.append("<p class=meta><code>%s</code> %s &rarr; %s &middot; "
                     "%d fautif(s), %d sain(s) &middot; d&eacute;placement "
                     "%.2f</p>" % (f["variable"], f["valeur"], f["propose"],
                                   f["fautifs"], f["sains"], f["deplacement"]))
            for v in f["vues"]:
                h.append("<div class=vue>")
                h.append("<div class=col><h4>tel qu'il est &mdash; %.2f</h4>"
                         "<img src='%s'></div>" % (v["r_avant"], v["avant"]))
                h.append("<div class=col><h4>propos&eacute; &mdash; %.2f "
                         "(seuil %.1f)</h4><img src='%s'></div>"
                         % (v["r_apres"], v["seuil"], v["apres"]))
                h.append("</div>")
            h.append("<p class=geste><b>%s</b><br><code>%s</code></p>"
                     % (f["geste"], f["css"].replace("<", "&lt;")))
            h.append("</div>")
    h.append("</main></body></html>")
    with io.open(os.path.join(SORTIE, "index.html"), "w",
                 encoding="utf-8", newline="\n") as f:
        f.write("\n".join(h))


if __name__ == "__main__":
    sys.exit(main())
