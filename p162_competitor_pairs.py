"""P162: Insight Boundary Benchmark v1 — Experiment 1 (the P159 design).

For each seed rule A, construct a genuine competitor B_N = A(n) + C*prod_{i=1..N}(n-i)
— B matches A EXACTLY on the N-term discovery window, diverges after.
Judge sees N terms, must: (1) state a rule, (2) predict 4 continuation
terms, (3) self-assess ambiguity ("is more than one simple rule
consistent with the data?").

Scored dimensions (the BOUNDARY benchmark):
  branch_choice   A (minimum-description) vs B (constructed) vs other
  ambiguity_awareness — did the judge DECLARE that alternative rules fit?
    (the Insight-vs-Hallucination extension: on an UNDERDETERMINED
     window, claiming uniqueness is overconfidence — the P152 boundary
     applied to the meta level)
  continuation    vs both branches' continuations
"""
import json
import numpy as np
import random

SEED_RULES = [
    {"name": "doubling", "A": lambda n: 2 ** n,
     "ruleA": "a_n = 2^n"},
    {"name": "squares", "A": lambda n: n * n, "ruleA": "a_n = n^2"},
    {"name": "fibonacci", "A": None, "ruleA": "a_n = a_(n-1) + a_(n-2), a1=a2=1"},
    {"name": "arithmetic3", "A": lambda n: 3 * n + 2, "ruleA": "a_n = 3n+2"},
    {"name": "triangular", "A": lambda n: n * (n + 1) // 2,
     "ruleA": "a_n = n(n+1)/2"},
]

N_WINDOW = 8
C = 1


def terms_A(rule, n_list):
    if rule["name"] == "fibonacci":
        seq = [1, 1]
        while len(seq) < max(n_list) + 1:
            seq.append(seq[-1] + seq[-2])
        return [seq[n - 1] for n in n_list]
    return [rule["A"](n) for n in n_list]


def build_competitors():
    """B_N = A(n) + prod_{i=1..N}(n-i), C=1 — B == A on n=1..N."""
    out = []
    for rule in SEED_RULES:
        n_list = list(range(1, N_WINDOW + 1))
        a_vals = terms_A(rule, n_list)
        cont_n = list(range(N_WINDOW + 1, N_WINDOW + 5))

        def B(n, r=rule):
            base = terms_A(r, [n])[0]
            prod = 1
            for i in range(1, N_WINDOW + 1):
                prod *= (n - i)
            return base + prod

        b_disc = terms_A(rule, n_list)          # B == A on the window
        b_cont = [B(n) for n in cont_n]
        out.append({"rule": rule, "a_window": a_vals,
                    "a_cont": terms_A(rule, cont_n), "b_cont": b_cont,
                    "cont_n": cont_n})
    return out


if __name__ == "__main__":
    comps = build_competitors()
    for c in comps:
        print(f"{c['rule']['name']:>12}: window={c['a_window']}")
        print(f"{'':>14} A+4={c['a_cont']}  B+4={c['b_cont']}")
    json.dump([{**{k: v for k, v in c.items() if k != "rule"},
                "rule_name": c["rule"]["name"], "ruleA": c["rule"]["ruleA"]}
               for c in comps],
              open("p162_competitor_pairs.json", "w"), indent=1)
