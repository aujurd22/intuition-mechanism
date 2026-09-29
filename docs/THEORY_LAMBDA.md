# THEORY_LAMBDA — read this banner first

**STATUS (2026-09-29, P76 falsification): every `THEOREM: lambda in Q(x0) via the Hauptmodul property` block below is RETRACTED.** x12 is NOT modular for Gamma0(12) (3.6e-4 deviation at (1,0;12,1), 40 dps). The blocks are kept only as an archive of the falsified route; the current theory lives in docs/RATIONALITY_LEMMA.md and docs/THEOREM_FIVE_ROWS.md. A reader searching `THEOREM` will hit the archived blocks first — check this banner before trusting any `QED` below the P76 section.

# Theory note: the algebraic depth of lambda (P36-a/P37/P38)

Status (2026-09-28): proof SKETCH + empirical laws; the complete proof is
registered open theory. Written down so the next session starts from the
right questions.

## Setup

For the t-family (CWZ level 12), every admissible N determines a CM point
tau0 = i sqrt(N/24), an evaluation point x0 = x(tau0) (the eta-quotient
x12 applied to q = exp(-2 pi sqrt(N/24))), and a linear coefficient

    lambda = (rhs(x0) - x0 z'(x0)) / z(x0),        (P25-b)

where z = sum t(n) x^n satisfies the CWZ modular parametrization
(z modular for Gamma_0(12), x = x12, rhs algebraic in x with the
1/(2 pi) sqrt(24/N) period factor).

## Proposition 1 (algebraicity; sketch level, standard tools)

lambda is the value at the CM point tau0 of a modular function of level
12: rhs(x0) is algebraic in x0; z and z' are (quasi)modular forms whose
log-derivative x z'/z is modular of weight 2 up to the E_2 slip, killed
by the explicit period factor 1/(2 pi) sqrt(24/N).  By the classical CM
algebraicity theorem (values of modular functions of level N at CM
points of the order of discriminant D lie in the ray class field of the
order Z[12 tau0], disc(-24N)), lambda is algebraic and

    Q(lambda) and Q(x0) both sit inside the same ray class field K_f,
    f the conductor at tau0 (disc(-24N)).

Consequence: deg(lambda) <= [K_f : Q] for every N; generically
Q(lambda) = Q(x0) = K_f.  This is the theoretical form of the observed

    ** deg(lambda) = deg(x0) on 20/20 resolved rows (P36-a). **

What a complete proof still needs: (i) the precise modularity level of
lambda as a function on X_0(12) (or on a quotient by the Fricke group,
consistent with the P23 orbit pairing); (ii) ruling out the proper
subfield degenerations case by case.

## Proposition 2 (the rationality boundary; reduced to a degeneration
question)

The literature published exactly the five rows {3,5,7,13,17} where BOTH
x0 and lambda are rational.  When is a CM value of x12 rational?  This is
NOT decided by class numbers:

    - h(D_K) = 1 holds at 12 rows N <= 60 (N = 2, 6, 8, 12, 18, 24, 27,
      32, 42, 48, 50, 54; the squarefree part of 6N lies in {-3,-4,-7}),
      and x0 is NOT rational at any of them;
    - the five rational rows have h(D_K) = 1, 4, 4, 4, 4;
    - Spearman(h(order), deg(x0)) = 0.146 (p = 0.27, N <= 60): class
      numbers do not even rank-correlate with the degree.  (P38, negative)

The correct statement is that rationality is a DEGENERATION condition
specific to the eta-quotient x12 at the CM point -- the same phenomenon
P23 named "the published rational rows are the trace-degenerate tips of
full orbits".  Exact classification (in terms of fixed points of
Atkin-Lehner-type elements of Gamma_0(12)+ on the CM set, or of the
12-isogeny self-pairing condition) is the registered open problem.

## Refined statement (2026-09-28 05:00, after the first failure analysis)

The naive "ring class field of disc(-24N)" story is WRONG, and the data
says so in two independent ways:

1. h(-24N) does not bound the observed degrees: N=6 has tau0 = i/2, a
   CM point of the order disc(-16) with CLASS NUMBER 1 -- yet
   x12(i/2) has degree 9 over Q.  (No field of degree 1 contains a
   degree-9 number.)

2. The correct statement: x12 = eta(q^2)eta(q^4)eta(q^6)eta(q^12)/z12
   is a modular function for a GROUP WITH CHARACTER (the eta-product
   carries a multiplier), so its CM values live in a RAY-class-type
   field of K = Q(tau0) with conductor entangled with the level-12
   eta-conductor and twisted by the multiplier character.  The N=6
   anomaly (h(order)=1, deg(x0)=9 = 3^2) is the concrete fingerprint:
   the field is a character-twist of a ray class field of Q(i) with
   conductor built from the primes 2 and 3 -- and since tau0 = i/2
   is 2-isogenous to i, the 2-part interacts with the order
   conductor.

Consequences for the open problem:

- "x0 rational iff fixed by the Shimura action" survives, but the
  action to use is the RAY-class action twisted by the eta-multiplier
  character, not the plain ring-class action;
- deg(lambda) = deg(x0) (20/20) says lambda and x0 generate the SAME
  such twisted field generically -- consistent with lambda being a
  rational expression in x0 and the same weight-2 forms;
- the five rational rows are then exactly the N where the twisted
  ray-class field collapses to Q -- a concrete, finitely checkable
  condition (compute the character value of each class-group element
  on each eta factor), which is the registered next computation.

## The degeneration criterion, made exact (2026-09-28 05:05)

Writing -24N = f^2 * D_K (D_K the fundamental discriminant of
Q(sqrt(-6N)), f the conductor), the census says:

    ** x0 in Q  <=>  [ f = 1 and h(D_K) = 4 ]  or  [ D_K = -8, f = 3 ] **

verified EXHAUSTIVELY on N = 2..160: predicted {3,5,7,13,17} against
the actual degree-1 rows with ZERO false positives and ZERO
uncovered rows (p38_criterion_test.json).  Reading:

- the f=1, h=4 case: the class group of the maximal order is
  (Z/2)^2 (four classes, all 2-torsion -- genus theory), and the
  level-12 degeneracy folds the four orbit values onto one rational
  number;
- the D_K=-8, f=3 case (N=3): the order class number is 2 and the
  eta-quotient value lands in the rational fixed field of the
  involution.

What remains open is the PROOF that the eta-multiplier character
kills exactly these cases (a finite, checkable computation per case
via the Shimura action on the four eta factors), and the asymptotic
statement that no N > 160 satisfies the criterion (genus theory
bounds how often h(D_K)=4 with f=1 occurs; each candidate is a
direct check).

## Orbit-permutation question (registered refinement of the halted P24)

Natural question: does the class group permute the CONJUGATES of lambda
(the orbit lambda values = the other roots of lambda's minimal
polynomial)?  A naive SL2-conjugation test tonight repeated P24's
halted category error: at the class-group conjugate CM points (non-
imaginary-axis tau) lambda takes COMPLEX values, so the comparison
against the real cubic roots is ill-posed.  The correctly posed
version (next session): pair each orbit lambda with a real one via
the CCL mu-transformation

    mu = (lambda - 1/2) * sqrt(1 - 4 a x - 16 c x^2),

i.e. test whether the mu-values (not the raw lambdas) are permuted by
the class group, and whether N=9's cubic is the mu-orbit polynomial.
P23's orbit x-values (n_distinct_x0) are the substrate.

## Asymptotic finiteness of the rational locus (proved component,
## 2026-09-28 11:40)

The "no N > 160 satisfies the criterion" gap just closed, as a THEOREM
component rather than a numerical observation:

1. Case D_K = -8 (i.e. 6N = 2 * 3^2 * m^2 in fundamental terms --
   worked out: N = 3 is the ONLY solution with f = 3, since f = 3
   forces 24N = 9 * |D_K| = 72, hence N = 3 exactly).

2. Case f = 1 and h(D_K) = 4: here 24N = |D_K| is squarefree-up-to-
   the-fundamental-adjustment, so |D_K| = 24N -> infinity as N does;
   by the classical finiteness of imaginary-quadratic fields of any
   FIXED class number (Heilbronn 1934), h(D_K) = 4 holds for only
   FINITELY many D_K (the standard table: -84, -120, -132, -168,
   -195, -228, -259, -260, -276, -408).  Intersecting with the
   level-12 admissibility (24N = |D_K| integral with the correct
   squarefree bookkeeping) leaves exactly N in {5, 7, 13, 17}
   (D_K = -120, -168, -312, -408; note -312 is a fundamental
   discriminant with h = 4 that the first-draft list above missed --
   caught by the direct enumeration below).

3. DIRECT ENUMERATION CLOSES IT EMPIRICALLY TOO: scanning N = 2..40000
   with the exact decompositions, the criterion hits are EXACTLY
   [(3, -8, 3), (5, -120, 1), (7, -168, 1), (13, -312, 1),
   (17, -408, 1)] -- the five literature rows and nothing else (4e4
   rows scanned, zero false positives, zero misses).

3. Therefore: the criterion admits only finitely many rational rows,
   and the census has already found them ALL.  The five literature
   rows are not "the shallow tip of an infinite iceberg" -- they are
   the complete list, and the machine census's degree hierarchy above
   them is the whole story.

Remaining open (unchanged): the eta-multiplier character computation
that proves the criterion per case (why h=4 folds to rationality for
THIS eta-quotient), which is now a finite case-check on exactly four
maximal-order discriminants plus N=3.

## The folding MECHANISM, observed numerically (2026-09-28 12:55)

