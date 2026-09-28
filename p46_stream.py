"""P46: cyclic discovery protocol -- does persistent STRUCTURAL memory
change future behavior?  (L8->L9 minimal test; pre-registered.)

Setup: an open-world stream of labeled-family samples over 8 ERAS.
Classes appear, vanish, return (RECALL), drift to extreme parameters
(VARIANT), or appear briefly (WEAK observation).  Two memory arms with
the SAME information budget at decision time:

  STR (structural memory): a frozen feature code = cross-half-stable
      MDL features over ACCUMULATED SEEN SAMPLES, updated at era
      boundaries.  Decision: cell identity -> majority seen-class;
      unseen cell -> NEW.  Memory footprint: the code (constant).
  EPI (episodic memory): per class, at most PROTO prototypes (nearest
      seen sample, cosine on raw 12-term vector).  Decision: nearest
      prototype within calib threshold -> that class, else NEW.
      Memory footprint: PROTO * n_classes_seen (bounded).

Registered predictions:
  R1 (recovery): strongly-observed returning classes are recognized
     from their FIRST sample by BOTH arms (delay 0).
  R2 (weak observation): the weakly-observed class is recovered by
     EPI (prototypes persist) but LOST by STR (class too small to
     stabilize) -- a memory-type-dependent recovery asymmetry.
  R3 (variant drift): VARIANT instances of an old class are accepted
     by STR (cell-level abstraction) but rejected as NEW by EPI
     (instance distance exceeds threshold) -- the abstraction
     advantage.
  R4 (footprint): at equal decision quality, STR's memory is O(1)
     vs EPI's O(classes * PROTO).

Run:  python p46_stream.py
"""
import json
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p40_corpus import build_corpus  # noqa: E402

corpus = build_corpus()
CLASSES = [(str(s), g) for (s, g) in
           [(2, "no"), (2, "alt"), (3, "no"), (3, "alt"),
            (4, "no"), (4, "alt"), (5, "no"), (5, "alt")]]
by_class = {c: [f for f, r in corpus.items() if r["cls"] == c]
            for c in CLASSES}

PROTO = 3          # EPI memory budget per class
SEEN_STRENGTH = {c: 0 for c in CLASSES}   # samples seen per class (STR bookkeeping)

# era script: (era, [(class, n_samples, extreme?)])
# RECALL arc: 5no strong in era1, absent eras 2-5, returns era 6.
# WEAK arc:   3alt only 4 samples in era 4, returns era 8.
# VARIANT:    2no drifts to extreme cshift in era 7.
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

rng = np.random.default_rng(4601)
used = defaultdict(list)
stream = []          # (era, fid, cls, is_variant, is_first_of_return)
for era, spec in ERAS:
    for cname, n, extreme in spec:
        cls = next(c for c in CLASSES
                   if c[0] + c[1] == cname or
                   (c[0] == cname[0] and c[1] == cname[1:]))
        pool = by_class[cls]
        if extreme:
            # variant: pick the most extreme cshift params not yet used
            cand = [f for f in pool if f not in used and
                    corpus[f]["params"][0] >= 2]
            cand.sort(key=lambda f: -corpus[f]["params"][0])
        else:
            cand = [f for f in pool if f not in used]
        rng.shuffle(cand)
        take = cand[:n]
        first_return = (SEEN_STRENGTH[cls] <= 5 and era > 1)
        for j, f in enumerate(take):
            used[cls].append(f)
            SEEN_STRENGTH[cls] += 1
            stream.append({"era": era, "fid": f, "cls": cls,
                           "variant": extreme,
                           "first_return": first_return and j == 0})
print(f"stream: {len(stream)} samples over {len(ERAS)} eras")

# ---- arms ----
def cosd(a, b):
    return 1 - float(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-300)

def stabilize(seen_fids):
    """Cross-half-stable + discriminative features + flip (P42 method)."""
    fids = sorted(seen_fids)
    if len(fids) < 8:
        return set()
    rng2 = np.random.default_rng(99)
    idx = rng2.permutation(len(fids))
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

