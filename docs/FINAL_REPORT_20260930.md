# FINAL NIGHT REPORT: 2026-09-29 evening → 2026-09-30 07:06

## Executive summary

~28 hours of continuous autonomous research across three lines
(modular forms theory, agent memory systems, LLM interestingness
judgment), closing with a nine-experiment RAG design-language arc
(P116-P127).  50+ registered experiments, ~55 commits pushed, 21
documentation files, 95+ scripts, 250 data files.

Three major theoretical results, five experimental laws replicated
across multiple substrates, three small-sample signals honestly killed
by expansion, one major theory falsified and replaced, one production
system validated against theoretical predictions, and a complete
query-construction design language (DR1-DR10) with two retracted
claims and one open detector problem.

## Line 0 (NEW): The RAG design language (P116-P127)

Measured on SQuAD within-article retrieval, n=2823 questions, flymemory's
paraphrase-multilingual-MiniLM-L12-v2 encoder:

| # | Finding | Numbers |
|---|---|---|
| P116 | contrast gradient | verbatim 100 > keyword 75 > question 48.3 |
| P117/P120 | gold-head prefix ceiling | 49.8 → 98.8; 200ch saturates; prefix-first wins at every L |
| P122-c | topic-sentence effect | head 98.8 vs tail 66.0 (32pp — dominates length choice) |
| P122-b | dose-response + hedge | bare question 49.8→7.9 @ dose 0.8; prefix hedges question damage (98.8→97.9) |
| P123 | metadata injection FAILS | title −9.1pp (zero within-store contrast) |
| P124 | reranker ≈ prefix substitutes | +24.6pp bare vs +1.2pp hybrid |
| P125 | conversational anchor BIMODAL | fresh ~98.9 / stale 5.9 (−44pp) |
| P125-b/c | guard recipes | weak arbiter fails (83.3); dual-rerank max wins (87.2, fresh 100.0) |
| P126/126-b | staleness detectors | question-style AUC 0.639, retrieval-feedback 0.737 — both insufficient (routing needs ~0.95 given payoff asymmetry) |
| P121 | census [1,300] | 6 TP + 294 TN, zero counterexamples (math line) |

Two retractions: P117-b "synonyms → 0%" (false at both mild and hard
perturbation); the "deployable hybrid rule" reading of P117/P120 (the
prefix was gold-context — a ceiling).

Two generalizable lessons: (i) an ARBITER must be conditioned at least
as strongly as the better candidate source (weak arbiter truncates the
strong channel); (ii) cross-encoder scores are not calibrated across
queries — max over differently-conditioned scorers crowns confidence,
not correctness (P125-c stale residual 19.1).

## Line 1: Six-Row Rationality Theorem

## Line 1: Six-Row Rationality Theorem

### The theorem

1/x6(i√(d/6)) is a positive integer exactly for d ∈ {1,3,5,7,13,17}
with values {8,12,20,32,104,200}.  The 2-elementary locus of
Cl(−24d) is {1,3,5,7,10,13,17,35,55,77}; the χ₂ = Kronecker(−3/·)
genus character is trivial exactly on the {3,5,7,13,17} subset.
Rationality requires BOTH conditions.

### The proof architecture (all arrows labeled)

P¹² ∈ M(Γ₀(6), χ₂) where χ₂ = Kronecker(−3/·) [Ligozat + 120dps]
  ↓ Shimura reciprocity
P¹² CM values in the GENUS FIELD (not ring class field)
  [quadratic nebentypus = genus character]
  ↓ P83-A cancellation
Ec/W₆ = (E₂*-combination)/(Weber product) at τ₀
  ↓ Weber class invariant evaluation [Schertz Thm 1]
Ec/W₆ = 40,72,120,408,792 for the six rows [numerically exact]
  ↓ Pell-unit structure [P81/P82]
1/x₆ = ε_fund^(−exp/2) → integer  [exp = class group exponent]

### What was falsified

- Hauptmodul claim: x₁₂ is quasimodular, NOT modular (P76)
- Idoneal ⟺ rational: d=17 rational but not idoneal (P101-v2)
- Single-Pell-power at composite d (P92)
- "Exact quadratic" x₆-over-j6D at 80dps (P75 correction)

### The one remaining gap

Schertz Thm 4 scope at non-coprime classes: the generator class
(2,0,9) for d=3 has ALL forms with even A — no coprime representative
exists (P114).  The proof for these classes requires the direct CM
derivative theorem or the Gross-Zagier/Kronecker limit formula.

## Line 2: Memory Geometry (six laws, five substrates)

