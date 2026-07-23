#!/usr/bin/env python3
# -*- coding: ascii -*-
"""sonde-lignes.py -- la mesure de contraste qui fait foi.

Trois approximations successives ont ete corrigees pour arriver ici, et
chacune a fait declarer des defauts qui n'existaient pas :

  1. le pire ARRET DECLARE du degrade  -- opposait au texte une couleur qu'il
     ne rencontre jamais (un arret "sable" en bas d'une couverture contre un
     titre qui reste en haut) ;
  2. le CADRE de l'element             -- englobe la marge interieure et la
     fin de derniere ligne, ou aucun glyphe ne se pose ; le colophon du
     Cheval de Turin y tombait a 1,38 alors que sa ligne de texte tient 6,06 ;
  3. la propriete `color` DANS UN SVG  -- la couleur y est `fill` ; `color`
     s'y herite sans jamais etre peinte, et les cartels de Rouges et Blancs
     etaient comptes 1,11 contre 10,09 reels.

Ce que fait cette sonde, et qui repond aux trois :
  - elle lit `fill` pour tout element d'un SVG, `color` ailleurs ;
  - elle masque les glyphes par `color:transparent` (JAMAIS `visibility`, qui
    emporterait le fond propre de l'element) sur l'element ET sa descendance ;
  - elle mesure sur les RECTANGLES DES LIGNES DE TEXTE, obtenus par Range,
    et non sur le cadre de l'element ;
  - elle lit les pixels REELLEMENT PEINTS de ces rectangles.

*** VERDICT D'USAGE, ETABLI LE 23/07/2026 : CETTE SONDE EST UN DETECTEUR,
*** ELLE NE FAIT PAS AUTORITE. Un bruit residuel subsiste au prelevement des
*** pixels et je n'ai pas su l'eliminer. Cas temoin, verifie a la main : la
*** pastille de piste de `hitchcock-truffaut`, texte #d9b98f sur fond #15120f,
*** vaut 10,03 -- la sonde annonce 1,09. Des pixels du fond de page se
*** retrouvent dans le rectangle d'une ligne pourtant entierement contenue
*** dans sa pastille, sans que la cause soit etablie.
***
*** CONSEQUENCE : ce que cette sonde signale se VERIFIE avant d'agir ; ce
*** qu'elle ne signale pas ne prouve rien. Aucune correction de dessin ne doit
*** etre decidee sur son seul comptage. Ce qu'elle a reellement apporte : deux
*** textes invisibles confirmes a la main (Lordsburg, le colophon du Cheval de
*** Turin) et deux regressions de la passe de dedoublement.

Elle reste conservatrice sur un point, volontairement : elle retient le pire
pixel de la ligne, y compris l'inter-mot. Un fond qui varie brutalement sous
une ligne est signale -- c'est le cas ou l'oeil, lui aussi, peine.

Aucune ecriture. Produit `resultats/lignes.json`.

Usage : RECETTE_BASE=http://127.0.0.1:8791 python sonde-lignes.py
"""

import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harnais  # noqa: E402

try:
    from PIL import Image
except ImportError:
    sys.stderr.write("ARRET : Pillow absent (aucune installation, mandat).\n")
    raise SystemExit(3)

SEUILS = {"courant": 4.5, "grand": 3.0}

JS_RELEVE = r"""
(seuils) => {
  const out = [];
  let i = 0;
  for (const el of document.querySelectorAll('*')) {
    let propre = '';
    for (const n of el.childNodes) if (n.nodeType === 3) propre += n.nodeValue;
    if (!propre.trim()) continue;
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden') continue;

    let opacite = 1;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const o = parseFloat(getComputedStyle(n).opacity);
      if (!isNaN(o)) opacite *= o;
    }
    if (opacite === 0) continue;

    // SVG : la couleur peinte est `fill`, jamais `color`.
    const estSVG = !!el.ownerSVGElement;
    const brut = window.__lireRgba(estSVG ? st.fill : st.color);
    if (!brut || brut.a === 0) continue;

    // Rectangles des LIGNES, pas du bloc.
    const rects = [];
    for (const n of el.childNodes) {
      if (n.nodeType !== 3 || !n.nodeValue.trim()) continue;
      const rg = document.createRange();
      rg.selectNodeContents(n);
      for (const r of rg.getClientRects()) {
        if (r.width < 1 || r.height < 1) continue;
        rects.push({x: r.left + window.scrollX, y: r.top + window.scrollY,
                    w: r.width, h: r.height});
      }
    }
    if (!rects.length) continue;

    const px = parseFloat(st.fontSize) || 16;
    const poids = parseInt(st.fontWeight, 10) || 400;
    const seuil = (px >= 24 || (px >= 18.66 && poids >= 700))
                ? seuils.grand : seuils.courant;

    el.setAttribute('data-l', 'l' + i);
    out.push({marque: 'l' + (i++), alpha: brut.a * opacite,
              couleur: [brut.r, brut.g, brut.b],
              seuil: seuil, rects: rects, px: px,
              extrait: propre.trim().slice(0, 40),
              chemin: window.__chemin(el)});
  }
  return out;
}
"""

