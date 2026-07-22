#!/usr/bin/env python3
# -*- coding: ascii -*-
"""migre-page-v2.py -- migration d'une page d'analyse vers le gabarit v2.

Prototype BKL-065-3, lot de 3 pages. C'est aussi la REPETITION du retrofit de
masse de BKL-065-5 : ce qui n'est pas scriptable ici ne le sera pas la-bas.

Ce que la migration fait, et rien d'autre :
  1. retire les appels de fontes tierces (P-24) ;
  2. lie les feuilles auto-hebergees fonts.css et mobilier.css (P-25) ;
  3. substitue les familles typographiques par les roles du systeme (P-20,
     P-26) -- le role se deduit du REPLI ecrit par l'auteur lui-meme
     (monospace -> mono, sans-serif -> sans, sinon serif), et les titres sont
     forces sur la famille du texte courant par une regle finale ;
  4. pose le menu du site (P-02) avec un unique aria-current ;
  5. pose le cartouche de provenance (P-15) et, s'il y a lieu, le lien vers
     la variante (P-03) ;
  6. remplace le caractere U+2190 du lien de retour par le chevron CSS (P-28).

Ce qu'elle ne touche PAS : la palette, la couverture, l'ossature, le texte.
L'identite bespoke appartient a l'oeuvre (SPEC-SITE-V2 section 6.1).

Chaque transformation porte son assert : si un motif attendu est absent ou si
un remplacement ne change rien, le script s'arrete AVANT d'ecrire. Aucune
ecriture partielle.

Usage : python migre-page-v2.py [--depot CHEMIN] [--verifier]
  --verifier : n'ecrit rien, controle l'etat des pages deja migrees.
Codes : 0 succes -- 1 assert en echec -- 2 fichier introuvable.
"""

import argparse
import io
import os
import re
import sys

# Le caractere lui-meme n'est PAS ecrit dans ce source : il s'y glisserait un
# octet non ASCII, et c'est precisement le glyphe qu'on retire.
FLECHE = u"\u2190"

# Le lot du prototype. Le volet, la provenance et la date viennent du registre
# (P-17 : le registre fait foi) ; ils sont repris ici pour que la page et le
# registre portent la meme information.
# Les libelles VISIBLES portent leurs entites HTML : ce fichier reste ASCII
# pur, la page reste en francais correct. Les textes de signature sont ceux du
# section 5.3 de la spec, au caractere pres -- ils ne se reecrivent pas film par film
# (P-14).
SIGNATURE_R1 = ("Analyse faite par IAGen Claude d'Anthropic "
                "(mod&egrave;le non sp&eacute;cifi&eacute;, supervision humaine).")

LOT = [
    {
        "fichier": "pandora.html",
        "volet": "critique",
        "regime": "R1 &mdash; Critique publi&eacute;e avant le site v2",
        "producteur": "Claude (pipeline, routine nocturne)",
        "signature": SIGNATURE_R1,
        "date": "2026-07-18 20:45",
        "date_lisible": "18 juillet 2026",
        "variante": {"url": "pandora-contrechamp.html",
                     "titre": "Pandora &mdash; Contrechamp",
                     "volet": "&Eacute;tude"},
    },
    {
        "fichier": "pandora-contrechamp.html",
        "volet": "etude",
        "regime": "R3 &mdash; &Eacute;tude",
        "producteur": "OpenAI GPT-5.5 (reprise et enrichissement squad)",
        # P-19 : le premier jet n'a pas ete produit par un modele de la squad.
        # Le segment "premier jet produit par..." nomme le producteur reel ;
        # le reste de la formule R3 est celui du section 5.3, inchange.
        "signature": ("&Eacute;tude &mdash; premier jet produit par OpenAI "
                      "GPT-5.5, repris et enrichi par la squad, r&eacute;vision "
                      "&eacute;ditoriale et validation par Christo Datso."),
        "date": "2026-07-18 23:45",
        "date_lisible": "18 juillet 2026",
        "variante": {"url": "pandora.html",
                     "titre": "Pandora &mdash; Champ",
                     "volet": "Critique"},
    },
    {
        "fichier": "rouges-et-blancs.html",
        "volet": "critique",
        "regime": "R1 &mdash; Critique publi&eacute;e avant le site v2",
        "producteur": "non sp&eacute;cifi&eacute;",
        "signature": SIGNATURE_R1,
        "date": "2026-07-04 10:11",
        "date_lisible": "4 juillet 2026",
        "variante": None,
    },
]

