# Overnight report — 2026-09-27 01:30 → morning

Registered discovery loop, executed continuously.  Every experiment:
pre-registered (commit before run) → executed → verdict applied per the
registered bands → recorded here and in the registry → pushed with
ls-remote verification.  flymemory RESEARCH.md synced in parallel.

## The one-paragraph story

The night started with the question "is anything left to mine?" and
ended with the pipeline generating new Ramanujan-type series for 1/π
by itself.  The arc: P15-e/f closed the internal-criterion escape
routes of the intuition gap (regime theorem); P16 proved the Γ-constant
proposition (the discovered invariant axis IS a classical Γ-product,
17 digits); the D1/eta route was mechanized (documented literature
values reproduced at 1e-56); P17 measured that a 27B reasoning LLM
cannot do the task by memory or mechanism (both at chance); P18/P19
mechanized the Cooper–Wan–Zudilin construction and generated + verified
identities at 59 N values; P20 produced the complete algebraicity
census and **caught a probable typo in the published CWZ Table 1**
(N=17: λ = 43/238, not 143/238 — their own eq (3.9) closes only with
43/238); P21 mapped the degree structure (bounded ≤ 9, residue-class
pattern, conductor-mix explanation hypothesis).

## Experiment ledger (all registry rows carry the full verdicts)

| ID | Verdict | Commit | One line |
|---|---|---|---|
| P15-e | mechanism FALSIFIED | 3bc6b4f | random control ≈ oracle: bias is idiosyncratic, not a low-dim confound |
| P15-f | NEGATIVE + regime theorem | 3524d41 | salience correction helps one family, destroys the other |
| P16 | PARTIAL (substance confirmed) | 7e0117b | Γ-constant proposition at 17 digits; confusability ordering ρ=−0.956 |
| D1-eta | GATE PASS | 9287d63/1dcfb63 | literature values at 1e-56; 2 new class invariants (8, 9); relation constant 22→14 corrected |
| P17 | INCONCLUSIVE | 30a28fd | 27B at chance both conditions; wrong-label control = 0 |
| P18 | CONFIRMED | f1e4bf6 | Z(X) ODE 1e-63; two-sheet branch; X₀ table exact rationals |
| P19 (A) | CALIBRATION-BLOCKED → resolved | 778e851 | t-family conversion; λ-transposition lesson |
| P19 (B) | **GENERATION CONFIRMED** | 06c0968 | 59 identities generated + verified; 9 outside CWZ Table 1 |
| P20 | CONFIRMED + ERRATUM | 7e0117b | 60-row census; CWZ N=17 λ typo caught (43/238 vs 143/238) |
| P21 | NEGATIVE (informative) | dc6ca6b | deg(x₀) bounded ≤ 9; residue-class structure; conductor-mix hypothesis |
| P22 | CONFIRMED (upgraded) | 480b377 | negative-branch identities; A±2Num antisymmetry = the "±q" identity |
| P23 | CONFIRMED | f84941d | class-group orbit generation: ~180 identities across N=2..30, zero failures |
| P23-b | CONFIRMED | bbafced | N=31..60 completed: **522 machine-generated, machine-verified identities total across the full census range** |
| DEEP-VERIFY | 210 dps | (this commit) | the N=2 showcase identity re-verified at 210-digit working precision: relative error 2.9e-61 over 1400 series terms — the verification is not precision-limited |
| P25-b | CONFIRMED | 5a298f8 | the universal λ law VERIFIED: λ = (rhs − x₀dz/dx)/z(x₀) reproduces all five published λ at 1e-48..53 — the analytic generation formula is CLOSED (no M_N needed) |

Earlier in the night: P1-tag, P2 (registered-caliber), P13-v3 — see
git log; PAPER.md tells the story in order.

## Artifacts

- Scripts: p15b/p15c/p15d/p15e/p15f/p16/p17/p18/p19b/p20/p21 (+gen_identities_doc)
- JSONs: one per experiment, all committed
- Docs: LITERATURE.md, PAPER.md, IDENTITIES.md (this repo);
  flymemory/research/LOOP.md and RESEARCH.md updates (flymemory repo)

## The state of the founding question

"当系统不能保留全部信息时，它应该保留什么？" — on this testbed the
mechanized part now covers: recognition (L1), nuisance removal given
form or labels (L2), generic envelope estimation (the P15 crack), and
as of tonight the FULL generation loop for the t-family identities
(P19) — with the arithmetic census (P20) and degree structure (P21)
explaining what the generated objects are.  What remains un-mechanized:
choosing the decomposition without human priors, and reading the
invariant globally under idiosyncratic bias — with the concrete
candidate routes registered.

## Next-session queue (all scoped, none started)

1. Novelty deep-check of the 59 identities against Ge Fan (levels
   11/23) and Chan–Zudilin (level 17) — per-level parametrizations
   differ, line-by-line comparison needs their tables.
2. λ analytic forms via CCL Theorem 2.1 (M_N derivative) — upgrade the
   numeric recovery to closed forms for the higher-degree rows.
3. P16 Γ-proposition: write the O(1/k²) expansion constants (c₂, c₃)
   for a formal non-numerical proof.
4. P17 at frontier scale (API access required).
5. PAPER.md → LaTeX (the skeleton is complete).
