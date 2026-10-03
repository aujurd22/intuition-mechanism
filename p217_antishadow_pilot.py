"""P217: anti-shadow contrast pilot (G4 — P-LAW1 causal test, external review G4).
Shadow rules: window-equivalent (d <= 1200) but divergent in the test band:
  S1: d in [1,1500] and d mod 12 in {1,5}   (diverges for d in [1501,2000])
  S2: d mod 12 in {1,5} and 7 does not divide d  (diverges at 7-multiples)
Condition A (baseline): discovery examples only.
Condition B (anti-shadow): same examples + two EXPLICIT refuted-shadow notes
  (with the concrete refuted rows).
Prediction (P-LAW1 causal): B > A on shadow-divergent test rows."""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
MODELS = ["doubao-seed-2.1-lite", "glm-5.3-flash"]
SEEDS = [0, 1]

def truth(d):
    return 1 if d % 12 in (1, 5) else 0

def main():
    import importlib, llm_client
    out = {}
    test_band = list(range(1201, 2001, 7))   # 100 test rows across the band
    divergent = [d for d in test_band if d > 1500]  # where S1 diverges
    # ask a BALANCED sample covering head, tail, AND the divergent region
    asked = sorted(set(test_band[:20] + test_band[-20:] + divergent[:20]))
    for model in MODELS:
        os.environ["ARK_MODEL"] = model
        import importlib as il
        il.reload(llm_client)
        out[model] = {}
        for cond in ["A_baseline", "B_antishadow"]:
            accs, div_accs = [], []
            for seed in SEEDS:
                rng = random.Random(seed * 13 + 3)
                exs = [d for d in range(1, 1201) if truth(d)]
                sample = rng.sample(exs, 14)
                lines = "\n".join(f"  d={d}: SPECIAL" for d in sorted(sample))
                negs = [d for d in range(1, 1201) if not truth(d)][:14:2]
                lines += "\n" + "\n".join(f"  d={d}: ordinary" for d in negs)
                if cond == "B_antishadow":
                    s1_ref = next(d for d in range(1501, 1600) if truth(d) and d % 12 in (1, 5))
                    s2_ref = next(d for d in range(1501, 2000) if truth(d) and d % 7 == 0)
                    lines += (f"\n  REFUTED candidate rule 1: 'SPECIAL iff d in [1,1500] and "
                              f"d mod 12 in {{1,5}}' — refuted at d={s1_ref} (SPECIAL but > 1500).\n"
                              f"  REFUTED candidate rule 2: 'SPECIAL iff d mod 12 in {{1,5}} and "
                              f"7 does not divide d' — refuted at d={s2_ref} (SPECIAL and 7 | d).")
                prompt = ("Numbers are marked SPECIAL or ordinary based on a hidden rule:\n"
                          + lines +
                          "\n\nTASK: State the rule in one sentence, then classify:\n"
                          + "\n".join(f"  d={d}" for d in asked) +
                          "\nFormat:\nRULE: <sentence>\nCLASSIFY:\n<d>: SPECIAL|ordinary per line")
                ans = llm_client.ask(prompt)
                # parse per-line
                preds = {}
                for m in re.finditer(r"(?:d\s*=\s*)?(\d+)\s*[:\-]\s*(SPECIAL|ordinary)", ans, re.I):
                    preds[int(m.group(1))] = 1 if m.group(2).lower() == "special" else 0
                ok = [int(preds.get(d, -1) == truth(d)) for d in asked if d in preds]
                div_ok = [int(preds.get(d, -1) == truth(d)) for d in divergent if d in preds]
                acc = sum(ok) / max(len(ok), 1)
                div_acc = sum(div_ok) / max(len(div_ok), 1)
                accs.append(acc); div_accs.append(div_acc)
            out[model][cond] = {"acc": sum(accs) / len(accs),
                                "divergent_acc": sum(div_accs) / len(div_accs),
                                "seeds": [round(a, 3) for a in accs]}
            print(f"{model} {cond}: acc={out[model][cond]['acc']:.3f} "
                  f"divergent={out[model][cond]['divergent_acc']:.3f}")
    for model in MODELS:
        a, b = out[model]["A_baseline"], out[model]["B_antishadow"]
        delta = b["divergent_acc"] - a["divergent_acc"]
        out[model]["causal_delta_divergent"] = round(delta, 3)
        print(f"{model}: anti-shadow causal delta (divergent) = {delta:+.3f} "
              f"({'P-LAW1 causal SUPPORTED' if delta > 0.05 else 'no effect' if abs(delta) <= 0.05 else 'HARM'})")
    json.dump(out, open("p217_antishadow_pilot.json", "w"), indent=1)
    print("saved p217_antishadow_pilot.json")

import json, re, random
if __name__ == "__main__":
    main()