MENU = [
    ("../index.html", "Accueil", None),
    ("../critiques.html", "Critiques", "critique"),
    ("../etudes.html", "Etudes", "etude"),
    ("../qui-sommes-nous.html", "Qui sommes-nous", None),
    ("../comment-ca-marche.html", "Comment ce site fonctionne", None),
    ("../demander-une-analyse.html", "Demander une analyse", None),
]

# Les entites HTML evitent d'ecrire un seul caractere accentue dans ce source :
# le script reste ASCII pur, la page reste en francais.
ETUDES = "&Eacute;tudes"


def echec(msg):
    sys.stderr.write("ASSERT EN ECHEC : %s\n" % msg)
    sys.exit(1)


def lire(chemin):
    with io.open(chemin, "r", encoding="utf-8") as f:
        return f.read()


def ecrire(chemin, texte):
    with io.open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(texte)


def bloc_menu(volet):
    liens = []
    for href, libelle, marque in MENU:
        if libelle == "Etudes":
            libelle = ETUDES
        courant = ' aria-current="page"' if marque == volet else ""
        liens.append('      <a href="%s"%s>%s</a>' % (href, courant, libelle))
    return (
        '<header class="chrome">\n'
        '  <div class="chrome-in">\n'
        '    <a class="marque" href="../index.html">Analyses de films</a>\n'
        '    <nav class="menu" aria-label="Navigation principale">\n'
        + "\n".join(liens) + "\n"
        '    </nav>\n'
        '  </div>\n'
        '</header>\n'
    )


def bloc_cartouche(p):
    lignes = []
    if p["variante"]:
        v = p["variante"]
        lignes.append(
            '<p class="variante"><span class="quoi">Autre regard sur ce film</span>'
            '<a href="%s">%s &mdash; %s</a></p>'
            % (v["url"], v["titre"], v["volet"]))
    # Les chaines de LOT portent DEJA leurs entites : aucune substitution
    # d'accents ici. La premiere version enchainait des .replace() partiels
    # et laissait passer "ETUDE", "Modele", "Publiee" -- une chaine de
    # remplacements n'est pas un encodage.
    lignes.append(
        '<div class="cartouche">\n'
        '  <span class="regime">%s</span>\n'
        '  <span class="signature">%s</span>\n'
        '  <span class="signature">Mod&egrave;le producteur : %s</span>\n'
        '  <span class="date-pub">Publi&eacute;e le %s</span>\n'
        '</div>'
        % (p["regime"], p["signature"], p["producteur"], p["date_lisible"]))
    return '<div class="wrap" style="padding-top:1.6rem;">\n' \
           + "\n".join(lignes) + "\n</div>\n"


def role_typo(valeur):
    v = valeur.lower()
    if "monospace" in v:
        return "var(--mono)"
    if "sans-serif" in v:
        return "var(--sans)"
    return "var(--serif)"


