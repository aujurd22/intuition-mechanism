"""P36-a: lambda arithmetic census over N = 2..60 (pre-registered,
docs/RESEARCH_PLAN.md P36-a row).

For each N in the t-family grid, compute x0 = x12(exp(-2 pi sqrt(N/24)))
and lambda = (r - S1)/S0 at 50 digits, then probe the ARITHMETIC DEPTH
of lambda:
  degree 1: lambda = p/q rational (continued fraction at 30 digits,
            denominator <= 10^6);
  degree 2: PSLQ finds an integer relation a + b lambda + c lambda^2
            with small coefficients (height <= 10^4);
  degree 3: cubic relation (height <= 10^3);
  else:     "no small relation found at 50 digits".

Known anchor rows (P25-b / literature): N=3,5,7,13,17 have RATIONAL
lambda (degree 1) -- these are the literature-published rows; N=11,19,23
have QUADRATIC lambda (degree 2) -- the machine-found rows.  The census
asks whether the hierarchy continues (cubic rows = one level deeper
than the literature).

Run:  python p36a_lambda_census.py
"""
import json
import os
import sys
from math import comb

import mpmath as mm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p19b_z12 import x12  # noqa: E402

mm.mp.dps = 50


def t_seq_n(n):
    v = 0
    for k in range(n // 2 + 1):
        v += comb(n, 2 * k) * comb(2 * k, k) ** 2 * comb(2 * n - 4 * k,
                                                         n - 2 * k)
    return v


TS = [mm.mpf(t_seq_n(n)) for n in range(400)]


def params_for(N):
    q = mm.exp(-2 * mm.pi * mm.sqrt(mm.mpf(N) / 24))
    x0 = mm.mpf(x12(q).real)
    S0 = sum(TS[n] * x0 ** n for n in range(400))
    S1 = sum(n * TS[n] * x0 ** n for n in range(400))
    r = (1 / (2 * mm.pi)) * mm.sqrt(mm.mpf(24) / N) / \
        mm.sqrt((1 + 4 * x0) * (1 - 4 * x0) * (1 - 8 * x0))
    lam = (r - S1) / S0
    return x0, lam


def rational_or_none(lam, max_den=10 ** 6, min_digits=25):
    """Continued-fraction rational recovery; None if none fits."""
    x = +lam
    p0, q0, p1, q1 = 0, 1, 1, 0
    while True:
        a = int(mm.floor(x))
        p2, q2 = a * p1 + p0, a * q1 + q0
        if q2 > max_den:
            return None
        approx = mm.mpf(p2) / q2
        if abs(approx - lam) < mm.mpf(10) ** (-min_digits):
            return p2, q2
        p0, q0, p1, q1 = p1, q1, p2, q2
        frac = x - a
        if frac < mm.mpf(10) ** (-min_digits):
            return None
        x = 1 / frac


def poly_rel_or_none(lam, degree, height):
    """PSLQ integer relation sum c_i lam^i = 0 with coefficients bounded
    by `height` (mpmath's pslq; sympy 1.13 has no top-level pslq)."""
    import mpmath as mpm
    vec = [mpm.mpf(1)] + [lam ** k for k in range(1, degree + 1)]
    try:
        rel = mpm.pslq(vec, tol=mpm.mpf(10) ** -30, maxcoeff=height,
                       maxsteps=1000)
        return [int(c) for c in rel] if rel else None
    except Exception:
        return None


def main():
    rows = []
    for N in range(2, 201):
        try:
            x0, lam = params_for(N)
        except Exception as ex:
            rows.append({"N": N, "error": str(ex)})
            continue
        if abs(x0) >= mm.mpf(1) / 8:
            rows.append({"N": N, "x0": mm.nstr(x0, 20),
                         "note": "outside radius 1/8"})
            continue
        rat = rational_or_none(lam)
        if rat:
            deg, poly = 1, [rat[1], rat[0]]        # q x + p
            height = max(abs(rat[0]), rat[1])
        else:
            poly = poly_rel_or_none(lam, 2, 10 ** 6)
            if poly:
                deg, height = 2, max(abs(c) for c in poly)
            else:
                poly = poly_rel_or_none(lam, 3, 10 ** 6)
                if poly:
                    deg, height = 3, max(abs(c) for c in poly)
                else:
                    deg, height, poly = None, None, None
        row = {"N": N, "x0": mm.nstr(x0, 25), "lambda": mm.nstr(lam, 30),
               "deg": deg}
        if poly:
            row["poly"] = poly
            row["height"] = height
        rows.append(row)
        print(f"N={N:3d} x0={mm.nstr(x0, 12):14s} deg={deg} "
              f"poly={poly if poly else '-'}", flush=True)
    json.dump(rows, open("p36a_lambda_census.json", "w"), indent=1)
    from collections import Counter
    degs = Counter(r.get("deg") for r in rows if "deg" in r)
    print("\ncensus:", dict(sorted(degs.items(), key=lambda x: (x[0] is None, x[0]))))
    print("saved p36a_lambda_census.json")


if __name__ == "__main__":
    main()
