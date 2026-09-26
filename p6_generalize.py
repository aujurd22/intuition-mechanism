"""P6: 17 -> 18 generalization test (registered prediction P6, two-tier).

Data: 20 members.
  - 17 literature series (Ramanujan 1914 eq 28-44), from p4_clean.SERIES.
  - 3 mechanically generated (D1 v2): d=19/43/67, all signature s=6.

Question (registry wording): given the 17 known in-family samples, does the
model's acceptance/ranking put the 18th valid member (Chudnovsky family,
d=19/43/67) above the uniform baseline?

Two tiers (the P4 lesson made into design):
  Tier A  BLIND           : ranker sees only normalized raw coefficient
          sequences (no invariant machinery). P4 says blind retrieval is at
          chance; the blind tier should confirm generalization does NOT
          happen blind -- the asymmetry IS the result.
  Tier B  GIVEN-INVARIANT : ranker sees the ratio-normalized invariant space
          (per-series z, linear factor, R-shape). Prediction: d=19/43/67
          rank next to the s=6 anchors (eq33/34).

Scoring: for each held-out mechanical member, rank of the CLOSEST same-s
member among the other 19 (cosine). Chance mean rank for a 5-member family
(3 literature s=6 + 1 query... we use the family size as-is): reported
below as `chance`.

Run:  python p6_generalize.py
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p4_clean import SERIES, NC, hyper3  # noqa: E402

# mechanically generated members (D1 v2): (name, s, A_lin, B_lin, z)
MECH = [
    ("d19", 6, 25, 342, -1728 / 96 ** 3),
    ("d43", 6, 789, 16254, -1728 / 960 ** 3),
    ("d67", 6, 10177, 261702, -1728 / 5280 ** 3),
]


def build_all():
    """20 rows: 17 literature + 3 mechanical."""
    rows, seqs = [], []
    for eq, s, Al, Bl, z, sign, c0 in SERIES:
        c = []
        for k in range(NC):
            H = hyper3(0.5, 1 / s, 1 - 1 / s, k)
            v = sign * (Al + Bl * k) * H * z ** k
            if c0 is not None and k == 0:
                v += c0
            c.append(v)
        seqs.append(np.array(c))
        rows.append({"name": eq, "s": s, "mech": False,
                     "Al": Al, "Bl": Bl, "z": z})
    for name, s, Al, Bl, z in MECH:
        c = []
        for k in range(NC):
            H = hyper3(0.5, 1 / s, 1 - 1 / s, k)
            c.append((Al + Bl * k) * H * z ** k)
        seqs.append(np.array(c))
        rows.append({"name": name, "s": s, "mech": True,
                     "Al": Al, "Bl": Bl, "z": z})
    return rows, seqs


def ratio_repr(c, Al, Bl, z):
    """Per-series invariant normalization -> R-shape (P4 Tier B repr)."""
    rk = []
    for k in range(NC - 1):
        if abs(c[k]) < 1e-300:
            rk.append(0.0)
            continue
        lin_corr = (Al + Bl * k) / (Al + Bl * (k + 1))
        rk.append((c[k + 1] / c[k]) * lin_corr / z)
    rk = np.array(rk, dtype=np.float64)[1:]  # drop c0-polluted slot
    return rk / (np.linalg.norm(rk) + 1e-300)


def rank_of_true_family(rep, i_query, s_arr):
    """Rank of the closest same-s member for query i (1 = best)."""
    zn = rep / (np.linalg.norm(rep, axis=1, keepdims=True) + 1e-12)
    sim = zn @ zn.T
    sim[i_query, i_query] = -np.inf
    order = np.argsort(-sim[i_query])
    for r, j in enumerate(order):
        if s_arr[j] == s_arr[i_query]:
            return r + 1, int(s_arr[j])
    return len(order), -1


def main():
    rows, seqs_raw = build_all()
    s_arr = np.array([r["s"] for r in rows])
    names = [r["name"] for r in rows]
    mech_idx = [i for i, r in enumerate(rows) if r["mech"]]
    print(f"members: {len(rows)} ({len(mech_idx)} mechanical, "
          f"{len(rows) - len(mech_idx)} literature)")
    print(f"mechanical: {[names[i] for i in mech_idx]} (all s=6)\n")

    # ---- representations ----
    X_blind = np.stack([c / (np.linalg.norm(c) + 1e-300)
                        for c in seqs_raw]).astype(np.float32)
    R_inv = np.stack([ratio_repr(c, r["Al"], r["Bl"], r["z"])
                      for c, r in zip(seqs_raw, rows)]).astype(np.float32)

    results = {}
    for tier, rep in (("A_blind", X_blind), ("B_invariant", R_inv)):
        per_mech = {}
        for i in mech_idx:
            rank, fam = rank_of_true_family(rep, i, s_arr)
            per_mech[names[i]] = {"rank": rank, "of": len(rows) - 1,
                                  "closest_family": fam}
        ranks = [v["rank"] for v in per_mech.values()]
        results[tier] = {
            "per_member": per_mech,
            "mean_rank": float(np.mean(ranks)),
            "norm_rank": round(float(np.mean(ranks)) / (len(rows) - 1), 3),
            "hit1": int(sum(1 for v in ranks if v == 1)),
        }
        print(f"--- Tier {tier} ---")
        for n, v in per_mech.items():
            print(f"  {n:5s}: rank {v['rank']:2d}/{v['of']} "
                  f"(closest s={v['closest_family']})")
        print(f"  mean rank {results[tier]['mean_rank']:.1f} / "
              f"{len(rows) - 1}; hit@1 {results[tier]['hit1']}/3\n")

    # chance: a random same-s draw sits uniformly among 19 positions whose
    # first same-s member appears at expected position
    # E[rank] = (N_others + 1) / (n_family_in_others + 1);
    # for a mech query: 16 others, s=6 family (eq33, eq34) => 17/3 = 5.67
    chance = (len(rows) - 1 + 1) / (2 + 1)
    print(f"chance mean rank (2-member family among 19): {chance:.2f}")

    verdict = {}
    for tier in ("A_blind", "B_invariant"):
        mr = results[tier]["mean_rank"]
        verdict[tier] = {
            "mean_rank": mr, "chance": chance,
            "beats_chance": bool(mr < chance),
            "ratio": round(chance / mr, 2) if mr else None,
        }
        print(f"  {tier}: mean_rank {mr:.2f} vs chance {chance:.2f} "
              f"-> {'BEATS' if mr < chance else 'AT/BELOW'} chance "
              f"({verdict[tier]['ratio']}x)")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "p6_results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"chance_mean_rank": chance, "tiers": results,
                   "verdict": verdict}, f, indent=1)
    print(f"results -> {out}")


if __name__ == "__main__":
    main()
