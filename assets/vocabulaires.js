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
    'melodrame',
    'polar',
    'thriller',
    'tragedie',
    'western'
  ],

  /* Attributs techniques — liste fermée arrêtée par la spec (§4.2). */
  technique: ['muet', 'n&b', 'couleur'],

  /* Ouvert aux SEULES valeurs des 3 entrées migrées — à relire par AH.
     Une liste fermée ne se garnit pas de termes décoratifs « pour plus tard » :
     P-12 fait de chaque ajout un acte daté et commité. */
  pays: [
    'Etats-Unis',
    'Hongrie',
    'Royaume-Uni',
    'Union sovietique'
  ],

  /* Enrichissement éditorial, facultatif et non bloquant (§4.2). */
  courant: [
    'romantisme noir',
    'surrealisme'
  ]
};

/* Axes dont une valeur inconnue BLOQUE la publication (P-10).
 * `courant` en est absent : il est explicitement non bloquant. */
const AXES_BLOQUANTS = ['volet', 'genreBase', 'technique', 'pays'];

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { VOCABULAIRES: VOCABULAIRES, AXES_BLOQUANTS: AXES_BLOQUANTS };
}
