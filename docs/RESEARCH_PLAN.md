# Insight Mechanism Reproduction Program (Research Plan)

> Version v1.0 · 2026-09-26 · Positioning: an extension track of the
> Mushroom-Body Program (T0–T3 are new testbeds; results write back to
> `research/RESEARCH.md` in the FlyMemory repo; new law candidates enter
> the L-series)
>
> Prior conclusions (settled in the 2026-09-26 conversation):
> - How Ramanujan's formulas were actually derived = a mechanical pipeline
>   (hypergeometric expansion skeleton + CM-point evaluation + Legendre
>   relations + numerical verification); "inspiration" was just two
>   pattern-completion events within it;
> - Inspiration decomposes into four parts — compression associative
>   memory, high-temperature retrieval, compression progress filter,
>   serial verification — each with a computational existence proof;
> - The breakthrough lies in three seams: ① when compression induces
>   structure ② private notation forging ③ impasse -> relaxation
>   meta-control + offline recombination.
> - This plan turns the three seams into runnable, falsifiable experiments
>   that write back into the law system.

---

## 0. Central hypotheses

**H0 (structure induction, seam ①)**
Under reconstruction loss with forced compression, the optimal encoder
converges to the family's generative skeleton: "surface-unrelated but
structure-homologous" samples become representation neighbours. The effect
has a compression-ratio WINDOW — under-compression is dominated by surface
features, over-compression loses all structure — and structure-domination
collapses outside the window (non-monotonic).

**H1 (engine loop, seam ③)**
In the loop "proposer + millisecond verifier + episodic memory + offline
compression recombination", the recombination mode has a significantly
higher hit rate than memoryless search, with an observable INSIGHT
SIGNATURE: the effective-hit rate immediately after a recombination event
significantly exceeds the background rate.

**H2 (notation forging, seam ②)**
When a model rebuilds a corpus of mathematical objects with self-forged
discrete primitives (private notation), the alignment between primitives
and true mathematical structure (eta products, modular-form skeletons, CM
classes) exceeds that of representations inheriting human notation.

---

## 1. Registered predictions (register first, run second; falsification is a result too)

