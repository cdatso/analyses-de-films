#!/usr/bin/env python3
# -*- coding: ascii -*-
"""sonde-liens.py -- zero lien mort interne sur v2-proto (mandat 4.5).

Les liens sont releves dans le DOM RENDU (et non par lecture du source) :
c'est le seul relevi qui voie ce qu'un visiteur peut reellement cliquer,
y compris ce que la liste statique et le composant de corpus produisent.

Trois controles :
  - cible HTTP : chaque lien interne est demande, son code doit etre 200 ;
  - ancre      : un lien vers `#quelque-chose` doit trouver sa cible dans
                 la page visee ;
  - sortant    : tout lien vers un autre hote est LISTE (il n'est pas
                 demande -- une recette ne sort pas sur le reseau public).

Cette sonde ne modifie aucun fichier du site.
"""

import sys
from urllib.parse import urldefrag, urlparse

import harnais

JS_LIENS = r"""
() => {
  const vus = [];
  for (const a of document.querySelectorAll('a[href]')) {
    const brut = a.getAttribute('href');
    if (!brut || brut.startsWith('mailto:') || brut.startsWith('tel:')) continue;
    vus.push({brut: brut, resolu: a.href, texte: (a.textContent || '').trim().slice(0, 40)});
  }
  return vus;
}
"""


def main():
    sync_playwright = harnais.playwright_ou_arret()
    cibles = harnais.pages_toutes()
    liens = {}
    sortants, morts, ancres_mortes = [], [], []

    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()

        # 1. Relever tous les liens du DOM rendu.
        for cible in cibles:
            page.goto(harnais.url(cible), wait_until="load", timeout=30000)
            page.wait_for_timeout(120)
            liens[cible] = page.evaluate(JS_LIENS)

        # 2. Dedoublonner les cibles internes, puis les demander une fois.
        internes = {}
        for source, lst in liens.items():
            for l in lst:
                p = urlparse(l["resolu"])
                if p.hostname not in ("127.0.0.1", "localhost"):
                    sortants.append((source, l["resolu"]))
                    continue
                internes.setdefault(l["resolu"], []).append(source)

        etats = {}
        ancres = {}
        for cible_url in sorted(internes):
            sans_ancre, fragment = urldefrag(cible_url)
            if sans_ancre not in etats:
                r = page.request.get(sans_ancre)
                etats[sans_ancre] = r.status
            if etats[sans_ancre] != 200:
                morts.append((cible_url, etats[sans_ancre], internes[cible_url][:2]))
                continue
            if fragment:
                if sans_ancre not in ancres:
                    page.goto(sans_ancre, wait_until="load", timeout=30000)
                    ancres[sans_ancre] = set(page.evaluate(
                        "() => Array.from(document.querySelectorAll('[id], a[name]'))"
                        ".map(e => e.id || e.getAttribute('name')).filter(Boolean)"))
                if fragment not in ancres[sans_ancre]:
                    ancres_mortes.append((cible_url, internes[cible_url][:2]))

        ctx.close()
        nav.close()

    harnais.ecrire_json("liens.json", {
        "par_page": {k: len(v) for k, v in liens.items()},
        "cibles_internes": len(internes),
        "morts": morts,
        "ancres_mortes": ancres_mortes,
        "sortants": sorted(set(u for _s, u in sortants)),
    })

    total = sum(len(v) for v in liens.values())
    print("Liens releves dans le DOM rendu de %d pages : %d" % (len(cibles), total))
    print("Cibles internes distinctes demandees        : %d" % len(internes))
    print("LIENS MORTS (statut != 200)                 : %d" % len(morts))
    for m in morts[:20]:
        print("   %s -> %s  (depuis %s)" % (m[1], m[0], ", ".join(m[2])))
    print("ANCRES MORTES (#fragment introuvable)       : %d" % len(ancres_mortes))
    for a in ancres_mortes[:20]:
        print("   %s  (depuis %s)" % (a[0], ", ".join(a[1])))
    hotes = sorted(set(urlparse(u).hostname for _s, u in sortants))
    print("Liens SORTANTS (listes, non demandes)       : %d vers %s"
          % (len(set(u for _s, u in sortants)), hotes if hotes else "-"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
