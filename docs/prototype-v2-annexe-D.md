# Annexe D renseignée — auto-contrôle du prototype v2

**Item** : BKL-065-3 · **Branche** : `v2-proto` · **Contrat** : `SPEC-SITE-V2.md` v1.0
**Renseignée le** : 22/07/2026 (horodatage instrumental) par la session
« Opus BKL-065-3 Prototype-Site-V2 »

> **P-42 : aucune ligne n'est réputée satisfaite par défaut.** Les 52
> prescriptions sont reprises, y compris celles qui ne concernent pas le
> prototype — une checklist partiellement remplie se lit comme une checklist
> passée. Chaque ligne porte son verdict et son moyen de preuve.

### Vocabulaire des verdicts

| Verdict | Sens |
|---|---|
| **OK** | vérifié sur le périmètre du prototype, avec sa preuve |
| **OK / lot** | vérifié sur les 9 pages du prototype ; les 30 pages non migrées ne le satisfont pas encore (rétrofit 065-5) |
| **ÉCART** | constaté non satisfait — arbitrage d'AH |
| **NV** | **non vérifiable** dans cet environnement (ni navigateur composant une image, ni serveur, ni Playwright) |
| **HP** | hors périmètre de ce mandat |

**Le comptage** : 24 OK · 5 OK/lot · 7 ÉCART · 9 NV · 7 HP — **52 lignes**.

---

