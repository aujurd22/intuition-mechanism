"""P7 multi-seed clean rerun (external-review action item).

Resolves the narrative inconsistency: the 0.693 (t7_notation) vs 0.802
(t7_revival lambda=0) numbers came from different init paths -- a seed/
init sensitivity that must be measured, not narrated. This script runs the
FIXED straight-through VQ across seeds x codebook sizes with a frozen
dataset and writes ONE result artifact.

For each (seed, codebook) cell: train VQ (lambda=0, pure reconstruction),
report ARI(code assignment, weight), plus the inherited baselines.

Run:  python t7_multiseed.py
"""
import json
import os
import sys

import numpy as np
import torch
import torch.nn as nn
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t0_scan import ari  # noqa: E402
from t1_modular import eisenstein_vec, embed_texts  # noqa: E402


class VQAE(nn.Module):
    def __init__(self, n_in=16, d_code=8, n_codes=12):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(n_in, 64), nn.GELU(),
                                 nn.Linear(64, d_code))
        self.dec = nn.Sequential(nn.Linear(d_code, 64), nn.GELU(),
                                 nn.Linear(64, n_in), nn.Sigmoid())
        self.register_buffer("codes", torch.randn(n_codes, d_code))

    def quantize(self, z):
        d = ((z.unsqueeze(1) - self.codes.unsqueeze(0)) ** 2).sum(-1)
        idx = d.argmin(1)
        return self.codes[idx], idx

    def forward(self, x):
        z_e = self.enc(x)
        z_q, idx = self.quantize(z_e)
        z_q_st = z_e + (z_q - z_e).detach()   # CORRECT straight-through
        rec = self.dec(z_q_st)
        return rec, z_e, z_q, idx


def train_vq(x, n_codes, seed, epochs=4000):
    torch.manual_seed(seed)
    vq = VQAE(x.shape[1], 8, n_codes)
    opt = torch.optim.Adam(vq.parameters(), lr=2e-3)
    xt = torch.tensor(x, dtype=torch.float32)
    ema = 0.95
    for step in range(epochs):
        rec, z_e, z_q, idx = vq(xt)
        loss = ((rec - xt) ** 2).mean() \
            + 0.05 * ((z_e - z_q.detach()) ** 2).mean() \
            + ((z_e.detach() - z_q) ** 2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
        with torch.no_grad():
            z_e_all = vq.enc(xt)
            z_q_all, idx_all = vq.quantize(z_e_all)
            used = np.unique(idx_all.numpy())
            for c in used:
                mask = idx_all == c
                vq.codes[c] = ema * vq.codes[c] \
                    + (1 - ema) * z_e_all[mask].mean(0)
            if step % 200 == 0 and len(used) < n_codes // 2:
                dead = [c for c in range(n_codes) if c not in used]
                for c in dead:
                    j = int(np.random.default_rng(step).integers(0, len(xt)))
                    vq.codes[c] = z_e_all[j]
    return vq


def main():
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
    emb = embed_texts([f"coefficients: "
                       + " ".join(f"{c:.3f}" for c in X[i][:16])
                       for i in range(len(X))])
    km_emb = KMeans(n_clusters=12, n_init=20, random_state=0).fit(emb)
    a_embed = ari(km_emb.labels_, labels)
    print(f"inherited raw KMeans ARI: {a_inherited:.3f} | "
          f"inherited embed ARI: {a_embed:.3f}\n", flush=True)

    grid = [(seed, n_codes) for seed in (0, 1, 2) for n_codes in (8, 12, 16, 24)]
    rows = []
    xt = torch.tensor(X, dtype=torch.float32)
    for seed, n_codes in grid:
        vq = train_vq(X, n_codes, seed)
        with torch.no_grad():
            _, _, _, idx = vq(xt)
        a = ari(idx.numpy(), labels)
        rows.append({"seed": seed, "n_codes": n_codes, "ARI": round(a, 3)})
        print(f"  seed={seed} codes={n_codes:2d}: ARI={a:+.3f}", flush=True)

    by_codes = {}
    for r in rows:
        by_codes.setdefault(r["n_codes"], []).append(r["ARI"])
    print("\n=== P7 multi-seed summary (ARI by codebook size) ===")
    for nc, vals in sorted(by_codes.items()):
        print(f"  codes={nc:2d}: mean={np.mean(vals):.3f} "
              f"std={np.std(vals):.3f}  vals={vals}")

    with open("t7_multiseed_results.json", "w", encoding="utf-8") as f:
        json.dump({"inherited_ari": a_inherited, "embed_ari": a_embed,
                   "rows": rows}, f, indent=1)
    print("results -> t7_multiseed_results.json")


if __name__ == "__main__":
    main()
