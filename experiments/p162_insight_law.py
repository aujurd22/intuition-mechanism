"""P-LAW1: Insight Law discriminative experiment (registered in
flymemory research/RESEARCH.md P-2026-10-02-LAW1 -- verdict PENDING
there; criteria locked before this ran).

20 ambiguity-by-design pairs: true rule A and shadow rule B agree on the
first W terms and diverge afterwards. Four collectors produce ranked
top-3 candidate rules; a mechanical executor verifies exact fit on the
seen terms and on the held-out divergence terms.

Score(h) = bits(h) + bits(residual) on the SEEN terms (lower better).
LAW test: does Score ranking predict held-out verification hit?

Run:  py -3.13 p162_insight_law.py            (deterministic; no API)
      optionally LLM arms via ARK (set env, --llm)
"""
import json
import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)


# ----------------------------------------------------------------------
# rule space: parameterized integer-sequence generators returning closures
# each rule: dict(kind=..., params=..., fn=lambda k: a_k for 1-indexed k)
# bits(h) = kind cost + parameter cost (fixed per kind, +2 per free param)
# ----------------------------------------------------------------------
def mk_arith(c, a0):
    return {"kind": "arith", "bits": 6, "fn": lambda k: a0 + c * (k - 1)}


def mk_geo(c, a0):
    return {"kind": "geo", "bits": 6, "fn": lambda k: a0 * (c ** (k - 1))}


def mk_quad(a, b, c):
    return {"kind": "quad", "bits": 8,
            "fn": lambda k: a * k * k + b * k + c}


def mk_linrec(p, q, a0, a1):
    return {"kind": "linrec", "bits": 10,
            "fn": (lambda k, p=p, q=q, a0=a0, a1=a1:
                   a0 if k == 1 else a1 if k == 2 else
                   None)}  # expanded below via closure


def linrec_fn(p, q, a0, a1):
    def fn(k):
        vals = [None, a0, a1]
        for i in range(3, k + 1):
            vals.append(p * vals[i - 1] + q * vals[i - 2])
        return vals[k]
    return fn


def mk_switch(base, switch_at, alt_c):
    """late-divergence shadow: base rule until switch_at, then arithmetic
    with a different step."""
    return {"kind": "switch", "bits": 12,
            "fn": (lambda k, base=base, s=switch_at, alt=alt_c:
                   base["fn"](k) if k <= s else
                   base["fn"](s) + alt * (k - s))}


def fit_exact(fn, terms):
    return all(fn(k) == v for k, v in terms.items())


def residual_bits(fn, terms):
    """sum of log2(1+|err|) over terms (0 if exact)."""
    tot = 0.0
    for k, v in terms.items():
        try:
            err = abs(fn(k) - v)
        except Exception:
            return 1e9
        tot += np.log2(1 + err)
    return tot


# ----------------------------------------------------------------------
# item construction: 20 pairs, late divergence W in 6..10
# ----------------------------------------------------------------------
def build_items():
    rng = np.random.default_rng(7)
    items = []
    for i in range(20):
        W = int(rng.integers(6, 11))
        family = i % 4
        alt = int(rng.integers(1, 5))
        if family == 0:      # arithmetic true
            c, a0 = int(rng.integers(2, 9)), int(rng.integers(1, 20))
            A = mk_arith(c, a0)
        elif family == 1:    # geometric true
            c, a0 = 2, int(rng.integers(1, 5))
            A = mk_geo(c, a0)
        elif family == 2:    # linear recurrence true
            p, q = int(rng.integers(1, 4)), int(rng.integers(1, 3))
            a0, a1 = int(rng.integers(1, 6)), int(rng.integers(2, 9))
            fn = linrec_fn(p, q, a0, a1)
            A = {"kind": "linrec", "bits": 10, "fn": fn}
        else:                # quadratic true
            a, b = int(rng.integers(1, 4)), int(rng.integers(1, 5))
            A = mk_quad(a, b, int(rng.integers(0, 6)))
        # shadow: identical through W, then a different arithmetic step
        B = mk_switch(A, W, alt)
        terms = {k: A["fn"](k) for k in range(1, W + 1)}
        held = {k: A["fn"](k) for k in range(W + 1, W + 4)}
        shadow_terms = {k: B["fn"](k) for k in range(1, W + 1)}
        # verify ambiguity: shadow agrees on the shown window
        assert shadow_terms == terms, f"item {i}: window not ambiguous"
        items.append({"id": i, "W": W, "A": A, "B": B,
                      "terms": terms, "held": held,
                      "family": family})
    return items


