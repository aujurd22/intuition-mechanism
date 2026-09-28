"""P53: novelty detection is coverage (C2 made quantitative).

Extends the P52 coverage law from recognition to novelty: a sample is
called NEW iff it falls outside every stored coverage ball (radius
THRESH = mind/2).  Predictions registered BEFORE the run, per family
and arm, from geometry alone:

  detection rate of a held-out novel class ~= P(distance from a novel
  sample to the nearest stored item > THRESH)  [estimated on the actual
  novel samples]
  false-NEW rate on known classes ~= P(distance from a known sample to
  its arm's stored representation > THRESH)   [estimated the same way]

Prediction: the SAME two ratios (novel-clearance/mind for detection,
R/mind or NN/mind for false alarms) explain the novelty columns, the
way they explained the recognition columns in P52.

Families: the four P52 families, each with a held-out novel class
(Markov: 6th chain F, unseen until the final era; envelope: class s4
held out of the stream entirely, queried at the end).
"""
import json
import numpy as np
from collections import defaultdict

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from p52_coverage_law import markov_stream  # noqa: E402

NTOK = 6


def novel_markov_samples(rng, n=12):
    """Author F: a chain unlike A-E (reverse cycle)."""
    cyc = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]
    M = np.full((NTOK, NTOK), 0.05)
    for i, j in cyc:
        M[i, j] += 0.45
    M = np.maximum(M, 0.01)
    M = (M.T / M.T.sum(axis=1, keepdims=True)).T  # transposed = new dynamics

    def gen(n_):
        out = [int(rng.integers(0, NTOK))]
        for _ in range(n_ - 1):
            out.append(int(rng.choice(NTOK, p=M[out[-1]])))
        return out

    def bigram(seq):
        v = np.zeros(NTOK * NTOK)
        for a, b in zip(seq, seq[1:]):
            v[a * NTOK + b] += 1
        return v / (len(seq) - 1)

    return [bigram(gen(40)) for _ in range(n)]


def envelope_novel(rng):
    """Held-out envelope class: s4 of the P15 dataset (stream used 0,1,2,3?).

    P52 envelope stream used classes {0,1,2,3}; for novelty we hold out
    class 3 from the stream and query it at the end instead.
    """
    from p15_envelope import make_dataset, poch_cum, blind_envelope
    X, y, _ = make_dataset(poch_cum, seed=777)
    y = np.asarray(y)
    U = np.stack([np.log(np.abs(blind_envelope(c.astype(np.float64))) + 1e-300)
                  for c in X])
    U = U - U.mean(axis=1, keepdims=True)
    return U, y


def run_family(stream, novel_feats, capacity=None):
    """Stream a normal training phase (no novel), then answer novel
    samples + a known-sample probe set.  Returns measured rates."""
    feats = np.array([f for _, _, f in stream])
    classes = [c for _, c, _ in stream]
    uniq = sorted(set(classes))
    cents0 = {c: feats[[i for i, cc in enumerate(classes) if cc == c]].mean(axis=0)
              for c in uniq}
    mind = min(float(np.linalg.norm(cents0[a] - cents0[b]))
               for i, a in enumerate(uniq) for b in uniq[i + 1:])
    thresh = mind / 2

    str_mem, cnt, epi = {}, defaultdict(int), defaultdict(list)
    known_detect_new = [0, 0]   # false-NEW on known probes
    novel_detect_new = [0, 0]   # true-NEW on novel samples
    novel_hits = []             # distance of each novel sample to stored
    known_dist = []             # known probe distance to stored
    for idx, (era, c, f) in enumerate(stream):
        str_mem.setdefault(c, np.zeros_like(f))
        cnt[c] += 1
        str_mem[c] += (f - str_mem[c]) / cnt[c]
        epi[c].append(idx)
        if capacity is not None and len(epi[c]) > capacity:
            epi[c].pop(0)

    # arm snapshots
    if capacity is None:
        stored = {c: [feats[j] for j in epi[c]] for c in epi}
        arm = "EPI-ALL"
    else:
        stored = {c: [cents0[c]] for c in uniq}
        arm = "STR"

    for f in novel_feats:
        d = min(float(np.linalg.norm(f - s))
                for c in stored for s in stored[c])
        novel_hits.append(d)
        novel_detect_new[1] += 1
        novel_detect_new[0] += d > thresh
    for c in uniq:
        own = [i for i, cc in enumerate(classes) if cc == c][-5:]
        for i in own:
            if arm == "STR":
                d = float(np.linalg.norm(feats[i] - str_mem[c]))
            else:
                pool = [feats[j] for j in epi[c] if j != i]
                d = min(float(np.linalg.norm(feats[i] - p)) for p in pool) \
                    if pool else 1e9
            known_dist.append(d)
            known_detect_new[1] += 1
            known_detect_new[0] += d > thresh
    return {"arm": arm, "mind": mind, "thresh": thresh,
            "novel_min_dist_over_mind": round(min(novel_hits) / mind, 3),
            "novel_median_dist_over_mind": round(float(np.median(novel_hits)) / mind, 3),
            "detection_rate": round(100 * novel_detect_new[0] / novel_detect_new[1], 1),
            "false_new_rate": round(100 * known_detect_new[0] / known_detect_new[1], 1)}


def main():
    rng = np.random.default_rng(5301)
    out = {}
    print("registered prediction: detection rate tracks novel-sample "
          "clearance vs THRESH; false-NEW tracks known-sample coverage miss")
    for regime in ("standard", "hard"):
        stream = markov_stream(regime, rng)
        novel = novel_markov_samples(rng)
        for cap, arm in ((None, "EPI-ALL"), (0, "STR")):
            if cap == 0:
                # STR arm: same run, stored = centroids
                r = run_family(stream, novel, capacity=None)
                # recompute with STR storage
                feats = np.array([f for _, _, f in stream])
                classes = [c for _, c, _ in stream]
                uniq = sorted(set(classes))
                cents0 = {c: feats[[i for i, cc in enumerate(classes)
                                    if cc == c]].mean(axis=0) for c in uniq}
                mind = r["mind"]
                thresh = mind / 2
                det = [min(float(np.linalg.norm(f - cents0[c])) for c in uniq)
                       for f in novel]
                known_d = []
                for idx, (era, c, f) in enumerate(stream[-15:]):
                    known_d.append(float(np.linalg.norm(f - cents0[c])))
                r = {"arm": "STR", "mind": mind,
                     "novel_min_dist_over_mind": round(min(det) / mind, 3),
                     "novel_median_dist_over_mind":
                         round(float(np.median(det)) / mind, 3),
                     "detection_rate": round(100 * sum(d > thresh for d in det)
                                             / len(det), 1),
                     "false_new_rate": round(100 * sum(d > thresh for d in known_d)
                                             / len(known_d), 1)}
            else:
                r = run_family(stream, novel, capacity=cap)
            out[f"markov-{regime}-{r['arm']}"] = r
            print(f"markov-{regime:9s} {r['arm']:8s} novel_min/mind="
                  f"{r['novel_min_dist_over_mind']:6.3f} det={r['detection_rate']:5.1f}%"
                  f"  falseNEW={r['false_new_rate']:5.1f}%")
    json.dump(out, open("p53_novelty_coverage.json", "w"), indent=1)
    print("saved p53_novelty_coverage.json")


if __name__ == "__main__":
    main()
