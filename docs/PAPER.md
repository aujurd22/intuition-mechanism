# What Can a Machine Discover? A Registered Testbed for Invariant Discovery in Mathematics

**Status**: skeleton v1 (2026-09-27). Every claim below carries a registry
row (docs/RESEARCH_PLAN.md), a script, and a JSON artifact in the repo.

## Abstract (draft)

When a family of mathematical objects is generated as
c_k = (A + Bk)·H_s(k)·z^k with s a structural invariant and (A, B, z)
nuisances, which steps of the human discovery path can a machine
reproduce?  We map this question with a pre-registered, falsifiable
testbed built on Ramanujan–Sato series for 1/π.  Three levels emerge:
**L1 recognition** of a known invariant (mechanized: 17/17), **L2
nuisance removal** given the operator family or the labels (mechanized:
0.975 / 0.750, with a supervision caveat), and **L3 blind discovery of
the representation itself** (not mechanized: every fixed-transform
menu, prediction objective, and internal selection criterion fails).
The L3 failure is not uniform: a generic three-parameter envelope fit
recovers the invariant's neighborhood structure at 0.946 (chance
0.247) — "estimate the envelope, cancel it, read the residual" is
mechanizable — but exact envelope identification, scheme selection, and
global clustering each fail for distinct, characterized reasons.  We
locate the remaining gap with three theorems-shaped statements: the
complementarity of envelope schemes, the regime theorem, and the
salience-trap closure of internal criteria.

## 1. The testbed

- 17 verified Ramanujan–Sato series (mechanical 50-digit gates);
  signatures s ∈ {2,3,4,6}; verified 17/17 (verify_17_v3).
- Counterfactual generator: independent random (A,B,z) per sample,
  s as the only class signal (p14_factorization.make_dataset lineage;
  TRUE cumulative-H variant fixed in P15).
- Readouts: same-signature kNN (hit@1/frac3), k-means ARI
  (row-normalized), 1-D residual-level ladder diagnostic.

## 2. The three-level ladder (all verdicts registry-confirmed)

| Level | Result | Evidence |
|---|---|---|
| L1 Recognise | MECHANIZED | P4 Tier B ratio-norm 17/17; c_s extraction 7/7; P1-tag salience-robust |
| L2 Remove nuisances (given form or labels) | MECHANIZED (caveats) | P14 arm c 0.975 (form given); arm b 0.750 (s-labels — supervised, not blind); P2 registered-caliber HOLDS 8/8 |
| L3 Discover the representation (blind) | OPEN, precisely shaped | P13 90-cell grid: chance; P15: crack 0.946; P15-b/c/d/e/f: the boundary mapped (below) |

## 3. The P15 arc: five registered experiments mapping one gap

1. **P15 (PARTIAL, substance-confirmed)**: blind 3-parameter log-domain
   envelope fit lifts hit@1 0.404 → 0.946.  The missing human step is
   mechanizable.
2. **P15-b (FALSIFIED)**: same-span refit is mathematically vacuous
   (idempotent); obstruction located — z-modulated per-sample fit bias
   on the invariant's own axis.
3. **P15-c (split)**: ratio-domain reconstruction is perfect on one
   family (1.000/1.000) and harmful on the other (ARI 0.087):
   envelope schemes are COMPLEMENTARY, neither dominates.
4. **P15-d (PARTIAL)**: silhouette-based blind scheme selection picks
   correctly when the signal is strong, falls into the salience trap
   (margin 0.0009) when weak.
5. **P15-e (FALSIFIED) + P15-f (NEGATIVE, regime theorem)**: the bias is
   not a low-dimensional confound (random control ≈ oracle ≈ blind);
   PC1-removal fixes one family and destroys the other — the invariant
   may be dominant or subordinate, and internal geometry cannot tell
   which.

**Theorem-shaped statements produced** (empirical, registry-backed):
- *Complementarity*: for every pair of generic envelope schemes there
  exist families on which each dominates.
- *Regime theorem*: salience correction is valid in the
  invariant-subordinate regime and destructive in the
  invariant-dominant regime; the regime is not encoded in the
  representation's internal geometry.
