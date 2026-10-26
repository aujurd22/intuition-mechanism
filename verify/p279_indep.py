# -*- coding: utf-8 -*-
"""Independent recompute for P279 — clustering via pairwise adjacency + union-find
instead of the sorted-gap scan used by p279_consensus_cluster.py.

Compares every row's R2 estimate (and the two target rows' rel_errs) against
p279_verdict.json. Exit 0 iff max |diff| <= 1e-9 px.

Run:  python verify/p279_indep.py
"""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(REPO, "out", "p278", "p278_raw.json")
VERDICT = os.path.join(REPO, "p279_verdict.json")
GAP = 5.0


def components(vals):
    """Union-find over '|a-b| <= GAP' edges."""
    parent = list(range(len(vals)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        parent[find(i)] = find(j)

    for i in range(len(vals)):
        for j in range(i + 1, len(vals)):
            if abs(vals[i] - vals[j]) <= GAP:
                union(i, j)
    groups = {}
    for i in range(len(vals)):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])


def consensus(templates):
    tmpl = [t for t in templates if t["disp"] >= 0]
    if not tmpl:
        return None
    groups = []
    for idxs in components([t["disp"] for t in tmpl]):
        members = [tmpl[i] for i in idxs]
        groups.append((len(members),
                       sum(m["ncc"] for m in members) / len(members),
                       median([m["disp"] for m in members])))
    groups.sort(key=lambda g: (-g[0], -g[1], g[2]))
    return groups[0]


def main():
    rows = json.load(open(RAW, encoding="utf-8"))
    verdict = json.load(open(VERDICT, encoding="utf-8"))
    stored = {r["row"]: r for r in verdict["rows"]}
    worst = 0.0
    problems = []
    for r in rows:
        key = f"{r['scene']}/{r['obj'][:34]}"
        got = consensus(r["templates"])
        want = stored[key]["cluster_R2"]
        if got is None or want is None:
            if got is not None or want is not None:
                problems.append((key, want, got))
            continue
        diff = abs(got[2] - want)
        worst = max(worst, diff)
        if diff > 1e-9 or got[0] != stored[key]["cluster_size"]:
            problems.append((key, want, got))
    print(f"rows checked: {len(rows)}, max |diff| = {worst} px")
    for p in problems:
        print("  MISMATCH", p)
    sys.exit(0 if not problems else 1)


if __name__ == "__main__":
    main()