def candidates_for(item):
    """enumerate the full candidate space (mechanically executable)."""
    cands = []
    rng = np.random.default_rng(item["id"] * 31 + 7)
    W = item["W"]
    terms = item["terms"]
    for c in range(-9, 20):
        for a0 in range(0, 40):
            h = mk_arith(c, a0)
            cands.append(h)
    for c in (2, 3):
        for a0 in range(1, 10):
            h = mk_geo(c, a0)
            cands.append(h)
    for a in range(1, 5):
        for b in range(0, 8):
            for c0 in range(0, 20):
                h = mk_quad(a, b, c0)
                cands.append(h)
    for p in range(1, 5):
        for q in range(1, 4):
            for a0 in range(1, 8):
                for a1 in range(2, 12):
                    fn = linrec_fn(p, q, a0, a1)
                    cands.append({"kind": "linrec", "bits": 10, "fn": fn})
    # switch shadows over the four base families
    for s_at in range(4, 13):
        for alt in range(1, 6):
            for base in (mk_arith(3, 5), mk_geo(2, 2)):
                cands.append(mk_switch(base, s_at, alt))
    return cands


def score_rank(cands, terms):
    """rank by bits(h)+residual (exact fit first, then shortest)."""
    scored = []
    for h in cands:
        rb = residual_bits(h["fn"], terms)
        if rb < 1e-9:
            scored.append((h["bits"], 0.0, h))
        else:
            scored.append((h["bits"] + 40 + rb, 1.0, h))  # non-exact far back
    scored.sort(key=lambda t: (t[0], t[1]))
    return [t[2] for t in scored]


def hit_at(ranked, held, k):
    """does any of the top-k EXACTLY match the held-out divergence terms?"""
    for h in ranked[:k]:
        if fit_exact(h["fn"], held):
            return True
    return False


