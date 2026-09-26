"""P2 registered-definition variant (review-nuance): surface ARI against
INSTANCE labels, made well-posed by instance downsampling.

v1 caliber change (registered in RESEARCH_PLAN): with 120 instances the
kmeans-vs-instance ARI degenerates, so v1 measured surface ARI against
edge-count quantile bins.  The review accepted the change but flagged the
REGISTERED variant as still open.  This script closes it:

  protocol: draw 2 instances per family (12 instances, 36 samples), kmeans
  k=6 on their latents, ARI vs family labels (structure) and vs instance
  labels (surface, registered caliber); average over 10 independent draws.

P2 (registered): within the P1 window, ARI_struct - ARI_surface > 0.1.

Run: python p2_registered_variant.py
"""
import json
import os
import sys

import numpy as np
import torch
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t0_scan import ari, sd_metrics, train_ae  # noqa: E402

DRAWS = 10
INST_PER_FAM = 2


def main():
    data = np.load("t0_dataset.npz", allow_pickle=True)
    x = data["adj"].astype(np.float32).reshape(len(data["adj"]), -1)
    family = data["family"]
    instance = data["instance"]
    fams = np.array(sorted(set(family.tolist())))
    edges = x.sum(1) / 2

    rng = np.random.default_rng(0)
    draws = []
    for _ in range(DRAWS):
        sel = []
        for f in fams:
            insts = sorted(set(instance[family == f].tolist()))
            sel += list(rng.choice(insts, INST_PER_FAM, replace=False))
        m = np.isin(instance, sel)
        draws.append(np.where(m)[0])

    rows = []
    for b in (1, 2, 4, 8, 16, 32, 64, 144):
        z, loss = train_ae(x, b, steps=3000, seed=0)
        sd, surf = sd_metrics(z, family, instance, k=10)
        gaps, ari_s_all, ari_i_all = [], [], []
        for idx in draws:
            zs = z[idx]
            km = KMeans(n_clusters=len(fams), n_init=10,
                        random_state=0).fit(zs)
            ari_s = ari(km.labels_, family[idx])
            ari_i = ari(km.labels_, instance[idx])
            ari_s_all.append(ari_s)
            ari_i_all.append(ari_i)
            gaps.append(ari_s - ari_i)
        c = round(x.shape[1] / b, 1)
        row = {"b": b, "compression": c, "recon_loss": round(loss, 5),
               "SD": round(sd, 3), "surface_dom": round(surf, 3),
               "ARI_struct_reg": round(float(np.mean(ari_s_all)), 3),
               "ARI_instance_reg": round(float(np.mean(ari_i_all)), 3),
               "gap_registered": round(float(np.mean(gaps)), 3),
               "gap_std": round(float(np.std(gaps)), 3)}
        rows.append(row)
        print(f"  b={b:4d} c={c:6.1f} ARI_s={row['ARI_struct_reg']:.3f} "
              f"ARI_i={row['ARI_instance_reg']:.3f} "
              f"gap={row['gap_registered']:+.3f}+-{row['gap_std']:.3f}",
              flush=True)

    print("\n=== P2 registered-caliber reading (gap > 0.1 within window?) ===")
    verdicts = {}
    for r in rows:
        in_window = (r["SD"] - r["surface_dom"]) * 100 > 15
        ok = r["gap_registered"] > 0.1
        verdicts[r["b"]] = {"in_window": in_window,
                            "p2_registered_hold": bool(ok)}
        print(f"  b={r['b']:4d} c={r['compression']:6.1f} "
              f"window={in_window} p2_hold={ok} "
              f"gap={r['gap_registered']:+.3f}")

    in_win = [r for r in rows if (r["SD"] - r["surface_dom"]) * 100 > 15]
    if in_win:
        worst = min(in_win, key=lambda r: r["gap_registered"])
        verdict = ("HOLDS in window" if worst["gap_registered"] > 0.1
                   else "FAILS in window (worst gap "
                   f"{worst['gap_registered']:+.3f} at c="
                   f"{worst['compression']})")
    else:
        verdict = "no window found in this run"
    print(f"P2 registered-caliber verdict: {verdict}")

    with open("p2_registered_results.json", "w", encoding="utf-8") as f:
        json.dump({"protocol": {"draws": DRAWS,
                                "instances_per_family": INST_PER_FAM,
                                "samples_per_draw": len(draws[0])},
                   "rows": rows, "verdicts": verdicts,
                   "verdict": verdict}, f, indent=1)
    print("results -> p2_registered_results.json")


if __name__ == "__main__":
    main()
