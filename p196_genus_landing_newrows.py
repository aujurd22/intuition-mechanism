"""P196: genus-field landing test on the NEW 2-elementary rows (P195 prediction).
For each new row d (4x-shadow), P12_raw(tau0) should lie in the genus REAL part.
Genus real part constructed from prime-discriminant structure (multiset)."""
from mpmath import mp, mpf, pslq, exp, pi, sqrt as msqrt
mp.dps = 120

def P12_raw(d):
    q = exp(-2 * pi * msqrt(mpf(d) / 6))
    def eta(qq):
        s = mpf(1); n = 1
        while True:
            t = qq ** n
            if t < mpf(10) ** -90: break
            s *= (1 - t); n += 1
        return qq ** (mpf(1) / 24) * s
    return (eta(q ** 2) * eta(q ** 6) / (eta(q) * eta(q ** 3))) ** 12

def prime_disc_multiset(D):
    """multiset of prime discriminants of D (correct 2-part handling)"""
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
    ms = []
    e2 = fac.get(2, 0)
    # 2-part: e2=1 -> 4 or -4 (D/4 mod 4); e2=2 -> -4; e2=3 -> +-8; e2>=4 -> (-4)*(-8)*4^k or (-4)^k
    if e2 >= 1:
        if e2 == 1:
            ms.append(4 if (D // 4) % 4 == 1 else -4)
        elif e2 == 2:
            ms.append(-4)
        elif e2 == 3:
            v = D // 8
            ms.append(8 if v % 4 == 1 else -8)
        else:
            ms.append(-4); ms.append(-8)      # covers e2 in {4,5}
            for _ in range(e2 - 5):
                ms.append(-4)
    # ORDER genus field: every prime dividing |D| contributes its p*,
    # regardless of exponent parity (conductor primes count too — this
    # is exactly what the d=12 case exposed).
    for p, e in fac.items():
        if p != 2:
            ms.append(p if p % 4 == 1 else -p)
    return ms

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

def genus_real_gens(D):
    ms = prime_disc_multiset(D)
    gens = set()
    for x in ms:
        if x > 0:
            gens.add(sf(x))
    for i in range(len(ms)):
        for j in range(i + 1, len(ms)):
            pr = ms[i] * ms[j]
            if pr > 0:
                gens.add(sf(pr))
    gens.discard(1)
    # greedy independence over squareclass (mod 2 exponent vectors)
    indep = []
    vecs = []
    for g in sorted(gens):
        # factor g
        v = {}
        n = g
        for p in range(2, 100000):
            if p * p > n: break
            while n % p == 0:
                v[p] = v.get(p, 0) + 1; n //= p
        if n > 1: v[n] = v.get(n, 0) + 1
        pr = frozenset(p for p, e in v.items() if e % 2 == 1)
        # g independent iff its parity vector not in span of existing
        span = {frozenset()}
        for vec in vecs:
            span |= {s ^ frozenset(vec) for s in span}
        if frozenset(pr) not in span:
            indep.append(g)
            vecs.append(frozenset(pr))
    return indep

def test(d):
    D = -24 * d
    X = P12_raw(d)
    gens = genus_real_gens(D)
    k = len(gens)
    n = 2 ** k
    import itertools
    basis = [mpf(1)]
    for r in range(1, k + 1):
        for combo in itertools.combinations(gens, r):
            pr = 1
            for g in combo: pr *= g
            basis.append(msqrt(pr))
    vec = basis + [X]
    rel = pslq(vec, tol=mpf(10) ** -60, maxcoeff=10 ** 25, maxsteps=10000)
    if rel is None:
        return False, f"basis dim {n}, no relation"
    residual = sum(rel[i] * vec[i] for i in range(len(vec)))
    m = max(abs(x) for x in rel)
    if abs(residual) > mpf(10) ** -40 * m:
        return False, "bogus relation"
    return True, f"IN genus real part (dim {n}), maxcoeff {mp.nstr(m, 2)}"

print("=== P196: genus landing on NEW 2-elementary rows ===")
for d in [4, 8, 12, 20, 28, 40, 52, 68, 140, 220, 308]:
    ok, info = test(d)
    print(f"d={d:<4} {'LANDING CONFIRMED' if ok else 'NO/FAIL':<20} {info}")
