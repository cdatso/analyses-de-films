#!/usr/bin/env python3
# -*- coding: ascii -*-
"""sonde-double-contexte.py -- les variables qui servent sur DEUX fonds.

Le constat qui rend ce script necessaire. Corriger une variable de texte
suppose qu'elle se pose toujours sur le meme genre de fond. Ce n'est pas le
cas : dans une page bespoke, le meme `--gris` colore un cartel sur le papier
ET une legende sur la couverture sombre. Assombrir pour le papier, c'est
casser la couverture ; eclaircir pour la couverture, c'est casser le papier.

Ce n'est pas un defaut de reglage, c'est une impossibilite arithmetique. Pour
un fond de luminance Lf, le seuil impose au texte :
    fond SOMBRE  ->  L_texte >= 4.5*(Lf+0.05)-0.05
    fond CLAIR   ->  L_texte <= (Lf+0.05)/4.5-0.05
Quand la borne basse depasse la borne haute, AUCUNE valeur ne convient.

La solution n'est pas d'iterer mais de DEDOUBLER -- et la maniere idiomatique
de dedoubler en CSS n'est pas de reecrire des regles : c'est de redefinir la
variable DANS le conteneur sombre. La cascade fait le reste, chaque
`color: var(--x)` du sous-arbre prend la valeur locale, sans qu'aucun
selecteur de texte ne soit touche.

Le script mesure donc, pour chaque variable en echec : les fonds qu'elle
rencontre, s'ils sont compatibles, et QUEL ELEMENT porte le fond sombre --
c'est lui qui recevra la redefinition.

Aucune ecriture. Produit `resultats/double-contexte.json`.

Usage : RECETTE_BASE=http://127.0.0.1:8791 python sonde-double-contexte.py
"""

import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harnais  # noqa: E402

SEUIL_COURANT = 4.5

JS = r"""
(seuil) => {
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
    if (opacite === 0) continue;

    const fond = window.__fondEffectif(el);
    const brut = window.__lireRgba(st.color);
    if (!brut) continue;
    const alpha = brut.a * opacite;
    const texte = alpha >= 0.999 ? brut
                : window.__composer({r: brut.r, g: brut.g, b: brut.b, a: alpha}, fond);

    // L'ANCETRE QUI PORTE LE FOND : c'est lui qui recevra la redefinition
    // de la variable. On remonte jusqu'au premier fond non transparent.
    let porteur = null;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const bg = window.__lireRgba(getComputedStyle(n).backgroundColor);
      if (bg && bg.a > 0.05) { porteur = n; break; }
    }

    const px = parseFloat(st.fontSize) || 16;
    const poids = parseInt(st.fontWeight, 10) || 400;
    const grand = px >= 24 || (px >= 18.66 && poids >= 700);

    sortie.push({
      texte: window.__hex(texte),
      fond: window.__hex(fond),
      seuil: grand ? 3.0 : seuil,
      ratio: Math.round(window.__ratio(texte, fond) * 100) / 100,
      porteur: porteur ? porteur.tagName.toLowerCase()
                 + (typeof porteur.className === 'string' && porteur.className
                    ? '.' + porteur.className.trim().split(/\s+/).join('.') : '')
               : null,
      extrait: propre.trim().slice(0, 34),
    });
  }
  return sortie;
}
"""


