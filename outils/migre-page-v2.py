#!/usr/bin/env python3
# -*- coding: ascii -*-
"""migre-page-v2.py -- migration d'une page d'analyse vers le gabarit v2.

Ecrit pour le prototype BKL-065-3 (lot de 3 pages), ETENDU pour le retrofit de
masse de BKL-065-5 (les 30 pages restantes). La repetition du prototype tient :
ce qui n'etait pas scriptable la-bas ne l'est pas devenu ici -- on l'a mesure,
5 pages sur 30 resistent aux asserts d'origine, et elles sont traitees a part,
jamais forcees.

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

RETROFIT PAR NATURE (P-45) -- les transformations sont groupees pour etre
commitees separement, donc revocables une par une :
  --nature typo        : etapes 1, 2, 3
  --nature signatures  : etape 5 (cartouche et variante)
  --nature gabarit     : etapes 4 et 6 (menu et chevron)
Sans --nature, les trois s'enchainent dans CET ordre (comportement du
prototype). L'ordre est contraint : le cartouche s'ancre sur l'unique
</header> de la page, que le menu dedoublerait -- signatures AVANT gabarit.

Chaque transformation porte son assert : si un motif attendu est absent ou si
un remplacement ne change rien, le script s'arrete AVANT d'ecrire. Aucune
ecriture partielle.

Usage : python migre-page-v2.py [--depot CHEMIN] [--lot proto|retrofit]
                               [--nature typo|gabarit|signatures|tout]
                               [--verifier] [--simuler]
  --verifier : n'ecrit rien, controle l'etat des pages du lot.
  --simuler  : joue toutes les transformations en memoire, n'ecrit rien,
               et rapporte ce qui aurait change. C'est la repetition.
Codes : 0 succes -- 1 assert en echec -- 2 fichier introuvable.
"""

import argparse
import io
import json
import os
import re
import subprocess
import sys

# Le caractere lui-meme n'est PAS ecrit dans ce source : il s'y glisserait un
# octet non ASCII, et c'est precisement le glyphe qu'on retire.
FLECHE = u"\u2190"

# Les libelles VISIBLES portent leurs entites HTML : ce fichier reste ASCII
# pur, la page reste en francais correct. Les textes de signature sont ceux du
# section 5.3 de la spec, au caractere pres -- ils ne se reecrivent pas film
# par film (P-14).
SIGNATURE_R1 = ("Analyse faite par IAGen Claude d'Anthropic "
                "(mod&egrave;le non sp&eacute;cifi&eacute;, supervision humaine).")

REGIME_R1 = "R1 &mdash; Critique publi&eacute;e avant le site v2"

MOIS = ["janvier", "f&eacute;vrier", "mars", "avril", "mai", "juin",
        "juillet", "ao&ucirc;t", "septembre", "octobre", "novembre",
        "d&eacute;cembre"]

# --- Le lot du prototype (065-3), conserve tel quel ------------------------
LOT_PROTO = [
    {
        "fichier": "pandora.html",
        "volet": "critique",
        "regime": REGIME_R1,
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
        "regime": REGIME_R1,
        "producteur": "non sp&eacute;cifi&eacute;",
        "signature": SIGNATURE_R1,
        "date": "2026-07-04 10:11",
        "date_lisible": "4 juillet 2026",
        "variante": None,
    },
]

DEJA_MIGREES = set(p["fichier"] for p in LOT_PROTO)

# --- Les pages qui RESISTENT aux asserts d'origine, et pourquoi ------------
# Mesure du 22/07/2026 : 25 des 30 pages passent tel quel. Les 5 autres ne
# sont pas des exceptions inventees pour faire passer le script -- chacune
# porte un ecart CONSTATE, nomme, et son traitement est explicite.
CAS_A_PART = {
    # Publiee sans identite bespoke : elle lit style.css (le chrome du site)
    # et ne declare ni fonte tierce, ni font-family, ni bloc <style>. Il n'y a
    # donc RIEN a substituer -- mais tout a lier : sans mobilier.css, les
    # variables de role (--serif, --sans) qu'emploie style.css v2 ne sont
    # definies nulle part et la page tomberait en repli.
    "annie-hall.html": {
        "sans_fonte_tierce": True,
        "sans_famille": True,
        "sans_bloc_style": True,
    },
}

