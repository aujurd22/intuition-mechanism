# -*- coding: utf-8 -*-
"""P262: head-to-head with FunSearch's own shipped heuristic + simulator
equivalence check.

FunSearch's public notebook ships its policy as: pre-open num_items bins at
capacity; per item, among FITTING bins choose argmax priority(item, bins[valid]);
count bins with >=1 item. Its shipped priority is -(bins - item) — i.e., under
their wrapper this is EXACTLY Best-Fit semantics. So:
  (1) equivalence check: official-funsearch policy vs our BF per instance
      (any mismatch = simulator discrepancy — P259 numbers would need audit);
  (2) paired Wilcoxon: our discovered heuristics (P259 stored per-instance
      excess) vs the official FunSearch artifact on all 20 OR3 + 5 Weibull.
Note: the Nature paper's exact OR3 heuristic is not in the public repo — the
comparison here is against the repo's official artifact.
"""
import os, sys, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
DS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "funsearch_datasets.json"), encoding="utf-8"))
P259 = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "p259_capstone_upgrade.json"), encoding="utf-8"))

def funsearch_binpack(inst):
    """FunSearch's exact wrapper (cell 4): pre-opened bins, argmax priority
    among fitting, count used. Shipped priority = -(bins - item) => Best-Fit."""
    cap, items = inst["capacity"], inst["items"]
    bins = [cap] * len(items)
    used = []
    for item in items:
        valid = [i for i in range(len(bins)) if bins[i] - item >= 0]
        if not valid:
            raise ValueError("pre-opened bins should always fit")
        best = max(valid, key=lambda i: -(bins[i] - item))
        bins[best] -= item
        if best not in used:
            used.append(best)
    return len(used)

def l1(inst):
    return -(-sum(inst["items"]) // inst["capacity"])

def main():
    from scipy import stats
    out = {}
    for name, insts in [("OR3", DS["OR3"]), ("Weibull", DS["Weibull 5k"])]:
        rows = []
        for k, inst in insts.items():
            fs = funsearch_binpack(inst)
            l_ = l1(inst)
            rows.append({"instance": k, "funsearch": fs - l_,
                         "ff": (ff := None) or None,  # filled from P259 below
                         "l1": l_})
            rows[-1].pop("ff")
        out[name] = rows
    # merge P259 stored per-instance excess (he/ff/bf) by position
    for m, v in P259["models"].items():
        fe = v["final_eval"]
        # OR3 rows are u500_00..19; P259 stored dev(00-09) and hold(10-19) apart
        for name, rows in [("OR3", out["OR3"]), ("Weibull", out["Weibull"])]:
            if name == "OR3":
                he = fe["OR3_dev"]["he_excess"] + fe["OR3_hold"]["he_excess"]
                ff = fe["OR3_dev"]["ff_excess"] + fe["OR3_hold"]["ff_excess"]
                bf = fe["OR3_dev"]["bf_excess"] + fe["OR3_hold"]["bf_excess"]
            else:
                he = fe["Weibull"]["he_excess"]
                ff = fe["Weibull"]["ff_excess"]
                bf = fe["Weibull"]["bf_excess"]
            for i, r in enumerate(rows):
                k = m.split("-")[0]
                r[f"he_{k}"] = he[i]; r[f"ff_{k}"] = ff[i]; r[f"bf_{k}"] = bf[i]
    # paired Wilcoxon: he vs funsearch on OR3 (n=20)
    mism = [(name, r["instance"], r["funsearch"], r["bf_glm"])
            for name in ("OR3", "Weibull") for r in out[name]
            if r["funsearch"] != r["bf_glm"]]
    print("funsearch-vs-ourBF mismatches:", mism if mism else "NONE (simulators equivalent)")

    stats_out = {}
    for m in P259["models"]:
        for name in ("OR3", "Weibull"):
            he = [r[f"he_{m.split(chr(45))[0]}"] for r in out[name]]
            fs = [r["funsearch"] for r in out[name]]
            w = stats.wilcoxon(he, fs)
            stats_out.setdefault(m, {})[name] = {
                "he_mean": round(sum(he)/len(he), 3),
                "funsearch_mean": round(sum(fs)/len(fs), 3),
                "wilcoxon_p": round(w.pvalue, 4)}
            print(f"{name} {m}: he {sum(he)/len(he):.2f} vs funsearch "
                  f"{sum(fs)/len(fs):.2f} (p={w.pvalue:.4f})")
    out["stats"] = stats_out
    out["mismatches"] = mism
    with open("p262_funsearch_headtohead.json", "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print("saved p262_funsearch_headtohead.json")

if __name__ == "__main__":
    main()
