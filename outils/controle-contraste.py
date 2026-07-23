#!/usr/bin/env python3
# -*- coding: ascii -*-
"""controle-contraste.py -- comptage mecanique du contraste WCAG AA (P-39).

Constat C-3 du mandat BKL-065-3. Cet outil COMPTE, il ne corrige RIEN :
chaque ecart releve est un arbitrage d'AH (corriger la palette OU documenter
l'exception). Aucun fichier du depot n'est modifie.

Pourquoi un script stdlib et pas un navigateur : l'arithmetique de contraste
WCAG (luminance relative, rapport (L1+0.05)/(L2+0.05)) n'exige aucun rendu.
Playwright reste hors du poste (BKL-069, autorisation R4 distincte).

METHODE ET SES LIMITES -- a lire avant d'interpreter les chiffres.
  1. Le CSS de chaque page est lu dans son bloc <style> inline (les pages
     d'analyse sont autonomes) ; la feuille partagee est lue pour l'accueil.
  2. Les proprietes personnalisees (--x) sont collectees puis var() est
     resolu recursivement, fallback compris.
  3. DEUX classes d'ecarts, parce qu'apparier une couleur a son fond reel
     demande l'arbre du document, que ce script n'a pas :
       E1 -- ECART CERTAIN : la regle declare `color` ET un fond. Le couple
             est celui que l'auteur a ecrit lui-meme ; aucune inference.
       E2 -- ECART PROBABLE : la regle ne declare que `color`, et cette
             couleur echoue contre TOUS les fonds declares dans la page.
             Aucun empilement possible ne la sauve. C'est une borne BASSE.
     Une regle `color` seule qui passe sur au moins un fond declare n'est
     PAS comptee : elle pourrait vivre dans un bloc a fond distinct.
     Consequence assumee : le comptage sous-estime plutot que d'inventer.
     La premiere version de cet outil appariait toute regle `color` au fond
     du body ; elle produisait des ratios de 1,00 en serie (texte de la
     couleur exacte du fond) -- artefacts de nesting, non defauts de palette.
  4. Les couleurs semi-transparentes sont composees sur le fond retenu.
  5. Grand texte (seuil 3:1) : font-size >= 24px, ou >= 18.66px en gras,
     lue dans la meme regle quand elle y figure ; sinon texte courant (4.5).

Usage :
    python controle-contraste.py [--depot CHEMIN] [--sortie FICHIER]
Sortie : rapport Markdown sur stdout, et dans le fichier si demande.
Code de sortie : 0 -- le comptage a abouti (meme avec des ecarts).
                 2 -- le comptage n'a pas pu etre fait.
"""

import argparse
import os
import re
import sys

RE_COMMENT = re.compile(r"/\*.*?\*/", re.S)
RE_STYLE = re.compile(r"<style[^>]*>(.*?)</style>", re.S | re.I)
RE_RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
RE_VAR = re.compile(r"var\(\s*(--[A-Za-z0-9_-]+)\s*(?:,\s*([^()]*(?:\([^()]*\)[^()]*)*))?\)")
RE_HEX = re.compile(r"^#([0-9a-fA-F]{3,8})$")
RE_FUNC = re.compile(r"^rgba?\(([^)]*)\)$", re.I)

SEUIL_COURANT = 4.5
SEUIL_GRAND = 3.0

NOMMEES = {
    "white": (255, 255, 255), "black": (0, 0, 0), "red": (255, 0, 0),
    "transparent": None, "inherit": None, "currentcolor": None, "none": None,
}


def sans_commentaires(css):
    return RE_COMMENT.sub(" ", css)


def parse_regles(css):
    """Retourne [(selecteur, {propriete: valeur})] dans l'ordre du document.

    Les blocs @media / @supports sont aplatis : leur contenu est traite comme
    des regles ordinaires. C'est volontaire -- un couple contraste declare
    sous media query compte comme un couple.
    """
    css = sans_commentaires(css)
    css = re.sub(r"@(media|supports)[^{]*\{", " ", css)
    regles = []
    for m in RE_RULE.finditer(css):
        sel = " ".join(m.group(1).split())
        if not sel or sel.startswith("@"):
            continue
        decls = {}
        for d in m.group(2).split(";"):
            if ":" not in d:
                continue
            k, _, v = d.partition(":")
            k = k.strip().lower()
            v = " ".join(v.split())
            if k:
                decls[k] = v
        if decls:
            regles.append((sel, decls))
    return regles


