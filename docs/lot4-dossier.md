# Lot 4 — dossier pour l'œil d'AH

**BKL-065-5, Temps 2.** Session « Opus BKL-065-5 Migration », **23/07/2026
09h02** (horodatage instrumental). Gate d'AH : « go pour le lot 4 ».

> **Ce que ce document n'est pas.** Ce n'est pas une liste de corrections
> appliquées. Le lot 4 est celui dont j'ai dit dès la proposition qu'il
> engageait le dessin et non la conformité. En l'ouvrant, j'ai d'abord voulu
> **vérifier la mesure elle-même** — et bien m'en a pris.

---

## 1. Ce que la vérification de la mesure a changé

Ma sonde de contraste retenait comme « pire cas », sur un fond en dégradé, le
plus défavorable des **arrêts de couleur déclarés**. C'est prudent, et souvent
faux : un dégradé qui va du bleu nuit au sable sur toute une couverture voit
son arrêt « sable » opposé à un texte qui ne descend jamais si bas.

J'ai donc écrit `outils/recette-playwright/sonde-fond-peint.py`, qui lit les
**pixels réellement peints** derrière chaque texte : les glyphes passent en
`color:transparent` (le fond propre de l'élément reste, la mise en page ne
bouge pas), une capture est prise, et le cadre de chaque élément est lu.

**Deux pièges rencontrés en la construisant, tous deux corrigés :**

| Piège | Effet | Correctif |
|---|---|---|
| `visibility:hidden` pour masquer le texte | masque l'élément **entier, fond compris** — un cartel à fond saumon posé sur une couverture sombre était mesuré contre la couverture | `color:transparent`, qui ne retire que les glyphes |
| descendance non masquée | les glyphes d'un `<em>` intérieur restaient peints et étaient comptés comme du fond | masquage de tout le sous-arbre |

**Limite qui subsiste, et que je ne masque pas** : la sonde prend le minimum
sur **tout le cadre** de l'élément, y compris les zones où aucun glyphe ne se
pose (fin de dernière ligne, marge intérieure). Elle **sur-détecte**. Elle est
un **détecteur**, pas un compteur : chaque cas qu'elle signale doit être vu.
C'est pourquoi les constats ci-dessous ont tous été **vérifiés un par un**.

---

## 2. ⚠️ Une régression de ma main — trouvée et corrigée

**Commit du correctif : `5bc3aee`.**

Ma passe de dédoublement avait rendu **quasi invisibles** les blocs de
provenance de deux pages :

| Page | Ratio après ma passe | Cause |
|---|---|---|
| `hamlet` | **1,00** | redéfinition calée sur un fond **calculé** (`#979c9d`, gris moyen) |
| `la-nuit-de-san-lorenzo` | **1,20** | idem (`#9a9fa7`) |

**Le fond calculé n'était pas le fond peint.** Ces blocs déclarent un fond
semi-transparent ; le calcul le composait sur le **corps clair** de la page,
alors qu'ils vivent dans un **conteneur sombre**. La couleur de texte a donc
été assombrie… vers la couleur du fond.

**Correctif** : la teinte d'origine restaurée en contexte — elle tenait déjà,
et largement : **6,75** et **8,17** mesurés sur pixels peints.

*Leçon, et elle vaut pour la suite du chantier : une correction de contraste
fondée sur le CSS seul doit être re-vérifiée à l'écran. Le CSS dit ce qui est
déclaré ; seul le rendu dit ce qui est vu.*

---

## 3. DEUX textes réellement invisibles — et ils sont en ligne aujourd'hui

*(Trois étaient annoncés ; le troisième s'est révélé un faux positif de ma
sonde à la vérification — voir §3.3.)*

Vérifiés au pixel, et **antérieurs à tout mon travail** : les valeurs sont
identiques sur `main`, donc **publiées à cette heure sur le site**.

### 3.1 `la-chevauchee-fantastique` — « Lordsburg » dans l'en-tête

| | |
|---|---|
| Élément | `.itineraire span strong` (le terminus de la ligne de diligence) |
| Texte | `#241a12` (`--brule`) · fond peint mesuré **(37, 27, 19)** |
| Ratio | **1,00** — le mot est invisible |
| Cause | la règle générique `strong{ color:var(--brule) }` s'applique **dans l'en-tête sombre**, où la couleur du texte est `--sable` |

