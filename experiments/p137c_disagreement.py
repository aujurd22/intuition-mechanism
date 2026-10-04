"""P137-b: EXECUTE the selector's top-1 — the set-overlap staleness feature.

Feature family (P130-b registered next features, item ii): SET membership
instead of mean cosine.
  ov3  = anchor paragraph in bare-query top-3?  (1/0; also graded |T3 ∩ {a}|/3)
  ov5  = anchor in bare top-5?
Routing: trust anchored iff ov >= theta.  Compare against the exhausted
cosine family (s2: AUC 0.737, best routed 80.6 < always-anchor 84.3)
under identical protocol and the oracle ceiling 92.7.
"""
import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np, json, sys
FM = "D:/djr82/flymemory"
sys.path.insert(0, FM)
sys.path.insert(0, FM + "/flymemory")
from flymemory.v3 import _get_model
from datasets import load_dataset

sel = json.load(open("p93b_articles.json", encoding="utf-8"))
titles = [s[0] for s in sel]
ds = load_dataset("rajpurkar/squad", split="validation")
art_ctxs, art_qs = {}, {}
for r in ds:
    t = r["title"].strip()
    if t not in titles:
        continue
    art_ctxs.setdefault(t, {})[r["context"].strip()] = None
    art_qs.setdefault(t, []).append((r["question"].strip(), r["context"].strip()))

model = _get_model()
L = 150
rows = []
for t in titles:
    paras = list(art_ctxs[t].keys())
    pvecs = model.encode(paras, convert_to_numpy=True,
                         normalize_embeddings=True).astype(np.float32)
    prev_para = None
    for q, gold in art_qs[t]:
        if gold not in art_ctxs[t]:
            prev_para = None
            continue
        gi = paras.index(gold)
        qv = model.encode([q], convert_to_numpy=True,
                          normalize_embeddings=True)[0].astype(np.float32)
        order = np.argsort(-(pvecs @ qv))
        top1_bare = int(order[0] == gi)
        if prev_para is None:
            prev_para = gold
            continue
        ai = paras.index(prev_para)          # anchor paragraph id
        av = model.encode([prev_para[:L].strip()], convert_to_numpy=True,
                          normalize_embeddings=True)[0].astype(np.float32)
        atv = model.encode([prev_para[:L].strip() + " " + q],
                           convert_to_numpy=True,
                           normalize_embeddings=True)[0].astype(np.float32)
        top1_anch = int(np.argsort(-(pvecs @ atv))[0] == gi)
        top_id_anch = int(np.argsort(-(pvecs @ atv))[0])
        rows.append({
            "stale": int(prev_para != gold),
            "ov3": int(ai in order[:3]), "ov5": int(ai in order[:5]),
            "ov1": int(order[0] == ai),
            "disagree": int(top_id_anch != int(order[0])),
            "top1_anch": top1_anch, "top1_bare": top1_bare})
        prev_para = gold

json.dump(rows, open("p137b_set_overlap_rows.json", "w"))
stale = np.array([r["stale"] for r in rows])
a1 = np.array([r["top1_anch"] for r in rows])
b1 = np.array([r["top1_bare"] for r in rows])


def auc(sig):
    f, s_ = sig[stale == 0], sig[stale == 1]
    return float((f[:, None] > s_[None, :]).mean()
                 + 0.5 * (f[:, None] == s_[None, :]).mean())


out = {"n": len(rows), "fresh_n": int((stale == 0).sum()),
       "stale_n": int(stale.sum()),
       "always_anchor": round(100 * float(a1.mean()), 1),
       "always_bare": round(100 * float(b1.mean()), 1)}
dis = np.array([r["disagree"] for r in rows])
out["disagree_split"] = {}
for name, mask in (("agree", dis == 0), ("disagree", dis == 1)):
    out["disagree_split"][name] = {
        "n": int(mask.sum()),
        "stale_rate": round(100 * float(stale[mask].mean()), 1),
        "anchored_top1": round(100 * float(a1[mask].mean()), 1),
        "bare_top1": round(100 * float(b1[mask].mean()), 1)}

# per-feature: AUC + routed accuracy at every achievable threshold + 5-fold CV
idx = np.arange(len(rows))
rng = np.random.default_rng(20260930)
rng.shuffle(idx)
folds = np.array_split(idx, 5)
for feat in ("disagree", "ov1", "ov3", "ov5"):
    sig = np.array([r[feat] for r in rows], dtype=np.float32)
    a = auc(sig)
    # exhaustive thresholds
    best = (-1, None)
    curve = []
    for th in (0.5, 1.5):
        trust = sig >= th
        top1 = np.where(trust, a1, b1)
        acc = round(100 * float(top1.mean()), 1)
        curve.append({"theta": th, "trust": round(100 * float(trust.mean()), 1),
                      "top1": acc})
        if acc > best[0]:
            best = (acc, th)
    # 5-fold CV: pick theta on train, apply to test
    cv = []
    for f in range(5):
        te = folds[f]
        tr = np.concatenate([folds[j] for j in range(5) if j != f])
        bb = (-1, None)
        for th in (0.5, 1.5):
            tr_trust = sig[tr] >= th
            acc = float(np.where(tr_trust, a1[tr], b1[tr]).mean())
            if acc > bb[0]:
                bb = (acc, th)
        te_trust = sig[te] >= bb[1]
        cv.append(float(np.where(te_trust, a1[te], b1[te]).mean()))
    out[feat] = {"auc": round(a, 3), "curve": curve,
                 "cv_mean": round(100 * float(np.mean(cv)), 1),
                 "cv_folds": [round(100 * x, 1) for x in cv]}

json.dump(out, open("p137c_disagreement_result.json", "w"), indent=1)
print(json.dumps(out, indent=1))
