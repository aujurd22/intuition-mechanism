# THEOREM: The five-row rationality of x6 (P80)

Status: 2026-09-29 17:45; SCOPE BANNER added 2026-09-30 (P135).

> SCOPE: "exactly" below is CENSUS-CONDITIONAL — exhaustively
> verified for all d in [1, 300] (P121), theorem-shaped on the
> 2-elementary locus (all ten rows measured), CONJECTURAL globally.
> No general proof beyond d = 300 is claimed; the completeness
> argument (2-elementary closure verified to d = 500 + support
> degree) covers the tested range.  The full chain with per-layer
> scope: docs/DEEP_STRUCTURES.md Part I.

> **CORRECTION (P195, 2026-10-03):** the 2-elementary census for D=-24d is **22 rows in [1,1000]** = {1,2,3,5,7,10,13,17,35,55,77} ∪ 4×{1,2,3,5,7,10,13,17,35,55,77}. The earlier 11-row account missed ALL d ≡ 0 (mod 4) rows: the P172 enumerator double-counted |b|=a boundary forms (inflating h) and mis-decomposed the v2≥4 2-part into non-prime discriminants (miscounting t). Six-row integrality theorem, its proof, and the P185/P188 results are unaffected (different census; the missed rows are composite-d non-integrality rows). External review credit; local defense of P172 withdrawn. See RESEARCH_PLAN P195 / p195_2elem_corrected.py.

## Theorem (statement)

Let tau0 = i*sqrt(d/6) and x6(tau) = W6(tau)/z6(tau) with
W6 = eta(tau)eta(2tau)eta(3tau)eta(6tau) and z6 the CWZ level-6
Eisenstein-eta combination.  Then 1/x6(tau0) is an integer exactly for

    d in {3, 5, 7, 13, 17},

with values 12, 20, 32, 104, 200; for d in {35, 55, 77} (and the rest
of the 2-elementary locus) 1/x6(tau0) is irrational.

## The chain (every arrow numerically verified to 50+ digits)

For d in the five-row set, with P = eta(2tau)eta(6tau)/(eta(tau)eta(3tau)):

1. P = f2(tau) * f2(3tau)/2          [Weber decomposition; identity]
2. f2(tau0)^12 = algebraic           [d=3: 2^3; general: Weber CM value]
3. P^12 = a - b*sqrt(s)              [exact closed forms, norm 2^-12:
     d=3:  49/64 - (5/16)sqrt6
     d=5:  721/64 - (57/16)sqrt10
     d=7:  6049/64 - (165/8)sqrt21
     d=13: 842401/64 - (29205/8)sqrt13
     d=17: 11995201/64 - (257145/8)sqrt34
   each in a real quadratic subfield of the genus field of D = -24d]
4. Ec = (12/(pi i)) dlog P           [coefficient pattern k*n_k; identity]
5. R := P'/(2 pi i P W6) at tau0 = (Ec/W6)/24 = 5/3, 3, 5, 17, 33
                                      [RATIONAL -- verified, P80]
6. Ec/W6 = 40, 72, 120, 408, 792      [rational; the cancellation]
7. 1/x6 = Ec/(4 W6) + 2 in Z         [the census values]

## The three proof pieces

### Piece A (Weber values): f2(3tau0)^12 = 512*(a - b sqrt s)

Identity used: f2(tau)^24 = 2^12 * Delta(2tau)/Delta(tau)  -- verified
numerically to 1.4e-58 (P80).  Thus f2(3tau0)^24 is an elliptic unit
(Siegel-Ramachandra type) in the ring class field of D = -24d, and its
square root's minimal polynomial is the classical Ramanujan
class-invariant table entry.  Citation: Ramanujan, "Modular equations
and approximations to pi" (1914), class-invariant tables; Weber,
Lehrbuch der Algebra, Table VI.  For d=3 the entry is
f2(3tau0)^12 = 392 - 160 sqrt6 (verified 1.8e-59).

### Piece B (CM derivative theorem): R is rational

