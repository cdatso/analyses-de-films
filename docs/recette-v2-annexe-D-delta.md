# Annexe D — DELTA de la migration

**Item** : BKL-065-5, Temps 4. Établi le **23/07/2026 à 11h55** (horodatage
instrumental), branche `v2-proto` à `13dab97`.

> **Ce que ce document est.** La recette du 22/07 a rendu **8 ÉCARTS**. Le
> mandat les a fait voyager en 065-5. Ce delta dit, ligne à ligne, **ce qu'ils
> sont devenus** — mesuré, jamais supposé.
>
> **Ce qu'il n'est pas.** Il ne remplace pas l'annexe D : celle-ci se
> régénère depuis le rapport de recette et garde donc les verdicts du 22/07.
> Les deux se lisent ensemble — l'une dit d'où l'on part, l'autre où l'on en
> est.

---

## 1. Les 8 écarts de la recette, aujourd'hui

| Écart | Constat du 22/07 | État au 23/07 | Verdict |
|---|---|---|---|
| **P-13** | seuil de couverture absent : `Pays` s'affichait à 3 entrées / 33 et masquait 30 analyses | seuil ≥ 50 % implémenté dans `corpus.js` ; vérifié en contexte neuf — `pays` et `technique` masquées à 9 %, réaffichées à 100 % après taxonomie | **SOLDÉ** |
| **P-18** | `producteur` sur **7 entrées / 33** | **33 / 33** — valeur journalisée ou mention explicite `non spécifié` | **SOLDÉ** |
| **P-36** | **5 affiches** > 300 Ko, max `pandora.jpg` à 1 660 Ko | **0 affiche** au-dessus ; max **290,9 Ko** ; poste affiches 7,82 → **6,10 Mo** | **SOLDÉ** |
| **P-37** | 2 pages à **1 937 Ko** en 1ʳᵉ visite (seuil 900) | pire 1ʳᵉ visite **613 Ko**, pire suivante **331 Ko** (seuil 400) — **0 page** au-dessus sur 39 | **SOLDÉ** |
| **P-38** | 1 page du prototype à +18 px, 3 pages non migrées jusqu'à +262 px | **0 débordement sur 39 pages**, à **320, 375 et 768 px** | **SOLDÉ** |
| **P-39** | **221 couples** sous le seuil AA | re-mesuré à **242** au rendu réel après rétrofit, puis **70** — **71 % traités** ; 1 exception documentée | **PARTIEL — voir §2** |
| **P-40** | 3 champs sans indicateur de focus (`outline:none`) | **0 élément inatteignable, 0 sans indicateur** sur le parcours complet | **SOLDÉ** |
| **P-50** | `corpus.js` lisait encore `genre` en repli | le champ `genre` est **retiré du registre** (33 occurrences) et n'est plus lu | **SOLDÉ** |

**Sept écarts sur huit sont soldés et mesurés.** Le huitième est P-39, seul
écart de nature éditoriale : chaque couple y est un arbitrage, pas un défaut
mécanique.

## 2. P-39 — où en est le contraste

| | |
|---|---|
| Mesure de la recette (22/07, avant rétrofit) | 221 couples |
| Re-mesure au rendu réel après rétrofit | **242 éléments** |
| **Restants au 23/07 11h55** | **70** |
| Traités | **71 %** |

Les 70 restants, par nature :

| Nature | Éléments | Pourquoi ils résistent |
|---|---|---|
| dégradé partiel | 37 | le texte passe sur une zone du dégradé et échoue sur une autre |
| texte courant | 20 | dont les 4 lots à **fonds contradictoires** (une valeur par contexte serait nécessaire) |
| dégradé total | 12 | idem partiel, sur toute la course du dégradé |
| opacité | 1 | |

**49 des 70 sont sur fond en dégradé.** Ni une couleur ni une règle locale ne
les règlent proprement : il faudrait un voile derrière le texte, un
déplacement de l'élément, ou une exception documentée. C'est une décision
d'ensemble, pas 70 arbitrages.

**Exception déjà documentée** : l'ornement `≈≈≈` d'*Au fil de l'eau*
(`docs/aa-exceptions-documentees.md`) — élément décoratif reconnu par P-29.

