#!/usr/bin/env python3
# -*- coding: ascii -*-
"""sonde-contraste.py -- P-39 rejoue au RENDU REEL.

Ce que l'outil statique (`outils/controle-contraste.py`) ne pouvait pas faire,
et pourquoi cette sonde existe. Le comptage du prototype lisait le CSS SANS
arbre de document : il ne savait pas sur quel fond un texte se pose vraiment.
Il a donc distingue deux classes, en assumant de sous-estimer :
    E1 (23) -- couple ecrit dans la meme regle : ECART CERTAIN ;
    E2 (48) -- couleur en echec sur TOUS les fonds declares : ECART PROBABLE.
Chromium compose : le fond effectif d'un element se lit en remontant ses
ancetres, la taille et la graisse reelles donnent le seuil applicable, et une
regle qui ne s'applique a aucun element rendu se voit.

Deux passes, volontairement independantes :
  RECONCILIATION -- chacun des 71 ecarts declares est retrouve par son
      selecteur dans la page rendue, puis CONFIRME ou ECARTE sur mesure.
  RECENSEMENT    -- balayage complet et independant de tous les textes
      rendus des 34 pages. C'est lui qui fait le tableau DEFINITIF : il
      voit aussi ce que l'outil statique ne pouvait pas voir.

La sonde COMPTE. Elle ne corrige aucune palette : chaque ligne est un
arbitrage d'AH en 065-5.
"""

import os
import re
import sys

import harnais

SEUIL_COURANT = 4.5
SEUIL_GRAND = 3.0

RE_TITRE = re.compile(r"^### (\S+\.html)\s*$")
RE_LIGNE = re.compile(
    r"^\|\s*\*\*(E[12])\*\*\s*\|\s*`([^`]*)`\s*\|\s*`([^`]*)`\s*\|"
    r"\s*`([^`]*)`\s*\|\s*\*\*([0-9.]+)\*\*\s*\|\s*([0-9.]+)")

JS_RECENSEMENT = r"""
(seuils) => {
  const lignes = [];
  const vus = new Set();
  for (const el of document.querySelectorAll('*')) {
    // Seuls les elements portant DIRECTEMENT du texte visible comptent :
    // sinon un conteneur herite du texte de ses enfants et on compte deux fois.
    let propre = '';
    for (const n of el.childNodes) {
      if (n.nodeType === 3) propre += n.nodeValue;
    }
    if (!propre.trim()) continue;
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden') continue;
    if (el.closest('[aria-hidden="true"]')) continue;   // non restitue
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    // Texte sorti du cadre (technique de masquage) : il n'est pas lu a l'ecran.
    if (r.right < 0 || r.bottom < 0 || r.left > 5000) continue;

    // Opacite EFFECTIVE : le produit de celles de l'element et de ses
    // ancetres. Un texte a 0.6 d'opacite n'a pas le contraste de sa couleur
    // nominale -- l'ignorer surestimerait le ratio.
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

    const px = parseFloat(st.fontSize) || 16;
    const poids = parseInt(st.fontWeight, 10) || 400;
    const grand = px >= 24 || (px >= 18.66 && poids >= 700);
    const seuil = grand ? seuils.grand : seuils.courant;

    // Pire et meilleur cas sur l'ensemble des fonds possibles.
    const cand = window.__fondsCandidats(el);
    let pire = Infinity, meilleur = -Infinity, fondPire = fond;
    for (const f of cand.fonds) {
      const r2 = window.__ratio(texte, f);
      if (r2 < pire) { pire = r2; fondPire = f; }
      if (r2 > meilleur) meilleur = r2;
    }

    const cle = window.__hex(texte) + '|' + window.__hex(fondPire) + '|' + seuil
                + '|' + el.tagName + '|' + (el.className || '');
    if (vus.has(cle)) continue;
    vus.add(cle);

    if (pire < seuil) {
      lignes.push({
        chemin: window.__chemin(el),
        texte: window.__hex(texte),
        fond: window.__hex(fondPire),
        ratio: Math.round(pire * 100) / 100,
        ratio_meilleur: Math.round(meilleur * 100) / 100,
        degrade: cand.degrade,
        // Sur un fond non uniforme, un texte peut passer sur une zone du
        // degrade et echouer sur une autre : le verdict n'est pas binaire.
        partiel: cand.degrade && meilleur >= seuil,
        seuil: seuil,
        px: Math.round(px * 10) / 10,
        poids: poids,
        opacite: Math.round(opacite * 100) / 100,
        classe: (typeof el.className === 'string' ? el.className : '') || '',
        extrait: propre.trim().slice(0, 45),
      });
    }
  }
  lignes.sort((a, b) => a.ratio - b.ratio);
  return lignes;
}
"""

JS_SELECTEUR = r"""
(args) => {
  const {selecteur, seuils} = args;
  let els;
  try { els = document.querySelectorAll(selecteur); }
  catch (e) { return {erreur: 'selecteur invalide'}; }
  if (!els.length) return {trouves: 0, cas: []};
  const cas = [];
  for (const el of els) {
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden') continue;
    const fond = window.__fondEffectif(el);
    const brut = window.__lireRgba(st.color);
    if (!brut) continue;
    const texte = brut.a >= 0.999 ? brut : window.__composer(brut, fond);
    const px = parseFloat(st.fontSize) || 16;
    const poids = parseInt(st.fontWeight, 10) || 400;
    const grand = px >= 24 || (px >= 18.66 && poids >= 700);
    const seuil = grand ? seuils.grand : seuils.courant;
    const ratio = window.__ratio(texte, fond);
    let propre = '';
    for (const n of el.childNodes) { if (n.nodeType === 3) propre += n.nodeValue; }
    cas.push({
      texte: window.__hex(texte), fond: window.__hex(fond),
      ratio: Math.round(ratio * 100) / 100, seuil: seuil,
      px: Math.round(px * 10) / 10, poids: poids,
      porte_du_texte: !!propre.trim(),
      echoue: ratio < seuil,
    });
  }
  return {trouves: els.length, cas: cas};
}
"""