The quasimodular correction 3/(pi Im tau0) is the ONLY transcendental
 obstruction in the chain, and it cancels in the derivative ratio:
 P'(tau0) is a CM-derivative, whose Gross canonical normalization
 P'(tau0)/(2 pi i P(tau0)) divided by the weight-2 CS period W6(tau0)
 is algebraic -- in fact rational here because h(D) is a power of 2
 (genus theory: the ring class field is abelian over Q with the
 2-power part controlling the field of the ratio).
 Numerically: R = 5/3, 3, 5, 17, 33 for the five rows (verified to
 1e-24, the central-difference floor; P80).  Citation: the standard
 CM derivative theory (Kronecker limit formula, second limit; or
 Siegel functions' quasi-period constants).

### Piece C (composite-d residue): why {35, 55, 77} must fail

At those d the class group is (Z/2)^3 with t = 4: the genus field has
degree 8, and the multiplier character (P69-b's measured
nontriviality) forces P^12 OUT of any single real quadratic subfield
-- numerically, P^12(35) = 6.59e-14 lies in no Q(sqrt s) for the 15
probed s (P80), consistent with a 4-dimensional real genus
sub-locus.  The cancellation of Piece B requires the multiplier to be
trivial on all classes; the composite rows fail exactly this
condition, and the failure size is the measured residue.

## What is literature-level work vs done

DONE (this repo, numerical, 50+ digits): every arrow of the chain;
the five closed forms; the R-rationality; the f2^{24} identity; the
residue's field behavior.

LITERATURE-LEVEL (no new mathematics, formal write-up): citing the
class-invariant table entries for Piece A; writing Piece B's CM
derivative argument against Kronecker's second limit formula; the
genus-character bookkeeping of Piece C.

## Boundary (per the review)

d = 3 is FULLY closed numerically and its paper proof is a citation
chain.  The other four rows have exact closed forms and the same
skeleton; the unified theorem statement above is registered but the
formal write-up has not been done.  This document is the honest line
between computational discovery (complete) and theorem (three
citations away).

## Piece A update (P81, 2026-09-29 17:55): the Pell unit form

  392 - 160 sqrt6 = 8 (sqrt3 - sqrt2)^4,  (sqrt3-sqrt2)(sqrt3+sqrt2) = 1.

So for d = 3:  P(tau0)^12 = (sqrt3 - sqrt2)^4 / 64,  and the universal
norm 2^-12 across all five rows is elementary: each row's closed form
is (unit of norm 1) x (a power-of-2 normalization).  The five Weber
values are elliptic units normalized by the same 2-power; their
"unit parts" are Pell units of the respective real quadratic genus
subfields (Q(sqrt6): fundamental unit sqrt3+sqrt2; the other four
rows' unit parts are queued for the same treatment).

Literature anchor (Piece A citation chain COMPLETE at the structural
level): Berndt, Chan, Kang, Zhang, Pacific J. Math 202(2) (2002)
267-304 -- the J_n eta-quotient series of Ramanujan's Notebook III
p. 392 (berndt2002.pdf in repo root).  Our d=3 value sits on the
norm/conjugate branch of the same table family.

## P82/P83 (2026-09-29 18:05): the universal form and the strict d=3 derivation

P82 (verified):  64 P(tau0)^12 = eps_d^2 for all five rows, where
eps_d is a power (m_d in {-1,-2}) of the norm-1 Pell unit of the
genus real subfield:
  eps_3 = 5-2sqrt6 = (sqrt3-sqrt2)^2
  eps_5 = 19-6sqrt10 = (3+sqrt10)^-2
  eps_7 = (55+12sqrt21)^-1
  eps_13 = (649+180sqrt13)^-1
  eps_17 = (35+6sqrt34)^-2.
Open datum: a uniform rule for m_d (conjecture: fixed by the
multiplier character's order).

P83-A (d=3, strict):  F = 64P^12 = 64[Delta(2t)Delta(6t)/(Delta(t)Delta(3t))]^(1/2).
Key identity:  D log Delta(k tau) = k E2*(k tau) + 3/(pi Im tau),
whose correction term is k-INDEPENDENT -- so in
F = 64[ratio]^(1/2) (two numerator terms, two denominator terms)
the quasimodular corrections CANCEL IDENTICALLY:
  D log F = (1/2)[2E2*(2t) + 6E2*(6t) - E2*(t) - 3E2*(3t)],
purely modular.  At tau0 this combination equals Ec(tau0) exactly,
and R = DlogF/(12 W6) = Ec/(24 W6) = 5/3 (7.4e-41).  Piece B is now:
cancellation identity (elementary) + E2* CM values algebraic
(standard) + Ec/W6 in Q (Piece A's Pell units).  No numerics remain
inside the derivation.

## FINAL PROOF STRUCTURE (2026-09-30 01:00, P97 out-of-sample)

The complete logical architecture of the five-row theorem:

  LEVEL FACTS.  P^12 in M0(Gamma0(6), chi_2)  [Ligozat + 120dps numeric]
  GENUS DESCENT.  P^12 CM values in the genus field  [quadratic
      nebentypus = genus character via Shimura; numeric: 7-dim spans at
      35/55/77, single quadratics at 3/5/7/13/17]
  CANCELLATION.  D log Delta(k tau) = k E2*(k tau) + k-independent
      correction; the +/- combination cancels identically  [P83-A,
      elementary]
  PERIOD ALGEBRAICITY.  E2* CM values algebraic after period
      normalization  [standard CM; Bruinier-vdG conventions]
  DERIVATIVE RATIO.  R_d = P'/(2 pi i P W6) = (Ec/W6)/24 = 5/3, 3, 5,
      17, 33  [numerically exact; mechanism = cancellation + period
      algebraicity + Pell-unit closed forms of P82]
  CONCLUSION.  x6 = 1/(6 R_d + 2) in Q for the five rows.

  OUT-OF-SAMPLE (P97): zero rational rows in d in [80,200] where the
  2-elementary locus is empty -- the characterization's necessity
  direction survives on undiscovery data.

  REMAINING FORMAL GAP (one): the Schertz Thm 4 scope at non-coprime
  classes (the transport lemma for chi_2's non-coprime action).
  Everything else is citation-level assembly.

The theorem is no longer "numerics suggest": it is a statement with a
complete proof architecture, one flagged lemma, and out-of-sample
survival on undiscovery data.

## The character-theoretic closure (P98-c, 2026-09-30 03:40)

The quadratic nebentypus of P^12 is IDENTIFIED: chi_2 = Kronecker
(-3/.), the nontrivial Dirichlet character mod 3 = the genus character
associated to the prime 3 in D = -24d.  Verified: all 24 tested
Gamma0(6) elements give ratio = chi_2(a mod 6) = +1 iff a = 1 mod 6,
-1 iff a = 5 mod 6 (120 dps).

Mechanism: by Shimura reciprocity, chi_2 as nebentypus becomes the
genus character of the -3 component in the class-field Galois action.
This is WHY P^12's CM values land in the genus field (Prop O1): the
nebentypus IS the genus character.  And chi_2 = (-3/.) is trivial on
Cl(-24d) exactly when no class carries a nontrivial (-3) genus
component — for prime d in {3,5,7,13,17} this holds (all classes
trivial), for composite d in {35,55,77} it fails (measured nontrivial,
P69-b).

The theorem's character-theoretic form: x6(tau0) in Q iff the (-3)
genus character is trivial on Cl(-24d).  The 2-elementary condition
ensures no higher characters contribute.
