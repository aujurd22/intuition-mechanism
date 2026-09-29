# Memory Geometry Constraints for RAG System Design

Status: 2026-09-30 05:10.  Synthesis of P90-P117b (the RAG transfer
track of the Memory Geometry program).  These are MEASURED constraints,
not theoretical speculations — each one is backed by experiments on
the SQuAD validation corpus (400 Wikipedia paragraphs, MiniLM 384-d).

## The five measured constraints

### C1. Query floor: ℓ_min ~ 6-12 tokens (P70-b/P96)

Below ~6 tokens, retrieval accuracy drops to near-chance.  Above
~12 tokens, accuracy saturates.  The floor is content-relative
(SQuAD topical paragraphs → knee below 5% cue; FlyMemory dense
conclusions → knee at 10-25%).

### C2. Sibling confusion: 25-50% top1 error (P93-b)

Within-article retrieval: the top-1 hit lands on a WRONG sibling
paragraph 25-50% of the time (Super_Bowl_50: 50%, Economic_inequality:
25%).  This is the dominant failure mode of bi-encoder retrieval.

### C3. Reranker oracle: +33pp available (P94)

An answer-sentence oracle re-ranker lifts top1 from 47.8% to 81.1%
(+33.3pp pooled).  This is the VALUE SPACE for cross-encoder
reranking — the gap between bi-encoder retrieval and perfect
query-content alignment.

### C4. Template dilution: non-monotone degradation (P111/P111-b)

When the text has a rigid template (uniform header), the degradation
curve becomes NON-MONOTONE — adding template text without adding
discriminative content HURTS retrieval.  The dip is a corpus-level
phenomenon (template structure), not an item-level one.

### C5. Query-side lexical fragility: dose-dependent (P122-b; supersedes P117-b)

Bare-question retrieval degrades STEEPLY and dose-dependently under
random-word substitution: top1 49.8 / 38.1 / 27.1 / 17.7 / 7.9 (%) at
substitution dose 0 / 0.2 / 0.4 / 0.6 / 0.8.  Synonym substitution at
the same nominal rate does NO damage (49.7 vs 49.8) — the earlier
"50% synonyms → 0%" claim (P117-b) is RETRACTED (inconsistent with
both measurements; script never archived).  The accurate picture: the
bi-encoder is lexically sensitive, degradation is gradual in the
substitution dose, and MEANING-PRESERVING rewording is safe while
MEANING-DESTROYING rewording kills at high doses.

### C6. Prefix injection hedges question-side damage (P122-b)

With a verbatim 150-char context prefix in the query, destroying up
to 80% of the question's content words costs only 0.9pp top1 (98.8 →
97.9).  The prefix, not the question, carries the retrieval mass.
Conversely the prefix itself is the more fragile asset: the same dose
applied to the PREFIX drops top1 to 59.3.  Ordering matters too:
prefix-first beats question-first at every length (P120), and 150-200
chars suffice (P120 n=2823 curve: 81.3 @ 50ch, 95.0 @ 100ch, 99.9 @
200ch).  SCOPE: the measured prefix is the gold paragraph's own head —
a ceiling, not a deployable rule (P123 measures the deployable
variants: title injection, cross-article stores).

## The design rules derived from these constraints

| Rule | Constraint addressed | Recommendation |
|---|---|---|
| DR1 | C1: query floor | Reject queries < 6 tokens; augment queries < 12 tokens |
| DR2 | C2: sibling confusion | Deploy cross-encoder reranker on top-10 |
| DR3 | C3: reranker value | Reranker can recover up to 33pp top1 |
| DR4 | C4: template dilution | Strip template headers before embedding; index only discriminative content |
| DR5 | C5: query fragility | Meaning-preserving rewording is safe; do not score against high-dose perturbation; prefer expansion over substitution |
| DR6 | C6: prefix hedge | Put a 150-200 char verbatim context prefix FIRST in the query; it hedges question-side paraphrase and carries the retrieval mass — protect its integrity |
| DR7 | C6: prefix source (P122-c) | Take the prefix from the HEAD of the chunk (first sentences / definitional lead): head 98.8% vs tail 66.0% — a 32pp effect that dominates the prefix-length choice |

## The hybrid query optimization (P117)

Context-injection query augmentation (prepend context[:150] + question)
lifts top1 from 55.6% to 91.1% (+35.5pp).  Prefix length sweep:
20ch = 60%, 50ch = 80%, 100ch = 97.8%, 150ch+ = 100%.  The optimal
prefix is 150 characters.

## The contrast gradient (P116)

Retrieval accuracy ordering by query type:
verbatim (100%) >> keyword (75%) >> natural question (48%).
The 48% for natural questions is the quantified first-stage bottleneck.

## The coverage geometry (P90/P93-b)

NN-cos band: p5=0.549, median=0.731, p95=0.824.  Isolate fraction 0%,
duplicate fraction 0%.  Dark tail: 99.86% of entries irrelevant to any
given query — but self-reachability is 100% (P70).  The dark tail and
self-reachability are complementary, not contradictory.

## What this framework does NOT cover

- Cross-encoder reranker performance (requires a reranker model)
- Multi-hop reasoning (requires chain-of-thought)
- Query understanding errors (requires NLU evaluation)
- Generation quality after retrieval (requires LLM evaluation)
- Latency/throughput optimization (systems engineering, not geometry)

## The unified principle

All five constraints reduce to one principle: **contrast** — the
amount of discriminative content in the query relative to the noise
space.  The hybrid query maximizes contrast by combining context
structure with question semantics.  The synonym substitution destroys
contrast by replacing discriminative tokens.  The template dilution
reduces contrast by adding non-discriminative prefix.  The query
floor sets a minimum contrast threshold.  The sibling confusion is
the failure mode when contrast is insufficient to separate siblings.

**RAG retrieval quality = contrast / noise_space_volume.**
