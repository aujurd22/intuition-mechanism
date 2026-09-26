"""P7 revival: does TASK LOSS make self-forged notation retain the
arithmetic invariant? (P7 falsification said pure reconstruction does not.)

Setup: VQ-AE on the hard Eisenstein config (12 weights x 10 instances,
16-dim), with a linear classification head on the quantized codes
predicting the weight. Task-loss weight lambda in {0, 0.1, 1, 10}:
  lambda = 0  : replicates the P7 falsification (reconstruction only)
  lambda > 0  : revival test -- task pressure forces the codes to retain
                the weight invariant
Metrics: ARI(code assignment, weight) vs the INHERITED baseline
(KMeans on raw vectors = 0.674 from t7 v2); reconstruction loss; transfer
to eta products (ARI vs exponent, no labels at transfer).

Run:  python t7_revival.py
"""
import os
import sys

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t0_scan import ari  # noqa: E402
from t1_modular import eisenstein_vec, eta_poly_pow, embed_texts  # noqa: E402


class VQAEHead(nn.Module):
    def __init__(self, n_in=16, d_code=8, n_codes=12, n_classes=12):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(n_in, 64), nn.GELU(),
                                 nn.Linear(64, d_code))
        self.dec = nn.Sequential(nn.Linear(d_code, 64), nn.GELU(),
                                 nn.Linear(64, n_in), nn.Sigmoid())
        self.head = nn.Linear(d_code, n_classes)
        self.register_buffer("codes", torch.randn(n_codes, d_code))

    def quantize(self, z):
        d = ((z.unsqueeze(1) - self.codes.unsqueeze(0)) ** 2).sum(-1)
        idx = d.argmin(1)
        return self.codes[idx], idx

    def forward(self, x):
        z_e = self.enc(x)
        z_q, idx = self.quantize(z_e)
        # standard straight-through: VALUE is z_q (quantized), GRADIENT flows
        # to z_e. The inverted version (z_q + (z_e - z_q).detach()) gave the
        # encoder values but routed gradients into the (buffer) codes -- the
        # encoder never received task/recon gradients through the quantizer
        # (found via the revival null result, 2026-09-26).
        z_q_st = z_e + (z_q - z_e).detach()
        rec = self.dec(z_q_st)
        logits = self.head(z_q_st)
        return rec, z_e, z_q, idx, logits


def train_vq_task(x, labels, lam, epochs=4000, n_codes=12):
    torch.manual_seed(0)
    vq = VQAEHead(x.shape[1], 8, n_codes, len(set(labels)))
    opt = torch.optim.Adam(vq.parameters(), lr=2e-3)
    xt = torch.tensor(x, dtype=torch.float32)
    yt = torch.tensor(labels, dtype=torch.long)
    ema = 0.95
    for step in range(epochs):
        rec, z_e, z_q, idx, logits = vq(xt)
        loss_r = ((rec - xt) ** 2).mean()
        loss_vq = ((z_e - z_q.detach()) ** 2).mean() \
            + ((z_e.detach() - z_q) ** 2).mean()
        loss_task = F.cross_entropy(logits, yt)
        loss = loss_r + 0.05 * loss_vq + lam * loss_task
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

    # inherited baseline (fixed from t7 v2)
    km_raw = KMeans(n_clusters=12, n_init=20, random_state=0).fit(X)
    a_inherited = ari(km_raw.labels_, labels)
    print(f"inherited raw KMeans ARI (baseline): {a_inherited:.3f}\n")

    rows = []
    for lam in (0.0, 0.1, 1.0, 10.0):
        vq = train_vq_task(X, labels, lam)
        with torch.no_grad():
            xt = torch.tensor(X, dtype=torch.float32)
            rec, _, _, idx, logits = vq(xt)
        recon = float(((rec - xt) ** 2).mean())
        acc = float((logits.argmax(1) == yt).float().mean()) \
            if (yt := torch.tensor(labels)) is not None else 0.0
        a_code = ari(idx.numpy(), labels)
        rows.append((lam, a_code, recon, acc))
        print(f"  lambda={lam:5.1f}  ARI(codes,weight)={a_code:+.3f}  "
              f"recon={recon:.5f}  task_acc={acc:.3f}", flush=True)

    # ---- transfer: best lambda model applied to eta products ----
    best_lam = max(rows, key=lambda r: r[1])[0]
    exps = list(range(2, 26, 2))
    vecs_e = [eta_poly_pow(m, 16) for m in exps]
    Xt, labels_t = [], []
    for li, v in enumerate(vecs_e):
        for _ in range(3):
            noisy = v + rng.normal(0, 2e-2, len(v))
            Xt.append(noisy / (np.linalg.norm(noisy) + 1e-12))
            labels_t.append(li)
    Xt = np.stack(Xt).astype(np.float32)
    labels_t = np.array(labels_t)
    vq = train_vq_task(X, labels, best_lam)
    with torch.no_grad():
        _, _, _, idx_t, _ = vq(torch.tensor(Xt, dtype=torch.float32))
    a_transfer = ari(idx_t.numpy(), labels_t)
    km_t = KMeans(n_clusters=12, n_init=20, random_state=0).fit(Xt)
    a_transfer_inh = ari(km_t.labels_, labels_t)
    print(f"\n=== transfer (best lambda={best_lam}) on eta products ===")
    print(f"  forged codes vs exponent ARI : {a_transfer:+.3f}")
    print(f"  inherited KMeans ARI         : {a_transfer_inh:+.3f}")

    print("\n=== P7 revival reading ===")
    print(f"  inherited baseline: {a_inherited:.3f}")
    for lam, a_code, recon, acc in rows:
        tag = "REVIVED" if a_code > a_inherited else "below inherited"
        print(f"  lambda={lam:5.1f}: ARI={a_code:+.3f} [{tag}]  recon={recon:.5f}")

    import json
    with open("t7_revival_results.json", "w", encoding="utf-8") as f:
        json.dump({"inherited_ari": a_inherited,
                   "rows": [{"lam": l, "ari": a, "recon": r, "acc": c}
                            for l, a, r, c in rows],
                   "transfer_ari": a_transfer}, f, indent=1)
    print("results -> t7_revival_results.json")


if __name__ == "__main__":
    main()
