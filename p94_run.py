import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np, json, sys, re
FM = "D:/djr82/flymemory"
sys.path.insert(0, FM)
sys.path.insert(0, FM + "/flymemory")
from flymemory.v3 import _embed
from datasets import load_dataset

titles = [s[0] for s in json.load(open("p93b_articles.json"))]
ds = load_dataset("rajpurkar/squad", split="validation")

def sent_of(context, ans_start, ans_text):
    end = ans_start + len(ans_text)
    pos = 0
    for sent in re.split("(?<=[.!?]) +", context):
        if pos <= ans_start < pos + len(sent):
            return sent.strip()
        pos += len(sent) + 1
    return context[max(0, ans_start-120):ans_start+len(ans_text)+40]

def emb(t):
    v = np.array(_embed(t), dtype=np.float32)
    return v/(np.linalg.norm(v)+1e-12)

art = {}
for r in ds:
    t = r["title"].strip()
    if t not in titles: continue
    a = art.setdefault(t, {"ctxs": {}, "qa": []})
    c = r["context"].strip()
    a["ctxs"][c] = None
    ans = r["answers"]["text"]
    ans_text = ans[0] if ans else ""
    ans_start = r["answers"]["answer_start"][0] if ans and r["answers"]["answer_start"] else 0
    a["qa"].append({"q": r["question"].strip(), "c": c,
                    "ans_text": ans_text, "ans_start": ans_start})

results = {}
tot_raw = tot_orc = n_all = 0
print("article | rawQ-top1 | ansSent-top1 | gap")
for t in titles:
    d = art[t]
    ctx_list = list(d["ctxs"].keys())
    E = np.array([emb(c) for c in ctx_list], dtype=np.float32)
    E = E/(np.linalg.norm(E, axis=1, keepdims=True)+1e-12)
    qa = [x for x in d["qa"] if x["ans_text"]]
    rng = np.random.default_rng(9401)
    if len(qa) > 60:
        qa = [qa[i] for i in rng.choice(len(qa), 60, replace=False)]
    raw1 = orc1 = 0
    for x in qa:
        qe = emb(x["q"])
        sc = E @ qe
        raw1 += ctx_list[int(np.argmax(sc))] == x["c"]
        s = sent_of(x["c"], x["ans_start"], x["ans_text"])
        se = emb(s)
        sc2 = E @ se
        orc1 += ctx_list[int(np.argmax(sc2))] == x["c"]
    n = len(qa)
    results[t] = {"raw_top1": round(100*raw1/n,1),
                  "oracle_top1": round(100*orc1/n,1), "n": n}
    tot_raw += raw1; tot_orc += orc1; n_all += n
    print(f"  {t}: raw={100*raw1/n:5.1f}%  oracle={100*orc1/n:5.1f}%  gap={100*(orc1-raw1)/n:+5.1f}pp")

print(f"POOLED: raw={100*tot_raw/n_all:.1f}%  oracle={100*tot_orc/n_all:.1f}%  n={n_all}")
results["pooled"] = {"raw": round(100*tot_raw/n_all,1),
                    "oracle": round(100*tot_orc/n_all,1), "n": n_all}
json.dump(results, open("p94_reranker_oracle.json", "w"), indent=1)
print("saved p94_reranker_oracle.json")
