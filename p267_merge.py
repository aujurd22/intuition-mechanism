# -*- coding: utf-8 -*-
"""P267 merge: screening validity + causal conversion + mediation.
Usage: python p267_merge.py <dir> <median>"""
import json, sys, glob, os
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
    d, median = sys.argv[1], float(sys.argv[2])
    ph1 = {json.load(open(f))["seed"]: json.load(open(f))
           for f in glob.glob(os.path.join(d, "phase1_*.json"))}
    out = {"median": median, "n": len(ph1)}
    # H-marker: screen alignment (train pairs, no leakage) predicts final in CONTROL
    ctl = {json.load(open(f))["seed"]: json.load(open(f))
           for f in glob.glob(os.path.join(d, "phase2_control_*.json"))}
    s = [ph1[k]["screen_align"] for k in ctl]
    f = [ctl[k]["final_test"] for k in ctl]
    r = pearson(s, f)
    w = stats.wilcoxon(s, [0.0]*len(s)) if False else None
    out["H_marker_control_corr"] = round(r, 3)
    # low-half definition (by screen align)
    keys_sorted = sorted(ctl, key=lambda k: ph1[k]["screen_align"])
    low_half = set(keys_sorted[:len(keys_sorted)//2])
    out["low_half_n"] = len(low_half)
    # causal conversion: paired, low-half seeds, screen_lrdrop vs control
    scr = {json.load(open(f))["seed"]: json.load(open(f))
           for f in glob.glob(os.path.join(d, "phase2_screen_lrdrop_*.json"))}
    alld = {json.load(open(f))["seed"]: json.load(open(f))
            for f in glob.glob(os.path.join(d, "phase2_all_lrdrop_*.json"))}
    def paired(a, b, seeds):
        ds = [a[k]["final_test"] - b[k]["final_test"] for k in seeds if k in a and k in b]
        better = sum(x > 0 for x in ds)
        p = stats.wilcoxon(ds).pvalue if len(ds) >= 6 and any(x != 0 for x in ds) else float("nan")
        return {"mean_delta": round(sum(ds)/len(ds), 4), "better": better,
                "worse": sum(x < 0 for x in ds), "wilcoxon_p": round(float(p), 4) if p == p else "n/a"}
    low = sorted(k for k in scr if k in low_half)
    out["H_causal_screen_lowhalf"] = paired(scr, ctl, low)
    out["H_causal_all_allseeds"] = paired(alld, ctl, sorted(ctl))
    # mediation: did the drop raise in-window alignment? (post_align, paired, low-half)
    med_s = [scr[k]["post_align"] - ctl[k]["post_align"] for k in low if k in scr and k in ctl]
    out["mediation_post_align_delta_lowhalf"] = round(sum(med_s)/len(med_s), 4) if med_s else None
    # gen ratios
    for name, dd in [("control", ctl), ("screen_lrdrop", scr), ("all_lrdrop", alld)]:
        accs = [dd[k]["final_test"] for k in dd]
        out[f"gen_ratio_{name}"] = round(sum(a >= 0.5 for a in accs)/len(accs), 2)
    json.dump(out, open(os.path.join(d, "p267_merge_verdict.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
