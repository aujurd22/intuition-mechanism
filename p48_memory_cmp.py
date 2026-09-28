"""P48-b/P52: memory-type comparison on the Markov author family.

Third non-math family for the prototype/exemplar separation (P46-c line).
Five Markov chains over 6 tokens play "authors"; samples are bigram-rate
vectors from 40-token sequences.  Arcs: RECALL (author absent >= 2 eras,
returns), WEAK (3 samples only), VARIANT (transition drift).

Arms:
  STR - per-author expected bigram-rate vector (structural memory)
  EPI - last <= 3 stored samples per author (episodic memory)

Both arms share the same calibration threshold (intra-author relative
distance median * 1.5) and answer recognition or NEW on every sample.
"""
import json
import numpy as np
from collections import defaultdict

NTOK = 6
SEQ_LEN = 40
CYCLES = {
    "A": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)],
    "B": [(0, 2), (2, 4), (4, 1), (1, 5), (5, 3), (3, 0)],
    "C": [(0, 5), (5, 2), (2, 1), (1, 4), (4, 3), (3, 0)],
    "D": [(0, 4), (4, 5), (5, 1), (1, 0), (2, 3), (3, 2)],
    "E": [(0, 1), (1, 3), (3, 5), (5, 2), (2, 4), (4, 0)],
}


def markov_matrix(kind):
    M = np.full((NTOK, NTOK), 0.05)
    for i, j in CYCLES[kind]:
        M[i, j] += 0.45
    M = np.maximum(M, 0.01)
    return M / M.sum(axis=1, keepdims=True)


def gen_seq(M, n=SEQ_LEN, rng=None):
    out = [int(rng.integers(0, NTOK))]
    for _ in range(n - 1):
        out.append(int(rng.choice(NTOK, p=M[out[-1]])))
    return out


def bigram_rates(seq):
    v = np.zeros(NTOK * NTOK)
    for a, b in zip(seq, seq[1:]):
        v[a * NTOK + b] += 1
    return v / (len(seq) - 1)


