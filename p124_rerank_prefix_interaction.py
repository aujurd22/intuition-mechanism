"""P124: reranker x prefix-injection interaction — substitutes or additive?

The RAG line has two independent remedies for the "question too far from
the answer paragraph" bottleneck (P116):
  - cross-encoder rerank of the top-10 pool (+33pp, P93-b)
  - verbatim context prefix in the query (-> 98.8, P120/P122)
If both fix the SAME bottleneck, prefix injection should SUBSUME the
reranker: reranking the hybrid query's top-10 pool should have no
headroom left (98.8 is already ~saturated), while reranking the bare
question's pool recovers its usual +30pp.  Practical consequence if
confirmed: with context injection available, the expensive reranker
stage can be SKIPPED.

Conditions (n = 2823, within-article stores):
  A  bare question, bi-encoder top1                       (~49.8)
  B  bare question, rerank top-10 -> top1
  C  hybrid@150 head prefix, bi-encoder top1              (~98.8)
  D  hybrid, rerank top-10 -> top1
Reranker: cross-encoder/ms-marco-MiniLM-L-6-v2 (the flymemory production
reranker), pairs = (query, paragraph), pool = bi-encoder top-10.
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
acc = {c: [0, 0] for c in ["A_bare_bi", "B_bare_rerank",
                           "C_hyb_bi", "D_hyb_rerank"]}

for t in titles:
    paras = list(art_ctxs[t].keys())
    pvecs = model.encode(paras, convert_to_numpy=True,
                         normalize_embeddings=True).astype(np.float32)
    for q, gold in art_qs[t]:
        if gold not in art_ctxs[t]:
            continue
        gi = paras.index(gold)
        hyb = gold[:L].strip() + " " + q
        for c, query in (("A_bare_bi", q), ("C_hyb_bi", hyb)):
            sims = pvecs @ model.encode([query], convert_to_numpy=True,
                                        normalize_embeddings=True)[0].astype(np.float32)
            order = np.argsort(-sims)
            acc[c][0] += int(order[0] == gi)
            acc[c][1] += 1
            pool = order[:POOL]
            scores = reranker.predict([(query, paras[j]) for j in pool])
            best = pool[int(np.argmax(scores))]
            rc = {"A_bare_bi": "B_bare_rerank", "C_hyb_bi": "D_hyb_rerank"}[c]
            acc[rc][0] += int(best == gi)
            acc[rc][1] += 1

out = {c: round(100 * s / n, 1) for c, (s, n) in acc.items()}
out["n"] = acc["A_bare_bi"][1]
json.dump(out, open("p124_rerank_prefix_interaction.json", "w"), indent=1)
print(json.dumps(out, indent=1))