*Le mot « Lordsburg » est le terme du voyage : le seul mot mis en gras de
l'itinéraire, et le seul qu'on ne peut pas lire.*

**Correctif proposé** : `header.ligne strong{ color:inherit; }` — le gras
reprend la couleur de son contexte. Une ligne, aucun effet ailleurs.

### 3.2 `le-cheval-de-turin` — le colophon du pied de page

| | |
|---|---|
| Texte | `#d9d6cf` (`--storm`) · fond peint **(216, 213, 206)** |
| Ratio | **1,00** |

**Correctif proposé** : une variable-sœur de texte assombrie pour le pied de
page, sur le modèle du lot 3.

### 3.3 `rouges-et-blancs` — les cartels du schéma SVG : **FAUX POSITIF**

> **ERRATUM du 23/07 09h12 (charte règle 5).** Ce cas était annoncé ci-dessus
> comme un troisième texte invisible. **Il ne l'est pas.** Vérification faite
> avant toute correction : les cartels sont parfaitement lisibles.

| | Ce que ma sonde lisait | Ce qui est réellement peint |
|---|---|---|
| Propriété | `color` héritée : `#0c0c0b` | **`fill="#c9c4b4"`** (écrit dans le balisage) |
| Ratio sur le champ `#1a1914` | 1,11 → « illisible » | **10,09 → largement conforme** |

**Dans un SVG, la couleur du texte se déclare en `fill`, pas en `color`.** La
valeur de `color` y est héritée du document et **n'est jamais peinte**. Ma
sonde la lisait quand même : elle a donc compté comme invisible un texte
clair sur fond sombre.

**Sans cette vérification, j'aurais « corrigé » un texte sain** — et abîmé un
schéma qui allait très bien. Le correctif porte sur l'outil, pas sur la page :
`sonde-fond-peint.py` lit désormais `fill` dès que l'élément appartient à un
SVG.

*Ce qui reste vrai de mon constat initial : `color:` est bien l'angle mort de
`applique-lots-aa.py` et de `dedouble-contexte.py`, qui ne savent pas
atteindre un `fill`. Simplement, ici, il n'y avait rien à atteindre.*

---

## 4. Ce qui reste au lot 4, et les trois voies

Le reste du lot 4 — les déplacements lourds — n'a **pas** été appliqué, et je
maintiens de ne pas l'appliquer mécaniquement. Rappel des cas les plus parlants
(mesures du 23/07) :

| Page | Variable | La correction mécanique donnerait | Pourquoi c'est inacceptable |
|---|---|---|---|
| `bienvenue-a-suburbicon` | `--creme` | `#f4efe3` → `#201a0d` | la crème est **le fond** de trois blocs |
| `pandora` | `--platre` | `#f2ead9` → `#51401c` | le plâtre est **le fond de la page** |
| `shutter-island` | `--paper` | déplacement 0,72 | idem, couleur de papier employée en texte |
| `julie-en-12-chapitres` | `--gris-fjord` | → `#f4f4f5` | le gris deviendrait blanc |

**Les trois voies, pour chacun** :
1. **corriger localement** l'élément fautif (une règle dédiée, la variable
   intacte) — la voie la plus fréquente et la moins invasive ;
2. **documenter l'exception** au registre `aa-exceptions-documentees.md`,
   avec son motif — P-30 pose « zéro écart *non déclaré* », pas « zéro
   écart », et P-39 prévoit qu'un écart soit **arbitré** ;
3. **retoucher le fond** — réservé aux cas où le texte est illisible, comme
   les trois du §3.

**Ma recommandation** : traiter d'abord les **trois invisibles du §3** (ce sont
des défauts de lisibilité réels, publiés, et leurs correctifs sont locaux et
sûrs), puis parcourir les déplacements lourds page par page, avec toi, en
choisissant entre corriger localement et documenter.

---

## 5. État de la mesure au moment d'écrire

| | |
|---|---|
| Écarts au départ du Temps 2 | 242 |
| Après lots 1, 2, 3, 5 et dédoublement | **85** (−65 %) |
| Écart documenté | 1 (l'ornement `≈≈≈` d'*Au fil de l'eau*) |
| Régressions introduites puis corrigées | 2 |
| Invisibles pré-existants identifiés | 3 |

`main` est restée à `0b0f476` du premier au dernier geste.
