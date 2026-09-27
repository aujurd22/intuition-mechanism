"""P32-h: balanced novelty detection (pre-registered,
docs/RESEARCH_PLAN.md P32-h row).

Fixes the P32-g design flaw (all 20 holdouts were from classes absent
from the context, so the correct answer was always "new" and the
pure-guess baseline was 25%):

  - 40 trials, seed 3301, exactly balanced: 20 existing-family
    holdouts + 20 genuinely-new holdouts, shuffled;
  - context per trial: 3 classes x 2 instances (A, A', B, B', C, C');
  - EXISTING trial: the holdout is a THIRD instance of one of the
    context classes, with a parameter triple different from both shown
    instances (matching requires abstracting the structure, not
    comparing literals);
  - NEW trial: the holdout is an instance of one of the 5 classes not
    present in the context;
  - answer space {A, B, C, NEW}; chance 25%;
  - two subjects: the blind API judge (doubao-seed-2.1-lite, thinking
    disabled, reasoning-before-answer) and the native subject (same
    protocol as P32-f).

Design committed before any subject answers.

Run:  python p32h_design.py
"""
import json
import os

import numpy as np

from p32h_corpus import build_corpus

rng = np.random.default_rng(3301)

CLASSES = [("2", "no"), ("2", "alt"), ("3", "no"), ("3", "alt"),
           ("4", "no"), ("4", "alt"), ("5", "no"), ("5", "alt")]

corpus = build_corpus()          # {fid: {"seq": [...12], "cls": (s, sign),
                                 #  "params": (cshift, wexp, wvar)}}
by_class = {}
for fid, rec in corpus.items():
    by_class.setdefault(rec["cls"], []).append(fid)

trials = []
labels = ["existing"] * 20 + ["new"] * 20
rng.shuffle(labels)
for t in range(40):
    kind = labels[t]
    ctx_classes = [CLASSES[i] for i in
                   rng.choice(8, size=3, replace=False)]
    # pick 2 distinct instances per context class
    ctx_fams = []                  # [(label, fid), ...] A, A', B, ...
    used = {}
    labels6 = ["A", "A'", "B", "B'", "C", "C'"]
    for ci, cls in enumerate(ctx_classes):
        pool = [f for f in by_class[cls]]
        picks = list(rng.choice(pool, size=2, replace=False))
        used[cls] = {corpus[picks[0]]["params"],
                     corpus[picks[1]]["params"]}
        for li in range(2):
            ctx_fams.append((labels6[2 * ci + li], picks[li]))
    if kind == "existing":
        hcls = ctx_classes[int(rng.integers(0, 3))]
        pool = [f for f in by_class[hcls]
                if corpus[f]["params"] not in used[hcls]]
        holdout = pool[int(rng.integers(0, len(pool)))]
    else:
        others = [c for c in CLASSES if c not in ctx_classes]
        hcls = others[int(rng.integers(0, len(others)))]
        pool = by_class[hcls]
        holdout = pool[int(rng.integers(0, len(pool)))]
    trials.append({
        "trial": t + 1, "kind": kind,
        "context": {lab: fid for lab, fid in ctx_fams},
        "holdout": holdout,
        "truth": "NEW" if kind == "new"
                 else ["A", "B", "C"][ctx_classes.index(hcls)],
        "holdout_class": list(hcls),
    })

json.dump({"seed": 3301, "n": 40, "trials": trials},
          open("p32h_design.json", "w"), indent=1)
print(f"design committed: 40 trials "
      f"({sum(t['kind'] == 'existing' for t in trials)} existing / "
      f"{sum(t['kind'] == 'new' for t in trials)} new)")

# export materials WITHOUT truth
lines = []
labels6 = ["A", "A'", "B", "B'", "C", "C'"]
for t in trials:
    lines.append(f"=== Trial {t['trial']:02d} ===")
    for lab in labels6:
        seq = corpus[t["context"][lab]]["seq"]
        lines.append(f"Family {lab}: " + ", ".join(map(str, seq)))
    seq = corpus[t["holdout"]]["seq"]
    lines.append("Holdout  H: " + ", ".join(map(str, seq)))
    lines.append("")
with open("p32h_materials.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("materials -> p32h_materials.txt (no truth column)")
