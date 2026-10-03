"""P224: boundary probe in a SECOND natural ecosystem (gap G3) —
FunSearch-style heuristic-rule discovery with a code-execution verifier.
Boundary-law falsifiable prediction: this domain (cheap verifier, examples
generable) should land INSIDE the compression boundary (pack helps).
Task: judge whether a top-5 selection heuristic is GOOD (avg top-5 sum >= 97%
of optimal on fresh random lists) or BAD. Truth = pure code execution."""
import os, sys, json, random, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def make_exec(body):
    """wrap a rule body (python lines, uses `lst`) into a callable returning top-5 sum"""
    code = f"def rule(lst):\n{body}\n    return 0\n"
    ns = {}
    exec(code, ns)
    return ns["rule"]

RULES = [
    ("sort the numbers in descending order and take the first five",
     "    s = sorted(lst, reverse=True)[:5]",),
    ("pick the five numbers closest to 100",
     "    s = sorted(lst, key=lambda x: abs(x - 100))[-5:]",),
    ("pick the five numbers farthest from the mean of the list",
     "    m = sum(lst)/len(lst)\n    s = sorted(lst, key=lambda x: -abs(x - m))[:5]",),
    ("sort by last digit in descending order and take the first five",
     "    s = sorted(lst, key=lambda x: -(x % 10))[:5]",),
    ("pick the five numbers closest to the mean of the list",
     "    m = sum(lst)/len(lst)\n    s = sorted(lst, key=lambda x: abs(x - m))[:5]",),
    ("sort the numbers in ascending order and take the first five",
     "    s = sorted(lst)[:5]",),
    ("pick numbers above 50, then take the five largest of those",
     "    f = [x for x in lst if x > 50]\n    s = sorted(f, reverse=True)[:5] if len(f) >= 5 else sorted(lst, reverse=True)[:5]",),
    ("sort by the number of divisors of each number, descending",
     "    s = sorted(lst, key=lambda x: -sum(1 for i in range(1, int(abs(x)) + 1) if abs(x) % i == 0))[:5]",),
]

def top5sum(lst):
    return sum(sorted(lst, reverse=True)[:5])

def avg_score(body_lines, trials=30, seed0=1000):
    tot = 0.0
    for t in range(trials):
        rng = random.Random(seed0 + t)
        lst = [rng.randint(0, 100) for _ in range(20)]
        code = "def rule(lst):\n" + body_lines + "\n    return sorted(s, reverse=True)[:5]\n"
        ns = {}
        exec(code, ns)
        tot += sum(ns["rule"](lst))
    return tot / trials

def main():
    random.seed(7)
    # ground truth by execution
    # compute optimal baseline and each rule's average score
    opt_scores = []
    for t in range(30):
        rng = random.Random(1000 + t)
        lst = [rng.randint(0, 100) for _ in range(20)]
        opt_scores.append(top5sum(lst))
    opt = sum(opt_scores) / 30
    rules = []
    for i, (desc, body) in enumerate(RULES):
        sc = avg_score(body)
        good = sc >= 0.97 * opt
        rules.append({"i": i, "desc": desc, "body": body, "score": sc, "good": good})
        print(f"rule{i}: score/opt = {sc/opt:.3f} -> {'GOOD' if good else 'BAD'}  | {desc[:60]}")
    json.dump({"opt": opt, "rules": [{**r, "score_over_opt": r["score"]/opt} for r in rules]},
              open("p224_rules_truth.json", "w"), indent=1)

    # LLM probe
    import importlib, llm_client
    out = {}
    for model in ["doubao-seed-2.1-lite", "glm-5.3-flash"]:
        os.environ["ARK_MODEL"] = model
        importlib.reload(llm_client)
        res = {}
        for cond in ["zeroshot", "pack"]:
            correct = 0; total = 0
            per = []
            for r in rules:
                if cond == "zeroshot":
                    prompt = (f"A selection heuristic for lists of numbers (values 0-100, list "
                              f"length 20) is described as:\n'{r['desc']}'\n\nThe GOAL is to "
                              "maximize the sum of the 5 selected numbers. Is this heuristic "
                              "GOOD (achieves >= 97% of the best possible top-5 sum on typical "
                              "random lists) or BAD?\nAnswer exactly one word: GOOD or BAD.")
                else:
                    exemplars = "\n".join(
                        f"  '{rr['desc']}' -> score {rr['score']/opt:.2f}x optimal = "
                        f"{'GOOD' if rr['good'] else 'BAD'}"
                        for j, rr in enumerate(rules) if j != r["i"])[:1500]
                    prompt = ("Selection heuristics for lists (values 0-100, length 20) are "
                              "judged by executed average top-5 sum vs optimal:\n" + exemplars +
                              f"\n\nNow judge this UNSEEN heuristic (goal: maximize top-5 sum):\n"
                              f"'{r['desc']}'\nAnswer exactly one word: GOOD or BAD.")
                ans = llm_client.ask(prompt).strip().upper()
                pred = "GOOD" if "GOOD" in ans[:20] else ("BAD" if "BAD" in ans[:20] else "?")
                ok = int(pred == ("GOOD" if r["good"] else "BAD"))
                correct += ok; total += 1
                per.append(ok)
                res.setdefault(cond, {})[f"rule{r['i']}"] = {"pred": pred, "truth": r["good"], "ok": ok}
            acc = correct / total
            res[cond + "_acc"] = acc
            print(f"{model} {cond}: acc = {acc:.3f} ({correct}/{total})")
        gain = res["pack_acc"] - res["zeroshot_acc"]
        res["pack_gain"] = round(gain, 3)
        verdict = ("INSIDE boundary (pack helps)" if gain > 0.10 else
                   "OUTSIDE/SATURATED (no pack gain)" if gain < -0.02 else "BORDERLINE")
        res["boundary_verdict"] = verdict
        print(f"{model} pack gain = {gain:+.3f} -> {verdict}")
    json.dump(res := out, open("p224_funsearch_probe.json", "w"), indent=1)
    print("saved p224_funsearch_probe.json")

import json
if __name__ == "__main__":
    main()
