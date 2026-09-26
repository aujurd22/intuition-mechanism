"""T0 dataset: synthetic graph families with structural vs surface labels.

Intuition-Mechanism Program, T0 (research plan Phase 0 item 3). For each of
K families, generate M decorated instances x R random relabelings. The
STRUCTURE label is the family; the SURFACE label is the instance (decoration
pattern). SD (structure domination) asks whether latent neighbours of an
anchor are same-family-different-instance.

Output: t0_dataset.npz with adjacency (N, n, n) float32 + family + instance
+ relabeling ids + meta json.

Run:  python t0_graphs.py [--families 6] [--instances 20] [--relabels 3]
                          [--noise 0.0] [--seed 0]
"""
import argparse
import json
import os

import numpy as np


def adj_cycle(n):
    a = np.zeros((n, n), dtype=np.float32)
    for i in range(n):
        a[i, (i + 1) % n] = a[(i + 1) % n, i] = 1
    return a


def adj_path(n):
    a = np.zeros((n, n), dtype=np.float32)
    for i in range(n - 1):
        a[i, i + 1] = a[i + 1, i] = 1
    return a


def adj_star(n):
    a = np.zeros((n, n), dtype=np.float32)
    a[0, 1:] = a[1:, 0] = 1
    return a


def adj_bipartite(n):
    k = n // 2
    a = np.zeros((n, n), dtype=np.float32)
    a[:k, k:] = a[k:, :k] = 1
    return a


def adj_grid(r, c):
    n = r * c
    a = np.zeros((n, n), dtype=np.float32)
    for i in range(r):
        for j in range(c):
            u = i * c + j
            if j + 1 < c:
                a[u, u + 1] = a[u + 1, u] = 1
            if i + 1 < r:
                a[u, u + c] = a[u + c, u] = 1
    return a


def adj_double_cycle(n):
    """Two n/2 cycles joined by a bridge edge."""
    h = n // 2
    a = adj_cycle(h)
    b = adj_cycle(n - h)
    a = np.block([[a, np.zeros((h, n - h), dtype=np.float32)],
                  [np.zeros((n - h, h), dtype=np.float32), b]])
    a[0, h] = a[h, 0] = 1  # bridge
    return a


FAMILIES = {
    "cycle": adj_cycle,
    "path": adj_path,
    "star": adj_star,
    "bipartite": adj_bipartite,
    "grid": lambda n: adj_grid(3, n // 3),
    "double_cycle": adj_double_cycle,
}


def decorate(a, rng, rate):
    """Random surface decoration: rewire `rate` fraction of edge slots."""
    n = a.shape[0]
    out = a.copy()
    m = int(n * (n - 1) / 2)
    n_flip = max(1, int(round(rate * m)))
    for _ in range(n_flip):
        i, j = rng.integers(0, n, 2)
        if i == j:
            continue
        out[i, j] = out[j, i] = 1 - out[i, j]
    np.fill_diagonal(out, 0)
    return out


def relabel(a, rng):
    perm = rng.permutation(a.shape[0])
    return a[np.ix_(perm, perm)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", type=int, default=6)
    ap.add_argument("--instances", type=int, default=20)
    ap.add_argument("--relabels", type=int, default=3)
    ap.add_argument("--noise", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="t0_dataset.npz")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    names = list(FAMILIES)[: args.families]
    n = 12
    adjs, fam, inst, rel = [], [], [], []
    for fi, name in enumerate(names):
        base = FAMILIES[name](n)
        for inst_id in range(args.instances):
            dec = decorate(base, rng, args.noise) if args.noise > 0 else base
            for r in range(args.relabels):
                adjs.append(relabel(dec, rng))
                fam.append(fi)
                inst.append(inst_id)
                rel.append(r)
    adjs = np.stack(adjs).astype(np.float32)
    fam = np.array(fam, dtype=np.int32)
    inst = np.array(inst, dtype=np.int32)
    rel = np.array(rel, dtype=np.int32)
    meta = {"families": names, "n": n, "instances": args.instances,
            "relabels": args.relabels, "noise": args.noise, "seed": args.seed}
    np.savez(args.out, adj=adjs, family=fam, instance=inst, relabel=rel,
             meta=json.dumps(meta))
    print(f"dataset: {adjs.shape[0]} samples, {len(names)} families, "
          f"noise={args.noise} -> {args.out}")


if __name__ == "__main__":
    main()
