"""P46 memory-comparison protocol replicated on the SECOND family
(P15 envelope counterfactual, continuous residual ladder).

Same structure as P46: 8 eras, RECALL/WEAK/VARIANT arcs, two memory
arms (STR = per-class normalized centroid; EPI = bounded instances),
same information budget, cosine decisions.

Key difference from the t-family: the class signal is a CONTINUOUS
1-D ladder position (not a discrete support signature), and adjacent
classes are only 0.8-1.3 fit-sigma apart (P15's registered finding).
This makes the family a HARDER test for structural memory.

Run:  python p46c_memory.py
"""
import json
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p15_envelope import make_dataset, poch_cum, blind_envelope  # noqa: E402

rng = np.random.default_rng(4601)
X, y, _ = make_dataset(poch_cum, seed=777)
y = np.asarray(y)
by_class = {si: [i for i in range(len(X)) if y[i] == si] for si in range(4)}
NC = X.shape[1]

# blind residual extraction (centered)
U = np.stack([np.log(np.abs(blind_envelope(c.astype(np.float64))) + 1e-300)
              for c in X])
U = U - U.mean(axis=1, keepdims=True)

# variant instance per class: most extreme late-half bend
bend = {i: float(U[i][12:].mean() - U[i][:12].mean()) for i in range(len(X))}
variant_of = {}
for si in range(4):
    pool = by_class[si]
    variant_of[si] = max(pool, key=lambda i: abs(bend[i] - np.median([bend[j] for j in pool])))

# era script (mirrors P46 arcs)
ERAS = [
    (1, [(0, 15, False), (3, 20, False)]),
    (2, [(1, 15, False), (2, 12, False)]),
    (3, [(0, 12, False), (3, 10, False)]),
    (4, [(2, 3, False), (1, 12, False)]),     # 2 WEAK
    (5, [(1, 10, False), (3, 10, False)]),
    (6, [(2, 10, False), (0, 10, False)]),    # 2 RECALL
    (7, [(0, 8, True), (1, 10, False)]),      # 0 VARIANT
    (8, [(2, 8, False), (3, 8, False), (1, 8, False)]),
]
stream = []
used = defaultdict(list)
for era, spec in ERAS:
    for si, n, extreme in spec:
        if extreme:
            idx = variant_of[si]
            stream.append({"era": era, "idx": idx, "cls": si,
                           "variant": True})
            used[si].append(idx)
            continue
        pool = [i for i in by_class[si]
                if i not in used[si] and i != variant_of.get(si)]
        rng.shuffle(pool)
        for i in pool[:n]:
            stream.append({"era": era, "idx": i, "cls": si,
                           "variant": False})
            used[si].append(i)
print(f"stream: {len(stream)} samples")

# calibration threshold (era-1 within-class NN distances, scaled)
cal = [s for s in stream if s["era"] == 1]
intra = []
for i in range(len(cal)):
    for j in range(i+1, len(cal)):
        if cal[i]["cls"] == cal[j]["cls"]:
            intra.append(cosd_a := 1 - float(U[cal[i]["idx"]] @ U[cal[j]["idx"]]) /
                         (np.linalg.norm(U[cal[i]["idx"]]) * np.linalg.norm(U[cal[j]["idx"]]) + 1e-300))
THRESH = float(np.median(intra)) * 1.5
print(f"calibration THRESH: {THRESH:.4f}")

def cosd(a, b):
    return 1 - float(a @ b) / (np.linalg.norm(a)*np.linalg.norm(b) + 1e-300)

# memory arms
str_mem = {}     # cls -> normalized centroid
epi = defaultdict(list)  # cls -> [indices] (max 3)
EPI_CAP = 3

score = {"STR": [0, 0], "EPI": [0, 0]}
var = {"STR": [0, 0], "EPI": [0, 0]}
rec = {"STR": [0, 0], "EPI": [0, 0]}
last_era = {}
log = []
var_n = 0

for item in stream:
    era, si, idx = item["era"], item["cls"], item["idx"]
    u = U[idx]
    # STR: nearest centroid, no threshold (forced classification)
    if str_mem:
        best = min(str_mem, key=lambda c: cosd(u, str_mem[c]))
        s_ans = best
    else:
        s_ans = si  # first sample: default
    s_ok = s_ans == si
    # EPI: NN instance
    pts = [(j, c) for c in epi for j in epi[c]]
    if pts:
        bj = min(pts, key=lambda jc: cosd(u, U[jc[0]]))
        e_ans = bj[1]
    else:
        e_ans = "NEW"
    e_ok = e_ans == si

    for arm, ans, ok in (("STR", s_ans, s_ok), ("EPI", e_ans, e_ok)):
        score[arm][1] += 1; score[arm][0] += ok
        if item["variant"]:
            var_n += 1; var[arm][0] += ok; var[arm][1] += 1
    # recovery
    if si in last_era and era - last_era[si] >= 2:
        rec["STR"][1] += 1; rec["STR"][0] += s_ok
        rec["EPI"][1] += 1; rec["EPI"][0] += e_ok
    last_era[si] = era

    # updates
    n = sum(1 for s in stream[:stream.index(item)+1] if s["cls"] == si)
    if si in str_mem:
        str_mem[si] = (str_mem[si] * (n-1) + u) / n
    else:
        str_mem[si] = u.copy()
    epi[si].append(idx)
    if len(epi[si]) > EPI_CAP:
        epi[si].pop(0)

print(f"\nSTR: {score['STR'][0]}/{score['STR'][1]} = "
      f"{100*score['STR'][0]/score['STR'][1]:.1f}%")
print(f"EPI: {score['EPI'][0]}/{score['EPI'][1]} = "
      f"{100*score['EPI'][0]/score['EPI'][1]:.1f}%")
print(f"variant (n={var_n}): STR {var['STR'][0]}/{var['STR'][1]}  "
      f"EPI {var['EPI'][0]}/{var['EPI'][1]}")
print(f"recovery episodes: {rec['STR'][0]+rec['EPI'][0]} total scored")
json.dump({"STR": score["STR"], "EPI": score["EPI"],
           "variant": var, "recovery": rec},
          open("p46c_memory_results.json", "w"), indent=1)
print("saved p46c_memory_results.json")
