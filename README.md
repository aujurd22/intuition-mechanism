# Intuition-Mechanism Program

**Insight Mechanism Reproduction Program** — a Mushroom-Body Program track.
Research plan: [docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md)

> Central question: can Ramanujan-style formula discovery be reduced to a
> mechanical pipeline? Which steps are the "inspiration", and can they be
> reproduced by a machine and their signature measured?

## Status

| Component | Status |
|---|---|
| `validator.py` | ✅ 50-digit verification gate; both anchors (Ramanujan / Chudnovsky) PASS |
| `family_gen.py` | ✅ Heegner CM points -> theta constants -> singular modulus -> j; d=163 anchor PASS (j = -640320^3, error 2.4e-101) |
| `series_gen.py` | ✅ **D1 GATE PASS**: starting from d alone, via z=1728/j and the 3F2 coefficient sums, the Chudnovsky coefficients (13591409, 545140134) are reproduced at 96.9 integer digits |
| T0 synthetic-family scan | next work unit (graph families + canonical forms, P1/P2) |
| T2 A/B engine (insight signature P5) | after D1 |

## Bugs caught by the anchor self-tests (the value of anchors)

1. The theta-function nome is `exp(pi*i*tau)`, NOT `exp(2*pi*i*tau)` — the
   squared nome pushed d=163's j off by 17 orders of magnitude;
2. Heegner j's imaginary part is float noise; the integer cube-root check
   must use the real part;
3. **Inverted identity**: from `1/pi = 12*T/640320^(3/2)` it follows that
   `T = 640320^(3/2)/(12*pi)`, not `pi*640320^(3/2)/12` — the numerical
   comparison (A*S0 ~= 1.359e7) exposed it on the spot.

## Law coupling

- Experiment conclusions write back to the Mushroom-Body Program repo
  ([aujurd22/flymemory](https://github.com/aujurd22/flymemory)),
  `research/RESEARCH.md` (L-series laws; L1 form law and L5 aggregation
  law were established there).
- The plan's P1-P7 prediction registry lives in docs/RESEARCH_PLAN.md
  (registered before running).
