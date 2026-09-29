"""P126-b: a RETRIEVAL-FEEDBACK staleness signal.

P126 rejected cos(anchor, question) (AUC 0.639, dominated by question
style).  The natural alternative asks the STORE instead of the question:
  s2 = cos(anchor_head_emb, bare_top1_paragraph_emb)
Fresh conversation: the bare retrieval still points near the anchor's
region -> s2 high.  Stale: the question moved elsewhere -> bare top-1
far from the anchor -> s2 low.
Also measured: s3 = cos(anchor, mean of bare top-5) and, as oracle
context, the always-anchor / always-bare endpoints.  Per-row data saved
this time (p126b_rows.json) so thresholds can be re-derived without a
rerun.
"""
import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np, json, sys
FM = "D:/djr82/flymemory"
sys.path.insert(0, FM)
sys.path.insert(0, FM + "/flymemory")
from flymemory.v3 import _get_model
from datasets import load_dataset

sel = json.load(open("p93b_articles.json"))
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
        sims = pvecs @ qv
        order = np.argsort(-sims)
        top1_bare = int(order[0] == gi)
        if prev_para is None:
            prev_para = gold
            continue
        av = model.encode([prev_para[:L].strip()], convert_to_numpy=True,
                          normalize_embeddings=True)[0].astype(np.float32)
        atv = model.encode([prev_para[:L].strip() + " " + q],
                           convert_to_numpy=True,
                           normalize_embeddings=True)[0].astype(np.float32)
        top1_anch = int(np.argsort(-(pvecs @ atv))[0] == gi)
        s2 = float(av @ pvecs[order[0]])
        s3 = float(av @ pvecs[order[:5]].mean(axis=0))
        rows.append({"stale": int(prev_para != gold), "s2": round(s2, 4),
                     "s3": round(s3, 4), "top1_anch": top1_anch,
                     "top1_bare": top1_bare})
        prev_para = gold

json.dump(rows, open("p126b_rows.json", "w"))
stale = np.array([r["stale"] for r in rows])
s2 = np.array([r["s2"] for r in rows])
s3 = np.array([r["s3"] for r in rows])
a1 = np.array([r["top1_anch"] for r in rows])
b1 = np.array([r["top1_bare"] for r in rows])


def auc(sig):
    f, s_ = sig[stale == 0], sig[stale == 1]
    return float((f[:, None] > s_[None, :]).mean()
                 + 0.5 * (f[:, None] == s_[None, :]).mean())


def route(sig, theta):
    trust = sig >= theta
    top1 = np.where(trust, a1, b1)
    return round(100 * float(top1.mean()), 1), round(100 * float(trust.mean()), 1)


out = {
    "n": len(rows), "fresh_n": int((stale == 0).sum()), "stale_n": int(stale.sum()),
    "auc_s2": round(auc(s2), 3), "auc_s3": round(auc(s3), 3),
    "s2_mean_fresh": round(float(s2[stale == 0].mean()), 3),
    "s2_mean_stale": round(float(s2[stale == 1].mean()), 3),
    "always_anchor": round(100 * float(a1.mean()), 1),
    "always_bare": round(100 * float(b1.mean()), 1),
    "routing_s2": [], "routing_s3": [],
}
for theta in np.round(np.arange(0.30, 0.85, 0.05), 2):
    t1, tr = route(s2, theta)
    out["routing_s2"].append({"theta": float(theta), "top1": t1, "trust": tr})
    t1, tr = route(s3, theta)
    out["routing_s3"].append({"theta": float(theta), "top1": t1, "trust": tr})
json.dump(out, open("p126b_feedback_guard.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if "routing" not in k}, indent=1))
best2 = max(out["routing_s2"], key=lambda c: c["top1"])
best3 = max(out["routing_s3"], key=lambda c: c["top1"])
print("best s2 route:", best2, " best s3 route:", best3)
