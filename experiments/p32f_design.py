"""P32-f: 4800 families, 1000 trials (pre-registered,
docs/RESEARCH_PLAN.md P32-f row, commit 528ee37).

100x scale-up vs P32-d.  Two arms:
  arm A (500 trials): 7-term window (as before)
  arm B (500 trials): 12-term window (tests the step-5 sign-flip
        information-boundary hypothesis -- confusions should vanish)

Design committed before subject answers.  Run generates design + truth.

Run:  python p32f_design.py
"""
import json
from math import comb

import numpy as np

rng = np.random.default_rng(44)


def make_family(step, sign_mode, weight_exp, cshift, wvar):
    def f(n):
        v = 0
        for k in range(n // step + 1):
            term = comb(n, step * k)
            base = comb(step * k, k)
            term *= base ** weight_exp
            m = n - step * k
            term *= comb(2 * m, m) if m > 0 else 1
            if wvar == 1:
                term *= comb(step * k + 1, k)
            sign = (-1) ** k if sign_mode == "alt" else 1
            term *= sign * (2 ** cshift) ** k
            v += term
        return v
    return f


CLASSES = [(2, "no"), (2, "alt"), (3, "no"), (3, "alt"),
           (4, "no"), (4, "alt"), (5, "no"), (5, "alt")]

families = {}
truth = {}
for (step, sign) in CLASSES:
    for rep in range(600):                     # 600 per class = 4800
        cshift = int(rng.integers(0, 4))
        wexp = int(rng.integers(1, 3))
        wvar = int(rng.integers(0, 2))
        fid = f"H{step}{'a' if sign=='alt' else 'n'}{rep:04d}"
        families[fid] = make_family(step, sign, wexp, cshift, wvar)
        truth[fid] = {"class": [step, sign], "step": step,
                      "sign": sign}

class_ids = {c: [fid for fid, tr in truth.items()
                 if tuple(tr["class"]) == c] for c in CLASSES}
trials = []
for t in range(1000):
    arm = "A7" if t < 500 else "B12"           # window arm
    wlen = 7 if arm == "A7" else 12
    truth_cls = CLASSES[int(rng.integers(0, 8))]
    distract_cls = CLASSES[int(rng.integers(0, 8))]
    while distract_cls == truth_cls:
        distract_cls = CLASSES[int(rng.integers(0, 8))]
    holdout = class_ids[truth_cls][int(rng.integers(
        0, len(class_ids[truth_cls])))]
    ctx = list(rng.choice(class_ids[distract_cls], 3, replace=False))
    trials.append({"trial": t + 1, "arm": arm, "wlen": wlen,
                   "holdout": holdout, "context": ctx,
                   "truth_class": truth_cls,
                   "distract_class": distract_cls})

# sequence cache: 12 terms per family
seqs = {fid: [fn(i) for i in range(12)] for fid, fn in families.items()}
json.dump({"families": families, "truth": truth, "trials": trials,
           "sequences": seqs},
          open("p32f_design.json", "w"), indent=1, default=str)
print(f"design committed: {len(families)} families, 1000 trials "
      f"(500 x 7-term arm A, 500 x 12-term arm B, seed 44)")
