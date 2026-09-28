"""P57 (step 4 of the genus-theory theorem): orbit triviality of x12.

Shimura reciprocity: x12(tau0) lies in the ring class field of the
order O = <1, 12*tau0> of disc D = -24N (tau0 = i*sqrt(N/24), so
12*tau0 = sqrt(-24N)/2).  The class group acts through reduced forms
(A,B,C) of disc D, each sending the CM point to tau_ab/12 with
tau_ab = (-B + i*sqrt(24N))/(2A).

REGISTERED PREDICTIONS (before the run):
  R1 (the five degenerate rows N = 3,5,7,13,17): the orbit values of
     x12 across ALL classes of disc -24N are EQUAL (max |Delta| <=
     1e-35) -- the eta-multiplier character is trivial on every
     2-torsion class, which is the mechanical core of step 4.
  R2 (control N=2, disc -48, h=2, also 2-torsion, but lambda is
     QUADRATIC there): the non-principal class value DIFFERS from the
     principal value -- the multiplier is nontrivial exactly where
     lambda escapes Q.
Falsification: any five-row class value differing, or N=2 orbit
collapsing (which would break the step-4 explanation of the
rational/quadratic boundary).
"""
import json
import os
import sys
from math import gcd, isqrt

import mpmath as mm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p19b_z12 import x12  # noqa: E402

mm.mp.dps = 50


def reduced_forms(D):
    """Reduced positive-definite forms (A,B,C), B^2-4AC = D < 0."""
    assert D < 0 and D % 4 == 0
    forms = []
    for A in range(1, isqrt(-D // 3) + 1):
        for B in range(-A, A + 1):
            if (B * B - D) % (4 * A):
                continue
            C = (B * B - D) // (4 * A)
            if C < A:
                continue
            if gcd(gcd(A, abs(B)), C) != 1:
                continue
            if abs(B) in (A, C) and B < 0:
                continue
            forms.append((A, B, C))
    return forms


def x12_at_tau(tau):
    q = mm.exp(2 * mm.pi * mm.j * tau)
    return x12(q)


def main():
    out = {}
    print("registered: five rows orbit-collapsed; N=2 control NOT collapsed")
    print(f"{'N':>3} {'D':>6} {'h':>2}  {'max |value - principal|':>26s}  verdict")
    for N in (2, 3, 5, 7, 13, 17):
        D = -24 * N
        forms = reduced_forms(D)
        tau0 = mm.mpc(0, mm.sqrt(mm.mpf(N) / 24))
        v0 = x12_at_tau(tau0)
        deltas = []
        vals = []
        for (A, B, C) in forms:
            tau_ab = (mm.mpc(-B, mm.sqrt(mm.mpf(24 * N)))) / (2 * A)
            v = x12_at_tau(tau_ab / 12)
            deltas.append(abs(v - v0))
            vals.append(mm.nstr(v, 30))
        maxd = max(deltas)
        collapsed = maxd <= mm.mpf(10) ** -35
        verdict = "COLLAPSED" if collapsed else "DIFFERS"
        out[N] = {"D": D, "h": len(forms),
                  "forms": [list(f) for f in forms],
                  "max_delta": mm.nstr(maxd, 8),
                  "collapsed": bool(collapsed),
                  "values": vals}
        print(f"{N:3d} {D:6d} {len(forms):2d}  {mm.nstr(maxd, 8):>26s}  {verdict}")
    five_ok = all(out[N]["collapsed"] for N in (3, 5, 7, 13, 17))
    ctrl_diff = not out[2]["collapsed"]
    print(f"\nR1 (five rows collapsed): {'CONFIRMED' if five_ok else 'FAILED'}")
    print(f"R2 (N=2 control differs): {'CONFIRMED' if ctrl_diff else 'FAILED'}")
    out["R1_five_rows_collapsed"] = bool(five_ok)
    out["R2_control_differs"] = bool(ctrl_diff)
    json.dump(out, open("p57_orbit_triviality.json", "w"), indent=1)
    print("saved p57_orbit_triviality.json")


if __name__ == "__main__":
    main()
