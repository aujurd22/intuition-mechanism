"""P212: enforce-loop demo — the user-facing data flow.
Case 1: doubao on d=421 (its chronic false positive) -> REFUTED -> regenerate -> ship.
Case 2: glm on d=978 (near-integer trap) -> machine ABSTAINs -> ship honestly labeled.
Case 3: glm on d=5 (plain row) -> VERIFIED first pass -> ship with evidence."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hallucination_gate.gate import enforce
from p33_n20 import params_for

CASES = [
    ("doubao-seed-2.1-lite", 421, "chronic false positive"),
    ("glm-5.3-flash", 978, "near-integer trap"),
    ("glm-5.3-flash", 5, "plain row"),
]

def main():
    import importlib, llm_client
    out = {}
    for model, d, note in CASES:
        os.environ["ARK_MODEL"] = model
        importlib.reload(llm_client)
        x0, lam = params_for(d)
        q = (f"A Ramanujan-type 1/pi series identity row with parameter d={d}, "
             f"x0={x0:.6f}, lambda={lam:.6f}. Is 1/x6 an exact integer for this d? "
             "Answer IMMEDIATELY with exactly one word: RATIONAL or NOT.")
        res = enforce(q, llm_client.ask, kind="sixrow", payload={"d": d},
                      extract_claim=lambda t: (
                          "RATIONAL" if "RATIONAL" in t.upper()[:80] else
                          ("NOT" if "NOT" in t.upper()[:80] else "?")))
        out[f"{model}/d={d}"] = {"note": note, **res}
        print(f"{model} d={d} ({note}):")
        print(f"  ship_status = {res['ship_status']}  rounds = {res['rounds_used']}")
        print(f"  shipped answer = {res['answer'][:100]}")
        for t in res["trace"]:
            print(f"    round{t['round']}: claim={t['claim']} gate={t['gate_status']}")
        print()
    json.dump(out, open("p212_enforce_demo.json", "w"), indent=1)
    print("saved p212_enforce_demo.json")

if __name__ == "__main__":
    main()
