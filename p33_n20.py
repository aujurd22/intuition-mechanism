"""P33-n20: interestingness correspondence at scale (pre-registered,
queued item #3).  21 identities = every census row with a known
lambda-degree (5 deg-1 + 8 deg-2 + 8 deg-3, interleaved by N).

Value axis (mechanical, registered): the lambda-degree itself
(1 < 2 < 3) -- P36-a established it reproduces the human publication
boundary.  Blind judge (deepseek-v4.1-flash, different family from
prior doubao/GLM judges): ranks ALL 21 by structural surprise given
the N-order presentation.  Correspondence: Spearman(judge, degree).

Registered bands (from P33): CONFIRMED rho >= 0.5; PARTIAL 0.3-0.5;
NEGATIVE < 0.3.

Run:  ARK_MODEL=deepseek-v4.1-flash python p33_n20.py
"""
import json
import os
import sys

import mpmath as mm
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm_client import ask_chat  # noqa: E402

mm.mp.dps = 40

CENSUS = json.load(open("p36a_lambda_census.json"))
DEG = {r["N"]: r["deg"] for r in CENSUS
       if "deg" in r and "error" not in r}
NS = sorted(DEG)          # 21 identities with known degrees


def params_for(N):
    from math import comb
    def t_seq(n):
        v = 0
        for k in range(n // 2 + 1):
            v += (comb(n, 2*k) * comb(2*k, k)**2
                  * comb(2*n - 4*k, n - 2*k))
        return v
    q = mm.exp(-2 * mm.pi * mm.sqrt(mm.mpf(N) / 24))
    x0 = mm.mpf(mm.re(__import__("p19b_z12").x12(q)))
    ts = [mm.mpf(t_seq(n)) for n in range(400)]
    S0 = sum(ts[n] * x0**n for n in range(400))
    S1 = sum(n * ts[n] * x0**n for n in range(400))
    r = (1/(2*mm.pi)) * mm.sqrt(mm.mpf(24)/N) / \
        mm.sqrt((1+4*x0)*(1-4*x0)*(1-8*x0))
    lam = (r - S1) / S0
    return float(x0.real), float(lam.real)


def main():
    tuples = []
    for N in NS:
        x0, lam = params_for(N)
        tuples.append((N, x0, lam, DEG[N]))
        print(f"N={N:3d} deg={DEG[N]} x0={x0:.6f} lam={lam:.6f}", flush=True)

    listing = "\n".join(
        f"N={N}: x0={x0:.6f}, lambda={lam:.6f}" for N, x0, lam, _ in tuples)
    prompt = (
        "You are shown a sequence of verified mathematical identities "
        "(Ramanujan-type 1/pi series parameters), in the order they were "
        "discovered (by N):\n" + listing +
        "\n\nRank ALL of them by how STRUCTURALLY SURPRISING each one is "
        "given everything seen before it -- novelty of the (x0, lambda) "
        "pair relative to the earlier pattern. Do NOT use N itself as a "
        "cue; judge the structure of the number pairs.\n\n"
        "Output exactly 21 lines, each of the form 'N=<n> <rank>' with "
        "rank 1 = MOST surprising, no ties, every identity ranked.")
    ans = ask_chat(prompt, max_tokens=8192)
    print("=== judge output (head) ===")
    print(ans[:600])

    import re
    ranks = {}
    for m in re.finditer(r"N\s*=\s*(\d+)\s*[:\- ]\s*(\d+)", ans):
        ranks[int(m.group(1))] = int(m.group(2))
    parsed = [N for N in NS if N in ranks]
    print(f"\nparsed {len(parsed)}/{len(NS)} judge rankings")

    degs = [DEG[N] for N in parsed]
    llm_r = [ranks[N] for N in parsed]
    def rank_of(v):
        return np.argsort(np.argsort(v))
    if len(parsed) >= 15:
        rho_deg = float(np.corrcoef(rank_of(degs), rank_of(llm_r))[0, 1])
        verdict = ("CONFIRMED" if rho_deg >= 0.5 else
                   "PARTIAL" if rho_deg >= 0.3 else "NEGATIVE")
        print(f"Spearman rho (lambda-degree vs judge surprise) = "
              f"{rho_deg:.3f} over {len(parsed)} -> {verdict}")
    else:
        rho_deg = None
        verdict = "NEGATIVE (unparseable)"
    json.dump({"Ns": parsed, "degrees": degs, "llm_ranks": llm_r,
               "spearman_rho_degree": rho_deg, "verdict": verdict},
              open("p33_n20_results.json", "w"), indent=1)
    print("saved p33_n20_results.json")


if __name__ == "__main__":
    main()
