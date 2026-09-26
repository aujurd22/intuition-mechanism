"""P4 clean three-tier experiment (external-review action item).

BUG FIXED: the earlier p4_anchors.py/p4_ratio.py built c_k as
(A+Bk) * z^k -- the hypergeometric factor hyper3(1/2, 1/s, 1-1/s, k) was
ADDED as a linear term instead of MULTIPLIED, so P4 v0/v1 measured garbage
sequences and their "negative" verdicts are invalid (retracted).

Correct coefficient:  c_k = sign * (A_lin + B_lin*k) * H_k * z^k
with H_k = (1/2)_k (1/s)_k (1-1/s)_k / (k!)^3,  s in {2,3,4,6}.

Three tiers (external-review design):
  A blind   : raw normalized c-sequences, kNN same-signature
  B ratio   : R_k = (c_{k+1}/c_k) normalized by the (A+Bk) linear factor
              and z -- leaves the pure hypergeometric signature
  C template: R_k matched against the 4 theoretical signature templates
              T_k(s) = (k+1/2)(k+1/s)(k+1-1/s)/(k+1)^3  -> s classification

Metrics: hit@1, hit@3-any, mean same-family fraction@3, ARI, per-signature
recall, and a properly computed chance baseline.

Run:  python p4_clean.py
"""
import json
import os
import sys
from math import comb

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t0_scan import ari  # noqa: E402
from t1_modular import embed_texts  # noqa: E402

NC = 32


def hyper3(a, b, c, k):
    from mpmath import rf, factorial
    return float(rf(a, k) * rf(b, k) * rf(c, k) / factorial(k) ** 3)


def h4(k):
    return hyper3(0.5, 0.25, 0.75, k)


# (eq, s, A_lin, B_lin, z, sign, c0) -- all from the VERIFIED encodings
SERIES = [
    ("eq28", 2, 1, 6, 0.25, +1, None),
    ("eq29", 2, 5, 42, 1 / 64, +1, None),
    ("eq30", 2, 5 * np.sqrt(5) - 1, 42 * np.sqrt(5) + 30,
     64 * ((3 - np.sqrt(5)) / 16) ** 4, +1, None),  # literature z (externally sourced)
    ("eq31", 3, 2, 15, 2 / 27, +1, None),
    ("eq32", 3, 4, 33, 4 / 125, +1, None),
    ("eq33", 6, 1, 11, 4 / 125, +1, None),
    ("eq34", 6, 8, 133, (4 / 85) ** 3, +1, None),
    ("eq35", 4, 3, 20, -1 / 8, -1, 1.5),                # 4/pi = 3/2 - (23/8)r1 + ...
    ("eq36", 4, 3, 28, -1 / (3 * 16), -1, 0.75),
    ("eq37", 4, 23, 260, -1 / 324, -1, 23 / 18),
    ("eq38", 4, 41, 644, -1 / (5 * 72 ** 2), -1, 41 / 72),
    ("eq39", 4, 1123, 21460, -1 / 882 ** 2, -1, 1123 / 882),
    ("eq40", 4, 1, 8, 1 / 9, +1, 1),
    ("eq41", 4, 1, 10, 1 / 81, +1, 1 / 9),
    ("eq42", 4, 3, 40, 1 / 49 ** 2, +1, 3 / 49),
    ("eq43", 4, 19, 280, 1 / 99 ** 2, +1, 19 / 99),
    ("eq44", 4, 1103, 26390, 1 / 99 ** 4, +1, 1103 / 99 ** 2),
]


def build():
    seqs, meta, texts = [], [], []
    for eq, s, Al, Bl, z, sign, c0 in SERIES:
        c = []
        for k in range(NC):
            lin = Al + Bl * k
            H = hyper3(0.5, 1 / s, 1 - 1 / s, k)
            v = sign * lin * H * z ** k
            if c0 is not None and k == 0:
                v += c0
            c.append(v)
        c = np.array(c, dtype=np.float64)
        c = c / (np.linalg.norm(c) + 1e-300)
        seqs.append(c)
        meta.append({"eq": eq, "s": s})
        texts.append("Ramanujan series coefficients: "
                     + " ".join(f"{v:.6g}" for v in c[:16]))
    return np.stack(seqs).astype(np.float32), meta, texts


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
    return {"hit1": h1, "hit3": h3, "mean_frac3": round(frac / len(idx), 3),
            "macro_recall": round(macro, 3)}


