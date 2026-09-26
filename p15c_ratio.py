"""P15-c: ratio-domain envelope reconstruction (pre-registered,
docs/RESEARCH_PLAN.md P15-c row, commit 49fb0e8).

Obstruction from P15-b: the direct log-domain envelope fit carries
z-MODULATED per-sample bias (z spans 9x -> the OLS effective k-weighting
varies with z) that lands on the invariant's own axis; no same-span
refit can remove it.

Fix (registered): work in the RATIO domain where z^k is EXACTLY the
intercept.  Per sample:
  rho_k = log(c_{k+1}/c_k)                (k = 0..NC-2)
  fit   rho ~ b0 + b1/(k+1) + b2/(k+1)^2 + b3/(k+1)^3   (OLS)
  cumulate: E_0 = 0, E_{k+1} = E_k + fit_k
  u = |c| / exp(E)                        (the representation)

Readout identical to P15: row-normalized kNN hit@1/frac3 + kmeans ARI
+ the 1-D ladder-gap diagnostic.  Registered bands on the TRUE family:
CONFIRMED ARI >= 0.6 with hit@1 >= 0.90; PARTIAL ARI in [0.325, 0.6);
NEGATIVE ARI <= 0.325.

Run:  python p15c_ratio.py
"""
import json
import os
import sys

import numpy as np
from sklearn.cluster import KMeans

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t0_scan import ari  # noqa: E402
from p15_envelope import (SIGS, knn_metrics, make_dataset,  # noqa: E402
                          poch_cum, poch_ratio)
from p15b_refine import ladder_gaps  # noqa: E402


def ratio_domain_residual(c):
    k = np.arange(len(c) - 1, dtype=float)
    with np.errstate(divide="ignore"):
        rho = np.diff(np.log(np.abs(c) + 1e-300))
    M = np.stack([np.ones_like(k), 1 / (k + 1), 1 / (k + 1) ** 2,
                  1 / (k + 1) ** 3], axis=1)
    b, *_ = np.linalg.lstsq(M, rho, rcond=None)
    fit = M @ b
    E = np.concatenate([[0.0], np.cumsum(fit)])       # length NC
    return np.abs(c) / np.exp(E)


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
        X, y, _ = make_dataset(poch, seed=0)
        rng = np.random.default_rng(1)
        ys = rng.permutation(y)
        print(f"\n=== family: {fam_name} ===", flush=True)

        U = np.stack([ratio_domain_residual(c) for c in X])
        m = readout(U, y)
        print(f"  ratio-domain  hit@1={m['hit1']:.3f} "
              f"frac3={m['frac3']:.3f} ARI={m['ari']:.3f}", flush=True)
        lad = ladder_gaps(U, y)
        print(f"  ladder: levels={lad['class_levels']} "
              f"stds={lad['class_stds']} gaps={lad['adjacent_gaps_sigma']}")
        sh = knn_metrics(U.astype(np.float64), ys)
        print(f"  shuffled hit@1={sh['hit1']:.3f}")

        verdict = ("CONFIRMED" if m["hit1"] >= 0.90 and m["ari"] >= 0.6
                   else "PARTIAL" if m["ari"] > 0.325
                   else "NEGATIVE")
        print(f"  P15-c verdict ({fam_name}): {verdict}")
        results.append({"family": fam_name, "metrics": m, "ladder": lad,
                        "shuffled_hit1": sh["hit1"], "verdict": verdict})

    print(f"\nP15-c final verdict (true family): {results[0]['verdict']}")
    with open("p15c_ratio_results.json", "w", encoding="utf-8") as f:
        json.dump({"results": results}, f, indent=1, default=str)
    print("results -> p15c_ratio_results.json")


if __name__ == "__main__":
    main()
