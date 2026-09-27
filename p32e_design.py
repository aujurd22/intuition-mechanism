"""P32-e: 480 synthetic families, 100 blind trials (pre-registered,
docs/RESEARCH_PLAN.md P32-e row, commit 24c0a2a).

10x scale-up of P32-d.  Same 8-class space ((step, sign) with step in
2..5), expanded radius/weight variants, seed 43 (independent of P32-d's
seed 42).  100 hold-out trials, open-judgment scoring.

This script generates the DESIGN (families + trials + truth committed
before subject answers) and prints the trial materials.

Run:  python p32e_design.py
"""
import json
from math import comb

import numpy as np

rng = np.random.default_rng(43)


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
    for rep in range(60):                      # 60 per class = 480
        cshift = int(rng.integers(0, 4))
        wexp = int(rng.integers(1, 3))
        wvar = int(rng.integers(0, 2))
        fid = f"G{step}{'a' if sign=='alt' else 'n'}{rep:02d}c{cshift}w{wexp}{wvar}"
        families[fid] = make_family(step, sign, wexp, cshift, wvar)
        truth[fid] = {"class": [step, sign], "step": step,
                      "sign": sign, "cshift": cshift, "wexp": wexp,
                      "wvar": wvar}

# 100 trials: 3 context families all from ONE distract class, hold-out
# from a different class (same protocol as P32-d: the truth class is
# NOT visible, so the subject must NAME the class, not match context)
trials = []
class_ids = {c: [fid for fid, tr in truth.items()
                 if tuple(tr["class"]) == c] for c in CLASSES}
for t in range(100):
    truth_cls = CLASSES[int(rng.integers(0, 8))]
    distract_cls = CLASSES[int(rng.integers(0, 8))]
    while distract_cls == truth_cls:
        distract_cls = CLASSES[int(rng.integers(0, 8))]
    holdout = class_ids[truth_cls][int(rng.integers(
        0, len(class_ids[truth_cls])))]
    ctx = list(rng.choice(class_ids[distract_cls], 3, replace=False))
    trials.append({"trial": t + 1, "holdout": holdout,
                   "context": ctx, "truth_class": truth_cls,
                   "distract_class": distract_cls})

json.dump({"families": {fid: [fn(i) for i in range(8)]
                        for fid, fn in families.items()},
           "truth": truth, "trials": trials},
          open("p32e_design.json", "w"), indent=1, default=str)
print(f"design committed: {len(families)} families, 8 classes, "
      f"100 trials (seed 43)")
for t in trials[:5]:
    print(f"  trial {t['trial']}: holdout={t['holdout']} "
          f"truth={t['truth_class']}")
print("... (95 more)")
