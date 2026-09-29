# NIGHT RESEARCH SUMMARY: 2026-09-29 02:09 → 2026-09-30 04:00

## Overview

~26 hours of continuous autonomous research (with breaks for the user's
audits). 50+ registered experiments. 3 major theorems advanced.
4 substrates tested for Memory Geometry. 2 new theorems proposed.
3 small-sample signals killed by expansion. 1 major theory falsified
and replaced.

## Line 1: Five-Row Rationality Theorem (math)

### The theorem (current form)

1/x6(tau0) is an integer exactly for d in {1,3,5,7,13,17} (values
8,12,20,32,104,200), where tau0 = i*sqrt(d/6) and x6 is the level-6
quasimodular function W6/z6. The 2-elementary locus of Cl(-24d) is
{3,5,7,10,13,17,35,55,77}; the chi_2 = Kronecker(-3/.) character is
trivial exactly on {3,5,7,13,17}. The composite-d and d=10 rows are
2-elementary but chi_2-nontrivial, forcing irrationality.

### The proof architecture (every arrow labeled)

1. Ligozat criterion → P^12 in M(Gamma0(6), chi_2)  [quadratic
   nebentypus, verified 1e-58 at 120dps]
2. Shimura reciprocity → P^12 CM values in the genus field
   [chi_2 = Kronecker(-3/.) = a genus character, P98-c]
3. Cancellation identity → D log F = (1/2)[2E2*(2t) + 6E2*(6t) -
   E2*(t) - 3E2*(3t)]  [k-independent correction cancels; P83-A,
   elementary]
4. E2* CM values period-algebraic  [standard CM theory]
5. W6 CM values = Weber class invariants  [Schertz Thm 1]
6. R_d = P'/(2 pi i P W6) = (Ec/W6)/24 in Q  [numerically exact:
   5/3, 3, 5, 17, 33]
7. x6 = 4/(Ec/W6 + 8) in Q  [algebraic identity]

### Key discoveries

- x12/x6 is QUASIMODULAR, not modular (P76 falsified Hauptmodul)
- P^12 IS Gamma0(6)-modular with quadratic chi_2 (P89, 120dps)
- d=1 is a sixth rational row (P106, missed by original census range)
- chi_2 = Kronecker(-3/.) identified (P98-c)
- m_d = exp(Cl)/2 (P82-CLOSURE, Z/4 at d=17 forces m=2)
- Transport lemma at non-coprime classes = the one remaining gap

### What was falsified

- Hauptmodul claim: x12 NOT modular for Gamma0(12) (P76)
- Single-Pell-power at composite d (P92)
- "Exact quadratic" x6-over-j6D at 80dps (P75 correction)
- Linear degree effect on surprise (P97-b, p=0.82)

### The one remaining lemma

Schertz Thm 4 scope at non-coprime classes: the transport of chi_2's
action through classes with gcd(A, 6) > 1. This is a write-up gap,
not a computational one — the numerical verification is complete.

## Line 2: Memory Geometry (agent memory laws)

### The laws (six, each with cross-substrate replication)

| Law | Statement | Substrates | Source |
|---|---|---|---|
| L1: Coverage | recognition = coverage within THRESH; R/mind and NN/mind govern viability | synthetic, SQuAD, matrix, FlyMemory | P52/P65/P110 |
| L2: Two-scale | prototype/exemplar divergence requires two-scale classes | twoscale, Gaussian | P65-b/P110 |
| L3: Plateau | capacity saturates at reachable fraction; cold start is first-class | synthetic, FlyMemory | P55/P70 |
| L4: Novelty | coverage AND clearance; contrast (not resolution) opens the window | SQuAD, production | P53/P54/P95 |
| L5: Query floor | l_min ~ #free-statistic-entries; knee location is content-relative | 5 substrates | P59/P64/P70-b/P90/P111 |
| L6: Eviction | core-first requires density heterogeneity + metric-coverage match; random can outperform | synthetic, Gaussian | P72/P110/P112 |

### The controller (P73/P74)

Inputs: r, nn, ts, cov, clr, lq, ff, eps → Outputs: type, capacity,
eviction, verification depth, query gate, novelty screening, rehearsal.
Zero fitted parameters.  R8 substrate-feasibility gate added from the
flyloop G1 lesson.

### The fourth substrate lesson (P110/P112)

Law 5 replicates universally (4/4 substrates).  Law 6 has a PRECONDITION:
core-first eviction requires density heterogeneity AND redundancy-metric/
coverage-structure match.  On uniform-density substrates, random eviction
outperforms all deterministic policies (65% vs 30%).

