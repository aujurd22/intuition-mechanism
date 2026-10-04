"""P164: Insight Boundary Benchmark — Experiment 2, the NOISE CONTROL.

Purpose: P162 showed all judges pass (declare ambiguity + pick MDL) on
clean windows.  A benchmark with zero failures is a rubber stamp.  This
experiment constructs the FAILURE condition: discovery windows where a
single perturbed term breaks the strong rule while weak rules still fit.

Design: strong-rule windows (from P154 families) with ONE term perturbed
(±1 at position k).  Now:
  - the strong rule (2^n) NO LONGER fits (broken by the perturbation)
  - weak rules (all even / increasing / x2-ish except at k) still fit
Optimal behavior (pre-registered): DETECT the anomalous term (name k or
say 'one term deviates') + either report both hypotheses or exclude the
perturbed term.
Failure mode (what we test for): silently switch to the weak rule and
declare NO ambiguity (overconfident pattern-matching on the noisy window).

3 models x 8 families x 3 noise positions (k=3,5,7) = 72 judgments.
"""
import json
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
fams = json.load(open("p154_sequence_families.json", encoding="utf-8"))

import llm_client


def run_model(model):
    os.environ["ARK_MODEL"] = model
    import importlib
    importlib.reload(llm_client)
    out = []
    for f in fams:
        disc8 = f["discovery"][:8]
        for kpos in (2, 4, 6):          # 0-based perturbation positions
            noisy = disc8[:]
            delta = 1 if noisy[kpos] % 2 == 0 else -1
            # keep parity of even families intact when possible: perturb by 2
            if noisy[kpos] % 2 == 0:
                delta = 2
            noisy[kpos] += delta
            prompt = (f"A sequence starts: {', '.join(str(x) for x in noisy)}, ...\n\n"
                      "TASK (answer all four):\n"
                      "1) RULE: state the generating rule in one short sentence.\n"
                      "2) ANOMALY: does any single term in the list deviate from "
                      "your rule? If yes, name its position (1-based). If none, "
                      "write NONE.\n"
                      "3) NEXT: predict the next 2 terms (terms 9-10).\n"
                      "4) AMBIGUITY: are multiple simple rules consistent with "
                      "these 8 terms? YES or NO.\n"
                      "Format:\nRULE: <sentence>\nANOMALY: <position or NONE>\n"
                      "NEXT: t9, t10\nAMBIGUITY: YES|NO")
            ans = llm_client.ask_chat(prompt, max_tokens=700)
            m_rule = re.search(r"RULE:\s*(.+)", ans)
            m_anom = re.search(r"ANOMALY:\s*(\d+|NONE)", ans, re.I)
            m_amb = re.search(r"AMBIGUITY:\s*(YES|NO)", ans, re.I)
            m_next = re.search(r"NEXT:\s*([-\d,\s]+)", ans)
            anom_pos = None
            if m_anom:
                tok = m_anom.group(1).upper()
                anom_pos = None if tok == "NONE" else int(tok)
            nexts = [int(x) for x in re.findall(r"-?\d+", m_next.group(1))][:2] if m_next else []
            # scoring
            detected = (anom_pos == kpos + 1)
            true9_10 = f["true_continuation"][:2]
            nexts_ok = sum(int(p == t) for p, t in zip(nexts, true9_10))
            # weak-rule capture: does the prediction continue the noisy window's
            # parity/local pattern instead of the true rule?
            entry = {"model": model, "family": f["name"], "kpos": kpos + 1,
                     "perturbed_value": noisy[kpos], "clean_value": disc8[kpos],
                     "anomaly_detected": detected,
                     "anom_pos_named": anom_pos,
                     "ambiguity": (m_amb.group(1).upper() == "YES" if m_amb else None),
                     "nexts": nexts, "true9_10": true9_10, "nexts_ok": nexts_ok,
                     "rule": (m_rule.group(1).strip() if m_rule else "")}
            out.append(entry)
            print(f"{model[:10]:>10} {f['name']:>13} k={kpos+1}: "
                  f"anom_detected={detected} amb={entry['ambiguity']} "
                  f"nexts_ok={nexts_ok}/2")
    return out


if __name__ == "__main__":
    allres = []
    for model in ("deepseek-v4-flash", "doubao-seed-2.1-lite",
                  "kimi-k2.8-preview"):
        allres.extend(run_model(model))
    json.dump(allres, open("p164_noise_control.json", "w"), indent=1)
    # summaries
    print("\n== summaries ==")
    for model in ("deepseek-v4-flash", "doubao-seed-2.1-lite",
                  "kimi-k2.8-preview"):
        rows = [e for e in allres if e["model"] == model]
        det = sum(1 for e in rows if e["anomaly_detected"])
        amb = sum(1 for e in rows if e["ambiguity"])
        nexts_ok = sum(1 for e in rows if e["nexts_ok"] == 2)
        print(f"{model:>22}: anomaly detected {det}/{len(rows)}, "
              f"ambiguity declared {amb}/{len(rows)}, "
              f"clean continuation {nexts_ok}/{len(rows)}")
    print("saved p164_noise_control.json")
