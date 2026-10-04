"""P15: blind envelope removal (review-route, pre-registered in
docs/RESEARCH_PLAN.md).

The review located P13's failure precisely: the missing operation is
"estimate the envelope, cancel it, read the residual" -- a DATA-DEPENDENT
transform that no fixed menu contains.  P15 tests exactly that step with
no s labels and no H_s knowledge:

  data   : c_k = (A + Bk) * H_s(k) * z^k, H_s the TRUE CUMULATIVE
           hypergeometric; A,B,z independent random per sample
           (same ranges as P14).  NOTE: p14's own poch3 is the per-k
           RATIO R_k, not H_k -- same bug class as p13_deep; P15
           generates cumulative H and reports both families.
  blind  : per sample, fit log|c| ~ a0 + a1*k + a2*log(k+1) by OLS
           (generic exponential+linear+power-law envelope) and take
           u = |c| / exp(fit).  Nothing else.
  oracle : u = |c| / ((A+Bk) z^k) with TRUE A,B,z (H_s untouched --
           the invariant carrier stays in the residual).
  arms   : raw / blind / blind+AE / oracle / shuffled control.

Registered thresholds: blind hit@1 >= 0.70 and ARI >= 0.6 => CONFIRMED;
0.45-0.70 => PARTIAL; <= 0.45 => NEGATIVE.  Health: oracle >= 0.95.

Run:  python p15_envelope.py
"""
import json
import os
import sys
from math import prod

import numpy as np
import torch
import torch.nn as nn
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t0_scan import ari  # noqa: E402

NC = 24
SIGS = (2, 3, 4, 6)
N_PER_CLASS = 60


def poch_cum(k, s):
    """TRUE cumulative H_k = (1/2)_k (1/s)_k (1-1/s)_k / (k!)^3."""
    if k == 0:
        return 1.0
    num = 1.0
    for j in range(k):
        num *= (j + 0.5) * (j + 1 / s) * (j + 1 - 1 / s)
        num /= (j + 1) ** 3
    return num


def poch_ratio(k, s):
    """p14's per-k ratio form (for the transfer-family arm)."""
    if k == 0:
        return 1.0
    return float(prod([k - 1 + j for j in (0.5, 1 / s, 1 - 1 / s)])
                 / (k ** 3))


def make_dataset(poch, seed=0):
    rng = np.random.default_rng(seed)
    X, y, nuis = [], [], []
    for si, s in enumerate(SIGS):
        Hs = np.array([poch(k, s) for k in range(NC)])
        for _ in range(N_PER_CLASS):
            A = rng.uniform(0.5, 5.0)
            B = rng.uniform(0.0, 3.0)
            z = rng.uniform(0.05, 0.45)
            k = np.arange(NC)
            c = (A + B * k) * Hs * z ** k
            c = c / (np.linalg.norm(c) + 1e-300)
            X.append(c)
            y.append(si)
            nuis.append([A, B, z])
    return (np.stack(X).astype(np.float32), np.array(y),
            np.array(nuis, dtype=np.float32))


def knn_metrics(rep, s_arr, k=3):
    zn = rep / (np.linalg.norm(rep, axis=1, keepdims=True) + 1e-12)
    sim = zn @ zn.T
    np.fill_diagonal(sim, -np.inf)
    idx = np.argsort(-sim, axis=1)[:, :k]
    h1 = h3 = frac = 0
    per_sig = {}
    for i, nb in enumerate(idx):
        same = (s_arr[nb] == s_arr[i]).astype(int)
        h1 += int(same[0])
        h3 += int(same.sum() >= 1)
        frac += same.mean()
        per_sig.setdefault(s_arr[i], []).append(same.mean())
    macro = float(np.mean([np.mean(v) for v in per_sig.values()]))
    return {"hit1": round(h1 / len(idx), 3),
            "hit3": round(h3 / len(idx), 3),
            "frac3": round(frac / len(idx), 3),
            "macro": round(macro, 3)}


