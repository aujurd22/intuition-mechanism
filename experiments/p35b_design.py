"""P35-b: blind rule-induction by subjects (pre-registered,
docs/RESEARCH_PLAN.md P35-b row).

Question: P35-a showed the sufficient code is discoverable by MDL
search.  Can a LANGUAGE MODEL discover it from a handful of labeled
examples -- and does its induced procedure generalize mechanically?

Protocol:
  - train: 24 sequences, 3 per class (seed 4401), labeled G1..G8 with
    a SHUFFLED name mapping (names carry no information);
  - the subject sees only raw sequences + labels and must output a
    precise decision procedure (pseudo-code over term values,
    constants, sign checks);
  - the procedure is then IMPLEMENTED AS WRITTEN and executed on 400
    held-out families (50 per class); scoring is mechanical;
  - subjects: a fresh ZCode subagent (no session context) and the
    blind API judge (doubao, thinking disabled).

Run:  python p35b_design.py     (exports train/test materials)
"""
import json
import sys

import numpy as np

from p32h_corpus import build_corpus

rng = np.random.default_rng(4401)
corpus = build_corpus()
CLASSES = [("2", "no"), ("2", "alt"), ("3", "no"), ("3", "alt"),
           ("4", "no"), ("4", "alt"), ("5", "no"), ("5", "alt")]
by_class = {c: [f for f, r in corpus.items() if r["cls"] == c]
            for c in CLASSES}

names = list("G12345678")
rng.shuffle(names)                      # name mapping carries no info
train = []
for c, g in zip(CLASSES, names):
    picks = rng.choice(by_class[c], size=3, replace=False)
    for f in picks:
        train.append((g, f))
rng.shuffle(train)

test = []
for c in CLASSES:
    pool = [f for f in by_class[c] if f not in
            {f for _, f in train}]
    picks = rng.choice(pool, size=50, replace=False)
    test += [(c, f) for f in picks]

with open("p35b_train.txt", "w", encoding="utf-8") as fh:
    for g, f in train:
        fh.write(f"{g}: " + ", ".join(map(str, corpus[f]["seq"][:12])) + "\n")
json.dump({"train": train,
           "test": [{"cls": list(c), "fid": f} for c, f in test]},
          open("p35b_design.json", "w"), indent=1)
print(f"train: {len(train)} labeled sequences -> p35b_train.txt")
print(f"test: {len(test)} held-out families")
