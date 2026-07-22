# Inventaire d'entrée de la migration v2 — LISTE GELÉE

**Item** : BKL-065-5 · **Temps 0, point 2 du mandat** du 22/07/2026.
**Mesuré le 22/07/2026 à 19h57:23** (horodatage instrumental `Get-Date`), branche `v2-proto`
à `2427c49`, `main` à `0b0f476`. **Toutes les valeurs sont mesurées, aucune
recopiée.**

> **Ce que « gelée » veut dire** : cette liste est le périmètre de la passe de
> rétrofit. Toute page qui y entrerait après ce point ferait l'objet d'un
> signalement à AH, jamais d'un ajout silencieux. *(Le corpus est passé de 29 à
> 33 pages pendant les travaux — c'est précisément ce que P-47 anticipe.)*

---

## 1. Le périmètre en trois nombres

| | Nombre | Source |
|---|---|---|
| URLs **publiés** (checklist de P-32) | **34** | annexe A régénérée du 22/07 (33 analyses + accueil) |
| Pages déjà migrées en v2 (prototype 065-3) | **3** | `pandora`, `pandora-contrechamp`, `rouges-et-blancs` |
| **Pages à rétrofiter** | **30** | 33 − 3 |
| Pages du menu v2, non encore publiées | 5 | `critiques`, `etudes`, `qui-sommes-nous`, `comment-ca-marche`, `demander-une-analyse` — elles rejoignent la liste **à la bascule** |

*Après bascule, le site exposera **39 URLs** : 34 publiés + les 5 pages du menu v2.*

## 2. Les 30 pages à rétrofiter — état d'entrée mesuré

`GF` = la page charge aujourd'hui des fontes Google (P-24 en défaut) ·
`ff` = nombre de déclarations `font-family` dans la page.

| # | Page | HTML | GF | ff |
|---|---|---|---|---|
| 1 | `annie-hall.html` | 12,2 Ko | — | 0 |
| 2 | `au-fil-de-leau.html` | 25,0 Ko | GF | 13 |
| 3 | `bienvenue-a-suburbicon.html` | 22,7 Ko | GF | 13 |
| 4 | `hamlet.html` | 46,7 Ko | GF | 16 |
| 5 | `hamnet.html` | 36,9 Ko | GF | 26 |
| 6 | `hitchcock-truffaut.html` | 39,3 Ko | GF | 16 |
| 7 | `julie-en-12-chapitres.html` | 23,4 Ko | GF | 15 |
| 8 | `la-chevauchee-fantastique.html` | 25,5 Ko | GF | 15 |
| 9 | `la-mariee-etait-en-noir.html` | 21,8 Ko | GF | 13 |
| 10 | `la-nuit-de-san-lorenzo.html` | 41,5 Ko | GF | 15 |
| 11 | `le-cheval-de-turin.html` | 22,7 Ko | GF | 11 |
| 12 | `le-doulos.html` | 30,0 Ko | GF | 28 |
| 13 | `le-golem.html` | 22,9 Ko | GF | 12 |
| 14 | `le-samourai.html` | 41,4 Ko | GF | 18 |
| 15 | `les-deux-orphelines.html` | 35,3 Ko | GF | 19 |
| 16 | `manhattan.html` | 24,5 Ko | GF | 11 |
| 17 | `moi-daniel-blake.html` | 23,3 Ko | GF | 15 |
| 18 | `nouvelle-vague.html` | 22,7 Ko | GF | 13 |
| 19 | `persona.html` | 31,7 Ko | GF | 17 |
| 20 | `raging-bull.html` | 24,5 Ko | GF | 12 |
| 21 | `retour-a-seoul.html` | 22,4 Ko | GF | 15 |
| 22 | `rosetta.html` | 32,2 Ko | GF | 20 |
| 23 | `sans-filtre.html` | 23,7 Ko | GF | 13 |
| 24 | `shutter-island.html` | 43,7 Ko | GF | 29 |
| 25 | `soudain-lete-dernier.html` | 41,6 Ko | GF | 27 |
| 26 | `soy-cuba.html` | 38,5 Ko | GF | 29 |
| 27 | `sud.html` | 34,4 Ko | GF | 28 |
| 28 | `sur-la-route-domaha.html` | 31,9 Ko | GF | 28 |
| 29 | `the-old-oak.html` | 35,4 Ko | GF | 20 |
| 30 | `waterloo.html` | 22,9 Ko | GF | 13 |

