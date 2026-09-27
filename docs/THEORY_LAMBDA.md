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
