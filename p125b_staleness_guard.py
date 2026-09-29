"""P125-b: the STALENESS GUARD — dual-query union + bare-question rerank.

P125 exposed the bimodal hazard of conversational anchor injection:
fresh anchor (prev answer from the same paragraph) ~98.9% top1; stale
anchor (conversation moved on) 5.9% — worse than no anchor (49.8).
This run completes the deployable recipe:

  For each turn, retrieve with BOTH:
    q_bare = question                       (staleness-proof)
    q_anch = prev_head[:150] + question     (contrast-rich when fresh)
  Take the UNION of the two top-10 pools, rerank the union with the
  cross-encoder using the BARE question (the reranker needs no anchor),
  return the top-1.

Predictions: fresh turns keep ~99 (gold is in the anchored pool and
ranks first under cross-attention); stale turns recover to at least the
bare+rerank level (~74 per P124-B, likely higher since the pool also
contains the bare top-10); overall > 90.
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

acc = {"all": [0, 0], "fresh": [0, 0], "stale": [0, 0], "first_turn": [0, 0]}
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
        pool_ids = list(np.argsort(-(pvecs @ qv))[:POOL])
        bucket = "first_turn"
        if prev_para is not None:
            av = model.encode([prev_para[:L].strip() + " " + q],
                              convert_to_numpy=True,
                              normalize_embeddings=True)[0].astype(np.float32)
            pool_ids += list(np.argsort(-(pvecs @ av))[:POOL])
            bucket = "fresh" if prev_para == gold else "stale"
        uniq = sorted(set(pool_ids))
        scores = reranker.predict([(q, paras[j]) for j in uniq])
        best = uniq[int(np.argmax(scores))]
        acc[bucket][0] += int(best == gi)
        acc[bucket][1] += 1
        acc["all"][0] += int(best == gi)
        acc["all"][1] += 1
        prev_para = gold

out = {c: round(100 * s / n, 1) for c, (s, n) in acc.items() if n}
out["n"] = {c: n for c, (s, n) in acc.items() if n}
json.dump(out, open("p125b_staleness_guard.json", "w"), indent=1)
print(json.dumps(out, indent=1))
