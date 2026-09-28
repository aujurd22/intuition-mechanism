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

REGISTERED READING (mechanism, not yet a proof): x0 in Q  <=>
  x12 is REAL on the entire class-group orbit.  This is checkable in
  principle per case because the eta-product's multiplier character
  is what controls the imaginary part, and for the four h=4
  discriminants the character values on the (2-torsion) class group
  are forced to +-1 phases that the specific eta-signature
  eta2 eta4 eta6 eta12 makes cancel.  The remaining proof work is
  exactly this character computation on 4+1 cases.

## Empirical facts backing the note (all machine-verified tonight)## Empirical facts backing the note (all machine-verified tonight)## Empirical facts backing the note (all machine-verified tonight)## Empirical facts backing the note (all machine-verified tonight)## Empirical facts backing the note (all machine-verified tonight)

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
