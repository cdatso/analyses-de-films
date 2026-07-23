#!/usr/bin/env python3
# -*- coding: ascii -*-
"""genere-liste-statique.py -- la liste du corpus, ecrite en dur (option b).

GATE AH du 22/07/2026 08h24, relaye dans la fenetre du prototype : la liste
complete du corpus est rendue EN DUR dans le HTML ; le JavaScript ne fait plus
que la FILTRER. Sans JS, on voit tout -- simplement non filtrable.

Frontiere P-31, telle que ratifiee le 21/07 : ce que la regle proscrit est une
transformation AU DEPLOIEMENT, pas un fichier genere AVANT commit, versionne et
lisible tel quel. La liste produite ici est du HTML ordinaire, relisible dans
le depot, servi sans aucune etape intermediaire.

Le risque de ce dispositif est la DERIVE entre deux gabarits -- celui de ce
script et celui de corpus.js. D'ou le mode --verifier : il regenere en memoire
et compare a ce qui est sur le disque. Toute divergence sort en code non nul.
C'est le controle a rejouer en recette.

Usage : python genere-liste-statique.py [--depot CHEMIN] [--verifier]
Codes : 0 conforme -- 1 derive ou marqueur absent -- 2 fichier introuvable.
"""

import argparse
import io
import os
import re
import sys

DEBUT = "<!-- LISTE-STATIQUE:DEBUT (genere par outils/genere-liste-statique.py) -->"
FIN = "<!-- LISTE-STATIQUE:FIN -->"

# Les trois pages qui rendent le meme composant (P-07), et leur filtre.
PAGES = [
    ("index.html", None),
    ("critiques.html", "critique"),
    ("etudes.html", "etude"),
]

# Meme table d'etiquettes que corpus.js. Toute valeur absente prend une
# majuscule initiale.
ETIQUETTES = {
    "critique": "Critiques", "etude": "&Eacute;tudes", "n&b": "N&amp;B",
    # Les identifiants du vocabulaire sont sans accent -- c'est ce qui les rend
    # stables et comparables. L'accent est une affaire d'affichage. Cette table
    # doit rester identique a celle de assets/corpus.js.
    "melodrame": "M&eacute;lodrame", "comedie": "Com&eacute;die",
    "tragedie": "Trag&eacute;die",
    "Etats-Unis": "&Eacute;tats-Unis",
    "Union sovietique": "Union sovi&eacute;tique",
}


def lire(chemin):
    with io.open(chemin, "r", encoding="utf-8") as f:
        return f.read()


def ecrire(chemin, texte):
    with io.open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(texte)


