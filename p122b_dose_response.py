"""P122-b: synonym-substitution DOSE-RESPONSE + the P117-b replication conflict.

P122 found question-side synonym substitution (30-word map, 50% of MATCHED
tokens) leaves retrieval at 49.7% vs 49.8% baseline -- conflicting with the
registered P117-b claim of 0% top1 after '50% synonym substitution'.
This run quantifies the dose properly:

  (i)  effective dose logging: how many tokens a 30-word synonym map can
       hit per SQuAD question (the map-based rate is bounded by coverage);
  (ii) RANDOM-WORD substitution (replace content words with words drawn
       from the article's own paragraph vocabulary -- guaranteed semantic
       destruction) at rates {20, 40, 60, 80}% on:
         - question alone          (dose-response curve)
         - hybrid@150, prefix kept verbatim (the hedge curve)
         - hybrid@150, prefix hit at the same rate (prefix fragility)

Prediction under the contrast law + lexical-sensitivity picture: the
question-alone curve degrades steeply with dose; the hybrid curve degrades
much slower at matched dose (the verbatim prefix carries the discriminative
content); prefix-hit hurts more than question-hit (prefix carries more of
the matching mass).
"""
import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np, json, sys, re
FM = "D:/djr82/flymemory"
sys.path.insert(0, FM)
sys.path.insert(0, FM + "/flymemory")
from flymemory.v3 import _get_model
from datasets import load_dataset

WORD = re.compile(r"[A-Za-z]{3,}")
STOP = set("the a an and or of to in on at for with by from as is are was "
           "were be been did does do what which who whom whose when where "
           "why how his her its their his hers our your not no yes".split())


def content_tokens(text):
    return [m for m in WORD.finditer(text) if m.group(0).lower() not in STOP]


def rand_subst(text, vocab, rate, rng):
    toks = content_tokens(text)
    k = int(round(len(toks) * rate))
    if k == 0 or not vocab:
        return text, 0
    pick = set(rng.choice(len(toks), size=min(k, len(toks)), replace=False).tolist())
    out, last, nsub = [], 0, 0
    for i, m in enumerate(toks):
        if i in pick:
            out.append(text[last:m.start()])
            out.append(vocab[int(rng.integers(len(vocab)))])
            last = m.end()
            nsub += 1
    out.append(text[last:])
    return "".join(out), nsub


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
RATES = [0.0, 0.2, 0.4, 0.6, 0.8]
rng = np.random.default_rng(20260930)
res = {"q_alone": {}, "hyb_q_hit": {}, "hyb_pre_hit": {}}
for r_ in RATES:
    res["q_alone"][r_] = [0, 0, 0]      # [top1_sum, n, nsubst_sum]
    res["hyb_q_hit"][r_] = [0, 0, 0]
    res["hyb_pre_hit"][r_] = [0, 0, 0]

dose_log = []
for t in titles:
    paras = list(art_ctxs[t].keys())
    pvecs = model.encode(paras, convert_to_numpy=True,
                         normalize_embeddings=True).astype(np.float32)
    vocab = sorted({w.lower() for p in paras for w in WORD.findall(p)
                    if w.lower() not in STOP})
    for q, gold in art_qs[t]:
        if gold not in art_ctxs[t]:
            continue
        gi = paras.index(gold)
        pre = gold[:L].strip()
        for r_ in RATES:
            qh, n1 = rand_subst(q, vocab, r_, rng)
            preh, n2 = rand_subst(pre, vocab, r_, rng)
            dose_log.append((r_, n1, len(content_tokens(q)), n2, len(content_tokens(pre))))
            for cond, txt in (("q_alone", qh), ("hyb_q_hit", pre + " " + qh),
                              ("hyb_pre_hit", preh + " " + q)):
                v = model.encode([txt], convert_to_numpy=True,
                                 normalize_embeddings=True)[0].astype(np.float32)
                top1 = int(np.argsort(-(pvecs @ v))[0] == gi)
                c = res[cond][r_]
                c[0] += top1
                c[1] += 1
                c[2] += (n1 if cond != "hyb_pre_hit" else n2)

out = {}
for cond, cc in res.items():
    out[cond] = {}
    for r_ in RATES:
        s, n, ns = cc[r_]
        key = str(r_)
        out[cond][key] = {"top1": round(100 * s / n, 1),
                          "mean_subst": round(ns / n, 2)}
eff = {}
for r_ in RATES:
    rows = [(n1, nt) for (rr, n1, nt, n2, np_) in dose_log if rr == r_ and nt > 0]
    if rows:
        eff[str(r_)] = round(float(np.mean([n1 / nt for n1, nt in rows])), 3)
out["effective_dose_q"] = eff
out["n"] = res["q_alone"]["0.0"][1]
json.dump(out, open("p122b_dose_response.json", "w"), indent=1)
print(json.dumps(out, indent=1))
