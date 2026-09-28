"""P48: the Markov "author" family -- extending the memory law beyond
mathematical sequences (pre-registered, registry row P48).

World: 5 "authors", each a first-order Markov chain over 6 tokens.
Chains are designed so that (i) marginal token frequencies are SIMILAR
across authors (unigram counts do not separate), (ii) the transition
STRUCTURE differs (which token follows which).  The sufficient
statistic of a 40-token sample is its 30-dim bigram-rate vector.

The family is NON-MATHEMATICAL: the objects are stylized "texts", the
hidden parameter is a transition matrix, and the applied analog is
authorship attribution / stylometry (Eder 2017: small-sample
attribution is the known hard problem).

Memory arms (P46 protocol on this family):
  STR: per-author expected bigram-rate vector (the compressed code),
       cosine NN, accept within calibration threshold
  EPI: <= 3 stored samples per author, cosine NN
Arcs: RECALL (author E strong era 1, absent 2-5, returns era 6),
      WEAK (author C only 3 samples era 4), VARIANT (author A's
      transition matrix drifts in era 7), NOVEL (author F, never
      seen, appears era 8 -- tests new-author detection).

Run:  python p48_markov.py
"""
import json
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

rng = np.random.default_rng(4801)
NTOK = 6
LEN = 40

def markov_matrix(kind, drift=0.0):
    """Build a 6x6 row-stochastic transition matrix with a distinctive
    structure but SIMILAR marginals across kinds."""
    M = np.full((NTOK, NTOK), 0.05)          # weak uniform base
    if kind == "A":
        cyc = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,0)]
        for i,j in cyc: M[i,j] += 0.45
        M[0,3] += 0.20; M[2,5] += 0.20        # A's extra bridges
    elif kind == "B":
        cyc = [(0,2),(2,4),(4,1),(1,5),(5,3),(3,0)]
        for i,j in cyc: M[i,j] += 0.45
        M[1,4] += 0.20; M[3,2] += 0.20
    elif kind == "C":
        cyc = [(0,5),(5,2),(2,1),(1,4),(4,3),(3,0)]
        for i,j in cyc: M[i,j] += 0.45
        M[0,2] += 0.20; M[4,0] += 0.20
    elif kind == "D":
        cyc = [(0,4),(4,5),(5,1),(1,0),(2,3),(3,2)]
        for i,j in cyc: M[i,j] += 0.45
        M[1,3] += 0.20; M[5,4] += 0.20
    elif kind == "E":
        # rare author: mostly like A but with one flipped bridge
        cyc = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,0)]
        for i,j in cyc: M[i,j] += 0.45
        M[0,4] += 0.20; M[2,0] += 0.20        # E's bridges differ from A
    elif kind == "F":
        cyc = [(0,3),(3,1),(1,4),(4,2),(2,5),(5,0)]
        for i,j in cyc: M[i,j] += 0.45
        M[0,5] += 0.20; M[3,4] += 0.20
    if drift > 0:
        # variant: perturb the cycle weights
        for i,j in cyc: M[i,j] += drift * (rng.random() - 0.5)
    M = np.maximum(M, 0.01)
    return M / M.sum(axis=1, keepdims=True)

def gen(M, n):
    out = [int(rng.integers(0, NTOK))]
    for _ in range(n - 1):
        out.append(int(rng.choice(NTOK, p=M[out[-1]])))
    return out

def bigram_rates(seq):
    v = np.zeros(NTOK * NTOK)
    for a, b in zip(seq, seq[1:]):
        v[a * NTOK + b] += 1
    return v / (len(seq) - 1)

# authors
MAT = {k: markov_matrix(k) for k in "ABCDE"}
MAT_A_drift = markov_matrix("A", drift=0.8)
MAT_F = markov_matrix("F")                     # the NOVEL author

# era script
ERAS = [
    (1, [("A", 20, MAT["A"], 0), ("E", 20, MAT["E"], 0)]),
    (2, [("B", 20, MAT["B"], 0), ("C", 20, MAT["C"], 0)]),
    (3, [("D", 20, MAT["D"], 0), ("A", 15, MAT["A"], 0)]),
    (4, [("C", 3, MAT["C"], 0), ("B", 15, MAT["B"], 0)]),     # C WEAK
    (5, [("D", 15, MAT["D"], 0), ("E", 15, MAT["E"], 0)]),
    (6, [("E", 12, MAT["E"], 0), ("A", 15, MAT["A"], 0),
         ("C", 10, MAT["C"], 0)]),                             # E RECALL, C returns
    (7, [("A", 12, MAT_A_drift, 1), ("B", 15, MAT["B"], 0)]),  # A VARIANT
    (8, [("C", 10, MAT["C"], 0), ("E", 10, MAT["E"], 0),
         ("F", 12, MAT_F, 0)]),                                # F NOVEL
]

