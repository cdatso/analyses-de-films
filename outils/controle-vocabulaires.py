#!/usr/bin/env python3
# -*- coding: ascii -*-
"""controle-vocabulaires.py -- garde-fou mecanique des axes fermes (P-10).

SPEC-SITE-V2 section 4.3. Toute valeur d'un axe ferme absente du vocabulaire EMPECHE
la publication : ce script sort en code non nul et NOMME la valeur fautive.
Modele : controle-glyphes.py. Python stdlib, ASCII pur, aucun fichier modifie.

Les deux fichiers sont du JavaScript ; ils sont lus par expression reguliere,
sans moteur JS. C'est suffisant parce que le registre est de la donnee
declarative (P-31 : rien n'est compile, tout est lisible tel quel).

Usage :
    python controle-vocabulaires.py [--depot CHEMIN] [--strict] [--autotest]

  --strict   : une entree a laquelle il manque un champ obligatoire du
               schema v2 (annexe B) est une faute. Sans cette option, les
               entrees non encore migrees sont comptees et tolerees --
               le retrofit de masse est le perimetre de BKL-065-5.
  --autotest : injecte une valeur inventee dans une copie EN MEMOIRE du
               registre et verifie que le controle la rejette. C'est la
               verification de P-10 elle-meme ; le depot n'est pas touche.

Codes de sortie : 0 conforme -- 1 valeur hors vocabulaire (ou champ manquant
en --strict) -- 2 fichier introuvable ou illisible.
"""

import argparse
import os
import re
import sys

OBLIGATOIRES_V2 = ["volet", "datePublication", "pays", "genreBase",
                   "technique", "producteur"]


def lire(chemin):
    with open(chemin, "r", encoding="utf-8") as f:
        return f.read()


def liste_js(source, nom):
    """Extrait un tableau de chaines.

    Accepte les deux formes du fichier : `nom: [...]` (propriete d'objet) et
    `const nom = [...]` (declaration). Confondre les deux faisait lire une
    liste d'axes bloquants VIDE -- donc un controle qui ne controlait rien
    tout en sortant en code 0. Detecte par l'autotest, ce qui est exactement
    sa raison d'etre.
    """
    m = re.search(re.escape(nom) + r"\s*[:=]\s*\[(.*?)\]", source, re.S)
    if not m:
        return None
    return [a or b for a, b in re.findall(r"'([^']*)'|\"([^\"]*)\"", m.group(1))]


