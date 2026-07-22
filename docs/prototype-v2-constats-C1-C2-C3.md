# Les trois constats du prototype v2 — C-1, C-2, C-3

**Item** : BKL-065-3 · **Branche** : `v2-proto` · **Session** : « Opus BKL-065-3
Prototype-Site-V2 » (AC-Exec / Code / Opus 4.8)
**Rédigé le** : 22/07/2026 à 08h11 (horodatage instrumental)
**Contrat** : `SPEC-SITE-V2.md` v1.0 — §12 (Q-3), §3.2 (réserve P-51), P-39

> Ces trois constats sont des **livrables de rang égal avec le prototype**
> (mandat §7.2). La session **observe et compte** ; elle ne tranche rien et ne
> corrige rien. Chaque écart relevé est un arbitrage d'AH.

---

## Limite commune aux trois constats — à lire d'abord

**Cette session n'a pas pu mesurer une seule géométrie.** Le navigateur
disponible ne compose aucune image : `document.documentElement.clientWidth`
et `window.innerWidth` y valent **0**, y compris après redimensionnement
explicite. Toute mesure de largeur, de hauteur, de longueur de ligne ou de
débordement prise dans cet environnement serait fausse — et une mesure fausse
vaut moins que pas de mesure.

**Ce qui reste valide et a été employé** : les **styles calculés** (famille
résolue, style et épaisseur de filet, couleur effective, contenu de
pseudo-élément) et le **journal réseau**, qui ne dépendent pas de la mise en
page. C'est sur eux que reposent les vérifications de P-20, P-21, P-24, P-26
et P-28.

**Ce qui reste dû** : tout jugement de proportion. Il appartient à AH sur un
navigateur réel — ce que le mandat prévoyait déjà (« la revue sur maquette
vivante est SON travail »). Les instruments sont livrés pour qu'il n'ait rien
à reconstruire.

---

## C-1 — La typographie unifiée tient-elle sur trois ossatures bespoke ? *(Q-3)*

### Ce qui a été fait

Trois pages migrées, choisies pour s'opposer :

| Page | Fond | Luminance | Ossature | Familles d'origine |
|---|---|---|---|---|
| `pandora.html` | `#f2ead9` | 0,827 | couverture « toile métaphysique », colonne unique | Marcellus (titres) · Spectral (texte) · Cutive Mono (cartels) |
| `pandora-contrechamp.html` | `#f2ead9` | 0,827 | la même, plus l'appareil théorique | idem |
| `rouges-et-blancs.html` | `#0c0c0b` | **0,004** | letterbox, cadre scope 2.35:1 | **Oswald** (titres) · Inter (texte) · JetBrains Mono |

**Critère de choix de la page sombre, écrit avant la migration** : fond le plus
sombre du corpus à 0,0007 près (2ᵉ des 33) **et** déplacement typographique
maximal — trois familles dont **aucune n'est une serif**, quand Pandora en
porte deux. `soudain-lete-dernier.html`, marginalement plus sombre, emploie
déjà **IBM Plex Mono**, une famille du système v2 : sa substitution aurait été
en partie un non-événement, donc le moins bon test de Q-3.

**Mesuré après migration** (styles calculés, moteur réel) : `body` et `h1` sur
**Literata** dans les trois pages ; **42 déclarations** de famille substituées
(13 + 13 + 16) ; **0 famille nommée résiduelle** ; **0 requête tierce** ;
cartels sur **IBM Plex Mono**.

### Ce que la session observe

**① Le rôle « mono » se pose sans heurt.** Les trois pages avaient déjà une
monospace, et à la même place — les cartels et la fiche technique. IBM Plex
Mono y remplace Cutive Mono et JetBrains Mono dans une fonction identique.
C'est la substitution la plus sûre des trois.

**② Le rôle « serif » absorbe deux fonctions qui étaient distinctes.** Chaque
page opposait une famille de titrage à une famille de texte ; P-26 les réunit.
Sur Pandora, l'écart est faible : Marcellus et Spectral sont deux serifs, et
Literata se substitue à l'une comme à l'autre sans changer la nature de la page.

