"""P227: dose-response of anti-shadow contrast (external review item 4).
Doses: 0 / 1 / 3 / 6 refuted-shadow notes. Models: doubao (weak, expected
beneficiary) + glm (strong, expected harmed). 3 seeds per cell. Answer:
(a) is the dose-response monotone for the weak model? (b) why does the
strong model suffer — attention dilution or hypothesis-space pollution?"""
import os, sys, json, re, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import os as _os
MODELS = _os.environ.get("P227_MODELS", "doubao-seed-2.1-lite,glm-5.3-flash").split(",")
DOSES = [0, 1, 3, 6]
SEEDS = [0, 1, 2, 3, 4]

def truth(d): return 1 if d % 12 in (1, 5) else 0

def main():
    import importlib, llm_client
    from p33_n20 import params_for
    # refuted-shadow notes pool (from real refutations: S1/S2 patterns)
    REFUTED = [
        ("SPECIAL iff d in [1,1500] and d mod 12 in {1,5}", 1513),
        ("SPECIAL iff d mod 12 in {1,5} and 7 does not divide d", 1519),
        ("SPECIAL iff d in [1,1750] and d mod 12 in {1,5}", 1753),
        ("SPECIAL iff d mod 12 in {1,5} and d mod 10 in {1,5}", 1525),
        ("SPECIAL iff d < 1800 and d mod 12 in {1,5}", 1801),
        ("SPECIAL iff d mod 12 in {1,5} and d mod 8 in {1,5}", 1529),
    ]
    test_band = sorted(set(list(range(1201, 2001, 7))[:20] + list(range(1501, 2001, 13))[:20]))
    out = {}
    if _os.path.exists("p227_dose_response.json"):
        try:
            prev = json.load(open("p227_dose_response.json", encoding="utf-8"))
            for mk, mv in prev.items():
                out.setdefault(mk, {}).update(mv)
        except Exception:
            pass
    for model in MODELS:
        os.environ["ARK_MODEL"] = model
        import importlib as il
        il.reload(llm_client)
        out[model] = {}
        for dose in DOSES:
            accs, div_accs = [], []
            for seed in SEEDS:
                rng = random.Random(seed * 17 + dose * 3 + 1)
                exs = sorted(d for d in range(1, 1201) if truth(d))
                sample = rng.sample(exs, 14)
                lines = "\n".join(f"  d={d}: SPECIAL" for d in sample)
                negs = [d for d in range(1, 1201) if not truth(d)][:14:2]
                lines += "\n" + "\n".join(f"  d={d}: ordinary" for d in negs)
                if dose > 0:
                    chosen = REFUTED[:dose]
                    ref = "\n".join(f"  REFUTED candidate: '{r[0]}' — refuted at d={r[1]}."
                                    for r in chosen)
                    lines += "\n" + ref
                prompt = ("Numbers are marked SPECIAL or ordinary by a hidden rule:\n"
                          + lines +
                          "\n\nTASK: State the rule in one sentence, then classify:\n"
                          + "\n".join(f"  d={d}" for d in test_band) +
                          "\nFormat:\nRULE: <sentence>\nCLASSIFY:\n<d>: SPECIAL|ordinary per line")
                ans = llm_client.ask(prompt)
                preds = {}
                for m in re.finditer(r"(?:d\s*=\s*)?(\d+)\s*[:\-]\s*(SPECIAL|ordinary)", ans, re.I):
                    preds[int(m.group(1))] = 1 if m.group(2).lower() == "special" else 0
                ok = [int(preds.get(d, -1) == truth(d)) for d in test_band if d in preds]
                div = [d for d in test_band if d > 1500]
                div_ok = [int(preds.get(d, -1) == truth(d)) for d in div if d in preds]
                accs.append(sum(ok) / max(len(ok), 1))
                div_accs.append(sum(div_ok) / max(len(div_ok), 1))
            out[model][f"dose{dose}"] = {"acc": sum(accs)/len(accs), "div_acc": sum(div_accs)/len(div_accs),
                                         "seeds": [round(a, 3) for a in accs]}
            json.dump(out, open("p227_dose_response.json", "w"), indent=1)
            print(f"{model} dose{dose}: acc={out[model][f'dose{dose}']['acc']:.3f} "
                  f"div={out[model][f'dose{dose}']['div_acc']:.3f} seeds={[round(a,3) for a in accs]}")
    json.dump(out, open("p227_dose_response.json", "w"), indent=1)
    print("saved p227_dose_response.json")

import json
if __name__ == "__main__":
    main()
