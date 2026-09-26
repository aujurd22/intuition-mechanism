"""P9: next-coefficient prediction objective (registered prediction P9).

Registered prediction (docs/RESEARCH_PLAN.md, registered 2026-09-26 pre-run):
  "Next-coefficient prediction (given c_0..c_k predict c_{k+1}) on the 21
   verified members: latent/predictor state clusters by signature s
   (ARI vs s > surface-magnitude baseline + 0.15); the predictor
   internalizes the ratio operator."  Falsifier: "clusters by surface
   magnitude or ties."

Operationalization (fixed pre-run; deviations recorded here and in the JSON):
  - 21 verified members exist, 20 are reproducible from this repo: the 17
    literature series (p4_clean.SERIES, Ramanujan 1914 eq 28-44) + the 3
    mechanical members (p6_generalize.MECH, d=19/43/67).  The 4th mechanical
    member (d=163) has no encoding in the current pipeline -> the run uses
    these 20 and records the deviation.
  - Coefficients: NC=64 per series, c_k = sign*(A+B*k)*H_k(1/s)*z^k (+c0 at
    k=0 for the sub-family that has one) -- the p4/p6 construction verbatim.
    log|c_k| is computed in log space (k*log|z| + log(A+B*k) + log H_k):
    at NC=64, z^k leaves float range for the small-|z| series (d67:
    |z|^63 ~ 1e-688), so raw float c_k underflows to 0 and would poison the
    log-diffs.  k=0 keeps the true float value because the +c0 series add
    c0 there (outside the log formula).
  - Predictor: MLP 8-32-32-1 (tanh).  Input: 8-step window of log-diffs
    d_k = log|c_{k+1}| - log|c_k| (55 windows per series); target: the next
    diff.  Latent state = last hidden layer (32-d), averaged over the
    held-out series' windows.  Training: MSE, Adam lr 1e-3, 300 epochs,
    minibatch 128, global standardization of X/y computed on the 19 training
    series only (no held-out leakage).  Leave-one-series-out x 20; seed 0
    everywhere; hyperparameters fixed pre-run (no tuning whatever happens).
  - Clustering: KMeans(k=4, n_init=20, random_state=0) on:
      latent            -> ari_latent_vs_s        MAIN (ARI vs signature s)
      log|c|[:8]        -> ari_input_baseline     surface proxy 1 (input repr)
      latent            -> ari_surface_magnitude  surface proxy 2 (ARI vs
                                                   |c_0| quartile bins, 5/bin)
      ratio_repr (p6)   -> ari_invariant_control  health check: the hand-
                                                   normalized R-shape should
                                                   cluster by s almost
                                                   perfectly; a low value
                                                   means pipeline bug
  - Verdict: SUPPORTED iff ari_latent_vs_s > max(ari_input_baseline,
    ari_surface_magnitude) + 0.15, else NOT-SUPPORTED (recorded as-is;
    a negative result is a result).

Run:  python p9_predict.py
"""
import json
import os
import sys

import numpy as np
import torch
import torch.nn as nn
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import sklearn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p4_clean import SERIES, hyper3  # noqa: E402
from p6_generalize import MECH, ratio_repr  # noqa: E402
from t0_scan import ari  # noqa: E402

NC = 64       # coefficients per series (P9 spec; p4/p6 used 32)
WINDOW = 8    # log-diff window length
HIDDEN = 32   # hidden width; latent = last hidden layer
EPOCHS = 300
LR = 1e-3
BATCH = 128
SEED = 0      # fixed pre-run; no tuning
N_CLUSTERS = 4


def build_all():
    """20 series (17 literature + 3 mechanical), NC coefficients each.

    Returns (rows, seqs, logcs):
      rows  metadata (incl. sign/c0, needed to replay the p6 construction)
      seqs float coefficient arrays, p6_generalize.build_all verbatim
           (late entries of small-|z| series underflow to 0.0 -- only the
           first 32 coefficients are ever consumed, by ratio_repr, exactly
           as in p6; k=0 never underflows)
      logcs  log|c_k| computed in log space (underflow-proof); k=0 uses the
           true float value so the +c0 sub-family is handled exactly
    """
    rows, seqs, logcs = [], [], []
    entries = [(eq, s, Al, Bl, z, sign, c0, False)
               for eq, s, Al, Bl, z, sign, c0 in SERIES]
    entries += [(name, s, Al, Bl, z, +1, None, True)
                for name, s, Al, Bl, z in MECH]
    for name, s, Al, Bl, z, sign, c0, mech in entries:
        lz = float(np.log(abs(z)))
        c, logc = [], np.empty(NC)
        for k in range(NC):
            H = hyper3(0.5, 1 / s, 1 - 1 / s, k)
            v = sign * (Al + Bl * k) * H * z ** k
            if c0 is not None and k == 0:
                v += c0
            c.append(v)
            if k == 0:
                logc[k] = np.log(abs(v) + 1e-300)   # +c0 lives outside logs
            else:
                logc[k] = np.log(abs(Al + Bl * k)) + np.log(H) + k * lz
        seqs.append(np.array(c, dtype=np.float64))
        logcs.append(logc)
        rows.append({"name": name, "s": s, "Al": Al, "Bl": Bl, "z": z,
                     "sign": sign, "c0": c0, "mech": mech})
    return rows, seqs, logcs


