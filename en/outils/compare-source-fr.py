#!/usr/bin/env python3
# -*- coding: ascii -*-
"""compare-source-fr.py -- controle de FRAICHEUR des pages de l'arbre /en/.

Socle i18n, BKL-CIN-085 lot L1 (analyse 5.2 point 5 : "le seul remede a la
derive"). Cet outil COMPTE et SIGNALE, il ne corrige RIEN et ne retraduit
rien : reactualiser une page EN est un geste editorial, jamais un automatisme.

PRINCIPE
  Chaque page de en/ porte, juste apres son <!DOCTYPE>, un marqueur :

      <!-- source-fr: <fichier-fr> <sha40> -->

  <sha40> est le commit qui touchait la page FR jumelle la derniere fois que
  la page EN a ete ecrite ou revue. Si la jumelle a bouge depuis, la page EN
  est peut-etre perimee -- et personne ne le saurait sans ce marqueur, une
  page anglaise n'ayant aucun moyen de crier qu'elle a vieilli.

POURQUOI LE BLOC GENERE EST IGNORE (arbitrage AH du 05/08/2026, elicitation
du mandat (b), question 5)
  index.html, critiques.html et etudes.html sont REECRITES a chaque
  publication par outils/genere-liste-statique.py, qui reinjecte la liste du
  corpus entre <!-- LISTE-STATIQUE:DEBUT --> et <!-- LISTE-STATIQUE:FIN -->.
  Leur sha bouge donc a chaque film, sans que rien de ce que la page EN
  reprend n'ait change. Compare betement, ce controle signalerait une derive
  apres CHAQUE publication -- et un garde-fou qui alerte toujours cesse
  d'etre lu.
  La comparaison porte donc sur le contenu de la page FR PRIVE de ce bloc,
  aux deux versions. Un changement entierement contenu dans la liste generee
  est classe COSMETIQUE et ne fait pas echouer le controle ; le marqueur peut
  alors etre reestampille a l'occasion, sans urgence.
  COUPLAGE ASSUME : cet outil connait les marqueurs du generateur. Si leur
  libelle change dans outils/genere-liste-statique.py, il change ici aussi.

USAGE
    python en/outils/compare-source-fr.py [--depot CHEMIN] [--reestampille]

  --reestampille : met a jour les sha des marqueurs a l'etat courant du
    depot, et n'ecrit RIEN d'autre. A jouer apres avoir revu une page EN,
    ou apres une derive jugee cosmetique. Sans ce drapeau, aucun fichier
    n'est modifie.

CODES DE SORTIE
    0 -- toutes les pages EN sont a jour (ou seule la liste generee a bouge)
    1 -- au moins une page EN est DERIVEE, ou son marqueur manque/est illisible
    2 -- le controle n'a pas pu etre fait (hors depot git, git absent...)
"""

import argparse
import os
import re
import subprocess
import sys

RE_MARQUEUR = re.compile(
    r"<!--\s*source-fr:\s*(?P<fichier>[^\s]+)\s+(?P<sha>[0-9a-f]{7,40})\s*-->")
RE_LISTE_GENEREE = re.compile(
    r"<!--\s*LISTE-STATIQUE:DEBUT.*?LISTE-STATIQUE:FIN\s*-->", re.S)


