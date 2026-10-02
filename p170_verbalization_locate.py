"""P170: WHERE is the verbalization gap — statement level or code level?

P156 showed all 3 models' STATED rules for the sci-data domain fail
5/10 on their own discovery set.  But the models' operative judgments
run 79-94% correct.  This experiment locates the gap:

  Step 1  each model states its rule (as in P156)
  Step 2  each model WRITES PYTHON CODE implementing its own stated rule
  Step 3  the code is EXECUTED on the discovery set + discriminators
  Step 4  compare: code-verdicts vs model-judgments vs truth

Outcomes:
  code matches model judgments, both beat stated-rule-literal
    -> the gap is at STATEMENT level (the model knows, can't say)
  code matches stated-rule-literal, both fail
    -> the gap is at KNOWLEDGE level (the model truly doesn't know)
  code is correct where stated-rule-literal fails
    -> the model CAN operationalize but the verbalization was lossy
"""
import sys, os, json, re, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
setup = json.load(open("p156_underdet_setup.json", encoding="utf-8"))
elicited = json.load(open("p156_elicited_rules.json", encoding="utf-8"))
disc = setup["disc"]
discrim = setup["discrim"]

CODE_PROMPT = """You stated this rule for distinguishing ANOMALOUS from NORMAL
signal series:

  YOUR RULE: {rule}

Write a complete Python function implementing YOUR rule EXACTLY as stated:

```python
def is_anomalous(series: list) -> bool:
    ...
```

The function receives a list of floats (the signal samples) and must
return True if ANOMALOUS, False if NORMAL.  Output ONLY the function
inside a python code block."""

results = {}
for model, rule in elicited.items():
    os.environ["ARK_MODEL"] = model
    import importlib
    import llm_client
    importlib.reload(llm_client)

    # step 2: write code
    ans = llm_client.ask_chat(
        CODE_PROMPT.format(rule=rule), max_tokens=1200)
    m = re.search(r"```python\n(.*?)```", ans, re.S)
    code = m.group(1) if m else None

    if not code:
        results[model] = {"error": "no code block in response"}
        continue

    # step 3: execute on discovery + discriminators
    test_prog = code + """

# test harness
import json, sys
data = json.load(open("p156_underdet_setup.json"))
results = []
for o in data["disc"]:
    results.append({"anomalous": o["anomalous"], "pred": is_anomalous(o["series"])})
for p in data["discrim"]:
    results.append({"anomalous": p["anomalous"], "pred": is_anomalous(p["series"])})
print(json.dumps(results))
"""
    tmp = f"_p170_test_{model.replace('-', '_')}.py"
    open(tmp, "w", encoding="utf-8").write(test_prog)
    import subprocess
    r = subprocess.run([sys.executable, tmp], capture_output=True,
                       timeout=30, text=True)
    if r.returncode != 0:
        results[model] = {"error": r.stderr[-300:]}
        continue
    preds = json.loads(r.stdout)

    # score
    n = len(preds)
    code_correct = sum(1 for p in preds if p["pred"] == p["anomalous"])
    code_acc = round(100 * code_correct / n, 1)
    results[model] = {"code_acc": code_acc, "n": n,
                      "log": f"{code_correct}/{n}"}

for model, r in results.items():
    print(model, r)
json.dump(results, open("p170_verbalization_locate.json", "w"), indent=1)
PYEOF