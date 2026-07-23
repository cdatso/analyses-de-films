#!/usr/bin/env python3
# -*- coding: ascii -*-
"""harnais.py -- socle commun des sondes de recette (BKL-065-4-recette).

Ce module ne mesure rien lui-meme : il fournit aux sondes le depot, la liste
des pages, l'URL de service local et l'ouverture de Chromium. Les sondes
CONSTATENT ; aucune d'elles n'ecrit dans le site.

Regles tenues ici :
  - ASCII pur, aucun chemin accentue en dur (le depot est deduit du fichier) ;
  - assert avant toute ecriture (voir ecrire_json / dossier_sortie) ;
  - la maquette est servie en LOCAL ; aucune sonde ne connait d'URL publique.

Usage : importe par les sondes soeurs. Executable seul pour auto-controle :
    python harnais.py
"""

import json
import os
import sys

# --- Depot et arborescence -------------------------------------------------

ICI = os.path.dirname(os.path.abspath(__file__))
DEPOT = os.path.dirname(os.path.dirname(ICI))          # outils/recette-playwright -> depot
DOSSIER_FILMS = os.path.join(DEPOT, "films")
DOSSIER_DOCS = os.path.join(DEPOT, "docs")
DOSSIER_RESULTATS = os.path.join(ICI, "resultats")

BASE = os.environ.get("RECETTE_BASE", "http://127.0.0.1:8765")

# Les 6 pages du menu v2 (SPEC-SITE-V2 P-02, nommage gate du 21/07 17h31).
PAGES_MENU = [
    "index.html",
    "critiques.html",
    "etudes.html",
    "qui-sommes-nous.html",
    "comment-ca-marche.html",
    "demander-une-analyse.html",
]

# Les 3 pages migrees par 065-3 (diptyque Pandora + page sombre).
PAGES_MIGREES = [
    "films/pandora.html",
    "films/pandora-contrechamp.html",
    "films/rouges-et-blancs.html",
]

# Le perimetre de verdict du mandat : les 9 pages du prototype.
PAGES_PROTOTYPE = PAGES_MENU + PAGES_MIGREES


def pages_films():
    """Toutes les pages d'analyse presentes dans le depot, triees."""
    assert os.path.isdir(DOSSIER_FILMS), "films/ introuvable sous %s" % DEPOT
    noms = sorted(n for n in os.listdir(DOSSIER_FILMS) if n.endswith(".html"))
    return ["films/" + n for n in noms]


def pages_toutes():
    """Les 6 pages de menu + toutes les pages d'analyse."""
    return PAGES_MENU + pages_films()


def pages_non_migrees():
    """Les pages d'analyse qui n'ont pas ete migrees par 065-3 (informatif)."""
    migrees = set(PAGES_MIGREES)
    return [p for p in pages_films() if p not in migrees]


def url(chemin):
    return BASE.rstrip("/") + "/" + chemin.lstrip("/")


# --- Sorties ---------------------------------------------------------------

def dossier_sortie():
    """Cree si besoin le dossier des resultats bruts et le retourne."""
    if not os.path.isdir(DOSSIER_RESULTATS):
        os.makedirs(DOSSIER_RESULTATS)
    assert os.path.isdir(DOSSIER_RESULTATS)
    return DOSSIER_RESULTATS


def ecrire_json(nom, donnees):
    """Ecrit un resultat brut. Assert avant ecriture : le nom reste dans
    resultats/, jamais ailleurs (aucune sonde ne peut ecrire dans le site)."""
    assert nom.endswith(".json"), "sortie attendue en .json : %r" % nom
    assert os.sep not in nom and "/" not in nom, "nom de fichier simple attendu"
    chemin = os.path.join(dossier_sortie(), nom)
    with open(chemin, "w", encoding="utf-8", newline="\n") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=1, sort_keys=True)
    return chemin


def lire_json(nom):
    chemin = os.path.join(DOSSIER_RESULTATS, nom)
    assert os.path.isfile(chemin), "resultat absent : %s" % chemin
    with open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)


# --- Navigateur ------------------------------------------------------------

