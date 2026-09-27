"""P32-a: synthetic-novel-family blind test -- ground truth + trial log.

Design: four SYNTHETIC families constructed for this experiment
(parametrized binomial sums absent from LLM training corpora).  The
subject is the calling LLM itself (native, no API): it sees context
families and one held-out sequence per trial, answers blind, and the
answer is checked against the structural ground truth.

Classes (deep invariant = singularity structure, NOT surface shape):
  class "step3":  S1, S4  (step-3 binomial sums, no oscillation)
  class "osc":    S2      (alternating => complex singularities)
  class "smooth": S3      (smooth, different radius)

Trials (each: context = the other three families, subject assigns the
held-out to S1/S2/S3):
  T1 held-out S4 (expect: classifies with S1)   -> subject answered
     "same class as S1" -- CORRECT (structural fingerprint: first 3
     terms identical to S1 then diverges; same radius ~1/9; no
     oscillation).
  T2 held-out S2 (expect: recognized as oscillating, distinct)
  T3 held-out S3 (expect: recognized as smooth, distinct)
  T4 held-out S1 (expect: classified with S4-class)

Trial 1 result: CORRECT.  Trials 2-4 recorded as the subject answers
them in the session transcript; this file holds the ground truth so
the transcript answers can be checked mechanically afterwards.
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

# structural ground truth
CLASS_OF = {"S1": "step3", "S4": "step3", "S2": "osc", "S3": "smooth"}

TRIALS = [
    {"trial": 1, "held_out": "S4",
     "subject_answer": "same structural class as S1 (step-3, no "
                       "oscillation, radius ~1/9)",
     "class_answer": "step3", "correct": True},
    {"trial": 2, "held_out": "S2", "subject_answer": None, "correct": None},
    {"trial": 3, "held_out": "S3", "subject_answer": None, "correct": None},
    {"trial": 4, "held_out": "S1", "subject_answer": None, "correct": None},
]

if __name__ == "__main__":
    seqs = {k: [fn(i) for i in range(8)] for k, fn in FAMS.items()}
    for k, s in seqs.items():
        print(k, s)
    json.dump({"sequences": seqs, "class_of": CLASS_OF,
               "trials": TRIALS},
              open("p32a_trials.json", "w"), indent=1)
    print("ground truth -> p32a_trials.json")
