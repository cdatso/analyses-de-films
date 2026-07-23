#!/usr/bin/env python3
# -*- coding: ascii -*-
"""normalise-v2.py -- les normalisations ponctuelles du retrofit BKL-065-5.

La nature 4 du mandat rassemble ce qui n'est pas une transformation de masse :
des defauts NOMMES, un par un, chacun avec sa regle, son perimetre et son
critere de verification. Rien d'automatique a l'aveugle -- une regle ne
s'applique qu'aux fichiers qu'elle nomme, et echoue bruyamment si le motif
attendu a disparu.

Regles disponibles (--regle) :
  calage-mobilier    : pose --mobilier-largeur sur chaque page, a la valeur
                       MESUREE par sonde-mobilier.py (arbitrage AH option B :
                       le mobilier se cale sur la colonne editoriale, pas sur
                       le menu). Aucune valeur devinee : une page non mesuree
                       n est pas touchee.
  collision-waterloo : la page nomme `cartouche` son en-tete de COUVERTURE
                       (header.cartouche + .cartouche-inner), nom qui entre en
                       collision avec le composant de mobilier `.cartouche`
                       (P-15/P-16). Sans renommage, les regles du mobilier
                       (chasse fixe, filets de volet, marges) s'appliqueraient
                       a la couverture du film. Renomme la classe BESPOKE,
                       jamais le composant partage. Zero effet editorial.

Usage : python normalise-v2.py --regle <nom> [--depot CHEMIN] [--simuler]
Codes : 0 succes -- 1 assert en echec -- 2 fichier introuvable.
"""

import argparse
import io
import os
import re
import sys


def echec(msg):
    sys.stderr.write("ASSERT EN ECHEC : %s\n" % msg)
    sys.exit(1)


def lire(chemin):
    with io.open(chemin, "r", encoding="utf-8") as f:
        return f.read()


def ecrire(chemin, texte):
    with io.open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(texte)


def collision_waterloo(depot, simuler):
    chemin = os.path.join(depot, "films", "waterloo.html")
    if not os.path.isfile(chemin):
        sys.stderr.write("Introuvable : %s\n" % chemin)
        return 2
    src = lire(chemin)

    # Les 5 occurrences constatees le 22/07/2026. Si l'une manque, la page a
    # change depuis le constat : on s'arrete plutot que de renommer a moitie.
    attendus = [
        ("header.cartouche{", "header.carte-titre{"),
        ("header.cartouche::after{", "header.carte-titre::after{"),
        (".cartouche-inner{", ".carte-titre-inner{"),
        ('<header class="cartouche">', '<header class="carte-titre">'),
        ('<div class="cartouche-inner">', '<div class="carte-titre-inner">'),
    ]
    t = src
    for avant, apres in attendus:
        if avant not in t:
            echec("waterloo.html : motif attendu absent -- %r" % avant)
        t = t.replace(avant, apres)

    # Le composant de mobilier ne doit plus etre nomme nulle part dans la
    # page : c'est TOUT l'objet de la regle.
    if "cartouche" in t:
        restants = [l for l in t.splitlines() if "cartouche" in l]
        echec("waterloo.html : %d ligne(s) nomment encore 'cartouche' : %s"
              % (len(restants), restants[:3]))
    if t == src:
        echec("waterloo.html : aucune modification produite")

    if not simuler:
        ecrire(chemin, t)
    print("waterloo.html  collision header.cartouche -> header.carte-titre  "
          "(%d occurrences)  %d -> %d octets%s"
          % (len(attendus), len(src), len(t),
             "  [SIMULATION]" if simuler else ""))
    return 0


ANCIEN_CONTENEUR = '<div class="wrap" style="padding-top:1.6rem;">'
NOUVEAU_CONTENEUR = '<div class="mobilier-wrap" style="padding-top:1.6rem;">'


def classe_mobilier(depot, simuler):
    """Le mobilier cesse d'emprunter la classe d'ossature des pages.

    Gate AH du 22/07/2026 20h34. Le gabarit posait le cartouche dans un
    `<div class="wrap">` -- une classe que chaque page bespoke definit a sa
    guise, ou pas du tout. La largeur du mobilier dependait donc de la feuille
    de la page : 4 pages la gouvernaient par leur propre regle, une cinquieme
    par `style.css`, et le filet defensif ne pouvait pas les rattraper (meme
    specificite, declaree avant). La classe propre `.mobilier-wrap` retire le
    sujet a la cascade des pages.

    Le motif remplace est la chaine EXACTE emise par le gabarit : les `.wrap`
    d'ossature des pages ne sont pas touchees -- elles ne regardent que
    l'ossature, et c'est tres bien ainsi.
    """
    dossier = os.path.join(depot, "films")
    noms = sorted(n for n in os.listdir(dossier) if n.endswith(".html"))
    faits, sans_objet = 0, []
    for nom in noms:
        chemin = os.path.join(dossier, nom)
        src = lire(chemin)
        if NOUVEAU_CONTENEUR in src:
            sans_objet.append((nom, "deja converti"))
            continue
        if src.count(ANCIEN_CONTENEUR) != 1:
            sans_objet.append((nom, "%d occurrence(s) du conteneur attendu"
                               % src.count(ANCIEN_CONTENEUR)))
            continue
        t = src.replace(ANCIEN_CONTENEUR, NOUVEAU_CONTENEUR, 1)
        if not simuler:
            ecrire(chemin, t)
        faits += 1
    print("conteneurs convertis : %d%s" % (faits,
                                           "  [SIMULATION]" if simuler else ""))
    if sans_objet:
        print("pages non converties : %d" % len(sans_objet))
        for nom, motif in sans_objet:
            print("   %-32s %s" % (nom, motif))
    if faits == 0:
        echec("aucun conteneur converti -- motif absent ou deja applique")
    return 0


