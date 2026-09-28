# Cross-Family Memory Comparison: The Condition Law

Four families, one protocol (P46 recovery/weak/variant arcs), two memory
types (structural vs episodic). The law:

**Structural memory beats episodic memory on recovery and drift IFF the
sufficient statistic produces a compact discrete partition (C1 AND C2
of the P50 two-condition law).**

| Family | C1 extraction | C2 novelty hull | STR | EPI | Winner |
|---|---|---|---|---|---|
| t-combinatorial | YES | YES | 83.7% | 82.5% (ALL) | STR |
| envelope ladder | YES | PARTIAL | 15.2%* | 84.8% (ALL) | EPI |
| Markov authors | PARTIAL | NO | 87.6% | n/a | both fail novelty |
| oscillators | YES | NO | 89.8% | 90.9% (ALL) | tie |

*envelope STR-centroid fails because centroid smoothing destroys the
local boundary in a continuous overlapping ladder; with normalized
cosine centroids it recovers to 52.5% but still underperforms EPI-ALL.

**The two-condition law**: recognition accuracy requires C1 (extraction
quality -- does the representation expose the class signal?); novelty
detection requires C1 AND C2 (does the representation place the new
class outside the known hull?). Neither condition alone suffices; both
are family-dependent.

**The discovery threshold** (P40-b/P42/P43): the sufficient statistic
must be discoverable at the available sample size. The MI/MDL-gain rank
correlation rises from 0.565 (m=10) to 0.890 (m=40) -- below m*, the
compressor finds features that compress but do not inform.

**The phase boundary** (P47): on matched geometry, both memory arms
rise monotonically with Delta/sigma, transitioning between ratio 1 and
2. The memory-type choice is secondary to the gap-to-noise ratio.

## The coverage law (P52, 2026-09-29)

P46-c phrased the prototype/exemplar reversal as discrete-vs-continuous
support. P52 replaces that phrasing with a measurable mechanism.

Protocol: shared absolute threshold THRESH = mind/2 (min inter-class
centroid L2 / 2, the P46-c rule) for BOTH arms; EPI capacity ladder
k in {1, 3, 10, ALL}; four families.

Two geometry ratios decide everything:

- R/mind  -- within-class spread over min inter-centroid distance.
  Governs the PROTOTYPE arm: the mean covers one ball of radius THRESH,
  viable iff R <= mind/2.
- NN/mind -- intra-class nearest-neighbor spacing over mind. Governs
  the EXEMPLAR arm: stored instances cover balls of radius THRESH,
  viable iff NN <= mind/2.

Measured (p52_coverage_geometry.json / p52_coverage_law.json):

| family | R/mind | NN/mind | STR | EPI1 | EPI3 | EPI10 | EPI-ALL |
|---|---|---|---|---|---|---|---|
| markov-standard | 0.432 | 0.427 | 64.6 | 15.4 | 38.5 | 63.1 | 68.5 |
| markov-hard | 1.414 | 1.500 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| markov-bimodal | 1.177 | 0.862 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| envelope-staircase | 1.411 | 0.318 | 25.8 | 28.3 | 55.0 | 73.3 | 76.7 |

Every cell follows from the two ratios; the all-zero rows were
predicted from geometry before the run. Three-seed check: orderings
stable, absolute numbers vary with stream order (online order effect) --
the claims are ordinal.

Reading:

1. The prototype's ONLY edge is denoising: on the concentrated family
   STR 64.6 >> EPI1 15.4 (a single instance carries sqrt(2) x R of
   sampling noise the mean averages away). The t-family result (STR
   wins) is the R ~= 0 limit: the class IS a point.
2. Exemplar memory is a nonparametric sampler: accuracy rises
   monotonically with capacity exactly where the support exceeds the
   decision radius (envelope: 28.3 -> 76.7). This, not
   "continuity", is why the envelope family favors EPI.
3. Capacity substitutes for structure (EPI-ALL >= STR on every viable
   family); structure does not substitute for capacity on extended
   classes (no k makes STR viable when R > mind/2). Asymmetry.
4. Limit case: as k -> inf, 1-NN approaches twice the Bayes error
   (Cover-Hart) while nearest-mean is unbounded-suboptimal on
   non-unimodal classes -- the coverage law is the finite-k,
   thresholded operationalization of that classical result.

