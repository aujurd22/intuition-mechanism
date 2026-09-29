# The Character Obstruction Theorem (P85 formalization)

Status: registered 2026-09-30 00:05.  This is the formalization of the
P69-b measured gap and the P89 nebentypus mechanism, stated as three
checkable propositions.  It is the "why exactly these five" half of the
five-row theorem.

## Setting

d positive, in the 2-elementary locus (Cl(-24d) a 2-group, genus theory).
tau0 = i*sqrt(d/6).  P = eta(2tau)eta(6tau)/(eta(tau)eta(3tau)) --
modular of level 6 with a multiplier of order 12;  P^12 has QUADRATIC
nebentypus chi_2 on Gamma0(6) (P89: numerically +-1 to 1e-58; in
theory via the Ligozat nebentypus formula).  x6 = W6/z6, quasimodular
(P76).  H = ring class field of D = -24d; G = its real genus
subfield chain.

## The three propositions

### Prop O1 (field containment via quadratic nebentypus)

P^12(tau0) lies in the real genus field of D = -24d.

Mechanism (Shimura reciprocity, quadratic case): a modular function
whose nebentypus is quadratic has CM values on which the ring class
Gal(H/K) acts through its GENUS quotient Cl/Cl^2; the further action
of the real-cl-conjugation element splits the field into real
quadratic factors.  Hence P^12(tau0) is a rational combination of the
sqrt(p*_S) -- the real genus basis.

Numerical support: five rows in a single real quadratic subfield
(P79, exact); composite rows in the full real genus field
(P89 step 1, 7-dim recognition); single-subfield membership
NEGATIVELY probed at 15 s-values (P80).

Formal gap: writing (i) with Schertz Thm 4's N-system bookkeeping
(gcd(A, 6) = 1 representatives + the chi_2 consistency) -- a citation-
level assembly.

### Prop O2 (the stabilizer identity)

Stab_{Cl}(P^12(tau0)) = ker(chi_2 viewed as a character of Cl via the
Artin map), where chi_2(𝔞) is the evaluation of the eta-quotient
nebentypus on the Artin-associated matrix.

Why this is the right form: a quadratic nebentypus means the value's
Galois orbit is the chi_2-isotypical orbit -- each class either fixes
the value (chi = +1) or sends it to the OTHER root of the same
quadratic minimal polynomial (chi = -1).  Extra collapse (a larger
stabilizer) would require the value to be annihilated by a genus
character it does not carry -- possible in principle, excluded by
the P80/P92 measurements at d = 35/55/77 (the value spans the full
4-dim locus, no extra collapse) and by the five rows' minimial
polynomial 4096x^2 - 6272x + 1 (exactly quadratic, no collapse).

Formal gap: the Schertz-Thm-4 transport for chi_2 at the
non-coprime classes -- the one place where the level-structure
subtlety (P63 addendum) still needs a lemma.

### Prop O3 (the obstruction direction)

chi_2 trivial on Cl(-24d)  <=>  P^12(tau0) in Q
 <=>  x6(tau0) in Q  (via the cancellation chain of P83-A:
     Ec/W6 = 24 R_d with R_d rational iff x6 rational).

"=>": immediate from O2 (trivial stabilizer = full class group fixed
the value = Q).  "<=": requires that Q-rationality of x6 forces the
FULL orbit to collapse -- which is O2 plus the non-degeneracy of the
quadratic (the minimal polynomial 4096x^2 - 6272x + 1 has two DISTINCT
roots, so rationality = both roots equal = stabilizer everything).

## The theorem this yields (once O1-O3 are formal)

x6(tau0) in Q  iff  d is in the 2-elementary locus  AND  chi_2 is
trivial on Cl(-24d).

The census locus {3,5,7,13,17} is then exactly the intersection, and
the composite-d failures are chi_2-nontrivial rows -- turning the
P69-b measurement into the theorem's content.

## What remains

1. The Schertz-Thm-4 transport lemma at non-coprime classes
   (the P63-addendum subtlety, now the only structural gap).
2. O2's non-collapse at t >= 3 (d=35/55/77 measured: value spans
   the 4-dim locus -- supports no-collapse, formal write-up pending).
3. m_d = exp(Cl)/2 (P82-CLOSURE) is the multiplicative shadow of the
   same story at the level of UNITS rather than x6 -- connecting the
   Pell-unit powers to chi_2's order would unify Pieces A and B.
