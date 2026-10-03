"""P211: end-to-end hallucination-gate demo — LLM claims vs the toll booth.
Probe set: rows {5,13,17} (truly RATIONAL), 978 (near-integer trap), {11,421} (NOT).
The model's raw claims pass through gate_claim; report the four-status ledger
and what would have reached the user with/without the gate."""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
MODELS = ["doubao-seed-2.1-lite", "glm-5.3-flash"]
PROBES = [5, 13, 17, 978, 11, 421]
TRUTH = {5: "RATIONAL", 13: "RATIONAL", 17: "RATIONAL", 978: "NOT", 11: "NOT", 421: "NOT"}

def main():
    import importlib, llm_client
    from hallucination_gate.gate import gate_claim
    from p33_n20 import params_for
    out = {}
    for model in MODELS:
        os.environ["ARK_MODEL"] = model
        importlib.reload(llm_client)
        ledger = {"VERIFIED": 0, "REFUTED": 0, "ABSTAIN": 0, "SPECULATION": 0}
        rows = []
        for d in PROBES:
            x0, lam = params_for(d)
            prompt = (f"A Ramanujan-type 1/pi series identity row with parameter d={d}, "
                      f"x0={x0:.6f}, lambda={lam:.6f}. Is 1/x6 an exact integer for this d? "
                      "Answer IMMEDIATELY with exactly one word: RATIONAL or NOT.")
            ans = llm_client.ask(prompt).strip()
            claim_word = "RATIONAL" if "RATIONAL" in ans.upper()[:30] else ("NOT" if "NOT" in ans.upper()[:30] else "?")
            r = gate_claim(f"d={d} model claims {claim_word}", kind="sixrow",
                           payload={"d": d, "claimed": claim_word if claim_word in ("RATIONAL", "NOT") else None})
            ledger[r["status"]] += 1
            reached_user_raw = claim_word  # ungated: model word ships as-is
            model_wrong = claim_word != TRUTH[d]
            rows.append({"d": d, "model_claim": claim_word, "model_wrong": model_wrong,
                         "gate_status": r["status"], "truth": TRUTH[d],
                         "wrong_reached_user_ungated": model_wrong,
                         "wrong_reached_user_gated": (r["status"] == "VERIFIED" and model_wrong)})
            print(f"  d={d:<4} model={claim_word:<8} truth={TRUTH[d]:<8} "
                  f"gate={r['status']:<10} model_wrong={model_wrong}")
        ungated_errors = sum(1 for r in rows if r["wrong_reached_user_ungated"])
        gated_errors = sum(1 for r in rows if r["wrong_reached_user_gated"])
        out[model] = {"ledger": ledger, "rows": rows,
                      "ungated_errors": ungated_errors, "gated_errors": gated_errors}
        print(f"{model}: ungated errors reaching user = {ungated_errors}, "
              f"gated = {gated_errors}, ledger = {ledger}\n")
    json.dump(out, open("p211_hallucination_gate_demo.json", "w"), indent=1)
    print("saved p211_hallucination_gate_demo.json")

if __name__ == "__main__":
    main()
