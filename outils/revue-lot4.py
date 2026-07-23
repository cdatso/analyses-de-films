#!/usr/bin/env python3
# -*- coding: ascii -*-
"""revue-lot4.py -- prepare les deplacements lourds pour l'oeil d'AH.

Le lot 4 ne se tranche pas sur des codes hexadecimaux : il se tranche en
regardant. Ce script produit, pour chacun des lots restants, un AVANT et un
APRES du meme fragment de page -- l'un tel qu'il est, l'autre avec la valeur
proposee injectee a la volee. Aucun fichier du site n'est modifie : la valeur
est posee dans le navigateur, le temps d'une capture.

La revue sort HORS DU DEPOT, dans `_scratch\\revue-lot4\\`, pour la meme
raison que les maquettes d'accueil : elle n'a pas a etre publiee, et la
bascule embarque deja assez de poids.

Chaque fiche porte : le fragment avant/apres, le nombre d'elements touches,
l'amplitude du deplacement, si la variable sert AUSSI a autre chose qu'du
texte (auquel cas la corriger deborderait), et la recommandation de la
session parmi les trois voies du dossier -- corriger localement, documenter
l'exception, retoucher le fond.

Usage : RECETTE_BASE=http://127.0.0.1:8791 python revue-lot4.py
"""

import base64
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

# Le `_scratch` de la squad vit a cote de `Projects`, pas dedans : quatre
# niveaux au-dessus de ce fichier (outils -> depot -> Projects -> Claude).
SORTIE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "_scratch", "revue-lot4")

MARGE = 28          # pixels de contexte autour du fragment
LARGEUR_MAX = 560


JS_REPERE = r"""
(cible) => {
  // Les elements dont la couleur de texte RENDUE est celle du lot.
  const trouves = [];
  for (const el of document.querySelectorAll('*')) {
    let propre = '';
    for (const n of el.childNodes) if (n.nodeType === 3) propre += n.nodeValue;
    if (!propre.trim()) continue;
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden') continue;
    const c = window.__lireRgba(el.ownerSVGElement ? st.fill : st.color);
    if (!c) continue;
    if (window.__hex(c).toLowerCase() !== cible) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;
    trouves.push({x: r.left + window.scrollX, y: r.top + window.scrollY,
                  w: r.width, h: r.height,
                  extrait: propre.trim().slice(0, 60)});
  }
  return trouves;
}
"""

JS_INJECTE = """(a) => {
  const s = document.createElement('style');
  s.id = '__revue';
  s.textContent = ':root{' + a.variable + ':' + a.valeur + ' !important;}';
  document.head.appendChild(s);
}"""

JS_RETIRE = """() => {
  const s = document.getElementById('__revue');
  if (s) s.remove();
}"""


def recommande(lot):
    """La voie que la session propose, et son motif -- en une phrase."""
    if lot["deplacement"] >= 0.4:
        return ("retoucher le fond ou documenter",
                "deplacement de %.2f : ce n'est plus un ajustement, la couleur"
                " change de nature. La variable sert souvent de FOND ailleurs."
                % lot["deplacement"])
    if lot["classe"] == "MIXTE":
        return ("corriger localement",
                "la variable porte aussi des fonds ou des filets : une soeur"
                " de texte deplace le texte seul.")
    return ("corriger",
            "la variable ne sert qu'au texte : le deplacement reste contenu"
            " (%.2f) et n'atteint rien d'autre." % lot["deplacement"])


