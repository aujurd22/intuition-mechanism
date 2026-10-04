"""P34-d: window extension (W17-20) + structural decomposition of the
window curve.

Pre-registered after the user asked to extend the window curve to
17/18/19/20 terms.  Two subject conditions on the same 100 trials:
  subject A: holistic pattern matching (method-matched to the P32-f /
             P34-c native curve; committed per-window BEFORE the
             structural rule below was derived -- the rule crystallized
             while answering W20, so W20 is B-only);
  subject B: the early-term support-pattern rule (tree()) -- 6 lines,
             mechanizable, uses only t2, t3, t4 and flip-presence.

THE RULE (structural, generator-exact):
  the k=1 term carries comb(n, step), which vanishes for n < step, so
    t2 != 6  -> step 2 (sign from t2 >< 6)
    t2 = 6, t3 != 20 -> step 3 (sign from t3 >< 20)
    t2 = 6, t3 = 20, t4 != 70 -> step 4 (sign from t4 >< 70)
    t2 = 6, t3 = 20, t4 = 70 -> step 5 (sign from flip-presence)

Census over ALL 4800 families (seed-44 replay): the rule is perfect
from W = 12 onward (99.1% at W10, 96.8% at W8, 87.5% at W5; all misses
at short W are (5,alt) families whose first flip has not surfaced yet).

Result: B scores 100/100 on the new trials; A scores 47/75 (63%).
The P34-c non-monotonic curve therefore CANNOT be an information
phenomenon -- information is ~total from W10-W12 on.  It measures cue
extraction, not information availability.

Run:  python p34d_tree_census.py
"""
import json
from math import comb

import numpy as np


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


def replay_corpus():
    """Regenerate the seed-44 4800-family corpus (verified: stored
    12-term prefixes match bit-for-bit)."""
    rng = np.random.default_rng(44)
    fams = {}
    for (step, sign) in CLASSES:
        for rep in range(600):
            cshift = int(rng.integers(0, 4))
            wexp = int(rng.integers(1, 3))
            wvar = int(rng.integers(0, 2))
            fid = f"H{step}{'a' if sign == 'alt' else 'n'}{rep:04d}"
            fams[fid] = (make_family(step, sign, wexp, cshift, wvar),
                         (str(step), sign))
    return fams


def tree(seq):
    t2, t3, t4 = seq[2], seq[3], seq[4]
    flips = any((seq[i] > 0) != (seq[i + 1] > 0)
                for i in range(len(seq) - 1))
    if t2 > 6:
        return ("2", "no")
    if t2 < 6:
        return ("2", "alt")
    if t3 > 20:
        return ("3", "no")
    if t3 < 20:
        return ("3", "alt")
    if t4 > 70:
        return ("4", "no")
    if t4 < 70:
        return ("4", "alt")
    return ("5", "alt") if flips else ("5", "no")


def census(fams):
    print("census over all 4800 families:")
    for W in (5, 6, 8, 10, 12, 16, 20):
        ok = sum(tree([f(n) for n in range(W)]) == tr
                 for f, tr in fams.values())
        print(f"  W={W}: {ok}/4800 ({100 * ok / 4800:.1f}%)")


def grade_new_trials(fams):
    design = json.load(open("p34c_ext_windows.json"))
    results = json.load(open("p34c_ext_results.json"))
    totA = totB = nA = nB = 0
    for w in (17, 18, 19, 20):
        r = results[f"w{w}"]
        totB += r["B_correct"]
        nB += r["n"]
        if r["A_correct"] is not None:
            totA += r["A_correct"]
            nA += r["n"]
        # re-verify subject B mechanically from the sequences
        for t, d in zip(design[f"w{w}"], r["detail"]):
            seq = fams[t["holdout"]][0]
            assert tree([seq(n) for n in range(w)]) == \
                tuple(d["truth"]), (w, t["trial"])
    print(f"new trials: A {totA}/{nA} ({100 * totA / nA:.0f}%) | "
          f"B {totB}/{nB} ({100 * totB / nB:.0f}%) -- B re-verified")


if __name__ == "__main__":
    fams = replay_corpus()
    d32 = json.load(open("p32f_design.json"))["sequences"]
    bad = [fid for fid in list(d32)[:50]
           if [fams[fid][0](n) for n in range(12)] != d32[fid]]
    assert not bad, f"replay mismatch: {bad[:3]}"
    print("replay verified against stored prefixes (50/50)")
    census(fams)
    grade_new_trials(fams)
