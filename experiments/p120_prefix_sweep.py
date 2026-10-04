"""P120: prefix-length response curve for the hybrid query (P117 single point -> curve).

Protocol (matches P116/P117): 6 SQuAD articles, within-article paragraph
store, leave-one-out top-1/top-10 by cosine.  For each real SQuAD question
whose gold paragraph is in the store, the query is

    prefix(context[:L]) + separator + question        (P117 order: prefix first)
    question + separator + prefix(context[:L])        (order ablation)

L swept over {0, 50, 100, 200, 400, full}.  L=0 reproduces the pure-question
baseline; L=full approaches verbatim.  Also: prefix-only (no question) at the
same lengths, to decompose where the gain comes from.

Contrast-law prediction (P54/P116/P117): accuracy rises with L, saturating
before L=full; the question contributes beyond the prefix (prefix-only <
hybrid at matched L).
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
SEP = " "
LENGTHS = [0, 50, 100, 200, 400, 10**9]

def rank_top1(qvec, pvecs, gold_idx):
    sims = pvecs @ qvec
    order = np.argsort(-sims)
    return int(order[0] == gold_idx), int(gold_idx in order[:10])

curves = {"prefix_first": {L: [0, 0, 0] for L in LENGTHS},   # [n, top1, top10]
          "question_first": {L: [0, 0, 0] for L in LENGTHS},
          "prefix_only": {L: [0, 0, 0] for L in LENGTHS}}

for t in titles:
    paras = list(art_ctxs[t].keys())
    pvecs = model.encode(paras, convert_to_numpy=True,
                         normalize_embeddings=True).astype(np.float32)
    for q, gold in art_qs[t]:
        if gold not in art_ctxs[t]:
            continue
        gi = paras.index(gold)
        qv = model.encode([q], convert_to_numpy=True,
                          normalize_embeddings=True)[0].astype(np.float32)
        for L in LENGTHS:
            pre = gold[:L].strip()
            if not pre:
                pre = gold.strip()
            for mode in ("prefix_first", "question_first", "prefix_only"):
                text = (pre + SEP + q) if mode == "prefix_first" else \
                       (q + SEP + pre) if mode == "question_first" else pre
                tv = model.encode([text], convert_to_numpy=True,
                                  normalize_embeddings=True)[0].astype(np.float32)
                h1, h10 = rank_top1(tv, pvecs, gi)
                c = curves[mode][L]
                c[0] += 1; c[1] += h1; c[2] += h10

out = {}
for mode, cc in curves.items():
    out[mode] = {}
    for L in LENGTHS:
        n, s1, s10 = cc[L]
        key = "full" if L == 10**9 else str(L)
        out[mode][key] = {"n": n, "top1": round(100*s1/n, 1), "top10": round(100*s10/n, 1)}

json.dump(out, open("p120_prefix_sweep.json", "w"), indent=1)
for mode, cc in out.items():
    print(mode, {k: (v["top1"], v["top10"]) for k, v in cc.items()})
