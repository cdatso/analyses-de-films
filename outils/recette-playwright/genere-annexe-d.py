#!/usr/bin/env python3
# -*- coding: ascii -*-
"""genere-annexe-d.py -- annexe D COMPLETE de la recette (BKL-065-4-recette).

Le comptage est MECANIQUE : les 52 lignes sont des donnees, le total est
calcule, et le document refuse de s'ecrire s'il ne porte pas exactement 52
lignes ou s'il reste un verdict "NV". C'est la lecon de P-42 appliquee a
l'outil lui-meme -- une checklist qui s'auto-compte ne peut pas mentir sur
son propre remplissage.

Colonne SOURCE, ajoutee par cette recette : elle dit QUI a etabli le verdict.
  [R] recette 065-4 -- mesure prise dans Chromium par les sondes de ce dossier ;
  [P] prototype 065-3 -- verdict repris tel quel, non rejoue ici.
Sans elle, un lecteur croirait que la recette a tout remesure : elle a
remesure ce que le prototype ne pouvait pas mesurer, et ce qui en dependait.

Usage : python genere-annexe-d.py [--sortie CHEMIN]
"""

import argparse
import os
import sys

import harnais

DATE = "22/07/2026"

OK, LOT, ECART, HP = "OK", "OK / lot", "ECART", "HP"

