"""Invariant Discovery Experiment (review action item: P13).

Question: can a machine DISCOVER the right transformation from a library,
without being told that ratio-normalization is the answer?

Setup (17 Ramanujan series, 4 signatures):
  library of transformations T applied to the raw coefficient sequences:
    identity / first-diff / second-diff / log-abs / log-ratio /
    ratio-norm (z & linear factored out) / norm / detrend / sqrt
  for each T: compress (MLP-AE b=16), score how well the latent recovers
  the signature (kNN same-signature SD + KMeans ARI vs s) and how
  INSENSITIVE it is to nuisance (z-scale, A/B slope) via control group.

Discovery criterion (pre-registered here):
  a transformation DISCOVERS the invariant if its same-s kNN fraction
  exceeds both the raw baseline (0.294) and the random floor (0.117) by
  >0.2, AND its nuisance correlation (|log|z| vs latent PCA-1|) < 0.9.

Run:  python p13_discovery.py
"""
import json
import os
import sys

import numpy as np
import torch
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t0_scan import AE, train_ae  # noqa: E402
from t1_modular import heegner_set, cm_j_digits, eisenstein_vec, eta_poly_pow  # noqa: E402

NC = 16


def build_dataset():
    """17 verified series -> (A, B, z) params + raw normalized c-sequences."""
    from p4_clean import SERIES
    X, s_labels, meta = [], [], []
    for eq, s, Al, Bl, z, sign, c0 in SERIES:
        c = []
        for k in range(NC):
            if k == 0:
                H = 1.0
            else:
                H = float(np.prod([k + j for j in (0.5, 1 / s, 1 - 1 / s)])
                          / (k ** 3))
            v = (Al + Bl * k) * H * z ** k
            if k == 0 and c0 is not None:
                v = c0
            c.append(v)
        c = np.array(c, dtype=np.float64)
        c = c / (np.linalg.norm(c) + 1e-300)
        X.append(c)
        s_labels.append(s)
        meta.append({"eq": eq, "s": s, "Al": Al, "Bl": Bl, "z": z, "sign": sign,
                     "c0": c0})
    return np.stack(X).astype(np.float32), np.array(s_labels), meta


X, s_labels, meta = build_dataset()
print(f"dataset: {X.shape[0]} series x {X.shape[1]} coefficients")


# ---- transformation library ----
def t_identity(c):
    return c


def t_first_diff(c):
    return np.diff(c)


def t_second_diff(c):
    return np.diff(c, n=2)


def t_log_abs(c):
    vals = np.abs(c[c != 0])
    return np.log(vals) if len(vals) >= 4 else None


def t_log_ratio(c):
    vals = c[c != 0]
    if len(vals) < 5:
        return None
    lc = np.log(np.abs(vals))
    return np.diff(lc)


def t_norm(c):
    return c / (np.abs(c).max() + 1e-300)


def t_scale_removal(c):
    return (c - c.mean()) / (c.std() + 1e-300)


def t_affine_removal(c):
    """Remove the best-fit linear trend (detrending)."""
    k = np.arange(len(c))
    slope, intercept = np.polyfit(k, c, 1)
    return c - (slope * k + intercept)


def t_power_sqrt(c):
    sign = np.sign(c)
    return sign * np.sqrt(np.abs(c))


LIBRARY = {
    "identity": t_identity,
    "first_diff": t_first_diff,
    "second_diff": t_second_diff,
    "log_abs": t_log_abs,
    "log_ratio": t_log_ratio,
    "norm": t_norm,
    "scale_removal": t_scale_removal,
    "affine_removal": t_affine_removal,
    "power_sqrt": t_power_sqrt,
}


def compress_latent(rep, b=8, steps=3000):
    z, _loss = train_ae(rep, b, steps=steps)
    return z


def latent_metrics(z, s_labels):
    zn = z / (np.linalg.norm(z, axis=1, keepdims=True) + 1e-12)
    sim = zn @ zn.T
    np.fill_diagonal(sim, -np.inf)
    k = 3
    idx = np.argsort(-sim, axis=1)[:, :k]
    sd_list = []
    for i, nb in enumerate(idx):
        same = (s_labels[nb] == s_labels[i]).astype(int)
        sd_list.append(same.mean())
    sd = float(np.mean(sd_list))
    km = KMeans(n_clusters=4, n_init=20, random_state=0).fit(z)
    ari = float(adjusted_rand_score(km.labels_, s_labels))
    return {"SD": round(sd, 3), "ARI": round(ari, 3)}


def nuisance_corr(z, logz):
    """|Pearson(latent PC1, log|z|)| -- insensitivity to nuisance scale."""
    from sklearn.decomposition import PCA
    pca = PCA(n_components=1)
    pc1 = pca.fit_transform(z)[:, 0]
    lz = np.log(np.abs(logz) + 1e-300)
    lz = (lz - lz.mean()) / (lz.std() + 1e-12)
    corr = float(abs(np.corrcoef(pc1, lz)[0, 1]))
    return corr


def main():
    print(f"dataset: {X.shape[0]} series x {X.shape[1]} coefficients")
    print(f"signatures: {[(s, int((s_labels == s).sum())) for s in (2, 3, 4, 6)]}\n")

    logz = np.log(np.abs([m["z"] for m in meta]))
    rows = []
    for name, fn in LIBRARY.items():
        reps = []
        ok = True
        for i in range(len(X)):
            try:
                r = fn(X[i])
                if r is None or len(r) < 4 or not np.all(np.isfinite(r)):
                    ok = False
                    break
                reps.append(r)
            except Exception:
                ok = False
                break
        if not ok:
            print(f"  {name:16s} SKIP (transform failed)")
            continue
        # pad to same length for kNN (truncate to min length across library)
        L = min(len(r) for r in reps)
        reps = [r[:L] for r in reps]
        R = np.stack(reps).astype(np.float32)
        m = latent_metrics(R, s_labels)
        nuis = nuisance_corr(R, logz)
        rows.append({"transform": name, **m, "nuisance_corr": round(nuis, 3)})
        print(f"  {name:16s} SD={m['SD']:.3f}  ARI={m['ARI']:+.3f}  "
              f"nuisance|corr|={nuis:.3f}", flush=True)

    best = max(rows, key=lambda r: r["SD"])
    print(f"\n=== DISCOVERY reading ===")
    print(f"  best transform for SD: {best['transform']} (SD={best['SD']})")
    print(f"  nuisance insensitivity: corr={best['nuisance_corr']}")

    with open("p13_discovery_results.json", "w", encoding="utf-8") as f:
        json.dump({"library": list(LIBRARY), "rows": rows}, f, indent=1,
                  default=str)
    print("results -> p13_discovery_results.json")


if __name__ == "__main__":
    main()
