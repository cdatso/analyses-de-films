# Tableau AA definitif -- P-39 au rendu reel

**Item** : BKL-065-4-recette - **Branche** : `v2-proto` - **Contrat** :
`SPEC-SITE-V2.md` v1.1, prescription **P-39** (4,5:1 texte courant,
3:1 grand texte).

**Ce document COMPTE et n'a rien corrige.** Chaque ligne est un
arbitrage qui attend AH en **BKL-065-5** : corriger la palette, ou
documenter l'exception. Aucun fichier du site n'a ete modifie.

## Methode, et en quoi elle differe du comptage du prototype

Le comptage de 065-3 (`outils/controle-contraste.py`) lisait le CSS
**sans arbre de document** : il ne pouvait pas savoir sur quel fond un
texte se pose. Il assumait de sous-estimer et distinguait deux classes,
**E1** (couple ecrit dans la meme regle, *certain*) et **E2** (couleur en
echec sur tous les fonds declares, *probable*).

La presente mesure est prise dans Chromium, sur la page composee :

- le fond effectif se lit en **remontant les ancetres** jusqu'a une
  couche opaque, les couches semi-transparentes etant composees ;
- les fonds en **degrade** sont traites par leurs arrets de couleur, et
  le verdict porte sur le **pire** d'entre eux (une couche a
  `background-image` couvre ce qui est dessous : le fond de page cesse
  d'etre un candidat) ;
- l'**opacite effective** est le produit de celles de l'element et de
  ses ancetres ;
- le seuil applicable vient de la **taille et de la graisse reelles** ;
- les textes `aria-hidden`, hors cadre ou de dimension nulle sont exclus.

*Controle du perimetre : aucune page du corpus n'emploie d'image bitmap
en fond (`background: url(...)`) -- tout fond est une couleur ou un
degrade, donc entierement decidable aux styles calcules. Aucune ligne de
ce tableau n'est laissee indeterminee.*

## 1. Les 71 ecarts declares par le prototype, confrontes au rendu reel

| Classe | Declares | CONFIRMES | ECARTES |
|---|---|---|---|
| **E1** (certains) | 23 | **17** | 6 |
| **E2** (probables) | 48 | **31** | 17 |
| **Total** | **71** | **48** | **23** |

Motifs des mises a l'ecart :

| Motif | Nombre | Lecture |
|---|---|---|
| (aucun texte porte par la regle) | 11 | les elements vises ne portent aucun texte -- il n'y a rien a lire |
| (regle sans element rendu) | 11 | la regle CSS existe mais ne s'applique a aucun element de la page |
| (passe au rendu reel) | 1 | le couple reel differe de celui suppose : le contraste passe |

### Detail des ecarts declares

| Page | Classe | Selecteur | Ratio statique | Ratio reel | Verdict |
|---|---|---|---|---|---|
| `annie-hall.html` | E1 | `footer` | 3.70 | 3.70 | CONFIRME |
| `annie-hall.html` | E2 | `header.hero .eyebrow` | 4.32 | 3.70 | CONFIRME |
| `au-fil-de-leau.html` | E2 | `.subtitle` | 1.09 | 1.00 | CONFIRME |
| `au-fil-de-leau.html` | E2 | `header.river` | 1.11 | 1.00 | ECARTE (aucun texte porte par la regle) |
| `au-fil-de-leau.html` | E2 | `.back-link` | 2.16 | 2.16 | CONFIRME |
| `au-fil-de-leau.html` | E2 | `.back-link:hover` | 2.45 | - | ECARTE (regle sans element rendu) |
| `bienvenue-a-suburbicon.html` | E2 | `.back-link` | 1.09 | 1.00 | CONFIRME |
| `bienvenue-a-suburbicon.html` | E2 | `.brochure-meta` | 1.10 | 1.00 | ECARTE (aucun texte porte par la regle) |
| `bienvenue-a-suburbicon.html` | E2 | `.subtitle` | 1.13 | 1.00 | CONFIRME |
| `bienvenue-a-suburbicon.html` | E2 | `header.brochure` | 1.15 | 1.00 | ECARTE (aucun texte porte par la regle) |
| `bienvenue-a-suburbicon.html` | E2 | `.back-link:hover` | 2.68 | - | ECARTE (regle sans element rendu) |
| `hamlet.html` | E1 | `.provenance` | 1.78 | 1.77 | CONFIRME |
| `hamlet.html` | E1 | `header.dalle` | 1.97 | 1.34 | ECARTE (aucun texte porte par la regle) |
| `hamlet.html` | E2 | `h3` | 4.45 | 4.45 | CONFIRME |
| `hamnet.html` | E1 | `.cast-card::before` | 2.33 | - | ECARTE (regle sans element rendu) |
| `hamnet.html` | E2 | `.back-link` | 4.35 | 3.93 | CONFIRME |
| `hitchcock-truffaut.html` | E1 | `section.sources .piste-num` | 2.52 | 2.52 | CONFIRME |
| `index.html` | E1 | `footer` | 3.70 | 3.70 | ECARTE (aucun texte porte par la regle) |
| `index.html` | E2 | `header.hero .eyebrow` | 4.32 | - | ECARTE (regle sans element rendu) |
| `julie-en-12-chapitres.html` | E1 | `.bandeau` | 4.39 | 4.39 | CONFIRME |
| `julie-en-12-chapitres.html` | E2 | `h1.title .chapitres` | 2.06 | 1.00 | CONFIRME |
| `julie-en-12-chapitres.html` | E2 | `.subtitle` | 2.26 | 1.00 | CONFIRME |
| `julie-en-12-chapitres.html` | E2 | `header.couverture` | 2.54 | 1.00 | ECARTE (aucun texte porte par la regle) |
| `julie-en-12-chapitres.html` | E2 | `.back-link:hover` | 2.84 | - | ECARTE (regle sans element rendu) |
| `julie-en-12-chapitres.html` | E2 | `.back-link` | 3.09 | 2.76 | CONFIRME |
| `la-chevauchee-fantastique.html` | E2 | `.meta-line` | 4.06 | 1.00 | CONFIRME |
| `la-nuit-de-san-lorenzo.html` | E1 | `.avertissement` | 1.23 | 1.23 | CONFIRME |
| `la-nuit-de-san-lorenzo.html` | E1 | `.provenance` | 1.51 | 1.51 | CONFIRME |
| `le-cheval-de-turin.html` | E2 | `.back-link` | 2.48 | 2.48 | CONFIRME |
| `le-cheval-de-turin.html` | E2 | `.back-link:hover` | 2.71 | - | ECARTE (regle sans element rendu) |
| `le-doulos.html` | E1 | `footer.endnote` | 3.86 | 3.86 | CONFIRME |
| `le-doulos.html` | E2 | `.back-link` | 3.86 | 3.86 | CONFIRME |
| `le-golem.html` | E1 | `footer.poussiere` | 4.28 | 4.28 | CONFIRME |
| `le-golem.html` | E2 | `.back-link` | 4.28 | 1.00 | CONFIRME |
| `le-samourai.html` | E1 | `.note` | 3.36 | 3.36 | CONFIRME |
| `le-samourai.html` | E2 | `.retour` | 4.27 | 3.76 | CONFIRME |
| `les-deux-orphelines.html` | E1 | `.fiche dt` | 4.07 | 4.07 | CONFIRME |
| `pandora-contrechamp.html` | E2 | `.cartel` | 3.02 | 3.02 | CONFIRME |
| `pandora-contrechamp.html` | E2 | `a` | 4.02 | 3.34 | CONFIRME |
| `pandora.html` | E1 | `.content-warning` | 1.88 | 1.88 | CONFIRME |
| `pandora.html` | E2 | `.eyebrow` | 1.86 | 1.86 | CONFIRME |
| `pandora.html` | E2 | `.back-link` | 1.88 | 1.00 | CONFIRME |
| `pandora.html` | E2 | `.cover` | 2.26 | 1.00 | ECARTE (aucun texte porte par la regle) |
| `pandora.html` | E2 | `.back-link:hover` | 2.70 | - | ECARTE (regle sans element rendu) |
| `pandora.html` | E2 | `.cartel` | 3.02 | 1.86 | CONFIRME |
| `pandora.html` | E2 | `sup.ref a` | 4.02 | 3.34 | CONFIRME |
| `persona.html` | E1 | `.content-warning` | 1.23 | 11.83 | ECARTE (passe au rendu reel) |
| `retour-a-seoul.html` | E2 | `.subtitle` | 1.12 | 1.00 | CONFIRME |
| `retour-a-seoul.html` | E2 | `header.nuit` | 1.14 | 1.00 | ECARTE (aucun texte porte par la regle) |
| `retour-a-seoul.html` | E2 | `.back-link` | 3.19 | 2.78 | CONFIRME |
| `rosetta.html` | E1 | `.section-head .tag` | 2.70 | 2.70 | CONFIRME |
| `rosetta.html` | E1 | `.fiche dt` | 4.30 | 4.30 | CONFIRME |
| `sans-filtre.html` | E2 | `.meta-line` | 1.72 | 1.00 | CONFIRME |
| `sans-filtre.html` | E2 | `.back-link` | 1.81 | 1.00 | CONFIRME |
| `sans-filtre.html` | E2 | `.title-orig` | 1.90 | 1.00 | CONFIRME |
| `sans-filtre.html` | E2 | `.trois-services` | 1.99 | 1.00 | ECARTE (aucun texte porte par la regle) |
| `sans-filtre.html` | E2 | `.subtitle` | 2.47 | 1.00 | CONFIRME |
| `sans-filtre.html` | E2 | `header.menu` | 2.75 | 1.00 | ECARTE (aucun texte porte par la regle) |
| `sans-filtre.html` | E2 | `.back-link:hover` | 3.02 | - | ECARTE (regle sans element rendu) |
| `shutter-island.html` | E1 | `.redact` | 1.00 | - | ECARTE (regle sans element rendu) |
| `shutter-island.html` | E1 | `.folder-tab` | 2.42 | 2.42 | CONFIRME |
| `shutter-island.html` | E1 | `footer.endnote` | 3.81 | 3.81 | CONFIRME |
| `shutter-island.html` | E2 | `.back-link` | 3.81 | 3.81 | CONFIRME |
| `soudain-lete-dernier.html` | E1 | `.edge-code` | 4.05 | 4.05 | ECARTE (aucun texte porte par la regle) |
| `soudain-lete-dernier.html` | E1 | `footer.endnote` | 4.32 | 4.32 | CONFIRME |
| `soudain-lete-dernier.html` | E2 | `.frame-border::before, .frame-border::after` | 4.32 | - | ECARTE (regle sans element rendu) |
| `sur-la-route-domaha.html` | E1 | `footer.endnote` | 3.38 | 3.38 | CONFIRME |
| `sur-la-route-domaha.html` | E2 | `.cachet` | 3.94 | 3.94 | CONFIRME |
| `sur-la-route-domaha.html` | E2 | `.back-link` | 4.11 | 3.38 | CONFIRME |
| `waterloo.html` | E2 | `.back-link:hover` | 3.93 | - | ECARTE (regle sans element rendu) |
| `waterloo.html` | E2 | `.back-link` | 4.48 | 4.48 | CONFIRME |

