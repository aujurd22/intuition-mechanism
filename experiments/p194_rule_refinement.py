"""P194: rule-refinement loop v1 (L4 loop closure: error -> update -> retest).
Round 0: law elicitation + probe the 12 (6 rows + 6 sinks).
Round 1: feed back ONLY the misclassified (d, truth) pairs, ask for a revised
rule, re-probe. Measure: does one refinement round clear the sinks without
breaking the rows? Cost accounting: extra calls per cleared bit."""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
MODELS = ["deepseek-v4-flash", "doubao-seed-2.1-lite"]
ROW_D = [1, 3, 5, 7, 13, 17]
SINK_D = [421, 348, 147, 653, 809, 821]

def parse(ans, n):
    m = {}
    for i in range(1, n + 1):
        mm = re.search(rf"{i}\s*[:\-]\s*(RATIONAL|NOT)\b", ans, re.I)
        if mm:
            m[i] = mm.group(1).upper()
    return [m.get(i) for i in range(1, n + 1)]

def probe(llm_client, rule, probes, dp=6):
    from p33_n20 import params_for
    lines = []
    for i, d in enumerate(probes, 1):
        x0, lam = params_for(d)
        lines.append(f"{i}: d={d}, x0={x0:.{dp}f}, lambda={lam:.{dp}f}")
    prompt = (f"Discovered rule: {rule}\n\n"
              "Using the rule you discovered, classify each held-out d.\n"
              + "\n".join(lines)
              + "\nAnswer one line each: '<i>: RATIONAL' or '<i>: NOT'.")
    return parse(llm_client.ask(prompt), len(probes))

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
    for model in MODELS:
        os.environ["ARK_MODEL"] = model
        importlib.reload(llm_client)
        # draw rules until one actually errs (rule-quality variance), max 5 draws
        for draw in range(5):
            m = re.search(r"RULE:\s*(.+)", llm_client.ask(law_prompt), re.S)
            rule = m.group(1).strip() if m else "(none)"
            vals = probe(llm_client, rule, probes)
            errs = [(probes[i], truth[i]) for i in range(12) if vals[i] != truth[i]]
            if errs:
                break
        rounds = [{"rule": rule[:400], "errs": [e[0] for e in errs], "n_errs": len(errs)}]
        print(f"{model} round0 (draw {draw}): {len(errs)} errs {sorted(set(e[0] for e in errs))}")
        # refinement rounds (max 3)
        cur_rule = rule
        for rnd in range(1, 4):
            if not errs:
                break
            fb = "\n".join(f"  d={d} is actually {t}" for d, t in errs)
            rp = (f"Your discovered rule was:\nRULE: {cur_rule}\n\n"
                  f"But it misclassified these cases:\n{fb}\n\n"
                  "TASK: Revise the rule so it correctly handles ALL the discovery "
                  "examples AND these new cases, while staying a single general "
                  "sentence.\nFormat:\nRULE: <sentence>")
            m2 = re.search(r"RULE:\s*(.+)", llm_client.ask(rp), re.S)
            cur_rule = m2.group(1).strip() if m2 else cur_rule
            vals = probe(llm_client, cur_rule, probes)
            errs = [(probes[i], truth[i]) for i in range(12) if vals[i] != truth[i]]
            rounds.append({"rule": cur_rule[:400], "errs": sorted(set(e[0] for e in errs)),
                           "n_errs": len(errs)})
            print(f"{model} round{rnd}: {len(errs)} errs {sorted(set(e[0] for e in errs))}")
        out[model] = {"rounds": rounds,
                      "final_rows": 6 - sum(1 for e in errs if e[1] == 'RATIONAL'),
                      "final_sinks": 6 - sum(1 for e in errs if e[1] == 'NOT'),
                      "calls_used": 2 + len(rounds) - 1}
    json.dump(out, open("p194_rule_refinement.json", "w"), indent=1)
    print("saved p194_rule_refinement.json")

if __name__ == "__main__":
    main()
