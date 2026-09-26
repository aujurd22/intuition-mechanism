# LITERATURE — theoretical anchors for the Mushroom-Body Program / Intuition-Mechanism track

Gathered 2026-09-27 overnight sweep. Purpose: ground the program's empirical
findings in formal theory, and name precisely the gap D1 must cross.

## 1. Math axis — where Ramanujan–Sato (A, B, z) actually come from

**The construction** (level 6, the level of our 17 series):

- Five McKay–Thompson-type modular functions with EXPLICIT eta-quotient
  forms (q = e^{2πiτ}):
  - j6B = (η(2τ)η(3τ)/η(τ)η(6τ))^12 = 1/q + 12 + 78q + …
  - j6C = (η(τ)η(3τ)/η(2τ)η(6τ))^6  = 1/q − 6 + 15q − …
  - j6D = (η(τ)η(2τ)/η(3τ)η(6τ))^4  = 1/q − 4 − 2q + …
  - j6E = (η(2τ)η³(3τ)/η(τ)η³(6τ))^3 = 1/q + 3 + 6q + …
  - j6A defined via (j6B^½ − j6B^−½)² = (j6C^½ + 8/j6C^½)² = (j6D^½ + 9/j6D^½)² − 4
- Conway–Norton linear relation: j6A − j6B − j6C − j6D + 2j6E = 22.
- The series triples arise from SPECIAL VALUES at CM points:
  Δ = j6A(√(−17/6)) = 39200 gives five formulas with (A,B) ∝ (11k+53) and
  Δ±4, Δ±32 (the shifts come from the linear relation); j6B(√(−5/6)) = φ¹²,
  j6C(√(−1/3)) = 32, j6D(√(−1/2)) = 81.

**The gap we must cross, now precisely named** (Wikipedia, level-6 article):
"a fully general closed-form algorithm for z(d) or (A,B,C) at arbitrary
discriminant d" is NOT in the literature — worked examples only.  Our D1
scan (0/27) used level-1 j alone; the parameter lives in level-6 eta
quotients.  This converts D1's negative from "unexplained failure" to
"wrong object attacked".

**Key references:**
- Chan, Chan, Liu (2004), "Domb's numbers and Ramanujan–Sato type series
  for 1/π", Adv. Math. 186, 396–410. PDF:
  https://mrc.sdu.edu.cn/ziliao/40.pdf
- Sato (2002), "Apéry numbers and Ramanujan's series for 1/π" — first
  results above level 4.
- Chan, Tanigawa, Yang, Zudilin (2011), Adv. Math. — level 6A.
- Chan & Verrill (2009), Math. Res. Lett. — Apéry / Almkvist–Zudilin (6D).
- Chan & Cooper (2012), Math. Proc. Camb. Phil. Soc. — general Γ₀(n)
  approach.
- Cooper (2015), "Holonomic alchemy and series for 1/π",
  https://arxiv.org/abs/1512.04608 — constructs level-6 Z, X from Dedekind
  eta; proves conjectural series.
- Zudilin (2007), "Ramanujan-type formulae for 1/π: A second wind?",
  https://arxiv.org/abs/0712.1332 — survey; modular forms of level 6 via
  eta identities (Borwein–Borwein framework).
- Huber — level 17 Ramanujan–Sato series,
  https://faculty.utrgv.edu/timothy.huber/research/17.pdf
- Hemmecke (2026), "Computer-assisted construction of Ramanujan–Sato
  series for 1/π", Ramanujan J.,
  https://link.springer.com/article/10.1007/s11139-026-01352-2 — the
  algorithmic-construction state of the art. Our differentiation: Hemmecke
  mechanizes construction WITH the modular-forms knowledge given; our
  program asks whether the route can be found by a learning system without
  it (P13/P15 results say: not by generic machinery alone).
- Conway & Norton (1979), "Monstrous Moonshine" — origin of the linear
  relations among McKay–Thompson series.

## 2. Theory axis — formal anchors for "what to keep"

- **Kolmogorov structure function / algorithmic sufficient statistic.**
  Vereshchagin & Vitányi (2004), "Kolmogorov's Structure Functions and
  Model Selection", IEEE Trans. IT 50(12), 3265–3290.
  https://arxiv.org/abs/cs/0204037 — for an INDIVIDUAL object, the
  structure function h_x(α) quantifies the model-complexity vs
  remaining-noise tradeoff; the algorithmic sufficient statistic is the
  formal answer to "when you cannot keep everything, what to keep".
  This is the formal twin of the program's founding question. Our L1–L3
  ladder is an empirical instantiation: the invariant s is the "meaningful
  information" at the compression levels we probed; A, B, z are the
  "noise" (in the algorithmic-statistics sense: recoverable from the
  model, not from the structure).
- **Ancillarity (Fisher).** Ghosh & Reid (2010), "Ancillary statistics: a
  review", http://utstat.toronto.edu/reid/research/A20n41.pdf — statistics
  whose distribution does not depend on the parameter of interest; the
  classical formalization of nuisance information. Our (A, B, z) are
  ancillary-in-reverse: they are the parameters of no interest. Fisher's
  conditioning argument (recover information by conditioning on the
  ancillary) is the classical analogue of our Tier-B normalization.