## 2. Recensement independant au rendu reel -- le tableau definitif

| Mesure | Valeur |
|---|---|
| Pages balayees | 34 |
| **Couples sous le seuil** | **221** |
| Pages concernees | 33 / 34 |
| dont pages **migrees en v2** (les 9 du prototype) | 43 couples |
| dont pages **non migrees** (retrofit 065-5) | 178 couples |

*Lecture : le comptage statique en annoncait 71 en se declarant borne
basse. Le rendu reel en mesure **221**. L'ecart ne vient pas d'une
aggravation du site mais de ce que le premier outil ne pouvait pas voir :
l'appariement d'un texte avec son fond reel.*

### Par nature d'ecart

| Nature | Nombre | Ce que l'arbitrage doit trancher |
|---|---|---|
| texte courant (seuil 4,5:1) | **176** | Texte courant sur fond uniforme. Seuil 4,5:1. Le coeur de la lisibilite. |
| fond en degrade : echoue sur une PARTIE du fond | **36** | Le fond est un degrade : le texte PASSE sur certaines zones et ECHOUE sur d'autres. Le ratio donne est le pire cas du degrade. |
| opacite < 1 | **6** | L'echec vient d'une opacite inferieure a 1 : la couleur pleine passerait. L'arbitrage porte sur l'opacite, pas sur la palette. |
| grand texte (seuil 3:1) | **2** | Grand texte (>= 24 px, ou >= 18,66 px en gras). Seuil 3:1. |
| identite de couleur (ratio 1,00) | **1** | Texte de la couleur exacte de son fond. A verifier : effet voulu (caviardage) ou defaut. |

### Par page

| Page | Migree v2 | Couples sous le seuil | Pire ratio |
|---|---|---|---|
| `pandora.html` | oui | 15 | 1.00 |
| `soudain-lete-dernier.html` | non | 15 | 2.96 |
| `index.html` | oui | 13 | 3.70 |
| `shutter-island.html` | non | 13 | 2.42 |
| `pandora-contrechamp.html` | oui | 12 | 1.72 |
| `julie-en-12-chapitres.html` | non | 10 | 1.60 |
| `le-doulos.html` | non | 9 | 3.38 |
| `le-samourai.html` | non | 9 | 3.09 |
| `rosetta.html` | non | 9 | 2.30 |
| `annie-hall.html` | non | 8 | 3.70 |
| `hitchcock-truffaut.html` | non | 8 | 2.52 |
| `au-fil-de-leau.html` | non | 7 | 2.16 |
| `hamlet.html` | non | 7 | 2.96 |
| `hamnet.html` | non | 7 | 3.54 |
| `le-cheval-de-turin.html` | non | 7 | 1.00 |
| `sur-la-route-domaha.html` | non | 7 | 2.91 |
| `raging-bull.html` | non | 6 | 2.37 |
| `la-chevauchee-fantastique.html` | non | 5 | 1.00 |
| `sans-filtre.html` | non | 5 | 2.75 |
| `waterloo.html` | non | 5 | 2.33 |
| `bienvenue-a-suburbicon.html` | non | 4 | 2.33 |
| `la-nuit-de-san-lorenzo.html` | non | 4 | 2.32 |
| `le-golem.html` | non | 4 | 2.33 |
| `les-deux-orphelines.html` | non | 4 | 1.74 |
| `persona.html` | non | 4 | 2.68 |
| `retour-a-seoul.html` | non | 4 | 2.78 |
| `la-mariee-etait-en-noir.html` | non | 3 | 2.24 |
| `manhattan.html` | non | 3 | 3.48 |
| `moi-daniel-blake.html` | non | 3 | 2.21 |
| `nouvelle-vague.html` | non | 3 | 1.91 |
| `rouges-et-blancs.html` | oui | 3 | 1.11 |
| `soy-cuba.html` | non | 3 | 3.18 |
| `sud.html` | non | 2 | 3.98 |

