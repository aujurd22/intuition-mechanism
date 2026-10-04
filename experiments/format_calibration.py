"""format_calibration: P128-b — which judge format carries YOUR model's
structural signal?

P119 (deepseek-v4.1-flash): forced-choice detects gdepth, absolute is null.
P128 (deepseek-v4-flash): the REVERSE (absolute rho 0.609, forced 63% ns).
Format effects on LLM structural judgment are MODEL-INSTANCE properties —
calibrate before any interestingness experiment.

Usage (40 API calls, ~10 min):
    ARK_API_KEY=... ARK_MODEL=<model> py -3 format_calibration.py

Protocol: 19 deg-matched pairs forced-choice (seeded side randomization) +
absolute 1-10 rating of the union identities; recommendation:
  forced rate >= 60% with binomial p < 0.05  -> use FORCED choice
  else |rho_gdepth| >= 0.4                   -> use ABSOLUTE rating
  else                                       -> model carries no signal;
                                                do not use it as judge.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
import json, re, random
from p33_n20 import params_for, DEG, NS
from llm_client import ask_chat


def gdepth(N):
    D = -24 * N
    sD = -1 if D < 0 else 1
    n = abs(D); v = 0
    while n % 2 == 0:
        n //= 2; v += 1
    odd = []
    p = 3
    while p * p <= n + 1:
        if n % p == 0:
            n //= p
            cnt = 1
            while n % p == 0:
                n //= p; cnt += 1
            odd.extend([(-1) ** ((p - 1) // 2) * p] * cnt)
        p += 2
    if n > 1:
        odd.append((-1) ** ((n - 1) // 2) * n)
    op = 1
    for f in odd:
        op *= f
    if v % 2 == 0 and v >= 2:
        part2 = [-4] * (v // 2)
    elif v >= 3:
        part2 = [sD * (1 if op > 0 else -1) * 8] + [-4] * ((v - 3) // 2)
    elif v == 1:
        part2 = [2]
    else:
        part2 = []
    return len(set(part2 + odd)) - 1


def load_pairs(path="p91_scaled_results.json"):
    d = json.load(open(path, encoding="utf-8"))
    return [p["pair"] for p in d["pairs"]["deg_matched"]]


def forced_choice(pairs, rng):
    pick_high, n_ok = 0, 0
    for lo, hi in pairs:
        a, b = (lo, hi) if rng.random() < 0.5 else (hi, lo)
        xa, la = params_for(a)
        xb, lb = params_for(b)
        prompt = (f"Two verified mathematical identities (Ramanujan-type 1/pi "
                  f"series parameters):\n\nN={a}: x0={xa:.6f}, lambda={la:.6f}\n"
                  f"N={b}: x0={xb:.6f}, lambda={lb:.6f}\n\n"
                  "Which is STRUCTURALLY MORE SURPRISING / unusual? Judge only "
                  "the structure of the numbers. Answer exactly one line: "
                  "'MORE: N=<n>'.")
        ans = ask_chat(prompt, max_tokens=2048)
        m = re.findall(r"N\s*=\s*(\d+)", ans)
        if m:
            pick_high += int(int(m[-1]) == hi)
            n_ok += 1
    return pick_high, n_ok


def absolute(ids):
    scores = {}
    for n in ids:
        x, l = params_for(n)
        prompt = (f"A verified mathematical identity (Ramanujan-type 1/pi "
                  f"series parameter):\n\nN={n}: x0={x:.6f}, lambda={l:.6f}\n\n"
                  "Rate how STRUCTURALLY SURPRISING / unusual this identity is, "
                  "judging only the structure of the numbers, on an integer "
                  "scale 1 (completely ordinary) to 10 (maximally surprising). "
                  "Answer exactly one line: 'RATING: <integer>'.")
        ans = ask_chat(prompt, max_tokens=2048)
        m = re.findall(r"RATING:\s*(\d+)", ans)
        if m:
            scores[n] = int(m[-1])
    return scores


def main():
    from scipy.stats import spearmanr, binomtest
    GDS = {N: gdepth(N) for N in NS}
    pairs = load_pairs()
    uniq = sorted({n for pr in pairs for n in pr})
    rng = random.Random(20260930)

    k, n = forced_choice(pairs, rng)
    p_fc = binomtest(k, n, 0.5).pvalue if n else 1.0
    scores = absolute(uniq)
    ns_ = sorted(scores)
    rho = spearmanr([GDS[x] for x in ns_], [scores[x] for x in ns_]).statistic \
        if len(ns_) >= 5 else 0.0

    if n and k / n >= 0.6 and p_fc < 0.05:
        verdict = "FORCED"
    elif abs(rho) >= 0.4:
        verdict = "ABSOLUTE"
    else:
        verdict = "NO-SIGNAL (do not use as judge)"
    out = {
        "model": os.environ.get("ARK_MODEL", "doubao-seed-2.1-lite"),
        "forced": {"k": k, "n": n, "rate": round(100 * k / max(n, 1), 1),
                   "p": round(float(p_fc), 4)},
        "absolute": {"n": len(scores), "rho_gdepth": round(float(rho), 3)},
        "recommended_format": verdict,
    }
    tag = re.sub(r"\W+", "_", out["model"])
    json.dump(out, open(f"calibration_{tag}.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
