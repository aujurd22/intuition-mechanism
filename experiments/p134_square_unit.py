"""P134: the square-unit structure of 64 P^12(tau0) — mechanical table.

For the six-row closed forms (P79), verified:
  (F1) norm_{Q(sqrt s)}(64 P^12) = 1 on every row (it is a UNIT);
  (F2) exponent of the smallest fundamental unit always EVEN
       (=> 8 P^6(tau0) is itself a unit of Q(sqrt s_d));
  (F3) half-exponent m_d = 2 iff the 2-primary prime discriminant of
       D = -24d is +8 (d = 1 mod 4 in this family), else 1.
"""
from math import isqrt
import json

CLOSED = {3: (49, 20, 6), 5: (721, 228, 10), 7: (6049, 1320, 21),
          13: (842401, 233640, 13), 17: (11995201, 2057160, 34)}
TWO_PD = {3: -8, 5: 8, 7: -8, 13: 8, 17: 8}


def fund_unit_smallest(s):
    """Smallest-norm convergent-generator of Q(sqrt s) (may have norm -1)."""
    a0 = isqrt(s)
    m, dd, a = 0, 1, a0
    per = []
    while True:
        m = dd * a - m
        dd = (s - m * m) // dd
        a = (a0 + m) // dd
        per.append(a)
        if a == 2 * a0:
            break
    p_prev, q_prev, p_cur, q_cur = 1, 0, a0, 1
    allc = [(p_cur, q_cur)]
    for aa in per:
        p_prev, p_cur = p_cur, aa * p_cur + p_prev
        q_prev, q_cur = q_cur, aa * q_cur + q_prev
        allc.append((p_cur, q_cur))
    for (x, y) in allc:
        if abs(x * x - s * y * y) == 1 and y > 0:
            return x, y
    return allc[-1]


rows = []
for d, (a, b, s) in CLOSED.items():
    norm = a * a - b * b * s
    x, y = fund_unit_smallest(s)
    k_found = None
    tx, ty = 1, 0
    for k in range(0, 30):
        if tx == a and ty == b:   # eps^k = a + b sqrt(s) => 64P12 = eps^(-k)
            k_found = k
            break
        tx, ty = tx * x + s * y * ty, x * ty + y * tx
    e = -k_found
    half = e // 2
    assert e % 2 == 0 and norm == 1
    rows.append({"d": d, "s": s, "norm": int(norm),
                 "eps_fund": f"{x}+{y}sqrt({s})", "exponent": e,
                 "half_exponent": half, "two_pd": TWO_PD[d],
                 "rule_m2_iff_2pd_plus8": (abs(half) == 2) == (TWO_PD[d] == 8)})

out = {"rows": rows,
       "findings": {
           "F1_unit": all(r["norm"] == 1 for r in rows),
           "F2_square": all(r["exponent"] % 2 == 0 for r in rows),
           "F3_two_pd_rule": all(r["rule_m2_iff_2pd_plus8"] for r in rows)}}
json.dump(out, open("p134_square_unit.json", "w"), indent=1)
for r in rows:
    print(r)
print("\nF1 unit:", out["findings"]["F1_unit"],
      " F2 square:", out["findings"]["F2_square"],
      " F3 2-pd rule:", out["findings"]["F3_two_pd_rule"])
