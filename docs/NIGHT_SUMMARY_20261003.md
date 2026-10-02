# Overnight Session Summary — 2026-10-02/03

HEAD at wrap: 3af42ef (+ part4 correction d0c16e3). All pushed.

## Arc of the night

### P185 — landing-field structure of P^12 (math line)
- **s_d = c_d · d with c_d ∈ {1,2,3}**: the P135 open core (uniform rule for
  the support coordinate) compresses to 2 bits per row. The candidate set is
  theorem-level from the Hecke genus-field structure (real quadratic subfields
  of Gen(-24d): {√2, √d, √2d} for d ≡ 1 mod 4; {√6, √2d, √3d} for d ≡ 3 mod 4).
- **Congruence conjecture (4/4 on testable rows)**: c_d = 2 iff d ≡ 2 mod 3;
  else c_d = 1 (d ≡ 1 mod 4) / 3 (d ≡ 3 mod 4) — a genus-character evaluation.
- **Universal genus descent verified**: 18/18 primes through d=67 (residual-
  checked PSLQ). Quadraticity is six-row-only (12 new primes all non-quadratic);
  generic primes span the full quartic genus real part. The P115 descent step
  is vindicated; remaining six-row content = stabilizer collapse (P89 target).
- **Coefficient meter**: genus-coordinate sizes separate rows by 15 orders of
  magnitude (six rows 1e0-1e7 vs generic ~1e22). Intermediates {11, 23, 47, 83}
  unpredicted by h, class-group structure, or d mod 12 (P185-b, open).
- Protocol hardening: PSLQ residual verification + adaptive maxcoeff (two
  silent-artifact classes caught: default maxsteps → None; maxcoeff 1e20 →
  false non-descent at true 1e22). Naive orbit evaluation f(α_x) withdrawn
  (twisted, not conjugate — needs the Schertz coprime-transport lemma).

### P186 — the Arena math-track plateau was a chunking bug (judgment line)
- Error anatomy: row recall 28-39% vs non-row rejection 83-91%, errors
  IDENTICAL across 3 models × 3 seeds — measurement-bug signature.
- Root cause: math was the only track with a static all-probes apply header;
  every chunk call resent the full 32-probe list; the parser zipped the first
  len(chunk) answers onto the next chunk's items.
- Smoking gun: perfect-model simulation caps the track at 84.4% with forced
  errors exactly at the observed positions (d=7, 5, 1, 13 missed; 991 FP).
- Corrected runs: 94-100% accuracy, row recall 6/6. API surface irrelevant.
- Retractions/corrections: P152/P153/P154 "math-resistant 76-79% = shrinking-
  law floor" leg retracted; benchmark spec bumped to v1.2; p153_v2_mega.py
  fixed; DEEP_STRUCTURES_part4 SCR citation annotated. Bug class audited
  repo-wide: exactly one instance (p169/p169b use single-probe calls, clean).

## Meta-lessons registered
1. Identical errors across models = measurement bug, not model limitation
   (model noise never replicates exactly).
2. Every "unsaturated plateau" claim needs a perfect-model misalignment/
   ceiling simulation as a control arm before it enters the registry.
3. PSLQ outputs are never evidence without an explicit residual check;
   search bounds (maxcoeff/maxsteps/dps) must grow until the verdict
   stabilizes (P160 protocol generalized).

## Open items for next session
- c_d congruence rule: proof via Shimura-reciprocity multiplier computation
  (Schertz Prop 2 style) — the 2-bit table layer's mechanism.
- Coefficient-meter intermediates {11, 23, 47, 83}: predictor unknown.
- Corrected math-track formal rerun (p186c) was left finishing in background;
  the corrected range already rests on 16 clean runs in p186_batch_knob.json
  and p186b_api_surface.json.
- Provenance audit: 259/261 artifacts present (p70/p70-b JSONs missing are
  pre-existing gaps from 09-29, numbers live in registry text).
