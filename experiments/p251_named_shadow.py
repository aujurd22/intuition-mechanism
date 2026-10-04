# -*- coding: utf-8 -*-
"""P251: stated-rule protocol on the named shadow ("multiples-extension").

P248 found the first NAMED shadow on the real d-domain: in the rich3 arm,
both models' W3 error sets were item-identical ([39,87,93,99,111,123,141] —
odd multiples of 3 with quotient >= 13, while odd multiples with quotient
<= 23 like 21/33/51/57/69 were labeled correctly). Review round-8: confirm
the shadow's EXPLICIT form with the statement-rule protocol (P170-184's
instrument, now applied to a real-domain shadow).

Protocol per model:
  round 1: label the 24 rows (W1+W3 rows, fresh context) — replicate the
           P248 rich3 setting (labels-only history);
  round 2: write the rule used as `lands(d) -> bool` in Python;
  execute the stated rule on the same rows: agreement with the model's own
  labels (does the stated rule reproduce the fingerprint?) and with truth
  (is it a shadow — passes the model's claims, fails the census?).
"""
import os, sys, json, re, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p240_validator_richness as p240
from p240_validator_richness import build_prompt, parse, verifier

ROWS = [9, 11, 13, 15, 17, 19, 21, 25, 27, 29, 33, 37,
        21, 33, 39, 51, 57, 69, 87, 93, 99, 111, 123, 141]
UNIQ = sorted(set(ROWS))
TRUTH = {d: p240.is_land(d) for d in UNIQ}
p240.TRUTH.update({d: ("land" if TRUTH[d] else "no") for d in UNIQ})

RULE_PROMPT = """You just labeled a batch of candidate d values as LAND / NO.
Now write down the rule you actually used, as a Python function:

def lands(d: int) -> bool:
    # your actual decision rule
    ...

It must return True exactly for the d values you would label LAND. Output
ONLY the code."""

MODELS = ["deepseek-v4-flash", "doubao-seed-2.1-lite"]

def main():
    import importlib, llm_client
    out = {}
    t0 = time.time()
    for model in MODELS:
        os.environ["ARK_MODEL"] = model
        importlib.reload(llm_client)
        history, labels = [], {}
        ans = llm_client.ask(build_prompt(UNIQ, "rich3", history, None))
        cur = parse(ans)
        for d in UNIQ:
            cur.setdefault(d, "NO")
        labels = cur
        wrong = sorted(d for d in UNIQ
                       if (labels[d] == "LAND") != TRUTH[d])
        history.append(verifier(None, "rich3", wrong))
        rule_code = llm_client.ask(RULE_PROMPT)
        m = re.search(r"```(?:python)?\s*(.*?)```", rule_code, re.S)
        code = m.group(1) if m else rule_code
        ns = {}
        exec_ok, stated_labels, exec_err = True, {}, None
        try:
            exec(code, ns)
            fn = ns.get("lands")
            for d in UNIQ:
                stated_labels[d] = bool(fn(d))
        except Exception as ex:
            exec_ok, exec_err = False, str(ex)
        if exec_ok:
            agree_own = sum((stated_labels[d] == (labels[d] == "LAND"))
                            for d in UNIQ)
            agree_truth = sum(stated_labels[d] == TRUTH[d] for d in UNIQ)
            fingerprint = sorted(d for d in UNIQ
                                 if stated_labels[d] != TRUTH[d])
        else:
            agree_own = agree_truth = None
            fingerprint = None
        out[model] = {
            "labels": {str(k): v for k, v in labels.items()},
            "model_wrong_set": wrong,
            "stated_rule_code": code[:800],
            "exec_ok": exec_ok, "exec_err": exec_err,
            "stated_vs_own_agreement": agree_own,
            "stated_vs_truth_correct": agree_truth,
            "stated_rule_wrong_set": fingerprint,
        }
        json.dump(out, open("p251_named_shadow.json", "w", encoding="utf-8"),
                  indent=1, ensure_ascii=False)
        print(f"[{int(time.time()-t0)}s] {model}: own wrong set {wrong} | "
              f"stated-rule vs own {agree_own}/24, vs truth {agree_truth}/24, "
              f"stated-rule wrong set {fingerprint}", flush=True)
    print(json.dumps({m: {"stated_vs_own_agreement": out[m]["stated_vs_own_agreement"],
                          "stated_vs_truth_correct": out[m]["stated_vs_truth_correct"]}
                      for m in MODELS}, indent=1))

if __name__ == "__main__":
    main()
