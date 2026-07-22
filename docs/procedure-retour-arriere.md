# Procédure de retour arrière de la bascule v2 — écrite ET éprouvée

**Item** : BKL-065-5 (migration & clôture de Phase II) · **Prescription** : **P-48**
(« la procédure de retour arrière est écrite ET éprouvée sur la branche locale avant
la bascule ») · **Garantie ② de l'amendement 1 au mandat du 22/07/2026**.

**Rédigé et éprouvé le 22/07/2026**, session « Opus BKL-065-5 Migration ». Ancres
instrumentales : session ouverte à **18h46:04** (`Get-Date`), essai à blanc exécuté
puis tag `v1-finale` posé à **19h53:07** (horodatage `git` du tag, dans la foulée de
l'essai).

> **Motif** (P-48) : *une procédure de secours jamais exécutée est une intention,
> pas un filet.* Ce document n'est pas une note d'intention : la séquence ci-dessous
> a été **exécutée à blanc**, et la preuve d'identité des arbres est collée au §3.

---

## 1. Ce que la procédure restaure, et ce qu'elle ne restaure pas

**Restauré** : l'intégralité de l'état publié du site v1 — le retour arrière
reconstruit un arbre **identique au bit près** à celui de `main` avant la bascule
(preuve au §3).

**Non restauré** : le temps pendant lequel un défaut a été **public** (§10.6 de la
spec). Un lien cassé a pu être suivi, indexé ou cité. C'est la raison d'être du
contrôle un-par-un des 34 URLs et des critères de fallback prédéfinis (§4).

**Point de vigilance** : la republication par GitHub Pages **n'est pas instantanée**.
Donnée de référence mesurée : Pages a servi le push du 21/07 en **~60 s** ; le retour
v1 est donc attendu **en 2 à 4 minutes, borne haute 5**. Un site encore en v2 90
secondes après le push du revert n'est **pas** un échec du retour arrière.

---

## 2. La commande de fallback — à coller telle quelle

> ⚠️ **On ne compose pas une commande d'urgence en situation d'urgence.** Les deux
> lignes ci-dessous sont la totalité du geste. `<SHA-DU-MERGE>` est le seul élément
> variable : il est relevé et **inscrit en toutes lettres dans le rapport de
> pré-bascule** au moment du merge, avant même que le push ne soit fait.

```bash
git -C "C:/Users/cdats/Claude/Projects/analyses-de-films" revert -m 1 <SHA-DU-MERGE> --no-edit
git -C "C:/Users/cdats/Claude/Projects/analyses-de-films" push origin main
```

**Deuxième filet, indépendant du premier** — le tag `v1-finale` :

```bash
git -C "C:/Users/cdats/Claude/Projects/analyses-de-films" push origin 0b0f47698177476e1d59501ab9a61d9906cca316:main --force-with-lease
```

*Le SHA est écrit en toutes lettres à dessein : c'est le commit sur lequel pointe le
tag `v1-finale` (posé et poussé le 22/07 à 19h53:07 sur autorisation d'AH « go, pousse
le tag aussi »), dernier commit du site v1 — une commande d'urgence ne doit dépendre d'aucune résolution de nom. Cette seconde forme est **plus brutale** —
elle réécrit l'historique de `main` — et n'est à employer que si le revert échoue.
La forme par revert est la voie normale : elle est additive, auditable, et
reversible à son tour.*

---

## 3. La preuve — essai à blanc du 22/07/2026, achevé à 19h53

Exécuté sur une **branche jetable locale** (`essai-retour-arriere`), jamais poussée,
supprimée après l'essai. `origin/main` est resté à `0b0f476` du premier au dernier
geste.

| # | Geste | Résultat constaté |
|---|---|---|
| 1 | `git branch essai-retour-arriere main` puis `checkout` | HEAD sur `0b0f476` |
| 2 | `git merge --no-ff v2-proto` | merge `0b1ba5f` — **82 fichiers, +22 555 / −197 lignes** ; `git diff HEAD v2-proto` = **0 fichier** (l'arbre du merge est bien celui de v2-proto) |
| 3 | `git revert -m 1 0b1ba5f --no-edit` | revert `08409cc` |
| 4 | **Contrôle d'identité** | `git diff --name-only main HEAD` = **0 fichier** |
| 5 | **Contrôle au hash** | arbre `main` = `c3873b0fc63d76e0fa119e40145e18a45afe956a` · arbre après revert = `c3873b0fc63d76e0fa119e40145e18a45afe956a` — **IDENTIQUES** |
| 6 | Nettoyage | branche jetable supprimée ; `main` toujours à `0b0f476` |

**Verdict : le retour arrière restaure l'état antérieur du site, prouvé au hash de
l'arbre, et non par ressemblance.**

---

## 4. Critères de déclenchement — aucun jugement à chaud

Garantie ④ de l'amendement 1. Ces critères sont **prédéfinis** : en situation, on ne
délibère pas, on constate et on applique.

**FALLBACK IMMÉDIAT**, sans arbitrage :
- tout **404 / 500** sur l'un des 34 URLs de l'annexe A du jour ;
- **CSS ou fontes non servis** (page nue, typographie de repli) ;
- **rendu cassé** sur une page-échantillon.

**PAS de fallback** — consigné, arbitré par AH à froid : tout autre défaut mineur
(écart de contraste résiduel, coquille, alignement).

Le diagnostic se fait **ensuite**, à froid, sur `v2-proto`. Jamais pendant.

---

## 5. Après un fallback

1. vérifier le retour effectif des 34 URLs en v1 (les mêmes sondes, mêmes URLs) ;
2. consigner au CHANGELOG l'heure du push de bascule, l'heure du constat, l'heure du
   push de revert, et le critère déclencheur — **factuellement** ;
3. le diagnostic et la reprise repartent de `v2-proto`, qui n'a pas bougé : le revert
   ne touche que `main`.