**③ Le point dur est nommément `rouges-et-blancs.html`, et il n'est pas
chromatique.** Son titrage était **Oswald**, une display **condensée**, posée
sur une ossature qui en dépend : barres letterbox, cadre scope 2.35:1, titres
en capitales étirées à l'horizontale. Literata 600 est large, ronde, de faible
contraste — l'inverse d'une condensée. *C'est là, et d'abord là, qu'il faut
regarder si la typographie unifiée « tient ».* La session ne peut pas le
trancher : c'est un jugement de proportion, et elle n'a pas de géométrie.

**④ Une conséquence non anticipée par la spec.** Les cartels de la fiche
technique servent d'**étiquettes de gabarit** — leur largeur participe de la
grille. Changer de monospace change leur chasse. Aucune prescription ne couvre
ce point ; il n'est pas grave, il est simplement à voir.

**⑤ Ce qui n'a PAS bougé, et c'est l'essentiel** : palette, couverture,
ossature, texte. La migration ne touche qu'aux familles. L'identité bespoke
appartient à l'œuvre (§6.1) et elle est intacte dans les trois pages.

### Ce que la session ne dit pas

Elle ne dit pas que la typographie unifiée est réussie, ni qu'elle échoue.
**Q-3 n'attend aucune décision d'AH** (spec §12) : c'est un constat de design,
et le constat est celui-ci — *le risque est réel, il est localisé, et il porte
sur une seule des trois pages.*

**À regarder en priorité** :
`films/rouges-et-blancs.html` — le titre en capitales, les barres letterbox,
et le rapport entre la hauteur du bloc-titre et le cadre scope.

---

## C-2 — Une carte seule « sonne-t-elle vide » ? *(réserve P-51)*

### L'instrument

`outils/observation-C2-carte-seule.html` — **page hors site**, liée par aucun
menu, jamais publiée. Elle montre côte à côte, sur le registre réel :

- **cas A** : l'objet en une réduit à **une carte seule** (l'unique Étude est
  retirée du tableau à la volée, ce qui prive la dernière publiée de sa variante) ;
- **cas B** : le **couple** champ / contrechamp, état de l'accueil au 22/07.

### Comportement vérifié (logique, pas géométrie)

| | cas A | cas B |
|---|---|---|
| Cartes rendues | **1** | 2 |
| Classe du bloc | `bloc-une` | `bloc-une couple` |
| Cartel | « Dernière analyse publiée » | « …— et son pendant » |
| Ligne de liaison | vide | « Même film, deux régimes » |

**P-51 se comporte comme écrite** : aucune entrée qui ne soit ni la dernière
publiée ni sa variante n'apparaît dans le bloc.

### Ce que la session observe

**① Le risque n'est probablement pas le vide, c'est l'étirement.** La grille
passe de deux colonnes à une seule : une carte seule occupe alors **toute la
largeur du bloc**, soit la pleine mesure de la page. Ce n'est pas une carte
dans un espace vide, c'est une carte étirée sur une mesure conçue pour deux.
Si le bloc « sonne » mal, le levier est la **grille**, pas P-51 — la
prescription peut rester telle quelle. *(Non vérifié par la mesure : pas de
géométrie. Déduit de la règle CSS `grid-template-columns`.)*

**② Et surtout — le cas A n'est pas hypothétique, il sera le cas normal.**
Aujourd'hui l'accueil affiche le couple, parce que `datePublication` n'existe
que sur les 3 entrées migrées et que la plus récente des trois est le
Contrechamp (18/07 23h45). **Après le rétro-remplissage de 065-5**, la dernière
publiée du corpus réel deviendra **`hitchcock-truffaut.html`** — ajoutée le
**21/07 à 23h38** (relevé git), une **Critique sans variante**.

> **Autrement dit : le cas que le prototype montre aujourd'hui n'est pas celui
> que le site montrera demain.** C'est le cas A qu'il faut juger, et c'est
> exactement pour cela que l'instrument existe.

