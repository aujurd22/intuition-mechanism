"""D1 gate: reproduce the Chudnovsky coefficients from the CM point.

Pipeline -- every number below is derived from d=163 alone, except the two
integer coefficients being verified at the end:

  d=163 -> tau = (1+sqrt(-163))/2  ->  nome q = exp(pi*i*tau)
        ->  k2 = (theta2/theta3)^4
        ->  j  = 256(1-k2+k2^2)^3 / (k2^2 (1-k2)^2)  =  -640320^3  (exact)
        ->  z  = -1728/j  (negative => alternating series)
        ->  c_k = (1/2)_k (1/6)_k (5/6)_k / (k!)^3
        ->  S0 = sum c_k z^k,   S1 = sum k c_k z^k

The 1/pi identity then requires

    pi * 640320^(3/2) / 12  ==  A*S0 + B*S1

with (A, B) integers. D1 acceptance: the residual of (A,B)=(13591409,
545140134) must vanish to < 1e-80 relative, AND B recovered by integer
rounding from (Y - A*S0)/S1 must carry >= 60 leading zero digits.

Run:  python series_gen.py     (exit 0 = D1 gate PASS)
"""
import sys

from mpmath import mp, mpc, mpf, sqrt, power, jtheta, exp, rf, factorial, pi

mp.dps = 110

D = 163
A_CHUD, B_CHUD = 13591409, 545140134
TERMS = 25          # |z| ~ 6.6e-15 -> 25 terms reach ~1e-360
GATE = mpf(10) ** -80


def cm_j(d: int):
    """Modular j at the Heegner CM point (d=3 mod 4 a-form), exact for h=1."""
    tau = (1 + mpc(0, mpf(d) ** 0.5)) / 2 if d % 4 == 3 else mpc(0, mpf(d) ** 0.5)
    q = exp(mpc(0, mp.pi) * tau)
    t2, t3 = jtheta(2, 0, q), jtheta(3, 0, q)
    k2 = (t2 / t3) ** 4
    return 256 * (1 - k2 + k2 ** 2) ** 3 / (k2 ** 2 * (1 - k2) ** 2)


def main() -> int:
    j = cm_j(D)
    j_real = mp.re(j)   # Heegner j is exactly real; imag part is float noise
    base = int(round(float((-j_real) ** (1 / 3))))
    print(f"j({D}) = {mp.nstr(j, 30)}")
    print(f"integer cube root: {base}  (check: {base}^3 == -j ? "
          f"{base ** 3 == -int(j_real)})")

    z = 1728 / j_real                   # j<0 for d=163 => z<0 (alternating)
    S0 = S1 = mpf(0)
    for k in range(TERMS):
        ck = (rf(mpf(1) / 2, k) * rf(mpf(1) / 6, k) * rf(mpf(5) / 6, k)
              / factorial(k) ** 3)
        ckz = ck * z ** k
        S0 += ckz
        S1 += k * ckz
    print(f"|z| = {mp.nstr(abs(z), 5)}; S0, S1 summed over {TERMS} terms")

    # from 1/pi = 12*(A*S0 + B*S1)/640320^(3/2):
    #   A*S0 + B*S1 = 640320^(3/2) / (12*pi)   (NOT pi*.../12 -- inverted
    #   identity was the D1-gate bug, caught numerically 2026-09-25)
    Y = base * sqrt(mpf(base)) / (12 * pi)
    resid = Y - (A_CHUD * S0 + B_CHUD * S1)
    rel = abs(resid) / abs(Y)
    print(f"residual (A,B)=({A_CHUD},{B_CHUD}): {mp.nstr(rel, 3)} relative")

    B_round = (Y - A_CHUD * S0) / S1
    digits = -mp.log(abs(B_round - B_CHUD) / B_CHUD, 10)
    print(f"B recovered by rounding: {mp.nstr(B_round, 12)} "
          f"-> integer {B_CHUD} confirmed to {mp.nstr(digits, 3)} digits")

    ok = rel < GATE and digits > 60
    print("D1 GATE PASS" if ok else "D1 GATE FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
