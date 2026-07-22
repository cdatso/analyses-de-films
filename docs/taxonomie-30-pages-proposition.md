# Table de taxonomie des 30 pages — PROPOSITION SOUMISE À AH

**ARRÊT n°1 du mandat BKL-065-5.** Session « Opus BKL-065-5 Migration »,
**22/07/2026 23h05** (horodatage instrumental).

> ⚠️ **Rien de ce tableau n'est écrit au registre.** C'est une proposition.
> Le gate attendu est « **go taxonomie** », amendements ligne à ligne bienvenus.
> Les champs mécaniques (`volet`, `datePublication`, `producteur`, `genreBase`)
> sont déjà posés et ne figurent pas ici — sauf les **deux `genreBase` que le
> script a refusé de deviner** (§4).

## 1. Pourquoi ces champs ne sont pas dérivables — mesuré trois fois

| Tentative | Résultat |
|---|---|
| Dériver `pays` du registre | **impossible** — le champ n'existe pas en v1 (diagnostic D-3) |
| Le lire dans la fiche technique des pages | **impossible** — aucune page ne porte le pays en champ structuré |
| Le lire dans la prose des analyses | **non fiable** — le balayage rend « Italie » sur `waterloo` (le film est italo-soviétique : vrai) *et* sur `raging-bull` (LaMotta est italo-américain : faux comme pays de production). Un mot présent n'est pas une donnée. |
| Dériver `technique` | **2 entrées sur 33** portent leur technique dans le texte libre (`(muet)`, `(N&B)`) |

**Conséquence** : les valeurs ci-dessous viennent de ma connaissance
filmographique, pas d'une opération sur les données du dépôt. C'est exactement
ce que le gate du 20/07 20h38 prévoit — travail de modèle **sous relecture**.

**Code de source**, porté par chaque valeur :
- **[C]** connaissance filmographique — à valider par ton œil ;
- **[P]** attesté explicitement par la page d'analyse elle-même ;
- **[D]** index Deleuze `Filmographie\Index-Deleuze-films.CSV` (BKL-062) ;
- **⚑** point de doute que je signale plutôt que de le lisser.

## 2. La table — 30 lignes

`pays` et `technique` sont des **listes** (vocabulaire fermé, P-09/P-10).

| # | slug | film | `pays` | `technique` |
|---|---|---|---|---|
| 1 | `annie-hall` | Allen, 1977 | Etats-Unis [C] | couleur [C] |
| 2 | `au-fil-de-leau` | Lang, 1950 — *House by the River* | Etats-Unis [C] | n&b [C] |
| 3 | `bienvenue-a-suburbicon` | Clooney, 2017 | Etats-Unis, Royaume-Uni [C] | couleur [C] |
| 4 | `hamlet` | Kozintsev, 1964 | Union sovietique [C] | n&b **[P]** |
| 5 | `hamnet` | Zhao, 2025 | Royaume-Uni, Etats-Unis [C] | couleur [C] |
| 6 | `hitchcock-truffaut` | Jones, 2015 | Etats-Unis, France [C] | couleur [C] ⚑ |
| 7 | `julie-en-12-chapitres` | Trier, 2021 | Norvege, France, Suede, Danemark [C] | couleur [C] |
| 8 | `la-chevauchee-fantastique` | Ford, 1939 | Etats-Unis [C] | n&b [C] |
| 9 | `la-mariee-etait-en-noir` | Truffaut, 1968 | France, Italie [C] | couleur [C] |
| 10 | `la-nuit-de-san-lorenzo` | Taviani, 1982 | Italie [C] | couleur [C] |
| 11 | `le-cheval-de-turin` | Tarr, 2011 | Hongrie, France, Allemagne, Suisse [C] ⚑ | n&b [C] |
| 12 | `le-doulos` | Melville, 1962 | France, Italie [C] | n&b [C] |
| 13 | `le-golem` | Duvivier, 1936 | France, Tchecoslovaquie [C] ⚑ | n&b [C] |
| 14 | `le-samourai` | Melville, 1967 | France, Italie [C] | couleur [C] |
| 15 | `les-deux-orphelines` | Griffith, 1921 | Etats-Unis [C] | muet, n&b **[P]** ⚑ |
| 16 | `manhattan` | Allen, 1979 | Etats-Unis [C] | n&b [C] |
| 17 | `moi-daniel-blake` | Loach, 2016 | Royaume-Uni, France, Belgique [C] | couleur [C] |
| 18 | `nouvelle-vague` | Linklater, 2025 | Etats-Unis, France [C] | n&b [C] |
| 19 | `persona` | Bergman, 1966 | Suede [C] | n&b [C] |
| 20 | `raging-bull` | Scorsese, 1980 | Etats-Unis [C] | n&b [C] ⚑ |
| 21 | `retour-a-seoul` | Chou, 2022 | France, Allemagne, Belgique, Coree du Sud [C] | couleur [C] |
| 22 | `rosetta` | Dardenne, 1999 | Belgique, France [C] | couleur [C] |
| 23 | `sans-filtre` | Ostlund, 2022 | Suede, Allemagne, France, Royaume-Uni [C] | couleur [C] |
| 24 | `shutter-island` | Scorsese, 2010 | Etats-Unis [C] | couleur [C] |
| 25 | `soudain-lete-dernier` | Mankiewicz, 1959 | Etats-Unis, Royaume-Uni [C] | n&b [C] |
| 26 | `soy-cuba` | Kalatozov, 1964 | Cuba, Union sovietique [C] | n&b [C] |
| 27 | `sud` | Akerman, 1999 | France, Belgique [C] | couleur [C] |
| 28 | `sur-la-route-domaha` | Webley, 2025 | Etats-Unis [C] | couleur [C] |
| 29 | `the-old-oak` | Loach, 2023 | Royaume-Uni, France, Belgique [C] | couleur [C] |
| 30 | `waterloo` | Bondartchouk, 1970 | Italie, Union sovietique [C] | couleur [C] |

