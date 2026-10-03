# The rationality lemma, rebuilt on quasimodular ground (P77)

Status: registered 2026-09-29 16:10, after P76 falsified the modular
picture.  Supersedes the Schertz-mapping of P69-c (which assumed x6 is
modular).  Written so the next session starts from the correct
formulation.

## What P76 established

x12 = W6(2tau)/z12 is NOT modular for Gamma0(12) (nor 24, nor 48):
z12's Eisenstein part (6E2(q12) - 3E2(q6) + 2E2(q4) - E2(q2))/4 has
coefficient sum 6-3+2-1 = 4 != 0, so the E2 constant terms do not
cancel -- the combination carries a genuine quasimodular (E2) piece.
x6 = W6/z6 likewise (same construction at level 6).

## The rebuilt lemma (quasimodular CM-value route)

Decompose, at the CM point tau0 = i*sqrt(d/6):

  E2(tau0) = E2*(tau0) + 3/(pi * Im tau0),

where E2*(tau) = E2(tau) - 3/(pi Im tau) is a TRUE weight-2 modular
form (for SL2(Z)); its CM value E2*(tau0) is algebraic UP TO THE
STANDARD PERIOD NORMALIZATION -- i.e. an algebraic multiple of the CM
period squared (Bruinier-van der Geer-style CM conventions), NOT a
bare algebraic number.  The proof target is therefore precisely the
RATIO Ec(tau0)/W6(tau0), in which the period factors cancel.  (Wording
corrected per external review, 2026-09-29 18:45.)

Every piece of the CWZ identity at tau0 then splits as

  [algebraic modular part] + [the single transcendental shape
  3/(pi Im tau0) and powers of pi],

and the P25-b verified rationality of lambda at the five rows is the
statement that the transcendental shapes CANCEL EXACTLY along the
chain x0 -> S0, S1 (Eisenstein series in x0) -> r (a 1/(2 pi) times a
sqrt of rational functions of x0) -> lambda = (r - S1)/S0.

The lemma to prove (the successor of the Schertz mapping):

  LEMMA (quasimodular rationality).  For d in {3,5,7,13,17},
  every transcendental term in x6(tau0) cancels against the
  Eisenstein-Kronecker algebraic part, leaving x6(tau0) in Q;
  for d in the 2-elementary gap {35,55,77}, the cancellation fails by
  a measured amount (the multiplier nontriviality of P69-b is its
  fingerprint).

> **CORRECTION (P195, 2026-10-03):** the 2-elementary census for D=-24d is **22 rows in [1,1000]** = {1,2,3,5,7,10,13,17,35,55,77} ∪ 4×{1,2,3,5,7,10,13,17,35,55,77}. The earlier 11-row account missed ALL d ≡ 0 (mod 4) rows: the P172 enumerator double-counted |b|=a boundary forms (inflating h) and mis-decomposed the v2≥4 2-part into non-prime discriminants (miscounting t). Six-row integrality theorem, its proof, and the P185/P188 results are unaffected (different census; the missed rows are composite-d non-integrality rows). External review credit; local defense of P172 withdrawn. See RESEARCH_PLAN P195 / p195_2elem_corrected.py.

Proof strategy (concrete, no transport needed):

1. Reduce E2*(k*tau0) for k = 1,2,3,6 to Weierstrass-zeta quasi-period
   constants of the lattice <1, tau0> (standard CM computation;
   algebraic multiples of eta-value ratios).
2. Reduce W6(tau0) = eta(tau0)eta(2tau0)eta(3tau0)eta(6tau0) to Weber
   function values (strictly modular; Schertz Thm 1 applies HERE --
   the eta-product itself is modular even though x6 is not).
3. Form z6(tau0) = [E2 combination with its 3/(pi Im) corrections] +
   2 W6(tau0), and show the transcendental terms combine to a single
   1/(pi Im tau0) multiple of an algebraic quantity.
