"""P46-b: corrected P46 -- true online STR compression, stronger EPI
family, preregistered calibration threshold (registry row P46-b).

Self-contained: stabilize() is inlined (importing p46_stream would
re-execute its module-level stream run).

FIX-1: STR memory = cell->class-count table (updated online) + a
  bounded 240-sample discovery reservoir (era-boundary rediscovery
  only).  Decisions read the table; raw samples are discarded.
FIX-2: EPI arms at 3 / 8 / ALL / CENTROID capacity.
FIX-3: threshold frozen from an independent calibration stream;
  sensitivity sweep recorded but not used for decisions.
"""
import json
import os
import sys
from collections import defaultdict
from math import log2

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p40_corpus import build_corpus  # noqa: E402

corpus = build_corpus()
CLASSES = [(str(s), g) for (s, g) in
           [(2, "no"), (2, "alt"), (3, "no"), (3, "alt"),
            (4, "no"), (4, "alt"), (5, "no"), (5, "alt")]]
by_class = {c: [f for f, r in corpus.items() if r["cls"] == c]
            for c in CLASSES}
KEY = {c: c[0] + c[1] for c in CLASSES}
VECS = {f: np.array(corpus[f]["seq"], dtype=float) for f in corpus}

def cosd(a, b):
    return 1 - float(a @ b) / (np.linalg.norm(a)*np.linalg.norm(b) + 1e-300)

rng = np.random.default_rng(4601)
ERAS = [
    (1, [("2no", 25, False), ("5no", 25, False)]),
    (2, [("4alt", 25, False), ("2alt", 25, False)]),
    (3, [("3no", 25, False), ("4no", 25, False)]),
    (4, [("3alt", 4, False), ("2alt", 20, False)]),
    (5, [("4alt", 25, False), ("3no", 20, False)]),
    (6, [("5no", 15, False), ("2no", 15, False), ("4no", 15, False)]),
    (7, [("2no", 15, True), ("5alt", 20, False)]),
    (8, [("3alt", 12, False), ("5no", 12, False), ("2alt", 15, False)]),
]
used = defaultdict(list)
stream = []
for era, spec in ERAS:
    for cname, n, extreme in spec:
        cls = next(c for c in CLASSES
                   if (c[0] + c[1]) == cname or
                   (c[0] == cname[0] and c[1] == cname[1:]))
        pool = by_class[cls]
        if extreme:
            cand = [f for f in pool if f not in used and
                    corpus[f]["params"][0] >= 2]
            cand.sort(key=lambda f: -corpus[f]["params"][0])
        else:
            cand = [f for f in pool if f not in used]
        rng.shuffle(cand)
        for f in cand[:n]:
            stream.append({"era": era, "fid": f, "cls": cls,
                           "variant": extreme})
print(f"stream: {len(stream)} samples")

# calibration stream (disjoint from main)
calib = []
for c in CLASSES[:3]:
    pool = [f for f in by_class[c] if f not in {s["fid"] for s in stream}]
    picks = list(np.random.default_rng(99).choice(np.array(pool),
                                                  size=4, replace=False))
    calib += [(f, c) for f in picks]
intra = [cosd(VECS[a], VECS[b])
         for i, (a, ca) in enumerate(calib)
         for b, cb in calib[i+1:] if ca == cb]
inter = [cosd(VECS[a], VECS[b])
         for a, ca in calib for b, cb in calib if ca != cb]
THRESH = (max(intra) + min(inter)) / 2
print(f"calibration: max intra {max(intra):.3f}, min inter {min(inter):.3f} "
      f"-> THRESH {THRESH:.3f} (frozen)")

