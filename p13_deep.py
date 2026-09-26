"""P13 v2: deep invariant discovery -- composite transforms + k-WTA sparse
readout + longer two-stage training, addressing the user directive:
"跑久一点, 结合 flypoet/flymemory 的东西, 深层次机制可能更隐蔽".

NAMING CORRECTION (review): the "two-phase consolidation" below is
hard-example reweighting (train all -> continue on the worst-reconstructed
half), NOT FlyMemory-style memory->replay->consolidation.  It reweights the
LOSS, it does not store or replay anything.

SCOPE CORRECTION (review): this v2 script ran a SINGLE cell (b=8, seed=0)
per transform -- not a full grid.  The true b x seed grid on TRUE sequences
(p13_deep's own sequence builder had a wrong per-k H factor) is
p13_grid.py; its verdict supersedes the numbers here.

Upgrades over p13_discovery.py:
  1. COMPOSITE TRANSFORM STACKS (singles + pairs), not single transforms
  2. k-WTA sparse readout (FlyPoet MBON pattern): latent -> top-k winner
     mask, similarity = mask Jaccard (sign is nuisance, not identity)
  3. Two-stage hard-example reweighting (see naming correction), 30000 steps

Run:  python p13_deep.py            (single cell per transform)
      python p13_grid.py            (TRUE b x seed grid -- authoritative)
"""
import itertools
import json
import os
import sys

import numpy as np
import torch
import torch.nn as nn
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t0_scan import ari  # noqa: E402
from t0_scan import AE  # noqa: E402
from t1_modular import (eisenstein_vec, eta_poly_pow, heegner_set,  # noqa: E402
                        cm_j_digits)


# ---------------- transformation library (single + composites) -------------

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
    return np.diff(np.log(np.abs(vals)))


def t_norm(c):
    return c / (np.abs(c).max() + 1e-300)


def t_scale_removal(c):
    return (c - c.mean()) / (c.std() + 1e-300)


def t_detrend(c):
    k = np.arange(len(c))
    slope, intercept = np.polyfit(k, c, 1)
    return c - (slope * k + intercept)


def t_log_abs_zero_safe(c):
    return np.log(np.abs(c) + 1e-250)


def t_sqrt_sign(c):
    return np.sign(c) * np.sqrt(np.abs(c))


SINGLE = {
    "identity": t_identity,
    "first_diff": t_first_diff,
    "second_diff": t_second_diff,
    "log_abs_zf": lambda c: t_log_abs(c) if (
        lambda v: len(v) >= 4)(c[np.abs(c) != 0]) else None,
    "log_ratio_zf": lambda c: (
        np.diff(np.log(np.abs(c[c != 0]))))
    if len(c[c != 0]) >= 5 else None,
    "norm": t_norm,
    "scale_removal": t_scale_removal,
    "detrend": t_detrend,
    "sqrt_sign": t_sqrt_sign,
    # composites (stacks)
    "ratio_log": lambda c: t_log_abs(t_first_diff(c)),
    "detrend_ratio": lambda c: t_first_diff(t_detrend(c)),
    "detrend_logdiff": lambda c: t_log_ratio(t_detrend(c)),
    "norm_ratio_log": lambda c: t_log_ratio(t_norm(t_first_diff(c))),
    "scale_ratio_log": lambda c: t_log_ratio(t_scale_removal(c)),
    "detrend_second_diff": lambda c: t_second_diff(t_detrend(c)),
}


# ---------------- readouts ----------------

def readout_knn(z, labels, k=3):
    zn = z / (np.linalg.norm(z, axis=1, keepdims=True) + 1e-12)
    sim = zn @ zn.T
    np.fill_diagonal(sim, -np.inf)
    idx = np.argsort(-sim, axis=1)[:, :k]
    h1 = h3 = frac = 0
    for i, nb in enumerate(idx):
        same = (labels[nb] == labels[i]).astype(int)
        h1 += int(same[0])
        h3 += int(same.sum() >= 1)
        frac += same.mean()
    return {"hit1": h1, "hit3": h3, "frac3": round(float(frac) / len(idx), 3)}


def readout_kwta(z, labels, kwta_k=2, k=3):
    """FlyPoet MBON pattern: k-WTA sparse binarization of the latent, then
    similarity = winner-set overlap (Jaccard)."""
    zs = z / (np.linalg.norm(z, axis=1, keepdims=True) + 1e-12)
    W = torch.tensor(zs, dtype=torch.float32)
    topk = torch.topk(torch.abs(W), kwta_k, dim=1)
    mask = torch.zeros_like(W)
    mask.scatter_(1, topk.indices, 1.0)
    # True Jaccard on winner masks (sign is nuisance, not identity)
    inter = mask.numpy() @ mask.numpy().T
    union = mask.numpy().sum(1)[:, None] + mask.numpy().sum(1)[None, :]             - inter
    jac = inter / (union + 1e-12)
    np.fill_diagonal(jac, -np.inf)
    idx = np.argsort(-jac, axis=1)[:, :k]
    h1 = h3 = frac = 0
    for i, nb in enumerate(idx):
        same = (labels[nb] == labels[i]).astype(int)
        h1 += int(same[0])
        h3 += int(same.sum() >= 1)
        frac += same.mean()
    return {"hit1": h1, "hit3": h3, "frac3": round(float(frac) / len(idx), 3)}


