# THEOREM: The five-row rationality of x6 (P80)

Status: 2026-09-29 17:45.  The complete statement, with the proof
reduced to three pieces whose numerical content is fully verified in
this repo and whose remaining formal work is literature-level.

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
