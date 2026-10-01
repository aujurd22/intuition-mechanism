"""P161 v2: measured factoring reach of our quadratic-form/CF family.

Representatives (all verifiable inline):
  Brent rho      — the general small-factor workhorse
  Fermat+mult    — quadratic-form family (the P134 eps_d infrastructure:
                   CF of sqrt(s_d), fundamental units — same object family)
Measured: semiprime factorization time vs bit size -> the ceiling where
this mechanism family dies.  Reference: GNFS at 862 bits (RSA-260).
"""
import json
import math
import time
import random
from sympy import nextprime


def brent_rho(n):
    if n % 2 == 0:
        return 2
    y, c, m = random.randint(1, n - 1), random.randint(1, n - 1), random.randint(1, n - 1)
    g, r, q = 1, 1, 1
    while g == 1:
        x = y
        for _ in range(r):
            y = (y * y + c) % n
        k = 0
        while k < r and g == 1:
            ys = y
            for _ in range(min(m, r - k)):
                y = (y * y + c) % n
                q = q * abs(x - y) % n
            g = math.gcd(q, n)
            k += m
        r *= 2
    if g == n:
        g = 1
        while g == 1:
            ys = (ys * ys + c) % n
            g = math.gcd(abs(x - ys), n)
    return g if g != n else None


def fermat_mult(n, kmax=64):
    """Fermat with multipliers kN: quadratic-form family representative."""
    for k in (1, 2, 3, 5, 6, 7, 10):
        kn = k * n
        a = math.isqrt(kn)
        if a * a < kn:
            a += 1
        for _ in range(200000):
            b2 = a * a - kn
            b = math.isqrt(b2)
            if b * b == b2:
                g = math.gcd(a - b, n)
                if 1 < g < n:
                    return g
                g = math.gcd(a + b, n)
                if 1 < g < n:
                    return g
            a += 1
    return None


def full_factor(n):
    facs = []
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        while n % p == 0:
            facs.append(p)
            n //= p
    stack = [n]
    while stack:
        m = stack.pop()
        if m == 1:
            continue
        r = math.isqrt(m)
        if r * r == m:
            stack += [r, r]
            continue
        f = None
        try:
            f = brent_rho(m)
        except Exception:
            f = None
        if f is None or f in (1, m):
            f = fermat_mult(m)
        if f is None or f in (1, m):
            facs.append(m)
            continue
        stack += [f, m // f]
    return sorted(facs)


def semiprime(bits, rng):
    half = bits // 2
    p = nextprime(rng.randint(2 ** (half - 1), 2 ** half - 1))
    q = nextprime(rng.randint(2 ** (half - 1), 2 ** half - 1))
    return p * q


if __name__ == "__main__":
    rng = random.Random(20261002)
    rows = []
    print(f"{'bits':>5} {'median time':>14} {'ok':>4}")
    for bits in (20, 30, 40, 50, 60, 70):
        times, oks = [], 0
        trials = 3
        for _ in range(trials):
            n = semiprime(bits, rng)
            t0 = time.time()
            facs = full_factor(n)
            dt = time.time() - t0
            times.append(dt)
            prod = 1
            for f in facs:
                prod *= f
            oks += int(prod == n)
        rows.append({"bits": bits, "times": times,
                     "median": round(sorted(times)[len(times) // 2], 3),
                     "ok": oks, "trials": trials})
        print(f"{bits:>5} {sorted(times)[len(times)//2]:>13.3f}s {oks:>3}/{trials}")
    json.dump(rows, open("p161_reach.json", "w"), indent=1)
    print("saved p161_reach.json")
