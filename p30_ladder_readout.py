"""P30: ladder-aware global readout (pre-registered,
docs/RESEARCH_PLAN.md P30 row, commit 0faaad2).

Compare the best possible GLOBAL clustering that uses the 1-D
residual-level ladder (the invariant axis per the Gamma-proposition)
against the 24-D k-means used in P15/P19-P27:

  arm A: 24-D k-means(k=4) on row-normalized residuals   [P15 caliber]
  arm B: 1-D k-means(k=4) on the sorted levels           [ladder readout]
  arm C: optimal 4-interval partition of sorted levels via DP
         (Fisher-Jenks exact segmentation, k=4)          [the ceiling arm]

If the ladder readout (B/C) dominates A by > 0.1 ARI, the P15-era
global-readout gap is a CLUSTERING-MODEL limitation — closable by
ladder-aware readouts; if B/C do not dominate, the gap is in the
per-sample level estimates themselves (information-limited).

Run:  python p30_ladder_readout.py
"""
import json
import os
import sys

import mpmath as mm
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p19b_z12 import x12, rhs_identity  # noqa: E402
from p15_envelope import make_dataset, poch_cum, blind_envelope  # noqa: E402
from t0_scan import ari  # noqa: E402

SIGS = (2, 3, 4, 6)
NC = 24


def t_poch(k, s):
    if k == 0:
        return 1.0
    out = 1.0
    for j in range(k):
        out *= (j + 0.5) * (j + 1 / s) * (j + 1 - 1 / s) / (j + 1) ** 3
    return out


def main():
    # counterfactual data, same as P15 (seed 0)
    rng = np.random.default_rng(0)
    X, y, nuis = [], [], []
    for si, s in enumerate(SIGS):
        Hs = np.array([mm.mpf(1)])
        H = [1.0]
        for k in range(1, NC):
            num = 1.0
            for j in range(k):
                num *= (j + 0.5) * (j + 1 / s) * (j + 1 - 1 / s) / (j + 1) ** 3
            H.append(num)
        Hs = np.array(H)
        for _ in range(60):
            A = rng.uniform(0.5, 5.0)
            B = rng.uniform(0.0, 3.0)
            z = rng.uniform(0.05, 0.45)
            kk = np.arange(NC)
            c = (A + B * kk) * Hs * z ** kk
            c = c / (np.linalg.norm(c) + 1e-300)
            X.append(c)
            y.append(si)
            nuis.append([A, B, z])
    X = np.stack(X).astype(np.float32)
    y = np.array(y)
    nuis = np.array(nuis, dtype=np.float32)
    print(f"counterfactual data: {len(X)} samples, NC={NC}")

    # blind envelope fit per sample (P15 caliber): 3-param log-domain fit
    k = np.arange(NC, dtype=float)
    reps = []
    for c in X:
        lc = np.log(np.abs(c) + 1e-300)
        M = np.stack([np.ones_like(k), k, np.log(k + 1)], axis=1)
        coef, *_ = np.linalg.lstsq(M, lc, rcond=None)
        env = np.exp(M @ coef)
        reps.append(np.abs(c) / (env + 1e-300))
    R = np.stack(reps)
    lvl = np.log(R.mean(1) + 1e-300)          # the 1-D ladder value
    Rn = R / (np.linalg.norm(R, axis=1, keepdims=True) + 1e-12)

    # arm A: 24-D k-means (row-normalized), the P15 caliber
    kmA = KMeans(n_clusters=4, n_init=10, random_state=0).fit(Rn)
    ariA = adjusted_rand_score(y, kmA.labels_)

    # arm B/C: 1-D ladder readout — optimal contiguous 4-partition via DP
    order = np.argsort(lvl)
    ls = lvl[order]
    ys = y[order]
    # DP for optimal contiguous 4-segment partition minimizing within-seg
    # variance (Jenks-style, exact for 1-D)
    n = len(ls)
    P = np.zeros(n + 1)
    P[1:] = np.cumsum(ls)
    Q = np.zeros(n + 1)
    Q[1:] = np.cumsum(ls ** 2)
    INF = 1e18
    # dp[seg][j]: min cost of partitioning ls[0:j] into seg intervals
    dp = np.full((5, n + 1), INF)
    dp[0, 0] = 0.0
    back = np.zeros((5, n + 1), dtype=int)
    for seg in range(1, 5):
        for j in range(seg, n + 1):
            best, arg = INF, 0
            for i in range(seg - 1, j):
                m = j - i
                segcost = (Q[j] - Q[i]) - (P[j] - P[i]) ** 2 / m
                v = dp[seg - 1, i] + segcost
                if v < best:
                    best, arg = v, i
            dp[seg, j] = best
            back[seg, j] = arg
    labels_sorted = np.zeros(n, dtype=int)
    j = n
    for seg in range(4, 0, -1):
        i = back[seg, j]
        labels_sorted[i:j] = seg - 1
        j = i
    # map back to original order
    labels = np.empty(n, dtype=int)
    labels[order] = labels_sorted[np.argsort(order)]
    ariC = adjusted_rand_score(y, labels)
    print(f"arm C (1-D DP 4-interval ladder): ARI = {ariC:.3f}")
    print(f"arm A (24-D k-means):             ARI = {ariA:.3f}")

    # also: 1-D DP with k=4 vs the CCK k-means for reference
    print(f"improvement: {ariC - ariA:+.3f}")

    verdict = ("CONFIRMED" if ariC - ariA > 0.1 else
               "PARTIAL" if abs(ariC - ariA) <= 0.1 else "NEGATIVE")
    print(f"P30 verdict: {verdict}")

    out = {"ariA_24d_kmeans": round(float(ariA), 3),
           "ariC_1d_dp4": round(float(ariC), 3),
           "improvement": round(float(ariC - ariA), 3),
           "verdict": verdict}
    with open("p30_ladder_readout_results.json", "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("results -> p30_ladder_readout_results.json")


if __name__ == "__main__":
    main()
