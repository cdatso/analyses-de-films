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
  }
];