### Les six doutes que je signale ⚑

| slug | ce dont je ne suis pas sûr |
|---|---|
| `hitchcock-truffaut` | documentaire **en couleur truffé d'archives en N&B**. `couleur` décrit le film, pas ce qu'on y voit le plus. Alternative : `couleur, n&b`. |
| `raging-bull` | **N&B avec les bobines familiales en 16 mm couleur**. Même question, tranchée dans l'autre sens par la critique : le film *est* un film en noir et blanc. Alternative : `n&b, couleur`. |
| `les-deux-orphelines` | muet **teinté/viré** à l'origine, souvent vu aujourd'hui en N&B pur. `muet, n&b` décrit la copie courante, pas la copie de 1921. |
| `le-cheval-de-turin` | co-production à cinq ou six partenaires selon les sources (les États-Unis y figurent parfois). J'ai retenu les quatre constants. |
| `le-golem` | production **franco-tchécoslovaque** tournée à Prague ; « Tchecoslovaquie » est un pays qui n'existe plus — à trancher : nom d'époque ou nom actuel ? |
| `hamlet` | l'URSS de 1964 : même question de nom d'époque. J'ai retenu `Union sovietique`, cohérent avec `rouges-et-blancs` déjà au registre. |

## 3. Ce que la table implique pour le vocabulaire fermé

`assets\vocabulaires.js` ne contient aujourd'hui que **4 pays** (les seules
valeurs des 3 entrées migrées). La table en demande **17** :

```
Allemagne · Belgique · Coree du Sud · Cuba · Danemark · Etats-Unis · France
Hongrie · Italie · Norvege · Royaume-Uni · Suede · Suisse · Tchecoslovaquie
Union sovietique
```
*(+ `Etats-Unis`, `Hongrie`, `Royaume-Uni`, `Union sovietique` déjà présents.)*

**P-12 fait de chaque ajout un acte délibéré, dans un commit propre.** Ces 13
ajouts iront donc dans **un commit à eux**, distinct de l'écriture du registre —
et seulement sur ton gate.

**Deux règles de nommage à arrêter, parce qu'elles vaudront pour tout le reste :**
1. **noms d'époque ou noms actuels** ? (`Union sovietique` / `Tchecoslovaquie`
   contre `Russie` / `Tchequie`). Je propose les **noms d'époque** : le pays de
   production est un fait daté, et `rouges-et-blancs` porte déjà
   `Union sovietique` ;
2. **sans accents**, comme les 4 valeurs existantes (`Etats-Unis`,
   `Union sovietique`) — cohérence avec l'existant, pas élégance typographique.

## 4. Les deux `genreBase` que le script a refusé de deviner

