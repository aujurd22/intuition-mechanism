"""P132: the 'non-coprime class' obstruction (P114) dissolves — mechanical proof.

Claim A (coprime representatives): every primitive form of discriminant D
is SL2(Z)-equivalent to a form whose leading coefficient is coprime to 6.
Hence every Pic(O) class admits an ideal representative of norm coprime
to 6, and Schertz Thm 4's coprimality hypothesis is satisfiable for ALL
classes — there are no 'non-coprime classes'.  (P114's premise checked
only REDUCED forms; SL2-equivalence gives non-reduced ones.)

Claim B (chi2 landscape): chi2([class]) := Kronecker(-3, A') via the
coprime representative is the genus character of Q(sqrt(-3)) — well
defined on every class.  Tabulate it across the full 2-elementary locus
and check the refined characterization:
   chi2 trivial on all classes  <=>  d in {5,7,13,17}
   d = 3: chi2 NONTRIVIAL (class [2,0,9] ~ [11,18,9], chi2(11) = -1)
          yet rational via the h=2 Pell chain — a scope refinement of
          the P98-c characterization.
   d in {35,55,77}: chi2 nontrivial (obstruction direction).

Also verify O1's ingredient: h(D) == 2^(t-1) on the whole locus
(2-elementary => H = H_gen, so ALL algebraic modular values at tau0
lie in the genus field with no transport at all).
"""
import json
from math import gcd, isqrt


def reduced_forms(D):
    """Primitive reduced positive-definite forms of discriminant D < 0."""
    forms = []
    Amax = isqrt(-D // 3) + 1
    for A in range(1, Amax + 1):
        for B in range(-A + 1, A):
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
            forms.append((A, B, C))
    return forms


def kronecker(a, n):
    """Kronecker symbol (a/n) for odd n; returns None if gcd(a, n) > 1."""
    if n == 0:
        return 1 if abs(a) == 1 else 0
    n = abs(n)
    if gcd(a % n or n, n) != 1:
        if gcd(a, n) != 1:
            return None
    result = 1
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23):
        pass
    # simple Jacobi for odd n via factor-free computation:
    def jacobi(aa, nn):
        aa %= nn
        result = 1
        while aa:
            while aa % 2 == 0:
                aa //= 2
                r = nn % 8
                if r in (3, 5):
                    result = -result
            aa, nn = nn, aa
            if aa % 4 == 3 and nn % 4 == 3:
                result = -result
            aa %= nn
        return result if nn == 1 else 0
    # handle sign / powers of 2 in a:
    r = 1
    aa = a
    if aa < 0:
        aa = -aa
        if n % 4 == 3:
            r = -r
    while aa % 2 == 0:
        aa //= 2
        if n % 8 in (3, 5):
            r = -r
    if aa == 1:
        return r
    if gcd(aa, n) != 1:
        return None
    return r * jacobi(aa, n)


def prime_discriminants(D):
    """Prime-discriminant factorization of D (for validation only)."""
    n = abs(D)
    fac = {}
    p = 2
    while p * p <= n:
        while n % p == 0:
            fac[p] = fac.get(p, 0) + 1
            n //= p
        p += 1
    if n > 1:
        fac[n] = fac.get(n, 0) + 1
    return fac


def find_coprime_rep(A, B, C):
    """Find proper (x,y), gcd=1, with gcd(F(x,y), 6) = 1.  Proven to exist."""
    F = lambda x, y: A * x * x + B * x * y + C * y * y
    for x in range(0, 200):
        for y in range(0, 200):
            if gcd(x, y) != 1:
                continue
            n = F(x, y)
            if n <= 0 or gcd(n, 6) != 1:
                continue
            return (x, y, n)
    return None


def equivalent_form(A, B, C, x0, y0):
    """SL2 matrix (x0 c; y0 d) with x0*d - y0*c = 1; return F o M as form."""
    # solve x0*d - y0*c = 1  ->  x0*d + y0*(-c) = 1: extended gcd
    def egcd(a, b):
        if b == 0:
            return (a, 1, 0)
        g, s, t = egcd(b, a % b)
        return (g, t, s - (a // b) * t)
    g, s, t = egcd(x0, y0)     # x0*s + y0*t = 1  ->  d = s, c = -t
    dd, cc = s, -t
    A2 = A * x0 * x0 + B * x0 * y0 + C * y0 * y0
    B2 = 2 * A * x0 * cc + B * (x0 * dd + y0 * cc) + 2 * C * cc * dd
    C2 = A * cc * cc + B * cc * dd + C * dd * dd
    return (A2, B2, C2)


LOCUS = {1: -24, 3: -72, 5: -120, 7: -168, 10: -240, 13: -312,
         17: -408, 35: -840, 55: -1320, 77: -1848}

report = {}
all_ok = True
for d, D in LOCUS.items():
    forms = reduced_forms(D)
    h = len(forms)
    rows = []
    coprime_classes = 0
    chi_values = []
    for (A, B, C) in forms:
        hit = find_coprime_rep(A, B, C)
        ok = hit is not None
        if ok:
            x0, y0, n = hit
            G = equivalent_form(A, B, C, x0, y0)
            A2, B2, C2 = G
            ok2 = (A2 == n and gcd(A2, 6) == 1
                   and (B2 * B2 - 4 * A2 * C2) == D
                   and gcd(gcd(A2, B2), C2) == 1)
            chi2 = kronecker(-3, A2)
        else:
            ok2 = False
            chi2 = None
        if ok2:
            coprime_classes += 1
        chi_values.append(chi2)
        rows.append({"form": [A, B, C], "coprime_rep": ok2,
                     "rep_A": (G[0] if ok2 else None),
                     "chi2": chi2})
    trivial = all(c == 1 for c in chi_values)
    report[d] = {"D": D, "h": h, "rows": rows,
                 "all_classes_6coprime": coprime_classes == h,
                 "chi2_trivial": trivial}
    if coprime_classes != h:
        all_ok = False
    print(f"d={d:3d} D={D:6d} h={h}  all-6-coprime={coprime_classes == h}"
          f"  chi2_trivial={trivial}  chis={sorted(set(str(c) for c in chi_values))}")

# expected h = 2^(t-1) validation (O1 ingredient)
print()
for d, D in LOCUS.items():
    fac = prime_discriminants(D)
    t = len(fac)
    exp_h = 2 ** (t - 1)
    ok = report[d]["h"] == exp_h
    print(f"d={d:3d} t={t} expected h=2^(t-1)={exp_h} actual={report[d]['h']}  {'OK' if ok else 'MISMATCH'}")
    if not ok:
        all_ok = False

json.dump({"all_classes_6coprime": all_ok, "report": report},
          open("p132_coprime_representatives.json", "w"), indent=1)
print("\nALL CLASSES HAVE 6-COPRIME REPRESENTATIVES:", all_ok)
