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
| `verify_17_v3.py` | ✅ **17/17 series VERIFIED** (Ramanujan 1914 eq 28-44, most at 1e-60+; source-double-checked) |
| `d1_generalize.py` | ✅ **D1 generalized (v2)**: 4/27 d produce integer series mechanically (d=19/43/67/163 — exactly the four Heegner d with j a negative perfect cube), all passing the independent 50-digit 1/pi gate; the pipeline reproduces the Ramanujan-Sato h=1 classification on its own |
| `p4_clean.py` | ✅ **P4 solved (given the invariant)**: Tier B ratio-normalized kNN 17/17; Tier C template matching 17/17; signature constant extraction 7/7 exact. Blind retrieval stays at chance — the open question moved from recognition to DISCOVERY of the normalization |
| `p6_generalize.py` | ✅ **P6 first verdict CONFIRMED**: the 3 mechanical members (d=19/43/67) rank 1/19 for signature s=6 in BOTH blind and invariant tiers (3/3 hit@1 vs chance 6.67) |
| `posz_scan_v2.py` + `posz_control.py` | ✅ **positive-z boundary measured**: PSLQ machinery validated (rediscovers eq28/eq29 at pi_err 1e-90; z-sensitivity ~1e-6), but the 8 remaining j>0 d miss all algebraic z forms — positive-z series need the modular-equation level-n machinery to construct z. Located "inspiration residue" for the positive family |
| T2 A/B engine (P5) | first-hit 7.75x CONFIRMED; post-recombination rate flagged as constructive (P5 v2 with a non-constructive recombination operator is next) |
| T7 notation forging (P7) | matched-budget PARITY (multi-seed); advantage requires redundant capacity; eta transfer fails |

## Current map (what is mechanized, what is not)

The program has measured the boundary of the mechanical pipeline:

- **Fully mechanized**: verification (50-digit gate), the h=1 negative-cube
  family (d -> integer series, no literature lookup), signature recognition
  given the invariant normalization (17/17 both tiers), and 17->18
  generalization for that sub-family (P6).
- **Located inspiration residues** (each now a concrete, testable step):
  1. **z-construction for the positive family** — z is not a rational
     multiple of k2(1-k2); it requires modular-equation level-n algebra
     (eq30's z = 64*((3-sqrt5)/16)^4 is a level-4 algebraic solution);
  2. **h=2 graded trace forms** — the class-number-2 discriminants
     (15, 35, 51, ...) need graded traces, a genuinely mathematical open
     problem;
  3. **Invariant discovery itself** — P4 showed recognition is trivial
     GIVEN the normalization; whether a prediction objective can induce
     the normalization is the open P9 experiment.

## Next (see docs/RESEARCH_PLAN.md registry for full detail)

1. P9: next-coefficient prediction -> does the latent state cluster by
   signature? (21 verified members as training data)
2. P5 v2: non-constructive cross-hit recombination operator
3. Positive-z level-n construction (eq30 as the level-4 template)
4. P7 capacity scaling (codes 12->64) + P1 tag-length gradient

## Bugs caught by the anchor self-tests (the value of anchors)

1. The theta-function nome is `exp(pi*i*tau)`, NOT `exp(2*pi*i*tau)` — the
   squared nome pushed d=163's j off by 17 orders of magnitude;
2. Heegner j's imaginary part is float noise; the integer cube-root check
   must use the real part;
3. **Inverted identity**: from `1/pi = 12*T/640320^(3/2)` it follows that
   `T = 640320^(3/2)/(12*pi)`, not `pi*640320^(3/2)/12` — the numerical
   comparison (A*S0 ~= 1.359e7) exposed it on the spot;
4. **PSLQ z-sensitivity** (`posz_control.py`): integer-relation recovery
   fails at |z - z_true| ~ 1e-6 — grid scanning for z is structurally
   hopeless; z must be constructed, not scanned;
5. **Review-caught pipeline artifacts** (2026-09-26): the P4 Tier C
   "degenerate constant" (template misalignment + normalization mismatch)
   and the D1 "0/27" (hardcoded base + division-based A recovery +
   fixed sum terms) were both analysis bugs caught by independent
   re-verification — both retracted and corrected in-registry.

## Law coupling

- Experiment conclusions write back to the Mushroom-Body Program repo
  ([aujurd22/flymemory](https://github.com/aujurd22/flymemory)),
  `research/RESEARCH.md` (L-series laws; L1 form law and L5 aggregation
  law were established there).
- The plan's P1-P9 prediction registry lives in docs/RESEARCH_PLAN.md
  (registered before running).
