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

### C7. Conversational anchors are bimodal: freshness is a state variable (P125)

Injecting the previous turn's answer paragraph as query context gives
+34.5pp ON AVERAGE (49.8 → 84.3) — and the average is a lie.  Fresh
anchors (the conversation is still on the paragraph being asked about:
84% of turns) sit at ~98.9%, effectively the gold ceiling for free.
Stale anchors (the conversation moved on: 16%) collapse to 5.9% —
44pp BELOW the no-anchor baseline; the stale anchor steers retrieval
to the previous paragraph.  A wrong-article anchor halves accuracy
(25.7).  Context injection is therefore a STATE-DEPENDENT
intervention: the same mechanism delivers +49pp or −44pp depending on
anchor freshness, which the query layer can measure and guard against
(DR9/DR10).

## The design rules derived from these constraints

| Rule | Constraint addressed | Recommendation |
|---|---|---|
| DR1 | C1: query floor | Reject queries < 6 tokens; augment queries < 12 tokens |
| DR2 | C2: sibling confusion | Deploy cross-encoder reranker on top-10 |
| DR3 | C3: reranker value | Reranker can recover up to 33pp top1 |
| DR4 | C4: template dilution | Strip template headers before embedding; index only discriminative content |
| DR5 | C5: query fragility | Meaning-preserving rewording is safe; do not score against high-dose perturbation; prefer expansion over substitution |
| DR6 | C6: prefix hedge | Put a 150-200 char verbatim context prefix FIRST in the query; it hedges question-side paraphrase and carries the retrieval mass — protect its integrity |
| DR7 | C6: prefix source (P122-c, P127) | Take the prefix from the HEAD of the chunk — but the magnitude is encoder-specific: head−tail gap 32.8pp on L12-v2 vs 5.2pp on all-MiniLM-L6-v2. Direction holds on both; calibrate per encoder |
| DR9 | C7: anchor staleness (P125) | Conversational anchors are bimodal: fresh ~98.9%, stale 5.9% (44pp below no-anchor). Never inject an anchor unguarded — see DR10 |
| DR10 | C7: staleness guard (P125-b) | Dual-query union (bare + anchored pools) with the BARE question as the reranker query: fresh keeps ~ceiling, stale recovers; the reranker needs no anchor |

## The hybrid query optimization (P117/P120) — a CEILING, not a deployable rule

Context-injection query augmentation (prepend gold-head[:150] + question)
lifts top1 from 49.8% to 98.8% (+49pp at n=2823).  Prefix length curve
(P120, n=2823, prefix-first): 81.3% @ 50ch, 95.0% @ 100ch, 99.9% @ 200ch
— 150-200 chars suffice.  Prefix-first beats question-first at every
length (P120 order effect).  Head-of-chunk is essential (P122-c): head
98.8% vs tail 66.0% — the topic sentence carries the mass.  SCOPE: the
injected prefix is the gold paragraph's own head — this measures the
CEILING of context injection.  The deployable variant fails: title
injection (metadata always available at query time) LOSES 9.1pp
within-article and 7.2pp cross-article (P123) — a title has zero
within-store contrast at paragraph granularity.

## The reranker interaction (P124)

The two remedies are ~95% substitutes.  Bare question: rerank lifts
49.8 → 74.4 (+24.6pp).  With the hybrid prefix already present: 98.8 →
100.0 (+1.2pp residual — cross-attention fixes only the last in-pool
ranking error).  DR8: with contrast-carrying context available, skip
the reranker (~1pp cost, POOL cross-attention passes saved per query);
without it, the reranker is worth +24.6pp.

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

All constraints reduce to one principle: **contrast** — the amount of
discriminative content in the query relative to the noise space.  The
hybrid query maximizes contrast by combining context structure with
question semantics.  Word substitution destroys contrast by replacing
discriminative tokens (P122-b: dose-dependent).  Template dilution and
title injection (P123) reduce contrast by adding non-discriminative
content — even REAL metadata fails when it has no within-store
contrast.  The query floor sets a minimum contrast threshold.  The
sibling confusion is the failure mode when contrast is insufficient to
separate siblings.  The prefix hedge (C6) works because the prefix, not
the question, carries the contrast — which is also why the prefix
itself is the fragile asset.

**RAG retrieval quality = contrast / noise_space_volume.**
