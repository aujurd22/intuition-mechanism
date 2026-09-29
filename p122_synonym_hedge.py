"""P122: does context-prefix injection HEDGE paraphrase risk?

Connects P117 (hybrid query +35pp) with P117-b (50% synonym substitution on
the query kills retrieval, 0% top1).  The hedge hypothesis: the verbatim
prefix carries exact lexical anchors into the query, so retrieval should
survive synonym substitution applied to the QUESTION side.

Conditions (6 SQuAD articles, within-article stores, leave-one-out cosine):
  A  question verbatim                      (baseline, ~50%)
  B  question synonym-substituted           (P117-b floor, ~0%)
  C  hybrid@150, question verbatim          (P117 ceiling, ~91%)
  D  hybrid@150, question substituted       (HEDGE TEST: D >> B ?)
  E  hybrid@150, PREFIX substituted         (prefix-side fragility)

Design rule at stake: if D >> B, context-prefix injection doubles as a
paraphrase hedge — a second actionable RAG rule beyond raw accuracy.
"""
import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np, json, sys, re
FM = "D:/djr82/flymemory"
sys.path.insert(0, FM)
sys.path.insert(0, FM + "/flymemory")
from flymemory.v3 import _get_model
from datasets import load_dataset

SYN = {
    "game": "match", "champion": "winner", "season": "year", "team": "squad",
    "defeated": "beaten", "won": "prevailed", "played": "performed",
    "broadcast": "aired", "show": "program", "song": "track",
    "album": "record", "film": "movie", "city": "town", "population": "inhabitants",
    "river": "waterway", "war": "conflict", "battle": "combat",
    "president": "leader", "government": "administration", "school": "academy",
    "university": "college", "island": "isle", "mountain": "peak",
    "language": "tongue", "written": "authored", "designed": "created",
    "built": "constructed", "largest": "biggest", "first": "initial",
    "second": "subsequent",
}
WORD = re.compile(r"[A-Za-z]+")


def subst(text, rate=0.5):
    toks = text.split(" ")
    content_idx = [i for i, t in enumerate(toks)
                   if WORD.fullmatch(t.strip(".,;:!?()'\"")) and t.strip(".,;:!?()'\"").lower() in SYN]
    k = max(1, int(len(content_idx) * rate))
    rng = np.random.default_rng(20260930)
    pick = set(rng.choice(content_idx, size=min(k, len(content_idx)), replace=False).tolist())
    out = []
    for i, t in enumerate(toks):
        if i in pick:
            core = t.strip(".,;:!?()'\"")
            repl = SYN.get(core.lower(), core)
            out.append(repl if core == t else t.replace(core, repl))
        else:
            out.append(t)
    return " ".join(out)


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
CONDS = ["A_q_verbatim", "B_q_subst", "C_hyb_q_verbatim",
         "D_hyb_q_subst", "E_hyb_prefix_subst"]
acc = {c: [0, 0] for c in CONDS}

for t in titles:
    paras = list(art_ctxs[t].keys())
    pvecs = model.encode(paras, convert_to_numpy=True,
                         normalize_embeddings=True).astype(np.float32)
    for q, gold in art_qs[t]:
        if gold not in art_ctxs[t]:
            continue
        gi = paras.index(gold)
        pre, q_sub = gold[:L].strip(), subst(q)
        pre_sub = subst(gold[:L]).strip() or gold[:L].strip()
        texts = {
            "A_q_verbatim": q,
            "B_q_subst": q_sub,
            "C_hyb_q_verbatim": pre + " " + q,
            "D_hyb_q_subst": pre + " " + q_sub,
            "E_hyb_prefix_subst": pre_sub + " " + q,
        }
        for c, txt in texts.items():
            v = model.encode([txt], convert_to_numpy=True,
                             normalize_embeddings=True)[0].astype(np.float32)
            top1 = int(np.argsort(-(pvecs @ v))[0] == gi)
            acc[c][0] += top1
            acc[c][1] += 1

out = {c: round(100 * s / n, 1) for c, (s, n) in acc.items()}
out["n"] = acc["A_q_verbatim"][1]
json.dump(out, open("p122_synonym_hedge.json", "w"), indent=1)
print(json.dumps(out, indent=1))