def png_data_uri(image):
    tampon = io.BytesIO()
    image.save(tampon, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(
        tampon.getvalue()).decode("ascii")


def main():
    chemin = os.path.join(ICI, "recette-playwright", "resultats",
                          "usage-variables.json")
    if not os.path.isfile(chemin):
        sys.stderr.write("ARRET : mesures absentes.\n")
        return 2
    with io.open(chemin, "r", encoding="utf-8") as f:
        lots = [x for x in json.load(f) if x["lourd"]]

    par_page = {}
    for x in lots:
        par_page.setdefault(x["page"], []).append(x)

    if not os.path.isdir(SORTIE):
        os.makedirs(SORTIE)

    fiches, manques = [], []
    sync = harnais.playwright_ou_arret()
    with sync() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        for nom_page in sorted(par_page,
                               key=lambda n: -sum(x["elements"]
                                                  for x in par_page[n])):
            page.set_viewport_size({"width": 1280, "height": 900})
            page.goto(harnais.url("films/" + nom_page), wait_until="load",
                      timeout=30000)
            page.wait_for_timeout(120)
            hauteur = page.evaluate(
                "() => Math.min(document.documentElement.scrollHeight, 20000)")
            page.set_viewport_size({"width": 1280, "height": int(hauteur)})
            page.evaluate(harnais.JS_FOND_EFFECTIF)
            page.wait_for_timeout(140)

            for lot in sorted(par_page[nom_page],
                              key=lambda x: -x["elements"]):
                zones = page.evaluate(JS_REPERE, lot["valeur"].lower())
                if not zones:
                    # NE JAMAIS SAUTER EN SILENCE. La premiere version de ce
                    # script passait au suivant sans rien dire : les trois
                    # pages les plus lourdes (pandora, rosetta,
                    # pandora-contrechamp) ont disparu de la revue sans que
                    # rien ne le signale. Un cas non presente est un cas non
                    # arbitre, et il doit se voir.
                    manques.append((nom_page, lot["variable"], lot["valeur"]))
                    continue
                z = zones[0]
                x0 = max(0, int(z["x"]) - MARGE)
                y0 = max(0, int(z["y"]) - MARGE)
                x1 = int(z["x"] + z["w"]) + MARGE
                y1 = int(z["y"] + z["h"]) + MARGE

                avant = Image.open(io.BytesIO(page.screenshot())).convert("RGB")
                page.evaluate(JS_INJECTE, {"variable": lot["variable"],
                                           "valeur": lot["propose"]})
                page.wait_for_timeout(80)
                apres = Image.open(io.BytesIO(page.screenshot())).convert("RGB")
                page.evaluate(JS_RETIRE)
                page.wait_for_timeout(40)

                boite = (min(x0, avant.width - 1), min(y0, avant.height - 1),
                         min(x1, avant.width), min(y1, avant.height))
                if boite[2] <= boite[0] or boite[3] <= boite[1]:
                    continue
                ia, ib = avant.crop(boite), apres.crop(boite)
                if ia.width > LARGEUR_MAX:
                    ratio = LARGEUR_MAX / float(ia.width)
                    taille = (LARGEUR_MAX, max(1, int(ia.height * ratio)))
                    ia = ia.resize(taille, Image.LANCZOS)
                    ib = ib.resize(taille, Image.LANCZOS)

                voie, motif = recommande(lot)
                fiches.append({
                    "page": nom_page, "variable": lot["variable"],
                    "valeur": lot["valeur"], "propose": lot["propose"],
                    "deplacement": lot["deplacement"],
                    "elements": lot["elements"], "classe": lot["classe"],
                    "usages_autres": lot.get("exemples_autres", []),
                    "ratio": lot["pire_ratio"], "extrait": z["extrait"],
                    "voie": voie, "motif": motif,
                    "avant": png_data_uri(ia), "apres": png_data_uri(ib),
                })
                print("  %-28s %-20s %2d el.  %s"
                      % (nom_page[:-5], lot["variable"], lot["elements"],
                         voie))
        ctx.close()
        nav.close()

    ecrire_revue(fiches, manques)
    print("")
    print("fiches preparees : %d" % len(fiches))
    if manques:
        print("CAS NON REPRESENTES : %d -- ils figurent en tete de la revue"
              % len(manques))
        for page_nom, var, val in manques:
            print("   %-28s %-20s valeur %s introuvable au rendu"
                  % (page_nom[:-5], var, val))
    print("revue : %s" % os.path.join(SORTIE, "index.html"))
    return 0


def ecrire_revue(fiches, manques=()):
    par_page = {}
    for f in fiches:
        par_page.setdefault(f["page"], []).append(f)

    h = []
    h.append("<!DOCTYPE html><html lang=fr><head><meta charset=utf-8>")
    h.append("<title>Revue du lot 4 &mdash; deplacements lourds</title>")
    h.append("<style>"
             "body{font:15px/1.6 system-ui,sans-serif;margin:0;"
             "background:#f7f5f1;color:#1a1a18}"
             "header{padding:2.4rem 2rem 1.6rem;border-bottom:1px solid #d8d3c6}"
             "h1{font-size:1.5rem;margin:0 0 .4rem;font-weight:600}"
             "header p{margin:.3rem 0;color:#55534e;max-width:60rem}"
             "main{padding:1.5rem 2rem 5rem}"
             "h2{font-size:1.1rem;margin:2.6rem 0 .8rem;padding-bottom:.35rem;"
             "border-bottom:2px solid #1a1a18}"
             ".fiche{background:#fff;border:1px solid #d8d3c6;margin:0 0 1.2rem;"
             "padding:1rem 1.2rem}"
             ".ligne{display:flex;gap:1.2rem;flex-wrap:wrap;align-items:flex-start}"
             ".vue{flex:1 1 300px;min-width:260px}"
             ".vue h4{margin:0 0 .35rem;font-size:.72rem;letter-spacing:.12em;"
             "text-transform:uppercase;color:#55534e;font-weight:600}"
             ".vue img{max-width:100%;display:block;border:1px solid #d8d3c6}"
             ".meta{font-size:.86rem;color:#3f3d38;margin:.7rem 0 0}"
             "code{background:#f1ede4;padding:.1rem .3rem;font-size:.85em}"
             ".pastille{display:inline-block;width:.85em;height:.85em;"
             "vertical-align:-.1em;border:1px solid #0003;margin-right:.25em}"
             ".voie{margin-top:.7rem;padding:.55rem .8rem;background:#f1ede4;"
             "border-left:3px solid #7a3b2e;font-size:.9rem}"
             ".voie b{color:#7a3b2e}"
             ".alerte{border-left-color:#a3302a;background:#fbf0ee}"
             "</style></head><body>")
    h.append("<header><h1>Lot 4 &mdash; les d&eacute;placements lourds, "
             "page par page</h1>")
    h.append("<p><b>%d cas</b> sur <b>%d pages</b>. Pour chacun&nbsp;: le "
             "fragment tel qu'il est, et le m&ecirc;me fragment avec la "
             "valeur propos&eacute;e. Rien n'est modifi&eacute; dans le site "
             "&mdash; la valeur est inject&eacute;e le temps d'une "
             "capture.</p>" % (len(fiches), len(par_page)))
    h.append("<p>Trois voies pour chaque cas&nbsp;: <b>corriger</b> "
             "(localement si la variable sert aussi ailleurs), "
             "<b>documenter l'exception</b> au registre, ou "
             "<b>retoucher le fond</b>. La recommandation de la session est "
             "indiqu&eacute;e&nbsp;; elle ne vaut pas d&eacute;cision.</p>")
    h.append("<p style='color:#a3302a'><b>&Agrave; savoir</b>&nbsp;: la mesure "
             "de contraste automatique s'est r&eacute;v&eacute;l&eacute;e peu "
             "s&ucirc;re sur les fonds complexes (un cas t&eacute;moin "
             "mesur&eacute; 1,09 vaut 10,03 en r&eacute;alit&eacute;). "
             "Les ratios ci-dessous viennent du calcul CSS&nbsp;; "
             "<b>l'&oelig;il tranche, pas le chiffre</b>.</p></header><main>")

    if manques:
        h.append("<div class='fiche' style='border-left:4px solid #a3302a'>")
        h.append("<h4 style='margin:0 0 .5rem'>%d cas NON "
                 "repr&eacute;sent&eacute;s ci-dessous</h4>" % len(manques))
        h.append("<p class=meta>La couleur relev&eacute;e lors de la mesure "
                 "ne se retrouve plus au rendu&nbsp;: ces lots ont "
                 "&eacute;t&eacute; d&eacute;plac&eacute;s depuis, par un lot "
                 "pr&eacute;c&eacute;dent ou par la passe de "
                 "d&eacute;doublement. <b>Ils sont &agrave; re-mesurer avant "
                 "arbitrage</b> &mdash; un cas non pr&eacute;sent&eacute; est "
                 "un cas non arbitr&eacute;.</p><p class=meta>")
        h.append("<br>".join("%s &middot; <code>%s</code> &middot; %s"
                             % (p[:-5], v, val) for p, v, val in manques))
        h.append("</p></div>")

    for nom in par_page:
        h.append("<h2>%s</h2>" % nom[:-5])
        for f in par_page[nom]:
            alerte = " alerte" if f["deplacement"] >= 0.4 else ""
            h.append("<div class=fiche>")
            h.append("<div class=ligne>")
            h.append("<div class=vue><h4>tel qu'il est</h4>"
                     "<img src='%s' alt=''></div>" % f["avant"])
            h.append("<div class=vue><h4>avec la valeur propos&eacute;e</h4>"
                     "<img src='%s' alt=''></div>" % f["apres"])
            h.append("</div>")
            h.append("<p class=meta><code>%s</code> "
                     "<span class=pastille style='background:%s'></span>%s "
                     "&rarr; <span class=pastille style='background:%s'></span>"
                     "%s &nbsp;&middot;&nbsp; %d &eacute;l&eacute;ment(s) "
                     "&middot; d&eacute;placement %.2f &middot; ratio actuel "
                     "%.2f</p>"
                     % (f["variable"], f["valeur"], f["valeur"], f["propose"],
                        f["propose"], f["elements"], f["deplacement"],
                        f["ratio"]))
            if f["classe"] == "MIXTE" and f["usages_autres"]:
                h.append("<p class=meta>Cette variable sert aussi &agrave; "
                         "&nbsp;: <b>%s</b> &mdash; la corriger en place "
                         "d&eacute;placerait aussi cela.</p>"
                         % ", ".join(f["usages_autres"]))
            h.append("<p class='voie%s'><b>%s</b> &mdash; %s</p>"
                     % (alerte, f["voie"], f["motif"]))
            h.append("</div>")
    h.append("</main></body></html>")

    with io.open(os.path.join(SORTIE, "index.html"), "w",
                 encoding="utf-8", newline="\n") as f:
        f.write("\n".join(h))


if __name__ == "__main__":
    sys.exit(main())
