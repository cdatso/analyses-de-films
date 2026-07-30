/* Vocabulaires contrôlés du registre — SPEC-SITE-V2 §4.3, prescription P-09.
 *
 * Fichier VERSIONNÉ et DÉDIÉ : c'est lui qui tient le mécanisme anti-dérive.
 * Trois règles solidaires y sont attachées :
 *   P-10 — toute valeur d'un axe fermé absente d'ici EMPÊCHE la publication
 *          (contrôle mécanique : outils/controle-vocabulaires.py) ;
 *   P-11 — le skill de production choisit dans ces listes et n'invente jamais ;
 *   P-12 — ajouter un terme est un ACTE DÉLIBÉRÉ, dans un commit propre,
 *          jamais mêlé à la publication d'une analyse.
 *
 * ⚠️ ÉTAT PROVISOIRE — prototype BKL-065-3.
 * `genreBase` est dérivé MÉCANIQUEMENT de la tête des 25 valeurs libres du
 * champ `genre` déprécié (P-50) : 11 têtes distinctes pour 33 entrées, ce qui
 * mesure exactement le diagnostic D-4. La liste ci-dessous n'est donc pas une
 * taxonomie arrêtée : sa fixation est un acte délibéré de BKL-065-5, sous gate
 * d'AH. Deux points relevés et NON tranchés par cette session :
 *   — « Film » (2 occurrences) est une tête dégénérée : « Film noir », « Film
 *     de guerre » — le mot ne nomme aucun genre. Il n'entre pas dans la liste ;
 *     les deux entrées concernées seront reclassées au rétrofit.
 *   — « Fresque », « Tragédie », « Polar » sont conservés tels quels : les
 *     fondre dans « Drame » ou « Policier » serait un arbitrage éditorial,
 *     qui n'appartient pas à un prototype.
 *
 * AJOUT DU 26/07/2026 (GATE AH « ajoute science-fiction, neo-noir et Hong Kong
 * au vocabulaire ») — escalade P-12 ouverte par la session one-shot Blade
 * Runner : aucune des dix valeurs de `genreBase` ne nommait le film, et la
 * coproduction hongkongaise (Shaw Brothers) n'avait pas son pays. Trois
 * termes inscrits, dans un commit propre distinct de la publication de la
 * fiche, conformement a P-12 :
 *   — `genreBase` : 'science-fiction', 'neo-noir' ;
 *   — `pays`      : 'Hong Kong'.
 * Orthographe NORMALISEE en ASCII non accentue, comme les 26 valeurs deja
 * presentes ('comedie', 'melodrame', 'Coree du Sud', 'Norvege') : le controle
 * P-10 est litteral. Le gate porte sur les TERMES, pas sur la fixation de la
 * liste, qui reste due a BKL-065-5.
 *
 * `pays` et `courant` ne sont pas dérivables (le pays n'est nulle part un champ,
 * diagnostic D-3) : la liste s'ouvre ici sur les seules valeurs des 3 entrées
 * migrées, renseignées par travail de modèle et DUES À LA RELECTURE D'AH
 * (gate du 20/07 20h38).
 */

const VOCABULAIRES = {

  /* Le volet est un attribut éditorial, jamais un chemin (P-01, P-03). */
  volet: ['critique', 'etude'],

  /* Dérivé mécaniquement des têtes de `genre` (voir en-tête). */
  genreBase: [
    'comedie',
    'documentaire',
    'drame',
    'fantastique',
    'fresque',
    'gothique',
    'melodrame',
    'peplum',
    'polar',
    'science-fiction',
    'thriller',
    'tragedie',
    'western'
  ],
  /* AJOUT DU 30/07/2026 (GATE AH « ajoute peplum au vocabulaire et fais le
   * merge », formule pré-remplie par la routine nocturne du 29-30/07,
   * prononcée par AH) — escalade P-12 ouverte par La Bataille de Marathon :
   * aucune des onze valeurs ne nommait le péplum ; `peplum` inscrit dans un
   * commit propre distinct de la publication, entrée rétrofittée
   * (fresque → peplum), même conduite que realisme magique le 27/07. */

  /* AJOUT DU 30/07/2026 (GATE AH « ajoute gothique au vocabulaire
   * genreBase », formule pré-remplie prononcée par AH à la remise de la
   * session supervisée) — escalade P-12 ouverte par Rebecca (1940) :
   * aucune des douze valeurs ne nommait le registre gothique du film,
   * `thriller` retenu à la rédaction comme valeur existante la plus juste
   * sans rabattage sur `drame` ; `gothique` inscrit dans ce commit, distinct
   * de la publication de la fiche, entrée rétrofittée (thriller → gothique)
   * sur l'entrée `rebecca`, seule concernée (aucune autre entrée du site
   * n'emploie encore ce terme). */

  /* Attributs techniques — liste fermée arrêtée par la spec (§4.2). */
  technique: ['muet', 'n&b', 'couleur'],

  /* Ouvert aux SEULES valeurs des 3 entrées migrées — à relire par AH.
     Une liste fermée ne se garnit pas de termes décoratifs « pour plus tard » :
     P-12 fait de chaque ajout un acte daté et commité. */
  pays: [
    'Allemagne',
    'Belgique',
    'Coree du Sud',
    'Cuba',
    'Danemark',
    'Etats-Unis',
    'France',
    'Hong Kong',
    'Hongrie',
    'Italie',
    'Japon',
    'Norvege',
    'Royaume-Uni',
    'Suede',
    'Suisse',
    'Tchecoslovaquie',
    'Union sovietique'
  ],

  /* Enrichissement éditorial, facultatif et non bloquant (§4.2).
     BASCULE DU 26/07/2026 (GATE AH « go neo-noir vers courant », fiche 20) :
     `neo-noir` quitte `genreBase` (0 usage au registre, vérifié) pour cet
     axe — c'est un registre stylistique, pas un genre de base ; constat
     porté par la note de fin de la session Blade Runner. */
  courant: [
    'neo-noir',
    'neorealisme',
    'realisme magique',
    'romantisme noir',
    'surrealisme'
  ]
  /* AJOUT DU 27/07/2026 (GATE AH « go vocab neorealisme avec rétrofit
     Rossellini », fiche 19) : `neorealisme` entre au vocabulaire — c'était
     l'escalade P-12 du pilote Scholar (25/07 : terme absent, facette OMISE
     de la page plutôt qu'inventée) ; rétrofit appliqué à l'entrée
     voyage-en-italie (seule page Rossellini du site — la fiche disait
     « 2 pages », le réel fait foi). */
  /* AJOUT DU 27/07/2026 soir (GATE AH « go vocab réalisme magique ») :
     `realisme magique` entre au vocabulaire — escalade P-12 de la routine
     nocturne (run de certification, L'Homme au crâne rasé : courant flamand,
     facette OMISE plutôt qu'inventée, non rabattue sur 'surrealisme') ;
     rétrofit appliqué à l'entrée lhomme-au-crane-rase (seule page Delvaux). */
};

/* Axes dont une valeur inconnue BLOQUE la publication (P-10).
 * `courant` en est absent : il est explicitement non bloquant. */
const AXES_BLOQUANTS = ['volet', 'genreBase', 'technique', 'pays'];

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { VOCABULAIRES: VOCABULAIRES, AXES_BLOQUANTS: AXES_BLOQUANTS };
}