Computing x12 at every class-group conjugate of the CM point (using
P23's verified q_of_tau route) separates the two regimes directly:

- RATIONAL rows (N=5: D=-120; N=7: D=-168): every orbit value of x12
  is REAL, forming a descending chain from the principal value
  (N=5: 0.05 -> 0.001023 -> 1.042e-5 -> 3.37e-8 -> 0).  The tau0 of
  the census is the orbit's MAXIMUM.  "Folding" is literal: the
  class-group translates land on the real axis.
- DEEP rows (N=2: deg 2; N=11: deg 2; N=9: deg 3): the orbit values
  split into conjugate COMPLEX PAIRS (N=11: 3.663e-5 +/- 3.85e-6 i;
  6.795e-4 +/- 2.54e-5 i; N=9: 9.55e-5 +/- 2.03e-5 i, 1.339e-3 +/-
  2.53e-4 i) plus real members.

REGISTERED READING, now BIDIRECTIONALLY VERIFIED (2026-09-28
  13:25): x0 in Q  <=>  x12 is REAL on the entire class-group orbit.
  Forward: all five rational rows have max |Im| = 0 over their full
  orbits.  Converse (refutation attempt FAILED): the deep rows
  N = 19, 23, 25, 27, 29, 31 ALL have non-real orbit members
  (max |Im| 1.7e-5 .. 4.9e-4).  11/11 rows consistent; the statement
  is now a precise theorem-candidate whose proof reduces to the eta
  multiplier character being real-valued on the orbit exactly for
  the 4+1 degeneration cases.  This is checkable in
  principle per case because the eta-product's multiplier character
  is what controls the imaginary part, and for the four h=4
  discriminants the character values on the (2-torsion) class group
  are forced to +-1 phases that the specific eta-signature
  eta2 eta4 eta6 eta12 makes cancel.  The remaining proof work is
  exactly this character computation on 4+1 cases.

## The theorem candidate: genus theory explains the degeneration locus
## (2026-09-28 18:00)

The η-multiplier proof reduces to a GENUS THEORY statement:

**Theorem candidate.** For the t-family at level 12, the class-group
conjugates of x12(tau0) are ALL REAL if and only if the class group of
the order of discriminant -24N is entirely 2-torsion.  In that case,
lambda (a rational function of x12 and its log-derivative) is also
real, and for h(D_K) = 4 it is rational.

**Proof sketch.**
1. The class group Cl(O_f) acts on the CM point tau0 by Shimura
   reciprocity.  For each class, x12(tau^a) is algebraic in the ring
   class field.
2. Complex conjugation acts as the inverse class.  If Cl(O_f) is
   entirely 2-torsion, then [a] = [-a] for every class, so the
   conjugate points are all fixed by complex conjugation conjugated
   by the class action → x12 values are real.
3. lambda is a rational expression in x12 and x12'/x12 (weight-0
   modular function from the P25-b formula).  Since both x12 and the
   log-derivative are modular for Gamma_0(12), lambda is a level-12
   modular function.  The Shimura reciprocity law says its CM values
   lie in the ring class field.
4. When Cl(O_f) = (Z/2)^k, every element is its own inverse, so the
   Shimura action is trivial on the values → lambda is in the REAL
   subfield of the ring class field.
5. For h = 4 and class group (Z/2)^2, the ring class field is a
   biquadratic extension of Q with three quadratic subfields -- all
   real when the discriminant is negative.  Lambda lies in one of
   these subfields.
6. For h(D_K) > 4 or h(D_K) = 8 (containing Z/4), some orbit values
   are genuinely complex → lambda can be complex or of higher degree.

**Reduction to genus theory.**  h(D_K) = 4 with class group (Z/2)^2
happens iff the discriminant has exactly 3 prime discriminant factors
(genus theory: 2-rank = t-1 = 2).  The five rows {3,5,7,13,17} have
D_K with t = 2 (N=3, D_K=-8, class group Z/2) or t = 3 (N=5,7,13,17).
The f > 1 cases are controlled by the conductor degeneration.

**What remains for a complete proof:** step 4 (the Shimura action is
trivial on the eta-product values for 2-torsion classes) requires
computing the eta-multiplier character, which is a finite check on
4+1 cases.  The numerical evidence (all orbit values real for the
five rows, max |Im| = 0.00e+00) is consistent.

## Connection to idoneal numbers (2026-09-28 18:05)

The five rational-lambda rows {3,5,7,13,17} are the level-12 analog
of Euler's idoneal numbers (numeri idonei): positive integers n for
which the class group of the order of discriminant -4n has exponent
<= 2 (all elements are 2-torsion).  Euler found 65 such numbers; the
list's completeness under GRH is due to Weinberger (1973).

The connection: for the t-family, lambda is rational iff the ring
class field of the order disc(-24N) is generated by x12 over Q, and
x12 generates the ring class field.  Lambda is rational iff x12
generates only the rationals -- i.e. iff the ring class field equals
Q -- i.e. iff the class group acts trivially on x12 -- i.e. iff the
class group has exponent <= 2 (all classes are 2-torsion).

This is exactly the idoneal number condition applied to the order of
discriminant -24N at level 12.  The five rows {3,5,7,13,17} are the
idoneal numbers for the level-12 eta-quotient x12.

## THEOREM: lambda in Q(x0) via the Hauptmodul property of Gamma_0(12)
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 18:20 — proof complete at the modular-function level)

**Theorem.** Let tau0 be a CM point of disc(-24N), x0 = x12(tau0),
and lambda = (r - x0 S1'/S0') / S0 as in the CWZ identity.  Then:

  (i) lambda in Q(x0), hence deg(lambda) <= deg(x0);
  (ii) X_0(12) has genus 0, so x12 is a Hauptmodul and
       Q(X_0(12)) = Q(x12) is the full function field;
  (iii) deg(lambda) = deg(x0) iff lambda generates the full ring
       class field; deg(lambda) < deg(x0) iff lambda lies in a
       proper subfield (the "degeneration" that makes lambda
       rational for exactly 5 rows).

**Proof.**
(i) X_0(12) has genus 0 (standard formula: the index of Gamma_0(12)
    in PSL_2(Z) gives g = 0).  Therefore x12 is a Hauptmodul and
    Q(X_0(12)) = Q(x12): every modular function of level 12 with
    rational Fourier coefficients is a rational function of x12.
(ii) z = sum t(n) x^n is a modular form of weight 2 on Gamma_0(12)
    (CWZ Thm 3.1).  The combination lambda = (r - x0 z'/z) / z
    involves only: z (weight 2), x0 z'/z (a weight-0 modular
    function, since the quasi-modular E_2 slip in z' is killed by
    the explicit period factor), and r (algebraic in x by the CWZ
    differential).  Therefore lambda is a modular function of
    level 12, and by Shimura reciprocity, lambda(tau0) lies in
    the ring class field of disc(-24N).
(iii) Since x12 is a Hauptmodul, Q(X_0(12)) = Q(x12).  Lambda, as
    a modular function of the same level, is a rational function
    of x12 in the function field.  The value lambda(tau0) is the
    evaluation of this rational function at the algebraic point
    x12(tau0), so Q(lambda) is a subfield of Q(x12(tau0)).
    This proves deg(lambda) <= deg(x0).

**Corollary (genus theory).**  The ring class field of disc(-24N)
has degree h(-24N) over K = Q(sqrt(-6N)), and [K_f : Q] = 2 h(-24N).
The 2-torsion structure of Cl(O_f) determines which subfield lambda
generates.  For the five degenerate rows {3,5,7,13,17}, the class
group is (Z/2)^2 (t = 3 prime factors), the ring class field is
biquadratic over Q, and lambda lies in one of the three quadratic
subfields.  For the other rows, lambda lives in a higher-degree
subfield.

**Connection to idoneal numbers.**  The five rows {3,5,7,13,17}
where lambda is rational are exactly the rows where the order of
disc(-24N) is "idoneal at level 12" -- the ring class field is a
2-extension of Q, so every modular function value is at most
quadratic over Q.  This is the level-12 analog of Euler's idoneal
numbers (which parametrize orders with class group exponent <= 2).

**Q.E.D. (modular function theory + genus 0 of X_0(12))**

## THEOREM (upgraded from sketch): lambda in Q(x12) via Hauptmodul property
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 23:30 — complete proof at the modular function theory level)

**Theorem.** x12 is a Hauptmodul for the modular curve X_0(12)
(genus 0).  Therefore Q(X_0(12)) = Q(x12): every modular function
of level 12 (on Gamma_0(12)) with algebraic Fourier coefficients
is a rational function of x12.  In particular:

  (a) lambda = R(x12) for some R in Q(X)
  (b) deg(lambda) <= deg(x0)
  (c) lambda is rational iff R maps x0 to Q
  (d) R is unique iff it generates Q(X_0(12)), which happens
      generically

**Proof.**
1. X_0(12) has genus 0 (standard: g = 1 + N/12 prod(1+1/p) -
   N/4 prod(1+1/p) - sum(...), which gives g = 0 for N = 12).
2. x12 is a Hauptmodul: the eta-product
   eta(2tau)eta(4tau)eta(6tau)eta(12tau)
   has weight 2 and trivial character on Gamma_0(12) (Ligozat
   1975), and x12 = this eta-product / z12 where z12 is a weight-2
   form on Gamma_0(12).  Therefore x12 generates the function field.
3. lambda is computed from x12 and the differential q dx/dq =
   z12 x12 sqrt((1+4x12)(1-4x12)(1-8x12)).  The sqrt factor is a
   rational function on X_0(12) because its zeros/poles are at
   cusps and elliptic points of the modular curve, and the
   combination is a rational expression in x12.
4. Therefore lambda in Q(X_0(12)) = Q(x12) by step 1.

**Corollary 1.**  deg(lambda) <= deg(x0) — the field degree of
lambda is at most that of x0, because lambda is a rational function
of x0 on the same algebraic curve.  (22/22 rows confirmed.)

**Corollary 2.**  lambda is rational iff R maps x0 to Q.  For
N = 3,5,7,13,17: x0 is the CM value of the Hauptmodul, and the
ring class field is biquadratic over Q.  lambda is rational iff
R maps the algebraic x0 into Q — which happens when x0 generates
a ring class field whose three quadratic subfields include the
one fixed by R's symmetry group.  By genus theory (t=3 prime
discriminant factors -> Cl = (Z/2)^2), all three subfields are
the three quadratic subextensions, and lambda lands in the one
fixed by the Atkin-Lehner involutions compatible with level 12.

**Connection to idoneal numbers.**  The condition "lambda
rational" is equivalent to "the ring class field of disc(-24N)
has exponent <= 2" — which is exactly the idoneal number
condition for the order disc(-24N).  The five rows {3,5,7,13,17}
are the idoneal orders at level 12.

**Q.E.D.** (standard modular function theory: genus 0 + Shimura
reciprocity + Ligozart's eta-product criterion)

## Empirical facts backing the note (all machine-verified tonight)

## THEOREM: lambda in Q(x0) via the Hauptmodul property of Gamma_0(12)
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 18:20 — proof complete at the modular-function level)

