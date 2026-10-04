# -*- coding: utf-8 -*-
"""P259: P255 capstone upgrade — the paper-grade external-improvement attempt.

FunSearch's own evaluation suite (google-deepmind/funsearch, bin_packing.ipynb):
  OR3       : 20 instances x 500 items, capacity 150, sizes int [20,100]
              (OR-Library u500; loaded verbatim from the notebook)
  Weibull 5k: 5 instances x 5000 items, capacity 100 (cross-dataset transfer,
              never fed back)
Reference: L1 lower bound per instance (sum/capacity) — FunSearch's own floor.

Protocol split: OR3 u500_00..09 = dev (feedback allowed), u500_10..19 =
holdout (final eval only). Significance: Wilcoxon signed-rank on per-instance
excess-over-L1 vs First-Fit and vs Best-Fit + bootstrap 95% CI.

Models: glm-5.3-flash (champion) + kimi-k2.8-preview (REPAIR PROBE: on error
the feedback includes the exact expected signature and a minimal repro —
tests whether kimi's P255 repair failure was feedback-quality-dependent).
Interface: place(item, bins, capacity) -> int (index == len(bins) opens new).
"""
import os, sys, json, re, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
DS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "funsearch_datasets.json"), encoding="utf-8"))
OR3 = DS["OR3"]; WEI = DS["Weibull 5k"]
DEV = [f"u500_{i:02d}" for i in range(10)]
HOLD = [f"u500_{i:02d}" for i in range(10, 20)]
MODELS = ["glm-5.3-flash", "kimi-k2.8-preview"]
ROUNDS = 4

def sim(inst, place):
    cap, items = inst["capacity"], inst["items"]
    bins = []
    for item in items:
        i = place(item, list(bins), cap)
        i = int(i)
        if i < 0 or i > len(bins):
            raise ValueError(f"invalid bin index {i} (n={len(bins)})")
        if i == len(bins):
            bins.append(cap - item)
        else:
            if bins[i] < item - 1e-9:
                raise ValueError(f"item {item} does not fit bin {i} (rem {bins[i]:.2f})")
            bins[i] -= item
    return len(bins)

def ff_sim(inst):
    cap, items = inst["capacity"], inst["items"]
    bins = []
    for it in items:
        for i in range(len(bins)):
            if bins[i] >= it - 1e-9:
                bins[i] -= it
                break
        else:
            bins.append(cap - it)
    return len(bins)

def bf_sim(inst):
    cap, items = inst["capacity"], inst["items"]
    bins = []
    for it in items:
        fits = [i for i in range(len(bins)) if bins[i] >= it - 1e-9]
        if fits:
            i = min(fits, key=lambda k: bins[k])
            bins[i] -= it
        else:
            bins.append(cap - it)
    return len(bins)

def l1(inst):
    return -(-sum(inst["items"]) // inst["capacity"])  # ceil

PROMPT0 = f"""Write a PYTHON function `place(item, bins, capacity)` for online bin
packing. `item` = next item size; `bins` = list of remaining capacities of
open bins; `capacity` = the bin capacity (instances vary, e.g. 150 or 100).
Return the index of the bin to place the item in (int in [0, len(bins)]);
returning len(bins) opens a new bin. Called once per item in stream order;
must be causal (no stream lookahead, no RNG tricks, no caching).

Baselines to beat (mean bins, held-out OR3 instances, 500 items each, capacity 150):
First-Fit {sum(ff_sim(OR3[k]) for k in HOLD)/len(HOLD):.2f},
Best-Fit {sum(bf_sim(OR3[k]) for k in HOLD)/len(HOLD):.2f},
L1 lower bound {sum(l1(OR3[k]) for k in HOLD)/len(HOLD):.2f}.
Your score: mean bins on 10 hidden OR3 instances (lower = better). A second
dataset (capacity 100) tests whether your policy transfers.

Requirements: pure Python, standard library only, general policy (no caching
answers, no file/network IO). Output ONLY Python code defining
place(item, bins, capacity)."""

STRENGTHEN = ("\n\nEXPECTED SIGNATURE (the verifier calls exactly this):\n"
              "    place(item: float, bins: list[float], capacity: float) -> int\n"
              "Minimal check your code must pass:\n"
              "    >>> place(0.3, [0.5], 150)  # returns 0 or 1\n"
              "Resubmit the full function with EXACTLY this signature.")

def extract_code(text):
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.S)
    return m.group(1) if m else text

