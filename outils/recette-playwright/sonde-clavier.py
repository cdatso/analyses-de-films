#!/usr/bin/env python3
# -*- coding: ascii -*-
"""sonde-clavier.py -- P-40 : tout interactif atteignable ET visible au clavier.

Le prototype avait pose la regle `:focus-visible` dans mobilier.css et
constate qu'elle "s'applique" ; il n'avait pas pu parcourir la page a la
tabulation. C'est ce parcours que cette sonde execute.

Deux exigences distinctes, mesurees separement :
  ATTEIGNABLE -- l'inventaire des elements focalisables de la page est
                 compare a l'ensemble reellement atteint en pressant Tab.
  VISIBLE     -- au moment ou l'element a le focus clavier, son indicateur
                 est mesure aux styles calcules : contour (outline-style
                 different de none ET outline-width > 0) ou, a defaut,
                 une ombre portee. Un focus sans indicateur est un ECART.

Rappel : Tab au clavier declenche `:focus-visible` (contrairement au clic),
c'est donc bien la regle du site qui est eprouvee.

Identite des elements : chaque focalisable recoit un numero d'inventaire
`data-recette-idx` POSE EN MEMOIRE dans la page chargee, jamais dans le
fichier. Un chemin CSS ne suffit pas -- plusieurs liens d'une meme liste
partagent le meme chemin, ce qui faisait s'arreter la premiere version de
cette sonde au bout de deux tabulations (defaut de la sonde, corrige).

Cette sonde ne modifie aucun fichier du site.
"""

import sys

import harnais

SELECTEUR_FOCALISABLE = (
    'a[href], button, input:not([type="hidden"]), select, textarea, '
    'summary, [tabindex]:not([tabindex="-1"])'
)

JS_INVENTAIRE = r"""
(selecteur) => {
  const visibles = [];
  let i = 0;
  for (const el of document.querySelectorAll(selecteur)) {
    const r = el.getBoundingClientRect();
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden') continue;
    if (r.width === 0 && r.height === 0) continue;
    el.setAttribute('data-recette-idx', String(i));   // en memoire seulement
    visibles.push({idx: i, chemin: window.__chemin(el),
                   texte: (el.textContent || '').trim().slice(0, 40),
                   bordure_repos: st.borderColor,
                   fond_repos: st.backgroundColor});
    i += 1;
  }
  return visibles;
}
"""

JS_FOCUS = r"""
() => {
  const el = document.activeElement;
  if (!el || el === document.body || el.nodeType !== 1) return null;
  const st = getComputedStyle(el);
  const largeur = parseFloat(st.outlineWidth) || 0;
  const contour = st.outlineStyle !== 'none' && largeur > 0;
  const ombre = st.boxShadow && st.boxShadow !== 'none';
  const idx = el.getAttribute('data-recette-idx');
  return {
    idx: idx === null ? -1 : parseInt(idx, 10),
    chemin: window.__chemin(el),
    balise: el.tagName.toLowerCase(),
    outlineStyle: st.outlineStyle,
    outlineWidth: st.outlineWidth,
    outlineColor: st.outlineColor,
    boxShadow: ombre ? st.boxShadow.slice(0, 60) : 'none',
    bordure_focus: st.borderColor,
    fond_focus: st.backgroundColor,
    visible: !!(contour || ombre),
  };
}
"""


def main():
    sync_playwright = harnais.playwright_ou_arret()
    resultats = {}
    r_inv = {}

    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()

        for cible in harnais.PAGES_PROTOTYPE:
            page.goto(harnais.url(cible), wait_until="load", timeout=30000)
            page.evaluate(harnais.JS_FOND_EFFECTIF)
            inventaire = page.evaluate(JS_INVENTAIRE, SELECTEUR_FOCALISABLE)

            page.evaluate("() => { if (document.activeElement) "
                          "document.activeElement.blur(); }")
            atteints, etapes, sans_indicateur = set(), [], []
            hors_inventaire = 0
            # Un tour complet, plus une marge : la tabulation traverse aussi
            # des elements que l'inventaire n'a pas retenus (elle boucle).
            for _ in range(len(inventaire) + 4):
                page.keyboard.press("Tab")
                etat = page.evaluate(JS_FOCUS)
                if etat is None:
                    continue
                if etat["idx"] < 0:
                    hors_inventaire += 1
                    continue
                if etat["idx"] not in atteints:
                    etapes.append(etat)
                    if not etat["visible"]:
                        sans_indicateur.append(etat)
                atteints.add(etat["idx"])

            manques = [e for e in inventaire if e["idx"] not in atteints]
            r_inv[cible] = inventaire
            resultats[cible] = {
                "focalisables": len(inventaire),
                "atteints": len(atteints),
                "hors_inventaire": hors_inventaire,
                "manques": manques,
                "sans_indicateur": sans_indicateur,
                "exemple": etapes[0] if etapes else None,
            }
        ctx.close()
        nav.close()

    harnais.ecrire_json("clavier.json", resultats)

    print("P-40 -- parcours a la tabulation, 9 pages du prototype")
    print("")
    print("%-38s %6s %8s %9s %s" % ("page", "focal.", "atteints",
                                    "non vus", "sans indicateur"))
    total_manques = total_sans = 0
    for cible, r in resultats.items():
        total_manques += len(r["manques"])
        total_sans += len(r["sans_indicateur"])
        print("%-38s %6d %8d %9d %s" % (
            cible, r["focalisables"], r["atteints"], len(r["manques"]),
            len(r["sans_indicateur"])))
    print("")
    print("elements focalisables jamais atteints : %d" % total_manques)
    print("elements focalises sans indicateur    : %d" % total_sans)
    for cible, r in resultats.items():
        for m in r["manques"][:3]:
            print("   NON ATTEINT  %-30s %s" % (cible, m["chemin"]))
        for s in r["sans_indicateur"][:3]:
            repos = next((e for e in r_inv.get(cible, []) if e["idx"] == s["idx"]), None)
            print("   SANS CONTOUR %-30s %s" % (cible, s["chemin"]))
            print("        outline au focus : %s / %s"
                  % (s["outlineStyle"], s["outlineWidth"]))
            print("        bordure  repos   : %s"
                  % (repos["bordure_repos"] if repos else "?"))
            print("        bordure  focus   : %s" % s["bordure_focus"])
    ex = next((r["exemple"] for r in resultats.values() if r["exemple"]), None)
    if ex:
        print("")
        print("Indicateur mesure sur le premier element focalise :")
        print("   element      : %s" % ex["chemin"])
        print("   outline      : %s (%s, %s)" % (ex["outlineStyle"],
                                                 ex["outlineWidth"],
                                                 ex["outlineColor"]))
        print("   box-shadow   : %s" % ex["boxShadow"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
