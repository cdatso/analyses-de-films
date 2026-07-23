# Les arbitrages de contraste AA, en 5 lots — PROPOSITION SOUMISE À AH

**ARRÊT n°2 du mandat BKL-065-5** (Temps 2). Session « Opus BKL-065-5
Migration », **23/07/2026** — mesures prises à 07h57, document rédigé à 08h12
(horodatage instrumental).

> ⚠️ **Rien n'est corrigé.** Chaque lot attend un gate « **go lot n** ».
> Amendements libres, y compris « on ne touche pas à celui-là ».

---

## 1. Pourquoi les chiffres ont bougé depuis la recette

Le tableau AA de la recette annonçait **221 couples**. Il a été mesuré le 22/07
sur un site dont **30 pages n'étaient pas encore rétrofitées**. Depuis :
substitution typographique, menu, cartouche, calage du mobilier. Arbitrer sur
cette photo serait arbitrer à côté.

**Re-mesure au rendu réel, ce matin, sur les 39 pages** (Playwright,
viewport 1280, fond effectif calculé en remontant les ancêtres) :

| | Recette 22/07 | **Ce matin** |
|---|---|---|
| Éléments en échec | 221 | **242** |
| Périmètre | 34 pages | **39 pages** (les 5 pages du menu v2 comprises) |

*L'écart n'est pas une aggravation : le rétrofit a ajouté un menu et un
cartouche sur 30 pages, et la mesure couvre désormais les 5 pages du menu qui
n'existaient pas au périmètre publié.*

## 2. Comment 242 échecs deviennent 5 décisions

Trois regroupements successifs, chacun mesuré :