def lit_ecarts_declares():
    """Relit le detail de outils/contraste-sortie.md (les 23 E1 + 48 E2)."""
    chemin = os.path.join(harnais.DEPOT, "outils", "contraste-sortie.md")
    assert os.path.isfile(chemin), "contraste-sortie.md introuvable"
    ecarts, page = [], None
    with open(chemin, "r", encoding="utf-8") as f:
        for ligne in f:
            t = RE_TITRE.match(ligne.strip())
            if t:
                page = t.group(1)
                continue
            m = RE_LIGNE.match(ligne.strip())
            if m and page:
                ecarts.append({
                    "page": page, "classe": m.group(1), "selecteur": m.group(2),
                    "texte": m.group(3), "fond": m.group(4),
                    "ratio_statique": float(m.group(5)),
                    "seuil": float(m.group(6)),
                })
    return ecarts


def chemin_page(nom):
    return nom if nom == "index.html" else "films/" + nom


def main():
    seuils = {"courant": SEUIL_COURANT, "grand": SEUIL_GRAND}
    declares = lit_ecarts_declares()
    e1 = [e for e in declares if e["classe"] == "E1"]
    e2 = [e for e in declares if e["classe"] == "E2"]
    print("Ecarts declares relus dans contraste-sortie.md : %d (E1 %d, E2 %d)"
          % (len(declares), len(e1), len(e2)))
    if (len(e1), len(e2)) != (23, 48):
        print("  ATTENTION : le comptage relu ne vaut pas 23/48 -- "
              "la reconciliation porterait sur un autre jeu.")

    # Le recensement porte sur TOUT le perimetre de l'outil statique -- les
    # 33 pages d'analyse plus l'accueil -- et non sur les seules pages ou un
    # ecart avait deja ete declare : sinon il ne pourrait rien decouvrir.
    pages = sorted([p.split("/")[-1] for p in harnais.pages_films()]
                   + ["index.html"])
    recensement = {}

    sync_playwright = harnais.playwright_ou_arret()
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()

        # --- Passe 1 : reconciliation des ecarts declares.
        for e in declares:
            cible = chemin_page(e["page"])
            page.goto(harnais.url(cible), wait_until="load", timeout=30000)
            page.evaluate(harnais.JS_FOND_EFFECTIF)
            r = page.evaluate(JS_SELECTEUR,
                              {"selecteur": e["selecteur"], "seuils": seuils})
            e.update(r)
            if r.get("erreur"):
                e["verdict"] = "INDETERMINE"
            elif r["trouves"] == 0:
                e["verdict"] = "ECARTE (regle sans element rendu)"
            else:
                echecs = [c for c in r["cas"] if c["echoue"] and c["porte_du_texte"]]
                if echecs:
                    e["verdict"] = "CONFIRME"
                    e["ratio_reel"] = min(c["ratio"] for c in echecs)
                    e["fond_reel"] = echecs[0]["fond"]
                    e["texte_reel"] = echecs[0]["texte"]
                else:
                    sans_texte = all(not c["porte_du_texte"] for c in r["cas"])
                    e["verdict"] = ("ECARTE (aucun texte porte par la regle)"
                                    if sans_texte else
                                    "ECARTE (passe au rendu reel)")
                    if r["cas"]:
                        e["ratio_reel"] = max(c["ratio"] for c in r["cas"])

        # --- Passe 2 : recensement independant.
        for nom in pages:
            cible = chemin_page(nom)
            page.goto(harnais.url(cible), wait_until="load", timeout=30000)
            page.evaluate(harnais.JS_FOND_EFFECTIF)
            page.wait_for_timeout(120)
            recensement[nom] = page.evaluate(JS_RECENSEMENT, seuils)

        ctx.close()
        nav.close()

    harnais.ecrire_json("contraste.json", {"declares": declares,
                                           "recensement": recensement})

    def compte(lst, v):
        return len([e for e in lst if e["verdict"].startswith(v)])

    print("")
    print("== PASSE 1 : reconciliation des %d ecarts declares ==" % len(declares))
    for classe, lst in (("E1 (certains)", e1), ("E2 (probables)", e2)):
        print("  %-16s CONFIRMES %2d   ECARTES %2d   INDETERMINES %2d"
              % (classe, compte(lst, "CONFIRME"), compte(lst, "ECARTE"),
                 compte(lst, "INDETERMINE")))

    print("")
    print("== PASSE 2 : recensement independant au rendu reel ==")
    total = sum(len(v) for v in recensement.values())
    en_echec = [p for p, v in recensement.items() if v]
    print("  pages balayees                 : %d" % len(recensement))
    print("  couples sous le seuil (mesures): %d" % total)
    print("  pages concernees               : %d / %d" % (len(en_echec), len(recensement)))
    print("")
    print("  %-34s %s" % ("page", "couples sous le seuil"))
    for nom in sorted(recensement, key=lambda n: -len(recensement[n])):
        if recensement[nom]:
            print("    %-32s %d" % (nom, len(recensement[nom])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
