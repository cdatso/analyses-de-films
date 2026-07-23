#!/usr/bin/env python3
# -*- coding: ascii -*-
"""sonde-post-bascule.py -- le controle des URLs PUBLIQUES, apres le push.

Garantie 3 de l'amendement 1 au mandat : les sondes doivent etre PRETES AVANT
le gate, pas ecrites dans l'urgence. Verdict attendu en ~2 minutes.

Ce qu'elle verifie, et rien d'autre -- ce sont exactement les criteres de
FALLBACK IMMEDIAT de la garantie 4 :
  1. les 34 URLs de l'annexe A repondent 200 ;
  2. les 5 pages du menu v2, qui n'existaient pas avant la bascule, aussi ;
  3. la feuille de mobilier, la feuille de fontes et les fontes elles-memes
     sont SERVIES (une page nue ou une typographie de repli = fallback) ;
  4. trois pages temoins rendent leur structure : menu, cartouche, corps.

Tout le reste -- contraste, poids, geometrie -- a ete mesure AVANT la bascule
et n'a pas a l'etre ici : en situation, on constate, on ne diagnostique pas.

MODE A BLANC : sans --public, la sonde tourne sur le serveur local et sert a
verifier qu'elle marche. Avec --public, elle interroge le site en ligne.

Usage : python sonde-post-bascule.py [--public] [--base URL]
Codes : 0 tout vert -- 1 FALLBACK (un critere dur en echec) -- 2 outillage.
"""

import argparse
import io
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harnais  # noqa: E402

BASE_PUBLIQUE = "https://www.cdatso.be/analyses-de-films"
ANNEXE_A = os.path.join(harnais.DOSSIER_DOCS, "recette-v2-annexe-A-regeneree.md")

PAGES_MENU_V2 = ["critiques.html", "etudes.html", "qui-sommes-nous.html",
                 "comment-ca-marche.html", "demander-une-analyse.html"]

TEMOINS = ["index.html", "films/pandora.html", "films/le-golem.html"]

JS_STRUCTURE = """() => ({
  menu: !!document.querySelector('header.chrome nav.menu'),
  aria: document.querySelectorAll('[aria-current="page"]').length,
  cartouche: !!document.querySelector('.cartouche'),
  corps: (document.body.innerText || '').trim().length,
  literata: document.fonts.check('16px Literata'),
  plex: document.fonts.check('12px "IBM Plex Mono"'),
})"""


def urls_de_annexe_a():
    """La checklist de P-32, lue dans l'annexe A du jour -- jamais recopiee."""
    if not os.path.isfile(ANNEXE_A):
        sys.stderr.write("ARRET : annexe A introuvable (%s)\n" % ANNEXE_A)
        raise SystemExit(2)
    with io.open(ANNEXE_A, "r", encoding="utf-8") as f:
        t = f.read()
    urls = re.findall(r"^\|\s*\d+\s*\|\s*`([^`]+)`", t, re.M)
    if not urls:
        sys.stderr.write("ARRET : aucune URL lue dans l'annexe A\n")
        raise SystemExit(2)
    return urls


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--public", action="store_true",
                    help="interroge le site EN LIGNE")
    ap.add_argument("--base", default=None)
    args = ap.parse_args()

    base = args.base or (BASE_PUBLIQUE if args.public else harnais.BASE)
    base = base.rstrip("/")
    urls = urls_de_annexe_a()
    print("base      : %s" % base)
    print("checklist : %d URLs (annexe A) + %d pages du menu v2"
          % (len(urls), len(PAGES_MENU_V2)))
    print("")

    depart = time.time()
    fallback, avertissements = [], []
    sync = harnais.playwright_ou_arret()
    with sync() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1280, "height": 900},
                              ignore_https_errors=False)
        page = ctx.new_page()

        # --- 1 et 2 : les documents repondent-ils ?
        for chemin in urls + PAGES_MENU_V2:
            cible = base + "/" + chemin.lstrip("/")
            try:
                r = page.goto(cible, wait_until="domcontentloaded",
                              timeout=25000)
                code = r.status if r else 0
            except Exception as e:          # noqa: BLE001
                code = 0
                avertissements.append("%s : %s" % (chemin, str(e)[:60]))
            if code != 200:
                fallback.append("%s -> %s" % (chemin, code or "pas de reponse"))
                print("  ECHEC  %-42s %s" % (chemin, code or "injoignable"))
        print("  documents en echec : %d / %d"
              % (len(fallback), len(urls) + len(PAGES_MENU_V2)))

        # --- 3 et 4 : les feuilles et les fontes sont-elles SERVIES ?
        print("")
        for chemin in TEMOINS:
            page.goto(base + "/" + chemin, wait_until="load", timeout=25000)
            page.wait_for_timeout(600)
            s = page.evaluate(JS_STRUCTURE)
            defauts = []
            if not s["menu"]:
                defauts.append("menu absent")
            if s["aria"] != 1:
                defauts.append("aria-current x%d" % s["aria"])
            if chemin.startswith("films/") and not s["cartouche"]:
                defauts.append("cartouche absent")
            if s["corps"] < 500:
                defauts.append("corps de page vide (%d car.)" % s["corps"])
            if not s["literata"]:
                defauts.append("Literata NON SERVIE")
            if not s["plex"]:
                defauts.append("IBM Plex Mono NON SERVIE")
            if defauts:
                fallback.append("%s : %s" % (chemin, ", ".join(defauts)))
            print("  %-30s %s" % (chemin,
                                  ", ".join(defauts) if defauts else "conforme"))

        ctx.close()
        nav.close()

    duree = time.time() - depart
    print("")
    print("duree du controle : %.0f s" % duree)
    if fallback:
        print("")
        print("*** CRITERE DE FALLBACK ATTEINT -- %d defaut(s) ***"
              % len(fallback))
        for f in fallback:
            print("    %s" % f)
        print("")
        print("Appliquer la procedure : docs/procedure-retour-arriere.md")
        return 1
    print("TOUT VERT -- aucun critere de fallback atteint.")
    if avertissements:
        print("avertissements (non bloquants) : %d" % len(avertissements))
        for a in avertissements[:5]:
            print("    %s" % a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