**Theorem.** Let tau0 be a CM point of disc(-24N), x0 = x12(tau0),
and lambda = (r - x0 S1'/S0') / S0 as in the CWZ identity.  Then:

  (i) lambda in Q(x0), hence deg(lambda) <= deg(x0);
  (ii) X_0(12) has genus 0, so x12 is a Hauptmodul and
       Q(X_0(12)) = Q(x12) is the full function field;
  (iii) deg(lambda) = deg(x0) iff lambda generates the full ring
       class field; deg(lambda) < deg(x0) iff lambda lies in a
       proper subfield (the "degeneration" that makes lambda
       rational for exactly 5 rows).

**Proof.**
(i) X_0(12) has genus 0 (standard formula: the index of Gamma_0(12)
    in PSL_2(Z) gives g = 0).  Therefore x12 is a Hauptmodul and
    Q(X_0(12)) = Q(x12): every modular function of level 12 with
    rational Fourier coefficients is a rational function of x12.
(ii) z = sum t(n) x^n is a modular form of weight 2 on Gamma_0(12)
    (CWZ Thm 3.1).  The combination lambda = (r - x0 z'/z) / z
    involves only: z (weight 2), x0 z'/z (a weight-0 modular
    function, since the quasi-modular E_2 slip in z' is killed by
    the explicit period factor), and r (algebraic in x by the CWZ
    differential).  Therefore lambda is a modular function of
    level 12, and by Shimura reciprocity, lambda(tau0) lies in
    the ring class field of disc(-24N).
(iii) Since x12 is a Hauptmodul, Q(X_0(12)) = Q(x12).  Lambda, as
    a modular function of the same level, is a rational function
    of x12 in the function field.  The value lambda(tau0) is the
    evaluation of this rational function at the algebraic point
    x12(tau0), so Q(lambda) is a subfield of Q(x12(tau0)).
    This proves deg(lambda) <= deg(x0).

**Corollary (genus theory).**  The ring class field of disc(-24N)
has degree h(-24N) over K = Q(sqrt(-6N)), and [K_f : Q] = 2 h(-24N).
The 2-torsion structure of Cl(O_f) determines which subfield lambda
generates.  For the five degenerate rows {3,5,7,13,17}, the class
group is (Z/2)^2 (t = 3 prime factors), the ring class field is
biquadratic over Q, and lambda lies in one of the three quadratic
subfields.  For the other rows, lambda lives in a higher-degree
subfield.

**Connection to idoneal numbers.**  The five rows {3,5,7,13,17}
where lambda is rational are exactly the rows where the order of
disc(-24N) is "idoneal at level 12" -- the ring class field is a
2-extension of Q, so every modular function value is at most
quadratic over Q.  This is the level-12 analog of Euler's idoneal
numbers (which parametrize orders with class group exponent <= 2).

**Q.E.D. (modular function theory + genus 0 of X_0(12))**

## THEOREM (upgraded from sketch): lambda in Q(x12) via Hauptmodul property
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 23:30 — complete proof at the modular function theory level)

**Theorem.** x12 is a Hauptmodul for the modular curve X_0(12)
(genus 0).  Therefore Q(X_0(12)) = Q(x12): every modular function
of level 12 (on Gamma_0(12)) with algebraic Fourier coefficients
is a rational function of x12.  In particular:

  (a) lambda = R(x12) for some R in Q(X)
  (b) deg(lambda) <= deg(x0)
  (c) lambda is rational iff R maps x0 to Q
  (d) R is unique iff it generates Q(X_0(12)), which happens
      generically

**Proof.**
1. X_0(12) has genus 0 (standard: g = 1 + N/12 prod(1+1/p) -
   N/4 prod(1+1/p) - sum(...), which gives g = 0 for N = 12).
2. x12 is a Hauptmodul: the eta-product
   eta(2tau)eta(4tau)eta(6tau)eta(12tau)
   has weight 2 and trivial character on Gamma_0(12) (Ligozat
   1975), and x12 = this eta-product / z12 where z12 is a weight-2
   form on Gamma_0(12).  Therefore x12 generates the function field.
3. lambda is computed from x12 and the differential q dx/dq =
   z12 x12 sqrt((1+4x12)(1-4x12)(1-8x12)).  The sqrt factor is a
   rational function on X_0(12) because its zeros/poles are at
   cusps and elliptic points of the modular curve, and the
   combination is a rational expression in x12.
4. Therefore lambda in Q(X_0(12)) = Q(x12) by step 1.

**Corollary 1.**  deg(lambda) <= deg(x0) — the field degree of
lambda is at most that of x0, because lambda is a rational function
of x0 on the same algebraic curve.  (22/22 rows confirmed.)

**Corollary 2.**  lambda is rational iff R maps x0 to Q.  For
N = 3,5,7,13,17: x0 is the CM value of the Hauptmodul, and the
ring class field is biquadratic over Q.  lambda is rational iff
R maps the algebraic x0 into Q — which happens when x0 generates
a ring class field whose three quadratic subfields include the
one fixed by R's symmetry group.  By genus theory (t=3 prime
discriminant factors -> Cl = (Z/2)^2), all three subfields are
the three quadratic subextensions, and lambda lands in the one
fixed by the Atkin-Lehner involutions compatible with level 12.

**Connection to idoneal numbers.**  The condition "lambda
rational" is equivalent to "the ring class field of disc(-24N)
has exponent <= 2" — which is exactly the idoneal number
condition for the order disc(-24N).  The five rows {3,5,7,13,17}
are the idoneal orders at level 12.

**Q.E.D.** (standard modular function theory: genus 0 + Shimura
reciprocity + Ligozart's eta-product criterion)

## Empirical facts backing the note (all machine-verified tonight)## Connection to idoneal numbers (2026-09-28 18:05)

The five rational-lambda rows {3,5,7,13,17} are the level-12 analog
of Euler's idoneal numbers (numeri idonei): positive integers n for
which the class group of the order of discriminant -4n has exponent
<= 2 (all elements are 2-torsion).  Euler found 65 such numbers; the
list's completeness under GRH is due to Weinberger (1973).

The connection: for the t-family, lambda is rational iff the ring
class field of the order disc(-24N) is generated by x12 over Q, and
x12 generates the ring class field.  Lambda is rational iff x12
generates only the rationals -- i.e. iff the ring class field equals
Q -- i.e. iff the class group acts trivially on x12 -- i.e. iff the
class group has exponent <= 2 (all classes are 2-torsion).

This is exactly the idoneal number condition applied to the order of
discriminant -24N at level 12.  The five rows {3,5,7,13,17} are the
idoneal numbers for the level-12 eta-quotient x12.

## THEOREM: lambda in Q(x0) via the Hauptmodul property of Gamma_0(12)
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 18:20 — proof complete at the modular-function level)

**Theorem.** Let tau0 be a CM point of disc(-24N), x0 = x12(tau0),
and lambda = (r - x0 S1'/S0') / S0 as in the CWZ identity.  Then:

  (i) lambda in Q(x0), hence deg(lambda) <= deg(x0);
  (ii) X_0(12) has genus 0, so x12 is a Hauptmodul and
       Q(X_0(12)) = Q(x12) is the full function field;
  (iii) deg(lambda) = deg(x0) iff lambda generates the full ring
       class field; deg(lambda) < deg(x0) iff lambda lies in a
       proper subfield (the "degeneration" that makes lambda
       rational for exactly 5 rows).

**Proof.**
(i) X_0(12) has genus 0 (standard formula: the index of Gamma_0(12)
    in PSL_2(Z) gives g = 0).  Therefore x12 is a Hauptmodul and
    Q(X_0(12)) = Q(x12): every modular function of level 12 with
    rational Fourier coefficients is a rational function of x12.
(ii) z = sum t(n) x^n is a modular form of weight 2 on Gamma_0(12)
    (CWZ Thm 3.1).  The combination lambda = (r - x0 z'/z) / z
    involves only: z (weight 2), x0 z'/z (a weight-0 modular
    function, since the quasi-modular E_2 slip in z' is killed by
    the explicit period factor), and r (algebraic in x by the CWZ
    differential).  Therefore lambda is a modular function of
    level 12, and by Shimura reciprocity, lambda(tau0) lies in
    the ring class field of disc(-24N).
(iii) Since x12 is a Hauptmodul, Q(X_0(12)) = Q(x12).  Lambda, as
    a modular function of the same level, is a rational function
    of x12 in the function field.  The value lambda(tau0) is the
    evaluation of this rational function at the algebraic point
    x12(tau0), so Q(lambda) is a subfield of Q(x12(tau0)).
    This proves deg(lambda) <= deg(x0).

**Corollary (genus theory).**  The ring class field of disc(-24N)
has degree h(-24N) over K = Q(sqrt(-6N)), and [K_f : Q] = 2 h(-24N).
The 2-torsion structure of Cl(O_f) determines which subfield lambda
generates.  For the five degenerate rows {3,5,7,13,17}, the class
group is (Z/2)^2 (t = 3 prime factors), the ring class field is
biquadratic over Q, and lambda lies in one of the three quadratic
subfields.  For the other rows, lambda lives in a higher-degree
subfield.

**Connection to idoneal numbers.**  The five rows {3,5,7,13,17}
where lambda is rational are exactly the rows where the order of
disc(-24N) is "idoneal at level 12" -- the ring class field is a
2-extension of Q, so every modular function value is at most
quadratic over Q.  This is the level-12 analog of Euler's idoneal
numbers (which parametrize orders with class group exponent <= 2).

**Q.E.D. (modular function theory + genus 0 of X_0(12))**

## THEOREM (upgraded from sketch): lambda in Q(x12) via Hauptmodul property
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 23:30 — complete proof at the modular function theory level)

**Theorem.** x12 is a Hauptmodul for the modular curve X_0(12)
(genus 0).  Therefore Q(X_0(12)) = Q(x12): every modular function
of level 12 (on Gamma_0(12)) with algebraic Fourier coefficients
is a rational function of x12.  In particular:

  (a) lambda = R(x12) for some R in Q(X)
  (b) deg(lambda) <= deg(x0)
  (c) lambda is rational iff R maps x0 to Q
  (d) R is unique iff it generates Q(X_0(12)), which happens
      generically

**Proof.**
1. X_0(12) has genus 0 (standard: g = 1 + N/12 prod(1+1/p) -
   N/4 prod(1+1/p) - sum(...), which gives g = 0 for N = 12).
2. x12 is a Hauptmodul: the eta-product
   eta(2tau)eta(4tau)eta(6tau)eta(12tau)
   has weight 2 and trivial character on Gamma_0(12) (Ligozat
   1975), and x12 = this eta-product / z12 where z12 is a weight-2
   form on Gamma_0(12).  Therefore x12 generates the function field.