# Masquer la COULEUR ne suffit pas : ce qui accompagne le texte doit partir
# avec lui. Un lien de note portant `border-bottom:1px dotted var(--brick)`
# laissait son filet POINTILLE dans le rectangle de la ligne ; la sonde lisait
# la couleur du lien parmi les pixels et concluait au ratio 1,00 -- le texte
# etait declare invisible contre son propre soulignement. Trente-huit faux
# positifs sur la seule page `the-old-oak`.
JS_MASQUE = """() => {
  for (const el of document.querySelectorAll('[data-l]')) {
    for (const n of [el].concat(Array.from(el.querySelectorAll('*')))) {
      n.style.setProperty('color', 'transparent', 'important');
      n.style.setProperty('fill', 'transparent', 'important');
      n.style.setProperty('text-shadow', 'none', 'important');
      n.style.setProperty('text-decoration-color', 'transparent',
                          'important');
      n.style.setProperty('border-color', 'transparent', 'important');
      n.style.setProperty('caret-color', 'transparent', 'important');
    }
  }
}"""


def lum(r, g, b):
    def c(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * c(r) + 0.7152 * c(g) + 0.0722 * c(b)


def main():
    sync = harnais.playwright_ou_arret()
    fiches = []
    with sync() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        for chemin in harnais.pages_films() + harnais.PAGES_MENU:
            nom = chemin.split("/")[-1]
            page.set_viewport_size({"width": 1280, "height": 900})
            page.goto(harnais.url(chemin), wait_until="load", timeout=30000)
            page.wait_for_timeout(120)
            # LA FENETRE EST PORTEE A LA HAUTEUR DU DOCUMENT AVANT TOUTE
            # MESURE. Une capture "pleine page" redimensionne la fenetre pour
            # composer l'image : les unites `vh`, les requetes de media et les
            # elements colles se deplacent alors ENTRE le moment ou l'on releve
            # les rectangles et celui ou l'on lit les pixels. Les cadres
            # pointaient a cote, et la sonde comptait 670 ecarts la ou il y en
            # a une fraction. En figeant la fenetre a la taille du document,
            # releve et capture decrivent la meme page.
            hauteur = page.evaluate(
                "() => Math.min(document.documentElement.scrollHeight, 20000)")
            page.set_viewport_size({"width": 1280, "height": int(hauteur)})
            page.evaluate(harnais.JS_FOND_EFFECTIF)
            page.wait_for_timeout(140)
            releve = page.evaluate(JS_RELEVE, SEUILS)
            if not releve:
                continue
            page.evaluate(JS_MASQUE)
            page.wait_for_timeout(60)
            image = Image.open(io.BytesIO(
                page.screenshot())).convert("RGB")
            for e in releve:
                pixels = []
                for r in e["rects"]:
                    x0, y0 = max(0, int(r["x"])), max(0, int(r["y"]))
                    x1 = min(image.width, int(r["x"] + r["w"]) + 1)
                    y1 = min(image.height, int(r["y"] + r["h"]) + 1)
                    if x1 <= x0 or y1 <= y0:
                        continue
                    zone = image.crop((x0, y0, x1, y1))
                    if zone.width * zone.height > 4000:
                        zone.thumbnail((64, 64))
                    pixels.extend(list(zone.getdata()))
                if not pixels:
                    continue
                couleur = e["couleur"]
                if e["alpha"] < 0.999:
                    moy = [sum(p[i] for p in pixels) / len(pixels)
                           for i in range(3)]
                    a = e["alpha"]
                    couleur = [a * couleur[i] + (1 - a) * moy[i]
                               for i in range(3)]
                lt = lum(*couleur)
                pire = min((max(lt, lum(*p)) + 0.05) / (min(lt, lum(*p)) + 0.05)
                           for p in pixels)
                if pire >= e["seuil"]:
                    continue
                fiches.append({
                    "page": nom, "chemin": e["chemin"],
                    "couleur": "#%02x%02x%02x" % tuple(int(round(c))
                                                       for c in couleur),
                    "seuil": e["seuil"], "ratio": round(pire, 2),
                    "px": e["px"], "extrait": e["extrait"],
                })
        ctx.close()
        nav.close()

    harnais.ecrire_json("lignes.json", fiches)
    print("ECARTS REELS, mesures sur les lignes de texte : %d" % len(fiches))
    par_page = {}
    for f in fiches:
        par_page.setdefault(f["page"], []).append(f)
    print("pages concernees : %d / 39" % len(par_page))
    print("")
    for nom in sorted(par_page, key=lambda n: -len(par_page[n])):
        v = par_page[nom]
        print("  %-30s %2d ecart(s), pire %.2f"
              % (nom[:-5], len(v), min(x["ratio"] for x in v)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
