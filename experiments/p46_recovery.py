"""P46-recovery: per-episode recovery analysis with proper replay.

Replays the P46 stream logging every sample's STR/EPI outcome, then
extracts RECOVERY EPISODES: (class, era) pairs where the class was
absent for >= 2 eras and returns.  Reports first-sample correctness
for both arms, per episode, with the pre-registered R1/R2 reading.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collections import defaultdict
import numpy as np
from p40_corpus import build_corpus

corpus = build_corpus()
CLASSES = [(str(s), g) for (s, g) in
           [(2, "no"), (2, "alt"), (3, "no"), (3, "alt"),
            (4, "no"), (4, "alt"), (5, "no"), (5, "alt")]]
by_class = {c: [f for f, r in corpus.items() if r["cls"] == c]
            for c in CLASSES}
KEY = {c: c[0] + c[1] for c in CLASSES}

# rebuild the stream identically to p46_stream.py
import numpy as _np
rng = _np.random.default_rng(4601)
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
print(f"stream rebuilt: {len(stream)}")

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

def sig(seq, code):
    out = []
    for name in sorted(code):
        if name.startswith("eq"):
            k = int(name.split("=")[0][2:]); c = int(name.split("=")[1])
            out.append(seq[k] == c)
        else:
            out.append(any((seq[i] > 0) != (seq[i+1] > 0)
                           for i in range(len(seq)-1)))
    return tuple(out)

seen_fids = []
protos = {}
code = set()
era_log = []
log = []
for idx, item in enumerate(stream):
    era, fid, cls = item["era"], item["fid"], item["cls"]
    key = KEY[cls]
    prev_code = code
    cell_seen = defaultdict(lambda: defaultdict(int))
    if prev_code:
        for f in seen_fids:
            cell_seen[sig(corpus[f]["seq"], prev_code)][KEY[corpus[f]["cls"]]] += 1
    seq = corpus[fid]["seq"]
    s_ans = "NEW"
    if prev_code:
        cell = sig(seq, prev_code)
        if cell in cell_seen:
            s_ans = max(cell_seen[cell], key=cell_seen[cell].get)
    s_ok = s_ans == key

    best_d, best_c = None, None
    for c2, fs in protos.items():
        for f in fs:
            va = np.array(seq, dtype=float)
            vb = np.array(corpus[f]["seq"], dtype=float)
            dd = 1 - float(va @ vb) / (np.linalg.norm(va)*np.linalg.norm(vb) + 1e-300)
            if best_d is None or dd < best_d:
                best_d, best_c = dd, c2
    e_ans = (KEY[best_c]) if best_c is not None and best_d <= 0.25 else "NEW"
    e_ok = e_ans == key

    n_before = len([x for x in log if x["key"] == key])
    log.append({"era": era, "key": key, "s_ans": s_ans, "e_ans": e_ans,
                "s_ok": s_ok, "e_ok": e_ok, "seen_before": n_before})
    seen_fids.append(fid)
    protos.setdefault(cls, [])
    if len(protos[cls]) < 3:
        protos[cls].append(fid)
    nxt = [s for s in stream[idx+1:] if s["era"] == era+1]
    if nxt and (idx+1 >= len(stream) or stream[idx+1]["era"] != era):
        code = stabilize(seen_fids)
        era_log.append({"era": era, "code": sorted(code)})

# recovery episodes: class seen before, absent >= 2 eras, returns
last_era = {}
print("=== recovery episodes (absence >= 2 eras) ===")
reported = set()
for r in log:
    key, era = r["key"], r["era"]
    if key in last_era and era - last_era[key] >= 2 and \
       (key, era) not in reported:
        first = r
        print(f"  era {era} {key} (absent {era - last_era[key]} eras, "
              f"{first['seen_before']} prior): "
              f"STR {'OK' if first['s_ok'] else 'MISS(' + first['s_ans'] + ')'}  "
              f"EPI {'OK' if first['e_ok'] else 'MISS(' + first['e_ans'] + ')'}")
        reported.add((key, era))
    last_era[key] = era
json.dump(log, open("p46_recovery_log.json", "w"), indent=1)
print("saved p46_recovery_log.json")