def collecte_variables(regles):
    variables = {}
    for _sel, decls in regles:
        for k, v in decls.items():
            if k.startswith("--"):
                variables[k] = v
    return variables


def resout(valeur, variables, profondeur=0):
    if valeur is None or profondeur > 12:
        return valeur
    if "var(" not in valeur:
        return valeur

    def remplace(m):
        nom, defaut = m.group(1), m.group(2)
        if nom in variables:
            return variables[nom]
        return defaut if defaut is not None else ""

    return resout(RE_VAR.sub(remplace, valeur).strip(), variables, profondeur + 1)


def en_rgba(valeur):
    """Retourne (r, g, b, alpha) ou None si la valeur n'est pas une couleur."""
    if not valeur:
        return None
    v = valeur.strip().lower()
    if v in NOMMEES:
        c = NOMMEES[v]
        return None if c is None else (c[0], c[1], c[2], 1.0)
    m = RE_HEX.match(v)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) == 4:
            h = "".join(c * 2 for c in h)
        if len(h) == 6:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
        if len(h) == 8:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16),
                    int(h[6:8], 16) / 255.0)
        return None
    m = RE_FUNC.match(v)
    if m:
        bruts = [x.strip() for x in m.group(1).replace("/", " ").split(",")]
        if len(bruts) == 1:
            bruts = m.group(1).split()
        try:
            canaux = []
            for x in bruts[:3]:
                canaux.append(int(round(float(x.rstrip("%")) * (2.55 if "%" in x else 1))))
            alpha = float(bruts[3].rstrip("%")) if len(bruts) > 3 else 1.0
            if len(bruts) > 3 and "%" in bruts[3]:
                alpha /= 100.0
            return (canaux[0], canaux[1], canaux[2], alpha)
        except (ValueError, IndexError):
            return None
    return None


def compose(dessus, dessous):
    """Aplatit une couleur semi-transparente sur son fond."""
    if dessus is None:
        return None
    r, g, b, a = dessus
    if a >= 0.999 or dessous is None:
        return (r, g, b, 1.0)
    fr, fg, fb, _ = dessous
    return (round(r * a + fr * (1 - a)),
            round(g * a + fg * (1 - a)),
            round(b * a + fb * (1 - a)), 1.0)