Le corpus ne comptant qu'une Étude et le régime Scholar étant coûteux par
construction, le couple restera l'exception — ce que l'arbitrage Q-1 avait
anticipé en écartant l'option qui aurait figé Pandora à l'accueil.

---

## C-3 — Comptage mécanique du contraste AA *(P-39)*

**Outil** : `outils/controle-contraste.py` — Python stdlib, ASCII pur, sans
navigateur. L'arithmétique WCAG (luminance relative, rapport
`(L1+0,05)/(L2+0,05)`) n'exige aucun rendu. **Sortie intégrale** :
`outils/contraste-sortie.md`. **Aucune palette n'a été modifiée.**

### Pourquoi le comptage est donné en deux classes

La première version de l'outil appariait toute règle `color` au fond du `body`.
Elle annonçait **136 écarts sur 34 pages, dont 34 pages en échec** — avec des
ratios de **1,00** en série, c'est-à-dire du texte exactement de la couleur du
fond. Ce n'étaient pas des défauts de palette : c'étaient des **artefacts de
nesting**, une règle vivant dans un bloc à fond distinct. *Un comptage qui
aurait déclenché 33 arbitrages inutiles ne vaut rien.* L'outil a donc été
durci avant que le constat ne soit rendu.

| Classe | Définition | Nature |
|---|---|---|
| **E1 — certain** | la règle déclare `color` **et** un fond : le couple est celui que l'auteur a écrit | aucune inférence |
| **E2 — probable** | la règle ne déclare que `color`, et cette couleur échoue contre **tous** les fonds déclarés de la page | borne **basse** |

Ce qui passe sur au moins un fond déclaré n'est pas compté : **le comptage
sous-estime plutôt qu'il n'invente.**

### Résultat

| Mesure | Valeur |
|---|---|
| Pages analysées | **34** (33 analyses + l'accueil) |
| Couples texte/fond distincts examinés | 421 |
| **Écarts CERTAINS (E1)** | **23** |
| Écarts PROBABLES (E2) | 48 |
| **Pages portant au moins un écart CERTAIN** | **17 / 34** |
| Pages portant au moins un écart, toutes classes | 25 / 34 |
| Pages sans aucun écart | 9 |

### Cinq observations qui commandent les arbitrages

**① Tous les écarts ne sont pas des défauts.** Le pire ratio du corpus est
`1,00`, sur le sélecteur **`.redact`** — du texte caviardé, de la couleur exacte
de son fond. C'est un **effet voulu**. Une correction automatique le
détruirait. C'est l'illustration la plus nette de ce que P-39 demande : chaque
écart est un arbitrage, jamais une correction mécanique.

**② Les fautes se concentrent sur le mobilier, pas sur le texte courant.** Les
sélecteurs qui échouent sont `.provenance`, `.content-warning`,
`.avertissement`, `.cartel`, `.eyebrow`, `.back-link`, `header.dalle` — des
mentions secondaires en gris clair. Le corps des analyses passe presque partout.

**③ Le chrome v2 hérite lui-même d'un écart.** `index.html` porte un E1 :
`footer` en `#7a7a74` sur `#f1ede4` = **3,70**. Ce ton vient de la palette v1
(`--ink-muted`), reprise telle quelle par le prototype — et il est désormais
sur les **six** pages du menu, qui partagent ce pied de page. *Écart introduit
par héritage, non par le prototype ; signalé, non corrigé.*

**④ La page sombre est la plus propre du lot.** `rouges-et-blancs.html` :
**zéro écart**, E1 comme E2. Le préjugé selon lequel les palettes sombres
seraient les plus exposées ne tient pas ici — c'est `shutter-island.html`
(fond clair `#ece3ca`) qui en porte le plus, avec 3 écarts certains.

**⑤ Le diptyque Pandora en porte un, certain** : `.content-warning`,
`#e2d6bd` sur `#9b9e9c` = **1,88**, dans la page champ. Le contrechamp n'en a
aucun de certain. Les deux pages partageant la palette, l'écart tient au bloc,
pas au film.

### Ce qui reste dû

P-39 se vérifie « mécanisé (§9.2) », c'est-à-dire **au navigateur**, sur les
couples réellement empilés. Playwright n'est pas installé (BKL-069,
autorisation R4 distincte). Le présent comptage est **une borne, pas la
recette** : il nomme où regarder, il ne clôt pas P-39.

