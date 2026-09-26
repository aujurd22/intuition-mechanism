"""P14: blind structural factorization under nuisance control.

Review-recommended route (2026-09-26): the previous P13 family tests used 17
literature series where s, A, B, z are naturally confounded. P14 makes the
nuisance variation EXPLICIT and counterfactual:

  for each signature s in {2,3,4,6}:  N samples with INDEPENDENT random
  (A, B, z) drawn from wide ranges. The ONLY thing constant within a class
  is s -- the invariant. Then three increasingly informed arms test WHERE
  discovery breaks:

  Arm 1  recon-only AE       : learn to reconstruct; is same-s structure
                               recoverable from the latent at all?
  Arm 2  DANN (GRL)          : explicit invariance pressure -- a gradient
                               reversal layer punishes nuisance-predictive
                               information (A,B,z) while a head predicts s.
                               THIS is the "machine discovers nuisance
                               removal" test.
  Arm 3  family-known        : given the correct functional family
                               {f_s}, pick s per sample by residual
                               minimization (hypothesis selection).
                               The "representation known, parameters not"
                               level.

Registered predictions (docs/RESEARCH_PLAN.md P14, pre-run):
  (a) recon-only AE same-s kNN <= 0.30  (nuisance-dominated, as in P9)
  (b) DANN same-s kNN >= 0.70           (invariance pressure works)
  (c) family-known selection >= 0.90 accuracy

Run:  python p14_factorization.py
"""
import json
import os
import sys
from math import prod

import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

NC = 24
SIGS = (2, 3, 4, 6)
N_PER_CLASS = 60


def poch3(k, s):
    """(1/2)_k (1/s)_k (1-1/s)_k / (k!)^3 -- exact Pochhammer product."""
    if k == 0:
        return 1.0
    return float(prod([k - 1 + j for j in (0.5, 1 / s, 1 - 1 / s)]) / (k ** 3))


def make_dataset(seed=0):
    """c_k = (A + B k) * H_s(k) * z^k with independent random A, B, z."""
    rng = np.random.default_rng(seed)
    X, y, nuis = [], [], []
    for si, s in enumerate(SIGS):
        Hs = np.array([poch3(k, s) for k in range(NC)])
        for _ in range(N_PER_CLASS):
            A = rng.uniform(0.5, 5.0)
            B = rng.uniform(0.0, 3.0)
            z = rng.uniform(0.05, 0.45)      # positive, same sign family
            k = np.arange(NC)
            c = (A + B * k) * Hs * z ** k
            c = c / (np.linalg.norm(c) + 1e-300)
            X.append(c)
            y.append(si)
            nuis.append([A, B, z])
    return (np.stack(X).astype(np.float32), np.array(y),
            np.array(nuis, dtype=np.float32))


class AE(nn.Module):
    def __init__(self, n_in, b=8):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(n_in, 64), nn.GELU(),
                                 nn.Linear(64, b))
        self.dec = nn.Sequential(nn.Linear(b, 64), nn.GELU(),
                                 nn.Linear(64, n_in))

    def forward(self, x):
        z = self.enc(x)
        return self.dec(z), z


class GRL(torch.autograd.Function):
    """Gradient reversal layer."""

    @staticmethod
    def forward(ctx, x, lam):
        ctx.lam = lam
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad):
        return -ctx.lam * grad, None


class DANN(nn.Module):
    def __init__(self, n_in, b=8):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(n_in, 64), nn.GELU(),
                                 nn.Linear(64, b))
        self.dec = nn.Sequential(nn.Linear(b, 64), nn.GELU(),
                                 nn.Linear(64, n_in))
        self.s_head = nn.Linear(b, len(SIGS))       # signature classifier
        self.n_head = nn.Linear(b, 3)               # nuisance (A,B,z) regression

    def forward(self, x, lam=1.0):
        z = self.enc(x)
        rec = self.dec(z)
        s_logits = self.s_head(z)
        n_pred = self.n_head(GRL.apply(z, lam))
        return rec, z, s_logits, n_pred


def knn_same_s(z, y, k=3):
    zn = z / (np.linalg.norm(z, axis=1, keepdims=True) + 1e-12)
    sim = zn @ zn.T
    np.fill_diagonal(sim, -np.inf)
    idx = np.argsort(-sim, axis=1)[:, :k]
    frac = []
    for i, nb in enumerate(idx):
        frac.append(float((y[nb] == y[i]).mean()))
    return float(np.mean(frac))