### Detail complet -- une ligne par couple, page par page

Colonnes : `ratio` = pire cas mesure - `seuil` = exigence applicable -
`opac.` = opacite effective - `px` = taille reelle.

#### `annie-hall.html` -- 8 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `html > body > header.hero > div.eyebrow` | `#7a7a74` | `#f1ede4` | **3.70** | 4.5 | 1.00 | 12 | Analyse cinématographique |
| `html > body > header.hero > div.meta` | `#7a7a74` | `#f1ede4` | **3.70** | 4.5 | 1.00 | 14 | États-Unis · 93 minutes · Comédie dramatique  |
| `html > body > header.hero > a.back-link` | `#7a7a74` | `#f1ede4` | **3.70** | 4.5 | 1.00 | 13 | ← Retour aux analyses |
| `html > body > footer` | `#7a7a74` | `#f1ede4` | **3.70** | 4.5 | 1.00 | 13 | Analyse rédigée à titre d'exercice critique e |
| `html > body > nav.toc > div.toc-title` | `#7a7a74` | `#faf8f4` | **4.07** | 4.5 | 1.00 | 12 | Sommaire |
| `fiche-layout > div.fact-grid > div > div.label` | `#7a7a74` | `#faf8f4` | **4.07** | 4.5 | 1.00 | 11 | Réalisation |
| `section#personnages > blockquote > cite` | `#7a7a74` | `#faf8f4` | **4.07** | 4.5 | 1.00 | 13 | — Alvy Singer |
| `section#themes > table > caption` | `#7a7a74` | `#faf8f4` | **4.07** | 4.5 | 1.00 | 13 | Principales tensions thématiques du film |

#### `au-fil-de-leau.html` -- 7 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `html > body > footer.colophon-final` | `#8fa39b` | `#ece7da` | **2.16** | 4.5 | 1.00 | 11 | Analyse sourcée · rédigée le 5 juillet 2026 · |
| `section#fiche > div.folio > span.num` | `#b98d3f` | `#ece7da` | **2.45** | 4.5 | 1.00 | 18 | Ch. I |
| `iv.river-inner > div.river-eyebrow > span.mono` | `#b98d3f` | `#415343` | **2.73** | 4.5 | 1.00 | 11 | Analyse cinématographique |
| `> header.river > div.river-inner > a.back-link` | `#8fa39b` | `#415343` | **3.10** | 4.5 | 1.00 | 11 | ← Retour aux analyses |
| ` header.river > div.river-inner > p.title-orig` | `#8fa39b` | `#415343` | **3.10** | 4.5 | 1.00 | 22 | House by the River |
| `header.river > div.river-inner > div.meta-line` | `#8fa39b` | `#415343` | **3.10** | 4.5 | 1.00 | 12 | États-Unis · Republic Pictures · 88 minutes · |
| `iv.river-inner > div.river-eyebrow > span.wave` | `#c39f5e` | `#415343` | **3.32** | 4.5 | 0.80 | 12 | ≈≈≈ |

#### `bienvenue-a-suburbicon.html` -- 4 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `section#fiche > div.panneau > span.lot` | `#e0876b` | `#f4efe3` | **2.33** | 4.5 | 1.00 | 10 | Lot 1 · Acte de vente |
| `er.brochure > div.brochure-inner > a.back-link` | `#f4efe3` | `#3e8f8a` | **3.33** | 4.5 | 1.00 | 11 | ← Retour aux analyses |
| `der.brochure > div.brochure-inner > p.subtitle` | `#f4efe3` | `#3e8f8a` | **3.33** | 4.5 | 1.00 | 17 | George Clooney, 2017 — un scénario noir des f |
| ` div.brochure-inner > div.brochure-meta > span` | `#f4efe3` | `#3e8f8a` | **3.33** | 4.5 | 1.00 | 11 | États-Unis · Paramount |

#### `hamlet.html` -- 7 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `> header.dalle > div.dalle-inner > span.cartel` | `#c08a52` | `#434b50` | **2.96** | 4.5 | 1.00 | 12 | Union soviétique — 1964 — Lenfilm |
| ` > body > nav.grille > div.inner > span.cartel` | `#c08a52` | `#414a4f` | **3.02** | 4.5 | 1.00 | 12 | Sommaire |
| `dy > header.dalle > div.dalle-inner > a.retour` | `#8a9a9d` | `#434b50` | **3.05** | 4.5 | 1.00 | 13 | ← Retour aux analyses |
| ` header.dalle > div.dalle-inner > div.titre-vo` | `#8a9a9d` | `#434b50` | **3.05** | 4.5 | 1.00 | 17 | Гамлет — |
| `er.dalle > div.dalle-inner > div.titre-vo > em` | `#8a9a9d` | `#434b50` | **3.05** | 4.5 | 1.00 | 17 | Gamlet |
| `av.grille > div.inner > ol > li > a > span.num` | `#8a9a9d` | `#414a4f` | **3.10** | 4.5 | 1.00 | 12 | I |
| `section#production > h3` | `#98602c` | `#eceeeb` | **4.45** | 4.5 | 1.00 | 17 | Refuser le studio |

#### `hamnet.html` -- 7 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `iche > div.frame-head > h2 > span.frame-jargon` | `#7a6c48` | `#e5d4b4` | **3.54** | 4.5 | 1.00 | 14 | — colophon |
| `section#synopsis > p.caution` | `#7a6c48` | `#e5d4b4` | **3.54** | 4.5 | 1.00 | 14 | La scène finale, construite comme une représe |
| `section#synopsis > p.caution > em` | `#7a6c48` | `#e5d4b4` | **3.54** | 4.5 | 1.00 | 14 | Hamlet |
| `html > body > footer.endnote` | `#7a6c48` | `#e5d4b4` | **3.54** | 4.5 | 1.00 | 11 | Manuscrit compilé à partir de sources publiqu |
| `html > body > footer.endnote > a` | `#7a6c48` | `#e5d4b4` | **3.54** | 4.5 | 1.00 | 11 | ← Retour aux analyses |
| `> header.cover > div.cover-inner > a.back-link` | `#7a6c48` | `#e7d9b6` | **3.69** | 4.5 | 1.00 | 12 | ← Retour aux analyses |
| `section#miseenscene > div.pinned > cite` | `#7a6c48` | `#eadfc3` | **3.90** | 4.5 | 1.00 | 11 | IndieWire, critique de 2025 |

