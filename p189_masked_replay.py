"""P189: masked replay (L4-2 family formation, bare values, d-axis hidden).

Condition CLUSTER: 12 bare values (6 row-integers + 6 non-row irrationals),
UNLABELED, shuffled. Ask: which form a special family and why.
Measure: (a) family pick = exactly the 6 integers; (b) "integer" observation;
(c) hidden-parameter hypothesis (family formation beyond the surface).
Condition LABEL: same values with INT/NOT labels -> one-sentence rule.
"""
import os, sys, json, re, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import os as _os
MODELS = _os.environ.get("P189_MODELS", "deepseek-v4-flash,doubao-seed-2.1-lite,kimi-k2.8-preview").split(",")
ROWS = [8.0, 12.0, 20.0, 32.0, 104.0, 200.0]
NON = [9.348469, 25.444411, 59.851431, 72.467376, 269.897020, 1975.707274]

HYP_WORDS = ["function", "special value", "parameter", "hidden", "generat",
             "formula", "sequence", "polynomial", "equation", "evaluation",
             "exact", "integer value"]

def main():
    from llm_client import ask
    out = {}
    if _os.path.exists("p189_masked_replay.json"):
        out = json.load(open("p189_masked_replay.json", encoding="utf-8"))
    for model in MODELS:
        os.environ["ARK_MODEL"] = model
        import importlib, llm_client
        importlib.reload(llm_client)
        out[model] = {}
        for seed in [0, 1]:
            rng = random.Random(seed * 77 + 5)
            mixed = [(v, "INT") for v in ROWS] + [(v, "NOT") for v in NON]
            rng.shuffle(mixed)
            lst = "\n".join(f"  {v}" for v, _ in mixed)

            # CLUSTER condition (unlabeled)
            p1 = ("Below are 12 numbers. Some of them form a special family; "
                  "the rest do not belong.\n" + lst +
                  "\n\nTASK 1: List exactly which numbers belong to the special family.\n"
                  "TASK 2: In one or two sentences, what makes them special?\n"
                  "TASK 3: If you suspect a hidden parameter or generating rule "
                  "behind the family (something not visible in the numbers alone), "
                  "state your best guess.\n"
                  "Format:\nFAMILY: <numbers>\nSPECIAL: <sentence>\nHIDDEN: <sentence or 'none'>")
            a1 = ask(p1)
            fam_ok = all(str(v) in a1 or f"{v:.6f}" in a1 or f"{v:.0f}" in a1
                         for v in ROWS)
            any_int_note = bool(re.search(r"integer|whole number", a1, re.I))
            hyp = [w for w in HYP_WORDS if w.lower() in a1.lower()]

            # LABEL condition
            lab = "\n".join(f"  {v} -> {'SPECIAL' if t == 'INT' else 'ordinary'}"
                            for v, t in mixed)
            p2 = ("Below are 12 numbers, some marked SPECIAL and some ordinary.\n"
                  + lab +
                  "\n\nTASK: In ONE sentence, state the rule separating SPECIAL "
                  "from ordinary.\nFormat:\nRULE: <sentence>")
            a2 = ask(p2)
            m = re.search(r"RULE:\s*(.+)", a2, re.S)
            rule = m.group(1).strip()[:300] if m else a2.strip()[:300]
            rule_int = bool(re.search(r"integer|whole number", rule, re.I))

            out[model][f"seed{seed}"] = {
                "family_exact": fam_ok, "integer_noted": any_int_note,
                "hyp_words": hyp, "hyp_count": len(hyp),
                "cluster_raw": a1[:600], "rule": rule, "rule_integer": rule_int,
            }
            print(f"{model} seed{seed}: family_exact={fam_ok} int_note={any_int_note} "
                  f"hyp={len(hyp)} rule_int={rule_int}")
            json.dump(out, open("p189_masked_replay.json", "w"), indent=1)
    json.dump(out, open("p189_masked_replay.json", "w"), indent=1)
    print("saved p189_masked_replay.json")

if __name__ == "__main__":
    main()
