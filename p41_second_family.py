"""P41: second-family gate -- the full chain on the counterfactual
envelope family (pre-registered, docs/RESEARCH_PLAN.md P41 row).

The P32->P39 chain (extraction -> recognition -> novelty) ran on ONE
family (the combinatorial-support t-family).  This experiment runs it
on a structurally DIFFERENT family: the P15 counterfactual family
c_k = (A+Bk) H_s(k) z^k, s in {2,3,4,6}, where the sufficient
statistic is a CONTINUOUS 1-D residual ladder (not a discrete
support signature).

Mechanical pipeline (P39 analog, no labels in the decisions):
  extraction: per-sample generic 3-parameter log-domain envelope
              (blind_envelope; no H_s knowledge);
  statistic : level(u) = mean log-residual;
  decision  : nearest context-family level within TAU*sigma (sigma =
              pooled envelope-fit residual std, label-free), else NEW.

REGISTERED STRUCTURAL PREDICTION (positional novelty): on a 1-D
ordered ladder, a holdout from an ABSENT family is detectable as NEW
only when the absent family sits at an END of the ladder (s=2 min or
s=6 max); an interior absent family (s=3 or s=4) is sandwiched
between context levels and is structurally undetectable by ANY
interval rule.  This is the same mechanism as P36-d's finding that
models perceive the binary rational/irrational boundary but not
interior degree differences.

Verdict bands (40 trials, 20 existing / 20 new): recognition >= 90%
AND novelty >= 90% => CONFIRMED; recognition >= 90%, novelty < 70%
=> PARTIAL (noise-limited); either < 70% => NEGATIVE.  The
positional prediction is scored separately (end-novelty vs
interior-novelty).

Run:  python p41_second_family.py
"""
import json
import sys, os

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p15_envelope import make_dataset, poch_cum, blind_envelope  # noqa: E402

rng = np.random.default_rng(4101)
SIGS = (2, 3, 4, 6)

X, y, _ = make_dataset(poch_cum, seed=777)
y = np.asarray(y)
by_class = {si: [i for i in range(len(X)) if y[i] == si] for si in range(4)}

# ---- extraction: residual levels for every sample ----
levels, sigmas = [], []
for i in range(len(X)):
    u = np.log(np.abs(blind_envelope(X[i].astype(np.float64))) + 1e-300)
    levels.append(float(np.mean(u)))
    sigmas.append(float(np.std(u)))
levels = np.array(levels)
sigma_pool = float(np.mean(sigmas))

# sanity: the ladder ordering (P15: monotone in s)
print("mean level per class:",
      {si: round(float(np.mean(levels[by_class[si]])), 4) for si in range(4)})
print(f"pooled fit sigma = {sigma_pool:.4f}")

TAU = 2.0

# ---- 40 balanced trials (20 existing / 20 new), families disjoint ----
trials = []
kinds = ["existing"] * 20 + ["new"] * 20
rng.shuffle(kinds)
for t, kind in enumerate(kinds):
    ctx = list(rng.choice(range(4), size=3, replace=False))
    absent = [si for si in range(4) if si not in ctx][0]
    if kind == "existing":
        fam = ctx[int(rng.integers(0, 3))]
        pool = by_class[fam]
        hold = pool[int(rng.integers(0, len(pool)))]
        truth = fam
    else:
        pool = by_class[absent]
        hold = pool[int(rng.integers(0, len(pool)))]
        truth = "NEW"
    trials.append({"trial": t + 1, "kind": kind, "ctx": ctx,
                   "absent": absent, "hold": int(hold),
                   "truth": truth})

# ---- mechanical decisions ----
detail = []
rec_ok = rec_n = new_ok = new_n = 0
end_hits = end_n = int_hits = int_n = 0
for t in trials:
    hold = t["hold"]
    lvl = levels[hold]
    # context family levels: mean of the 2 instances closest to each other?
    # label-free and fixed: use ALL class members?  No -- context gives 2
    # instances per family by design; emulate: pick 2 random members.
    fam_levels = {}
    fam_sig = {}
    for si in t["ctx"]:
        picks = rng.choice(by_class[si], size=2, replace=False)
        fam_levels[si] = float(np.mean(levels[picks]))
        fam_sig[si] = float(np.mean([sigmas[p] for p in picks]))
    best, best_d = None, None
    for si, mu in fam_levels.items():
        d = abs(lvl - mu)
        if best_d is None or d < best_d:
            best, best_d = si, d
    ans = best if best_d <= TAU * sigma_pool else "NEW"
    hit = ans == t["truth"]
    if t["kind"] == "existing":
        rec_n += 1
        rec_ok += hit
    else:
        new_n += 1
        new_ok += hit
        positional_end = t["absent"] in (0, 3)   # s=2 min, s=6 max ends
        if positional_end:
            end_n += 1
            end_hits += hit
        else:
            int_n += 1
            int_hits += hit
    detail.append({"trial": t["trial"], "kind": t["kind"],
                   "absent": t["absent"], "truth": str(t["truth"]),
                   "ans": str(ans), "ok": bool(hit)})

print(f"\nrecognition: {rec_ok}/{rec_n}   novelty: {new_ok}/{new_n}")
print(f"positional split (NEW trials): end-absent {end_hits}/{end_n}, "
      f"interior-absent {int_hits}/{int_n}")

verdict = ("CONFIRMED" if rec_ok / max(rec_n, 1) >= .9 and new_ok / max(new_n, 1) >= .9
           else "PARTIAL" if rec_ok / max(rec_n, 1) >= .9
           else "NEGATIVE")
print(f"verdict: {verdict}")
json.dump({"levels_ladder": {str(si): float(np.mean(levels[by_class[si]]))
                             for si in range(4)},
           "sigma_pool": sigma_pool, "TAU": TAU,
           "recognition": f"{rec_ok}/{rec_n}", "novelty": f"{new_ok}/{new_n}",
           "end_absent": f"{end_hits}/{end_n}",
           "interior_absent": f"{int_hits}/{int_n}",
           "verdict": verdict, "detail": detail},
          open("p41_results.json", "w"), indent=1)
print("saved p41_results.json")
