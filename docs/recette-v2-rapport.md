# Rapport de recette mécanisée — site v2 sur `v2-proto`

**Item** : BKL-065-4-recette · **Branche** : `v2-proto` · **Contrat** :
`SPEC-SITE-V2.md` **v1.1** (52 prescriptions, zéro question ouverte)
**Session** : « BKL-065-4-recette » · **Exécutant** : AC-Exec / Code / **Opus 4.8**
(substitution de calibre prononcée par AH en fenêtre le 22/07 — le mandat visait
Sonnet ; le mandat lui-même est inchangé)
**Date** : 22/07/2026, 12h13 → 13h43 (horodatage instrumental `Get-Date`)
**Dépôt à l'entrée** : `v2-proto` @ `72a78e8`, arbre propre, synchronisé

---

## 1. Verdict d'ensemble

**La limite structurante du prototype est levée.** Les 8 lignes que l'annexe D
de 065-3 laissait « non vérifiables » portent toutes un verdict mesuré.
`clientWidth` vaut 320 quand on demande 320 : la géométrie se mesure.

| | Prototype 065-3 | **Recette 065-4** |
|---|---|---|
| Lignes « non vérifiables » | **8** | **0** |
| OK | 25 | 32 |
| OK / lot | 5 | 7 |
| ÉCART | 7 | **8** |
| Hors périmètre | 7 | 5 |

**22 des 52 lignes portent une mesure prise par cette recette** ; les 30 autres
sont des verdicts du prototype repris tels quels, et l'annexe D dit lesquels
(colonne `Src`, valeurs `[R]` / `[P]`).