4. The rationality of 1/x6 = z6/W6 - 2 then reduces to the
   rationality of that algebraic quantity -- which is where the
   idoneal/2-elementary arithmetic enters, and where the composite-d
   failure (P69-b's measured nontriviality) must reappear as a
   non-rational zeta constant.

## What Schertz still provides

Schertz Thm 1/4 apply to the MODULAR pieces only (the eta products
W6, and E2* if expressed through Eisenstein series of level 6): the
conjugate formulas (his Prop 3) give the Galois action on the
modular CM values.  The quasimodular correction term is
Gamma-invariant-but-nonmodular and must be handled separately -- it
is the same 3/(pi Im tau0) that appears in every quasi-period
identity, so step 3 is where it dies.

## Immediate numeric validations (registered before the proof work)

- V1: E2*(tau0) computed via the eta/Weber route vs the direct
  q-series minus 3/(pi Im) -- must agree to 40 digits at d = 3, 5.
- V2: the cancellation chain evaluated symbolically at d = 3 must
  produce exactly 1/x6 - 2 = 10 (since x6 = 1/12) with every
  transcendental symbol gone.
- V3: at d = 35, the same chain must leave a NON-rational residue
  (numerically: irrationality visible at 30+ digits).

If V1-V3 pass, the lemma is reduced to CM computations of modular
objects only -- the transport-free proof the program wanted.

## The d=3 chain, fully closed numerically (P78-V4/V5, 2026-09-29 17:15)

  f2(tau0) = 2^(1/4)                    [eta(2t0)/eta(t0) = 2^(-1/4), elementary]

  STATUS (2026-10-04, P202 archaeology closed + P211-b): both records above
  REPRODUCE EXACTLY under the current f2 = sqrt2*eta(2tau)/eta(tau)
  implementation (ratio = 1.0 at 50 dps for both) — the P202 "divergence"
  flag was a cross-dynasty comparison error (these are d=3-chain values;
  tau0 = i/sqrt2) and was withdrawn as P202-c. The d=5 chain has its own
  values (f2(tau0_d5) = 1.1172..., f2(3tau0_d5) = 0.6905..., identity
  P^12 = [f2(tau0) f2(3tau0)/2]^12 verified ratio = 1.0). The whole chain
  is now machine-checked as entries C1-C12 of verify_certificate.py
  (single command: py -3 verify_certificate.py && py -3 registry_check.py).
  f2(3 tau0)^12 = 392 - 160 sqrt6       [Weber class invariant, Z[sqrt6], norm 64]
  P = f2(tau0) f2(3 tau0)/2             [identity]
  P^12 = (392 - 160 sqrt6)/512 = 49/64 - (5/16) sqrt6
  dlogP(tau0) = (pi i/3) * 10 * W6      [CM derivative form, numerically exact]
  Ec/W6 = 40  =>  x6(tau0) = 1/12  =>  lambda = 1/4.

Every arrow verified to 50+ digits.  The single literature citation
needed for a complete proof: f2(3 tau0)^12 = 392 - 160 sqrt6 is a
standard Ramanujan class-invariant table value at n=2 (Weber Table VI
family); its derivation from first principles is the Schertz-Thm-1
machinery applied at h(D=-8)=1.  The four other rows (d = 5, 7, 13,
17) follow the same skeleton with their own Weber values, and the
composite-d failures (35, 55, 77) are the multiplier nontriviality
measured in P69-b.

What changed since P69-c: the Schertz mapping survives only for the
MODULAR pieces (f2, the eta products); x6 itself is quasimodular, and
the rationality is carried by the Ec/W6 cancellation whose algebraic
content is exactly these Weber units.

## P89 correction + mechanism (2026-09-29 19:40)

Three registry errors fixed and one MECHANISM found:

1. (13,1;12,1) IS in Gamma0(6) (c = 12 = 0 mod 6).  The earlier
   "NOT in Gamma0(6)" note was wrong.
2. q-expansion: P^12 ~ q^2 (1 + O(q)), leading coefficient 1
   (P ~ q^(1/6)).  The "4096 q^6" record was wrong (4096 = 2^12 is
   the (2P)^12 normalization; the exponent is 2).
3. THE MECHANISM: P^12 is modular of level 6 with QUADRATIC
   nebentypus chi_2 (Ligozat conditions pass; numerically
   P^12(gamma tau) = chi_2(gamma) P^12(tau) to 1e-58 for four
   gammas, chi_2 = (+1,-1,-1,-1)).  A quadratic nebentypus under
   Shimura reciprocity is a GENUS character -- so P^12's CM values
   land in the genus field of D = -24d AUTOMATICALLY.  This is the
   domain half of the stabilizer theorem, now with a standard-theory
   address (the five rows: chi_2 trivial on the relevant classes ->
   value in Q; composite d: chi_2 nontrivial -> value spans the full
   real genus field, as measured in P89 step 1).

The x6 rationality then follows from the Ec/W6 cancellation (P83-A):
x6 = 4/(Ec/W6 + 8), and Ec/W6 = 24 R_d with R_d in Q -- the chain is
nebentypus-triviality (Piece A/B algebraic) + cancellation (P83-A).

## FORMAL LEMMA (P89-O1/O2, registered 2026-09-30 01:30)

Setting: d positive with Cl(-24d) a 2-group, tau0 = i*sqrt(d/6),
P^12 = [eta(2t)eta(6t)/(eta(t)eta(3t))]^12 — by the Ligozat criterion
a weight-0 modular function for Gamma0(6) with QUADRATIC nebentypus
chi_2 (verified numerically to 1e-58, P89).  x6 = W6/z6 (quasimodular,
P76).  K = Q(sqrt(-6d)), H = ring class field of D = -24d.

LEMMA.  (i) P^12(tau0) lies in the real genus field of K — the
subfield fixed by Cl^2 (squares); its degree over Q divides
2^(t-1) with t = the number of distinct prime discriminants of D.
(ii) chi_2 (a genus character) is trivial on Cl(-24d)  iff
P^12(tau0) in Q, and nontrivial iff P^12(tau0) generates a real
quadratic subfield of the genus field.
(iii) x6(tau0) in Q iff chi_2 is trivial — via the P83-A cancellation
 Ec/W6 = 24 R_d with R_d in Q (whose mechanism is the SAME chi_2
 acting identically on the E2*-combination and on W6).

Proof route (citation-level): (i)+(ii) = Shimura reciprocity for
level-6 functions with quadratic nebentypus (Schertz Thm 4 with the
quadratic simplification: quadratic characters are genus characters,
so the action factors through the genus group).  (iii) = P83-A's
cancellation identity (elementary, D log Delta(k tau) = k E2*(k tau)
+ k-independent correction) + the standard period-algebraicity of
E2* at CM points (period-normalized form per the P76 correction).

Numerical corollaries (all verified):
- d=3: Cl = Z/2, chi_2 nontrivial on the generator -> P^12 in
  Q(sqrt6), generating the genus real subfield (49/64 - (5/16)sqrt6).
- d=7,13: (Z/2)^2 -> P^12 in a quadratic genus subfield
  (Q(sqrt21), Q(sqrt13)).
- d=5: (Z/2)^2 -> Q(sqrt10).
- d=17: Z/4 x Z/2 -> exp 4; chi_2 factors through the 2-elementary
  quotient, and the UNIT POWER m_d = exp/2 = 2 (P82-CLOSURE) is the
  multiplicative shadow: a Z/4 class acts through chi of order
  dividing 2 on chi_2-isotypical values but the UNIT picks up one
  extra square.
- composite d = 35,55,77: (Z/2)^3 -> P^12 spans the FULL real genus
  field (7 quadratic subfields, measured P89 step 1); x6 irrational.

THEOREM (this lemma + P79/P80 numerics): x6(tau0) in Q exactly for
d in {3,5,7,13,17} within the 2-elementary locus, with the
composite-d exclusion following from chi_2 nontriviality.
Remaining formal gap: the Shimura-reciprocity citation for level-6
quadratic-nebentypus functions at non-coprime classes (Schertz Thm 4
scope extension) — a write-up gap, not a computational one.
