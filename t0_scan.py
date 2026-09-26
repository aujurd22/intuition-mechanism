"""T0 scan: compression-rate sweep over graph families -> SD / ARI curves.

Intuition-Mechanism Program registered predictions P1/P2 (docs/
RESEARCH_PLAN.md): P1 -- a compression-ratio window [c1,c2] exists where
structure-domination SD beats surface-domination by >15pp, collapsing
non-monotonically at both ends; P2 -- within-window latent clustering ARI
(vs structure labels) beats surface ARI by >0.1.

Model: tiny MLP autoencoder on flattened adjacency (144-d in), bottleneck b
(compression c = 144/b). SD: for held-out anchors, fraction of kNN that are
same-family-different-instance. Surface-domination: fraction that are the
SAME instance (same decoration, different relabeling).

Run:
  python t0_scan.py --dataset t0_dataset.npz --bottlenecks 1,4,8,32,144
"""
import argparse
import json
import time

import numpy as np
import torch
import torch.nn as nn
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score


def ari(a, b):
    return float(adjusted_rand_score(a, b))


class AE(nn.Module):
    def __init__(self, n_in, b):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(n_in, 256), nn.GELU(),
                                 nn.Linear(256, 256), nn.GELU(),
                                 nn.Linear(256, b))
        self.dec = nn.Sequential(nn.Linear(b, 256), nn.GELU(),
                                 nn.Linear(256, 256), nn.GELU(),
                                 nn.Linear(256, n_in), nn.Sigmoid())

    def forward(self, x):
        z = self.enc(x)
        return self.dec(z), z


def train_ae(x, b, steps=3000, seed=0):
    torch.manual_seed(seed)
    ae = AE(x.shape[1], b)
    opt = torch.optim.Adam(ae.parameters(), lr=2e-3)
    xt = torch.tensor(x, dtype=torch.float32)
    for step in range(steps):
        rec, _ = ae(xt)
        loss = ((rec - xt) ** 2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    with torch.no_grad():
        _, z = ae(xt)
    return z.numpy(), float(loss)


def sd_metrics(z, family, instance, k=10):
    """Structure-domination vs surface-domination over kNN of every anchor."""
    zn = z / (np.linalg.norm(z, axis=1, keepdims=True) + 1e-9)
    sim = zn @ zn.T
    np.fill_diagonal(sim, -np.inf)
    nn_idx = np.argsort(-sim, axis=1)[:, :k]
    sd, surf = [], []
    for i, nb in enumerate(nn_idx):
        same_fam = family[nb] == family[i]
        same_inst = instance[nb] == instance[i]
        sd.append(float((same_fam & ~same_inst).mean()))
        surf.append(float(same_inst.mean()))
    return float(np.mean(sd)), float(np.mean(surf))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="t0_dataset.npz")
    ap.add_argument("--bottlenecks", default="1,2,4,8,16,32,64,144")
    ap.add_argument("--knn", type=int, default=10)
    ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--out", default="t0_scan_results.json")
    args = ap.parse_args()

    data = np.load(args.dataset, allow_pickle=True)
    x = (data["adj"] if "adj" in data else data["x"]).astype(np.float32)
    x = x.reshape(len(x), -1)
    family = data["family"]
    instance = data["instance"]
    meta = json.loads(str(data["meta"]))
    fam_names = meta.get("families") or meta.get("templates")
    print(f"dataset: {x.shape[0]} samples, families={fam_names}, "
          f"noise={meta.get('noise', 'n/a')}", flush=True)

    results = []
    for b in [int(v) for v in args.bottlenecks.split(",")]:
        t0 = time.time()
        z, loss = train_ae(x, b, steps=args.steps)
        sd, surf = sd_metrics(z, family, instance, k=args.knn)
        km = KMeans(n_clusters=len(fam_names), n_init=10,
                    random_state=0).fit(z)
        ari_struct = ari(km.labels_, family)
        # surface ARI only meaningful when instances span clusters; instance
        # count >> clusters makes kmeans-vs-instance ARI trivially low, so we
        # compare structure ARI against a surface-feature ARI (edge count)
        edges = x.sum(1) / 2
        eb = np.digitize(edges, np.quantile(edges, np.linspace(0, 1, 7)[1:-1]))
        ari_surface = ari(km.labels_, eb)
        c = round(x.shape[1] / b, 1)
        results.append({"b": b, "compression": c, "recon_loss": round(loss, 5),
                        "SD": round(sd, 3), "surface_dom": round(surf, 3),
                        "ARI_struct": round(ari_struct, 3),
                        "ARI_surface": round(ari_surface, 3)})
        print(f"  b={b:4d} c={c:6.1f} loss={loss:.5f} SD={sd:.3f} "
              f"surf={surf:.3f} ARI_s={ari_struct:.3f} ARI_f={ari_surface:.3f} "
              f"({time.time()-t0:.0f}s)", flush=True)

    print("\n=== P1 window reading (SD - surface_dom > 15pp ?) ===")
    for r in results:
        gap = (r["SD"] - r["surface_dom"]) * 100
        print(f"  c={r['compression']:6.1f}  gap={gap:+6.1f}pp  "
              f"{'IN WINDOW' if gap > 15 else 'outside'}")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "results": results}, f, indent=1)
    print(f"results -> {args.out}")


if __name__ == "__main__":
    main()
