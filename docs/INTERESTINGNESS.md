# Mechanical Interestingness: the two-axis theory (P33-n20 → P97-b)

Status: 2026-09-30 03:30.  Synthesis of the interestingness line after
three rounds of expansion-killed signals.  This document is the
current truth; superseded claims live in the registry history.

## The question

Can "interesting / structurally surprising" be produced mechanically
from measurable structure — and if so, which structure?

## The two confirmed axes

### Axis 1 — surprise tracks GENUS-STRUCTURE DEPTH (P91-scaled)

Within a fixed lambda-degree, the blind judge prefers the identity
with higher genus-field depth: 8/9 consistent votes (88.9%, binomial
p = 0.039, swap-controlled, abstain-on-disagree).  The votes
concentrate at the structural transitions, not uniformly.

### Axis 2 — utility tracks PUBLISHED RATIONALITY (P92)

Asked which identity is "more useful as a seed for further
discovery", the judge REVERSES its surprise preference: rational
(degree-1, published) rows are preferred 13:3 over deep rows.  The
judge holds two distinct concepts and applies them oppositely
depending on the question — novelty and utility are separable
judgments, not one.

## The refuted candidates

- LINEAR DEGREE EFFECT within fixed genus depth: refuted twice
  (P96-b 10:4 at the 2v3 gap; expansion 11:9, p = 0.82).
- RESOLUTION REFINEMENT as a novelty lever: refuted (P54 — contrast,
  not resolution, opens the detection window).
- PELL-POWER FORM at composite d: refuted (P92 — the simple unit form
  is a prime-row phenomenon).

## The consolidated statement

  SURPRISE  = detection of genus-structure depth transitions.
      Mechanical proxy: genus-field depth (t - 1) at fixed algebraic
      degree.  Confirmed at 88.9% (p = 0.039); signal concentrates at
      structural transitions.

  UTILITY   = proximity to the published-rationality locus.
      Mechanical proxy: algebraic degree 1 (the rational, published,
      family-seeding rows); the judge's utility framing reverses to
      prefer them 13:3.

  The two axes are DISSOCIABLE: the same pair of identities gets
  opposite preference labels under the two framings.

## Honest boundaries

- Effect sizes are moderate: the confirmed surprise signal is 8/9
  votes in the cleanest cell; per-pair noise is large; the 21-row
  sample carries only 3 degree levels and 3 genus depths.
- Three small-sample signals were killed by expansion (P88's 0.622,
  P96-b's 10:4, P91's original confound).  Every number in this
  document has survived at least one expansion attempt.
- "Interestingness" here is a blind judge's pairwise preference --
  whether it models HUMAN interestingness is the next question, not
  this one.

## The judge landscape (P119 / P128 / P128-c, 2026-09-30)

Structural judgment is a MODEL x FORMAT interaction — calibrate both
axes before any experiment (tool: format_calibration.py, 40 calls):

| model | forced-choice | absolute rho_gdepth | verdict |
|---|---|---|---|
| deepseek-v4.1-flash | 88.9% (p=.039) | 0.254 ns | FORCED |
| deepseek-v4-flash | 63.2% ns | 0.609 (14/14 pairs) | ABSOLUTE |
| doubao-seed-2.1-lite | 78.9% (p=.019) | 0.079 ns | FORCED |
| kimi-k2.8-preview | 57.9% ns | 0.08 | NO-SIGNAL |
| minimax-m3 | 63.2% ns | -0.188 | NO-SIGNAL |

The deepseek siblings SPLIT on format; doubao replicates the gdepth
axis on an independent family via forced choice; kimi/minimax are
floor in both.  The earlier single-model "forced > absolute" rule
(P119) is a model-instance property, not a format law.

## The connection to the five-row theorem

The surprise axis (genus depth) is exactly the axis along which the
character-obstruction theorem (CHARACTER_OBSTRUCTION.md) lives: the
five rows are the chi_2-trivial locus; the composite rows carry the
full genus field.  The mechanical-interestingness proxy and the
arithmetic obstruction are the same object seen from the judge side
and the class-field side respectively.
