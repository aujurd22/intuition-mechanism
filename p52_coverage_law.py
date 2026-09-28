"""P52: the coverage law of memory type.

Uniform protocol across families (P46-c calibration rule):
  THRESH = min inter-class centroid L2 distance / 2, absolute, shared by
  both arms.  STR = running per-class mean (capacity 1 by construction).
  EPI(k) = nearest instance, capacity k per class, k in {1, 3, 10, ALL}.

Coverage-law prediction:
  - concentrated classes (support radius R <~ THRESH): STR ~ EPI(k) for
    all k; capacity insensitive.
  - extended classes (R > THRESH): centroid ball misses the class fringe;
    k instance balls cover more -> accuracy rises with k.

Families: Markov standard / Markov hard (concentrated, overlapping) /
Markov bimodal / envelope staircase (P15, extended).  Per family we also
report the measured spread ratio R/mind (R = mean own-class query
distance to class centroid).
"""
import json
import numpy as np
from collections import defaultdict

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ---------------- dataset builders: stream of (era, class, feat) ----------
def markov_stream(regime, rng):
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

    if regime == "bimodal":
        w, n = 0.45, 16
        chains = [mk(CYCLES[k], w) for k in CYCLES] + [mk([(0, 3), (3, 1), (1, 5),
                                                           (5, 4), (4, 2), (2, 0)], w)]
        auth = {"A": (0, 1), "B": (2, 3), "C": (4, 5)}
        eras = [(1, ["A", "B"]), (2, ["C"]), (3, ["A", "B"]), (4, ["C"]),
                (5, ["A", "B", "C"])]
        stream = []
        for era, anames in eras:
            for a in anames:
                for _ in range(12):
                    ci = auth[a][int(rng.random() < 0.5)]
                    stream.append((era, a, bigram(gen(chains[ci], n))))
        return stream

    w, n = (0.45, 40) if regime == "standard" else (0.18, 12)
    MAT = {k: mk(CYCLES[k], w) for k in CYCLES}
    eras = [(1, ["A", "B"]), (2, ["C", "D"]), (3, ["E", "A"]), (4, ["B", "C"]),
            (5, ["D", "E"]), (6, ["A", "B", "C"])]
    stream = []
    for era, anames in eras:
        for a in anames:
            for _ in range(10):
                stream.append((era, a, bigram(gen(MAT[a], n))))
    return stream


def envelope_stream(rng):
    from p15_envelope import make_dataset, poch_cum, blind_envelope
    X, y, _ = make_dataset(poch_cum, seed=777)
    y = np.asarray(y)
    U = np.stack([np.log(np.abs(blind_envelope(c.astype(np.float64))) + 1e-300)
                  for c in X])
    U = U - U.mean(axis=1, keepdims=True)
    by = {si: [i for i in range(len(X)) if y[i] == si] for si in range(4)}
    eras = [(1, [0, 2]), (2, [1]), (3, [0, 1]), (4, [3, 2]), (5, [1, 0]),
            (6, [2, 1, 3])]
    used = defaultdict(list)
    stream = []
    for era, sis in eras:
        for si in sis:
            pool = [i for i in by[si] if i not in used[si]]
            rng.shuffle(pool)
            for i in pool[:10]:
                stream.append((era, si, U[i]))
                used[si].append(i)
    return stream


# ---------------- uniform protocol ----------------------------------------
def run(stream, capacity):
    """capacity: None for ALL, else int. Returns accuracy dict."""
    feats = np.array([f for _, _, f in stream])
    classes = [c for _, c, _ in stream]
    uniq = sorted(set(classes))
    cents0 = {c: feats[[i for i, cc in enumerate(classes) if cc == c]].mean(axis=0)
              for c in uniq}
    mind = min(float(np.linalg.norm(cents0[a] - cents0[b]))
               for i, a in enumerate(uniq) for b in uniq[i + 1:])
    thresh = mind / 2

    str_mem, cnt = {}, defaultdict(int)
    epi = defaultdict(list)
    S = {"STR": [0, 0], "EPI": [0, 0]}
    for idx, (era, c, f) in enumerate(stream):
        # STR
        if str_mem:
            b = min(str_mem, key=lambda k: float(np.linalg.norm(f - str_mem[k])))
            d = float(np.linalg.norm(f - str_mem[b]))
            s_ok = (d <= thresh) and (b == c)
        else:
            s_ok = False
        S["STR"][1] += 1
        S["STR"][0] += s_ok
        # EPI(k)
        pts = [(j, cc) for cc in epi for j in epi[cc]]
        if pts:
            j, cc = min(pts, key=lambda jc: float(np.linalg.norm(f - feats[jc[0]])))
            d = float(np.linalg.norm(f - feats[j]))
            e_ok = (d <= thresh) and (cc == c)
        else:
            e_ok = False
        S["EPI"][1] += 1
        S["EPI"][0] += e_ok
        # online updates AFTER answering
        str_mem.setdefault(c, np.zeros_like(f))
        cnt[c] += 1
        str_mem[c] += (f - str_mem[c]) / cnt[c]
        epi[c].append(idx)
        if capacity is not None and len(epi[c]) > capacity:
            epi[c].pop(0)          # FIFO: most recent k kept
    return S, mind


def spread_ratio(stream):
    feats = np.array([f for _, _, f in stream])
    classes = [c for _, c, _ in stream]
    uniq = sorted(set(classes))
    cents = {c: feats[[i for i, cc in enumerate(classes) if cc == c]].mean(axis=0)
             for c in uniq}
    mind = min(float(np.linalg.norm(cents[a] - cents[b]))
               for i, a in enumerate(uniq) for b in uniq[i + 1:])
    rs = []
    for c in uniq:
        own = [i for i, cc in enumerate(classes) if cc == c]
        rs.append(float(np.mean([np.linalg.norm(feats[i] - cents[c])
                                 for i in own])))
    return float(np.mean(rs)) / mind


def main():
    rng = np.random.default_rng(5232)
    fams = {
        "markov-standard": markov_stream("standard", rng),
        "markov-hard": markov_stream("hard", rng),
        "markov-bimodal": markov_stream("bimodal", rng),
        "envelope-staircase": envelope_stream(rng),
    }
    out = {}
    print(f"{'family':22s} {'R/mind':>7s} {'STR':>7s} {'EPI1':>7s} "
          f"{'EPI3':>7s} {'EPI10':>7s} {'EPI-ALL':>8s}")
    for name, stream in fams.items():
        r = spread_ratio(stream)
        row = {"spread_ratio": round(r, 3)}
        s_str, _ = run(stream, None)
        row["STR"] = round(100 * s_str["STR"][0] / s_str["STR"][1], 1)
        for k in (1, 3, 10, None):
            s, mind = run(stream, k)
            key = f"EPI{k}" if k else "EPI-ALL"
            row[key] = round(100 * s["EPI"][0] / s["EPI"][1], 1)
        out[name] = row
        print(f"{name:22s} {r:7.3f} {row['STR']:7.1f} {row['EPI1']:7.1f} "
              f"{row['EPI3']:7.1f} {row['EPI10']:7.1f} {row['EPI-ALL']:8.1f}")
    json.dump(out, open("p52_coverage_law.json", "w"), indent=1)
    print("saved p52_coverage_law.json")


if __name__ == "__main__":
    main()
