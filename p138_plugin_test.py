"""P138: does the "intuition plugin" (contrast exemplar pack + mechanical
verifier) actually improve an agent on a task with ground truth?
Pre-build test of the P136/P138 MCP proposal — no tool is built; we test
the PROTOCOL under controlled conditions.

Task: binary classify (d, x0, lambda) as RATIONAL-ROW vs NOT, where truth
is the P121 census (six-row theorem, zero errors on [1,300]).  Stimuli
are 6-decimal numbers — the LLM cannot compute the answer; it can only
recognize structure.

Conditions:
  A  bare:          zero-shot, no pack
  B  pack:          6 locus exemplars WITH labels (the contrast pack =
                    the "intuition distillation" payload) + short charter
  C  pack+verifier: B + the mechanical verifier's readout for the CANDIDATE
                    (1/x6 to 8 decimals — integer vs irrational expansion)

Test set (n=22, truth from P121):
  positives (6):  d in {1,3,5,7,13,17}
  hard negatives (4): 35,55,77 (multi-support 2-elementary) + 10 (2-elementary,
                      chi-support multi)
  easy negatives (6): 2,11,19,23,25,43 (degree 1-2 irrational rows)
  perturbation negatives (6): locus rows' (x0, lambda) perturbed ~1%
                      (digits look native; constructively NOT rational rows)
                      — measures the reliability/hallucination floor.

Metrics: accuracy overall; positive recall (capability); perturbation
false-positive rate (reliability); per model (deepseek-v4-flash,
doubao-seed-2.1-lite).
Pre-registered bars: B - A >= 15pp => pack effective; perturbation FP
< 20% => reliable; C expected near-100 (the verifier readout is close
to dispositive).
"""
import os, sys, json, random, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("HF_HUB_OFFLINE", "1")
from p33_n20 import params_for
from llm_client import ask_chat

# ---- stimuli ------------------------------------------------------------
LOCUS = [1, 3, 5, 7, 13, 17]
HARD_NEG = [35, 55, 77, 10]
EASY_NEG = [2, 11, 19, 23, 25, 43]
rng = random.Random(20260930)


def fmt(x):
    return f"{x:.6f}"


def perturb(d):
    x0, lam = params_for(d)
    dx = x0 * (0.004 + 0.01 * rng.random()) * rng.choice([-1, 1])
    dl = lam * (0.004 + 0.01 * rng.random()) * rng.choice([-1, 1])
    return fmt(x0 + dx), fmt(lam + dl)


TEST = []
for d in LOCUS:
    x0, lam = params_for(d)
    TEST.append({"d": d, "x0": fmt(x0), "lam": fmt(lam), "truth": 1, "kind": "pos"})
for d in HARD_NEG + EASY_NEG:
    x0, lam = params_for(d)
    TEST.append({"d": d, "x0": fmt(x0), "lam": fmt(lam), "truth": 0, "kind": "neg"})
for d in LOCUS:
    x0s, lams = perturb(d)
    TEST.append({"d": d, "x0": x0s, "lam": lams, "truth": 0, "kind": "perturb"})

# verifier readout for every candidate: 1/x6 from the closed Lambert census
from mpmath import mp, mpf, exp, pi, sqrt as msqrt
mp.dps = 30


def one_over_x6(d):
    q = exp(-2 * pi * msqrt(mpf(d) / 6))
    S = lambda k: sum(mpf(n) * q ** (k * n) / (1 - q ** (k * n))
                      for n in range(1, 80) if q ** (k * n) > mpf(10) ** -25)
    ec = 4 + 24 * (S(1) + 3 * S(3) - 2 * S(2) - 6 * S(6))
    # eta product W6 via pentagonal
    def eta(q):
        s = mpf(1); n = 1
        while True:
            sg = -1 if n % 2 else 1
            p1 = n * (3 * n - 1) // 2; p2 = n * (3 * n + 1) // 2
            s += sg * (q ** p1 + q ** p2)
            if q ** p1 < mpf(10) ** -24:
                break
            n += 1
        return q ** (mpf(1) / 24) * s
    w6 = eta(q) * eta(q ** 2) * eta(q ** 3) * eta(q ** 6)
    return ec / (4 * w6) + 2


