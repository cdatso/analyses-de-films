// Registre des analyses publiées sur le site.
// Pour ajouter un film : ajouter un objet à ce tableau et créer le fichier HTML correspondant dans /films.
// Convention d'images : déposer l'affiche dans assets/posters/<slug>.jpg
// (le champ poster peut être omis tant qu'aucune image n'est disponible —
// l'absence de fichier est gérée proprement par la page).
const FILMS = [
  {
    slug: 'annie-hall',
    title: 'Annie Hall',
    director: 'Woody Allen',
    year: 1977,
    genre: 'Comédie dramatique romantique',
    summary: "Comment un film sur une rupture amoureuse a redéfini la comédie romantique américaine.",
    url: 'films/annie-hall.html',
    poster: 'assets/posters/annie-hall.jpg'
  },
  {
    slug: 'the-old-oak',
    title: 'The Old Oak',
    director: 'Ken Loach',
    year: 2023,
    genre: 'Drame social',
    summary: "Le dernier pub debout, la dernière fable de Ken Loach : réfugiés syriens et mineurs abandonnés dans le nord-est de l'Angleterre.",
    url: 'films/the-old-oak.html',
    poster: 'assets/posters/the-old-oak.jpg'
  },
  {
    slug: 'soudain-lete-dernier',
    title: "Soudain l'été dernier",
    director: 'Joseph L. Mankiewicz',
    year: 1959,
    genre: 'Mélodrame gothique',
    summary: "Un mélodrame gothique sur l'emprise maternelle, la censure du Code Hays et une vérité qu'on tente de faire taire à coups de scalpel.",
    url: 'films/soudain-lete-dernier.html',
    poster: 'assets/posters/soudain-lete-dernier.jpg'
  },
  {
    slug: 'soy-cuba',
    title: 'Soy Cuba',
    director: 'Mikhaïl Kalatozov',
    year: 1964,
    genre: 'Drame de propagande',
    summary: "Un manifeste de propagande cubano-soviétique dont la virtuosité visuelle a fini par échapper à ses propres commanditaires.",
    url: 'films/soy-cuba.html',
    poster: 'assets/posters/soy-cuba.jpg'
  },
  {
    slug: 'sud',
    title: 'Sud',
    director: 'Chantal Akerman',
    year: 1999,
    genre: 'Documentaire',
    summary: "Une traversée silencieuse du Sud des États-Unis, hantée par le meurtre raciste de James Byrd Jr.",
    url: 'films/sud.html',
    poster: 'assets/posters/sud.jpg'
  },
  {
    slug: 'shutter-island',
    title: 'Shutter Island',
    director: 'Martin Scorsese',
    year: 2010,
    genre: 'Thriller psychologique',
    summary: "Un marshal fédéral enquête sur une île-asile où la vérité qu'il cherche finit par se retourner contre lui.",
    url: 'films/shutter-island.html',
    poster: 'assets/posters/shutter-island.jpg'
  },
  {
    slug: 'hamnet',
    title: 'Hamnet',
    director: 'Chloé Zhao',
    year: 2025,
    genre: 'Drame historique',
    summary: "Comment le deuil d'un fils disparu a pu donner naissance à l'un des chefs-d'œuvre de Shakespeare.",
    url: 'films/hamnet.html',
    poster: 'assets/posters/hamnet.jpg'
  },
  {
    slug: 'les-deux-orphelines',
    title: 'Les Deux Orphelines',
    director: 'D. W. Griffith',
    year: 1921,
    genre: 'Mélodrame historique (muet)',
    summary: "Deux sœurs de cœur séparées par la Révolution française, dans le dernier mélodrame muet où Griffith réunit une dernière fois les sœurs Gish.",
    url: 'films/les-deux-orphelines.html',
    poster: 'assets/posters/les-deux-orphelines.jpg'
  },
  {
    slug: 'rosetta',
    title: 'Rosetta',
    director: 'Jean-Pierre & Luc Dardenne',
    year: 1999,
    genre: 'Drame social',
    summary: "Une adolescente en quête désespérée d'un emploi stable, filmée caméra à l'épaule par les frères Dardenne jusqu'à la Palme d'or.",
    url: 'films/rosetta.html',
    poster: 'assets/posters/rosetta.jpg'
  },
  {
    slug: 'rouges-et-blancs',
    title: 'Rouges et Blancs',
    director: 'Miklós Jancsó',
    year: 1967,
    genre: 'Drame de guerre',
    summary: "Une chorégraphie glaciale de la guerre civile russe, où Miklós Jancsó filme la violence comme une géométrie sans héros.",
    url: 'films/rouges-et-blancs.html',
    poster: 'assets/posters/rouges-et-blancs.jpg'
  },
  {
    slug: 'persona',
    title: 'Persona',
    director: 'Ingmar Bergman',
    year: 1966,
    genre: 'Drame psychologique',
    summary: "Écrit en quatorze jours sur un lit d'hôpital, un huis clos entre une infirmière et une actrice devenue muette qui a fini par redéfinir le cinéma moderne.",
    url: 'films/persona.html',
    poster: 'assets/posters/persona.jpg'
  },
  {
    slug: 'au-fil-de-leau',
    title: "Au fil de l'eau",
    director: 'Fritz Lang',
    year: 1950,
    genre: 'Film noir gothique',
    summary: "Un romancier raté transforme son crime en roman à succès — mais la rivière de Fritz Lang rend toujours ce qu'on lui confie.",
    url: 'films/au-fil-de-leau.html',
    poster: 'assets/posters/au-fil-de-leau.jpg'
  },
  {
    slug: 'raging-bull',
    title: 'Raging Bull',
    director: 'Martin Scorsese',
    year: 1980,
    genre: 'Drame biographique',
    summary: "Scorsese pensait signer son dernier film ; il a filmé la jalousie d'un champion comme un opéra en noir et blanc, à hauteur de coups.",
    url: 'films/raging-bull.html',
    poster: 'assets/posters/raging-bull.jpg'
  },
  {
    slug: 'le-cheval-de-turin',
    title: 'Le Cheval de Turin',
    director: 'Béla Tarr',
    year: 2011,
    genre: 'Drame contemplatif',
    summary: "Six jours de vent, un cheval qui refuse, la lumière qui s'éteint : le dernier film de Béla Tarr regarde la fin du monde à hauteur de pommes de terre.",
    url: 'films/le-cheval-de-turin.html',
    poster: 'assets/posters/le-cheval-de-turin.jpg'
  },
  {
    slug: 'la-mariee-etait-en-noir',
    title: 'La mariée était en noir',
    director: 'François Truffaut',
    year: 1968,
    genre: 'Thriller',
    summary: "Cinq noms sur une liste, une robe mi-lys mi-corbeau : Truffaut filme la vengeance comme un chagrin d'amour, sous le regard d'Hitchcock.",
    url: 'films/la-mariee-etait-en-noir.html',
    poster: 'assets/posters/la-mariee-etait-en-noir.jpg'
  },
  {
    slug: 'bienvenue-a-suburbicon',
    title: 'Bienvenue à Suburbicon',
    director: 'George Clooney',
    year: 2017,
    genre: 'Comédie noire',
    summary: "Un scénario noir des Coen greffé sur un fait divers de la ségrégation : pendant que la banlieue assiège sa seule famille innocente, le crime blanc prospère pavillon contre pavillon.",
    url: 'films/bienvenue-a-suburbicon.html',
    poster: 'assets/posters/bienvenue-a-suburbicon.jpg'
  },
  {
    slug: 'manhattan',
    title: 'Manhattan',
    director: 'Woody Allen',
    year: 1979,
    genre: 'Comédie dramatique',
    summary: "Une déclaration d'amour en Scope noir et blanc à une ville rêvée sur du Gershwin — chef-d'œuvre formel devenu pièce à conviction de son propre auteur.",
    url: 'films/manhattan.html',
    poster: 'assets/posters/manhattan.jpg'
  },
  {
    slug: 'sans-filtre',
    title: 'Sans Filtre',
    director: 'Ruben Östlund',
    year: 2022,
    genre: 'Comédie satirique',
    summary: "Un yacht d'oligarques, une tempête gastrique, une dame pipi promue capitaine : la Palme d'or la plus clivante de la décennie filme la lutte des classes à hauteur d'estomac.",
    url: 'films/sans-filtre.html',
    poster: 'assets/posters/sans-filtre.jpg'
  }
];