def playwright_ou_arret():
    """Playwright est un PREREQUIS du mandat, pas une dependance a installer.
    S'il manque : arret net et signalement (mandat 5, aucune installation)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.stderr.write(
            "ARRET : playwright absent de cet environnement.\n"
            "Le mandat interdit toute installation -- signaler a AH.\n")
        raise SystemExit(3)
    return sync_playwright


JS_FOND_EFFECTIF = r"""
(() => {
  // Fond effectif d'un element : on remonte les ancetres jusqu'a une couche
  // opaque, en composant les couches semi-transparentes rencontrees.
  window.__lireRgba = (s) => {
    const m = String(s).match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(/[,\s\/]+/).filter(x => x.length).map(Number);
    if (p.length < 3 || p.some(isNaN)) return null;
    return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1};
  };
  window.__composer = (dessus, dessous) => ({
    r: Math.round(dessus.r * dessus.a + dessous.r * (1 - dessus.a)),
    g: Math.round(dessus.g * dessus.a + dessous.g * (1 - dessus.a)),
    b: Math.round(dessus.b * dessus.a + dessous.b * (1 - dessus.a)),
    a: 1,
  });
  window.__fondEffectif = (el) => {
    const couches = [];
    let n = el;
    while (n && n.nodeType === 1) {
      const c = window.__lireRgba(getComputedStyle(n).backgroundColor);
      if (c && c.a > 0) {
        couches.push(c);
        if (c.a >= 0.999) break;
      }
      n = n.parentElement;
    }
    let fond = {r: 255, g: 255, b: 255, a: 1};   // le canevas du navigateur
    for (let i = couches.length - 1; i >= 0; i--) {
      fond = window.__composer(couches[i], fond);
    }
    return fond;
  };
  // Fonds CANDIDATS d'un element. Un fond n'est pas toujours une couleur
  // plate : les couvertures du corpus emploient des degrades, portes par
  // `background-image` et non par `background-color`. Remonter les seuls
  // `background-color` fait alors traverser la couverture et rend le fond du
  // corps de page -- d'ou des ratios de 1,00 sur du texte parfaitement
  // lisible. On collecte donc AUSSI les arrets de couleur des degrades
  // rencontres, et le verdict se prononce sur le pire d'entre eux.
  window.__fondsCandidats = (el) => {
    const base = window.__fondEffectif(el);   // fond si l'on ignore les images
    let degrade = false;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const st = getComputedStyle(n);
      const img = st.backgroundImage;
      if (img && img !== 'none') {
        // Cette couche COUVRE tout ce qui est dessous : le fond de page
        // cesse d'etre un candidat, sans quoi le pire cas serait toujours
        // celui d'un fond que le lecteur ne voit pas.
        degrade = true;
        const arrets = (img.match(/rgba?\([^)]+\)/g) || [])
          .map(window.__lireRgba).filter(c => c && c.a > 0);
        const opaques = arrets.filter(c => c.a >= 0.999);
        const socle = opaques.length ? opaques : [base];
        const fonds = [];
        for (const c of arrets) {
          if (c.a >= 0.999) { fonds.push(c); continue; }
          for (const s of socle) fonds.push(window.__composer(c, s));
        }
        if (fonds.length) return {fonds: fonds, degrade: true};
        return {fonds: [base], degrade: true};
      }
      const bc = window.__lireRgba(st.backgroundColor);
      if (bc && bc.a >= 0.999) break;      // couche opaque : on s'arrete
    }
    return {fonds: [base], degrade: degrade};
  };
  window.__luminance = (c) => {
    const f = (v) => {
      v = v / 255;
      return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
  };
  window.__ratio = (a, b) => {
    let l1 = window.__luminance(a), l2 = window.__luminance(b);
    if (l1 < l2) { const t = l1; l1 = l2; l2 = t; }
    return (l1 + 0.05) / (l2 + 0.05);
  };
  window.__hex = (c) => '#' + [c.r, c.g, c.b]
    .map(v => Math.max(0, Math.min(255, v)).toString(16).padStart(2, '0')).join('');
  window.__chemin = (el) => {
    const bouts = [];
    let n = el;
    while (n && n.nodeType === 1 && bouts.length < 6) {
      let b = n.tagName.toLowerCase();
      if (n.id) { bouts.unshift(b + '#' + n.id); break; }
      if (n.classList.length) b += '.' + Array.from(n.classList).join('.');
      bouts.unshift(b);
      n = n.parentElement;
    }
    return bouts.join(' > ');
  };
  return true;
})()
"""


def autocontrole():
    """Verifie que le socle voit ce qu'il doit voir, sans rien ecrire."""
    print("depot        : %s" % DEPOT)
    print("base         : %s" % BASE)
    print("pages menu   : %d" % len(PAGES_MENU))
    print("pages films  : %d" % len(pages_films()))
    print("prototype    : %d" % len(PAGES_PROTOTYPE))
    print("non migrees  : %d" % len(pages_non_migrees()))
    playwright_ou_arret()
    print("playwright   : present")
    return 0


if __name__ == "__main__":
    sys.exit(autocontrole())
