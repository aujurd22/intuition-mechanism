"""T1: real mathematical objects -- does compression cluster by arithmetic
invariant? (Intuition-Mechanism Program, registered prediction P3.)

Objects (all locally recomputable, no external corpus):
  A. Eisenstein q-expansion prefixes  E_w: a_n = sigma_{w-1}(n), w in 2..12
     (label = weight; shape of the divisor-sum sequence encodes it)
  B. Eta-product prefixes (Pi (1-q^n))^m, m in 2..12 (label = exponent)
  C. CM j-values: 64-digit strings of j((1+sqrt(-d))/2), d = Heegner set +
     class-number-2 discriminants (label = discriminant)

Representations compared (P3: AE ARI > text-embedding ARI + 0.15):
  ae        : MLP-AE bottleneck b=16 on the normalized vector
  embed     : sentence-transformers embedding of the textual form (baseline)
  raw       : the raw normalized vector itself
  random    : uniform random vectors (floor)

Run:  python t1_modular.py
"""
import json
import os
import sys

import numpy as np
import torch
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t0_scan import AE, ari, sd_metrics, train_ae  # noqa: E402

from mpmath import mp, mpc, mpf, jtheta, exp  # noqa: E402

mp.dps = 120


def sigma(n, s):
    return sum(d ** s for d in range(1, n + 1) if n % d == 0)


def eisenstein_vec(w, n_coef=32):
    v = np.array([sigma(n, w - 1) for n in range(1, n_coef + 1)],
                 dtype=np.float64)
    return v / (np.linalg.norm(v) + 1e-12)


def eta_poly_pow(m, n_coef=32):
    """(Pi_{n>=1} (1 - q^n))^m coefficient vector, degrees 1..n_coef.

    Base series via Euler's pentagonal number theorem; integer powers by
    repeated convolution -- exact arithmetic throughout.
    """
    base = np.zeros(n_coef + 1, dtype=np.int64)
    base[0] = 1
    k = 1
    while k * (3 * k - 1) // 2 <= n_coef:
        for g in (k * (3 * k - 1) // 2, k * (3 * k + 1) // 2):
            if g <= n_coef:
                base[g] += (-1) ** k
        k += 1
    result = base.copy()
    for _ in range(m - 1):
        result = np.convolve(result, base)[: n_coef + 1]
    v = result[1:].astype(np.float64)
    return v / (np.linalg.norm(v) + 1e-12)


def cm_j_digits(d, n_digits=64):
    tau = (1 + mpc(0, mpf(d) ** 0.5)) / 2 if d % 4 == 3 else mpc(0, mpf(d) ** 0.5)
    q = exp(mpc(0, mp.pi) * tau)
    t2, t3 = jtheta(2, 0, q), jtheta(3, 0, q)
    k2 = (t2 / t3) ** 4
    j = 256 * (1 - k2 + k2 ** 2) ** 3 / (k2 ** 2 * (1 - k2) ** 2)
    digits = mp.nstr(abs(mp.re(j)), n_digits + 8).replace(".", "").replace("e", "")
    digits = "".join(ch for ch in digits if ch.isdigit())[:n_digits]
    v = np.array([int(ch) for ch in digits.ljust(n_digits, "0")], dtype=np.float64)
    return v / 9.0


def heegner_set():
    h1 = [1, 2, 3, 7, 11, 19, 43, 67, 163]
    h2 = [15, 20, 24, 35, 40, 51, 52, 88, 91, 115, 123, 148, 187, 232, 235,
          267, 403, 427]
    return h1 + h2


def knn_sd(z, labels, k=3):
    zn = z / (np.linalg.norm(z, axis=1, keepdims=True) + 1e-9)
    sim = zn @ zn.T
    np.fill_diagonal(sim, -np.inf)
    idx = np.argsort(-sim, axis=1)[:, :k]
    sd = [float((labels[row] == labels[nb]).mean()) for row, nb in enumerate(idx)]
    return float(np.mean(sd))


def eval_repr(z, labels, name, k=3):
    n_clusters = len(set(labels))
    km = KMeans(n_clusters=n_clusters, n_init=20, random_state=0).fit(z)
    a = float(adjusted_rand_score(km.labels_, labels))
    sd = knn_sd(z, labels, k)
    print(f"    {name:10s} ARI={a:+.3f}  SD={sd:.3f}")
    return {"ari": a, "sd": sd}


def embed_texts(texts):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2",
                                device="cpu")
    v = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return v.astype(np.float32)


