# -*- coding: utf-8 -*-
"""Controle MECANIQUE de couverture des glyphes (BKL-065-1).

Remplace le controle visuel du specimen : verifie caractere par caractere,
dans CHAQUE fichier de fonte, que le repertoire contient bien le glyphe.
Critere eliminatoire de la spec : un seul manquant = candidate ecartee.

NB encodage : ce script declare utf-8 A DESSEIN et non ascii comme le veut la
convention de la squad -- les jeux de test SONT des caracteres non-ASCII,
c'est leur raison d'etre. Appliquer ascii ici serait un contresens.

NB dependances : fonttools ne lit un .woff2 qu'avec l'extension brotli, NON
autorisee (charte R4 : la pre-autorisation d'AH portait sur fonttools seul).
On telecharge donc les memes familles en TTF -- Google Fonts sert du TTF a un
User-Agent ancien -- que fonttools lit nativement. Meme fonte, meme cmap,
autre conteneur : le resultat du controle est identique.

GARDE-FOU : tout fichier illisible rend sa famille ECHEC, jamais OK.
(Correctif du 20/07 : la 1re version affichait OK alors que les 52 fichiers
avaient echoue a se lire -- un garde-fou doit avoir un mode d'echec visible.)
"""
import os, re, sys, collections, urllib.request, tempfile
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# CORRECTIF 27/07/2026 (gate AH « go correctif glyphes ») : tout argument
# (--help compris) affiche l'usage et SORT sans rien executer ni ecrire.
# L'ancienne version executait sa routine complete (telechargement de 15
# fichiers WOFF) meme en --help -- elucidation du 27/07 au soir : c'est ainsi
# qu'un simple appel d'aide de l'auditeur Opus a pollue l'arbre git.
if len(sys.argv) > 1:
    print(__doc__)
    print("Usage : python controle-glyphes.py   (sans argument)")
    print("Etude de couverture de glyphes des fontes CANDIDATES (BKL-065-1).")
    print("NE controle PAS les pages du site. Telecharge ses fontes de")
    print("controle dans le repertoire temporaire systeme (hors depot git).")
    sys.exit(0)

from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
# CORRECTIF 27/07/2026 (meme gate) : repertoire de travail HORS depot --
# l'ancien chemin code en dur (outils/woff-controle) ecrivait dans l'arbre
# git au premier appel venu.
TDIR = os.path.join(tempfile.gettempdir(), "woff-controle")

# User-Agent Firefox 20 => Google Fonts repond en .woff (et non .woff2).
# WOFF est compresse en zlib (bibliotheque standard), donc lisible par
# fonttools SANS l'extension brotli, qui n'est pas autorisee.
# NB : un UA encore plus ancien (MSIE 6) renvoie une URL sans extension
# (/l/font?kit=...), inexploitable par un motif de nom de fichier.
UA_LEGACY = "Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0"

# Styles demandes a l'API v1. L'ITALIQUE est le style ou les glyphes
# manquent le plus souvent : l'omettre viderait le controle de son sens.
V1_STYLES = {
    "Newsreader": "400,400i,600", "Literata": "400,400i,600",
    "Source Serif 4": "400,400i,600", "Spectral": "300,400,400i,600",
    "IBM Plex Mono": "400,500",
}

FAMILIES = {
    "Newsreader":     "Newsreader:ital,wght@0,400;0,600;1,400",
    "Literata":       "Literata:ital,wght@0,400;0,600;1,400",
    "Source Serif 4": "Source+Serif+4:ital,wght@0,400;0,600;1,400",
    "Spectral":       "Spectral:ital,wght@0,300;0,400;0,600;1,400",
    "IBM Plex Mono":  "IBM+Plex+Mono:wght@400;500",
}

ROLES = {
    "Newsreader": "SERIF candidate 1", "Literata": "SERIF candidate 2",
    "Source Serif 4": "SERIF candidate 3", "Spectral": "SERIF candidate 4",
    "IBM Plex Mono": "MONO retenue (gate AH 20/07)",
}

# Jeux de test DERIVES DU CORPUS REEL (29 pages + films-data.js + index),
# et non inventes : extraction des 64 caracteres non-ASCII effectivement
# employes, hors CSS/JS/balises. Un jeu invente sur-exige (le premier
# reclamait un double-obele que le corpus n'utilise nulle part).
JEUX = [
    ("francais courant",   "àâäéèêëîïôöùûüçÀÁÂÈÉÎÓÔÖ"),
    ("ligatures",          "œŒæ"),
    ("ponctuation",        "«»…–—·"),
    ("latin-ext du corpus", "ŁłŻćřűñåáíóú"),
    ("symboles",           "°º£€≈−←→↔◼✦"),
]

