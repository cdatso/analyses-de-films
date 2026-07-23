# Rapport de pré-bascule — BKL-065-5

**Temps 5 du mandat**, remis à AH le **23/07/2026 à 11h58** (horodatage
instrumental). Session « Opus BKL-065-5 Migration ».

> ⚠️ **CE DOCUMENT NE DEMANDE PAS LE GATE. IL LE PRÉPARE.**
> La garantie ⑥ de l'amendement 1 fixe **cinq cases** à cocher avant que
> « GO BASCULE » puisse être prononcé. **Une d'elles est vide, et elle ne peut
> pas l'être par moi** : la revue intégrale du site v2 par AH, servi en local.
>
> Sur GitHub Pages, **pousser sur `main`, c'est publier**. Tout se vérifie
> avant, rien après.

---

## 1. Les cinq cases de la garantie ⑥

| | Case | État |
|---|---|---|
| 1 | **Revue intégrale locale des 34 pages par AH** | ⬜ **NON FAITE — condition d'entrée du gate** |
| 2 | Tag `v1-finale` posé | ✅ sur `0b0f476`, poussé le 22/07 à 19h53:07 |
| 3 | Commande de fallback prête à coller | ✅ écrite en toutes lettres, §5 |
| 4 | Sondes post-bascule prêtes | ✅ éprouvées à blanc, **10 s** pour 39 documents |
| 5 | Critères de fallback affichés | ✅ §6, prédéfinis |

**Quatre cases sur cinq.** La première est la tienne.

## 2. Ce que la bascule publierait

| | |
|---|---|
| Fichiers modifiés ou ajoutés | **152** |
| Lignes | +101 305 / −1 137 |
| Poids binaire ajouté | **4,03 Mo** |
| Commits de la session | **39**, tous révocables individuellement |

Répartition du poids binaire :

| | |
|---|---|
| `docs/recette-v2-captures` | 2,13 Mo |
| `assets/posters` (recompressées) | 1,31 Mo |
| `assets/fonts` | 0,59 Mo |

> **Point signalé, non tranché** : les 2,13 Mo de captures de recette seront
> **publiquement accessibles** — GitHub Pages sert tout le dépôt. Elles ne
> présentent aucun risque (ce sont des captures du site lui-même), mais elles
> seront en ligne. Les retirer avant le merge est possible ; les garder est
> défendable au titre de la transparence du chantier. **À ton arbitrage.**

Après bascule, le site exposera **39 URLs** : les 34 publiés + les 5 pages du
menu v2 qui n'existaient pas.

## 3. L'état du site, mesuré

### 3.1 Les prescriptions vérifiables, sur 39 pages

| | Exigence | Mesuré |
|---|---|---|
| **P-32** | aucun URL cassé | **0 lien mort** sur 625 cibles · **0 ancre morte** |
| **P-24** | aucune requête tierce | **0 page** |
| **P-33** | aucune URL absolue | **0** |
| **P-37** | ≤ 900 Ko / 400 Ko | pire **613** / **331 Ko** |
| **P-38** | 0 défilement à 320 px | **0** à 320, 375 et 768 px |
| **P-40** | clavier atteignable, visible | **0** inatteignable, **0** sans indicateur |
| **P-35** | HTML ≤ 60 Ko | max **49,0 Ko** |
| **P-36** | affiche ≤ 300 Ko | max **290,9 Ko** |
| **P-20** | 0 `@font-face` en page | **0** |
| **P-02 / P-15 / P-17** | menu, cartouche, registre↔page | **33/33**, 0 divergence |

### 3.2 Les 8 écarts de la recette du 22/07

**Sept soldés, un partiel.** Détail ligne à ligne :
`docs/recette-v2-annexe-D-delta.md`.

Le partiel est **P-39 (contraste)** : 242 éléments mesurés au rendu réel après
rétrofit, **70 restants — 71 % traités**. Dont **49 sur fond en dégradé**, où
le texte passe sur une zone et échoue sur une autre : ni une couleur ni une
règle locale ne les règlent. C'est une décision d'ensemble (voile, déplacement,
ou exception documentée), pas 70 arbitrages.

**Une exception est déjà documentée** au registre
`docs/aa-exceptions-documentees.md`.

### 3.3 Deux défauts PRÉ-EXISTANTS corrigés au passage

Ils étaient **en ligne depuis des semaines**, identiques sur `main` :

- **« Lordsburg »** dans l'en-tête de `la-chevauchee-fantastique` : ratio
  **1,00**, mot invisible → **6,59** ;
- **le colophon de `le-cheval-de-turin`** : ratio **1,00** → **6,06** ;
- **l'hébreu du `le-golem`** : `Frank Ruhl Libre` était embarquée mais nommée
  par aucune pile — le filigrane `אמת`, pivot de l'analyse, tombait sur Times
  New Roman. Réparé.

## 4. Ce qui reste ouvert, et qui doit être connu AVANT le gate

