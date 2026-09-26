"""verify_17 v2: uniform modern-notation verification of Ramanujan's 17
series via the 3F2 hypergeometric kernel G(w) = 3F2(1/2, p2, p3; 1, 1; w)
and its derivative (mp.diff). Handles the z=-1 conditionally-convergent
alternating group analytically (no fragile direct summation).

Each entry: {eq, target (the series must equal this), form} where form is
one of:
  poly   : target == c0 + A*G(w) + B*w*G'(w)          (w inside radius)
  alt    : target == c0 + sign*(A*w*G'(w) + B*(G(w)-1))  (w = -1 boundary)
  scale  : target == c0 + A*G(w) + B*w*G'(w) with algebraic w

Run:  python verify_17_v2.py    (exit 0 iff all 17 PASS at 1e-40)
"""
import sys

from mpmath import mp, mpf, pi, sqrt, hyper, diff

mp.dps = 60
TOL = mpf(10) ** -40

P28 = [mpf(1) / 2, mpf(1) / 2, mpf(1) / 2]
P3 = [mpf(1) / 2, mpf(1) / 3, mpf(2) / 3]
P6 = [mpf(1) / 2, mpf(1) / 6, mpf(5) / 6]
P4 = [mpf(1) / 2, mpf(1) / 4, mpf(3) / 4]


def G(w, p):
    return hyper(p[:2], [1, 1], w) if False else hyper(
        [p[0], p[1], p[2]], [mpf(1), mpf(1)], w)


def Gd(w, p):
    return diff(lambda u: G(u, p), w)


def main() -> int:
    checks = []

    # --- s=2 family (eq 28, 29): G with (1/2,1/2,1/2) ---
    checks.append((28, 4 / pi, lambda: G(mpf(1) / 4, P28)
                   + (6 / 4) * Gd(mpf(1) / 4, P28)))
    checks.append((29, 16 / pi, lambda: 5 * G(mpf(1) / 64, P28)
                   + 42 * (mpf(1) / 64) * Gd(mpf(1) / 64, P28)))
    z30 = ((sqrt(5) - 1) / 2) ** 8
    checks.append((30, 32 / pi, lambda: (5 * sqrt(5) - 1) * G(z30, P28)
                   + (42 * sqrt(5) + 30) * z30 * Gd(z30, P28)))

    # --- s=3 family (eq 31, 32): G with (1/2,1/3,2/3) ---
    checks.append((31, 27 / 4, lambda: 2 * G(mpf(2) / 27, P3)
                   + 15 * (mpf(2) / 27) * Gd(mpf(2) / 27, P3)))
    checks.append((32, 15 * sqrt(3) / 2, lambda: 4 * G(mpf(4) / 125, P3)
                   + 33 * (mpf(4) / 125) * Gd(mpf(4) / 125, P3)))

    # --- s=6 family (eq 33, 34): G with (1/2,1/6,5/6) ---
    checks.append((33, 5 * sqrt(5) / (2 * sqrt(3)), lambda: G(mpf(4) / 125, P6)
                   + 11 * (mpf(4) / 125) * Gd(mpf(4) / 125, P6)))
    z34 = (mpf(4) / 85) ** 3
    checks.append((34, 85 * sqrt(85) / (18 * sqrt(3)), lambda: 8 * G(z34, P6)
                   + 133 * z34 * Gd(z34, P6)))

    # --- s=4 alternating family (eq 35-39): w = -1/12, -1/72, -1/1764 ...
    # sum = c0 + (A*w*G'(w) + B*(G(w)-1)) with w negative
    checks.append((35, 4 / pi, lambda: mpf(3) / 2
                   + 3 * (-1) * Gd(mpf(-1) / 8, P4)
                   + 20 * (mpf(-1) / 8) * Gd(mpf(-1) / 8, P4)
                   + 20 * (G(mpf(-1) / 8, P4) - 1)))
    checks.append((36, 4 / sqrt(3), lambda: mpf(3) / 4
                   + 3 * (mpf(-1) / 16) * Gd(mpf(-1) / 48, P4)
                   + 28 * (mpf(-1) / 48) * Gd(mpf(-1) / 48, P4)
                   + 28 * (G(mpf(-1) / 48, P4) - 1)))
    checks.append((37, 4 / pi, lambda: mpf(23) / 18
                   + 23 * (mpf(-1) / 72) * Gd(mpf(-1) / 72, P4)
                   + 260 * (mpf(-1) / 72) * Gd(mpf(-1) / 72, P4)
                   + 260 * (G(mpf(-1) / 72, P4) - 1)))
    checks.append((38, 4 / sqrt(5), lambda: mpf(41) / 72
                   + 41 * (mpf(-1) / 360) * Gd(mpf(-1) / 360, P4)
                   + 644 * (mpf(-1) / 360) * Gd(mpf(-1) / 360, P4)
                   + 644 * (G(mpf(-1) / 360, P4) - 1)))
    checks.append((39, 4 / pi, lambda: mpf(1123) / 882
                   + 1123 * (mpf(-1) / 1764) * Gd(mpf(-1) / 1764, P4)
                   + 21460 * (mpf(-1) / 1764) * Gd(mpf(-1) / 1764, P4)
                   + 21460 * (G(mpf(-1) / 1764, P4) - 1)))

    # --- s=4 positive family (eq 40-44): sum = c0 + A*w*G'(w) + B*(G(w)-1)
    # with w = 4/9^m-style and A absorbing the 1/9^m prefactor
    checks.append((40, 2 * sqrt(3), lambda: mpf(1)
                   + (1 / 9) * (8 * (mpf(4) / 9) * Gd(mpf(4) / 9, P4)
                                + 9 * (G(mpf(4) / 9, P4) - 1))))
    checks.append((41, 1 / (2 * sqrt(2)), lambda: mpf(1) / 9
                   + (1 / 81) * (10 * (mpf(4) / 81) * Gd(mpf(4) / 81, P4)
                                 + 11 * (G(mpf(4) / 81, P4) - 1))))
    checks.append((42, 1 / (3 * sqrt(3)), lambda: mpf(3) / 49
                   + (1 / 49) * (40 * (mpf(4) / 49) * Gd(mpf(4) / 49, P4)
                                 + 43 * (G(mpf(4) / 49, P4) - 1))))
    checks.append((43, 2 / sqrt(11), lambda: mpf(19) / 99
                   + (1 / 99) * (280 * (mpf(4) / 99) * Gd(mpf(4) / 99, P4)
                                 + 299 * (G(mpf(4) / 99, P4) - 1))))
    checks.append((44, 1 / (2 * sqrt(2)), lambda: mpf(1103) / 99 ** 2
                   + (1 / 99 ** 2) * (26390 * (mpf(4) / 99 ** 4)
                                      * Gd(mpf(4) / 99 ** 4, P4)
                                      + 27493 * (G(mpf(4) / 99 ** 4, P4) - 1))))

    npass = 0
    for eq, target, fn in checks:
        try:
            val = fn()
            err = abs(val - target)
            ok = err < TOL
        except Exception as e:
            val, err, ok = None, None, False
            print(f"  eq({eq}): EXC {str(e)[:60]}")
            continue
        npass += ok
        print(f"  eq({eq}): val={mp.nstr(val, 12)}  target={mp.nstr(target, 12)}"
              f"  err={mp.nstr(err, 3)}  {'PASS' if ok else 'FAIL'}")
    print(f"\n{npass}/{len(checks)} verified at 1e-40")
    return 0 if npass == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