- *Three-closure*: naive criteria (salience capture), confound
  regression (idiosyncratic bias), and corrected criteria (regime
  ambiguity) exhaust the internal-criterion family — external
  information or structural priors are required.

## 4. The Γ-proposition (P16, proven numerically at 17 digits)

After exact envelope removal the residual is u_k = C_s·H'_s(k) with

  C_s = 1 / ( Γ(1/2)·Γ(1/s)·Γ(1−1/s) ),

i.e. **the invariant axis a blind pipeline discovers IS a Gamma-product
constant** — the machine rediscovers a classical Γ-identity as its
readout axis.  Consequence: pairwise confusability is ordered by the
Γ-gaps; empirically ρ = −0.956 with the most-confused pair (2,3) =
smallest Γ-gap.  Registered caveat: the pre-registered arithmetic band
(1e-25) was an instrument-range error; recorded as a meta-lesson on
band-setting.

**Proposition (Γ-constant).** Let H_s(k) = (1/2)_k(1/s)_k(1−1/s)_k/(k!)³.
Then lim_{k→∞} H_s(k)·k^{3/2} = 1/(Γ(1/2)Γ(1/s)Γ(1−1/s)).
*Proof sketch:* (a)_k/k! = Γ(k+a)/(Γ(a)Γ(k+1)) ~ k^{a−1}/Γ(a) by Stirling;
multiply the three factors; the exponents sum to −3/2 and the constants
to the reciprocal Γ-triple.  The product converges as O(1/k); numerics:
extrapolated constant matches the formula to 1.7–3.4e-17 for all four s
(p16_gamma.py, after the registered revision).
*Corollary (a-priori confusability):* adjacent-s confusion is predicted
by the Γ-gap |log C_a − log C_b|; the ordering {2,3} < {3,4} < {2,4} =
{4,6} < {3,6} < {2,6} matches the empirical confusion counts.

## 4b. Mechanical series generation (P18/P19 — the generation theorem)

**Theorem (Cooper–Wan–Zudilin, level 12; numerically verified).** Let
z = ¼(6P(q¹²) − 3P(q⁶) + 2P(q⁴) − P(q²)) + 2η(2τ)η(4τ)η(6τ)η(12τ),
x = η(2τ)η(4τ)η(6τ)η(12τ)/z, and t(n) = Σ_{k≤n/2} C(n,2k)C(2k,k)²·
C(2n−4k,n−2k) (radius 1/8).  Then z = Σ t(n)xⁿ, q dx/dq =
z·x·√((1+4x)(1−4x)(1−8x)), and for every CM point x₀ = x(τ₀),

  Σ_{n≥0} (n + λ) t(n) x₀ⁿ = (1/(2π))·√(24/N)/√((1+4x₀)(1−4x₀)(1−8x₀)),

with λ algebraic, recoverable numerically (the paper's own protocol).

**P19 result:** the pipeline is implemented end-to-end.  Calibration:
N=5 (x₀=1/20, λ=1/4) verified at 1.56e-61.  x₁₂ machinery validated
against the paper's Table 1 at 1e-52..55.  Nine NEW-N identities
(N = 2, 6, 11, 12, 15, 19, 23, 29, 31 — none in the CWZ table)
verified to machine precision, with x₀ and λ recognized as explicit
algebraic numbers, e.g. N=2: x₀ satisfies 50v²+4v−1=0 (v=(3√6−2)/50),
λ = (6−√6)/15.  Novelty: absent from the CWZ table and from
Chan–Cooper 2012's tables (novel-to-our-sources; framework-derivable
via CCL Thm 2.1 — the M_N modular-polynomial route is unnecessary for
the numeric-recovery variant).

**P20 census** (running at writing time): systematic (x_N, λ_N)
classification for N = 1..60.

## 5. The generation side (D1, D1-eta)

