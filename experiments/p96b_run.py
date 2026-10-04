"""P96-b: within-gdepth=2 degree pairs -- does surprise track degree
when genus depth is fixed?  Swap-controlled, abstain recorded."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root
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


def judge(nA, nB):
    xA, lA = params_for(nA)
    xB, lB = params_for(nB)
    prompt = ("Two verified mathematical identities (Ramanujan-type 1/pi series "
              "parameters):\n\n"
              f"N={nA}: x0={xA:.6f}, lambda={lA:.6f}\n"
              f"N={nB}: x0={xB:.6f}, lambda={lB:.6f}\n\n"
              "Which is STRUCTURALLY MORE SURPRISING / unusual? Judge only the "
              "structure of the numbers. Answer exactly one line: 'MORE: N=<n>'.")
    ans = ask_chat(prompt, max_tokens=2048)
    m = re.findall(r"N\s*=\s*(\d+)", ans)
    return int(m[-1]) if m else None


rng = np.random.default_rng(9601)
G2 = [N for N in NS if gdepth(N) == 2]
pairs = []
for (da, db) in ((1, 2), (1, 3), (2, 3)):
    la = [N for N in G2 if DEG[N] == da]
    lb = [N for N in G2 if DEG[N] == db]
    for _ in range(7):
        if la and lb:
            pairs.append((da, db, int(rng.choice(la)), int(rng.choice(lb))))
print(f"sampling {len(pairs)} pairs from {len(G2)} gdepth-2 rows")

records = []
for (da, db, nA, nB) in pairs:
    d_lo, d_hi = min(da, db), max(da, db)
    if da < db:
        n_lo, n_hi = nA, nB
    else:
        n_lo, n_hi = nB, nA
    votes = {"lo": 0, "hi": 0, "abstain": 0}
    for first, second in ((n_lo, n_hi), (n_hi, n_lo)):
        w = judge(first, second)
        if w is None:
            votes["abstain"] += 1
        elif w == n_hi:
            votes["hi"] += 1
        else:
            votes["lo"] += 1
    records.append({"pair": [n_lo, n_hi], "degrees": [d_lo, d_hi],
                    "votes": votes})
    print(f"deg {d_lo}v{d_hi} ({n_lo},{n_hi}): lo={votes['lo']} "
          f"hi={votes['hi']} abs={votes['abstain']}")

hi_wins = sum(1 for r in records if r["votes"]["hi"] > r["votes"]["lo"])
lo_wins = sum(1 for r in records if r["votes"]["lo"] > r["votes"]["hi"])
ties = sum(1 for r in records if r["votes"]["hi"] == r["votes"]["lo"])
abst = sum(r["votes"]["abstain"] for r in records)
print(f"SUMMARY: hi-degree wins {hi_wins}, lo-degree wins {lo_wins}, "
      f"ties {ties}, abstain votes {abst}")
json.dump(records, open("p96b_within_g2.json", "w"), indent=1)
print("saved p96b_within_g2.json")
