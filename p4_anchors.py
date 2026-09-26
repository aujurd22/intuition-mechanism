"""P4 v0: anchor retrieval over the 17 verified Ramanujan series.

The 17 series belong to four hypergeometric signatures s in {2,3,4,6}
(structure labels). Question: do representations of the series recover the
signature grouping? (The plan's P4, operationalized as leave-one-out
retrieval: for each series, are its nearest neighbours same-signature?)

Representations: raw normalized effective-coefficient sequences (32 terms,
sign included); text embeddings of rendered descriptions; random floor.
Metrics: hit@1/@3 (same-signature fraction in kNN), k-means ARI vs s.

Chance baseline: sum_s C(n_s,2)-weighted same-s probability.

Run:  python p4_anchors.py
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t1_modular import embed_texts  # noqa: E402


def hyper3(a, b, c, k):
    from mpmath import rf, factorial
    return rf(a, k) * rf(b, k) * rf(c, k) / factorial(k) ** 3


def h4(k):
    from mpmath import rf, factorial, mpf
    return rf(mpf(1) / 2, k) * rf(mpf(1) / 4, k) * rf(mpf(3) / 4, k) \
        / factorial(k) ** 3


# (eq, s, A, B, z, series-kind) -- all values from the VERIFIED encodings
SERIES = [
    ("eq28", 2, lambda k: 1 + 6 * k, lambda k: hyper3(1 / 2, 1 / 2, 1 / 2, k),
     lambda k: 1 / 4, "pos"),
    ("eq29", 2, lambda k: 5 + 42 * k, lambda k: hyper3(1 / 2, 1 / 2, 1 / 2, k),
     lambda k: 1 / 64, "pos"),
    ("eq30", 2, lambda k: (5 * np.sqrt(5) - 1) + (42 * np.sqrt(5) + 30) * k,
     lambda k: hyper3(1 / 2, 1 / 2, 1 / 2, k),
     lambda k: 0.000332597441440752932869945, "pos"),
    ("eq31", 3, lambda k: 2 + 15 * k, lambda k: hyper3(1 / 2, 1 / 3, 2 / 3, k),
     lambda k: 2 / 27, "pos"),
    ("eq32", 3, lambda k: 4 + 33 * k, lambda k: hyper3(1 / 2, 1 / 3, 2 / 3, k),
     lambda k: 4 / 125, "pos"),
    ("eq33", 6, lambda k: 1 + 11 * k, lambda k: hyper3(1 / 2, 1 / 6, 5 / 6, k),
     lambda k: 4 / 125, "pos"),
    ("eq34", 6, lambda k: 8 + 133 * k, lambda k: hyper3(1 / 2, 1 / 6, 5 / 6, k),
     lambda k: (4 / 85) ** 3, "pos"),
    ("eq35", 4, lambda k: 3 + 20 * k, lambda k: h4(k),
     lambda k: 1 / 8, "alt"),
    ("eq36", 4, lambda k: 3 + 28 * k, lambda k: h4(k),
     lambda k: 1 / (3 * 16), "alt"),
    ("eq37", 4, lambda k: 23 + 260 * k, lambda k: h4(k),
     lambda k: 1 / (18 ** 2), "alt"),
    ("eq38", 4, lambda k: 41 + 644 * k, lambda k: h4(k),
     lambda k: 1 / (5 * 72 ** 2), "alt"),
    ("eq39", 4, lambda k: 1123 + 21460 * k, lambda k: h4(k),
     lambda k: 1 / (882 ** 2), "alt"),
    ("eq40", 4, lambda k: 1 + 8 * k, lambda k: h4(k),
     lambda k: 1 / 9, "pos"),
    ("eq41", 4, lambda k: 1 + 10 * k, lambda k: h4(k),
     lambda k: 1 / 9 ** 2, "pos"),
    ("eq42", 4, lambda k: 3 + 40 * k, lambda k: h4(k),
     lambda k: 1 / 49 ** 2, "pos"),
    ("eq43", 4, lambda k: 19 + 280 * k, lambda k: h4(k),
     lambda k: 1 / 99 ** 2, "pos"),
    ("eq44", 4, lambda k: 1103 + 26390 * k, lambda k: h4(k),
     lambda k: 1 / 99 ** 4, "pos"),
]

NC = 32  # coefficient terms per series


def main():
    from mpmath import mp
    mp.dps = 40

    rows, seqs, texts = [], [], []
    for eq, s, A, B, z, kind in SERIES:
        c = []
        for k in range(NC):
            term = A(k) if k == 0 else A(k) + B(k) * k
            term = term * B(k - 1 + 1 - 1) if False else term
            h = B(k - 1 + 1 - 1) if False else None
            val = term * z(k) ** k
            if kind == "alt" and k >= 1:
                val = (-1) ** k * term  # alternating sign on the continuation
            c.append(float(val))
        c = np.array(c, dtype=np.float64)
        c = c / (np.linalg.norm(c) + 1e-300)
        seqs.append(c)
        rows.append({"eq": eq, "s": s})
        texts.append("Ramanujan series coefficients: "
                     + " ".join(f"{v:.6g}" for v in c[:16]))
    seqs = np.stack(seqs).astype(np.float32)

    # text embeddings
    emb = np.asarray(embed_texts(texts), dtype=np.float32)

    print(f"anchors: {len(rows)}, signatures: "
          f"{[(s, sum(1 for r in rows if r['s'] == s)) for s in (2, 3, 4, 6)]}")

    # ---- leave-one-out retrieval: raw vs embed vs random ----
    def knn_hits(z_all, s_labels, k=3):
        zn = z_all / (np.linalg.norm(z_all, axis=1, keepdims=True) + 1e-12)
        sim = zn @ zn.T
        np.fill_diagonal(sim, -np.inf)
        idx = np.argsort(-sim, axis=1)[:, :k]
        hits1 = hits3 = 0
        for i, nb in enumerate(idx):
            same = (s_labels[nb] == s_labels[i]).astype(int)
            hits1 += int(same[0])
            hits3 += int(same.sum() >= 1)
        return hits1, hits3

    s_arr = np.array([r["s"] for r in rows])
    rng = np.random.default_rng(0)
    res = {}
    for name, rep in (("raw", seqs), ("embed", emb),
                      ("random", rng.standard_normal(seqs.shape).astype(np.float32))):
        h1, h3 = knn_hits(rep, s_arr, 3)
        km = KMeans(n_clusters=4, n_init=20, random_state=0).fit(rep)
        a = ari(km.labels_, s_arr)
        res[name] = {"hit1": h1, "hit3": h3, "ARI": round(a, 3)}
        print(f"  {name:8s} hit@1={h1}/17  hit@3={h3}/17  ARI(vs s)={a:+.3f}")

    # chance: expected same-s fraction for a random neighbour
    n_by_s = {s: sum(1 for r in rows if r["s"] == s) for s in (2, 3, 4, 6)}
    # for each anchor, P(random neighbour same s) = (n_s - 1)/16 averaged
    chance = np.mean([(n_by_s[r["s"]] - 1) / 16 for r in rows])
    print(f"  chance same-s (avg): {chance:.3f}")

    with open("p4_results.json", "w", encoding="utf-8") as f:
        json.dump({"rows": rows, "results": res, "chance": chance}, f, indent=1)
    print("results -> p4_results.json")


if __name__ == "__main__":
    from sklearn.cluster import KMeans
    from sklearn.metrics import adjusted_rand_score as ari
    main()
