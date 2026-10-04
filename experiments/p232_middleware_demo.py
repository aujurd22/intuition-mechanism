# -*- coding: utf-8 -*-
"""P232: middleware demo — gated_ask() end-to-end on three cases.
Case 1: plain row (d=5) — should pass round 1, ship VERIFIED.
Case 2: near-integer trap (d=978) — should ship ABSTAIN round 1.
Case 3: non-row (d=11) — should pass round 1, ship VERIFIED."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
from hallucination_gate.middleware import gated_ask

def main():
    os.environ["ARK_MODEL"] = "glm-5.3-flash"
    import importlib, llm_client
    importlib.reload(llm_client)
    from p33_n20 import params_for
    out = {}
    for d, note in [(5, "plain row"), (978, "near-integer trap"), (11, "non-row")]:
        x0, lam = params_for(d)
        q = (f"A Ramanujan-type 1/pi series identity row with parameter d={d}, "
             f"x0={x0:.6f}, lambda={lam:.6f}. Is 1/x6 an exact integer for this d? "
             "Answer IMMEDIATELY with exactly one word: RATIONAL or NOT.")
        r = gated_ask(q, domain="sixrow", payload={"d": d})
        out[f"d={d}"] = {"note": note, "ship_status": r["ship_status"],
                         "rounds": r["rounds_used"], "answer": r["answer"][:120]}
        print(f"d={d:<4} ({note}): ship={r['ship_status']:<10} rounds={r['rounds_used']} "
              f"answer={r['answer'][:60]}")
    json.dump(out, open("p232_middleware_demo.json", "w"), indent=1)
    print("saved p232_middleware_demo.json")

if __name__ == "__main__":
    main()