stream = []
for era, spec in ERAS:
    for aname, n, mat, variant in spec:
        for _ in range(n):
            seq = gen(mat, LEN)
            stream.append({"era": era, "author": aname, "seq": seq,
                           "variant": variant, "novel": aname == "F"})
print(f"stream: {len(stream)} samples over {len(ERAS)} eras")

# features: bigram rates
for s in stream:
    s["feat"] = bigram_rates(s["seq"])

def cosd(a, b):
    return 1 - float(a @ b) / (np.linalg.norm(a)*np.linalg.norm(b) + 1e-300)

# calibration threshold (era-1 samples, within-author NN distances)
cal = [s for s in stream if s["era"] == 1]
intra = [cosd(cal[i]["feat"], cal[j]["feat"])
         for i in range(len(cal)) for j in range(i+1, len(cal))
         if cal[i]["author"] == cal[j]["author"]]
THRESH = float(np.median(intra)) * 1.5
print(f"calibration threshold: {THRESH:.4f}")

# STR memory: running per-author mean bigram vector
str_mem = {}
def str_update(author, feat):
    if author not in str_mem:
        str_mem[author] = [feat.copy(), 1]
    else:
        v, n = str_mem[author]
        str_mem[author] = [(v * n + feat) / (n + 1), n + 1]

# EPI memory: <= 3 stored samples per author
epi_mem = defaultdict(list)

results = {"STR": [0,0], "EPI": [0,0]}
novel_det = {"STR": [], "EPI": []}
recovery = []
last_era = {}
seen_authors = set()
log = []

for idx, s in enumerate(stream):
    f, author, era = s["feat"], s["author"], s["era"]
    # STR: nearest author signature; unknown author (F/novel) -> NEW
    known = {a: v[0] for a, v in str_mem.items()}
    if known:
        best_a = min(known, key=lambda a: cosd(f, known[a]))
        d = cosd(f, known[best_a])
        s_ans = best_a if d <= THRESH else "NEW"
    else:
        s_ans = "NEW"
    # EPI: nearest stored sample
    best_d, best_a = None, None
    for a, samples in epi_mem.items():
        for other in samples:
            d = cosd(f, other)
            if best_d is None or d < best_d:
                best_d, best_a = d, a
    e_ans = best_a if (best_a and best_d <= THRESH) else "NEW"
    truth = author if author != "F" else "NEW"

    for arm, ans in (("STR", s_ans), ("EPI", e_ans)):
        hit = (ans == truth)
        results[arm][1] += 1
        results[arm][0] += hit
        if s["novel"]:
            novel_det[arm].append(ans == "NEW" and hit)
    # exclude novel-author samples from recognition scoring
    if s["novel"]:
        results["STR"][1] -= 1; results["STR"][0] -= (s_ans == "NEW" and truth == "NEW")
        results["EPI"][1] -= 1; results["EPI"][0] -= (e_ans == "NEW" and truth == "NEW")
        # rescore: for novel samples the truth is NEW
        results["STR"][1] += 1; results["STR"][0] += (s_ans == "NEW")
        results["EPI"][1] += 1; results["EPI"][0] += (e_ans == "NEW")
    # recovery bookkeeping
    if author != "F" and author in seen_authors:
        prev = max((x["era"] for x in log if x["author"] == author), default=None)
        if prev and era - prev >= 2:
            recovery.append({"era": era, "author": author,
                             "absence": era - prev,
                             "STR": s_ans, "EPI": e_ans, "truth": author})
    seen_authors.add(author)
    last_era[author] = era
    log.append({"era": era, "author": author, "s_ans": s_ans, "e_ans": e_ans,
                "truth": truth, "novel": s["novel"]})
    # memory updates (after scoring -- no leakage)
    str_update(author if author != "F" else "NEW_F", f)
    epi_mem[author].append(f)
    if len(epi_mem[author]) > 3:
        epi_mem[author].pop(0)

print(f"\nSTR: {results['STR'][0]}/{results['STR'][1]}  "
      f"EPI: {results['EPI'][0]}/{results['EPI'][1]}")
print(f"novel-detection accuracy: STR {sum(novel_det['STR'])}/{len(novel_det['STR'])}  "
      f"EPI {sum(novel_det['EPI'])}/{len(novel_det['EPI'])}")
print("recovery episodes:")
for r in recovery:
    print(f"  era {r['era']} {r['author']} (absent {r['absence']}): "
          f"STR={r['STR']} EPI={r['EPI']} truth={r['truth']}")
json.dump({"results": {k: v for k, v in results.items()},
           "novel_det": {k: sum(v) for k, v in novel_det.items()},
           "recovery": recovery},
          open("p48_results.json", "w"), indent=1)
print("saved p48_results.json")