| ID | Experiment | Prediction | Falsification | Status |
|------|------|------|----------|------|
| P1 | T0 sweep | A compression window [c1,c2] exists with SD > surface-domination + 15pp inside and collapse at both ends (non-monotonic) | SD monotonic or always <= surface-domination | partial (over-compression wall confirmed both domains; under-compression end conditional on surface salience) |
| P2 | T0 mixed families | Within-window latent clustering ARI vs structure labels > ARI vs surface labels + 0.1 | no window or reversal | rides on P1 |
| P3 | T1 math objects | Compression representation of q-expansions clusters by arithmetic invariant (CM disc / level / weight) with ARI > text-embedding baseline + 0.15 | ties or worse | PARTIAL (holds on shape objects; fails on digit-identity objects — representation must match invariant type) |
| P4 | T1 retrieval | With 17 known Ramanujan series as anchors, top-k retrieval of same-family candidates > uniform and text-embedding baselines | ties | anchors READY: all 17 series mechanically verified at 1e-15 (verify_17_v3.py; eq30's true z solved numerically as 3.3260e-4) -- P4 experiment unblocked |
| P5 | T2 engine A/B | Time to first valid formula with recombination <= 1/2 of memoryless baseline, and "hit within 1 step of recombination" rate > 3x background | no advantage | CONFIRMED (v2 hard space + seeded start: first fresh hit 7.75x faster; post-recombination rate 1.0 vs 0.128 = 7.8x) |
| P6 | 17->18 generalization | Given 17 in-family samples, the model's acceptance/ranking hit rate for an 18th valid member > uniform baseline significantly | ties | partially unblocked: 17 verified + Chudnovsky (d=163, D1-passed) as the 18th in the extended family |
| P7 | H2 notation | Self-forged codebook primitive-structure alignment > inherited representation alignment | reversal | **CONFIRMED (revised 2026-09-26) -- WITH UNRESOLVED VARIANCE**: with a CORRECT straight-through VQ, forged alignment 0.693 vs inherited raw 0.674 / embed 0.142 (margin only +0.019, single run each). The earlier FALSIFICATION was an implementation artifact: the straight-through estimator was inverted (values from z_e, gradients into the buffer codes), so the encoder never received quantizer gradients. **Revival lambda sweep (t7_revival_results.json, second run) does NOT match the main run**: lam=0 scores 0.802 -- HIGHER than the main forged 0.693 (two runs of nominally the same setup differ by +0.11; run variance unresolved, multi-seed rerun required). Sweep is NOT flat (0.559-0.820; the commit-message claim "lambda sweep flat" is wrong): lam=10 harms (0.559, recon 10x worse), lam=0 vs 1.0 comparable (0.802 vs 0.820). Transfer: forged codes do not transfer to eta products (main 0.494; revival 0.351; inherited 1.000) -- inherited-favored, consistent across both runs |
| P8 | T0 surface salience | With a unique 40-char surface tag per instance, SD collapses at c~=1 and recovers at mid compression (two-sided window) | c=1 SD stays high (>=0.5) | FALSIFIED (c=1 SD 0.545; surface salience creates a MID-compression interference valley instead) |

Thresholds (15pp, 0.1, 0.15, 3x) are v1; one revision is allowed after the
baseline runs, and revisions must be recorded in this registry.

---

## 2. Testbed tiers

### T0 synthetic families (toy, pure CPU, ~1-10M parameter models)

**Purpose**: make H0 a scannable curve in an environment where structure
labels are mechanically computable.

**Data (two domains, for generality)**:
1. Algebraic identity families: small algebra templates ((a+b)^2,
   distributivity, associativity); surface noise = variable renaming, term
   reordering, equivalent rewrites; structure label = template isomorphism class.
2. Graph families: generation skeletons (tree / cycle / bipartite variants)
   + random relabeling + random edge decoration; structure label =
   isomorphism class (computed mechanically).

**Model & sweep**: small transformer autoencoder / VQ-VAE; bottleneck sweep
(compression c = input information / bottleneck capacity, 2-3 orders of
magnitude); crossed with family count K (2/8/32) and surface-noise strength.

**Metrics**:
- Structure-domination SD: among an anchor's kNN, the fraction
  "same-structure AND different-surface"; surface-domination defined
  symmetrically;
- Clustering ARI (against structure labels vs surface labels).

**Output**: SD-vs-compression curve families; if P1 holds -> law candidate
**L5 (structure-induction window)** enters the MB law system.

### T1 real math objects (CPU, fully self-generated data)

**Purpose**: test H0 on real mathematical structure (P3/P4).

**Data generation (key: everything recomputable locally)**:
- q-expansions: eta products, Eisenstein series,
  j(tau) = q^-1 + 744 + 196884q + ... (mpmath high-precision direct evaluation);
- CM discriminant table: d in the Heegner set + class-number-2 samples,
  j((1+sqrt(-d))/2) at high precision;
- structure labels = discriminant / level / weight / is-CM.

**Baselines**: generic text-embedding model over the q-expansion strings +
uniform random retrieval.

### T2 Ramanujan engine (end-to-end minimal loop, CPU tier)

**Components**:
1. Family generator D1 (an artifact in its own right): d -> valid 1/pi
   series. Implemented per the Borwein reconstruction pipeline: 2F1(1/2,1/2;1;k^2)
   expansion -> singular modulus k_d at the CM point (K'/K=sqrt(d)) ->
   Legendre relations + parameter differentiation produce the (A+Bn) factor
   -> high-precision floats + PSLQ integerization. **Acceptance: reproduce
   the Chudnovsky coefficients (d=163 -> 640320, 13591409, 545140134)**,
   then generate new series for unseen d.
2. Verifier: integer arithmetic + mpmath, 50-digit precision, milliseconds.
3. Proposer: small model or template combinator over a raw-material
   dictionary (q-expansions, binomial coefficients, j-value fragments).
4. Episodic memory + offline recombination: failure neighbourhoods and
   success patterns written in; compression-recombination triggered every N
   steps (reuses FlyMemory design principles; local vector store, the live
   flymemory service is untouched).

**Protocol**: A/B comparison (A = memoryless persistent search; B = with
recombination). Logs align every recombination event with hit events —
for the P5 insight-signature test.

**17->18 test (P6)**: the family generator produces >=18 valid series for
distinct d; freeze 17 as "known", test whether the model ranks the 18th
valid member first in retrieval/proposal distributions.

### T3 (optional, second phase) proof-task transplant

miniF2F small-scale: impasse detection (beam exhaustion / loss plateau) ->
write the impasse state into episodic memory -> offline compression
recombination -> restart search. Criterion: does the proof-rate gain
concentrate on problems requiring cross-domain lemmas?

---

## 3. Deliverables

| ID | Deliverable | Acceptance |
|------|--------|------|
| D1 | Family generator (d -> integer series) | Reproduces the Chudnovsky coefficients + produces >=18 new series |
| D2 | T0 scan curves + L5 candidate law (with registered P1/P2 verdicts) | Reproducible script + one-page conclusion |
| D3 | T2 A/B report + insight-signature analysis | P5 verdict + event logs |
| D4 | 17->18 generalization report | P6 verdict |
| D5 | Everything written back to FlyMemory `research/RESEARCH.md` | Document merge |

---

## 4. Schedule (serial; gate: if a stage's acceptance fails, stop and attribute — never push through)

| Phase | Content | Budget | Gate |
|------|------|------|------|
| Phase 0 (week 1) | Verifier + tests; family-generator prototype (Chudnovsky acceptance first); T0 synthetic-family generation script; text-embedding and uniform baselines | 3-5 work units | D1 acceptance passes |
| Phase 1 (weeks 2-3) | Full T0 sweep (compression x families x noise); P1/P2 verdicts; L5 draft or negative-result attribution | 3-5 overnight batches | P1/P2 concluded |
| Phase 2 (weeks 4-6) | T1 data pipeline + P3/P4; T2 minimal loop (A baseline -> B); P5 | 2-3 weeks | P3-P5 concluded |
| Phase 3 (month 2+) | 17->18 (P6); H2 notation forging (P7); T3 depending on results; write back to RESEARCH.md | elastic | — |

**Quick start (first work unit)**:
1. `validator.py`: 50-digit verification for 1/pi series + self-tests
   against the two known formulas (Ramanujan 9801 / Chudnovsky); ✅ done
2. `family_gen.py` skeleton: mpmath 100-digit j((1+sqrt(-d))/2) and
   singular moduli, PSLQ integerization interface; ✅ done (d=163 anchor
   PASS after the nome-squared bug fix)
3. T0 graph-family generator + canonical (structure-label) computation. ✅ done

---

## 5. Hard discipline (inherited rules, each one hard)

- **Serial**: GPU training / batch scans run serially, never in parallel
  with the flymemory service or other tasks; check memory with
  `python ctypes` before starting (never PowerShell inline — Git Bash
  escaping breaks it);
- T0-T2 are all designed CPU-tier (<=10M params, controlled mpmath
  precision) — never near the 32GB red line;
- Stream large corpora; watchdogs on chained long tasks; never swallow
  exit codes with `tail -1`;
- **Measure first, write second**: register every prediction before
  running; threshold revisions must leave a trail;
- Negative results enter the negative-results chain per house tradition
  (P1 falsified = the structure-induction window does not exist — itself a
  high-value MB-program conclusion);
- The live flymemory library is untouched; the engine uses its own local
  store.

---

## 6. Risks & falsification exits

| Risk | Exit |
|------|------|
| No structure-induction window in T0 | Negative result + attribution (families too shallow? wrong compression objective?) -> adjust the bottleneck objective (add denoising/masking) and rescan once; still nothing => L5 recorded as falsified |
| PSLQ integerization fails in the family generator | Downgrade: numeric series still support the T2 verifier loop; integerization hangs as a separate subproblem |
| T2 hit rate too low for signal | Shrink the space first: restrict proposals from "any d" to "interpolation within known families", confirm loop sensitivity, then open up |
| Baseline too strong (text embedding already clusters) | Conclusion pivots: "structure is readable from the surface" — still valid and interesting; P3 re-judged as "surface sufficiency" |

---

## 7. Coupling with the MB program

- Of the three seams, seam ① directly reuses the MB core question "when
  does compression induce structure"; T0/T1 are its controlled
  experiments; seam ③ reuses FlyMemory's memory design principles; seam ②' s
  codebook experiment borrows FlyPoet's activation-compression setup;
- L5 (structure-induction window) is a law candidate, finalized after
  P1/P2 verdicts per L-series convention;
- The insight signature (P5) is a registered forward prediction;
- All conclusions are written back to the main documents per house
  convention, keeping a single source of truth.
