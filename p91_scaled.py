"""P91-scaled: 28 deg-matched + ~10 gdepth-matched pairs, swap-controlled
forced-choice.  Pre-registered verdict rules:
  P91-a (deg-matched, n=28): pick-high-gdepth rate > 50% (binomial) =>
    gdepth IS an independent surprise axis within a degree level.
    NOT significant => gdepth was a proxy artifact.
  P91-b (gdepth-matched, n=10): pick-high-degree > 50% => degree is an
    independent axis within a genus-depth level.
Swap control: each pair is queried in BOTH presentation orders; a pair
only counts when both orders agree (disagreement = abstain, recorded)."""
import sys
sys.path.insert(0, ".")
import json
import itertools
import numpy as np
from p33_n20 import params_for, DEG, NS
from llm_client import ask_chat

def gdepth(N):
    D = -24*N
    sD = -1 if D < 0 else 1
    n = abs(D); v = 0
    while n % 2 == 0: n //= 2; v += 1
    odd = []
    p = 3
    while p*p <= n + 1:
        if n % p == 0:
            n //= p
            cnt = 1
            while n % p == 0: n //= p; cnt += 1
            odd.extend([(-1)**((p-1)//2)*p] * cnt)
        p += 2
    if n > 1: odd.append((-1)**((n-1)//2)*n)
    odd_prod = 1
    for f in odd: odd_prod *= f
    if v % 2 == 0 and v >= 2: part2 = [-4]*(v//2)
    elif v >= 3: part2 = [sD*(1 if odd_prod > 0 else -1)*8] + [-4]*((v-3)//2)
    elif v == 1: part2 = [2]
    else: part2 = []
    return len(set(part2 + odd)) - 1

DEGS = {N: DEG[N] for N in NS}
GDS = {N: gdepth(N) for N in NS}

def judge(nA, nB):
    xA, lA = params_for(nA)
    xB, lB = params_for(nB)
    prompt = (f"Two verified mathematical identities (Ramanujan-type 1/pi series "
              f"parameters):\n\nN={nA}: x0={xA:.6f}, lambda={lA:.6f}\n"
              f"N={nB}: x0={xB:.6f}, lambda={lB:.6f}\n\n"
              "Which is STRUCTURALLY MORE SURPRISING / unusual? Judge only the "
              "structure of the numbers. Answer exactly one line: 'MORE: N=<n>'.")
    ans = ask_chat(prompt, max_tokens=2048)
    m = __import__("re").findall(r"N\s*=\s*(\d+)", ans)
    return int(m[-1]) if m else None

def swap_controlled(n_hi_gd, n_lo_gd):
    """n_hi_gd has higher gdepth.  Returns 'high'/'low'/None (disagree)."""
    votes = {"high": 0, "low": 0}
    for first, second in ((n_lo_gd, n_hi_gd), (n_hi_gd, n_lo_gd)):
        w = judge(first, second)
        if w is None: continue
        votes["high" if w == n_hi_gd else "low"] += 1
    if votes["high"] > votes["low"]: return "high"
    if votes["low"] > votes["high"]: return "low"
    return None


def run_experiment():
    # ---- deg-matched pairs: same degree, LOW vs HIGH gdepth ----
    deg_matched = []
    for dg in sorted(set(DEGS.values())):
        pool = [N for N in NS if DEGS[N] == dg]
        if len(pool) < 2: continue
        gmin, gmax = min(GDS[N] for N in pool), max(GDS[N] for N in pool)
        if gmin == gmax: continue
        lows = [N for N in pool if GDS[N] == gmin]
        highs = [N for N in pool if GDS[N] == gmax]
        allp = list(itertools.product(lows, highs))
        rng = np.random.default_rng(9101 + dg)
        take = allp if len(allp) <= 8 else list(rng.choice(len(allp), 8, replace=False)
                                                .__class__(rng.choice(len(allp), 8,
                                                                      replace=False)))
        if len(allp) <= 8:
            take = allp
        else:
            idx = rng.choice(len(allp), 8, replace=False)
            take = [allp[i] for i in idx]
        for (lo, hi) in take:
            deg_matched.append((lo, hi, dg))

    # ---- gdepth-matched pairs: same gdepth, LOW vs HIGH degree ----
    gd_matched = []
    for g in sorted(set(GDS.values())):
        pool = [N for N in NS if GDS[N] == g]
        if len(pool) < 2: continue
        dmin, dmax = min(DEGS[N] for N in pool), max(DEGS[N] for N in pool)
        if dmin == dmax: continue
        lows = [N for N in pool if DEGS[N] == dmin]
        highs = [N for N in pool if DEGS[N] == dmax]
        for lo in lows[:2]:
            for hi in highs[:2]:
                gd_matched.append((lo, hi, g))

    print(f"deg-matched: {len(deg_matched)} pairs; gdepth-matched: {len(gd_matched)} pairs")

    res = {"deg_matched": [], "gdepth_matched": []}
    hi_votes = {"deg": [], "gdepth": []}
    for (lo, hi, dg) in deg_matched:
        pick = swap_controlled(hi, lo)   # hi = higher gdepth
        rec = {"pair": (lo, hi), "degree": dg, "gdepths": (GDS[lo], GDS[hi]),
               "pick": pick}
        res["deg_matched"].append(rec)
        if pick: hi_votes["deg"].append(pick == "high")
        print(f"deg={dg}: ({lo} g{GDS[lo]}) vs ({hi} g{GDS[hi]}) -> "
              f"{pick or 'ABSTAIN'}")
    for (lo, hi, g) in gd_matched:
        d_lo, d_hi = DEGS[lo], DEGS[hi]
        pick = swap_controlled(hi, lo)   # hi = higher degree
        rec = {"pair": (lo, hi), "gdepth": g, "degrees": (d_lo, d_hi),
               "pick": pick}
        res["gdepth_matched"].append(rec)
        if pick: hi_votes["gdepth"].append(pick == "high")
        print(f"gdepth={g}: ({lo} d{DEGS[lo]}) vs ({hi} d{DEGS[hi]}) -> "
              f"{pick or 'ABSTAIN'}")

    from scipy.stats import binomtest
    summary = {}
    for axis, votes in hi_votes.items():
        n = len(votes); k = sum(votes)
        p = binomtest(k, n, 0.5).pvalue if n else None
        summary[axis] = {"n_consistent": n, "k_high": k,
                         "rate": round(100*k/n, 1) if n else None,
                         "p_two_sided": round(p, 4) if p is not None else None}
        print(f"{axis}: {k}/{n} = {100*k/max(n,1):.1f}%  (binomial p={p})")
    json.dump({"pairs": res, "summary": summary},
              open("p91_scaled_results.json", "w"), indent=1)
    print("saved p91_scaled_results.json")


if __name__ == "__main__":
    run_experiment()