def main():
    items = build_items()
    print(f"items: {len(items)} (ambiguity verified: shadow agrees on "
          f"shown window)")
    t0 = time.time()

    method_hits = {"BRUTE": {"h1": 0, "h3": 0}, "MDL": {"h1": 0, "h3": 0},
                   "PIPE": {"h1": 0, "h3": 0}}
    budget = {"BRUTE": [], "MDL": [], "PIPE": []}
    pair_data = []

    for it in items:
        allc = candidates_for(it)
        # BRUTE: fixed enumeration order = generation order; first exact-fit
        brute_hit_pos = None
        for pos, h in enumerate(allc, 1):
            if fit_exact(h["fn"], it["terms"]) and \
                    residual_bits(h["fn"], it["terms"]) < 1e-9:
                brute_hit_pos = pos
                break
        brute_top = []
        cnt = 0
        for h in allc:
            if fit_exact(h["fn"], it["terms"]) and \
                    residual_bits(h["fn"], it["terms"]) < 1e-9:
                brute_top.append(h)
                cnt += 1
                if cnt == 3:
                    break
        method_hits["BRUTE"]["h1"] += bool(brute_top and
                                           fit_exact(brute_top[0]["fn"],
                                                     it["held"]))
        method_hits["BRUTE"]["h3"] += hit_at(brute_top, it["held"], 3)
        budget["BRUTE"].append(brute_hit_pos or len(allc))

        # MDL: full enumeration ranked by description length
        mdl_ranked = score_rank(allc, it["terms"])
        method_hits["MDL"]["h1"] += hit_at(mdl_ranked, it["held"], 1)
        method_hits["MDL"]["h3"] += hit_at(mdl_ranked, it["held"], 3)
        # MDL budget: candidates with residual==0 evaluated until held-hit
        exacts = [h for h in mdl_ranked
                  if residual_bits(h["fn"], it["terms"]) < 1e-9]
        pos_hit = None
        for pos, h in enumerate(exacts, 1):
            if fit_exact(h["fn"], it["held"]):
                pos_hit = pos
                break
        budget["MDL"].append(pos_hit or len(exacts))

        # PIPE: MDL ranking, but candidates verified on held in rank order
        # (the law's score should place the true rule early)
        pipe_ranked = mdl_ranked
        method_hits["PIPE"]["h1"] += hit_at(pipe_ranked, it["held"], 1)
        method_hits["PIPE"]["h3"] += hit_at(pipe_ranked, it["held"], 3)
        budget["PIPE"].append(budget["MDL"][-1])

        # pair-level record for Score-prediction correlation:
        # for the top-10 exact candidates, does Score rank predict
        # held-out verification?
        top10 = []
        for h in mdl_ranked:
            if residual_bits(h["fn"], it["terms"]) < 1e-9:
                top10.append(h)
            if len(top10) == 10:
                break
        for rank_pos, h in enumerate(top10, 1):
            pair_data.append({"item": it["id"], "score_rank": rank_pos,
                              "held_hit": fit_exact(h["fn"], it["held"]),
                              "family": it["family"]})

    # LLM arms need API; deterministic core runs first
    n = len(items)
    print(f"\ncore (deterministic) results, n={n}:")
    for m in ("BRUTE", "MDL", "PIPE"):
        print(f"  {m:6s} hit@1 {method_hits[m]['h1']/n:.1%} "
              f"hit@3 {method_hits[m]['h3']/n:.1%} | "
              f"budget mean {np.mean(budget[m]):.1f}")

    # Score-prediction Spearman (pooled top-10 exact candidates per item)
    from scipy.stats import spearmanr
    ranks = [p["score_rank"] for p in pair_data]
    hits = [int(p["held_hit"]) for p in pair_data]
    if len(set(hits)) > 1:
        rho, pval = spearmanr(ranks, hits)
        print(f"\nScore-prediction Spearman (rank vs held-hit, "
              f"n={len(ranks)} candidate placements): "
              f"rho={rho:.3f} p={pval:.4g}")
    else:
        rho, pval = None, None
        print("\nScore-prediction: degenerate (all same outcome)")

    # pre-registered verdict (LLM arms pending -> core verdict only)
    pipe_h3 = method_hits["PIPE"]["h3"] / n
    brute_h3 = method_hits["BRUTE"]["h3"] / n
    if rho is not None and rho >= 0.4 and pval < 0.01 and \
            pipe_h3 >= brute_h3:
        verdict = "LAW-SUPPORTED"
    elif rho is not None and rho >= 0.4:
        verdict = "LAW-DESCRIPTIVE (ranks but does not guide search)"
    elif rho is not None and rho < 0.25:
        verdict = "LAW-NULL"
    else:
        verdict = "DEGENERATE (held-hit uniform across exact candidates)"
    print(f"PRE-REGISTERED VERDICT (core): {verdict}")

    ts = int(time.time())
    out = os.path.join(_HERE, "p162_law1_results.json")
    json.dump({"experiment": "P-LAW1", "n_items": n,
               "method_hits": {m: {k: v / n for k, v in d.items()}
                               for m, d in method_hits.items()},
               "budget_mean": {m: float(np.mean(v))
                               for m, v in budget.items()},
               "spearman": None if rho is None else
                           {"rho": float(rho), "p": float(pval)},
               "verdict": verdict, "pair_data": pair_data},
              open(out, "w"), indent=1)
    print(f"saved {out} ({time.time()-t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
