"""P193: ambiguity-active probe #1 — precision knob on the ambiguity sinks.
Hard probes: rows {1,3,5,7,13,17} + hard non-rows {421, 348, 147, 653, 809, 821}.
x0 displayed at 6 / 9 / 12 decimals. If the residual errors are display-driven,
higher precision separates rows (clean reciprocals) from sinks (tiny nonzero);
if rule-internal, errors persist at all precisions."""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import os as _os
MODELS = _os.environ.get("P193_MODELS", "deepseek-v4-flash,doubao-seed-2.1-lite,kimi-k2.8-preview").split(",")
ROW_D = [1, 3, 5, 7, 13, 17]
SINK_D = [421, 348, 147, 653, 809, 821]

def parse(ans, n):
    m = {}
    for i in range(1, n + 1):
        mm = re.search(rf"{i}\s*[:\-]\s*(RATIONAL|NOT)\b", ans, re.I)
        if mm:
            m[i] = mm.group(1).upper()
    return [m.get(i) for i in range(1, n + 1)]

def main():
    import importlib, llm_client
    from p33_n20 import params_for
    law = json.load(open("p138_plugin_test.json", encoding="utf-8"))["testset"][:14]
    law_lines = [f"d={t['d']}: x0={t['x0']}, lambda={t['lam']} -> "
                 + ("RATIONAL" if t["truth"] else "NOT") for t in law]
    law_prompt = ("You are shown parameter pairs of Ramanujan-type 1/pi series "
                  "identities. Some d are RATIONAL rows (1/x6 an exact integer), "
                  "the rest are NOT.\n" + "\n".join(law_lines)
                  + "\n\nTASK: State the hidden rule separating RATIONAL from "
                  "NOT in ONE sentence (applicable to unseen d).\nFormat:\nRULE: <sentence>")
    probes = ROW_D + SINK_D
    truth = ["RATIONAL"] * 6 + ["NOT"] * 6
    out = {}
    if _os.path.exists("p193_precision_probe.json"):
        out = json.load(open("p193_precision_probe.json", encoding="utf-8"))
    for model in MODELS:
        os.environ["ARK_MODEL"] = model
        importlib.reload(llm_client)
        m = re.search(r"RULE:\s*(.+)", llm_client.ask(law_prompt), re.S)
        rule = m.group(1).strip() if m else "(none)"
        out[model] = {}
        for dp in (6, 9, 12):
            lines = []
            for i, d in enumerate(probes, 1):
                x0, lam = params_for(d)
                lines.append(f"{i}: d={d}, x0={x0:.{dp}f}, lambda={lam:.{dp}f}")
            prompt = (f"Discovered rule: {rule}\n\n"
                      "Using the rule you discovered, classify each held-out d.\n"
                      + "\n".join(lines)
                      + "\nAnswer one line each: '<i>: RATIONAL' or '<i>: NOT'.")
            vals = parse(llm_client.ask(prompt), len(probes))
            rows_ok = sum(int(vals[i] == truth[i]) for i in range(6))
            sinks_ok = sum(int(vals[i] == truth[i]) for i in range(6, 12))
            out[model][f"dp{dp}"] = {"row_recall": f"{rows_ok}/6", "sink_reject": f"{sinks_ok}/6",
                                     "errs": [probes[i] for i in range(12) if vals[i] != truth[i]]}
            print(f"{model} dp{dp}: rows {rows_ok}/6  sinks {sinks_ok}/6  errs={out[model][f'dp{dp}']['errs']}")
            json.dump(out, open("p193_precision_probe.json", "w"), indent=1)
    json.dump(out, open("p193_precision_probe.json", "w"), indent=1)
    print("saved p193_precision_probe.json")

if __name__ == "__main__":
    main()
