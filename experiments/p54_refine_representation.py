"""P54: representation refinement moves the C2 novelty window.

P53 showed the Markov family's held-out author is INVISIBLE in bigram
space (novel clearance 0.37 x mind < known NN spacing 0.43 x mind):
novelty detectability is a property of the representation.  Registered
predictions (before the run):

  P1: the clearance/coverage ratio (novel_min_dist / known_NN_dist)
      RISES with n-gram order n (context separates reversal dynamics
      that share marginal transition profiles).
  P2: there is an order n* where the C2 window opens:
      NN/mind < 0.5 AND novel_min/mind > 0.5.
  Falsification: ratio flat/decreasing in n, or no window by n=4.

Protocol: markov-standard streams (5 authors), held-out author F
(reverse-cycle chain) queried after training; shared absolute threshold
THRESH = mind/2; EPI-ALL arm for coverage side.
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


def mk(cycles, w=0.45):
    M = np.full((NTOK, NTOK), 0.05)
    for i, j in cycles:
        M[i, j] += w
    return np.maximum(M, 0.01) / np.maximum(M, 0.01).sum(axis=1, keepdims=True)


def gen(M, n, rng):
    out = [int(rng.integers(0, NTOK))]
    for _ in range(n - 1):
        out.append(int(rng.choice(NTOK, p=M[out[-1]])))
    return out


def ngram_feat(seq, order):
    d = NTOK ** order
    v = np.zeros(d)
    for k in range(len(seq) - order + 1):
        idx = 0
        for t in seq[k:k + order]:
            idx = idx * NTOK + t
        v[idx] += 1
    return v / max(1, len(seq) - order + 1)


def stream_and_novel(order, rng, n_authors=5, per_era=10):
    MAT = {k: mk(CYCLES[k]) for k in CYCLES}
    eras = [(1, ["A", "B"]), (2, ["C", "D"]), (3, ["E", "A"]), (4, ["B", "C"]),
            (5, ["D", "E"]), (6, ["A", "B", "C"])]
    stream = []
    for era, anames in eras:
        for a in anames:
            for _ in range(per_era):
                stream.append((era, a, ngram_feat(gen(MAT[a], 40, rng), order)))
    # held-out author F: reverse cycle (transposed transition matrix)
    MF = mk(CYCLES["A"]).T
    novel = [ngram_feat(gen(MF, 40, rng), order) for _ in range(12)]
    return stream, novel


def geometry(stream, novel):
    feats = np.array([f for _, _, f in stream])
    classes = [c for _, c, _ in stream]
    uniq = sorted(set(classes))
    cents = {c: feats[[i for i, cc in enumerate(classes) if cc == c]].mean(axis=0)
             for c in uniq}
    mind = min(float(np.linalg.norm(cents[a] - cents[b]))
               for i, a in enumerate(uniq) for b in uniq[i + 1:])
    thresh = mind / 2
    nns = []
    for i, c in enumerate(classes):
        own = [j for j, cc in enumerate(classes) if cc == c and j != i]
        nns.append(min(float(np.linalg.norm(feats[i] - feats[j])) for j in own))
    nn_mean = float(np.mean(nns))
    det = 0
    clearance = []
    for f in novel:
        d = min(float(np.linalg.norm(f - feats[j])) for j in range(len(feats)))
        clearance.append(d)
        det += d > thresh
    false_new = sum(nn > thresh for nn in nns) / len(nns)
    return {"order_dim": int(feats.shape[1]),
            "mind": mind,
            "NN_over_mind": round(nn_mean / mind, 3),
            "novel_min_over_mind": round(min(clearance) / mind, 3),
            "novel_median_over_mind": round(float(np.median(clearance)) / mind, 3),
            "ratio_clearance_over_NN": round(min(clearance) / nn_mean, 3),
            "detection_pct": round(100 * det / len(clearance), 1),
            "false_new_pct": round(100 * false_new, 1),
            "window_open": bool(nn_mean / mind < 0.5
                                and min(clearance) / mind > 0.5)}


def main():
    rows = {}
    print("registered: ratio rises with order; window opens at some n*")
    print(f"{'order':5s} {'dim':>6s} {'NN/mind':>8s} {'novel_min/mind':>14s} "
          f"{'ratio':>7s} {'det%':>6s} {'falseNEW%':>9s} {'window':>7s}")
    for order in (2, 3, 4):
        rng = np.random.default_rng(5400 + order)
        stream, novel = stream_and_novel(order, rng)
        g = geometry(stream, novel)
        rows[f"ngram-{order}"] = g
        print(f"{order:5d} {g['order_dim']:6d} {g['NN_over_mind']:8.3f} "
              f"{g['novel_min_over_mind']:14.3f} {g['ratio_clearance_over_NN']:7.3f} "
              f"{g['detection_pct']:6.1f} {g['false_new_pct']:9.1f} "
              f"{str(g['window_open']):>7s}")
    json.dump(rows, open("p54_refine_representation.json", "w"), indent=1)
    print("saved p54_refine_representation.json")


if __name__ == "__main__":
    main()