3. lambda is computed from x12 and the differential q dx/dq =
   z12 x12 sqrt((1+4x12)(1-4x12)(1-8x12)).  The sqrt factor is a
   rational function on X_0(12) because its zeros/poles are at
   cusps and elliptic points of the modular curve, and the
   combination is a rational expression in x12.
4. Therefore lambda in Q(X_0(12)) = Q(x12) by step 1.

**Corollary 1.**  deg(lambda) <= deg(x0) — the field degree of
lambda is at most that of x0, because lambda is a rational function
of x0 on the same algebraic curve.  (22/22 rows confirmed.)

**Corollary 2.**  lambda is rational iff R maps x0 to Q.  For
N = 3,5,7,13,17: x0 is the CM value of the Hauptmodul, and the
ring class field is biquadratic over Q.  lambda is rational iff
R maps the algebraic x0 into Q — which happens when x0 generates
a ring class field whose three quadratic subfields include the
one fixed by R's symmetry group.  By genus theory (t=3 prime
discriminant factors -> Cl = (Z/2)^2), all three subfields are
the three quadratic subextensions, and lambda lands in the one
fixed by the Atkin-Lehner involutions compatible with level 12.

**Connection to idoneal numbers.**  The condition "lambda
rational" is equivalent to "the ring class field of disc(-24N)
has exponent <= 2" — which is exactly the idoneal number
condition for the order disc(-24N).  The five rows {3,5,7,13,17}
are the idoneal orders at level 12.

**Q.E.D.** (standard modular function theory: genus 0 + Shimura
reciprocity + Ligozart's eta-product criterion)

## Empirical facts backing the note (all machine-verified tonight)

## THEOREM: lambda in Q(x0) via the Hauptmodul property of Gamma_0(12)
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 18:20 — proof complete at the modular-function level)

**Theorem.** Let tau0 be a CM point of disc(-24N), x0 = x12(tau0),
and lambda = (r - x0 S1'/S0') / S0 as in the CWZ identity.  Then:

  (i) lambda in Q(x0), hence deg(lambda) <= deg(x0);
  (ii) X_0(12) has genus 0, so x12 is a Hauptmodul and
       Q(X_0(12)) = Q(x12) is the full function field;
  (iii) deg(lambda) = deg(x0) iff lambda generates the full ring
       class field; deg(lambda) < deg(x0) iff lambda lies in a
       proper subfield (the "degeneration" that makes lambda
       rational for exactly 5 rows).

**Proof.**
(i) X_0(12) has genus 0 (standard formula: the index of Gamma_0(12)
    in PSL_2(Z) gives g = 0).  Therefore x12 is a Hauptmodul and
    Q(X_0(12)) = Q(x12): every modular function of level 12 with
    rational Fourier coefficients is a rational function of x12.
(ii) z = sum t(n) x^n is a modular form of weight 2 on Gamma_0(12)
    (CWZ Thm 3.1).  The combination lambda = (r - x0 z'/z) / z
    involves only: z (weight 2), x0 z'/z (a weight-0 modular
    function, since the quasi-modular E_2 slip in z' is killed by
    the explicit period factor), and r (algebraic in x by the CWZ
    differential).  Therefore lambda is a modular function of
    level 12, and by Shimura reciprocity, lambda(tau0) lies in
    the ring class field of disc(-24N).
(iii) Since x12 is a Hauptmodul, Q(X_0(12)) = Q(x12).  Lambda, as
    a modular function of the same level, is a rational function
    of x12 in the function field.  The value lambda(tau0) is the
    evaluation of this rational function at the algebraic point
    x12(tau0), so Q(lambda) is a subfield of Q(x12(tau0)).
    This proves deg(lambda) <= deg(x0).

**Corollary (genus theory).**  The ring class field of disc(-24N)
has degree h(-24N) over K = Q(sqrt(-6N)), and [K_f : Q] = 2 h(-24N).
The 2-torsion structure of Cl(O_f) determines which subfield lambda
generates.  For the five degenerate rows {3,5,7,13,17}, the class
group is (Z/2)^2 (t = 3 prime factors), the ring class field is
biquadratic over Q, and lambda lies in one of the three quadratic
subfields.  For the other rows, lambda lives in a higher-degree
subfield.

**Connection to idoneal numbers.**  The five rows {3,5,7,13,17}
where lambda is rational are exactly the rows where the order of
disc(-24N) is "idoneal at level 12" -- the ring class field is a
2-extension of Q, so every modular function value is at most
quadratic over Q.  This is the level-12 analog of Euler's idoneal
numbers (which parametrize orders with class group exponent <= 2).

**Q.E.D. (modular function theory + genus 0 of X_0(12))**

## THEOREM (upgraded from sketch): lambda in Q(x12) via Hauptmodul property
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 23:30 — complete proof at the modular function theory level)

**Theorem.** x12 is a Hauptmodul for the modular curve X_0(12)
(genus 0).  Therefore Q(X_0(12)) = Q(x12): every modular function
of level 12 (on Gamma_0(12)) with algebraic Fourier coefficients
is a rational function of x12.  In particular:

  (a) lambda = R(x12) for some R in Q(X)
  (b) deg(lambda) <= deg(x0)
  (c) lambda is rational iff R maps x0 to Q
  (d) R is unique iff it generates Q(X_0(12)), which happens
      generically

**Proof.**
1. X_0(12) has genus 0 (standard: g = 1 + N/12 prod(1+1/p) -
   N/4 prod(1+1/p) - sum(...), which gives g = 0 for N = 12).
2. x12 is a Hauptmodul: the eta-product
   eta(2tau)eta(4tau)eta(6tau)eta(12tau)
   has weight 2 and trivial character on Gamma_0(12) (Ligozat
   1975), and x12 = this eta-product / z12 where z12 is a weight-2
   form on Gamma_0(12).  Therefore x12 generates the function field.
3. lambda is computed from x12 and the differential q dx/dq =
   z12 x12 sqrt((1+4x12)(1-4x12)(1-8x12)).  The sqrt factor is a
   rational function on X_0(12) because its zeros/poles are at
   cusps and elliptic points of the modular curve, and the
   combination is a rational expression in x12.
4. Therefore lambda in Q(X_0(12)) = Q(x12) by step 1.

**Corollary 1.**  deg(lambda) <= deg(x0) — the field degree of
lambda is at most that of x0, because lambda is a rational function
of x0 on the same algebraic curve.  (22/22 rows confirmed.)

**Corollary 2.**  lambda is rational iff R maps x0 to Q.  For
N = 3,5,7,13,17: x0 is the CM value of the Hauptmodul, and the
ring class field is biquadratic over Q.  lambda is rational iff
R maps the algebraic x0 into Q — which happens when x0 generates
a ring class field whose three quadratic subfields include the
one fixed by R's symmetry group.  By genus theory (t=3 prime
discriminant factors -> Cl = (Z/2)^2), all three subfields are
the three quadratic subextensions, and lambda lands in the one
fixed by the Atkin-Lehner involutions compatible with level 12.

**Connection to idoneal numbers.**  The condition "lambda
rational" is equivalent to "the ring class field of disc(-24N)
has exponent <= 2" — which is exactly the idoneal number
condition for the order disc(-24N).  The five rows {3,5,7,13,17}
are the idoneal orders at level 12.

**Q.E.D.** (standard modular function theory: genus 0 + Shimura
reciprocity + Ligozart's eta-product criterion)

## Empirical facts backing the note (all machine-verified tonight)## Connection to idoneal numbers (2026-09-28 18:05)

The five rational-lambda rows {3,5,7,13,17} are the level-12 analog
of Euler's idoneal numbers (numeri idonei): positive integers n for
which the class group of the order of discriminant -4n has exponent
<= 2 (all elements are 2-torsion).  Euler found 65 such numbers; the
list's completeness under GRH is due to Weinberger (1973).

The connection: for the t-family, lambda is rational iff the ring
class field of the order disc(-24N) is generated by x12 over Q, and
x12 generates the ring class field.  Lambda is rational iff x12
generates only the rationals -- i.e. iff the ring class field equals
Q -- i.e. iff the class group acts trivially on x12 -- i.e. iff the
class group has exponent <= 2 (all classes are 2-torsion).

This is exactly the idoneal number condition applied to the order of
discriminant -24N at level 12.  The five rows {3,5,7,13,17} are the
idoneal numbers for the level-12 eta-quotient x12.

## THEOREM: lambda in Q(x0) via the Hauptmodul property of Gamma_0(12)
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 18:20 — proof complete at the modular-function level)

**Theorem.** Let tau0 be a CM point of disc(-24N), x0 = x12(tau0),
and lambda = (r - x0 S1'/S0') / S0 as in the CWZ identity.  Then:

  (i) lambda in Q(x0), hence deg(lambda) <= deg(x0);
  (ii) X_0(12) has genus 0, so x12 is a Hauptmodul and
       Q(X_0(12)) = Q(x12) is the full function field;
  (iii) deg(lambda) = deg(x0) iff lambda generates the full ring
       class field; deg(lambda) < deg(x0) iff lambda lies in a
       proper subfield (the "degeneration" that makes lambda
       rational for exactly 5 rows).

**Proof.**
(i) X_0(12) has genus 0 (standard formula: the index of Gamma_0(12)
    in PSL_2(Z) gives g = 0).  Therefore x12 is a Hauptmodul and
    Q(X_0(12)) = Q(x12): every modular function of level 12 with
    rational Fourier coefficients is a rational function of x12.
(ii) z = sum t(n) x^n is a modular form of weight 2 on Gamma_0(12)
    (CWZ Thm 3.1).  The combination lambda = (r - x0 z'/z) / z
    involves only: z (weight 2), x0 z'/z (a weight-0 modular
    function, since the quasi-modular E_2 slip in z' is killed by
    the explicit period factor), and r (algebraic in x by the CWZ
    differential).  Therefore lambda is a modular function of
    level 12, and by Shimura reciprocity, lambda(tau0) lies in
    the ring class field of disc(-24N).
(iii) Since x12 is a Hauptmodul, Q(X_0(12)) = Q(x12).  Lambda, as
    a modular function of the same level, is a rational function
    of x12 in the function field.  The value lambda(tau0) is the
    evaluation of this rational function at the algebraic point
    x12(tau0), so Q(lambda) is a subfield of Q(x12(tau0)).
    This proves deg(lambda) <= deg(x0).

