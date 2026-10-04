"""P47 + P46-c-b joint runner.

P47: synthetic phase-boundary sweep.  4 classes with orthonormal signal
directions u_i; sample = Delta*u_i + sigma*eps.  Delta/sigma swept.
Both memory arms (STR = normalized running centroid, cosine NN;
EPI-ALL = unbounded cosine NN over all seen), forced classification,
8-era stream with absence arcs (identical era script to P46).

P46-c-b: re-run the P46-c STR arm on the ENVELOPE family with
NORMALIZED centroids + cosine NN (the metric that carries the
direction signal), vs the same EPI arms -- testing whether the P46-c
failure was metric wiring.
"""
import json
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p15_envelope import make_dataset, poch_cum, blind_envelope  # noqa: E402

K = 24
ERAS = [
    (1, [0, 2]), (2, [1, 3]), (3, [0, 1]), (4, [2, 3]),
    (5, [1, 2]), (6, [0, 3]), (7, [0, 1, 2]), (8, [3, 1, 0]),
]
N_PER = 10

def cosd(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 1 - float(a @ b) / (na * nb + 1e-300)

def run_stream(samples, n_classes=4):
    """samples: list of (vec, cls).  STR = normalized running centroid;
    EPI-ALL = cosine NN over all seen.  Forced classification."""
    cents = {}
    counts = defaultdict(int)
    seen = []
    s_ok = e_ok = 0
    for vec, cls in samples:
        # STR: nearest normalized centroid (cosine)
        if cents:
            best_c = min(cents, key=lambda c: cosd(vec, cents[c]))
            s_ans = best_c
        else:
            s_ans = None
        # EPI-ALL: cosine NN over all seen
        if seen:
            best_f = min(seen, key=lambda p: cosd(vec, p[0]))
            e_ans = best_f[1]
        else:
            e_ans = None
        s_ok += (s_ans == cls)
        e_ok += (e_ans == cls)
        # update centroid
        counts[cls] += 1
        n = counts[cls]
        if cls not in cents:
            cents[cls] = vec.copy()
        else:
            cents[cls] = cents[cls] + (vec - cents[cls]) / n
        cents[cls] /= (np.linalg.norm(cents[cls]) + 1e-300)
        seen.append((vec.copy(), cls))
    return s_ok, e_ok, len(seen)

# ================= P47: synthetic sweep =================
print("=== P47: Delta/sigma phase sweep (synthetic orthonormal classes) ===")
u = np.linalg.qr(np.random.default_rng(47).normal(size=(K, 4)))[0].T  # orthonormal dirs
p47 = []
for ratio in (0.125, 0.25, 0.5, 1.0, 2.0, 4.0):
    sigma = 1.0
    Delta = ratio * sigma
    rng = np.random.default_rng(int(1000 + ratio * 100))
    samples = []
    # 8 eras x 4 classes x 10 samples with absence arcs per ERAS
    for era, classes in ERAS:
        for ci in classes:
            for _ in range(N_PER):
                eps = rng.normal(0, sigma, K)
                samples.append((Delta * u[ci] + eps, ci))
    s_ok, e_ok, stored = run_stream(samples)
    n = len(samples)
    p47.append({"ratio": ratio, "STR": s_ok / n, "EPI_ALL": e_ok / n,
                "stored": stored})
    print(f"  Delta/sigma={ratio:6.3f}: STR={s_ok/n:.3f}  "
          f"EPI-ALL={e_ok/n:.3f}  (stored {stored})")
json.dump(p47, open("p47_phase_results.json", "w"), indent=1)
print("saved p47_phase_results.json")

# ================= P46-c-b: envelope family, normalized-cosine STR ======
print("\n=== P46-c-b: envelope family, NORMALIZED-cosine STR ===")
X, y, nuis = make_dataset(poch_cum, seed=777)
y = np.asarray(y)
by_class = {si: [i for i in range(len(X)) if y[i] == si] for si in range(4)}
A, B, z = nuis[:, 0], nuis[:, 1], nuis[:, 2]
k = np.arange(X.shape[1], dtype=float)

U = np.stack([np.log(np.abs(blind_envelope(c.astype(np.float64))) + 1e-300)
              for c in X])
U = U - U.mean(axis=1, keepdims=True)
# normalize directions (unit vectors): the cosine metric's own space
Un = U / (np.linalg.norm(U, axis=1, keepdims=True) + 1e-300)

variant_of = {}
for si in range(4):
    med = np.median(z[by_class[si]])
    variant_of[si] = max(by_class[si], key=lambda i: abs(z[i] - med))

ERAS_ENV = [
    (1, [(0, 20, False), (2, 25, False)]),
    (2, [(1, 20, False)]),
    (3, [(0, 15, False), (1, 15, False)]),
    (4, [(3, 4, False), (2, 15, False)]),
    (5, [(1, 15, False), (0, 15, False)]),
    (6, [(2, 15, False), (1, 12, False)]),
    (7, [(0, 12, True), (3, 10, False)]),
    (8, [(3, 10, False), (1, 10, False), (0, 10, False)]),
]
stream = []
used = defaultdict(list)
for era, spec in ERAS_ENV:
    for si, n, extreme in spec:
        if extreme:
            i = variant_of[si]
            stream.append({"era": era, "idx": i, "cls": si, "variant": True})
            used[si].append(i)
            continue
        pool = [j for j in by_class[si]
                if j not in used[si] and j != variant_of[si]]
        rng2 = np.random.default_rng(4601)
        rng2.shuffle(pool)
        for j in pool[:n]:
            stream.append({"era": era, "idx": j, "cls": si, "variant": False})
            used[si].append(j)
print(f"stream: {len(stream)}")

cents = {}
counts = defaultdict(int)
seen = []
s_ok = e_ok = 0
for item in stream:
    v = Un[item["idx"]]
    cls = item["cls"]
    s_ans = min(cents, key=lambda c: cosd(v, cents[c])) if cents else None
    e_ans = (min(seen, key=lambda p: cosd(v, p[0]))[1]
             if seen else None)
    s_ok += (s_ans == cls)
    e_ok += (e_ans == cls)
    counts[cls] += 1
    n = counts[cls]
    if cls not in cents:
        cents[cls] = v.copy()
    else:
        cents[cls] = cents[cls] + (v - cents[cls]) / n
        cents[cls] /= (np.linalg.norm(cents[cls]) + 1e-300)
    seen.append((v.copy(), cls))
n = len(stream)
print(f"normalized-cosine STR: {s_ok}/{n} = {100*s_ok/n:.1f}%   "
      f"EPI-ALL: {e_ok}/{n} = {100*e_ok/n:.1f}%")
json.dump({"STR_norm_cos": s_ok / n, "EPI_ALL": e_ok / n, "n": n},
          open("p46cb_results.json", "w"), indent=1)
print("saved p46cb_results.json")
