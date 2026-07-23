#!/usr/bin/env python3
# -*- coding: ascii -*-
"""sonde-fontes.py -- P-29, P-30 et rendu des fontes auto-hebergees.

Le prototype avait classe P-29 et P-30 "non verifiables" parce que l'outil
`controle-glyphes.py` vit hors du depot. Chromium offre mieux que cet outil :
il dit quelle fonte a REELLEMENT compose chaque glyphe (CDP
`CSS.getPlatformFontsForNode`). On ne raisonne plus sur le repertoire declare
d'un fichier de fonte, on lit le resultat de la composition.

Methode :
  1. relever tous les caracteres non-ASCII reellement affiches par les pages ;
  2. les faire composer un a un, dans le contexte typographique du site
     (une balise par caractere, injectee EN MEMOIRE dans la page chargee) ;
  3. demander a Chromium quelle famille a compose chaque balise ;
  4. tout caractere compose par une famille hors du systeme v2 est un REPLI.

Verdicts rendus :
  P-30  "zero repli NON DECLARE" : un repli non present dans la liste P-29
        est un ECHEC nomme, caractere par caractere.
  P-29  la liste nominative de la spec est confrontee aux replis mesures :
        exhaustive ? a jour ? (un symbole liste mais jamais repli est signale
        comme perime, un repli non liste comme manquant).

Cette sonde ne modifie aucun fichier du site.
"""

import sys
import unicodedata

import harnais

# Le systeme typographique v2 (gates des 20-21/07) + la pile systeme servie
# par Windows a ce poste. Toute autre famille composant un glyphe = repli.
FAMILLES_SYSTEME_V2 = {
    "literata", "ibm plex mono", "frank ruhl libre",
    # pile d'interface (P-26, 0 octet) telle que Chromium la resout ici :
    "segoe ui", "segoe ui variable", "segoe ui variable text", "arial",
    "helvetica", "system-ui", "sans-serif", "-apple-system",
}

# Liste nominative de P-29 (SPEC-SITE-V2 v1.1, section 7.3).
# Les symboles sont ecrits en echappements \uXXXX : le script reste ASCII pur
# (regle de la squad) sans rien perdre de sa precision.
LISTE_P29 = {
    chr(0x2192): "fleche droite -- itineraire, La Chevauchee fantastique",
    chr(0x2248): "presque egal -- la riviere, Au fil de l'eau",
    chr(0x25FC): "carre plein -- armees, Waterloo",
    chr(0x2726): "etoile quatre branches -- ornement des Sources",
    chr(0x2194): "fleche double -- Les Deux Orphelines",
}

# Un temoin par role typographique du systeme v2 (P-20, P-25, P-26).
SELECTEURS_TEMOINS = [
    ("titre", "h1"),
    ("texte courant", "main p, .wrap p, article p, body > p"),
    ("menu", "nav.menu a"),
    ("cartouche (mono)", ".cartouche"),
    ("code", "code"),
]

JS_CARACTERES = r"""
() => {
  const vus = new Set();
  const marche = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = marche.nextNode())) {
    const st = getComputedStyle(n.parentElement);
    if (st.display === 'none' || st.visibility === 'hidden') continue;
    for (const c of n.nodeValue) {
      if (c.codePointAt(0) > 127) vus.add(c);
    }
  }
  return Array.from(vus);
}
"""

JS_BANC = r"""
(caracteres) => {
  // Banc d'essai injecte EN MEMOIRE : une balise par caractere, dans le
  // contexte typographique du corps de texte du site.
  const anc = document.getElementById('banc-recette');
  if (anc) anc.remove();
  const banc = document.createElement('div');
  banc.id = 'banc-recette';
  banc.style.cssText = 'position:absolute;left:-9999px;top:0;font-size:32px;';
  caracteres.forEach((c, i) => {
    const s = document.createElement('span');
    s.setAttribute('data-glyphe', String(i));
    s.textContent = c;
    banc.appendChild(s);
  });
  document.body.appendChild(banc);
  banc.getBoundingClientRect();          // force la composition
  return caracteres.length;
}
"""

# Contre-epreuve de l'hebreu (spec 7.2). Si un caractere hebreu ne compose pas
# en Frank Ruhl Libre dans le contexte du site mais y compose des qu'on NOMME
# la famille, alors le fichier de fonte est sain et c'est le CHAINAGE qui
# manque -- deux causes tres differentes, qu'un verdict doit distinguer.
JS_BANC_NOMME = r"""
(essais) => {
  const anc = document.getElementById('banc-nomme');
  if (anc) anc.remove();
  const banc = document.createElement('div');
  banc.id = 'banc-nomme';
  banc.style.cssText = 'position:absolute;left:-9999px;top:0;font-size:32px;';
  essais.forEach((e, i) => {
    const s = document.createElement('span');
    s.setAttribute('data-nomme', String(i));
    s.style.fontFamily = e.famille;
    s.textContent = e.caractere;
    banc.appendChild(s);
  });
  document.body.appendChild(banc);
  banc.getBoundingClientRect();
  return essais.length;
}
"""