**29 des 30 pages chargent des fontes tierces** ; `annie-hall.html` est la seule
autonome (acquis constaté dès le §1 de la spec). **Aucune page n'atteint le seuil
de P-35** (60 Ko) : maximum `hamlet.html` à 46,7 Ko — la marge absorbe le menu et
le cartouche ajoutés par le gabarit v2.

## 3. État d'entrée du registre `films-data.js`

33 entrées. Le rétrofit du registre (nature 3) part de là :

| Champ (annexe B) | Renseigné | Reste à faire |
|---|---|---|
| `slug`, `title`, `director`, `year`, `url`, `summary` | 33 / 33 | — |
| `datePublication` | **3 / 33** | 30, dérivées de `git log --diff-filter=A` |
| `volet` | **3 / 33** | 30 (É-2 de la v1.1) |
| `genreBase` | **3 / 33** | 30, dérivées mécaniquement de `genre` |
| `technique` | **3 / 33** | 30, dérivées mécaniquement de `genre` |
| `pays` | **3 / 33** | 30 — **travail de modèle SOUS RELECTURE AH (arrêt n°1)** |
| `producteur` | **7 / 33** | 26 (P-18 : jamais vide, jamais deviné) |
| `genre` (déprécié, P-50) | 33 / 33 | à retirer en fin de passe, après dérivation |

## 4. Affiches — état d'entrée (P-36)

32 affiches, **7,82 Mo** au total (le vrai poste de poids du site).
**5 dépassent le seuil de 300 Ko** :

| Affiche | Poids | Conséquence mesurée |
|---|---|---|
| `pandora.jpg` | **1 660,1 Ko** | cause unique du dépassement P-37 sur les 2 pages du diptyque (1 937 Ko à la 1ʳᵉ visite) |
| `hitchcock-truffaut.jpg` | 475,9 Ko | |
| `moi-daniel-blake.jpg` | 326,3 Ko | |
| `raging-bull.jpg` | 318,4 Ko | |
| `le-samourai.jpg` | 317,6 Ko | |

*La spec (§9.3.1) en annonçait 4 sur la mesure du 21/07 ; il y en a **5** au
22/07 — `hitchcock-truffaut` a été publiée entre-temps. Mesure, pas recopie.*

## 5. Les 8 ÉCARTS hérités de la recette, et leur nature de rattachement

| Écart | Objet | Traité en nature |
|---|---|---|
| P-13 | seuil de couverture ≥ 50 % pas encore implémenté dans `corpus.js` | 4 — normalisations |
| P-18 | `producteur` sur 7 entrées / 33 | 2 — signatures & provenance |
| P-36 | 5 affiches > 300 Ko | 5 — affiches |
| P-37 | 2 pages > 900 Ko (conséquence directe de P-36) | 5 — affiches |
| P-38 | `pandora-contrechamp` +18 px à 320 px (+ 3 pages non migrées) | 4 — normalisations |
| P-39 | 221 couples de contraste sous le seuil | **Temps 2, par lots gatés** |
| P-40 | focus clavier neutralisé sur 3 champs (`style.css` l. 368) | 4 — normalisations |
| P-50 | `corpus.js` lit encore `genre` en repli | 3 — registre |

## 6. Ce que cet inventaire NE couvre pas, et pourquoi

- le **contenu éditorial** des 30 analyses : INTOUCHÉ (cadrage ②) ;
- le **skill** et la **routine** : hors mandat (paquet de reprise, gate 08h11) ;
- `films-a-traiter.md`, les specs, `PLANNING.csv` : jamais.