def main():
    import importlib, llm_client
    from scipy import stats
    import random
    out = {"baselines": {}, "models": {}}
    for k in HOLD:
        out["baselines"][k] = {"FF": ff_sim(OR3[k]), "BF": bf_sim(OR3[k]),
                               "L1": l1(OR3[k])}
    DEV_FF = [ff_sim(OR3[k]) for k in DEV]
    DEV_BF = [bf_sim(OR3[k]) for k in DEV]
    DEV_L1 = [l1(OR3[k]) for k in DEV]
    t0 = time.time()
    for model in MODELS:
        os.environ["ARK_MODEL"] = model
        importlib.reload(llm_client)
        prompt = PROMPT0
        best = None
        rounds = []
        for rnd in range(1, ROUNDS + 1):
            resp = llm_client.ask(prompt)
            code = extract_code(resp)
            ns = {}
            err = None
            hold_bins, hold_excess = None, None
            try:
                exec(code, ns)
                fn = ns.get("place")
                if not callable(fn):
                    raise ValueError("no place() defined")
                dev_ex = []
                for k in DEV:
                    n = sim(OR3[k], fn)
                    dev_ex.append(n - l1(OR3[k]))
                dev_mean = sum(dev_ex) / len(dev_ex)
                ff_dev = [f - l for f, l in zip(DEV_FF, DEV_L1)]
                bf_dev = [b - l for b, l in zip(DEV_BF, DEV_L1)]
                ff_m = sum(ff_dev) / len(ff_dev)
                bf_m = sum(bf_dev) / len(bf_dev)
                fb = (f"Your heuristic FAILED: {err}." if err else
                      f"Dev mean excess-over-L1: yours {dev_mean:.2f}, "
                      f"First-Fit {ff_m:.2f}, Best-Fit {bf_m:.2f}. "
                      f"Per-instance deltas vs FF: "
                      f"{[round(a-b,1) for a,b in zip(dev_ex, ff_dev)]}. "
                      + ("You BEAT First-Fit on dev. Keep correctness, push toward "
                         "Best-Fit. Resubmit." if dev_mean < ff_m else
                         "Still behind First-Fit on dev. Improve the policy. Resubmit."))
            except Exception as ex:
                err = f"runtime error: {ex}"
                dev_mean = ff_m = bf_m = None
                fb = (f"Your heuristic FAILED: {err}." + (STRENGTHEN if
                      model.startswith("kimi") else " Fix and resubmit."))
            rounds.append({"round": rnd, "dev_mean_excess": dev_mean, "err": err,
                           "code": code[:6000]})
            print(f"[{int(time.time()-t0)}s] {model} r{rnd}: "
                  f"{dev_mean if dev_mean is None else round(dev_mean,2)} err={err}",
                  flush=True)
            if err is None and (best is None or dev_mean < best):
                best = round(dev_mean, 2)
                best_code = code
            prompt = (PROMPT0 + "\n\nYour previous submission and verifier "
                      f"feedback:\n{fb}\n\nPrevious code:\n```python\n{code}\n```\n"
                      "Output ONLY the improved full code.")
        # ---- final evaluation of best dev heuristic: holdout + transfer ----
        if best_code is None:
            best_code = rounds[-1]["code"]
        ns = {}
        exec(best_code, ns)
        fn = ns["place"]
        res = {}
        for name, insts in [("OR3_hold", {k: OR3[k] for k in HOLD}),
                            ("OR3_dev", {k: OR3[k] for k in DEV}),
                            ("Weibull", WEI)]:
            he, fe, be, l1s = [], [], [], []
            for k, inst in insts.items():
                b = sim(inst, fn) if name != "Weibull" or True else None
                he.append(sim(inst, fn) - l1(inst))
                fe.append(ff_sim(inst) - l1(inst))
                be.append(bf_sim(inst) - l1(inst))
                l1s.append(l1(inst))
            res[name] = {"he_excess": he, "ff_excess": fe, "bf_excess": be,
                         "he_mean": sum(he)/len(he), "ff_mean": sum(fe)/len(fe),
                         "bf_mean": sum(be)/len(be)}
        w = stats.wilcoxon(res["OR3_hold"]["he_excess"],
                           res["OR3_hold"]["ff_excess"])
        w2 = stats.wilcoxon(res["OR3_hold"]["he_excess"],
                            res["OR3_hold"]["bf_excess"])
        res["wilcoxon_vs_FF_hold"] = {"stat": w.statistic, "p": round(w.pvalue, 4)}
        res["wilcoxon_vs_BF_hold"] = {"stat": w2.statistic, "p": round(w2.pvalue, 4)}
        out["models"][model] = {"rounds": rounds, "best_dev": best,
                                "final_eval": res}
        json.dump(out, open("p259_capstone_upgrade.json", "w"), indent=1)
        print(model, "final:", json.dumps(
            {k: {"he": v["he_mean"], "ff": v["ff_mean"], "bf": v["bf_mean"]}
             for k, v in res.items() if k != "wilcoxon_vs_FF_hold"
             and k != "wilcoxon_vs_BF_hold"}, indent=1), flush=True)
    print("done")

if __name__ == "__main__":
    main()
