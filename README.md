# Analyses de films

Critiques et études de cinéma sourcées — contexte, mise en scène, thèmes et
postérité, une œuvre à la fois. Site statique publié sur GitHub Pages et servi
sous le domaine [www.cdatso.be/analyses-de-films](https://www.cdatso.be/analyses-de-films/).

## Ce que c'est

Un site d'analyses cinématographiques en français, avec un arbre anglais pour
les pages de présentation. Chaque analyse est un article long, structuré et
accompagné d'une bibliographie numérotée ; chaque page a son identité visuelle
propre, dérivée du film.

Le site est écrit par une équipe où l'intelligence artificielle est un ensemble
de capacités spécialisées opérant **sous mandat et sous responsabilité
humaine** — pas un collaborateur artificiel autonome. Le [manifeste](manifeste.html)
expose cette position ; [comment ça marche](comment-ca-marche.html) décrit le
cycle réel de production (mandat, contrôles, audit, publication) ; la
[carte des activités](carte-des-activites.html) en donne l'état, régénéré à
partir du dépôt.

## Organisation du dépôt

| Chemin | Rôle |
|---|---|
| `index.html`, `critiques.html`, `etudes.html` | pages d'entrée et listes (générées à partir du registre) |
| `films/` | une page par analyse |
| `en/` | arbre anglais des pages de présentation |
| `assets/` | feuilles de style, polices, affiches, `films-data.js` (le registre des analyses) |
| `docs/` | journaux internes (analyses, recherche d'images, erreurs) |
| `outils/` | scripts de génération et de contrôle (Python, bibliothèque standard) |
| `outils/hooks/` | hook `pre-push` : batterie de contrôles bloquante avant toute publication |
| `sitemap.xml` | généré, jamais édité à la main |

## Contrat de qualité

Aucune page ne se publie sans passer une batterie de contrôles, jouée par le
hook `pre-push` : vocabulaires fermés du registre, listes statiques sans
dérive, poids des affiches, contraste des couleurs (écarts certains gatés
contre une base de référence). Le détail des règles vit dans une spécification
de site interne ; ce qui est observable ici, ce sont les outils qui les
appliquent.

Le site ne charge aucune ressource tierce et n'emploie ni suivi ni analytique.

## Licences

Répartition détaillée dans [`LICENSE.md`](LICENSE.md) :

- **textes** (analyses, pages, manifeste) : CC BY-NC-SA 4.0 ;
- **code du site** (HTML, CSS, scripts) : EUPL 1.2 ;
- **données du registre** : CC BY 4.0 ;
- **visuels des œuvres** (affiches, photogrammes) : exclus de toute licence —
  propriété de leurs ayants droit, reproduits au titre de la citation critique.

## Contact

Une [page de demande](demander-une-analyse.html) permet de proposer un film ;
la présentation de l'équipe est sur [qui sommes-nous](qui-sommes-nous.html).
