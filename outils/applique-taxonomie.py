#!/usr/bin/env python3
# -*- coding: ascii -*-
"""applique-taxonomie.py -- ecrit la taxonomie GATEE par AH au registre.

Source : `docs/taxonomie-30-pages-proposition.md`, soumise le 22/07/2026 23h05.
Gate d'AH du 22/07/2026 : "go, polar pour les deux, noms d'epoque sans
accents". Rien ici n'est decide par le script : la table est celle qui a ete
relue, les deux arbitrages sont ceux qui ont ete prononces.

DEUX ETAPES SEPAREES, et ce n'est pas cosmetique (P-12) : ajouter un terme a un
vocabulaire ferme est un ACTE DELIBERE, qui ne se melange jamais a l'ecriture
des donnees. D'ou deux commandes, donc deux commits :

  --vocabulaire : ajoute les 11 pays manquants a assets/vocabulaires.js
  --registre    : ecrit pays, technique, genreBase et deleuze sur les entrees

Convention de nommage arretee par le gate : NOMS D'EPOQUE (le pays de
production est un fait date -- l'URSS a produit Hamlet en 1964, pas la Russie)
et SANS ACCENTS (coherence avec les 4 valeurs deja au vocabulaire).

Usage : python applique-taxonomie.py --vocabulaire|--registre [--simuler]
Codes : 0 succes -- 1 assert en echec -- 2 fichier introuvable.
"""

import argparse
import io
import os
import re
import sys

# --- La table gatee --------------------------------------------------------
# slug : (pays, technique, genreBase force ou None, deleuze ou None)
TABLE = {
    "annie-hall": (["Etats-Unis"], ["couleur"], None, None),
    "au-fil-de-leau": (["Etats-Unis"], ["n&b"], "polar", None),
    "bienvenue-a-suburbicon": (["Etats-Unis", "Royaume-Uni"], ["couleur"],
                               None, None),
    "hamlet": (["Union sovietique"], ["n&b"], None, None),
    "hamnet": (["Royaume-Uni", "Etats-Unis"], ["couleur"], None, None),
    "hitchcock-truffaut": (["Etats-Unis", "France"], ["couleur"], None, None),
    "julie-en-12-chapitres": (["Norvege", "France", "Suede", "Danemark"],
                              ["couleur"], None, None),
    "la-chevauchee-fantastique": (["Etats-Unis"], ["n&b"], None,
                                  ("IM", [203],
                                   "le western (Ford) : de la situation a "
                                   "l'action, l'englobant et le duel")),
    "la-mariee-etait-en-noir": (["France", "Italie"], ["couleur"], None, None),
    "la-nuit-de-san-lorenzo": (["Italie"], ["couleur"], None, None),
    "le-cheval-de-turin": (["Hongrie", "France", "Allemagne", "Suisse"],
                           ["n&b"], None, None),
    "le-doulos": (["France", "Italie"], ["n&b"], "polar", None),
    "le-golem": (["France", "Tchecoslovaquie"], ["n&b"], None, None),
    "le-samourai": (["France", "Italie"], ["couleur"], None, None),
    "les-deux-orphelines": (["Etats-Unis"], ["muet", "n&b"], None, None),
    "manhattan": (["Etats-Unis"], ["n&b"], None, None),
    "moi-daniel-blake": (["Royaume-Uni", "France", "Belgique"], ["couleur"],
                         None, None),
    "nouvelle-vague": (["Etats-Unis", "France"], ["n&b"], None, None),
    "persona": (["Suede"], ["n&b"], None,
                ("IM", [142, 149],
                 "la limite du visage ou le n\u00e9ant : Bergman ; les "
                 "composantes affectives du gros plan")),
    "raging-bull": (["Etats-Unis"], ["n&b"], None, None),
    "retour-a-seoul": (["France", "Allemagne", "Belgique", "Coree du Sud"],
                       ["couleur"], None, None),
    "rosetta": (["Belgique", "France"], ["couleur"], None, None),
    "sans-filtre": (["Suede", "Allemagne", "France", "Royaume-Uni"],
                    ["couleur"], None, None),
    "shutter-island": (["Etats-Unis"], ["couleur"], None, None),
    "soudain-lete-dernier": (["Etats-Unis", "Royaume-Uni"], ["n&b"], None,
                             None),
    "soy-cuba": (["Cuba", "Union sovietique"], ["n&b"], None, None),
    "sud": (["France", "Belgique"], ["couleur"], None, None),
    "sur-la-route-domaha": (["Etats-Unis"], ["couleur"], None, None),
    "the-old-oak": (["Royaume-Uni", "France", "Belgique"], ["couleur"], None,
                    None),
    "waterloo": (["Italie", "Union sovietique"], ["couleur"], None, None),
}


def echec(msg):
    sys.stderr.write("ASSERT EN ECHEC : %s\n" % msg)
    sys.exit(1)


def lire(chemin):
    with io.open(chemin, "r", encoding="utf-8") as f:
        return f.read()