def readout_all(z, labels):
    return {"knn": readout_knn(z, labels),
            "kwta2": readout_kwta(z, labels, kwta_k=2),
            "kwta4": readout_kwta(z, labels, kwta_k=4)}


# ---------------- two-phase consolidation training ----------------

def train_two_phase(x, b, seed, phase1=12000, phase2=18000):
    """Two-stage HARD-EXAMPLE REWEIGHTING (not memory consolidation): coarse
    full-batch pass, then continue training only on the worst-reconstructed
    half.  Reweights the loss; stores/replays nothing."""
    torch.manual_seed(seed)
    ae = AE(x.shape[1], b)
    opt = torch.optim.Adam(ae.parameters(), lr=2e-3)
    xt = torch.tensor(x, dtype=torch.float32)
    for step in range(phase1):
        rec, _ = ae(xt)
        loss = ((rec - xt) ** 2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    # consolidation: reweight the worst-reconstructed half for phase 2
    with torch.no_grad():
        rec_all, _ = ae(xt)
        err = ((rec_all - xt) ** 2).mean(dim=1)
    hard = torch.argsort(err, descending=True)[: max(1, len(xt) // 2)]
    for step in range(phase2):
        rec, _ = ae(xt[hard])
        loss = ((rec - xt[hard]) ** 2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    with torch.no_grad():
        _, z = ae(xt)
    return z.numpy()


# ---------------- main sweep ----------------

def main():
    from t1_modular import heegner_set
    from p4_clean import SERIES, hyper3

    NC = 24
    rows, s_arr, eq_arr, seqs = [], [], [], []
    for eq, s, Al, Bl, z, sign, c0 in SERIES:
        c = []
        for k in range(NC):
            if k == 0:
                H = 1.0
            else:
                from math import prod
                H = float(prod([k + j for j in (0.5, 1 / s, 1 - 1 / s)])
                          / (k ** 3))
            v = sign * (Al + Bl * k) * H * z ** k
            if k == 0 and c0 is not None:
                v += c0
            c.append(v)
        c = np.array(c, dtype=np.float64)
        seqs.append(c)
        s_arr = np.append(s_arr, s)
        eq_arr.append(eq)
        rows.append({"eq": eq, "s": s})
    seqs = np.stack(seqs)

    s_arr = np.array(s_arr)
    logz = np.log(np.abs([m["z"] for m in
                          [{"z": float(np.sign(c0 or 1) * (abs(c0 or 1) + 1e-300))}
                           for c0 in [None] * 0]] or [1.0])) if False else None

    # transformation library applied to all series
    names = list(SINGLE)
    reps_by_t = {}
    for name, fn in SINGLE.items():
        reps = []
        ok = True
        for c in seqs:
            try:
                r = fn(c)
                if r is None or len(r) < 8 or not np.all(np.isfinite(r)):
                    ok = False
                    break
                r = r / (np.linalg.norm(r) + 1e-12)
                reps.append(r.astype(np.float32))
            except Exception:
                ok = False
                break
        if ok:
            L = min(len(r) for r in reps)
            reps_by_t[name] = np.stack([r[:L] for r in reps])
    print(f"transforms usable: {list(reps_by_t)}", flush=True)

    # AE latents per transform (short training for each; the two-phase
    # consolidation AE runs once on the best-known transform family)
    t0 = time.time()
    latents = {}
    for name in reps_by_t:
        z = train_two_phase(reps_by_t[name], b=8, seed=0)
        latents[name] = z
    print(f"two-phase AE latents done ({time.time()-t0:.0f}s)", flush=True)

    # ---- sweep: transform x readout ----
    all_rows = []
    for name in reps_by_t:
        z = latents[name]
        for ro_name, ro in readout_all(z, s_arr).items():
            all_rows.append({"transform": name, "readout": ro_name, **ro})
        h1 = ro["hit1"]
        print(f"  {name:20s} {ro_name}: hit@1={h1}/17", flush=True)

    # aggregate best per transform
    best = {}
    for r in all_rows:
        key = r["transform"]
        if key not in best or r["hit1"] > best[key]["hit1"]:
            best[key] = r

    chance = float(np.mean([(s_arr == s_arr[i]).sum() - 1 for i in range(len(s_arr))])
                   / (len(s_arr) - 1))
    print(f"\n=== P13 v2: best per transform (chance hit@1 = {chance:.3f}) ===")
    for name in sorted(best, key=lambda n: -best[n]["hit1"]):
        b = best[name]
        print(f"  {name:22s} hit@1={b['hit1']:2d}/17 ({b['hit1']/17:.2f})")

    with open("p13_deep_results.json", "w", encoding="utf-8") as f:
        json.dump({"chance": chance, "rows": all_rows,
                   "best": {k: v["hit1"] for k, v in best.items()}},
                  f, indent=1, default=str)
    print("results -> p13_deep_results.json")


if __name__ == "__main__":
    import time
    main()
