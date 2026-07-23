/* Composant unique de liste et de recherche — SPEC-SITE-V2 §3, §4.
 *
 * P-07 : « critiques.html » et « etudes.html » rendent LE MÊME composant que
 * l'accueil, avec un filtre différent. Il n'existe pas deux rails parallèles :
 * les Études sont des entrées marquées dans un index unique.
 * P-08 : la recherche ne lit AUCUN fichier de films/ — le registre est la
 * source unique de vérité structurée.
 * P-49 : aucun index plein texte. La recherche porte sur les métadonnées.
 *
 * ⚠️ PROVISOIRE — dégradation sans JavaScript (§4.5, point NON tranché).
 * Sans JS, la liste ne se construit pas : chaque page porte un <noscript> qui
 * le dit. Le repli des maquettes renvoyait vers « Critiques » — page qui, dans
 * le site réel, dépend du même script : le repli tourne en rond. Constaté, non
 * corrigé (poste de décision, fiche 2 bis).
 */

(function (global) {
  'use strict';

  /* Repli des diacritiques par table EXPLICITE — pas de plage de caractères
     combinants dans le source : invisible à la relecture, cassable au moindre
     accident d'encodage, et la recherche échouerait alors en silence. */
  var PLI = (function () {
    var acc = 'àâäãåáçéèêëîïìíñôöòóõøùûüúÿý',
        pla = 'aaaaaaceeeeiiiinoooooouuuuyy', m = {}, i;
    for (i = 0; i < acc.length; i++) { m[acc[i]] = pla[i]; }
    m['œ'] = 'oe'; m['æ'] = 'ae';
    return m;
  })();

  function norm(s) {
    s = (s === null || s === undefined) ? '' : s.toString().toLowerCase();
    var out = '', i;
    for (i = 0; i < s.length; i++) {
      out += (PLI[s[i]] !== undefined ? PLI[s[i]] : s[i]);
    }
    return out;
  }

  /* Le volet est un attribut de données (P-01). Les 30 entrées non encore
     migrées n'en portent pas : le prototype les lit comme « critique », ce qui
     est vrai du corpus au 22/07 (une seule Étude, migrée). Ce repli disparaît
     au rétrofit de BKL-065-5, où le champ devient obligatoire. */
  function volet(f) {
    return f.volet === 'etude' ? 'etude' : 'critique';
  }

  function estEtude(f) { return volet(f) === 'etude'; }

  var MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet',
              'août', 'septembre', 'octobre', 'novembre', 'décembre'];

  function dateFr(iso) {
    if (!iso) { return ''; }
    var p = iso.split(' ')[0].split('-');
    if (p.length !== 3) { return ''; }
    return (+p[2]) + ' ' + MOIS[(+p[1]) - 1] + ' ' + p[0];
  }

  /* Étiquettes d'affichage des valeurs de vocabulaire. Le registre stocke des
     identifiants sans accent et en minuscules (stables, comparables) ; l'écran
     montre du français. Aucune valeur n'est traduite : seule sa casse change,
     sauf pour le volet dont le pluriel est celui des entrées de menu. */
  var ETIQUETTES = {
    critique: 'Critiques', etude: 'Études', 'n&b': 'N&B',
    /* Les identifiants du vocabulaire sont sans accent — c'est ce qui les rend
       stables et comparables. L'accent est une affaire d'affichage, et il vit
       ici. Cette table doit rester identique à celle de
       outils/genere-liste-statique.py : le contrôle --verifier détecte toute
       dérive entre les deux gabarits. */
    melodrame: 'Mélodrame', comedie: 'Comédie', tragedie: 'Tragédie',
    'Etats-Unis': 'États-Unis', 'Union sovietique': 'Union soviétique'
  };

  function etiquette(v) {
    if (ETIQUETTES[v]) { return ETIQUETTES[v]; }
    v = String(v);
    return v.charAt(0).toUpperCase() + v.slice(1);
  }

  function echappe(s) {
    return (s === null || s === undefined ? '' : String(s))
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /* Ordre de publication (P-06) : datePublication décroissante, puis titre
     décroissant en cas d'égalité — les horodatages git étant à la minute, le
     départage alphabétique inverse n'est qu'un filet.
     ⚠️ PROTOTYPE : seules les 3 entrées migrées portent datePublication ; les
     autres sont rangées APRÈS, par titre. L'objet en une porte donc sur le
     sous-ensemble daté — signalé au rapport, corrigé au rétrofit 065-5. */
  function parDate(a, b) {
    var da = a.datePublication || '', db = b.datePublication || '';
    if (da && !db) { return -1; }
    if (!da && db) { return 1; }
    if (da !== db) { return da < db ? 1 : -1; }
    return b.title.localeCompare(a.title, 'fr');
  }

  function trie(films) { return films.slice().sort(parDate); }

  /* ------------------------------------------------- ordre du catalogue ---
     GATE AH du 22/07 : la mécanique et le classement sont à la main de ce
     mandat. Choix rendu, et motivé au constat de fin.

     L'ordre de la liste est ALPHABÉTIQUE par titre, replié sans accent.
     Ce n'est pas l'ordre du registre (qui est celui des ajouts, arbitraire
     pour un lecteur), ni l'ordre de publication (qui ferait doublon avec
     l'objet en une, et qui de toute façon n'existe que sur 3 entrées).
     Un index est un catalogue : on y cherche un titre.

     Le repli des accents sert AUSSI de clé de tri, au lieu de
     localeCompare : Python n'a pas de collation française dans sa
     bibliothèque standard, et le HTML statique doit sortir dans EXACTEMENT
     le même ordre que ce script. Une clé repliée, elle, se reproduit à
     l'identique des deux côtés — et le contrôle de dérive le prouve.
     Les articles initiaux ne sont pas escamotés : « Le Doulos » se range à
     « L », comme il s'écrit. Escamoter demanderait une règle de plus, et
     surprendrait autant qu'elle aiderait. */
  function cleCatalogue(f) { return norm(f.title || ''); }

  function ordreCatalogue(a, b) {
    var ka = cleCatalogue(a), kb = cleCatalogue(b);
    if (ka !== kb) { return ka < kb ? -1 : 1; }
    return (a.title || '') < (b.title || '') ? -1 : 1;
  }

  /* ------------------------------------------------------- la recherche ---
     JETONS, et non sous-chaîne globale. La sous-chaîne sur un champ
     concaténé impose au lecteur l'ordre des mots : « loach drame »
     n'y trouve rien, « annie woody » non plus. Découper la requête en
     jetons et exiger que CHACUN se trouve quelque part (ET) libère cet
     ordre — c'est ce qu'un lecteur attend d'un champ de recherche.
     Chaque jeton reste une SOUS-CHAÎNE : « melv » trouve Melville, ce qui
     évite d'avoir à gérer les pluriels et les formes fléchies du français
     avec un analyseur qu'on n'aura pas. */
  function jetons(requete) {
    var bruts = norm(requete).split(/\s+/), sortie = [], i;
    for (i = 0; i < bruts.length; i++) {
      if (bruts[i]) { sortie.push(bruts[i]); }
    }
    return sortie;
  }

  function correspondJetons(index, mots) {
    var i;
    for (i = 0; i < mots.length; i++) {
      if (index.indexOf(mots[i]) === -1) { return false; }
    }
    return true;
  }

  /* ---------------------------------------------------------------- une --- */

  function carteUne(f) {
    if (!f) { return ''; }
    return '<article class="carte-une" data-volet="' + volet(f) + '">'
      + '<span class="pastille">' + (estEtude(f) ? 'Étude' : 'Critique') + '</span>'
      + '<h3>' + echappe(f.title) + '</h3>'
      + '<div class="meta">' + echappe(f.director)
      + (f.year ? ' · ' + f.year : '')
      + (f.datePublication ? ' — publiée le ' + dateFr(f.datePublication) : '')
      + '</div>'
      + '<p>' + echappe(f.summary) + '</p>'
      + '<a class="lien" href="' + echappe(f.url) + '">Lire l\'analyse</a>'
      + '</article>';
  }

  /* P-06 + P-51 : la dernière publiée, et SA variante s'il y en a une.
     Jamais une entrée qui ne soit ni l'une ni l'autre : une Critique sans
     variante occupe seule le bloc (arbitrage Q-1 du 21/07). */
  function rendUne(films, elBloc, elCartel, elLiaison) {
    if (!elBloc) { return; }
    var ordre = trie(films);
    var derniere = ordre[0];
    if (!derniere) { return; }
    var couple = null, i;
    for (i = 0; i < films.length; i++) {
      if (derniere.variantOf && films[i].slug === derniere.variantOf) { couple = films[i]; }
      if (!derniere.variantOf && films[i].variantOf === derniere.slug) { couple = films[i]; }
    }
    elBloc.className = 'bloc-une' + (couple ? ' couple' : '');
    elBloc.innerHTML = couple
      ? carteUne(derniere) + carteUne(couple)
      : carteUne(derniere);
    if (elCartel) {
      elCartel.textContent = couple
        ? 'Dernière analyse publiée — et son pendant'
        : 'Dernière analyse publiée';
    }
    if (elLiaison) {
      elLiaison.textContent = couple
        ? 'Même film, deux régimes — champ et contrechamp.'
        : '';
    }
  }

  /* ------------------------------------------------------------ facettes --- */

  /* P-13 : une facette ne s'affiche que si elle discrimine — au moins 3 valeurs
     distinctes, aucune au-dessus de 80 %, ET le champ renseigné sur au moins
     la MOITIÉ du corpus affiché. P-52 : le volet est EXEMPTÉ, il s'affiche
     toujours (sans quoi la règle masquerait la thèse éditoriale du site, 97 %
     du corpus étant sur une seule valeur).

     Le seuil de COUVERTURE est l'ajout de la v1.1 de la spec (É-3, gate AH du
     22/07 11h54) : le prototype affichait « Pays », renseignée sur 3 entrées
     sur 33 — une facette qui, actionnée, MASQUAIT 30 analyses. Une facette
     éparse ne discrimine pas le corpus, elle le tronque. */
  function couverture(films, cle) {
    var n = 0, i, v;
    for (i = 0; i < films.length; i++) {
      v = films[i][cle];
      if (v === undefined || v === null || v === '') { continue; }
      if (Object.prototype.toString.call(v) === '[object Array]' && !v.length) {
        continue;
      }
      n++;
    }
    return films.length ? n / films.length : 0;
  }

  function discrimine(valeurs, total, tauxCouverture) {
    var noms = Object.keys(valeurs), i;
    if (noms.length < 3) { return false; }
    if (tauxCouverture < 0.5) { return false; }
    for (i = 0; i < noms.length; i++) {
      if (valeurs[noms[i]] / total > 0.8) { return false; }
    }
    return true;
  }

  function compte(films, cle) {
    var n = {}, i, j, v;
    for (i = 0; i < films.length; i++) {
      v = films[i][cle];
      if (v === undefined || v === null || v === '') { continue; }
      if (Object.prototype.toString.call(v) === '[object Array]') {
        for (j = 0; j < v.length; j++) { n[v[j]] = (n[v[j]] || 0) + 1; }
      } else {
        n[v] = (n[v] || 0) + 1;
      }
    }
    return n;
  }

  function correspond(f, cle, valeur) {
    var v = f[cle];
    if (Object.prototype.toString.call(v) === '[object Array]') {
      return v.indexOf(valeur) !== -1;
    }
    return v === valeur;
  }

  /* ---------------------------------------------------------------- rend --- */

  function monte(options) {
    var films = options.films,
        filtreVolet = options.volet || null,
        elListe = document.getElementById(options.liste),
        elCompte = options.compte ? document.getElementById(options.compte) : null,
        elQ = options.recherche ? document.getElementById(options.recherche) : null,
        elFacettes = options.facettes ? document.getElementById(options.facettes) : null;

    if (!elListe) { return; }

    /* Option (b) — gate AH du 22/07 08h24. La liste est déjà dans le HTML,
       écrite en dur par outils/genere-liste-statique.py : sans JavaScript le
       lecteur voit TOUT le corpus, simplement non filtrable. Le script ne fait
       que filtrer — et il commence par révéler les commandes, masquées dans le
       HTML parce qu'elles ne serviraient à rien sans lui. */
    if (elQ) { elQ.hidden = false; }
    if (elFacettes) { elFacettes.hidden = false; }

    /* Le corpus de cette vue : c'est ici, et ici seulement, que « Critiques »
       et « Études » diffèrent de l'accueil (P-07). */
    var corpus = filtreVolet
      ? films.filter(function (f) { return volet(f) === filtreVolet; })
      : films.slice();

    var ordre = trie(films);
    var derniere = ordre[0];

    var actifs = {};
    if (!filtreVolet) { actifs.volet = null; }

    var AXES = [
      { cle: 'volet', titre: 'Volet', exempt: true,
        valeur: function (f) { return volet(f); } },
      { cle: 'genreBase', titre: 'Genre' },
      { cle: 'pays', titre: 'Pays' },
      { cle: 'technique', titre: 'Technique' },
      { cle: 'decennie', titre: 'Décennie',
        valeur: function (f) { return f.year ? (Math.floor(f.year / 10) * 10) + 's' : null; } }
    ];

    /* Décennie et volet sont DÉRIVÉS (§4.2) : on les matérialise sur une copie
       de travail, jamais dans le registre. */
    var travail = corpus.map(function (f) {
      var c = {}, k;
      for (k in f) { if (Object.prototype.hasOwnProperty.call(f, k)) { c[k] = f[k]; } }
      c.volet = volet(f);
      c.decennie = f.year ? (Math.floor(f.year / 10) * 10) + 's' : null;
      /* Index de recherche calculé UNE FOIS par entrée, à l'amorçage, et non
         à chaque frappe : c'est ce qui tient le seuil de 100 ms de P-41 quand
         le corpus grandira. */
      c._index = norm([f.title, f.director, f.year, f.genreBase, f.genre,
                       (f.pays || []).join(' '), c.decennie].join(' '));
      return c;
    }).sort(ordreCatalogue);

    function facettesVisibles() {
      var vues = [], i, n;
      for (i = 0; i < AXES.length; i++) {
        if (filtreVolet && AXES[i].cle === 'volet') { continue; }
        n = compte(travail, AXES[i].cle);
        if (AXES[i].exempt
            || discrimine(n, travail.length,
                          couverture(travail, AXES[i].cle))) {
          vues.push({ axe: AXES[i], valeurs: n });
        }
      }
      return vues;
    }

    function rendFacettes() {
      if (!elFacettes) { return; }
      var vues = facettesVisibles();
      elFacettes.innerHTML = vues.map(function (v) {
        var noms = Object.keys(v.valeurs).sort();
        return '<div class="facette"><span class="titre-facette">'
          + echappe(v.axe.titre) + '</span>'
          + '<button class="filtre" data-axe="' + v.axe.cle + '" data-val=""'
          + ' aria-pressed="' + (actifs[v.axe.cle] ? 'false' : 'true') + '">Tout</button>'
          + noms.map(function (n) {
              return '<button class="filtre" data-axe="' + v.axe.cle + '"'
                + ' data-val="' + echappe(n) + '"'
                + ' aria-pressed="' + (actifs[v.axe.cle] === n ? 'true' : 'false') + '">'
                + echappe(etiquette(n)) + ' <span aria-hidden="true">(' + v.valeurs[n] + ')</span>'
                + '</button>';
            }).join('')
          + '</div>';
      }).join('');
    }

    function rend() {
      /* Aucun classement par pertinence : les résultats gardent l'ordre du
         catalogue. Le filtre étant conjonctif, TOUTES les entrées retenues
         satisfont TOUS les jetons — il n'y a pas de gradient à trier. Un
         pseudo-score (le titre vaut plus que le réalisateur) ferait bouger
         les lignes d'une manière que le lecteur ne peut pas prévoir, sur une
         liste qui tient le plus souvent dans un écran une fois filtrée. */
      var mots = elQ ? jetons(elQ.value) : [];
      var vus = travail.filter(function (f) {
        var axe;
        for (axe in actifs) {
          if (actifs[axe] && !correspond(f, axe, actifs[axe])) { return false; }
        }
        return mots.length ? correspondJetons(f._index, mots) : true;
      });
      /* Le compteur cite la requête TELLE QUE TAPÉE, pas les jetons repliés :
         le repli est une mécanique interne, le lecteur n'a pas à la voir. */
      var t = mots.length && elQ ? elQ.value.trim() : '';

      if (elCompte) {
        elCompte.textContent = vus.length + (vus.length > 1 ? ' analyses' : ' analyse')
          + (t && elQ ? ' pour « ' + elQ.value.trim() + ' »' : '')
          + ' — sur ' + travail.length;
      }

      elListe.innerHTML = vus.length ? vus.map(function (f) {
        return '<li><a class="entree" href="' + echappe(f.url) + '"'
          + ' data-volet="' + f.volet + '">'
          + '<span class="t">' + echappe(f.title)
          + (f.volet === 'etude' ? '<span class="marq">Étude</span>' : '')
          + (derniere && f.slug === derniere.slug
              ? '<span class="neuf">dernière publiée</span>' : '')
          + '</span>'
          + '<span class="a">' + (f.year || '') + '</span>'
          + '<span class="d">' + echappe(f.director)
          /* P-50 : `genre` est déprécié et n'est plus lu. Le repli sur le
             texte libre était l'écart assumé du prototype, le temps que
             `genreBase` couvre le corpus — il le couvre à 33/33 depuis le
             rétrofit 065-5, le repli n'a plus d'objet. */
          + (f.genreBase ? ' — ' + echappe(etiquette(f.genreBase)) : '')
          + '</span>'
          + '</a></li>';
      }).join('') : '<li class="vide">Aucune analyse ne correspond.</li>';
    }

    if (elQ) { elQ.addEventListener('input', rend); }

    if (elFacettes) {
      elFacettes.addEventListener('click', function (e) {
        var b = e.target.closest ? e.target.closest('button.filtre') : null;
        if (!b) { return; }
        var axe = b.getAttribute('data-axe'), val = b.getAttribute('data-val');
        actifs[axe] = val || null;
        rendFacettes();
        rend();
      });
      rendFacettes();
    }

    rend();
  }

  global.Corpus = { monte: monte, rendUne: rendUne, volet: volet, trie: trie };

})(this);
