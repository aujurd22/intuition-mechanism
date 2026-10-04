# -*- coding: utf-8 -*-
"""G2B LLM-side exam — the SAME registered items as the human package.

Mirrors g2b_package/学习页.md + 考页.md in text form:
  call 1: 16 train pairs -> exam1 (12 plurals + confidence + scope question)
  call 2: cipher legend  -> exam2 (8 cipher stems -> suffix um/is/ok)

Predictions tested (G2B preregistration, docs/G2B_LEARNABLE_DOMAIN.md):
  exam1 near-ceiling (in-context learning), exam2 -> if surface-form binding,
  collapse toward 1/3; structural transfer -> high. Scope self-awareness
  compared qualitatively with the human 0-2 rubric.
"""
import os, sys, json, re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEY = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "answer_key.json"), encoding="utf-8"))

TRAIN = "\n".join(f"{r['stem']} -> {r['plural']}" for r in KEY["train"])
EXAM1 = "\n".join(f"{i+1}. {r['stem']}"
                  for i, r in enumerate(KEY["exam1"]))
LEGEND = "  ".join(f"{v}={k}" for k, v in KEY["cipher_legend"].items())
EXAM2 = "\n".join(f"{i+14}. {r['cipher']}" for i, r in enumerate(KEY["exam2"]))

PROMPT1 = f"""A fictional language called Star-Speech marks plural nouns with a
suffix. Here are all 16 examples of singular -> plural:

{TRAIN}

(The alphabet is only: b d g k p t a i u.)

Learn the pattern from these examples, then answer for 12 NEW words. For each,
give the plural and say whether you are SURE or GUESSING. Then answer one final
question. Answer EXACTLY in this format:

1. <plural> <SURE|GUESSING>
2. <plural> <SURE|GUESSING>
...
12. <plural> <SURE|GUESSING>
SCOPE: <one or two sentences: when could your method fail? what is its range of validity?>

The 12 new words:
{EXAM1}"""

PROMPT2 = f"""Star-Speech words can also be written in a symbol script. Legend:
{LEGEND}

You already know how Star-Speech forms plurals (suffixes: um, is, ok).
For each symbol-written NEW word below, decide which suffix it takes.
Answer EXACTLY one line per item, format: "N. <um|is|ok>"

{EXAM2}"""

MODELS = ["deepseek-v4-flash", "glm-5.3-flash", "doubao-seed-2.1-lite"]

def parse1(text):
    plurals, confs = [], []
    for line in text.splitlines():
        m = re.match(r"\s*(\d+)\.\s*\S*?(um|is|ok)\b.*?(SURE|GUESSING)", line, re.I)
        if m:
            plurals.append(m.group(2).lower())
            confs.append(m.group(3).upper())
    return plurals, confs

def parse2(text):
    out = {}
    for line in text.splitlines():
        m = re.match(r"\s*(\d+)\.\s*\**\s*(um|is|ok)\b", line, re.I)
        if m:
            out[int(m.group(1))] = m.group(2).lower()
    return [out.get(i) for i in range(14, 22)]

def main():
    import importlib, llm_client
    results = {}
    for model in MODELS:
        os.environ["ARK_MODEL"] = model
        importlib.reload(llm_client)
        t1 = llm_client.ask(PROMPT1)
        p1, conf = parse1(t1)
        truth1 = [r["plural"][-2:] if r["plural"].endswith(("um", "ok")) else "is"
                  for r in KEY["exam1"]]
        acc1 = sum(a == t for a, t in zip(p1, truth1)) / 12 if p1 else 0.0
        sure_idx = [i for i, c in enumerate(conf) if c == "SURE"]
        guess_idx = [i for i, c in enumerate(conf) if c == "GUESSING"]
        cal = None
        if sure_idx and guess_idx:
            cal = (sum(p1[i] == truth1[i] for i in sure_idx) / len(sure_idx)
                   - sum(p1[i] == truth1[i] for i in guess_idx) / len(guess_idx))
        scope = t1.split("SCOPE:")[-1].strip()[:500] if "SCOPE:" in t1 else ""
        t2 = llm_client.ask(PROMPT2)
        p2 = parse2(t2)
        truth2 = [r["plural"][-2:] if r["plural"].endswith(("um", "ok")) else "is"
                  for r in KEY["exam2"]]
        acc2 = sum(a == t for a, t in zip(p2, truth2)) / 8 if p2 else 0.0
        results[model] = {
            "exam1_acc": round(acc1, 3), "exam1_parsed": len(p1),
            "calibration_sure_minus_guess": round(cal, 3) if cal is not None else None,
            "scope_answer": scope,
            "exam2_acc": round(acc2, 3), "exam2_parsed": len(p2),
            "raw1": t1[:2000], "raw2": t2[:1000],
        }
        print(f"{model}: exam1 {acc1:.2f} (parsed {len(p1)}/12), "
              f"exam2 {acc2:.2f} (parsed {len(p2)}/8)", flush=True)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "g2b_llm_results.json")
    json.dump(results, open(out, "w", encoding="utf-8"), indent=1)
    print("saved", out)

if __name__ == "__main__":
    main()
