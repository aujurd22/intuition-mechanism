"""P43: MI/MDL crossing -- the quantitative version of the decoupling
law (pre-registered, docs/RESEARCH_PLAN.md P43 row).

For each candidate feature and split size m, compute:
  (a) MDL-gain: code-length reduction vs the base code (P35-a's
      two-part Gaussian code on the discovery split);
  (b) mutual information with the true class (analysis-only).

Prediction: spurious mode features have HIGH MDL-gain but LOW MI;
true support features have both; the discovery threshold m* is where
the two orderings agree.

Run:  python p43_mi_mdl.py
"""
import json
import os
import sys
from itertools import combinations
from math import log2

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p40_corpus import build_corpus  # noqa: E402

corpus = build_corpus()
CLASSES = [(str(s), g) for (s, g) in
           [(2, "no"), (2, "alt"), (3, "no"), (3, "alt"),
            (4, "no"), (4, "alt"), (5, "no"), (5, "alt")]]
by_class = {c: [f for f, r in corpus.items() if r["cls"] == c]
            for c in CLASSES}

def extract_features(fids, corpus):
    X = np.array([corpus[f]["seq"] for f in sorted(fids)], dtype=float)
    feats = {}
    for k in range(1, 12):
        uq, cnt = np.unique(X[:, k], return_counts=True)
        mode = uq[cnt.argmax()]
        feats[f"eq{k}={int(mode)}"] = (X[:, k] == mode)
    feats["flip"] = np.any(np.diff(np.sign(X), axis=1) != 0, axis=1)
    return feats, sorted(feats)

def compute_mi_per_feature(fids, corpus, feat_names, feats):
    """Mutual information I(feature ; class) in bits, computed from
    the joint empirical distribution on the given sample set."""
    labels = [corpus[f]["cls"] for f in sorted(fids)]
    mi = {}
    for name in feat_names:
        vals = feats[name]
        # P(feature)
        p_f = np.mean(vals)
        # P(class)
        classes = sorted(set(labels))
        p_c = {c: labels.count(c) / len(labels) for c in classes}
        # I(F;C) = sum_f sum_c P(f,c) log2 P(f,c) / (P(f)P(c))
        mi_bits = 0.0
        for fv in (True, False):
            mask = (vals == fv)
            pf = np.mean(mask)
            if pf == 0:
                continue
            for c in classes:
                pc_mask = np.array([l == c for l in labels])
                pfc = np.mean(mask & pc_mask)
                if pfc == 0:
                    continue
                mi_bits += pfc * np.log2(pfc / (pf * p_c[c]))
        mi[name] = mi_bits
    return mi

# split sizes
results = []
for m in (10, 20, 40, 60):
    for seed in range(5):
        rng = np.random.default_rng(7000 + 100 * m + seed)
        split = []
        for c in CLASSES:
            split += list(rng.choice(by_class[c], size=m, replace=False))
        fids = sorted(split)
        X = np.array([corpus[f]["seq"] for f in fids], dtype=float)
        N = len(fids)
        # features on this split
        feats = {}
        for k in range(1, 12):
            uq, cnt = np.unique(X[:, k], return_counts=True)
            mode = uq[cnt.argmax()]
            feats[f"eq{k}={int(mode)}"] = (X[:, k] == mode)
        feats["flip"] = np.any(np.diff(np.sign(X), axis=1) != 0, axis=1)
        feat_names = sorted(feats)
        # MI per feature (analysis-only, uses labels)
        mi_vals = compute_mi_per_feature(fids, corpus, feat_names, feats)
        # MDL-gain per feature: bits(base) - bits(with this one feature)
        LOGX = np.log(np.abs(X) + 1e-300)
        QUANT = 0.05

        def gaussian_bits(key):
            _, inv = np.unique(key, axis=0, return_inverse=True)
            ncells = inv.max() + 1
            bits = N * log2(ncells)
            m_cnt = np.bincount(inv, minlength=ncells).astype(float)
            for pos in range(12):
                x = LOGX[:, pos]
                s1 = np.bincount(inv, weights=x, minlength=ncells)
                s2 = np.bincount(inv, weights=x*x, minlength=ncells)
                mu = (s1[inv] - x) / np.maximum(m_cnt[inv] - 1, 1)
                var = (s2[inv] - x*x) / np.maximum(m_cnt[inv] - 1, 1) - mu**2
                sd = np.sqrt(np.maximum(var, QUANT**2))
                solo = m_cnt[inv] <= 1
                rngv = max(x.max() - x.min(), QUANT)
                bits += np.sum(np.where(
                    solo, np.log2(rngv * np.sqrt(2*np.pi*np.e)),
                    np.log2(sd * np.sqrt(2*np.pi*np.e))))
            return bits

        base_bits = gaussian_bits(np.zeros((N, 1), dtype=bool))
        gains = {}
        for name in feat_names:
            key = np.array([feats[name]]).T
            g = base_bits - gaussian_bits(key)
            gains[name] = g
        row = {"m": m, "seed": seed,
               "features": {name: {"mi": round(mi_vals[name], 4),
                                    "mdl_gain": round(gains[name], 1)}
                            for name in feat_names}}
        results.append(row)

# correlation: MI vs MDL-gain, per split size
from scipy.stats import spearmanr
print("=== MI vs MDL-gain rank correlation per split size ===")
for m in (10, 20, 40, 60):
    rows = [r for r in results if r["m"] == m]
    mis, gains = [], []
    for r in rows:
        for name, d in r["features"].items():
            mis.append(d["mi"])
            gains.append(d["mdl_gain"])
    rho, p = spearmanr(mis, gains)
    print(f"  m={m:3d}: Spearman(MI, MDL-gain) rho={rho:.3f} p={p:.4f} "
          f"(n={len(mis)} feature instances)")

json.dump(results, open("p43_mi_mdl_results.json", "w"), indent=1)
print("saved p43_mi_mdl_results.json")
