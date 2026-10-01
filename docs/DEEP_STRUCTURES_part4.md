# Part IV — The Formal Definition (P154, from the user's V2 directive)

## IV.1 The definition

> **Insight is verified compression of experience into transferable
> structure.**

Four necessary conditions, each mechanically checkable:

| # | Condition | Mechanical check | Failure mode |
|---|---|---|---|
| 1 | **Compression** — the stated structure is SHORTER than the experience it covers | mdl_ratio = bits(data)/bits(rule) > 1 | restatement (rule ≈ data length) |
| 2 | **Verification** — the structure survives mechanical testing on data NOT used to form it | verifier(probe set) agreement = 1.0 | hallucination (compressed but wrong) |
| 3 | **Transfer** — the structure holds when the CARRIER changes (regime, shape, field) | probe accuracy = 1.0 on out-of-carrier items | overfit (fits discovery set only) |
| 4 | **Novelty** — the structure is not a restatement of the input | rule statement absent from charter; rule adds a predicate the data did not display verbatim | paraphrase |

**Boundary (mechanical, not judged):**
  INSIGHT         = conditions 1 ∧ 2 ∧ 3 ∧ 4
  HALLUCINATION   = compression present, verification < 1
  OVERFIT         = verification 1 on discovery set, transfer < 1
  PARAPHRASE      = novelty fails
The P152 arena run demonstrated the boundary catching a real case: the
judge's "class number 1" rule scored 5/6 on probes — famous-hypothesis
SHAPE, verification failure — refused INSIGHT status mechanically.

## IV.2 Search-space collapse (SCR)

The four conditions presuppose a search space that COLLAPSED.  The
collapse is measurable as prediction-entropy reduction:

    H_before = entropy of the candidate-continuation distribution
               BEFORE the structure is committed
    H_after  = entropy AFTER
    SCR      = H_before / H_after

Operationalization without eliciting a distribution: the ENSEMBLE
spread of predicted continuations across models x seeds.  P153's
math-track data is the first measurement: across three models the
predicted continuations of the census probes disagreed massively
(76-79% agreement with a fixed rule = high H_before relative to a
solved domain, where all models read 100%).

The chain closes:  Compression REDUCES the description, Verification
TESTS the reduction, Transfer ESTABLISHES it beyond the discovery
carrier, Novelty GUARANTEES the reduction was not already given.
Insight = the event of H collapsing under all four guards.

## IV.3 What still separates this from a general intelligence definition

- H_before is operationalized as ENSEMBLE spread (model-relative), not
  as an absolute count of the hypothesis space — an absolute SCR needs
  a hypothesis-space grammar, which is domain-specific (P135's open
  core: the class-invariant table layer is exactly an unenumerated H).
- Condition 4 (Novelty) is currently "not stated in charter" — a
  conservative bound; true novelty vs training-set membership remains
  open (the P152 math-track HALLUCINATION rule, class-number-1, IS
  likely in training corpora — flagged, not resolved).
- The curiosity loop (direction 5): H_before is also the INFORMATION-
  GAIN signal for experiment selection (P137's greedy loop) — the two
  halves of the program share the same quantity.

---

# Part V — Experiment 2: counterexample pressure (P154)

The user's Experiment 2, mechanized: 8 sequence families with
execution-generatable truth, each probed for (a) stated rule,
(b) 4-term continuation, (c) membership judgment.  Mechanical scoring
against THREE attractors:

  TRUE continuation        (the strong explanation wins)
  degree-7 polyfit         (the overfit attractor: fits the 8 discovery
                            terms perfectly, diverges after)
  weakest-consistent rule  (e.g. 'all even' / 'all odd')

Plus the classic trap: odd numbers 1,3,5,7... with a membership probe
on 9 (odd: YES; the 'all primes' hallucination: NO).

Results: p154_counterexample_results.json (3 models x 8 families).

## IV.4 SCR MEASURED (P155) — residual disagreement across independent judges

Operationalization: H_before per probe = binary entropy of the 9
judgments (3 models x 3 seeds, P153 archive) around the judgment
distribution.  The mechanical verifier's H_after = 0 (deterministic),
so the RESIDUAL H is exactly the un-collapsed hypothesis space that
survives after each judge's independent discovery attempt.

| domain | residual H | unanimous% | reading |
|---|---|---|---|
| code_pattern | 0.000 | 100% | FULL COLLAPSE — the purity rule transferred identically to every judge |
| list_ops | 0.000 | 100% | full collapse |
| string_ops / recursion | 0.084 | 83% | near-collapse |
| date_logic / dict_ops / numeric | 0.10-0.18 | 80% | near-collapse |
| math | 0.231 | 72% | partial — models share most of the rule, split on a probe subset |
| sci_data | 0.357 | 50% | NO collapse — every judge carries a PRIVATE hypothesis |

TWO findings:

1. The collapse ordering REPRODUCES the accuracy ordering (Spearman
   ~1.0 across the nine domains) — residual disagreement is a
   domain-intrinsic property, not judge noise.  A domain is a
   compression domain iff independent judges COLLAPSE to the same
   structure — which is the P144/P146 boundary rediscovered from the
   judge side.

2. sci_data is UNDERDETERMINED: doubao reads 93.8% (high accuracy)
   while disagreeing with the other two judges — at least two
   DIFFERENT transferable structures fit the discovery set.  This is
   the textbook underdetermination of theory by evidence, appearing
   as a measurement.  The SCR frame says what to do: raise H_before
   by widening the probe carrier until the private hypotheses diverge
   (regime change did not separate them; a carrier that breaks BOTH
   candidate rules would).

CENTRAL QUESTION operationalized: "what kind of compression produces
transferable structure" = "which discovery sets drive residual H to 0
across independent judges" — measurable per domain, per probe, with
the archive already on disk.

## IV.5 THE VERBALIZATION GAP, measured (P156)

Protocol: elicit each model's stated rule for the sci-data discovery
set (3 models, same 10 series, charter demands a portable rule), then
IMPLEMENT the stated rules literally and score them.

Result: ALL THREE stated rules fail on 5/10 discovery series — every
one misclassifies exactly the NORMAL series (a T=2 damped sine at
dt=0.25 has +++--- sign blocks; "strict alternation" (deepseek),
"+++− 4-blocks" (doubao), "++−− cycle" (kimi) all reject those).  On
the T4/T6 discriminator probes, all three implemented rules collapse
to ALWAYS-ANOMALOUS.

Yet the models' OPERATIVE judgments run 79-94% correct on the same
probes (P153) — far above their stated rules.

    stated rule accuracy   ≈ 50% (worse than the all-NORMAL prior)
    operative accuracy     ≈ 79-94%

CONCLUSION (Polanyi's paradox, quantified): the models know a sign-
structure rule they CANNOT state.  The verbalization channel is the
bottleneck, not the knowledge.  DESIGN CONSEQUENCE for the Arena
(backend for P152's choice): the Verification component MUST score
probe agreement — scoring rule-statement quality would deny INSIGHT
status to every judge on this domain, including the 79-94%-accurate
ones.  "We know more than we can tell" is now a measured number.
