#!/usr/bin/env python3
# -*- coding: ascii -*-
"""sonde-contraste-lots.py -- P-39 re-mesure APRES retrofit, et regroupe.

Pourquoi une nouvelle mesure. Le tableau AA de la recette (221 couples) a ete
etabli le 22/07 sur un site dont 30 pages n'etaient PAS encore retrofitees.
Depuis : substitution typographique, menu, cartouche de provenance, calage du
mobilier. Des couples ont disparu, d'autres sont nes. Arbitrer sur la photo
d'hier serait arbitrer a cote.

Pourquoi regrouper. Le mandat interdit 221 decisions unitaires. Or les 33
palettes bespoke reutilisent LEURS couleurs : le meme couple texte/fond
revient sur des dizaines d'elements et souvent sur plusieurs pages. Le lot
naturel n'est donc pas la page, c'est LE COUPLE DE COULEURS -- une decision
par couple corrige tous ses elements d'un coup.

Ce que la sonde PROPOSE, et sur quel principe. Pour chaque couple en echec,
elle cherche la couleur de texte la PLUS PROCHE de l'originale qui atteigne le
seuil : teinte et saturation conservees (HSL), seule la clarte bouge, et dans
le sens impose par le fond (plus sombre sur fond clair, plus claire sur fond
sombre). C'est le minimum de deplacement -- l'identite bespoke est une
exigence de la spec (A-1), pas une variable d'ajustement.

La sonde ne CORRIGE rien. Chaque lot est un arbitrage d'AH (ARRET n.2).

Usage : RECETTE_BASE=http://127.0.0.1:8791 python sonde-contraste-lots.py
"""

import colorsys
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harnais  # noqa: E402

SEUILS = {"courant": 4.5, "grand": 3.0}


def _js_recensement():
    """Le JS de recensement vit dans sonde-contraste.py : on le REUTILISE.

    Le copier, c'est creer deux definitions de ce qu'est un ecart -- et la
    premiere divergence silencieuse serait invisible.
    """
    mod = import_module("sonde-contraste".replace("-", "_")) \
        if False else None
    # Le nom de fichier porte des tirets : import classique impossible.
    import importlib.util
    chemin = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "sonde-contraste.py")
    spec = importlib.util.spec_from_file_location("sonde_contraste", chemin)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.JS_RECENSEMENT


# --- Colorimetrie ----------------------------------------------------------

def hex_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(c))))
                                   for c in rgb)


def luminance(rgb):
    def canal(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (canal(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = luminance(a), luminance(b)
    if la < lb:
        la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)


def corrige(texte_hex, fond_hex, seuil):
    """Couleur de texte la plus proche atteignant le seuil.

    Teinte et saturation figees ; seule la clarte se deplace, par pas fins,
    dans le sens impose par le fond. Rend None si meme le noir (ou le blanc)
    ne suffit pas -- auquel cas c'est le FOND qu'il faut arbitrer, et cela ne
    se decide pas dans un script.
    """
    t, f = hex_rgb(texte_hex), hex_rgb(fond_hex)
    if ratio(t, f) >= seuil:
        return texte_hex, 0.0
    h, l, s = colorsys.rgb_to_hls(*[c / 255.0 for c in t])
    vers_le_sombre = luminance(f) > luminance(t) or luminance(f) > 0.18
    pas = -0.002 if vers_le_sombre else 0.002
    l2 = l
    for _ in range(600):
        l2 += pas
        if not 0.0 <= l2 <= 1.0:
            break
        cand = tuple(c * 255.0 for c in colorsys.hls_to_rgb(h, l2, s))
        if ratio(cand, f) >= seuil:
            return rgb_hex(cand), abs(l2 - l)
    # Dernier recours : l'extremite, si elle tient le seuil.
    for extreme in ((0, 0, 0), (255, 255, 255)):
        if ratio(extreme, f) >= seuil:
            return rgb_hex(extreme), 1.0
    return None, None


# --- Regroupement ----------------------------------------------------------

def main():
    js = _js_recensement()
    pages = sorted([p.split("/")[-1] for p in harnais.pages_films()])
    chemins = ["films/" + p for p in pages] + harnais.PAGES_MENU

    couples = {}
    total = 0
    sync = harnais.playwright_ou_arret()
    with sync() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        for chemin in chemins:
            page.goto(harnais.url(chemin), wait_until="load", timeout=30000)
            page.evaluate(harnais.JS_FOND_EFFECTIF)
            page.wait_for_timeout(110)
            # Le JS rend une LISTE de lignes en echec, deja triee.
            lignes = page.evaluate(js, SEUILS)
            nom = chemin.split("/")[-1]
            for c in lignes:
                total += 1
                cle = (c["texte"], c["fond"], c["seuil"],
                       round(c.get("opacite", 1.0), 2))
                e = couples.setdefault(cle, {"pages": {}, "elements": 0,
                                             "pire": 99.0, "extraits": [],
                                             "degrade": False,
                                             "partiel": False})
                e["elements"] += 1
                e["pages"][nom] = e["pages"].get(nom, 0) + 1
                e["pire"] = min(e["pire"], c["ratio"])
                # Une seule occurrence en degrade suffit a qualifier le lot :
                # le fond n'y est pas uniforme, et l'arbitrage differe.
                if c.get("degrade"):
                    e["degrade"] = True
                if c.get("partiel"):
                    e["partiel"] = True
                if len(e["extraits"]) < 3 and c.get("extrait"):
                    e["extraits"].append(c["extrait"][:46])
        ctx.close()
        nav.close()

    print("couples en echec (elements) : %d" % total)
    print("COUPLES DE COULEURS DISTINCTS : %d" % len(couples))
    print("")
    ordre = sorted(couples.items(), key=lambda kv: -kv[1]["elements"])
    lignes = []
    for (texte, fond, seuil, opac), e in ordre:
        prop, ecart = corrige(texte, fond, seuil)
        if e["degrade"]:
            nature = "degrade partiel" if e["partiel"] else "degrade"
        elif opac < 0.999:
            nature = "opacite"
        elif seuil == SEUILS["grand"]:
            nature = "grand texte"
        elif round(e["pire"], 2) <= 1.02:
            nature = "identite de couleur"
        else:
            nature = "texte courant"
        lignes.append({"texte": texte, "fond": fond, "seuil": seuil,
                       "opacite": opac, "nature": nature,
                       "elements": e["elements"],
                       "pages": e["pages"], "pire_ratio": round(e["pire"], 2),
                       "propose": prop,
                       "deplacement_clarte": (round(ecart, 3)
                                              if ecart is not None else None),
                       "extraits": e["extraits"]})
        print("%-9s sur %-9s seuil %.1f opac %.2f %3d el. %2d p. "
              "ratio %.2f  [%-16s] -> %s"
              % (texte, fond, seuil, opac, e["elements"], len(e["pages"]),
                 e["pire"], nature, prop or "IMPOSSIBLE (arbitrer le FOND)"))
    harnais.ecrire_json("contraste-lots.json", lignes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
