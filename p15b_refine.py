"""P15-b: level-protected envelope refinement (pre-registered, see
docs/RESEARCH_PLAN.md P15-b row, commit b233de5).

Closes P15's residual gap: after the pass-1 generic envelope fit, the
per-sample (A+Bk)-curvature survives as ~0.003 log-level noise because
{1, k, log(k+1)} cannot separate log(A+Bk) from log H_s's power law.
REFINEMENT (registered): re-fit the residual with the SAME generic basis
minus the intercept -- {k, log(k+1)} -- and subtract; iterate twice.
An unrestricted refit (with intercept) is degenerate: it fits away ALL
discrete structure for ANY data.  Protecting the per-sample constant
level is the minimal non-degenerate iteration: it cancels exactly the
k-dependent nuisance while the candidate invariant (a per-sample level)
survives, scaled by a fixed shared shape vector.

Also computes the registered diagnostic: adjacent-class gap compression
in pooled-sigma on the 1-D residual-level ladder.

Run:  python p15b_refine.py
"""
import json
import os
import sys

import numpy as np
from sklearn.cluster import KMeans

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t0_scan import ari  # noqa: E402
from p15_envelope import (SIGS, blind_envelope, knn_metrics,  # noqa: E402
                          make_dataset, poch_cum, poch_ratio)


def refine(r, basis_cols=("lin", "logk"), passes=2):
    """Intercept-free generic refit of the residual; protect the level."""
    k = np.arange(r.shape[1], dtype=float)
    cols = [k, np.log(k + 1)]
    M = np.stack(cols, axis=1)                      # no ones-column
    out = r.copy()
    for _ in range(passes):
        nu = out - (M @ np.linalg.lstsq(M, out.T, rcond=None)[0]).T
        out = nu
    return out


def ladder_gaps(B, y):
    """1-D residual-level ladder: class means +- std and adjacent gaps in
    pooled sigma (registered diagnostic)."""
    lvl = np.log(B.mean(1) + 1e-300)
    mus, sds = [], []
    for si in range(len(SIGS)):
        v = lvl[y == si]
        mus.append(v.mean())
        sds.append(v.std() + 1e-12)
    gaps = []
    for i in range(len(mus) - 1):
        pooled = np.sqrt((sds[i] ** 2 + sds[i + 1] ** 2) / 2)
        gaps.append(round((mus[i + 1] - mus[i]) / pooled, 2))
    return {"class_levels": [round(m, 4) for m in mus],
            "class_stds": [round(s, 4) for s in sds],
            "adjacent_gaps_sigma": gaps}


def readout(R, y):
    m = knn_metrics(R.astype(np.float64), y)
    Rn = R / (np.linalg.norm(R, axis=1, keepdims=True) + 1e-12)
    km = KMeans(n_clusters=len(SIGS), n_init=10,
                random_state=0).fit(Rn)
    m["ari"] = round(ari(km.labels_, y), 3)
    return m


def main():
    results = []
    for fam_name, poch in (("cumulative-TRUE", poch_cum),
                           ("ratio-form(p14)", poch_ratio)):
        X, y, nuis = make_dataset(poch, seed=0)
        rng = np.random.default_rng(1)
        ys = rng.permutation(y)
        print(f"\n=== family: {fam_name} ===", flush=True)

        pass1 = np.stack([blind_envelope(c) for c in X])
        arms = {
            "pass1 (P15)": pass1,
            "refined x1": refine(pass1, passes=1),
            "refined x2": refine(pass1, passes=2),
        }
        rows = {}
        for name, R in arms.items():
            rows[name] = readout(R, y)
            print(f"  {name:12s} hit@1={rows[name]['hit1']:.3f} "
                  f"frac3={rows[name]['frac3']:.3f} "
                  f"ARI={rows[name]['ari']:.3f}", flush=True)
        rows["ladder_pass1"] = ladder_gaps(pass1, y)
        rows["ladder_refined"] = ladder_gaps(arms["refined x2"], y)
        sh = knn_metrics(arms["refined x2"].astype(np.float64), ys)
        print(f"  shuffled(refined) hit@1={sh['hit1']:.3f}")

        verdict = ("CONFIRMED" if rows["refined x2"]["hit1"] >= 0.90
                   and rows["refined x2"]["ari"] >= 0.6
                   else "PARTIAL" if rows["refined x2"]["hit1"] > 0.45
                   else "NEGATIVE")
        print(f"  P15-b verdict ({fam_name}): {verdict}")
        results.append({"family": fam_name, "rows": rows,
                        "shuffled_hit1": sh["hit1"], "verdict": verdict})

    print(f"\nP15-b final verdict (true family): {results[0]['verdict']}")
    with open("p15b_refine_results.json", "w", encoding="utf-8") as f:
        json.dump({"results": results}, f, indent=1, default=str)
    print("results -> p15b_refine_results.json")


if __name__ == "__main__":
    main()