def luminance(couleur):
    def canal(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b, _ = couleur
    return 0.2126 * canal(r) + 0.7152 * canal(g) + 0.0722 * canal(b)


def rapport(c1, c2):
    l1, l2 = luminance(c1), luminance(c2)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def hexa(couleur):
    return "#%02x%02x%02x" % (couleur[0], couleur[1], couleur[2])


def taille_px(decls, variables):
    v = resout(decls.get("font-size"), variables)
    if not v:
        return None
    m = re.match(r"^(-?[0-9.]+)\s*(px|rem|em)$", v.strip())
    if not m:
        return None
    n = float(m.group(1))
    return n if m.group(2) == "px" else n * 16.0


def est_gras(decls, variables):
    v = (resout(decls.get("font-weight"), variables) or "").strip()
    if v in ("bold", "bolder"):
        return True
    try:
        return int(v) >= 700
    except ValueError:
        return False


def seuil_de(decls, variables):
    px = taille_px(decls, variables)
    if px is None:
        return SEUIL_COURANT, "courant"
    if px >= 24.0 or (px >= 18.66 and est_gras(decls, variables)):
        return SEUIL_GRAND, "grand"
    return SEUIL_COURANT, "courant"


def fond_de_regle(decls, variables):
    for prop in ("background-color", "background"):
        if prop in decls:
            brut = resout(decls[prop], variables)
            for jeton in re.split(r"\s+(?![^(]*\))", brut or ""):
                c = en_rgba(jeton)
                if c is not None:
                    return c
    return None


def analyse_page(chemin, css_partagee=None):
    with open(chemin, "r", encoding="utf-8") as f:
        html = f.read()
    css = "\n".join(RE_STYLE.findall(html))
    if css_partagee and 'href="assets/style.css"' in html or (
            css_partagee and 'href="../assets/style.css"' in html):
        css = css_partagee + "\n" + css
    if not css.strip():
        return None
    regles = parse_regles(css)
    variables = collecte_variables(regles)

    fond_page = None
    couleur_page = None
    for sel, decls in regles:
        if re.search(r"(^|,\s*)body(\s*|,|$)", sel):
            f = fond_de_regle(decls, variables)
            if f is not None:
                fond_page = compose(f, (255, 255, 255, 1.0))
            c = en_rgba(resout(decls.get("color"), variables))
            if c is not None:
                couleur_page = c
    if fond_page is None:
        fond_page = (255, 255, 255, 1.0)

    # Inventaire de TOUS les fonds opaques declares dans la page : c'est
    # l'ensemble des fonds sur lesquels un texte peut reellement se poser.
    fonds = {hexa(fond_page): fond_page}
    for _sel, decls in regles:
        f = fond_de_regle(decls, variables)
        if f is not None:
            f = compose(f, fond_page)
            fonds[hexa(f)] = f

    couples = []
    vus = set()
    for sel, decls in regles:
        if "color" not in decls:
            continue
        avant = en_rgba(resout(decls["color"], variables))
        if avant is None:
            continue
        seuil, genre = seuil_de(decls, variables)
        propre = fond_de_regle(decls, variables)

        if propre is not None:
            # E1 : le couple est declare dans la meme regle -- certain.
            fond = compose(propre, fond_page)
            texte = compose(avant, fond)
            if texte is None:
                continue
            cle = ("E1", hexa(texte), hexa(fond), seuil)
            if cle in vus:
                continue
            vus.add(cle)
            couples.append({
                "classe": "E1", "selecteur": sel[:70],
                "texte": hexa(texte), "fond": hexa(fond),
                "ratio": rapport(texte, fond), "seuil": seuil, "genre": genre,
            })
            continue

        # E2 : pas de fond dans la regle. On retient le MEILLEUR fond declare
        # de la page : si meme celui-la echoue, aucun empilement ne sauve.
        meilleur, meilleur_ratio = None, -1.0
        for f in fonds.values():
            texte = compose(avant, f)
            if texte is None:
                continue
            r = rapport(texte, f)
            if r > meilleur_ratio:
                meilleur, meilleur_ratio = f, r
        if meilleur is None:
            continue
        texte = compose(avant, meilleur)
        cle = ("E2", hexa(texte), hexa(meilleur), seuil)
        if cle in vus:
            continue
        vus.add(cle)
        couples.append({
            "classe": "E2", "selecteur": sel[:70],
            "texte": hexa(texte), "fond": hexa(meilleur),
            "ratio": meilleur_ratio, "seuil": seuil, "genre": genre,
        })

    return {
        "page": os.path.basename(chemin),
        "fond_page": hexa(fond_page),
        "luminance_fond": luminance(fond_page),
        "couleur_body": hexa(couleur_page) if couleur_page else "-",
        "fonds_declares": len(fonds),
        "couples": couples,
        "echecs": [c for c in couples if c["ratio"] < c["seuil"]],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depot", default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    ap.add_argument("--sortie", default=None)
    args = ap.parse_args()

    depot = args.depot
    dossier_films = os.path.join(depot, "films")
    if not os.path.isdir(dossier_films):
        sys.stderr.write("Dossier films/ introuvable sous %s\n" % depot)
        return 2

    chemin_partage = os.path.join(depot, "assets", "style.css")
    css_partagee = ""
    if os.path.isfile(chemin_partage):
        with open(chemin_partage, "r", encoding="utf-8") as f:
            css_partagee = f.read()

    pages = sorted(os.path.join(dossier_films, n)
                   for n in os.listdir(dossier_films) if n.endswith(".html"))
    accueil = os.path.join(depot, "index.html")
    if os.path.isfile(accueil):
        pages.append(accueil)

    rapports = []
    for p in pages:
        r = analyse_page(p, css_partagee)
        if r is not None:
            rapports.append(r)

    lignes = []
    lignes.append("# Comptage du contraste AA -- constat C-3 (P-39)")
    lignes.append("")
    lignes.append("Outil : `outils/controle-contraste.py` (Python stdlib, ASCII pur).")
    lignes.append("COMPTAGE SEUL -- aucune palette n'est corrigee par cet outil.")
    lignes.append("")
    lignes.append("Seuils : texte courant 4,5:1 ; grand texte 3:1.")
    lignes.append("")
    lignes.append("E1 = ecart CERTAIN (couple ecrit dans la meme regle).")
    lignes.append("E2 = ecart PROBABLE (couleur en echec sur TOUS les fonds")
    lignes.append("declares par la page). Borne basse : ce qui passe sur au")
    lignes.append("moins un fond declare n'est pas compte.")
    lignes.append("")
    nb_pages = len(rapports)
    e1 = [c for r in rapports for c in r["echecs"] if c["classe"] == "E1"]
    e2 = [c for r in rapports for c in r["echecs"] if c["classe"] == "E2"]
    pages_e1 = [r for r in rapports if any(c["classe"] == "E1" for c in r["echecs"])]
    en_echec = [r for r in rapports if r["echecs"]]
    total_couples = sum(len(r["couples"]) for r in rapports)
    lignes.append("## Resultat global")
    lignes.append("")
    lignes.append("| Mesure | Valeur |")
    lignes.append("|---|---|")
    lignes.append("| Pages analysees | %d |" % nb_pages)
    lignes.append("| Couples texte/fond distincts examines | %d |" % total_couples)
    lignes.append("| Ecarts CERTAINS (E1) | %d |" % len(e1))
    lignes.append("| Ecarts PROBABLES (E2) | %d |" % len(e2))
    lignes.append("| **Pages avec au moins un ecart CERTAIN** | **%d / %d** |"
                  % (len(pages_e1), nb_pages))
    lignes.append("| Pages avec au moins un ecart, toutes classes | %d / %d |"
                  % (len(en_echec), nb_pages))
    lignes.append("")
    lignes.append("## Par page")
    lignes.append("")
    lignes.append("| Page | Fond | Luminance | Fonds declares | Couples | E1 | E2 |")
    lignes.append("|---|---|---|---|---|---|---|")
    for r in sorted(rapports, key=lambda x: (
            -len([c for c in x["echecs"] if c["classe"] == "E1"]),
            -len(x["echecs"]), x["page"])):
        n1 = len([c for c in r["echecs"] if c["classe"] == "E1"])
        n2 = len([c for c in r["echecs"] if c["classe"] == "E2"])
        lignes.append("| `%s` | `%s` | %.3f | %d | %d | **%d** | %d |" % (
            r["page"], r["fond_page"], r["luminance_fond"],
            r["fonds_declares"], len(r["couples"]), n1, n2))
    lignes.append("")
    lignes.append("## Detail des couples sous le seuil")
    lignes.append("")
    for r in sorted(rapports, key=lambda x: x["page"]):
        if not r["echecs"]:
            continue
        lignes.append("### %s" % r["page"])
        lignes.append("")
        lignes.append("| Classe | Selecteur | Texte | Fond | Ratio | Seuil |")
        lignes.append("|---|---|---|---|---|---|")
        for c in sorted(r["echecs"], key=lambda x: (x["classe"], x["ratio"])):
            lignes.append("| **%s** | `%s` | `%s` | `%s` | **%.2f** | %.1f (%s) |" % (
                c["classe"], c["selecteur"], c["texte"], c["fond"], c["ratio"],
                c["seuil"], c["genre"]))
        lignes.append("")
    lignes.append("## Classement des fonds du plus sombre au plus clair")
    lignes.append("")
    lignes.append("| # | Page | Fond | Luminance relative |")
    lignes.append("|---|---|---|---|")
    for i, r in enumerate(sorted(rapports, key=lambda x: x["luminance_fond"])[:10], 1):
        lignes.append("| %d | `%s` | `%s` | %.4f |" % (
            i, r["page"], r["fond_page"], r["luminance_fond"]))
    lignes.append("")

    texte = "\n".join(lignes)
    sys.stdout.write(texte + "\n")
    if args.sortie:
        with open(args.sortie, "w", encoding="utf-8", newline="\n") as f:
            f.write(texte + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
