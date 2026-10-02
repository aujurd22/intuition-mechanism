"""P169: Arena v2.5 — extend the C/N/V/T scoring to ALL live domains
(constrained-set, config-compliance, code-pass-fail, python-traps).

Per domain: law elicitation (labeled discovery set) once per seed, then
held-out probes scored by (a) the judge, (b) the domain's mechanical
verifier as ground-truth arbiter.
"""
import sys, os, json, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sympy import isprime
from intuition_pack.verifiers import run_verifier, register_constraint

for name, fn in [("sum_is_100", lambda o: sum(o) == 100),
                 ("len_is_7", lambda o: len(o) == 7),
                 ("all_prime", lambda o: all(isprime(x) for x in o)),
                 ("all_even", lambda o: all(x % 2 == 0 for x in o)),
                 ("strictly_increasing",
                  lambda o: all(o[i] < o[i+1] for i in range(len(o)-1))),
                 ("no_duplicates", lambda o: len(set(o)) == len(o)),
                 ("max_min_diff_30", lambda o: max(o) - min(o) == 30),
                 ("contains_20", lambda o: 20 in o)]:
    register_constraint(name, fn)


def spec_constrained():
    items = json.load(open("constrained_items.json", encoding="utf-8"))
    disc, probes = items[:5], items[5:]
    law_lines = []
    for it in disc:
        cons = "; ".join(c["text"] for c in it["constraints"])
        v = "ALL SATISFIED" if it["passes"] else "SOME VIOLATED"
        law_lines.append(f"OBJECT: {it['object']}\nCLAIMED: {cons}\nVERDICT: {v}")
    law_prompt = ("Objects with claimed constraint lists. Some objects "
                  "satisfy ALL their constraints, some violate at least one.\n\n"
                  + "\n".join(law_lines)
                  + "\n\nTASK: In ONE sentence, state how to decide whether an "
                  "object satisfies its claimed constraints.\n"
                  "Format:\nRULE: <sentence>")

    def apply_builder(chunk, rule):
        body = ""
        for i, it in enumerate(chunk, 1):
            pl = it["payload"]
            cons = "; ".join(c["text"] for c in pl["constraints"])
            body += f"--- Object {i} ---\nOBJECT {pl['object']}\nCLAIMED: {cons}\n"
        return (f"Discovered rule: {rule}\n\n{body}"
                "\nAnswer one line per object: '<i>: PASS' or '<i>: FAIL'.")

    payloads = [{"id": it["id"], "payload": {"object": it["object"],
                                             "constraints": it["constraints"]}}
                for it in probes]
    truth = ["PASS" if it["passes"] else "FAIL" for it in probes]
    return {"name": "constrained-set", "verifier": "constraint_check",
            "law_prompt": law_prompt, "apply_builder": apply_builder,
            "payloads": payloads, "truth": truth, "tokens": "PASS|FAIL",
            "disc_bits": json.dumps([it["object"] for it in disc])}


def spec_config():
    items = json.load(open("config_items.json", encoding="utf-8"))
    disc, probes = items[:4], items[4:]
    law_lines = []
    for it in disc:
        v = "COMPLIANT" if it["passes"] else "NON-COMPLIANT"
        law_lines.append(f"CONFIG: {json.dumps(it['object'])}\nVERDICT: {v}")
    law_prompt = ("Deployment configs checked against a schema (host string "
                  "lowercase; port int 1-65535; retries int 1-5; mode enum "
                  "http|grpc; tls object with enabled bool and cert string "
                  "lowercase). Some configs are COMPLIANT, some are not.\n\n"
                  + "\n".join(law_lines)
                  + "\n\nTASK: In ONE sentence, state how to decide compliance.\n"
                  "Format:\nRULE: <sentence>")

    def apply_builder(chunk, rule):
        body = ""
        for i, it in enumerate(chunk, 1):
            body += f"--- Config {i} ---\n{json.dumps(it['payload']['object'])}\n"
        return (f"Discovered rule: {rule}\n\n{body}"
                "\nAnswer one line per config: '<i>: PASS' or '<i>: FAIL'.")

    payloads = [{"id": it["id"], "payload": {"object": it["object"],
                                             "schema": it["schema"]}}
                for it in probes]
    truth = ["PASS" if it["passes"] else "FAIL" for it in probes]
    return {"name": "config-compliance", "verifier": "schema_check",
            "law_prompt": law_prompt, "apply_builder": apply_builder,
            "payloads": payloads, "truth": truth, "tokens": "PASS|FAIL",
            "disc_bits": json.dumps([it["object"] for it in disc])}