---

## Ce que la session n'a pas tranché — récapitulatif

| # | Point | À qui |
|---|---|---|
| 1 | ~~Q-3 — la typographie unifiée tient-elle sur `rouges-et-blancs` ?~~ | **TRANCHÉ — erratum 2** |
| 2 | ~~C-2 — le bloc de une à une seule carte~~ | **TRANCHÉ — erratum 2** |
| 3 | Chacun des 23 écarts E1 — corriger la palette ou documenter l'exception | AH, écart par écart |
| 4 | Le ton `--ink-muted` du pied de page, hérité et sous AA | AH |
| 5 | ~~La dégradation sans JavaScript, balisée PROVISOIRE~~ | **TRANCHÉ — voir erratum 1** |

---

## ERRATUM 2 — 22/07/2026 11h44 : C-1 et C-2 sont tranchés

Lignes 1 et 2 barrées et non effacées (charte, règle 5). **Gates d'AH
prononcés dans la fenêtre de la session, sur la maquette vivante**, après la
validation du prototype de 11h41.

**C-1 / Q-3 — « oui » : la typographie unifiée TIENT.** Y compris sur le point
dur que ce constat avait nommé : `films/rouges-et-blancs.html`, dont le titrage
était une display **condensée** (Oswald) posée sur une ossature **letterbox
scope 2.35:1**, et que remplace Literata 600 — large, ronde, de faible
contraste. Le risque de design ouvert depuis le 20/07 est levé **sur pièces**.

> **Conséquence pour 065-5** : le système typographique unique auto-hébergé est
> éprouvé, plus rien ne s'oppose à la substitution des **30 pages restantes**.
> *La session note, sans en tirer de conclusion : le verdict a porté sur les 3
> pages migrées ; les 30 autres n'ont pas été vues sous Literata.*

**C-2 — « non » : la carte seule ne sonne PAS vide.** La réserve de conception
du §3.2 est levée : **`P-51` s'applique telle qu'elle est écrite, sans
modification**. L'observation de la session — le risque n'était peut-être pas
le vide mais l'**étirement** d'une carte unique sur une grille conçue pour deux
— n'appelle donc aucune suite.

*Ce qui rendait ce verdict urgent : le cas jugé n'est pas théorique. C'est
celui que le site affichera dès le rétro-remplissage de `datePublication` en
065-5, la dernière publiée devenant `hitchcock-truffaut`, Critique sans
variante.*

**Q-3 était la dernière question ouverte de `SPEC-SITE-V2`** (§12) : la spec
n'en porte plus aucune. *L'inscrire dans la spec elle-même revient au greffe —
c'est hors du périmètre d'écriture de cette session.*

**Non couverts par ces deux gates**, et toujours ouverts : les **6 décisions de
spec** (ligne 3 du tableau de la note de fin) et les **23 arbitrages de
contraste AA** (lignes 3 et 4 ci-dessus).

---

## ERRATUM 1 — 22/07/2026 08h30

**La ligne 5 du tableau ci-dessus n'est plus vraie.** Elle est barrée et non
effacée : le raisonnement d'origine fait partie de la mémoire du projet
(charte, règle 5).

**Gate d'AH relayé dans la fenêtre du prototype, 22/07** — « go option (b)
pour la dégradation sans JS », relais de l'enregistrement de 08h24 :

> **Option (b)** — la liste complète du corpus est rendue **en dur dans le
> HTML** ; le JavaScript ne fait plus que la **filtrer**. Sans JS, on voit
> tout, simplement non filtrable.

