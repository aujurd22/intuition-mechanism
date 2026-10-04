"""P63: exact Dedekind-sum implementation of the eta multiplier nu(gamma).

The eta multiplier is the exact-arithmetic tool step 4 of the
genus-theory theorem needs (THEORY_LAMBDA.md).  For gamma = (a b; c d)
in SL_2(Z), c != 0:

    eta(gamma tau) = nu(gamma) * (c tau + d)^(1/2) * eta(tau)

    nu(gamma) = exp(pi i (a + d) / (12 c)) * exp(pi i * s(-d, c))

    s(h, k) = sum_{r=1}^{k} ((r/k)) ((h r / k)),   ((x)) = x - floor(x) - 1/2
              (0 when x is an integer)

Dedekind sums are computed in exact rational arithmetic (fractions),
the exponentials to 50 digits.

Registered validation gate: for 20 random gamma in SL_2(Z) (c > 0) and
3 random tau, | eta(gamma tau) / ((c tau + d)^(1/2) eta(tau)) - nu(gamma) |
<= 1e-30, and nu(gamma) is an exact 24th root of unity (|nu| = 1,
nu^24 = 1 within 1e-30).  Falsification: any gate failing.
"""
import json
import cmath
from fractions import Fraction

import mpmath as mm

mm.mp.dps = 50


def dedekind_sum(h, k):
    """Exact s(h,k) for integers h, k (k > 0), via the matched residues."""
    h = h % k
    total = Fraction(0)
    for r in range(1, k + 1):
        x = Fraction(r, k)
        p1 = x - Fraction(1) if r != k else Fraction(0)  # ((r/k)): 0 at integer k
        # ((r/k)) = r/k - 1/2 for 1 <= r <= k-1, and 0 for r == k
        p1 = (Fraction(r, k) - Fraction(1, 2)) if r < k else Fraction(0)
        hr = (h * r) % k
        p2 = (Fraction(hr, k) - Fraction(1, 2)) if hr != 0 else Fraction(0)
        total += p1 * p2
    return total


def eta_multiplier(a, b, c, d):
    """nu(gamma) for gamma = (a b; c d), c > 0, ad - bc = 1."""
    assert a * d - b * c == 1
    assert c > 0
    s = dedekind_sum(-d, c)
    phase = mm.pi * (mm.mpf(a + d) / (12 * c) + mm.mpf(s.numerator) / s.denominator)
    return mm.exp(mm.j * phase)


def eta_q(q):
    """Dedekind eta from q = e^(2 pi i tau): q^(1/24) * prod_{n>=1} (1 - q^n)."""
    q = mm.mpc(q)
    s = mm.mpc(1)
    n = 1
    while True:
        qn = q ** n
        if abs(qn) < mm.mpf(10) ** -45:
            break
        s *= 1 - qn
        n += 1
    return q ** (mm.mpf(1) / 24) * s


def check_gate(a, b, c, d, tau):
    nu = eta_multiplier(a, b, c, d)
    gtau = (a * tau + b) / (c * tau + d)
    lhs = eta_q(mm.exp(2 * mm.pi * mm.j * gtau))
    rhs = nu * (c * tau + d) ** (mm.mpf(1) / 2) * eta_q(mm.exp(2 * mm.pi * mm.j * tau))
    err = abs(lhs - rhs)
    # 24th root of unity check: nu^24 == 1
    root_err = abs(nu ** 24 - 1)
    return err, root_err


def random_sl2(rng, cmax=12):
    import numpy as np
    while True:
        a = int(rng.integers(-cmax, cmax + 1))
        b = int(rng.integers(-cmax, cmax + 1))
        c = int(rng.integers(1, cmax + 1))
        # choose d with ad = 1 (mod c)
        a_mod = a % c
        inv = None
        for cand in range(c):
            if (a_mod * cand) % c == 1 % c and c > 1 or (c == 1 and cand == 0):
                if (a_mod * cand) % c == 1 % c:
                    inv = cand
                    break
        if inv is None:
            continue
        d = inv + c * int(rng.integers(-cmax, cmax + 1))
        if a * d - b * c != 1:
            # adjust b to make det 1: b = (ad - 1)/c
            if (a * d - 1) % c != 0:
                continue
            b = (a * d - 1) // c
        return a, b, c, d


def main():
    import numpy as np
    rng = np.random.default_rng(6301)
    worst = mm.mpf(0)
    worst_root = mm.mpf(0)
    rows = []
    for _ in range(20):
        a, b, c, d = random_sl2(rng)
        for taure in (0.3, -0.2, 0.15):
            tau = mm.mpc(taure, 1.1)
            err, root_err = check_gate(a, b, c, d, tau)
            worst = max(worst, err)
            worst_root = max(worst_root, root_err)
            rows.append({"gamma": [a, b, c, d], "err": mm.nstr(err, 4),
                         "root_err": mm.nstr(root_err, 4)})
    ok = worst <= mm.mpf(10) ** -30 and worst_root <= mm.mpf(10) ** -30
    print(f"worst transformation error: {mm.nstr(worst, 4)}")
    print(f"worst nu^24 != 1 error:     {mm.nstr(worst_root, 4)}")
    print(f"GATE: {'PASS' if ok else 'FAIL'}")
    json.dump({"worst_err": mm.nstr(worst, 6),
               "worst_root_err": mm.nstr(worst_root, 6),
               "gate_pass": bool(ok), "checks": rows},
              open("p63_eta_multiplier.json", "w"), indent=1)
    print("saved p63_eta_multiplier.json")


if __name__ == "__main__":
    main()
