"""P29: universal-function G shape characterization (pre-registered,
docs/RESEARCH_PLAN.md P29 row, commit fa54e1b).

From the P20 census artifact's 59 (x0, lambda) pairs, fit candidate
closed forms for the universal lambda function G(x0):

  (i)   linear:      lambda = a + b*x0
  (ii)  square-root: lambda = a + b*sqrt(x0)
  (iii) quadratic:   lambda = a + b*x0 + c*x0^2

Registered bands: CONFIRMED if any form fits all 59 pairs with max
relative residual < 1e-6; PARTIAL < 1e-2; NEGATIVE otherwise.

Run:  python p29_gshape.py
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    p20 = json.load(open("p20_census_results.json"))
    pts = []
    for row in p20["rows"]:
        if N := row.get("N"):
            pass
        if "x" not in row or "lambda" not in row:
            continue
        try:
            x0 = float(row["x"])
            lam = float(row["lambda"])
        except (TypeError, ValueError):
            continue
        if x0 > 0 and lam > 0:
            pts.append((N, x0, lam))
    print(f"census points: {len(pts)}")

    xs = np.array([p[1] for p in pts])
    ls = np.array([p[2] for p in pts])

    def fit_residual(name, feats):
        A = np.vstack(feats + [np.ones(len(xs))]).T
        coef, *_ = np.linalg.lstsq(A, ls, rcond=None)
        pred = A @ coef
        res = np.abs(pred - ls) / np.abs(ls)
        print(f"  {name:28s} max_rel_resid = {res.max():.3e}")
        return res.max(), coef

    results = {}
    r1 = fit_residual("linear a+b*x", [xs])
    results["linear"] = r1[0]
    r2 = fit_residual("sqrt a+b*sqrt(x)", [np.sqrt(xs)])
    results["sqrt"] = r2[0]
    r3 = fit_residual("quadratic a+b*x+c*x^2", [xs, xs ** 2])
    results["quadratic"] = r3[0]
    r4 = fit_residual("sqrt a+b*sqrt+c*x", [np.sqrt(xs), xs])
    results["sqrt+lin"] = r4[0]

    best = min(results, key=results.get)
    print(f"\nbest form: {best} (max_rel_resid = {results[best]:.3e})")
    verdict = ("CONFIRMED" if results[best] < 1e-6 else
               "PARTIAL" if results[best] < 1e-2 else "NEGATIVE")
    print(f"P29 verdict: {verdict}")

    with open("p29_gshape_results.json", "w", encoding="utf-8") as f:
        json.dump({"results": results, "best_form": best,
                   "verdict": verdict}, f, indent=1)
    print("results -> p29_gshape_results.json")


if __name__ == "__main__":
    main()
