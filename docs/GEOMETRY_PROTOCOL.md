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

## What this protocol does NOT cover

- Write-path policies (flyloop's V7 axes) -- needs the online loop.
- m_d / Pell-unit structure -- mathematics-line objects.
- Anything requiring ground-truth labels beyond the corpus itself.

## Usage

A new substrate is admitted by running M1-M4 and appending one row.
Law verdicts are read off, not re-argued: a row FAILS a law if the
predicted ordering is inverted, and the failure immediately localizes
which input (r/nn/ts/cov/clr/lq/ff/eps) the substrate violates.
