# The Geometry of Agent Memory

Status: working synthesis of the registered experiments P40-b, P46,
P52-P55, P59, P61, P64, P65, P66, P72 (2026-09-28/29).  Self-contained;
the registry rows in RESEARCH_PLAN.md carry the artifact pointers.

## Setup

An agent stores items (memories) and answers recognition / novelty
questions about new items, using a bounded store and a fixed
sufficient-statistic representation.  We measure everything with two
geometry ratios of the representation, one absolute decision threshold
THRESH = mind/2 (half the minimum inter-class centroid distance, the
P46-c rule), and one online streaming protocol.

Definitions:

- R  -- within-class spread (mean distance of a class's samples to its
  centroid);  mind -- minimum inter-class centroid distance.
- NN -- intra-class nearest-neighbor spacing.
- Coverage event: a query falls within THRESH of its arm's stored
  representation.  Clearance: a novel sample sits beyond THRESH from
  ALL stored items.

## Law 1 (coverage): recognition = coverage (P52/P65)

An arm can only recognize what its stored representation covers within
the decision radius.  Prototype arm (class mean) viable iff R/mind <=
0.5; exemplar arm (instances) viable iff NN/mind <= 0.5.  Interventional
confirmation: with the class geometry swept directly (regular simplex,
sigma scanned), the prototype arm's accuracy crosses 50% at R/mind =
0.500 exactly (99.0 / 92.3 / 47.9 / 14.0 / 0.6 / 0.0 at R/mind =
0.3..1.2).

## Law 2 (two scales): the prototype/exemplar divergence needs two-scale classes (P65-b)

Single-scale families LOCK NN/mind ~= R/mind (both co-vary with noise),
so neither arm can dominate.  Constructing dense-core + sparse-fringe
classes decouples the ratios and restores the divergence (+9 points for
the exemplar arm, consistent across cells).  The family table obeys
this: envelope/visual (two-scale in feature space) diverge; Gaussian
blobs and well-separated Markov chains do not.

## Law 3 (plateau): capacity saturates at the reachable fraction (P55)

Accuracy of the exemplar arm = coverage-event rate minus cross-class
theft (exact where no cross pair lies within THRESH).  The coverage
event SATURATES at a plateau equal to the THRESH-reachable fraction of
the class support -- coverage is a mixture (core queries always
covered, fringe never), not an exponential in storage count.  Cold
start is first-class: an agent scored early in life underperforms its
plateau by the arrival transient.

## Law 4 (novelty): coverage AND clearance (P53/P54)

A novel class is detectable iff known-coverage holds AND the novel
class clears the union of coverage balls.  Each failure mode is a
distinct pathology: clearance failure = invisible novel class (detection
8-25% at healthy false alarms); coverage failure = vacuous detection
(100% detection at 100% false alarms).  The window is real
(envelope/EPI-ALL: 95% detection at 6.7% false alarms).  The lever for
opening it is CONTRAST (features encoding the hypothesized novelty
structure), not resolution -- refining the same feature family inflates
all distances and closes the window (P54).

## Law 5 (query floor): l_min ~ #free-statistic-entries (P59/P61/P64)

Below a query-resolution floor, no detector works at any training size:
detection is at chance for all m.  The floor scales with the number of
free entries of the sufficient statistic (~1 token per free entry:
alphabet 6 -> 40 tokens; alphabet 10 -> 80).  The (training m, query
length) plane is three-region: floor-limited / discovery-limited
(saturating at the training-side threshold m* ~ 20) / ceiling.  More
data cannot buy back a too-short query.

## Law 6 (storage policy): keep the fringe (P66/P72)

The Hart consistent subset approximates the fringe set; its size tracks
the boundary-carrying mass (fringe fraction), not R/mind.  Streaming
version: under budget, evicting the most-covered (redundant-core)
entries preserves 100% recognition where LRU gives 92% and
fringe-first eviction 54%.  Evict by redundancy, never by recency
alone; on thin-coverage families all policies tie at the family's own
plateau (the redundancy signal itself degenerates).

## Production anchors (P62, P70, P70-b)

The live FlyMemory store (7,325 active memories): NN-cosine band
[0.44, 0.93], zero isolates, zero near-duplicates; dark tail 99.86% per
query (a per-query fact, not a contradiction of self-reachability).
Self-retrieval: 100% hit@1 near-verbatim; 91.7% hit@1 / 100% hit@10
under half-text cues (raw encoder, rerank off).  Degradation knee
between 10-25% of the text (~6-12 tokens) -- the synthetic l_min law
cross-validates on production.  Hook rule: user messages under ~10
tokens cannot reliably retrieve their target; above ~25 tokens they can.

## Design rules for memory systems

1. Choose the memory type by geometry (two ratios), not by taste.
2. Capacity substitutes for structure; structure never substitutes for
   capacity on extended classes.
3. Store until fringe-reachability, then stop (plateau).
4. Budget novelty screening by the statistic's stabilization cost
   (l_min), and open the window with contrast features.
5. Evict redundant cores, keep fringe (streaming Hart).
6. Report the arrival profile with any memory evaluation (cold start).
