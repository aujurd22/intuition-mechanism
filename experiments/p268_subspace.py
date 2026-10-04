# -*- coding: utf-8 -*-
"""P268: phase-2 offline analysis on banked trajectories (pre-registered).
Usage: python p268_subspace.py <p265_seeds_dir>"""
import json, sys, glob, os, itertools
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

def sub_angle(A, B, k):
    ca = A - A.mean(0, keepdims=True)
    cb = B - B.mean(0, keepdims=True)
    ua = np.linalg.svd(ca, full_matrices=False)[2][:k]
    ub = np.linalg.svd(cb, full_matrices=False)[2][:k]
    cos = np.linalg.svd(ua @ ub.T, compute_uv=False)
    return float(np.degrees(np.arccos(np.clip(cos, -1, 1))).mean())

def main():
    d = sys.argv[1]
    rows = []
    for f in sorted(glob.glob(os.path.join(d, "seed_*.json"))):
        r = json.load(open(f))
        s = r["seed"]
        z = np.load(f.replace(".json", ".npz"))
        emb = {int(k.split("_")[1]): z[f"emb_{int(k.split('_')[1])}"]
               for k in z.files if k.startswith("emb_")}
        lg = {int(k.split("_")[1]): z[f"logits_{int(k.split('_')[1])}"]
              for k in z.files if k.startswith("logits_")}
        # replicate the worker split to label rows
        random = __import__("random")
        pairs = list(itertools.product(range(12), range(12)))
        random.Random(s).shuffle(pairs)
        ntr = int(len(pairs) * 0.6)
        tr_rows = [a * 12 + b for a, b in pairs[:ntr]]
        te_rows = [a * 12 + b for a, b in pairs[ntr:]]
        rows.append({"seed": s, "final": r["final_test"], "emb": emb, "lg": lg,
                     "tr_rows": tr_rows, "te_rows": te_rows})
    EPS = [400, 700, 1000, 1300, 2000, 2500]
    wins = [r for r in rows if r["final"] >= 0.5]
    lose = [r for r in rows if r["final"] < 0.5]
    out = {"n": len(rows), "n_win": len(wins)}
    res = {}
    for a, b in zip(EPS[:-1], EPS[1:]):
        wk = f"{a}_{b}"
        m = {}
        # A1 trunk rotation
        m["A1_trunk_rot_win"] = round(np.mean([sub_angle(w["emb"][a], w["emb"][b], 32) for w in wins]), 2)
        m["A1_trunk_rot_lose"] = round(np.mean([sub_angle(l["emb"][a], l["emb"][b], 32) for l in lose]), 2)
        # A2 function rotation (centered logits, top-8)
        m["A2_fn_rot_win"] = round(np.mean([sub_angle(w["lg"][a], w["lg"][b], 8) for w in wins]), 2)
        m["A2_fn_rot_lose"] = round(np.mean([sub_angle(l["lg"][a], l["lg"][b], 8) for l in lose]), 2)
        # A3 row-displacement ratio (emb)
        def ratio(r):
            d = np.linalg.norm(r["emb"][b] - r["emb"][a], axis=1)
            return float(d[r["te_rows"]].mean() / (d[r["tr_rows"]].mean() + 1e-9))
        m["A3_ratio_win"] = round(float(np.mean([ratio(w) for w in wins])), 4)
        m["A3_ratio_lose"] = round(float(np.mean([ratio(l) for l in lose])), 4)
        # A4 curvature proxy: angle between consecutive displacement vectors
        def curv(r, i):
            d1 = (r["emb"][EPS[i+1]] - r["emb"][EPS[i]]).flatten()
            d2 = (r["emb"][EPS[i+2]] - r["emb"][EPS[i+1]]).flatten()
            cos = d1 @ d2 / ((np.linalg.norm(d1) * np.linalg.norm(d2)) + 1e-9)
            return float(np.degrees(np.arccos(np.clip(cos, -1, 1))))
        for i in range(len(EPS) - 2):
            m[f"A4_curv_{EPS[i]}_{EPS[i+1]}_{EPS[i+2]}_win"] = round(np.mean([curv(w, i) for w in wins]), 2)
            m[f"A4_curv_{EPS[i]}_{EPS[i+1]}_{EPS[i+2]}_lose"] = round(np.mean([curv(l, i) for l in lose]), 2)
        # correlations with final
        m["A1_rot_corr"] = round(pearson([sub_angle(r["emb"][a], r["emb"][b], 32) for r in rows], [r["final"] for r in rows]), 3)
        m["A2_rot_corr"] = round(pearson([sub_angle(r["lg"][a], r["lg"][b], 8) for r in rows], [r["final"] for r in rows]), 3)
        m["A3_ratio_corr"] = round(pearson([ratio(r) for r in rows], [r["final"] for r in rows]), 3)
        res[wk] = m
    out["per_window"] = res
    # pre-registered discriminative test (multiplicity-aware)
    disc = []
    for wk, m in res.items():
        for k, v in m.items():
            if k.endswith("_win"):
                kl = k[:-4] + "_lose"
                if abs(v - m[kl]) / max(abs(v), abs(m[kl]), 1e-9) > 0.15:
                    disc.append(f"{wk}:{k}")
    out["discriminative_windows"] = disc
    json.dump(out, open("p268_verdict.json", "w"), indent=1)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
