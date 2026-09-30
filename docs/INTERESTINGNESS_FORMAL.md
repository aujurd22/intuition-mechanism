# The Two-Axis Theory of LLM Interestingness Judgment — Formal Statement

Status: 2026-09-30, closing formalization (user directive: 收口).
This document states the interestingness program as definitions,
propositions, and predictions, with each claim labeled by its proof
type.  It supersedes the narrative form in INTERESTINGNESS.md, which
remains the empirical appendix.  Companion document:
docs/CHARACTER_OBSTRUCTION.md (the shared genus-theory substrate).

## 0. What kind of theory this is

The object of study is the LLM judge as a MEASUREMENT INSTRUMENT for
mathematical structure.  The propositions below are device-validity
claims: whether the instrument's readings track structural variables
of the stimulus set.  They are not claims about mathematics itself,
nor (yet) about human judgment.

## 1. Definitions

DEF 1 (stimulus set).  The identity corpus X: Ramanujan-type 1/pi
series parameters indexed by d, each stimulus presented as the pair
(x0(d), lambda(d)) in fixed 6-decimal format, with the census
variables known: 1/x6(i*sqrt(d/6)), lambda-degree deg(d), and the
arithmetic of D = -24d.

DEF 2 (structural variables).  For d in the census:
  deg(d)      the lambda-degree (1, 2, or 3);
  gdepth(d)   t - 1, t = number of distinct prime discriminants
              factoring D = -24d (the genus-group rank; P88);
  pub(d)      in {rat, irr}: whether 1/x6 is a published-rational
              integer (the six-row locus {1,3,5,7,13,17}).

DEF 3 (judge).  A judge J = (M, frame) is a model M with a framing
prompt frame in {surprise, utility}, forced-choice on an unordered
stimulus pair {a, b}, temperature 0, side-randomized (seeded).  The
reading J(pair) is the chosen index.

DEF 4 (frame orderings).  Each frame f induces a tentative ordering
<_{f} on X:  a <_{surprise} b iff b has higher gdepth;  a <_{utility}
b iff pub(a) = rat and pub(b) = irr.  The theory's content is the
extent to which the judge's readings realize these orderings.

DEF 5 (carrier).  M is a CARRIER for frame f on a pair family P if
the pooled agreement of J with <_{f} over P satisfies the
pre-registered device threshold: rate >= 60% at binomial p < 0.05.
Non-carriers split into WEAK (60% <= rate, ns) and FLOOR (rate
statistically indistinguishable from chance at the available power).

## 2. Propositions

PROP I1 (the degree-matched surprise law).
On deg-matched pairs (pairs with equal deg), a surprise-frame carrier
agrees with <_{surprise} at carrier rates.  Empirical content: pooled
per model over seeds — deepseek-v4.1-flash 23/28 = 82.1% (p = .0009),
doubao-seed-2.1-lite 30/38 = 78.9% (p = .0005); weak: v4-flash 25/38 =
65.8% (p = .073).  PROOF TYPE: empirical, multi-seed (P91-scaled,
P128-c, P130, P129, P131).
SCOPE CLAUSE (I1-a, the locality condition): the law holds ONLY on
deg-matched pairs; on gross (degree-unmatched) pairs the same
model-frame reads at chance (doubao 8/16, P129) because the depth cue
and the astonishing-simplicity cue cancel.  The surprise ordering is
therefore a WITHIN-DEGREE discriminator and does not extend to the
unmatched pair poset.

PROP I2 (the utility law).
On pairs mixing pub-classes, a utility-frame carrier agrees with
<_{utility} at carrier rates, and the agreement is CROSS-FAMILY and
PAIRING-ROBUST: deepseek-v4.1 13/3, doubao 15/16 — including on gross
pairs where I1 degenerates.  PROOF TYPE: empirical, two independent
families (P92, P129).

PROP I3 (dissociation).
The frame orderings <_{surprise} and <_{utility} are linearly
independent on X: there exist pairs where the two framings produce
OPPOSITE majorities from the same judge (the rational-vs-deep pairs:
surprise splits while utility chooses rational at 13/3 and 15/16).
Hence the two axes are not one axis relabeled.  PROOF TYPE: empirical,
double-dissociation design (P92, P129).

PROP I4 (the carrier landscape theorem).
Carrier status for a given frame is a MODEL-INSTANCE property, not a
model-family property, and is not stable across output formats:
  - the deepseek siblings split (v4.1 carries surprise-via-forced;
    v4-flash carries surprise-via-ABSOLUTE and is only weak forced);
  - doubao carries forced (independent family);
  - kimi and minimax are floor in both formats (57 votes each).
Full matrix with pooled statistics: p131_landscape_consolidated.json;
PROOF TYPE: empirical, every cell at least two-run (P128-c, P130
series), floors triple-seeded (P131/P131-b).

COROLLARY (mandatory calibration).  No interestingness reading may be
attributed to structure before the judge is calibrated by the 40-call
dual-format protocol (format_calibration.py, P128-b); a calibration
does not transfer across models or output formats.

## 3. The shared substrate with the mathematics line

gdepth is defined from the prime-discriminant factorization of
D = -24d — the same genus theory that supplies the field and orbit
structure of the six-row theorem (docs/CHARACTER_OBSTRUCTION.md, Prop
O1/O2-corrected).  The program's two halves therefore stand on one
arithmetic object: the mathematics line measures what the genus group
does to CM values; the judgment line measures what the genus group
does to LLM attention.  The observed correspondence (judges rank by
gdepth at fixed degree at 79-82% on carriers) is the program's
central unexplained coincidence — registered as the open question
below.

## 4. Pre-registered predictions

P-A (no family clustering): as new models are calibrated, carrier
status will not cluster by model family (so far: 1-of-2 in the
deepseek family, 1-of-1 doubao, 0-of-2 in the others — consistent,
unfalsified).
P-B (utility robustness asymmetry): the utility axis will replicate
across carriers more reliably than the surprise axis (so far 2/2 vs
format-split — consistent, unfalsified).
P-C (human anchor): if human raters are run (P102 design), their
surprise ordering will agree with gdepth at carrier-like rates on
deg-matched pairs — the program's bridge claim, untested.

## 5. Honest boundaries

- Every rate is a device-level reading of specific checkpoints at
  temperature 0; nothing here licenses "LLMs find mathematics
  interesting" in a phenomenological sense.
- Floor cells have power only against strong effects (38-57 votes);
  a weak kimi/minimax signal below 60% is not excluded.
- The stimulus format (6-decimal pairs) is one slice of presentation
  space; P116-P127 showed presentation effects of comparable size to
  the effects measured here.
- The theory contains no mechanism: I1/I2 state WHAT the instrument
  tracks, and the mechanism (why genus depth is visible to a language
  model at all) is the open question.
