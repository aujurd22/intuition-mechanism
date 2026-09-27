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

## Abstract Part II (2026-09-28): recognition, novelty, and the
arithmetic depth of a hidden parameter

A second campaign moves from envelope invariants to WHOLE STRUCTURES.
On a 4800-family generator corpus with pre-registered blind protocols:
(1) cross-family structural recognition is real (878/1120 subject
trials, two models); (2) it dissociates from novelty detection --
blind judges classify known families at 75-80% but detect genuinely
absent structure at chance (P32-h), and the deficit is CAUSALLY an
extraction failure: supplying the four-feature sufficient cue lifts
novelty to 20/20 (p = 9e-13) while context truncation does not
(P32-i); (3) the sufficient cue itself -- three terms and a sign
flag -- is discoverable from raw data by blind MDL search (P35-a) and
its schema is inducible by an LLM from 24 examples (P35-b);
(4) on the identity side, the algebraic degree of the hidden
parameter lambda, censused over N = 2..160 with fully verified
minimal polynomials, EXACTLY reproduces the human publication
boundary of the family -- the five rational-lambda rows are
precisely what the literature contains, and the machine census
reaches two levels deeper, to a verified cubic-lambda identity at
N = 9 with a closed radical form (P36-a); no further shallow rows
exist through N = 800; (5) blind judges read that depth off twelve
digits of x0, separating deep from plain perfectly in five
consecutive runs across two model families (P36-c/d/e).  The
testbed's moral: insight, here, is the extraction of a small,
predictively valid sufficient structure -- and "which structure is
worth keeping" turns out to be measurable as arithmetic depth.

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
Then lim_{k→∞} H_s(k)·k^{3/2} = 1/(Γ(1/2)Γ(1/s)Γ(1−1/s)), which by
Euler's reflection formula collapses to the closed form

  C_s = sin(π/s) / π^{3/2}.

*Proof sketch:* (a)_k/k! = Γ(k+a)/(Γ(a)Γ(k+1)) ~ k^{a−1}/Γ(a) by Stirling;
multiply the three factors; the exponents sum to −3/2 and the constants
to the reciprocal Γ-triple, then apply the reflection formula.  The
product converges as O(1/k); numerics: extrapolated constant matches the
closed form to 1.7–3.4e-17 for all four s (p16_gamma.py, after the
registered revision).
*Corollary (a-priori confusability):* adjacent-s confusion is predicted
by the Γ-gap |log C_a − log C_b| = |log sin(π/a) − log sin(π/b)|; the
ordering {2,3} < {3,4} < {2,4} = {4,6} < {3,6} < {2,6} matches the
empirical confusion counts.

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

**Showcase identity (N = 2, written out).**  With
t(n) = Σ_{k≤n/2} C(n,2k)C(2k,k)²C(2n−4k,n−2k),  x₀ = (3√6−2)/50,
λ = (6−√6)/15, N = 2:

  Σ_{n≥0} (n + λ) t(n) x₀ⁿ = (1/(2π))·√12/√((1+4x₀)(1−4x₀)(1−8x₀)),

numerically verified to the full 60-digit working precision.  The
eight further identities (N = 6, 11, 12, 15, 19, 23, 29, 31) are in
p19b_z12_results.json with their algebraic (x₀, λ); docs/IDENTITIES.md
lists all 59 mechanically generated identities for N = 2..60, each
re-verified at machine precision.