# (numero, intitule abrege, verdict, source, preuve/motif)
LIGNES = [
 ("P-01", "Un seul dossier `films/` pour les deux volets", OK, "P",
  "aucun dossier nomme d'apres un volet ; `films/` porte l'Etude et les 32 Critiques"),
 ("P-02", "Menu partout, un seul `aria-current`", LOT, "P",
  "9 pages sur 9 : exactement 1 `aria-current=\"page\"` ; les 30 pages non migrees n'ont pas de menu"),
 ("P-03", "Lien vers la variante, qualifie par son volet", OK, "R",
  "sonde-liens : les 2 liens du diptyque resolus en 200, aucun lien mort, le libelle porte le volet"),
 ("P-04", "L'accueil ne liste le corpus qu'une fois", OK, "P",
  "un seul `<ol class=\"liste\">` ; la grille d'affiches de la v1 a disparu"),
 ("P-05", "Pas de formulaire sur l'accueil", OK, "P",
  "`grep '<form'` sur `index.html` = 0 ; le formulaire vit sur `demander-une-analyse.html`"),
 ("P-06", "Objet en une = derniere publiee, a egalite titre decroissant", OK, "P",
  "tri `(datePublication, title)` dans `corpus.js` ; reserve : 3 entrees portent le champ (065-5)"),
 ("P-51", "Jamais d'entree qui ne soit la derniere ou sa variante", OK, "P",
  "instrument `outils/observation-C2-carte-seule.html`, cas A : 1 carte, classe `bloc-une` sans `couple`"),
 ("P-07", "Volets jamais a parite visuelle ; vues filtrees", OK, "P",
  "`critiques.html` et `etudes.html` appellent `Corpus.monte()` avec le seul parametre `volet`"),
 ("P-08", "Aucune facette derivee des pages", OK, "P",
  "`corpus.js` ne lit que `FILMS` ; aucun acces a `films/`"),
 ("P-09", "Vocabulaires fermes, fichier versionne dedie", OK, "P",
  "`assets/vocabulaires.js`, commite ; 5 axes (volet, genreBase, technique, pays, courant)"),
 ("P-10", "Valeur hors vocabulaire = publication bloquee", OK, "P",
  "`controle-vocabulaires.py --autotest` : valeur inventee rejetee, code de sortie 1, depot non modifie"),
 ("P-11", "Le skill choisit et n'invente pas", HP, "P",
  "l'adaptation du skill est le perimetre de 065-5"),
 ("P-12", "Ajout de terme = commit propre", OK, "P",
  "aucun commit ne mele ajout de terme et publication d'analyse"),
 ("P-13", "Facette affichee si >= 3 valeurs, <= 80 % et couverture >= 50 %", ECART, "P",
  "ECART DU PROTOTYPE, arbitre depuis : le seuil de couverture a ete AJOUTE a P-13 en"
  " v1.1 (E-3, gate 11h54). Le prototype implemente encore la regle SANS seuil --"
  " `Pays` s'affiche a 3 entrees / 33. La mise en conformite est 065-5"),
 ("P-52", "Le volet est exempte de P-13", OK, "P",
  "volet affiche malgre 32/33 sur une valeur (97 %)"),
 ("P-14", "Trois formulations invariantes", LOT, "P",
  "2 des 3 regimes ont un exemplaire (R1 x2, R3 x1) ; R2 n'aura d'instance qu'a la 1re publication v2"),
 ("P-15", "Cartouche sur toute page d'analyse", LOT, "P",
  "3/3 des pages migrees ; aucun cartouche ne laisse le modele implicite"),
 ("P-16", "Cartouche = composant unique", OK, "P",
  "aucune page migree ne restyle `.cartouche`. Collision de noms signalee : `waterloo.html` (065-5)"),
 ("P-17", "Registre et cartouche portent la meme information", LOT, "P",
  "3/3 : `producteur` du registre repris mot pour mot dans le cartouche"),
 ("P-18", "`producteur` obligatoire pour toute entree", ECART, "P",
  "7 entrees sur 33 le portent. Retro-remplissage = 065-5"),
 ("P-19", "Provenance hors squad nommee", OK, "P",
  "`pandora-contrechamp.html` : premier jet OpenAI GPT-5.5, repris et enrichi par la squad"),
 ("P-20", "Aucune famille propre en page", LOT, "R",
  "sonde-fontes : sur les 3 pages migrees, les temoins composent en Literata et IBM Plex Mono,"
  " familles du systeme partage ; 29 des 30 pages restantes chargent encore leurs propres familles"),
 ("P-21", "Marqueur invariant en forme, couleur locale", OK, "R",
  "sonde-gris, styles calcules : Critique `solid 1px`, Etude `double 3px`, tous deux en"
  " `currentColor`, sur 2 palettes opposees. Le critere amende en v1.1 (E-4 : 2 palettes"
  " et non 3) est SATISFAIT -- la ligne quitte l'ecart du prototype"),
 ("P-22", "La distinction ne repose jamais sur la seule couleur", OK, "R",
  "DEUX preuves : forme differente aux styles calcules (style ET epaisseur de filet), et"
  " captures en niveaux de gris des deux cartouches (`gris-cartouche-*.png`) ou la"
  " distinction reste lisible. Le volet 'non verifiable' du prototype est leve"),
 ("P-23", "`--volet` declaree une fois par volet", OK, "P",
  "2 declarations dans `mobilier.css` ; `grep '--volet:'` dans `films/` = 0"),
 ("P-24", "Aucune requete vers un domaine tiers", LOT, "R",
  "journal reseau Chromium, cache froid, 39 pages : **0 requete tierce sur les 9 pages du"
  " prototype**. Informatif : 170 requetes tierces sur 29 des 30 pages non migrees"
  " (Google Fonts) -- perimetre du retrofit 065-5"),
 ("P-25", "Fontes auto-hebergees + licences embarquees", OK, "R",
  "15 `.woff2` servis, 0 manquant au journal reseau ; 3 licences OFL. SIGNALEMENT : les 2"
  " fichiers Frank Ruhl Libre ne sont atteignables par aucune page -- voir P-27"),
 ("P-26", "Titrage et texte sur la meme famille", OK, "R",
  "sonde-fontes : la ou la feuille demande Literata, c'est Literata qui compose (titre ET"
  " texte). La ou un temoin compose en Segoe UI, la feuille demandait `system-ui` : c'est"
  " la pile d'interface, conforme au systeme a trois familles"),
 ("P-27", "`unicode-range` restreint pour les non-latines", OK, "R",
  "journal reseau : aucune fonte non latine telechargee sur les 9 pages du prototype, le"
  " critere est satisfait. SIGNALEMENT dont la portee depasse P-27 : la contre-epreuve"
  " montre que `Frank Ruhl Libre` compose l'hebreu et se telecharge DES QU'ON LA NOMME --"
  " or AUCUNE pile `font-family` ne la nomme (`--serif` = Literata, Georgia, Times New"
  " Roman, serif). L'hebreu de `le-golem` tombera donc en repli Times New Roman au"
  " retrofit. Le fichier est sain, le CHAINAGE manque : a traiter en 065-5"),
 ("P-28", "Mobilier sans glyphe de fonte", LOT, "R",
  "sonde-fontes : 0 occurrence de U+2190 sur les 3 pages migrees, chevron CSS en place ;"
  " U+2190 subsiste sur les 30 pages non migrees (065-5)"),
 ("P-29", "Symboles bespoke listes nominativement", OK, "R",
  "**la ligne quitte 'non verifiable'.** Composition reelle mesuree glyphe par glyphe"
  " (CDP `CSS.getPlatformFontsForNode`) : sur les 9 pages du prototype, 1 seul repli,"
  " U+2192, ET IL EST LISTE. La liste est donc exhaustive sur ce perimetre."
  " SIGNALEMENT pour 065-5 : sur les 30 pages non migrees, 4 replis ne sont PAS listes --"
  " U+2190 (30 pages), U+25C6 (`le-samourai`), et 3 lettres hebraiques (`le-golem`)"),
 ("P-30", "Zero repli NON DECLARE", OK, "R",
  "**la ligne quitte 'non verifiable'.** Perimetre des 9 pages du prototype : 1 repli"
  " mesure, declare. Aucun repli non declare. Methode superieure a celle qu'annoncait la"
  " spec : on ne confronte plus les caracteres au repertoire suppose d'un fichier de"
  " fonte, on lit la famille qui a REELLEMENT compose chaque glyphe"),
 ("P-31", "Aucune etape de compilation", OK, "P",
  "0 manifeste de paquets, 0 configuration de bundler ; les outils Python lisent et rapportent"),
 ("P-32", "Aucun URL publie ne casse", OK, "R",
  "**la ligne quitte 'non verifiable'.** Sur la maquette locale : 39/39 documents en 200,"
  " 625 cibles internes distinctes demandees, **0 lien mort et 0 ancre morte** sur 2 086"
  " liens releves dans le DOM rendu. Annexe A regeneree : **34 URLs** (contre 33 listes"
  " dans la spec) -- l'arbitrage E-1 est confirme sur mesure. LIMITE DECLAREE : le site"
  " PUBLIE porte encore la v1 ; le controle des URLs publics appartient a la bascule 065-5"),
 ("P-33", "Liens relatifs, aucune URL absolue", OK, "R",
  "`grep 'cdatso.be'` sur tout le depot = 0, et les 625 cibles internes resolues par le"
  " navigateur pointent toutes vers l'hote local -- aucune n'est absolue"),
 ("P-34", "Recette mecanisee par Playwright", OK, "R",
  "**la ligne quitte 'hors perimetre'.** Playwright 1.61.0 + Chromium 149 installes le"
  " 22/07 (gate R4, BKL-069 en PROD) ; la presente recette EST leur mise en oeuvre :"
  " 8 sondes rejouables dans `outils/recette-playwright/`"),
 ("P-35", "HTML <= 60 Ko", OK, "P",
  "maximum du corpus : 46,7 Kio"),
 ("P-36", "Affiche <= 300 Ko", ECART, "P",
  "5 affiches depassent (maximum `pandora.jpg` a 1 660 Kio). Recompression = 065-5."
  " La recette en mesure la consequence directe : voir P-37"),
 ("P-37", "Page <= 900 Ko a la 1re visite, 400 ensuite", ECART, "R",
  "**la ligne quitte 'non verifiable'.** Journal reseau, protocole isole (un contexte"
  " neuf par mesure). 7 pages sur 9 conformes. **2 pages en ecart, les deux du diptyque** :"
  " `pandora.html` et `pandora-contrechamp.html` a **1 937 Ko** en 1re visite (seuil 900)"
  " et **1 743 Ko** en visite suivante (seuil 400). Cause unique et mesuree :"
  " `pandora.jpg`, 1 660 Ko -- c'est P-36 qui produit P-37. Temoin : `rouges-et-blancs`,"
  " affiche de 36 Ko, tient a 392 / 198 Ko"),
 ("P-38", "Aucun defilement horizontal a 320 px", ECART, "R",
  "**la ligne quitte 'non verifiable' -- `clientWidth` vaut bien 320.** 39 pages mesurees"
  " a 320, 375 et 768 px. A 768 px : aucune page en defaut. A 320 px : **1 page du"
  " prototype en ecart**, `pandora-contrechamp.html`, +18 px, element nomme"
  " `section#sources > div.note > code` -- le nom de fichier"
  " `sources_pandora_analyse_haute.txt` en chasse fixe, insecable, 292 px de large."
  " 3 pages non migrees debordent aussi (`hamnet` +262, `hitchcock-truffaut` +100,"
  " `persona` +34) : perimetre 065-5"),
 ("P-39", "Contraste AA 4,5:1 / 3:1", ECART, "R",
  "comptage REJOUE aux styles calcules. Les 71 ecarts declares par le prototype sont"
  " confrontes un a un : **48 CONFIRMES** (17 des 23 certains, 31 des 48 probables) et"
  " **23 ECARTES** (regle sans element rendu, ou sans texte, ou qui passe reellement)."
  " Recensement independant des 34 pages : **221 couples sous le seuil**, dont 43 sur les"
  " 9 pages migrees. Tableau definitif : `docs/recette-v2-tableau-AA.md`. COMPTE, JAMAIS"
  " CORRIGE -- chaque ligne est un arbitrage d'AH en 065-5"),
 ("P-40", "Interactif atteignable et visible au clavier", ECART, "R",
  "**le parcours a la tabulation est fait, il n'est plus 'non verifiable'.** 382 elements"
  " focalisables sur les 9 pages : **382 atteints, 0 inatteignable**. Indicateur visible"
  " sur 379. **3 en ecart**, les 3 champs de `demander-une-analyse.html` : `outline-style`"
  " vaut `none` au focus clavier. Cause identifiee : `assets/style.css` (v1) declare"
  " `form.request-form input:focus { outline: none }`, plus specifique que le"
  " `input:focus-visible` de `mobilier.css` et charge APRES lui. Le repli est un"
  " changement de COULEUR de bordure seul (#d8d3c6 -> #7a3b2e) -- exactement ce que la"
  " doctrine d'accessibilite du site proscrit ailleurs (P-22)"),
 ("P-41", "Recherche < 100 ms, jusqu'a 500 entrees", OK, "R",
  "RECONFIRME au moteur reel (une ligne deja verdictee ne se reprend pas sur parole) :"
  " corpus reel 33 entrees, pire cycle **1,4 ms** ; jeu synthetique de **500 entrees**,"
  " pire cycle **9,3 ms**, soit **9,3 % du seuil**. Cycle mesure : frappe -> filtrage ->"
  " rendu, l'evenement `input` etant distribue de facon synchrone"),
 ("P-42", "Chaque ligne verifiee et datee", OK, "R",
  "le present document : 52 lignes, comptage mecanique, **aucune ligne 'non verifiable'**,"
  " aucune reputee satisfaite, chaque verdict portant sa source ([R] ou [P]) et sa date"),
 ("P-43", "Le volet pilote ne conditionne pas la bascule", HP, "P",
  "volet 'pilote' de 065-4 (Scholar), hors du perimetre de cette recette"),
 ("P-44", "`v2-proto` poussee des creation, jamais fusionnee", OK, "R",
  "controle de sortie : `git rev-list v2-proto..main` = 0 ; `origin/main` et"
  " `origin/staging` inchanges du premier au dernier geste de la session"),
 ("P-45", "Retrofit commite par nature", HP, "P", "065-5"),
 ("P-46", "Premier push sur `main` = point de non-retour", HP, "P",
  "aucun push sur `main` par ce mandat -- verifiable au journal"),
 ("P-47", "Annexe A regeneree avant bascule", OK, "R",
  "**la ligne quitte 'hors perimetre'.** Regeneree depuis le depot (systeme de fichiers +"
  " git), branche `v2-proto` : `docs/recette-v2-annexe-A-regeneree.md`, **34 URLs**."
  " `SPEC-SITE-V2.md` N'A PAS ETE OUVERTE EN ECRITURE : le script d'origine ecrivait dans"
  " la spec, c'est la DESTINATION qui a ete adaptee. L'integration reste la main du greffe"),
 ("P-48", "Retour arriere ecrit ET eprouve", HP, "P", "065-5"),
 ("P-49", "Pas d'index plein texte en 065-3", OK, "P",
  "aucune trace : la recherche porte sur les seules metadonnees du registre"),
 ("P-50", "`genre` deprecie, non lu par le site v2", ECART, "P",
  "ecart assume de la session 065-3 : `corpus.js` lit encore `f.genre` en repli"
  " d'affichage pour les 30 entrees sans `genreBase`. Disparait au retrofit"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sortie", default=os.path.join(
        harnais.DOSSIER_DOCS, "recette-v2-annexe-D-complete.md"))
    args = ap.parse_args()

    # --- Garde-fous : l'outil refuse de produire une checklist fausse.
    assert len(LIGNES) == 52, "52 prescriptions attendues, %d fournies" % len(LIGNES)
    numeros = [l[0] for l in LIGNES]
    assert len(set(numeros)) == 52, "numero de prescription en double"
    for num, _i, verdict, source, preuve in LIGNES:
        assert verdict in (OK, LOT, ECART, HP), "%s : verdict inconnu" % num
        assert source in ("R", "P"), "%s : source inconnue" % num
        assert preuve.strip(), "%s : ligne sans preuve" % num
        assert "non verifiable" not in verdict.lower(), "%s : NV interdit" % num

    compte = {}
    for _n, _i, v, _s, _p in LIGNES:
        compte[v] = compte.get(v, 0) + 1
    rejoues = len([l for l in LIGNES if l[3] == "R"])

    o = []
    a = o.append
    a("# Annexe D COMPLETE -- recette mecanisee du site v2")
    a("")
    a("**Item** : BKL-065-4-recette - **Branche** : `v2-proto` - **Contrat** :")
    a("`SPEC-SITE-V2.md` **v1.1** (52 prescriptions, zero question ouverte)")
    a("**Etablie le** : %s (horodatage instrumental) - **Outil** : Playwright" % DATE)
    a("1.61.0 + Chromium 149, sondes de `outils/recette-playwright/`")
    a("")
    a("> **P-42 : aucune ligne n'est reputee satisfaite par defaut**, et")
    a("> **aucune ligne n'est laissee 'non verifiable'**. Les 8 lignes que le")
    a("> prototype ne pouvait pas trancher -- faute d'un moteur composant une")
    a("> image et d'un journal reseau -- portent ici un verdict mesure.")
    a("")
    a("> **La recette CONSTATE, elle ne corrige jamais.** Aucun fichier du site")
    a("> n'a ete modifie par ce mandat : ni palette, ni page, ni feuille, ni")
    a("> registre, ni spec. Les corrections sont le perimetre de BKL-065-5.")
    a("")
    a("## Vocabulaire des verdicts")
    a("")
    a("| Verdict | Sens |")
    a("|---|---|")
    a("| **OK** | verifie, avec sa preuve |")
    a("| **OK / lot** | verifie sur les 9 pages du prototype ; les 30 pages non"
      " migrees ne le satisfont pas encore (retrofit 065-5) |")
    a("| **ECART** | constate non satisfait -- arbitrage d'AH ou tache de 065-5 |")
    a("| **HP** | hors perimetre de ce mandat, avec son repreneur nomme |")
    a("")
    a("## Source du verdict")
    a("")
    a("| Source | Sens |")
    a("|---|---|")
    a("| **[R]** | mesure prise par CETTE recette, dans Chromium |")
    a("| **[P]** | verdict du prototype 065-3, repris tel quel et non rejoue |")
    a("")
    a("*Cette colonne n'existait pas dans l'annexe D du prototype. Sans elle,")
    a("le document laisserait croire que tout a ete remesure : la recette a")
    a("remesure ce que le prototype ne pouvait pas mesurer, et ce qui en")
    a("dependait. Le reste est repris, et se voit.*")
    a("")
    a("## Comptage")
    a("")
    a("| | Prototype 065-3 (22/07 08h16) | **Recette 065-4 (%s)** |" % DATE)
    a("|---|---|---|")
    a("| OK | 25 | **%d** |" % compte.get(OK, 0))
    a("| OK / lot | 5 | **%d** |" % compte.get(LOT, 0))
    a("| ECART | 7 | **%d** |" % compte.get(ECART, 0))
    a("| **NON VERIFIABLE** | **8** | **0** |")
    a("| HP | 7 | **%d** |" % compte.get(HP, 0))
    a("| **Total** | **52** | **%d** |" % len(LIGNES))
    a("")
    a("**%d des 52 lignes portent une mesure prise par cette recette.**" % rejoues)
    a("")
    a("### Ce que le passage au navigateur reel a change")
    a("")
    a("| Ligne | Avant (prototype) | Apres (recette) |")
    a("|---|---|---|")
    a("| P-29, P-30 | non verifiable (outil hors depot) | **OK** -- composition reelle lue glyphe par glyphe |")
    a("| P-32 | non verifiable (rien n'est publie) | **OK** sur maquette locale, 0 lien mort sur 2 086 |")
    a("| P-37 | non verifiable (pas de journal reseau) | **ECART** -- 2 pages a 1 937 Ko |")
    a("| P-38 | non verifiable (`clientWidth` = 0) | **ECART** -- 1 page a +18 px |")
    a("| P-22, P-24, P-27 | volets non mesurables | **verifies entierement** |")
    a("| P-34 | hors perimetre (Playwright non installe) | **OK** -- cette recette en est la mise en oeuvre |")
    a("| P-47 | hors perimetre (renvoye a 065-4) | **OK** -- annexe A regeneree, 34 URLs |")
    a("| P-21 | ecart (critere inatteignable) | **OK** -- critere amende en v1.1 (E-4), desormais satisfait |")
    a("| P-40 | ecart, parcours clavier non verifie | **ECART** caracterise -- 3 champs, cause nommee |")
    a("")
    a("---")
    a("")
    a("## Les 52 lignes")
    a("")
    a("| # | Prescription (abregee) | Verdict | Src | Preuve / motif |")
    a("|---|---|---|---|---|")
    for num, intitule, verdict, source, preuve in LIGNES:
        a("| **%s** | %s | **%s** | %s | %s |"
          % (num, intitule, verdict, source, preuve))
    a("")
    a("---")
    a("")
    a("## Les ecarts, rassembles")
    a("")
    a("| # | Prescription | Nature | Qui tranche |")
    a("|---|---|---|---|")
    ecarts = [(n, i) for n, i, v, _s, _p in LIGNES if v == ECART]
    tranche = {
        "P-13": "065-5 (la spec est deja amendee, le prototype ne l'est pas)",
        "P-18": "065-5 (retro-remplissage)",
        "P-36": "065-5 (recompression des 5 affiches)",
        "P-37": "065-5 -- consequence directe de P-36, aucune decision propre",
        "P-38": "065-5 (une regle de coupure sur `code`)",
        "P-39": "**AH**, ecart par ecart -- tableau definitif fourni",
        "P-40": "**AH** : la regle v1 qui neutralise le focus doit-elle tomber ?",
        "P-50": "disparait au retrofit",
    }
    for n, i in ecarts:
        a("| %s | %s | %s | %s |"
          % (n, "**%s**" % n, i, tranche.get(n, "065-5")))
    a("")
    a("## Ce qui reste hors perimetre, avec son repreneur")
    a("")
    a("| # | Prescription | Repreneur |")
    a("|---|---|---|")
    for n, i, v, _s, _p in LIGNES:
        if v == HP:
            a("| **%s** | %s | %s |" % (n, i, "065-4 pilote" if n == "P-43"
                                        else ("065-5" if n != "P-11" else "065-5 (skill)")))
    a("")

    texte = "\n".join(o) + "\n"
    # Le garde-fou porte sur la COLONNE VERDICT, pas sur la prose : le
    # document explique justement ce qui a cesse d'etre "non verifiable",
    # et une recherche de texte brut se declencherait sur ces phrases-la.
    verdicts_rendus = set()
    for ligne in texte.split("\n"):
        if ligne.startswith("| **P-") and ligne.count("|") >= 6:
            verdicts_rendus.add(ligne.split("|")[3].strip().strip("*"))
    assert verdicts_rendus <= {OK, LOT, ECART, HP}, \
        "verdict inattendu dans le tableau : %s" % (
            verdicts_rendus - {OK, LOT, ECART, HP})
    assert len(verdicts_rendus) == 4, \
        "les 4 verdicts attendus ne sont pas tous representes : %s" % verdicts_rendus

    with open(args.sortie, "w", encoding="utf-8", newline="\n") as f:
        f.write(texte)

    print("Annexe D complete ecrite : %s" % args.sortie)
    print("  lignes           : %d" % len(LIGNES))
    print("  OK %d | OK/lot %d | ECART %d | HP %d | NV 0"
          % (compte.get(OK, 0), compte.get(LOT, 0), compte.get(ECART, 0),
             compte.get(HP, 0)))
    print("  mesurees par cette recette : %d / 52" % rejoues)
    return 0


if __name__ == "__main__":
    sys.exit(main())
