import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np, json, sys
FM = "D:/djr82/flymemory"
sys.path.insert(0, FM)
sys.path.insert(0, FM + "/flymemory")
from flymemory.v3 import _embed
from datasets import load_dataset
from sklearn.metrics import roc_auc_score

titles = [s[0] for s in json.load(open("p93b_articles.json"))]
ds = load_dataset("rajpurkar/squad", split="validation")
art_q = {}
for r in ds:
    t = r["title"].strip()
    if t not in titles: continue
    art_q.setdefault(t, []).append(r["question"].strip())

def emb(t):
    v = np.array(_embed(t), dtype=np.float32)
    return v/(np.linalg.norm(v)+1e-12)

print("store-article | AUROC | median max-cos(in) | median max-cos(ood)")
aucs = []
for store_t in titles:
    qs_store = art_q[store_t][:40]
    store = np.array([emb(q) for q in qs_store])
    in_scores, ood_scores = [], []
    for q in art_q[store_t][40:60]:
        v = emb(q)
        in_scores.append(float((store @ v).max()))
    for other_t in titles:
        if other_t == store_t: continue
        for q in art_q[other_t][:8]:
            v = emb(q)
            ood_scores.append(float((store @ v).max()))
    y = [1]*len(in_scores) + [0]*len(ood_scores)
    auc = roc_auc_score(y, in_scores + ood_scores)
    aucs.append(auc)
    print("  %-34s AUROC=%.3f  in=%.3f  ood=%.3f" % (store_t, auc,
          np.median(in_scores), np.median(ood_scores)))

print("MEAN AUROC = %.3f" % np.mean(aucs))
json.dump({"mean_auroc": round(float(np.mean(aucs)),3),
           "per_store": {t2: round(float(a),3) for t2, a in zip(titles, aucs)}},
          open("p95_clearance.json", "w"), indent=1)
print("saved p95_clearance.json")