def ecrire(chemin, texte):
    with io.open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(texte)


def liste_js(valeurs):
    return "[" + ", ".join("'%s'" % v for v in valeurs) + "]"


def etape_vocabulaire(depot, simuler):
    chemin = os.path.join(depot, "assets", "vocabulaires.js")
    src = lire(chemin)
    m = re.search(r"pays:\s*\[(.*?)\]", src, re.S)
    if not m:
        echec("vocabulaires.js : liste `pays` introuvable")
    presents = re.findall(r"'([^']+)'", m.group(1))

    voulus = []
    for pays, _, _, _ in TABLE.values():
        for p in pays:
            if p not in voulus:
                voulus.append(p)
    manquants = sorted(p for p in voulus if p not in presents)
    if not manquants:
        print("aucun pays a ajouter -- vocabulaire deja complet")
        return 0

    # Toute valeur accentuee trahirait la convention arretee au gate.
    for p in manquants:
        if any(ord(c) > 127 for c in p):
            echec("valeur accentuee contraire au gate : %r" % p)

    complet = sorted(presents + manquants)
    bloc = ("[\n" + "".join("    '%s',\n" % p for p in complet[:-1])
            + "    '%s'\n  ]" % complet[-1])
    nouveau = src[:m.start()] + "pays: " + bloc + src[m.end():]
    if nouveau == src:
        echec("vocabulaires.js : aucune modification produite")
    if not simuler:
        ecrire(chemin, nouveau)
    print("pays au vocabulaire : %d -> %d (%d ajout(s))%s"
          % (len(presents), len(complet), len(manquants),
             "  [SIMULATION]" if simuler else ""))
    for p in manquants:
        print("   + %s" % p)
    return 0


def etape_registre(depot, simuler):
    chemin = os.path.join(depot, "assets", "films-data.js")
    src = lire(chemin)

    # Le vocabulaire doit AVOIR ETE etendu : on n'ecrit pas une valeur qui
    # ferait echouer le controle P-10 juste apres.
    voc = lire(os.path.join(depot, "assets", "vocabulaires.js"))
    mv = re.search(r"pays:\s*\[(.*?)\]", voc, re.S)
    connus = set(re.findall(r"'([^']+)'", mv.group(1))) if mv else set()
    for slug, (pays, _, _, _) in TABLE.items():
        for p in pays:
            if p not in connus:
                echec("%s : pays '%s' absent du vocabulaire -- jouer d'abord "
                      "--vocabulaire (P-12)" % (slug, p))

    objets = re.compile(r"(\n  \{\n)(.*?)(\n  \})", re.S)
    faits, ignores = [], []

    def traite(m):
        ouvre, corps, ferme = m.group(1), m.group(2), m.group(3)
        ms = re.search(r"slug:\s*'([^']+)'", corps)
        slug = ms.group(1) if ms else None
        if slug not in TABLE:
            ignores.append(slug)
            return m.group(0)
        pays, technique, genre_force, deleuze = TABLE[slug]
        if "pays:" in corps:
            ignores.append(slug + " (deja pose)")
            return m.group(0)

        ajouts = ["    pays: %s," % liste_js(pays),
                  "    technique: %s," % liste_js(technique)]
        corps2 = corps
        if genre_force:
            if "genreBase:" in corps2:
                echec("%s : genreBase deja pose, le gate le voulait absent"
                      % slug)
            ajouts.append("    genreBase: '%s'," % genre_force)
        if deleuze:
            oeuvre, pages, concepts = deleuze
            ajouts.append(
                "    deleuze: { oeuvre: '%s', pages: [%s], concepts: '%s' },"
                % (oeuvre, ", ".join(str(p) for p in pages), concepts))
        ajouts[-1] = ajouts[-1].rstrip(",")
        if not corps2.rstrip().endswith(","):
            corps2 = corps2.rstrip() + ","
        faits.append(slug)
        return ouvre + corps2 + "\n" + "\n".join(ajouts) + ferme

    resultat = objets.sub(traite, src)
    if len(faits) != len(TABLE):
        echec("%d entrees traitees sur %d attendues -- %s"
              % (len(faits), len(TABLE),
                 sorted(set(TABLE) - set(faits))))
    if not simuler:
        ecrire(chemin, resultat)
    print("entrees enrichies : %d%s" % (len(faits),
                                        "  [SIMULATION]" if simuler else ""))
    print("entrees ignorees  : %d (%s)"
          % (len(ignores), ", ".join(str(i) for i in ignores if i)))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depot", default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    ap.add_argument("--vocabulaire", action="store_true")
    ap.add_argument("--registre", action="store_true")
    ap.add_argument("--simuler", action="store_true")
    args = ap.parse_args()
    if args.vocabulaire == args.registre:
        echec("choisir --vocabulaire OU --registre (P-12 : jamais les deux)")
    if args.vocabulaire:
        return etape_vocabulaire(args.depot, args.simuler)
    return etape_registre(args.depot, args.simuler)


if __name__ == "__main__":
    sys.exit(main())