def main():
    X, meta, texts = build()
    s_arr = np.array([m["s"] for m in meta])
    print(f"anchors: {len(X)}; signatures: "
          f"{[(s, int((s_arr == s).sum())) for s in (2, 3, 4, 6)]}")

    # proper chance: E[same-s in 3 draws without replacement] per anchor
    chances = []
    for i in range(len(X)):
        ns = int((s_arr == s_arr[i]).sum()) - 1
        others = len(X) - 1
        # P(same-s in k=3 draws without replacement)
        p0 = comb(others - ns, 3) / comb(others, 3) if others - ns >= 3 else 0.0
        chances.append(1 - p0)
    chance3 = float(np.mean(chances))
    chance1 = float(np.mean([(s_arr == s_arr[i]).sum() - 1
                             for i in range(len(X))]) / (len(X) - 1))
    print(f"chance hit@1 = {chance1:.3f}; chance hit@3-any = {chance3:.3f}\n")

    emb = np.asarray(embed_texts(texts), dtype=np.float32)
    rng = np.random.default_rng(0)
    rand = rng.standard_normal(X.shape).astype(np.float32)

    # ---- Tier A: blind raw ----
    mA = knn_metrics(X, s_arr)
    # ---- Tier A': text embedding (de-leaked) ----
    mE = knn_metrics(emb, s_arr)
    # ---- Tier B: ratio-normalized (z and linear factor divided out) ----
    R = []
    for i, (eq, s, Al, Bl, z, sign, c0) in enumerate(SERIES):
        c = X[i]
        rk = []
        for k in range(NC - 1):
            if abs(c[k]) < 1e-300:
                rk.append(0.0)
                continue
            lin_ratio = (Al + Bl * k) / (Al + Bl * (k + 1))
            rk.append((c[k + 1] / c[k]) / (lin_ratio * z))
        rk = np.array(rk, dtype=np.float64)
        rk = rk / (np.linalg.norm(rk) + 1e-300)
        R.append(rk)
    R = np.stack(R).astype(np.float32)
    mB = knn_metrics(R, s_arr)

    # ---- Tier C: theoretical signature templates ----
    ks = np.arange(1, NC)
    templates = {}
    for s in (2, 3, 4, 6):
        templates[s] = np.array([(k + 0.5) * (k + 1 / s) * (k + 1 - 1 / s)
                                 / (k + 1) ** 3 for k in ks], dtype=np.float64)
    correct = 0
    per_sig_c = {}
    for i, (eq, s, Al, Bl, z, sign, c0) in enumerate(SERIES):
        rk = R[i]
        rk_n = rk / (np.linalg.norm(rk) + 1e-300)
        dists = {}
        for st, T in templates.items():
            Tn = T / (np.linalg.norm(T) + 1e-300)
            dists[st] = float(np.linalg.norm(rk_n - Tn))
        pred = min(dists, key=dists.get)
        per_sig_c.setdefault(s, []).append(pred == s)
    c_acc = float(np.mean([np.mean(v) for v in per_sig_c.values()]))

    mR = knn_metrics(R, s_arr)
    print(f"Tier A  blind raw   : {mA}")
    print(f"Tier A' embed       : {mE}")
    print(f"Tier B  ratio-norm  : {mB}")
    print(f"Tier C  template s-classification accuracy: {c_acc:.3f}")
    print(f"  (per-signature: "
          f"{ {s: round(float(np.mean(v)), 2) for s, v in per_sig_c.items()} })")

    with open("p4_clean_results.json", "w", encoding="utf-8") as f:
        json.dump({"chance_hit1": chance1, "chance_hit3": chance3,
                   "tierA_raw": mA, "tierA_embed": mE, "tierB_ratio": mB,
                   "tierC_template_acc": c_acc,
                   "tierC_per_signature": {str(s): round(float(np.mean(v)), 2)
                                           for s, v in per_sig_c.items()}},
                  f, indent=1)
    print("results -> p4_clean_results.json")


if __name__ == "__main__":
    main()
