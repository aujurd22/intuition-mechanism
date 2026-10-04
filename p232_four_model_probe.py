# -*- coding: utf-8 -*-
"""P232 probe: 4 models × 41 rules zero-shot (judgment-side thickening)."""
import os, sys, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

d = json.load(open("p232_rules_truth.json", encoding="utf-8"))
opt = d["opt"]
labeled = [r for r in d["labeled"] if r.get("good") is not None]

MODELS = ["doubao-seed-2.1-lite", "glm-5.3-flash", "deepseek-v4-flash", "kimi-k2.8-preview"]

def main():
    import importlib, llm_client
    from p33_n20 import params_for
    results = {}
    for model in MODELS:
        os.environ["ARK_MODEL"] = model
        import importlib as il
        il.reload(llm_client)
        correct = 0
        errs = []
        for r in labeled:
            d_num = 99  # placeholder d
            x0, lam = 0.05, 0.25  # placeholder params
            # extract d from the body if possible, otherwise use position
            prompt = (f"A selection heuristic for lists of numbers (values 0-100, "
                      f"length 20) is described as:\n'{r['desc']}'\n\nThe GOAL is to "
                      "maximize the sum of the 5 selected numbers. Is this heuristic "
                      "GOOD (achieves >= 97% of the best possible top-5 sum on typical "
                      "random lists) or BAD?\nAnswer exactly one word: GOOD or BAD.")
            ans = llm_client.ask(prompt).strip().upper()
            pred = 1 if "GOOD" in ans[:20] else 0
            truth = 1 if r["good"] else 0
            if pred == truth:
                correct += 1
            else:
                errs.append(r["desc"][:40])
        acc = correct / len(labeled)
        results[model] = {"acc": round(acc, 3), "correct": correct, "total": len(labeled),
                          "errors": errs}
        print(f"{model}: acc = {correct}/{len(labeled)} = {acc:.3f}  errs = {errs}")
    json.dump(results, open("p232_four_model_results.json", "w"), indent=1)
    print("saved p232_four_model_results.json")

if __name__ == "__main__":
    main()
