"""P153: Arena v2 MEGA-RUN — quantity + variety for statistical credibility.

Scale (per model):
  3 SDB tracks   math (32 probes) / sci-data (30) / code-pattern (20)
                 law stated once per seed, probes batched ~10/call
  5 elementary   date_logic, string_ops, list_ops, numeric, dict_ops (28)
  3 seeds x 3 models => ~900 item-level judgments, ~100 API calls

Outputs: p153_v2_{model}.json
  {track: {seeds: {seed: [{id, truth, pred}...]}, aggregate: {...}}}
"""
import os
import sys
import json
import random
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
MODELS = ["deepseek-v4-flash", "doubao-seed-2.1-lite", "kimi-k2.8-preview"]
SEEDS = [0, 1, 2]
CHUNK = 10


def parse_generic(ans, n, tokens):
    m = {}
    for i in range(1, n + 1):
        mm = re.search(rf"{i}\s*[:\-]\s*({tokens})\b", ans, re.I)
        if mm:
            m[i] = mm.group(1).upper()
    return [m.get(i) for i in range(1, n + 1)]


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def math_tracks(probes):
    law_set = json.load(open("p138_plugin_test.json",
                             encoding="utf-8"))["testset"][:14]
    law_lines = [f"d={t['d']}: x0={t['x0']}, lambda={t['lam']} -> "
                 + ("RATIONAL" if t["truth"] else "NOT") for t in law_set]
    law_prompt = ("You are shown parameter pairs of Ramanujan-type 1/pi series "
                  "identities. Some d are RATIONAL rows (1/x6 an exact integer), "
                  "the rest are NOT.\n" + "\n".join(law_lines)
                  + "\n\nTASK: State the hidden rule separating RATIONAL from "
                  "NOT in ONE sentence (applicable to unseen d).\n"
                  "Format:\nRULE: <sentence>")
    probe_lines = [f"{i}: d={p['d']}, x0={p['x0']}, lambda={p['lam']}"
                   for i, p in enumerate(probes, 1)]
    apply_head = ("Using the rule you discovered, classify each held-out d.\n"
                  + "\n".join(probe_lines)
                  + "\nAnswer one line each: '<i>: RATIONAL' or '<i>: NOT'.")
    return {"law_prompt": law_prompt, "truth": [p["truth"] for p in probes],
            "tokens": "RATIONAL|NOT", "law_call": law_prompt,
            "apply_head": apply_head,
            "probes": [{"id": p["d"]} for p in probes]}


def sci_tracks(probes):
    first = probes[:4]
    law_lines = []
    for i, p in enumerate(first, 1):
        law_lines.append(f"--- Series {i} ---\n{p['series']}")
    law_prompt = ("Below are sampled signals from a physical process. Some are "
                  "NORMAL, some are not.\n" + "\n".join(law_lines)
                  + "\n\nTASK: State in ONE sentence the law (period, damping, "
                  "what makes a series anomalous).\nFormat:\nRULE: <sentence>")
    truth = ["ANOMALOUS" if p["anomalous"] else "NORMAL" for p in probes]

    def series_block(chunk):
        body = ""
        for i, p in enumerate(chunk, 1):
            body += f"--- Series {i} ---\n{p['series']}\n"
        return body

    return {"law_prompt": law_prompt, "truth": truth,
            "tokens": "NORMAL|ANOMALOUS",
            "apply_head_builder": series_block,
            "probes": [{"id": i, "series": p["series"]}
                       for i, p in enumerate(probes, 1)]}


def code_tracks(probes):
    law_lines = []
    for i, p in enumerate([p for p in probes if p["truth"] == "PURE"][:3], 1):
        law_lines.append(f"--- Function {i} (PURE) ---\n{p['code']}")
    for i, p in enumerate([p for p in probes if p["truth"] == "IMPURE"][:3], 4):
        law_lines.append(f"--- Function {i} (IMPURE) ---\n{p['code']}")
    law_prompt = ("Functions from a team codebase — ALL pass their tests, but "
                  "some violate the team design rule.\n" + "\n".join(law_lines)
                  + "\n\nTASK: State in ONE sentence the design rule that "
                  "separates PURE from IMPURE.\nFormat:\nRULE: <sentence>")
    truth = [p["truth"] for p in probes]

    def fn_block(chunk):
        body = ""
        for i, p in enumerate(chunk, 1):
            body += f"--- Function {i} (tests pass) ---\n{p['code']}\n"
        return body

    return {"law_prompt": law_prompt, "truth": truth,
            "tokens": "PURE|IMPURE",
            "apply_head_builder": fn_block,
            "probes": [{"id": i, "code": p["code"], "test": p["test"]}
                       for i, p in enumerate(probes, 1)]}