def migre(chemin, p):
    src = lire(chemin)
    t = src

    # 1. Fontes tierces -----------------------------------------------------
    avant = len(re.findall(r"fonts\.(?:googleapis|gstatic)\.com", t))
    if avant == 0:
        echec("%s : aucun appel de fonte tierce, page deja migree ?"
              % os.path.basename(chemin))
    t = re.sub(r'[ \t]*<link[^>]*fonts\.(?:googleapis|gstatic)\.com[^>]*>\s*\n',
               "", t)
    if re.search(r"fonts\.(?:googleapis|gstatic)\.com", t):
        echec("%s : appel de fonte tierce residuel" % chemin)

    # 2. Feuilles auto-hebergees -------------------------------------------
    ancre = "</title>"
    if ancre not in t:
        echec("%s : pas de </title> ou inserer les feuilles" % chemin)
    t = t.replace(
        ancre,
        ancre + '\n<link rel="stylesheet" href="../assets/fonts.css">'
                '\n<link rel="stylesheet" href="../assets/mobilier.css">', 1)

    # 3. Substitution typographique ----------------------------------------
    n_familles = len(re.findall(r"font-family\s*:", t))
    if n_familles == 0:
        echec("%s : aucune declaration font-family" % chemin)

    def sub_famille(m):
        return "font-family:" + role_typo(m.group(1))

    t = re.sub(r"font-family\s*:\s*([^;}]+)", sub_famille, t)
    if re.search(r"font-family\s*:\s*'", t):
        echec("%s : famille nommee residuelle apres substitution" % chemin)

    # Les titres suivent le texte courant (P-26). Regle posee en FIN de la
    # feuille de la page : meme specificite, elle l'emporte par l'ordre.
    fin_style = t.rfind("</style>")
    if fin_style < 0:
        echec("%s : pas de </style>" % chemin)
    t = (t[:fin_style]
         + "\n  /* Substitution typographique v2 (P-20, P-26) : titrage et\n"
           "     texte courant sur la meme famille. Palette, couverture et\n"
           "     ossature de la page restent intactes. */\n"
           "  body{font-family:var(--serif);}\n"
           "  h1,h2,h3{font-family:var(--serif);}\n"
         + t[fin_style:])

    # 4. Cartouche et variante ---------------------------------------------
    # AVANT le menu, et non apres : le menu apporte son propre </header>, ce
    # qui rendrait l'ancre ambigue. L'assert l'a attrape au premier essai --
    # c'est sa raison d'etre, et la page n'a pas ete ecrite pour autant.
    if "</header>" not in t:
        echec("%s : pas de </header> ou poser le cartouche" % chemin)
    if t.count("</header>") != 1:
        echec("%s : %d occurrences de </header>, ancre ambigue"
              % (chemin, t.count("</header>")))
    t = t.replace("</header>", "</header>\n\n" + bloc_cartouche(p), 1)

    # 5. Menu ---------------------------------------------------------------
    m = re.search(r"<body[^>]*>", t)
    if not m:
        echec("%s : pas de balise body" % chemin)
    if 'class="chrome"' in t:
        echec("%s : menu deja present" % chemin)
    corps = '<body data-volet="%s">' % p["volet"]
    t = t[:m.start()] + corps + "\n\n" + bloc_menu(p["volet"]) + t[m.end():]

    # 6. Chevron ------------------------------------------------------------
    n_fleches = t.count(FLECHE)
    if n_fleches == 0:
        echec("%s : aucune fleche U+2190 a remplacer" % chemin)
    t = t.replace(FLECHE + " ", "").replace(FLECHE, "")
    if FLECHE in t:
        echec("%s : fleche residuelle" % chemin)
    t = re.sub(r'class="back-link"', 'class="back-link lien-retour"', t)
    if "lien-retour" not in t:
        echec("%s : lien de retour introuvable" % chemin)

    if t == src:
        echec("%s : aucune modification produite" % chemin)

    ecrire(chemin, t)
    return {
        "page": os.path.basename(chemin),
        "fontes_tierces_retirees": avant,
        "familles_substituees": n_familles,
        "fleches_retirees": n_fleches,
        "octets": (len(src), len(t)),
    }


def verifie(chemin):
    t = lire(chemin)
    return {
        "page": os.path.basename(chemin),
        "fontes tierces": len(re.findall(r"fonts\.(?:googleapis|gstatic)\.com", t)),
        "familles nommees": len(re.findall(r"font-family\s*:\s*'", t)),
        "fleche U+2190": t.count(FLECHE),
        "menu": 1 if 'class="chrome"' in t else 0,
        "aria-current": t.count('aria-current="page"'),
        "cartouche": 1 if 'class="cartouche"' in t else 0,
        "data-volet": 1 if "data-volet" in t else 0,
        "chevron": 1 if "lien-retour" in t else 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depot", default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    ap.add_argument("--verifier", action="store_true")
    args = ap.parse_args()

    for p in LOT:
        chemin = os.path.join(args.depot, "films", p["fichier"])
        if not os.path.isfile(chemin):
            sys.stderr.write("Introuvable : %s\n" % chemin)
            return 2
        if args.verifier:
            r = verifie(chemin)
            print("%-28s %s" % (r.pop("page"), "  ".join(
                "%s=%s" % (k, v) for k, v in r.items())))
        else:
            r = migre(chemin, p)
            print("%-28s fontes tierces retirees=%d  familles substituees=%d  "
                  "fleches=%d  %d -> %d octets" % (
                      r["page"], r["fontes_tierces_retirees"],
                      r["familles_substituees"], r["fleches_retirees"],
                      r["octets"][0], r["octets"][1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