## Line 3: Interestingness (two-axis theory)

### The theory (P98)

SURPRISE = genus-structure-depth detection (confirmed 88.9% within
fixed degree, p = 0.039).  UTILITY = proximity to published-rationality
locus (13:3 reversal).  The axes are DISSOCIABLE: same pairs, opposite
preferences under different framings.

### The three killed signals

1. Linear degree within fixed gdepth: refuted twice (P96-b 10:4 →
   P97-b expansion 11:9, p = 0.82)
2. Resolution refinement as novelty lever: refuted (P54)
3. argsort-correlation as rank statistic: caught by external audit
   (P88 correction)

## The five-substrate ladder

| substrate | Law 5 (query floor) | Law 6 (eviction) | distinctive finding |
|---|---|---|---|
| synthetic twoscale | ✓ knee 10-25% | ✓ core 100% >> fringe 54% | two-scale divergence |
| FlyMemory production | ✓ knee 6-12 tok | not tested | ℓ_min cross-validation |
| SQuAD retrieval | ✓ knee < 5% | ✓ core 42.5% > LRU 30% | sibling confusion 25-50% |
| numerical matrix | ✓ knee 10-25% | ✗ core = LRU (uniform density) | density precondition |
| mathematical text | NON-MONOTONE | not tested | template dilution effect |

## Method notes (the meta-research findings)

- Register-first discipline: caught 3 bugs and 1 statistical artifact
  before they contaminated conclusions
- Expansion-before-belief: killed 3 small-sample signals
- External audits: caught the argsort bug, the .real extraction bug,
  and the v=4 decompose bug — all by independent re-computation
- Negative results are results: 3 killed signals + 2 falsified
  conjectures + 1 retracted claim = the honest portion of the output

## Commit chain (sessions 2-3)

~30 commits from 02:09 to 04:15 (2026-09-30), all pushed and verified.
HEAD at time of writing: post-P111-b.

## Morning extension (04:15 → 07:30): the RAG design-language arc

A nine-experiment arc (P116-P127) that converted the coverage-law
program into a query-construction design language, measured on SQuAD
within-article retrieval at n=2823 (encoder:
paraphrase-multilingual-MiniLM-L12-v2):

| P | result |
|---|---|
| P116 | contrast gradient: verbatim 100 > keyword 75 > question 48.3 |
| P117/P120 | gold-head prefix ceiling 49.8 -> 98.8; saturates at ~200ch; prefix-first wins at every length |
| P121 | math census extended to d in [1,300]: 6 TP + 294 TN, zero counterexamples; missing P118-c artifact regenerated |
| P122 | synonym substitution does NO damage -> P117-b "0%" claim RETRACTED |
| P122-b | random-word dose-response 49.8 -> 7.9; the prefix hedges question-side damage (98.8 -> 97.9 at dose 0.8) |
| P122-c | topic-sentence effect: head 98.8 vs tail 66.0 (32pp) — but see P127 |
| P123 | title/metadata injection FAILS (-9.1pp): zero within-store contrast = pure dilution |
| P124 | reranker and prefix are ~95% substitutes: +24.6pp bare, +1.2pp hybrid |
| P125 | conversational anchor is BIMODAL: fresh ~98.9 / stale 5.9 (-44pp) |
| P125-b | guard v1 (bare-question arbiter) FAILS: 83.3 < 84.3 — weak arbiter truncates the strong channel |
| P125-c | guard v2 (dual rerank, elementwise max) WINS: 87.2, fresh 100.0, stale 19.1 residual |
| P126/126-b | staleness detectors rejected: AUC 0.639 (question style) / 0.737 (retrieval feedback); routing needs ~0.95 given the payoff asymmetry |
| P127 | second-encoder replication: hazards transfer (bimodal anchor, dilution, ceiling), magnitudes are encoder-specific (head-tail gap 32.8pp L12 vs 5.2pp L6) |

Two retractions (P117-b synonym claim; the "deployable hybrid" reading
of P117/P120 — the prefix was gold-context, i.e. a ceiling) and two
generalizable lessons (arbiter conditioning; cross-query score
calibration) are recorded in the registry and in
docs/RAG_DESIGN_CONSTRAINTS.md (C1-C7, DR1-DR10).

Provenance audit: 150 artifact citations scanned, 148 present, 2
annotated as never-archived live-service probes (P70/P70-b).
