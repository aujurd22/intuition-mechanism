"""Solve for the true power-base z of each failing series (gate-driven
transcription correction): findroot of sum(z) = mult/pi at 60 digits, then
compare against the transcribed z. A clean rational/algebraic z_true means
the summand structure is right and only the base was mis-transcribed.

Run:  python solve_z.py
"""
import sys

from mpmath import mp, mpf, pi, sqrt, rf, factorial, findroot

mp.dps = 60


def poch3(p, k):
    a, b, c = p
    if (a, b, c) == (1 / 2, 1 / 2, 1 / 2):
        return rf(a, k) ** 3 / factorial(k) ** 3
    return rf(a, k) * rf(b, k) * rf(c, k) / factorial(k) ** 3


def hyper_sum(z, A, B, p, c0, k0=1, terms=120):
    total = c0
    for k in range(k0, terms):
        total += (A + B * k) * poch3(p, k) * z ** k
    return total


CASES = [
    # eq, mult (sum(z)*pi must equal this), c0, A, B, poch-triple, transcribed z
    dict(eq=31, mult=27 / 4, c0=mpf(2), A=2, B=15,
         p=(1 / 2, 1 / 3, 2 / 3), zt=mpf(2) / 27),
    dict(eq=32, mult=15 * sqrt(3) / 2, c0=mpf(4), A=4, B=33,
         p=(1 / 2, 1 / 3, 2 / 3), zt=mpf(4) / 125),
    dict(eq=33, mult=5 * sqrt(5) / (2 * sqrt(3)), c0=mpf(1), A=1, B=11,
         p=(1 / 2, 1 / 6, 5 / 6), zt=mpf(4) / 125),
    dict(eq=34, mult=85 * sqrt(85) / (18 * sqrt(3)), c0=mpf(8), A=8, B=133,
         p=(1 / 2, 1 / 6, 5 / 6), zt=(mpf(4) / 85) ** 3),
    dict(eq=35, mult=4, c0=mpf(3) / 2, A=3, B=20,
         p=(1 / 2, 1 / 4, 3 / 4), zt=mpf(-1) / 8),
    dict(eq=36, mult=4 / sqrt(3), c0=mpf(3) / 4, A=3, B=28,
         p=(1 / 2, 1 / 4, 3 / 4), zt=mpf(-1) / 12),
    dict(eq=37, mult=4, c0=mpf(23) / 18, A=23, B=260,
         p=(1 / 2, 1 / 4, 3 / 4), zt=mpf(-1) / 72),
    dict(eq=38, mult=4 / sqrt(5), c0=mpf(41) / 72, A=41, B=644,
         p=(1 / 2, 1 / 4, 3 / 4), zt=mpf(-1) / 360),
    dict(eq=39, mult=4, c0=mpf(1123) / 882, A=1123, B=21460,
         p=(1 / 2, 1 / 4, 3 / 4), zt=mpf(-1) / 1764),
    dict(eq=40, mult=2 * sqrt(3), c0=mpf(1), A=1, B=8,
         p=(1 / 2, 1 / 4, 3 / 4), zt=mpf(4) / 9),
    dict(eq=41, mult=1 / (2 * sqrt(2)), c0=mpf(1) / 9, A=1, B=10,
         p=(1 / 2, 1 / 4, 3 / 4), zt=mpf(4) / 81),
    dict(eq=42, mult=1 / (3 * sqrt(3)), c0=mpf(3) / 49, A=3, B=40,
         p=(1 / 2, 1 / 4, 3 / 4), zt=mpf(4) / 49),
    dict(eq=43, mult=2 / sqrt(11), c0=mpf(19) / 99, A=19, B=280,
         p=(1 / 2, 1 / 4, 3 / 4), zt=mpf(4) / 99),
    dict(eq=44, mult=1 / (2 * sqrt(2)), c0=mpf(1103) / 99 ** 2, A=1103, B=26390,
         p=(1 / 2, 1 / 4, 3 / 4), zt=mpf(4) / 99 ** 4),
]


def main() -> int:
    for s in CASES:
        target = s["mult"] / pi
        try:
            z_true = findroot(
                lambda zz: hyper_sum(zz, s["A"], s["B"], s["p"], s["c0"]) - target,
                s["zt"], tol=mpf(10) ** -50, maxsteps=50)
        except Exception as e:
            print(f"  eq({s['eq']}): findroot failed ({str(e)[:40]})")
            continue
        print(f"  eq({s['eq']}): z_true = {mp.nstr(z_true, 25)}   "
              f"(transcribed {mp.nstr(s['zt'], 12)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
