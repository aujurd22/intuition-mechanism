"""P154 Experiment 2: counterexample pressure — does the model seek the
STRONGEST explanation or any consistent one?

Design: 8 sequence families with mechanically-generatable true rules.
Discovery: first 8 terms.  Model must (a) state the rule, (b) predict
terms 9-12.  Mechanical scoring:
  strong_acc     predicted terms match the TRUE rule continuation
  overfit_ratio  |pred - polyfit_continuation| vs |pred - true|:
                 predictions CLOSER to the degree-7 polynomial extrapolation
                 (which fits the 8 terms perfectly and diverges after) than
                 to the truth = captured by the overfit attractor
  weak_capture   predictions consistent with the WEAKEST simple rule
                 (e.g. 'all even' / 'all odd') but not the true rule
Trap family included: odd numbers (9,15,21...) — the classic '1,3,5,7 =>
all prime' hallucination shape is probed with a membership question.
"""
import json
import math

FAMILIES = [
    {"name": "doubling", "rule": "a_n = 2^n",
     "gen": lambda n: 2 ** n,
     "start": 1, "weak": "all powers grow by doubling / all even"},
    {"name": "fibonacci", "rule": "a_n = a_(n-1) + a_(n-2), a_1=a_2=1",
     "gen": None, "start": 1, "weak": "increasing / all positive"},
    {"name": "squares", "rule": "a_n = n^2",
     "gen": lambda n: n * n, "start": 1, "weak": "increasing, differences odd"},
    {"name": "triangular", "rule": "a_n = n(n+1)/2",
     "gen": lambda n: n * (n + 1) // 2, "start": 1, "weak": "increasing"},
    {"name": "arithmetic3", "rule": "a_n = 3n + 2",
     "gen": lambda n: 3 * n + 2, "start": 1, "weak": "all ≡ 2 mod 3"},
    {"name": "alt_geometric", "rule": "a_n = (-2)^n",
     "gen": lambda n: (-2) ** n, "start": 1, "weak": "magnitude doubles"},
    {"name": "cubes", "rule": "a_n = n^3",
     "gen": lambda n: n ** 3, "start": 1, "weak": "grows fast, odd/even mix"},
    {"name": "odd_trap", "rule": "a_n = 2n - 1 (odd numbers)",
     "gen": lambda n: 2 * n - 1, "start": 1, "weak": "all odd",
     "membership_trap": {"q": 9, "true": True,
                         "wrong_rule": "all primes",
                         "wrong_answer": False}},
]


def terms(fam, start, count):
    if fam["name"] == "fibonacci":
        out = [1, 1]
        while len(out) < start + count:
            out.append(out[-1] + out[-2])
        return out[start - 1:start - 1 + count]
    return [fam["gen"](n) for n in range(start, start + count)]


def polyfit_continuation(terms, count):
    """Degree-(len-1) polynomial through all discovery terms, extrapolated:
    the canonical OVERFIT continuation."""
    import numpy as np
    xs = np.arange(1, len(terms) + 1)
    coeffs = np.polyfit(xs, terms, len(terms) - 1)
    xs2 = np.arange(len(terms) + 1, len(terms) + 1 + count)
    return [int(round(v)) for v in np.polyval(coeffs, xs2)]


def build_all():
    out = []
    for fam in FAMILIES:
        disc = terms(fam, fam["start"], 8)
        true_cont = terms(fam, fam["start"] + 8, 4)
        overfit = polyfit_continuation(disc, 4)
        out.append({"name": fam["name"], "discovery": disc,
                    "true_continuation": true_cont,
                    "overfit_continuation": overfit,
                    "rule": fam["rule"], "weak": fam["weak"],
                    "membership_trap": fam.get("membership_trap")})
    return out


if __name__ == "__main__":
    fams = build_all()
    for f in fams:
        print(f["name"], "disc:", f["discovery"], "true+4:", f["true_continuation"],
              "polyfit+4:", f["overfit_continuation"])
    json.dump(fams, open("p154_sequence_families.json", "w"), indent=1)