| Étape | Ce qu'on regarde | Reste |
|---|---|---|
| départ | un élément de page | 242 |
| ① | le **couple de couleurs** (le même revient sur des dizaines d'éléments) | 116 |
| ② | la **variable de palette** qui produit la couleur (une variable nourrit plusieurs couples) | 64 + 21 hors palette |
| ③ | le **lot d'arbitrage** (même nature, même geste, même risque) | **5** |

### Le contrôle qui commande tout le reste

Corriger une variable de palette n'est sans risque **que si elle ne sert qu'à
colorer du texte**. Vérification faite sur les 64 variables :

- **18 sont sûres** — elles n'apparaissent qu'en `color:` ;
- **46 sont mixtes** — elles servent aussi de fond, de filet, de dégradé.
  *Assombrir `--platre` de 60 % pour rattraper un cartel, ce serait repeindre
  la couverture du film.*

**Pour les mixtes, je ne propose pas de toucher à la variable** mais d'ajouter
une **variable-sœur de texte** (`--gris` reste pour les fonds et les filets ;
`--gris-texte` porte la valeur corrigée, et seules les déclarations `color:`
basculent). Mécanique, révocable, zéro effet sur les fonds.

### Le principe de correction, dans tous les lots

Teinte et saturation **figées** ; seule la clarté se déplace, dans le sens
imposé par le fond, **jusqu'au premier point où le seuil est atteint** — jamais
au-delà. L'identité bespoke est une exigence de la spec (acquis A-1), pas une
variable d'ajustement.

---

## LOT 1 — le chrome partagé : **une variable, 54 éléments, 7 pages**

**Le lot le plus rentable du chantier : 22 % des échecs en une décision.**

| | |
|---|---|
| Fichier | `assets/style.css` |
| Variables | `--ink-muted` **et** `--mobilier-attenue` (même valeur `#7a7a74`) |
| Usage | **21 + 5 déclarations, toutes en `color:`** → lot **SÛR** |
| Pages touchées | `index`, `critiques`, `etudes`, `qui-sommes-nous`, `comment-ca-marche`, `demander-une-analyse`, `annie-hall` |
| Éléments | **54** |

| Fond | Ratio actuel | Avec `#6c6c67` |
|---|---|---|
| `#faf8f4` (papier) | 3,70 → *échec* | **4,98** ✓ |
| `#f1ede4` (papier alt.) | 4,07 → *échec* | **4,52** ✓ |

**Proposition : `#7a7a74` → `#6c6c67`** (déplacement de clarté 0,054 — un gris
très légèrement plus dense, sur des mentions secondaires : sommaire, légendes,
pied de page, méta). C'est le premier gris qui tient **les deux** fonds.

> `annie-hall` est dans ce lot parce qu'elle n'a pas de feuille bespoke : elle
> lit le chrome du site. Cohérent avec son traitement en « cas à part » au
> Temps 1.

---

## LOT 2 — variables sûres, ajustement fin : **12 lots, 41 éléments**

Variables servant **uniquement** au texte, déplacement de clarté **≤ 0,15**
(imperceptible hors comparaison côte à côte). Correction directe de la valeur.

| Page | Variable | Actuel | Proposé | Élém. | Ratio |
|---|---|---|---|---|---|
| `le-samourai` | `--acier` | `#6d7a86` | `#566069` | 8 | 3,09 |
| `hamnet` | `--ink-faint` | `#7a6c48` | `#685c3d` | 6 | 3,54 |
| `pandora-contrechamp` | `--encre-douce` | `#3f4550` | `#2f333b` | 4 | 3,44 |
| `hitchcock-truffaut` | `--gris` | `#8b8073` | `#736a5f` | 3 | 3,28 |
| `manhattan` | `--gris` | `#7c828c` | `#6a7079` | 3 | 3,48 |
| `hamlet` | `--mer` | `#8a9a9d` | `#b0bbbd` | 3 | 3,05 |
| `persona` | `--grey` | `#8c8c86` | `#676762` | 3 | 2,68 |
| `raging-bull` | `--halftone` | `#7b756a` | `#615c53` | 3 | 3,10 |
| `waterloo` | `--laiton` | `#a07d33` | `#695221` | 3 | 2,33 |
| `les-deux-orphelines` | `--sepia-deep` | `#7c541f` | `#734e1d` | 2 | 4,07 |
| `la-chevauchee-fantastique` | `--ciel` | `#4a6d8c` | `#3e5b75` | 2 | 3,47 |
| `nouvelle-vague` | `--gris-labo` | `#8e8b82` | `#6f6c64` | 1 | 2,94 |

*`hamlet --mer` s'**éclaircit** au lieu de s'assombrir : le texte est sur fond
sombre. Le sens est déterminé par le fond, pas par une règle uniforme.*

---

## LOT 3 — variables mixtes, ajustement fin : **23 lots, 71 éléments**

Même ampleur de déplacement, mais **la variable sert aussi ailleurs** →
variable-sœur `--<nom>-texte`, les fonds et filets restent **intacts**.

Les dix plus fournis (les 13 autres portent 1 à 2 éléments) :

| Page | Variable | Actuel | Proposé | Élém. | Sert aussi à |
|---|---|---|---|---|---|
| `soudain-lete-dernier` | `--safelight` | `#b23a2e` | `#d25c50` | 8 | fond, filet |
| `soudain-lete-dernier` | `--silver` | `#7a756a` | `#69655b` | 7 | filet |
| `le-doulos` | `--ink-faint` | `#79715f` | `#645e4f` | 7 | filets |
| `shutter-island` | `--ink-faint` | `#7d7050` | `#665b41` | 7 | ombre, filets |
| `sans-filtre` | `--or` | `#b2903f` | `#866d30` | 5 | fond, filet |
| `sur-la-route-domaha` | `--ink-faint` | `#8a7c63` | `#695e4b` | 5 | filets |
| `rosetta` | `--vest` | `#d9560f` | `#9e3f0b` | 4 | contour, filet |
| `la-nuit-de-san-lorenzo` | `--ble` | `#c08a2c` | `#825d1e` | 4 | fond, dégradé |
| `raging-bull` | `--belt` | `#a8842c` | `#71591e` | 3 | filets |
| `soy-cuba` | `--red` | `#c3281c` | `#e34539` | 3 | fond, dégradé |

---

## LOT 4 — les déplacements lourds : **29 lots, 68 éléments** ⚠️

**Ceux-là, je ne les propose pas en bloc.** Déplacement de clarté **> 0,15** :
ce n'est plus un ajustement, c'est **un changement de couleur visible**. Les
appliquer mécaniquement abîmerait des identités que la spec protège.

Les cas les plus parlants :

| Page | Variable | Ce que la correction mécanique donnerait | Pourquoi c'est un problème |
|---|---|---|---|
| `bienvenue-a-suburbicon` | `--creme` | `#f4efe3` → `#201a0d` | **la crème deviendrait presque noire** — la variable est le fond de trois blocs |
| `pandora` | `--platre` | `#f2ead9` → `#51401c` | idem : le plâtre **est** le fond de la page |
| `shutter-island` | `--paper` | `#a88f61` → déplacement 0,72 | même famille : couleur de papier employée en texte |
| `hitchcock-truffaut` | `--noir` | `#000000` → `#ffffff` | inversion pure et simple |
| `julie-en-12-chapitres` | `--gris-fjord` | → `#f4f4f5` | le gris deviendrait blanc |

**Ma lecture** : dans presque tous ces cas, le vrai problème n'est pas la
couleur du texte mais **le couple** — un texte clair posé sur un fond clair
(souvent dans un dégradé). Trois voies, à trancher lot par lot :

1. **corriger localement** l'élément fautif (une règle dédiée, sans toucher à
   la variable) ;
