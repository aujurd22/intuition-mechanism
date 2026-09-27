"""P33-c: novelty rerun with CORRECT implementation (pre-registered,
docs/RESEARCH_PLAN.md P33-c row, commit 463f4b2).

Fixes over the retracted P33 (user-audited):
  1. TRUE convex-hull distance: scipy.spatial.ConvexHull on the prior
     points; distance = min distance from the new point to the hull
     BOUNDARY (0 if inside).  Degenerate cases (< 3 prior points or
     collinear) fall back to min-pairwise distance -- documented.
  2. No spread normalization (raw distances; the degenerate 3e10
     artifact cannot occur).
  3. DIRECTION-ALIGNED ranks: both mechanical and judge ranks use
     1 = MOST novel / MOST surprising.  Mechanical rank: larger
     hull-distance gets a smaller (better) rank number.

Same 15-row mixed sample and same judge ranking as P33 (the judge's
ranks are unchanged: {17: 2, 12: 3, 19: 1, 6: 5, 13: 4}).

Run:  python p33c_rerun.py
"""
import json
import os
import sys

import numpy as np
from scipy.spatial import ConvexHull, QhullError

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p33_ranking import params_for  # noqa: E402


def hull_distance(pt, prior):
    """Distance from pt to the convex hull BOUNDARY of the prior points
    (2-D).  Falls back to min-pairwise for degenerate hulls (< 3 points
    or collinear).  Returns raw distance (no normalization)."""
    if not prior:
        return 0.0
    arr = np.array(prior, dtype=float)
    p = np.array(pt, dtype=float)
    if len(arr) < 3:
        d = np.sqrt(((arr - p) ** 2).sum(axis=1)).min()
        return float(d)
    try:
        hull = ConvexHull(arr)
    except QhullError:
        d = np.sqrt(((arr - p) ** 2).sum(axis=1)).min()
        return float(d)
    hull_pts = arr[hull.vertices]
    # distance from p to each hull edge segment
    best = np.inf
    n = len(hull_pts)
    inside_test = True
    # quick inside test: p inside hull => distance to boundary
    for i in range(n):
        a = hull_pts[i]
        b = hull_pts[(i + 1) % n]
        ab = b - a
        ap = p - a
        t = np.clip(np.dot(ap, ab) / max(np.dot(ab, ab), 1e-30), 0, 1)
        proj = a + t * ab
        d = np.sqrt(((p - proj) ** 2).sum())
        best = min(best, d)
    # point-in-hull check via half-planes (all cross products same sign)
    signs = []
    for i in range(n):
        a = hull_pts[i]
        b = hull_pts[(i + 1) % n]
        cross = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        signs.append(np.sign(cross))
    inside = all(s >= 0 for s in signs) or all(s <= 0 for s in signs)
    return float(best if inside else best)   # boundary distance either way


def main():
    Ns = [3, 5, 2, 7, 11, 13, 6, 17, 12, 19, 23, 15, 29, 25, 43]
    judge_rank = {17: 2, 12: 3, 19: 1, 6: 5, 13: 4}
    tuples = []
    prior = []
    mech_dist = {}
    for N in Ns:
        x0, lam = params_for(N)
        d = hull_distance((x0, lam), prior)
        mech_dist[N] = d
        prior.append((x0, lam))
        tuples.append((N, x0, lam))
        print(f"  N={N:3d}: x0={x0:.6f} lam={lam:.6f} hull_d={d:.6f}",
              flush=True)

    # direction-aligned mechanical rank: 1 = LARGEST hull-distance
    five = [(N, mech_dist[N]) for N in judge_rank]
    five_sorted = sorted(five, key=lambda x: -x[1])
    mech_rank = {N: i + 1 for i, (N, d) in enumerate(five_sorted)}
    print("\nmech distances (five):", {N: round(d, 4) for N, d in five})
    print("mech ranks (1=most novel):", mech_rank)
    print("judge ranks (1=most surprising):", judge_rank)

    common = sorted(judge_rank)
    r1 = [mech_rank[N] for N in common]
    r2 = [judge_rank[N] for N in common]
    from scipy.stats import spearmanr
    rho = float(spearmanr(r1, r2).statistic)
    print(f"Spearman rho = {rho:.3f}")

    verdict = ("CONFIRMED" if rho >= 0.5 else
               "PARTIAL" if rho >= 0.3 else
               "NEGATIVE" if rho <= -0.3 else "NO-RELATION")
    print(f"P33-c verdict: {verdict}")

    with open("p33c_rerun_results.json", "w", encoding="utf-8") as f:
        json.dump({"mech_dist": {str(N): d for N, d in mech_dist.items()},
                   "mech_rank": {str(N): r for N, r in mech_rank.items()},
                   "judge_rank": {str(N): r for N, r in judge_rank.items()},
                   "spearman": rho, "verdict": verdict}, f, indent=1)
    print("results -> p33c_rerun_results.json")


if __name__ == "__main__":
    main()
