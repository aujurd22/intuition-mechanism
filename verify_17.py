"""Item-by-item mechanical verification of Ramanujan's 17 series for 1/pi
(1914, "Modular equations and approximations to pi", equations 28-44).

Transcribed from the primary source (ramanujan.sirinudi.org ram06.html).
Each entry: {eq, lhs (multiplier M such that the series sums to M/pi, or an
explicit X/pi form), c0 (constant/leading fraction term), A, B (arithmetic
progression integers for the continuation), a triple of Pochhammer
parameters (p1,p2,p3), z (power base), and k0 (first continuation index)}.

Structure per series:
  sum = c0 + sum_{k>=k0} (A + B*k) * Poch(p1,k)Poch(p2,k)Poch(p3,k)/(k!)^3 * z^k
and the gate checks  sum * pi == stated value  to 1e-45.

For eq 35-44 the printed r_k = 4^(k-1) * h_k with h_k =
(1/2)_k(1/4)_k(3/4)_k/(k!)^3 -- folded into (A,B,z,k0) below.

Run:  python verify_17.py    (prints PASS/FAIL per equation, exit 0 iff all)
"""
import sys

from mpmath import mp, mpf, pi, sqrt, rf, factorial

mp.dps = 60
TOL = mpf(10) ** -45


def poch3(p, k):
    a, b, c = p
    if a == 1 / 2 and b == 1 / 2 and c == 1 / 2:
        return rf(a, k) ** 3 / factorial(k) ** 3
    return rf(a, k) * rf(b, k) * rf(c, k) / factorial(k) ** 3


SERIES = [
    # eq, lhs_target (= sum*pi / stated-constant handling via mult), c0, A, B, poch, z, k0
    dict(eq=28, mult=4, c0=mpf(1), A=1, B=6,
         p=(1 / 2, 1 / 2, 1 / 2), z=mpf(1) / 4, k0=1),
    dict(eq=29, mult=16, c0=mpf(5), A=5, B=42,
         p=(1 / 2, 1 / 2, 1 / 2), z=mpf(1) / 64, k0=1),
    dict(eq=30, mult=32, c0=5 * sqrt(5) - 1, A=42 * sqrt(5) + 30, B=0,
         p=(1 / 2, 1 / 2, 1 / 2), z=((sqrt(5) - 1) / 2) ** 8, k0=1, linear_in=sqrt(5)),
    dict(eq=31, mult=27 / 4, c0=mpf(2), A=2, B=15,
         p=(1 / 2, 1 / 3, 2 / 3), z=mpf(2) / 27, k0=1),
    dict(eq=32, mult=15 * sqrt(3) / 2, c0=mpf(4), A=4, B=33,
         p=(1 / 2, 1 / 3, 2 / 3), z=mpf(4) / 125, k0=1),
    dict(eq=33, mult=5 * sqrt(5) / (2 * sqrt(3)), c0=mpf(1), A=1, B=11,
         p=(1 / 2, 1 / 6, 5 / 6), z=mpf(4) / 125, k0=1),
    dict(eq=34, mult=85 * sqrt(85) / (18 * sqrt(3)), c0=mpf(8), A=8, B=133,
         p=(1 / 2, 1 / 6, 5 / 6), z=(mpf(4) / 85) ** 3, k0=1),
    dict(eq=35, mult=4, c0=mpf(3) / 2, A=3, B=20,
         p=(1 / 2, 1 / 4, 3 / 4), z=mpf(-1) / 8, k0=1),
    dict(eq=36, mult=4 / sqrt(3), c0=mpf(3) / 4, A=3, B=28,
         p=(1 / 2, 1 / 4, 3 / 4), z=mpf(-1) / 12, k0=1),
    dict(eq=37, mult=4, c0=mpf(23) / 18, A=23, B=260,
         p=(1 / 2, 1 / 4, 3 / 4), z=mpf(-1) / 72, k0=1),
    dict(eq=38, mult=4 / sqrt(5), c0=mpf(41) / 72, A=41, B=644,
         p=(1 / 2, 1 / 4, 3 / 4), z=mpf(-1) / 360, k0=1),
    dict(eq=39, mult=4, c0=mpf(1123) / 882, A=1123, B=21460,
         p=(1 / 2, 1 / 4, 3 / 4), z=mpf(-1) / 1764, k0=1),
    dict(eq=40, mult=2 * sqrt(3), c0=mpf(1), A=1, B=8,
         p=(1 / 2, 1 / 4, 3 / 4), z=mpf(4) / 9, k0=1),
    dict(eq=41, mult=1 / (2 * sqrt(2)), c0=mpf(1) / 9, A=1, B=10,
         p=(1 / 2, 1 / 4, 3 / 4), z=mpf(4) / 81, k0=1),
    dict(eq=42, mult=1 / (3 * sqrt(3)), c0=mpf(3) / 49, A=3, B=40,
         p=(1 / 2, 1 / 4, 3 / 4), z=mpf(4) / 49, k0=1),
    dict(eq=43, mult=2 / sqrt(11), c0=mpf(19) / 99, A=19, B=280,
         p=(1 / 2, 1 / 4, 3 / 4), z=mpf(4) / 99, k0=1),
    dict(eq=44, mult=1 / (2 * sqrt(2)), c0=mpf(1103) / 99 ** 2, A=1103, B=26390,
         p=(1 / 2, 1 / 4, 3 / 4), z=mpf(4) / 99 ** 4, k0=1),
]


def main() -> int:
    npass = 0
    for s in SERIES:
        total = s["c0"]
        for k in range(s["k0"], 80):
            total += (s["A"] + s["B"] * k) * poch3(s["p"], k) * s["z"] ** k
        # gate: total == mult / pi   <=>  total * pi == mult
        err = abs(total * pi - s["mult"])
        ok = err < TOL
        npass += ok
        print(f"  eq({s['eq']}): |sum*pi - {mp.nstr(s['mult'], 6)}| = "
              f"{mp.nstr(err, 3)}  {'PASS' if ok else 'FAIL'}")
    print(f"\n{npass}/{len(SERIES)} series verified at 1e-45")
    return 0 if npass == len(SERIES) else 1


if __name__ == "__main__":
    sys.exit(main())
