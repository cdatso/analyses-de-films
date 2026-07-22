#!/usr/bin/env python3
# -*- coding: ascii -*-
"""bilan-reseau.py -- lit resultats/reseau.json et rend les verdicts P-24,
P-27, P-32, P-37. Lecture seule ; aucune mesure nouvelle."""

import sys

import harnais

SEUIL_PREMIERE = 900 * 1024
SEUIL_SUIVANTE = 400 * 1024

# Les fichiers de fontes non latines du systeme typographique v2 (P-27).
NON_LATINES = ("cyrillic", "cyrillique", "hebrew", "hebreu", "frankruhl",
               "frank-ruhl", "frank_ruhl")


def ko(n):
    return n / 1024.0


def main():
    r = harnais.lire_json("reseau.json")
    proto = harnais.PAGES_PROTOTYPE
    autres = harnais.pages_non_migrees()

    print("== P-24 : requetes tierces ==")
    print("%-40s %s" % ("page", "requetes tierces"))
    ko_proto = 0
    for p in proto:
        n = len(r[p]["froid"]["tiers"])
        ko_proto += n
        print("  %-38s %d" % (p, n))
    n_autres = sum(len(r[p]["froid"]["tiers"]) for p in autres)
    pages_autres = sum(1 for p in autres if r[p]["froid"]["tiers"])
    print("  TOTAL prototype (9 pages)              : %d" % ko_proto)
    print("  Informatif -- 30 pages non migrees     : %d requetes sur %d pages"
          % (n_autres, pages_autres))

    print("")
    print("== P-32 : statut HTTP des documents ==")
    casses = [(p, r[p]["statut"]) for p in harnais.pages_toutes()
              if r[p]["statut"] != 200]
    print("  documents servis : %d" % len(r))
    print("  hors 200         : %d %s" % (len(casses), casses))

    print("")
    print("== P-37 : poids de page ==")
    print("  seuils : premiere visite %d o (900 Ko) / suivante %d o (400 Ko)"
          % (SEUIL_PREMIERE, SEUIL_SUIVANTE))
    print("  %-38s %10s %10s  %s" % ("page", "1re (Ko)", "suiv (Ko)", "verdict"))
    ecarts = []
    for p in proto:
        f = r[p]["froid"]["octets"]
        c = r[p]["chaud"]["octets"]
        v = []
        if f > SEUIL_PREMIERE:
            v.append("1re>900Ko")
        if c > SEUIL_SUIVANTE:
            v.append("suiv>400Ko")
        if v:
            ecarts.append((p, f, c, ",".join(v)))
        print("  %-38s %10.1f %10.1f  %s" % (p, ko(f), ko(c),
                                             ",".join(v) if v else "OK"))
    print("  pages du prototype en ecart : %d" % len(ecarts))

    print("")
    print("== P-27 : subsets non latins telecharges ==")
    for p in proto:
        polices = r[p]["froid"]["polices"]
        nl = [x for x in polices if any(k in x.lower() for k in NON_LATINES)]
        print("  %-38s %2d fontes  dont non latines : %s"
              % (p, len(polices), nl if nl else "aucune"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