def elementary_track(name, items):
    return {"law_prompt": None,
            "truth": ["PASS" if it["passes"] else "FAIL" for it in items],
            "tokens": "PASS|FAIL",
            "apply_head_builder": lambda chunk: "\n".join(
                f"--- Candidate {i} ---\nCODE:\n{it['code']}\nTESTS:\n{it['test']}"
                for i, it in enumerate(chunk, 1)),
            "probes": [{"id": it["id"], "code": it["code"],
                        "test": it["test"]} for it in items]}


def run_model(model):
    os.environ["ARK_MODEL"] = model
    import importlib
    import llm_client
    importlib.reload(llm_client)
    from p153a_probe_sets import (build_math_probes, build_sci_probes,
                                  build_code_probes)

    tracks = {
        "math": math_tracks(build_math_probes()),
        "sci_data": sci_tracks(build_sci_probes()),
        "code_pattern": code_tracks(build_code_probes()),
    }
    for name, items in json.load(open("p151_domains.json",
                                      encoding="utf-8")).items():
        tracks[name] = elementary_track(name, items)

    model_out = {}
    for tname, tr in tracks.items():
        tdata = {"seeds": {}, "truth": tr["truth"],
                 "ids": [p["id"] for p in tr["probes"]]}
        for seed in SEEDS:
            rng = random.Random(seed * 1000 + (hash(tname) % 997))
            rule = None
            if tr["law_prompt"]:
                m = re.search(r"RULE:\s*(.+)",
                              llm_client.ask_chat(tr["law_prompt"],
                                                  max_tokens=800), re.S)
                rule = m.group(1).strip() if m else "(none stated)"
            judgments = []
            for chunk in chunks(tr["probes"], CHUNK):
                builder = tr.get("apply_head_builder")
                body = builder(chunk) if builder else tr["apply_head"]
                tail = (f"Discovered rule: {rule}\n\n" if rule else "") + body
                tail += ("\nAnswer one line per candidate, in order: "
                         f"'<i>: {tr['tokens'].replace('|', '' or ' or ')}'.".replace(
                             tr["tokens"], " or ".join(tr["tokens"].split("|"))))
                ans = llm_client.ask_chat(tail, max_tokens=1500)
                preds = parse_generic(ans, len(chunk), tr["tokens"])
                for p, it in zip(preds, chunk):
                    judgments.append({"id": it["id"], "truth": None,
                                      "pred": p})
            # attach truth by order within chunk reconstruction
            all_items = list(chunks(tr["probes"], CHUNK))
            flat = [it for ch in all_items for it in ch]
            for jd, it in zip(judgments, flat):
                jd["truth"] = tr["truth"][tr["probes"].index(
                    next(p for p in tr["probes"] if p["id"] == jd["id"]))]
            tdata["seeds"][seed] = judgments
        # aggregate
        accs = []
        for seed, jds in tdata["seeds"].items():
            valid = [j for j in jds if j["pred"] is not None]
            accs.append(round(100 * sum(int(j["pred"] == j["truth"])
                                        for j in valid) / max(len(valid), 1), 1))
        tdata["aggregate"] = {"seed_accs": accs,
                              "mean_acc": round(sum(accs) / len(accs), 1),
                              "n_items": len(tr["probes"])}
        model_out[tname] = {k: tdata[k] for k in ("aggregate", "ids")}
        model_out[tname]["seeds"] = tdata["seeds"]
        print(f"{model:>22} {tname:>13}: {tdata['aggregate']}")
    return model_out


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else MODELS[0]
    res = run_model(model)
    json.dump(res, open(f"p153_v2_{model}.json", "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    print(f"saved p153_v2_{model}.json")