#### `hitchcock-truffaut.html` -- 8 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `on#sources > div.tete-section > span.piste-num` | `#15120f` | `#7a4a24` | **2.52** | 4.5 | 1.00 | 14 | S |
| `> div.bobine-inner > div.compteur > span.rouge` | `#c1201d` | `#241e19` | **2.74** | 4.5 | 1.00 | 12 | 8 |
| `er.bobine > div.bobine-inner > h1 > span.barre` | `#c1201d` | `#1b1815` | **2.94** | 3.0 | 1.00 | 46 | / |
| `#fiche > div.tete-section > div > span.libelle` | `#8b8073` | `#f1ece1` | **3.28** | 4.5 | 1.00 | 10 | Bande 1 / 9 |
| `tion#fiche > div.fiche > dl.credits > div > dt` | `#8b8073` | `#f1ece1` | **3.28** | 4.5 | 1.00 | 10 | Titre |
| `html > body > footer > span` | `#8b8073` | `#f1ece1` | **3.28** | 4.5 | 1.00 | 10 | Analyse rédigée à partir des sources ci-dessu |
| `#mise-en-scene > div.transcription > span.voix` | `#c1201d` | `#e5ddcc` | **4.45** | 4.5 | 1.00 | 10 | Bande — au sujet de Psychose |
| `-scene > div.transcription > p > sup.piste > a` | `#c1201d` | `#e5ddcc` | **4.45** | 4.5 | 1.00 | 10 | 2 |

