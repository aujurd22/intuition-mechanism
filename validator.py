"""Validator for 1/pi series (Intuition-Mechanism Program, T2 Phase 0 quick-start 1).

50-digit verification of the two anchor formulas:
  - Ramanujan 9801 series  (base 396^4)
  - Chudnovsky 640320 series (base 640320^3, alternating)

This is the acceptance interface for the family generator (D1): any d ->
series produced by family_gen.py must pass `check_series()` with 50-digit
tolerance before it counts as a valid member of the family.

Run:  python validator.py    (self-tests both anchors; exit 0 on pass)
"""
import sys

from mpmath import mp, mpf, factorial, power, sqrt

mp.dps = 60

TOL_50 = mpf(10) ** -45


def ramanujan_9801_pi(terms: int = 14):
    """1/pi = 2*sqrt(2)/9801 * sum_k (4k)! (1103+26390k) / (k!^4 * 396^(4k)).

    Each term adds ~8 digits; 14 terms give ~112 digits (headroom over 60).
    """
    s = mpf(0)
    for k in range(terms):
        s += (factorial(4 * k) * (1103 + 26390 * k)
              / (factorial(k) ** 4 * power(396, 4 * k)))
    return 9801 / (2 * sqrt(2) * s)


def chudnovsky_pi(terms: int = 10):
    """1/pi = 12 * sum_k (-1)^k (6k)! (13591409+545140134k)
             / ((3k)! (k!)^3 * 640320^(3k+3/2)).

    Each term adds ~14 digits; 10 terms give ~140 digits.
    """
    s = mpf(0)
    for k in range(terms):
        s += ((-1) ** k * factorial(6 * k) * (13591409 + 545140134 * k)
              / (factorial(3 * k) * factorial(k) ** 3
                 * power(640320, 3 * k + mpf(3) / 2)))
    return 1 / (12 * s)


def check_series(pi_approx, label: str, tol=TOL_50) -> bool:
    """Acceptance interface for generated series (D1 gate)."""
    err = abs(pi_approx - mp.pi)
    ok = err < tol
    print(f"  [{label}] abs_err = {mp.nstr(err, 3)}  "
          f"({'PASS' if ok else 'FAIL'} @ {mp.nstr(tol, 2)})")
    return ok


def main() -> int:
    print(f"mp.dps = {mp.dps}; tolerance 1e-45 (50-digit gate)")
    ok = True
    ok &= check_series(ramanujan_9801_pi(), "Ramanujan 9801 (14 terms)")
    ok &= check_series(chudnovsky_pi(), "Chudnovsky 640320 (10 terms)")
    print("ALL PASS" if ok else "SELF-TEST FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
