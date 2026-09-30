"""P130-b: can ANY detector built from the (s2, s3) feature family beat
always-anchor?  The staleness-detector open problem, bounded.

Data: p126b_rows.json — 2817 conversational turns, each with
  stale         ground truth (prev paragraph != current gold)
  s2            cos(anchor-head, bare-top-1 paragraph)
  s3            cos(anchor-head, bare-top-5 mean)
  top1_anch     retrieval top1 with the anchored query
  top1_bare     retrieval top1 with the bare query

Protocol (honest): 5-fold CV.  For each fold, pick (feature, theta) on
the TRAIN fold maximizing routed accuracy, apply to TEST fold; report
mean test accuracy vs the two baselines.  Also report:
  oracle-router  mean(max(top1_anch, top1_bare))  — the ceiling for ANY
                 routing guard on this substrate
  calibrated requirement — the AUC a detector needs given the payoff
                 asymmetry (computed empirically: the smallest
                 fresh/stale mean-gap any candidate must beat).
"""
import json
import numpy as np

rows = json.load(open("p126b_rows.json", encoding="utf-8"))
stale = np.array([r["stale"] for r in rows], dtype=np.float32)
s2 = np.array([r["s2"] for r in rows], dtype=np.float32)
s3 = np.array([r["s3"] for r in rows], dtype=np.float32)
a1 = np.array([r["top1_anch"] for r in rows], dtype=np.float32)
b1 = np.array([r["top1_bare"] for r in rows], dtype=np.float32)

FEATURES = {"s2": s2, "s3": s3, "s2+s3": s2 + s3, "s2*s3": s2 * s3,
            "s2-s3": s2 - s3}
THETAS = np.round(np.arange(0.25, 0.90, 0.025), 3)

n = len(rows)
idx = np.arange(n)
rng = np.random.default_rng(20260930)
rng.shuffle(idx)
folds = np.array_split(idx, 5)

cv_scores, cv_choices = [], []
for f in range(5):
    test = folds[f]
    train = np.concatenate([folds[j] for j in range(5) if j != f])
    best = (-1, None, None)
    for fname, feat in FEATURES.items():
        for th in THETAS:
            trust = feat[train] >= th
            acc = float(np.where(trust, a1[train], b1[train]).mean())
            if acc > best[0]:
                best = (acc, fname, th)
    acc_b, fname_b, th_b = best
    feat = FEATURES[fname_b]
    trust = feat[test] >= th_b
    test_acc = float(np.where(trust, a1[test], b1[test]).mean())
    cv_scores.append(test_acc)
    cv_choices.append((fname_b, float(th_b)))

oracle = float(np.maximum(a1, b1).mean())
base_anchor = float(a1.mean())
base_bare = float(b1.mean())

# payoff-asymmetry requirement: empirically, what separated-mean does a
# detector need?  Simulate detectors with controlled AUC by mixing the
# label distributions: for target AUC in {0.64..0.99}, check the best
# routed accuracy achievable by ANY threshold on a synthetic signal with
# that AUC (rank-based construction: fresh rows draw high ranks).
def routed_acc_at_auc(target_auc, trials=30):
    accs = []
    n_f, n_s = int((stale == 0).sum()), int(stale.sum())
    for _ in range(trials):
        sig = np.zeros(n)
        rf = rng.random(n_f)
        # generate fresh/stale signal distributions whose separation ~ target AUC
        # via a rank-interpolation trick between pure noise (AUC .5) and
        # perfectly separated (AUC 1.0)
        rs = rng.random(n_s)
        w = 2 * (target_auc - 0.5)  # 0..1 mixing weight
        # stochastic rank pairing: with prob w fresh draws beat stale draws
        pooled = np.concatenate([rf, rs])
        # deterministic construction: quantile shift
        sig[:n_f] = rf + w * 1.0
        sig[n_f:] = rs
        labels = np.concatenate([np.zeros(n_f), np.ones(n_s)])
        order = np.argsort(sig)
        lab_o = labels[order]
        # routed acc via best threshold on ranks
        fr = sig[:n_f]; sr = sig[n_f:]
        th_grid = np.quantile(sig, np.linspace(0.05, 0.95, 37))
        cand = []
        for th in th_grid:
            trust = sig >= th
            # trust -> anchored outcome on fresh, bare on stale (proxy: use
            # the empirical per-group rates)
            t_f = trust[:n_f].mean() if n_f else 0
            t_s = trust[n_s:].mean() if n_s else 0
            # anchored acc among fresh ~ a1[stale==0].mean(); anchored acc
            # among stale ~ a1[stale==1].mean(); bare acc likewise
            acc = (t_f * float(a1[stale == 0].mean())
                   + (1 - t_f) * float(b1[stale == 0].mean())) * (n_f / n) \
                + (t_s * float(a1[stale == 1].mean())
                   + (1 - t_s) * float(b1[stale == 1].mean())) * (n_s / n)
            cand.append(acc)
        accs.append(max(cand))
    return float(np.mean(accs))


req = {f"auc_{a}": round(routed_acc_at_auc(a), 1)
       for a in (0.6, 0.7, 0.737, 0.8, 0.9, 0.99)}

out = {
    "n": n,
    "baselines": {"always_anchor": round(100 * base_anchor, 1),
                  "always_bare": round(100 * base_bare, 1)},
    "oracle_router": round(100 * oracle, 1),
    "cv_routed": round(100 * float(np.mean(cv_scores)), 1),
    "cv_folds": [round(100 * s, 1) for s in cv_scores],
    "cv_choices": cv_choices,
    "routing_acc_if_detector_had_auc": req,
}
json.dump(out, open("p130b_detector_bound.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "cv_choices"}, indent=1))
