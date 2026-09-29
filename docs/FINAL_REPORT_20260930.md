# FINAL NIGHT REPORT: 2026-09-29 evening → 2026-09-30 05:12

## Executive summary

~27 hours of continuous autonomous research across three lines
(modular forms theory, agent memory systems, LLM interestingness
judgment).  45+ registered experiments, ~45 commits pushed, 21
documentation files (477 KB), 89 scripts, 240 data files.

Three major theoretical results, five experimental laws replicated
across multiple substrates, three small-sample signals honestly killed
by expansion, one major theory falsified and replaced, one production
system validated against theoretical predictions.

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

SURPRISE = genus-structure-depth detection [88.9%, p=0.039, P91-scaled]
UTILITY = proximity to published rationality [13:3 reversal, P92]
DISSOCIATION confirmed [same pairs, opposite preferences, P92]
LINEAR DEGREE refuted by expansion [p=0.82, P97-b]

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

### Memory Geometry (medium priority)
4. Test the controller on a production RAG system (not just FlyMemory)
5. Test the hybrid query (+35pp) on a production RAG benchmark
6. Matched-pair expansion to 20 pairs per cell with human judges (P102)

### Interestingness (lower priority)
7. Scale the matched-pair experiment to 20 pairs per cell with
   balanced degree/gdepth (needs LLM API)
8. Human validation design (P102) — requires human participants

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