# Les 4 pages publiees le 21/07 nomment leur lien de retour "retour" et non
# "back-link" : variante de gabarit du skill, constatee, sans consequence
# editoriale. Le script accepte les deux noms plutot que d'en imposer un.
CLASSES_RETOUR = ("back-link", "retour")

MENU = [
    ("../index.html", "Accueil", None),
    ("../critiques.html", "Critiques", "critique"),
    ("../etudes.html", "Etudes", "etude"),
    ("../qui-sommes-nous.html", "Qui sommes-nous", None),
    ("../comment-ca-marche.html", "Comment ce site fonctionne", None),
    ("../demander-une-analyse.html", "Demander une analyse", None),
]

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


def date_git(depot, relatif):
    """Date de PREMIERE apparition du fichier sur main (P-45, D-5).

    Mecanique, jamais devinee : c'est git qui repond. Le dernier element de la
    liste est le commit d'ajout le plus ancien.
    """
    sortie = subprocess.check_output(
        ["git", "-C", depot, "log", "main", "--diff-filter=A",
         "--format=%ad", "--date=format:%Y-%m-%d %H:%M", "--", relatif],
        stderr=subprocess.STDOUT).decode("ascii", "replace")
    lignes = [l.strip() for l in sortie.splitlines() if l.strip()]
    if not lignes:
        echec("%s : aucune date d'ajout dans l'historique de main" % relatif)
    return lignes[-1]


def date_lisible(iso):
    a, m, j = iso[:10].split("-")
    return "%d %s %s" % (int(j), MOIS[int(m) - 1], a)


def producteurs_du_registre(depot):
    """Lit le champ producteur de chaque entree. Le registre FAIT FOI (P-17).

    Ce qui n'y est pas journalise ne s'invente pas : la valeur est alors
    'non specifie', explicitement (P-18) -- jamais un champ vide, jamais une
    valeur deduite.
    """
    t = lire(os.path.join(depot, "assets", "films-data.js"))
    trouve = {}
    for bloc in re.split(r"\n\s*\{", t):
        m = re.search(r"slug:\s*['\"]([^'\"]+)", bloc)
        if not m:
            continue
        p = re.search(r"producteur:\s*['\"]([^'\"]*)['\"]", bloc)
        trouve[m.group(1)] = p.group(1) if p and p.group(1).strip() else None
    return trouve


def lot_retrofit(depot):
    """Construit le lot des 30 pages, entierement a partir de MESURES."""
    dossier = os.path.join(depot, "films")
    noms = sorted(n for n in os.listdir(dossier)
                  if n.endswith(".html") and n not in DEJA_MIGREES)
    prod = producteurs_du_registre(depot)
    lot = []
    for nom in noms:
        slug = nom[:-5]
        iso = date_git(depot, "films/" + nom)
        valeur = prod.get(slug)
        lot.append({
            "fichier": nom,
            # Les 30 sont des Critiques : la seule Etude du corpus
            # (pandora-contrechamp) appartient au lot du prototype.
            "volet": "critique",
            "regime": REGIME_R1,
            # Journalise -> nomme ; non journalise -> dit non specifie.
            "producteur": valeur if valeur else "non sp&eacute;cifi&eacute;",
            "signature": SIGNATURE_R1,
            "date": iso,
            "date_lisible": date_lisible(iso),
            "variante": None,
        })
    return lot


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
    # Les chaines portent DEJA leurs entites : aucune substitution d'accents
    # ici. La premiere version enchainait des .replace() partiels et laissait
    # passer "ETUDE", "Modele", "Publiee" -- une chaine de remplacements n'est
    # pas un encodage.
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