Le vocabulaire fermé n'a **pas de tête « noir »**, et « Film » n'en est pas une :
le mot ne nomme aucun genre. La session prototype l'avait déjà relevé sans le
trancher — c'est un arbitrage éditorial.

| slug | `genre` libre actuel | option (a) — mapper | option (b) — enrichir |
|---|---|---|---|
| `au-fil-de-leau` | « Film noir gothique » | `polar` | `noir` (nouveau terme) |
| `le-doulos` | « Film noir » | `polar` | `noir` |

**Ma recommandation : option (a), `polar`.** Motif : `le-samourai` porte déjà
« Polar / film noir » et a été classé `polar` mécaniquement — les trois films
tomberaient dans la même case, ce qui est le comportement attendu d'une facette.
Créer `noir` séparerait *Le Doulos* du *Samouraï*, deux Melville du même monde.

*L'option (b) se défend si tu tiens le film noir pour un genre distinct du
polar — c'est une position tenable en histoire du cinéma, et elle t'appartient.*

## 5. `courant` — ce que je propose de NE PAS remplir tout de suite

`courant` est **facultatif et non bloquant** (§4.2 de la spec). Le vocabulaire
n'en contient que deux termes (`romantisme noir`, `surrealisme`), et chaque
ajout est un acte P-12.

**Constat qui change la donne** : depuis le correctif P-13 de ce soir, une
facette renseignée sur moins de la moitié du corpus **ne s'affiche pas**. Un
`courant` posé sur 8 films sur 33 (24 %) serait donc **invisible** — du travail
d'arbitrage pour un champ que personne ne verrait.

**Je propose de le laisser vide et d'en faire une passe éditoriale ultérieure**,
avec le manifeste (BKL-038). Si tu préfères l'ouvrir maintenant, les rattachements
les moins discutables seraient :

| courant | films |
|---|---|
| naturalisme social | `rosetta`, `moi-daniel-blake`, `the-old-oak` |
| film noir | `au-fil-de-leau`, `le-doulos`, `le-samourai` |
| classicisme hollywoodien | `la-chevauchee-fantastique`, `soudain-lete-dernier` |
| modernisme | `persona`, `sud`, `le-cheval-de-turin` |

*Onze films sur 33 : 33 %. Toujours sous le seuil d'affichage.*

## 6. `deleuze` — 2 films sur 30, et un piège évité

Croisement mécanique du corpus avec l'index BKL-062 (694 occurrences,
400 films, **Cinéma 1 seul** — *Cinéma 2* a été reporté au second temps).

| slug | œuvre | pages | concepts |
|---|---|---|---|
| `persona` | Image-Mouvement | **142** et **149** | l'affect comme entité · l'icône · la priméité selon Peirce · **la limite du visage ou le néant : Bergman** · les composantes affectives du gros plan |
| `la-chevauchee-fantastique` | Image-Mouvement | **203** | de la situation à l'action : la secondéité · l'englobant et le duel · le rêve américain · **le western (Ford)** |

**Le piège** : l'index contient bien « **Le Golem** » — mais c'est celui de
**Paul Wegener (1920)**, cité trois fois, et non le **Duvivier de 1936** qui est
au corpus. Un rapprochement par titre seul aurait attribué à notre page une
référence deleuzienne qui ne la concerne pas. Même prudence sur
« Les Sept Samouraïs » (Kurosawa), sans rapport avec `le-samourai`.

**Vingt-huit films sur trente n'ont donc aucune référence**, et c'est un résultat,
pas un manque : Deleuze n'a pas écrit sur eux dans *L'Image-Mouvement*. Le
croisement avec *Cinéma 2* reste dû à un mandat ultérieur (BKL-062, second temps)
et pourra enrichir la facette sans rien invalider ici.

## 7. Ce que j'écrirai au registre sur ton gate

1. les 13 termes de `pays` ajoutés à `vocabulaires.js` — **commit propre, P-12** ;
2. `pays` et `technique` sur les 30 entrées — **commit de registre** ;
3. les 2 `genreBase` arbitrés ;
4. `deleuze` sur `persona` et `la-chevauchee-fantastique` ;
5. `courant` : rien, sauf gate contraire ;
6. puis, **et seulement alors**, le retrait du champ `genre` déprécié (P-50) —
   il reste la source de tout ce qui précède jusqu'à ce moment-là.
