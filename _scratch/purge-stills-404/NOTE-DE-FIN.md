# NOTE DE FIN — Purge des 14 requêtes 404 `assets/stills` (7 pages v1)

**Session** : « Sonnet Purge Stills 404 » — 27/07/2026, 07h19 à 07h31 (Get-Date,
instrumental).
**Mandat** : `claude-config\mandats\MANDAT-2026-07-27-PURGE-STILLS-404-sonnet.md`
(BKL-003, GATE-AH « standup axe A » point ②).

## Statut
CLOS. Merge `main` fait, push fait, contrôle post-publication vert sur les 7
pages.

## Diff chiffré
Branche `purge-stills-404` → `main`, merge `08c42c7` (fast-forward refusé,
`--no-ff`), commit de fusion `GATE-AH:`.

| Fichier | Suppressions | Ajouts |
|---|---|---|
| `assets/style.css` | 14 | 0 |
| `films/annie-hall.html` | 12 | 0 |
| `films/hamnet.html` | 24 | 0 |
| `films/shutter-island.html` | 24 | 0 |
| `films/soudain-lete-dernier.html` | 24 | 0 |
| `films/soy-cuba.html` | 24 | 0 |
| `films/sud.html` | 24 | 0 |
| `films/the-old-oak.html` | 24 | 0 |
| **Total (8 fichiers)** | **170** | **0** |

Retiré par page : le bloc `<div class="stills-row">` (2 `<img>`) ; le script
inline `hideBrokenImg` (ne servait qu'à ce bloc, vérifié par recherche
exhaustive) ; la règle CSS `.stills-row`/`.stills-row img` (globale dans
`assets/style.css` + copie inline locale dans 6 des 7 pages — `annie-hall.html`
n'en avait pas). Aucune ligne de contenu visible modifiée. Un artefact de
double ligne vide (retrait du bloc `<script>`) a été détecté et corrigé avant
remise pour revenir au nombre de lignes vides identique à `main` (contrôle
négatif à l'octet, texte hors blocs retirés = identique).

## Contrôles exécutés
- `assets/stills` / `stills-row` / `hideBrokenImg` : 0 occurrence sur
  `films/`, `assets/`, `index.html` (avant ET après merge).
- 7 pages : 13 à 47 Ko (plafond mandat : 60 Ko).
- Rendu local (page témoin `annie-hall.html`, `file://`) : section « Mise en
  scène et procédés » intacte, 0 requête réseau vers `stills`.
- Post-publication (les 7 pages, site live `cdatso.github.io/analyses-de-films`) :
  build GitHub Pages attendu jusqu'à statut `built`, puis `curl` sur chacune
  des 7 URLs → 0 occurrence `stills` dans le HTML servi.

## Ce qui n'a PAS été fait
Rien — le mandat est intégralement exécuté (retrait + build mort + merge +
push + contrôle post-publication).

## CALIBRE (R-012)
Modèle déclaré au mandat : **Sonnet**. Calibre sous lequel je crois avoir
travaillé de bout en bout : **Sonnet 5** (`claude-sonnet-5`). Aucun moyen de
détecter une bascule automatique côté agent — à recouper avec l'interface
d'AH ; un écart se consigne.

## Routage des suites
Aucun reliquat. Tout est fini : mandat clos, rien à router.

| Reliquat | Fichier concerné | Repreneur | Texte ou critère prêt ? |
|---|---|---|---|
| — | — | — | (néant) |

---
Cette fenêtre ne reçoit plus ni mandat, ni gate, ni question.
Tout gate futur concernant mes artefacts passe par une NOUVELLE session
mandatée ou par le greffe. Les autorisations d'écriture de mon mandat §8
sont ÉTEINTES.