class AE(nn.Module):
    def __init__(self, dim, b=8):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(dim, 64), nn.GELU(),
                                 nn.Linear(64, b))
        self.dec = nn.Sequential(nn.Linear(b, 64), nn.GELU(),
                                 nn.Linear(64, dim))

    def forward(self, x):
        z = self.enc(x)
        return self.dec(z), z


def ae_latent(X, b=8, steps=4000, seed=0):
    torch.manual_seed(seed)
    m = AE(X.shape[1], b)
    opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    xt = torch.tensor(X, dtype=torch.float32)
    for _ in range(steps):
        rec, _ = m(xt)
        loss = ((rec - xt) ** 2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    with torch.no_grad():
        _, z = m(xt)
    return z.numpy()


def blind_envelope(c):
    """Generic 3-parameter log-domain envelope (per sample, no H_s/s)."""
    k = np.arange(len(c), dtype=float)
    lc = np.log(np.abs(c) + 1e-300)
    M = np.stack([np.ones_like(k), k, np.log(k + 1)], axis=1)
    coef, *_ = np.linalg.lstsq(M, lc, rcond=None)
    env = np.exp(M @ coef)
    return np.abs(c) / (env + 1e-300)


def main():
    for fam_name, poch in (("cumulative-TRUE", poch_cum),
                           ("ratio-form(p14)", poch_ratio)):
        X, y, nuis = make_dataset(poch, seed=0)
        chance = float(np.mean([(y == y[i]).sum() - 1
                                for i in range(len(y))]) / (len(y) - 1))
        print(f"\n=== family: {fam_name} (n={len(X)}, NC={NC}, "
              f"chance hit@1={chance:.3f}) ===", flush=True)

        A, B, z = nuis[:, 0], nuis[:, 1], nuis[:, 2]
        k = np.arange(NC, dtype=float)

        # representations
        reps = {}
        reps["raw"] = X
        reps["blind"] = np.stack([blind_envelope(c) for c in X])
        env = (A[:, None] + B[:, None] * k[None, :]) * z[:, None] ** k[None, :]
        reps["oracle"] = np.abs(X) / env
        reps["blind_AE"] = ae_latent(reps["blind"])

        rows = {}
        for name, R in reps.items():
            rows[name] = knn_metrics(R.astype(np.float64), y)
            # kmeans on row-normalized reps (same caliber as the kNN readout;
            # unnormalized kmeans clusters by residual SCALE, an artifact:
            # oracle residuals are H_s/||c|| with wide per-sample scale)
            Rn = R / (np.linalg.norm(R, axis=1, keepdims=True) + 1e-12)
            km = KMeans(n_clusters=len(SIGS), n_init=10,
                        random_state=0).fit(Rn)
            rows[name]["ari"] = round(ari(km.labels_, y), 3)
            print(f"  {name:9s} hit@1={rows[name]['hit1']:.3f} "
                  f"hit@3={rows[name]['hit3']:.3f} "
                  f"frac3={rows[name]['frac3']:.3f} "
                  f"ARI={rows[name]['ari']:.3f}", flush=True)

        # shuffled control on the blind arm
        rng = np.random.default_rng(1)
        ys = rng.permutation(y)
        sh = knn_metrics(reps["blind"].astype(np.float64), ys)
        print(f"  shuffled blind hit@1={sh['hit1']:.3f} (control)")

        verdict = ("CONFIRMED" if rows["blind"]["hit1"] >= 0.70
                   and rows["blind"]["ari"] >= 0.6
                   else "PARTIAL" if rows["blind"]["hit1"] > 0.45
                   else "NEGATIVE")
        print(f"  P15 verdict ({fam_name}): {verdict}")
        results.append({
            "family": fam_name, "chance": chance, "rows": rows,
            "shuffled_hit1": sh["hit1"], "verdict": verdict,
        })

    verdict0 = results[0]["verdict"]
    print(f"\nP15 final verdict (true family): {verdict0}")
    with open("p15_envelope_results.json", "w", encoding="utf-8") as f:
        json.dump({"results": results}, f, indent=1, default=str)
    print("results -> p15_envelope_results.json")


results = []

if __name__ == "__main__":
    main()