def git(depot, *args):
    """Retourne (code, sortie). Jamais d'exception : le controle rend un
    verdict, il ne casse pas."""
    try:
        p = subprocess.run(["git", "-C", depot] + list(args),
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
        return p.returncode, p.stdout
    except (OSError, ValueError) as exc:
        return 127, str(exc)


def sans_liste_generee(contenu):
    """Retire le bloc reinjecte a chaque publication (voir l'en-tete)."""
    return RE_LISTE_GENEREE.sub("", contenu)


def sha_courant(depot, fichier_fr):
    code, sortie = git(depot, "log", "-1", "--format=%H", "--", fichier_fr)
    return sortie.strip() if code == 0 else ""


def contenu_a(depot, sha, fichier_fr):
    code, sortie = git(depot, "show", "%s:%s" % (sha, fichier_fr))
    return sortie if code == 0 else None


def examine(depot, page_en):
    """Retourne un dict de verdict pour une page de en/."""
    chemin = os.path.join(depot, page_en)
    with open(chemin, "r", encoding="utf-8") as f:
        tete = f.read(4096)

    m = RE_MARQUEUR.search(tete)
    if not m:
        return {"page": page_en, "etat": "MARQUEUR ABSENT", "grave": True,
                "detail": "aucun <!-- source-fr: ... --> dans les 4 premiers Ko"}

    fichier_fr, sha_pose = m.group("fichier"), m.group("sha")

    if not os.path.isfile(os.path.join(depot, fichier_fr)):
        return {"page": page_en, "etat": "JUMELLE INTROUVABLE", "grave": True,
                "detail": fichier_fr}

    actuel = sha_courant(depot, fichier_fr)
    if not actuel:
        return {"page": page_en, "etat": "SANS HISTORIQUE", "grave": True,
                "detail": "git ne connait aucun commit pour %s" % fichier_fr}

    if actuel.startswith(sha_pose) or sha_pose.startswith(actuel[:len(sha_pose)]):
        return {"page": page_en, "etat": "A JOUR", "grave": False,
                "detail": "%s @ %s" % (fichier_fr, actuel[:10])}

    # La jumelle a bouge. Reste a savoir si c'est ailleurs que dans la liste
    # generee -- seul cas qui engage une relecture de la page anglaise.
    avant = contenu_a(depot, sha_pose, fichier_fr)
    apres = contenu_a(depot, actuel, fichier_fr)
    if avant is None or apres is None:
        return {"page": page_en, "etat": "DERIVEE", "grave": True,
                "detail": "%s a bouge (%s -> %s) ; contenu d'origine illisible,"
                          " comparaison impossible"
                          % (fichier_fr, sha_pose[:10], actuel[:10])}

    if sans_liste_generee(avant) == sans_liste_generee(apres):
        return {"page": page_en, "etat": "COSMETIQUE", "grave": False,
                "detail": "%s : seule la liste generee a bouge (%s -> %s) --"
                          " reestampille quand tu veux"
                          % (fichier_fr, sha_pose[:10], actuel[:10])}

    code, journal = git(depot, "log", "--oneline",
                        "%s..%s" % (sha_pose, actuel), "--", fichier_fr)
    commits = [l for l in journal.splitlines() if l.strip()]
    return {"page": page_en, "etat": "DERIVEE", "grave": True,
            "detail": "%s a change hors de la liste generee : %d commit(s)"
                      " depuis %s" % (fichier_fr, len(commits), sha_pose[:10]),
            "commits": commits}


def reestampille(depot, page_en):
    chemin = os.path.join(depot, page_en)
    with open(chemin, "r", encoding="utf-8") as f:
        contenu = f.read()
    m = RE_MARQUEUR.search(contenu)
    if not m:
        return False
    actuel = sha_courant(depot, m.group("fichier"))
    if not actuel or actuel == m.group("sha"):
        return False
    neuf = "<!-- source-fr: %s %s -->" % (m.group("fichier"), actuel)
    contenu = contenu[:m.start()] + neuf + contenu[m.end():]
    with open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(contenu)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depot", default=os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    ap.add_argument("--reestampille", action="store_true")
    args = ap.parse_args()

    depot = os.path.abspath(args.depot)
    arbre_en = os.path.join(depot, "en")
    if not os.path.isdir(arbre_en):
        sys.stderr.write("Arbre en/ introuvable sous %s\n" % depot)
        return 2
    if git(depot, "rev-parse", "--git-dir")[0] != 0:
        sys.stderr.write("%s n'est pas un depot git utilisable.\n" % depot)
        return 2

    pages = sorted("en/" + n for n in os.listdir(arbre_en)
                   if n.endswith(".html"))
    if not pages:
        sys.stderr.write("Aucune page .html dans en/ -- rien a controler.\n")
        return 2

    if args.reestampille:
        touchees = [p for p in pages if reestampille(depot, p)]
        print("Reestampillage : %d page(s) mise(s) a jour%s"
              % (len(touchees), (" : " + ", ".join(touchees)) if touchees else ""))
        return 0

    verdicts = [examine(depot, p) for p in pages]
    largeur = max(len(v["page"]) for v in verdicts)

    print("# Fraicheur de l'arbre /en/ -- socle i18n (BKL-CIN-085)")
    print("")
    for v in verdicts:
        print("  %-*s  %-18s  %s" % (largeur, v["page"], v["etat"], v["detail"]))
        for c in v.get("commits", []):
            print("  %-*s    %s" % (largeur, "", c))
    print("")

    graves = [v for v in verdicts if v["grave"]]
    print("%d page(s) controlee(s), %d a revoir." % (len(verdicts), len(graves)))
    if graves:
        print("")
        print("Une page DERIVEE n'est pas retraduite par cet outil : sa reprise")
        print("est un geste editorial, et la revue d'AH lui reste due.")
        print("Une fois la page EN revue, rejoue avec --reestampille.")
    return 1 if graves else 0


if __name__ == "__main__":
    sys.exit(main())