def sig_of(seq, code):
    out = []
    for name in sorted(code):
        if name.startswith("eq"):
            kk = int(name.split("=")[0][2:]); c = int(name.split("=")[1])
            out.append(seq[kk] == c)
        else:
            out.append(any((seq[i] > 0) != (seq[i+1] > 0)
                           for i in range(len(seq)-1)))
    return tuple(out)

seen_fids = []
protos = {}            # cls -> [fids] (max PROTO)
era_log = []
str_correct = epi_correct = 0
tot = 0
recovery = {"STR": [], "EPI": []}          # 1 = first-sample correct
false_new = {"STR": 0, "EPI": 0}
var_accept = {"STR": 0, "EPI": 0}
var_n = 0

# calibration set for EPI threshold: first few samples of era 1
calib_dist = []

for item in stream:
    era, fid, cls = item["era"], item["fid"], item["cls"]
    seq = corpus[fid]["seq"]
    # ---- STR decision (code frozen at previous era boundary) ----
    if era_log and era_log[-1]["era"] != era:
        pass
    code = era_log[-1]["code"] if era_log else set()
    cell_seen = defaultdict(lambda: defaultdict(int))
    for f in seen_fids:
        if code:
            cell_seen[sig_of(corpus[f]["seq"], code)][
                corpus[f]["cls"]] += 1
    s_ans = "NEW"
    if code:
        cell = sig_of(seq, code)
        if cell in cell_seen:
            best_cls = max(cell_seen[cell], key=cell_seen[cell].get)
            s_ans = best_cls[0] + best_cls[1]
    s_ok = s_ans == cls[0] + cls[1]
    str_correct += s_ok
    tot += 1

    # ---- EPI decision ----
    e_ans = "NEW"
    if protos:
        best_d, best_cls = None, None
        for c2, fs in protos.items():
            for f in fs:
                d = cosd(np.array(corpus[fid]["seq"], dtype=float),
                         np.array(corpus[f]["seq"], dtype=float))
                if best_d is None or d < best_d:
                    best_d, best_cls = d, c2
        thr = 0.25
        e_ans = (best_cls[0] + best_cls[1]) if best_d <= thr else "NEW"
    e_ok = e_ans == cls[0] + cls[1]
    epi_correct += e_ok

    # metrics
    if item["first_return"]:
        recovery["STR"].append(int(s_ok))
        recovery["EPI"].append(int(e_ok))
    if cls[0] + cls[1] not in [c[0]+c[1] for c in protos] and \
       not any(c[0]+c[1] == cls[0]+cls[1] for c in
               [c for c in CLASSES if len(protos.get(c, [])) > 0]) and \
       s_ans == "NEW":
        false_new["STR"] += 1
    if item["variant"]:
        var_n += 1
        var_accept["STR"] += (s_ans == cls[0] + cls[1])
        var_accept["EPI"] += (e_ans == cls[0] + cls[1])

    # ---- memory update at era boundaries (after last sample of era) ----
    seen_fids.append(fid)
    protos.setdefault(cls, [])
    if len(protos[cls]) < PROTO:
        protos[cls].append(fid)
    nxt = [s for s in stream if s["era"] == era + 1]
    if nxt and (item is stream[-1] or
                stream[stream.index(item)+1]["era"] != era):
        code = stabilize(seen_fids)
        era_log.append({"era": era, "code": sorted(code)})

print(f"overall: STR {str_correct}/{tot}  EPI {epi_correct}/{tot}")
print(f"recovery (first-sample of returning weak/strong classes): "
      f"STR {sum(recovery['STR'])}/{len(recovery['STR'])}  "
      f"EPI {sum(recovery['EPI'])}/{len(recovery['EPI'])}")
print(f"variant acceptance (drifted instances): STR {var_accept['STR']}/{var_n}  "
      f"EPI {var_accept['EPI']}/{var_n}")
print(f"STR memory footprint: {len(era_log[-1]['code']) if era_log else 0} features "
      f"(constant); EPI: {sum(len(v) for v in protos.values())} prototypes")
json.dump({"overall": {"STR": f"{str_correct}/{tot}",
                       "EPI": f"{epi_correct}/{tot}"},
           "recovery": recovery, "variant": {"n": var_n, "acc": var_accept},
           "eras": era_log},
          open("p46_results.json", "w"), indent=1)
print("saved p46_results.json")
