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

## Incidents techniques du pipeline

| Date | Incident | Détail | Résolution | À retenir |
|---|---|---|---|---|
| 5 juil. 2026 | Échec du déploiement GitHub Pages (commit 5a736dd) | Build Jekyll OK, étape « Deploy to GitHub Pages » en échec ; relance du job restée en file > 10 min | `POST /repos/cdatso/analyses-de-films/pages/builds` (build frais via API) → construit en ~30 s | Premier réflexe en cas d'échec de déploiement ; intégré à la skill (étape 10) |
