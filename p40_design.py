"""P40: blind end-to-end discovery-generalization (pre-registered,
docs/RESEARCH_PLAN.md P40 row).

Closes the P39 scope caveat (user audit): "code discoverable" (P35-a)
and "code drives novelty" (P39) must become ONE blind chain --

  discovery split  -> MDL search finds a code on DISCOVERY families
                      ONLY (160 families, 20 per class; labels never
                      shown to the search; truth never consulted);
  freeze           -> the discovered feature set + a cell->class map
                      built WITHOUT labels (cell identity = class
                      identity by construction; any correspondence to
                      the true class names is scored at the end only);
  transfer         -> the frozen pipeline (a) recognizes all 4800
                      families, (b) runs the P32-h novelty task on
                      trials whose families were NEVER in the
                      discovery split.

Verdict bands: transfer recognition >= 95% AND novelty >= 90% on
unseen trials => CONFIRMED; recognition >= 95% but novelty fails =>
PARTIAL; either < 80% => NEGATIVE.

Run:  python p40_design.py && python p40_run.py
"""
import json
import os
import sys
from itertools import combinations

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p40_corpus import build_corpus  # noqa: E402

rng = np.random.default_rng(9001)
CLASSES = [("2", "no"), ("2", "alt"), ("3", "no"), ("3", "alt"),
           ("4", "no"), ("4", "alt"), ("5", "no"), ("5", "alt")]

corpus = build_corpus()          # {fid: {"seq", "cls", "params"}}
by_class = {c: [f for f, r in corpus.items() if r["cls"] == c]
            for c in CLASSES}

# ---- discovery split: 20 families per class (160 total) ----
discovery = []
for c in CLASSES:
    picks = rng.choice(by_class[c], size=20, replace=False)
    discovery += list(picks)
discovery_set = set(discovery)

# ---- MDL feature space (identical to P35-a: threshold-free) ----
fids = sorted(discovery)
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
QUANT = 0.05


def code_bits(cols):
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
        rngv = max(x.max() - x.min(), QUANT)
        bits += np.sum(np.where(
            solo, np.log2(rngv * np.sqrt(2 * np.pi * np.e)),
            np.log2(sd * np.sqrt(2 * np.pi * np.e))))
    return float(bits), int(ncells)


# ---- blind search on the discovery split (sizes 1..4) ----
best_overall = None
search_log = []
for r in range(1, 5):
    best = None
    for combo in combinations(range(len(feat_names)), r):
        cols = [i in combo for i in range(len(feat_names))]
        bits, ncells = code_bits(cols)
        if best is None or bits < best[0]:
            best = (bits, combo, ncells)
    search_log.append({"size": r, "bits": best[0], "cells": best[2],
                       "features": [feat_names[i] for i in best[1]]})
    print(f"size {r}: {best[0]:.0f} bits, {best[2]} cells, "
          f"{[feat_names[i] for i in best[1]]}")
    best_overall = best

win_features = [feat_names[i] for i in best_overall[1]]
print("\ndiscovered code (blind, 160 families):", win_features)

# ---- freeze: cell -> class map built WITHOUT labels ----
# key: the boolean signature vector; each distinct cell IS a class.
# For novelty we only need cell equality, so no labels are stored --
# the map is {family-letter -> cell} from the P32-h contexts, plus
# the cells of all 4800 families for recognition scoring.
F = {}
for name in feat_names:
    if name in win_features:
        F[name] = feats[name]
# recompute features on the FULL corpus for transfer
Xall = np.array([corpus[f]["seq"] for f in sorted(corpus)], dtype=float)
allfeat = {}
for name in win_features:
    if name.startswith("eq"):
        k = int(name.split("=")[0][2:])
        const = int(name.split("=")[1])
        allfeat[name] = (Xall[:, k] == const)
    else:
        allfeat[name] = np.any(np.diff(np.sign(Xall), axis=1) != 0, axis=1)
key_all = np.array([allfeat[n] for n in win_features]).T
fid_order = sorted(corpus)
cell_of = {fid: tuple(key_all[i]) for i, fid in enumerate(fid_order)}

# recognition: does the frozen code partition the full corpus
# consistently with the discovery cells?
disc_cells = {}
for f in fids:
    disc_cells.setdefault(cell_of[f], set()).add(corpus[f]["cls"])
consistent = all(len(v) == 1 for v in disc_cells.values())
print(f"discovery cells: {len(disc_cells)}, all-pure: {consistent}")

json.dump({"discovery_split": sorted(discovery),
           "search_log": search_log,
           "discovered_features": win_features,
           "cells_pure": consistent,
           "n_cells": len(disc_cells)},
          open("p40_design.json", "w"), indent=1)
print("saved p40_design.json")
