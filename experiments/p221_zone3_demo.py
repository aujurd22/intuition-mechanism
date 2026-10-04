"""P221: zone-3 demo — the doubao 4x-family rule (known FAIL from P205/P217)
goes through gate_zone3 and gets SHADOW-DETECTED with concrete failing rows."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
from hallucination_gate.gate import gate_zone3

def main():
    os.environ["ARK_MODEL"] = "doubao-seed-2.1-lite"
    import importlib, llm_client
    importlib.reload(llm_client)
    # the 9x family IS the shadow-divergent region for doubao's 4x rule
    rows = [{"d": d, "expect": "ordinary"} for d in
            [9, 18, 27, 45, 63, 90, 117, 153, 315, 495, 693]]  # truth: all FULL=ordinary-side
    rule = "SPECIAL iff d = 4*d' with d' in {1, 2} (i.e. d = 4 or 8); otherwise ordinary"
    r = gate_zone3(rule, llm_client.ask, rows)
    print("verdict:", r["verdict"])
    print("status :", r["status"])
    print("note   :", r["note"])
    print("failing:", r.get("failing_rows", [])[:5])
    # a TRUE mechanism rule for contrast: mod-12 rule evaluated on its own window rows
    rows2 = [{"d": d, "expect": "SPECIAL" if d % 12 in (1, 5) else "ordinary"}
             for d in [1201, 1205, 1213, 1217, 1229, 1241]]
    r2 = gate_zone3("SPECIAL iff d mod 12 in {1, 5}", llm_client.ask, rows2)
    print("\ncontrast — true mechanism rule on its own divergent band:")
    print("verdict:", r2["verdict"], "| status:", r2["status"])
    json.dump({"shadow_case": r, "mechanism_case": r2},
              open("p221_zone3_demo.json", "w"), indent=1, default=str)
    print("saved p221_zone3_demo.json")

if __name__ == "__main__":
    main()
