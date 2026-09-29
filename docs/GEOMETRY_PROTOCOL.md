# The Unified Geometry Protocol (cross-substrate measurement standard)

Status: registered 2026-09-30 00:05.  Purpose: one measurement protocol
so that any new substrate (a new corpus, a new memory service, a new
embedding model) enters the SAME law table as synthetic families,
FlyMemory production, and the SQuAD retrieval corpus -- "one more
substrate" then means "one more row in one table", not "another ad-hoc
experiment".

## The four measurements (fixed order, fixed definitions)

### M1 — coverage geometry (Laws 1-2)

Embed the substrate's items with its production encoder.  Compute:

  NN-cos band        (5th..95th percentile of nearest-neighbor cosine)
  median NN-cos      (the anisotropy anchor; P62: 0.731 production)
  isolate fraction   (NN < 0.30; P62 production: 0%)
  duplicate fraction (NN > 0.98; P62 production: 0%)
  fringe fraction    (NN > TH; TH = median NN)   [NOTE: definitionally
                      0.5 when TH = median -- prefer TH = mind/2-class
                      thresholds when classes exist; the median-TH value
                      is recorded only as a distribution anchor]

Interpretation: the band shape and the isolate/duplicate fractions
characterize the substrate; they are inputs to the Controller (P73).

### M2 — query floor (Law 5)

Sample 60 items.  For cue fractions {5, 10, 25, 50, 100}% of each
item's text, retrieve top-10 against the full store; record hit@10.
Report the curve, not just the knee: the knee LOCATION is
content-relative (SQuAD topical distinctiveness puts it below 5%,
P90; FlyMemory's dense conclusions put it at 10-25%, P70-b), while
the curve's MONOTONE-RISE-TO-CEILING shape is the law.

Cross-check: the knee token-count should approximate the encoder's
free-statistic entry count (P64).

### M3 — budget retention (Law 6)

Stream the full corpus through a store of budget B = 30% of N, in
arrival order.  Four eviction policies: core-first (most neighbors
within TH), LRU, random, fringe-first.  Probe: every original item
retrieves its best surviving neighbor; success = cosine >= TH and
cluster label preserved.  Report all four, ordered.

Prediction (Law 6): core-first > LRU ~ random >> fringe-first.
Replicated: P72 (twoscale 100/92/92/54), P90 (SQuAD 42.5/30/38/30).

### M4 — clearance / novelty (Law 4)

Hold out a topically-distinct subset.  Detection = simple threshold
at the acceptance radius.  Report detection AND false-alarm rates
separately (the P53 two failure modes: clearance failure = blind;
coverage failure = vacuous).  Optional: contrast-feature arm (P54)
if the raw-embedding detection fails.

## Reporting standard

One law-table row per substrate, with the fixed column set:
  substrate | N | encoder | NN-band | fringe% | degradation curve
  | eviction order + values | clearance rates | law verdicts.

## The law table (as of 2026-09-30 07:20)

| substrate | N / encoder | NN-band (p5/med/p95) | degradation (5/10/25/50/100% cue) | eviction core/LRU/rand/fringe | law verdicts |
|---|---|---|---|---|---|
| synthetic twoscale | families / native | n/a (constructed) | knee 10-25% (P64) | **100 / 92 / 92 / 54** (P72) | L1-L6 all pass; two-scale divergence demonstrated (P65-b) |
| FlyMemory production | 7325 / L12-v2 | 0.439 / 0.691 / 0.929; isolate 0%, dup 0% (P62) | knee 6-12 tokens (P70-b) | not tested (live service) | L1/L5 pass; dark tail 99.86% + self-reach 100% both hold (P70) |
| SQuAD paragraphs | 400 / L12-v2 | 0.549 / 0.731 / 0.824; isolate 0%, dup 0% (P90/P111-b) | 95.0/96.7/100/100/100 — knee < 5% (P90) | **42.5 / 30.0 / 38.2 / 30.0** (P90; random > LRU, cf. P112) | L1/L5/L6 pass; sibling confusion 25-50% = reranker space (P93-b); query-construction layer P116-P127 (DR1-DR10) |
| Gaussian matrix (R^32) | 500 / none | n/a (constructed) | knee 10-25% (P110) | core = LRU (uniform density — L6 precondition fails) | L5 pass; L6 partial — density-heterogeneity precondition isolated (P110/P112) |
| mathematical text | 21 / 50dps | median 0.997 (template anisotropy) | NON-MONOTONE 73.3/73.3/**53.3 dip**/... (P111) | not tested | L5 FAILS as stated — template dilution effect discovered; corpus-level, not item-level (P113) |

Reading guide: the law table's job is localization, not celebration.
A row fails a law exactly where its substrate violates the law's input
condition (math text violates L5 via template anisotropy; the Gaussian
matrix violates L6 via uniform density).  The query-construction layer
(DR1-DR10, P116-P127) is measured on the SQuAD row and is
encoder-relative (P127): hazards transfer across encoders, magnitudes
do not.

## What this protocol does NOT cover

- Write-path policies (flyloop's V7 axes) -- needs the online loop.
- m_d / Pell-unit structure -- mathematics-line objects.
- Anything requiring ground-truth labels beyond the corpus itself.

## Usage

A new substrate is admitted by running M1-M4 and appending one row.
Law verdicts are read off, not re-argued: a row FAILS a law if the
predicted ordering is inverted, and the failure immediately localizes
which input (r/nn/ts/cov/clr/lq/ff/eps) the substrate violates.