d → τ → q → θ → k² → j is mechanized; j → (A,B,z) is NOT (0/27).
Literature diagnosis (docs/LITERATURE.md): the parameters live in
**level-6 eta quotients** at CM points plus Conway–Norton linear
relations — not in level-1 j.  D1-eta: machinery validated (documented
values reproduced at 1e-56..59; relation constant corrected 22 → 14);
3/36 integer CM-value hits incl. two small class invariants (8, 9)
mechanically recovered; recovery of (A,B,z) for the known members
remains open (registered limitation).

## 6. Failure-mode taxonomy (the negative-results section)

| Mode | Experiment | Mechanism |
|---|---|---|
| Objectives learn the nuisance | P9 | PCA-1 ≈ log|z| (0.999) |
| Fixed transforms insufficient | P13 v1/v2/v3 | 90-cell ceiling 0.529; AE never lifts raw |
| Same-span refinement vacuous | P15-b | OLS residual ⊥ basis; idempotent refit |
| Bias is idiosyncratic | P15-e | random control ≈ oracle confound removal |
| Internal criteria salience-trapped | P15-d | picks raw by 0.0009 |
| Regime ambiguity | P15-f | PC1 removal: +one family, destroys the other |

## 7. Relation to formal theory (docs/LITERATURE.md)

- "What to keep" for individual objects = algorithmic sufficient
  statistic (Vereshchagin–Vitányi 2004): our ladder instantiates it on
  a math family.
- Nuisance = ancillarity (Fisher; Ghosh–Reid 2010).
- Invariance does not identify the invariant (Rosenfeld et al. 2021 on
  IRM): our regime theorem is the sequence-level microcosm.
- Content/style identifiability requires external assumptions
  (nonlinear ICA: sparsity/mechanism shifts; minimal-change principle):
  our three-closure is the experimental demonstration.
- The machine-discovery differentiation vs Hemmecke (2026): algorithmic
  construction WITH modular-forms knowledge vs testing whether the
  route is findable WITHOUT it.

## 7b. The LLM baseline (P17) — memory vs mechanism

A 27B reasoning model (Ternary-Bonsai-2, local) on the counterfactual
testbed: literature-real series 0.235, counterfactual series 0.250 —
both at chance (0.247), INCONCLUSIVE as a discriminator at this scale.
Two registered secondary findings: with deliberately wrong few-shot
labels the model answers from structure ZERO times (labels act as
authority, suppressing computation); and raw decimal sequences do not
reveal the signature even for literature-famous series — consistent
with L3.  The memory-vs-mechanism discriminator stays open for
stronger models or tool-scaffolded prompting.

## 7c. The generation side, mechanically (P18, P19)

P18 (CONFIRMED): the Cooper–Wan–Zudilin level-6 machinery Z(X) is
implemented and verified numerically — third-order ODE residual 1e-63,
differential identity 1e-68 — including the discovery that the sqrt
branch has TWO SHEETS meeting at the stationary point X = 1/36.  The
CM-point table yields EXACT RATIONALS (1/36, 1/54, 1/100, …): a
mechanically generated Γ₀(6) class-invariant table.

P19 (CALIBRATION-BLOCKED): mechanical generation of the series
themselves is blocked on the λ_N definition (it requires the modular
polynomial M_N's derivative, per CCL 2004 Theorem 2.1, under the
X = 4x(1−x) convention) — implementation scoped at roughly half a
session.  The verified substrate (Z/X machinery + X₀ table + sequence
generators) is in the repo.

## 8. Open experiments (registered next steps)

- Exact envelope identification via structural priors (known class
  count + ladder shape) — the remaining readout gap.
- External-information routes: counterfactual perturbation access.
- LLM baseline at frontier scale + tool-scaffolded prompting (P17's
  registered continuation).
- D1-eta stage (iii): derive (A,B,z) from eta values for known members;
  then novel-series generation (P19 continuation: implement the
  X = 4x(1−x) convention and the M_N modular-polynomial derivative).
- Extending confusability theory: Γ-gap ⇒ a priori difficulty ranking
  for new invariant families.

## Reproducibility

Every experiment: one script, one JSON, one registry row with
pre-registered thresholds; thresholds revised only through recorded
amendments (P16 REVISION 1 documents the practice failure honestly).
CI runs the mathematical gates (validator, Heegner j, Chudnovsky).