def luminance(h):
    h = h.lstrip("#")
    rgb = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]

    def c(v):
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (c(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def variables_de_page(chemin):
    with io.open(chemin, "r", encoding="utf-8") as f:
        t = f.read()
    trouve = {}
    for m in re.finditer(r"(--[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\s*;", t):
        nom, val = m.group(1), m.group(2).lower()
        if len(val) == 4:
            val = "#" + "".join(c * 2 for c in val[1:])
        trouve.setdefault(val[:7], []).append(nom)
    return trouve


def main():
    sync = harnais.playwright_ou_arret()
    par_variable = {}
    with sync() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        for chemin in harnais.pages_films():
            nom = chemin.split("/")[-1]
            palette = variables_de_page(
                os.path.join(harnais.DOSSIER_FILMS, nom))
            page.goto(harnais.url(chemin), wait_until="load", timeout=30000)
            page.evaluate(harnais.JS_FOND_EFFECTIF)
            page.wait_for_timeout(110)
            for c in page.evaluate(JS, SEUIL_COURANT):
                noms = palette.get(c["texte"])
                if not noms:
                    continue
                cle = (nom, sorted(noms)[0])
                e = par_variable.setdefault(cle, {
                    "page": nom, "variable": sorted(noms)[0],
                    "valeur": c["texte"], "fonds": {}})
                f = e["fonds"].setdefault(c["fond"], {
                    "elements": 0, "echecs": 0, "seuil": c["seuil"],
                    "porteurs": {}, "pire": 99.0})
                f["elements"] += 1
                f["pire"] = min(f["pire"], c["ratio"])
                if c["ratio"] < c["seuil"]:
                    f["echecs"] += 1
                if c["porteur"]:
                    f["porteurs"][c["porteur"]] = \
                        f["porteurs"].get(c["porteur"], 0) + 1
        ctx.close()
        nav.close()

    # Verdict par variable : une valeur unique est-elle possible ?
    sortie = []
    for (page_nom, variable), e in par_variable.items():
        if len(e["fonds"]) < 2:
            continue
        if not any(f["echecs"] for f in e["fonds"].values()):
            continue
        # Pour UN fond donne, le texte convient s'il est assez SOMBRE
        # (L <= haut) OU assez CLAIR (L >= bas). Deux intervalles, pas un.
        # Une valeur unique existe donc si l'une de ces deux strategies tient
        # sur TOUS les fonds a la fois :
        #   A -- plus sombre que tous  : L <= min(haut_i), realisable si >= 0
        #   B -- plus clair que tous   : L >= max(bas_i),  realisable si <= 1
        # Confondre les deux bornes en une seule condition (mini <= maxi)
        # declare impossibles des cas qui ne le sont pas : une page dont tous
        # les fonds sont clairs se corrige tres bien par un texte sombre.
        mini, maxi = -1.0, 2.0
        fond_mini = fond_maxi = None
        for hexa, f in e["fonds"].items():
            lf = luminance(hexa)
            s = f["seuil"]
            bas = s * (lf + 0.05) - 0.05
            haut = (lf + 0.05) / s - 0.05
            if bas > mini:
                mini, fond_mini = bas, hexa
            if haut < maxi:
                maxi, fond_maxi = haut, hexa
        strategie_sombre = maxi >= 0.0
        strategie_claire = mini <= 1.0
        possible = strategie_sombre or strategie_claire
        sortie.append({
            "page": page_nom, "variable": variable, "valeur": e["valeur"],
            "possible": possible,
            "strategie_sombre": strategie_sombre,
            "strategie_claire": strategie_claire,
            "borne_basse": round(mini, 3), "fond_qui_l_impose": fond_mini,
            "borne_haute": round(maxi, 3), "fond_qui_l_impose_2": fond_maxi,
            "fonds": {h: {"elements": f["elements"], "echecs": f["echecs"],
                          "pire": f["pire"], "seuil": f["seuil"],
                          "luminance": round(luminance(h), 3),
                          "porteurs": sorted(f["porteurs"],
                                             key=f["porteurs"].get,
                                             reverse=True)[:3]}
                      for h, f in e["fonds"].items()},
        })

    sortie.sort(key=lambda x: (x["possible"], x["page"]))
    harnais.ecrire_json("double-contexte.json", sortie)

    impossibles = [x for x in sortie if not x["possible"]]
    print("variables rencontrant PLUSIEURS fonds, avec au moins un echec : %d"
          % len(sortie))
    print("  dont A DEDOUBLER (aucune valeur unique possible) : %d"
          % len(impossibles))
    print("")
    solubles = [x for x in sortie if x["possible"]]
    print("  dont solubles par une valeur unique (deja couvertes par les "
          "lots 2/3/4) : %d" % len(solubles))
    print("")
    for x in impossibles:
        print("%-26s %-16s %s" % (x["page"][:-5], x["variable"], x["valeur"]))
        print("     aucun texte assez sombre (borne %.3f, fond %s) NI assez "
              "clair (borne %.3f, fond %s)"
              % (x["borne_haute"], x["fond_qui_l_impose_2"],
                 x["borne_basse"], x["fond_qui_l_impose"]))
        for h, f in sorted(x["fonds"].items(), key=lambda kv: kv[1]["luminance"]):
            print("     fond %s L=%.3f  %d el. (%d en echec)  porteur: %s"
                  % (h, f["luminance"], f["elements"], f["echecs"],
                     ", ".join(f["porteurs"]) or "?"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
