"""Direction 2: positive-z family scan (D1 v2 boundary, other side).

D1 v2 classified 9 of the 27 d as j>0 (positive-z family): Ramanujan 1914
eq 28-33 are instances of that family, with z = 1/4, 1/64, 2/27, 4/125 ...
For a CM point with j > 0, the classic (Borwein) form is

  1/pi = sum_k (A + B k) * (1/2)_k (1/s)_k (1-1/s)_k / (k!)^3 * z^k

with z > 0 an algebraic number tied to the CM point.  We do NOT know the
closed form mapping d -> z for the positive family from first principles
in this repo, so we SCAN: for each j>0 d, solve for the z that makes the
identity hold with integer (A, B) -- i.e. a 3-parameter integer relation
(A, B, z).  Strategy per d, per signature s in {2,3,4,6}:

  1. numeric z-solve:  findroot on  c0-term + (A + Bk)H_k z^k == M/pi
     with (A, B, M) left FREE is underdetermined -- instead use the
     two-sum trick from series_gen: for a FIXED s, z is pinned by
     requiring TWO independent integer relations.  Concretely:
       Y(z) = sum (A+Bk) H_k z^k  is affine in (A, B) for fixed z:
       Y = A*S0(z) + B*S1(z).
     For the CORRECT z, both A and B are integers (small).  So:
       scan z over a log grid; at each z compute (A, B) by 2D integer
       least squares on the constraint Y_true = A*S0 + B*S1 where
       Y_true is fixed = M/pi ... but M is also unknown!

  Practical resolution: we use the RATIO structure.  For the true z,
     the pair (A(z), B(z)) recovered from ANY consistent (Y, M) must be
     integers.  We set Y = M/pi with M unknown and absorb it: define
     the 3-vector relation  [S0(z), S1(z), -1/pi] and run PSLQ for
     integer (A, B, M).  Scan z; accept where PSLQ returns small coeffs.
  Grid: z in [1/4096, 1/2], 600 log-spaced points; refine winners by
     local findroot on the PSLQ residual.

This is a genuinely mechanical scan (no literature lookup); miss list =
"data product".  Run:  python posz_scan.py
"""
import json
import math
import os
import sys

import numpy as np
from mpmath import mp, mpc, mpf, pi, sqrt, rf, factorial, jtheta, exp, pslq

mp.dps = 80

HERE = os.path.dirname(os.path.abspath(__file__))


def cm_tau(d):
    if d % 4 == 3:
        return (1 + mpc(0, mpf(d) ** 0.5)) / 2
    return mpc(0, mpf(d) ** 0.5)


def j_of_tau(tau):
    q = exp(mpc(0, mp.pi) * tau)
    t2, t3 = jtheta(2, 0, q), jtheta(3, 0, q)
    k2 = (t2 / t3) ** 4
    return 256 * (1 - k2 + k2 ** 2) ** 3 / (k2 ** 2 * (1 - k2) ** 2)


def H(k, s):
    return rf(mpf(1) / 2, k) * rf(mpf(1) / s, k) * rf(mpf(1) - 1 / mpf(s), k) \
        / factorial(k) ** 3


def sums(z, s, terms):
    S0 = S1 = mpf(0)
    for k in range(terms):
        h = H(k, s) * z ** k
        S0 += h
        S1 += k * h
    return S0, S1


def n_terms(z):
    az = abs(float(z))
    if az >= 1:
        return 400
    return min(4000, int(math.ceil(-60 / math.log10(az))) + 20)


def pslq_abm(S0, S1, maxcoeff=10 ** 12):
    """Find integer (A, B, M) with A*S0 + B*S1 = M/pi."""
    rel = pslq([S0, S1, -1 / pi], tol=mpf(10) ** -40, maxcoeff=maxcoeff)
    return rel


POS_D = [1, 2, 20, 24, 40, 52, 88, 148, 232]   # j>0 from D1 v2
SIGNS = [2, 3, 4, 6]

def main():
    rows = []
    hits = []
    for d in POS_D:
        j = j_of_tau(cm_tau(d))
        jr = mp.re(j)
        best = None
        for s in SIGNS:
            # scan z on a log grid
            zs = [mpf(10) ** e for e in
                  np.linspace(-6, math.log10(0.5), 240)]
            for z in zs:
                terms = n_terms(z)
                S0, S1 = sums(z, s, terms)
                if abs(S0) < 1e-20:
                    continue
                rel = pslq_abm(S0, S1)
                if rel is None:
                    continue
                A, B, M = rel
                if A == 0 and B == 0:
                    continue
                # verify residual at higher precision
                S0r, S1r = sums(z, s, terms + 40)
                resid = abs(A * S0r + B * S1r - M / pi) * pi
                small = max(abs(A), abs(B), abs(M)) < 10 ** 9
                if resid < mpf(10) ** -25 and small:
                    if best is None or resid < best["resid"]:
                        best = {"d": d, "s": s, "z": mp.nstr(z, 20),
                                "A": A, "B": B, "M": M,
                                "resid": mp.nstr(resid, 3)}
        if best:
            hits.append(best)
            print(f"  d={d:4d}  HIT  s={best['s']}  z={best['z']}  "
                  f"A={best['A']}  B={best['B']}  M={best['M']}  "
                  f"resid={best['resid']}", flush=True)
        else:
            print(f"  d={d:4d}  miss (no small integer relation on grid)",
                  flush=True)
        rows.append(best or {"d": d, "hit": False})

    print(f"\n=== positive-z scan: {len(hits)}/{len(POS_D)} d produced "
          f"integer relations ===")
    out = os.path.join(HERE, "posz_scan_results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"hits": len(hits), "total": len(POS_D), "rows": rows},
                  f, indent=1, default=str)
    print(f"results -> {out}")


if __name__ == "__main__":
    main()