def nature_typo(t, chemin, cas, journal):
    # 1. Fontes tierces -----------------------------------------------------
    avant = len(re.findall(r"fonts\.(?:googleapis|gstatic)\.com", t))
    if avant == 0 and not cas.get("sans_fonte_tierce"):
        echec("%s : aucun appel de fonte tierce, page deja migree ?"
              % os.path.basename(chemin))
    if avant:
        t = re.sub(
            r'[ \t]*<link[^>]*fonts\.(?:googleapis|gstatic)\.com[^>]*>\s*\n',
            "", t)
        if re.search(r"fonts\.(?:googleapis|gstatic)\.com", t):
            echec("%s : appel de fonte tierce residuel" % chemin)
    journal["fontes_tierces_retirees"] = avant

    # 2. Feuilles auto-hebergees -------------------------------------------
    ancre = "</title>"
    if ancre not in t:
        echec("%s : pas de </title> ou inserer les feuilles" % chemin)
    if "assets/mobilier.css" in t:
        echec("%s : mobilier.css deja lie" % chemin)
    t = t.replace(
        ancre,
        ancre + '\n<link rel="stylesheet" href="../assets/fonts.css">'
                '\n<link rel="stylesheet" href="../assets/mobilier.css">', 1)

    # 3. Substitution typographique ----------------------------------------
    n_familles = len(re.findall(r"font-family\s*:", t))
    if n_familles == 0 and not cas.get("sans_famille"):
        echec("%s : aucune declaration font-family" % chemin)
    journal["familles_substituees"] = n_familles
    if n_familles:
        def sub_famille(m):
            return "font-family:" + role_typo(m.group(1))
        t = re.sub(r"font-family\s*:\s*([^;}]+)", sub_famille, t)
        if re.search(r"font-family\s*:\s*'", t):
            echec("%s : famille nommee residuelle apres substitution" % chemin)

    # Les titres suivent le texte courant (P-26). Regle posee en FIN de la
    # feuille de la page : meme specificite, elle l'emporte par l'ordre.
    fin_style = t.rfind("</style>")
    if fin_style < 0:
        if not cas.get("sans_bloc_style"):
            echec("%s : pas de </style>" % chemin)
        # Page sans feuille propre : rien a surcharger, elle herite du
        # systeme par mobilier.css. On n'INVENTE pas un bloc <style>.
        journal["regle_titrage"] = "sans objet (page sans feuille propre)"
    else:
        t = (t[:fin_style]
             + "\n  /* Substitution typographique v2 (P-20, P-26) : titrage et\n"
               "     texte courant sur la meme famille. Palette, couverture et\n"
               "     ossature de la page restent intactes. */\n"
               "  body{font-family:var(--serif);}\n"
               "  h1,h2,h3{font-family:var(--serif);}\n"
             + t[fin_style:])
        journal["regle_titrage"] = "posee"
    return t


def nature_gabarit(t, chemin, p, journal):
    # 4. Menu ---------------------------------------------------------------
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
    # Le lien de retour porte 'back-link' ou 'retour' selon la generation du
    # skill qui a produit la page. Les deux sont acceptes ; aucune n'est
    # renommee, on AJOUTE la classe de mobilier.
    pose = 0
    for classe in CLASSES_RETOUR:
        motif = r'class="%s(?![-\w])' % classe
        if re.search(motif, t):
            t = re.sub(motif, 'class="%s lien-retour' % classe, t)
            pose += 1
    if pose == 0 or "lien-retour" not in t:
        echec("%s : lien de retour introuvable (ni %s)"
              % (chemin, " ni ".join(CLASSES_RETOUR)))
    journal["fleches_retirees"] = n_fleches
    journal["classe_retour"] = pose
    return t


