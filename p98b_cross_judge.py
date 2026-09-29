"""P98-b: cross-judge replication of the two-axis interestingness theory.
Judges: deepseek-v4.1-flash (discovering judge), kimi-k2.8-preview,
minimax-m3.  Identical pair lists (deg-matched 19 + utility 8),
identical prompts, swap-controlled.  Verdicts per judge, then
agreement table."""
import os
os.environ.setdefault("HF_HUB_OFFLINE", "0")
import sys
sys.path.insert(0, ".")
import json
import re
import numpy as np
from p33_n20 import params_for, DEG, NS
from llm_client import ask_chat


def gdepth(N):
    D = -24 * N
    sD = -1 if D < 0 else 1
    n = abs(D)
    v = 0
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


def judge(nA, nB, framing):
    xA, lA = params_for(nA)
    xB, lB = params_for(nB)
    q = {
        "surprise": "Which is STRUCTURALLY MORE SURPRISING / unusual?",
        "utility": ("Which would be MORE USEFUL as a seed for discovering "
                    "further identities of the same kind?"),
    }[framing]
    prompt = ("Two verified mathematical identities (Ramanujan-type 1/pi series "
              "parameters):\n\n"
              f"N={nA}: x0={xA:.6f}, lambda={lA:.6f}\n"
              f"N={nB}: x0={xB:.6f}, lambda={lB:.6f}\n\n{q} Judge only the "
              f"structure of the numbers. Answer exactly one line: 'MORE: N=<n>'.")
    ans = ask_chat(prompt, max_tokens=2048)
    m = re.findall(r"N\s*=\s*(\d+)", ans)
    return int(m[-1]) if m else None


# rebuild the identical deg-matched pair list (same seeds as P91-scaled)
rng = np.random.default_rng(9101)
deg_pairs = []
deg_pool = {}
for N in NS:
    deg_pool.setdefault(DEG[N], []).append(N)
for dg in sorted(d for d in set(DEG.values()) if d is not None):
    pool = [N for N in NS if DEG[N] == dg]
    if len(pool) < 2:
        continue
    gmin = min(gdepth(N) for N in pool)
    gmax = max(gdepth(N) for N in pool)
    if gmin == gmax:
        continue
    lows = [N for N in pool if gdepth(N) == gmin]
    highs = [N for N in pool if gdepth(N) == gmax]
    allp = list(__import__("itertools").product(lows, highs))
    if len(allp) <= 8:
        take = allp
    else:
        idx = rng.choice(len(allp), 8, replace=False)
        take = [allp[i] for i in idx]
    for (lo, hi) in take:
        deg_pairs.append((lo, hi, dg))

# utility pairs (rational vs deep)
utility_pairs = [(3, 29), (5, 37), (7, 31), (13, 53), (17, 49),
                 (7, 27), (13, 9), (17, 2)]

JUDGES = ["deepseek-v4.1-flash", "kimi-k2.8-preview", "minimax-m3"]
all_out = {}
for judge_model in JUDGES:
    os.environ["ARK_MODEL"] = judge_model
    # re-import to pick up the new MODEL
    import importlib
    import llm_client
    importlib.reload(llm_client)
    from llm_client import ask_chat as _ac
    globals()["ask_chat"] = _ac

    jres = {"deg_high_gdepth": 0, "deg_decided": 0, "deg_pairs": [],
            "util_rational": 0, "util_decided": 0, "util_pairs": []}
    for (lo, hi, dg) in deg_pairs:
        for first, second in ((lo, hi), (hi, lo)):
            w = judge(first, second, "surprise")
            if w is None:
                continue
            jres["deg_decided"] += 1
            pick_high = (w == hi)
            jres["deg_high_gdepth"] += pick_high
            jres["deg_pairs"].append({"pair": (lo, hi), "pick_high": pick_high})
    for (rat, deep) in utility_pairs:
        for first, second in ((rat, deep), (deep, rat)):
            w = judge(first, second, "utility")
            if w is None:
                continue
            jres["util_decided"] += 1
            pick_rat = (w == rat)
            jres["util_rational"] += pick_rat
            jres["util_pairs"].append({"pair": (rat, deep),
                                       "pick_rational": pick_rat})
    dd = jres["deg_decided"] or 1
    ud = jres["util_decided"] or 1
    print(f"{judge_model}: deg-axis high-gdepth {jres['deg_high_gdepth']}/"
          f"{jres['deg_decided']} ({100*jres['deg_high_gdepth']/dd:.0f}%) | "
          f"utility rational {jres['util_rational']}/{jres['util_decided']} "
          f"({100*jres['util_rational']/ud:.0f}%)")
    all_out[judge_model] = jres

json.dump(all_out, open("p98b_cross_judge.json", "w"), indent=1)
print("saved p98b_cross_judge.json")
