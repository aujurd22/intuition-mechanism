# The Two Deep Questions (P134)

Status: 2026-09-30, written in response to the user's closing
directive.  Not a new experiment — the synthesis the program was
building toward.  Two questions:

  Q-MATH  Why exactly these 6 rational rows — what is the unified
          structure behind the Pell-unit normalization?
  Q-LLM   Why is this genus/support structure visible to language
          models at all?

---

# Part I — Q-MATH: the Pell-unit normalization is the elliptic-unit
# specialization, in three layers

## I.0 The datum to explain (all verified tonight, p134_square_unit)

For the six rows, in the smallest-generator convention:

    d=3:  64 P^12(tau0) = eps^(-2),  eps = 5+2sqrt6      (2-pd = -8)
    d=5:  64 P^12(tau0) = eps^(-4),  eps = 3+sqrt10      (2-pd = +8)
    d=7:  64 P^12(tau0) = eps^(-2),  eps = 55+12sqrt21   (2-pd = -8)
    d=13: 64 P^12(tau0) = eps^(-4),  eps = 18+5sqrt13    (2-pd = +8)
    d=17: 64 P^12(tau0) = eps^(-4),  eps = 35+6sqrt34    (2-pd = +8)
    d=1:  64 P^12(tau0) = 1                              (base case)

Three regularities, each mechanically verified:
  (F1) norm_{Q(sqrt s_d)}(64 P^12) = 1 on every row — it is a UNIT;
  (F2) the exponent is always EVEN — 8 P^6(tau0) is itself a unit of
       the same real quadratic (the square root stays in the field);
  (F3) the half-exponent m_d is 1 or 2, decided by the SIGN of the
       2-primary prime discriminant: m_d = 2 iff 2-pd = +8
       (in this family: d = 1 mod 4), m_d = 1 iff 2-pd = -8.
(The earlier registered account of m_d via the Z/4 class-group factor
is superseded: d=13 has m=2 with no Z/4 in sight, and the 2-pd sign
fits all five rows at once.)

## I.1 Layer 1 — the FIELD (O1, proved)

2-elementary => Pic^2 = 1 => H = H_gen.  Every algebraic modular
value at tau0 is a sign-vector combination of the real genus
coordinates sqrt(s) = sqrt(|product of prime discriminants|)/2^k.
No transport, no coprimality.  This is where the "support" lives: the
support of a value is the set of coordinates its sign vector touches.

## I.2 Layer 2 — the UNIT (the Pell normalization explained)

64 P^12 = 2^30 * sqrt(Delta(2t)Delta(6t) / Delta(t)Delta(3t)).
Ratios of Delta at CM points are Siegel-Ramachandra/Robert ELLIPTIC
UNITS of the ring class field (the classical theorem that CM values
of modular-function derivative ratios generate the unit subgroup up
to finite index).  So P^12(tau0) was never going to be an arbitrary
algebraic number: it is an elliptic unit from birth.

