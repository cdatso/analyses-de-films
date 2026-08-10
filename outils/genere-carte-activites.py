#!/usr/bin/env python3
# -*- coding: ascii -*-
"""genere-carte-activites.py -- dispositif anti-peremption de la carte des
activites (premiere page technique du site, arbitrage AH du 10/08/2026,
question 3).

Meme patron que outils/genere-liste-statique.py : marqueurs dedies,
regeneration EN MEMOIRE pour --verifier, codes de sortie 0/1/2. La
difference tient au partage des roles entre les deux sources :

  - les NOMBRES PROUVABLES (analyses publiees, pages publiees au total) sont
    COMPTES ICI, dans ce script, par une lecture directe du depot du site --
    jamais ecrits a la main, jamais lus dans la maquette Design qui a inspire
    cette page (ses propres chiffres sont perimes des sa capture, voir le
    mandat) ;
  - les STATUTS (En cours / En vigueur / Termine / Gele) et leurs libelles
    FR+EN viennent du fichier de donnees versionne
    outils/carte-activites-donnees.json, sous UNE DATE D'ETAT obligatoire :
    ce script REFUSE DE RENDRE si une date manque ;
  - les chiffres de GOUVERNANCE (regles de la charte, prescriptions de la
    spec) ne sont comptes NULLE PART ici : leur source vit dans un depot
    prive, hors d'atteinte de tout outil du depot public -- ils s'enoncent
    sans chiffre dans les textes du fichier de donnees.

Deux pages rendues, meme gabarit de marqueurs, un jeu de donnees commun :
    carte-des-activites.html       (lang=fr)
    en/carte-des-activites.html    (lang=en)

Usage : python genere-carte-activites.py [--depot CHEMIN] [--verifier]
Codes : 0 conforme -- 1 derive, marqueur absent ou date d'etat manquante --
        2 fichier introuvable.
"""

import argparse
import io
import json
import os
import sys

DEBUT = "<!-- CARTE-ACTIVITES:DEBUT (genere par outils/genere-carte-activites.py) -->"
FIN = "<!-- CARTE-ACTIVITES:FIN -->"

# Repertoires hors publication -- meme perimetre que le generateur de sitemap
# du depot (mandat voisin et independant : cette liste est ecrite ICI, sans
# dependre de son outillage, non gate a ce jour). .git est le depot lui-meme, _scratch le
# vivier du vif, outils/docs/assets ne portent aucune page publiee.
EXCLUS = set(["_scratch", ".git", "outils", "assets", "docs"])

# Libelles fixes de la legende a 4 statuts (maquette DES-001, arbitrage AH du
# 10/08 sur la traduction EN de "Gele / en attente" -> "On hold"). Accents en
# entites HTML : le SOURCE de ce script reste ASCII pur (patron etabli par
# genere-liste-statique.py) ; les textes qui viennent du fichier de donnees,
# eux, portent leurs accents en UTF-8 normal.
STATUTS = {
    "en-cours": {
        "classe": "en-cours", "fr": "En cours", "en": "Ongoing"},
    "en-vigueur-place": {
        "classe": "en-vigueur-place",
        "fr": "En vigueur / en place", "en": "In force / in place"},
    "termine": {
        "classe": "termine", "fr": "Termin&eacute;", "en": "Completed"},
    "gele": {
        "classe": "gele",
        "fr": "Gel&eacute; / en attente", "en": "On hold"},
}

MOIS_EN = ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"]


def lire(chemin):
    with io.open(chemin, "r", encoding="utf-8") as f:
        return f.read()


def ecrire(chemin, texte):
    with io.open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(texte)


def echappe(s):
    """Meme echappement que genere-liste-statique.py : & < > " et rien d'autre."""
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def formate_date(iso, lang):
    annee, mois, jour = iso.split("-")
    if lang == "fr":
        return "%s/%s/%s" % (jour, mois, annee)
    return "%s %s %s" % (int(jour), MOIS_EN[int(mois) - 1], annee)


def libelle_date(iso, lang):
    if lang == "fr":
        return "&Eacute;tat au %s" % formate_date(iso, "fr")
    return "As of %s" % formate_date(iso, "en")


def compte_analyses(depot):
    """Nombre PROUVABLE d'analyses publiees -- une page par film, dans films/."""
    dossier = os.path.join(depot, "films")
    if not os.path.isdir(dossier):
        return 0
    return len([f for f in os.listdir(dossier) if f.endswith(".html")])


def compte_pages(depot):
    """Nombre PROUVABLE de pages HTML publiees, tout le depot, hors EXCLUS."""
    total = 0
    for racine, sousrepertoires, fichiers in os.walk(depot):
        rel = os.path.relpath(racine, depot)
        rel = "" if rel == "." else rel.replace(os.sep, "/")
        sommet = rel.split("/")[0] if rel else ""
        if sommet in EXCLUS:
            sousrepertoires[:] = []
            continue
        sousrepertoires[:] = [d for d in sousrepertoires if d not in EXCLUS]
        total += len([f for f in fichiers if f.endswith(".html")])
    return total


def valide_dates(donnees):
    """Rend la liste des activites sans date d'etat -- vide si tout est en regle."""
    manquants = []
    for groupe in donnees["groupes"]:
        for a in groupe["activites"]:
            if not a.get("date_etat"):
                manquants.append("%s/%s" % (groupe["id"], a["id"]))
    for a in donnees["run"]["activites"]:
        if not a.get("date_etat"):
            manquants.append("run/%s" % a["id"])
    return manquants


