"""P32-a: synthetic-novel-family blind test (pre-registered,
docs/RESEARCH_PLAN.md P32-a row).

Design (fixes P32's invalid held-out problem): four SYNTHETIC families,
constructed for this experiment (parametrized binomial sums absent from
training corpora).  The subject (calling LLM, native) sees THREE
context families and ONE held-out family's first 8 terms, and must
assign the held-out to its structure class.

The four families differ in SINGULARITY STRUCTURE (the deep invariant,
not surface coefficients):
  S1: r~9, step-3 binomial sum, no oscillation
  S2: alternating signs (complex singularities), r~9
  S3: smooth poly-times-exp, r~6, no oscillation
  S4: r~9 with a different step-3 shape (near-S1 but distinct)

Classes for the test: {S1,S4} same class "step-3 no-osc"; {S2} =
"oscillating"; {S3} = "smooth".  The subject must group S1 with S4 --
the structure-level match, not the surface match.

Run: python prints the four sequences; the LLM-subject (this session's
model) answers in the transcript; ground truth recorded here.
"""
from math import comb
import json


def S1(n):
    v = 0
    for k in range(n // 3 + 1):
        v += comb(n, 3 * k) * comb(3 * k, k) ** 2 * comb(2 * n - 6 * k,
                                                         n - 3 * k) * 2 ** k
    return v


def S2(n):
    v = 0
    for k in range(n // 2 + 1):
        v += (-1) ** k * comb(n, 2 * k) * comb(2 * k, k) ** 3
    return v


def S3(n):
    v = 0
    for k in range(n + 1):
        v += comb(n, k) ** 2 * comb(3 * k, k)
    return v


def S4(n):
    v = 0
    for k in range(n // 3 + 1):
        v += comb(n, 3 * k) * comb(3 * k, k) * comb(2 * n - 6 * k,
                                                    n - 3 * k) * 3 ** k
    return v


FAMS = {"S1": S1, "S2": S2, "S3": S3, "S4": S4}

if __name__ == "__main__":
    seqs = {k: [fn(i) for i in range(8)] for k, fn in FAMS.items()}
    for k, s in seqs.items():
        print(k, s)
    json.dump(seqs, open("p32a_families.json", "w"))
    print("ground truth: S1 and S4 are the SAME structural class "
          "(step-3, no oscillation); S2 oscillating; S3 smooth-different")
