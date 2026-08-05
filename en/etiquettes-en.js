/* Table d'étiquettes ANGLAISES — socle i18n, BKL-CIN-085 lot L1.
 *
 * ⚠️ POSÉE, NON CÂBLÉE. Sous l'option B (gate AH du 05/08/2026, Q-1), aucune
 * liste EN n'est générée et aucune analyse n'est traduite : ce fichier n'est
 * lu par AUCUNE page aujourd'hui. Il est acté maintenant parce que c'est
 * précisément le travail qui, non fait, transformerait une montée en charge
 * ultérieure (options A ou C) en refonte — §5.2 point 4 de l'analyse.
 *
 * CE QUI FONDE CE FICHIER, et qui est l'actif le plus précieux du dossier :
 * les vocabulaires fermés du site séparent DÉJÀ l'identifiant ASCII de son
 * étiquette d'affichage (`comedie`, `Etats-Unis`… sont des CLÉS, jamais des
 * libellés). Ajouter une langue ne coûte donc qu'une table de plus, indexée
 * sur les MÊMES identifiants.
 *
 * CONSÉQUENCE DE GOUVERNANCE, à ne pas perdre de vue :
 *   — aucune valeur n'est ajoutée à `assets/vocabulaires.js` ; ce fichier ne
 *     déclenche donc PAS P-12 (l'ajout d'un terme reste un acte délibéré et
 *     commité à part) ;
 *   — P-10 continue de porter sur les identifiants, jamais sur les libellés :
 *     traduire une étiquette ne peut pas bloquer une publication ;
 *   — la table FR de référence vit en DEUX exemplaires qui doivent rester
 *     identiques (`assets/corpus.js` et `outils/genere-liste-statique.py`,
 *     dérive contrôlée au hook par `--verifier`). CE FICHIER N'ENTRE PAS
 *     dans ce couple : il ne duplique rien tant qu'aucune liste EN n'est
 *     générée. Le jour où une liste EN le serait, la question Q-6 — ajournée
 *     le 05/08, non close — se rouvre ENTIÈREMENT, et la résorption de la
 *     duplication FR passe AVANT l'ajout de la seconde langue.
 *
 * VARIANTE D'ANGLAIS : britannique (déclarée au socle, cohérente avec un site
 * belge et avec la prescription de ponctuation P-60). D'où « Colour ».
 *
 * Toute clé absente d'ici se rend, comme en français, par sa propre valeur
 * avec l'initiale en capitale (fonction `etiquette` de corpus.js).
 */

var ETIQUETTES_EN = {

  /* Volet — arbitrage AH du 05/08/2026 (élicitation du mandat (b), question
     D). « Critique » est un substantif anglais qui signifie exactement ce que
     le site produit — une analyse critique détaillée — et n'emporte pas la
     promesse de VERDICT que « review » porte dans l'écriture de cinéma
     anglophone, que le §5.7 de la spec récuse expressément. Le faux ami
     signalé à l'annexe 8 de l'analyse visait « criticism » (la discipline),
     jamais « critique » (la pièce). Les IDENTIFIANTS, eux, restent
     `critique` / `etude`. */
  volet: {
    critique: 'Critiques',
    etude: 'Studies'
  },

  /* Genre de base. Deux libellés où les taxonomies française et anglophone
     ne se recouvrent pas exactement, et où le choix est donc un choix :
       — `fantastique` : le français range ici le surnaturel (Le Golem) ; le
         mot anglais « fantastic » nomme un MODE critique (Todorov), pas un
         rayon. « Fantasy » est le terme de catalogue, retenu à ce titre.
       — `polar` : rendu « Crime », et non « Thriller » — le site tient les
         deux valeurs pour distinctes et les emploie distinctement. */
  genreBase: {
    'comedie': 'Comedy',
    'documentaire': 'Documentary',
    'drame': 'Drama',
    'fantastique': 'Fantasy',
    'fresque': 'Historical epic',
    'gothique': 'Gothic',
    'melodrame': 'Melodrama',
    'peplum': 'Peplum',
    'polar': 'Crime',
    'science-fiction': 'Science fiction',
    'thriller': 'Thriller',
    'tragedie': 'Tragedy',
    'western': 'Western'
  },

  /* Attributs techniques. Liste fermée arrêtée par la spec (§4.2). */
  technique: {
    'muet': 'Silent',
    'n&b': 'B&W',
    'couleur': 'Colour'
  },

  /* Pays. Les identifiants sont des chaînes ASCII non accentuées ; les
     libellés anglais sont les formes courantes d'usage, jamais les formes
     protocolaires. « Union sovietique » garde son nom historique : le corpus
     porte des films de 1964 et 1967, pas de la Russie d'aujourd'hui. */
  pays: {
    'Allemagne': 'Germany',
    'Belgique': 'Belgium',
    'Coree du Sud': 'South Korea',
    'Cuba': 'Cuba',
    'Danemark': 'Denmark',
    'Etats-Unis': 'United States',
    'France': 'France',
    'Hong Kong': 'Hong Kong',
    'Hongrie': 'Hungary',
    'Italie': 'Italy',
    'Japon': 'Japan',
    'Norvege': 'Norway',
    'Royaume-Uni': 'United Kingdom',
    'Suede': 'Sweden',
    'Suisse': 'Switzerland',
    'Tchecoslovaquie': 'Czechoslovakia',
    'Union sovietique': 'Soviet Union'
  },

  /* Courant — axe d'enrichissement éditorial, non bloquant (§4.2). */
  courant: {
    'neo-noir': 'Neo-noir',
    'neorealisme': 'Neorealism',
    'realisme magique': 'Magical realism',
    'romantisme noir': 'Dark Romanticism',
    'surrealisme': 'Surrealism'
  }
};

/* Noms des AXES eux-mêmes (titres de facettes). Indexés sur les clés
   employées par `Corpus.monte` dans assets/corpus.js. `decennie` est dérivé
   de `year` et n'existe pas au registre : sa clé est néanmoins celle-ci. */
var AXES_EN = {
  volet: 'Section',
  genreBase: 'Genre',
  pays: 'Country',
  technique: 'Format',
  decennie: 'Decade',
  courant: 'Movement',
  director: 'Director'
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ETIQUETTES_EN: ETIQUETTES_EN, AXES_EN: AXES_EN };
}