## 3. Ce que le Temps 4 a trouvé EN PLUS

### 3.1 Réparé — `Frank Ruhl Libre` n'était atteignable par aucune pile

La fonte était embarquée, déclarée en `@font-face` avec son `unicode-range`
hébreu, sa licence versée au dépôt : **tout était là sauf son nom dans une
pile**. Le navigateur ne pouvait donc jamais l'atteindre, et l'hébreu du
*Golem* tombait sur Times New Roman.

Ce n'est pas un détail : `אמת` est le **filigrane de couverture** du film et le
pivot de son analyse. Réparé ; replis mesurés sur les 30 pages : **8 → 5**.

*(Ce reliquat était routé vers 065-5 par la note de clôture de la recette. Il
n'avait pas été traité au Temps 1 ; la sonde des fontes l'a retrouvé.)*

### 3.2 À arbitrer — 14 requêtes en 404 par visite, sur 7 pages

Sept pages appellent des photogrammes `assets/stills/<slug>-1.jpg` et `-2.jpg`.
**Le dossier `assets/stills/` n'existe pas** — il n'a jamais existé. Les mêmes
appels sont présents sur `main` : **le défaut est en ligne aujourd'hui**.

Pages concernées : `annie-hall`, `hamnet`, `shutter-island`,
`soudain-lete-dernier`, `soy-cuba`, `sud`, `the-old-oak`.

**Rien ne casse à l'écran** : chaque balise porte un `onerror` qui retire
l'image et masque le bloc s'il devient vide. Mais ce sont 14 requêtes en échec
par visite, visibles dans la console de tout lecteur qui l'ouvre.

**Deux voies, à trancher par AH** :
1. **retirer les balises** — le site cesse de demander ce qui n'existe pas ;
2. **les laisser** — elles préfigurent le volet ② de la Phase II (extraction
   outillée de photogrammes, PLAN-GENERAL), et le jour où les fichiers
   arriveront, les pages les afficheront sans retouche.

*Recommandation de la session : les laisser, et le dire au rapport. Le coût est
nul pour le lecteur, et retirer les balises reviendrait à défaire un travail
qu'il faudra refaire.*

### 3.3 À arbitrer — un repli de plus que ce que P-29 déclare

`U+25C6` (losange plein) sur `le-samourai` tombe en repli et **ne figure pas**
dans la liste de P-29, qui en déclare cinq. P-30 exige « zéro repli **non
déclaré** » : le critère est donc en défaut d'une unité.

La liste vit **dans `SPEC-SITE-V2.md`**, hors du périmètre d'écriture de ce
mandat (§8). **C'est la main du greffe, sur gate d'AH.**

## 4. Les autres prescriptions, re-mesurées au Temps 4

| | Exigence | Mesuré sur 39 pages |
|---|---|---|
| **P-32** | aucun URL cassé | **0 lien mort** sur 625 cibles internes · **0 ancre morte** |
| **P-24** | aucune requête tierce | **0 page** |
| **P-33** | aucune URL absolue | **0 occurrence** |
| **P-20** | aucune `@font-face` en page | **0** |
| **P-35** | HTML ≤ 60 Ko | max **49,0 Ko** (`hamlet`) |
| **P-02** | menu partout, un seul `aria-current` | **33/33** |
| **P-15** | cartouche partout | **33/33** |
| **P-17** | registre ↔ page | **0 divergence** |

## 5. Ce qui reste avant le gate de bascule

- les **70 écarts de contraste** — décision d'ensemble à prendre ;
- les **deux arbitrages du §3** — photogrammes absents, repli `U+25C6` ;
- l'annexe A du jour, **régénérée** : `docs/recette-v2-annexe-A-regeneree.md`,
  **34 URLs** (33 analyses + accueil), HEAD `13dab97` — c'est la checklist de
  P-32 pour la vérification post-bascule ;
- les **cinq cases** de la garantie ⑥ : revue intégrale locale par AH, tag
  `v1-finale` (posé), fallback prêt (écrit), sondes publiques prêtes, critères
  de fallback affichés.
