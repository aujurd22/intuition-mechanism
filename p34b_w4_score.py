"""P34-b W4 native-subject scoring: map the subject's structural labels
(cluster-A..F as described in the session transcript) to the k-means
cluster ids via the cluster profiles, then score against the
appearance truth.

Subject label -> k-means mapping (from the profile description):
  cluster-A (neg, gentle)   -> cluster 3 (40% neg, flat shape)
  cluster-B (pos, tiny)     -> cluster 5 (13% neg, slowest growth)
  cluster-C (pos, plateau)  -> cluster 0 (0% neg, moderate)  [n=858]
  cluster-D (pos, mid-jump) -> cluster 7 (80% neg but mild... no) --
     actually cluster-D is all-positive mid-jump -> cluster 0/5 mix;
     the profile match is cluster 5 (slow) vs 0 (moderate): mid-jump
     maps to cluster 0.
  cluster-E (neg, steep-large) -> cluster 6 (100% neg, deepest) or 4;
     steepest-large maps to cluster 6.
  cluster-F (pos, steep)    -> cluster 1 (steepest positive growth).

The subject answered for 25 W4 trials with labels A-F; the scoring
maps each to the k-means id and compares with the appearance truth.
"""
import json

# subject answers from the transcript (label per trial)
subject_labels = {
    1: "A", 2: "A", 3: "A", 4: "B", 5: "C", 6: "D", 7: "E", 8: "A",
    9: "F", 10: "D", 11: "C", 12: "C", 13: "A", 14: "E", 15: "E",
    16: "E", 17: "C", 18: "C", 19: "C", 20: "E", 21: "B", 22: "C",
    23: "C", 24: "A", 25: "B",
}

label_to_cluster = {
    "A": 3,   # neg gentle
    "B": 5,   # pos tiny
    "C": 0,   # pos plateau (largest all-positive cluster)
    "D": 0,   # pos mid-jump (same all-positive family)
    "E": 6,   # neg steep-large (deepest negative)
    "F": 1,   # pos steep
}

d = json.load(open('p34b_window_design.json'))
app = json.load(open('p34b_appearance_truth.json'))['clusters']

n_ok = 0
rows = []
for t in d['w4']:
    tn = t['trial']
    mine = label_to_cluster[subject_labels[tn]]
    truth = t['truth_class']
    ok = mine == truth
    n_ok += ok
    rows.append({"trial": tn, "subject_label": subject_labels[tn],
                 "mapped": mine, "truth": truth, "correct": ok})
    if not ok:
        pass
print(f"W4 native vs appearance-truth: {n_ok}/25")
from math import comb as C
pval = sum(C(25, k)*0.125**k*0.875**(25-k) for k in range(n_ok, 26))
print(f"binomial p (chance 1/8=0.125): {pval:.4f}")
verdict = ("CONFIRMED" if n_ok >= 15 else "PARTIAL" if n_ok >= 10
           else "NEGATIVE")
print(f"P34-b W4 verdict: {verdict}")
json.dump({"rows": rows, "score": f"{n_ok}/25", "pvalue": pval,
           "verdict": verdict},
          open('p34b_w4_scored.json', 'w'), indent=1)
print("-> p34b_w4_scored.json")
