"""P195: CORRECTED 2-elementary locus — fixes the P172 enumerator bugs.
Bug 1: (A,-A,C) and (A,A,C) both counted when C > A (missing |B|=A -> B>=0).
Bug 2: prime-discriminant 2-part for v2 >= 4 produced non-prime 'discriminants'.
Fixed criterion: Cl(D) is 2-elementary <=> ALL reduced primitive forms are
ambiguous (b=0 or |b|=a or a=c) — no t/genus-number needed."""
import json
from math import gcd, isqrt

def reduced_forms(D):
    forms = []
    Amax = isqrt(-D // 3) + 1
    for A in range(1, Amax + 1):
        for B in range(-A + 1, A + 1):          # FIX 1: -A < B <= A
            if B % 2 != D % 2:
                continue
            if (B * B - D) % (4 * A):
                continue
            C = (B * B - D) // (4 * A)
            if C < A:
                continue
            if C == A and B < 0:                 # a=c boundary: B >= 0
                continue
            if gcd(gcd(A, abs(B)), C) != 1:
                continue
            forms.append((A, B, C))
    return forms

def is_ambiguous(f):
    a, b, c = f
    return b == 0 or abs(b) == a or a == c

def is_2elementary(D):
    forms = reduced_forms(D)
    amb = [f for f in forms if is_ambiguous(f)]
    return len(amb) == len(forms), len(forms), len(amb)

locus = {}
for d in range(1, 1001):
    D = -24 * d
    ok, h, amb = is_2elementary(D)
    if ok:
        locus[d] = {"D": D, "h": h}

L = sorted(locus)
print(f"corrected 2-elementary locus in [1,1000]: {L}")
print(f"count: {len(L)}")
old11 = {1, 2, 3, 5, 7, 10, 13, 17, 35, 55, 77}
quadrupled = sorted(4 * d for d in old11)
print(f"\nold 11-row set:      {sorted(old11)}")
print(f"4x that set:         {quadrupled}")
print(f"new rows beyond 11:  {[d for d in L if d not in old11]}")
print(f"reviewer claim 22 = 11 U 4x11: {set(L) == (old11 | set(quadrupled)) if all(d <= 500 for d in L) else 'check beyond 500'}")
beyond500 = [d for d in L if d > 500]
print(f"rows beyond 500 in [1,1000]: {beyond500}")
beyond308 = [d for d in L if d > 308]
print(f"rows in (308,1000]: {beyond308}  (reviewer claimed none)")
json.dump({"locus_[1,1000]": L, "details": {str(k): v for k, v in locus.items()}},
          open("p195_2elem_corrected.json", "w"), indent=1)
print("saved p195_2elem_corrected.json")
