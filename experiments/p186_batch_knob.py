"""P186: Arena math-track error anatomy + batch knob.

FINDING 1 (anatomy, from existing p153_v2 data): row recall 28-39% vs non-row
rejection 83-91% — the 76-79% plateau is asymmetric. Errors are IDENTICAL
across 3 models x 3 seeds (same misses d=7,1,13; same false RATIONALs
{122,420,421,653,809,991}) — stimulus-determined, not model noise.

FINDING 2 (this run): batch knob. Same law set (14 examples), same 32 probes
in the same fixed order (seed 20261001); only the apply-call chunking varies
(CHUNK in {8, 32}). If accuracy depends on chunk size, the Arena plateau is a
BATCHING artifact. Single-call 8-probe interrogation scored 8/8 on the
error ids — prediction: small chunks >> big chunks.
"""
import os, sys, json, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
MODELS = ["deepseek-v4-flash", "doubao-seed-2.1-lite"]
CHUNKS = [8, 32]
SEEDS = [0, 1]


def parse(ans, n):
    m = {}
    for i in range(1, n + 1):
        mm = re.search(rf"{i}\s*[:\-]\s*(RATIONAL|NOT)\b", ans, re.I)
        if mm:
            m[i] = mm.group(1).upper()
    return [m.get(i) for i in range(1, n + 1)]


def main():
    from llm_client import ask
    from p153a_probe_sets import build_math_probes

    probes = build_math_probes(seed=20261001)  # the exact fixed order
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
        import importlib
        import llm_client
        importlib.reload(llm_client)
        out[model] = {}
        for seed in SEEDS:
            rule = ask(law_prompt).strip()
            for chunk in CHUNKS:
                preds = [None] * len(probes)
                for s in range(0, len(probes), chunk):
                    block = probes[s:s + chunk]
                    lines = [f"{i}: d={p['d']}, x0={p['x0']}, lambda={p['lam']}"
                             for i, p in enumerate(block, 1)]
                    prompt = (f"Discovered rule: {rule}\n\n"
                              "Using the rule you discovered, classify each "
                              "held-out d.\n" + "\n".join(lines)
                              + "\nAnswer one line each: '<i>: RATIONAL' or '<i>: NOT'.")
                    ans = ask(prompt)
                    vals = parse(ans, len(block))
                    for j, v in enumerate(vals):
                        preds[s + j] = v
                truth = [p["truth"] for p in probes]
                correct = sum(int(p == t) for p, t in zip(preds, truth))
                rows_idx = [i for i, p in enumerate(probes)
                            if p["kind"] == "row_consistency"]
                rows_ok = sum(int(preds[i] == truth[i]) for i in rows_idx)
                key = f"seed{seed}_chunk{chunk}"
                out[model][key] = {
                    "acc": correct / len(probes),
                    "row_recall": rows_ok / len(rows_idx),
                    "errors": [{"d": probes[i]["d"], "pred": preds[i]}
                               for i in range(len(probes)) if preds[i] != truth[i]],
                    "unparsed": sum(int(v is None) for v in preds),
                }
                print(f"{model} {key}: acc={correct}/{len(probes)} "
                      f"row_recall={rows_ok}/{len(rows_idx)} "
                      f"err_ds={[e['d'] for e in out[model][key]['errors']]}")
    json.dump(out, open("p186_batch_knob.json", "w"), indent=1)
    print("saved p186_batch_knob.json")


if __name__ == "__main__":
    main()
