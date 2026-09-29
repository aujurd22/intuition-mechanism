"""P122-c: WHERE should the prefix come from — head or tail of the chunk?

P120 showed (a) 150-200 char prefix saturates accuracy, (b) prefix-first
ordering beats question-first by 1-3.5pp.  Unsettled design question: does
the prefix have to come from the START of the paragraph (topic-sentence
hypothesis: leading sentences carry the entity definitions that match the
question) or does any 150-char window work (mass hypothesis: any verbatim
chunk carries enough lexical anchors)?

Conditions (n = all validation questions, 6 articles, within-article stores):
  head_prefix   hybrid = gold[:150] + " " + question     (P120 config)
  tail_prefix   hybrid = gold[-150:] + " " + question
  head_prefix_first  vs tail_prefix_first is the comparison;
  both use prefix-first ordering (the P120 winner) so the only difference
  is WHERE the prefix comes from.
Also: head vs tail with question-first ordering, to see if the ordering
effect and the source effect interact.

Prediction under the topic-sentence hypothesis: head > tail by a wide
margin (the tail of a SQuAD paragraph is often elaboration/detail, while
questions target the definitional head).
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
CONDS = ["head_first", "tail_first", "head_last", "tail_last"]  # {src}_{query order}
acc = {c: [0, 0] for c in CONDS}

for t in titles:
    paras = list(art_ctxs[t].keys())
    pvecs = model.encode(paras, convert_to_numpy=True,
                         normalize_embeddings=True).astype(np.float32)
    for q, gold in art_qs[t]:
        if gold not in art_ctxs[t]:
            continue
        gi = paras.index(gold)
        head, tail = gold[:L].strip(), gold[-L:].strip()
        texts = {"head_first": head + " " + q, "tail_first": tail + " " + q,
                 "head_last": q + " " + head, "tail_last": q + " " + tail}
        for c, txt in texts.items():
            v = model.encode([txt], convert_to_numpy=True,
                             normalize_embeddings=True)[0].astype(np.float32)
            acc[c][0] += int(np.argsort(-(pvecs @ v))[0] == gi)
            acc[c][1] += 1

out = {c: round(100 * s / n, 1) for c, (s, n) in acc.items()}
out["n"] = acc["head_first"][1]
json.dump(out, open("p122c_prefix_source.json", "w"), indent=1)
print(json.dumps(out, indent=1))
