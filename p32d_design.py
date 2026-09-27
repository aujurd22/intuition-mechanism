"""P32-d: 50 synthetic families, 10 blind hold-out trials
(pre-registered, docs/RESEARCH_PLAN.md P32-d row, commit 19d181a).

Parametrized generator (ground truth = construction parameters):
  class = (step k, sign mode)  -- 4 classes x structural variants
  step k in {2, 3, 4, 5}
  sign mode: nosign / alternating (for step even: alternating maps to
             the same class family; classes are (k, sign) pairs)
  radius: the 2^c weight factor shifts the singularity
  coefficient-weight variants: comb(3k,k) vs comb(3k,k)^2 etc.

Class space (8 classes, 2 classes shown per trial as context, subject
assigns hold-out to one of the 8): chance = 1/8 = 0.125.

Truth committed here BEFORE the subject (this session's LLM) answers in
the transcript.  Scoring mechanical.
"""
import json
from math import comb

import numpy as np

rng = np.random.default_rng(42)   # fixed seed: truth reproducible


def make_family(step, sign_mode, weight_exp, cshift):
    """Returns f(n): a binomial sum with the given structural params."""
    def f(n):
        v = 0
        for k in range(n // step + 1):
            term = comb(n, step * k)
            base = comb(step * k, k)
            term *= base ** weight_exp
            m = n - step * k
            term *= comb(2 * m, m) if m > 0 else 1
            sign = (-1) ** k if sign_mode == "alt" else 1
            term *= sign * (2 ** cshift) ** k
            v += term
        return v
    return f


# 8 classes: (step, sign) pairs over steps 2..5
CLASSES = [(2, "no"), (2, "alt"), (3, "no"), (3, "alt"),
           (4, "no"), (4, "alt"), (5, "no"), (5, "alt")]

families = {}
truth = {}
for i, (step, sign) in enumerate(CLASSES):
    for rep in range(6):                      # 6 families per class = 48
        cshift = int(rng.integers(0, 3))       # radius variation
        wexp = int(rng.integers(1, 3))         # weight exponent 1 or 2
        fid = f"F{i:02d}r{rep}"
        families[fid] = make_family(step, sign, wexp, cshift)
        truth[fid] = {"class": (step, sign), "step": step,
                      "sign": sign, "cshift": cshift, "wexp": wexp}

# 10 trials: pick 5 context families from one class + 1 hold-out from
# a different class; subject assigns hold-out to the correct class
trials = []
for t in range(10):
    cls_correct = CLASSES[int(rng.integers(0, 8))]
    cls_distract = CLASSES[int(rng.integers(0, 8))]
    while cls_distract == cls_correct:
        cls_distract = CLASSES[int(rng.integers(0, 8))]
    ids_correct = [fid for fid, tr in truth.items()
                   if tr["class"] == cls_correct]
    ids_distract = [fid for fid, tr in truth.items()
                    if tr["class"] == cls_distract]
    holdout = ids_correct[int(rng.integers(0, len(ids_correct)))]
    ctx = list(rng.choice(ids_distract, 3, replace=False))
    trials.append({"trial": t + 1, "holdout": holdout,
                   "context": ctx,
                   "truth_class": cls_correct,
                   "distract_class": cls_distract})

json.dump({"families": {fid: [fn(i) for i in range(8)]
                        for fid, fn in families.items()},
           "truth": truth, "trials": trials},
          open("p32d_design.json", "w"), indent=1, default=str)
print("design committed: 48 families, 8 classes, 10 trials")
print("truth classes (step, sign):", CLASSES)
for t in trials:
    print(f"  trial {t['trial']}: holdout={t['holdout']} "
          f"truth={t['truth_class']} distract={t['distract_class']}")
