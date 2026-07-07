# Journal des erreurs — accès aux sources et incidents de pipeline

Suivi interne des ressources documentaires inaccessibles pendant la recherche (403, paywall,
certificat, indisponibilité) et des incidents techniques du pipeline. Objectif : permettre une
récupération manuelle des sources pertinentes (l'utilisateur peut y avoir accès de son côté)
et garder la trace des pannes pour améliorer le processus.

Conventions :
- **Intérêt** : Fort (source de premier plan pour l'analyse, à récupérer si possible) /
  Moyen (utile mais couverte par d'autres sources) / Faible.
- **Statut** : 🔴 non récupérée · 🟡 partiellement couverte par une autre source · 🟢 récupérée
  (préciser comment) · ⚪ abandonnée.
- Une ligne par ressource ; les incidents techniques (déploiement, outils) vont dans la
  seconde table.

*Dernière mise à jour : 6 juillet 2026*

---

## Sources inaccessibles

| Date | Film | Ressource | URL | Erreur | Intérêt | Statut |
|---|---|---|---|---|---|---|
| 5 juil. 2026 | Au fil de l'eau (1950) | DVDClassik — analyse et critique | https://www.dvdclassik.com/critique/au-fil-de-l-eau-lang | HTTP 403 (blocage robot) | Fort — analyse française de référence | 🟡 couverte par Revus & Corrigés et Festival Lumière |
| 5 juil. 2026 | Au fil de l'eau (1950) | Slant Magazine — review | https://www.slantmagazine.com/film/house-by-the-river/ | HTTP 403 (blocage robot) | Moyen | 🟡 citée via extraits de recherche uniquement |
| 5 juil. 2026 | Raging Bull (1980) | RogerEbert.com — Great Movies | https://www.rogerebert.com/reviews/great-movie-raging-bull-1980 | HTTP 403 (blocage robot) | Fort — texte canonique d'Ebert | 🔴 non récupérée (analyse rédigée sans) |
| 5 juil. 2026 | Le Cheval de Turin (2011) | Critikat — critique | https://www.critikat.com/actualite-cine/critique/le-cheval-de-turin/ | Erreur certificat SSL (« unable to get local issuer certificate ») | Fort — critique française de fond | 🟡 couverte par Silence…Action ! et Persée (non consulté) |
| 6 juil. 2026 | La mariée était en noir (1968) | DVDClassik — analyse et critique | https://www.dvdclassik.com/critique/la-mariee-etait-en-noir-truffaut | HTTP 403 (blocage robot, récurrent sur ce domaine) | Fort — analyse française de référence | 🟡 couverte par Wikipédia fr + CinéDweller + Libre Critique |
| 6 juil. 2026 | Manhattan (1979) | American Society of Cinematographers — « Black-and-White Romantic Realism » | https://theasc.com/articles/manhattan-black-and-white-romantic-realism | HTTP 403 (blocage robot) | Fort — analyse technique de la photo de Gordon Willis | 🔴 non récupérée (citée en référence, non consultée) |
| 6 juil. 2026 | Retour à Séoul (2022) | Festival de Cannes — « Retour à Séoul, le regard de Davy Chou » | https://www.festival-cannes.com/fr/75-editions/retrospective/2022/actualites/articles/retour-a-seoul-le-regard-de-davy-chou | HTTP 404 (page retirée) | Moyen — propos du réalisateur | 🟡 couverte par la presse française |
| 6-7 juil. 2026 (routine nocturne) | Le Doulos (1962) | DVDClassik — analyse et critique | https://www.dvdclassik.com/critique/le-doulos-melville | HTTP 403 (blocage robot, récurrent sur ce domaine) | Fort — analyse française de référence | 🟡 couverte par avoir-alire.com et Mon Cinéma à Moi |
| 6-7 juil. 2026 (routine nocturne) | Le Doulos (1962) | Criterion Collection — fiche/essai du film | https://www.criterion.com/films/759-le-doulos | HTTP 403 (blocage robot) | Fort — essai critique de référence | 🔴 non récupérée (analyse rédigée sans) |
| 6-7 juil. 2026 (routine nocturne) | Le Doulos (1962) | Slant Magazine — review | https://www.slantmagazine.com/film/le-doulos/ | HTTP 403 (blocage robot) | Moyen | 🟡 couverte par Wikipedia (EN) et La Cinémathèque française |

## Incidents techniques du pipeline

| Date | Incident | Détail | Résolution | À retenir |
|---|---|---|---|---|
| 5 juil. 2026 | Échec du déploiement GitHub Pages (commit 5a736dd) | Build Jekyll OK, étape « Deploy to GitHub Pages » en échec ; relance du job restée en file > 10 min | `POST /repos/cdatso/analyses-de-films/pages/builds` (build frais via API) → construit en ~30 s | Premier réflexe en cas d'échec de déploiement ; intégré à la skill (étape 10) |
| 6 juil. 2026 | Pipeline Pages complètement coincé (commit 46d8857, merge du lot de 10) | Build Jekyll OK, deploy en échec ; relances zombies INANNULABLES (HTTP 409 « Cannot cancel a workflow re-run that has not yet queued », y compris via `force-cancel` et l'UI) ; build API bloqué en « building » ; état du site : `errored` (l'ancienne version restait servie) | Réinitialisation de la source Pages via API : `PUT /pages` source → `staging` (contenu identique) + build frais → débloqué en ~40 s, site à jour ; puis `PUT /pages` source → `main` + build frais. Vérif finale : 12/12 pages en 200, registre servi = 24 films | Remède de niveau 2 (= le « Pages source reset » de l'incident du 2 juil.) ; runs zombies non purgés immédiatement côté GitHub : cosmétique, se résorbe seul. Intégré à la skill (étape 10) |
