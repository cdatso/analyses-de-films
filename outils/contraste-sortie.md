# Comptage du contraste AA -- constat C-3 (P-39)

Outil : `outils/controle-contraste.py` (Python stdlib, ASCII pur).
COMPTAGE SEUL -- aucune palette n'est corrigee par cet outil.

Seuils : texte courant 4,5:1 ; grand texte 3:1.

E1 = ecart CERTAIN (couple ecrit dans la meme regle).
E2 = ecart PROBABLE (couleur en echec sur TOUS les fonds
declares par la page). Borne basse : ce qui passe sur au
moins un fond declare n'est pas compte.

## Resultat global

| Mesure | Valeur |
|---|---|
| Pages analysees | 34 |
| Couples texte/fond distincts examines | 421 |
| Ecarts CERTAINS (E1) | 23 |
| Ecarts PROBABLES (E2) | 48 |
| **Pages avec au moins un ecart CERTAIN** | **17 / 34** |
| Pages avec au moins un ecart, toutes classes | 25 / 34 |

## Par page

| Page | Fond | Luminance | Fonds declares | Couples | E1 | E2 |
|---|---|---|---|---|---|---|
| `shutter-island.html` | `#ece3ca` | 0.770 | 9 | 14 | **3** | 1 |
| `hamlet.html` | `#eceeeb` | 0.850 | 10 | 16 | **2** | 1 |
| `soudain-lete-dernier.html` | `#0a0a09` | 0.003 | 7 | 12 | **2** | 1 |
| `la-nuit-de-san-lorenzo.html` | `#f4ede1` | 0.852 | 9 | 17 | **2** | 0 |
| `rosetta.html` | `#1b1a17` | 0.010 | 8 | 13 | **2** | 0 |
| `pandora.html` | `#f2ead9` | 0.827 | 3 | 12 | **1** | 6 |
| `julie-en-12-chapitres.html` | `#f5f2ec` | 0.890 | 3 | 11 | **1** | 5 |
| `sur-la-route-domaha.html` | `#f1e9d8` | 0.819 | 5 | 17 | **1** | 2 |
| `annie-hall.html` | `#faf8f4` | 0.940 | 6 | 12 | **1** | 1 |
| `hamnet.html` | `#ece0bf` | 0.749 | 10 | 17 | **1** | 1 |
| `index.html` | `#faf8f4` | 0.940 | 6 | 12 | **1** | 1 |
| `le-doulos.html` | `#ece5d5` | 0.787 | 5 | 14 | **1** | 1 |
| `le-golem.html` | `#e9dfc8` | 0.743 | 3 | 11 | **1** | 1 |
| `le-samourai.html` | `#eceee9` | 0.849 | 5 | 11 | **1** | 1 |
| `hitchcock-truffaut.html` | `#f1ece1` | 0.841 | 8 | 13 | **1** | 0 |
| `les-deux-orphelines.html` | `#15110d` | 0.006 | 8 | 12 | **1** | 0 |
| `persona.html` | `#e9e9e6` | 0.813 | 5 | 10 | **1** | 0 |
| `sans-filtre.html` | `#f6f4ee` | 0.905 | 4 | 13 | **0** | 7 |
| `bienvenue-a-suburbicon.html` | `#f4efe3` | 0.865 | 3 | 12 | **0** | 5 |
| `au-fil-de-leau.html` | `#ece7da` | 0.800 | 2 | 9 | **0** | 4 |
| `retour-a-seoul.html` | `#eef0ef` | 0.867 | 3 | 10 | **0** | 3 |
| `le-cheval-de-turin.html` | `#d9d6cf` | 0.673 | 4 | 8 | **0** | 2 |
| `pandora-contrechamp.html` | `#f2ead9` | 0.827 | 4 | 9 | **0** | 2 |
| `waterloo.html` | `#e9dfc6` | 0.742 | 3 | 14 | **0** | 2 |
| `la-chevauchee-fantastique.html` | `#e9dbbd` | 0.717 | 5 | 15 | **0** | 1 |
| `la-mariee-etait-en-noir.html` | `#f1efe9` | 0.863 | 6 | 8 | **0** | 0 |
| `manhattan.html` | `#f2f3f5` | 0.896 | 3 | 12 | **0** | 0 |
| `moi-daniel-blake.html` | `#ebebe8` | 0.829 | 3 | 11 | **0** | 0 |
| `nouvelle-vague.html` | `#f0eee8` | 0.855 | 5 | 10 | **0** | 0 |
| `raging-bull.html` | `#fcfcfc` | 0.973 | 6 | 11 | **0** | 0 |
| `rouges-et-blancs.html` | `#0c0c0b` | 0.004 | 9 | 12 | **0** | 0 |
| `soy-cuba.html` | `#f1e8d4` | 0.812 | 8 | 16 | **0** | 0 |
| `sud.html` | `#efe7d6` | 0.804 | 5 | 15 | **0** | 0 |
| `the-old-oak.html` | `#e6e0d1` | 0.747 | 5 | 12 | **0** | 0 |

## Detail des couples sous le seuil

