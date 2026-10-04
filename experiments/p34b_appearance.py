"""P34-b: appearance-truth window curve (pre-registered,
docs/RESEARCH_PLAN.md P34-b row, commit 78e4510).

Fixes P34's root cause: class truth re-defined by SEQUENCE-APPEARANCE
clustering on the 4800-family corpus (normalized 12-term shape vectors,
k-means k=8, seed fixed).  The construction-parameter truth is retained
only as a cross-check.

Then the window-curve test with appearance-truth: 7 windows x 25
hold-out trials, subject assigns each hold-out to the context cluster
it matches.

Run:  python p34b_appearance.py
"""
import json
import os
import sys

import numpy as np
from sklearn.cluster import KMeans

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SEED = 777
K = 8


def main():
    d = json.load(open('p32f_design.json'))
    seqs = d['sequences']
    fids = sorted(seqs.keys())
    # shape vectors: normalized 12-term sequences (log-magnitude,
    # sign preserved)
    feats = []
    for fid in fids:
        s = np.array(seqs[fid], dtype=float)
        mag = np.log(np.abs(s) + 1.0)
        sgn = np.sign(s)
        feats.append(mag * sgn)
    X = np.array(feats)
    print(f"feature matrix: {X.shape}")

    km = KMeans(n_clusters=K, n_init=10, random_state=SEED).fit(X)
    labels = km.labels_

    # cluster coherence check: mean within-class vs between-class
    # distance on the first two principal components is skipped; simple
    # proxy: average pairwise cosine similarity within vs across
    from sklearn.metrics import silhouette_score
    sil = float(silhouette_score(X, labels, sample_size=500,
                                 random_state=SEED))
    print(f"cluster silhouette: {sil:.3f}")

    # save appearance-truth
    app_truth = {fid: int(l) for fid, l in zip(fids, labels)}
    json.dump({"clusters": app_truth, "silhouette": sil},
              open('p34b_appearance_truth.json', 'w'), indent=1)
    print("appearance truth -> p34b_appearance_truth.json")

    # window-curve trials: 7 windows x 25 trials, hold-out from one
    # appearance class, context from another
    rng = np.random.default_rng(SEED)
    cls_ids = {}
    for fid, l in app_truth.items():
        cls_ids.setdefault(l, []).append(fid)
    design = {}
    for w in (4, 5, 6, 7, 10, 12, 16):
        trials = []
        for t in range(25):
            truth_cls = int(rng.integers(0, K))
            distract = truth_cls
            while distract == truth_cls:
                distract = int(rng.integers(0, K))
            pool_t = cls_ids[truth_cls]
            holdout = pool_t[int(rng.integers(0, len(pool_t)))]
            ctx = list(rng.choice(cls_ids[distract], 3, replace=False))
            trials.append({"trial": t + 1, "holdout": holdout,
                           "context": ctx,
                           "truth_class": truth_cls,
                           "distract_class": distract})
        design[f"w{w}"] = trials
    json.dump(design, open('p34b_window_design.json', 'w'), indent=1,
              default=str)
    print("window design -> p34b_window_design.json "
          "(7 windows x 25 trials, appearance truth)")


if __name__ == "__main__":
    main()
