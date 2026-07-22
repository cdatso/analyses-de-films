#!/usr/bin/env python3
# -*- coding: ascii -*-
"""sonde-poids.py -- P-37 sous protocole isole.

Pourquoi cette sonde separee. Dans `sonde-reseau.py`, la "visite suivante" est
mesuree dans UN contexte qui parcourt les pages en sequence : le resultat
depend alors de l'ordre de visite. Le diptyque Pandora l'a montre --
`pandora-contrechamp.html`, visitee la premiere, paie l'affiche partagee
(1 660 Ko), et `pandora.html`, visitee ensuite, ne paie plus rien (36 Ko).
Aucun des deux chiffres ne decrit la page.

Protocole isole, un contexte NEUF par mesure :
  premiere visite  : contexte vide -> page cible.
  visite suivante  : contexte vide -> index.html -> page cible.
Le second cas est exactement ce que le seuil de 400 Ko vise : un visiteur qui
a deja charge le mobilier partage (fontes, feuilles) arrive sur une page.
Chaque page est ainsi mesuree seule, sans heritage d'une autre page d'analyse.

Cette sonde ne modifie aucun fichier du site.
"""

import sys
from urllib.parse import urlparse

import harnais

SEUIL_PREMIERE = 900 * 1024
SEUIL_SUIVANTE = 400 * 1024


def charge(page, cible):
    total = {"octets": 0, "detail": []}

    def sur_reponse(reponse):
        try:
            t = reponse.request.sizes()
        except Exception:
            t = {}
        n = int(t.get("responseBodySize") or 0) + int(t.get("responseHeadersSize") or 0)
        total["octets"] += n
        if n > 0:
            total["detail"].append((urlparse(reponse.url).path, n))

    page.on("response", sur_reponse)
    page.goto(harnais.url(cible), wait_until="load", timeout=30000)
    page.wait_for_timeout(400)
    page.remove_listener("response", sur_reponse)
    total["detail"].sort(key=lambda x: -x[1])
    return total


def main():
    sync_playwright = harnais.playwright_ou_arret()
    resultats = {}
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        for cible in harnais.PAGES_PROTOTYPE:
            ctx = nav.new_context(viewport={"width": 1280, "height": 900})
            p = ctx.new_page()
            premiere = charge(p, cible)
            ctx.close()

            ctx = nav.new_context(viewport={"width": 1280, "height": 900})
            p = ctx.new_page()
            charge(p, "index.html")             # le visiteur arrive par l'accueil
            suivante = charge(p, cible)
            ctx.close()

            resultats[cible] = {"premiere": premiere, "suivante": suivante}
        nav.close()

    harnais.ecrire_json("poids.json", resultats)

    print("P-37 -- protocole isole (un contexte neuf par mesure)")
    print("seuils : 1re visite 900 Ko  |  visite suivante 400 Ko")
    print("")
    print("%-38s %10s %10s  %s" % ("page", "1re (Ko)", "suiv (Ko)", "verdict"))
    ecarts = 0
    for cible, r in resultats.items():
        a, b = r["premiere"]["octets"], r["suivante"]["octets"]
        v = []
        if a > SEUIL_PREMIERE:
            v.append("1re>900Ko")
        if b > SEUIL_SUIVANTE:
            v.append("suiv>400Ko")
        if v:
            ecarts += 1
        print("%-38s %10.1f %10.1f  %s" % (cible, a / 1024.0, b / 1024.0,
                                           ",".join(v) if v else "OK"))
    print("")
    print("pages en ecart : %d / %d" % (ecarts, len(resultats)))
    print("")
    print("Les 3 plus grosses ressources de chaque page en visite suivante :")
    for cible, r in resultats.items():
        bouts = ", ".join("%s %.0f Ko" % (c, n / 1024.0)
                          for c, n in r["suivante"]["detail"][:3])
        print("  %-38s %s" % (cible, bouts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