### annie-hall.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E1** | `footer` | `#7a7a74` | `#f1ede4` | **3.70** | 4.5 (courant) |
| **E2** | `header.hero .eyebrow` | `#7a7a74` | `#ffffff` | **4.32** | 4.5 (courant) |

### au-fil-de-leau.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E2** | `.subtitle` | `#ebe5d8` | `#e2dcc9` | **1.09** | 4.5 (courant) |
| **E2** | `header.river` | `#ece7da` | `#e2dcc9` | **1.11** | 4.5 (courant) |
| **E2** | `.back-link` | `#8fa39b` | `#ece7da` | **2.16** | 4.5 (courant) |
| **E2** | `.back-link:hover` | `#b98d3f` | `#ece7da` | **2.45** | 4.5 (courant) |

### bienvenue-a-suburbicon.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E2** | `.back-link` | `#f8f5ed` | `#ffffff` | **1.09** | 4.5 (courant) |
| **E2** | `.brochure-meta` | `#f7f4eb` | `#ffffff` | **1.10** | 4.5 (courant) |
| **E2** | `.subtitle` | `#f5f1e6` | `#ffffff` | **1.13** | 4.5 (courant) |
| **E2** | `header.brochure` | `#f4efe3` | `#ffffff` | **1.15** | 4.5 (courant) |
| **E2** | `.back-link:hover` | `#e0876b` | `#ffffff` | **2.68** | 4.5 (courant) |

### hamlet.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E1** | `.provenance` | `#c9d0cf` | `#969c9d` | **1.78** | 4.5 (courant) |
| **E1** | `header.dalle` | `#c9d0cf` | `#8e9495` | **1.97** | 4.5 (courant) |
| **E2** | `h3` | `#98602c` | `#eceeeb` | **4.45** | 4.5 (courant) |

### hamnet.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E1** | `.cast-card::before` | `#b08f3f` | `#ece0bf` | **2.33** | 4.5 (courant) |
| **E2** | `.back-link` | `#7a6c48` | `#f4ebd3` | **4.35** | 4.5 (courant) |

### hitchcock-truffaut.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E1** | `section.sources .piste-num` | `#15120f` | `#7a4a24` | **2.52** | 4.5 (courant) |

### index.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E1** | `footer` | `#7a7a74` | `#f1ede4` | **3.70** | 4.5 (courant) |
| **E2** | `header.hero .eyebrow` | `#7a7a74` | `#ffffff` | **4.32** | 4.5 (courant) |

### julie-en-12-chapitres.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E1** | `.bandeau` | `#26344d` | `#c98a77` | **4.39** | 4.5 (courant) |
| **E2** | `h1.title .chapitres` | `#ead8cf` | `#c98a77` | **2.06** | 4.5 (courant) |
| **E2** | `.subtitle` | `#efe3dc` | `#c98a77` | **2.26** | 4.5 (courant) |
| **E2** | `header.couverture` | `#f5f2ec` | `#c98a77` | **2.54** | 4.5 (courant) |
| **E2** | `.back-link:hover` | `#c98a77` | `#ffffff` | **2.84** | 4.5 (courant) |
| **E2** | `.back-link` | `#8d939e` | `#ffffff` | **3.09** | 4.5 (courant) |

### la-chevauchee-fantastique.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E2** | `.meta-line` | `#867a68` | `#241a12` | **4.06** | 4.5 (courant) |

### la-nuit-de-san-lorenzo.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E1** | `.avertissement` | `#f0d9d2` | `#ddc4b7` | **1.23** | 4.5 (courant) |
| **E1** | `.provenance` | `#b9c4d6` | `#9a9fa7` | **1.51** | 4.5 (courant) |

### le-cheval-de-turin.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E2** | `.back-link` | `#8d867b` | `#d9d6cf` | **2.48** | 4.5 (courant) |
| **E2** | `.back-link:hover` | `#9c7b45` | `#d9d6cf` | **2.71** | 4.5 (courant) |

### le-doulos.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E1** | `footer.endnote` | `#79715f` | `#ece5d5` | **3.86** | 4.5 (courant) |
| **E2** | `.back-link` | `#79715f` | `#ece5d5` | **3.86** | 4.5 (courant) |

### le-golem.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E1** | `footer.poussiere` | `#80796c` | `#171310` | **4.28** | 4.5 (courant) |
| **E2** | `.back-link` | `#80796c` | `#171310` | **4.28** | 4.5 (courant) |

### le-samourai.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E1** | `.note` | `#6d7a86` | `#dfe2dc` | **3.36** | 4.5 (courant) |
| **E2** | `.retour` | `#6d7a86` | `#fbfcfa` | **4.27** | 4.5 (courant) |

### les-deux-orphelines.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E1** | `.fiche dt` | `#7c541f` | `#d8c9a4` | **4.07** | 4.5 (courant) |

### pandora-contrechamp.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E2** | `.cartel` | `#8d8677` | `#f2ead9` | **3.02** | 4.5 (courant) |
| **E2** | `a` | `#2f7d80` | `#f2ead9` | **4.02** | 4.5 (courant) |

