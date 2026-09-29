import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np, json, sys
FM = "D:/djr82/flymemory"
sys.path.insert(0, FM)
sys.path.insert(0, FM + "/flymemory")
from flymemory.v3 import _embed
from datasets import load_dataset

sel = json.load(open("p93b_articles.json"))
titles = [s[0] for s in sel]
ds = load_dataset("rajpurkar/squad", split="validation")
art_ctxs, art_qs = {}, {}
for r in ds:
    t = r["title"].strip()
    if t not in titles: continue
    art_ctxs.setdefault(t, {})[r["context"].strip()] = None
    art_qs.setdefault(t, []).append((r["question"].strip(), r["context"].strip()))

results = {}
print("within-article needle discrimination (query=real SQuAD question):")
for t in titles:
    d = art_ctxs[t]
    ctx_list = list(d.keys())
    qs = art_qs[t]
    E = np.array([_embed(c) for c in ctx_list], dtype=np.float32)
    E = E/(np.linalg.norm(E, axis=1, keepdims=True)+1e-12)
    rng = np.random.default_rng(9303)
    qsample = qs if len(qs) <= 60 else [qs[i] for i in rng.choice(len(qs), 60, replace=False)]
    hit10 = top_sib = tot = 0
    for q, true_c in qsample:
        qe = np.array(_embed(q), dtype=np.float32)
        qe = qe/(np.linalg.norm(qe)+1e-12)
        sc = E @ qe
        top = np.argsort(-sc)[:10]
        hits = sum(1 for j in top if ctx_list[j] == true_c)
        if hits > 0:
            hit10 += 1
            if ctx_list[top[0]] != true_c: top_sib += 1
        tot += 1
    results[t] = {"n_ctx": len(ctx_list), "n_q": tot,
                  "hit10": round(100*hit10/tot,1),
                  "top1_wrong_para": round(100*top_sib/tot,1)}
    print(f"  {t}: n_ctx={len(ctx_list)} hit@10={100*hit10/tot:.1f}% top1-wrong={100*top_sib/tot:.1f}%")

json.dump(results, open("p93b_within_article.json", "w"), indent=1)
print("saved p93b_within_article.json")