def echappe(s):
    """Meme echappement que corpus.js : & < > " et rien d'autre."""
    if s is None:
        return ""
    return (unicode_str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def unicode_str(s):
    return s if isinstance(s, type(u"")) else u"%s" % s


def etiquette(v):
    """Rend du HTML PRET A POSER -- deja echappe, entites comprises.

    Piege evite : les valeurs de la table portent des entites (&eacute;). Les
    repasser dans echappe() transformerait leur & en &amp; et afficherait
    litteralement "M&eacute;lodrame". La table est donc rendue telle quelle,
    et seules les valeurs absentes de la table sont echappees.
    """
    if v in ETIQUETTES:
        return ETIQUETTES[v]
    v = unicode_str(v)
    return echappe(v[:1].upper() + v[1:])


# Repli des diacritiques -- MEME table que la constante PLI de corpus.js.
# Ecrite en points de code : le fichier reste ASCII pur, et la table reste
# lisible caractere par caractere. Elle sert a deux choses, la recherche
# (cote JS) et la CLE DE TRI (des deux cotes) : c'est elle qui garantit que le
# HTML statique sort dans exactement l'ordre que produira le script.
_ACCENTUES = (u"\u00e0\u00e2\u00e4\u00e3\u00e5\u00e1\u00e7\u00e9\u00e8\u00ea"
              u"\u00eb\u00ee\u00ef\u00ec\u00ed\u00f1\u00f4\u00f6\u00f2\u00f3"
              u"\u00f5\u00f8\u00f9\u00fb\u00fc\u00fa\u00ff\u00fd")
_PLATS = u"aaaaaaceeeeiiiinoooooouuuuyy"
PLI = dict(zip(_ACCENTUES, _PLATS))
PLI[u"\u0153"] = u"oe"   # oe lie
PLI[u"\u00e6"] = u"ae"   # ae lie




def norm(s):
    s = unicode_str(s or u"").lower()
    return u"".join(PLI.get(c, c) for c in s)


def ordre_catalogue(f):
    """Ordre du catalogue : alphabetique par titre replie.

    Voir corpus.js pour le motif. Les articles initiaux ne sont pas escamotes.
    Le titre brut sert de departage, pour que deux titres de meme repli aient
    un ordre stable et identique des deux cotes.
    """
    return (norm(f["title"]), unicode_str(f["title"] or u""))


def decoupe_entrees(source):
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
                entrees.append(u"".join(courant))
                continue
        if profondeur >= 1:
            courant.append(ch)
    return entrees


def champ(bloc, nom):
    m = re.search(re.escape(nom) + r"\s*:\s*\[(.*?)\]", bloc, re.S)
    if m:
        return [a or b for a, b in
                re.findall(r"'([^']*)'|\"([^\"]*)\"", m.group(1))]
    for motif in (r"\s*:\s*'((?:[^'\\]|\\.)*)'", r'\s*:\s*"((?:[^"\\]|\\.)*)"'):
        m = re.search(re.escape(nom) + motif, bloc)
        if m:
            return m.group(1).replace("\\'", "'").replace('\\"', '"')
    m = re.search(re.escape(nom) + r"\s*:\s*(\d+)", bloc)
    if m:
        return int(m.group(1))
    return None


def entree(bloc):
    return {
        "slug": champ(bloc, "slug"),
        "title": champ(bloc, "title"),
        "director": champ(bloc, "director"),
        "year": champ(bloc, "year"),
        "url": champ(bloc, "url"),
        "genre": champ(bloc, "genre"),
        "genreBase": champ(bloc, "genreBase"),
        "volet": champ(bloc, "volet") or "critique",
        "datePublication": champ(bloc, "datePublication"),
    }


def cle_tri(f):
    """Meme ordre que corpus.js : datees d'abord, date puis titre decroissants.

    Python trie en ordre croissant ; on inverse en negativant les rangs, ce que
    des chaines ne permettent pas -- d'ou le passage par un tri stable en deux
    temps dans derniere_publiee().
    """
    return (0 if f["datePublication"] else 1,
            f["datePublication"] or "", f["title"] or "")


def derniere_publiee(films):
    dates = [f for f in films if f["datePublication"]]
    if not dates:
        return None
    dates.sort(key=lambda f: (f["datePublication"], f["title"]), reverse=True)
    return dates[0]


def li(f, derniere):
    marq = ('<span class="marq">&Eacute;tude</span>'
            if f["volet"] == "etude" else "")
    neuf = ('<span class="neuf">derni&egrave;re publi&eacute;e</span>'
            if derniere and f["slug"] == derniere["slug"] else "")
    if f["genreBase"]:
        suite = u" &mdash; " + etiquette(f["genreBase"])
    elif f["genre"]:
        suite = u" &mdash; " + echappe(f["genre"])
    else:
        suite = u""
    return (u'      <li><a class="entree" href="%s" data-volet="%s">'
            u'<span class="t">%s%s%s</span>'
            u'<span class="a">%s</span>'
            u'<span class="d">%s%s</span>'
            u'</a></li>'
            % (echappe(f["url"]), f["volet"], echappe(f["title"]), marq, neuf,
               f["year"] or "", echappe(f["director"]), suite))


def bloc(films, filtre, derniere):
    vus = [f for f in films if filtre is None or f["volet"] == filtre]
    return DEBUT + u"\n" + u"\n".join(li(f, derniere) for f in vus) + u"\n    " + FIN


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

    registre = os.path.join(args.depot, "assets", "films-data.js")
    if not os.path.isfile(registre):
        sys.stderr.write("Introuvable : %s\n" % registre)
        return 2

    films = [entree(b) for b in decoupe_entrees(lire(registre))]
    films = [f for f in films if f["slug"]]
    derniere = derniere_publiee(films)
    # L'ordre du catalogue, arrete par le gate du 22/07 : alphabetique sur le
    # titre replie. Applique ICI, une fois, avant tout filtrage -- exactement
    # comme corpus.js trie sa copie de travail a l'amorcage.
    films.sort(key=ordre_catalogue)

    code = 0
    for nom, filtre in PAGES:
        chemin = os.path.join(args.depot, nom)
        if not os.path.isfile(chemin):
            sys.stderr.write("Introuvable : %s\n" % chemin)
            return 2
        contenu = bloc(films, filtre, derniere)
        src, neuf = applique(chemin, contenu)
        if src is None:
            return 1
        n = len([f for f in films if filtre is None or f["volet"] == filtre])
        if args.verifier:
            etat = "conforme" if src == neuf else "DERIVE"
            if src != neuf:
                code = 1
            print("%-24s %-9s %d entrees en dur" % (nom, etat, n))
        else:
            if src != neuf:
                ecrire(chemin, neuf)
            print("%-24s %d entrees ecrites en dur" % (nom, n))

    if args.verifier and code == 0:
        print("")
        print("Aucune derive entre le gabarit du script et le HTML du depot.")
    elif args.verifier:
        print("")
        print("DERIVE : le HTML ne correspond plus au registre. Regenerer.")
    return code


if __name__ == "__main__":
    sys.exit(main())
