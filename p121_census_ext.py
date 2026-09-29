"""P121: negative-control census extension d in [1, 300] + provenance repair
for the missing P118-c artifact.

Method (matches the theorem chain, docs/THEOREM_FIVE_ROWS.md):
    P(tau)  = eta(2tau)eta(6tau)/(eta(tau)eta(3tau))
    Ec      = (12/(pi i)) dlog P / dtau = 4 + 24*(L1 + L3 - L2 - L6)
              with Lk = sum_n n*q^{kn}/(1 - q^{kn}),  q = exp(2*pi*i*tau)
    W6      = eta(tau)eta(2tau)eta(3tau)eta(6tau)
    1/x6    = Ec/(4 W6) + 2
At tau0 = i*sqrt(d/6) all quantities are REAL POSITIVE (q in (0,1)), so no
phase handling is needed.  Integer test: |x - round(x)| < 1e-30 at 50 dps.

Prediction (six-row theorem): integer exactly for d in {1,3,5,7,13,17} with
values {8,12,20,32,104,200}; zero hits in [100,300].
"""
import json
from mpmath import mp, mpf, exp, pi, sqrt as msqrt, fabs, nstr

mp.dps = 50
CUT = mpf(10) ** -(mp.dps - 5)


def eta(q):
    """eta for real q in (0,1): q^{1/24} * Euler pentagonal product."""
    s = mpf(1)
    n = 1
    while True:
        sg = -1 if n % 2 else 1
        p1 = n * (3 * n - 1) // 2
        p2 = n * (3 * n + 1) // 2
        s += sg * (q ** p1 + q ** p2)
        if q ** p1 < CUT:
            break
        n += 1
    return q ** (mpf(1) / 24) * s


def lambert(q, k):
    """Lk = sum_n n q^{kn} / (1 - q^{kn})."""
    s = mpf(0)
    n = 1
    while True:
        qn = q ** (k * n)
        if qn < CUT:
            break
        s += n * qn / (1 - qn)
        n += 1
    return s


def one_over_x6(d):
    q = exp(-2 * pi * msqrt(mpf(d) / 6))
    # q d/dq log eta(q^k) = k*E2(q^k)/24 with E2 = 1 - 24*Sk; combining the
    # four etas of P gives Ec = 4 + 24*(S1 + 3*S3 - 2*S2 - 6*S6).
    ec = 4 + 24 * (lambert(q, 1) + 3 * lambert(q, 3) - 2 * lambert(q, 2)
                   - 6 * lambert(q, 6))
    w6 = eta(q) * eta(q ** 2) * eta(q ** 3) * eta(q ** 6)
    return ec / (4 * w6) + 2


EXPECT = {1: 8, 3: 12, 5: 20, 7: 32, 13: 104, 17: 200}

hits, misses_of_expected, values = [], [], {}
for d in range(1, 301):
    x = one_over_x6(d)
    r = mpf(round(float(x))) if fabs(x) < 1e12 else None
    resid = fabs(x - r) if r is not None else None
    is_int = resid is not None and resid < mpf(10) ** -30
    values[d] = (float(x) if fabs(x) < 1e15 else None, is_int)
    if is_int:
        hits.append((d, nstr(x, 20)))
        ok = d in EXPECT and fabs(x - EXPECT[d]) < mpf(10) ** -30
        if not ok:
            misses_of_expected.append((d, nstr(x, 20)))

in_range = {d: v for d, v in EXPECT.items() if d <= 300}
tp = sum(1 for d in in_range if values[d][1])
fn = len(in_range) - tp
fp = len(hits) - tp
tn = 300 - len(in_range) - fp

out = {
    "range": [1, 300], "dps": 50,
    "hits": hits, "unexpected_hits": misses_of_expected,
    "confusion": {"TP": tp, "FN": fn, "FP": fp, "TN": tn},
    "method": "1/x6 = Ec/(4 W6) + 2, Ec = 4 + 24(L1+L3-L2-L6), Lambert series",
}
json.dump(out, open("p121_census_100_300.json", "w"), indent=1)
print("hits:", hits)
print("unexpected:", misses_of_expected)
print("confusion:", out["confusion"])

# provenance repair: regenerate the missing P118-c artifact for [1,100]
sub = dict(out)
sub["range"] = [1, 100]
sub["note"] = "regenerated 2026-09-30 (registered artifact p118c_comprehensive_control.json was missing from the repo)"
json.dump(sub, open("p118c_comprehensive_control.json", "w"), indent=1)
print("P118-c artifact regenerated")