def windows(logc):
    """8-step windows of log-diffs -> next diff (55 windows for NC=64).

    Note d_0 is c0-polluted for the +c0 sub-family; it is kept because the
    registered objective is next-coefficient prediction on the raw series.
    """
    d = np.diff(logc)
    X = np.stack([d[j:j + WINDOW] for j in range(len(d) - WINDOW)])
    y = d[WINDOW:]
    return X, y


class Predictor(nn.Module):
    """8 -> 32 -> 32 -> 1 MLP; latent = post-tanh second hidden layer."""

    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(WINDOW, HIDDEN)
        self.fc2 = nn.Linear(HIDDEN, HIDDEN)
        self.out = nn.Linear(HIDDEN, 1)

    def forward(self, x, return_hidden=False):
        h = torch.tanh(self.fc1(x))
        h = torch.tanh(self.fc2(h))
        y = self.out(h).squeeze(-1)
        return (y, h) if return_hidden else y


def train_fold(Xtr, ytr):
    """Train one LOSO fold (identical seed for every fold)."""
    torch.manual_seed(SEED)
    model = Predictor()
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    Xt = torch.from_numpy(Xtr).float()
    yt = torch.from_numpy(ytr).float()
    g = torch.Generator().manual_seed(SEED)
    model.train()
    for _ in range(EPOCHS):
        perm = torch.randperm(len(Xt), generator=g)
        for i in range(0, len(Xt), BATCH):
            idx = perm[i:i + BATCH]
            opt.zero_grad()
            nn.functional.mse_loss(model(Xt[idx]), yt[idx]).backward()
            opt.step()
    return model


