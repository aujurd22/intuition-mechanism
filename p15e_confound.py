"""P15-e: 2D confound regression-out (pre-registered, docs/RESEARCH_PLAN.md
P15-e row, commit 324d0df).

P15-b located the obstruction: per-sample envelope-fit bias lands on the
invariant's own axis.  A 1D oracle-z regression-out probe did NOT help
(ARI 0.325 -> 0.321): the bias is not linear in z.  Registered hypothesis:
bias = f(z, B/A) -- both modulate the pass-1 OLS effective k-weighting.

Blind confound estimates (from the sample's OWN fits, no labels):
  z_hat : exp(a1) from the direct log-domain envelope fit
  BA_hat: b1 of the ratio-domain asymptotic fit (~ B/A - 1.5)

Arms: baseline / linear-2D [1,z,b1] / quadratic-2D [+ z^2, z*b1, b1^2] /
ORACLE confound (true z, true B/A) / random-2D control.

Registered bands (true family): CONFIRMED any blind arm ARI >= 0.6 with
hit@1 >= 0.90; PARTIAL ARI in (0.325, 0.6); NEGATIVE all <= 0.325.

Run:  python p15e_confound.py
"""
import json
import os
import sys

import numpy as np
from sklearn.cluster import KMeans

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t0_scan import ari  # noqa: E402
from p15_envelope import (SIGS, blind_envelope, knn_metrics,  # noqa: E402
                          make_dataset, poch_cum, poch_ratio)
from p15c_ratio import ratio_domain_residual  # noqa: E402


def norm_rows(R):
    return R / (np.linalg.norm(R, axis=1, keepdims=True) + 1e-12)


def readout(R, y):
    m = knn_metrics(R.astype(np.float64), y)
    Q = norm_rows(R)
    km = KMeans(n_clusters=len(SIGS), n_init=10, random_state=0).fit(Q)
    m["ari"] = round(ari(km.labels_, y), 3)
    return m


def regress_out(R, C):
    """Per-coordinate OLS removal of confound columns C (n x d_c)."""
    C1 = np.hstack([np.ones((len(C), 1)), C])
    coef, *_ = np.linalg.lstsq(C1, R, rcond=None)
    return R - C1 @ coef


def confound_columns(X, z_use=None, ba_use=None, quad=False):
    """Blind per-sample confound estimates: z_hat from the direct fit's
    exponential coefficient; B/A proxy from the ratio-domain b1."""
    n = len(X)
    if z_use is None:
        z = np.empty(n)
        for i, c in enumerate(X):
            k = np.arange(len(c), dtype=float)
            M = np.stack([np.ones_like(k), k, np.log(k + 1)], axis=1)
            a, *_ = np.linalg.lstsq(M, np.log(np.abs(c) + 1e-300), rcond=None)
            z[i] = np.exp(a[1])
    else:
        z = z_use
    if ba_use is None:
        ba = np.empty(n)
        for i, c in enumerate(X):
            kr = np.arange(len(c) - 1, dtype=float)
            rho = np.diff(np.log(np.abs(c) + 1e-300))
            M = np.stack([np.ones_like(kr), 1 / (kr + 1), 1 / (kr + 1) ** 2,
                          1 / (kr + 1) ** 3], axis=1)
            b, *_ = np.linalg.lstsq(M, rho, rcond=None)
            ba[i] = b[1]
    else:
        ba = ba_use
    zs = (z - z.mean()) / (z.std() + 1e-12)
    bs = (ba - ba.mean()) / (ba.std() + 1e-12)
    cols = [zs, bs]
    if quad:
        cols += [zs ** 2, zs * bs, bs ** 2]
    return np.stack(cols, axis=1)


def main():
    results = []
    for fam_name, poch in (("cumulative-TRUE", poch_cum),
                           ("ratio-form(p14)", poch_ratio)):
        X, y, nuis = make_dataset(poch, seed=0)
        A_true, B_true, z_true = nuis[:, 0], nuis[:, 1], nuis[:, 2]
        print(f"\n=== family: {fam_name} ===", flush=True)

        R0 = np.stack([blind_envelope(c) for c in X])
        rng = np.random.default_rng(7)
        rand_cols, _ = np.linalg.qr(rng.standard_normal((len(X), 2)))
        arms = {
            "baseline": None,
            "linear2D_blind": confound_columns(X, quad=False),
            "quad2D_blind": confound_columns(X, quad=True),
            "quad2D_oracle": confound_columns(X, z_use=z_true,
                                              ba_use=B_true / A_true,
                                              quad=True),
            "random2D_control": rand_cols,
        }
        rows = {}
        for name, C in arms.items():
            R = R0 if C is None else regress_out(R0, C)
            rows[name] = readout(R, y)
            print(f"  {name:18s} hit@1={rows[name]['hit1']:.3f} "
                  f"frac3={rows[name]['frac3']:.3f} "
                  f"ARI={rows[name]['ari']:.3f}", flush=True)

        blind_aris = [rows["linear2D_blind"]["ari"],
                      rows["quad2D_blind"]["ari"]]
        blind_hit = [rows["linear2D_blind"]["hit1"],
                     rows["quad2D_blind"]["hit1"]]
        if any(a >= 0.6 and h >= 0.90 for a, h in zip(blind_aris, blind_hit)):
            verdict = "CONFIRMED"
        elif any(a > 0.325 for a in blind_aris):
            verdict = "PARTIAL"
        else:
            verdict = "NEGATIVE"
        print(f"  P15-e verdict ({fam_name}): {verdict}")
        results.append({"family": fam_name, "rows": rows,
                        "verdict": verdict})

    print(f"\nP15-e final verdict (true family): {results[0]['verdict']}")
    with open("p15e_confound_results.json", "w", encoding="utf-8") as f:
        json.dump({"results": results}, f, indent=1, default=str)
    print("results -> p15e_confound_results.json")


if __name__ == "__main__":
    main()
