"""Control: can the posz_scan machinery REDISCOVER a known positive-z series?
eq28: 1/pi = sum (1+6k) H_k (1/4)^k  -> (A,B,M) = (1,6,4), s=2, z=1/4.
If the grid misses this, the 0/9 is a scanner artifact, not a fact.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mpmath import mp, mpf, pslq, pi

mp.dps = 80


def H(k, s):
    from mpmath import rf, factorial
    return rf(mpf(1) / 2, k) * rf(mpf(1) / s, k) * rf(mpf(1) - 1 / mpf(s), k) \
        / factorial(k) ** 3


def sums(z, s, terms):
    S0 = S1 = mpf(0)
    for k in range(terms):
        h = H(k, s) * z ** k
        S0 += h
        S1 += k * h
    return S0, S1


# --- exact check at the known z ---
z = mpf(1) / 4
S0, S1 = sums(z, 2, 120)
rel = pslq([S0, S1, -1 / pi], tol=mpf(10) ** -40, maxcoeff=10 ** 12)
print(f"eq28 at z=1/4, s=2: pslq -> {rel}  (expect [1, 6, 4])")

# --- grid check: does the scan grid contain a z close enough to 1/4? ---
import numpy as np
# where does 1/4 sit? find nearest grid point
import math
target = float(z)
lg = np.linspace(-6, math.log10(0.5), 240)
dists = [abs(10 ** e - target) for e in lg]
i_best = int(np.argmin(dists))
z_best = mpf(10) ** lg[i_best]
print(f"nearest grid point to 1/4: z = {mp.nstr(z_best, 12)} "
      f"(rel err {mp.nstr(abs(z_best - z) / z, 3)})")
S0g, S1g = sums(z_best, 2, 300)
relg = pslq([S0g, S1g, -1 / pi], tol=mpf(10) ** -40, maxcoeff=10 ** 12)
print(f"pslq at nearest grid point -> {relg}")
if relg is None or abs(relg[0]) > 10 ** 6:
    print("=> GRID IS TOO COARSE at z~0.25: pslq fails off the exact z.")
    # refine: local scan around 1/4
    fine = [mpf(1) / 4 + delta for delta in
            (0, mpf(10) ** -6, -mpf(10) ** -6)]
    for zf in fine:
        S0f, S1f = sums(zf, 2, 300)
        relf = pslq([S0f, S1f, -1 / pi], tol=mpf(10) ** -40, maxcoeff=10 ** 12)
        print(f"  fine z={mp.nstr(zf, 15)}: pslq -> {relf}")