Scope caveat: all numbers are within the shared absolute-threshold
protocol. Per-arm relative-distance normalization (used in the first
Markov runs) is a DIFFERENT protocol and gives different absolute
numbers; the law is stated and tested inside one protocol.

Design note for future arms: the memory-type choice is a sampling
strategy. "Store the mean" and "store instances" are two ends of one
coverage dial; the agent-relevant question is not WHICH memory type
but whether the stored representation's coverage ball(s) match the
class support against the decision radius.

## The coverage curve, quantitatively (P55, 2026-09-29)

Instrumented decomposition of the EPI(k) arm:

  accuracy = P(coverage event) - P(cross-class theft)

Exact where f_cross = 0 (markov: 67.7 = 67.7 at k=40); envelope's
8.3-point gap at k=40 is theft, matching its f_cross = 0.0075.

The registered iid model a(k) = 1-(1-f)^k is FALSIFIED in shape: it
predicts ~100% coverage at large k, measurement saturates at 67.7% /
80.8%.  Reason: f is a population average over heterogeneous query
positions.  Coverage is a MIXTURE -- queries in the class core are
covered almost surely at any k; queries in the fringe are covered
never -- so the curve rises to a plateau equal to the THRESH-reachable
fraction of the class support (computable pre-run from full-storage
geometry), with the pre-plateau transient set by the online arrival
profile.  The k_eff = 6 reading of 40 stored samples conflates
heterogeneity with correlation; do not use it.

Two design consequences:

1. Storage beyond the fringe-reachability of the class buys NOTHING
   (accuracy plateaus): the marginal instance only helps queries whose
   neighborhood is still empty -- spending samples on class cores is
   waste.  (Connects to P40-b's discovery threshold: below m* the
   fringe is most of the class.)
2. Cold start is a first-class term: an agent scored early faces
   near-empty storage and underperforms its plateau by the arrival
   transient.  Memory evaluations must report the arrival profile.

## The unified coverage table (P52-P60, 2026-09-29 night)

All families under ONE protocol (THRESH = mind/2 absolute, online
streaming, EPI FIFO capacity):

| family | R/mind | NN/mind | STR | EPI-ALL | reading |
|---|---|---|---|---|---|
| markov-standard | 0.432 | 0.427 | 64.6 | 68.5 | concentrated: tie, both viable |
| markov-hard | 1.414 | 1.500 | 0.0 | 0.0 | no coverage anywhere |
| markov-bimodal | 1.177 | 0.862 | 0.0 | 0.0 | no coverage |
| envelope | 1.411 | 0.318 | 25.8 | 76.7 | extended+dense: EPI >> STR |
| visual (P60) | 0.586 | 0.214 | 35.2 | 62.5 | extended: EPI >> STR |

Two ratios order every row. The memory-type "choice" is read off the
geometry, and the P55 refinement says the EPI column saturates at the
THRESH-reachable plateau rather than at 100.

Query-side companion (P59): the detection threshold l* exists
(chance below ~12 tokens, ceiling at ~80 on markov-hard), and
representation fusion halves it. Symmetric to the training-side
discovery threshold m* (P40-b): discovery needs enough samples,
detection needs enough query.

## Interventional confirmation (P65/P65-b, 2026-09-29)

Regular-simplex families with sigma swept directly:

| R/mind | STR | EPI-ALL |
|---|---|---|
| 0.30 | 99.0 | 99.0 |
| 0.40 | 92.3 | 94.3 |
| 0.50 | 47.9 | 52.8 |
| 0.60 | 14.0 | 12.4 |
| 0.80 | 0.6 | 0.3 |

The prototype viability boundary crosses 50% at R/mind = 0.500
exactly.  But single-scale Gaussians LOCK NN/mind ~ R/mind (both co-
vary with sigma), so the arms never diverge: the divergence is not
reachable in single-scale families.  Constructing two-scale classes
(dense core + extended fringe, D=5) decouples the ratios and restores
the divergence (+9 points EPI-ALL over STR, consistent across cells).

FINAL FORM of the memory law: (1) prototype viability boundary at
R/mind = 0.5 (interventionally confirmed); (2) the prototype/exemplar
divergence exists only under two-scale class structure; (3) capacity
trades against fringe coverage up to the reachable plateau (P55);
(4) novelty adds the clearance condition (P53); (5) the query side has
its own floor l_min ~ #free-statistic-entries (P64).
