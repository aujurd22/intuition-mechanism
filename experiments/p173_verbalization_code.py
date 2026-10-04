"""P173: verbalization gap CROSS-DOMAIN — code-pass-fail domain.

P170 showed the gap is at knowledge level (50% = chance) for sci_data.
This tests whether the gap is DOMAIN-UNIVERSAL by running the same
protocol (state rule -> write code -> execute) on the code-pass-fail
domain.

If gap > 0 on code domain too -> the verbalization gap is a general
LLM property (Polanyi's paradox is universal across domains).
If gap = 0 -> the gap is domain-specific (sci_data's sign-block
structure is uniquely hard to verbalize).
"""
import sys, os, json, re, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
import llm_client

items = json.load(open("codefix_items.json", encoding="utf-8"))
disc, probes = items[:4], items[4:]

# step 1: elicit rule (same protocol as P169 Arena law elicitation)
law_lines = []
for it in disc:
    v = "PASS" if it["passes"] else "FAIL"
    law_lines.append(f"CODE:\n{it['code']}\nTESTS:\n{it['test']}\nVERDICT: {v}")
law_prompt = ("Code candidates with their tests. Some pass, some fail.\n\n"
              + "\n".join(law_lines)
              + "\n\nTASK: In ONE sentence, state how to decide pass/fail.\n"
              "Format:\nRULE: <sentence>")

MODEL = "deepseek-v4-flash"
os.environ["ARK_MODEL"] = MODEL
import importlib
importlib.reload(llm_client)
ans1 = llm_client.ask_chat(law_prompt, max_tokens=600)
m_rule = re.search(r"RULE:\s*(.+)", ans1, re.S)
stated_rule = m_rule.group(1).strip() if m_rule else "(none)"

# step 2: write code implementing the stated rule
code_prompt = (f"You stated this rule for determining whether code passes "
               f"its tests:\n\n  YOUR RULE: {stated_rule}\n\n"
               "Write a complete Python function implementing YOUR rule:\n\n"
               "```python\ndef check_code(code_str: str, test_str: str) -> str:\n"
               "    ...\n```\n\n"
               "The function receives the code and test strings and must "
               "return 'PASS' or 'FAIL'. Output ONLY the function inside "
               "a python code block.")
ans2 = llm_client.ask_chat(code_prompt, max_tokens=1200)
m_code = re.search(r"```python\n(.*?)```", ans2, re.S)
model_code = m_code.group(1) if m_code else None

results = {"model": MODEL, "stated_rule": stated_rule}
if not model_code:
    results["error"] = "no code from model"
    json.dump(results, open("p173_verbalization_code.json", "w"), indent=1)
    print(json.dumps(results, indent=1))
    sys.exit(0)

# step 3: execute the model's own code on all items
all_items = items
verdicts = []
exec_ok = True
for it in all_items:
    harness = (model_code + "\n"
               + f"import json\n"
               + f"result = check_code({json.dumps(it['code'])}, "
               + f"{json.dumps(it['test'])})\n"
               + f"print(result)\n")
    tmp = "_p173_exec.py"
    open(tmp, "w", encoding="utf-8").write(harness)
    try:
        r = subprocess.run([sys.executable, tmp], capture_output=True,
                           timeout=10, text=True)
        v = r.stdout.strip().split("\n")[-1] if r.stdout.strip() else ""
        verdicts.append(v)
    except Exception as e:
        verdicts.append(None)

# step 4: score
tp = fp = tn = fn = err = 0
for it, v in zip(all_items, verdicts):
    truth = "PASS" if it["passes"] else "FAIL"
    if v is None:
        err += 1
    elif v.upper().strip("'\"") == "PASS":
        if truth == "PASS":
            tp += 1
        else:
            fp += 1
    else:
        if truth == "FAIL":
            fn += 1
        else:
            fn += 1  # model said FAIL but truth was PASS

code_acc = round(100 * (tp + fn) / max(len(all_items), 1), 1)
results["code_execution"] = {
    "accuracy": code_acc, "tp": tp, "fp": fp, "tn": fn, "err": err}
results["code_snippet_head"] = model_code[:200]
json.dump(results, open("p173_verbalization_code.json", "w"), indent=1)
print(f"stated rule code accuracy: {code_acc}% ({tp}+{fn} of {len(all_items)})")
print(f"code head: {model_code[:150]}")
PYEOF