**Ce que le prototype constatait est donc résolu, et par la racine.** Le repli
qui « tournait en rond » — renvoyer vers « Critiques », page dépendant du même
script — disparaît : il n'y a plus de repli à faire, puisqu'il n'y a plus rien
à remplacer. Les trois pages qui rendent le composant (`index`, `critiques`,
`etudes`) portent leur liste en HTML ordinaire ; le script révèle les commandes
de filtrage à l'amorçage, et se contente de filtrer ensuite.

**Implémentation et contrôle** : bloc généré par
`outils/genere-liste-statique.py` entre marqueurs, **jamais édité à la main**.
Le risque réel de ce dispositif est la **dérive entre deux gabarits** — celui
du script Python et celui de `corpus.js`. D'où le mode `--verifier`, qui
régénère en mémoire et compare au disque : *contrôle de recette à rejouer.*

**Vérifié au moteur** : les **33 `<li>`** du rendu JavaScript et ceux du HTML
statique sont **identiques balise à balise** (comparaison des `outerHTML`
normalisés, 0 divergence). Le lecteur sans JavaScript voit exactement la même
liste que le lecteur qui en a un.

*Frontière P-31 respectée telle qu'elle a été ratifiée le 21/07 : ce que la
règle proscrit est une transformation **au déploiement**, pas un fichier généré
avant commit, versionné et lisible tel quel. Le HTML publié se lit dans le
dépôt, et se sert sans étape intermédiaire.*

**Reste hors de cet erratum** : le point ② du gate enregistré à 08h24 — la
mécanique de recherche et de classement déléguée à ce mandat — **n'a pas été
relayé** dans la fenêtre du prototype. La session ne se l'attribue pas.
*(Relayé depuis, à 08h40 — voir la section suivante.)*

---

# La mécanique de recherche — choix rendu par la session

**Gate d'AH du 22/07** : « la mécanique de recherche et le classement sont à ta
main, choix documenté au constat ». C'est la **seule décision de design que ce
mandat rend lui-même** ; tout le reste est constat. Elle est donc écrite ici
avec ses motifs et ses mesures, pour être révocable en connaissance de cause.

## Décision 1 — Des JETONS, et non une sous-chaîne globale

**Ce qui existait** : la requête entière était cherchée comme une sous-chaîne
dans un champ concaténé (titre + réalisateur + année + genre + pays + décennie).

**Le défaut, vérifié** : cette forme **impose au lecteur l'ordre des mots**.
`loach drame` ne trouvait rien — les deux termes existent, mais pas côte à côte
et pas dans cet ordre. `annie woody` non plus.

**Retenu** : la requête est découpée en jetons sur les espaces, et **chaque
jeton doit se trouver quelque part** dans l'entrée (conjonction, ET). Chaque
jeton reste une **sous-chaîne** : `melv` trouve Melville — ce qui dispense
d'un analyseur morphologique du français qu'on n'aura pas, et qu'un site
statique n'a pas à embarquer.

**Mesuré** : `loach drame` et `drame loach` renvoient désormais **le même
résultat** (*Moi, Daniel Blake* et *The Old Oak*), dans le même ordre.

**Ce qui a été écarté** : le OU (une requête à deux mots ramènerait la moitié
du corpus) ; les opérateurs (`"` , `-`, `OR`) — une syntaxe que personne
n'apprendra sur un site de 33 films ; la recherche floue, qui ferait apparaître
des résultats que le lecteur n'a pas demandés sans qu'il comprenne pourquoi.

## Décision 2 — Aucun classement par pertinence

**Retenu** : les résultats **gardent l'ordre du catalogue**. Il n'y a pas de
score.

**Motif** : le filtre étant conjonctif, **toutes** les entrées retenues
satisfont **tous** les jetons — il n'existe pas de gradient à trier. Un
pseudo-score (« le titre vaut plus que le réalisateur ») ferait bouger les
lignes d'une manière que le lecteur ne peut pas prévoir, sur une liste qui,
une fois filtrée, tient presque toujours dans un écran. *Un classement se
justifie quand il y a trop de résultats pour les lire ; ce n'est pas le cas ici,
et ce ne le sera pas davantage à 500 films avec des facettes.*