for t in TEST:
    t["verifier"] = f"{float(one_over_x6(t['d'])):.8f}"

# ---- prompts ------------------------------------------------------------
PACK = "\n".join(
    f"  d={d}: x0={fmt(params_for(d)[0])}, lambda={fmt(params_for(d)[1])}  -> RATIONAL (1/x6 = {v})"
    for d, v in zip(LOCUS, [8, 12, 20, 32, 104, 200]))

PROMPTS = {
    "A": ("You are given parameters of a Ramanujan-type 1/pi series identity. "
          "Decide whether 1/x6 at this point is an INTEGER (RATIONAL row) or not. "
          "Judge only the arithmetic structure of the numbers.\n"
          "d={d}  x0={x0}  lambda={lam}\n"
          "Answer exactly one line: 'VERDICT: RATIONAL' or 'VERDICT: NOT'."),
    "B": ("You are calibrating judgment on Ramanujan-type 1/pi series identities. "
          "The known RATIONAL rows (exhaustively verified) are:\n" + PACK + "\n\n"
          "These six are the ONLY rational rows in their family; every other "
          "parameter pair is NOT a rational row. Now judge a candidate:\n"
          "d={d}  x0={x0}  lambda={lam}\n"
          "Answer exactly one line: 'VERDICT: RATIONAL' or 'VERDICT: NOT'."),
    "C": ("You are calibrating judgment on Ramanujan-type 1/pi series identities. "
          "The known RATIONAL rows (exhaustively verified) are:\n" + PACK + "\n\n"
          "A mechanical verifier computed the candidate's 1/x6 to 8 decimals:\n"
          "  d={d}: verifier(1/x6) = {verifier}\n"
          "An exact integer readout (e.g. 12.00000000) means RATIONAL; an "
          "irrational expansion (random decimals) means NOT. Judge the candidate:\n"
          "d={d}  x0={x0}  lambda={lam}\n"
          "Answer exactly one line: 'VERDICT: RATIONAL' or 'VERDICT: NOT'."),
}

def run_experiment():
    MODELS = ["deepseek-v4-flash", "doubao-seed-2.1-lite"]
    out = {}
    for model in MODELS:
        os.environ["ARK_MODEL"] = model
        # llm_client reads ARK_MODEL at import time -> reload
        import importlib
        import llm_client
        importlib.reload(llm_client)
        res = {}
        for cond in ("A", "B", "C"):
            n = {"pos": [0, 0], "neg": [0, 0], "perturb": [0, 0]}
            for t in TEST:
                prompt = PROMPTS[cond].format(
                    d=t["d"], x0=t["x0"], lam=t["lam"], verifier=t["verifier"])
                ans = llm_client.ask_chat(prompt, max_tokens=512)
                pred = 1 if re.search(r"VERDICT:\s*RATIONAL", ans, re.I) else \
                    0 if re.search(r"VERDICT:\s*NOT", ans, re.I) else None
                key = t["kind"]
                n[key][1] += 1
                if pred is not None and pred == t["truth"]:
                    n[key][0] += 1
            res[cond] = {k: {"correct": v[0], "n": v[1],
                             "acc": round(100 * v[0] / v[1], 1)}
                         for k, v in n.items()}
            res[cond]["overall"] = round(
                100 * sum(v[0] for v in n.values()) / sum(v[1] for v in n.values()), 1)
        out[model] = res
        print(model, json.dumps(res, indent=1))

    json.dump({"testset": TEST, "results": out},
              open("p138_plugin_test.json", "w"), indent=1)
    print("saved p138_plugin_test.json")



if __name__ == "__main__":
    run_experiment()
