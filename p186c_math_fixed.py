"""P186-c: corrected math-track stats — 3 models x 3 seeds x 32 probes with
the FIXED per-chunk builder (rule injected per call). Replaces the retracted
76-79% plateau numbers."""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
MODELS = ["deepseek-v4-flash", "doubao-seed-2.1-lite", "kimi-k2.8-preview"]
SEEDS = [0, 1, 2]

def parse(ans, n):
    m = {}
    for i in range(1, n + 1):
        mm = re.search(rf"{i}\s*[:\-]\s*(RATIONAL|NOT)\b", ans, re.I)
        if mm:
            m[i] = mm.group(1).upper()
    return [m.get(i) for i in range(1, n + 1)]

def main():
    import importlib
    import llm_client
    from p153a_probe_sets import build_math_probes
    probes = build_math_probes(seed=20261001)
    truth = [p["truth"] for p in probes]
    law = json.load(open("p138_plugin_test.json", encoding="utf-8"))["testset"][:14]
    law_lines = [f"d={t['d']}: x0={t['x0']}, lambda={t['lam']} -> "
                 + ("RATIONAL" if t["truth"] else "NOT") for t in law]
    law_prompt = ("You are shown parameter pairs of Ramanujan-type 1/pi series "
                  "identities. Some d are RATIONAL rows (1/x6 an exact integer), "
                  "the rest are NOT.\n" + "\n".join(law_lines)
                  + "\n\nTASK: State the hidden rule separating RATIONAL from "
                  "NOT in ONE sentence (applicable to unseen d).\nFormat:\nRULE: <sentence>")
    out = {}
    for model in MODELS:
        os.environ["ARK_MODEL"] = model
        importlib.reload(llm_client)
        seed_accs = []
        all_errs = []
        rows_total = rows_ok = 0
        for seed in SEEDS:
            rule_m = re.search(r"RULE:\s*(.+)", llm_client.ask(law_prompt), re.S)
            rule = rule_m.group(1).strip() if rule_m else "(none stated)"
            preds = []
            CHUNK = 10
            for s in range(0, len(probes), CHUNK):
                block = probes[s:s + CHUNK]
                lines = [f"{i}: d={p['d']}, x0={p['x0']}, lambda={p['lam']}"
                         for i, p in enumerate(block, 1)]
                prompt = (f"Discovered rule: {rule}\n\n"
                          "Using the rule you discovered, classify each held-out d.\n"
                          + "\n".join(lines)
                          + "\nAnswer one line each: '<i>: RATIONAL' or '<i>: NOT'.")
                vals = parse(llm_client.ask(prompt), len(block))
                preds += vals
            ok = sum(int(p == t) for p, t in zip(preds, truth))
            ridx = [i for i, p in enumerate(probes) if p["kind"] == "row_consistency"]
            rok = sum(int(preds[i] == truth[i]) for i in ridx)
            rows_total += len(ridx); rows_ok += rok
            errs = [probes[i]["d"] for i in range(len(probes)) if preds[i] != truth[i]]
            all_errs += errs
            seed_accs.append(round(100 * ok / len(probes), 1))
            print(f"{model} seed{seed}: {ok}/32 errs={errs}")
        out[model] = {"seed_accs": seed_accs, "mean": round(sum(seed_accs) / 3, 1),
                      "row_recall": f"{rows_ok}/{rows_total}",
                      "err_counts": {str(d): all_errs.count(d) for d in sorted(set(all_errs))}}
        print(f"{model} MEAN {out[model]['mean']}%  row_recall {out[model]['row_recall']}")
    json.dump(out, open("p186c_math_fixed.json", "w"), indent=1)
    print("saved p186c_math_fixed.json")

if __name__ == "__main__":
    main()
