"""P15-f: salience-corrected scheme selection (pre-registered,
docs/RESEARCH_PLAN.md P15-f row, commit 3bc6b4f).

P15-d: silhouette selection falls into the salience trap on the true
family (picks raw by 0.0009).  Registered fix: remove the TOP-1
PRINCIPAL COMPONENT of each candidate's row-normalized representation
before clustering+scoring -- salient structure lives on one variance
axis and is discounted; invariant structure is distributed and survives.

Bootstrap (200 resamples) CI on the decisive silhouette margin.

Registered bands: CONFIRMED = corrected selection picks the higher-ARI
scheme on BOTH families with CI excluding zero on the decisive margin;
PARTIAL = correct selection, CI includes zero; NEGATIVE = any wrong
selection.

Run:  python p15f_select.py
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


def drop_pc1(Q):
    mu = Q.mean(0)
    U, S, Vt = np.linalg.svd(Q - mu, full_matrices=False)
    return norm_rows((Q - mu) - np.outer(U[:, 0] * S[0], Vt[0]) + mu)


def corrected_silhouette(R, rng):
    Q = drop_pc1(norm_rows(R))
    km = KMeans(n_clusters=len(SIGS), n_init=10, random_state=0).fit(Q)
    return float(silhouette_score(Q, km.labels_, metric="cosine")), km


def naive_silhouette(R):
    Q = norm_rows(R)
    km = KMeans(n_clusters=len(SIGS), n_init=10, random_state=0).fit(Q)
    return float(silhouette_score(Q, km.labels_, metric="cosine"))


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
        rng = np.random.default_rng(11)
        for name, R in cands.items():
            s_corr, km = corrected_silhouette(R, rng)
            s_naive = naive_silhouette(R)
            rows[name] = {"sil_naive": round(s_naive, 4),
                          "sil_corrected": round(s_corr, 4),
                          "ari": round(ari(km.labels_, y), 3),
                          "hit1": knn_metrics(R.astype(np.float64), y)["hit1"]}
            print(f"  {name:7s} sil_naive={s_naive:+.4f} "
                  f"sil_corr={s_corr:+.4f} ARI={rows[name]['ari']:+.3f}",
                  flush=True)

        pick_corr = max(rows, key=lambda n: rows[n]["sil_corrected"])
        pick_naive = max(rows, key=lambda n: rows[n]["sil_naive"])
        best = max(rows, key=lambda n: rows[n]["ari"])
        # bootstrap CI on the decisive corrected margin
        Qs = {n: drop_pc1(norm_rows(R)) for n, R in cands.items()}
        margins = []
        ranked = sorted(rows, key=lambda n: -rows[n]["sil_corrected"])
        for _ in range(200):
            idx = rng.choice(len(y), len(y), replace=True)
            sils = {}
            for n in ranked[:2]:
                km = KMeans(n_clusters=len(SIGS), n_init=5,
                            random_state=0).fit(Qs[n][idx])
                sils[n] = silhouette_score(Qs[n][idx], km.labels_,
                                           metric="cosine")
            margins.append(sils[ranked[0]] - sils[ranked[1]])
        lo, hi = np.percentile(margins, [2.5, 97.5])
        decisive_ci_excl = (lo > 0)
        print(f"  selected naive={pick_naive} corrected={pick_corr} "
              f"(best ARI: {best}); decisive margin CI "
              f"[{lo:+.4f},{hi:+.4f}] excludes0={decisive_ci_excl}")

        correct = (pick_corr == best)
        verdict = ("CONFIRMED" if correct and decisive_ci_excl
                   else "PARTIAL" if correct else "NEGATIVE")
        results.append({"family": fam_name, "rows": rows,
                        "pick_naive": pick_naive, "pick_corrected":
                        pick_corr, "best_by_ari": best,
                        "ci": [round(float(lo), 4), round(float(hi), 4)],
                        "verdict": verdict})
        print(f"  P15-f verdict ({fam_name}): {verdict}")

    n_ok = sum(r["verdict"] == "CONFIRMED" for r in results)
    if n_ok == 2:
        final = "CONFIRMED"
    elif all(r["pick_corrected"] == r["best_by_ari"] for r in results):
        final = "PARTIAL"
    else:
        final = "NEGATIVE"
    print(f"\nP15-f final verdict: {final}")
    with open("p15f_select_results.json", "w", encoding="utf-8") as f:
        json.dump({"results": results, "verdict": final}, f, indent=1,
                  default=str)
    print("results -> p15f_select_results.json")


if __name__ == "__main__":
    main()