def calage_mobilier(depot, simuler):
    """Pose --mobilier-largeur sur chaque page, a la valeur MESUREE.

    Arbitrage AH du 22/07/2026 (option B) : le mobilier se cale sur la colonne
    editoriale de sa page. La valeur ne se devine pas -- elle vient de
    `sonde-mobilier.py`, qui l'a mesuree au rendu reel. Une page dont la
    colonne n'etait pas mesurable, ou qui declare son propre `.wrap`, n'est
    PAS touchee : on ne pose pas une valeur qu'on n'a pas constatee.
    """
    import json
    mesures = os.path.join(depot, "outils", "recette-playwright", "resultats",
                           "mobilier.json")
    if not os.path.isfile(mesures):
        echec("mesures absentes : jouer d'abord sonde-mobilier.py (%s)"
              % mesures)
    with io.open(mesures, "r", encoding="utf-8") as f:
        donnees = json.load(f)

    poses, ignorees = 0, []
    for m in donnees:
        if not m.get("largeur_proposee_rem"):
            ignorees.append((m["page"], m.get("motif", "sans mesure")))
            continue
        chemin = os.path.join(depot, "films", m["page"])
        src = lire(chemin)
        if "--mobilier-largeur" in src:
            # Une mesure plus juste remplace une mesure plus ancienne : la
            # valeur suit le constat, elle ne se fige pas au premier passage.
            attendue = "--mobilier-largeur:%srem;" % m["largeur_proposee_rem"]
            if attendue in src:
                ignorees.append((m["page"], "deja calee a la bonne valeur"))
                continue
            t = re.sub(r"--mobilier-largeur:\s*[0-9.]+rem;", attendue, src)
            if t == src:
                echec("%s : valeur non remplacee" % m["page"])
            if not simuler:
                ecrire(chemin, t)
            poses += 1
            continue
        # La variable se pose sur :root de la page, la ou vit sa palette.
        ancre = ":root{"
        if ancre not in src:
            ancre = ":root {"
        if ancre not in src:
            # Page sans feuille propre (annie-hall) : il n'existe aucun :root
            # ou loger la variable, et on n'invente pas un bloc <style> pour
            # une page qui a fait le choix de n'en pas avoir. La valeur se
            # pose sur le conteneur lui-meme -- meme mecanisme, autre porteur.
            if NOUVEAU_CONTENEUR not in src:
                ignorees.append((m["page"],
                                 "ni :root ni conteneur de mobilier"))
                continue
            inline = ('<div class="mobilier-wrap" '
                      'style="--mobilier-largeur:%srem;padding-top:1.6rem;">'
                      % m["largeur_proposee_rem"])
            t = src.replace(NOUVEAU_CONTENEUR, inline, 1)
            if t == src:
                echec("%s : la variable n'a pas ete posee en ligne" % m["page"])
            if not simuler:
                ecrire(chemin, t)
            poses += 1
            continue
        declaration = (
            "\n    /* Largeur du mobilier partage (cartouche, bandeau de\n"
            "       variante), calee sur la colonne editoriale MESUREE de\n"
            "       cette page (%d px au rendu). Arbitrage AH du 22/07/2026,\n"
            "       option B : le mobilier suit le texte, pas le menu. */\n"
            "    --mobilier-largeur:%srem;\n" % (m["colonne_px"],
                                                 m["largeur_proposee_rem"]))
        t = src.replace(ancre, ancre + declaration, 1)
        if t == src:
            echec("%s : la variable n'a pas ete posee" % m["page"])
        if not simuler:
            ecrire(chemin, t)
        poses += 1

    print("variables posees : %d%s" % (poses,
                                       "  [SIMULATION]" if simuler else ""))
    print("pages ignorees   : %d" % len(ignorees))
    for nom, motif in ignorees:
        print("   %-32s %s" % (nom, motif))
    if poses == 0:
        echec("aucune variable posee -- rien a faire ou mesures perimees")
    return 0


REGLES = {"collision-waterloo": collision_waterloo,
          "classe-mobilier": classe_mobilier,
          "calage-mobilier": calage_mobilier}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--regle", required=True, choices=sorted(REGLES))
    ap.add_argument("--depot", default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    ap.add_argument("--simuler", action="store_true")
    args = ap.parse_args()
    return REGLES[args.regle](args.depot, args.simuler)


if __name__ == "__main__":
    sys.exit(main())
