# The Memory Geometry Controller (registered design, P73)

Status: registered 2026-09-29, post-review.  This is the theory-side
deliverable of the program review: a mechanical mapping from measured
representation geometry to memory policy, with every rule bound to a
registered law and zero free parameters left to discretion.  The
downstream consumer is a closed-loop harness (flyloop RSI-0), which
treats this controller as the structured mutation space — optimizing
WITHIN the mapping's constraints tests whether the laws form a runnable
self-improvement rule rather than post-hoc description.

## 1. Inputs (all measured, no fits)

| symbol | quantity | how measured | source law |
|---|---|---|---|
| r   | R/mind  (class spread / min inter-class distance) | centroid geometry | L1 |
| nn  | NN/mind (intra-class spacing / mind)             | pair statistics   | L1 |
| ts  | two-scale flag (core+fringe present)             | per-class radius vs NN profile | L2 |
| cov | reachable fraction at current capacity           | instrumented probes (P55) | L3 |
| clr | novel-clearance ratio (clearance / THRESH)       | held-out probe    | L4 |
| lq  | query length / l_min                             | l_min = #free-statistic-entries | L5 |
| ff  | fringe fraction (entries not redundantly covered)| neighbor count within THRESH | L6 |
| eps | write/read noise                                 | measured flip rate | L4, V7 |

## 2. Output rules (each bound to its law)

R1 (type, v4 final after two synthetic falsifications).  STARVED
(per-class capacity <= cap*(r, D), the measured crossover curve: D=6 gives 1/3/5/5 at r = 0.15/0.25/0.35/0.45; D=12 gives 1/2/8/12 -- P74) and r <= 0.5 -> prototype: a capacity-1
exemplar store IS a noisy prototype, and the denoised mean dominates it
unconditionally (P52: STR 64.6 >> EPI1 15.4; P73-c: 60.0 vs 25.5 at
sigma=1.8).  NON-STARVED -> exemplar with core-first eviction, at any
r: with dense sampling the exemplar arm ties the prototype at the
ceiling in the interior and beats it wherever the mean-ball misses mass
(P73-b: epi = 100% at every sigma, proto 60-98).  The ff-gate of v2 is
DROPPED (it was the wrong correction: ff only matters in the
non-starved regime where both arms have coverage, and there the
exemplar already wins).  Tie zone (r ~ 0.4-0.55, non-starved): ordering
flips across seeds -- honest no-law, degenerate choice.
[L1, L2, L3, L6; P52/P65/P65-b/P73-synth/P73-b/P73-c]

R2 (capacity).  Grow the store until the marginal entry adds less than
delta coverage (cov plateau reached, P55); never past it.  Expected
capacity ~ fringe fraction x reachable support, NOT ~ total input.
[L3, L6; P55/P66]

R3 (eviction).  When budget binds, evict the most-covered entry first
(maximum same-class neighbor count within THRESH).  Never evict by
recency alone.  Guard: if ff-signal degenerates (no entry has >= 1
neighbor within THRESH -- thin-coverage regime), fall back to LRU.
[L6; P72/P72-b, P66]

R4 (write verification).  Verification depth = f(eps, r): deep
verification when support is sparse (r large); at full support the
depth term is minor (V7A: +0.29-0.45 n.s.) -- but see V7C (the clean
2x2 at one matcher regime) before fixing the exact coefficient.
[L4; V7A/V7C]

R5 (query gate).  lq < 1 -> mark retrieval unreliable (report, do not
answer from memory); lq >= 1 -> proceed.  l_min is measured, not
assumed: #tokens at which the representation's own entries stabilize
(P64: ~1 token per free statistic entry; production cross-check
P70-b: knee at 6-12 tokens).
[L5; P59/P61/P64/P70-b]

R6 (novelty screening).  Enable novelty reporting only when clr > 1
with healthy known-coverage (both arms inside their Law-1 viability):
outside that window novelty output is either blind or vacuous
(P53's two failure modes).  Screening features must be contrast
features (encode the hypothesized novelty structure); resolution
refinement is not a substitute (P54).
[L4; P53/P54]

R7 (rehearsal).  Refresh budget goes to fringe entries first
(complement of R3: evicting the core = rehearsing the fringe by
construction).
[L6; P72]

R8 (substrate feasibility, from the harness's G1 lesson).  Every R1-R7
output must pass a substrate-feasibility check before execution: can
the memory engine ACTUALLY represent this policy's writes?  A policy
that is optimal in the abstract layer (e.g., capacity 13 per class)
but violates an encoding constraint (entry-size limits, chunk
atomicity, key structure) is not in the feasible policy set and must
be rejected BEFORE the run -- the G1 failure mode was a statistically
correct mutation that the substrate could not express.  The
feasibility predicates are substrate-specific and belong to the
harness; the controller's obligation is the explicit gate.
[G1 findings, harness repo]

## 3. Falsifiable predictions for the controller (registered)

- P73-P01 (dominance): across the registered family set, the
  controller dominates every FIXED policy (pure prototype, pure
  exemplar, LRU, fixed-verification) on the family-matched metric,
  because it switches the one dimension each fixed policy gets wrong.
- P73-P02 (transition sharpness): the controller's advantage is
  concentrated at the law boundaries (r ~= 0.5, lq ~= 1, the
  two-scale threshold) and vanishes in the interior of each region --
  a distinctive signature that the mapping (not extra tuning) carries
  the performance.
- P73-P03 (no-regression): applying the controller to a regime where
  all inputs are interior (no boundary nearby) matches, not exceeds,
  the best fixed policy -- the controller should not pay for its
  switching logic.
- P73-P04 (RSI-0 interface): mutations that move a config OUTSIDE the
  controller's constraint set (e.g., fringe-first eviction, capacity
  past the plateau) must underperform the constrained menu -- the
  constraint set is the theorem's footprint inside the search space.

## 4. What this controller deliberately does NOT include

- No learned weights: every threshold (0.5, l_min, delta) comes from a
  registered measurement, not a fit.
- No prediction about write verification at sparse support beyond
  V7C's scope (the clean 2x2 is pending; R4 inherits its result).
- No claim about the abstraction/compression axis (a,b vs raw pairs):
  that is flyloop's V7 factorial axis, not a Law-1..6 input.