*Literature anchoring:* the identity shape is exactly the
Chan–Chan–Liu Theorem 2·1 structure specialized to the level-12
t-family — CWZ state this explicitly ("Theorems 3.1 and 3.2 can be
used in a theorem of Chan, Chan and Liu to produce a family of series
for 1/π of the form (3.9)").  Our contribution is the registered,
zero-human-mathematics pipeline that instantiates it.

**Class-group orbit generation (P23, CONFIRMED).**  The identity holds
not just at the cusp-side representative but at EVERY conjugate CM
point: enumerating the reduced forms of D = −24N and evaluating the
level-12 machinery at each τ-form yields a verified identity per form —
~180 identities across N = 2..30, zero failures.  The orbit size
(distinct x₀ values modulo conjugation) is the class-group image on the
level structure; e.g. N = 5 has four conjugate values of which the CWZ
row's 1/20 is one — the published rational rows are the trace-
degenerate tips of full orbits.

**Universal λ law (P25, CONFIRMED).**  The linear parameter is a
UNIVERSAL function of the CM point alone:

  λ = ( rhs(x₀) − x₀·dz/dx(x₀) ) / z(x₀),

verified against all five published λ values at 1e-48..53 — including
the N=17 value 43/238 (confirming the erratum: 143/238 cannot arise
from the correct machinery).  No modular polynomials, no per-case
mathematics: the analytic generation formula for the whole t-family is
closed.

**P20 census** (CONFIRMED): the systematic (x_N, λ_N) algebraicity
classification for N = 1..60.  All five CWZ rational rows reproduced;
13 N carry quadratic x_N and 8 N carry quadratic λ_N beyond the paper's
table; and the census **caught a probable typo in the published CWZ
Table 1**: at N = 17 the arXiv v2 table prints λ = 143/238, but eq
(3.9) closes only with λ = 43/238 (80-digit solve; residual 4.8e-56
vs 0.42 miss).  The first literature-erratum catch of the mechanical
pipeline.

**P21 census extension** (NEGATIVE as registered, informative):
deg(x₀) is BOUNDED (≤ 9 for all N = 2..60, while h(−24N) reaches 30)
with clean residue-class structure — deg 1 exactly at the CWZ five;
deg 2 at N = 2, 11, 19, 23, 25, 35, 43, 47; deg 3 at N = 9, 27, 29,
31, 37, 39, 41, 49, 53 — so the naive deg-vs-h(D) prediction fails:
x is a level-12 function whose CM values live in ring-class fields of
MIXED conductors (the level-12 η fractions shift the relevant order).
Registered as the explanation hypothesis.

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

## 7b2. The first positive L3 datapoint (P32-a) — cross-family distillation

The internal-criteria closure (P15-d/e/f) showed that within ONE family,
no purely internal criterion can identify the nuisance.  P32-a tested
the obvious escape: **cross-family distillation** — can a frontier LLM
identify the structural class of a NOVEL family from context families?

Design fixes over the first P32 attempt: (i) the held-out families are
SYNTHETIC, constructed for the experiment (parametrized binomial sums
absent from training corpora) — removing the recall-vs-inference
confound that made the original invalid (famous sequences are in every
LLM's training data); (ii) the subject is the calling LLM itself,
answering blind in-transcript before the mechanical ground-truth check;
(iii) two of the four trials are OPEN judgments ("none of the context
families matches").

**Result: 4/4 structural identifications.**  The subject classified the
held-out S4 with S1 from the step-3 fingerprint (identical first three
terms then divergence, same radius), recognized S2 as an oscillating
self-family distinct from all context, S3 as a smooth self-family with a
deeper radius, and S1 as S4-class in reverse — including two "none of
the above" open judgments answered correctly.

Registered caveats: the subject judged its own experiment (ground truth
mechanical by construction, but design-aware); four trials is a
demonstration, not a statistics-grade sample.  Queued: multi-family
expansion with independent judges.

**Reading:** the L3 barrier conclusion is revised — "impossible within
one family" stands, but the nuisance-identification prior IS
distillable across families by a frontier LLM.  Intuition, on this
testbed, is exactly the cross-family residue.

**Scale-up and honest boundaries (P32-d/e/f/g, P33-c, P34).**  The
series was then pushed through five scale/robustness rounds:

- **P32-d** (48 auto-generated families, seed-fixed truth committed
  first): 9/10 open-judgment (chance 1/10).  A SCORING-PROTOCOL lesson:
  the first mechanical scoring gave 0/10 because the trial design puts
  all context families in one distract class (the truth class is never
  visible) — "match a context family" is impossible by construction;
  the correct scoring is open-judgment naming of the (step, sign)
  class.  Protocol must match design.
- **P32-e** (480 families): 96/100 (binomial p = 4.65e-81).  All four
  errors are one confusion pair: step-5 alt/no where the sign flip
  lands beyond term 8 — an information boundary of the 7-term window.
- **P32-f** (4800 families, 1000 trials): the first pass ran a
  surface-heuristic script (282/1000) and is explicitly scoped as a
  BASELINE, not a subject result; the NATIVE subject then answered all
  1000 trials: **762/1000 (76.2%, p < 1e-300)** — arm A7 (7-term
  window) 89.8%, arm B12 (12-term) 62.6%.  VERDICT: **PARTIAL
  (strong positive)** -- against the pre-registered criterion
  (accuracy >= 90% AND fewer step-5 confusions in the 12-term arm) it
  fails both conditions; the B12 < A7 reversal was later explained by
  the P34-d decomposition (attention dilution, not an information
  boundary -- that mechanism predicted the opposite direction and is
  falsified).
- **P33 → P33-c**: the first novelty-correlation run was retracted
  after a user-led code audit found three implementation bugs
  (min-pairwise instead of convex-hull distance, degenerate spread
  normalization, rank-direction mismatch).  The corrected rerun gives
  rho = +0.30 (PARTIAL, n=5): direction flipped, confirming the audit
  materially changes the result.  A second user audit then caught a
  residual bug in the corrected implementation: the inside-the-hull
  branch was a no-op (boundary distance returned either way,
  contradicting the registered definition "inside -> 0").  After the
  fix the five judged points all lie OUTSIDE the prior hull, so every
  distance and rho = +0.30 are unchanged bit-for-bit; the fix matters
  for future full-census runs, where interior points now score 0 as
  registered.
- **P32-g** (independent blind judge, doubao-seed-2.1-lite): the
  balanced-design blind replication was INCONCLUSIVE — the judge
  scored 8/20 "new" (chance 0.25) with 12 false-family assignments,
  reproducing the adjacent-class confusion on an independent model;
  the design was itself confounded (the correct answer was always
  "new").
- **P34** (window-curve): the first pass ran a script classifier
  (flat 27.4%) — the P33 mistake repeated; the native pass then
  exposed a SECOND design-layer discovery: the construction-parameter
  class truth crosses sequence-appearance boundaries ((2,alt) with
  large cshift looks like (4,alt) small cshift), so class truth was
  re-defined by appearance clustering (P34-b, silhouette 0.645) and
  the native window-curve measurement queued.

**P34-d: the window curve is a cue-extraction curve, not an
information curve (DOUBLE CONFIRMED).**  Extending the window curve
to W17-20 (100 fresh blind trials, design committed before answering)
and splitting the subject into two conditions separated the two
effects P34-c had conflated.  Subject A (holistic pattern matching,
the method behind the whole native curve) scored 47/75 (63%): W17
40%, W18 76%, W19 72% -- the non-monotonic wiggle continues.  Subject
B is a 6-line rule read off the generator's support structure: the
k=1 term carries comb(n, step), which vanishes for n < step, so the
first three informative terms decide everything -- t2 vs 6 (step 2),
t3 vs 20 (step 3), t4 vs 70 (step 4), and flip-presence (step 5's
sign).  Subject B scored 100/100, and an all-corpus census makes it
exact: 100.0% (4800/4800) at every window >= 12, 99.1% at W10, 96.8%
at W8, 87.5% at W5 -- every short-window miss is a (5,alt) family
whose first flip has not yet surfaced, exactly the predicted hole.
The conclusion inverts the P34-c reading: task information is total
from W12 onward, yet the native subject never exceeds 76% there --
the non-monotonic curve measures attention and cue extraction under
growing distractor material, not information availability.  The
information-window hypothesis survives as a claim about the subject
(there is an optimal attention window) and is falsified as a claim
about the task (the optimal classifier is monotone-perfect in W).
At W17-20 the simplest possible script is perfect while the LLM sits
at 63%: extra terms add zero information and dilute attention away
from the three terms that decide everything.

**P32-h: structure recognition without novelty detection
(PARTIAL -- the dissociation).**  The balanced design the P32-g fix
called for: 40 blind trials, 20 holdouts from context-present classes
(third instances, different parameter triples) and 20 from classes
absent from the context, answer space {A, B, C, NEW}.  The blind API
judge (doubao-seed-2.1-lite, thinking disabled, 200-word bounded
reasoning) splits cleanly down the ladder the program cares about:
existing-family matching 16/20 (80%, p ~ 4e-7) -- but novelty
detection 4/20 (20%, at the 25% guess line).  The judge declares NEW
only 7 times in 40 (true: 20), and its new-trial misses are absorbed
by the context families indiscriminately (A x9, B x5, C x2) -- a
generic "must be one of the above" prior, not the adjacent-class
boundary mode.  The native subject with the declared structural
method scores 38/40 (both misses transcription slips), showing the
information a correct novelty decision needs IS in the visible
window (as P34-d established) -- the blind judge fails because its
structure reading collapses under appearance variability, not
because novelty is unreadable.  Empirically the ladder now reads:
recognition YES, novelty NO (for the blind judge), interestingness
untested.

**P32-i: the deficit is in extraction, causally (Arm S SUPPORTED).**
Two interventions on the same 40 novelty trials separate the candidate
mechanisms.  Supplying the cue-extraction procedure (the P34-d support
signature) lifts the blind judge to 39/40 -- existing 19/20, new
20/20 (p = 9e-13): the novelty-comparison step is trivial once the
sufficient cue is computed, so the P32-h failure is an extraction
failure, not a comparison failure.  Merely truncating every sequence
to 8 terms does NOT teach extraction: new rises to 11/20 (p = .004)
but existing collapses to 10/20 (p = .003 vs baseline) and the judge's
NEW-answer rate flips from 7/40 to 19/40 -- truncation swaps a
conservative bias for a liberal one and leaves net accuracy unchanged
(21/40 vs 20/40).  So the causal story is not "too much context
dilutes attention": it is "the sufficient cue must actually be
computed, and nothing about having less material computes it."  The
missing piece between representation and novelty decision is the
wiring -- exactly the seam the program's next experiments target.
The dissociation is model-robust: GLM-5.3-flash replicates it on the
same trials (existing 15/20, new 6/20).  And the capstone (P39): the
whole ladder -- support-pattern recognition feeding a novelty
comparison -- runs as a 20-line mechanical pipeline at 40/40 on the
same trials.  Everything above chance in this section is now either
mechanized (recognition, novelty-given-the-code, the depth census)
or localized to a specific missing wiring (extraction inside the LLM,
interestingness-as-value).

**P35: the sufficient code is discoverable, by search and (half) by
LLM.**  P34-d supplied the 6-line code with generator knowledge; P35-a
removes the knowledge.  An exhaustive MDL search over a blind,
threshold-free feature space (equality-to-corpus-mode at each
position, plus sign-flip) finds, on the full 4800-family corpus, the
feature set {eq2=6, eq3=20, eq4=70, flip} -- exactly the P34-d tree
-- with no labels, no generator, and no class count; 8 of 9 winner
cells align with the true classes (~600 members each).  No
late-position feature was ever selected: all compressible structure
sits in the first five terms.  The LLM arm (P35-b) induces the right
SCHEMA from 24 labeled examples (a decision tree over flip and early
terms; 55.8% executed on 400 held-out, chance 12.5%) and one
recalibration round lifts it to 76.2%, but thresholds fitted to 3
examples per class never cover the parameter range -- the MDL code
scores 400/400 on the same test.  Decomposition: where-to-look is
inducible from tiny data; exact calibration is a data requirement.

**P36: interestingness is mechanical, and it explains the literature
(the night's headline).**  For every N in 2..160 the lambda of the
t-family identity is computed at 50-60 digits and probed by PSLQ
(every reported relation verified by residual < 1e-40 and direct
identity substitution at error <= 5e-51).  The arithmetic depth of
lambda forms an exact hierarchy: degree 1 for N in {3,5,7,13,17} --
exactly and only the rows humans published; degree 2 for {2,11,19,23,
25,35,43,47,55,73}; degree 3 for {9,27,29,31,37,41,49,53}.  Across
all 20 resolved rows where the x0 side is known, deg(lambda) equals
deg(x0) exactly -- lambda lives in Q(x0) at the same degree, never
deeper -- so the two-row census (x0 from P20/P21, lambda from this
census) tightens the boundary further: humans published exactly the
rows where BOTH hidden parameters are rational.  The hidden
parameter's algebraic degree reproduces the human editorial boundary
of the family perfectly, and the machine census goes two levels past
it.  The showcase is N=9: lambda satisfies 96 l^3 - 192 l^2 + 114 l
- 17 = 0 (height 192, the cleanest non-rational relation found) with
the exact radical

  lambda_9 = 2/3 - (3 sqrt(2) + 19)^(1/3)/12
             - 7/(12 (3 sqrt(2) + 19)^(1/3)),

an identity one algebraic level deeper than anything published in
this family.  And the depth is VISIBLE: a blind judge shown only x0
to 12 digits separates deep from plain 15/15, names four rationals
exactly (1/12, 1/32, 1/104, 1/200), and its full ranking correlates
with true depth at |rho| = 0.79 (p = 4e-4; 0.51 as written before
honoring its own final correction), above a mechanical
rational-detector baseline (0.61).  Insight, on this testbed, is
detecting arithmetic depth from the surface -- and the depth axis
itself turned out to be exactly what the human authors were tracking
all along.

**Cumulative subject record: 878/1120 trials (78.4%) across two models
and two window lengths (chance 140/1120) -- strong positive evidence
for cross-family structural abstraction (recognition layer), while
the flagship P32-f row is honestly scored PARTIAL against its own
pre-registered criterion.**  Two meta-lessons are
registered as first-class results: (1) per-trial attention is
irreducible — batch class-lists cannot substitute for per-trial
judgment; (2) scoring protocol must match experimental design — the
two 0-score failures (P32-d, P34 native) were scoring artifacts, and
the P33 negative was an implementation/convention mismatch, all
caught before entering the conclusion set.

**P32-b/c replication (CONFIRMED).**  Six additional synthetic families
spanning the full structural parameter space (step-2/3/4, oscillating
periods 2 and 3, radii 1/4..1/12): the native subject classified all
six correctly (6/6; chance of a perfect random assignment 2.1e-05) —
including the period-3 vs period-2 oscillation distinction (M6 flips
sign after three positive terms; M2 after two).  An INDEPENDENT BLIND
JUDGE (a different model, doubao-seed-2.1-lite, thinking disabled, no
class definitions, no class count) then grouped the same six sequences:
pairwise agreement with the constructed truth 13/15 = 0.87, with both
disagreements attributable to sequence-length granularity (step-3 vs
step-4 indistinguishable at 8 terms).  The judge invented its own class
names that closely parallel the constructed partition.  Combined:
TEN synthetic families, ten correct classifications by the subject,
plus an independent-judge replication at 0.87 — the cross-family
distillation result stands on two independent models.

## 7c. The generation side, mechanically (P18, P19)

Covered in section 4b above (P18 machinery, P19 generation,
P20 census, P23 orbits, P25 universal lambda law) — see the
experiment ledger for the full verdict chain.

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
- P37/P38 (open theory): the proof that lambda is algebraic at CM
  points for the level-12 family, and the exact degeneration criterion
  deciding WHICH N give rational lambda (the class-number route is
  falsified; the Atkin-Lehner / isogeny-self-pairing route is
  registered) — see docs/THEORY_LAMBDA.md.
- Independent-session replication of the P32-i causal scaffold
  (Arm S), the one remaining caveat on the causal claim.
- Novelty-as-wiring: connect the discovered sufficient code (P35-a)
  to the novelty comparison end-to-end in one system, then extend to
  interestingness-as-value (worth-pursuing), which the degree axis
  does not yet capture.

## Reproducibility

Every experiment: one script, one JSON, one registry row with
pre-registered thresholds; thresholds revised only through recorded
amendments (P16 REVISION 1 documents the practice failure honestly).
CI runs the mathematical gates (validator, Heegner j, Chudnovsky).