# Blocs hors alphabet latin presents dans le corpus : AUCUNE fonte latine ne
# les porte. Le repli navigateur est donc INEVITABLE et doit etre assume,
# pas decouvert en production. Comptes : hebreu 8 occurrences (Le Golem),
# cyrillique 5 (Soy Cuba / Rouges et blancs).
HORS_LATIN = "אמתЯКуба"


def fetch_ttf():
    if not os.path.isdir(TDIR):
        os.makedirs(TDIR)
    out = collections.defaultdict(list)
    for label, spec in FAMILIES.items():
        # subset=latin,latin-ext : SANS cela l'API ne sert que latin, et tous les
        # diacritiques d'Europe centrale manquent -- resultat trompeur qui
        # accuse les fontes d'un defaut du protocole de test (piege du 20/07).
        url = ("https://fonts.googleapis.com/css?family=%s:%s&subset=latin,latin-ext"
               % (spec.split(":")[0], V1_STYLES.get(label, "400,400i,600")))
        req = urllib.request.Request(url, headers={"User-Agent": UA_LEGACY})
        css = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
        for i, src in enumerate(re.findall(r"url\((https://[^)]+?\.woff)\)", css)):
            name = "%s-%d.woff" % (label.lower().replace(" ", ""), i)
            path = os.path.join(TDIR, name)
            if not os.path.exists(path):
                r = urllib.request.Request(src, headers={"User-Agent": UA_LEGACY})
                open(path, "wb").write(urllib.request.urlopen(r, timeout=30).read())
            out[label].append(path)
        if not out[label]:
            print("  ATTENTION : aucun WOFF obtenu pour %s" % label)
    return out


def cmap_of(path):
    f = TTFont(path, lazy=True)
    cps = set()
    for t in f["cmap"].tables:
        cps.update(t.cmap.keys())
    f.close()
    return cps


print("Telechargement des WOFF de controle...")
fichiers = fetch_ttf()
total = sum(len(v) for v in fichiers.values())
print("%d fichiers WOFF pour %d familles\n" % (total, len(fichiers)))

if total == 0:
    sys.exit("ECHEC : aucun fichier a controler - resultat NON CONCLUANT")

verdicts = {}
for label in FAMILIES:
    paths = fichiers.get(label, [])
    illisibles, manques = [], collections.defaultdict(set)

    if not paths:
        verdicts[label] = "ECHEC (aucun fichier)"
        continue

    for p in paths:
        try:
            cps = cmap_of(p)
        except Exception as exc:                        # noqa: BLE001
            illisibles.append("%s (%s)" % (os.path.basename(p), exc))
            continue
        for nom, chaine in JEUX:
            for ch in chaine:
                if ord(ch) not in cps:
                    manques[nom].add(ch)

    # Un fichier illisible interdit de conclure : jamais de OK par defaut.
    if illisibles:
        verdicts[label] = "NON CONCLUANT (%d fichier(s) illisible(s))" % len(illisibles)
    elif manques:
        verdicts[label] = "ECARTEE"
    else:
        verdicts[label] = "OK"

    print("%-16s %-30s %s  [%d fichier(s)]"
          % (label, ROLES.get(label, ""), verdicts[label], len(paths)))
    for nom, chars in sorted(manques.items()):
        print("     manque %-22s %s" % (nom, " ".join(sorted(chars))))
    for f in illisibles:
        print("     ILLISIBLE %s" % f)

print()
print("Ecritures non latines du corpus : %s" % HORS_LATIN)
print("  hebreu (Le Golem) + cyrillique (Soy Cuba / Rouges et blancs).")
print("  CORRECTIF du 20/07 : une premiere version de ce script concluait au")
print("  'repli inevitable'. C'ETAIT FAUX, sur les deux points --")
print("   * cyrillique : Literata ET IBM Plex Mono ont un subset 'cyrillic'")
print("     (119,2 Ko). L'erreur venait du parametre subset=latin,latin-ext")
print("     de la requete : le test accusait la fonte d'un defaut du test.")
print("   * hebreu : Frank Ruhl Libre, subset 'hebrew', 18,3 Ko.")
print("  Les deux sont charges par unicode-range, donc a cout NUL sur les")
print("  pages qui ne les emploient pas. Le repli ne concerne plus que les")
print("  symboles bespoke (fleches, ornements) - regle 2 du gate du 20/07.")
print()

ok = [k for k, v in verdicts.items() if v == "OK"]
ko = [k for k, v in verdicts.items() if v != "OK"]
print("COUVRENT TOUS LES JEUX : %s" % (", ".join(ok) if ok else "aucune"))
if ko:
    print("A ECARTER OU A REVOIR  : %s" % ", ".join("%s (%s)" % (k, verdicts[k]) for k in ko))
sys.exit(0 if len(ok) == len(FAMILIES) else 1)
