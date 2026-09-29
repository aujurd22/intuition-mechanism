"""P125-c: the CORRECTED staleness recipe — dual rerank with score max.

P125-b proved a weak arbiter (bare-question rerank) truncates the fresh
channel.  Fix: keep BOTH conditionings.  For each turn:
  pool   = union(bare top-10, anchored top-10)
  s_bare = cross-encoder scores with the BARE query
  s_anch = cross-encoder scores with the ANCHORED query
  pick argmax_j max(s_bare[j], s_anch[j])
Fresh turns: the anchored scores reproduce the anchored advantage; stale
turns: the bare scores provide the fallback (and the anchored scores of
stale anchors rank low, so max is safe).

Prediction: fresh ~99, stale >= 83, overall ~95+ at 2x rerank cost.
A cheaper hybrid is measured in P126 (route-then-query with no rerank).
"""
import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np, json, sys
FM = "D:/djr82/flymemory"
sys.path.insert(0, FM)
sys.path.insert(0, FM + "/flymemory")
from flymemory.v3 import _get_model
from sentence_transformers import CrossEncoder
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
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=256)
L, POOL = 150, 10

acc = {"all": [0, 0], "fresh": [0, 0], "stale": [0, 0]}
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
        if prev_para is None:
            # first turn: bare pool + bare rerank (P124-B recipe)
            pool = list(np.argsort(-(pvecs @ qv))[:POOL])
            scores = reranker.predict([(q, paras[j]) for j in pool])
            best = pool[int(np.argmax(scores))]
            acc["all"][0] += int(best == gi); acc["all"][1] += 1
            prev_para = gold
            continue
        av = model.encode([prev_para[:L].strip() + " " + q],
                          convert_to_numpy=True,
                          normalize_embeddings=True)[0].astype(np.float32)
        pool = sorted(set(list(np.argsort(-(pvecs @ qv))[:POOL]) +
                          list(np.argsort(-(pvecs @ av))[:POOL])))
        s_bare = reranker.predict([(q, paras[j]) for j in pool])
        s_anch = reranker.predict([(prev_para[:L].strip() + " " + q, paras[j])
                                   for j in pool])
        combined = np.maximum(s_bare, s_anch)
        best = pool[int(np.argmax(combined))]
        bucket = "fresh" if prev_para == gold else "stale"
        acc[bucket][0] += int(best == gi); acc[bucket][1] += 1
        acc["all"][0] += int(best == gi); acc["all"][1] += 1
        prev_para = gold

out = {c: round(100 * s / n, 1) for c, (s, n) in acc.items() if n}
out["n"] = {c: n for c, (s, n) in acc.items() if n}
json.dump(out, open("p125c_dual_rerank.json", "w"), indent=1)
print(json.dumps(out, indent=1))
