"""P7 v0: notation forging -- do self-forged discrete primitives align with
arithmetic structure better than inherited notation?

(registered prediction P7, docs/RESEARCH_PLAN.md: forged alignment >
inherited alignment; falsification: reversal)

Setup: VQ-AE (encoder -> discrete codebook via straight-through estimator)
on the HARD Eisenstein config (12 weights x 3 noisy instances, 16-dim
coefficient vectors -- T1's eisenstein_hard). The code assignment of each
sample is its FORGED notation; the INHERITED notations are the raw
coefficient vector (k-means) and the text embedding.

Metrics:
  align  : ARI(code assignment, weight) vs ARI(KMeans(raw), weight) vs
           ARI(KMeans(embed), weight)
  transfer: encoder+codebook applied to ETA products (12 exponents) --
           does the forged code align with the exponent WITHOUT retraining?
           (the "private notation runs analogical search" claim)

Run:  python t7_notation.py
"""
import os
import sys

import numpy as np
import torch
import torch.nn as nn
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t0_scan import ari  # noqa: E402
from t1_modular import eisenstein_vec, eta_poly_pow, embed_texts  # noqa: E402


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
        zq = self.codes[idx]
        return zq, idx

    def forward(self, x):
        z_e = self.enc(x)
        z_q, idx = self.quantize(z_e)
        rec = self.dec(z_q + (z_e - z_q).detach())  # straight-through
        return rec, z_e, z_q, idx


def train_vq(x, epochs=4000, n_codes=12):
    torch.manual_seed(0)
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
        with torch.no_grad():  # EMA codebook + dead-code reinjection
            z_e_all = vq.enc(xt)
            z_q_all, idx = vq.quantize(z_e_all)
            used = np.unique(idx.numpy())
            for c in used:
                mask = idx == c
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

    print("training VQ-AE (12 codes) on hard Eisenstein...", flush=True)
    vq = train_vq(X, n_codes=12)
    with torch.no_grad():
        xt = torch.tensor(X, dtype=torch.float32)
        _, _, _, idx = vq(xt)
    forged_codes = idx.numpy()

    a_forged = ari(forged_codes, labels)
    km_raw = KMeans(n_clusters=12, n_init=20, random_state=0).fit(X)
    a_inherited_raw = ari(km_raw.labels_, labels)
    emb = embed_texts([f"coefficients: " + " ".join(f"{c:.3f}" for c in X[i][:16])
                       for i in range(len(X))])
    km_emb = KMeans(n_clusters=12, n_init=20, random_state=0).fit(emb)
    a_inherited_embed = ari(km_emb.labels_, labels)

    print("\n=== P7 v0: alignment with arithmetic structure (weight) ===")
    print(f"  forged codebook ARI   : {a_forged:+.3f}")
    print(f"  inherited raw ARI     : {a_inherited_raw:+.3f}")
    print(f"  inherited embed ARI   : {a_inherited_embed:+.3f}")

    # ---- transfer: forged codebook on ETA products (no retraining) ----
    exps = list(range(2, 26, 2))
    vecs_e = [eta_poly_pow(m, 16) for m in exps]
    Xt, labels_t = [], []
    for li, v in enumerate(vecs_e):
        for _ in range(10):
            noisy = v + rng.normal(0, 2e-2, len(v))
            Xt.append(noisy / (np.linalg.norm(noisy) + 1e-12))
            labels_t.append(li)
    Xt = np.stack(Xt).astype(np.float32)
    labels_t = np.array(labels_t)
    with torch.no_grad():
        _, _, _, idx_t = vq(torch.tensor(Xt, dtype=torch.float32))
    codes_t = idx_t.numpy()
    a_transfer = ari(codes_t, labels_t)
    km_t = KMeans(n_clusters=12, n_init=20, random_state=0).fit(Xt)
    a_transfer_inherited = ari(km_t.labels_, labels_t)
    print(f"\n=== transfer (Eisenstein-forged codes on eta products) ===")
    print(f"  forged codes vs exponent ARI   : {a_transfer:+.3f}")
    print(f"  inherited kmeans vs exponent   : {a_transfer_inherited:+.3f}")

    verdict = "P7 v0: forged > inherited" if a_forged > a_inherited_raw \
        else "P7 v0: forged <= inherited (falsified at this scale)"
    print(f"\n{verdict} | transfer {'HIT' if a_transfer > 0.3 else 'MISS'}")

    import json
    with open("t7_results.json", "w", encoding="utf-8") as f:
        json.dump({"forged_ari": a_forged,
                   "inherited_raw_ari": a_inherited_raw,
                   "inherited_embed_ari": a_inherited_embed,
                   "transfer_ari": a_transfer,
                   "transfer_inherited_ari": a_transfer_inherited}, f, indent=1)
    print("results -> t7_results.json")


if __name__ == "__main__":
    main()
