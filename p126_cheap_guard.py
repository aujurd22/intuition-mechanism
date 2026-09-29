"""P126: a CHEAP staleness guard — anchor-question similarity routing.

P125-b's dual-query union + rerank is robust but costs 2x POOL
cross-attention passes per turn.  A cheaper guard: measure
s = cos(anchor_emb, question_emb) with the SAME bi-encoder (no extra
model), route on a threshold:
  s >= theta  -> trust the anchored query (fresh regime)
  s <  theta  -> fall back to the bare question
This run measures the fresh/stale separation in s and the routing
accuracy curve over theta.

Outputs:
  - fresh/stale s distributions (AUC of separation)
  - routed top1 vs theta curve; compare against the two ceilings
    (always-anchor 84.3 bimodal, always-bare 49.8, union+rerank P125-b)
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
rows = []  # (is_stale, s, top1_anchored, top1_bare)
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
        top1_bare = int(np.argsort(-(pvecs @ qv))[0] == gi)
        if prev_para is None:
            prev_para = gold
            continue
        av = model.encode([prev_para[:L].strip()], convert_to_numpy=True,
                          normalize_embeddings=True)[0].astype(np.float32)
        s = float(qv @ av)
        anchored_text = prev_para[:L].strip() + " " + q
        atv = model.encode([anchored_text], convert_to_numpy=True,
                           normalize_embeddings=True)[0].astype(np.float32)
        top1_anch = int(np.argsort(-(pvecs @ atv))[0] == gi)
        rows.append((int(prev_para != gold), s, top1_anch, top1_bare))
        prev_para = gold

arr = np.array(rows, dtype=np.float32)
stale, s, a1, b1 = arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3]
# AUC: P(s_fresh > s_stale) + 0.5 * P(equal)
sf, ss_ = s[stale == 0], s[stale == 1]
auc = float((sf[:, None] > ss_[None, :]).mean() + 0.5 * (sf[:, None] == ss_[None, :]).mean())
curve = []
for theta in np.round(np.arange(0.30, 0.81, 0.05), 2):
    trust = s >= theta
    top1 = np.where(trust, a1, b1)
    curve.append({"theta": float(theta),
                  "top1": round(100 * float(top1.mean()), 1),
                  "trust_rate": round(100 * float(trust.mean()), 1)})
out = {
    "n_turns_with_history": int(len(rows)),
    "fresh_n": int((stale == 0).sum()), "stale_n": int(stale.sum()),
    "s_mean_fresh": round(float(sf.mean()), 3), "s_mean_stale": round(float(ss_.mean()), 3),
    "separation_auc": round(auc, 3),
    "always_bare_top1": round(100 * float(b1.mean()), 1),
    "always_anchor_top1": round(100 * float(a1.mean()), 1),
    "routing_curve": curve,
}
json.dump(out, open("p126_cheap_guard.json", "w"), indent=1)
print(json.dumps(out, indent=1))