| # | Point | Nature |
|---|---|---|
| 1 | **70 écarts de contraste** dont 49 en dégradé | décision d'ensemble |
| 2 | **14 requêtes en 404 par visite** sur 7 pages (`assets/stills/` n'a jamais existé) — **défaut antérieur, déjà en ligne**, sans effet visible (`onerror`) | arbitrage : retirer les balises ou les laisser pour le volet ② |
| 3 | **`U+25C6`** en repli, absent de la liste **P-29** — P-30 en défaut d'une unité ; la liste vit **dans la spec**, hors de mon périmètre | main du greffe, sur gate |
| 4 | **Bandeau `.proto-note`** : il annonce un « prototype », mention qui deviendra fausse une fois public | arbitrage |
| 5 | **2,13 Mo de captures de recette** publiés avec le reste | arbitrage |

*Aucun de ces cinq points n'est un critère de fallback. Ils sont listés pour
que le gate se prononce en les connaissant, non pour le retarder.*

## 5. La commande de fallback — prête à coller

**Ne pas composer une commande d'urgence en situation d'urgence.**

> **SHA DU MERGE DE BASCULE, relevé le 23/07/2026 à 12h14, AVANT le push :**
> **`33183e9095a03e683061258e93b6076334242523`**
> *(court : `33183e9`) — contrôle fait au moment du relevé : l'arbre de `main`
> après merge est identique à celui de `v2-proto`, 0 fichier de différence.*

```bash
git -C "C:/Users/cdats/Claude/Projects/analyses-de-films" revert -m 1 33183e9095a03e683061258e93b6076334242523 --no-edit
git -C "C:/Users/cdats/Claude/Projects/analyses-de-films" push origin main
```

**Second filet, indépendant** — le tag `v1-finale`, SHA écrit en toutes lettres
pour ne dépendre d'aucune résolution de nom :

```bash
git -C "C:/Users/cdats/Claude/Projects/analyses-de-films" push origin 0b0f47698177476e1d59501ab9a61d9906cca316:main --force-with-lease
```

**Procédure ÉPROUVÉE** le 22/07 : merge à blanc puis revert sur branche
jetable, **arbres identiques au hash** (`c3873b0f…`), `git diff` vide. Détail :
`docs/procedure-retour-arriere.md`.

**Délai attendu** : Pages a servi le push du 21/07 en ~60 s → retour v1 en
**2 à 4 minutes**, borne haute 5. Un site encore en v2 90 secondes après le
push du revert **n'est pas** un échec du retour arrière.

## 6. Critères de fallback — aucun jugement à chaud

**FALLBACK IMMÉDIAT**, sans délibération :

- tout **404 / 500** sur l'un des 39 URLs ;
- **CSS ou fontes non servis** (page nue, typographie de repli) ;
- **rendu cassé** sur une page-témoin.

**PAS de fallback** : tout autre défaut mineur — consigné, arbitré à froid.

Le contrôle est automatisé :

```bash
python outils/recette-playwright/sonde-post-bascule.py --public
```

Elle vérifie les 34 URLs de l'annexe A **du jour** + les 5 pages du menu, puis
sur trois témoins (`index`, `pandora`, `le-golem`) : menu présent, un seul
`aria-current`, cartouche, corps non vide, **Literata et IBM Plex Mono
réellement servies**. Code de sortie **1 = fallback**.

*Éprouvée à blanc en local : 39 documents, 0 échec, **10 secondes**.*

## 7. Fenêtre de bascule — garantie ⑤

| | |
|---|---|
| Routine nocturne | **en pause** (`enabled:false`) — vérifié ce jour |
| Canari pré-nuit | **en pause** (`enabled:false`) |
| Briefing du soir | actif, **21h06** — brouillon Gmail seul, n'écrit pas dans le dépôt |
| À éviter | dimanche 18h00 (sauvegarde v5) · fin de soirée |
| Requis | **AH présent**, moment calme choisi par lui |

**Aucune tâche planifiée n'écrit dans le dépôt du site.** La seule contrainte
d'horaire est d'éviter 21h06 par simple hygiène.

## 8. La séquence, le moment venu

1. AH prononce **« GO BASCULE »** — la formule exacte, aucun synonyme ;
2. la session **écho-confirme** (R-009) et attend la confirmation ;
3. `git merge --no-ff v2-proto` sur `main`, message de bascule ;
4. **le SHA du merge est relevé et inscrit au §5** ;
5. `git push origin main` — **le site v2 est public** ;
6. `sonde-post-bascule.py --public` — verdict en ~2 min ;
7. spot visuel sur 3 pages, temps de service de Pages noté ;
8. si un critère du §6 est atteint : **fallback immédiat**, diagnostic ensuite.

---

## État des références à l'heure de ce rapport

| | |
|---|---|
| `origin/main` | **`0b0f476`** — inchangée depuis le 22/07 à 18h46 |
| `origin/staging` | `d680c7e` — jamais touchée |
| `v2-proto` | `3a63297` — **39 commits** de la session |
| tag `v1-finale` | `0b0f476` — posé et poussé |
| Arbre de travail | propre |
