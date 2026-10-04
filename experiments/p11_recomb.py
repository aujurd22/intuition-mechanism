"""P11: non-constructive recombination (P5 v2).

Mechanism finding (pre-registered as part of the run): in the Eisenstein
ring, EVERY multiplicative recombination operator is constructive --
low-weight form spaces are 1-dimensional (E8 ~ E4^2, E10 ~ E4*E6, ...),
so any product of proportional pairs stays proportional (verified
empirically: CROSS (m1*m2, n1*n2), SWAP (m1*n2, m2*n1) and POWER-MIX
(m1*m2, n1^2) all hit 49/49 = rate 1.0 -- identical to the v1 flaw).

The genuinely non-constructive operator is ADDITIVE-MIX:
    m1 + m2  vs  n1 + n2     with m1=c1*n1, m2=c2*n2
proportional to n1+n2 IFF c1 == c2 -- no guarantee whatsoever. The
verifier decides. That is the P11 measurement.

Run:  python p11_recomb.py
"""
import json
import os
import random
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t2_engine import build_basis, monomials, is_proportional

TRIALS = 20
BUDGET = 300
SEED_HIT = ("E8", "E4*E4")


def run_arm(memory, seed, monos, by_weight):
    rng = random.Random(seed)
    seen = {frozenset(SEED_HIT)}
    hits = [SEED_HIT]           # list of (left, right) with left ~ right
    recomb_events = recomb_hits = 0
    rand_props = rand_hits = 0
    for step in range(1, BUDGET + 1):
        proposal = None
        is_recomb = False
        if memory and len(hits) >= 2 and rng.random() < 0.5:
            # ADDITIVE-MIX: pick two distinct hits, sum the two sides
            (m1, n1), (m2, n2) = rng.sample(hits, 2)
            # additive mixing needs the underlying weights equal; for the
            # seeded hits and monomial hits we know monos[name][1]; for
            # SUM-hits weight is the shared weight (carry it along)
            proposal = ("SUM", m1, m2, n1, n2)
            is_recomb = True
        if proposal is None:
            w = rng.choice([w for w in by_weight if len(by_weight[w]) > 1])
            a, b = rng.sample(by_weight[w], 2)
            if frozenset((a, b)) in seen:
                continue
            proposal = ("PAIR", a, b)
            rand_props += 1

        if proposal[0] == "SUM":
            _, m1, m2, n1, n2 = proposal
            key = frozenset((f"({m1}+{m2})", f"({n1}+{n2})"))
            if key in seen:
                continue
            seen.add(key)
            recomb_events += 1
            wl = monos[m1][1] if m1 in monos else None
            wr = monos[m2][1] if m2 in monos else None
            if wl is None or wr is None or wl != wr:
                continue          # weight mismatch: invalid additive mix
            s_left = monos[m1][0] + monos[m2][0]
            s_right = monos[n1][0] + monos[n2][0]
            if is_proportional(s_left, s_right):
                recomb_hits += 1
                hits.append((f"({m1}+{m2})", f"({n1}+{n2})"))
        else:
            _, a, b = proposal
            seen.add(frozenset((a, b)))
            if monos[a][1] == monos[b][1] and \
                    is_proportional(monos[a][0], monos[b][0]):
                rand_hits += 1
                hits.append((a, b))
    return {"recomb_events": recomb_events, "recomb_hits": recomb_hits,
            "rand_props": rand_props, "rand_hits": rand_hits,
            "total_hits": len(hits) - 1}


def main():
    print("building space...", flush=True)
    basis = build_basis()
    monos = monomials(basis, max_factors=2, max_weight=36)
    by_weight = {}
    for name, (s, w, g) in monos.items():
        by_weight.setdefault(w, []).append(name)
    print(f"monomials: {len(monos)}", flush=True)

    print(f"A/B: {TRIALS} trials x {BUDGET} budget", flush=True)
    A = [run_arm(False, t, monos, by_weight) for t in range(TRIALS)]
    B = [run_arm(True, t, monos, by_weight) for t in range(TRIALS)]

    agg = lambda runs, k: float(np.mean([r[k] for r in runs]))
    background = (sum(r["rand_hits"] for r in A) + sum(r["rand_hits"] for r in B)) / \
                 max(sum(r["rand_props"] for r in A) + sum(r["rand_props"] for r in B), 1)
    recomb_events = sum(r["recomb_events"] for r in B)
    recomb_hits = sum(r["recomb_hits"] for r in B)
    post_rate = recomb_hits / recomb_events if recomb_events else None

    print(f"\nrecomb events: {recomb_events}, hits: {recomb_hits} "
          f"-> post_rate {post_rate}")
    print(f"background (pooled random): {background:.3f}")
    if post_rate is None or recomb_events < 20:
        verdict = "NOT-TESTABLE"
    else:
        verdict = "SUPPORTED" if post_rate > 3 * background else "NOT-SUPPORTED"
    print(f"P11 verdict: {verdict}")

    with open("p11_results.json", "w", encoding="utf-8") as f:
        json.dump({"A": A, "B": B, "background_pooled": background,
                   "recomb_events": recomb_events, "recomb_hits": recomb_hits,
                   "post_rate": post_rate, "verdict": verdict,
                   "note": ("multiplicative operators (CROSS/SWAP/POWER-MIX) "
                            "are all constructive in this ring (rate 1.0, "
                            "low-weight spaces 1-dim); ADDITIVE-MIX is the "
                            "first genuinely non-constructive operator")},
                  f, indent=1)
    print("results -> p11_results.json")


if __name__ == "__main__":
    main()
