"""P32-b: multi-family expansion (pre-registered,
docs/RESEARCH_PLAN.md P32-b row, commit f50a666).

Six NEW synthetic families (novel parametrized binomial sums), spanning
step sizes 2/3/4, with and without sign alternation, radii 1/5..1/12.
Ground truth (class by singularity structure) fixed BY CONSTRUCTION
before the subject answers:

  M1: step-3, no oscillation, r ~ 1/9     (class: step3)
  M2: step-2 alternating, r ~ 1/6         (class: osc)
  M3: step-4, no oscillation, r ~ 1/12    (class: step4)
  M4: smooth, no step structure, r ~ 1/7  (class: smooth)
  M5: step-2, no oscillation, r ~ 1/4     (class: step2)
  M6: step-3 alternating, r ~ 1/10        (class: osc-step3)

The subject sees all six 8-term sequences and must assign each to its
singularity class.  Scored mechanically against this file's ground
truth.

Run:  python p32b_families.py   (prints sequences + writes truth JSON)
"""
from math import comb
import json


def M1(n):
    v = 0
    for k in range(n // 3 + 1):
        v += comb(n, 3 * k) * comb(3 * k, k) ** 2 * comb(2 * n - 6 * k,
                                                         n - 3 * k) * 2 ** k
    return v


def M2(n):
    v = 0
    for k in range(n // 2 + 1):
        v += (-1) ** k * comb(n, 2 * k) * comb(2 * k, k) ** 2 * \
            comb(2 * n - 4 * k, n - 2 * k) * 3 ** k
    return v


def M3(n):
    v = 0
    for k in range(n // 4 + 1):
        v += comb(n, 4 * k) * comb(4 * k, 2 * k) * comb(2 * k, k) * \
            comb(3 * n - 8 * k, n - 4 * k)
    return v


def M4(n):
    v = 0
    for k in range(n + 1):
        v += comb(n, k) ** 2 * comb(2 * k, k) * comb(n + k, k)
    return v


def M5(n):
    v = 0
    for k in range(n // 2 + 1):
        v += comb(n, 2 * k) * comb(2 * k, k) * comb(2 * n - 4 * k,
                                                    n - 2 * k) * 2 ** (n - k)
    return v


def M6(n):
    v = 0
    for k in range(n // 3 + 1):
        v += (-1) ** k * comb(n, 3 * k) * comb(3 * k, k) ** 3 * \
            comb(2 * n - 6 * k, n - 3 * k)
    return v


FAMS = {"M1": M1, "M2": M2, "M3": M3, "M4": M4, "M5": M5, "M6": M6}
CLASS_OF = {"M1": "step3-nosign", "M2": "osc-step2", "M3": "step4-nosign",
            "M4": "smooth", "M5": "step2-nosign", "M6": "osc-step3"}

if __name__ == "__main__":
    seqs = {}
    for k, fn in FAMS.items():
        seqs[k] = [fn(i) for i in range(8)]
        print(k, CLASS_OF[k], seqs[k])
    json.dump({"sequences": seqs, "class_of": CLASS_OF},
              open("p32b_families.json", "w"), indent=1)
    print("truth -> p32b_families.json")
