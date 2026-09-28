"""P46-c: P46 protocol on the SECOND structural family (P15
counterfactual envelope family; continuous residual ladder).

Arms: STR = per-class mean residual vector (centered), updated online;
EPI = <=3 residual instances per class (NN L2).  Decisions: nearest
centroid / instance with a label-free threshold = half the minimum
calibration centroid distance (P41 oracle arm's verified geometry).
Arcs mirror P46: RECALL (s4 strong era1, absent 2-5, returns era6),
WEAK (s6: 4 samples era4, returns era8), VARIANT (s2 extreme-z era7).

Run:  python p46c_second_family.py
"""
import json
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p15_envelope import make_dataset, poch_cum, blind_envelope  # noqa: E402

rng = np.random.default_rng(4601)
X, y, nuis = make_dataset(poch_cum, seed=777)
y = np.asarray(y)
by_class = {si: [i for i in range(len(X)) if y[i] == si] for si in range(4)}
NC = X.shape[1]
k = np.arange(NC, dtype=float)
A, B, z = nuis[:, 0], nuis[:, 1], nuis[:, 2]

# blind residual extraction (centered)
U = np.stack([np.log(np.abs(blind_envelope(c.astype(np.float64))) + 1e-300)
              for c in X])
U = U - U.mean(axis=1, keepdims=True)
# variant instance per class: extreme z
variant_of = {}
for si in range(4):
    med = np.median(z[by_class[si]])
    variant_of[si] = max(by_class[si], key=lambda i: abs(z[i] - med))

ERAS = [
    (1, [(0, 20, False), (2, 25, False)]),   # s2, s4(strong)
    (2, [(1, 20, False)]),
    (3, [(0, 15, False), (1, 15, False)]),
    (4, [(3, 4, False), (2, 15, False)]),    # s6 WEAK
    (5, [(1, 15, False), (0, 15, False)]),
    (6, [(2, 15, False), (1, 12, False)]),   # s2? no: s4 RECALL (cls 2)
    (7, [(0, 12, True), (3, 10, False)]),    # s2 VARIANT
    (8, [(3, 10, False), (1, 10, False), (0, 10, False)]),
]
stream = []
used = defaultdict(list)
for era, spec in ERAS:
    for si, n, extreme in spec:
        if extreme:
            i = variant_of[si]
            stream.append({"era": era, "idx": i, "cls": si, "variant": True})
            used[si].append(i)
            continue
        pool = [i for i in by_class[si]
                if i not in used[si] and i != variant_of[si]]
        rng.shuffle(pool)
        for i in pool[:n]:
            stream.append({"era": era, "idx": i, "cls": si, "variant": False})
            used[si].append(i)
print(f"stream: {len(stream)} samples")

# calibration threshold: half the min inter-class centroid L2 distance
cents0 = {si: U[by_class[si]].mean(axis=0) for si in range(4)}
mind = min(float(np.linalg.norm(cents0[a] - cents0[b]))
           for a in range(4) for b in range(a+1, 4))
THRESH = mind / 2
print(f"calibration: min inter-centroid L2 = {mind:.4f} -> THRESH {THRESH:.4f}")

# arms
STR_mem = {}
EPI = defaultdict(list)
score = {"STR": [0, 0], "EPI": [0, 0], "EPI-ALL": [0, 0]}
rec = {"STR": [0, 0], "EPI": [0, 0]}
var = {"STR": [0, 0], "EPI": [0, 0]}
last_era = {}
count_seen = defaultdict(int)
log = []

all_seen = []
for item in stream:
    era, si, idx = item["era"], item["cls"], item["idx"]
    u = U[idx]
    # STR: nearest centroid, accept within THRESH
    ans_s, hit_s = "NEW", False
    if STR_mem:
        best = min(STR_mem, key=lambda c: float(np.linalg.norm(u - STR_mem[c])))
        d = float(np.linalg.norm(u - STR_mem[best]))
        if d <= THRESH:
            ans_s, hit_s = best, best == si
    # EPI (3/class): NN instance within THRESH
    ans_e, hit_e = "NEW", False
    pts = [(j, c) for c in EPI for j in EPI[c]]
    if pts:
        bj = min(pts, key=lambda jc: float(np.linalg.norm(u - U[jc[0]])))
        d = float(np.linalg.norm(u - U[bj[0]]))
        if d <= THRESH:
            ans_e, hit_e = bj[1], bj[1] == si
    # EPI-ALL: NN over ALL seen (unbounded)
    a_all, h_all = "NEW", False
    if all_seen:
        bj = min(all_seen, key=lambda j: float(np.linalg.norm(u - U[j])))
        d = float(np.linalg.norm(u - U[bj]))
        if d <= THRESH:
            a_all, h_all = y[bj], True
    score["STR"][1] += 1; score["STR"][0] += hit_s
    score["EPI"][1] += 1; score["EPI"][0] += hit_e
    score["EPI-ALL"][1] += 1; score["EPI-ALL"][0] += h_all
    last_seen = last_era.get(si)
    if last_seen is not None and era - last_seen >= 2:
        rec["STR"][1] += 1; rec["STR"][0] += hit_s
        rec["EPI"][1] += 1; rec["EPI"][0] += hit_e
    if item["variant"]:
        var["STR"][1] += 1; var["STR"][0] += hit_s
        var["EPI"][1] += 1; var["EPI"][0] += hit_e
    if last_seen is not None or True:
        pass
    last_era[si] = era
    # updates
    count_seen[si] += 1
    if si in STR_mem:
        STR_mem[si] = (STR_mem[si] * (count_seen[si] - 1) + u) / count_seen[si]
    else:
        STR_mem[si] = u.copy()
    EPI[si].append(idx)
    if len(EPI[si]) > 3:
        EPI[si].pop(0)
    all_seen.append(idx)
    log.append({"era": era, "cls": si, "STR": hit_s, "EPI": hit_e,
                "EPI_ALL": h_all})

print(f"\nSTR: {score['STR'][0]}/{score['STR'][1]}  "
      f"EPI: {score['EPI'][0]}/{score['EPI'][1]}  "
      f"EPI-ALL: {score['EPI-ALL'][0]}/{score['EPI-ALL'][1]}")
print(f"recovery: STR {rec['STR'][0]}/{rec['STR'][1]}  "
      f"EPI {rec['EPI'][0]}/{rec['EPI'][1]}")
print(f"variant: STR {var['STR'][0]}/{var['STR'][1]}  "
      f"EPI {var['EPI'][0]}/{var['EPI'][1]}")
json.dump({"STR": score["STR"], "EPI": score["EPI"],
           "EPI_ALL": score["EPI-ALL"], "recovery": rec, "variant": var},
          open("p46c_results.json", "w"), indent=1)
print("saved p46c_results.json")
