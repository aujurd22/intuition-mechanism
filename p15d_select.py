"""P15-d: blind scheme selection (pre-registered, docs/RESEARCH_PLAN.md
P15-d row, commit 7d60dd4).

P15-c showed the two generic envelope schemes are COMPLEMENTARY:
  direct log-domain fit : 0.946/0.325 (true family)  0.992/0.361 (ratio fam)
  ratio-domain cumulant : 0.838/0.087 (true family)  1.000/1.000 (ratio fam)

Question: can the scheme be SELECTED per dataset without labels?
Registered criterion: kmeans(k=4) on each candidate (raw / direct /
ratio), score each clustering by cosine silhouette, pick the highest;
only then look at labels (evaluation-only).

Registered bands: CONFIRMED = the better scheme (by ARI) is selected on
BOTH families; PARTIAL = one; NEGATIVE = neither.  Concatenation
ensemble reported as a diagnostic.

Run:  python p15d_select.py
"""
import json
import os
import sys

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t0_scan import ari  # noqa: E402
from p15_envelope import (SIGS, blind_envelope, knn_metrics,  # noqa: E402
                          make_dataset, poch_cum, poch_ratio)
from p15c_ratio import ratio_domain_residual  # noqa: E402


def norm_rows(R):
    return R / (np.linalg.norm(R, axis=1, keepdims=True) + 1e-12)


def eval_scheme(R, y):
    Q = norm_rows(R)
    km = KMeans(n_clusters=len(SIGS), n_init=10, random_state=0).fit(Q)
    sil = float(silhouette_score(Q, km.labels_, metric="cosine"))
    m = knn_metrics(R.astype(np.float64), y)
    return {"silhouette": round(sil, 4),
            "hit1": m["hit1"], "ari": round(ari(km.labels_, y), 3)}


def main():
    results = []
    for fam_name, poch in (("cumulative-TRUE", poch_cum),
                           ("ratio-form(p14)", poch_ratio)):
        X, y, _ = make_dataset(poch, seed=0)
        print(f"\n=== family: {fam_name} ===", flush=True)

        cands = {
            "raw": X,
            "direct": np.stack([blind_envelope(c) for c in X]),
            "ratio": np.stack([ratio_domain_residual(c) for c in X]),
        }
        rows = {}
        for name, R in cands.items():
            rows[name] = eval_scheme(R, y)
            print(f"  {name:7s} silhouette={rows[name]['silhouette']:+.4f} "
                  f"-> hit@1={rows[name]['hit1']:.3f} "
                  f"ARI={rows[name]['ari']:.3f}", flush=True)

        picked = max(rows, key=lambda n: rows[n]["silhouette"])
        best_true = max(rows, key=lambda n: rows[n]["ari"])
        ok = picked == best_true
        print(f"  selected: {picked} (best by ARI: {best_true}) "
              f"-> {'CORRECT' if ok else 'WRONG'}")

        # diagnostic: concatenation ensemble
        ens = np.hstack([norm_rows(cands["direct"]),
                         norm_rows(cands["ratio"])])
        rows["ensemble"] = eval_scheme(ens, y)
        print(f"  ensemble hit@1={rows['ensemble']['hit1']:.3f} "
              f"ARI={rows['ensemble']['ari']:.3f} (diagnostic)")

        results.append({"family": fam_name, "rows": rows,
                        "selected": picked, "best_by_ari": best_true,
                        "selection_correct": bool(ok)})

    n_ok = sum(r["selection_correct"] for r in results)
    verdict = ("CONFIRMED" if n_ok == 2 else "PARTIAL" if n_ok == 1
               else "NEGATIVE")
    print(f"\nP15-d verdict: {verdict} ({n_ok}/2 families select the "
          f"higher-ARI scheme blind)")
    with open("p15d_select_results.json", "w", encoding="utf-8") as f:
        json.dump({"results": results, "verdict": verdict}, f, indent=1,
                  default=str)
    print("results -> p15d_select_results.json")


if __name__ == "__main__":
    main()
