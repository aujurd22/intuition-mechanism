# Intuition-Mechanism Program

<p align="center">
  <a href="README.zh-CN.md">中文</a> · <b>English</b>
</p>

**Build your own System-One judge: verified, calibrated, audit-trail included.**

**Insight Mechanism Reproduction Program** — a Mushroom-Body Program track.
**Canonical research state: [docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md)**
(pre-registered experiment registry, 110+ unique P-numbers P1–P169, ~350 KB,
every row with prediction, verdict and artifacts).  This README is the
detailed entry point.

> Central question: can Ramanujan-style formula discovery be reduced to a
> mechanical pipeline?  Which steps are the "inspiration", and can they be
> reproduced by a machine and their signature measured?

## What you get (the intuition-pack plugin, P140-P169)

This repo ships `intuition_pack/` — an open protocol for building **your
own Jev-class judgment engine** against any domain, without training:

```
pack_probe      is your domain a compression domain?  (learning curve)
pack_build      distill contrast exemplars + charter + verifier spec
verify / score  mechanical verdicts with full audit trails + abstain
regression      mechanical gate — a pack version ships only if it passes
hook / MCP      auto-injection into your agent's context per domain
```

Every judgment passes **four mechanically-checked conditions**
(Compression / Verification / Transfer / Novelty) — the
Insight-vs-Hallucination boundary is enforced by code, not by a judge's
opinion.  Your data stays local; the verifier registry (10 verifiers +
templates) covers execution, predicate, numeric, schema, set, and regex
shapes.

