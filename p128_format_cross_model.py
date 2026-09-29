"""P128: cross-model test of the FORMAT effect (P119) — deepseek-v4-flash.

P119 (single model, deepseek-v4.1-flash): forced-choice detects the
gdepth axis (88.9%), absolute 1-10 rating does not (rho ~ 0.254 ns).
P98-b: kimi/minimax are near-chance at forced choice (floor — untestable
for format effects).  This run tests the second deepseek sibling:

  Format A  forced choice (P91 prompt verbatim), 19 deg-matched pairs,
             single presentation order with seeded side randomization
  Format B  absolute 1-10 rating per identity (P118-b protocol), the
             21 unique N's, rho(gdepth) and the paired within-pair
             difference test

Prediction if the format effect is a deepseek-family property:
forced > 50% (binomial) while absolute rho ~ 0.
"""
import os
os.environ.setdefault("ARK_MODEL", "deepseek-v4-flash")
import sys
sys.path.insert(0, ".")
import json, re, random
from p33_n20 import params_for, DEG, NS
from llm_client import ask_chat


def gdepth(N):
    """Inlined copy of p91_scaled.gdepth — do NOT import p91_scaled: its
    module-level code re-runs the API experiment and overwrites artifacts
    (the 2026-09-30 incident, see registry P128)."""
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
    odd_prod = 1
    for f in odd:
        odd_prod *= f
    if v % 2 == 0 and v >= 2:
        part2 = [-4] * (v // 2)
    elif v >= 3:
        part2 = [sD * (1 if odd_prod > 0 else -1) * 8] + [-4] * ((v - 3) // 2)
    elif v == 1:
        part2 = [2]
    else:
        part2 = []
    return len(set(part2 + odd)) - 1

GDS = {N: gdepth(N) for N in NS}
results = json.load(open("p91_scaled_results.json"))
pairs = [p["pair"] for p in results["pairs"]["deg_matched"]]
uniq = sorted({n for pr in pairs for n in pr})
rng = random.Random(20260930)

# ---- Format A: forced choice, randomized side ----
pick_high, n_ok = 0, 0
detail = []
for lo, hi in pairs:
    a, b = (lo, hi) if rng.random() < 0.5 else (hi, lo)
    xa, la = params_for(a)
    xb, lb = params_for(b)
    prompt = (f"Two verified mathematical identities (Ramanujan-type 1/pi series "
              f"parameters):\n\nN={a}: x0={xa:.6f}, lambda={la:.6f}\n"
              f"N={b}: x0={xb:.6f}, lambda={lb:.6f}\n\n"
              "Which is STRUCTURALLY MORE SURPRISING / unusual? Judge only the "
              "structure of the numbers. Answer exactly one line: 'MORE: N=<n>'.")
    ans = ask_chat(prompt, max_tokens=2048)
    m = re.findall(r"N\s*=\s*(\d+)", ans)
    if m:
        pick = int(m[-1])
        hit = (pick == hi)
        pick_high += int(hit)
        n_ok += 1
        detail.append({"pair": [lo, hi], "shown": [a, b], "pick": pick,
                       "high": hit})
    detail.append if False else None

# ---- Format B: absolute rating ----
scores = {}
for n in uniq:
    x, l = params_for(n)
    prompt = (f"A verified mathematical identity (Ramanujan-type 1/pi series "
              f"parameter):\n\nN={n}: x0={x:.6f}, lambda={l:.6f}\n\n"
              "Rate how STRUCTURALLY SURPRISING / unusual this identity is, "
              "judging only the structure of the numbers, on an integer scale "
              "1 (completely ordinary) to 10 (maximally surprising). "
              "Answer exactly one line: 'RATING: <integer>'.")
    ans = ask_chat(prompt, max_tokens=2048)
    m = re.findall(r"RATING:\s*(\d+)", ans)
    if m:
        scores[n] = int(m[-1])

from scipy.stats import spearmanr
ns = sorted(scores)
rho_gd = spearmanr([GDS[n] for n in ns], [scores[n] for n in ns]).statistic
rho_deg = spearmanr([DEG[n] for n in ns], [scores[n] for n in ns]).statistic
# paired within-pair sign test on rating differences
wins = 0
valid = 0
for lo, hi in pairs:
    if lo in scores and hi in scores and scores[lo] != scores[hi]:
        valid += 1
        wins += int(scores[hi] > scores[lo])

out = {
    "model": os.environ.get("ARK_MODEL"),
    "forced_choice": {"n_valid": n_ok, "pick_high": pick_high,
                      "rate": round(100 * pick_high / max(n_ok, 1), 1)},
    "absolute": {"n_scored": len(scores), "rho_gdepth": round(float(rho_gd), 3),
                 "rho_degree": round(float(rho_deg), 3),
                 "pair_wins_high": wins, "pair_valid": valid},
    "scores": scores,
    "detail": detail,
}
json.dump(out, open("p128_format_cross_model.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("model", "forced_choice", "absolute")},
                 indent=1))