def spec_codepass():
    items = json.load(open("codefix_items.json", encoding="utf-8"))
    disc, probes = items[:4], items[4:]
    law_lines = []
    for it in disc:
        v = "PASS" if it["passes"] else "FAIL"
        law_lines.append(f"CODE:\n{it['code']}\nTESTS:\n{it['test']}\nVERDICT: {v}")
    law_prompt = ("Code candidates with their tests. Some pass, some fail.\n\n"
                  + "\n".join(law_lines)
                  + "\n\nTASK: In ONE sentence, state how to decide pass/fail.\n"
                  "Format:\nRULE: <sentence>")

    def apply_builder(chunk, rule):
        body = ""
        for i, it in enumerate(chunk, 1):
            pl = it["payload"]
            body += (f"--- Candidate {i} ---\nCODE:\n{pl['code']}\n"
                     f"TESTS:\n{pl['test']}\n")
        return (f"Discovered rule: {rule}\n\n{body}"
                "\nAnswer one line per candidate: '<i>: PASS' or '<i>: FAIL'.")

    payloads = [{"id": it["id"], "payload": {"code": it["code"],
                                             "test": it["test"]}}
                for it in probes]
    truth = ["PASS" if it["passes"] else "FAIL" for it in probes]
    return {"name": "code-pass-fail", "verifier": "pytest_check",
            "law_prompt": law_prompt, "apply_builder": apply_builder,
            "payloads": payloads, "truth": truth, "tokens": "PASS|FAIL",
            "disc_bits": json.dumps([it["code"] for it in disc])}


def spec_traps():
    items = json.load(open("python_traps_items.json", encoding="utf-8"))
    disc, probes = items[:4], items[4:]
    law_lines = []
    for it in disc:
        v = "PASS" if it["passes"] else "FAIL"
        law_lines.append(f"CODE:\n{it['code']}\nTESTS:\n{it['test']}\nVERDICT: {v}")
    law_prompt = ("Python snippets with their tests — watch for silent "
                  "semantic traps.\n\n" + "\n".join(law_lines)
                  + "\n\nTASK: In ONE sentence, state how to decide pass/fail.\n"
                  "Format:\nRULE: <sentence>")

    def apply_builder(chunk, rule):
        body = ""
        for i, it in enumerate(chunk, 1):
            pl = it["payload"]
            body += (f"--- Candidate {i} ---\nCODE:\n{pl['code']}\n"
                     f"TESTS:\n{pl['test']}\n")
        return (f"Discovered rule: {rule}\n\n{body}"
                "\nAnswer one line per candidate: '<i>: PASS' or '<i>: FAIL'.")

    payloads = [{"id": it["id"], "payload": {"code": it["code"],
                                             "test": it["test"]}}
                for it in probes]
    truth = ["PASS" if it["passes"] else "FAIL" for it in probes]
    return {"name": "python-traps", "verifier": "pytest_check",
            "law_prompt": law_prompt, "apply_builder": apply_builder,
            "payloads": payloads, "truth": truth, "tokens": "PASS|FAIL",
            "disc_bits": json.dumps([it["code"] for it in disc])}


def run_model(model):
    os.environ["ARK_MODEL"] = model
    import importlib
    import llm_client
    importlib.reload(llm_client)
    specs = [spec_constrained(), spec_config(), spec_codepass(), spec_traps()]
    model_out = {}
    for sp in specs:
        tdata = {"seeds": {}, "truth": sp["truth"],
                 "ids": [p["id"] for p in sp["payloads"]]}
        tt = {p["id"]: t for p, t in zip(sp["payloads"], sp["truth"])}
        for seed in range(3):
            m = re.search(r"RULE:\s*(.+)",
                          llm_client.ask_chat(sp["law_prompt"], max_tokens=800),
                          re.S)
            rule = m.group(1).strip() if m else "(none)"
            judgments = []
            for it in sp["payloads"]:
                ans = llm_client.ask_chat(
                    sp["apply_builder"]([it], rule), max_tokens=400)
                mm = re.search(r"\b(" + sp["tokens"] + r")\b", ans, re.I)
                pred = mm.group(1).upper() if mm else None
                judgments.append({"id": it["id"], "pred": pred})
            tdata["seeds"][seed] = judgments
        v_agree, n = 0, 0
        for seed, jds in tdata["seeds"].items():
            for jd in jds:
                payload = next(p["payload"] for p in sp["payloads"]
                               if p["id"] == jd["id"])
                mv = run_verifier(sp["verifier"], payload)["verdict"]
                n += 1
                if jd["pred"] is not None and \
                   jd["pred"].split()[0] == mv.split()[0]:
                    v_agree += 1
        accs = []
        for seed, jds in tdata["seeds"].items():
            valid = [j for j in jds if j["pred"] is not None]
            accs.append(round(100 * sum(int(j["pred"] == tt[j["id"]])
                                        for j in valid) / max(len(valid), 1), 1))
        tdata["aggregate"] = {"seed_accs": accs,
                              "mean_acc": round(sum(accs)/len(accs), 1),
                              "verify_agreement":
                                  round(100 * v_agree / max(n, 1), 1),
                              "n_items": len(sp["payloads"])}
        model_out[sp["name"]] = tdata
        print(f"{model[:18]:>18} {sp['name']:>18}: {tdata['aggregate']}")
    return model_out


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "deepseek-v4-flash"
    res = run_model(model)
    json.dump(res, open(f"p169_arena25_{model}.json", "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    print(f"saved p169_arena25_{model}.json")