2. **documenter l'exception** au titre de P-30/P-39, avec son motif ;
3. **retoucher le fond** à cet endroit — le plus invasif, réservé aux cas où le
   texte est réellement illisible.

**Je propose de traiter ce lot en dernier, cas par cas, après les lots 1-3** —
et volontiers avec ton œil sur les pages concernées, puisqu'il s'agit de design
et non de conformité.

---

## LOT 5 — hors palette : **7 couples, 8 éléments**

Couleurs écrites **en dur** dans une règle, sans passer par une variable.
Petit lot, traitement à l'unité, sans effet de bord possible.

| Page | Couple | Ratio | Proposé | Nature |
|---|---|---|---|---|
| `shutter-island` | `#aa4c41` / `#ece3ca` | 4,30 | `#a54a3f` | opacité |
| `au-fil-de-leau` | `#c39f5e` / `#415343` | 3,32 | `#d5bc8f` | dégradé partiel |
| `le-doulos` | `#576b77` / `#ece5d5` | 4,43 | `#566a76` | opacité |
| `le-golem` | `#80796c` / `#171310` | 4,28 | `#847d6f` | texte courant |
| `rosetta` | `#d96d30` / `#d8d5c9` | 2,31 | `#94471b` | opacité |
| `sur-la-route-domaha` | `#be653f` / `#f1e9d8` | 3,39 | `#a05535` | opacité |
| `waterloo` | `#958b77` / `#3f321b` | 3,71 | `#a39b89` | dégradé |

*Quatre des sept viennent d'une **opacité < 1** : la couleur pleine passerait,
c'est la transparence qui fait échouer. L'arbitrage porte donc sur l'opacité
autant que sur la teinte — remonter l'opacité serait l'autre solution.*

---

## 3. Récapitulatif, et ce que je recommande

| Lot | Objet | Lots | Élém. | Risque | Recommandation |
|---|---|---|---|---|---|
| **1** | chrome partagé `style.css` | 1 | **54** | nul (variable de texte pure) | **go franc** |
| **2** | variables sûres, fines | 12 | 41 | nul | **go franc** |
| **3** | variables mixtes, fines | 23 | 71 | faible (variable-sœur) | **go** |
| **4** | déplacements lourds | 29 | 68 | **élevé** | cas par cas, après 1-3 |
| **5** | hors palette | 7 | 8 | nul | **go** |
| | | | **242** | | |

**Les lots 1, 2, 3 et 5 traitent 174 des 242 échecs (72 %) sans toucher à un
seul fond ni à une seule ossature.** Ils sont mécaniques, mesurables et
révocables commit par commit.

**Le lot 4 est le seul qui engage le dessin.** C'est aussi celui où
« documenter l'exception » est une réponse légitime : P-30 pose déjà le
principe « zéro repli **non déclaré** » plutôt que « zéro repli », et P-39
prévoit explicitement qu'un écart puisse être **arbitré** plutôt que corrigé.

## 4. Après application

Re-mesure au moteur, et le comptage post-correctif doit tomber à **zéro écart
non documenté** (P-39). Les écarts que tu choisiras de documenter iront au
rapport de migration avec leur motif — jamais laissés silencieux.
