# Procédure d'adoption au site d'une page du pilote

*BKL-CIN-098, lot D. Écrite le 21/09/2026 (session « Opus CIN-098 lot D Adoption ») et appliquée le
même jour à un premier cas, *Le Château ambulant* — voir §7. Norme : `SPEC-SITE-V2` v1.11,
**régime R4** (§5.2, §5.3) et **P-62**.*

**Adopter, c'est COPIER.** Une page qu'AH a lue et validée sur la surface d'essai
(`pilote.cdatso.be`) entre au site par une copie à l'octet, puis par des substitutions qui changent
**ce qui dit d'où vient la page**, et rien d'autre. La page du pilote n'est jamais retouchée : elle
reste en ligne, c'est la pièce de mesure de la chaîne.

## 1. Préalables — tous exigés, sinon on ne commence pas

1. **Un mandat et un gate PAR PAGE** : le push est la publication (charte règle 6). Formule de gate
   adressée, du type « go adoption `<slug>` — fenêtre `<session>` ».
2. **AH a lu et validé la page** (jugement de qualité cité, avec sa date).
3. **La demande est en `publiee_pilote`** dans la vue publique `demandes_publiques`, avec
   `page_pilote` = `https://pilote.cdatso.be/films/<slug>.html` (lire la clé publiable par
   expression régulière, sans jamais l'afficher).
4. **La cible n'existe pas** en production : `films/<slug>.html` absent, 0 occurrence du slug dans
   `assets/films-data.js` et `docs/journal_analyses_films.md`. Sinon : ARRÊT.
5. **Les valeurs des axes fermés** du registre pilote (`volet`, `genreBase`, `pays`, `technique`)
   existent dans `assets/vocabulaires.js` de la production. Sinon : ARRÊT — l'ajout d'un terme est
   un acte distinct (P-12), jamais mêlé à une adoption.
6. **Mesures « avant »** : `git status --porcelain -uall` et `HEAD` du dépôt pilote ; SHA-256 de la
   page et de l'affiche pilotes ; SHA-256 de `skills\analyse-films-cinema\SKILL.md` (épinglé par le
   calque pilote) ; les contrôles du §4 sur le dépôt de production intact.
7. **La date au registre** est décidée par AH. Premier cas : la date d'**adoption** (décision d'AH
   du 20/09/2026) ; la date de production reste écrite dans la note de provenance.

## 2. Les gestes, dans l'ordre

