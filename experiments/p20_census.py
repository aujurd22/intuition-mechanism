"""P20: algebraicity census of (x_N, lambda_N) for N = 1..60
(pre-registered, docs/RESEARCH_PLAN.md P20 row, commit 7229102).

Extends the CWZ Table 1 (5 rational rows + N=1 divergent) to a
systematic census.  For each N:
  q     = e^{-2 pi sqrt(N/24)}
  x_N   = x12(q)          (level-12 machinery, verified in P19-b)
  rhs   = (1/(2 pi)) sqrt(24/N) / sqrt((1+4x)(1-4x)(1-8x))
  S0,S1 = t-sums at x_N
  lambda= (rhs - S0)/S1
Classification: rational / quadratic (pslq) / higher, for x_N and
lambda_N.  Registered checks: N in {3,5,7,13,17} must reproduce the
CWZ rational pairs; N=1 is the divergent boundary (x = 1/8).

Run:  python p20_census.py
"""
import json
import os
import sys
from math import comb

import mpmath as mm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p19b_z12 import x12, tsums, rhs_identity  # noqa: E402

mm.mp.dps = 50


def classify(v, tol=mm.mpf('1e-25')):
    """Return (tag, detail) for an mpf value."""
    rel1 = mm.pslq([v, mm.mpf(1)], tol=tol, maxcoeff=10 ** 6)
    if rel1:
        a, b = rel1
        from math import gcd
        g = gcd(abs(a), abs(b)) or 1
        return "rational", f"{-b // g}/{a // g}" if a else "0"
    rel2 = mm.pslq([v * v, v, mm.mpf(1)], tol=tol, maxcoeff=10 ** 6)
    if rel2:
        a, b, c = rel2
        return "quadratic", f"{a}v^2+{b}v+{c}=0"
    return "higher", ""


def main():
    out = {"rows": [], "cwz_check": {}}
    cwz_rational = {3: "1/12", 5: "1/20", 7: "1/32", 13: "1/104",
                    17: "1/200"}
    cwz_lambda = {3: "1/4", 5: "1/4", 7: "5/21", 13: "1/5",
                  17: "143/238"}
    ok_cwz = True
    for N in range(1, 61):
        q = mm.exp(-2 * mm.pi * mm.sqrt(mm.mpf(N) / 24))
        row = {"N": N}
        if N == 1:
            row["note"] = "x = 1/8 = radius (divergent series; CWZ agree)"
            out["rows"].append(row)
            print(f"  N={N:3d}: boundary (x=1/8, divergent)", flush=True)
            continue
        x0 = x12(q)
        if abs(x0.imag) > mm.mpf('1e-30'):
            row["x"] = "complex"
            out["rows"].append(row)
            print(f"  N={N:3d}: complex x", flush=True)
            continue
        x0 = mm.mpf(x0.real)
        tag_x, det_x = classify(x0)
        S0, S1 = tsums(x0, N=700)
        r = rhs_identity(N, x0)
        lam = mm.mpf(((r - S1) / S0).real)
        tag_l, det_l = classify(lam)
        row.update({"x": mm.nstr(x0, 25), "x_class": tag_x,
                    "x_detail": det_x,
                    "lambda": mm.nstr(lam, 30), "lambda_class": tag_l,
                    "lambda_detail": det_l})
        if N in cwz_rational:
            from fractions import Fraction
            fr = Fraction(cwz_rational[N])
            match = abs(x0 - mm.mpf(fr.numerator) / mm.mpf(fr.denominator)) \
                < mm.mpf('1e-30')
            row["cwz_rational_match"] = bool(match)
            ok_cwz = ok_cwz and match
        out["rows"].append(row)
        print(f"  N={N:3d}: x[{tag_x}: {det_x[:28]}] "
              f"lam[{tag_l}: {det_l[:28]}]", flush=True)

    n_rat_x = sum(1 for r in out["rows"] if r.get("x_class") == "rational")
    n_rat_l = sum(1 for r in out["rows"] if r.get("lambda_class")
                  == "rational")
    n_quad = sum(1 for r in out["rows"] if r.get("x_class") == "quadratic")
    print(f"\ncensus: rational-x N = {n_rat_x}, quadratic-x = {n_quad}, "
          f"rational-lambda = {n_rat_l}, total = 60")
    print(f"CWZ rows reproduced: {ok_cwz}")
    out["summary"] = {"rational_x": n_rat_x, "quadratic_x": n_quad,
                      "rational_lambda": n_rat_l, "cwz_ok": ok_cwz}
    verdict = ("CONFIRMED" if ok_cwz and n_rat_x >= 5
               else "PARTIAL" if ok_cwz else "NEGATIVE")
    out["verdict"] = verdict
    print(f"P20 verdict: {verdict}")

    with open("p20_census_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print("results -> p20_census_results.json")


if __name__ == "__main__":
    main()
