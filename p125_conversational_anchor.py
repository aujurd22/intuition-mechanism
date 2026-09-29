"""P125: CONVERSATIONAL anchor injection — the deployable hybrid.

P123 killed metadata injection (title, -9pp) and P117/P120 measured a
gold-context ceiling.  The deployable path that remains is CONVERSATION
history: in a multi-turn session about one document, the previous turn's
answer paragraph is available at query time.  Does injecting it help?

Protocol (simulates conversation order with SQuAD's native question
order inside each article):
  For each question k (k >= 2, same article as k-1):
    prev_ctx = the paragraph answered by question k-1
  Conditions:
    A  question alone (within-article)                     ~49.8
    B  prev_ctx[:150] + " " + question                     (conversational anchor)
    C  gold head[:150] + question                          (ceiling, ~98.8)
    D  prev_ctx[:150] + question, but ONLY turns where the previous
       paragraph DIFFERS from the current gold (the interesting
       sub-population: a stale anchor)
Also: dependency break test — first question of each article has no
history; measure how B behaves there (random anchor = another article's
paragraph head as negative control, condition E).
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
CONDS = ["A_q_alone", "B_prev_anchor", "C_gold_ceiling",
         "B_stale_only", "E_random_anchor"]
acc = {c: [0, 0] for c in CONDS}

for t in titles:
    paras = list(art_ctxs[t].keys())
    pvecs = model.encode(paras, convert_to_numpy=True,
                         normalize_embeddings=True).astype(np.float32)
    qs = art_qs[t]
    # random anchor source: head of a paragraph from the NEXT article (cyclic)
    other_t = titles[(titles.index(t) + 1) % len(titles)]
    rand_anchor = list(art_ctxs[other_t].keys())[0][:L].strip()
    prev_para = None
    for k, (q, gold) in enumerate(qs):
        if gold not in art_ctxs[t]:
            prev_para = None
            continue
        gi = paras.index(gold)
        head = gold[:L].strip()
        prev_head = prev_para[:L].strip() if prev_para else None
        is_stale = prev_para is not None and prev_para != gold
        texts = {"A_q_alone": q,
                 "C_gold_ceiling": head + " " + q,
                 "E_random_anchor": rand_anchor + " " + q}
        if prev_head:
            texts["B_prev_anchor"] = prev_head + " " + q
        if is_stale:
            texts["B_stale_only"] = prev_head + " " + q
        for c, txt in texts.items():
            v = model.encode([txt], convert_to_numpy=True,
                             normalize_embeddings=True)[0].astype(np.float32)
            acc[c][0] += int(np.argsort(-(pvecs @ v))[0] == gi)
            acc[c][1] += 1
        prev_para = gold

out = {c: round(100 * s / n, 1) for c, (s, n) in acc.items() if n}
out["n_per_cond"] = {c: n for c, (s, n) in acc.items() if n}
json.dump(out, open("p125_conversational_anchor.json", "w"), indent=1)
print(json.dumps(out, indent=1))