Measured positioning vs [Jev](https://arxiv.org/html/2609.37647v1)
(the trained System-One discriminator this protocol was benchmarked
against): on the shared dataset (SMS Spam, n=200) zero-shot LLM judges
tie it (96.0-97.0% vs 96.5%) and the pack lifts to **97.5% with a
confidence gate at 99.5% / 91% coverage** (Jev: 95.5% / 63%); on
verifier-backed domains the mechanical layer scores **100% with ECE
0.0075 at $0 and 0.37 ms**.  What this is NOT: a replacement for Jev's
breadth (37 datasets, 432 ms forward pass).  What it is: the
**distillation source and calibration harness** — every judgment in the
archive has passed mechanical verification, so the same pipeline that
judges your domain also produces the training data (and the daily
auto-scan keeps re-finding where the window is open).

> **Insight is verified compression of experience into transferable
> structure.**  Four conditions, mechanically enforced.  Everything else
> is hallucination — and that boundary is measurable.

The program split into three interlocking lines as it ran:

```
            ┌────────────────────────────────────────────┐
            │   the 1/pi identity pipeline (CWZ machine) │
            │   generates identities at industrial scale │
            └──────────────┬─────────────────────────────┘
                           │  who decides what is worth keeping?
        ┌──────────────────┼──────────────────────────┐
        ▼                  ▼                          ▼
┌───────────────┐  ┌────────────────┐  ┌─────────────────────────┐
│ MATH LINE     │  │ JUDGMENT LINE  │  │ MEMORY LINE             │
│ WHY exactly   │  │ can an LLM     │  │ what must a limited     │
│ these rows    │  │ SEE structure, │  │ store keep so that      │
│ are rational  │  │ and can its    │  │ novelty is detectable   │
│ (six-row      │  │ "taste" be     │  │ at all? (coverage       │
│ theorem)      │  │ calibrated?    │  │ geometry → RAG design)  │
└───────┬───────┘  └───────┬────────┘  └───────────┬─────────────┘
        │                  │                       │
        └──────────────────┴───────────────────────┘
                           ▼
        one shared arithmetic object: the GENUS GROUP
   (it organizes the CM values, the human canon, the digits
    the models read, and the geometry of every memory store)
```

---

## 1. The mathematics line: the six-row rationality theorem

**Statement (exhaustively verified for d ∈ [1,300]).**
Let tau0 = i*sqrt(d/6) and x6 = W6/z6 (an explicit level-6 function
built from Dedekind eta products).  Then

    1/x6(tau0) ∈ Z  exactly for d ∈ {1, 3, 5, 7, 13, 17}
                    — verified exhaustively for all d ∈ [1, 300] —

with values **8, 12, 20, 32, 104, 200** (P121: 6 true positives, 294
true negatives, 0 false anything, 50 dps, two independent code paths
agreeing to 3.5e-17; an earlier independent census at [80,200]
agrees).  SCOPE, stated precisely: "exactly" is CENSUS-CONDITIONAL —
exhaustively proved on [1,300], theorem-shaped on the 2-elementary
locus (all ten rows measured, mechanism below), and a conjecture
globally: no counterexample is known or expected anywhere, but a
general proof beyond d = 300 is not given (it would need, e.g., a
proof that the class group is never 2-elementary beyond d = 77 —
verified by enumeration only up to d = 500).

![six-row theorem](docs/fig_sixrow.png)

**Why these six (the three-layer answer, P134).**  Write
64·P¹²(τ₀) for the Weber-function value behind x₆.  It is:

1. **an elliptic unit by birth** — 64P¹² = 2³⁰·√(Δ(2τ₀)Δ(6τ₀)/Δ(τ₀)Δ(3τ₀)),
   a Siegel–Ramachandra unit of the ring class field (P79–P84);
2. **forced into Pell form** — on these rows its Galois "support" is a
   single real quadratic coordinate, and a rank-1 field admits only
   one unit shape: 64P¹² = ε_fund^(−2m_d), always a SQUARE of a unit
   (F2, mechanically verified), with the half-exponent |m_d| = 2
   exactly when the 2-primary prime discriminant of D = −24d is +8
   (F3: m = 1, 2, 1, 2, 2 for d = 3, 5, 7, 13, 17);
3. **projected to rationality by the derivative cancellation** — the
   quasimodular obstruction in x₆ cancels identically (P83-A), leaving
   a weight-2 CM ratio whose period cancels: R_d = (Ec/W₆)/24 ∈ ℚ,
   and 1/x₆ = 6R_d + 2 ∈ ℤ.

The field layer is a theorem (2-elementary class group ⟹ H = H_gen,
P132-O1); the orbit layer is measured (support characters χ₋₃ / χ₋₈ /
χ₁₃ per row, P132-O2); the unit layer is verified numerically to
50+ digits everywhere.  The one honestly open core: a uniform rule
predicting the support coordinate s_d ∈ {6, 10, 21, 13, 34} from
arithmetic data alone — this is the classical class-invariant TABLE
layer (Ramanujan 1914 / Weber Table VI), which historically never had
a closed rule either.

The four-layer chain **field → orbit → unit → rationality** — each
layer with content, input, output, proof type, verification, and
failure mode, plus the full scope statement — is written out in
[docs/DEEP_STRUCTURES.md Part I](docs/DEEP_STRUCTURES.md).  Statement
and proof labels: [docs/THEOREM_FIVE_ROWS.md](docs/THEOREM_FIVE_ROWS.md);
the genus-theory layer: [docs/CHARACTER_OBSTRUCTION.md](docs/CHARACTER_OBSTRUCTION.md).

---

## 2. The judgment line: what can an LLM see, and is its taste measurable?

### 2.1 Structure recognition and novelty

| Question | Verdict | Evidence |
|---|---|---|
| Can an LLM see "same generator, new instance"? | **YES** | P32-f native 762/1000 (76.2%, p<1e-300); P32-h existing arm 16/20 (p≈4e-7) |
| Can it see "this is NOT any known structure"? | **NO for the blind judge** (4/20, at guess line) — but 38/40 when handed the structural representation: information present, wiring missing | P32-h |
| Does cue extraction (not information) bottleneck the window curve? | **CAUSALLY ESTABLISHED** | P34-d 6-line early-term rule classifies 4800/4800 from W=12 while the holistic subject sits at 40–76%; P32-i cue injection lifts blind judge to 39/40 |

**The P34-d hinge: information availability is monotone in the
observation window; extraction is not.**  "Knowing what to throw away"
(the k=1 term carries C(n, step), vanishing for n < step) beats twelve
times the raw signal — the toy version of *insight as compression*.

### 2.2 The two-axis interestingness theory (formal: P133)

The judge = (model, framing) is a measurement instrument.  Two axes:

- **SURPRISE** tracks genus-structure depth gdepth = t−1 (the genus
  rank of D = −24d) — but ONLY on degree-matched pairs (the locality
  clause): carriers read 82.1% / 78.9% pooled (p = .0009 / .0005),
  while on gross pairs the same model reads at chance — the depth cue
  and the "astonishing simplicity" cue (1/12, 1/20 are themselves
  arresting) cancel (P129).
- **UTILITY** tracks membership in the published record (rational
  rows): 13:3 and 15:16 reversals, cross-family, pairing-robust
  (P92/P129).

The axes are dissociable (same pairs, opposite majorities — P92/I3),
and **carrier status is a model×format property** (I4):

![judge landscape](docs/fig_landscape.png)

Every cell is at least two-run (P130 series), floors rest on 57 votes
across three presentation seeds (P131), and the calibration is
mandatory before any reading (format_calibration.py, 40 calls,
P128-b).  Central open question: WHY is genus depth visible to a
language model at all — the registered answer attempt is
[docs/DEEP_STRUCTURES.md Part II](docs/DEEP_STRUCTURES.md) (digit
trace + canon absorption), with a pre-registered falsification design
(height-matched deg-matched pairs).

### 2.3 Insight Arena (P152–P153): the formal benchmark

**Discovery Score = mean(Compression, Novelty, Verification, Transfer)**,
all four mechanically computed; the **Insight-vs-Hallucination boundary
is the Verification component** — a stated rule is an INSIGHT iff it
survives mechanical probe verification AND transfers out-of-carrier.

Arena v2 mega-run (P153): 3 models × 8 domains × 3 seeds = **909
item-level judgments**, every one archived with id/truth/pred:

| Domain | deepseek | doubao | kimi | n/model |
|---|---|---|---|---|
| math (census) | 77.1 | 79.2 | 76.0 | 96 |
| sci-data | 81.2 | 93.8 | 79.2 | 48 |
| code-pattern | 100 | 100 | 100 | 60 |
| 5 elementary code domains | 94–100 | 86–100 | 93–100 | 15–18 |

Three standing results: (1) **math is the resistant domain** — no model
exceeds 80% at n=96 (the shrinking law has a floor); (2) code-pattern
saturated cross-model (variance elimination); (3) elementary domains
confirmed at scale. The math track's first run also caught a textbook
HALLUCINATION: the judge stated "RATIONAL iff class number 1" (a
famous-hypothesis-shaped guess) — 5/6 probes, boundary refused INSIGHT.
The Insight-vs-Hallucination boundary is now mechanically enforced, not
judged (P152).

---

## 3. The memory line: coverage geometry → controller → RAG design

### 3.1 The six laws

| Law | Statement | Key numbers |
|---|---|---|
| L1 Coverage | identification = coverage; prototype viability crosses at a precise resource ratio | R/mind = **0.500** boundary (P52/P65) |
| L2 Two-scale | prototype-vs-exemplar divergence needs two-scale class structure | +9 pts after decoupling (P65-b) |
| L3 Plateau | accuracy = coverage-event − cross-class theft; saturates at THRESH-reachable fraction | f_cross = 0 ⇒ exact (P52/P55) |
| L4 Novelty | novelty = coverage AND clearance; contrast (not resolution) opens the window | 95% detection @ 6.7% FA (P53/P54) |
| L5 Query floor | retrieval needs ℓ_min ≈ #free-statistic-entries tokens | K=6→40 tokens; production knee 6–12 (P64/P70-b) |
| L6 Eviction | core-first eviction requires density heterogeneity | 100 > 92.4 ≈ 92.4 > 53.6 (P72); random ≥ LRU on uniform density (P110/P112) |

![memory geometry](docs/fig_geometry.png)

These replicate across five substrates (synthetic families, FlyMemory
production, SQuAD, Gaussian matrix, mathematical text — the last one
*fails* L5 by the template-dilution effect, which is itself a finding:
P111/P113).  The **generalization stack** (P145–P151): probe (compression-domain
detector, with the positive-only-poisoning and form-sensitivity laws) →
conditional pack build → verifier registry (10 verifiers incl. a
template library: schema_check/set_match/all_match) → mechanical gate →
multi-domain hook routing. Three live domains; the **auto-scan loop**
(auto_scan_loop.py, scheduled daily) re-probes candidate domains and
builds only where the shrinking-law window is still open.  The **Memory Geometry Controller** (P73/P74: r, nn, ts,
cov, clr, lq, ff, eps → type/capacity/eviction/verification/query
gate) compresses the laws into a zero-fit-parameter policy, validated
end-to-end on FlyMemory production data (P115).
[docs/MEMORY_GEOMETRY.md](docs/MEMORY_GEOMETRY.md),
[docs/MEMORY_CONTROLLER.md](docs/MEMORY_CONTROLLER.md).

### 3.2 The RAG design language (P116–P127)

Measured on SQuAD retrieval (n = 2823 questions, 6 articles, flymemory
production encoder):

![RAG findings](docs/fig_rag.png)

| # | Finding | Numbers |
|---|---|---|
| C1 | contrast gradient | verbatim 100 > keyword 75 > question 48.3 |
| C6 | gold-head prefix ceiling | 49.8 → **98.8**; saturates ~200 chars; prefix-first wins at every length |
| C6 | topic-sentence effect | head 98.8 vs tail 66.0 (32.8pp on L12-v2; only 5.2pp on L6-v2 — encoder-relative, P127) |
| C5 | bare-question fragility is dose-dependent, NOT the registered "synonyms→0%" (retracted) | 49.8 → 7.9 at dose 0.8; synonym substitution harmless (P122/P122-b) |
| C6 | the prefix hedges question-side damage | 98.8 → 97.9 at dose 0.8; the prefix itself is the fragile asset (59.3) |
| — | metadata injection FAILS | title −9.1pp: zero within-store contrast = pure dilution (P123) |
| — | reranker ≈ prefix substitutes | +24.6pp bare vs **+1.2pp** hybrid (P124) |
| C7 | conversational anchors are BIMODAL | fresh ~98.9 / stale **5.9** (−44pp) |
| — | guard: dual rerank with elementwise max | 87.2 overall, fresh 100.0 (P125-c); cheap staleness signals all rejected (AUC ≤ 0.737, P126/126-b; oracle router ceiling 92.7) |

The design rules DR1–DR10 with the C1–C7 constraints live in
[docs/RAG_DESIGN_CONSTRAINTS.md](docs/RAG_DESIGN_CONSTRAINTS.md); the
controller-facing summary is R5 of MEMORY_CONTROLLER.md.  Two claims
were retracted on the way (P117-b synonyms; the "deployable hybrid"
reading — the measured prefix is the gold paragraph's own head, i.e. a
ceiling), each with a registry pointer.

---

## 4. Where the program stands — one table

| Line | Question | Verdict |
|---|---|---|
| Generation | can the t-family 1/pi pipeline run end-to-end? | **YES** — CWZ machine + 9 identities not in CWZ Table 1; CWZ erratum found (N=17) and Lean-formalized (P18/P19) |
| Invariant recognition | is recognition mechanical given the invariant? | **YES** — 17/17 both tiers; blind envelope removal 0.946 (P4/P15) |
| Structure recognition | can an LLM see "same generator, new instance"? | **YES** (76.2%, p<1e-300) |
| Novelty detection | blind judge sees "new"? | **NO** (4/20) — but trivial with the structural representation handed over (38/40): wiring problem, not scale problem |
| Math theorem | WHY exactly {1,3,5,7,13,17}? | **CHARACTERIZED — verified exhaustively on [1,300], theorem-shaped on the 2-elementary locus, conjectural globally** — elliptic-unit chain field→orbit→unit→rationality (P134/P135); support characters per row (P132); census [1,300] zero errors (P121); open core = the class-invariant table layer + global completeness |
| Interestingness | is "interesting" mechanically decidable? | **TWO-AXIS THEORY, formalized (P133)** — surprise (degree-matched, locality clause) + utility (cross-family) + landscape theorem (model×format); every cell multi-run |
| Memory geometry | which memory should an agent keep? | **SIX LAWS + CONTROLLER** — R/mind = 0.500 boundary; controller validated on production (P115) |
| Retrieval transfer | do the laws survive outside our stack? | **YES, five substrates** — plus the RAG design language (DR1–DR10) as the applied payload |

## 5. Method notes (what keeps this honest)

- **Register-first**: design + verdict criteria written before running;
  scored against the pre-registered bar, not the story (P32-f was
  downgraded CONFIRMED → PARTIAL on audit).
- **Retraction discipline**: three retractions and one per-row criterion
  correction are IN the registry with pointers (P117-b, P98-c, P119,
  the deployable-hybrid reading) — negative results are results.
- **Expansion-before-belief**: three small-sample signals were killed by
  expansion (P88's 0.622, P96-b's 10:4, P97-b's 11:9); floors rest on
  38–57 votes.
- **Independent re-derivation**: external audits and self-audits caught
  the argsort-correlation bug, the .real-extraction bug, the v=4
  decompose bug, the nome-convention trap (η(kτ) = η_nome(q^k), not
  η(kq)), and the reduced-forms-only provenance gap (P132's Lemma A
  came from auditing it).
- **Provenance audit is mechanical**: audit_provenance.py scans all
  artifact citations in the registry (181/183 present; the 2 missing
  are annotated live-service probes).
- **Subjects are declared**: native design-aware arms vs blind API
  judges reported separately, never mixed.

## 6. Repository map

```
docs/
  RESEARCH_PLAN.md            the registry: 108 P-numbers, every verdict + artifact
  THEOREM_FIVE_ROWS.md        six-row theorem: statement + proof labels
  CHARACTER_OBSTRUCTION.md    genus-theory layer (P132 closed + corrected)
  DEEP_STRUCTURES.md          the two deep questions (P134 synthesis)
  INTERESTINGNESS_FORMAL.md   two-axis theory, formal (P133)
  MEMORY_GEOMETRY.md          six laws, five substrates
  MEMORY_CONTROLLER.md        R1-R8 policy spec + DR interface layer
  RAG_DESIGN_CONSTRAINTS.md   C1-C7 + DR1-DR10 design language
  GEOMETRY_PROTOCOL.md        cross-substrate M1-M4 standard + law table
  NIGHT_SUMMARY / HANDOFF     session summaries
  fig_*.png                   the four figures above
format_calibration.py         per-model judge calibration (P128-b)
audit_provenance.py           registry artifact-citation audit
p*.py, *.json                 ~100 experiment scripts + archived results
```

## 7. Law coupling

- Experiment conclusions write back to the Mushroom-Body Program repo
  ([aujurd22/flymemory](https://github.com/aujurd22/flymemory)),
  `research/RESEARCH.md` (L-series laws; L1 form law and L5 aggregation
  law were established there).
- The full prediction registry lives in docs/RESEARCH_PLAN.md
  (registered before running).  Everything pushed here is reproducible
  from the archived JSONs; figure source: make_readme_figures.py.
