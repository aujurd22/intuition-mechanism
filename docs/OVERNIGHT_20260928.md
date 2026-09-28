# Overnight arc 2026-09-28 (P32-h .. P38)

Session goal: autonomous exploration to 09:00.  Everything below is
committed and ls-remote verified; registry = docs/RESEARCH_PLAN.md
(rows P32-f amendment .. P38), paper = docs/PAPER.md.

## The night in one paragraph

The program's question moved from "can an LLM recognize structure?"
(yes -- established earlier) to three sharper results: the LLM
recognition-vs-novelty dissociation is real and model-robust
(P32-h/i); the sufficient statistic behind the whole family corpus is
so small that it can be rediscovered BLIND by a 4-feature MDL search
(P35-a) and supplied causally to fix the novelty deficit to 100%
(P32-i); and the math side produced the headline — **the algebraic
degree of the hidden parameter lambda exactly reproduces the human
publication boundary of the Ramanujan-type family, and the machine
census goes two levels deeper, with a fully verified cubic-lambda
identity at N=9 whose closed radical form the literature does not
contain** (P36-a).

## Results table

| Row | Verdict | One line |
|---|---|---|
| P32-f amendment | PARTIAL (strong positive) | 76.2% < the pre-registered 90%; B12 < A7 reversal explained by P34-d |
| P33-c fix | (numbers unchanged) | inside-hull no-op branch fixed; five judged points outside hull; rho=+0.300 bit-for-bit |
| P32-h | PARTIAL | blind judge: existing 16/20 vs new 4/20 -- recognition without novelty (doubao); GLM replicates 15/20 vs 6/20 |
| P32-i | Arm S SUPPORTED | supply the extraction procedure -> 39/40, new-arm 20/20 (p=9e-13, doubao); truncation arm swaps bias, net 21/40 |
| P34-d amendment | (user census reproduced) | tree = 100% from W7 on the 280-family clean corpus |
| P35-a | CONFIRMED | blind MDL rediscovers {eq2=6, eq3=20, eq4=70, flip} on 4800 families; 8/9 cells = truth |
| P35-b | PARTIAL | schema induced from 24 examples (55.8% -> 76.2% calibrated; GLM 93.8% zero-shot); tree 400/400 |
| P36-a | CONFIRMED (headline) | lambda-degree census N=2..160: degree 1 = exactly the published rows; deg(lambda)=deg(x0) 20/20; N=9 cubic + exact radical |
| P36-c/d/e | CONFIRMED boundary | deep/plain partition 15/15 x4 + exact PLAIN set at n=20; direction unstable (convention) |
| P37 | SCOPED | CCL Thm 2.1 levels {1..9} exclude level 12; lambda-algebraicity proof open |
| P38 | (a) sketch / (b) NEGATIVE | class numbers do NOT decide rationality (h(D_K)=1 at 12 non-rational rows); degeneration condition open |

## Commit chain

6151612 (P34-d) -> 7eda0f9 (audit fixes + P32-h) -> 46fe484 (P32-i +
README) -> 20b5bf2 (P35 + P36 headline) -> d3ad9f5 (hardening) ->
086e59a (census final) -> ba21b3b (theory note + P36-e/P38) ->
4fbbb5d (cross-model) -> 69ab5a2 (P36-d) -> HEAD.  Writeback:
flymemory repo research/RESEARCH.md (baaf1a3, aced3b2).

## Queued next

1. Independent-session replication of P32-i Arm S (the causal claim's
   last caveat).
2. degeneration classification: rational-x0 criterion via Atkin-Lehner
   fixed points / 12-isogeny self-pairing (P38 open half); P23 orbit
   data is the substrate.
3. P33 with n >= 20 (interestingness correspondence at scale), now
   with the mechanical lambda-degree rank as the value axis.
4. PAPER.md -> LaTeX.

# Session 2 (2026-09-29 00:20 - 03:30): the coverage arc

Thread: the memory-type question rebuilt from geometry. Nine registry
entries landed (P52-P60), six verified, three falsified productively,
one open theory gap sharpened (P57).

## Results in order

- P52 coverage law: two geometry ratios (R/mind, NN/mind) explain every
  cell of the 4-family x capacity-ladder grid; prototype's only edge is
  denoising; capacity substitutes for structure, never the reverse.
- P53 novelty = coverage + clearance: C2 made quantitative; window
  realized (envelope/EPI-ALL 95% det @ 6.7% FA); markov novel author
  invisible in bigram space = representation property, not arm property.
- P54 contrast, not resolution: refinement falsified (ratio falls,
  window closes); contrast-matched asymmetry features open it wide
  (5/5 seeds, 100% @ ~0% FA).
- P55 exact decomposition: accuracy = coverage-event - theft (exact
  where f_cross=0); iid model falsified; plateau = THRESH-reachable
  fraction; cold start is first-class.
- P57 NEGATIVE (theory): naive orbit points are NOT Shimura conjugate
  points; "all orbit values real" was a B=0 artifact; lambda(N=2) is
  cubic not quadratic; step 4 of the genus-theorem stays open with the
  ray-class transport as its precise content.
- P59 query-side detection threshold l* exists (chance at 12 tokens,
  ceiling at 80); fused space halves l*; AND fails, pooling wins.
  Two detector bugs caught and corrected (LOO violation, tuple
  broadcast) -- both had produced fake 100% detections.
