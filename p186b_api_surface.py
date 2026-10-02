"""P186-b: isolate the API-surface variable. Same law set, same 32 probes,
same rule injection — only ask (Responses API, reasoning minimal) vs
ask_chat (chat completions, thinking disabled) varies."""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def parse(ans, n):
    m = {}
    for i in range(1, n + 1):
        mm = re.search(rf"{i}\s*[:\-]\s*(RATIONAL|NOT)\b", ans, re.I)
        if mm:
            m[i] = mm.group(1).upper()
    return [m.get(i) for i in range(1, n + 1)]

def run(path_fn, label):
    from llm_client import ask_chat
    from p153a_probe_sets import build_math_probes
    probes = build_math_probes(seed=20261001)
    law = json.load(open("p138_plugin_test.json", encoding="utf-8"))["testset"][:14]
    law_lines = [f"d={t['d']}: x0={t['x0']}, lambda={t['lam']} -> "
                 + ("RATIONAL" if t["truth"] else "NOT") for t in law]
    law_prompt = ("You are shown parameter pairs of Ramanujan-type 1/pi series "
                  "identities. Some d are RATIONAL rows (1/x6 an exact integer), "
                  "the rest are NOT.\n" + "\n".join(law_lines)
                  + "\n\nTASK: State the hidden rule separating RATIONAL from "
                  "NOT in ONE sentence (applicable to unseen d).\nFormat:\nRULE: <sentence>")
    out = {}
    for seed in [0, 1]:
        reply = ask_chat(law_prompt, max_tokens=800)
        m = re.search(r"RULE:\s*(.+)", reply, re.S)
        rule = m.group(1).strip() if m else "(none stated)"
        CHUNK = 10
        preds = [None] * len(probes)
        for s in range(0, len(probes), CHUNK):
            block = probes[s:s + CHUNK]
            lines = [f"{i}: d={p['d']}, x0={p['x0']}, lambda={p['lam']}"
                     for i, p in enumerate(block, 1)]
            prompt = (f"Discovered rule: {rule}\n\n"
                      "Using the rule you discovered, classify each held-out d.\n"
                      + "\n".join(lines)
                      + "\nAnswer one line per candidate, in order: '<i>: RATIONAL or NOT'.")
            ans = path_fn(prompt)
            vals = parse(ans, len(block))
            for j, v in enumerate(vals):
                preds[s + j] = v
        truth = [p["truth"] for p in probes]
        ok = sum(int(p == t) for p, t in zip(preds, truth))
        rows_idx = [i for i, p in enumerate(probes) if p["kind"] == "row_consistency"]
        rows_ok = sum(int(preds[i] == truth[i]) for i in rows_idx)
        errs = [probes[i]["d"] for i in range(len(probes)) if preds[i] != truth[i]]
        out[seed] = {"acc": ok / 32, "row_recall": rows_ok / 6, "errors": errs,
                     "unparsed": sum(int(v is None) for v in preds)}
        print(f"{label} seed{seed}: acc={ok}/32 row_recall={rows_ok}/6 "
              f"errs={errs} unparsed={out[seed]['unparsed']}")
    return out

if __name__ == "__main__":
    os.environ.setdefault("ARK_MODEL", "deepseek-v4-flash")
    import importlib
    import llm_client
    importlib.reload(llm_client)
    res = {}
    res["ask_chat"] = run(llm_client.ask_chat, "ask_chat")
    res["ask"] = run(llm_client.ask, "ask")
    json.dump(res, open("p186b_api_surface.json", "w"), indent=1)
    print("saved p186b_api_surface.json")
