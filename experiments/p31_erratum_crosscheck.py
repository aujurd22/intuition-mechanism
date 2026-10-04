"""Independent cross-verification of the N=17 erratum finding:
two INDEPENDENT algorithms for the t-family series identity.

  Algorithm A: t(n) by closed-form binomial sum
               t(n) = sum_{k<=n/2} C(n,2k) C(2k,k)^2 C(2n-4k,n-2k)
  Algorithm B: t(n) by the CWZ four-term recurrence
               (n+1)^3 t(n+1) = 2(2n+1)(2n^2+2n+1)t(n)
                              + 4n(4n^2+1)t(n-1)
                              - 64n(n-1)(2n-1)t(n-2)

  x0 = x12(q) from the verified level-12 machinery; identity:
  sum (n + lambda) t(n) x0^n = (1/(2 pi)) sqrt(24/17) / sqrt((1+4x0)(1-4x0)(1-8x0))

  Checked for lambda = 43/238 (predicted correct) and 143/238 (the
  arXiv v2 Table-1 print) at 100 dps.
"""
import mpmath as mm
from math import comb

mm.mp.dps = 100


def t_binom(n):
    v = 0
    for k in range(n // 2 + 1):
        v += comb(n, 2 * k) * comb(2 * k, k) ** 2 * comb(2 * n - 4 * k,
                                                         n - 2 * k)
    return v


def t_recur_printed(N):
    """t(n) via the printed recurrence, t(0)=1:
    (n+1)^3 t(n+1) = 2(2n+1)(2n^2+2n+1) t(n) + 4n(4n^2+1) t(n-1)
                     - 64 n(n-1)(2n-1) t(n-2)."""
    ts = {0: 1}
    for n in range(0, N):
        val = 2 * (2 * n + 1) * (2 * n * n + 2 * n + 1) * ts[n]
        if n >= 1:
            val += 4 * n * (4 * n * n + 1) * ts[n - 1]
        if n >= 2:
            val -= 64 * n * (n - 1) * (2 * n - 1) * ts[n - 2]
        ts[n + 1] = val // (n + 1) ** 3   # exact division per CWZ
    return [ts[i] for i in range(N)]


def main():
    N_terms = 900
    tsA = [mm.mpf(t_binom(n)) for n in range(N_terms)]
    tsB = [mm.mpf(v) for v in t_recur_printed(N_terms)]
    agree = all(tsA[i] == tsB[i] for i in range(N_terms))
    print(f"algorithm A (binomial sum) vs B (recurrence): identical = "
          f"{agree} over {N_terms} terms")

    # x0 at N=17 from the verified machinery
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from p19b_z12 import x12, rhs_identity
    q = mm.exp(-2 * mm.pi * mm.sqrt(mm.mpf(17) / 24))
    x0 = mm.mpf(x12(q).real)

    r = rhs_identity(17, x0)
    for lam_str, lam in (("43/238", mm.mpf(43) / 238),
                         ("143/238", mm.mpf(143) / 238)):
        lhsA = sum((n + lam) * tsA[n] * x0 ** n for n in range(N_terms))
        lhsB = sum((n + lam) * tsB[n] * x0 ** n for n in range(N_terms))
        print(f"lambda={lam_str:8s}: |lhsA - rhs| = "
              f"{mm.nstr(abs(lhsA - r), 8)},  |lhsB - rhs| = "
              f"{mm.nstr(abs(lhsB - r), 8)}")


if __name__ == "__main__":
    import os
    main()
