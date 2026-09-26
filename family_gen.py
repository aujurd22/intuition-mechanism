"""Family generator skeleton: Heegner d -> integer 1/pi series.

T2 Phase 0 quick-start item 2 (Intuition-Mechanism Program, D1).

Math path (Borwein & Borwein, Pi and the AGM ch.5; Chudnovsky):
  tau   = (1+sqrt(-d))/2  for d = 3 mod 4, else sqrt(-d)   (Heegner CM point)
  q     = exp(2*pi*i*tau)                                  (|q| = exp(-pi*sqrt(d)))
  k2    = (theta2(0,q)/theta3(0,q))^4                      (singular modulus k_d^2)
  j     = 256*(1-k2+k2^2)^3 / (k2^2*(1-k2)^2)              (modular invariant)

Anchor (d=163): j((1+sqrt(-163))/2) ~= -640320^3  (Ramanujan constant;
e^(pi*sqrt(163)) = 640320^3 + 744 + eps) -- self-test below must PASS at
1e-40 relative before any series generation is trusted.

series_from_j() is the PSLQ integer-relation interface (D1 acceptance);
returns NotImplemented until the Borwein derivation pipeline lands.

Run:  python family_gen.py    (runs the d=163 anchor self-test)
"""
import sys

from mpmath import mp, mpc, mpf, sqrt, power, jtheta, exp

mp.dps = 100

# Heegner numbers (class number 1) + Chudnovsky's d=163 family anchor
HEEGNER = [1, 2, 3, 7, 11, 19, 43, 67, 163]


def cm_tau(d: int):
    """CM point tau with |Im(tau)| = sqrt(d)/2 (d=3 mod 4 uses the a-form)."""
    if d % 4 == 3:
        return (1 + mpc(0, mpf(d) ** 0.5)) / 2
    return mpc(0, mpf(d) ** 0.5)


def singular_modulus_k2(d: int):
    """k_d^2 via theta constants at nome q = exp(pi*i*tau).

    NOTE: theta functions use nome exp(pi*i*tau) (period pi), NOT
    exp(2*pi*i*tau) -- the squared nome makes lambda complex at CM points
    and gave j = +6.9e34 instead of -640320^3 for d=163 (caught by the
    anchor self-test, 2026-09-24).
    """
    q = exp(mpc(0, mp.pi) * cm_tau(d))
    t2 = jtheta(2, 0, q)
    t3 = jtheta(3, 0, q)
    return (t2 / t3) ** 4


def j_from_k2(k2):
    return 256 * (1 - k2 + k2 ** 2) ** 3 / (k2 ** 2 * (1 - k2) ** 2)


def series_from_j(j_val, d: int):
    """PSLQ integer-relation pipeline: j -> (A, B) coefficients -> series.

    D1 acceptance: for d=163 this must reproduce the Chudnovsky triple
    (640320, 13591409, 545140134). NotImplemented at skeleton stage.
    """
    raise NotImplementedError("PSLQ pipeline lands after the d=163 anchor "
                              "self-test is trusted (see module docstring)")


def main() -> int:
    print(f"mp.dps = {mp.dps}")
    ok = True
    for d in HEEGNER:
        k2 = singular_modulus_k2(d)
        j = j_from_k2(k2)
        print(f"  d={d:4d}  j = {mp.nstr(j, 30)}")
    # anchor: d=163 -> j ~= -640320^3 (real part dominates; imaginary tiny)
    j163 = j_from_k2(singular_modulus_k2(163))
    anchor = -(power(640320, 3))
    err = abs(j163 - anchor) / abs(anchor)
    print(f"  d=163 anchor: |j - (-640320^3)|/|anchor| = {mp.nstr(err, 3)}")
    ok = err < mpf(10) ** -40
    print("ANCHOR PASS" if ok else "ANCHOR FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
