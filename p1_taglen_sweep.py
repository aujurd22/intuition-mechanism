"""P1 (registry direction 4): surface-salience tag_len sweep.

Question: when a random surface tag is attached to each instance, does the
discovered latent keep tracking the algebraic family (invariant) or drift
to the salient-but-uninformative tag?  Probe: each instance's 3 relabels
share one tag, so tag capture inflates same-INSTANCE kNN recall while
pure invariance keeps instance recall at chance (1/59 ~ 2%).

Run: python p1_taglen_sweep.py
"""
import os
import sys

import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

torch.set_num_threads(4)
torch.manual_seed(0)


class AE(nn.Module):
    def __init__(self, dim, lat=32):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(dim, 256), nn.ReLU(),
                                 nn.Linear(256, lat))
        self.dec = nn.Sequential(nn.Linear(lat, 256), nn.ReLU(),
                                 nn.Linear(256, dim))

    def forward(self, x):
        z = self.enc(x)
        return z, self.dec(z)


def train_latents(X, epochs=60):
    x = torch.tensor(X, dtype=torch.float32)
    ae = AE(x.shape[1])
    opt = torch.optim.Adam(ae.parameters(), lr=1e-3)
    for _ in range(epochs):
        opt.zero_grad()
        z, xr = ae(x)
        loss = ((xr - x) ** 2).mean()
        loss.backward()
        opt.step()
    with torch.no_grad():
        z, xr = ae(x)
        return z.numpy(), float(((xr - x) ** 2).mean())


def knn_recall(Z, groups, k=5):
    zn = Z / (np.linalg.norm(Z, axis=1, keepdims=True) + 1e-9)
    sim = zn @ zn.T
    np.fill_diagonal(sim, -np.inf)
    idx = np.argsort(-sim, axis=1)[:, :k]
    return float(np.mean([(groups[nb] == groups[i]).mean()
                          for i, nb in enumerate(idx)]))


def main():
    print(f"{'tag_len':>7} {'fam_knn@5':>10} {'inst_knn@5':>11} "
          f"{'recon_mse':>10}")
    for tl in (0, 16, 32, 64):
        d = np.load(f"t0_algebra_tag{tl}.npz")
        X, fam, inst = d["x"], d["family"], d["instance"]
        Z, mse = train_latents(X)
        f_r = knn_recall(Z, fam)
        i_r = knn_recall(Z, inst)
        print(f"{tl:>7} {f_r:>10.3f} {i_r:>11.3f} {mse:>10.4f}", flush=True)
    n_inst = 60
    print(f"\nchance inst_knn ~ {1/(n_inst-1):.3f}; "
          "rising inst_knn with tag_len = salience capture; "
          "flat ~chance = tag ignored (invariant kept).")


if __name__ == "__main__":
    main()
