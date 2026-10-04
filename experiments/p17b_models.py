"""P17-B: memory-vs-mechanism discriminator across API models
(P17 continuation: 'stronger models' registered route).

Conditions per model (identical data/protocol to p17_llm.py, seed 123):
  B-counterfactual: 20 fresh-generator series (memory route closed),
    few-shot with 4 correct examples;
  A-lit: the 17 real literature series (memory route open).
Chance 0.25.  Bands: B >= 0.70 CONFIRMED (first positive L3 datapoint);
0.45-0.70 PARTIAL; B < 0.45 & A >= 0.70 MEMORY-ONLY.

Models: doubao-seed-2.1-lite (already known), deepseek-v4.1-flash,
deepseek-v4-flash, minimax-m3, kimi-k2.8-preview (user-provided list).

Run:  python p17b_models.py [model ...]   (default: all four new models)
"""
import json
import os
import sys
import time
import urllib.request

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
from llm_client import BASE, KEY  # noqa: E402
from p17_llm import fmt, parse_digit, fewshot_prompt, SIGS  # noqa: E402
from p15_envelope import make_dataset, poch_cum  # noqa: E402
from p4_clean import build  # noqa: E402


def ask(model, prompt, max_tokens=4096):
    body = json.dumps({"model": model,
                       "messages": [{"role": "user", "content": prompt}],
                       "temperature": 0, "max_tokens": max_tokens,
                       "thinking": {"type": "disabled"}}).encode()
    req = urllib.request.Request(BASE + "/chat/completions", data=body,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {KEY}"})
    last = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                out = json.loads(r.read())
            msg = out["choices"][0]["message"]
            return (msg.get("content") or "") + "\n" + \
                (msg.get("reasoning_content") or "")
        except urllib.error.HTTPError as ex:
            last = ex
            if ex.code == 429:
                time.sleep(60 * (attempt + 1))
                continue
            raise
        except Exception as ex:
            last = ex
            time.sleep(10)
    raise last


def run_model(model):
    rng = np.random.default_rng(123)
    seqs, meta, _ = build()
    a_items = [(seqs[i], meta[i]["s"]) for i in range(len(seqs))]
    X, y, _ = make_dataset(poch_cum, seed=777)
    order = rng.permutation(len(X))[:20]
    examples = []
    for si, s in enumerate(SIGS):
        idx = [i for i in order[:8] if y[i] == si][:1]
        examples.append((s, X[idx[0]]))
    b_items = [(X[i], SIGS[y[i]]) for i in order[8:8 + 20]]

    res = {"B": [], "A": []}
    print(f"=== {model}: B-counterfactual ===", flush=True)
    for seq, s in b_items:
        d = parse_digit(ask(model, fewshot_prompt(examples, seq)))
        res["B"].append(int(d == str(s)))
        print(f"  true={s} {'OK' if d == str(s) else f'X({d})'}", flush=True)
    print(f"=== {model}: A-lit ===", flush=True)
    for seq, s in a_items:
        d = parse_digit(ask(model, fewshot_prompt(examples, seq)))
        res["A"].append(int(d == str(s)))
        print(f"  true={s} {'OK' if d == str(s) else f'X({d})'}", flush=True)
    return {"B_acc": round(float(np.mean(res["B"])), 3),
            "A_acc": round(float(np.mean(res["A"])), 3),
            "n": {"B": len(res["B"]), "A": len(res["A"])},
            "raw": res}


def main():
    models = sys.argv[1:] or ["deepseek-v4.1-flash", "deepseek-v4-flash",
                              "minimax-m3", "kimi-k2.8-preview"]
    allres = {}
    if os.path.exists("p17b_models_results.json"):
        allres = json.load(open("p17b_models_results.json"))
    for m in models:
        if m in allres:
            print(f"skip {m} (already scored)")
            continue
        try:
            allres[m] = run_model(m)
        except Exception as ex:
            allres[m] = {"error": f"{type(ex).__name__}: {ex}"[:200]}
        json.dump(allres, open("p17b_models_results.json", "w"), indent=1)
        print(f"--> {m}: {json.dumps(allres[m].get('B_acc', allres[m]))}",
              flush=True)
    print("\n=== summary (chance 0.25; bands on B) ===")
    for m, r in allres.items():
        if "B_acc" in r:
            band = ("CONFIRMED" if r["B_acc"] >= 0.70 else
                    "PARTIAL" if r["B_acc"] >= 0.45 else
                    "MEMORY-ONLY" if r["A_acc"] >= 0.70 else "INCONCLUSIVE")
            print(f"  {m:24s} B={r['B_acc']:.3f} A={r['A_acc']:.3f} -> {band}")


if __name__ == "__main__":
    main()