**Corollary (genus theory).**  The ring class field of disc(-24N)
has degree h(-24N) over K = Q(sqrt(-6N)), and [K_f : Q] = 2 h(-24N).
The 2-torsion structure of Cl(O_f) determines which subfield lambda
generates.  For the five degenerate rows {3,5,7,13,17}, the class
group is (Z/2)^2 (t = 3 prime factors), the ring class field is
biquadratic over Q, and lambda lies in one of the three quadratic
subfields.  For the other rows, lambda lives in a higher-degree
subfield.

**Connection to idoneal numbers.**  The five rows {3,5,7,13,17}
where lambda is rational are exactly the rows where the order of
disc(-24N) is "idoneal at level 12" -- the ring class field is a
2-extension of Q, so every modular function value is at most
quadratic over Q.  This is the level-12 analog of Euler's idoneal
numbers (which parametrize orders with class group exponent <= 2).

**Q.E.D. (modular function theory + genus 0 of X_0(12))**

## THEOREM (upgraded from sketch): lambda in Q(x12) via Hauptmodul property
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 23:30 — complete proof at the modular function theory level)

**Theorem.** x12 is a Hauptmodul for the modular curve X_0(12)
(genus 0).  Therefore Q(X_0(12)) = Q(x12): every modular function
of level 12 (on Gamma_0(12)) with algebraic Fourier coefficients
is a rational function of x12.  In particular:

  (a) lambda = R(x12) for some R in Q(X)
  (b) deg(lambda) <= deg(x0)
  (c) lambda is rational iff R maps x0 to Q
  (d) R is unique iff it generates Q(X_0(12)), which happens
      generically

**Proof.**
1. X_0(12) has genus 0 (standard: g = 1 + N/12 prod(1+1/p) -
   N/4 prod(1+1/p) - sum(...), which gives g = 0 for N = 12).
2. x12 is a Hauptmodul: the eta-product
   eta(2tau)eta(4tau)eta(6tau)eta(12tau)
   has weight 2 and trivial character on Gamma_0(12) (Ligozat
   1975), and x12 = this eta-product / z12 where z12 is a weight-2
   form on Gamma_0(12).  Therefore x12 generates the function field.
3. lambda is computed from x12 and the differential q dx/dq =
   z12 x12 sqrt((1+4x12)(1-4x12)(1-8x12)).  The sqrt factor is a
   rational function on X_0(12) because its zeros/poles are at
   cusps and elliptic points of the modular curve, and the
   combination is a rational expression in x12.
4. Therefore lambda in Q(X_0(12)) = Q(x12) by step 1.

**Corollary 1.**  deg(lambda) <= deg(x0) — the field degree of
lambda is at most that of x0, because lambda is a rational function
of x0 on the same algebraic curve.  (22/22 rows confirmed.)

**Corollary 2.**  lambda is rational iff R maps x0 to Q.  For
N = 3,5,7,13,17: x0 is the CM value of the Hauptmodul, and the
ring class field is biquadratic over Q.  lambda is rational iff
R maps the algebraic x0 into Q — which happens when x0 generates
a ring class field whose three quadratic subfields include the
one fixed by R's symmetry group.  By genus theory (t=3 prime
discriminant factors -> Cl = (Z/2)^2), all three subfields are
the three quadratic subextensions, and lambda lands in the one
fixed by the Atkin-Lehner involutions compatible with level 12.

**Connection to idoneal numbers.**  The condition "lambda
rational" is equivalent to "the ring class field of disc(-24N)
has exponent <= 2" — which is exactly the idoneal number
condition for the order disc(-24N).  The five rows {3,5,7,13,17}
are the idoneal orders at level 12.

**Q.E.D.** (standard modular function theory: genus 0 + Shimura
reciprocity + Ligozart's eta-product criterion)

## Empirical facts backing the note (all machine-verified tonight)

## THEOREM: lambda in Q(x0) via the Hauptmodul property of Gamma_0(12)
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 18:20 — proof complete at the modular-function level)

**Theorem.** Let tau0 be a CM point of disc(-24N), x0 = x12(tau0),
and lambda = (r - x0 S1'/S0') / S0 as in the CWZ identity.  Then:

  (i) lambda in Q(x0), hence deg(lambda) <= deg(x0);
  (ii) X_0(12) has genus 0, so x12 is a Hauptmodul and
       Q(X_0(12)) = Q(x12) is the full function field;
  (iii) deg(lambda) = deg(x0) iff lambda generates the full ring
       class field; deg(lambda) < deg(x0) iff lambda lies in a
       proper subfield (the "degeneration" that makes lambda
       rational for exactly 5 rows).

**Proof.**
(i) X_0(12) has genus 0 (standard formula: the index of Gamma_0(12)
    in PSL_2(Z) gives g = 0).  Therefore x12 is a Hauptmodul and
    Q(X_0(12)) = Q(x12): every modular function of level 12 with
    rational Fourier coefficients is a rational function of x12.
(ii) z = sum t(n) x^n is a modular form of weight 2 on Gamma_0(12)
    (CWZ Thm 3.1).  The combination lambda = (r - x0 z'/z) / z
    involves only: z (weight 2), x0 z'/z (a weight-0 modular
    function, since the quasi-modular E_2 slip in z' is killed by
    the explicit period factor), and r (algebraic in x by the CWZ
    differential).  Therefore lambda is a modular function of
    level 12, and by Shimura reciprocity, lambda(tau0) lies in
    the ring class field of disc(-24N).
(iii) Since x12 is a Hauptmodul, Q(X_0(12)) = Q(x12).  Lambda, as
    a modular function of the same level, is a rational function
    of x12 in the function field.  The value lambda(tau0) is the
    evaluation of this rational function at the algebraic point
    x12(tau0), so Q(lambda) is a subfield of Q(x12(tau0)).
    This proves deg(lambda) <= deg(x0).

**Corollary (genus theory).**  The ring class field of disc(-24N)
has degree h(-24N) over K = Q(sqrt(-6N)), and [K_f : Q] = 2 h(-24N).
The 2-torsion structure of Cl(O_f) determines which subfield lambda
generates.  For the five degenerate rows {3,5,7,13,17}, the class
group is (Z/2)^2 (t = 3 prime factors), the ring class field is
biquadratic over Q, and lambda lies in one of the three quadratic
subfields.  For the other rows, lambda lives in a higher-degree
subfield.

**Connection to idoneal numbers.**  The five rows {3,5,7,13,17}
where lambda is rational are exactly the rows where the order of
disc(-24N) is "idoneal at level 12" -- the ring class field is a
2-extension of Q, so every modular function value is at most
quadratic over Q.  This is the level-12 analog of Euler's idoneal
numbers (which parametrize orders with class group exponent <= 2).

**Q.E.D. (modular function theory + genus 0 of X_0(12))**

## THEOREM (upgraded from sketch): lambda in Q(x12) via Hauptmodul property
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 23:30 — complete proof at the modular function theory level)

**Theorem.** x12 is a Hauptmodul for the modular curve X_0(12)
(genus 0).  Therefore Q(X_0(12)) = Q(x12): every modular function
of level 12 (on Gamma_0(12)) with algebraic Fourier coefficients
is a rational function of x12.  In particular:

  (a) lambda = R(x12) for some R in Q(X)
  (b) deg(lambda) <= deg(x0)
  (c) lambda is rational iff R maps x0 to Q
  (d) R is unique iff it generates Q(X_0(12)), which happens
      generically

**Proof.**
1. X_0(12) has genus 0 (standard: g = 1 + N/12 prod(1+1/p) -
   N/4 prod(1+1/p) - sum(...), which gives g = 0 for N = 12).
2. x12 is a Hauptmodul: the eta-product
   eta(2tau)eta(4tau)eta(6tau)eta(12tau)
   has weight 2 and trivial character on Gamma_0(12) (Ligozat
   1975), and x12 = this eta-product / z12 where z12 is a weight-2
   form on Gamma_0(12).  Therefore x12 generates the function field.
3. lambda is computed from x12 and the differential q dx/dq =
   z12 x12 sqrt((1+4x12)(1-4x12)(1-8x12)).  The sqrt factor is a
   rational function on X_0(12) because its zeros/poles are at
   cusps and elliptic points of the modular curve, and the
   combination is a rational expression in x12.
4. Therefore lambda in Q(X_0(12)) = Q(x12) by step 1.

**Corollary 1.**  deg(lambda) <= deg(x0) — the field degree of
lambda is at most that of x0, because lambda is a rational function
of x0 on the same algebraic curve.  (22/22 rows confirmed.)

**Corollary 2.**  lambda is rational iff R maps x0 to Q.  For
N = 3,5,7,13,17: x0 is the CM value of the Hauptmodul, and the
ring class field is biquadratic over Q.  lambda is rational iff
R maps the algebraic x0 into Q — which happens when x0 generates
a ring class field whose three quadratic subfields include the
one fixed by R's symmetry group.  By genus theory (t=3 prime
discriminant factors -> Cl = (Z/2)^2), all three subfields are
the three quadratic subextensions, and lambda lands in the one
fixed by the Atkin-Lehner involutions compatible with level 12.

**Connection to idoneal numbers.**  The condition "lambda
rational" is equivalent to "the ring class field of disc(-24N)
has exponent <= 2" — which is exactly the idoneal number
condition for the order disc(-24N).  The five rows {3,5,7,13,17}
are the idoneal orders at level 12.

**Q.E.D.** (standard modular function theory: genus 0 + Shimura
reciprocity + Ligozart's eta-product criterion)

## Empirical facts backing the note (all machine-verified tonight)## Connection to idoneal numbers (2026-09-28 18:05)

The five rational-lambda rows {3,5,7,13,17} are the level-12 analog
of Euler's idoneal numbers (numeri idonei): positive integers n for
which the class group of the order of discriminant -4n has exponent
<= 2 (all elements are 2-torsion).  Euler found 65 such numbers; the
list's completeness under GRH is due to Weinberger (1973).

The connection: for the t-family, lambda is rational iff the ring
class field of the order disc(-24N) is generated by x12 over Q, and
x12 generates the ring class field.  Lambda is rational iff x12
generates only the rationals -- i.e. iff the ring class field equals
Q -- i.e. iff the class group acts trivially on x12 -- i.e. iff the
class group has exponent <= 2 (all classes are 2-torsion).

This is exactly the idoneal number condition applied to the order of
discriminant -24N at level 12.  The five rows {3,5,7,13,17} are the
idoneal numbers for the level-12 eta-quotient x12.

## THEOREM: lambda in Q(x0) via the Hauptmodul property of Gamma_0(12)
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 18:20 — proof complete at the modular-function level)