def nature_signatures(t, chemin, p, journal):
    # 5. Cartouche et variante ---------------------------------------------
    # AVANT le menu, et non apres : le menu apporte son propre </header>, ce
    # qui rendrait l'ancre ambigue. L'assert l'a attrape au premier essai --
    # c'est sa raison d'etre, et la page n'a pas ete ecrite pour autant.
    if 'class="cartouche"' in t:
        echec("%s : cartouche deja pose" % chemin)
    if 'class="chrome"' in t:
        # L'ordre des natures n'est pas un detail : le menu apporte un second
        # </header> et l'ancre du cartouche cesse d'etre unique. Le prototype
        # l'avait deja rencontre ; l'assert le redit plutot que de deviner
        # laquelle des deux ancres est la bonne.
        echec("%s : le menu est deja pose -- le cartouche s'ancre AVANT lui "
              "(ordre des natures : typo, signatures, gabarit)" % chemin)
    if "</header>" not in t:
        echec("%s : pas de </header> ou poser le cartouche" % chemin)
    if t.count("</header>") != 1:
        echec("%s : %d occurrences de </header>, ancre ambigue"
              % (chemin, t.count("</header>")))
    t = t.replace("</header>", "</header>\n\n" + bloc_cartouche(p), 1)
    journal["cartouche"] = "pose"
    journal["producteur"] = p["producteur"]
    journal["date"] = p["date"]
    return t


NATURES = {
    "typo": [nature_typo],
    "gabarit": [nature_gabarit],
    "signatures": [nature_signatures],
}


def migre(chemin, p, natures, simuler):
    src = lire(chemin)
    t = src
    cas = CAS_A_PART.get(os.path.basename(chemin), {})
    journal = {"page": os.path.basename(chemin),
               "cas_a_part": bool(cas)}
    for nom in natures:
        for fonction in NATURES[nom]:
            if fonction is nature_typo:
                t = fonction(t, chemin, cas, journal)
            else:
                t = fonction(t, chemin, p, journal)
    if t == src:
        echec("%s : aucune modification produite" % chemin)
    journal["octets"] = (len(src), len(t))
    if not simuler:
        ecrire(chemin, t)
    return journal


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
    ap.add_argument("--lot", choices=["proto", "retrofit"], default="proto")
    ap.add_argument("--nature",
                    choices=["typo", "gabarit", "signatures", "tout"],
                    default="tout")
    ap.add_argument("--verifier", action="store_true")
    ap.add_argument("--simuler", action="store_true")
    ap.add_argument("--json", action="store_true",
                    help="rapport machine, pour le rapport de migration")
    args = ap.parse_args()

    lot = LOT_PROTO if args.lot == "proto" else lot_retrofit(args.depot)
    # ORDRE IMPOSE, pas arbitraire : le cartouche s'ancre sur l'unique
    # </header> de la page, que le menu dedoublerait. signatures AVANT gabarit.
    natures = (["typo", "signatures", "gabarit"] if args.nature == "tout"
               else [args.nature])

    rapports = []
    for p in lot:
        chemin = os.path.join(args.depot, "films", p["fichier"])
        if not os.path.isfile(chemin):
            sys.stderr.write("Introuvable : %s\n" % chemin)
            return 2
        if args.verifier:
            r = verifie(chemin)
            rapports.append(r)
            if not args.json:
                print("%-32s %s" % (r["page"], "  ".join(
                    "%s=%s" % (k, v) for k, v in r.items() if k != "page")))
        else:
            r = migre(chemin, p, natures, args.simuler)
            rapports.append(r)
            if not args.json:
                marque = " [cas a part]" if r["cas_a_part"] else ""
                print("%-32s %d -> %d octets%s" % (
                    r["page"], r["octets"][0], r["octets"][1], marque))
    if args.json:
        print(json.dumps(rapports, indent=1, sort_keys=True))
    elif not args.verifier:
        print("")
        print("lot=%s  natures=%s  %s  pages=%d" % (
            args.lot, ",".join(natures),
            "SIMULATION (rien ecrit)" if args.simuler else "ECRIT",
            len(rapports)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
