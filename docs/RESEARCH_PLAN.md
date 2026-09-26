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
| P2 | T0 mixed families | Within-window latent clustering ARI vs structure labels > ARI vs surface labels + 0.1 | no window or reversal | HOLDS (both calibers). v1 caliber (edge-count bins): confirmed in t0_scan. REGISTERED-CALIBER VARIANT CLOSED (p2_registered_variant.py, 2026-09-26): instance downsampling (2 inst/family x 10 draws) makes the registered instance-label ARI well-posed -- ARI_instance ~= 0 at every bottleneck while ARI_struct leads by +0.109..+0.218 (all 8 b, all > 0.1; verdict HOLDS in window). The caliber change is validated, not concealing a failure. See p2_registered_results.json |
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
| P13-v3 | M1 corrected discovery grid | TRUE sequences (p13_deep's H factor was a per-k product, not the cumulative hypergeometric -> surrogate inputs): 15 transforms x b{4,16} x seeds{0,1,2} x 3 readouts (kNN, k-WTA2/4), two-stage hard-example-reweighting AE, PLUS pre-AE raw baselines to separate "transform extracts but AE destroys" from "transform insufficient" | any (transform, cell) exceeding chance 0.368 by >0.15 after selection correction | **CONFIRMED-NEGATIVE (p13_grid.py, 90 cells, 56 min): no config is a discovery.** Best AE cell 9/17=0.529 (identity/norm/ratio_log; best-of-18-selection, not significant); best raw 8/17=0.471 (log_ratio_zf, norm_ratio_log -- the ratio direction, as theory predicts); the AE NEVER lifts separation above its raw input (raw=8 -> AE<=8). Reading: fixed transforms get at most the ratio shape, and the remaining gap to P4's 17/17 is exactly the ENVELOPE-ESTIMATION step ((A+Bk)z^k removal) that no fixed transform performs -- reviewer's nuisance-identification reading confirmed. See p13_grid_results.json |
| P14 | M1 blind factorization | Under nuisance-controlled data (random A,B,z per sample, s the invariant): (a) recon-only AE same-s kNN <= 0.30; (b) DANN (GRL nuisance removal + s-classifier) same-s kNN >= 0.70; (c) family-known hypothesis selection >= 0.90 accuracy | (b) <= 0.35 => even explicit invariance pressure + counterfactual data cannot discover the invariant | **VERDICT IN (2026-09-26): (b) CONFIRMED 0.750 + s-acc 0.883, (c) CONFIRMED 0.975, (a) not supported (recon AE already reaches 0.475).** SUPERVISION SCOPE (review-nuance, 2026-09-26): arm (b) trains with s LABELS (cross-entropy on the s-head) -- it establishes SUPERVISED invariance extraction (labels known -> GRL machinery removes nuisances), not blind factorization; arm (c) knows only the family FORM (no labels, parameters fit by least squares) and reaches 0.975. The blind end is arm (a): plain recon AE partially separates s at 0.475 without any pressure. Review's six-condition spec: I(u;s)up and I(u;A/B/z)down are satisfied BY CONSTRUCTION in (b)'s objective; reconstruction yes; SIMPLICITY PRIOR not formalized (registered limitation). Three-layer map wording: L2 = family-known parameter fitting (0.975) AND label-supervised adversarial removal (0.750); blind representation discovery remains L3/P13 (chance). See p14_results.json |
| P12 | T7 capacity scaling | codes 12->64 sweep: forged-ARI exceeds inherited at codes >= some threshold c*, with the curve shape reported (monotone / threshold / flat) | forged never exceeds inherited | NON-ROBUST (p12_capacity.py, 7 codes x 3 seeds): forged ARI peaks at codes=24 (0.728+-0.060, above inherited 0.674) but falls back at 32/48/64 (0.641/0.560/0.482) -- no threshold c*; over-provisioned capacity degrades alignment (codebook redundancy disperses classes). The P7 "advantage requires redundant capacity" reading is itself falsified at higher capacity |
| P1-tag | M1 surface-salience gradient | tag_len sweep 0/16/32/64: as a pure-noise per-instance tag grows to dominate the input string, same-family kNN holds while same-instance (tag) kNN stays at chance | tag capture dominates at large tag_len (fam kNN collapse or inst kNN >> 0.1) | INVARIANT-ROBUST (p1_taglen_sweep.py, seed 0): at tag_len=64 (tag >2x formula content) family kNN drops only 5.4pp (0.772->0.718) and instance recall rises to just 0.046 vs chance 0.017. Salience capture exists but is second-order; supports L1 -- the latent's organizing axis stays algebraic even under surface-dominated input. See p1_taglen_results.json |
| P15-b | M2 envelope refinement | Close P15's residual gap (per-sample fit error ~0.003 log-level from (A+Bk) vs k^{-3/2} non-orthogonality). REFINEMENT: after the P15 pass-1 envelope fit, re-fit the residual with the generic basis {k, log(k+1)} INTERCEPT-FREE and subtract (iterated 2x), then read out as in P15. Registered rationale: an unrestricted refit (with intercept) is degenerate -- it fits away ALL discrete structure for any data; protecting the per-sample constant level is the minimal non-degenerate iteration, and it is exactly "estimate the k-dependent nuisance, cancel it, keep the level". Alternative refinement REJECTED at registration: reading asymptotic-series coefficients of log-ratios (1/k, 1/k^2, ...) -- analysis shows the nuisance (B/A)^2 lands directly on the 1/k^2 coefficient (up to ~18) and drowns the s-gaps (0.014-0.08); coefficient reading relocates rather than cancels nuisance | refined arm keeps hit@1 >= 0.90 AND closes the ARI leg (>= 0.6, target ~oracle) on the TRUE family; report adjacent-class gap compression in pooled-sigma | **VERDICT IN (2026-09-27): FALSIFIED as registered -- the refinement is mathematically near-vacuous.** Pass-1 OLS residual is already orthogonal to its basis; refitting with {k, log(k+1)} (a subset of the same span minus intercept) removes nothing new (direct evidence: refined x1 == refined x2 exactly, idempotent; hit@1 unchanged 0.946). ARI leg NOT closed: 0.325 -> 0.240 (true family, row-normalized), 0.361 -> -0.002 (ratio family); raw-scale kmeans unchanged 0.325. Audit + diagnostic located the TRUE obstruction: adjacent-class ladder gaps stay ~1 sigma (0.85/1.04/1.46 -> 0.93/1.16/1.60 pooled-sigma, no compression). SVD rank-1 axis (98.4% of variance) has strictly ordered class means (-0.184/-0.071/+0.037/+0.218) but sample scatter (0.11-0.17) exceeds class gaps (~0.11). The scatter is z-MODULATED FIT BIAS: z spans 9x (0.05-0.45), so the per-sample OLS effective k-weighting varies with z and the level estimate's bias lands on the SAME axis as the invariant. No fixed-basis per-sample refit (same span) can remove it; population SVD cannot either (bias is on the signal axis). Obstruction recorded; candidate route registered as P15-c (ratio-domain reconstruction closes the z channel exactly). See p15b_refine_results.json |
| P15-c | M2 ratio-domain reconstruction | Close the P15-b-identified obstruction (z-modulated per-sample fit bias on the invariant's own axis). Blind per sample: rho_k = log(c_{k+1}/c_k); fit rho ~ b0 + b1/(k+1) + b2/(k+1)^2 + b3/(k+1)^3 (OLS, 23 points); reconstruct log-envelope by cumulating the fitted ratio function (E_0=0, E_{k+1}=E_k+fit_k) and take u = |c|/exp(E). KEY: z^k becomes EXACTLY the intercept (b0 = log z) -- the z channel cannot leak into level bias, unlike the direct log-domain fit where z modulates the effective k-weighting. Readout identical to P15 (row-normalized kNN hit@1/frac3 + kmeans ARI + ladder-gap diagnostic). | ARI >= 0.6 with hit@1 >= 0.90 on the TRUE family => CONFIRMED (exact envelope identification mechanized; the ladder is resolved globally); ARI in [0.325, 0.6) => PARTIAL (bias reduced, obstruction partially lifted); ARI <= 0.325 => NEGATIVE (z channel was not the operative bias). Health: shuffled ~ chance. | **VERDICT IN (2026-09-27): NEGATIVE on the registered TRUE family (ARI 0.087 <= 0.325 band; hit@1 0.838, ladder gaps degraded 0.85/1.04/1.46 -> 0.40/0.33/0.77 pooled-sigma); SPLIT by family -- CONFIRMED (1.000/1.000) on the ratio-form transfer family.** Mechanism: the ratio domain is family-ADAPTIVE. For the ratio-form family (R_s -> 1 fast) the cumulated asymptotic fit reconstructs (A+Bk)z^k almost exactly, exposing the s-content perfectly. For the TRUE family (H_s ~ C_s k^-1.5, a strong power law) the universal -1.5/k term collides with the (A+Bk) log-ratio's 1/(k+c) shape; small-c (B/A large) samples suffer large truncation error that the cumulation amplifies into per-sample multiplicative distortion -- worse than the direct fit. CONSEQUENCE (program-level): the two generic envelope schemes are COMPLEMENTARY, each near-perfect on one family and degrading on the other (direct: 0.946/0.325 vs ratio: 0.838/0.087 on true; 0.992/0.361 vs 1.000/1.000 on ratio-form); neither dominates. The L3 remainder 'decomposition choice' is now CONCRETE and one level up: not which transform, but WHICH ENVELOPE SCHEME -- and selecting it blind per dataset (unsupervised scheme selection) is the registered next step P15-d. See p15c_ratio_results.json |
| P15-d | M3 blind scheme selection | P15-c showed the two generic envelope schemes are complementary (direct: 0.946/0.325 on true vs 0.992/0.361 on ratio; ratio-domain: 0.838/0.087 vs 1.000/1.000). Question: can the SCHEME be selected per dataset WITHOUT labels? Registered criterion (label-free): run kmeans(k=4) on each candidate representation (raw / direct-envelope / ratio-envelope), score each clustering by cosine SILHOUETTE, select the scheme with the highest silhouette; only then compare the selected scheme's hit@1/ARI against labels (evaluation-only). Diagnostic (registered alongside): concatenation ensemble of the two envelope representations (row-normalized, equal weight) -- does combining beat selecting? | CONFIRMED if silhouette selection picks the higher-ARI scheme on BOTH families (true -> direct, ratio-form -> ratio); PARTIAL if one; NEGATIVE if neither. Ensemble reported as diagnostic. | **VERDICT IN (2026-09-27): PARTIAL (1/2).** Ratio-form family: silhouette selects ratio-domain (0.9870 vs 0.6463/0.7510) -- CORRECT, reads out 1.000/1.000. TRUE family: silhouette selects RAW over direct by a 0.0009 margin (0.7178 vs 0.7169) -- WRONG. FAILURE MODE (registered insight): the selection criterion itself falls into the salience trap -- silhouette rewards the clean clustering of the DOMINANT variable (z-decay blob structure), not alignment with the invariant; this is P9's lesson (prediction objectives learn log|z|) resurrected one level up at the meta-selection layer. Ensemble diagnostic: true family 0.946/0.325 (= direct, which dominates the concatenation); ratio family 1.000/0.451 (better than direct alone, worse than ratio alone). PROGRAM-LEVEL close of the P15 arc: representation mechanisms are salience-robust (P1-tag), but LABEL-FREE SELECTION criteria are not; distinguishing invariant-structure from salient-structure by purely internal criteria is now the sharpest open statement of the remaining gap. See p15d_select_results.json |
| P15-e | M2 2D confound regression-out | Close the ARI leg by removing the P15-b obstruction explicitly. Prior probes: 1D oracle-z regression-out on the direct representation did NOT help (ARI 0.325->0.321, unregistered probe) => bias is NOT linear in z alone; hypothesis: bias = f(z, B/A) (2D, since both modulate the pass-1 OLS effective k-weighting). METHOD: from the sample's OWN fits (blind), take ẑ = exp(a1) from the direct log-domain fit and B/A proxy from the ratio-domain fit's b1 coefficient; regress the direct-envelope representation per-coordinate on confound columns [1, ẑ, b1] and [1, ẑ, b1, ẑ², ẑ·b1, b1²]; re-cluster. Validity: in counterfactual data (z, B/A) are INDEPENDENT of class by construction, so the confound subspace is class-free and its removal cannot destroy class information except accidentally (random-direction control registered). Arms: baseline / linear-2D / quadratic-2D / ORACLE-confound (true z, true B/A) / random-2D control. | CONFIRMED if any blind arm reaches ARI >= 0.6 with hit@1 >= 0.90; PARTIAL if ARI in (0.325, 0.6); NEGATIVE if all blind arms <= 0.325. Oracle arm reports the identification ceiling; random control must stay ~baseline. | **VERDICT IN (2026-09-27 01:55): mechanism FALSIFIED -- the obstruction is NOT a low-dimensional (z, B/A) confound.** TRUE family: baseline 0.325, linear2D 0.360, quad2D 0.179 (destructive), oracle-2D 0.395, RANDOM-2D control 0.379 -- the random control matches oracle and blind removal within noise, so any apparent gain is perturbation noise, not confound removal; quad columns eat signal. Ratio family: regression-out actively destroys (0.361 -> -0.001). CONCLUSION: the per-sample bias is IDIOSYNCRATIC (not expressible as a low-dim function of the fit parameters); representation-side cleanup is exhausted; kNN 0.946 shows the information is present -- the ARI leg requires a ladder-shape-aware (mild-prior) global readout or an entirely different clustering principle, not more nuisance regression. See p15e_confound_results.json |
| P15-f | M3 salience-corrected selection | Fix P15-d's salience trap. Registered criterion: for each candidate representation, remove the TOP-1 PRINCIPAL COMPONENT (of the row-normalized representation), re-run kmeans(k=4), score by cosine silhouette; select the scheme by post-removal silhouette. Rationale: salient structure (z-decay blob) is dominated by one variance axis; invariant structure is distributed and survives its removal. Bootstrap (200 resamples) CI on the silhouette difference between the top-2 schemes. Candidates: raw / direct / ratio (same as P15-d). | CONFIRMED if corrected selection picks the higher-ARI scheme on BOTH families with the bootstrap CI excluding zero on the decisive margin; PARTIAL if correct selection but CI includes zero; NEGATIVE if any wrong selection. | **VERDICT IN (2026-09-27 02:10): NEGATIVE per bands -- and the failure mode completes a theorem-shaped statement of the gap.** TRUE family: corrected selection flips to the RIGHT pick (ratio, CI [+0.0051,+0.1368] excl 0) and PC1 removal itself lifts ratio's ARI 0.087 -> 0.394 (invariant subordinate: discounting the dominant axis helps). Ratio family: corrected selection flips the RIGHT naive pick to WRONG (direct over ratio, CI excl 0) and PC1 removal destroys the perfect clustering (1.000 -> 0.291) -- because there the invariant IS the dominant axis (regime: invariant-dominant). REGIME THEOREM (registered reading): the invariant may live on the dominant variance axis or in subordinate directions, family-dependently; SALIENCE CORRECTION IS ONLY VALID IN ONE REGIME, and the representation's internal geometry does not encode which regime holds. With P15-d (naive) + P15-e (confound regression) + P15-f (salience correction), all three internal-criterion families have now failed with distinct mechanisms: salience capture, idiosyncratic bias, regime ambiguity. Selecting or cleaning representations by purely internal criteria is closed as a route; the remaining openings are external information (counterfactual perturbation access, world models) or mild structural priors (e.g., known class count + ladder shape). See p15f_select_results.json |
| D1-eta | T5 eta-quotient route | LITERATURE.md diagnosis: (A,B,C) live in level-6 eta quotients j6B..j6E at CM points (+Conway-Norton linear relation j6A-j6B-j6C-j6D+2j6E=22), NOT in level-1 j -- explaining D1's 0/27. MECHANIZE: (i) validate eta machinery by reproducing the literature worked values (j6C(sqrt(-1/3))=32, j6D(sqrt(-1/2))=81, j6A(sqrt(-17/6))=39200, linear relation at generic tau); (ii) sweep tau=sqrt(-d/6) (+ shifted forms) over a Heegner-style d grid, recognize algebraic values of all five functions (rational/low-degree via PSLQ at 50 digits); (iii) for algebraic hits, attempt recovery of our known s=6 members (eq33: 1,11,z=4/125; eq34: 8,133,z=(4/85)^3) from the function values -- the pure-hypergeometric subcase. | GATE (i) must reproduce all documented values at 1e-30. FIND bar (ii): count of algebraic hits vs total cells. RECOVERY bar (iii): both known members' (A,B,z) recovered mechanically => D1 progressed from 0/27 to mechanized-known-members; novel-series generation explicitly OUT OF SCOPE tonight (needs refined-sequence theory, registered limitation). | pre-run registration (2026-09-27 01:55); verdict pending |
| P15 | M2 blind envelope removal | Review-route test ("the missing step is envelope estimation, not another fixed transform"): counterfactual data (TRUE cumulative H_s, random A,B,z per sample, no s labels in training). Each sample is fitted INDEPENDENTLY with a generic 3-parameter log-domain envelope log\|c\| ~ a0 + a1*k + a2*log(k+1) (exponential decay + linear envelope + power law -- no H_s knowledge, no s labels); residual u = \|c\|/envelope is the representation. Arms: raw baseline / blind residual / blind-residual AE / ORACLE nuisance removal (exact (A+Bk)z^k, no H_s) / shuffled control | blind residual same-s hit@1 >= 0.70 AND kmeans ARI >= 0.6 => envelope estimation MECHANIZES the missing step (L3 opens); 0.45-0.70 => PARTIAL (signal exposed, fit noise leaks); <= 0.45 => NEGATIVE. Health: oracle >= 0.95, shuffled ~ chance. | **VERDICT IN (2026-09-27): PARTIAL by the letter -- hit@1 leg CONFIRMED, ARI leg not met -- but the hit@1 leg is the decisive one.** TRUE family: blind hit@1 0.946 (chance 0.247; P13 fixed-transform ceiling 0.529 demolished), frac3 0.903; ratio-family 0.992. Oracle 1.000/ARI 1.000 (health ok; first-run oracle ARI=-0.000 was a kmeans-scale artifact, fixed by row-normalizing reps for kmeans). Shuffled 0.233 ~ chance. ARI leg 0.325: diagnostic shows the invariant after blind cancellation sits on a 1-D residual-level ladder (log C_s monotone: 0.0066/0.0088/0.0116/0.0170, within-class std ~0.003 from per-sample envelope fit error) with adjacent-class gaps 0.8-1.3 sigma -- kmeans cannot cut overlapping ladder intervals (even 1-D kmeans 0.276); cosine-kNN resolves them via residual shape. blind_AE does not lift over blind (0.875), consistent with P13-v3. READING: the review's missing step IS mechanizable by a generic statistical decomposition; the L3 remainder decomposes into (i) exact envelope identification (open -- the 0.946 vs oracle 1.000 gap is fit error from (A+Bk) and k^{-3/2} non-orthogonality) and (ii) global readout robust to residual leakage. See p15_envelope_results.json |

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