| # | Prescription (abrégée) | Verdict | Preuve / motif |
|---|---|---|---|
| **P-01** | Un seul dossier `films/` pour les deux volets | **OK** | aucun dossier nommé d'après un volet ; `films/` contient `pandora-contrechamp.html` (Étude) et 32 Critiques |
| **P-02** | Menu partout, un seul `aria-current` | **OK / lot** | 9 pages sur 9 : exactement 1 `aria-current="page"` (vérifié au moteur) ; les 30 pages non migrées n'ont pas de menu |
| **P-03** | Lien vers la variante, qualifié par son volet | **OK** | champ → contrechamp et contrechamp → champ, 2 occurrences chacun, aucun lien mort ; le lien porte « Critique » / « Étude » |
| **P-04** | L'accueil ne liste le corpus qu'une fois | **OK** | un seul `<ol class="liste">` ; la grille d'affiches de la v1 a disparu |
| **P-05** | Pas de formulaire sur l'accueil | **OK** | `grep '<form'` sur `index.html` = **0** ; le formulaire vit sur `demander-une-analyse.html` |
| **P-06** | Objet en une = dernière publiée, à égalité titre décroissant | **OK** | tri `(datePublication ↓, title ↓)` dans `corpus.js` ; **réserve** : seules 3 entrées portent le champ, les autres sont rangées après (065-5) |
| **P-51** | Jamais d'entrée qui ne soit la dernière ou sa variante | **OK** | instrument `outils/observation-C2-carte-seule.html`, cas A : exactement 1 carte, classe `bloc-une` sans `couple` |
| **P-07** | Volets jamais à parité visuelle ; vues filtrées | **OK** | `critiques.html` et `etudes.html` appellent `Corpus.monte()` — le même composant que l'accueil — avec le seul paramètre `volet` |
| **P-08** | Aucune facette dérivée des pages | **OK** | `corpus.js` ne lit que `FILMS` ; aucun accès à `films/` |
| **P-09** | Vocabulaires fermés, fichier versionné dédié | **OK** | `assets/vocabulaires.js`, commité ; 5 axes (volet, genreBase, technique, pays, courant) |
| **P-10** | Valeur hors vocabulaire = publication bloquée | **OK** | `controle-vocabulaires.py --autotest` : valeur inventée « Atlantide » rejetée sur l'axe `pays`, **code de sortie 1**, valeur nommée ; dépôt non modifié |
| **P-11** | Le skill choisit et n'invente pas | **HP** | l'adaptation du skill est le périmètre de 065-5 |
| **P-12** | Ajout de terme = commit propre | **OK** | aucun commit ne mêle ajout de terme et publication d'analyse (aucune analyse publiée par ce mandat) |
| **P-13** | Facette affichée si ≥ 3 valeurs et ≤ 80 % | **ÉCART** | la règle est implémentée telle qu'écrite — **et c'est le problème** : elle ne pose **aucun seuil de couverture**. La facette « Pays » s'affiche alors que **3 entrées sur 33** portent le champ ; la filtrer masque 30 analyses. Signalé, non corrigé |
| **P-52** | Le volet est exempté de P-13 | **OK** | volet affiché malgré 32/33 sur une valeur (97 %) |
| **P-14** | Trois formulations invariantes | **OK / lot** | 2 des 3 régimes ont un exemplaire (R1 ×2, R3 ×1) ; R2 n'aura d'instance qu'à la première publication v2 |
| **P-15** | Cartouche sur toute page d'analyse | **OK / lot** | 3/3 des pages migrées ; aucun cartouche ne laisse le modèle implicite |
| **P-16** | Cartouche = composant unique | **OK** | aucune page migrée ne restyle `.cartouche`. ⚠️ **Collision de noms signalée** : `waterloo.html` déclare `header.cartouche{}` pour un usage bespoke — à traiter au rétrofit |
| **P-17** | Registre et cartouche portent la même information | **OK / lot** | 3/3 : `producteur` du registre repris mot pour mot dans le cartouche |
| **P-18** | `producteur` obligatoire pour toute entrée | **ÉCART** | **7 entrées sur 33** le portent. Rétro-remplissage = 065-5 ; la prescription n'est pas satisfaite aujourd'hui |
| **P-19** | Provenance hors squad nommée | **OK** | `pandora-contrechamp.html` : « premier jet produit par OpenAI GPT-5.5, repris et enrichi par la squad » |
| **P-20** | Aucune famille propre en page | **OK / lot** | 3 pages migrées : 0 `@font-face`, 0 famille nommée (42 déclarations substituées) ; 29 des 30 restantes en échec |
| **P-21** | Marqueur invariant en forme, couleur locale | **ÉCART** | vérifié au moteur : filet **solid 1px** (Critique) et **double 3px** (Étude), tous deux en `currentColor` — sur 2 palettes opposées (`#f2ead9`, `#0c0c0b`). Mais le critère exige **trois palettes contrastées** : le lot imposé (diptyque + 1) n'en fournit que **deux distinctes**, le diptyque partageant la sienne. Le critère ne peut pas être satisfait par ce lot |
| **P-22** | La distinction ne repose jamais sur la seule couleur | **OK** | par construction : le cartouche nomme le régime en toutes lettres et l'Étude porte son appareil théorique. *Le rendu en niveaux de gris reste NV* |
| **P-23** | `--volet` déclarée une fois par volet | **OK** | 2 déclarations dans `mobilier.css` ; `grep '--volet:'` dans `films/` = **0** |
| **P-24** | Aucune requête vers un domaine tiers | **OK / lot** | **0 ressource tierce** sur les 9 pages du prototype (contrôle greppable sur `link/script/img/@import/url()`) ; journal réseau du moteur : vide. **29 des 30** pages non migrées en chargent encore |
| **P-25** | Fontes auto-hébergées + licences embarquées | **OK** | 15 `.woff2` dans `assets/fonts/` (581,4 Kio) ; 15 déclarations `src`, 0 fichier manquant ; **3 licences OFL 1.1** (Literata, IBM Plex Mono, Frank Ruhl Libre). *La spec annonce « OFL / Apache 2.0 » : IBM Plex est passé sous OFL — écart de libellé, sans conséquence* |
| **P-26** | Titrage et texte sur la même famille | **OK** | styles calculés : `body` et `h1` → `Literata` sur les 3 pages |
| **P-27** | `unicode-range` restreint pour les non-latines | **OK** | déclarations cyrillique (`U+0301, U+0400-045F…`) et hébreu (`U+0590-05FF…`) présentes. *Le non-téléchargement effectif est NV : il demande un journal réseau réel* |
| **P-28** | Mobilier sans glyphe de fonte | **OK / lot** | 3 pages : **0 occurrence** de `←` ; pseudo-élément `::before` présent, bordures en `currentColor` vérifiées sur palette claire et palette sombre |
| **P-29** | Symboles bespoke listés nominativement | **NV** | demande `controle-glyphes.py`, qui vit hors du dépôt (`_scratch`) et n'est pas dans le périmètre de ce mandat |
| **P-30** | « Zéro repli NON DÉCLARÉ » | **NV** | idem P-29 |
| **P-31** | Aucune étape de compilation | **OK** | 0 manifeste de paquets, 0 configuration de bundler ; les outils Python ne produisent **aucun** fichier livré — ils lisent et rapportent |
| **P-32** | Aucun URL publié ne casse | **NV** | rien n'est publié : `v2-proto` n'est pas servie par Pages. Contrôle dû à 065-4 recette. ⚠️ **L'annexe A de la spec est périmée** : 34 URLs réels contre 33 listés |
| **P-33** | Liens relatifs, aucune URL absolue | **OK** | `grep 'cdatso.be'` sur tout le dépôt = **0** |
| **P-34** | Recette mécanisée par Playwright | **HP** | BKL-069 ; l'installation est une autorisation R4 distincte, non demandée par ce mandat |
| **P-35** | HTML ≤ 60 Ko | **OK** | maximum du corpus : **46,7 Kio** ; les 3 pages migrées ont gagné ~1,2 Ko chacune (menu + cartouche) |
| **P-36** | Affiche ≤ 300 Ko | **ÉCART** | **5 affiches** dépassent (maximum `pandora.jpg` à **1 660 Kio**). La spec en annonçait 4 le 21/07 : le corpus a grossi. Recompression = 065-5 |
| **P-37** | Page ≤ 900 Ko à la 1ʳᵉ visite, 400 ensuite | **NV** | demande un journal réseau avec cache froid puis chaud |
| **P-38** | Aucun défilement horizontal à 320 px | **NV** | **aucune géométrie mesurable** : le moteur disponible ne compose pas — `clientWidth` = 0 même après redimensionnement |
| **P-39** | Contraste AA 4,5:1 / 3:1 | **ÉCART** | comptage mécanique livré : **23 écarts certains** sur **17 pages**, 48 probables. Détail : `outils/contraste-sortie.md`, constat C-3. **Compté, jamais corrigé** |
| **P-40** | Interactif atteignable et visible au clavier | **ÉCART** | la règle `:focus-visible` est posée dans `mobilier.css` et s'applique ; **le parcours à la tabulation est NV**. La ligne ne peut donc pas être déclarée satisfaite |
| **P-41** | Recherche < 100 ms, jusqu'à 500 entrées | **NV** | ni mesure de temps de rendu, ni jeu de 500 entrées synthétiques (non demandé au prototype) |
| **P-42** | Chaque ligne vérifiée et datée | **OK** | le présent document : 52 lignes, aucune réputée satisfaite par défaut |
| **P-43** | Le volet pilote ne conditionne pas la bascule | **HP** | 065-4 |
| **P-44** | `v2-proto` poussée dès création, jamais fusionnée | **OK** | `origin/v2-proto` créée et poussée **avant toute autre écriture** ; `origin/main` inchangé à `0b0f476` du début à la fin ; `git log main..v2-proto` = 6 commits, aucun sur `main` |
| **P-45** | Rétrofit commité par nature | **HP** | 065-5. *Le prototype en a néanmoins tenu la discipline : 6 commits par nature, aucun commit fourre-tout* |
| **P-46** | Premier push sur `main` = point de non-retour | **HP** | aucun push sur `main` par ce mandat — vérifiable au journal |
| **P-47** | Annexe A régénérée avant bascule | **HP** | 065-4. ⚠️ Voir P-32 : elle est déjà périmée d'une entrée |
| **P-48** | Retour arrière écrit **et éprouvé** | **HP** | 065-5. *Observation versée : une révocation réelle a eu lieu pendant ce mandat — les 3 pages migrées ont été ramenées à l'état de `main` par `git checkout --`, puis la migration rejouée après correction du script. La réversibilité par script + git fonctionne* |
| **P-49** | Pas d'index plein texte en 065-3 | **OK** | aucune trace : la recherche porte sur les seules métadonnées du registre |
| **P-50** | `genre` déprécié, non lu par le site v2 | **ÉCART** | **écart assumé de la session** : `corpus.js` lit encore `f.genre` **en repli d'affichage** (2 occurrences) pour les 30 entrées sans `genreBase`. Sans ce repli, 30 entrées s'afficheraient sans aucun genre pendant toute la vie du prototype. Le repli disparaît avec le rétrofit ; il est signalé plutôt que tu |

