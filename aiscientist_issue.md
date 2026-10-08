# Proposal: math-intuition module — structured conjecture pipeline (from a working Ramanujan-style implementation)

Hi — we run an open research program on **mechanizing the "insight"
step** of mathematical discovery ([intuition-mechanism](https://github.com/aujurd22/intuition-mechanism),
27★): a registered prediction ledger, structure-induction windows, and
a Ramanujan-style pipeline that produces **named-conjecture candidates
with mechanical verification trails** — every output passes
mechanically-checked Compression / Verification / Transfer / Novelty
conditions (the insight-vs-hallucination boundary enforced by code,
not by an LLM's opinion).

**What we could contribute to AI-Scientist's math stage:** a drop-in
"conjecture proposer with audit trail" module —

- input: a domain sample set (as in your template experiments);
- output: ranked conjectures, each with (a) the structural evidence it
  was induced from, (b) a formal or executable check, (c) a
  novelty screen against existing knowledge (mathlib coverage via our
  [selflearner](https://github.com/aujurd22/selflearner) — 181k parsed
  theorems / 66k tactic proofs — or a lighter corpus);
- everything logged in a registry with P-numbered provenance, so an
  AI-Scientist paper can cite *which* structure induction produced the
  idea, not just the final text.

Measured positioning (vs Jev, arXiv 2609.37647, on the shared dataset):
zero-shot LLM judges tie the trained discriminator (96.0-97.0% vs
96.5%) and the contrast-exemplar pack lifts to **97.5% with a
confidence gate at 99.5% / 91% coverage**; local verdict latency
0.37ms at $0 cost.

**Question:** does the paper-generation pipeline have a natural seam
where a "candidate-conjecture with verification trail" provider could
plug in (e.g. between idea generation and experiment design)? If yes,
we're happy to prepare a PR or a standalone repo structured to your
interface. Also happy to hear from anyone for whom this would be
useful.