**Les 8 lignes non vérifiables sont devenues 5 OK et 2 ÉCART** (la huitième,
P-41, était déjà rétablie par l'erratum 1 du prototype et a été reconfirmée).

**Trois écarts nouveaux, tous mesurés :**

| Ligne | Écart | Mesure | Cause |
|---|---|---|---|
| **P-37** | poids de page | 1 937 Ko à la 1ʳᵉ visite (seuil 900), 1 743 Ko ensuite (seuil 400), sur les **2 pages du diptyque** | `pandora.jpg` — 1 660 Ko. C'est **P-36 qui produit P-37** |
| **P-38** | défilement horizontal | `pandora-contrechamp.html`, **+18 px à 320 px** | un nom de fichier insécable en chasse fixe dans `section#sources > div.note > code` |
| **P-40** | focus clavier | **3 champs sur 382 éléments focalisables** | `style.css` (v1) neutralise l'`outline` du `:focus-visible` de `mobilier.css` |

**Aucune correction n'a été faite.** Ni palette, ni page, ni feuille, ni
registre, ni spec. La recette constate.

---

## 2. Méthode et outillage

Maquette servie **en local** (`python -m http.server 8765 --bind 127.0.0.1`)
sur l'arbre de travail de `v2-proto`. Le site public n'a jamais été sollicité.
Chromium 149 piloté par Playwright 1.61.0 (binding Python, sans Node —
conforme au verdict d'évaluation du 20/07).

Huit sondes rejouables, ASCII pur, dans `outils/recette-playwright/` :

| Sonde | Ce qu'elle établit |
|---|---|
| `harnais.py` | socle commun : dépôt, listes de pages, ouverture du navigateur, calcul du fond effectif et des ratios |
| `sonde-reseau.py` | journal réseau des 39 pages, cache froid et chaud (P-24, P-27, P-32) |
| `sonde-poids.py` | P-37 sous protocole isolé (un contexte neuf par mesure) |
| `sonde-geometrie.py` | P-38 à 320/375/768 px sur 39 pages + captures |
| `sonde-clavier.py` | P-40, parcours complet à la tabulation |
| `sonde-fontes.py` | P-29, P-30, composition réelle glyphe par glyphe |
| `sonde-gris.py` | P-22, distinction de volet hors couleur |
| `sonde-liens.py` | liens et ancres internes, relevés dans le DOM rendu |
| `sonde-contraste.py` | P-39, réconciliation + recensement indépendant |
| `sonde-recherche.py` | P-41 reconfirmée au moteur réel |

Trois bilans de lecture seule (`bilan-reseau.py`, `bilan-contraste.py`,
`genere-annexe-d.py`) et un générateur d'annexe A. Aucun n'écrit dans le site :
`harnais.ecrire_json` refuse toute destination hors de `resultats/`, et le
générateur d'annexe A refuse toute destination hors de `docs/`.

---

## 3. Les huit lignes « non vérifiables », une à une

### P-38 — aucun défilement horizontal à 320 px → **ÉCART**

39 pages × 3 largeurs. Élément fautif nommé quand il y en a un.

| Largeur | Pages en débordement | Dont prototype |
|---|---|---|
| 320 px | 4 / 39 | **1** |
| 375 px | 2 / 39 | 0 |
| 768 px | **0 / 39** | 0 |

`pandora-contrechamp.html` déborde de **18 px** à 320 px. L'élément est
`section#sources > div.note > code`, largeur mesurée 292 px : le nom de fichier
`sources_pandora_analyse_haute.txt`, en chasse fixe et sans point de coupure.
Les trois autres (`hamnet` +262 px, `hitchcock-truffaut` +100 px, `persona`
+34 px) sont des pages **non migrées** — périmètre 065-5.

### P-40 — atteignable et visible au clavier → **ÉCART**

Deux exigences mesurées séparément.

| Mesure | Résultat |
|---|---|
| Éléments focalisables sur les 9 pages | 382 |
| **Atteints à la tabulation** | **382 — aucun inatteignable** |
| Portant un indicateur visible | 379 |
| **Sans indicateur** | **3** |

Les trois sont les champs de `demander-une-analyse.html` (`#film-title`,
`#film-director`, `#film-year`). Au focus clavier, `outline-style` vaut `none`.

**Cause identifiée, pas supposée** : `assets/style.css` ligne 368 déclare
`form.request-form input:focus { outline: none; border-color: var(--accent); }`.
Ce sélecteur est plus spécifique que le `input:focus-visible` de
`mobilier.css`, et la feuille est chargée **après** lui. Le repli est un
changement de **couleur de bordure seule** (`#d8d3c6` → `#7a3b2e`) — soit
précisément ce que la doctrine d'accessibilité du site interdit ailleurs
(P-22 : la distinction ne repose jamais sur la seule couleur).

*C'est le même mécanisme que l'écart de structure §2.1 déjà signalé par le
prototype : la feuille v1 survit sous la feuille v2 et gagne par la cascade.*

### P-37 — poids de page → **ÉCART**

Protocole **isolé**, un contexte neuf par mesure : 1ʳᵉ visite = cache vide ;
visite suivante = l'accueil déjà chargé, puis la page cible.

| Page | 1ʳᵉ visite | Suivante | Verdict |
|---|---|---|---|
| les 6 pages du menu | 176 → 268 Ko | 0 → 10 Ko | OK |
| `films/rouges-et-blancs.html` | 392 Ko | 198 Ko | OK |
| **`films/pandora.html`** | **1 937 Ko** | **1 743 Ko** | 1ʳᵉ > 900, suiv. > 400 |
| **`films/pandora-contrechamp.html`** | **1 936 Ko** | **1 743 Ko** | idem |

Cause unique : `pandora.jpg`, **1 660 Ko**. Le témoin est net —
`rouges-et-blancs`, dont l'affiche pèse 36 Ko, tient largement les deux seuils.
**P-37 n'appelle aucune décision propre : elle tombera avec P-36.**

> ⚠️ **Un premier chiffrage était faux et a été refait.** Dans la sonde réseau,
> la « visite suivante » est mesurée en parcourant les pages en séquence : le
> résultat dépend alors de l'ordre. Le diptyque partageant une affiche,
> `pandora-contrechamp` payait les 1 660 Ko et `pandora`, visitée ensuite,
> n'affichait que 36 Ko — **aucun des deux chiffres ne décrivait la page**.
> D'où `sonde-poids.py` et son protocole isolé. Les chiffres ci-dessus sont
> ceux-là.

### P-32 — aucun URL ne casse → **OK** (avec limite déclarée)

| Mesure | Résultat |
|---|---|
| Documents servis | **39 / 39 en 200** |
| Liens relevés dans le DOM rendu | 2 086 |
| Cibles internes distinctes demandées | 625 |
| **Liens morts** | **0** |
| **Ancres mortes** (`#fragment` introuvable) | **0** |
| Liens sortants | 335, **listés et non demandés** |

Les liens sortants (bibliographies) sont inventoriés mais **jamais sollicités** :
une recette ne sort pas sur le réseau public.

**Limite déclarée** : le site *publié* porte encore la v1. Ce contrôle vaut pour
la maquette locale de `v2-proto`. Le contrôle des URLs publics appartient à la
bascule 065-5, sur la checklist de l'annexe A régénérée.

### P-24 — zéro requête tierce → **OK / lot**, confirmé au journal réseau

| Périmètre | Requêtes tierces |
|---|---|
| **Les 9 pages du prototype** | **0** |
| Les 30 pages non migrées *(informatif)* | 170, sur 29 pages (Google Fonts) |

Le contrôle greppable du prototype est confirmé par la mesure : rien ne sort.

### P-27 — `unicode-range` restreint → **OK**, avec un signalement qui le dépasse

Aucune fonte non latine n'est téléchargée sur les 9 pages du prototype : le
critère est satisfait.

**Mais la contre-épreuve a mis au jour autre chose.** En nommant explicitement
la famille, un caractère hébreu compose bien en **Frank Ruhl Libre**, et le
fichier `frankruhllibre-hebrew-400-normal.woff2` **se télécharge**. La fonte est
donc saine. Or **aucune pile `font-family` du site ne nomme cette famille** :
`--serif` vaut `'Literata', Georgia, 'Times New Roman', serif`.

**Conséquence mesurée** : l'hébreu de `le-golem.html` compose aujourd'hui en
**Times New Roman**, et continuera de le faire après le rétrofit si rien n'est
chaîné. Les 2 fichiers Frank Ruhl Libre du dépôt ne sont atteignables par
aucune page. *Le fichier est bon, le chaînage manque.* — à traiter en 065-5.

*Le cyrillique, lui, fonctionne : il est déclaré sous le nom `Literata`, que les
piles nomment déjà.*

### P-29 et P-30 — replis de glyphes → **OK** tous les deux

Le prototype les avait classées non vérifiables parce que `controle-glyphes.py`
vit hors du dépôt. **Chromium offre mieux que cet outil** : il dit quelle
famille a *réellement* composé chaque glyphe
(CDP `CSS.getPlatformFontsForNode`). On ne raisonne plus sur le répertoire
supposé d'un fichier de fonte — on lit le résultat de la composition.

Méthode : les 75 caractères non-ASCII réellement affichés par le corpus sont
composés un à un dans le contexte typographique v2, et la famille de chacun est
lue.

| Périmètre | Replis mesurés | Non déclarés |
|---|---|---|
| **Les 9 pages du prototype** | 1 (`U+2192`) | **0** |
| Les 30 pages non migrées *(informatif)* | 9 | **4** |

**P-30 (« zéro repli NON DÉCLARÉ ») est satisfaite** sur le périmètre du
prototype, et **P-29 (liste exhaustive) aussi** : le seul repli mesuré, `U+2192`,
figure bien dans la liste de la spec.

**Signalement pour 065-5** — sur les pages non migrées, quatre replis ne sont
pas dans la liste P-29 : `U+2190` (← , **30 pages**), `U+25C6` (`le-samourai`),
et trois lettres hébraïques (`le-golem`). `U+2190` disparaîtra avec le chevron
CSS (P-28) ; les autres devront rejoindre la liste ou la palette.

### P-22 — la distinction ne repose jamais sur la seule couleur → **OK**

Deux preuves plutôt qu'une.

| Volet | `--volet` | Filet mesuré | Régime en toutes lettres |
|---|---|---|---|
| Critique | `1px solid currentColor` | `solid 1px` | « R1 — Critique publiée avant le site v2 » |
| Étude | `3px double currentColor` | `double 3px` | « R3 — Étude » |

La différence est de **forme** (style *et* épaisseur), donc elle survit à la
perte de la couleur — et les captures en niveaux de gris
(`gris-cartouche-critique.png`, `gris-cartouche-etude.png`) le montrent à l'œil.

### P-41 — recherche < 100 ms → **OK**, reconfirmée

Une ligne déjà verdictée ne se reprend pas sur parole.

| Jeu | Entrées | Pire cycle | Part du seuil |
|---|---|---|---|
| Corpus réel | 33 | **1,4 ms** | 1,4 % |
| Jeu synthétique | **500** | **9,3 ms** | **9,3 %** |

Cycle mesuré : frappe → filtrage → rendu, l'événement `input` étant distribué de
façon synchrone (l'écouteur s'exécute entièrement pendant `dispatchEvent`).

> ⚠️ **Une première mesure était sans objet.** `films-data.js` déclare
> `const FILMS` : la liaison existe dans la portée globale mais **n'est pas une
> propriété de `window`**. Ma sonde lisait `window.FILMS`, donc zéro entrée, et
> **le jeu de 500 n'a jamais été monté** — le tableau affichait « 500 » en
> annonçant 32 résultats. Corrigé : identifiant nu, corpus passé en argument,
> écouteurs du premier montage retirés pour ne pas mesurer deux montages.
> *Une lecture non consciente à 0,9 ms aurait été un faux succès.*

---

## 4. Contraste AA (P-39) — le tableau définitif

Livrable séparé : **`docs/recette-v2-tableau-AA.md`**.

### Les 71 écarts déclarés, confrontés au rendu réel

| Classe | Déclarés | **CONFIRMÉS** | ÉCARTÉS |
|---|---|---|---|
| E1 (certains) | 23 | **17** | 6 |
| E2 (probables) | 48 | **31** | 17 |
| **Total** | **71** | **48** | **23** |

Motifs des mises à l'écart : la règle CSS existe mais **ne s'applique à aucun
élément rendu** (11), les éléments visés **ne portent aucun texte** (11), ou le
couple réel diffère du couple supposé et **passe** (1).

### Recensement indépendant des 34 pages

| Mesure | Valeur |
|---|---|
| Couples sous le seuil, au rendu réel | **221** |
| Pages concernées | 33 / 34 |
| dont pages **migrées v2** | 43 |
| dont pages **non migrées** | 178 |

| Nature | Nombre |
|---|---|
| Texte courant (seuil 4,5:1) | 176 |
| Fond en dégradé : échoue sur une **partie** du fond | 36 |
| Opacité < 1 | 6 |
| Grand texte (seuil 3:1) | 2 |
| Identité de couleur (ratio 1,00) | 1 |

Le comptage statique annonçait 71 **en se déclarant borne basse** ; le rendu
réel en mesure 221. L'écart ne traduit pas une aggravation du site mais ce que
le premier outil ne pouvait pas voir : l'appariement d'un texte avec son fond
réel.

> ⚠️ **Deux défauts de ma propre sonde, trouvés et corrigés avant de compter.**
> ① Les couvertures du corpus emploient des **dégradés**, portés par
> `background-image` : en ne remontant que les `background-color`, la sonde
> traversait la couverture et retenait le fond du corps de page — d'où **35
> ratios de 1,00 sur du texte parfaitement lisible**. Corrigé : une couche à
> `background-image` couvre ce qui est dessous, et le verdict porte sur le pire
> de ses arrêts de couleur. ② L'**opacité effective** (produit de celles des
> ancêtres) n'était pas prise en compte.
> *Contrôle de périmètre : aucune page du corpus n'emploie d'image bitmap en
> fond — tout fond est une couleur ou un dégradé, donc entièrement décidable
> aux styles calculés. **Aucune ligne du tableau n'est laissée indéterminée.***

**Compté, jamais corrigé** : les 221 lignes sont des arbitrages qui attendent AH
en 065-5.

---

## 5. Liens, mobile, annexe A

**Liens** — 2 086 liens relevés dans le DOM rendu des 39 pages, 625 cibles
internes distinctes : **0 lien mort, 0 ancre morte**.

**Mobile** — captures dans `docs/recette-v2-captures/` : accueil, une Critique
(`pandora`) et une Étude (`pandora-contrechamp`), à 320, 375 et 768 px, plus les
4 captures en niveaux de gris de P-22. **13 fichiers, 2,1 Mo.**

> **Choix déclaré sur le poids des captures.** En PNG pleine page, une analyse
> illustrée pèse ~2 Mo : les 9 captures faisaient **5,5 Mo pour un dépôt de
> 10 Mo**. D'où deux décisions, dites plutôt que subies : JPEG q=50, et
> **pleine page à 320 px seulement** — la largeur où vit le critère de P-38 ; à
> 375 et 768 px, le premier écran suffit, le défilement horizontal étant de
> toute façon mesuré sur *toute* la page, pour les 39 pages, par la sonde.
> Si même 2,1 Mo est jugé excessif dans le dépôt, les captures peuvent vivre
> hors dépôt — **c'est un arbitrage d'AH, pas une décision de recette.**

**Annexe A** — régénérée dans `docs/recette-v2-annexe-A-regeneree.md` :
**34 URLs** (33 analyses + l'accueil), dont 1 Étude et 32 Critiques.
L'arbitrage **E-1 est confirmé sur mesure** : la spec en liste 33.
**`SPEC-SITE-V2.md` n'a pas été ouverte en écriture** — le script d'origine y
écrivait, c'est la *destination* qui a été adaptée. L'intégration reste la main
du greffe.

---

## 6. Ce que cette recette n'a pas fait

- **Aucune correction.** Aucun fichier du site modifié : ni palette, ni page, ni
  feuille, ni registre, ni spec, ni skill, ni routine.
- **Aucune installation.** Playwright et Chromium étaient en place (gate R4 du
  22/07 12h06). Rien d'autre n'a été ajouté.
- **Aucun accès au site public.** La maquette locale, et rien d'autre. Les 335
  liens sortants ont été listés sans être suivis.
- **`main` et `staging` n'ont pas été touchées** — empreintes contrôlées à
  l'entrée et à la sortie.
- **Les 30 pages non migrées n'ont pas été verdictées** : elles sont mesurées et
  rapportées en *informatif*, leur mise en conformité étant le rétrofit 065-5.
- **Le rendu n'a pas été jugé.** La recette mesure des seuils ; l'appréciation
  visuelle reste à AH.

---

## 7. Escalades — ce qui appelle une décision d'AH

| # | Objet | Ce qui est demandé |
|---|---|---|
| **E-a** | **P-40** — la règle v1 `form.request-form input:focus { outline: none }` neutralise le focus visible du système v2 | trancher : la règle v1 tombe-t-elle au rétrofit ? Le repli couleur-seule est-il accepté en attendant ? |
| **E-b** | **P-27 / P-25** — `Frank Ruhl Libre` n'est nommée par aucune pile `font-family` | trancher en 065-5 : chaîner la famille (l'hébreu de `le-golem` compose sinon en Times New Roman), ou assumer le repli et l'inscrire à la liste P-29 |
| **E-c** | **P-39** — 221 couples sous le seuil | le tableau définitif est fourni ; les arbitrages restent entiers |
| **E-d** | **Poids des captures** (2,1 Mo dans le dépôt) | les garder dans `docs/`, ou les sortir du dépôt |
| **E-e** | **P-13** — la spec est amendée en v1.1 (seuil de couverture ≥ 50 %), le prototype implémente encore l'ancienne règle | rien à décider ici ; à inscrire au périmètre de 065-5 |

### Ambiguïtés du mandat, signalées et non réinterprétées

| Point | Lecture retenue |
|---|---|
| §4.4 « les 9 pages du prototype **+** les 3 migrées » — les 3 migrées sont déjà dans les 9 (6 menu + 3) | verdict rendu sur **9 pages** ; les 30 non migrées mesurées et rapportées en informatif, ce qui couvre les deux lectures |
| §4.2 P-32 « aucun URL publié ne casse » — rien n'est publié depuis `v2-proto` | verdict sur la **maquette locale**, limite déclarée, contrôle public renvoyé à la bascule |
| §4.2 P-29/P-30 — l'outil vit hors dépôt | l'outil n'a **pas** été copié dans le dépôt (geste non autorisé) ; il n'a pas été utilisé non plus, Chromium fournissant une mesure plus directe |

---

## 8. Contrôles de sortie

| Contrôle | Résultat |
|---|---|
| `git rev-list v2-proto..main` | 0 — aucun commit du prototype n'a atteint `main` |
| `origin/main` | inchangée du premier au dernier geste |
| `origin/staging` | inchangée |
| `SPEC-SITE-V2.md` | non modifiée (`git status` vide) |
| Serveur local | tué en fin de session |
| Fichiers temporaires | les résultats bruts vivent dans `outils/recette-playwright/resultats/` |

---

*Rapport établi le 22/07/2026. La recette constate ; le verdict de recette est
un gate d'AH ; les corrections sont BKL-065-5.*