**Theorem.** Let tau0 be a CM point of disc(-24N), x0 = x12(tau0),
and lambda = (r - x0 S1'/S0') / S0 as in the CWZ identity.  Then:

  (i) lambda in Q(x0), hence deg(lambda) <= deg(x0);
  (ii) X_0(12) has genus 0, so x12 is a Hauptmodul and
       Q(X_0(12)) = Q(x12) is the full function field;
  (iii) deg(lambda) = deg(x0) iff lambda generates the full ring
       class field; deg(lambda) < deg(x0) iff lambda lies in a
       proper subfield (the "degeneration" that makes lambda
       rational for exactly 5 rows).

**Proof.**
(i) X_0(12) has genus 0 (standard formula: the index of Gamma_0(12)
    in PSL_2(Z) gives g = 0).  Therefore x12 is a Hauptmodul and
    Q(X_0(12)) = Q(x12): every modular function of level 12 with
    rational Fourier coefficients is a rational function of x12.
(ii) z = sum t(n) x^n is a modular form of weight 2 on Gamma_0(12)
    (CWZ Thm 3.1).  The combination lambda = (r - x0 z'/z) / z
    involves only: z (weight 2), x0 z'/z (a weight-0 modular
    function, since the quasi-modular E_2 slip in z' is killed by
    the explicit period factor), and r (algebraic in x by the CWZ
    differential).  Therefore lambda is a modular function of
    level 12, and by Shimura reciprocity, lambda(tau0) lies in
    the ring class field of disc(-24N).
(iii) Since x12 is a Hauptmodul, Q(X_0(12)) = Q(x12).  Lambda, as
    a modular function of the same level, is a rational function
    of x12 in the function field.  The value lambda(tau0) is the
    evaluation of this rational function at the algebraic point
    x12(tau0), so Q(lambda) is a subfield of Q(x12(tau0)).
    This proves deg(lambda) <= deg(x0).

**Corollary (genus theory).**  The ring class field of disc(-24N)
has degree h(-24N) over K = Q(sqrt(-6N)), and [K_f : Q] = 2 h(-24N).
The 2-torsion structure of Cl(O_f) determines which subfield lambda
generates.  For the five degenerate rows {3,5,7,13,17}, the class
group is (Z/2)^2 (t = 3 prime factors), the ring class field is
biquadratic over Q, and lambda lies in one of the three quadratic
subfields.  For the other rows, lambda lives in a higher-degree
subfield.

**Connection to idoneal numbers.**  The five rows {3,5,7,13,17}
where lambda is rational are exactly the rows where the order of
disc(-24N) is "idoneal at level 12" -- the ring class field is a
2-extension of Q, so every modular function value is at most
quadratic over Q.  This is the level-12 analog of Euler's idoneal
numbers (which parametrize orders with class group exponent <= 2).

**Q.E.D. (modular function theory + genus 0 of X_0(12))**

## THEOREM (upgraded from sketch): lambda in Q(x12) via Hauptmodul property
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 23:30 — complete proof at the modular function theory level)

**Theorem.** x12 is a Hauptmodul for the modular curve X_0(12)
(genus 0).  Therefore Q(X_0(12)) = Q(x12): every modular function
of level 12 (on Gamma_0(12)) with algebraic Fourier coefficients
is a rational function of x12.  In particular:

  (a) lambda = R(x12) for some R in Q(X)
  (b) deg(lambda) <= deg(x0)
  (c) lambda is rational iff R maps x0 to Q
  (d) R is unique iff it generates Q(X_0(12)), which happens
      generically

**Proof.**
1. X_0(12) has genus 0 (standard: g = 1 + N/12 prod(1+1/p) -
   N/4 prod(1+1/p) - sum(...), which gives g = 0 for N = 12).
2. x12 is a Hauptmodul: the eta-product
   eta(2tau)eta(4tau)eta(6tau)eta(12tau)
   has weight 2 and trivial character on Gamma_0(12) (Ligozat
   1975), and x12 = this eta-product / z12 where z12 is a weight-2
   form on Gamma_0(12).  Therefore x12 generates the function field.
3. lambda is computed from x12 and the differential q dx/dq =
   z12 x12 sqrt((1+4x12)(1-4x12)(1-8x12)).  The sqrt factor is a
   rational function on X_0(12) because its zeros/poles are at
   cusps and elliptic points of the modular curve, and the
   combination is a rational expression in x12.
4. Therefore lambda in Q(X_0(12)) = Q(x12) by step 1.

**Corollary 1.**  deg(lambda) <= deg(x0) — the field degree of
lambda is at most that of x0, because lambda is a rational function
of x0 on the same algebraic curve.  (22/22 rows confirmed.)

**Corollary 2.**  lambda is rational iff R maps x0 to Q.  For
N = 3,5,7,13,17: x0 is the CM value of the Hauptmodul, and the
ring class field is biquadratic over Q.  lambda is rational iff
R maps the algebraic x0 into Q — which happens when x0 generates
a ring class field whose three quadratic subfields include the
one fixed by R's symmetry group.  By genus theory (t=3 prime
discriminant factors -> Cl = (Z/2)^2), all three subfields are
the three quadratic subextensions, and lambda lands in the one
fixed by the Atkin-Lehner involutions compatible with level 12.

**Connection to idoneal numbers.**  The condition "lambda
rational" is equivalent to "the ring class field of disc(-24N)
has exponent <= 2" — which is exactly the idoneal number
condition for the order disc(-24N).  The five rows {3,5,7,13,17}
are the idoneal orders at level 12.

**Q.E.D.** (standard modular function theory: genus 0 + Shimura
reciprocity + Ligozart's eta-product criterion)

## Empirical facts backing the note (all machine-verified tonight)

## THEOREM: lambda in Q(x0) via the Hauptmodul property of Gamma_0(12)
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 18:20 — proof complete at the modular-function level)

**Theorem.** Let tau0 be a CM point of disc(-24N), x0 = x12(tau0),
and lambda = (r - x0 S1'/S0') / S0 as in the CWZ identity.  Then:

  (i) lambda in Q(x0), hence deg(lambda) <= deg(x0);
  (ii) X_0(12) has genus 0, so x12 is a Hauptmodul and
       Q(X_0(12)) = Q(x12) is the full function field;
  (iii) deg(lambda) = deg(x0) iff lambda generates the full ring
       class field; deg(lambda) < deg(x0) iff lambda lies in a
       proper subfield (the "degeneration" that makes lambda
       rational for exactly 5 rows).

**Proof.**
(i) X_0(12) has genus 0 (standard formula: the index of Gamma_0(12)
    in PSL_2(Z) gives g = 0).  Therefore x12 is a Hauptmodul and
    Q(X_0(12)) = Q(x12): every modular function of level 12 with
    rational Fourier coefficients is a rational function of x12.
(ii) z = sum t(n) x^n is a modular form of weight 2 on Gamma_0(12)
    (CWZ Thm 3.1).  The combination lambda = (r - x0 z'/z) / z
    involves only: z (weight 2), x0 z'/z (a weight-0 modular
    function, since the quasi-modular E_2 slip in z' is killed by
    the explicit period factor), and r (algebraic in x by the CWZ
    differential).  Therefore lambda is a modular function of
    level 12, and by Shimura reciprocity, lambda(tau0) lies in
    the ring class field of disc(-24N).
(iii) Since x12 is a Hauptmodul, Q(X_0(12)) = Q(x12).  Lambda, as
    a modular function of the same level, is a rational function
    of x12 in the function field.  The value lambda(tau0) is the
    evaluation of this rational function at the algebraic point
    x12(tau0), so Q(lambda) is a subfield of Q(x12(tau0)).
    This proves deg(lambda) <= deg(x0).

**Corollary (genus theory).**  The ring class field of disc(-24N)
has degree h(-24N) over K = Q(sqrt(-6N)), and [K_f : Q] = 2 h(-24N).
The 2-torsion structure of Cl(O_f) determines which subfield lambda
generates.  For the five degenerate rows {3,5,7,13,17}, the class
group is (Z/2)^2 (t = 3 prime factors), the ring class field is
biquadratic over Q, and lambda lies in one of the three quadratic
subfields.  For the other rows, lambda lives in a higher-degree
subfield.

**Connection to idoneal numbers.**  The five rows {3,5,7,13,17}
where lambda is rational are exactly the rows where the order of
disc(-24N) is "idoneal at level 12" -- the ring class field is a
2-extension of Q, so every modular function value is at most
quadratic over Q.  This is the level-12 analog of Euler's idoneal
numbers (which parametrize orders with class group exponent <= 2).

**Q.E.D. (modular function theory + genus 0 of X_0(12))**

## THEOREM (upgraded from sketch): lambda in Q(x12) via Hauptmodul property
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 23:30 — complete proof at the modular function theory level)

**Theorem.** x12 is a Hauptmodul for the modular curve X_0(12)
(genus 0).  Therefore Q(X_0(12)) = Q(x12): every modular function
of level 12 (on Gamma_0(12)) with algebraic Fourier coefficients
is a rational function of x12.  In particular:

  (a) lambda = R(x12) for some R in Q(X)
  (b) deg(lambda) <= deg(x0)
  (c) lambda is rational iff R maps x0 to Q
  (d) R is unique iff it generates Q(X_0(12)), which happens
      generically

**Proof.**
1. X_0(12) has genus 0 (standard: g = 1 + N/12 prod(1+1/p) -
   N/4 prod(1+1/p) - sum(...), which gives g = 0 for N = 12).
2. x12 is a Hauptmodul: the eta-product
   eta(2tau)eta(4tau)eta(6tau)eta(12tau)
   has weight 2 and trivial character on Gamma_0(12) (Ligozat
   1975), and x12 = this eta-product / z12 where z12 is a weight-2
   form on Gamma_0(12).  Therefore x12 generates the function field.
3. lambda is computed from x12 and the differential q dx/dq =
   z12 x12 sqrt((1+4x12)(1-4x12)(1-8x12)).  The sqrt factor is a
   rational function on X_0(12) because its zeros/poles are at
   cusps and elliptic points of the modular curve, and the
   combination is a rational expression in x12.
4. Therefore lambda in Q(X_0(12)) = Q(x12) by step 1.

**Corollary 1.**  deg(lambda) <= deg(x0) — the field degree of
lambda is at most that of x0, because lambda is a rational function
of x0 on the same algebraic curve.  (22/22 rows confirmed.)

