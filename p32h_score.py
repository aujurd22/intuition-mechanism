"""P32-h scorer: grades both subject arms against the committed truth
and writes p32h_results.json with the per-arm breakdown and the
confusion structure (which context family absorbs each false
'existing' answer)."""
import json
from collections import Counter

design = json.load(open("p32h_design.json"))
truth = {t["trial"]: t for t in design["trials"]}

arms = {}
try:
    judge = json.load(open("p32h_judge_answers.json"))
    arms["judge"] = {int(k): v["answer"] for k, v in judge.items()}
except FileNotFoundError:
    arms["judge"] = {}
try:
    native = json.load(open("p32h_native_answers.json"))["answers"]
    arms["native"] = {int(k): v for k, v in native.items()}
except FileNotFoundError:
    arms["native"] = {}

results = {}
for arm, ans in arms.items():
    if not ans:
        continue
    total = ok = ex_ok = ex_n = new_ok = new_n = 0
    confusion = Counter()
    per = {}
    for tid, t in sorted(truth.items()):
        a = ans.get(tid)
        hit = a == t["truth"]
        total += 1
        ok += hit
        if t["kind"] == "existing":
            ex_n += 1
            ex_ok += hit
        else:
            new_n += 1
            new_ok += hit
            if not hit and a is not None and a != "NEW":
                confusion[a] += 1
        per[str(tid)] = {"answer": a, "truth": t["truth"],
                         "kind": t["kind"], "ok": hit}
    results[arm] = {"total": f"{ok}/{total}", "existing": f"{ex_ok}/{ex_n}",
                    "new": f"{new_ok}/{new_n}",
                    "false_existing_to": dict(confusion), "detail": per}
    print(f"{arm:7s}: total {ok}/{total} | existing {ex_ok}/{ex_n} "
          f"| new {new_ok}/{new_n} | new-absorbed-by {dict(confusion)}")

json.dump(results, open("p32h_results.json", "w"), indent=1)
print("saved p32h_results.json")