### pandora.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E1** | `.content-warning` | `#e2d6bd` | `#9b9e9c` | **1.88** | 4.5 (courant) |
| **E2** | `.eyebrow` | `#c9a97a` | `#f2ead9` | **1.86** | 4.5 (courant) |
| **E2** | `.back-link` | `#e2d6bd` | `#9b9e9c` | **1.88** | 4.5 (courant) |
| **E2** | `.cover` | `#f2ead9` | `#9b9e9c` | **2.26** | 4.5 (courant) |
| **E2** | `.back-link:hover` | `#ffffff` | `#9b9e9c` | **2.70** | 4.5 (courant) |
| **E2** | `.cartel` | `#8d8677` | `#f2ead9` | **3.02** | 4.5 (courant) |
| **E2** | `sup.ref a` | `#2f7d80` | `#f2ead9` | **4.02** | 4.5 (courant) |

### persona.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E1** | `.content-warning` | `#d3d3ce` | `#e9e9e6` | **1.23** | 4.5 (courant) |

### retour-a-seoul.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E2** | `.subtitle` | `#f1f2f1` | `#ffffff` | **1.12** | 4.5 (courant) |
| **E2** | `header.nuit` | `#eef0ef` | `#ffffff` | **1.14** | 4.5 (courant) |
| **E2** | `.back-link` | `#8a9199` | `#ffffff` | **3.19** | 4.5 (courant) |

### rosetta.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E1** | `.section-head .tag` | `#d9560f` | `#d8d5c9` | **2.70** | 4.5 (courant) |
| **E1** | `.fiche dt` | `#a3410b` | `#d8d5c9` | **4.30** | 4.5 (courant) |

### sans-filtre.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E2** | `.meta-line` | `#d4c296` | `#b2903f` | **1.72** | 4.5 (courant) |
| **E2** | `.back-link` | `#d7c79f` | `#b2903f` | **1.81** | 4.5 (courant) |
| **E2** | `.title-orig` | `#dbcca8` | `#b2903f` | **1.90** | 4.5 (courant) |
| **E2** | `.trois-services` | `#ded1b1` | `#b2903f` | **1.99** | 4.5 (courant) |
| **E2** | `.subtitle` | `#eee8d9` | `#b2903f` | **2.47** | 4.5 (courant) |
| **E2** | `header.menu` | `#f6f4ee` | `#b2903f` | **2.75** | 4.5 (courant) |
| **E2** | `.back-link:hover` | `#b2903f` | `#ffffff` | **3.02** | 4.5 (courant) |

### shutter-island.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E1** | `.redact` | `#161310` | `#161310` | **1.00** | 4.5 (courant) |
| **E1** | `.folder-tab` | `#ece3ca` | `#a88f61` | **2.42** | 4.5 (courant) |
| **E1** | `footer.endnote` | `#7d7050` | `#ece3ca` | **3.81** | 4.5 (courant) |
| **E2** | `.back-link` | `#7d7050` | `#ece3ca` | **3.81** | 4.5 (courant) |

### soudain-lete-dernier.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E1** | `.edge-code` | `#7a756a` | `#141311` | **4.05** | 4.5 (courant) |
| **E1** | `footer.endnote` | `#7a756a` | `#0a0a09` | **4.32** | 4.5 (courant) |
| **E2** | `.frame-border::before, .frame-border::after` | `#7a756a` | `#0a0a09` | **4.32** | 4.5 (courant) |

### sur-la-route-domaha.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E1** | `footer.endnote` | `#8a7c63` | `#f1e9d8` | **3.38** | 4.5 (courant) |
| **E2** | `.cachet` | `#b8562e` | `#f1e9d8` | **3.94** | 4.5 (courant) |
| **E2** | `.back-link` | `#8a7c63` | `#201d19` | **4.11** | 4.5 (courant) |

### waterloo.html

| Classe | Selecteur | Texte | Fond | Ratio | Seuil |
|---|---|---|---|---|---|
| **E2** | `.back-link:hover` | `#a07d33` | `#2e2517` | **3.93** | 4.5 (courant) |
| **E2** | `.back-link` | `#958b77` | `#2e2517` | **4.48** | 4.5 (courant) |

## Classement des fonds du plus sombre au plus clair

| # | Page | Fond | Luminance relative |
|---|---|---|---|
| 1 | `soudain-lete-dernier.html` | `#0a0a09` | 0.0030 |
| 2 | `rouges-et-blancs.html` | `#0c0c0b` | 0.0037 |
| 3 | `les-deux-orphelines.html` | `#15110d` | 0.0059 |
| 4 | `rosetta.html` | `#1b1a17` | 0.0103 |
| 5 | `le-cheval-de-turin.html` | `#d9d6cf` | 0.6735 |
| 6 | `la-chevauchee-fantastique.html` | `#e9dbbd` | 0.7166 |
| 7 | `waterloo.html` | `#e9dfc6` | 0.7418 |
| 8 | `le-golem.html` | `#e9dfc8` | 0.7427 |
| 9 | `the-old-oak.html` | `#e6e0d1` | 0.7474 |
| 10 | `hamnet.html` | `#ece0bf` | 0.7491 |

