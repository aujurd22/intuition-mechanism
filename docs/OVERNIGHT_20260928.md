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