def stabilize(fids):
    fids = sorted(fids)
    if len(fids) < 8:
        return set()
    r2 = np.random.default_rng(99)
    idx = r2.permutation(len(fids))
    hA = [fids[i] for i in idx[:len(fids)//2]]
    hB = [fids[i] for i in idx[len(fids)//2:]]
    code = set()
    for k in range(1, 12):
        def mode(fs):
            vals = [corpus[f]["seq"][k] for f in fs]
            uq, cnt = np.unique(np.array(vals), return_counts=True)
            return int(uq[cnt.argmax()])
        ca, cb = mode(hA), mode(hB)
        if ca != cb:
            continue
        n_eq = sum(1 for f in fids if corpus[f]["seq"][k] == ca)
        if 0 < n_eq < len(fids):
            code.add(f"eq{k}={ca}")
    if any(any((corpus[f]["seq"][i] > 0) != (corpus[f]["seq"][i+1] > 0)
               for i in range(11)) for f in fids):
        code.add("flip")
    return code

code = set()
table = {}                 # cell -> {classkey: count}   (STR memory)
reservoir = []             # bounded 240
n_seen = 0
epi_protos = {"EPI-3": defaultdict(list), "EPI-8": defaultdict(list)}
epi_seen = {"EPI-ALL": []}
epi_cents = {"EPI-CENT": {}}
ARMS = ["STR", "EPI-3", "EPI-8", "EPI-ALL", "EPI-CENT"]
score = {a: [0, 0] for a in ARMS}
var_accept = {a: 0 for a in ARMS}
var_n = 0
recovery = []
last_era = {}

def sig(seq):
    out = []
    for name in sorted(code):
        if name.startswith("eq"):
            k = int(name.split("=")[0][2:]); c = int(name.split("=")[1])
            out.append(seq[k] == c)
        else:
            out.append(any((seq[i] > 0) != (seq[i+1] > 0)
                           for i in range(11)))
    return tuple(out)

for idx, item in enumerate(stream):
    era, fid, cls = item["era"], item["fid"], item["cls"]
    clskey = KEY[cls]
    seq = VECS[fid]

    # STR decision: table only
    cell = sig(seq)
    s_ans = "NEW"
    if cell in table and table[cell]:
        s_ans = max(table[cell], key=table[cell].get)

    answers = {"STR": s_ans}
    for arm in ("EPI-3", "EPI-8"):
        best_d, best_c = None, None
        for c2, fs in epi_protos[arm].items():
            for f in fs:
                d = cosd(seq, VECS[f])
                if best_d is None or d < best_d:
                    best_d, best_c = d, c2
        answers[arm] = ("NEW" if best_d is None or best_d > THRESH
                        else best_c)
    best_d, best_c = None, None
    for f in epi_seen["EPI-ALL"]:
        d = cosd(seq, VECS[f])
        if best_d is None or d < best_d:
            best_d = d
            best_c = KEY[corpus[f]["cls"]]
    answers["EPI-ALL"] = best_c if best_c else "NEW"
    best_d, best_c = None, None
    for c2, cen in epi_cents["EPI-CENT"].items():
        d = cosd(seq, cen)
        if best_d is None or d < best_d:
            best_d, best_c = d, c2
    answers["EPI-CENT"] = best_c if best_c else "NEW"

    for arm, a2 in answers.items():
        hit = a2 == clskey
        score[arm][1] += 1
        score[arm][0] += hit
        if item["variant"] and hit:
            var_accept[arm] += 1
    if item["variant"]:
        var_n += 1
    if clskey in last_era and era - last_era[clskey] >= 2:
        recovery.append({"era": era, "key": clskey,
                         "absence": era - last_era[clskey],
                         **{a: answers[a] for a in ARMS}})
    last_era[clskey] = era

    # updates (STR: table + bounded reservoir; samples otherwise discarded)
    n_seen += 1
    if len(reservoir) < 240:
        reservoir.append(fid)
    else:
        jj = int(np.random.default_rng(n_seen).integers(0, n_seen))
        if jj < 240:
            reservoir[jj] = fid
    table.setdefault(cell, defaultdict(int))
    table[cell][clskey] += 1
    for arm in ("EPI-3", "EPI-8"):
        cfg = epi_protos[arm]
        cfg[clskey].append(fid)
        cap = int(arm.split("-")[1])
        if len(cfg[clskey]) > cap:
            cen = np.mean([VECS[f] for f in cfg[clskey]], axis=0)
            far = max(cfg[clskey], key=lambda f: np.linalg.norm(VECS[f] - cen))
            cfg[clskey].remove(far)
    nn = len(epi_cents["EPI-CENT"].get(clskey, []))
    cen0 = epi_cents["EPI-CENT"].get(clskey, np.zeros(12))
    epi_cents["EPI-CENT"][clskey] = seq / nn if nn == 0 else \
        (cen0 * (nn - 1) + seq) / nn
    epi_seen["EPI-ALL"].append(fid)

    nxt = [s for s in stream[idx+1:] if s["era"] == era+1]
    if nxt and (idx + 1 >= len(stream) or stream[idx+1]["era"] != era):
        new_code = stabilize(sorted(reservoir))
        if new_code:
            code = new_code
            table = {}
            for f in reservoir:
                cc = sig(corpus[f]["seq"])
                table.setdefault(cc, defaultdict(int))
                table[cc][KEY[corpus[f]["cls"]]] += 1

print("\n=== P46-b (online STR; THRESH preregistered from calibration) ===")
for arm in ARMS:
    t = score[arm]
    print(f"  {arm:10s}: {t[0]}/{t[1]} = {100*t[0]/max(t[1],1):.1f}%   "
          f"variant {var_accept[arm]}/{var_n}")
print(f"STR footprint: {len(code)} features + {len(table)}-cell table "
      f"(raw samples discarded); EPI-ALL footprint: "
      f"{len(epi_seen['EPI-ALL'])} stored samples")
print("\nrecovery episodes:")
for r in recovery:
    print(f"  era {r['era']:2d} {r['key']} (absent {r['absence']}): " +
          "  ".join(f"{a}={r[a]}" for a in ARMS))
json.dump({"threshold": THRESH,
           "totals": {a: score[a] for a in ARMS},
           "var_accept": var_accept, "var_n": var_n,
           "recovery": recovery,
           "footprint": {"STR": {"features": len(code), "cells": len(table)},
                         "EPI-ALL": len(epi_seen["EPI-ALL"])}},
          open("p46b_results.json", "w"), indent=1)
print("saved p46b_results.json")