def main():
    rng = np.random.default_rng(0)
    results = {}

    # ---- A. Eisenstein series, label = weight ----
    weights = [2, 4, 6, 8, 10, 12]
    vecs = [eisenstein_vec(w) for w in weights]
    X, labels, texts = [], [], []
    for li, v in enumerate(vecs):
        for inst in range(3):
            noisy = v.copy()
            noisy[5:] += rng.normal(0, 1e-3, len(v) - 5)
            X.append(noisy / (np.linalg.norm(noisy) + 1e-12))
            labels.append(li)
            texts.append("coefficients: "
                         + " ".join(f"{c:.3f}" for c in noisy[:20]))
    X = np.stack(X).astype(np.float32)
    labels = np.array(labels)
    print("A. Eisenstein q-expansions (label = weight)", flush=True)
    z, _loss = train_ae(X, 16, steps=2000)
    results["eisenstein"] = {"ae": eval_repr(z, labels, "ae"),
                             "raw": eval_repr(X, labels, "raw"),
                             "embed": eval_repr(embed_texts(texts), labels, "embed")}
    rngv = np.random.default_rng(1).standard_normal(X.shape).astype(np.float32)
    results["eisenstein"]["random"] = eval_repr(rngv, labels, "random")

    # ---- A2. HARDER: 12 weights, full-coefficient noise ----
    weights_h = list(range(2, 26, 2))
    vecs = [eisenstein_vec(w, 16) for w in weights_h]
    X, labels, texts = [], [], []
    for li, v in enumerate(vecs):
        for inst in range(3):
            noisy = v + rng.normal(0, 2e-2, len(v))
            X.append(noisy / (np.linalg.norm(noisy) + 1e-12))
            labels.append(li)
            texts.append("coefficients: " + " ".join(f"{c:.3f}" for c in noisy))
    X = np.stack(X).astype(np.float32)
    labels = np.array(labels)
    print("A2. Eisenstein HARD (12 weights, full noise)", flush=True)
    z, _loss = train_ae(X, 16, steps=2000)
    results["eisenstein_hard"] = {"ae": eval_repr(z, labels, "ae"),
                                  "raw": eval_repr(X, labels, "raw"),
                                  "embed": eval_repr(embed_texts(texts), labels, "embed")}
    rngv = np.random.default_rng(4).standard_normal(X.shape).astype(np.float32)
    results["eisenstein_hard"]["random"] = eval_repr(rngv, labels, "random")

    # ---- B. Eta products, label = exponent ----
    exps = [2, 4, 6, 8, 10, 12]
    vecs = [eta_poly_pow(m) for m in exps]
    X, labels, texts = [], [], []
    for li, v in enumerate(vecs):
        for inst in range(3):
            noisy = v.copy()
            noisy[5:] += rng.normal(0, 1e-3, len(v) - 5)
            X.append(noisy / (np.linalg.norm(noisy) + 1e-12))
            labels.append(li)
            texts.append("coefficients: "
                         + " ".join(f"{c:.3f}" for c in noisy[:20]))
    X = np.stack(X).astype(np.float32)
    labels = np.array(labels)
    print("B. Eta products (label = exponent)", flush=True)
    z, _loss = train_ae(X, 16, steps=2000)
    results["eta"] = {"ae": eval_repr(z, labels, "ae"),
                      "raw": eval_repr(X, labels, "raw"),
                      "embed": eval_repr(embed_texts(texts), labels, "embed")}
    rngv = np.random.default_rng(2).standard_normal(X.shape).astype(np.float32)
    results["eta"]["random"] = eval_repr(rngv, labels, "random")

    # ---- C. CM j-value digits, label = discriminant ----
    disc = heegner_set()
    X, labels, texts = [], [], []
    for di, d in enumerate(disc):
        v = cm_j_digits(d)
        for shift in [0, 1, 2]:
            X.append(np.roll(v, -shift)[: len(v)] / 9.0)
            labels.append(di)
            texts.append("digits: "
                         + "".join(str(int(x * 9)) for x in v[:40]))
    X = np.stack(X).astype(np.float32)
    labels = np.array(labels)
    print("C. CM j-value digits (label = discriminant)", flush=True)
    z, _loss = train_ae(X, 16, steps=2000)
    results["cm_digits"] = {"ae": eval_repr(z, labels, "ae"),
                            "raw": eval_repr(X, labels, "raw"),
                            "embed": eval_repr(embed_texts(texts), labels, "embed")}
    rngv = np.random.default_rng(3).standard_normal(X.shape).astype(np.float32)
    results["cm_digits"]["random"] = eval_repr(rngv, labels, "random")

    print("\n=== P3 reading (AE ARI > embed ARI + 0.15 ?) ===")
    for t, r in results.items():
        print(f"  {t:10s} ae={r['ae']['ari']:+.3f} embed={r['embed']['ari']:+.3f} "
              f"raw={r['raw']['ari']:+.3f} random={r['random']['ari']:+.3f}")

    with open("t1_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1)
    print("results -> t1_results.json")


if __name__ == "__main__":
    main()
