import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np, json, sys
FM = "D:/djr82/flymemory"
sys.path.insert(0, FM)
sys.path.insert(0, FM + "/flymemory")
from flymemory.v3 import _embed
from datasets import load_dataset

titles = [s[0] for s in json.load(open("p93b_articles.json"))]
ds = load_dataset("rajpurkar/squad", split="validation")
art = {}
for r in ds:
    t = r["title"].strip()
    if t not in titles: continue
    a = art.setdefault(t, {"ctxs": {}, "q": []})
    a["ctxs"][r["context"].strip()] = None
    a["q"].append((r["question"].strip(), r["context"].strip()))

def emb(t):
    v = np.array(_embed(t), dtype=np.float32)
    return v/(np.linalg.norm(v)+1e-12)

KS = [1, 2, 3, 4, 6, 8, 12]
results = {}
for t in titles:
    d = art[t]
    ctx_list = list(d["ctxs"].keys())
    E = np.array([emb(c) for c in ctx_list], dtype=np.float32)
    E = E/(np.linalg.norm(E, axis=1, keepdims=True)+1e-12)
    qs = d["q"]
    rng = np.random.default_rng(9501)
    qsample = qs if len(qs) <= 50 else [qs[i] for i in rng.choice(len(qs), 50, replace=False)]
    row = {}
    for k in KS:
        hit = 0
        for q, true_c in qsample:
            words = q.split()
            qk = " ".join(words[:k])
            qe = emb(qk)
            sc = E @ qe
            top = np.argsort(-sc)[:10]
            hit += int(true_c in [ctx_list[j] for j in top])
        row[k] = round(100*hit/len(qsample), 1)
    results[t] = row
    print("%-32s" % t + "  ".join("%dw:%5.1f" % (k, row[k]) for k in KS))

# pooled per k
pooled = {}
for k in KS:
    vals = [results[t][k] for t in titles]
    pooled[k] = round(float(np.mean(vals)), 1)
print("pooled:", pooled)
json.dump({"per_article": results, "pooled": pooled},
          open("p96_question_floor.json", "w"), indent=1)
print("saved p96_question_floor.json")
