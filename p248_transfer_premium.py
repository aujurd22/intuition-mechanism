# -*- coding: utf-8 -*-
"""P248: does the rich10 numeric premium buy TRANSFER? (P240 follow-up, pre-registered)

P240 found the label cliff (unlabeled <= 0 flow, labeled >= 5.1) and rich10 ~= rich3
on row-patching. Registered follow-up: the numeric-evidence premium should appear
only when evidence enables rule induction (transfer), not row patches.

Design: three FRESH row windows (same patch protocol as fixed P240, history carries
the model's own labels):
  W1 = [9,11,13,15,17,19,21,25,27,29,33,37]   (truth: 13,17 land; f(9)=49.0322 trap)
  W2 = [41,43,45,47,49,51,53,57,63,69,77,91]  (no lands)
  W3 = [21,33,39,51,57,69,87,93,99,111,123,141] (no lands; odd multiples —
        maximally tempting for "all odds land" heuristics)
Windows are revealed sequentially; feedback at the arm's richness each round.

Arms: rich3 (wrong-row labels) vs rich10 (labels + f(d) values).
Metric: errors per window (e1, e2, e3); transfer = e2+e3.
Pre-stated readings:
  rich10 transfer < rich3 transfer  -> numeric evidence buys rule induction (premium real)
  equal                             -> labels are the active ingredient even for
                                       transfer; the cliff is the whole story
"""
import os, sys, json, re, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p240_validator_richness as p240
from p240_validator_richness import (one_over_x6, is_land, build_prompt, parse,
                                     verifier, BITS_PER_ROW)
import mpmath as _mp  # noqa: F401  (imported transitively)

WINDOWS = [
    ("W1", [9, 11, 13, 15, 17, 19, 21, 25, 27, 29, 33, 37]),
    ("W2", [41, 43, 45, 47, 49, 51, 53, 57, 63, 69, 77, 91]),
    ("W3", [21, 33, 39, 51, 57, 69, 87, 93, 99, 111, 123, 141]),
]
MODELS = ["deepseek-v4-flash", "doubao-seed-2.1-lite"]
ALL_ROWS = sorted({d for _, rows in WINDOWS for d in rows})
TRUTH = {d: ("land" if is_land(d) else "no") for d in ALL_ROWS}
p240.TRUTH.update(TRUTH)   # verifier() reads its own module global

def main():
    import importlib, llm_client
    t0 = time.time()
    results = []
    for arm in ["rich3", "rich10"]:
        for model in MODELS:
            os.environ["ARK_MODEL"] = model
            importlib.reload(llm_client)
            history, labels = [], {}
            werrs = []
            for wname, rows in WINDOWS:
                ans = llm_client.ask(build_prompt(rows, arm, history, labels or None))
                cur = parse(ans)
                for d, v in labels.items():   # resubmit safety net
                    cur.setdefault(d, v)
                missing = [d for d in rows if d not in cur]
                if missing:                    # one retry with explicit nudge
                    ans = llm_client.ask(build_prompt(
                        rows, arm, history + [f"unparsed rows: {missing}; answer all 12"],
                        cur or None))
                    cur = parse(ans)
                    for d, v in labels.items():
                        cur.setdefault(d, v)
                labels = cur
                errs = [d for d in rows
                        if d not in cur or (cur[d] == "LAND") != (TRUTH[d] == "land")]
                werrs.append(len(errs))
                if errs:
                    history.append(verifier(None, arm, sorted(errs)))
                print(f"[{int(time.time()-t0)}s] {arm} {model} {wname}: "
                      f"errs={len(errs)} {sorted(errs)}", flush=True)
            results.append({"arm": arm, "model": model, "window_errs": werrs,
                            "transfer_errs": sum(werrs[1:])})
    summary = {}
    for arm in ["rich3", "rich10"]:
        rs = [r for r in results if r["arm"] == arm]
        per_window = [round(sum(r["window_errs"][i] for r in rs) / len(rs), 1)
                      for i in range(3)]
        transfer = sum(r["transfer_errs"] for r in rs)
        summary[arm] = {"mean_window_errs": per_window, "transfer_total": transfer}
        print(f"{arm}: window errs {per_window}, transfer total {transfer}")
    premium = summary["rich3"]["transfer_total"] - summary["rich10"]["transfer_total"]
    verdict = {"summary": summary, "premium_rich_minus_rich10": premium,
               "reading": ("numeric premium REAL on transfer" if premium > 2 else
                           "labels suffice — cliff is the whole story" if premium <= 2
                           else None)}
    json.dump({"results": results, "truth": {str(k): v for k, v in TRUTH.items()},
               "verdict": verdict}, open("p248_transfer_premium.json", "w"), indent=1)
    print(json.dumps(verdict, indent=1))

if __name__ == "__main__":
    main()