def charge_vocabulaires(chemin):
    src = lire(chemin)
    bloc = re.search(r"VOCABULAIRES\s*=\s*\{(.*?)\n\};", src, re.S)
    if not bloc:
        raise ValueError("bloc VOCABULAIRES introuvable")
    corps = bloc.group(1)
    vocs = {}
    for nom in re.findall(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*:\s*\[", corps, re.M):
        vocs[nom] = liste_js(corps, nom) or []
    axes = liste_js(src, "AXES_BLOQUANTS") or []
    return vocs, axes


def decoupe_entrees(source):
    """Retourne la liste des blocs texte de chaque objet du tableau FILMS."""
    debut = source.find("const FILMS")
    if debut < 0:
        raise ValueError("tableau FILMS introuvable")
    corps = source[debut:]
    entrees, profondeur, courant = [], 0, []
    for ch in corps:
        if ch == "{":
            profondeur += 1
            if profondeur == 1:
                courant = []
                continue
        elif ch == "}":
            profondeur -= 1
            if profondeur == 0:
                entrees.append("".join(courant))
                continue
        if profondeur >= 1:
            courant.append(ch)
    return entrees


def champ(bloc, nom):
    """Valeur d'un champ : chaine -> str, tableau -> list, absent -> None."""
    m = re.search(re.escape(nom) + r"\s*:\s*\[(.*?)\]", bloc, re.S)
    if m:
        return [a or b for a, b in
                re.findall(r"'([^']*)'|\"([^\"]*)\"", m.group(1))]
    m = re.search(re.escape(nom) + r"\s*:\s*'([^']*)'", bloc)
    if m:
        return m.group(1)
    m = re.search(re.escape(nom) + r'\s*:\s*"([^"]*)"', bloc)
    if m:
        return m.group(1)
    return None


def controle(entrees, vocs, axes, strict):
    fautes, incompletes, migrees = [], [], 0
    for bloc in entrees:
        slug = champ(bloc, "slug") or "(sans slug)"
        manquants = [c for c in OBLIGATOIRES_V2 if champ(bloc, c) is None]
        if len(manquants) == len(OBLIGATOIRES_V2):
            incompletes.append((slug, "entree non migree (schema v1)"))
            continue
        if manquants:
            incompletes.append((slug, "champs absents : " + ", ".join(manquants)))
        else:
            migrees += 1
        for axe in axes:
            v = champ(bloc, axe)
            if v is None:
                continue
            valeurs = v if isinstance(v, list) else [v]
            for val in valeurs:
                if val not in vocs.get(axe, []):
                    fautes.append((slug, axe, val))
    if strict:
        fautes.extend((s, "schema", m) for s, m in incompletes)
    return fautes, incompletes, migrees


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depot", default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--autotest", action="store_true")
    args = ap.parse_args()

    f_registre = os.path.join(args.depot, "assets", "films-data.js")
    f_vocs = os.path.join(args.depot, "assets", "vocabulaires.js")
    for f in (f_registre, f_vocs):
        if not os.path.isfile(f):
            sys.stderr.write("Introuvable : %s\n" % f)
            return 2

    vocs, axes = charge_vocabulaires(f_vocs)
    source = lire(f_registre)
    entrees = decoupe_entrees(source)

    print("Registre  : %s" % f_registre)
    print("Vocabulaires : %s" % f_vocs)
    print("Axes bloquants : %s" % ", ".join(axes))
    print("Entrees : %d, dont %d au schema v2" % (
        len(entrees), sum(1 for b in entrees if champ(b, "volet") is not None)))
    print("")

    if args.autotest:
        # Verification de P-10 : le controle DOIT rejeter une valeur inventee.
        # L'injection se fait sur une copie en memoire ; le depot est intact.
        faux = list(entrees)
        faux.append("slug: 'autotest', volet: 'critique', datePublication: '2026-01-01 00:00', "
                    "pays: ['Atlantide'], genreBase: 'melodrame', "
                    "technique: ['couleur'], producteur: 'non specifie'")
        f2, _i2, _m2 = controle(faux, vocs, axes, args.strict)
        attendu = [x for x in f2 if x[2] == "Atlantide"]
        if not attendu:
            print("AUTOTEST ECHOUE : la valeur inventee n'a pas ete rejetee.")
            return 1
        print("AUTOTEST : valeur inventee 'Atlantide' rejetee sur l'axe '%s'."
              % attendu[0][1])
        print("           P-10 verifiee -- le depot n'a pas ete modifie.")
        print("")

    fautes, incompletes, migrees = controle(entrees, vocs, axes, args.strict)

    if incompletes:
        print("Entrees non conformes au schema v2 (tolerees hors --strict) : %d"
              % len(incompletes))
        for slug, motif in incompletes[:5]:
            print("  - %-28s %s" % (slug, motif))
        if len(incompletes) > 5:
            print("  ... et %d autres" % (len(incompletes) - 5))
        print("")

    if fautes:
        print("ECHEC : %d valeur(s) hors vocabulaire." % len(fautes))
        for slug, axe, val in fautes:
            print("  - entree '%s', axe '%s' : valeur '%s' absente du vocabulaire"
                  % (slug, axe, val))
        return 1

    print("CONFORME : aucune valeur hors vocabulaire sur %d entree(s) migree(s)."
          % migrees)
    return 0


if __name__ == "__main__":
    sys.exit(main())
