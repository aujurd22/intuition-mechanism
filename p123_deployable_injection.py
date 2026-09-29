"""P123: DEPLOYABLE context injection — the honest version of the hybrid rule.

Scope correction to P117/P120: the hybrid prefix there was the GOLD
paragraph's own head — unavailable at query time in a real system.  Those
runs measure the CEILING of context injection ("you already hold a chunk
of the target").  This run tests what a real system can inject:

  A  question only                       (baseline, ~50%)
  B  title + " " + question              (document/entity metadata — ALWAYS
                                          available in a corpus-indexed RAG)
  C  gold-head150 + question             (the P120 ceiling, re-measured here
                                          in the same run for calibration)

Within-article stores make title injection maximally easy (the title is
constant per store) — the honest task where it CAN matter is cross-article
retrieval, so this run also does the CROSS-ARTICLE variant:

  D  question only, global store (all paragraphs of the 6 articles)
  E  title + question, global store

Predictions: B >> A within-article (title carries the entity core); B
still far below C (the gold head carries question-specific lexical mass).
Cross-article: D should sit below the within-article baseline (harder
task), and E should beat D by a wider margin (the title disambiguates
WHICH article's entities the question targets).
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
CONDS = ["A_q_within", "B_title_within", "C_goldhead_within",
         "D_q_global", "E_title_global"]
acc = {c: [0, 0] for c in CONDS}

# global store: all paragraphs with their article index
all_paras, all_art = [], []
for t in titles:
    for p in art_ctxs[t]:
        all_paras.append(p)
        all_art.append(t)
GVEC = model.encode(all_paras, convert_to_numpy=True,
                    normalize_embeddings=True).astype(np.float32)
all_art = np.array(all_art)

for t in titles:
    paras = list(art_ctxs[t].keys())
    pvecs = model.encode(paras, convert_to_numpy=True,
                         normalize_embeddings=True).astype(np.float32)
    for q, gold in art_qs[t]:
        if gold not in art_ctxs[t]:
            continue
        gi = paras.index(gold)
        head = gold[:150].strip()
        texts = {"A_q_within": q, "B_title_within": t.replace("_", " ") + " " + q,
                 "C_goldhead_within": head + " " + q}
        for c, txt in texts.items():
            v = model.encode([txt], convert_to_numpy=True,
                             normalize_embeddings=True)[0].astype(np.float32)
            acc[c][0] += int(np.argsort(-(pvecs @ v))[0] == gi)
            acc[c][1] += 1
        # global-store variants: hit = same-article gold paragraph ranked #1
        for c, txt in (("D_q_global", q),
                       ("E_title_global", t.replace("_", " ") + " " + q)):
            v = model.encode([txt], convert_to_numpy=True,
                             normalize_embeddings=True)[0].astype(np.float32)
            top1 = int(np.argsort(-(GVEC @ v))[0] == int(np.where(all_art == t)[0][gi]))
            acc[c][0] += top1
            acc[c][1] += 1

out = {c: round(100 * s / n, 1) for c, (s, n) in acc.items()}
out["n"] = acc["A_q_within"][1]
json.dump(out, open("p123_deployable_injection.json", "w"), indent=1)
print(json.dumps(out, indent=1))
