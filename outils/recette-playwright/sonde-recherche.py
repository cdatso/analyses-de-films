#!/usr/bin/env python3
# -*- coding: ascii -*-
"""sonde-recherche.py -- P-41 confirmee au moteur reel.

Le prototype avait mesure P-41 hors navigateur composant (erratum 1 du
22/07 08h40 : une mesure de temps n'exige aucune geometrie). Le mandat
demande de la CONFIRMER au moteur reel -- une ligne deja verdictee ne se
reprend pas sur parole.

Cycle mesure : frappe -> filtrage -> rendu. L'evenement `input` est
distribue de facon SYNCHRONE ; l'ecouteur de `corpus.js` s'execute donc
entierement pendant `dispatchEvent`, et l'encadrer par `performance.now()`
mesure bien le cycle complet, rendu du DOM inclus.

Deux jeux, ceux que P-41 nomme :
  - le corpus REEL servi par la page ;
  - un jeu SYNTHETIQUE de 500 entrees (le plafond de la prescription),
    injecte en memoire avant montage -- le registre du depot n'est pas
    touche.

Cette sonde ne modifie aucun fichier du site.
"""

import sys

import harnais

SEUIL_MS = 100.0
REQUETES = ["a", "pan", "dora", "ren", "1954", "zzzz", ""]

JS_MESURE = r"""
(requetes) => {
  const champ = document.getElementById('q');
  if (!champ) return {erreur: 'champ de recherche absent'};
  const liste = document.getElementById('liste');
  const mesures = [];
  for (const r of requetes) {
    champ.value = r;
    const t0 = performance.now();
    champ.dispatchEvent(new Event('input', {bubbles: true}));
    const t1 = performance.now();
    mesures.push({
      requete: r,
      ms: t1 - t0,
      resultats: liste ? liste.children.length : -1,
    });
  }
  return {mesures: mesures, entrees: window.__corpusMonte || FILMS.length};
}
"""

# `films-data.js` declare `const FILMS` : la liaison existe dans la portee
# globale mais N'EST PAS une propriete de `window` (const/let ne le sont
# jamais). La premiere version de cette sonde lisait `window.FILMS`, donc
# zero entree, et son jeu de 500 n'a jamais ete monte -- defaut de la sonde,
# corrige : on lit l'identifiant nu et on remonte sur un corpus passe en
# argument, sans jamais reaffecter la constante.
JS_GONFLE = r"""
(cible) => {
  const base = FILMS;
  if (!base || !base.length) return {erreur: 'FILMS absent'};
  const gonfle = [];
  let i = 0;
  while (gonfle.length < cible) {
    const f = Object.assign({}, base[i % base.length]);
    f.title = f.title + ' [' + gonfle.length + ']';
    f.slug = (f.slug || 'x') + '-' + gonfle.length;
    gonfle.push(f);
    i += 1;
  }
  // Les ecouteurs du premier montage sont retires en remplacant les noeuds
  // par leur clone : sans cela, deux montages repondraient a chaque frappe
  // et la mesure porterait sur autre chose que le site.
  for (const id of ['q', 'facettes']) {
    const el = document.getElementById(id);
    if (el) el.parentNode.replaceChild(el.cloneNode(true), el);
  }
  document.getElementById('liste').innerHTML = '';
  Corpus.monte({films: gonfle, volet: 'critique', liste: 'liste',
                compte: 'compte', recherche: 'q', facettes: 'facettes'});
  window.__corpusMonte = gonfle.length;
  return {entrees: gonfle.length,
          rendus: document.getElementById('liste').children.length};
}
"""


def main():
    sync_playwright = harnais.playwright_ou_arret()
    resultats = {}
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()

        page.goto(harnais.url("critiques.html"), wait_until="load", timeout=30000)
        resultats["corpus_reel"] = page.evaluate(JS_MESURE, REQUETES)

        gonflage = page.evaluate(JS_GONFLE, 500)
        resultats["gonflage"] = gonflage
        resultats["corpus_500"] = page.evaluate(JS_MESURE, REQUETES)

        ctx.close()
        nav.close()

    harnais.ecrire_json("recherche.json", resultats)

    print("P-41 -- cycle frappe/filtrage/rendu, mesure au moteur reel")
    print("seuil : %.0f ms jusqu'a 500 entrees" % SEUIL_MS)
    pire = 0.0
    for jeu in ("corpus_reel", "corpus_500"):
        bloc = resultats[jeu]
        if "erreur" in bloc:
            print("  %s : ECHEC %s" % (jeu, bloc["erreur"]))
            continue
        print("")
        print("  %s -- %d entrees" % (jeu, bloc["entrees"]))
        print("    %-10s %10s %10s" % ("requete", "ms", "resultats"))
        for m in bloc["mesures"]:
            pire = max(pire, m["ms"])
            print("    %-10s %10.3f %10d"
                  % (repr(m["requete"]), m["ms"], m["resultats"]))
    print("")
    print("pire mesure toutes requetes confondues : %.3f ms (%.1f %% du seuil)"
          % (pire, 100.0 * pire / SEUIL_MS))
    print("verdict : %s" % ("OK" if pire < SEUIL_MS else "ECART"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
