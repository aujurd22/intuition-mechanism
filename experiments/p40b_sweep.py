"""P40-b: discovery sample-size sweep (registered as the P40 fix).

For split sizes m in {10, 20, 40, 60} families per class and 5 seeds
each: run the blind MDL search on the split, freeze the winner, and
score (a) code identity vs the 4800-corpus reference tree features
{eq2=6, eq3=20, eq4=70, flip}, (b) transfer purity (all cells pure
over the FULL corpus).  Hypothesis: there is a sample-size threshold
below which the frozen code overfits (spurious mode features) and
above which it is stable.

Run:  python p40b_sweep.py
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
CLASSES = [("2", "no"), ("2", "alt"), (3, "no"), (3, "alt"),
           ("4", "no"), ("4", "alt"), (5, "no"), (5, "alt")]
CLASSES = [(str(s), g) for (s, g) in
           [(2, "no"), (2, "alt"), (3, "no"), (3, "alt"),
            (4, "no"), (4, "alt"), (5, "no"), (5, "alt")]]
by_class = {c: [f for f, r in corpus.items() if r["cls"] == c]
            for c in CLASSES}
REFERENCE = {"eq2=6", "eq3=20", "eq4=70", "flip"}


def mdl_search(split_fids, X, feat_names, feats, LOGX, N, QUANT=0.05):
    best = None
    for r in range(1, 5):
        for combo in combinations(range(len(feat_names)), r):
            used = [feat_names[i] for i in combo]
            key = np.array([feats[n] for n in used]).T
            _, inv = np.unique(key, axis=0, return_inverse=True)
            ncells = inv.max() + 1
            bits = len(used) * log2(len(feat_names)) + N * log2(ncells)
            m = np.bincount(inv, minlength=ncells).astype(float)
            for pos in range(12):
                x = LOGX[:, pos]
                s1 = np.bincount(inv, weights=x, minlength=ncells)
                s2 = np.bincount(inv, weights=x * x, minlength=ncells)
                mu = (s1[inv] - x) / np.maximum(m[inv] - 1, 1)
                var = (s2[inv] - x * x) / np.maximum(m[inv] - 1, 1) - mu ** 2
                sd = np.sqrt(np.maximum(var, QUANT ** 2))
                solo = m[inv] <= 1
                rngv = max(x.max() - x.min(), QUANT)
                bits += np.sum(np.where(
                    solo, np.log2(rngv * np.sqrt(2 * np.pi * np.e)),
                    np.log2(sd * np.sqrt(2 * np.pi * np.e))))
            if best is None or bits < best[0]:
                best = (bits, used)
    return best[1]


def transfer_purity(win_features, corpus):
    def sig(seq):
        out = []
        for name in win_features:
            if name.startswith("eq"):
                k = int(name.split("=")[0][2:])
                c = int(name.split("=")[1])
                out.append(seq[k] == c)
            else:
                out.append(any((seq[i] > 0) != (seq[i + 1] > 0)
                               for i in range(len(seq) - 1)))
        return tuple(out)
    from collections import defaultdict
    cells = defaultdict(set)
    for fid, r in corpus.items():
        cells[sig(r["seq"])].add(r["cls"])
    return len(cells), all(len(v) == 1 for v in cells.values())


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
        feats = {}
        for k in range(1, 12):
            uq, counts = np.unique(X[:, k], return_counts=True)
            mode = uq[counts.argmax()]
            feats[f"eq{k}={int(mode)}"] = (X[:, k] == mode)
        feats["flip"] = np.any(np.diff(np.sign(X), axis=1) != 0, axis=1)
        feat_names = sorted(feats)
        LOGX = np.log(np.abs(X) + 1e-300)
        win = mdl_search(split, X, feat_names, feats, LOGX, N)
        ncells, pure = transfer_purity(win, corpus)
        exact = set(win) == REFERENCE
        results.append({"m_per_class": m, "seed": seed, "code": win,
                        "exact_match": exact, "cells": ncells,
                        "transfer_pure": pure})
        print(f"m={m:3d} seed={seed}: {win} exact={exact} "
              f"cells={ncells} pure={pure}", flush=True)

summary = []
for m in (10, 20, 40, 60):
    rows = [r for r in results if r["m_per_class"] == m]
    summary.append({"m_per_class": m,
                    "exact_match_rate": sum(r["exact_match"] for r in rows) / 5,
                    "pure_transfer_rate": sum(r["transfer_pure"] for r in rows) / 5})
    print(f"m={m}: exact {summary[-1]['exact_match_rate']:.0%}, "
          f"pure {summary[-1]['pure_transfer_rate']:.0%}")
json.dump({"results": results, "summary": summary},
          open("p40b_sweep_results.json", "w"), indent=1)
print("saved p40b_sweep_results.json")
