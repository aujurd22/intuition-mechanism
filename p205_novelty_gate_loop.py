"""P205: DISCOVERY LOOP v1 with NOVELTY GATE (external review item 1).
P198's failure mode: verified memorization passes C^V. Gate design:
after the loop converges on the 4x-family, run the COUNTERFACTUAL FAMILY
exam (9x-shadow, 11 rows, ground truth ALL FULL — computed p205_truth_9x.json).
Scoring:
  PASS-STRONG: predicts FULL for all 9x rows AND explicitly limits the rule's
               scope to the 4x family (mechanism awareness)
  PASS-WEAK:   predicts FULL but claims the rule transfers
  FAIL:        predicts specific s values in the 9x family (memorized-rule extrapolation)
"""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import os as _os
MODELS = _os.environ.get("P205_MODELS", "deepseek-v4-flash,doubao-seed-2.1-lite").split(",")
ALL_D = [4, 8, 12, 20, 28, 40, 52, 68, 140, 220, 308]
TRUTH = {4: 3, 8: 6}
GENS = json.load(open("p198_truth_newrows.json"))  # genus gens per d
T9 = {int(k): v for k, v in json.load(open("p205_truth_9x.json")).items()}
D9 = sorted(T9)

def parse_preds(ans):
    out = {}
    if _os.path.exists("p205_novelty_gate.json"):
        out = json.load(open("p205_novelty_gate.json", encoding="utf-8"))
    for line in ans.splitlines():
        m = re.search(r"d\s*=\s*(\d+)\s*[:\-]\s*(FULL|LANDING\s*s\s*=\s*(\d+))", line, re.I)
        if m:
            out[int(m.group(1))] = "FULL" if m.group(2).upper().startswith("FULL") else int(m.group(3))
    return out

def main():
    import importlib, llm_client
    out = {}
    if _os.path.exists("p205_novelty_gate.json"):
        out = json.load(open("p205_novelty_gate.json", encoding="utf-8"))
    for model in MODELS:
        os.environ["ARK_MODEL"] = model
        importlib.reload(llm_client)
        history = ""
        rounds = []
        # ---- phase 1: discovery loop on 4x family (as P198) ----
        for rnd in range(1, 3):
            seed_rows = "\n".join(
                f"  d={d} (genus generators {GENS[str(d)]['gens']}): landing Q(sqrt({TRUTH[d]}))"
                for d in sorted(TRUTH))
            task = (f"Your previous rule failed on:\n{history}\nRevise and predict ALL rows.\n") if history else ""
            prompt = (
                "BACKGROUND: for special denominators d, P^12(tau0) lands in a quadratic "
                "field Q(sqrt(s)). Known six prime rows: s = c*d with c in {1,2,3} by "
                "d mod 3 and d mod 4.\n\nNEW FAMILY (4x-shadows): two rows solved:\n"
                + seed_rows +
                f"\n\nRemaining rows: " + ", ".join(f"d={d} (generators {GENS[str(d)]['gens']})" for d in ALL_D if d not in TRUTH) +
                f"\n\nTASK 1: state a rule predicting quadratic landing vs FULL.\n"
                "TASK 2: predict every row, format: d=<d>: LANDING s=<s>  or  d=<d>: FULL\n" + task +
                "Format:\nRULE: <sentence>\nPREDICTIONS:\n<lines>")
            ans = llm_client.ask(prompt)
            m = re.search(r"RULE:\s*(.+?)(?=\nPREDICTIONS:|\Z)", ans, re.S)
            rule = m.group(1).strip()[:400] if m else "(none)"
            preds = parse_preds(ans)
            errs = [(d, TRUTH.get(d, "FULL"), preds.get(d, "MISSING"))
                    for d in ALL_D if preds.get(d, "MISSING") != TRUTH.get(d, "FULL")]
            rounds.append({"round": rnd, "rule": rule, "n_errs": len(errs), "errs": errs})
            print(f"{model} round{rnd}: errs={len(errs)}")
            history = "\n".join(f"  d={e[0]}: truth={'FULL' if e[1]=='FULL' else 'Q(sqrt '+str(e[1])+')'}, you said {e[2]}"
                                for e in errs[:8])
            if not errs:
                break
        final_rule = rounds[-1]["rule"]
        # ---- phase 2: NOVELTY GATE — counterfactual 9x family exam ----
        gate_rows = "\n".join(
            f"  d={d} (genus generators {T9[d]['gens']})"
            for d in D9)
        gp = ("NEW FAMILY (different conductor): the 9x-shadow rows:\n" + gate_rows +
              f"\n\nYour rule: {final_rule}\n\n"
              "TASK 1: Does your rule transfer to this family, or was it specific to the "
              "previous family? Answer: TRANSFERS or SPECIFIC, with one sentence why.\n"
              "TASK 2: Predict every row: d=<d>: LANDING s=<s>  or  d=<d>: FULL\n"
              "Format:\nTRANSFER: TRANSFERS|SPECIFIC\nWHY: <sentence>\nPREDICTIONS:\n<lines>")
        gans = llm_client.ask(gp)
        gm = re.search(r"TRANSFER:\s*(TRANSFERS|SPECIFIC)", gans, re.I)
        transfer_claim = gm.group(1).upper() if gm else "(unparsed)"
        gpreds = parse_preds(gans)
        gtruth = {d: "FULL" for d in D9}
        gerrs = [(d, gpreds.get(d, "MISSING")) for d in D9 if gpreds.get(d, "MISSING") != "FULL"]
        if gerrs:
            gate = "FAIL"
        elif transfer_claim == "SPECIFIC":
            gate = "PASS-STRONG"
        else:
            gate = "PASS-WEAK"
        out[model] = {"rounds": rounds, "final_rule": final_rule,
                      "gate": gate, "transfer_claim": transfer_claim,
                      "gate_errs": gerrs, "gate_raw": gans[:500]}
        print(f"{model} NOVELTY GATE: {gate}  transfer_claim={transfer_claim}  errs={gerrs}")
        json.dump(out, open("p205_novelty_gate.json", "w"), indent=1)
    json.dump(out, open("p205_novelty_gate.json", "w"), indent=1)
    print("saved p205_novelty_gate.json")

if __name__ == "__main__":
    main()
