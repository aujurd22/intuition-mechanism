# -*- coding: utf-8 -*-
"""P265 merge: function-space geometry verdict.
Usage: python p265_merge.py <dir>"""
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
    Y = None
    seeds, fin = {}, {}
    for f in js:
        s = json.load(open(f))["seed"]
        z = np.load(f.replace(".json", ".npz"))
        for k in z.files:
            ep = int(k.split("_")[1])
            tgt = seeds.setdefault(s, {})
            tgt.setdefault("logits", {})[ep] = z[f"logits_{ep}"]
            tgt.setdefault("emb", {})[ep] = z[f"emb_{ep}"]
        fin[s] = json.load(open(f))["final_test"]
        if Y is None:
            P = z["logits_400"].shape[0]
            Y = np.zeros((P, 12))
            for i, (a, b) in enumerate(itertools.product(range(12), repeat=2)):
                Y[i, (a + b) % 12] = 1.0
    # use json finals
    fin = {json.load(open(f))["seed"]: json.load(open(f))["final_test"] for f in js}
    win_seeds = [s for s in fin if fin[s] >= 0.5]
    lose_seeds = [s for s in fin if fin[s] < 0.5]
    eps = [400, 700, 1000, 1300, 2000, 2500]

    def softmax(z):
        e = np.exp(z - z.max(axis=1, keepdims=True))
        return e / e.sum(axis=1, keepdims=True)

    metrics = {}
    for (a, b) in zip(eps[:-1], eps[1:]):
        m1_w, m1_l, m2_w, m2_l = [], [], [], []
        rot_w, rot_l = [], []
        for s in fin:
            fa, fb = seeds[s]["logits"][a], seeds[s]["logits"][b]
            df = (fb - fa).flatten()
            needed = (Y - softmax(fa)).flatten()
            align = float(df @ needed / ((np.linalg.norm(df) * np.linalg.norm(needed)) + 1e-9))
            ea, eb = seeds[s]["emb"][a], seeds[s]["emb"][b]
            ca = ea - ea.mean(0, keepdims=True)
            cb = eb - eb.mean(0, keepdims=True)
            ua = np.linalg.svd(ca, full_matrices=False)[2][:16]
            ub = np.linalg.svd(cb, full_matrices=False)[2][:16]
            cos = np.linalg.svd(ua @ ub.T, compute_uv=False)
            ang = float(np.degrees(np.arccos(np.clip(cos, -1, 1))).mean())
            grp_w = s in win_seeds
            (m1_w if grp_w else m1_l).append(align)
            # persistence: cosine between this window's df and the NEXT window's df
            nxt = eps[eps.index(b) + 1] if eps.index(b) + 1 < len(eps) else None
            if nxt:
                df2 = (seeds[s]["logits"][nxt] - fb).flatten()
                pers = float(df @ df2 / ((np.linalg.norm(df) * np.linalg.norm(df2)) + 1e-9))
                (m2_w if grp_w else m2_l).append(pers)
            (rot_w if grp_w else rot_l).append(ang)
        key = f"{a}_{b}"
        metrics[key] = {
            "M1_align_win": round(float(np.mean(m1_w)), 4),
            "M1_align_lose": round(float(np.mean(m1_l)), 4),
            "M2_persist_win": round(float(np.mean(m2_w)), 4) if m2_w else None,
            "M2_persist_lose": round(float(np.mean(m2_l)), 4) if m2_l else None,
            "M3_rot_deg_win": round(float(np.mean(rot_w)), 2),
            "M3_rot_deg_lose": round(float(np.mean(rot_l)), 2),
        }
    # correlation with final: M1 alignment in bifurcation window
    corr = {}
    for (a, b) in zip(eps[:-1], eps[1:]):
        aligns = []
        for s in fin:
            fa, fb = seeds[s]["logits"][a], seeds[s]["logits"][b]
            df = (fb - fa).flatten()
            needed = (Y - softmax(fa)).flatten()
            aligns.append(float(df @ needed / ((np.linalg.norm(df) * np.linalg.norm(needed)) + 1e-9)))
        corr[f"M1_{a}_{b}"] = round(pearson(aligns, [fin[s] for s in fin]), 3)
    out = {"n": len(rows), "n_win": len(win_seeds), "metrics": metrics,
           "M1_corr_with_final": corr}
    json.dump(out, open(os.path.join(d, "p265_merge_verdict.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    import itertools
    main()