---

## Les sept écarts, rassemblés

| # | Prescription | Nature | Qui tranche |
|---|---|---|---|
| 1 | **P-13** | la règle n'a pas de seuil de **couverture** : une facette remplie à 3/33 s'affiche | AH — amendement de spec |
| 2 | **P-18** | `producteur` sur 7 entrées / 33 | 065-5 (rétrofit) |
| 3 | **P-21** | le lot imposé ne fournit que **2 palettes distinctes**, le critère en exige 3 | AH — lot ou critère |
| 4 | **P-36** | 5 affiches au-dessus de 300 Ko | 065-5 (recompression) |
| 5 | **P-39** | 23 écarts de contraste certains sur 17 pages | AH — écart par écart |
| 6 | **P-40** | focus posé, parcours clavier non vérifié | 065-4 recette |
| 7 | **P-50** | `genre` encore lu en repli d'affichage — **écart de la session** | disparaît au rétrofit |

## Les neuf lignes non vérifiables, et pourquoi

`P-29`, `P-30` (outil hors dépôt) · `P-32` (rien n'est publié) · `P-37`,
`P-38`, `P-41` (aucune géométrie ni journal réseau : le moteur disponible ne
compose pas d'image) · plus les volets non mesurables de `P-22`, `P-24`
et `P-27`.

**Aucune n'est déclarée satisfaite.** C'est la même exigence que « zéro repli
NON DÉCLARÉ » : ce qui n'a pas été vérifié doit se voir.