def etat_html(statut, lang):
    info = STATUTS[statut]
    return '<span class="etat etat-%s">%s</span>' % (info["classe"], info[lang])


def item_html(item, lang, conteneur):
    libelle = echappe(item["libelle_%s" % lang])
    description = echappe(item["description_%s" % lang])
    date_lbl = libelle_date(item["date_etat"], lang)
    return (
        '        <%s class="activite">\n'
        '          <div class="activite-ligne">\n'
        '            <h3>%s</h3>\n'
        '            %s\n'
        '          </div>\n'
        '          <p class="activite-description">%s</p>\n'
        '          <p class="activite-date">%s</p>\n'
        '        </%s>' % (conteneur, libelle, etat_html(item["statut"], lang),
                            description, date_lbl, conteneur)
    )


def groupe_html(groupe, lang):
    items = "\n".join(item_html(a, lang, "li") for a in groupe["activites"])
    return (
        '      <section class="grappe">\n'
        '        <div class="grappe-entete">\n'
        '          <h2>%s</h2>\n'
        '          <p>%s</p>\n'
        '        </div>\n'
        '        <ul class="grappe-items">\n'
        '%s\n'
        '        </ul>\n'
        '      </section>' % (echappe(groupe["libelle_%s" % lang]),
                               echappe(groupe["soustitre_%s" % lang]), items)
    )


def run_html(run, lang):
    cases = "\n".join(item_html(a, lang, "div") for a in run["activites"])
    return (
        '    <section class="run">\n'
        '      <div class="run-entete">\n'
        '        <h2>%s</h2>\n'
        '        <p>%s</p>\n'
        '      </div>\n'
        '      <div class="run-grille">\n'
        '%s\n'
        '      </div>\n'
        '    </section>' % (echappe(run["libelle_%s" % lang]),
                             echappe(run["soustitre_%s" % lang]), cases)
    )


def central_html(central, lang, na, npages):
    phrase = central["phrase_%s" % lang].format(analyses=na, pages=npages)
    return (
        '    <div class="noeud-central">\n'
        '      <div class="noeud-surtitre">%s</div>\n'
        '      <div class="noeud-titre">%s</div>\n'
        '      <p class="noeud-phrase">%s</p>\n'
        '      <div class="noeud-note">%s</div>\n'
        '    </div>' % (echappe(central["surtitre_%s" % lang]),
                         echappe(central["titre_%s" % lang]), echappe(phrase),
                         echappe(central["note_%s" % lang]))
    )


def legende_html(lang):
    ordre = ["en-cours", "en-vigueur-place", "termine", "gele"]
    spans = "\n".join(
        '      <span class="etat etat-%s">%s</span>'
        % (STATUTS[k]["classe"], STATUTS[k][lang]) for k in ordre)
    label = "L&eacute;gende des statuts" if lang == "fr" else "Status legend"
    return '    <div class="carte-legende" role="note" aria-label="%s">\n%s\n    </div>' % (
        label, spans)


def bloc(donnees, lang, na, npages):
    parties = [
        legende_html(lang),
        central_html(donnees["central"], lang, na, npages),
        '    <div class="grappes">',
    ]
    parties.extend(groupe_html(g, lang) for g in donnees["groupes"])
    parties.append('    </div>')
    parties.append(run_html(donnees["run"], lang))
    return DEBUT + "\n" + "\n".join(parties) + "\n    " + FIN


def applique(chemin, contenu):
    src = lire(chemin)
    i, j = src.find(DEBUT), src.find(FIN)
    if i < 0 or j < 0:
        sys.stderr.write("Marqueurs absents dans %s\n" % chemin)
        return None, None
    neuf = src[:i] + contenu + src[j + len(FIN):]
    return src, neuf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depot", default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    ap.add_argument("--verifier", action="store_true")
    args = ap.parse_args()

    depot = args.depot
    chemin_donnees = os.path.join(depot, "outils", "carte-activites-donnees.json")
    if not os.path.isfile(chemin_donnees):
        sys.stderr.write("Introuvable : %s\n" % chemin_donnees)
        return 2

    donnees = json.loads(lire(chemin_donnees))

    manquants = valide_dates(donnees)
    if manquants:
        sys.stderr.write(
            "Date d'etat manquante pour : %s\n" % ", ".join(manquants))
        sys.stderr.write(
            "Le generateur refuse de rendre sans date (arbitrage AH du "
            "10/08/2026, question 3).\n")
        return 1

    na = compte_analyses(depot)
    npages = compte_pages(depot)

    pages = [("carte-des-activites.html", "fr"),
             (os.path.join("en", "carte-des-activites.html"), "en")]

    code = 0
    for rel, lang in pages:
        chemin = os.path.join(depot, rel)
        if not os.path.isfile(chemin):
            sys.stderr.write("Introuvable : %s\n" % chemin)
            return 2
        contenu = bloc(donnees, lang, na, npages)
        src, neuf = applique(chemin, contenu)
        if src is None:
            return 1
        if args.verifier:
            etat = "conforme" if src == neuf else "DERIVE"
            if src != neuf:
                code = 1
            print("%-28s %-9s %d analyses, %d pages" % (rel, etat, na, npages))
        else:
            if src != neuf:
                ecrire(chemin, neuf)
            print("%-28s ecrit -- %d analyses, %d pages" % (rel, na, npages))

    if args.verifier and code == 0:
        print("")
        print("Aucune derive entre le gabarit du script et le HTML du depot.")
    elif args.verifier:
        print("")
        print("DERIVE : le HTML ne correspond plus aux donnees. Regenerer.")
    return code


if __name__ == "__main__":
    sys.exit(main())