def nom_unicode(c):
    try:
        return unicodedata.name(c)
    except ValueError:
        return "U+%04X" % ord(c)


def main():
    sync_playwright = harnais.playwright_ou_arret()
    caracteres = set()
    par_page = {}
    fontes_page = {}

    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        cdp = ctx.new_cdp_session(page)
        cdp.send("DOM.enable")
        cdp.send("CSS.enable")

        # 1. Inventaire des caracteres non-ASCII reellement affiches.
        for cible in harnais.pages_toutes():
            page.goto(harnais.url(cible), wait_until="load", timeout=30000)
            page.wait_for_timeout(120)
            vus = page.evaluate(JS_CARACTERES)
            par_page[cible] = vus
            if cible in harnais.PAGES_PROTOTYPE:
                caracteres.update(vus)
                # `CSS.getPlatformFontsForNode` ne rend que les fontes des
                # noeuds texte ENFANTS DIRECTS du noeud interroge : interroger
                # `body` ne dit presque rien (et rien du tout sur une page
                # dont le corps n'a que des blocs). On interroge donc des
                # elements TEMOINS, un par role typographique.
                doc = cdp.send("DOM.getDocument", {"depth": 1})
                temoins = {}
                for role, sel in SELECTEURS_TEMOINS:
                    trouve = cdp.send("DOM.querySelector", {
                        "nodeId": doc["root"]["nodeId"], "selector": sel})
                    if not trouve.get("nodeId"):
                        continue
                    fontes = cdp.send("CSS.getPlatformFontsForNode",
                                      {"nodeId": trouve["nodeId"]})
                    noms = sorted(((f["familyName"], f["glyphCount"])
                                   for f in fontes.get("fonts", [])
                                   if f.get("glyphCount")), key=lambda x: -x[1])
                    if not noms:
                        continue
                    # La famille DEMANDEE par la feuille : sans elle, on ne
                    # peut pas distinguer "la fonte n'a pas charge" (defaut)
                    # de "la page demandait la pile systeme" (conforme).
                    demandee = page.evaluate(
                        "(sel) => { const e = document.querySelector(sel);"
                        " return e ? getComputedStyle(e).fontFamily : null; }",
                        sel)
                    temoins[role] = {"composee": noms, "demandee": demandee}
                fontes_page[cible] = temoins

        # 2. Banc d'essai, caractere par caractere, sur une page v2.
        # On eprouve les caracteres des 9 pages du prototype (perimetre du
        # verdict) ET ceux des 30 pages non migrees (informatif) : c'est
        # exactement le jeu que le retrofit de 065-5 fera passer dans ce
        # meme systeme typographique.
        tous = set()
        for v in par_page.values():
            tous.update(v)
        liste = sorted(tous)
        page.goto(harnais.url("index.html"), wait_until="load", timeout=30000)
        page.evaluate(JS_BANC, liste)
        page.wait_for_timeout(200)

        doc = cdp.send("DOM.getDocument", {"depth": -1})
        noeuds = cdp.send("DOM.querySelectorAll", {
            "nodeId": doc["root"]["nodeId"], "selector": "span[data-glyphe]"})

        composition = {}
        for i, node_id in enumerate(noeuds["nodeIds"]):
            fontes = cdp.send("CSS.getPlatformFontsForNode", {"nodeId": node_id})
            noms = [f["familyName"] for f in fontes.get("fonts", [])
                    if f.get("glyphCount")]
            composition[liste[i]] = noms

        # Contre-epreuve : les memes caracteres, famille NOMMEE explicitement.
        essais = [{"caractere": chr(0x05D0), "famille": "'Frank Ruhl Libre'"},
                  {"caractere": chr(0x05EA), "famille": "'Frank Ruhl Libre'"},
                  {"caractere": chr(0x0410), "famille": "'Literata'"}]
        polices_vues = []
        page.on("request", lambda r: polices_vues.append(r.url)
                if r.resource_type == "font" else None)
        page.evaluate(JS_BANC_NOMME, essais)
        page.wait_for_timeout(500)

        doc2 = cdp.send("DOM.getDocument", {"depth": -1})
        n2 = cdp.send("DOM.querySelectorAll", {
            "nodeId": doc2["root"]["nodeId"], "selector": "span[data-nomme]"})
        contre_epreuve = []
        for i, node_id in enumerate(n2["nodeIds"]):
            fontes = cdp.send("CSS.getPlatformFontsForNode", {"nodeId": node_id})
            contre_epreuve.append({
                "caractere": "U+%04X" % ord(essais[i]["caractere"]),
                "famille_demandee": essais[i]["famille"],
                "famille_composee": [f["familyName"] for f in fontes.get("fonts", [])
                                     if f.get("glyphCount")],
            })

        ctx.close()
        nav.close()

    replis = {}
    for c, noms in composition.items():
        hors = [n for n in noms if n.strip().lower() not in FAMILLES_SYSTEME_V2]
        if hors or not noms:
            replis[c] = noms
    replis_proto = {c: v for c, v in replis.items() if c in caracteres}

    harnais.ecrire_json("fontes.json", {
        "caracteres_prototype": sorted(caracteres),
        "composition": {("U+%04X" % ord(c)): v for c, v in composition.items()},
        "replis": {("U+%04X" % ord(c)): v for c, v in replis.items()},
        "fontes_par_page": fontes_page,
        "contre_epreuve": contre_epreuve,
        "polices_contre_epreuve": sorted(set(polices_vues)),
        "caracteres_par_page": {k: sorted(v) for k, v in par_page.items()},
    })

    print("Fontes DEMANDEES par la feuille et fontes qui ont REELLEMENT compose")
    for cible, temoins in fontes_page.items():
        print("  %s" % cible)
        for role, bloc in temoins.items():
            composee = ", ".join("%s (%d)" % (n, g) for n, g in bloc["composee"])
            demandee = (bloc["demandee"] or "?").split(",")[0].strip()
            tete = composee.split(" (")[0]
            accord = "conforme" if tete.lower().strip("'\"") in \
                demandee.lower().strip("'\"") or demandee.lower().startswith(
                    ("system-ui", "-apple-system")) else "A VERIFIER"
            print("      %-18s demandee %-16s composee %-28s %s"
                  % (role, demandee, composee, accord))

    print("")
    print("== Contre-epreuve : la famille nommee explicitement ==")
    for e in contre_epreuve:
        print("   %s demande %-22s compose par %s"
              % (e["caractere"], e["famille_demandee"],
                 ", ".join(e["famille_composee"]) or "(aucune)"))
    print("   fichiers de fonte demandes pendant la contre-epreuve : %s"
          % (", ".join(u.rsplit("/", 1)[-1] for u in sorted(set(polices_vues)))
             or "aucun"))

    print("")
    print("Caracteres non-ASCII composes : %d (dont %d affiches par les 9 "
          "pages du prototype)" % (len(composition), len(caracteres)))
    print("")
    print("== P-30 : zero repli NON DECLARE (perimetre : les 9 pages) ==")
    non_declares = [c for c in replis_proto if c not in LISTE_P29]
    print("  caracteres en repli mesure : %d" % len(replis_proto))
    for c in sorted(replis_proto):
        etat = "DECLARE P-29" if c in LISTE_P29 else "NON DECLARE"
        print("     U+%04X %-34s compose par %-24s %s"
              % (ord(c), nom_unicode(c)[:34],
                 ", ".join(replis_proto[c]) or "(aucune)", etat))
    print("  VERDICT P-30 : %s" % ("OK -- aucun repli non declare"
                                   if not non_declares else
                                   "ECART -- %d repli(s) non declare(s)"
                                   % len(non_declares)))

    print("")
    print("== P-29 : la liste nominative est-elle exhaustive et a jour ? ==")
    print("  symboles listes par la spec : %d" % len(LISTE_P29))
    for c, note in sorted(LISTE_P29.items()):
        ou = "prototype" if c in caracteres else (
            "corpus (page non migree)" if c in composition else "ABSENT DU DEPOT")
        etat = "en repli" if c in replis else "compose sans repli"
        print("     U+%04X %-46s %-24s %s" % (ord(c), note, ou, etat))

    print("")
    print("== Informatif pour 065-5 : tout le corpus dans le systeme v2 ==")
    hors_proto = {c: v for c, v in replis.items() if c not in caracteres}
    print("  replis mesures sur les 30 pages non migrees : %d" % len(hors_proto))
    for c in sorted(hors_proto):
        etat = "DECLARE P-29" if c in LISTE_P29 else "NON DECLARE -- a lister"
        pages = [p for p, v in par_page.items() if c in v]
        print("     U+%04X %-30s %-22s %s  (%d page(s) : %s)"
              % (ord(c), nom_unicode(c)[:30],
                 ", ".join(hors_proto[c]) or "(aucune)", etat,
                 len(pages), ", ".join(p.split("/")[-1] for p in pages[:3])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
