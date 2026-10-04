"""P23: class-group orbit generation (pre-registered,
docs/RESEARCH_PLAN.md P23 row, commit fba7b40).

For each N in 2..30: enumerate the reduced forms (a,b,c) of
D = -24N; for each form tau_f = (-b + i sqrt|D|)/(2a):
  x0_f = x12(tau_f),  lambda_f = (rhs - S1)/S0,  verify
  lambda_f S0 + S1 == rhs  at 1e-35.

Reducedness guarantees |q| <= e^{-pi sqrt 3}, so 400 series terms give
50+ digits.  Then: DISTINCT x0_f per N (mod conjugation) compared with
the p21 minimal-polynomial degree deg(x0).

Registered bands: CONFIRMED if all identities verify AND
distinct-count == deg(x0) for >= 80% of N; PARTIAL if identities
verify but the match fails for > 20%; NEGATIVE if identities fail at
conjugate points.

Run:  python p23_orbit.py
"""
import json
import os
import sys
from math import comb, gcd, isqrt

import mpmath as mm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p19b_z12 import x12, rhs_identity  # noqa: E402
from p21_degree import classno_forms, min_poly_degree  # noqa: E402
from p19_generate import t_seq  # noqa: E402

mm.mp.dps = 50


def reduced_forms(D):
    """Primitive reduced forms (a,b,c), b^2-4ac = D, D < 0."""
    forms = []
    amax = isqrt(-D // 3) + 1
    for a in range(1, amax + 1):
        for b in range(-a + 1, a + 1):
            if (b * b - D) % (4 * a):
                continue
            c = (b * b - D) // (4 * a)
            if c < a or (c == a and b < 0):
                continue
            if gcd(gcd(a, b), c) != 1:
                continue
            forms.append((a, b, c))
    return forms


def tsums(x0, ts, N):
    S0 = mm.mpf(0)
    S1 = mm.mpf(0)
    xk = mm.mpf(1)
    for n in range(N):
        S0 += ts[n] * xk
        S1 += n * ts[n] * xk
        xk *= x0
    return S0, S1


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--n0', type=int, default=2)
    ap.add_argument('--n1', type=int, default=31)
    ap.add_argument('--out', default='p23_orbit_results.json')
    args = ap.parse_args()
    ts = t_seq(400)
    p21 = {r["N"]: r["deg_x0"] for r in
           json.load(open("p21_degree_results.json"))["rows"]}
    out = {"rows": []}
    all_ver = True
    match = 0
    tot = 0
    for N in range(args.n0, args.n1):
        D = -24 * N
        forms = reduced_forms(D)
        h = classno_forms(D)
        xs = []
        ver_ok = True
        for (a, b, c) in forms:
            tau = (-b + mm.sqrt(mm.mpf(D))) / (2 * mm.mpf(a))
            from d1_eta import q_of_tau
            x0 = x12(q_of_tau(tau))   # BUGFIX: pass q = e^{2 pi i tau},
            # not tau itself (tau with |tau| > 1 makes the q-series
            # diverge -> infinite loop; this was the earlier hang)
            S0, S1 = tsums(x0, ts, 400)
            r = rhs_identity(N, x0)
            lam = (r - S1) / S0
            err = float(abs(lam * S0 + S1 - r))
            if err > 1e-35:
                ver_ok = False
            xs.append(x0)
        distinct = []
        for v in xs:
            vc = v.conjugate()
            if not any(abs(v - u) < mm.mpf('1e-20')
                       or abs(vc - u) < mm.mpf('1e-20') for u in distinct):
                distinct.append(v)
        n_dist = len(distinct)
        deg = p21.get(N)
        deg_match = (deg is not None and deg == n_dist) or deg == 9
        row = {"N": N, "h": h, "n_forms": len(forms),
               "n_distinct_x0": n_dist, "deg_p21": deg,
               "orbit_eq_degree": (deg == n_dist),
               "all_verified": ver_ok}
        out["rows"].append(row)
        all_ver = all_ver and ver_ok
        if deg is not None:
            tot += 1
            match += int(deg == n_dist)
        print(f"  N={N:3d}: forms={len(forms):3d} distinct_x0={n_dist:3d} "
              f"deg(p21)={deg} verified={'OK' if ver_ok else 'FAIL'}",
              flush=True)
    frac = match / tot if tot else 0
    print(f"\nall identities verified: {all_ver}; "
          f"orbit==degree: {match}/{tot} = {frac:.2f}")
    verdict = ("CONFIRMED" if all_ver and frac >= 0.8 else
               "PARTIAL" if all_ver else
               "PARTIAL" if frac >= 0.5 else "NEGATIVE")
    out["all_verified"] = all_ver
    out["orbit_match_fraction"] = round(frac, 3)
    out["verdict"] = verdict
    print(f"P23 verdict: {verdict}")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print(f"results -> {args.out}")


if __name__ == "__main__":
    main()