- **IRM critique.** Rosenfeld, Ravikumar, Risteski (ICLR 2021), "The Risks
  of Invariant Risk Minimization",
  https://arxiv.org/abs/2010.05761 — invariance constraints do NOT
  identify the causal/invariant predictor; spurious invariants abound
  unless strong external assumptions hold. Our regime theorem (P15-f) is
  the sequence-level microcosm: the invariant may be dominant or
  subordinate, and internal geometry cannot tell which.
- **Nonlinear ICA identifiability.** "On the Identifiability of Nonlinear
  ICA: Sparsity and Beyond" (2024),
  https://arxiv.org/abs/2406.02542 ; Minimal Change Principle (Kong et
  al., NeurIPS 2024); Independent Mechanism Analysis (IMA) principle —
  content/style (invariant/nuisance) separation is identifiable ONLY under
  external assumptions (mechanism sparsity, environment diversity).
  Matches our closure result: P15-d/e/f show all purely internal criteria
  fail with distinct mechanisms.
- **Information bottleneck** (Tishby et al.) — compression vs relevant
  information tradeoff; the probabilistic ancestor of the structure
  function view; connects to L3 (phase-transition law) via the compression
  axis.
- **DANN/GRL** (Ganin et al.) — the L2 mechanism (used in P14 arm b with
  the registered supervision caveat).

## 2b. Neighbouring field — ML symmetry/discovery (added 2026-09-27 night)

- **SymmetryGAN** (Thaler, Phys. Rev. D 2022) — adversarial
  unsupervised symmetry discovery;
  https://jthaler.net/olympus/files/2022/03/symmetrygan.pdf
- **Liu & Tegmark (2022), "Machine Learning Hidden Symmetries"** —
  symmetries that become manifest only in a LEARNED coordinate system;
  closest ML analogue to our envelope-removal (the right coordinates
  reveal the invariant).  Difference: their method needs the symmetry
  to exist as an exact transformation of a scalar observable; our
  invariant is statistical (a class signal), not a pointwise symmetry.
- **LieAugmenter (2026)** — symmetry discovery as learning
  task-dependent augmentations; assumes a task loss (labels) — outside
  our L3 blind setting, useful as L2 comparison.
- **Ramanujan Machine** (Technion) — exhaustive computer search over
  formula spaces producing new constants formulas; the canonical
  "computer discovery" project.  Differentiation: massive compute over
  a HUMAN-DESIGNED ansatz + post-hoc proof; our program measures which
  levels of the discovery path need that ansatz (P13/P15) — the two
  are complementary, and our testbed could benchmark such searchers.
- **WZ-method line** — Guillera's WZ proofs; "analogues of WZ seeds and
  Ramanujan-type 1/π series" (arXiv 2026-07): the proof side of
  discovery; registered as the natural partner for candidate series
  our pipeline might one day generate.
- **Bhat & Sinha (Dec 2025)** — Ramanujan 1/π series linked to
  logarithmic conformal field theories: a deeper physical substrate
  for why signature-kernels are modular; candidate explanation for the
  Γ-constant axis (P16).
- **Galois groups of Apéry-like sequences mod p** (Nov 2025) —
  computational structure of exactly the Domb/AZ sequences behind
  level-6 Ramanujan–Sato; possible invariants for a future testbed
  round.

## 5. Observed-domain map (where our results sit)

```
 algorithmic statistics (KSF)          theory of "what to keep"
 Fisher ancillarity                    theory of nuisance
 IRM critique / nonlinear ICA          invariance ≠ identifiability
 ML symmetry discovery                 needs labels/priors (L2)
 Ramanujan Machine / WZ / Hemmecke     search WITH human ansatz (L1-L2)
 ─────────────────────────────────────────────────────────────────
 THIS PROGRAM: L1/L2 mechanized, L3 gap measured experimentally,
 regime theorem, complementary schemes, Γ-axis proposition.
```


## 3. Mapping table — what the theory gives us, what is ours

| Program statement | Formal anchor | Status |
|---|---|---|
| "What to keep under compression" | Algorithmic sufficient statistic / KSF | language borrowed; our L1–L3 = empirical instantiation on a math family |
| nuisance (A,B,z) | ancillary statistics (inverted reading) | language borrowed |
| L2 "invariance pressure mechanizes removal" | DANN; IRM objective | ours: measured 0.750/0.975 + supervision caveat |
| P15-f regime theorem | Rosenfeld's spurious-invariant critique | OURS as empirical microcosm; theory predicts non-identifiability, we give the 2-regime mechanism |
| "internal criteria fail 3 ways" | nonlinear-ICA identifiability (needs external assumptions) | OURS as a closed experimental demonstration |
| D1 0/27 (j alone insufficient) | level-6 eta-quotient construction (Chan school) | OURS as diagnosis; eta route = next experiment (D1-eta) |
| Γ-product ladder (log C_s = −log Γ(1/2)Γ(1/s)Γ(1−1/s)) | Pochhammer asymptotics | ours to state as a proposition; confusability prediction testable |

## 4. Next experiments this motivates

- **D1-eta**: mechanize j6B..j6E at CM points τ_d for our 27-d grid;
  recognize algebraic values; generate (A,B,z) via the linear-relation
  shifts; verify against the 50-digit gate. Falsifies/complicates Hemmecke-style
  "algorithmic" construction by asking how much is search vs knowledge.
- **LLM baseline** on the same testbed (memory vs mechanism discrimination).
- **Γ-proposition + confusability matrix** (cheap, closes the theory loop).
