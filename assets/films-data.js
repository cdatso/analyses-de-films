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
    poster: 'assets/posters/rouges-et-blancs.jpg',
    // --- schéma v2 (annexe B) — entrée migrée par le prototype BKL-065-3 ---
    volet: 'critique',
    datePublication: '2026-07-04 10:11',
    pays: ['Hongrie', 'Union sovietique'],
    genreBase: 'drame',
    technique: ['n&b'],
    producteur: 'non spécifié'
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
  },
  {
    slug: 'retour-a-seoul',
    title: 'Retour à Séoul',
    director: 'Davy Chou',
    year: 2022,
    genre: 'Drame',
    summary: "Une adoptée française rentre « chez elle » dans un pays dont elle ne parle pas la langue — et refuse huit ans durant toutes les identités qu'on lui tend.",
    url: 'films/retour-a-seoul.html',
    poster: 'assets/posters/retour-a-seoul.jpg'
  },
  {
    slug: 'waterloo',
    title: 'Waterloo',
    director: 'Sergueï Bondartchouk',
    year: 1970,
    genre: 'Fresque historique',
    summary: "Vingt mille soldats soviétiques, un producteur italien et deux empires du cinéma pour rejouer la journée qui a défait Napoléon — la dernière bataille filmée sans trucage à cette échelle.",
    url: 'films/waterloo.html',
    poster: 'assets/posters/waterloo.jpg'
  },
  {
    slug: 'nouvelle-vague',
    title: 'Nouvelle Vague',
    director: 'Richard Linklater',
    year: 2025,
    genre: 'Comédie dramatique',
    summary: "Le tournage d'À bout de souffle rejoué plan par plan, en français et en 1.37 : la déclaration d'amour d'un cinéphile texan au geste le plus libre du cinéma.",
    url: 'films/nouvelle-vague.html',
    poster: 'assets/posters/nouvelle-vague.jpg'
  },
  {
    slug: 'julie-en-12-chapitres',
    title: 'Julie (en 12 chapitres)',
    director: 'Joachim Trier',
    year: 2021,
    genre: 'Comédie dramatique',
    summary: "Quatre ans de la vie d'une femme qui essaie toutes les vies possibles, racontés comme un roman — et le prix d'interprétation de Cannes pour Renate Reinsve.",
    url: 'films/julie-en-12-chapitres.html',
    poster: 'assets/posters/julie-en-12-chapitres.jpg'
  },
  {
    slug: 'le-golem',
    title: 'Le Golem',
    director: 'Julien Duvivier',
    year: 1936,
    genre: 'Fantastique',
    summary: "Un cinéaste français filme à Prague, trois ans après l'arrivée de Hitler au pouvoir, la légende du géant d'argile qui venge le ghetto : le fantastique comme éditorial.",
    url: 'films/le-golem.html',
    poster: 'assets/posters/le-golem.jpg'
  },
  {
    slug: 'moi-daniel-blake',
    title: 'Moi, Daniel Blake',
    director: 'Ken Loach',
    year: 2016,
    genre: 'Drame social',
    summary: "Trop malade pour travailler, pas assez pour être indemnisé : la Palme d'or la plus politique de la décennie, écrite à la bombe sur le mur d'une administration.",
    url: 'films/moi-daniel-blake.html',
    poster: 'assets/posters/moi-daniel-blake.jpg'
  },
  {
    slug: 'la-chevauchee-fantastique',
    title: 'La Chevauchée fantastique',
    director: 'John Ford',
    year: 1939,
    genre: 'Western',
    summary: "Neuf voyageurs que la bonne société ne mettrait jamais dans la même pièce, une diligence, le territoire apache : le film qui a rendu au western ses lettres de noblesse.",
    url: 'films/la-chevauchee-fantastique.html',
    poster: 'assets/posters/la-chevauchee-fantastique.jpg'
  },
  {
    slug: 'le-doulos',
    title: 'Le Doulos',
    director: 'Jean-Pierre Melville',
    year: 1962,
    genre: 'Film noir',
    summary: "Un mot d'argot qui désigne à la fois un chapeau et un indicateur : Melville construit tout un polar sur l'impossibilité de savoir, jusqu'au bout, qui porte lequel des deux sens.",
    url: 'films/le-doulos.html',
    poster: 'assets/posters/le-doulos.jpg'
  },
  {
    slug: 'sur-la-route-domaha',
    title: "Sur la route d'Omaha",
    director: 'Cole Webley',
    year: 2025,
    genre: 'Drame',
    summary: "Un père ruiné par la crise de 2008 conduit ses deux enfants vers une destination qu'il leur tait — et que ce road movie ne dévoile qu'à ses tout derniers mètres, quitte à rétroéclairer chaque étape parcourue.",
    url: 'films/sur-la-route-domaha.html',
    poster: 'assets/posters/sur-la-route-domaha.jpg'
  },
  {
    slug: 'pandora',
    title: 'Pandora — Champ',
    director: 'Albert Lewin',
    year: 1951,
    genre: 'Mélodrame fantastique',
    summary: "Albert Lewin filme Ava Gardner comme une statue de déesse pour mieux la faire redescendre parmi les mortels : un mélodrame ouvertement surréaliste, jugé prétentieux à sa sortie avant d'être reconnu comme un sommet du romantisme noir.",
    url: 'films/pandora.html',
    poster: 'assets/posters/pandora.jpg',
    producteur: 'Claude (pipeline, routine nocturne)',
    // --- schéma v2 (annexe B) — entrée migrée par le prototype BKL-065-3 ---
    volet: 'critique',
    datePublication: '2026-07-18 20:45',
    pays: ['Royaume-Uni', 'Etats-Unis'],
    genreBase: 'melodrame',
    technique: ['couleur'],
    courant: ['romantisme noir', 'surrealisme']
  },
  {
    slug: 'pandora-contrechamp',
    title: 'Pandora — Contrechamp',
    director: 'Albert Lewin',
    year: 1951,
    genre: 'Mélodrame fantastique',
    summary: "La même œuvre relue par un second regard : reprise et enrichissement squad d'une analyse déléguée à OpenAI GPT-5.5, avec un appareil théorique deleuzien (l'ouverture à la lunette, la « femme originaire ») absent du champ.",
    url: 'films/pandora-contrechamp.html',
    poster: 'assets/posters/pandora.jpg',
    producteur: 'OpenAI GPT-5.5 (reprise et enrichissement squad)',
    variantOf: 'pandora',
    // --- schéma v2 (annexe B) — entrée migrée par le prototype BKL-065-3 ---
    volet: 'etude',
    datePublication: '2026-07-18 23:45',
    pays: ['Royaume-Uni', 'Etats-Unis'],
    genreBase: 'melodrame',
    technique: ['couleur'],
    courant: ['romantisme noir', 'surrealisme']
  },
  {
    slug: 'la-nuit-de-san-lorenzo',
    title: 'La Nuit de San Lorenzo',
    director: 'Paolo et Vittorio Taviani',
    year: 1982,
    genre: 'Drame de guerre',
    summary: "Les Taviani racontent le massacre de leur propre ville comme une berceuse d'étoiles filantes — parti pris magnifique, qui aura aussi fixé pour le monde entier une responsabilité que les archives ont depuis déplacée.",
    url: 'films/la-nuit-de-san-lorenzo.html',
    poster: 'assets/posters/la-nuit-de-san-lorenzo.jpg',
    producteur: 'Claude Opus (session supervisée)'
  },
  {
    slug: 'hamlet',
    title: 'Hamlet',
    director: 'Grigori Kozintsev',
    year: 1964,
    genre: 'Tragédie shakespearienne (N&B)',
    summary: "Kozintsev retire au rôle le plus commenté du théâtre occidental ce dont on croyait qu'il était fait — l'hésitation : son prince n'est pas empêché par lui-même, mais par une forteresse d'État dont le film ne cesse de filmer les barreaux.",
    url: 'films/hamlet.html',
    poster: 'assets/posters/hamlet.jpg',
    producteur: 'Claude Opus (session supervisée)'
  },
  {
    slug: 'le-samourai',
    title: 'Le Samouraï',
    director: 'Jean-Pierre Melville',
    year: 1967,
    genre: 'Polar / film noir',
    summary: "Un tueur à gages qui n'est plus qu'une méthode : Melville retire la couleur de la couleur, invente de toutes pièces la citation du Bushido qui ouvre le film, et fait tenir une morale entière sur un document faux.",
    url: 'films/le-samourai.html',
    poster: 'assets/posters/le-samourai.jpg',
    producteur: 'Claude (pipeline, routine nocturne)'
  },
  {
    slug: 'hitchcock-truffaut',
    title: 'Hitchcock/Truffaut',
    director: 'Kent Jones',
    year: 2015,
    genre: 'Documentaire',
    summary: "Truffaut avait enfermé Hitchcock huit jours dans un bureau d'Universal pour le sauver de sa réputation d'amuseur ; cinquante ans plus tard, Kent Jones rouvre les bandes et compose, sans tout à fait le vouloir, le portrait d'un panthéon devenu club.",
    url: 'films/hitchcock-truffaut.html',
    poster: 'assets/posters/hitchcock-truffaut.jpg',
    producteur: 'Claude (pipeline, routine nocturne)'
  }
];
