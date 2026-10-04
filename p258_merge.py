# -*- coding: utf-8 -*-
"""P258 merge: readout wiring vs outcome, winner/loser comparison.
Usage: python p258_merge.py <dir-with-seed-jsons>"""
import json, sys, glob, os

def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sx = (sum((x - mx) ** 2 for x in xs)) ** 0.5
    sy = (sum((y - my) ** 2 for y in ys)) ** 0.5
    if sx == 0 or sy == 0:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)

def main():
    d = sys.argv[1]
    rows = []
    for f in sorted(glob.glob(os.path.join(d, "seed_*.json"))):
        rows.append(json.load(open(f)))
    ys = [r["final_test"] for r in rows]
    corrs = {}
    for key in ["wiring3", "wiring4", "probe_mod3"]:
        for ep in [400, 1000]:
            xs = [r["snaps"][str(ep)][key] for r in rows]
            corrs[f"{key}@{ep}"] = round(pearson(xs, ys), 3)
    winners = [r for r in rows if r["final_test"] >= 0.5]
    losers = [r for r in rows if r["final_test"] < 0.5]
    def mean(rs, ep, key):
        return round(sum(r["snaps"][str(ep)][key] for r in rs) / max(1, len(rs)), 4)
    comp = {
        "n_win": len(winners), "n_lose": len(losers),
        "wiring3@1000_win": mean(winners, 1000, "wiring3"),
        "wiring3@1000_lose": mean(losers, 1000, "wiring3"),
        "wiring3@400_win": mean(winners, 400, "wiring3"),
        "wiring3@400_lose": mean(losers, 400, "wiring3"),
        "probe_mod3@1000_win": mean(winners, 1000, "probe_mod3"),
        "probe_mod3@1000_lose": mean(losers, 1000, "probe_mod3"),
    }
    bar = 2.0 / (len(rows) - 2) ** 0.5 * 2  # rough |r| significance bar, n~40
    verdict = {"n": len(rows), "correlations": corrs, "winner_vs_loser": comp,
               "H_wiring": bool(corrs["wiring3@1000"] > bar),
               "bar_approx": round(bar, 3)}
    out = os.path.join(d, "p258_merge_verdict.json")
    json.dump(verdict, open(out, "w"), indent=1)
    print(json.dumps(verdict, indent=1))

if __name__ == "__main__":
    main()
