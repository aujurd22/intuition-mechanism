# -*- coding: utf-8 -*-
"""P264 merge: A/B discriminator + velocity analysis.
Usage: python p264_merge.py <dir>"""
import json, sys, glob, os
import numpy as np
from scipy import stats

def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs)/n, sum(ys)/n
    sx = (sum((x-mx)**2 for x in xs))**0.5
    sy = (sum((y-my)**2 for y in ys))**0.5
    if sx == 0 or sy == 0:
        return 0.0
    return sum((x-mx)*(y-my) for x, y in zip(xs, ys))/(sx*sy)

def main():
    d = sys.argv[1]
    js = sorted(glob.glob(os.path.join(d, "seed_*.json")))
    rows = [json.load(open(f)) for f in js]
    out = {"n": len(rows)}
    # ---- A/B: full-task probe vs component probes ----
    ys = [r["final_test"] for r in rows]
    for key in ["probe_full12", "probe_mod3", "test"]:
        for ep in [400, 700, 1000, 1300]:
            xs = [r["snaps"][str(ep)][key] for r in rows]
            out[f"corr {key}@{ep}"] = round(pearson(xs, ys), 3)
    wins = [r for r in rows if r["final_test"] >= 0.5]
    lose = [r for r in rows if r["final_test"] < 0.5]
    f12_1000_w = round(sum(w["snaps"]["1000"]["probe_full12"] for w in wins)/max(1,len(wins)), 3)
    f12_1000_l = round(sum(l["snaps"]["1000"]["probe_full12"] for l in lose)/max(1,len(lose)), 3)
    f12_400_w = round(sum(w["snaps"]["400"]["probe_full12"] for w in wins)/max(1,len(wins)), 3)
    f12_400_l = round(sum(l["snaps"]["400"]["probe_full12"] for l in lose)/max(1,len(lose)), 3)
    gap = abs(f12_1000_w - f12_1000_l)
    out["A_B"] = {
        "full12@1000_win": f12_1000_w, "full12@1000_lose": f12_1000_l,
        "full12@400_win": f12_400_w, "full12@400_lose": f12_400_l,
        "reading": ("B supported: losers hold an INCOMPLETE representation (full-task "
                    "decodability separates where component probes did not)"
                    if gap > 0.15
                    else "A supported: full-task decodability also equal — the difference "
                         "is trunk dynamics after ep1000, not static content"),
    }
    # ---- velocity ----
    vel = {}
    for key in out:
        if not key.startswith("corr disp"):
            continue
    wins_d, lose_d = [], []
    for w in wins:
        wins_d.append(w["disp"])
    for l in lose:
        lose_d.append(l["disp"])
    wkeys = sorted(wins_d[0].keys()) if wins_d else []
    for wk in wkeys:
        wm = sum(d[wk] for d in wins_d)/max(1, len(wins_d))
        lm = sum(d[wk] for d in lose_d)/max(1, len(lose_d))
        allv = [d["disp"][wk] for d in rows]
        vel[wk] = {"win": round(wm, 4), "lose": round(lm, 4),
                   "corr_final": round(pearson(allv, ys), 3)}
    out["velocity"] = vel
    json.dump(out, open(os.path.join(d, "p264_merge_verdict.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
