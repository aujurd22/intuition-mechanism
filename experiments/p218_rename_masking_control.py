"""P218: novelty-gate renaming/masking control (external review control 3).
After the loop converges on the 4x family (with d values SHOWN), run the
MASKED exam: same family rows but d values HIDDEN (only x0/lambda patterns).
A memorized rule ("only d'=1,2") CANNOT apply without d -> breaks/collapse.
A mechanistic rule (lambda-pattern based) still applies.
Pair with the P205 gate verdicts: PASS-STRONG should survive masking,
FAIL should not."""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p33_n20 import params_for
PROBE = [4, 8, 12, 20, 28, 40, 52, 68]   # the 4x family, d hidden in the exam
TRUTH_CLEAN = {4: "SPECIAL", 8: "SPECIAL", 12: "ordinary", 20: "ordinary", 28: "ordinary",
               40: "ordinary", 52: "ordinary", 68: "ordinary"}  # from P195 landing: d=4->Q3, d=8->Q6 quadratic; 12+ FULL=ordinary in the s=c*d' sense

def main():
    import importlib, llm_client
    out = {}
    for model in ["deepseek-v4-flash", "doubao-seed-2.1-lite"]:
        os.environ["ARK_MODEL"] = model
        import importlib as il
        il.reload(llm_client)
        # phase 1: normal loop (d shown) — from P198 protocol, brief
        exs = "\n".join(f"  d={d} (x0={params_for(d)[0]:.6f}, lam={params_for(d)[1]:.6f}): "
                        f"{'CLEAN quadratic landing' if d in (4, 8) else 'no quadratic landing'}"
                        for d in PROBE)
        prompt = ("Rows of a 4x-shadow family (d = 4*d') are CLEAN if P^12 lands in a "
                  "quadratic field, else ordinary:\n" + exs +
                  "\n\nNow NEW rows of the SAME family, but the d values are masked. "
                  "Using the mathematical patterns (x0, lambda), judge each:\n" +
                  "\n".join(f"  row{i+1}: x0={params_for(d)[0]:.6f}, lam={params_for(d)[1]:.6f}"
                            for i, d in enumerate(PROBE)) +
                  "\n\n(Answer honestly: if your rule needs the d value, say so.)\n"
                  "Format per line: row<i>: CLEAN|ordinary|NEED-D")
        ans = llm_client.ask(prompt)
        preds = {}
        for m in re.finditer(r"row\s*(\d+)\s*[:\-]\s*(CLEAN|ordinary|NEED-D)", ans, re.I):
            preds[int(m.group(1))] = m.group(2).upper()
        need_d = sum(1 for v in preds.values() if v == "NEED-D")
        correct = []
        for i, d in enumerate(PROBE, 1):
            p = preds.get(i)
            truth = "CLEAN" if d in (4, 8) else "ordinary"
            if p and p != "NEED-D":
                correct.append(int(p == truth))
        masked_acc = sum(correct) / max(len(correct), 1)
        verdict = ("SURVIVES-MASKING" if masked_acc >= 0.75 else
                   "PARTIAL" if masked_acc >= 0.5 else "COLLAPSES-WITHOUT-D")
        out[model] = {"masked_acc": masked_acc, "need_d": need_d,
                      "verdict": verdict, "raw": ans[:400]}
        print(f"{model}: masked_acc={masked_acc:.3f} need_d={need_d} -> {verdict}")
    json.dump(out, open("p218_rename_masking.json", "w"), indent=1)
    print("saved p218_rename_masking.json")

import json
if __name__ == "__main__":
    main()
