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
     distinctes, et aucune au-dessus de 80 %. P-52 : le volet est EXEMPTÉ, il
     s'affiche toujours (sans quoi la règle masquerait la thèse éditoriale du
     site, 97 % du corpus étant sur une seule valeur). */
  function discrimine(valeurs, total) {
    var noms = Object.keys(valeurs), i;
    if (noms.length < 3) { return false; }
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
      return c;
    });

    function facettesVisibles() {
      var vues = [], i, n;
      for (i = 0; i < AXES.length; i++) {
        if (filtreVolet && AXES[i].cle === 'volet') { continue; }
        n = compte(travail, AXES[i].cle);
        if (AXES[i].exempt || discrimine(n, travail.length)) {
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
      var t = elQ ? norm(elQ.value.trim()) : '';
      var vus = travail.filter(function (f) {
        var axe;
        for (axe in actifs) {
          if (actifs[axe] && !correspond(f, axe, actifs[axe])) { return false; }
        }
        if (!t) { return true; }
        return norm([f.title, f.director, f.year, f.genreBase, f.genre,
                     (f.pays || []).join(' '), f.decennie].join(' ')).indexOf(t) !== -1;
      });

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
          + (f.genreBase ? ' — ' + echappe(etiquette(f.genreBase))
                         : (f.genre ? ' — ' + echappe(f.genre) : ''))
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