def main():
    import sys
    hard = "--hard" in sys.argv
    rng = np.random.default_rng(4801)
    if hard:
        # overlap regime: weak cycles + short sequences -> bigram vectors
        # form one continuous overlapping cloud (P46-c predicts EPI wins)
        global NTOK, SEQ_LEN
        cyc_w, seq_len = 0.18, 12
    else:
        cyc_w, seq_len = 0.45, SEQ_LEN

    def mk(kind):
        M = np.full((NTOK, NTOK), 0.05)
        for i, j in CYCLES[kind]:
            M[i, j] += cyc_w
        M = np.maximum(M, 0.01)
        return M / M.sum(axis=1, keepdims=True)

    MAT = {k: mk(k) for k in CYCLES}

    ERAS = [
        (1, [("A", 15, 0), ("E", 15, 0)]),
        (2, [("B", 15, 0), ("C", 15, 0)]),
        (3, [("D", 15, 0), ("A", 10, 0)]),
        (4, [("C", 3, 0), ("B", 12, 0)]),
        (5, [("D", 12, 0), ("E", 12, 0)]),
        (6, [("E", 10, 0), ("A", 12, 0), ("C", 10, 0)]),
        (7, [("A", 10, 1), ("B", 15, 0)]),
        (8, [("C", 8, 0), ("E", 8, 0), ("B", 8, 0)]),
    ]

    stream = []
    for era, spec in ERAS:
        for aname, n, variant in spec:
            M = MAT[aname]
            if variant:
                M = np.maximum(M + rng.normal(0, 0.08, M.shape) * M, 0.01)
                M /= M.sum(axis=1, keepdims=True)
            for _ in range(n):
                seq = gen_seq(M, n=seq_len, rng=rng)
                stream.append({"era": era, "author": aname,
                               "feat": bigram_rates(seq),
                               "seq_len": seq_len,
                               "variant": bool(variant)})
    print(f"stream: {len(stream)} samples")

    cal = [s for s in stream if s["era"] == 1]
    dists = []
    for i in range(len(cal)):
        for j in range(i + 1, len(cal)):
            if cal[i]["author"] == cal[j]["author"]:
                a, b = cal[i]["feat"], cal[j]["feat"]
                dists.append(np.linalg.norm(a - b)
                             / (np.linalg.norm(a) + 1e-300))
    thresh = float(np.median(dists)) * 1.5
    print(f"calibration threshold: {thresh:.4f}")

    str_mem = {}
    epi_mem = defaultdict(list)
    counts = defaultdict(int)
    score = {"STR": [0, 0], "EPI": [0, 0]}
    arc = {a: {arm: [0, 0] for arm in ("STR", "EPI")}
           for a in ("RECALL", "WEAK", "VARIANT")}
    # arc membership by (author, era) windows
    arc_of = {}
    for s in stream:
        a, era = s["author"], s["era"]
        if a == "E" and era >= 6:
            arc_of[id(s)] = "RECALL"
        elif a == "A" and era >= 6:
            arc_of[id(s)] = "RECALL"
        elif a == "C" and s_era_weak(stream, s):
            arc_of[id(s)] = "WEAK"

    for s in stream:
        feat, truth = s["feat"], s["author"]
        s_ans = answer_str(str_mem, feat, thresh)
        e_ans = answer_epi(epi_mem, feat, thresh)
        for arm, ans in (("STR", s_ans), ("EPI", e_ans)):
            ok = ans == truth
            score[arm][1] += 1
            score[arm][0] += ok
            tag = arc_tag(s, stream)
            if tag:
                arc[tag][arm][1] += 1
                arc[tag][arm][0] += ok
        str_mem.setdefault(truth, np.zeros_like(feat))
        counts[truth] += 1
        str_mem[truth] += (feat - str_mem[truth]) / counts[truth]
        epi_mem[truth].append(feat)
        if len(epi_mem[truth]) > 3:
            epi_mem[truth].pop(0)

    print("\n=== P48 Markov family memory comparison ===")
    out = {"thresh": thresh, "n": len(stream)}
    for arm in ("STR", "EPI"):
        t = score[arm]
        pct = 100 * t[0] / max(t[1], 1)
        print(f"  {arm:4s}: {t[0]}/{t[1]} = {pct:.1f}%")
        out[arm] = {"correct": t[0], "total": t[1], "pct": round(pct, 1)}
    print("\narcs:")
    out["arcs"] = {}
    for tag, d in arc.items():
        row = {}
        for arm in ("STR", "EPI"):
            t = d[arm]
            row[arm] = f"{t[0]}/{t[1]}"
            print(f"  {tag:8s} {arm}: {t[0]}/{t[1]}")
        out["arcs"][tag] = row
    json.dump(out, open("p48_memory_results.json", "w"), indent=1)
    print("\nsaved p48_memory_results.json")


def s_era_weak(stream, s):
    # C's era-4 samples (only 3 in that era) count as WEAK
    return s["author"] == "C" and s["era"] == 4


def arc_tag(s, stream):
    if s["variant"]:
        return "VARIANT"
    a, era = s["author"], s["era"]
    if a == "C" and era == 4:
        return "WEAK"
    if a in ("A", "E") and era == 6:
        return "RECALL"
    return None


def answer_str(str_mem, feat, thresh):
    if not str_mem:
        return "NEW"
    best_a = min(str_mem, key=lambda a: np.linalg.norm(feat - str_mem[a]))
    d = np.linalg.norm(feat - str_mem[best_a])
    denom = np.linalg.norm(str_mem[best_a]) + 1e-300
    return best_a if d / denom <= thresh else "NEW"


def answer_epi(epi_mem, feat, thresh):
    best_d, best_a = None, None
    for a, samples in epi_mem.items():
        for sample in samples:
            d = np.linalg.norm(feat - sample)
            if best_d is None or d < best_d:
                best_d, best_a = d, a
    if best_d is None:
        return "NEW"
    denom = np.linalg.norm(feat) + 1e-300
    return best_a if best_d / denom <= thresh else "NEW"


if __name__ == "__main__":
    main()
