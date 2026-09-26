"""P13 v3 corrected grid: TRUE Ramanujan-Sato sequences (imported from
p4_clean.build, the 17/17-verified construction) x bottleneck x seed.

FINDING THIS FIXES: p13_deep.py generated its sequences with a WRONG
per-k product H(k) = (k+0.5)(k+1/s)(k+2-1/s)/k^3 instead of the true
cumulative hypergeometric H_k = (1/2)_k (1/s)_k (1-1/s)_k / (k!)^3.
Its inputs were surrogates where the signature sits in a leading
one-step factor (EASIER to find than in the real series).  The negative
verdict on those easier inputs transfers conservatively, but the grid
must be rerun on the true coefficients.

Grid: transforms (SINGLE library) x b in {4,16} x seeds {0,1,2}, two-
phase consolidation AE (p13_deep.train_two_phase), three readouts.  For
each transform we ALSO score the raw (pre-AE) representation -- this
separates "transform extracts the signature but the AE destroys it"
from "the transform itself is insufficient".

Run:  python p13_grid.py   (~30-40 min CPU, serial)
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p4_clean import SERIES, build  # noqa: E402  (TRUE sequences)
from p13_deep import (SINGLE, readout_all,  # noqa: E402
                      train_two_phase)


def knn_hit1(rep, s_arr, k=3):
    rep = np.atleast_2d(rep)
    zn = rep / (np.linalg.norm(rep, axis=1, keepdims=True) + 1e-12)
    sim = zn @ zn.T
    np.fill_diagonal(sim, -np.inf)
    idx = np.argsort(-sim, axis=1)[:, :k]
    h1 = sum(int(s_arr[nb[0]] == s_arr[i]) for i, nb in enumerate(idx))
    return h1


def main():
    seqs, meta, _ = build()
    X = np.stack(seqs)
    s_arr = np.array([m["s"] for m in meta])
    n = len(s_arr)
    chance = float(np.mean([(s_arr == s_arr[i]).sum() - 1
                            for i in range(n)]) / (n - 1))
    print(f"TRUE sequences: {X.shape}, signatures "
          f"{[(s, int((s_arr == s).sum())) for s in (2, 3, 4, 6)]}; "
          f"chance hit@1 = {chance:.3f}", flush=True)

    reps_by_t = {}
    for name, fn in SINGLE.items():
        reps = []
        ok = True
        for c in X:
            try:
                r = fn(c)
                if r is None or len(r) < 8 or not np.all(np.isfinite(r)):
                    ok = False
                    break
                r = r / (np.linalg.norm(r) + 1e-12)
                reps.append(r.astype(np.float32))
            except Exception:
                ok = False
                break
        if ok:
            L = min(len(r) for r in reps)
            reps_by_t[name] = np.stack([r[:L] for r in reps])
    print(f"transforms usable: {list(reps_by_t)}", flush=True)

    cells = []
    t00 = time.time()
    for name, reps in reps_by_t.items():
        raw_h1 = knn_hit1(reps, s_arr)
        row = {"transform": name, "raw_hit1_preAE": int(raw_h1), "cells": []}
        for b in (4, 16):
            for seed in (0, 1, 2):
                t0 = time.time()
                z = train_two_phase(reps, b=b, seed=seed)
                ro = readout_all(z, s_arr)
                cell = {"b": b, "seed": seed,
                        "knn_hit1": ro["knn"]["hit1"],
                        "kwta2_hit1": ro["kwta2"]["hit1"],
                        "kwta4_hit1": ro["kwta4"]["hit1"]}
                row["cells"].append(cell)
                best = max(cell["knn_hit1"], cell["kwta2_hit1"],
                           cell["kwta4_hit1"])
                print(f"  {name:22s} b={b:2d} seed={seed} "
                      f"best_hit1={best}/17 raw={raw_h1}/17 "
                      f"({time.time()-t0:.0f}s)", flush=True)
        cells.append(row)

    # aggregate: best AE cell per transform + raw reference
    print(f"\n=== P13 v3 summary (chance {chance:.3f}; "
          f"total {time.time()-t00:.0f}s) ===")
    summary = []
    for row in cells:
        best_cell = max(row["cells"], key=lambda c: max(
            c["knn_hit1"], c["kwta2_hit1"], c["kwta4_hit1"]))
        best_h1 = max(best_cell["knn_hit1"], best_cell["kwta2_hit1"],
                      best_cell["kwta4_hit1"])
        summary.append({"transform": row["transform"],
                        "raw_hit1_preAE": row["raw_hit1_preAE"],
                        "best_ae_hit1": best_h1,
                        "best_cell": best_cell})
        print(f"  {row['transform']:22s} raw={row['raw_hit1_preAE']:2d}/17 "
              f"bestAE={best_h1:2d}/17 (b={best_cell['b']}, "
              f"seed={best_cell['seed']})")
    n_above = sum(1 for s in summary
                  if max(s["raw_hit1_preAE"], s["best_ae_hit1"]) / 17 > chance + 0.15)
    print(f"\ntransforms beating chance+0.15: {n_above}/{len(summary)}")

    with open("p13_grid_results.json", "w", encoding="utf-8") as f:
        json.dump({"chance": chance, "grid": "b{4,16} x seed{0,1,2}",
                   "sequences": "TRUE (p4_clean.build, 17/17 verified)",
                   "summary": summary, "cells": cells},
                  f, indent=1, default=str)
    print("results -> p13_grid_results.json")


if __name__ == "__main__":
    main()
