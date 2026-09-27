# Intuition-Mechanism Program

**Insight Mechanism Reproduction Program** — a Mushroom-Body Program track.
**Canonical research state: [docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md)**
(pre-registered experiment registry, P1–P34, every row with verdict and
artifacts). This README is only the compressed entry point.

> Central question: can Ramanujan-style formula discovery be reduced to a
> mechanical pipeline? Which steps are the "inspiration", and can they be
> reproduced by a machine and their signature measured?

## Where the program stands (2026-09-28)

The original single question has decomposed into an empirical ladder. Each
layer now has its own measured verdict:

| Layer | Question | Verdict | Key evidence |
|---|---|---|---|
| Generation (math side) | can the t-family 1/pi pipeline run end-to-end? | **YES** | P18/P19: CWZ machine + 9 identities not in CWZ Table 1, machine-verified; CWZ Table 1 erratum found (N=17: 143/238 -> 43/238, Lean-formalized) |
| Invariant recognition (L1) | given the invariant, is recognition mechanical? | **YES** | P4 17/17 both tiers; P15 blind envelope removal hit@1 0.946 |
| Blind discovery (L2/L3) | can the system find the decomposition/invariant without labels? | **PARTIAL / open** | P15 arc: blind envelope removal works (0.946); three internal criterion routes closed (regime theorem); P32 series: cross-family structural abstraction is real |
| Structure recognition (LLM subjects) | can an LLM see "same generator, new instance"? | **YES** | P32-f native 762/1000 (76.2%, p<1e-300; honestly scored PARTIAL vs its own pre-registered 90% bar); P32-h existing arm 16/20 (80%, p~4e-7) |
| Novelty detection | can it see "this is NOT any of the known structures"? | **NO for the blind judge** | P32-h new arm 4/20 (20%, at the 25% guess line); judge declares NEW only 7/40 times; native structural subject 38/40 (information IS present) |
| Interestingness | given something new, is it worth pursuing? | **UNTESTED** | P33-c only: LLM surprise vs parameter-space novelty rho=+0.30, n=5 |

## The P34-d result (the current hinge)

The LLM window curve looked like an "information window" phenomenon
(W5 peak 67%, W10 trough 40%). P34-d decomposed it: a 6-line rule over the
**early-term support pattern** (t2 vs 6, t3 vs 20, t4 vs 70, flip-presence —
the k=1 term carries comb(n, step), which vanishes for n < step) classifies
all 8 families **perfectly from W=12 on** (census 4800/4800; independently
reproduced on the 280-family appearance-verified corpus: 100% from W7).
Yet the holistic LLM subject sits at 40–76% there. So:

**Information availability is monotone in W; extraction is not. The curve
measures cue extraction, not information.** "Knowing what to throw away"
(t2, t3, t4, flip) beats having twelve times as much raw signal — the toy
version of *insight as compression*.

## Current boundary and biggest unknowns

1. **Cue extraction as the bottleneck** — supported by dissociation, not yet
   by causal intervention; the registered next step endogenously supplies /
   withholds the sufficient cue and measures the effect (P32-i / P34-e).
2. **Novelty detection** — absent in the blind judge, trivial for a reader
   with the structural representation: the open question is *wiring the
   structure representation to the novelty comparison*, not more
   classification scale.
3. **Interestingness** — no experiment yet separates "novel" from "worth
   keeping / predicting"; P33 (n=5) is directional only.
4. Math side: z-construction for the positive-j family; h=2 graded traces;
   general-d 1/pi theory (blocks P4/P6 completion).

## Method notes (what keeps this honest)

- Pre-register design + verdict criteria before running; score against the
  pre-registered bar, not the story (P32-f was downgraded CONFIRMED ->
  PARTIAL on audit).
- User audits are part of the loop and have caught real bugs twice
  (P33 hull-distance implementation; P33-c inside-hull no-op branch).
- Anchor/self-test discipline on the math side (nome convention, inverted
  identity, PSLQ z-sensitivity — see git history and the registry).
- Subjects are declared: native design-aware arms vs blind API judges are
  reported separately, never mixed.

## Law coupling

- Experiment conclusions write back to the Mushroom-Body Program repo
  ([aujurd22/flymemory](https://github.com/aujurd22/flymemory)),
  `research/RESEARCH.md` (L-series laws; L1 form law and L5 aggregation
  law were established there).
- The full prediction registry lives in docs/RESEARCH_PLAN.md
  (registered before running).