- P60 visual family joins the unified table: four families ordered by
  two ratios.

## Discipline notes

Both false-100% detections in P59 were caught by prediction-vs-result
sanity checks, not by eyeballing plausibility -- the register-first
rule paid for itself twice tonight.

## Queued next

1. Ligozat eta-multiplier character implemented exactly (Dedekind-sum
   route) + the level-compatible transport matrices; then step 4 of the
   genus-theorem is either proven or precisely blocked.
2. l* / m* symmetry: is there one law (sample-complexity of novelty)
   with the two thresholds as its training/query projections?
3. Coverage law on the real FlyMemory store (the service IS the
   extended-support regime: heterogeneous entries, dense cores).

## Session 2 addendum (04:40-05:25)

- P61: the (m, seqn) plane is three-region, not one law -- an absolute
  query-resolution floor (~16 tokens), a training-side gate saturating
  at the discovery threshold m* ~ 20, and a ceiling. More data cannot
  buy back a too-short query.
- P62: production FlyMemory audit (read-only): 7325 active memories in
  a narrow anisotropic band (NN-cos 0.44-0.93), zero isolates, zero
  near-duplicates; dark tail 99.86%/query; raw cosine is content-blind
  for novelty in this band.
- P63: exact eta-multiplier extraction validated (24th-root rounding,
  two-tau cross-check, 30/30). Closed-form reconstruction abandoned
  (branch bookkeeping), honestly. Transport-matrix first construction
  BLOCKED with the obstruction precise (no gamma to tau0; subgroup
  scaling fails the order-12 test) -- the class action on X_0(12)-
  structures is step 4's real content.
- P64: l_min scales with statistic dimension (~1 token per free entry:
  K=6 -> 40 tokens, K=10 -> 80). Novelty screening budget = the
  representation's own stabilization cost.

Commit chain (session 2): 4fec85d (P52) -> 369f041 (P53) -> 9790766
(P54) -> d8cdb5b (P55) -> e26b8c6 (P57) -> 6727e4c (P59) -> f843a65
(P60) -> d36d6b9 (P61) -> 90c730e (P62) -> a6ccb0b (P63) -> 5443eee
(transport blocker) -> 7d7e324 (P64).

## Session 2 close (06:25)

Interventional capstone: P65/P65-b. STR viability boundary crosses 50%
at R/mind = 0.500 exactly (simplex geometry, sigma swept). The
prototype/exemplar divergence is UNREACHABLE in single-scale families
(NN/mind locked to R/mind); constructed two-scale classes decouple the
ratios and restore it (+9 pts, consistent). Final form of the memory
law written into MEMORY_LAW.md: boundary (0.5), two-scale condition,
capacity-vs-plateau, novelty clearance, query floor l_min.

Session 2 totals: 14 registry entries landed (P52-P65 + P65-b),
6 confirmed, 5 falsified-with-mechanism, 2 clean negatives (P57 orbit,
P61 single-law), 1 production audit, 1 theory sharpening (P57/P63:
step 4 has its tool; the class-action derivation is the open piece).

## Session 3 (2026-09-29 02:09 - 03:15): literature bridges + Weber reduction

- P66 Hart condensation bridge: the consistent subset ~ the fringe set;
  condensing ratio tracks boundary-carrying mass; label-consistency and
  threshold-coverage are independent criteria.
- P63 v3: closed-form eta multiplier restored (Wikipedia/Estermann form),
  33/33 gate; v2's numeric extraction had a Re(gamma tau) branch bug.
- P57/P68 re-framing: x12(tau0) is itself rational for the five rows --
  no Galois transport needed; the theorem is Weber-type invariant
  rationality; the SL2-transport campaigns attacked the wrong target.
- P69 THE REDUCTION: x12(tau) = x6(2tau) exactly; level-6 census
  d in [2,80]: rational locus = exactly {3,5,7,13,17}, inverse values
  integer (12,20,32,104,200) -- a Ramanujan-type class invariant.
- P69-b: arithmetic core = 2-elementary locus INTERSECT multiplier
  triviality; 2-elementary locus {3,5,7,13,17,35,55,77}; the gap
  {35,55,77} measured non-trivial multiplier; Kani Thm 32 anchor.
- P69-c: the open lemma mapped into Schertz Thm 4 (2002).
- P70/P70-b: production self-retrieval 100% hit@1; half-text cue 91.7%;
  degradation knee at 10-25% cue matches the synthetic l_min law.
- P71: explicit quadratic x6 over j6D found (eigen 1.7e-60);
  discriminant-vanishing route falsified honestly.

Commit chain: 3a09c9d (P66) -> c714d33 (P63v3) -> 5443eee (transport
blocker) -> 7d7e324 (P64) -> d18bd9d (ledger) -> d36d6b9 (P61) ->
90c730e (P62) -> a6ccb0b (P63) -> 7fadd56 (P70) -> 804556d (P70-b) ->
6c03519 (P65) -> e26b8c6..(session 2) -> 3a09c9d..62fc043 (P69-b) ->
7fcd38a (P69-c) -> 80e0321 -> c384050 (P68) -> 5413b3e (P69) -> 62fc043
-> 7fcd38a -> 7fadd56 -> 804556d -> HEAD.
