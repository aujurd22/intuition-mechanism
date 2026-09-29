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

### C5. Synonym fragility: 50% substitution → 0% retrieval (P117-b)

Replacing 50% of content words with synonyms COMPLETELY DESTROYS
bi-encoder retrieval (top1 → 0%).  The MiniLM embedding is LEXICALLY
SENSITIVE, not paraphrase-invariant.  Query reformulation is
dangerous; query expansion (adding more terms) is safer.

## The design rules derived from these constraints

| Rule | Constraint addressed | Recommendation |
|---|---|---|
| DR1 | C1: query floor | Reject queries < 6 tokens; augment queries < 12 tokens |
| DR2 | C2: sibling confusion | Deploy cross-encoder reranker on top-10 |
| DR3 | C3: reranker value | Reranker can recover up to 33pp top1 |
| DR4 | C4: template dilution | Strip template headers before embedding; index only discriminative content |
| DR5 | C5: synonym fragility | Do NOT paraphrase queries; use original wording; expand rather than substitute |

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
