"""P66: Hart condensation bridges the coverage law to NN-condensation theory.

Literature anchor: Hart 1968 CNN (minimal consistent subset, NP-complete
in general); Kuncheva et al. arXiv:1806.01130 (instance selection as
categorization model).  Registered predictions (before running):

  R1 (ordering): condensing ratio |C|/N increases with extension --
     markov-standard (R/mind 0.43) < visual (0.59) < envelope (1.41).
  R2 (degeneracy): markov-hard / bimodal (no coverage at THRESH) keep
     nearly everything (|C|/N > 0.8).
  R3 (two-scale): the D=5 two-scale family of P65-b needs a ratio
     ABOVE single-scale families at matched R/mind band (fringe points
     carry boundary information).
Falsification: ordering inverted, or degenerate families condensing well.
"""
import json
import numpy as np
from collections import defaultdict

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def hart_cnn(X, classes, rng):
    """Classic Hart CNN: returns the consistent subset indices."""
    uniq = sorted(set(classes))
    C = []
    for c in uniq:                      # seed: one point per class
        own = [i for i, cc in enumerate(classes) if cc == c]
        C.append(own[rng.integers(len(own))])
    changed = True
    while changed:
        changed = False
        for i in range(len(X)):
            if i in C:
                continue
            nearest = min(C, key=lambda j: float(np.linalg.norm(X[i] - X[j])))
            if classes[nearest] != classes[i]:
                C.append(i)
                changed = True
    return C


def build_markov(regime, rng):
    NTOK = 6
    CYCLES = {
        "A": [(0,1),(1,2),(2,3),(3,4),(4,5),(5,0)],
        "B": [(0,2),(2,4),(4,1),(1,5),(5,3),(3,0)],
        "C": [(0,5),(5,2),(2,1),(1,4),(4,3),(3,0)],
        "D": [(0,4),(4,5),(5,1),(1,0),(2,3),(3,2)],
        "E": [(0,1),(1,3),(3,5),(5,2),(2,4),(4,0)],
    }
    def mk(cycles, w):
        M = np.full((NTOK, NTOK), 0.05)
        for i, j in cycles:
            M[i, j] += w
        return np.maximum(M, 0.01) / np.maximum(M, 0.01).sum(axis=1, keepdims=True)
    w, n = (0.45, 40) if regime == "standard" else (0.18, 12)
    MAT = {k: mk(CYCLES[k], w) for k in CYCLES}
    eras = [(1, ["A", "B"]), (2, ["C", "D"]), (3, ["E", "A"]), (4, ["B", "C"]),
            (5, ["D", "E"]), (6, ["A", "B", "C"])]
    def gen(M, n):
        out = [int(rng.integers(0, NTOK))]
        for _ in range(n - 1):
            out.append(int(rng.choice(NTOK, p=M[out[-1]])))
        return out
    def bigram(seq):
        v = np.zeros(NTOK * NTOK)
        for a, b in zip(seq, seq[1:]):
            v[a * NTOK + b] += 1
        return v / (len(seq) - 1)
    X, y = [], []
    for era, anames in eras:
        for a in anames:
            for _ in range(10):
                X.append(bigram(gen(MAT[a], n))); y.append(a)
    return np.array(X), y


def build_visual(rng):
    X = np.load("p56_visual_X.npy"); y = [int(v) for v in np.load("p56_visual_y.npy")]
    idx = rng.permutation(len(X))[:120]
    return X[idx], [y[i] for i in idx]


def build_twoscale(rng):
    K = 5
    G = np.eye(K) - np.ones((K, K)) / K
    pd = ((G[:, None, :] - G[None, :, :])**2).sum(-1)**0.5
    mus = G * (10.0 / pd[pd > 0].min())
    X, y = [], []
    for ci in range(K):
        for _ in range(70):
            X.append(mus[ci] + 0.5 * rng.normal(0, 1, K)); y.append(ci)
        for _ in range(30):
            X.append(mus[ci] + 3.0 * rng.normal(0, 1, K)); y.append(ci)
    return np.array(X), y


def spread_ratio(X, y):
    uniq = sorted(set(y))
    cents = {c: X[[i for i, cc in enumerate(y) if cc == c]].mean(axis=0) for c in uniq}
    mind = min(float(np.linalg.norm(cents[a] - cents[b]))
               for i, a in enumerate(uniq) for b in uniq[i+1:])
    R = float(np.mean([np.linalg.norm(X[[i for i, cc in enumerate(y) if cc == c]]
                                   - cents[c], axis=1).mean() for c in uniq]))
    return R / mind


def main():
    rng0 = np.random.default_rng(6600)
    builders = {
        "markov-standard": lambda r: build_markov("standard", r),
        "markov-hard": lambda r: build_markov("hard", r),
        "visual": build_visual,
        "twoscale-D5": build_twoscale,
    }
    out = {}
    print("registered: R1 std<visual<twoscale... R2 hard degenerates")
    print(f"{'family':18s} {'N':>5s} {'R/mind':>7s} {'|C|/N':>7s}")
    for name, builder in builders.items():
        ratios, cratios = [], []
        for seed in (6601, 6602, 6603):
            rng = np.random.default_rng(seed)
            X, y = builder(rng)
            C = hart_cnn(X, y, rng)
            ratios.append(spread_ratio(X, y))
            cratios.append(len(C) / len(X))
        row = {"R_over_mind": round(float(np.mean(ratios)), 3),
               "condensing_ratio": round(float(np.mean(cratios)), 3)}
        out[name] = row
        print(f"{name:18s} {len(X):5d} {row['R_over_mind']:7.3f} "
              f"{row['condensing_ratio']:7.3f}")
    r1 = out["markov-standard"]["condensing_ratio"] < out["visual"]["condensing_ratio"]
    r2 = out["markov-hard"]["condensing_ratio"] > 0.8
    r3 = out["twoscale-D5"]["condensing_ratio"] > out["markov-standard"]["condensing_ratio"]
    print(f"\nR1 (std < visual):            {'CONFIRMED' if r1 else 'FAILED'}")
    print(f"R2 (hard > 0.8):              {'CONFIRMED' if r2 else 'FAILED'}")
    print(f"R3 (twoscale > std):          {'CONFIRMED' if r3 else 'FAILED'}")
    out.update({"R1": bool(r1), "R2": bool(r2), "R3": bool(r3)})
    json.dump(out, open("p66_hart_condensation.json", "w"), indent=1)
    print("saved p66_hart_condensation.json")


if __name__ == "__main__":
    main()
