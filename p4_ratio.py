"""P4 v1: ratio-shape representations -- can second-order features recover
the signature that first-order features missed?

Mechanistic background: for c_k = (A+Bk) * H_k * z^k with
H_k = (1/2)_k (1/s)_k (1-1/s)_k / (k!)^3, the log-ratio
log(c_{k+1}/c_k) = log z + (B-slope term) + a Pochhammer 1/k correction
whose FIRST-order coefficient is s-INDEPENDENT ((1/s)+(1-1/s) = 1 cancels
the (1/2)+(1) parts...). The signature enters only at O(1/k^2) via
(1/2 - 1/s)^2. So: centered first differences should still fail;
second differences carry the s-signal in principle.

Representations:
  d1 : centered first differences of log|c_k|   (30-dim)
  d2 : second differences of log|c_k|           (29-dim)
  raw+d1+d2 concat
Baselines: random; chance same-s = 0.368.

Run:  python p4_ratio.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t0_scan import ari  # noqa: E402
from p4_anchors import SERIES, NC  # noqa: E402


def build_sequences():
    from mpmath import mp
    mp.dps = 40
    rows, seqs = [], []
    for eq, s, A, B, z, kind in SERIES:
        c = []
        for k in range(NC):
            term = (A(k) if k == 0 else A(k) + B(k) * k) * z(k) ** k
            if kind == "alt" and k >= 1:
                term = (-1) ** k * term
            c.append(float(term))
        c = np.array(c, dtype=np.float64)
        c = c / (np.linalg.norm(c) + 1e-300)
        seqs.append(c)
        rows.append({"eq": eq, "s": s})
    return rows, np.stack(seqs)


def main():
    rows, seqs = build_sequences()
    s_arr = np.array([r["s"] for r in rows])
    labs = np.array([r["eq"] for r in rows])

    lnc = np.log(np.abs(seqs) + 1e-300)
    d1 = np.diff(lnc, axis=1)                      # first differences
    d1c = d1 - d1.mean(axis=1, keepdims=True)      # remove the z level
    d2 = np.diff(d1, axis=1)                       # second differences

    from sklearn.cluster import KMeans

    def knn(z_all, k=3):
        zn = z_all / (np.linalg.norm(z_all, axis=1, keepdims=True) + 1e-12)
        sim = zn @ zn.T
        np.fill_diagonal(sim, -np.inf)
        idx = np.argsort(-sim, axis=1)[:, :k]
        h1 = h3 = 0
        for i, nb in enumerate(idx):
            same = (s_arr[nb] == s_arr[i]).astype(int)
            h1 += int(same[0])
            h3 += int(same.sum() >= 1)
        return h1, h3

    rng = np.random.default_rng(0)
    print(f"anchors: {len(rows)}; chance same-s (avg): 0.368")
    for name, rep in (("d1_centered", d1c.astype(np.float32)),
                      ("d2", d2.astype(np.float32)),
                      ("d1+d2", np.concatenate([d1c, d2], axis=1).astype(np.float32)),
                      ("random", rng.standard_normal(d1c.shape).astype(np.float32))):
        h1, h3 = knn(rep, 3)
        km = KMeans(n_clusters=4, n_init=20, random_state=0).fit(rep)
        a = ari(km.labels_, s_arr)
        print(f"  {name:11s} hit@1={h1}/17  hit@3={h3}/17  ARI(vs s)={a:+.3f}")

    with open("p4_ratio_results.json", "w", encoding="utf-8") as f:
        json.dump({"note": "P4 v1 ratio-shape probe", "rows": rows}, f,
                  indent=1, default=str)
    print("results -> p4_ratio_results.json")


if __name__ == "__main__":
    import json  # noqa: F401
    main()
