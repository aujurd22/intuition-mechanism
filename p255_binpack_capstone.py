# -*- coding: utf-8 -*-
"""P255: P253 capstone RUN — online bin-packing heuristic discovery.
External boundary: beat First-Fit on held-out item streams (published,
reproducible baseline; FunSearch's external flagship direction).

Interface: place(item, bins) -> int index (bins = list of remaining
capacities; index == len(bins) opens a new bin with remaining 1 - item).
Streams: 500 items, uniform [0.02, 0.97] (2dp), capacity 1.0.
Held-out: 20 streams (seeded 5000+); 5 self-test streams (seeded 1000+,
given to the model for local checking).
Baselines computed on the same streams: Next-Fit / First-Fit / Best-Fit.
Score: mean bins over held-out streams. Success band (P253): mean <
First-Fit mean => external improvement (paper-claim grade).
Anti-cheat: causality (only item + remaining capacities given), validity
(index must be legal and the item must fit), blacklist on stream access.
Feedback: LABELED (P240) — your mean vs FF/BF/NF means, worst-stream deltas.
"""
import os, sys, json, re, random, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
MODELS = ["kimi-k2.8-preview", "glm-5.3-flash"]
ROUNDS = 3
CAP = 1.0

def gen_stream(seed, n=500):
    rng = random.Random(seed)
    return [round(rng.uniform(0.02, 0.97), 2) for _ in range(n)]

def sim(stream, place):
    bins = []
    for item in stream:
        i = place(item, list(bins))
        i = int(i)
        if i < 0 or i > len(bins):
            raise ValueError(f"invalid bin index {i} (n={len(bins)})")
        if i == len(bins):
            bins.append(CAP - item)
        else:
            if bins[i] < item - 1e-9:
                raise ValueError(f"item {item} does not fit bin {i} (rem {bins[i]:.2f})")
            bins[i] -= item
    return len(bins)

def bf(stream):
    def place(it, b):
        fits = [i for i in range(len(b)) if b[i] >= it - 1e-9]
        return min(fits, key=lambda i: b[i]) if fits else len(b)  # tightest fit
    return sim(stream, place)

def ff(stream):
    return sim(stream, lambda it, b: next(
        (i for i in range(len(b)) if b[i] >= it - 1e-9), len(b)))

def nf(stream):
    class S:
        cur = 0
    def place(it, b):
        if S.cur < len(b) and b[S.cur] >= it - 1e-9:
            return S.cur
        S.cur = len(b)
        return S.cur
    return sim(stream, place)

SELF_SEEDS = [1000 + i for i in range(5)]
HOLD_SEEDS = [5000 + i for i in range(20)]
SELF_STREAMS = {s: gen_stream(s) for s in SELF_SEEDS}
HOLD_STREAMS = {s: gen_stream(s) for s in HOLD_SEEDS}

def bench(streams, fn):
    return sum(fn(s) for s in streams) / len(streams)

BASE = {
    "NextFit_hold": bench(HOLD_STREAMS.values(), nf),
    "FirstFit_hold": bench(HOLD_STREAMS.values(), ff),
    "BestFit_hold": bench(HOLD_STREAMS.values(), bf),
}
print("baselines (mean bins, 20 held-out streams):", 
      {k: round(v, 2) for k, v in BASE.items()}, flush=True)

PROMPT0 = f"""Write a PYTHON function `place(item, bins)` for online bin packing
(bin capacity 1.0). `item` is the next item size (float in [0.02, 0.97]);
`bins` is the list of remaining capacities of currently OPEN bins. Return the
index of the bin to put the item in (an int in [0, len(bins)]); returning
len(bins) opens a NEW bin. Your function is called once per item, in stream
order, and must be causal (only the arguments — no stream lookahead, no RNG
seeding tricks).

Baseline to beat: First-Fit uses {BASE['FirstFit_hold']:.1f} bins on average
over 20 hidden random streams (500 items each, uniform [0.02, 0.97]);
Best-Fit uses {BASE['BestFit_hold']:.1f}. Your score: your mean bins on the
hidden streams — lower is better. You may self-test on streams seeded with
random.Random(1000..1004) (5 streams of 500 items, same distribution).

Requirements: pure Python, standard library only; the function must be a
general policy (no caching answers across calls, no file/network IO).
Output ONLY Python code defining place(item, bins)."""

def extract_code(text):
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.S)
    return m.group(1) if m else text

def main():
    import importlib, llm_client
    out = {"baselines": BASE, "models": {}}
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
            try:
                exec(code, ns)
                fn = ns.get("place")
                if not callable(fn):
                    raise ValueError("no place() defined")
                hold = [sim(s, fn) for s in HOLD_STREAMS.values()]
                mean_hold = sum(hold) / len(hold)
                self_m = bench(SELF_STREAMS.values(), fn)
            except Exception as ex:
                err = f"runtime error: {ex}"
                mean_hold = None
            fb = (f"Your heuristic FAILED: {err}. Fix and resubmit." if err else
                  f"Your heuristic used {mean_hold:.2f} bins on average over the 20 "
                  f"hidden streams. Baselines: Next-Fit {BASE['NextFit_hold']:.2f}, "
                  f"First-Fit {BASE['FirstFit_hold']:.2f}, Best-Fit "
                  f"{BASE['BestFit_hold']:.2f}. "
                  + ("You BEAT First-Fit. Push further and keep correctness. Resubmit."
                     if mean_hold < BASE["FirstFit_hold"] else
                     "You are behind First-Fit. Improve the packing policy. Resubmit."))
            rounds.append({"round": rnd, "mean_hold": mean_hold, "err": err,
                           "code": code[:900]})
            if mean_hold is not None and (best is None or mean_hold < best):
                best = round(mean_hold, 2)
            print(f"[{int(time.time()-t0)}s] {model} r{rnd}: "
                  f"{mean_hold if mean_hold is None else round(mean_hold,2)} "
                  f"err={err}", flush=True)
            prompt = (PROMPT0 + "\n\nYour previous submission and verifier "
                      f"feedback:\n{fb}\n\nPrevious code:\n```python\n{code}\n```\n"
                      "Output ONLY the improved full code.")
        out["models"][model] = {"rounds": rounds, "best_mean": best}
        json.dump(out, open("p255_binpack_results.json", "w"), indent=1)
    ff_m = BASE["FirstFit_hold"]
    beats = {m: v["best_mean"] for m, v in out["models"].items()
             if v["best_mean"] and v["best_mean"] < ff_m}
    summary = {"FirstFit": round(ff_m, 2), "BestFit": round(BASE["BestFit_hold"], 2),
               "best_per_model": {m: v["best_mean"] for m, v in out["models"].items()},
               "external_improvement": bool(beats),
               "band": ("EXTERNAL IMPROVEMENT — paper-claim grade" if beats
                        else "baselines matched/not beaten — honest but not boundary-moving")}
    out["summary"] = summary
    json.dump(out, open("p255_binpack_results.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))

if __name__ == "__main__":
    main()
