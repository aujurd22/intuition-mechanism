"""P12 capacity scaling (P7 testbed, registered pre-run).

Question: does the forged-representation ARI scale with VQ codebook capacity?
Sweep n_codes in {8, 12, 16, 24, 32, 48, 64} x seeds {0,1,2} on the SAME
frozen hard-Eisenstein dataset as t7_multiseed (12 weights x 10 instances,
16 coeffs, noise 2e-2, rng seed 0), reusing t7_multiseed.train_vq verbatim
(imported, not rewritten).

Baseline: inherited raw KMeans ARI (n_clusters=12, n_init=20) -- one
horizontal line.

Curve shape (registered vocabulary): monotone / threshold / flat /
non-monotone.
  monotone      = per-codes means non-decreasing across the whole grid
  flat          = total range <= 0.08 and every step <= 0.02
  non-monotone  = has a downturn (neither of the above)

Verdict rule (registered):
  - exists c* such that mean ARI > inherited for ALL codes >= c* -> THRESHOLD at c*
  - mean never exceeds inherited                                  -> NEVER-EXCEEDS
  - exceeds somewhere but no such c* (e.g. up at 24, back down at 48/64)
                                                                   -> NON-ROBUST

Run:  python p12_capacity.py
"""
import json
import os
import sys
import time

import numpy as np
import torch
from sklearn.cluster import KMeans

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t0_scan import ari  # noqa: E402
from t1_modular import eisenstein_vec  # noqa: E402
from t7_multiseed import train_vq  # noqa: E402  (verbatim reuse)

CODES_GRID = (8, 12, 16, 24, 32, 48, 64)
SEEDS = (0, 1, 2)


def main():
    # Dataset: identical protocol to t7_multiseed.main (rng seed 0, weights
    # 2..24 step 2, 10 instances each, 16 coeffs, noise 2e-2, L2-normalized).
    rng = np.random.default_rng(0)
    weights = list(range(2, 26, 2))
    vecs = [eisenstein_vec(w, 16) for w in weights]
    X, labels = [], []
    for li, v in enumerate(vecs):
        for _ in range(10):
            noisy = v + rng.normal(0, 2e-2, len(v))
            X.append(noisy / (np.linalg.norm(noisy) + 1e-12))
            labels.append(li)
    X = np.stack(X).astype(np.float32)
    labels = np.array(labels)

    km_raw = KMeans(n_clusters=12, n_init=20, random_state=0).fit(X)
    a_inherited = ari(km_raw.labels_, labels)
    print(f"inherited raw KMeans ARI: {a_inherited:.4f}\n", flush=True)

    rows = []
    raw_vals = {}                      # unrounded ARI per codes (for stats)
    xt = torch.tensor(X, dtype=torch.float32)
    t0 = time.time()
    for n_codes in CODES_GRID:
        for seed in SEEDS:
            vq = train_vq(X, n_codes, seed)
            with torch.no_grad():
                _, _, _, idx = vq(xt)
            a = ari(idx.numpy(), labels)
            rows.append({"n_codes": n_codes, "seed": seed,
                         "ARI": round(a, 3)})
            raw_vals.setdefault(n_codes, []).append(a)
            print(f"  codes={n_codes:2d} seed={seed}: ARI={a:+.3f} "
                  f"[{time.time() - t0:6.1f}s]", flush=True)

    print("\n=== P12 capacity curve (forged ARI by codebook size) ===")
    per_codes = {}
    for nc in sorted(raw_vals):
        vals = raw_vals[nc]
        mu, sd = float(np.mean(vals)), float(np.std(vals))
        per_codes[nc] = {"mean": round(mu, 4), "std": round(sd, 4),
                         "values": [round(v, 3) for v in vals],
                         "mean_gt_inherited": bool(mu > a_inherited)}
        flag = "  > inherited" if mu > a_inherited else ""
        print(f"  codes={nc:2d}: mean={mu:.3f} std={sd:.3f} "
              f"vals={[round(v, 3) for v in vals]}{flag}")

    # ---- curve shape + verdict (rules in the module docstring) ----
    grid_sorted = sorted(per_codes)
    means = [float(np.mean(raw_vals[nc])) for nc in grid_sorted]
    exceeds = [m > a_inherited for m in means]
    diffs = np.diff(means)

    first_exceed = exceeds.index(True) if any(exceeds) else None
    stays_above = first_exceed is not None and all(exceeds[first_exceed:])
    mono_up = bool(np.all(diffs >= -1e-9))
    flat = bool(np.max(means) - np.min(means) <= 0.08
                and np.all(np.abs(diffs) <= 0.02))

    if flat:
        curve_shape = "flat"
    elif mono_up:
        curve_shape = "monotone"
    else:
        curve_shape = "non-monotone"

    if first_exceed is None:
        verdict, c_star = "NEVER-EXCEEDS", None
    elif stays_above:
        verdict, c_star = "THRESHOLD", grid_sorted[first_exceed]
    else:
        verdict, c_star = "NON-ROBUST", None

    print(f"\ncurve_shape: {curve_shape}")
    print(f"verdict: {verdict}" + (f" at c*={c_star}" if c_star else ""))

    out = {"plan": "P12",
           "dataset": "hard-Eisenstein 12 weights x 10 instances, 16 coeffs, "
                      "noise 2e-2, rng seed 0 (identical to t7_multiseed)",
           "protocol": {"codes_grid": list(CODES_GRID),
                        "seeds": list(SEEDS),
                        "train": "t7_multiseed.train_vq, 4000 epochs, "
                                 "imported verbatim"},
           "inherited_ari": a_inherited,
           "per_codes": {str(nc): per_codes[nc] for nc in grid_sorted},
           "rows": rows,
           "curve_shape": curve_shape,
           "c_star": c_star,
           "verdict": verdict}
    with open("p12_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("results -> p12_results.json")


if __name__ == "__main__":
    main()
