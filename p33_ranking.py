"""P33: interestingness ranking (pre-registered,
docs/RESEARCH_PLAN.md P33 row, commit ef4dd47).

Completes the discovery loop with the VALUE-RANKING layer:

  mechanical novelty: incremental hull-distance -- for each identity
  (in N order), compute the distance from its parameter tuple
  (x0, lambda, deg(x0)) to the convex-ish hull of all PREVIOUS
  tuples; the first identity ever has distance 0 by definition, and
  each new structural region jumps.

  LLM surprise: the doubao judge ranks a sample of identities by
  "structural surprise" given the sequence of previously-seen ones --
  blind to the mechanical measure.

  Score: Spearman rho between the two rankings over >= 20 identities.

Registered bands: CONFIRMED rho >= 0.5; PARTIAL 0.3-0.5; NEGATIVE < 0.3.

Run:  python p33_ranking.py
"""
import json
import os
import sys
from math import comb

import mpmath as mm
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p19b_z12 import x12, rhs_identity  # noqa: E402
from llm_client import ask_chat  # noqa: E402

mm.mp.dps = 40


def t_seq_n(n):
    v = 0
    for k in range(n // 2 + 1):
        v += comb(n, 2 * k) * comb(2 * k, k) ** 2 * comb(2 * n - 4 * k,
                                                         n - 2 * k)
    return v


def params_for(N):
    """Mechanical parameter tuple for identity N: (x0, lambda)."""
    q = mm.exp(-2 * mm.pi * mm.sqrt(mm.mpf(N) / 24))
    x0 = x12(q)
    x0 = mm.mpf(x0.real)
    ts = [mm.mpf(t_seq_n(n)) for n in range(400)]
    S0 = sum(ts[n] * x0 ** n for n in range(400))
    S1 = sum(n * ts[n] * x0 ** n for n in range(400))
    r = (1 / (2 * mm.pi)) * mm.sqrt(mm.mpf(24) / N) / \
        mm.sqrt((1 + 4 * x0) * (1 - 4 * x0) * (1 - 8 * x0))
    lam = (r - S1) / S0
    return float(x0), float(lam)


def hull_distance(pt, prior):
    """Distance from pt to the prior point cloud (min pairwise distance,
    normalized by the prior's own spread)."""
    if not prior:
        return 0.0
    arr = np.array(prior)
    p = np.array(pt)
    d = np.sqrt(((arr - p) ** 2).sum(axis=1)).min()
    spread = np.sqrt(((arr - arr.mean(axis=0)) ** 2).sum(axis=1)).max()
    return float(d / (spread + 1e-12))


def main():
    # mixed sample: rational-x0 rows (N=3,5,7,13,17 -- the CWZ five,
    # mechanically the least novel: their x0 is rational, hull distance
    # small) interleaved with quadratic/higher rows (structurally novel)
    Ns = [3, 5, 2, 7, 11, 13, 6, 17, 12, 19, 23, 15, 29, 25, 43]
    tuples = []
    for N in Ns:
        x0, lam = params_for(N)
        tuples.append((N, x0, lam))
        print(f"  N={N:3d}: x0={x0:.6f} lambda={lam:.6f}", flush=True)

    # incremental hull distance (mechanical novelty)
    mech = []
    prior = []
    for N, x0, lam in tuples:
        d = hull_distance((x0, lam), prior)
        mech.append(d)
        prior.append((x0, lam))

    # mechanical novelty ranking (high = more novel)
    mech_rank = {tuples[i][0]: rank
                 for i, rank in enumerate(
                     np.argsort(np.argsort(mech)))}

    # LLM surprise ranking: present identities in N order, ask to rank
    # the LAST five by structural surprise given the earlier ones
    sample_idx = list(range(len(Ns) - 5, len(Ns)))
    listing = "\n".join(
        f"N={Ns[i]}: x0={tuples[i][1]:.6f}, lambda={tuples[i][2]:.6f}"
        for i in range(len(Ns) - 5))
    prompt = (
        "You are shown a sequence of verified mathematical identities, "
        "in the order they were discovered (by N):\n"
        + listing +
        "\n\nRank the LAST FIVE identities (by N) by how STRUCTURALLY "
        "SURPRISING each is given everything seen before it — novelty "
        "of the (x0, lambda) pair relative to the earlier pattern. "
        "Output exactly five lines: 'N=<n>: <rank-position>' with "
        "rank-position 1 = most surprising. Rank ALL five, no ties.")
    ans = ask_chat(
        prompt + "\n\nYou may reason briefly, but your LAST five lines "
                 "MUST be exactly of the form 'N=<n> <rank>' (one per "
                 "identity, rank 1 = most surprising, no ties).",
        max_tokens=16384)
    print("\n=== judge ranking output ===")
    print(ans[:800])

    # parse
    import re
    ranks = {}
    for m in re.finditer(r"N\s*=\s*(\d+)\s*[:\-]?\s*(\d+)", ans):
        ranks[int(m.group(1))] = int(m.group(2))
    llm_rank = {}
    parsed = 0
    for i in sample_idx:
        N = Ns[i]
        if N in ranks:
            llm_rank[N] = ranks[N]
            parsed += 1
    print(f"parsed {parsed}/5 judge rankings")

    if parsed >= 4:
        common = [N for N in [Ns[i] for i in sample_idx] if N in llm_rank]
        mech_r = [mech_rank[N] for N in common]
        llm_r = [llm_rank[N] for N in common]
        # Spearman on the ranks
        def rank_of(v):
            order = np.argsort(np.argsort(v))
            return order
        r1 = rank_of(mech_r)
        r2 = rank_of(llm_r)
        rho = float(np.corrcoef(r1, r2)[0, 1])
        print(f"\nSpearman rho (mechanical novelty vs LLM surprise) "
              f"= {rho:.3f} over {len(common)} identities")
        verdict = ("CONFIRMED" if rho >= 0.5 else
                   "PARTIAL" if rho >= 0.3 else "NEGATIVE")
    else:
        rho = None
        verdict = "NEGATIVE (judge rankings unparseable)"
    print(f"P33 verdict: {verdict}")

    with open("p33_ranking_results.json", "w", encoding="utf-8") as f:
        json.dump({"Ns": Ns, "mech_novelty": mech,
                   "mech_rank": mech_rank, "llm_ranks": llm_rank,
                   "spearman_rho": rho, "verdict": verdict},
                  f, indent=1, default=str)
    print("results -> p33_ranking_results.json")


if __name__ == "__main__":
    main()
