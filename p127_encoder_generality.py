"""P127: ENCODER GENERALITY of the DR rules — second-encoder replication.

All P116-P126 runs used flymemory's default embedder
(paraphrase-multilingual-MiniLM-L12-v2) — the registry said "MiniLM"
generically.  This run replicates the five headline conditions on
all-MiniLM-L6-v2 (English specialist, 6-layer) to test whether the
design rules are encoder-general or L12-specific:

  A  bare question                        (L12: 49.8)
  C  gold-head150 + question              (L12: 98.8)
  T  gold-TAIL150 + question              (L12: 66.0)
  X  title + question                     (L12: 40.7 — dilution)
  P125 bimodal: fresh-anchor vs stale-anchor top1
                                          (L12: ~98.9 / 5.9)
"""
import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np, json, sys
from sentence_transformers import SentenceTransformer
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

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
L = 150
CONDS = ["A_bare", "C_goldhead", "T_goldtail", "X_title",
         "F_fresh_anchor", "S_stale_anchor"]
acc = {c: [0, 0] for c in CONDS}


def emb(texts):
    return model.encode(texts, convert_to_numpy=True,
                        normalize_embeddings=True).astype(np.float32)


for t in titles:
    paras = list(art_ctxs[t].keys())
    pvecs = emb(paras)
    prev_para = None
    for q, gold in art_qs[t]:
        if gold not in art_ctxs[t]:
            prev_para = None
            continue
        gi = paras.index(gold)
        head, tail = gold[:L].strip(), gold[-L:].strip()
        texts = {"A_bare": q, "C_goldhead": head + " " + q,
                 "T_goldtail": tail + " " + q,
                 "X_title": t.replace("_", " ") + " " + q}
        if prev_para is not None:
            bucket = "F_fresh_anchor" if prev_para == gold else "S_stale_anchor"
            texts[bucket] = prev_para[:L].strip() + " " + q
        for c, txt in texts.items():
            v = emb([txt])[0]
            acc[c][0] += int(np.argsort(-(pvecs @ v))[0] == gi)
            acc[c][1] += 1
        prev_para = gold

out = {c: round(100 * s / n, 1) for c, (s, n) in acc.items() if n}
out["n"] = {c: n for c, (s, n) in acc.items() if n}
json.dump(out, open("p127_encoder_generality.json", "w"), indent=1)
print(json.dumps(out, indent=1))
