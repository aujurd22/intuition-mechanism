"""P163: HALLUCINATION downgrade-tracking — test the judge's refuted rule.

P152's math-track judge stated: "RATIONAL iff Q(sqrt(-d)) has class
number 1."  The boundary refused it INSIGHT (5/6 probes).  But per the
user's direction 4, refuted rules should be DOWNGRADED and TRACKED, not
discarded.  Test: what IS the class number of Q(sqrt(-d)) for the six
rows and the probes?  Is the judge's rule a *corrupted* version of a
true pattern (e.g. small class number correlates with rationality)?

Class number of Q(sqrt(-d)) for d>0: h(-4d) via class-number formula
(computed by enumerating reduced primitive forms of discriminant -4d).
"""
import json
from math import gcd, isqrt


def h_imag(D):
    """Class number of the imaginary quadratic order of discriminant D<0
    by counting reduced primitive positive-definite forms."""
    forms = 0
    Amax = isqrt(-D // 3) + 1
    for A in range(1, Amax + 1):
        for B in range(-A + 1, A + 1):
            if B % 2 != D % 2:
                continue
            if (B * B - D) % (4 * A):
                continue
            C = (B * B - D) // (4 * A)
            if C < A:
                continue
            if C == A and B < 0:
                continue
            if gcd(gcd(A, B), C) != 1:
                continue
            forms += 1
    return forms


def class_number_Q_sqrt_neg_d(d):
    """h of Q(sqrt(-d)) — discriminant: fundamental D of K=Q(sqrt(-d)).
    For d squarefree: D = -4d if d ≡ 1,2 mod 4; D = -d if d ≡ 3 mod 4."""
    # squarefree part
    dd = d
    f = 1
    p = 2
    while p * p <= dd:
        while dd % (p * p) == 0:
            dd //= p * p
            f *= p
        p += 1
    if dd == 1:
        # d was a perfect square: K = Q, not a quadratic field
        return None
    # d = f^2 * dd, dd squarefree; K = Q(sqrt(-dd)), m = -dd
    # discriminant rule: D = m if m ≡ 1 (mod 4) else 4m
    m = -dd
    D = m if m % 4 == 1 else 4 * m
    return h_imag(D)


if __name__ == "__main__":
    LOCUS = [1, 3, 5, 7, 13, 17]
    NONLOCUS = [10, 25, 35, 55, 77, 91, 2, 11, 19, 23, 43]
    rows = []
    print(f"{'d':>4} {'K':>14} {'h(K)':>5} {'rational':>9}")
    for d in LOCUS + NONLOCUS:
        h = class_number_Q_sqrt_neg_d(d)
        rat = d in LOCUS
        kname = f"Q(sqrt({-d}))"
        rows.append({"d": d, "h": h, "rational": rat})
        print(f"{d:>4} {kname:>14} {str(h):>5} {str(rat):>9}")
    # correlation: is h small exactly on the locus?
    locus_h = [r["h"] for r in rows if r["rational"]]
    non_h = [r["h"] for r in rows if not r["rational"]]
    print("\nlocus h values:", locus_h)
    print("non-locus h values:", non_h)
    # judge's rule: RATIONAL iff h==1
    tp = sum(1 for r in rows if r["rational"] and r["h"] == 1)
    fp = sum(1 for r in rows if not r["rational"] and r["h"] == 1)
    fn = sum(1 for r in rows if r["rational"] and r["h"] != 1)
    print(f"\njudge rule 'h==1 => RATIONAL': TP={tp} FP={fp} FN={fn}")
    print("=> rule accuracy:", f"{100*(tp)/max(tp+fp+fn,1) if False else ''}")
    json.dump(rows, open("p163_classnumbers.json", "w"), indent=1)
    print("saved p163_classnumbers.json")