| Law | Statement | Substrates |
|---|---|---|
| L1: Coverage | R/mind = 0.500 exact boundary | simplex D=6/8/12, SQuAD, Gaussian |
| L2: Two-scale | divergence needs two-scale classes | P65-b |
| L3: Plateau | capacity saturates at reachable fraction | P55 |
| L4: Novelty | coverage AND clearance; contrast opens window | P53/P54/P95 |
| L5: Query floor | ℓ_min ~ free-statistic-entries; template dilution effect | P59/P64/P70-b/P90/P111 |
| L6: Eviction | core-first requires density heterogeneity + correlation | P72/P110/P112/P112-b |

Controller: P73 spec → P74 phase boundary → v4 → R8 feasibility gate.
Applied to FlyMemory production data (P115): controller reproduces the
existing design choices, validating the framework.

## Line 3: Interestingness (two-axis theory)

SURPRISE = genus-structure-depth detection [88.9%, p=0.039, P91-scaled;
REPLICATED at 78.9%, p=0.019 on doubao-seed-2.1-lite, P128-c — now an
independent-family result]
UTILITY = proximity to published rationality [13:3 reversal, P92]
DISSOCIATION confirmed [same pairs, opposite preferences, P92]
LINEAR DEGREE refuted by expansion [p=0.82, P97-b]
JUDGE LANDSCAPE (P128 series): structural judgment is a model x format
interaction — deepseek-v4.1 carries via forced choice, its sibling
v4-flash via ABSOLUTE (reversal), doubao via forced, kimi/minimax are
floor in both.  Format calibration is now a mandatory pre-step
(format_calibration.py, P128-b).  P119's "forced > absolute" retracted
to a model-instance property.
CLOSING REPLICATION (P129): doubao forced-choice is bit-stable across
presentation seeds (15/19 = 78.9% twice); Axis 2 (utility) replicates
cross-family at 15/16; Axis 1 (surprise) scope refined — 78.9% on
deg-matched pairs but exactly chance on gross pairs (the depth cue and
the astonishing-simplicity cue cancel): Axis 1 experiments must
degree-match.

SEED-SOLIDIFYING ROUND (P130 series, 08:20-08:45): every judge-landscape
cell re-run at presentation seed 777. Carriers replicate: v4.1 forced
78.9% p=.019 (single-order scope), v4-flash absolute rho 0.447 + 7/8
pairs, doubao forced bit-identical. Nulls replicate: v4.1 absolute
0.230. Floors pooled to 38 votes: kimi 60.5%, minimax 52.6%. The
staleness-detector open problem is now bounded: the (s2, s3) cosine
feature family is formally insufficient (5-fold CV 84.1% vs always-
anchor 84.3%), and the oracle router ceiling is 92.7% — future work
needs reranker-disagreement or set-overlap features (registered).

## The cross-cutting findings

| Finding | Source | Significance |
|---|---|---|
| R/mind = 0.500 boundary | P65/P114-b | universal across D=4/6/8 |
| ℓ_min ~ #free-entries | P64/P96 | query design rule |
| Random >> deterministic eviction | P112 | Law 6 scope limitation |
| χ₂ = Kronecker(−3/·) | P98-c | character-theoretic mechanism |
| 3 expansion-killed signals | P88/P96-b/P97-b | methodological discipline |
| 1 census range bug found | P106 | d=1 sixth row discovered |

## What remains open (for the next session)

### Math (highest priority)
1. Schertz Thm 4 scope: prove the transport lemma for non-coprime
   classes, OR cite a published theorem that covers this case
2. m_d mechanism: connect exp/2 to the unit index Q of CM theory
3. Composite-d exact field: identify the degree-4..8 field of
   P^12(35/55/77) in the genus field

### RAG line (freshly opened, P116-P127)
4. A calibrated staleness detector: both cheap signals rejected
   (AUC 0.639 / 0.737 vs the ~0.95 the payoff asymmetry demands);
   per-row data saved (p126b_rows.json) for detector development
5. Encoder generality: P127 replication on all-MiniLM-L6-v2
   (running at report time)
6. Third substrate: replicate the DR rules on a non-Wikipedia corpus
   (the rules are currently SQuAD + L12-v2 specific)

### Memory Geometry (medium priority)
7. Test the controller on a production RAG system (not just FlyMemory)
8. Matched-pair expansion to 20 pairs per cell with human judges (P102)

### Interestingness (lower priority)
9. Scale the matched-pair experiment to 20 pairs per cell with
   balanced degree/gdepth (needs LLM API)
10. Human validation design (P102) — requires human participants

## The program-level insight

The three lines converge on a single principle: **limited-capacity
systems preserve structure through contrast, not through volume.**

In the math line: the rationality locus is the χ₂-trivial locus (a
character-theoretic constraint, not a size constraint).
In the memory line: retrieval quality depends on coverage geometry
(a density constraint, not a size constraint).
In the interestingness line: surprise tracks structural depth (a
relational signal, not an absolute magnitude).

These are three instances of the same principle: **what matters is
not how much you have, but how the things you have are structured
relative to what you need to distinguish.**
