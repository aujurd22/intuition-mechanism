"""P21: degree-vs-class-number (pre-registered,
docs/RESEARCH_PLAN.md P21 row, commit 2f4e67a).

Classical CM theory: for tau0 = i*sqrt(N/24) (K = Q(sqrt(-6N)), order
discriminant D = -24N), the CM value x0 = x12(tau0) generates over K an
extension whose degree is governed by the ORDER CLASS NUMBER h(D).

  (i)   h(D) computed two ways: reduced-form counting and Kronecker's
        multiplicative formula (cross-checked, registered);
  (ii)  minimal-polynomial degree of x0 via pslq, degrees 1..8;
  (iii) comparison across N = 2..60.

Registered bands: CONFIRMED if deg(x0) in {h, h/2, 2h, h/3} for >= 80%
of N with the pattern named; PARTIAL 50-80%; NEGATIVE otherwise.

Run:  python p21_degree.py
"""
import json
import os
import sys
from math import comb, gcd, isqrt

import mpmath as mm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p19b_z12 import x12  # noqa: E402

mm.mp.dps = 80


def classno_forms(D):
    """h(D): count reduced positive forms b^2 - 4ac = D."""
    if D >= 0 or D % 4 not in (0, 1):
        raise ValueError("bad discriminant")
    h = 0
    a = 1
    amax = isqrt(-D // 3) + 1
    while a <= amax:
        for b in range(-a + 1, a + 1):
            if (b * b - D) % (4 * a):
                continue
            c = (b * b - D) // (4 * a)
            if c < a or (c == a and b < 0):
                continue
            h += 1
        a += 1
    return h


def prime_factors(n):
    fs = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            fs.append(d)
            n //= d
        d += 1
    if n > 1:
        fs.append(n)
    return fs


def fundamental_discriminant(D):
    """D = f^2 * D_K with D_K fundamental; return (D_K, f)."""
    f = 1
    d = D
    while True:
        moved = False
        for p in prime_factors(d):
            if d % (p * p) == 0:
                cand = d // (p * p)
                if cand % 4 in (0, 1):
                    d = cand
                    f *= p
                    moved = True
                    break
        if not moved:
            break
    return d, f


def kronecker_char(D, p):
    if p == 2:
        d = D % 8
        return 0 if d % 2 == 0 else (1 if d in (1, 7) else -1)
    d = D % p
    if d == 0:
        return 0
    ls = pow(d, (p - 1) // 2, p)
    return 1 if ls == 1 else -1


def classno_kron(D):
    """Kronecker: h(f^2 D_K) = h(D_K) * f * prod_{p|f}(1 - chi(p)/p),
    divided by the unit index w (1 unless D_K = -3 or -4)."""
    D_K, f = fundamental_discriminant(D)
    hK = classno_forms(D_K)
    w = 3 if D_K == -3 else 2 if D_K == -4 else 1
    res = hK * f
    for p in sorted(set(prime_factors(f))):
        chi = kronecker_char(D_K, p)
        res = res * (p - chi) // p
    return res // w


def min_poly_degree(v, dmax=8):
    for d in range(1, dmax + 1):
        rel = mm.pslq([v ** k for k in range(d, -1, -1)],
                      tol=mm.mpf('1e-30'), maxcoeff=10 ** 9)
        if rel:
            return d, rel
    return None, None


def main():
    out = {"rows": []}
    n_match = 0
    n_tot = 0
    patterns = {}
    for N in range(2, 61):
        D = -24 * N
        h_forms = classno_forms(D)
        h_kron = classno_kron(D)
        if h_forms != h_kron:
            print(f"  !! N={N}: cross-check FAIL forms={h_forms} "
                  f"kron={h_kron}", flush=True)
        h = h_forms
        q = mm.exp(-2 * mm.pi * mm.sqrt(mm.mpf(N) / 24))
        x0c = x12(q)
        x0 = mm.mpf(x0c.real)
        d, rel = min_poly_degree(x0)
        d = d if d is not None else 9
        pat = ("h" if d == h else
               "h/2" if d * 2 == h else
               "2h" if d == 2 * h else
               "h/3" if d * 3 == h else "other")
        patterns[pat] = patterns.get(pat, 0) + 1
        if pat != "other":
            n_match += 1
        n_tot += 1
        out["rows"].append({"N": N, "D": D, "h": h, "deg_x0": d,
                            "pattern": pat})
        print(f"  N={N:3d} D={D:6d} h={h:4d} deg(x0)={d:3d} {pat}",
              flush=True)

    frac = n_match / n_tot
    print(f"\nmatch (deg in {{h, h/2, 2h, h/3}}): {n_match}/{n_tot} "
          f"= {frac:.2f}")
    print("patterns:", patterns)
    verdict = ("CONFIRMED" if frac >= 0.8 else
               "PARTIAL" if frac >= 0.5 else "NEGATIVE")
    out["verdict"] = verdict
    out["match_fraction"] = round(frac, 3)
    print(f"P21 verdict: {verdict}")

    with open("p21_degree_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print("results -> p21_degree_results.json")


if __name__ == "__main__":
    main()