def arm1_recon(X, y, steps=6000, seed=0):
    torch.manual_seed(seed)
    ae = AE(X.shape[1])
    opt = torch.optim.Adam(ae.parameters(), lr=2e-3)
    xt = torch.tensor(X)
    for _ in range(steps):
        rec, _ = ae(xt)
        loss = ((rec - xt) ** 2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    with torch.no_grad():
        _, z = ae(xt)
    return z.numpy()


def arm2_dann(X, y, nuis, steps=6000, seed=0, lam=1.0):
    torch.manual_seed(seed)
    m = DANN(X.shape[1])
    opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    xt, yt = torch.tensor(X), torch.tensor(y, dtype=torch.long)
    nt = torch.tensor(nuis)
    # normalize nuisance targets for stable regression
    nt = (nt - nt.mean(0)) / (nt.std(0) + 1e-6)
    for _ in range(steps):
        rec, _, s_logits, n_pred = m(xt, lam=lam)
        loss = ((rec - xt) ** 2).mean() \
            + 1.0 * nn.functional.cross_entropy(s_logits, yt) \
            + 1.0 * ((n_pred - nt) ** 2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    with torch.no_grad():
        _, z, s_logits, _ = m(xt)
    acc = float((s_logits.argmax(1) == yt).float().mean())
    return z.numpy(), acc


def arm3_family_known(X, y, z_grid=None):
    """Hypothesis selection with PROPER parameter fitting: for each candidate
    signature s, grid-search z and solve (A, B) by least squares on the two
    basis vectors [H_s(k) z^k, k H_s(k) z^k]; pick the s with the lowest
    residual. This is the 'family known, parameters unknown' level."""
    k = np.arange(NC)
    if z_grid is None:
        z_grid = np.linspace(0.02, 0.6, 60)
    correct = 0
    for i in range(len(X)):
        c = X[i]
        best_s, best_res = None, np.inf
        for si, s in enumerate(SIGS):
            Hs = np.array([poch3(kk, s) for kk in k])
            for z in z_grid:
                v1 = Hs * z ** k
                v2 = k * Hs * z ** k
                M = np.stack([v1, v2], axis=1)
                try:
                    ab, res, *_ = np.linalg.lstsq(M, c, rcond=None)
                    r = float(np.linalg.norm(M @ ab - c))
                except Exception:
                    continue
                if r < best_res:
                    best_res, best_s = r, si
        correct += int(best_s == y[i])
    return correct / len(X)


def main():
    X, y, nuis = make_dataset(seed=0)
    print(f"dataset: {len(X)} samples ({len(SIGS)} signatures x "
          f"{N_PER_CLASS}), NC={NC}")
    print(f"  nuisance ranges: A~U(0.5,5), B~U(0,3), z~U(0.05,0.45)\n")

    # Arm 1: recon-only
    z1 = arm1_recon(X, y)
    a1 = knn_same_s(z1, y)
    print(f"Arm 1 recon-only AE    : same-s kNN@3 = {a1:.3f}  "
          f"(registered <= 0.30)")

    # Arm 2: DANN
    z2, s_acc = arm2_dann(X, y, nuis)
    a2 = knn_same_s(z2, y)
    print(f"Arm 2 DANN (GRL)       : same-s kNN@3 = {a2:.3f}  "
          f"| s-classifier acc = {s_acc:.3f}  (registered >= 0.70)")

    # Arm 3: family-known
    a3 = arm3_family_known(X, y)
    print(f"Arm 3 family-known     : selection acc = {a3:.3f}  "
          f"(registered >= 0.90)")

    print("\n=== P14 reading ===")
    print(f"  (a) recon-only <= 0.30 : {a1:.3f} -> "
          f"{'CONFIRMED' if a1 <= 0.30 else 'not supported'}")
    print(f"  (b) DANN >= 0.70       : {a2:.3f} -> "
          f"{'CONFIRMED' if a2 >= 0.70 else 'NOT SUPPORTED'}")
    print(f"  (c) family >= 0.90     : {a3:.3f} -> "
          f"{'CONFIRMED' if a3 >= 0.90 else 'not supported'}")

    with open("p14_results.json", "w", encoding="utf-8") as f:
        json.dump({"n": len(X), "n_per_class": N_PER_CLASS,
                   "arm1_recon_knn": a1,
                   "arm2_dann_knn": a2, "arm2_s_acc": s_acc,
                   "arm3_family_acc": a3}, f, indent=1)
    print("results -> p14_results.json")


if __name__ == "__main__":
    main()
