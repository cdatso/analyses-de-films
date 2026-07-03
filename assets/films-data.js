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
    summary: "Comment un film sur une rupture amoureuse a redéfini la comédie romantique américaine.",
    url: 'films/annie-hall.html',
    poster: 'assets/posters/annie-hall.jpg'
  },
  {
    slug: 'the-old-oak',
    title: 'The Old Oak',
    director: 'Ken Loach',
    year: 2023,
    summary: "Le dernier pub debout, la dernière fable de Ken Loach : réfugiés syriens et mineurs abandonnés dans le nord-est de l'Angleterre.",
    url: 'films/the-old-oak.html',
    poster: 'assets/posters/the-old-oak.jpg'
  },
  {
    slug: 'soudain-lete-dernier',
    title: "Soudain l'été dernier",
    director: 'Joseph L. Mankiewicz',
    year: 1959,
    summary: "Un mélodrame gothique sur l'emprise maternelle, la censure du Code Hays et une vérité qu'on tente de faire taire à coups de scalpel.",
    url: 'films/soudain-lete-dernier.html',
    poster: 'assets/posters/soudain-lete-dernier.jpg'
  },
  {
    slug: 'soy-cuba',
    title: 'Soy Cuba',
    director: 'Mikhaïl Kalatozov',
    year: 1964,
    summary: "Un manifeste de propagande cubano-soviétique dont la virtuosité visuelle a fini par échapper à ses propres commanditaires.",
    url: 'films/soy-cuba.html',
    poster: 'assets/posters/soy-cuba.jpg'
  },
  {
    slug: 'sud',
    title: 'Sud',
    director: 'Chantal Akerman',
    year: 1999,
    summary: "Une traversée silencieuse du Sud des États-Unis, hantée par le meurtre raciste de James Byrd Jr.",
    url: 'films/sud.html',
    poster: 'assets/posters/sud.jpg'
  },
  {
    slug: 'shutter-island',
    title: 'Shutter Island',
    director: 'Martin Scorsese',
    year: 2010,
    summary: "Un marshal fédéral enquête sur une île-asile où la vérité qu'il cherche finit par se retourner contre lui.",
    url: 'films/shutter-island.html',
    poster: 'assets/posters/shutter-island.jpg'
  },
  {
    slug: 'hamnet',
    title: 'Hamnet',
    director: 'Chloé Zhao',
    year: 2025,
    summary: "Comment le deuil d'un fils disparu a pu donner naissance à l'un des chefs-d'œuvre de Shakespeare.",
    url: 'films/hamnet.html',
    poster: 'assets/posters/hamnet.jpg'
  }
];
