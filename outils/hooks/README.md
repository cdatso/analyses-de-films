# outils/hooks/ -- hook pre-push (RUN-001)

Un hook git `pre-push` versionne dans le depot, qui rejoue une batterie de
controle avant tout push vers `main`. Decision RUN-001 (revue S3 du
31/07/2026, option B de `PROPOSITION-2026-07-29-CI-PUBLICATION.md`).

## Ce qu'il fait, et ce qu'il ne fait pas

- Il ne regarde QUE les pushes vers `refs/heads/main`. Un push vers
  `staging` (ou toute autre branche) sort immediatement, sans rien lire ni
  afficher -- les routines nocturnes headless ne sont jamais concernees.
- Avant de lancer la batterie sur un push vers main, il exige un arbre de
  travail propre (`git status --porcelain` vide). Les scripts de controle
  lisent les fichiers du disque, pas l'objet git du commit pousse : un
  arbre sale controlerait autre chose que ce qui part reellement en
  production.
- Il ne modifie AUCUN fichier du depot (tous les scripts tournent en mode
  lecture seule : `--strict`, `--verifier`, `--simuler`).
- Il ne touche pas aux scripts de controle existants dans `outils\` : s'ils
  revelent un defaut, c'est signale, jamais corrige a la volee.

## Activation (geste separe, PAS fait par ce depot de fichiers)

```
git config core.hooksPath outils/hooks
```

A executer une fois par clone/poste, sur go d'AH ou du greffe apres
validation. Sans cette commande, le hook existe dans le depot mais n'est
pas actif.

Pour revenir au comportement par defaut de git (`.git/hooks/`) :

```
git config --unset core.hooksPath
```

## Batterie jouee (dans l'ordre, sur push vers main uniquement)

1. `controle-vocabulaires.py --strict` -- axes fermes du registre (P-10).
2. `genere-liste-statique.py --verifier` -- pas de derive entre le HTML en
   dur et le gabarit qui l'a produit.
3. `recompresse-affiches.py --seuil 300 --simuler` -- aucune affiche
   au-dessus de 300 Ko (P-36), verifie sans rien reecrire.
4. `controle-contraste.py` -- gate uniquement sur les ecarts CERTAINS (E1,
   couple couleur/fond ecrit dans la meme regle). Les ecarts PROBABLES
   (E2, bornes basses) restent affiches dans le rapport mais ne bloquent
   pas le push -- coherent avec la doctrine du script lui-meme (sous-estimer
   plutot qu'inventer).

`controle-glyphes.py` est volontairement EXCLU : il ne controle pas les
pages du site (il le dit dans sa propre docstring) et depend du reseau
(telechargement de fontes) -- hors perimetre d'un gate joue a chaque push.

Echec de n'importe quel controle -> push refuse, avec le detail (quel
controle, quel fichier/quelle valeur) imprime par le script lui-meme.

## Si python est absent ou casse sur le poste

Le hook laisse alors le push vers main PASSER, avec un avertissement fort
en sortie d'erreur -- un poste mal configure ne doit pas bloquer totalement
une publication (arbitrage AH du 31/07/2026). Corrige l'environnement
avant la prochaine publication : aucun controle n'aura ete rejoue.

## Contournement exceptionnel

```
git push --no-verify
```

Le gate ne s'interdit jamais techniquement -- doctrine gates, pas verrous
(mandat RUN-001, point 5). C'est un geste EXCEPTIONNEL, a CONSIGNER
(CHANGELOG), jamais une pratique de routine.
