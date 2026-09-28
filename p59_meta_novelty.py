"""P59: meta-level novelty detection via multi-space coverage profiles.

P48-b declared novelty detection "unreliable" on the overlapping Markov
family with single representations.  The P52/P53 coverage theory gives
the design: a query is evidence-of-novel only if it is FRINGE in every
representation space simultaneously (known queries are core-or-fringe
per space with partially independent fringes; a genuinely novel class
is fringe in all).

Registered predictions (before the run), on markov-hard (weak cycles,
12-token sequences, held-out reverse-cycle author F):
  R1: asymmetry-space alone achieves detection >= 60% at false-alarm
      <= 10% (contrast survives the short-sequence noise).
  R2: the AND rule (min over normalized per-space distances of
      {bigram, asymmetry}) detection@FA<=10% >= asymmetry-only
      (the conjunction costs nothing against the better single space).
Falsification: R1 below 60%, or AND below asym-only.
"""
import json
import numpy as np
from collections import defaultdict

NTOK = 6
CYCLES = {
    "A": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)],
    "B": [(0, 2), (2, 4), (4, 1), (1, 5), (5, 3), (3, 0)],
    "C": [(0, 5), (5, 2), (2, 1), (1, 4), (4, 3), (3, 0)],
    "D": [(0, 4), (4, 5), (5, 1), (1, 0), (2, 3), (3, 2)],
    "E": [(0, 1), (1, 3), (3, 5), (5, 2), (2, 4), (4, 0)],
}


def mk(cycles, w):
    M = np.full((NTOK, NTOK), 0.05)
    for i, j in cycles:
        M[i, j] += w
    return np.maximum(M, 0.01) / np.maximum(M, 0.01).sum(axis=1, keepdims=True)


def gen(M, n, rng):
    out = [int(rng.integers(0, NTOK))]
    for _ in range(n - 1):
        out.append(int(rng.choice(NTOK, p=M[out[-1]])))
    return out


def feats(seq):
    v = np.zeros(NTOK * NTOK)
    for a, b in zip(seq, seq[1:]):
        v[a * NTOK + b] += 1
    v /= max(1, len(seq) - 1)
    asym = v - v.reshape(NTOK, NTOK).T.reshape(-1)
    return v, asym


def build(seed, w=0.18, seqn=12):
    rng = np.random.default_rng(seed)
    MAT = {k: mk(CYCLES[k], w) for k in CYCLES}
    MF = mk(CYCLES["A"], w).T
    eras = [(1, ["A", "B"]), (2, ["C", "D"]), (3, ["E", "A"]), (4, ["B", "C"]),
            (5, ["D", "E"]), (6, ["A", "B", "C"])]
    cal, known = [], []
    for era, anames in eras:
        for a in anames:
            for _ in range(10):
                bg, asy = feats(gen(MAT[a], seqn, rng))
                (cal if era == 1 else known).append((bg, asy))
    novel = [feats(gen(MF, seqn, rng)) for _ in range(40)]
    return cal, known, novel


def scores(cal, known, novel, space):
    idx = {"bigram": 0, "asym": 1}[space]
    stored = np.array([c[idx] for c in cal + known])
    calv = np.array([c[idx] for c in cal])
    # per-space scale: median self-distance of calibration samples
    # (leave-one-out within calibration)
    ds = []
    for i in range(len(calv)):
        dd = [np.linalg.norm(calv[i] - calv[j])
              for j in range(len(calv)) if j != i]
        ds.append(min(dd))
    s = float(np.median(ds))
    def dist(v):
        return min(float(np.linalg.norm(v - u)) for u in stored)
    kn = np.array([dist(c[idx]) / s for c in known])
    nv = np.array([dist(c[idx]) / s for c in novel])
    return kn, nv


def det_at_fa(kn, nv, fa_target=0.10):
    t = np.quantile(kn, 1 - fa_target)
    det = float(np.mean(nv > t))
    fa = float(np.mean(kn > t))
    return det, fa


def main():
    rows = {}
    print("registered: R1 asym det@FA10 >= 60%; R2 AND >= asym")
    for seed in (5901, 5902, 5903):
        cal, known, novel = build(seed)
        kb, nb = scores(cal, known, novel, "bigram")
        ka, na = scores(cal, known, novel, "asym")
        kmin = np.minimum(kb, ka)
        nmin = np.minimum(nb, na)
        row = {}
        for tag, (k, n) in (("bigram", (kb, nb)), ("asym", (ka, na)),
                            ("AND", (kmin, nmin))):
            d, f = det_at_fa(k, n)
            row[tag] = {"det@FA10": round(100 * d, 1),
                        "actual_FA": round(100 * f, 1)}
        # also sweep detection at FA<=5
        for tag, (k, n) in (("bigram", (kb, nb)), ("asym", (ka, na)),
                            ("AND", (kmin, nmin))):
            d, f = det_at_fa(k, n, 0.05)
            row[tag]["det@FA5"] = round(100 * d, 1)
        rows[f"seed-{seed}"] = row
        print(f"seed {seed}: " + "  ".join(
            f"{tag}: det@FA10={row[tag]['det@FA10']:5.1f}% "
            f"det@FA5={row[tag]['det@FA5']:5.1f}%"
            for tag in ("bigram", "asym", "AND")))
    agg = {tag: {"det@FA10": round(float(np.mean(
                [rows[s][tag]["det@FA10"] for s in rows])), 1),
            "det@FA5": round(float(np.mean(
                [rows[s][tag]["det@FA5"] for s in rows])), 1)}
           for tag in ("bigram", "asym", "AND")}
    r1 = agg["asym"]["det@FA10"] >= 60.0
    r2 = agg["AND"]["det@FA10"] >= agg["asym"]["det@FA10"]
    print(f"\nmeans: {agg}")
    print(f"R1 (asym >= 60% @FA10): {'CONFIRMED' if r1 else 'FAILED'}")
    print(f"R2 (AND >= asym):       {'CONFIRMED' if r2 else 'FAILED'}")
    json.dump({"per_seed": rows, "means": agg,
               "R1_asym_ge60": bool(r1), "R2_AND_ge_asym": bool(r2)},
              open("p59_meta_novelty.json", "w"), indent=1)
    print("saved p59_meta_novelty.json")


if __name__ == "__main__":
    main()