## Décision 3 — L'ordre du catalogue est ALPHABÉTIQUE par titre

C'est le vrai changement, et il touche la page même sans recherche.

**Ce qui existait** : la liste sortait dans **l'ordre du registre**, c'est-à-dire
l'ordre où les analyses ont été ajoutées au fichier — *Annie Hall, The Old Oak,
Soudain l'été dernier, Soy Cuba…* Un ordre parfaitement arbitraire pour un
lecteur, et qui de surcroît **bouge à chaque publication**.

**Retenu** : alphabétique par titre, sur le titre **replié sans accent**.

**Motifs** : ① un index est un **catalogue** — on y cherche un titre, on ne le
parcourt pas comme un fil d'actualité ; ② la **nouveauté est déjà servie** par
l'objet en une, juste au-dessus : un corpus trié par date en ferait le doublon ;
③ l'ordre alphabétique est **stable** — publier une analyse insère une ligne,
sans déplacer les autres ; ④ argument décisif et pratique : `datePublication`
n'existe que sur **3 entrées sur 33**, un tri par date serait aujourd'hui du
bruit.

**Deux choix subordonnés, nommés pour être discutables** :

- **Le repli sans accent sert de clé de tri**, et non `localeCompare('fr')`.
  Motif technique dur : le HTML statique de l'option (b) est produit par un
  script Python, dont la bibliothèque standard **n'a pas de collation
  française**. Une clé repliée, elle, se reproduit à l'identique des deux côtés
  — et le contrôle de dérive le prouve à chaque exécution. *Effet : les accents
  sont ignorés au tri, ce qui est le comportement français attendu.*
- **Les articles initiaux ne sont pas escamotés.** *Le Doulos* se range à « L »,
  comme il s'écrit. Un catalogue de bibliothèque rangerait « Doulos, Le » ;
  c'est plus savant, mais cela demande une règle de plus, elle échoue sur les
  titres étrangers (*The Old Oak*), et elle surprend autant qu'elle aide.

## Mesures — P-41 est désormais VÉRIFIÉE, et non plus « non vérifiable »

Une mesure de **temps** ne demande aucune géométrie : elle est valide dans cet
environnement, contrairement à tout le reste. P-41 exige « moins de 100 ms sur
le corpus complet, et utilisable jusqu'à 500 entrées ».

| Requête | Corpus réel (33) | Jeu synthétique (500) |
|---|---|---|
| vide (rendu de toute la liste) | **0,38 ms** | **5,98 ms** |
| un jeton (`loach`) | **0,065 ms** | **0,87 ms** |
| deux jetons (`loach drame`) | **0,065 ms** | **0,89 ms** |
| terme accentué (`melodrame`) | **0,065 ms** | — |

*Protocole : moyenne de 20 passes (10 à 500 entrées), horloge `performance.now()`,
mesure du cycle complet frappe → filtrage → rendu du HTML de la liste.*

**Marge : le seuil de 100 ms n'est atteint à aucun moment — le cas le plus
lourd, le rendu des 500 entrées sans filtre, en consomme 6 %.** L'index de
recherche de chaque entrée est calculé **une fois à l'amorçage** et non à
chaque frappe : c'est ce qui tient le seuil quand le corpus grandira.

## Ce qui reste révocable

Aucune de ces trois décisions n'est structurante : elles vivent dans
`assets/corpus.js` et dans le gabarit jumeau `outils/genere-liste-statique.py`.
La seule contrainte à respecter en les révoquant est que **les deux gabarits
restent d'accord** — ce que `--verifier` contrôle. *Au rétrofit de 065-5, un
troisième gabarit entrera en scène : le skill. Il devra s'aligner sur les deux
autres, faute de quoi une publication réordonnera silencieusement la liste.*