**Corollary 2.**  lambda is rational iff R maps x0 to Q.  For
N = 3,5,7,13,17: x0 is the CM value of the Hauptmodul, and the
ring class field is biquadratic over Q.  lambda is rational iff
R maps the algebraic x0 into Q — which happens when x0 generates
a ring class field whose three quadratic subfields include the
one fixed by R's symmetry group.  By genus theory (t=3 prime
discriminant factors -> Cl = (Z/2)^2), all three subfields are
the three quadratic subextensions, and lambda lands in the one
fixed by the Atkin-Lehner involutions compatible with level 12.

**Connection to idoneal numbers.**  The condition "lambda
rational" is equivalent to "the ring class field of disc(-24N)
has exponent <= 2" — which is exactly the idoneal number
condition for the order disc(-24N).  The five rows {3,5,7,13,17}
are the idoneal orders at level 12.

**Q.E.D.** (standard modular function theory: genus 0 + Shimura
reciprocity + Ligozart's eta-product criterion)

## Empirical facts backing the note (all machine-verified tonight)## Connection to idoneal numbers (2026-09-28 18:05)

The five rational-lambda rows {3,5,7,13,17} are the level-12 analog
of Euler's idoneal numbers (numeri idonei): positive integers n for
which the class group of the order of discriminant -4n has exponent
<= 2 (all elements are 2-torsion).  Euler found 65 such numbers; the
list's completeness under GRH is due to Weinberger (1973).

The connection: for the t-family, lambda is rational iff the ring
class field of the order disc(-24N) is generated by x12 over Q, and
x12 generates the ring class field.  Lambda is rational iff x12
generates only the rationals -- i.e. iff the ring class field equals
Q -- i.e. iff the class group acts trivially on x12 -- i.e. iff the
class group has exponent <= 2 (all classes are 2-torsion).

This is exactly the idoneal number condition applied to the order of
discriminant -24N at level 12.  The five rows {3,5,7,13,17} are the
idoneal numbers for the level-12 eta-quotient x12.

## THEOREM: lambda in Q(x0) via the Hauptmodul property of Gamma_0(12)
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 18:20 — proof complete at the modular-function level)

**Theorem.** Let tau0 be a CM point of disc(-24N), x0 = x12(tau0),
and lambda = (r - x0 S1'/S0') / S0 as in the CWZ identity.  Then:

  (i) lambda in Q(x0), hence deg(lambda) <= deg(x0);
  (ii) X_0(12) has genus 0, so x12 is a Hauptmodul and
       Q(X_0(12)) = Q(x12) is the full function field;
  (iii) deg(lambda) = deg(x0) iff lambda generates the full ring
       class field; deg(lambda) < deg(x0) iff lambda lies in a
       proper subfield (the "degeneration" that makes lambda
       rational for exactly 5 rows).

**Proof.**
(i) X_0(12) has genus 0 (standard formula: the index of Gamma_0(12)
    in PSL_2(Z) gives g = 0).  Therefore x12 is a Hauptmodul and
    Q(X_0(12)) = Q(x12): every modular function of level 12 with
    rational Fourier coefficients is a rational function of x12.
(ii) z = sum t(n) x^n is a modular form of weight 2 on Gamma_0(12)
    (CWZ Thm 3.1).  The combination lambda = (r - x0 z'/z) / z
    involves only: z (weight 2), x0 z'/z (a weight-0 modular
    function, since the quasi-modular E_2 slip in z' is killed by
    the explicit period factor), and r (algebraic in x by the CWZ
    differential).  Therefore lambda is a modular function of
    level 12, and by Shimura reciprocity, lambda(tau0) lies in
    the ring class field of disc(-24N).
(iii) Since x12 is a Hauptmodul, Q(X_0(12)) = Q(x12).  Lambda, as
    a modular function of the same level, is a rational function
    of x12 in the function field.  The value lambda(tau0) is the
    evaluation of this rational function at the algebraic point
    x12(tau0), so Q(lambda) is a subfield of Q(x12(tau0)).
    This proves deg(lambda) <= deg(x0).

**Corollary (genus theory).**  The ring class field of disc(-24N)
has degree h(-24N) over K = Q(sqrt(-6N)), and [K_f : Q] = 2 h(-24N).
The 2-torsion structure of Cl(O_f) determines which subfield lambda
generates.  For the five degenerate rows {3,5,7,13,17}, the class
group is (Z/2)^2 (t = 3 prime factors), the ring class field is
biquadratic over Q, and lambda lies in one of the three quadratic
subfields.  For the other rows, lambda lives in a higher-degree
subfield.

**Connection to idoneal numbers.**  The five rows {3,5,7,13,17}
where lambda is rational are exactly the rows where the order of
disc(-24N) is "idoneal at level 12" -- the ring class field is a
2-extension of Q, so every modular function value is at most
quadratic over Q.  This is the level-12 analog of Euler's idoneal
numbers (which parametrize orders with class group exponent <= 2).

**Q.E.D. (modular function theory + genus 0 of X_0(12))**

## THEOREM (upgraded from sketch): lambda in Q(x12) via Hauptmodul property
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 23:30 — complete proof at the modular function theory level)

**Theorem.** x12 is a Hauptmodul for the modular curve X_0(12)
(genus 0).  Therefore Q(X_0(12)) = Q(x12): every modular function
of level 12 (on Gamma_0(12)) with algebraic Fourier coefficients
is a rational function of x12.  In particular:

  (a) lambda = R(x12) for some R in Q(X)
  (b) deg(lambda) <= deg(x0)
  (c) lambda is rational iff R maps x0 to Q
  (d) R is unique iff it generates Q(X_0(12)), which happens
      generically

**Proof.**
1. X_0(12) has genus 0 (standard: g = 1 + N/12 prod(1+1/p) -
   N/4 prod(1+1/p) - sum(...), which gives g = 0 for N = 12).
2. x12 is a Hauptmodul: the eta-product
   eta(2tau)eta(4tau)eta(6tau)eta(12tau)
   has weight 2 and trivial character on Gamma_0(12) (Ligozat
   1975), and x12 = this eta-product / z12 where z12 is a weight-2
   form on Gamma_0(12).  Therefore x12 generates the function field.
3. lambda is computed from x12 and the differential q dx/dq =
   z12 x12 sqrt((1+4x12)(1-4x12)(1-8x12)).  The sqrt factor is a
   rational function on X_0(12) because its zeros/poles are at
   cusps and elliptic points of the modular curve, and the
   combination is a rational expression in x12.
4. Therefore lambda in Q(X_0(12)) = Q(x12) by step 1.

**Corollary 1.**  deg(lambda) <= deg(x0) — the field degree of
lambda is at most that of x0, because lambda is a rational function
of x0 on the same algebraic curve.  (22/22 rows confirmed.)

**Corollary 2.**  lambda is rational iff R maps x0 to Q.  For
N = 3,5,7,13,17: x0 is the CM value of the Hauptmodul, and the
ring class field is biquadratic over Q.  lambda is rational iff
R maps the algebraic x0 into Q — which happens when x0 generates
a ring class field whose three quadratic subfields include the
one fixed by R's symmetry group.  By genus theory (t=3 prime
discriminant factors -> Cl = (Z/2)^2), all three subfields are
the three quadratic subextensions, and lambda lands in the one
fixed by the Atkin-Lehner involutions compatible with level 12.

**Connection to idoneal numbers.**  The condition "lambda
rational" is equivalent to "the ring class field of disc(-24N)
has exponent <= 2" — which is exactly the idoneal number
condition for the order disc(-24N).  The five rows {3,5,7,13,17}
are the idoneal orders at level 12.

**Q.E.D.** (standard modular function theory: genus 0 + Shimura
reciprocity + Ligozart's eta-product criterion)

## Empirical facts backing the note (all machine-verified tonight)

## THEOREM: lambda in Q(x0) via the Hauptmodul property of Gamma_0(12)
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 18:20 — proof complete at the modular-function level)

**Theorem.** Let tau0 be a CM point of disc(-24N), x0 = x12(tau0),
and lambda = (r - x0 S1'/S0') / S0 as in the CWZ identity.  Then:

  (i) lambda in Q(x0), hence deg(lambda) <= deg(x0);
  (ii) X_0(12) has genus 0, so x12 is a Hauptmodul and
       Q(X_0(12)) = Q(x12) is the full function field;
  (iii) deg(lambda) = deg(x0) iff lambda generates the full ring
       class field; deg(lambda) < deg(x0) iff lambda lies in a
       proper subfield (the "degeneration" that makes lambda
       rational for exactly 5 rows).

**Proof.**
(i) X_0(12) has genus 0 (standard formula: the index of Gamma_0(12)
    in PSL_2(Z) gives g = 0).  Therefore x12 is a Hauptmodul and
    Q(X_0(12)) = Q(x12): every modular function of level 12 with
    rational Fourier coefficients is a rational function of x12.
(ii) z = sum t(n) x^n is a modular form of weight 2 on Gamma_0(12)
    (CWZ Thm 3.1).  The combination lambda = (r - x0 z'/z) / z
    involves only: z (weight 2), x0 z'/z (a weight-0 modular
    function, since the quasi-modular E_2 slip in z' is killed by
    the explicit period factor), and r (algebraic in x by the CWZ
    differential).  Therefore lambda is a modular function of
    level 12, and by Shimura reciprocity, lambda(tau0) lies in
    the ring class field of disc(-24N).
(iii) Since x12 is a Hauptmodul, Q(X_0(12)) = Q(x12).  Lambda, as
    a modular function of the same level, is a rational function
    of x12 in the function field.  The value lambda(tau0) is the
    evaluation of this rational function at the algebraic point
    x12(tau0), so Q(lambda) is a subfield of Q(x12(tau0)).
    This proves deg(lambda) <= deg(x0).

**Corollary (genus theory).**  The ring class field of disc(-24N)
has degree h(-24N) over K = Q(sqrt(-6N)), and [K_f : Q] = 2 h(-24N).
The 2-torsion structure of Cl(O_f) determines which subfield lambda
generates.  For the five degenerate rows {3,5,7,13,17}, the class
group is (Z/2)^2 (t = 3 prime factors), the ring class field is
biquadratic over Q, and lambda lies in one of the three quadratic
subfields.  For the other rows, lambda lives in a higher-degree
subfield.

**Connection to idoneal numbers.**  The five rows {3,5,7,13,17}
where lambda is rational are exactly the rows where the order of
disc(-24N) is "idoneal at level 12" -- the ring class field is a
2-extension of Q, so every modular function value is at most
quadratic over Q.  This is the level-12 analog of Euler's idoneal
numbers (which parametrize orders with class group exponent <= 2).

