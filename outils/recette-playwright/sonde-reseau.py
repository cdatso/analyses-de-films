#!/usr/bin/env python3
# -*- coding: ascii -*-
"""sonde-reseau.py -- journal reseau au rendu reel (P-24, P-27, P-32, P-37).

Ce que la sonde etablit, et par quelle preuve :
  P-24  aucune requete vers un domaine tiers -- toute requete dont l'hote
        n'est pas le serveur local est un ECHEC, nommee avec son URL.
  P-27  les subsets non latins ne sont pas telecharges sur une page latine --
        liste des .woff2 reellement demandes, page par page.
  P-32  aucun URL ne casse -- code HTTP de chaque document.
  P-37  poids de page : PREMIERE visite (contexte neuf, cache vide) et visite
        SUIVANTE (meme contexte, l'accueil deja visite -- c'est le sens du
        seuil : les fontes sont mutualisees et ne se rechargent pas).

Limite declaree : le serveur local est `python -m http.server`, dont la
politique de cache (Last-Modified, pas de Cache-Control) n'est pas celle de
GitHub Pages. La mesure "visite suivante" vaut pour l'architecture du site
(ressources mutualisees), pas pour les en-tetes du futur hebergeur.

Cette sonde ne modifie aucun fichier du site.
"""

import sys
from urllib.parse import urlparse

import harnais


def hote_local(u):
    p = urlparse(u)
    return p.hostname in ("127.0.0.1", "localhost")


def collecte(page, cible):
    """Charge une page et retourne le journal de ses requetes."""
    journal = []

    def sur_reponse(reponse):
        req = reponse.request
        try:
            tailles = req.sizes()
        except Exception:
            tailles = {}
        journal.append({
            "url": reponse.url,
            "type": req.resource_type,
            "statut": reponse.status,
            "octets": int(tailles.get("responseBodySize") or 0)
                      + int(tailles.get("responseHeadersSize") or 0),
            "tiers": not hote_local(reponse.url),
        })

    def sur_echec(req):
        journal.append({
            "url": req.url, "type": req.resource_type, "statut": 0,
            "octets": 0, "tiers": not hote_local(req.url),
            "echec": req.failure,
        })

    page.on("response", sur_reponse)
    page.on("requestfailed", sur_echec)
    reponse = page.goto(harnais.url(cible), wait_until="load", timeout=30000)
    page.wait_for_timeout(400)
    page.remove_listener("response", sur_reponse)
    page.remove_listener("requestfailed", sur_echec)
    return (reponse.status if reponse else 0), journal


def resume(journal):
    return {
        "requetes": len(journal),
        "octets": sum(e["octets"] for e in journal),
        "tiers": [e["url"] for e in journal if e["tiers"]],
        "non_200": [(e["url"], e["statut"]) for e in journal
                    if e["statut"] not in (200, 304)],
        "polices": sorted(e["url"].rsplit("/", 1)[-1] for e in journal
                          if e["type"] == "font" or e["url"].endswith(".woff2")),
    }


def main():
    sync_playwright = harnais.playwright_ou_arret()
    cibles = harnais.pages_toutes()
    resultats = {}

    with sync_playwright() as pw:
        nav = pw.chromium.launch()

        # --- Visites SUIVANTES : un seul contexte, l'accueil d'abord.
        ctx_chaud = nav.new_context(viewport={"width": 1280, "height": 900})
        page_chaude = ctx_chaud.new_page()
        collecte(page_chaude, "index.html")          # amorce le cache partage

        for cible in cibles:
            # --- PREMIERE visite : contexte neuf, cache vide.
            ctx_froid = nav.new_context(viewport={"width": 1280, "height": 900})
            page_froide = ctx_froid.new_page()
            statut, froid = collecte(page_froide, cible)
            ctx_froid.close()

            _s, chaud = collecte(page_chaude, cible)

            resultats[cible] = {
                "statut": statut,
                "froid": resume(froid),
                "chaud": resume(chaud),
                "journal_froid": froid,
            }
            sys.stderr.write("  %-46s %3d  froid %7d o  chaud %7d o\n" % (
                cible, statut, resultats[cible]["froid"]["octets"],
                resultats[cible]["chaud"]["octets"]))

        ctx_chaud.close()
        nav.close()

    chemin = harnais.ecrire_json("reseau.json", resultats)
    tiers = {c: r["froid"]["tiers"] for c, r in resultats.items() if r["froid"]["tiers"]}
    casses = {c: r["statut"] for c, r in resultats.items() if r["statut"] != 200}
    print("pages mesurees        : %d" % len(resultats))
    print("pages a requete tierce: %d" % len(tiers))
    for c, urls in sorted(tiers.items()):
        print("   %s -> %s" % (c, ", ".join(sorted(set(urls))[:4])))
    print("documents non 200     : %d %s" % (len(casses), casses if casses else ""))
    print("resultat brut         : %s" % chemin)
    return 0


if __name__ == "__main__":
    sys.exit(main())
