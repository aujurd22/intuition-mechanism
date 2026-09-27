"""P35-a: blind MDL discovery of the sufficient code (pre-registered,
docs/RESEARCH_PLAN.md P35-a row).

Question: P34-d supplied the 6-line code WITH generator knowledge.
Can the code be DISCOVERED from raw data alone -- no labels, no
generator, no knowledge that 8 classes exist -- by a mechanical
minimum-description-length search?

Protocol:
  - corpus: the 280 appearance-verified families (p34c_corpus.json),
    12-term sequences; the class labels are used ONLY as the check
    column after the search, never inside it;
  - candidate features (blind, threshold-free): for each position
    k in 1..11, eq_k := (s[k] == corpus-mode(s[k])) -- "equality to
    the corpus-modal value" is a natural operator that requires no
    magic constants; plus flip := any sign change;
  - a feature set induces a partition of the corpus into cells;
    two-part code: cost(features) + log2(#cells) per sequence +
    per-cell leave-one-out Gaussian code in the log-magnitude domain
    (sigma floored; singleton cells pay full quantization cost);
  - exhaustive search over feature sets of size 1..5;
  - the winner is then compared to the true 8 classes (check only).

Run:  python p35a_mdl_discover.py
"""
import itertools
import json
import sys

import numpy as np

corpus_file = sys.argv[1] if len(sys.argv) > 1 else "p34c_corpus.json"
max_r = int(sys.argv[2]) if len(sys.argv) > 2 else 4
if corpus_file == "p32f":
    seqs = json.load(open("p32f_design.json"))["sequences"]
    truth = None
else:
    corpus = json.load(open(corpus_file))
    seqs = corpus["families"]
    truth = corpus["truth"]
fids = sorted(seqs)
X = np.array([seqs[f] for f in fids], dtype=float)      # 280 x 12
N = len(fids)

# ---- blind features -------------------------------------------------
feats = {}
for k in range(1, 12):
    uq, counts = np.unique(X[:, k], return_counts=True)
    mode = uq[counts.argmax()]
    feats[f"eq{k}={int(mode)}"] = (X[:, k] == mode)
feats["flip"] = np.any(np.diff(np.sign(X), axis=1) != 0, axis=1)
feat_names = sorted(feats)
F = np.array([feats[n] for n in feat_names]).T         # N x 13 bool
print(f"features ({len(feat_names)}):", feat_names)

LOGX = np.log(np.abs(X) + 1e-300)
QUANT = 0.05          # quantization floor for sigma (log-domain)
S1 = np.stack([LOGX[:, pos].sum() for pos in range(12)])
S2 = np.stack([(LOGX[:, pos] ** 2).sum() for pos in range(12)])


def code_bits(cols):
    """Total two-part code length (vectorized leave-one-out)."""
    used = [feat_names[i] for i, c in enumerate(cols) if c]
    if not used:
        return float("inf"), 0
    key = np.array([feats[n] for n in used]).T
    _, inv = np.unique(key, axis=0, return_inverse=True)
    ncells = inv.max() + 1
    bits = len(used) * np.log2(len(feat_names)) + N * np.log2(ncells)
    m = np.bincount(inv, minlength=ncells).astype(float)
    for pos in range(12):
        x = LOGX[:, pos]
        xx = x * x
        s1 = np.bincount(inv, weights=x, minlength=ncells)
        s2 = np.bincount(inv, weights=xx, minlength=ncells)
        mu = (s1[inv] - x) / (m[inv] - 1)
        var = (s2[inv] - xx) / (m[inv] - 1) - mu * mu
        sd = np.sqrt(np.maximum(var, QUANT ** 2))
        solo = m[inv] <= 1
        rng = max(x.max() - x.min(), QUANT)
        bits += np.sum(np.where(
            solo,
            np.log2(rng * np.sqrt(2 * np.pi * np.e)),
            np.log2(sd * np.sqrt(2 * np.pi * np.e))))
    return float(bits), int(ncells)


results = []
for r in range(1, max_r + 1):
    best = None
    for combo in itertools.combinations(range(len(feat_names)), r):
        cols = [i in combo for i in range(len(feat_names))]
        bits, ncells = code_bits(cols)
        if best is None or bits < best[0]:
            best = (bits, combo, ncells)
    results.append((r, best))
    names = [feat_names[i] for i in best[1]]
    print(f"size {r}: best {best[0]:.0f} bits, {best[2]} cells, {names}")

# full-cell check: winner partition vs the true 8 classes
win = results[-1][1]
cols = [i in win[1] for i in range(len(feat_names))]
bits, ncells = code_bits(cols)
used = [feat_names[i] for i, c in enumerate(cols) if c]
key = np.array([feats[n] for n in used]).T
cells = {}
for i in range(N):
    cells.setdefault(tuple(key[i]), []).append(i)
print(f"\nwinner partition: {len(cells)} cells")
if truth is not None:
    for cell, members in sorted(cells.items()):
        cls = set(tuple(truth[f]["class"]) for f in (fids[i] for i in members))
        print(f"  {cell}: n={len(members)} true-classes={sorted(cls)}")
else:
    for cell, members in sorted(cells.items()):
        print(f"  {cell}: n={len(members)}")
json.dump({"feature_space": feat_names,
           "search": [{"size": r, "bits": b[0], "cells": b[2],
                       "features": [feat_names[i] for i in b[1]]}
                      for r, b in results]},
          open(sys.argv[3] if len(sys.argv) > 3 else "p35a_mdl_results.json", "w"),
          indent=1)
print("saved")