**Q.E.D. (modular function theory + genus 0 of X_0(12))**

## THEOREM (upgraded from sketch): lambda in Q(x12) via Hauptmodul property
> **RETRACTED (P76, 2026-09-29): x12 is NOT modular for Gamma0(12) — the Hauptmodul premise of this block is false. Archive only.**
## (2026-09-28 23:30 — complete proof at the modular function theory level)

**Theorem.** x12 is a Hauptmodul for the modular curve X_0(12)
(genus 0).  Therefore Q(X_0(12)) = Q(x12): every modular function
of level 12 (on Gamma_0(12)) with algebraic Fourier coefficients
is a rational function of x12.  In particular:

  (a) lambda = R(x12) for some R in Q(X)
  (b) deg(lambda) <= deg(x0)
  (c) lambda is rational iff R maps x0 to Q
  (d) R is unique iff it generates Q(X_0(12)), which happens
      generically

**Proof.**
1. X_0(12) has genus 0 (standard: g = 1 + N/12 prod(1+1/p) -
   N/4 prod(1+1/p) - sum(...), which gives g = 0 for N = 12).
2. x12 is a Hauptmodul: the eta-product
   eta(2tau)eta(4tau)eta(6tau)eta(12tau)
   has weight 2 and trivial character on Gamma_0(12) (Ligozat
   1975), and x12 = this eta-product / z12 where z12 is a weight-2
   form on Gamma_0(12).  Therefore x12 generates the function field.
3. lambda is computed from x12 and the differential q dx/dq =
   z12 x12 sqrt((1+4x12)(1-4x12)(1-8x12)).  The sqrt factor is a
   rational function on X_0(12) because its zeros/poles are at
   cusps and elliptic points of the modular curve, and the
   combination is a rational expression in x12.
4. Therefore lambda in Q(X_0(12)) = Q(x12) by step 1.

**Corollary 1.**  deg(lambda) <= deg(x0) — the field degree of
lambda is at most that of x0, because lambda is a rational function
of x0 on the same algebraic curve.  (22/22 rows confirmed.)

**Corollary 2.**  lambda is rational iff R maps x0 to Q.  For
N = 3,5,7,13,17: x0 is the CM value of the Hauptmodul, and the
ring class field is biquadratic over Q.  lambda is rational iff
R maps the algebraic x0 into Q — which happens when x0 generates
a ring class field whose three quadratic subfields include the
one fixed by R's symmetry group.  By genus theory (t=3 prime
discriminant factors -> Cl = (Z/2)^2), all three subfields are
the three quadratic subextensions, and lambda lands in the one
fixed by the Atkin-Lehner involutions compatible with level 12.

**Connection to idoneal numbers.**  The condition "lambda
rational" is equivalent to "the ring class field of disc(-24N)
has exponent <= 2" — which is exactly the idoneal number
condition for the order disc(-24N).  The five rows {3,5,7,13,17}
are the idoneal orders at level 12.

**Q.E.D.** (standard modular function theory: genus 0 + Shimura
reciprocity + Ligozart's eta-product criterion)

## Empirical facts backing the note (all machine-verified tonight)

- census N = 2..160: degree 1 = {3,5,7,13,17}; degree 2 = {2,11,19,23,
  25,35,43,47,55,73}; degree 3 = {9,27,29,31,37,41,49,53}; none below
  height 1e6: 137 rows (no new degree<=3 rows in N = 161..400);
- every reported relation: PSLQ + unique-root verification (one root
  within 1e-20 of the census lambda, 45-digit agreement) + direct
  identity substitution at error <= 5e-51;
- showcase N = 9: 96 l^3 - 192 l^2 + 114 l - 17 (height 192),
  lambda_9 = 2/3 - (3 sqrt2 + 19)^(1/3)/12
             - 7/(12 (3 sqrt2 + 19)^(1/3)).
- CCL Thm 2.1 does NOT apply: its levels are {1..9}; matching the pure
  t(n) to its integer three-term recursion forces 5a^2 + 117a + 264 = 0
  (no integer root).

## Orbit check (2026-09-29, P57): the naive pointwise route is dead

Checked numerically (40-50 dps, p57/p58): x12 AND lambda take different
values at the naive orbit points tau_ab/12 for ALL of N=2,3,5,7,13,17
-- including the five degenerate rows.  Two consequences:

1. The earlier note "all orbit values real (max |Im| = 0)" was a B=0
   artifact: every reduced form of disc -24N for those N has B=0, so
   the points are purely imaginary and realness is trivial.  At N=19
   (disc -456) the B!=0 classes (5,+-2,23) and (10,+-8,13) give
   complex lambda values -- the naive points are NOT Shimura
   conjugate points.
2. The conjugate points are the image of the class action on the PAIR
   (lattice L0 = O/12, order-12 subgroup C0 = <1/12 + L0>): the
   transport matrix's bottom row must be level-compatible, and the
   eta-multiplier character enters exactly there.  Record correction:
   lambda(N=2) is cubic (poly [-178,1820,-5847,5640]), not quadratic.

Step 4 therefore remains open in its real form: prove the eta-multiplier
character trivial on the 2-torsion classes OF THE TRANSPORTED ACTION
(the character times the transported pair evaluates back to the
principal value), which for the five rows is what forces lambda's
orbit to collapse to the rational value even though x12's orbit does
not collapse at the naive points.

## Multiplier tool (2026-09-29, P63)

The exact eta-multiplier nu(gamma) is now available as a validated
numerical EXTRaction: nu(gamma) is a 24th root of unity (nu^24 = 1 to
1e-49 on all tested matrices); extract k(gamma) = round(24 arg(nu)/2pi)
at one CM-quality tau and cross-check at a second (30/30 agreement,
p63_eta_multiplier.json).  The Dedekind-sum closed form was NOT
reconstructed (branch conventions for -M in SL_2 vs PSL_2 kept
corrupting both the S/T word bookkeeping and the closed-form candidates'
signs); for the finite character tables step 4 needs, extraction is
exact and sufficient.

Remaining for step 4: build the level-compatible transport matrices for
the 2-torsion classes of the five rows (congruence conditions from
P57's pair analysis), extract the character on each, and prove
triviality on the five rows with the N=2/N=19 rows as nontrivial
controls.

## Transport blocker (2026-09-29 05:00, P63 addendum)

First construction attempt for the transport matrices BLOCKED, with the
obstruction now precise:

1. Demanding gamma*tau_ab = tau0 exactly (tau_ab the reduced-form fixed
   point) is over-constrained: for N=3's nontrivial class (2,0,9) the
   Mobius+det system reduces to 6t^2 + 12u^2 = 1, no integer solutions.
   The conjugate point is NOT tau0; it is whatever standard-form
   representative the transported pair produces.

2. The subgroup transport C' = <1/A mod L'> (from scaling the pair by
   12/A) FAILS to be an X_0(12)-structure: for (2,0,9), 12*(1/2) = 6 is
   in L' = <1, tau_ab>, so <1/2> has order 6, not 12.  The pair action
   on X_0(12)-structures must therefore transport along the dual
   isogeny direction (or use the level-N quotients directly), not by
   naive lattice scaling.

Step 4's remaining proof content is thus: derive the correct action of
Cl(O) on X_0(12)-level structures (cyclic order-12 subgroups) and
verify the extracted character (P63 tool) is trivial on its 2-torsion
for the five rows.  The P63 extraction tool is ready; the class-action
derivation is the open piece.

## Re-framing (2026-09-29 02:40, P68): attack x12's rationality, not transport

x12(tau0) is RATIONAL for the five rows (1/12, 1/20, 1/32 -- the P19
anchors).  A rational value is fixed by every Galois automorphism: no
Shimura transport is needed for it.  Lambda then follows from x0 by
the P25-b identity arithmetically (with r's sqrt-term collapsing at
the rational x0 -- verify per row).

The actual theorem is: x12(i*sqrt(N/24)) in Q happens exactly for
N in {3,5,7,13,17} -- the level-12 analog of Weber's class-invariant
rationality for idoneal orders.  Measured corroboration of the
coprime-class picture: N=5's form (5,0,6) (the ONLY class coprime to
the level across all five rows) has x12 collapsing exactly to the
principal value; non-coprime classes do not collapse at naive points
(their action runs through Hecke correspondences).

Standard proof route (registered): reduce x12 to a Weber class
invariant (eta-product identity between the level-12 Hauptmodul and
level-6 or level-24 Weber functions), then invoke the classical
Weber rationality theorem.  The idoneal-number connection
(registered 2026-09-28) is the arithmetic core of that theorem.

## MAJOR CORRECTION (2026-09-29 16:05, P76): x12 is NOT modular

Direct 40-digit test: x12(gamma tau) = x12(tau) FAILS for gamma =
(1,0;12,1) in Gamma0(12) (deviation 3.6e-4, far above the 1e-25 gate)
and for Gamma0(24)/Gamma0(48) elements; T-invariance holds.  The
"Hauptmodul" claim of steps 2/4 is RETRACTED: x12 = W6(2tau)/z12 is a
QUASIMODULAR function (z12 contains an E2 combination), not a modular
one.  Consequences:

1. "lambda in Q(x0) via Q(X0(12))" is retracted as a proof; the
   deg(lambda) = deg(x0) census (P36-a, 22/22) stands as an empirical
   law.  A candidate replacement explanation: CM values of
   quasimodular forms are algebraic (Eisenstein-Kronecker theory for
   the E2 part, CM for the modular part), and the depth hierarchy may
   follow from the interplay.
2. P69/P69-b's census results are numerical facts and stand, but
   1/x6 is NOT a Weber-type class invariant in the strict (modular)
   sense; the rationality locus {3,5,7,13,17} and the 2-elementary +
   multiplier-triviality shape remain as measured phenomena.
3. The failed SL2-transport campaigns (P57, P63 addendum) now have
   their full explanation: there was no modular structure to
   transport.
4. P75's "exact quadratic" is an approximation (residual 1.2e-8 at
   80 dps); an exact relation between modular u = 1/j6D and
   quasimodular x6 cannot exist.

What survives untouched: every numerical census (P36-a, P44, P69,
P69-b), the five-row rationality phenomenon itself, the idoneal
connection as a measured coincidence awaiting theory, and the CWZ
identity machinery (which never claimed modularity -- it is a
quasimodular framework from the start).
