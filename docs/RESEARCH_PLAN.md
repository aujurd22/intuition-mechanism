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
| P2 | T0 mixed families | Within-window latent clustering ARI vs structure labels > ARI vs surface labels + 0.1 | no window or reversal | rides on P1; REVIEW NOTE (2026-09-26): the surface-ARI actually measured uses edge-count quantile bins, not the registered instance labels (instance count >> clusters degenerates the registered form) -- kou-jing change registered here; the registered-definition variant remains open |
| P3 | T1 math objects | Compression representation of q-expansions clusters by arithmetic invariant (CM disc / level / weight) with ARI > text-embedding baseline + 0.15 | ties or worse | PARTIAL (holds on shape objects; fails on digit-identity objects — representation must match invariant type) |
| P4 | T1 retrieval | With 17 known Ramanujan series as anchors, top-k retrieval of same-family candidates > uniform and text-embedding baselines | ties | **FOUR-TIER VERDICT, REVISED TWICE (external review + p4_clean v3, 2026-09-26)**: the v2 Tier C "near-degenerate constant" reading is RETRACTED -- it compared a NORMALIZED measured R_0 against UNNORMALIZED theoretical constants and misaligned the template by one slot, while c_0 pollution corrupted R_0 for the s=4 family. Corrected numbers: Tier A (blind raw) and A' (de-leaked embed) remain at chance (hit@1 5/17 vs 0.368); **Tier B (ratio-normalized, c0-polluted R_0 dropped) hit@1 17/17**; **Tier C (template matching, aligned + normalized) 17/17**; **c_s = (1/s)(1-1/s) extracted EXACTLY from c_1/c_0 on the c0-free series (7/7: 0.25, 2/9, 5/36)**. Verdict: the signature is fully recoverable once the invariant normalization is applied -- from both the constant and the R_k shape; blind surface retrieval stays at chance. The open question moves from recognition (solved, given the invariant) to DISCOVERY of the normalization itself |
| P5 | T2 engine A/B | Time to first valid formula with recombination <= 1/2 of memoryless baseline, and "hit within 1 step of recombination" rate > 3x background | no advantage | CONFIRMED on the first-hit measurement (v2 hard space + seeded start: first fresh hit 7.75x faster). REVIEW NOTE (2026-09-26): the post-recombination hit rate 1.0 is a CONSTRUCTIVE property (multiplying both sides of a known identity by a basis element preserves proportionality), not an independent measurement; the measured quantity is the A-arm baseline 0.128. A non-constructive recombination operator is required before the insight-signature rate claim can be re-registered |
| P6 | 17->18 generalization | Given 17 in-family samples, the model's acceptance/ranking hit rate for an 18th valid member > uniform baseline significantly | ties | FIRST VERDICT (p6_generalize.py, 2026-09-26): CONFIRMED -- the 3 mechanically generated h=1 members (d=19/43/67) rank 1/19 for their true signature in BOTH the blind-raw and given-invariant tiers (3/3 hit@1, mean rank 1.0 vs chance 6.67; the mechanical (A,B,z) magnitudes carry family signal even blind). Full verdict remains open on the h=2 and positive-z sides. Previously: MECHANICALLY UNBLOCKED for the h=1 sub-family: d1_generalize.py v2 produces FOUR integer series (d=19, 43, 67, 163 -- the four Heegner d with j a negative perfect cube), each independently verified at the 50-digit gate; with Ramanujan 1914 eq 28-44 the extended family now has 21 verified members. NOTE (review, 2026-09-26): the v1 "0/27, A all converge to 13591409" negative result was a pipeline artifact (hardcoded BASE=640320; fixed terms) -- retracted and superseded by the corrected run. The h=2 discriminants (15, 35, 51, ...) and positive-j d (1, 2, 20, ...) remain outside the current pipeline form (graded trace forms / positive-z family) -- P6 full verdict still open |
| P7 | H2 notation | Self-forged codebook primitive-structure alignment > inherited representation alignment | reversal | **REVISED after multi-seed rerun (t7_multiseed.py, 3 seeds x codes {8,12,16,24})**: matched budget (12 codes/12 classes) forged 0.620+-0.083 vs inherited 0.674 -- PARITY within seed noise (the single-run 0.693 was at the favorable end; the 0.802 revival run at the other). Over-provisioned codes=24 reaches 0.713+-0.038, slightly above inherited; codes=8 collapses (0.272). Verdict: forged notation MATCHES but does not EXCEED inherited at matched budget; the advantage requires redundant capacity. Run-variance RESOLVED by the multi-seed artifact (t7_multiseed_results.json) |
| P8 | T0 surface salience | With a unique 40-char surface tag per instance, SD collapses at c~=1 and recovers at mid compression (two-sided window) | c=1 SD stays high (>=0.5) | FALSIFIED (c=1 SD 0.545; surface salience creates a MID-compression interference valley instead) |
| P9 | T0 prediction objective | A next-coefficient predictor's latent clusters by signature s (ARI > surface-magnitude baseline + 0.15) | latent clusters by log abs(z) magnitude instead; PCA-1 ~ 0.999 with log abs(z); cross-signature magnitude pairs co-cluster | NOT-SUPPORTED (f193d36: latent PCA-1 correlates 0.999 with log abs(z); ARI vs s = -0.082 vs surface baselines -0.114 / |c0| bins 0.420; R-shape control ARI 1.000 -- pipeline healthy) |
| P10 | T0 positive-z construction | Level-n singular-modulus products (beta_n(1-beta_n) x rational q) reproduce a positive-z family series | zero novel integer series in the 1720-cell scan (9 pos d x 6 levels x 4 sigs x 8 prefactors); health checks reproduce eq28/eq29 exactly at 1e-81 | BOUNDARY-CONFIRMED (2e534dc: the positive-z family needs the modular equation's own algebraic solutions, not singular-moduli products; consistent with eq30's nested quartic z) |
| P11 | T2 non-constructive recombination | Cross/Swap/Power-Mix operators over two DISTINCT hits produce new proportional pairs above background | hit rate <= background | NOT-SUPPORTED (b5fcb65: cross-level recombination between distinct hits is structurally impossible in the current single-family space -- all 49/49 cross-pairs fail the exact verifier; the honest result is that the T2 space has exactly ONE relation family, so non-constructive recombination has no substrate. A multi-family space is required for a real P11 test) |
| P9 | T4 prediction objective | Next-coefficient prediction (given c_0..c_k predict c_{k+1}) on the 21 verified members: latent/predictor state clusters by signature s (ARI vs s > surface-magnitude baseline + 0.15); the predictor internalizes the ratio operator | clusters by surface magnitude or ties | NOT-SUPPORTED (p9_predict.py, LOSO 20-fold, seed 0): ARI(latent, s) = -0.082 vs surface baselines (input -0.114, |c0| bins 0.420) + 0.15; R-shape invariant control 1.000 (pipeline healthy); PCA-1 of latent correlates 0.999 with log|z| -- the prediction objective's variance is dominated by the log|z| slope, the signature lives in the small residual the predictor never needs. Negative result registered; the "invariant discovery" is NOT induced by a plain next-coefficient objective |
| P10 | T5 positive-z level-n | Construct z for the positive family via modular-equation level-n algebra (eq30 z = 64*((3-sqrt5)/16)^4 as the level-4 template): each level's z -> integer (A,B,M) via PSLQ, gated at 1e-25 | no level beyond the known instances yields integer relations | BOUNDARY-CONFIRMED (p10_leveln.py): health checks reproduce eq28 (z=1/4, (1,6,4)) and eq29 (z=1/64, (5,42,16)) at pi_err 1e-81 -- the level-n K/K=n*sqrt(d) construction is sound; the scan (9 d x 6 levels x 4 signatures x 8 q-prefactors, 1720 cells) finds ZERO novel series. Positive-z z is not a rational multiple of beta_n(1-beta_n); it needs the modular equation's own algebraic solutions (eq30: nested quartic). Inspiration residue double-confirmed |
| P11 | T2 P5 v2 | Non-constructive cross-hit recombination operator (interpolate/exchange fragments between two DISTINCT hits, verifier decides): post-recombination hit rate > 3x background rate | no advantage | NOT-SUPPORTED (p11_recomb.py): first MECHANISM FINDING -- all multiplicative recombination operators (CROSS/SWAP/POWER-MIX) are constructive in this ring (rate 1.0; low-weight form spaces are 1-dimensional), reproducing the v1 flaw in a new guise. The genuinely non-constructive ADDITIVE-MIX (m1+m2 vs n1+n2, hits iff the two proportionality constants agree) measures post_rate 0.045 over 2032 events vs background 0.156 -- BELOW background (3.5x worse). Insight-signature recombination does not exist in the Eisenstein ring at this scale |
| P14 | M1 blind factorization | Under nuisance-controlled data (random A,B,z per sample, s the invariant): (a) recon-only AE same-s kNN <= 0.30; (b) DANN (GRL nuisance removal + s-classifier) same-s kNN >= 0.70; (c) family-known hypothesis selection >= 0.90 accuracy | (b) <= 0.35 => even explicit invariance pressure + counterfactual data cannot discover the invariant | **VERDICT IN (2026-09-26): (b) CONFIRMED 0.750 + s-acc 0.883, (c) CONFIRMED 0.975, (a) not supported (recon AE already reaches 0.475).** KEY RESULT: with counterfactual nuisance data (240 samples, independent random A/B/z per sample) explicit invariance pressure (DANN/GRL) DOES recover the signature at kNN 0.750, and hypothesis-selection over the known family reaches 0.975. The 'machine discovers nuisance removal' level is mechanizable. The remaining un-mechanized step is only the OUTERMOST level: discovering the operator family itself (P13's negative). See p14_results.json |
| P12 | T7 capacity scaling | codes 12->64 sweep: forged-ARI exceeds inherited at codes >= some threshold c*, with the curve shape reported (monotone / threshold / flat) | forged never exceeds inherited | NON-ROBUST (p12_capacity.py, 7 codes x 3 seeds): forged ARI peaks at codes=24 (0.728+-0.060, above inherited 0.674) but falls back at 32/48/64 (0.641/0.560/0.482) -- no threshold c*; over-provisioned capacity degrades alignment (codebook redundancy disperses classes). The P7 "advantage requires redundant capacity" reading is itself falsified at higher capacity |

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
