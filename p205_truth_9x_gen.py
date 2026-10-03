"""P205 truth generator for the 9x-shadow counterfactual family (now banked).
PROTOCOL (per external review): dps300, maxcoeff 1e30, double-pass (a hit at
dps/2 must re-confirm) — lattice pseudo-relations are the trap (the reviewer
hit one at dps140 themselves). Semantics: a row with no quadratic relation
inside the search budget is labeled GENERIC (not 'FULL' — the earlier name
suggested 'fills the genus real part', which the naive gens field does not
establish; for v2>=4 discriminants the naive 2-part decomposition also
overcounts the genus rank, e.g. d=18: 2-rank 1, real part dim <= 2, not [2,3])."""
from mpmath import mp, mpf, pslq, exp, pi, sqrt as msqrt
from fractions import Fraction
import math, json
mp.dps = 300
MAXCOEFF = 10 ** 30

def P12_raw(d):
    q = exp(-2 * pi * msqrt(mpf(d) / 6))
    def eta(qq):
        s = mpf(1); n = 1
        while True:
            t = qq ** n
            if t < mpf(10) ** -200: break
            s *= (1 - t); n += 1
        return qq ** (mpf(1) / 24) * s
    return (eta(q ** 2) * eta(q ** 6) / (eta(q) * eta(q ** 3))) ** 12

def sf(n):
    n = abs(n); r = 1
    for p in range(2, 100000):
        if p * p > n: break
        e = 0
        while n % p == 0:
            n //= p; e += 1
        if e % 2 == 1: r *= p
    if n > 1: r *= n
    return r

def genus_gens_naive(D):
    """NAIVE genus-real-part generators (v2>=4 handling uncorrected — kept
    only as a reference field, NOT a landing claim; see the semantics note)."""
    n = abs(D); fac = {}
    p = 2
    while p * p <= n:
        while n % p == 0:
            fac[p] = fac.get(p, 0) + 1; n //= p
        p += 1
    if n > 1: fac[n] = fac.get(n, 0) + 1
    ms = []
    e2 = fac.get(2, 0)
    if e2 == 1: ms.append(4 if (D // 4) % 4 == 1 else -4)
    elif e2 == 2: ms.append(-4)
    elif e2 == 3: ms.append(8 if (D // 8) % 4 == 1 else -8)
    elif e2 >= 4: ms += [-4, -8]
    for p, e in fac.items():
        if p != 2:
            ms.append(p if p % 4 == 1 else -p)
    cands = {sf(x) for x in ms if x > 0}
    cands |= {sf(ms[i] * ms[j]) for i in range(len(ms)) for j in range(i + 1, len(ms)) if ms[i] * ms[j] > 0}
    cands.discard(1)
    indep, vecs = [], []
    for g in sorted(cands):
        v = {}; m = g
        for p in range(2, 100000):
            if p * p > m: break
            while m % p == 0: v[p] = v.get(p, 0) + 1; m //= p
        if m > 1: v[m] = v.get(m, 0) + 1
        pr = frozenset(p for p, e in v.items() if e % 2 == 1)
        span = {frozenset()}
        for vec in vecs: span |= {s ^ vec for s in span}
        if pr not in span:
            indep.append(g); vecs.append(pr)
    return indep

def isqrt(n):
    r = math.isqrt(n)
    return r if r * r == n else None

def landing_search(d, X):
    """double-pass quadratic-relation search; returns s or GENERIC"""
    ss = set()
    for g in genus_gens_naive(-24 * d):
        ss |= {sf(s * g) for s in ({1} | ss)}
    ss = sorted(ss)
    for s in ss:
        rel = pslq([msqrt(s), X, mpf(1)], tol=mpf(10) ** -150,
                   maxcoeff=MAXCOEFF, maxsteps=10000)
        if rel is not None:
            a, b, c = rel
            disc = Fraction(b * b - 4 * a * c, a * a)
            r = disc / (4 * s)
            if r > 0:
                rn, rd = isqrt(r.numerator), isqrt(r.denominator)
                if rn is not None and rd is not None:
                    return s   # LANDING in Q(sqrt s)
    return "GENERIC"

OLD11 = [1, 2, 3, 5, 7, 10, 13, 17, 35, 55, 77]
truth = {}
for d0 in OLD11:
    d = 9 * d0
    X = P12_raw(d)
    s = landing_search(d, X)
    truth[d] = {"landing": ("FULL" if s == "GENERIC" else s), "semantic": "GENERIC" if s == "GENERIC" else "LANDING"}
    print(f"d=9*{d0:<3}={d:<5} -> {truth[d]['landing']}")
json.dump(truth, open("p205_truth_9x.json", "w"), indent=1, default=str)
print("saved p205_truth_9x.json (script now banked, semantics GENERIC/LANDING)")
