"""P230: GENERATION-SIDE loop (external review item 3, the FunSearch reproduction).
The model WRITES a top-5 selection heuristic (python code), the verifier
EXECUTES it on fresh random lists and scores vs optimal, the score is fed
back, and the model iterates. Measures: generation-side improvement curve —
the boundary law's central prediction (generation open but verifier-gated)
lives here. Boundary-law probe: does verifier feedback move generation-side
accuracy, mirroring the judge-side saturation?"""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
MODELS = ["doubao-seed-2.1-lite", "glm-5.3-flash"]
ROUNDS = 4

def top5sum(lst):
    return sum(sorted(lst, reverse=True)[:5])

def score_rule(code, trials=30, seed0=5000):
    """execute the rule (defines rule(lst) -> list of 5 picks) and score"""
    ns = {}
    try:
        exec(code, ns)
    except Exception as ex:
        return None, f"exec error: {ex}"
    if "rule" not in ns:
        return None, "no rule() defined"
    tot, opt_tot = 0.0, 0.0
    for t in range(trials):
        rng = random.Random(seed0 + t)
        lst = [rng.randint(0, 100) for _ in range(20)]
        try:
            picks = list(ns["rule"](lst))
        except Exception as ex:
            return None, f"runtime error: {ex}"
        # ANTI-CHEAT: picks must be a 5-element subset of lst (no repeats, no
        # outside values) — doubao round2 exploited exactly this (1.030x > 1)
        if len(picks) != 5 or any(picks.count(p) > lst.count(p) for p in picks)            or any(p not in lst for p in picks):
            return None, "ANTI-CHEAT: picks must be 5 distinct members of lst"
        s = sum(picks)
        tot += s
        opt_tot += top5sum(lst)
    return tot / opt_tot, None

def main():
    import importlib, llm_client
    out = {}
    for model in MODELS:
        os.environ["ARK_MODEL"] = model
        import importlib as il
        il.reload(llm_client)
        history = []
        best = 0.0
        prompt0 = ("Write a PYTHON function `rule(lst)` that selects 5 numbers from the "
                   "list `lst` (ints 0-100, length 20) to MAXIMIZE the sum of the 5 picked "
                   "numbers. Return them as a list.\n\n"
                   "def rule(lst):\n    # your heuristic\n    return [...]\n\n"
                   "It will be executed on 30 fresh random lists and scored as "
                   "(your top-5 sum) / (optimal top-5 sum). Output ONLY the code.")
        code, score, err = None, None, None
        rounds = []
        for rnd in range(1, ROUNDS + 1):
            if rnd == 1:
                p = prompt0
            elif score is None:
                p = (f"Your previous heuristic failed"
                     + (f" ({err})" if err else "") +
                     ".\nWrite a corrected version. Output ONLY the code.\n\nPrevious code:\n"
                     + code)
            else:
                p = (f"Your previous heuristic scored {score:.3f}x optimal."
                     "\nImprove it. Output ONLY the code.\n\nPrevious code:\n" + code)
            text = llm_client.ask(p)
            mm = (re.search(r"```(?:python)?\s*(def rule\(lst\):.*?)```", text, re.S)
                  or re.search(r"(def rule\(lst\):.*?)(?=\Z)", text, re.S))
            code = mm.group(1).strip() if mm else text.strip()
            sc, err = score_rule(code, trials=30, seed0=5000 + rnd * 100)
            best = max(best, sc or 0)
            rounds.append({"round": rnd, "score": sc, "err": err[:80] if err else None})
            print(f"{model} round{rnd}: score={sc}")
        out[model] = {"rounds": rounds, "best": best,
                      "improvement": best - (rounds[0]["score"] or 0)}
        print(f"{model} BEST = {best:.3f}x optimal, improvement over round1 = "
              f"{best - rounds[0]['score'] if rounds[0]['score'] else 'n/a'}")
    json.dump(out, open("p230_generation_side.json", "w"), indent=1, default=str)
    print("saved p230_generation_side.json")

import random
if __name__ == "__main__":
    main()