#### `index.html` -- 13 couple(s) *(migree v2)*

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `> div.wrap > div.seuil-in > div.reserve-auteur` | `#7a7a74` | `#f1ede4` | **3.70** | 4.5 | 1.00 | 14 | Le chapeau du seuil (3 à 5 paragraphes posant |
| `p > div.seuil-in > div.reserve-auteur > strong` | `#7a7a74` | `#f1ede4` | **3.70** | 4.5 | 1.00 | 14 | texte d'AH |
| `rap > div.seuil-in > div.reserve-auteur > code` | `#7a7a74` | `#f1ede4` | **3.70** | 4.5 | 1.00 | 14 | _scratch\prototypes-accueil\accueil-A-le-seui |
| `div#bloc-une > article.carte-une > div.meta` | `#7a7a74` | `#f1ede4` | **3.70** | 4.5 | 1.00 | 12 | Albert Lewin · 1951 — publiée le 18 juillet 2 |
| `html > body > footer > div.f-in` | `#7a7a74` | `#f1ede4` | **3.70** | 4.5 | 1.00 | 13 | Analyses rédigées à titre d'exercice critique |
| `> header.chrome > div.chrome-in > nav.menu > a` | `#7a7a74` | `#faf8f4` | **4.07** | 4.5 | 1.00 | 14 | Critiques |
| `tion.seuil > div.wrap > div.seuil-in > p.appui` | `#7a7a74` | `#faf8f4` | **4.07** | 4.5 | 1.00 | 14 | Sur la méthode, ses limites et son journal d' |
| `div#bloc-une > article.carte-une > div.meta` | `#7a7a74` | `#faf8f4` | **4.07** | 4.5 | 1.00 | 12 | Albert Lewin · 1951 — publiée le 18 juillet 2 |
| `div#liaison` | `#7a7a74` | `#faf8f4` | **4.07** | 4.5 | 1.00 | 11 | Même film, deux régimes — champ et contrecham |
| `iv#facettes > div.facette > span.titre-facette` | `#7a7a74` | `#faf8f4` | **4.07** | 4.5 | 1.00 | 10 | Volet |
| `div#compte` | `#7a7a74` | `#faf8f4` | **4.07** | 4.5 | 1.00 | 11 | 33 analyses — sur 33 |
| `ol#liste > li > a.entree > span.a` | `#7a7a74` | `#faf8f4` | **4.07** | 4.5 | 1.00 | 12 | 1977 |
| `ol#liste > li > a.entree > span.d` | `#7a7a74` | `#faf8f4` | **4.07** | 4.5 | 1.00 | 13 | Woody Allen — Comédie dramatique romantique |

#### `julie-en-12-chapitres.html` -- 10 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `ouverture > div.couverture-inner > a.back-link` | `#8d939e` | `#826a6f` | **1.60** | 4.5 | 1.00 | 11 | ← Retour aux analyses |
| `verture > div.couverture-inner > div.meta-line` | `#8d939e` | `#826a6f` | **1.60** | 4.5 | 1.00 | 10 | Norvège / France / Suède / Danemark · 128 min |
| `couverture > div.couverture-inner > div.auteur` | `#c98a77` | `#826a6f` | **1.74** | 4.5 | 1.00 | 11 | Joachim Trier |
| `section#fiche > div.chapitre-tete > span.no` | `#c98a77` | `#f5f2ec` | **2.54** | 4.5 | 1.00 | 10 | Prologue |
| `che-layout > div.pagedegarde > div > div.label` | `#8d939e` | `#f5f2ec` | **2.76** | 4.5 | 1.00 | 10 | Réalisation |
| `section#reception > blockquote > span.attrib` | `#8d939e` | `#f5f2ec` | **2.76** | 4.5 | 1.00 | 10 | Consensus Rotten Tomatoes, cité par Wikipédia |
| `html > body > footer.acheve` | `#8d939e` | `#f5f2ec` | **2.76** | 4.5 | 1.00 | 10 | Analyse sourcée · rédigée le 6 juillet 2026 · |
| `html > body > nav.matiere > ol > li > span.no` | `#c98a77` | `#ffffff` | **2.84** | 4.5 | 1.00 | 11 | Prologue |
| `re > div.couverture-inner > div > span.bandeau` | `#26344d` | `#c98a77` | **4.39** | 4.5 | 1.00 | 10 | Verdens verste menneske · « La pire personne  |
| `couverture > div.couverture-inner > p.subtitle` | `#f5f2ec` | `#826a6f` | **4.43** | 4.5 | 1.00 | 17 | 2021 — quatre ans de la vie d'une femme qui e |

#### `la-chevauchee-fantastique.html` -- 5 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `v.ligne-inner > div.itineraire > span > strong` | `#241a12` | `#241a12` | **1.00** | 4.5 | 1.00 | 10 | Lordsburg |
| `ligne > div.ligne-inner > div > span.compagnie` | `#a63d2f` | `#363b41` | **1.79** | 4.5 | 1.00 | 11 | Overland Stage Line · Territoire de l'Arizona |
| `div.ligne-inner > div.itineraire > span.fleche` | `#a63d2f` | `#363b41` | **1.79** | 4.5 | 1.00 | 10 | → |
| `eption > blockquote > span.attrib > sup.fn > a` | `#4a6d8c` | `#ddcda9` | **3.47** | 4.5 | 1.00 | 10 | [3] |
| `section#synopsis > p > sup.fn > a` | `#4a6d8c` | `#e9dbbd` | **3.97** | 4.5 | 1.00 | 10 | [1] |

#### `la-mariee-etait-en-noir.html` -- 3 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `iche-layout > div.etat-civil > div > div.label` | `#a5a19a` | `#f1efe9` | **2.24** | 4.5 | 1.00 | 10 | Réalisation |
| `section#reception > blockquote > span.attrib` | `#a5a19a` | `#f1efe9` | **2.24** | 4.5 | 1.00 | 10 | Jean-Louis Bory, 1968, cité par Wikipédia |
| `html > body > footer.condoleances` | `#a5a19a` | `#f1efe9` | **2.24** | 4.5 | 1.00 | 10 | Analyse sourcée · rédigée le 6 juillet 2026 · |

#### `la-nuit-de-san-lorenzo.html` -- 4 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `section#structure > div.voix > sup.ref > a` | `#c08a2c` | `#eae0cd` | **2.32** | 4.5 | 1.00 | 12 | 3 |
| `fiche-wrap > div.fiche > dl > dd > sup.ref > a` | `#c08a2c` | `#f4ede1` | **2.61** | 4.5 | 1.00 | 12 | 1 |
| `tion#reception > div.dossier > p > sup.ref > a` | `#c08a2c` | `#fbf6ec` | **2.82** | 4.5 | 1.00 | 12 | 9 |
| `v.veillee > div.inner > ol > li > a > span.num` | `#c08a2c` | `#1e3457` | **4.11** | 4.5 | 1.00 | 12 | I |

#### `le-cheval-de-turin.html` -- 7 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `html > body > footer.extinction` | `#d9d6cf` | `#d9d6cf` | **1.00** | 4.5 | 1.00 | 10 | Analyse sourcée · rédigée le 5 juillet 2026 · |
| `section#reception > blockquote > span.attrib` | `#8d867b` | `#cfccc6` | **2.25** | 4.5 | 1.00 | 10 | A. O. Scott, New York Times, cité par Wikipéd |
| `iv.storm-inner > div.storm-eyebrow > span.mono` | `#9c7b45` | `#413c35` | **2.77** | 4.5 | 1.00 | 11 | Analyse cinématographique |
| `iv.storm-inner > div.ephemeride > span.jour-vi` | `#9c7b45` | `#413c35` | **2.77** | 4.5 | 1.00 | 11 | Jour VI — obscurité |
| `> header.storm > div.storm-inner > a.back-link` | `#8d867b` | `#413c35` | **3.03** | 4.5 | 1.00 | 11 | ← Retour aux analyses |
| ` header.storm > div.storm-inner > p.title-orig` | `#8d867b` | `#413c35` | **3.03** | 4.5 | 1.00 | 18 | A torinói ló |
| `torm > div.storm-inner > div.ephemeride > span` | `#8d867b` | `#413c35` | **3.03** | 4.5 | 1.00 | 11 | Jour I |

#### `le-doulos.html` -- 9 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `section#miseenscene > div.coupure > cite` | `#79715f` | `#e1d7bf` | **3.38** | 4.5 | 1.00 | 10 | Claude Beylie, Cahiers du Cinéma, cité par Mo |
| `he > div.colonne-head > h2 > span.colonne-sous` | `#79715f` | `#e0dbcd` | **3.50** | 4.5 | 1.00 | 12 | — état civil du film |
| `section#synopsis > p.discretion` | `#79715f` | `#e0dbcd` | **3.50** | 4.5 | 1.00 | 13 | Le film retarde son verdict jusqu'aux toutes  |
| `div.cover-inner > div.avis-sheet > a.back-link` | `#79715f` | `#ece5d5` | **3.86** | 4.5 | 1.00 | 11 | ← Retour aux analyses |
| `cover-inner > div.avis-sheet > div.avis-number` | `#79715f` | `#ece5d5` | **3.86** | 4.5 | 1.00 | 12 | Avis n  — un mot d'argot pour deux vérités :  |
| `inner > div.avis-sheet > div.avis-number > sup` | `#79715f` | `#ece5d5` | **3.86** | 4.5 | 1.00 | 10 | o |
| `html > body > footer.endnote` | `#79715f` | `#ece5d5` | **3.86** | 4.5 | 1.00 | 10 | Avis compilé à partir de sources publiques co |
| `html > body > footer.endnote > a` | `#79715f` | `#ece5d5` | **3.86** | 4.5 | 1.00 | 10 | ← Retour aux analyses |
| ` div.cover-inner > div.avis-sheet > div.cachet` | `#576b77` | `#ece5d5` | **4.43** | 4.5 | 0.85 | 11 | 8 FÉV.1963 |

#### `le-golem.html` -- 4 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `section#fiche > div.signe > span.ref` | `#b78c2e` | `#e9dfc8` | **2.33** | 4.5 | 1.00 | 11 | Signe I |
| `eption > blockquote > span.attrib > sup.fn > a` | `#7c4326` | `#171310` | **2.36** | 4.5 | 1.00 | 10 | [3] |
| `grenier > div.grenier-inner > div > span.sceau` | `#b78c2e` | `#553928` | **3.40** | 4.5 | 1.00 | 10 | Prague · règne de Rodolphe II · d'après la lé |
| `html > body > footer.poussiere` | `#80796c` | `#171310` | **4.28** | 4.5 | 1.00 | 10 | Analyse sourcée · rédigée le 6 juillet 2026 · |

#### `le-samourai.html` -- 9 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `der.quai.carrelage > div.quai-inner > a.retour` | `#6d7a86` | `#d6d9d5` | **3.09** | 4.5 | 1.00 | 11 | ← Retour aux analyses |
| `relage > div.quai-inner > div.direction > span` | `#6d7a86` | `#d6d9d5` | **3.09** | 4.5 | 1.00 | 11 | terminus |
| `section#sources > div.note` | `#6d7a86` | `#dfe2dc` | **3.36** | 4.5 | 1.00 | 11 | Sources effectivement consultées lors de la p |
| `on#fiche > div.station > div > span.quai-label` | `#6d7a86` | `#eceee9` | **3.76** | 4.5 | 1.00 | 10 | Station 1 |
| `tion#fiche > div.fiche > dl.credits > div > dt` | `#6d7a86` | `#eceee9` | **3.76** | 4.5 | 1.00 | 10 | Titre |
| `fiche > div.fiche > figure.poster > figcaption` | `#6d7a86` | `#eceee9` | **3.76** | 4.5 | 1.00 | 10 | Affiche d'exploitation — le chapeau, l'imperm |
| `section#mise-en-scene > blockquote > cite` | `#6d7a86` | `#eceee9` | **3.76** | 4.5 | 1.00 | 10 | Jean-Pierre Melville, entretien avec Rui Nogu |
| `section#mise-en-scene > blockquote > cite > em` | `#6d7a86` | `#eceee9` | **3.76** | 4.5 | 1.00 | 10 | Sight and Sound |
| `html > body > footer > span` | `#6d7a86` | `#eceee9` | **3.76** | 4.5 | 1.00 | 10 | Analyse rédigée à partir des sources ci-dessu |

#### `les-deux-orphelines.html` -- 4 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `rap > div.crosscut > p.cc-caption > sup.fn > a` | `#233a5c` | `#0a0806` | **1.74** | 4.5 | 1.00 | 11 | [1] |
| `he > div.wrap > div.fiche-wrap > dl.fiche > dt` | `#7c541f` | `#d8c9a4` | **4.07** | 4.5 | 1.00 | 11 | Titre français |
| `ction#reception > div.wrap > blockquote > cite` | `#7c541f` | `#d8c9a4` | **4.07** | 4.5 | 1.00 | 11 | Moving Picture World, cité par TCM |
| `body > nav.programme > ol > li > a > span.num` | `#a9752f` | `#1e1812` | **4.41** | 4.5 | 1.00 | 12 | 01 |

#### `manhattan.html` -- 3 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `section#fiche > div.mouvement > span.num` | `#7c828c` | `#f2f3f5` | **3.48** | 4.5 | 1.00 | 10 | 1er mouvement · Partition |
| `fiche-layout > div.partition > div > div.label` | `#7c828c` | `#f2f3f5` | **3.48** | 4.5 | 1.00 | 10 | Réalisation |
| `section#synopsis > p > sup.fn > a` | `#7c828c` | `#f2f3f5` | **3.48** | 4.5 | 1.00 | 10 | [1] |

#### `moi-daniel-blake.html` -- 3 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `html > body > footer.file-attente` | `#9aa0a4` | `#ebebe8` | **2.21** | 4.5 | 1.00 | 10 | Analyse sourcée · rédigée le 6 juillet 2026 · |
| `ody > header.mur > div.mur-inner > a.back-link` | `#9aa0a4` | `#373e44` | **4.10** | 4.5 | 1.00 | 11 | ← Retour aux analyses |
| `y > header.mur > div.mur-inner > div.meta-line` | `#9aa0a4` | `#373e44` | **4.10** | 4.5 | 1.00 | 10 | Royaume-Uni / France · 100 minutes · Couleur  |

#### `nouvelle-vague.html` -- 3 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `section#fiche > div.jour > span.ref` | `#d3a92c` | `#f0eee8` | **1.91** | 4.5 | 1.00 | 11 | Jour 1 · Générique |
| `section#synopsis > p > sup.fn > a` | `#d3a92c` | `#f0eee8` | **1.91** | 4.5 | 1.00 | 10 | [1] |
| `fiche-layout > div.generique > div > div.label` | `#8e8b82` | `#f0eee8` | **2.94** | 4.5 | 1.00 | 10 | Réalisation |

#### `pandora-contrechamp.html` -- 12 couple(s) *(migree v2)*

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `.cover > div.cover-inner > span.eyebrow.cartel` | `#2f7d80` | `#b8955f` | **1.72** | 4.5 | 1.00 | 11 | Royaume-Uni — 1951 — Technicolor · Contrecham |
| `r.cover > div.cover-inner > div.provenance > a` | `#2f7d80` | `#b8955f` | **1.72** | 4.5 | 1.00 | 12 | → Voir aussi le champ : analyse du pipeline ( |
| `n#fiche > div.fiche-wrap > div.fiche > dl > dt` | `#8d8677` | `#e2d6bd` | **2.51** | 4.5 | 1.00 | 10 | Titre original |
| `html > body > nav.programme > span.cartel` | `#8d8677` | `#f2ead9` | **3.02** | 4.5 | 1.00 | 11 | Sommaire |
| ` > div.fiche-wrap > figure.poster > figcaption` | `#8d8677` | `#f2ead9` | **3.02** | 4.5 | 1.00 | 10 | Affiche d'exploitation — collection de référe |
| `fiche-wrap > div.fiche > dl > dd > sup.ref > a` | `#2f7d80` | `#e2d6bd` | **3.34** | 4.5 | 1.00 | 10 | 2 |
| `eader.cover > div.cover-inner > div.orig-title` | `#3f4550` | `#b8955f` | **3.44** | 4.5 | 1.00 | 17 | Pandora and the Flying Dutchman |
| `header.cover > div.cover-inner > div.meta-line` | `#3f4550` | `#b8955f` | **3.44** | 4.5 | 1.00 | 12 | Albert Lewin · Romulus Films · Photographie d |
| `eader.cover > div.cover-inner > div.provenance` | `#3f4550` | `#b8955f` | **3.44** | 4.5 | 1.00 | 12 | Analyse déléguée — OpenAI GPT-5.5, relecture  |
| `.cover > div.cover-inner > div.content-warning` | `#3f4550` | `#b8955f` | **3.44** | 4.5 | 1.00 | 14 | Le film comporte un suicide par empoisonnemen |
| `html > body > div.wrap > p.variante > a` | `#2f7d80` | `#f2ead9` | **4.02** | 4.5 | 1.00 | 14 | Pandora — Champ — Critique |
| `body > nav.programme > ol > li > a > span.num` | `#2f7d80` | `#f2ead9` | **4.02** | 4.5 | 1.00 | 13 | I |

#### `pandora.html` -- 15 couple(s) *(migree v2)*

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `.cover > div.cover-inner > span.eyebrow.cartel` | `#c9a97a` | `#c9a97a` | **1.00** | 4.5 | 1.00 | 11 | Royaume-Uni — 1951 — Technicolor |
| `eader.cover > div.cover-inner > div.orig-title` | `#e2d6bd` | `#c9a97a` | **1.55** | 4.5 | 1.00 | 17 | Pandora and the Flying Dutchman |
| `header.cover > div.cover-inner > div.meta-line` | `#e2d6bd` | `#c9a97a` | **1.55** | 4.5 | 1.00 | 12 | Albert Lewin · Romulus Films · Photographie d |
| `dy > header.cover > div.cover-inner > div.note` | `#e2d6bd` | `#c9a97a` | **1.55** | 4.5 | 1.00 | 12 | Analyse du pipeline — Claude (routine nocturn |
| ` header.cover > div.cover-inner > div.note > a` | `#e2d6bd` | `#c9a97a` | **1.55** | 4.5 | 1.00 | 12 | → Voir aussi le contrechamp : analyse délégué |
| `.cover > div.cover-inner > div.content-warning` | `#e2d6bd` | `#c9a97a` | **1.55** | 4.5 | 1.00 | 14 | Le film comporte un suicide par empoisonnemen |
| `er > div.cover-inner > a.back-link.lien-retour` | `#f2ead9` | `#c9a97a` | **1.86** | 4.5 | 1.00 | 14 | Retour aux analyses |
| `l > body > header.cover > div.cover-inner > h1` | `#f2ead9` | `#c9a97a` | **1.86** | 3.0 | 1.00 | 90 | Pandora |
| `er.cover > div.cover-inner > div.note > strong` | `#f2ead9` | `#c9a97a` | **1.86** | 4.5 | 1.00 | 12 | Provenance. |
| `body > nav.programme > ol > li > a > span.num` | `#c9a97a` | `#f2ead9` | **1.86** | 4.5 | 1.00 | 13 | I |
| `n#fiche > div.fiche-wrap > div.fiche > dl > dt` | `#8d8677` | `#e2d6bd` | **2.51** | 4.5 | 1.00 | 10 | Titre original |
| `html > body > nav.programme > span.cartel` | `#8d8677` | `#f2ead9` | **3.02** | 4.5 | 1.00 | 11 | Sommaire |
| ` > div.fiche-wrap > figure.poster > figcaption` | `#8d8677` | `#f2ead9` | **3.02** | 4.5 | 1.00 | 10 | Affiche d'exploitation — collection de référe |
| `fiche-wrap > div.fiche > dl > dd > sup.ref > a` | `#2f7d80` | `#e2d6bd` | **3.34** | 4.5 | 1.00 | 10 | 1 |
| `section#synopsis > p > sup.ref > a` | `#2f7d80` | `#f2ead9` | **4.02** | 4.5 | 1.00 | 10 | 7 |

#### `persona.html` -- 4 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `es > div.cast-grid > div.cast-card > span.role` | `#8c8c86` | `#e5e5e2` | **2.68** | 4.5 | 1.00 | 12 | Bibi Andersson |
| `tion#fiche > div.carton > span.num-leader.mono` | `#8c8c86` | `#e9e9e6` | **2.78** | 4.5 | 1.00 | 14 | 01 |
| `> div.fiche-wrap > div.fact-grid > div > div.k` | `#8c8c86` | `#e9e9e6` | **2.78** | 4.5 | 1.00 | 11 | Réalisation, scénario |
| `> header.cover > div.cover-inner > a.back-link` | `#6c6c68` | `#0d0d0c` | **3.69** | 4.5 | 0.75 | 10 | ← Retour aux analyses |

#### `raging-bull.html` -- 6 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `ntexte > blockquote > span.attrib > sup.fn > a` | `#a8842c` | `#ddd4bd` | **2.37** | 4.5 | 1.00 | 10 | [4] |
| `section#fiche > div.round-head > span.bell` | `#a8842c` | `#e5decc` | **2.61** | 4.5 | 1.00 | 11 | Round 1 · Pesée officielle |
| `section#synopsis > p > sup.fn > a` | `#a8842c` | `#e5decc` | **2.61** | 4.5 | 1.00 | 10 | [1] |
| `section#contexte > blockquote > span.attrib` | `#7b756a` | `#ddd4bd` | **3.10** | 4.5 | 1.00 | 10 | Martin Scorsese, cité par Cinephilia & Beyond |
| `.fiche-layout > div.weigh-in > div > div.label` | `#7b756a` | `#e5decc` | **3.41** | 4.5 | 1.00 | 10 | Réalisation |
| `html > body > footer.final` | `#7b756a` | `#e5decc` | **3.41** | 4.5 | 1.00 | 10 | Analyse sourcée · rédigée le 5 juillet 2026 · |

#### `retour-a-seoul.html` -- 4 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `html > body > footer.classement` | `#8a9199` | `#eef0ef` | **2.78** | 4.5 | 1.00 | 10 | Analyse sourcée · rédigée le 6 juillet 2026 · |
| `nuit > div.nuit-inner > div > span.dossier-ref` | `#d63a63` | `#452634` | **2.94** | 4.5 | 1.00 | 10 | Dossier d'adoption · Hammond · réf. K-85 |
| `y > header.nuit > div.nuit-inner > a.back-link` | `#8a9199` | `#452634` | **4.17** | 4.5 | 1.00 | 11 | ← Retour aux analyses |
| `> header.nuit > div.nuit-inner > div.meta-line` | `#8a9199` | `#452634` | **4.17** | 4.5 | 1.00 | 10 | France / Allemagne / Belgique / Qatar / Cambo |

#### `rosetta.html` -- 9 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `header.cover > div.id-card > div.id-top > span` | `#8f8c7e` | `#d8d5c9` | **2.30** | 4.5 | 1.00 | 10 | DOSSIER N° 94/1999 |
| `d-card > div.id-body > div.id-fields > div > b` | `#8f8c7e` | `#d8d5c9` | **2.30** | 4.5 | 1.00 | 10 | NOM |
| ` body > header.cover > div.id-card > div.stamp` | `#d96d30` | `#d8d5c9` | **2.31** | 4.5 | 0.82 | 18 | PRÉCARITÉ |
| `fiche > div.wrap > div.section-head > span.tag` | `#d9560f` | `#d8d5c9` | **2.70** | 4.5 | 1.00 | 11 | 01 |
| `tml > body > header.cover > span.label.eyebrow` | `#d9560f` | `#26251f` | **3.87** | 4.5 | 1.00 | 11 | Analyse cinématographique — drame social · 19 |
| `header.cover > div.cover-title > div.meta-line` | `#d9560f` | `#26251f` | **3.87** | 4.5 | 1.00 | 12 | JEAN-PIERRE & LUC DARDENNE — 1999 — BELGIQUE  |
| `iv.circuit-ring > div.circuit-stop > span.time` | `#d9560f` | `#26251f` | **3.87** | 4.5 | 1.00 | 10 | 06:40 |
| `he > div.wrap > div.fiche-wrap > dl.fiche > dt` | `#a3410b` | `#d8d5c9` | **4.30** | 4.5 | 1.00 | 10 | Titre |
| `ction#reception > div.wrap > blockquote > cite` | `#a3410b` | `#d8d5c9` | **4.30** | 4.5 | 1.00 | 11 | Jean-Pierre Dardenne, The Guardian, cité par  |

#### `rouges-et-blancs.html` -- 3 couple(s) *(migree v2)*

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `ap > div.geometry > div.geo-field > svg > text` | `#0c0c0b` | `#1a1914` | **1.11** | 4.5 | 1.00 | 9 | MONASTÈRE |
| `> header.cover > div.cover-frame > h1 > span.r` | `#9a2020` | `#26251f` | **1.90** | 3.0 | 1.00 | 70 | Rouges |
| `body > nav.programme > ol > li > a > span.num` | `#9a2020` | `#050504` | **2.53** | 4.5 | 1.00 | 12 | 01 |

#### `sans-filtre.html` -- 5 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `section#fiche > div.service > span.num` | `#b2903f` | `#f6f4ee` | **2.75** | 4.5 | 1.00 | 10 | Premier service |
| `he-layout > div.embarquement > div > div.label` | `#b2903f` | `#f6f4ee` | **2.75** | 4.5 | 1.00 | 10 | Réalisation & scénario |
| `html > body > footer.addition` | `#b2903f` | `#f6f4ee` | **2.75** | 4.5 | 1.00 | 10 | Analyse sourcée · rédigée le 6 juillet 2026 · |
| `section#reception > blockquote > span.attrib` | `#b2903f` | `#ffffff` | **3.02** | 4.5 | 1.00 | 10 | Titre de la critique cannoise de Bulles de Cu |
| `ody > header.menu > div.menu-inner > span.mono` | `#b2903f` | `#1d3d5c` | **3.71** | 4.5 | 1.00 | 10 | Analyse cinématographique · M/Y Christina O |

#### `shutter-island.html` -- 13 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `eader.cover > div.cover-inner > div.folder-tab` | `#ece3ca` | `#a88f61` | **2.42** | 4.5 | 1.00 | 12 | Ashecliffe Hospital — Service des dossiers |
| `section#miseenscene > div.pinned > cite` | `#7d7050` | `#e0d4b2` | **3.31** | 4.5 | 1.00 | 10 | Roger Ebert, critique de 2010 |
| ` div.frame-head > div > h2 > span.frame-jargon` | `#7d7050` | `#e1d9c2` | **3.46** | 4.5 | 1.00 | 12 | — pièce d'ouverture |
| `section#synopsis > p.caution` | `#7d7050` | `#e1d9c2` | **3.46** | 4.5 | 1.00 | 13 | Le mécanisme de la révélation finale, qui rec |
| `sources > div.sources-inner > span.stamp-label` | `#9c2b23` | `#c9b384` | **3.69** | 4.5 | 1.00 | 11 | Sources consultées |
| `div.telex > div.telex-inner > span.telex-label` | `#a9791f` | `#232c2d` | **3.70** | 4.5 | 1.00 | 10 | Bulletin — chiffres à l'appui |
| `div.cover-inner > div.case-sheet > a.back-link` | `#7d7050` | `#ece3ca` | **3.81** | 4.5 | 1.00 | 11 | ← Retour aux analyses |
| `cover-inner > div.case-sheet > div.case-number` | `#7d7050` | `#ece3ca` | **3.81** | 4.5 | 1.00 | 12 | Dossier n  — Ouvert le 3 juillet 2026 |
| `inner > div.case-sheet > div.case-number > sup` | `#7d7050` | `#ece3ca` | **3.81** | 4.5 | 1.00 | 10 | o |
| `html > body > footer.endnote` | `#7d7050` | `#ece3ca` | **3.81** | 4.5 | 1.00 | 10 | Dossier compilé à partir de sources publiques |
| `html > body > footer.endnote > a` | `#7d7050` | `#ece3ca` | **3.81** | 4.5 | 1.00 | 10 | ← Retour aux analyses |
| `.cover-inner > div.case-sheet > div.stamp-diag` | `#aa4c41` | `#ece3ca` | **4.30** | 4.5 | 0.82 | 13 | Confidentiel |
| `nner > div.case-sheet > div.stamp-diag > small` | `#aa4c41` | `#ece3ca` | **4.30** | 4.5 | 0.82 | 9 | Eyes only |

#### `soudain-lete-dernier.html` -- 15 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `a#ref-18b` | `#b23a2e` | `#1a1916` | **2.96** | 4.5 | 1.00 | 9 | [18] |
| `es > div.cast-grid > div.cast-card > span.role` | `#b23a2e` | `#1a1916` | **2.96** | 4.5 | 1.00 | 10 | Katharine Hepburn |
| `ction#sources > div.sources-inner > span.label` | `#b23a2e` | `#141311` | **3.13** | 4.5 | 1.00 | 11 | Sources consultées |
| `.frame-border > div.cover-eyebrow > span.label` | `#b23a2e` | `#0a0a09` | **3.34** | 4.5 | 1.00 | 11 | Planche contact — mélodrame gothique |
| `der > div.cover-media > dl.filecard > div > dt` | `#b23a2e` | `#0a0a09` | **3.34** | 4.5 | 1.00 | 10 | Réalisation |
| ` div.frame-heading-text > span.frame-num-label` | `#b23a2e` | `#0a0a09` | **3.34** | 4.5 | 1.00 | 11 | Négatif nº 01 |
| `a#ref-1` | `#b23a2e` | `#0a0a09` | **3.34** | 4.5 | 1.00 | 14 | [1] |
| `v.theme-list > div.theme-item > span.theme-tag` | `#b23a2e` | `#0a0a09` | **3.34** | 4.5 | 1.00 | 10 | Emprise maternelle et mémoire falsifiée |
| `ption > div.lighttable > span.lighttable-label` | `#7a756a` | `#e8e2d2` | **3.55** | 4.5 | 1.00 | 10 | Table lumineuse — chiffres à l'appui |
| `section#miseenscene > div.pinned > cite` | `#7a756a` | `#1a1916` | **3.83** | 4.5 | 1.00 | 10 | Variety, critique de 1959 |
| `over-inner > div.frame-border > span.frame-num` | `#7a756a` | `#0a0a09` | **4.32** | 4.5 | 1.00 | 11 | Bobine 01 · 35 mm |
| `iv.frame-heading-text > h2 > span.frame-jargon` | `#7a756a` | `#0a0a09` | **4.32** | 4.5 | 1.00 | 12 | — planche contact |
| `section#synopsis > p.caution` | `#7a756a` | `#0a0a09` | **4.32** | 4.5 | 1.00 | 12 | Le mécanisme de révélation final, construit c |
| `html > body > footer.endnote` | `#7a756a` | `#0a0a09` | **4.32** | 4.5 | 1.00 | 11 | Planche compilée à partir de sources publique |
| `html > body > footer.endnote > a` | `#7a756a` | `#0a0a09` | **4.32** | 4.5 | 1.00 | 11 | ← Retour aux analyses |

#### `soy-cuba.html` -- 3 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `a#ref-5c` | `#c3281c` | `#171410` | **3.18** | 4.5 | 1.00 | 8 | [5] |
| `a#ref-6f` | `#c3281c` | `#e3d6b4` | **3.99** | 4.5 | 1.00 | 12 | [6] |
| ` > body > main > p.content-note > span.eyebrow` | `#c3281c` | `#eedcc9` | **4.32** | 4.5 | 1.00 | 11 | Avis — contenu sensible |

#### `sud.html` -- 2 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `#miseenscene > div.road-diagram > span.eyebrow` | `#8a8271` | `#20281f` | **3.98** | 4.5 | 1.00 | 11 | Le plan final — env. 7 minutes, sans coupe ni |
| ` > body > main > p.content-note > span.eyebrow` | `#a05138` | `#eadecd` | **4.24** | 4.5 | 1.00 | 11 | Avis — contenu sensible |

#### `sur-la-route-domaha.html` -- 7 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `section#miseenscene > div.coupure > cite` | `#8a7c63` | `#e4d9bf` | **2.91** | 4.5 | 1.00 | 10 | Consensus critique, Rotten Tomatoes |
| `he > div.colonne-head > h2 > span.colonne-sous` | `#8a7c63` | `#e2decc` | **3.02** | 4.5 | 1.00 | 12 | — papiers du véhicule |
| `section#synopsis > p.discretion` | `#8a7c63` | `#e2decc` | **3.02** | 4.5 | 1.00 | 13 | Le film retient sa véritable destination — et |
| `div.cover-inner > div.avis-sheet > a.back-link` | `#8a7c63` | `#f1e9d8` | **3.38** | 4.5 | 1.00 | 11 | ← Retour aux analyses |
| `html > body > footer.endnote` | `#8a7c63` | `#f1e9d8` | **3.38** | 4.5 | 1.00 | 10 | Analyse compilée à partir de sources publique |
| `html > body > footer.endnote > a` | `#8a7c63` | `#f1e9d8` | **3.38** | 4.5 | 1.00 | 10 | ← Retour aux analyses |
| ` div.cover-inner > div.avis-sheet > div.cachet` | `#be653f` | `#f1e9d8` | **3.39** | 4.5 | 0.90 | 10 | 84MIN |

#### `waterloo.html` -- 5 couple(s)

| Element | Texte | Fond | Ratio | Seuil | Opac. | px | Extrait |
|---|---|---|---|---|---|---|---|
| `section#fiche > div.ordre > span.ref` | `#a07d33` | `#d3c9b1` | **2.33** | 4.5 | 1.00 | 10 | Ordre n°1 · État des forces |
| `che-layout > div.etat-forces > div > div.label` | `#a07d33` | `#d3c9b1` | **2.33** | 4.5 | 1.00 | 10 | Réalisation |
| `div.cartouche-inner > div > span.date-bataille` | `#a07d33` | `#3f321b` | **3.25** | 4.5 | 1.00 | 10 | Plateau de Mont-Saint-Jean · 18 juin 1815 |
| `.cartouche > div.cartouche-inner > a.back-link` | `#958b77` | `#3f321b` | **3.71** | 4.5 | 1.00 | 11 | ← Retour aux analyses |
| `div.cartouche-inner > div.forces > span.neutre` | `#958b77` | `#3f321b` | **3.71** | 4.5 | 1.00 | 11 | Italie / URSS · 134 min · Couleur |

