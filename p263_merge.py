# -*- coding: utf-8 -*-
"""P263 merge: window-lever verdict. Usage: python p263_merge.py <dir>"""
import json, sys, glob, os

def main():
    d = sys.argv[1]
    rows = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(d, "*.json")))
            if "verdict" not in os.path.basename(f)]
    summary = {}
    for arm in ["control", "readout_only", "reweight"]:
        accs = [r["final_test"] for r in rows if r["arm"] == arm]
        mean = sum(accs) / len(accs)
        var = sum((a - mean) ** 2 for a in accs) / (len(accs) - 1)
        summary[arm] = {"mean": round(mean, 4), "std": round(var ** 0.5, 4),
                        "gen_ratio": round(sum(a >= 0.5 for a in accs) / len(accs), 2),
                        "n": len(accs)}
        print(f"{arm}: {mean:.3f} +/- {var**0.5:.3f}  gen>=0.5 "
              f"{summary[arm]['gen_ratio']}")
    c, ro = summary["control"], summary["readout_only"]
    verdict = {
        "summary": summary,
        "H_consolidation": ("CONFIRMED" if ro["mean"] > c["mean"] + 0.2 and
                            ro["gen_ratio"] >= 2 * max(c["gen_ratio"], 0.1)
                            else "NOT CONFIRMED"),
        "note": ("readout-only in-window converts losers -> consolidation is the "
                 "causal lever" if ro["mean"] > c["mean"] + 0.2 else
                 "wiring alone insufficient — trunk must keep changing; "
                 "consolidation hypothesis needs revision"),
    }
    json.dump(verdict, open(os.path.join(d, "p263_merge_verdict.json"), "w"),
              indent=1)
    print(json.dumps(verdict, indent=1))

if __name__ == "__main__":
    main()