1. **Copie à l'octet** de `films/<slug>.html` et, s'il y en a une, de `assets/posters/<slug>.jpg`,
   depuis le dépôt pilote : `[System.IO.File]::Copy(<src>, <dst>, $false)` (le `$false` refuse
   d'écraser). Vérifier SHA-256 source = cible.
2. **Les quatre substitutions** (§3), sur la copie de production seulement. Chaque texte remplacé
   doit apparaître **exactement une fois** ; sinon ARRÊT sans écrire.
3. **Registre** — UNE entrée ajoutée en fin de `FILMS`, **recopiée** de l'entrée pilote ; seuls
   changent `datePublication` (décision d'AH) et `producteur` =
   `'<Modèle> (chaîne pilote automatique, adoptée)'` (P-62 ③). `url` et `poster` gardent leurs
   chemins relatifs, valables en production. Prouver champ par champ que rien d'autre ne diffère.
4. **Journal de production** — UNE ligne dans `docs/journal_analyses_films.md`, qui nomme la
   provenance : *adoptée du pilote ; activation du <date heure> ; commit pilote `<sha>` ; lue et
   validée par AH le <date> ; adoptée le <date>*.
5. **Générateurs** : `python outils/genere-liste-statique.py --depot .` puis
   `python outils/genere-sitemap.py --depot .` — la page adoptée entre au catalogue **et** au
   sitemap (elle est indexable).
6. **Contrôles** (§4), comparés à l'« avant ».
7. **La preuve par le diff** (§5).
8. **Commit à fichiers nommés, en un appel**, puis **ARRÊT** : remise à AH (diff de preuve, entrée,
   ligne de journal, lecture de plage, recherche de secrets) — et push **seulement** sur son gate,
   **une** fois, hook joué, jamais `--no-verify`.
9. **Recette sur ce qui est servi** (cache de 600 s) : page adoptée 200, sans bandeau, sans
   `noindex`, signature R4 mot pour mot, servie = dépôt à l'octet ; catalogue, sitemap, affiche ;
   **et le pilote n'a pas bougé** (sa page 200, avec bandeau et `noindex`, identique à l'octet ;
   `git status` du dépôt pilote = l'« avant »). Puis rappeler à AH son geste : depuis sa page
   privée, la demande passe de `publiee_pilote` à `traitee`.

## 3. Les quatre substitutions — la table du calque pilote, parcourue à l'envers

| # | Zone | Dans la page du pilote | Dans la page adoptée |
|---|---|---|---|
| ① | balise `robots` | `<meta name="robots" content="noindex, nofollow">` | **retirée** — aucune page de production n'en porte (mesuré : 0 sur 48 le 20/09/2026 ; re-mesurer) |
| ② | bandeau **et sa feuille** | le bloc `<div class="bandeau-pilote" role="note">…</div>` (premier enfant de `<body>`) **et** `<link rel="stylesheet" href="../assets/pilote.css">` dans `<head>` | **les deux retirés**, avec la ligne vide qui suit le bloc. ⚠️ La table du calque ne nomme pas ce lien, mais la chaîne le pose sur toute page : `pilote.css` porte **toutes** les règles du bandeau et n'existe pas en production (décision d'AH du 21/09/2026 : il appartient à la zone ②) |
| ③ | note « Provenance » | « …chaîne pilote automatique, sans relecture humaine — surface d'essai, hors du corpus publié. » | P-62 ② : « Analyse produite le \<date\> par la chaîne pilote automatique, sans relecture humaine ; lue, validée et adoptée au site le \<date\> par Christo Datso. » |
| ④ | **cartouche** (bloc contigu de trois lignes) | étiquette `R2 &mdash; Critique nouvelle` · signature « …(\<Modèle\>, chaîne pilote automatique, sans relecture humaine). » · `Publi&eacute;e le <date de production>` | étiquette `R4 &mdash; Page adopt&eacute;e du pilote` · signature = **formule R4 mot pour mot**, recopiée de `SPEC-SITE-V2` §5.3 : « Analyse produite par IAGen Claude d'Anthropic (modèle \<nom\>, chaîne automatique), relue et adoptée par Christo Datso. », `<nom>` = le modèle tel que le journal pilote l'a inscrit · `Publi&eacute;e le <date au registre>` (décision d'AH du 21/09/2026 : la zone ④ est le cartouche entier — l'étiquette R2 serait fausse, P-15, et la date du cartouche suit toujours `datePublication`) |

*Le texte de l'étiquette R4 n'est pas fixé par la norme (le nom du régime au tableau §5.2 a été
recopié) : question routée au greffe.*

## 4. Contrôles, comparés à l'« avant »

`controle-vocabulaires.py --strict` · `genere-liste-statique.py --verifier` ·
`genere-sitemap.py --verifier` · `recompresse-affiches.py --seuil 300 --simuler` ·
`controle-contraste.py --sortie-e1 <fichier>` (0 E1 **nouveau** hors `outils/hooks/baseline-e1.txt`) ·
P-62 sur la page (0 `bandeau-pilote`, 0 `noindex`, 0 `pilote.cdatso.be`, 0 `pilote.css`) ·
**P-14 sur tout le corpus** (toute signature relève de R1 à R4 ; `pandora-contrechamp` relève de
R3 adaptée par P-19). `controle-glyphes.py` ne contrôle pas les pages du site : il était rouge
avant le premier cas, il ne peut pas être changé par une adoption.

## 5. La preuve par le diff

`diff -u <pilote>/films/<slug>.html <production>/films/<slug>.html`, **cité en entier** à la
remise : il ne montre que les quatre zones (cinq emplacements : robots, lien `pilote.css`, bandeau,
provenance, cartouche). **Une autre zone = ARRÊT.** Compléter par la preuve que tout le reste est
identique : `<style>` bespoke, et tout ce qui va du sommaire à `</html>` (dont `<main>`, le texte de
l'analyse).

## 6. Ce qui ne se fait JAMAIS

- **Écrire dans le dépôt pilote**, sous aucune forme — la page pilote reste telle quelle.
- **Réécrire, corriger ou « améliorer » l'analyse** : un défaut vu se rapporte à AH, qui décide.
- **Modifier la skill de production** (`analyse-films-cinema`) ou le calque : leur empreinte est
  épinglée, la modifier arrête la chaîne. L'adoption n'est PAS une étape de la skill.
- Inventer ou amender la formule R4 ; ajouter un lien vers `pilote.cdatso.be` (P-62 ⑤).
- Pousser sans le gate de la page, deux fois, ou avec `--no-verify`.
- Écrire en base : le passage de la demande en `traitee` est un geste d'AH.

## 7. Retour arrière

Une adoption est **un** commit : `git revert <commit>` puis `genere-liste-statique.py` et
`genere-sitemap.py` si besoin, et push **sur gate** — la page pilote, intouchée, reste la
référence. Doctrine et délais de republication de GitHub Pages :
[`procedure-retour-arriere.md`](procedure-retour-arriere.md) (§1 : le retour arrière ne restaure pas
le temps pendant lequel la page a été publique).

## 8. Cas appliqués

| Date | Page | Commit pilote | Validée par AH | Adoptée | Mandat |
|---|---|---|---|---|---|
| 21/09/2026 | *Le Château ambulant* (`le-chateau-ambulant`) | `4d6ffbf` (activation du 19/09/2026 00h10) | 19/09/2026 | 21/09/2026 | BKL-CIN-098 lot D |

*Deux conséquences constatées au premier cas, à attendre aux suivants : ① avec la date
d'adoption, la page adoptée devient la « dernière publiée » (badge des listes, première carte de
l'accueil) ; ② `core.autocrlf=true` sur ce dépôt : le registre et le journal sont en CRLF dans
l'arbre de travail — écrire en CRLF pour ne pas mêler les fins de ligne.*