def main():
    rows, seqs, logcs = build_all()
    s_arr = np.array([r["s"] for r in rows])
    names = [r["name"] for r in rows]
    n = len(rows)
    print(f"members: {n} (literature {sum(not r['mech'] for r in rows)}, "
          f"mechanical {sum(r['mech'] for r in rows)})")
    print("signatures: " + ", ".join(
        f"s={s}: {int((s_arr == s).sum())}" for s in (2, 3, 4, 6)))

    data = [windows(lc) for lc in logcs]     # per-series (X 55x8, y 55)
    print(f"windows per series: {len(data[0][0])}\n")

    # ---- leave-one-series-out: latent = mean last-hidden activation ----
    latent = np.zeros((n, HIDDEN))
    mse_model, mse_persist = [], []
    for i in range(n):
        tr = [j for j in range(n) if j != i]
        Xtr = np.concatenate([data[j][0] for j in tr])
        ytr = np.concatenate([data[j][1] for j in tr])
        mu, sd = Xtr.mean(), Xtr.std() + 1e-12
        ymu, ysd = ytr.mean(), ytr.std() + 1e-12
        model = train_fold((Xtr - mu) / sd, (ytr - ymu) / ysd)
        Xi, yi = data[i]
        model.eval()
        with torch.no_grad():
            pred, h = model(torch.from_numpy((Xi - mu) / sd).float(),
                            return_hidden=True)
        latent[i] = h.mean(dim=0).numpy()
        # raw-unit held-out MSE + persistence baseline (last input diff)
        pred_raw = pred.numpy() * ysd + ymu
        mse_model.append(float(np.mean((pred_raw - yi) ** 2)))
        mse_persist.append(float(np.mean((Xi[:, -1] - yi) ** 2)))
        print(f"  fold {i + 1:2d}/{n} held-out {names[i]:5s} (s={s_arr[i]}): "
              f"mse {mse_model[-1]:.4f} vs persistence {mse_persist[-1]:.4f}")

    # ---- clustering & ARIs ----
    def km_labels(rep):
        return KMeans(n_clusters=N_CLUSTERS, n_init=20,
                      random_state=SEED).fit_predict(rep)

    latent_lab = km_labels(latent)
    ari_latent_vs_s = ari(latent_lab, s_arr)

    # surface proxy 1: raw input representation, log|c| first 8 terms
    input_repr = np.stack([lc[:WINDOW] for lc in logcs])
    ari_input_baseline = ari(km_labels(input_repr), s_arr)

    # surface proxy 2: latent clusters vs |c_0| quartile bins (5 per bin;
    # rank-based, so log vs raw gives identical bins)
    c0_abs = np.array([abs(seqs[i][0]) for i in range(n)])
    mag_bins = (np.argsort(np.argsort(c0_abs)) // 5).astype(int)
    ari_surface_magnitude = ari(latent_lab, mag_bins)

    # control: p6's hand-normalized R-shape.  ratio_repr loops to its own
    # NC (=32, from p4_clean), so it reads exactly the slots p6 used.
    R = np.stack([ratio_repr(seqs[i], rows[i]["Al"], rows[i]["Bl"],
                             rows[i]["z"]) for i in range(n)])
    ari_invariant_control = ari(km_labels(R), s_arr)

    # PCA readout: do the first 2 latent components separate by s?
    pca = PCA(n_components=2, random_state=SEED)
    L2 = pca.fit_transform(latent)
    ari_pca2_vs_s = ari(km_labels(L2), s_arr)

    baseline_max = max(ari_input_baseline, ari_surface_magnitude)
    margin = ari_latent_vs_s - (baseline_max + 0.15)
    verdict = "SUPPORTED" if margin > 0 else "NOT-SUPPORTED"

    print("\n--- P9 clustering results ---")
    print(f"ARI latent vs s             : {ari_latent_vs_s:.3f}   <- main")
    print(f"ARI input-repr log|c|[:8]   : {ari_input_baseline:.3f}"
          "   <- surface baseline 1")
    print(f"ARI latent vs |c0| bins     : {ari_surface_magnitude:.3f}"
          "   <- surface baseline 2")
    print(f"ARI invariant control (R)   : {ari_invariant_control:.3f}"
          "   <- health check")
    print(f"ARI PCA-2 of latent vs s    : {ari_pca2_vs_s:.3f}")
    print(f"held-out MSE model {np.mean(mse_model):.4f} "
          f"vs persistence {np.mean(mse_persist):.4f}")
    print(f"\nverdict: {verdict} (latent {ari_latent_vs_s:.3f} vs "
          f"max baseline {baseline_max:.3f} + 0.15; margin {margin:+.3f})")

    print("\nlatent clusters:")
    for c in sorted(set(latent_lab.tolist())):
        mem = [f"{names[i]}(s={s_arr[i]})"
               for i in range(n) if latent_lab[i] == c]
        print(f"  cluster {c}: {', '.join(mem)}")

    print("\nPCA-2 coordinates by signature:")
    for s in (2, 3, 4, 6):
        pts = [f"{names[i]}:({L2[i, 0]:+.2f},{L2[i, 1]:+.2f})"
               for i in range(n) if s_arr[i] == s]
        print(f"  s={s}: {'  '.join(pts)}")

    out = {
        "prediction": "P9 (docs/RESEARCH_PLAN.md, registered 2026-09-26 "
                      "pre-run): next-coefficient prediction; latent/predictor "
                      "state clusters by signature s (ARI vs s > "
                      "surface-magnitude baseline + 0.15); falsifier: "
                      "clusters by surface magnitude or ties",
        "n_series": n,
        "series_note": "21 verified members exist; 20 reproducible from this "
                       "repo (17 literature + 3 mechanical d19/43/67; d=163 "
                       "has no pipeline encoding). Run uses the 20.",
        "s_counts": {str(s): int((s_arr == s).sum()) for s in (2, 3, 4, 6)},
        "config": {
            "NC": NC, "window": WINDOW, "hidden": HIDDEN, "epochs": EPOCHS,
            "lr": LR, "batch": BATCH, "seed": SEED, "k": N_CLUSTERS,
            "model": "MLP 8-32-32-1 tanh; latent = last hidden layer (32d), "
                     "mean over the held-out series' 55 windows",
            "target": "log-diffs d_k = log|c_{k+1}| - log|c_k|; 8-step "
                      "window -> next diff",
            "scaling": "global standardization of X and y from the 19 "
                       "training series of each LOSO fold (no leakage)",
            "logc": "log|c_k| in log space (k*log|z|+log(A+B*k)+log H_k); "
                    "raw float c_k underflows for small-|z| series at NC=64",
            "torch_version": torch.__version__,
            "sklearn_version": sklearn.__version__,
        },
        "ari_latent_vs_s": round(ari_latent_vs_s, 4),
        "ari_input_baseline": round(ari_input_baseline, 4),
        "ari_surface_magnitude": round(ari_surface_magnitude, 4),
        "ari_invariant_control": round(ari_invariant_control, 4),
        "ari_pca2_vs_s": round(ari_pca2_vs_s, 4),
        "pca_explained_variance_ratio":
            [round(float(v), 4) for v in pca.explained_variance_ratio_],
        "heldout_mse_model": round(float(np.mean(mse_model)), 6),
        "heldout_mse_persistence": round(float(np.mean(mse_persist)), 6),
        "verdict_rule": "SUPPORTED iff ari_latent_vs_s > max("
                        "ari_input_baseline, ari_surface_magnitude) + 0.15",
        "verdict_margin": round(float(margin), 4),
        "verdict": verdict,
        "per_series": [
            {"name": names[i], "s": int(s_arr[i]),
             "mech": bool(rows[i]["mech"]),
             "latent_cluster": int(latent_lab[i]),
             "log_abs_z": round(float(np.log(abs(rows[i]["z"]))), 3),
             "log_abs_c0": round(float(np.log(c0_abs[i])), 3),
             "mag_bin": int(mag_bins[i]),
             "pca2": [round(float(L2[i, 0]), 4), round(float(L2[i, 1]), 4)],
             "latent": [round(float(v), 4) for v in latent[i]]}
            for i in range(n)
        ],
    }
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "p9_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(f"\nresults -> {out_path}")


if __name__ == "__main__":
    main()