On the six rows its support is a SINGLE real coordinate, and a real
quadratic field has unit RANK 1 — so being a unit there IS being a
power of the fundamental unit.  The "Pell-unit normalization" is
therefore not an accident to explain case-by-case; it is the
inevitable form of an elliptic unit once it descends to a rank-1
field.  What genus theory leaves to chance is only:
  (a) WHICH coordinate (the support character, P132's table);
  (b) the Weber f2 2-adic normalization — which fixes the square and
      the half-exponent m_d by the 2-pd sign (F3 above).

## I.3 Layer 3 — the DERIVATIVE (why x6 itself is rational)

x6 = W6/z6 involves not P^12 but the derivative ratio
Ec/W6 = 24 R_d.  The P83-A cancellation identity converts the
quasimodular (non-modular) part of x6 into exactly a weight-2
modular combination E2*(2t),E2*(6t),E2*(t),E2*(3t) — so Ec/W6 is a
ratio of two weight-2 CM objects: the Chowla-Selberg period cancels,
leaving an algebraic number; the elliptic-unit layer makes it
RATIONAL (R_d in Q); and the census-integrality is the last
divisibility step (1/x6 = 6 R_d + 2 in Z).

## I.4 The unified statement

    1/x6(tau0) in Z  <=>  2-elementary (field layer)
                      AND  P^12 single-coordinate support (orbit layer)
                      AND  the elliptic unit's derivative projection
                           R_d is rational with 6R_d+2 in Z (unit layer).

The six rows are where all three layers collapse simultaneously; the
census (P121) says this happens exactly for {1,3,5,7,13,17} in
[1,300], and the 2-elementary closure at d=77 plus the measured
multi-support on composites (P89) make the list finite and complete
in the tested range.

## I.5 What remains honestly open in Q-MATH

Not whether the theorem is true (census-complete) and not whether the
layers are real (each verified), but the UNIFORM RULE: given d, predict
the support coordinate s_d and m_d from arithmetic data without
evaluating the CM value.  The m_d rule (F3) is now uniform; the
s_d rule is not (6, 10, 21, 13, 34 follow no pattern in d we could
find — they are the classical Ramanujan/Weber class-invariant table
entries, i.e. exactly the part of the theory that historically
required TABLES).  This is the precise boundary between theorem and
table in the six-row story.

---

# Part II — Q-LLM: why the genus/support structure is visible to
# language models

The judge reads 6-decimal pairs (x0, lambda).  Genus depth is a
statement about the Galois group of a field extension.  Three links
carry one to the other; the first two are arguably sufficient, the
third is the open residue.

## II.1 The trace is literally in the digits

The stimuli are not arbitrary decimals — they are exact algebraic
numbers whose decimal/continued-fraction structure is a deterministic
function of their defining arithmetic:
  - the six rows have lambda RATIONAL with small denominators: the
    denominators encode R_d = (Ec/W6)/24, the CM-derivative datum
    (1/x6 = 6 R_d + 2: 8, 12, 20, 32, 104, 200);
  - deeper rows have lambda of degree 2-3, whose minimal-polynomial
    discriminants and CF periods encode the class-group data — the
    CF period of a quadratic irrational IS its regulator, i.e. the
    log of the same Pell unit that P79 names.
So "gdepth visible in the digits" does not require magic: the genus
structure determines the height, the denominator shape, and the
period structure of the stimulus numbers.  Digits are the surface of
the field tower.

## II.2 The judge absorbed the canon that is organized by these
## invariants

Pretraining corpora (Ramanujan-series literature, OEIS, class-
invariant tables, problem sets) have been CURATED BY HUMANS for a
century around exactly the invariants in question: rationality,
small denominators, famous quadratic irrationals, Pell pairs.
The judge's "surprise" is a distance-from-the-typical under this
absorbed canon; on deg-matched pairs the canon's depth-organization
correlates with gdepth, so the judge's readings track gdepth at
carrier rates.  The utility axis is even more directly canon-bound:
pub(d) is literally membership in the published record — which is
why I2 replicates across families while I1 is format-fragile (the
utility reading checks membership in a memorized list; the surprise
reading measures a subtler typicality gradient).

## II.3 The honest residue (and its falsification design)

What is NOT yet explained: whether the judges read gdepth PER SE or
a correlate.  Within deg-matched pairs, higher-gdepth rows also tend
to have larger |d|, larger R_d, taller denominators.  A judge that
prefers "more complicated decimals" would mimic the gdepth signal.
The registered falsification is a DESIGN, not a new model:
  height-matched deg-matched pairs (equalize denominator size and
  CF period length, keep gdepth different).
  - signal dies  -> the instrument reads height, and I1 must be
    restated with height as the mediator (gdepth demoted to
    correlate);
  - signal lives -> the map to genus structure is tighter than
    height, and the mechanism question sharpens to: what digit-level
    statistic separates genus classes at equal height?
Either outcome is a clean result.  Until run, I1 carries the caveat
"mediation between gdepth and surface height not separated".

## II.4 The two-layer summary

  Math line:  elliptic unit -> (field, orbit, unit) three layers ->
              six-row collapse.
  Judge line:  algebraic trace -> (digits, canon) two links ->
              carrier-rate agreement.
  The shared object is the genus group: it organizes the CM values
  AND the human canon AND (therefore) the absorbed statistics of the
  judge.  The program's central coincidence — that a language
  model's blind preference tracks the genus group at all — is
  explained one level down (canon absorption of digit traces) and
  leaves one level open (per-se mediation, II.3).
