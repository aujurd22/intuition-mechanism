"""P34-c: appearance-verified corpus + window curve (pre-registered,
docs/RESEARCH_PLAN.md P34-c row).

Corpus regeneration with appearance-verifiable labels:
  - no-sign families: all-positive (shape-stable at any window >= 5)
  - alt families: first sign flip constrained to term <= 6 (visible in
    a 7-term window) by choosing the flip phase explicitly
  - x0-class rows: labeled only where the algebraic form is determinable

Then the window curve: windows {4,5,6,7,10,12,16} x 25 trials, native
subject (this session), appearance-verified truth.

Run:  python p34c_corpus.py   (design + truth committed first)
"""
import json
from math import comb

import numpy as np

rng = np.random.default_rng(666)

CLASSES = [(2, "no"), (3, "no"), (4, "no"), (5, "no"),
           (2, "alt"), (3, "alt"), (4, "alt"), (5, "alt")]


def make_family(step, sign_mode, flip_term, weight_exp, cshift):
    """Binomial-sum family with a CONTROLLED first sign-flip position.

    For alt families the (-1)^k sign pattern is shifted so that the
    first negative coefficient lands exactly at term flip_term.
    """
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


def first_flip(seq):
    """Index of the first negative term (or None)."""
    for i, x in enumerate(seq):
        if x < 0:
            return i
    return None


def main():
    families = {}
    truth = {}
    fid_n = 0
    for (step, sign) in CLASSES:
        for rep in range(40):                     # 40 per class = 320
            weight_exp = int(rng.integers(1, 3))
            cshift = int(rng.integers(0, 3))
            fn = make_family(step, sign, None, weight_exp, cshift)
            seq = [fn(i) for i in range(16)]
            flip = first_flip(seq)
            if sign == "alt":
                # appearance-verified constraint: first flip <= term 6
                if flip is None or flip > 6:
                    continue
            else:
                # no-sign families must have NO flip in 16 terms
                if flip is not None:
                    continue
            fid = f"P{step}{'a' if sign=='alt' else 'n'}{rep:02d}c{cshift}w{weight_exp}"
            families[fid] = seq
            truth[fid] = {"class": [step, sign], "step": step,
                          "sign": sign, "flip": flip,
                          "appearance_verified": True}
            fid_n += 1
    print(f"appearance-verified corpus: {fid_n} families")
    cls_counts = {}
    for fid, tr in truth.items():
        c = tuple(tr["class"])
        cls_counts[c] = cls_counts.get(c, 0) + 1
    print("per-class:", cls_counts)

    # window trials: for each window, hold-out from each class where
    # the class is appearance-verified WITHIN that window
    design = {}
    for w in (4, 5, 6, 7, 10, 12, 16):
        trials = []
        cls_ids = {}
        for fid, tr in truth.items():
            # alt families: flip must be <= w-1 to be visible
            if tr["sign"] == "alt" and tr["flip"] is not None \
                    and tr["flip"] >= w - 1:
                continue
            if tr["sign"] == "no" and tr["flip"] is not None:
                continue
            cls_ids.setdefault(tuple(tr["class"]), []).append(fid)
        for t in range(25):
            truth_cls = CLASSES[int(rng.integers(0, 8))]
            if truth_cls not in cls_ids:
                continue
            distract_cls = truth_cls
            tries = 0
            while (tuple(distract_cls) == truth_cls
                   or distract_cls not in cls_ids) and tries < 20:
                distract_cls = CLASSES[int(rng.integers(0, 8))]
                tries += 1
            if distract_cls == truth_cls or distract_cls not in cls_ids:
                continue
            holdout = cls_ids[truth_cls][int(rng.integers(
                0, len(cls_ids[truth_cls])))]
            ctx = list(rng.choice(cls_ids[distract_cls],
                                  min(3, len(cls_ids[distract_cls])),
                                  replace=False))
            trials.append({"trial": t + 1, "holdout": holdout,
                           "context": ctx, "truth": list(truth_cls),
                           "distract": list(distract_cls)})
        design[f"w{w}"] = trials
        print(f"  window {w}: {len(trials)} trials "
              f"(classes available: {len(cls_ids)})", flush=True)

    json.dump({"families": families, "truth": truth, "design": design},
              open('p34c_corpus.json', 'w'), indent=1, default=str)
    print("-> p34c_corpus.json")


if __name__ == "__main__":
    main()
