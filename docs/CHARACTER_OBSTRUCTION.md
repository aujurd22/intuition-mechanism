# The Character Obstruction Theorem — CLOSED and CORRECTED (P132)

Status: 2026-09-30, final.  This revision closes the one remaining
formal gap registered in the previous version ("the Schertz-Thm-4
transport lemma at non-coprime classes", P114) and corrects the
character-theoretic criterion that the previous version stated.  The
numerical six-row theorem is untouched (P121: 6 TP + 294 TN over
d in [1, 300]).

## Setting

d positive, in the 2-elementary locus {1,3,5,7,10,13,17,35,55,77}
(Cl(-24d) a 2-group).  tau0 = i*sqrt(d/6).  P = eta(2t)eta(6t)/
(eta(t)eta(3t)), modular of level 6; P^12 has quadratic nebentypus
chi_2 on Gamma0(6) (Ligozat criterion; verified +-1 to 1e-58, P89).
x6 = W6/z6, quasimodular (P76).  H = ring class field of D = -24d,
H_gen = its genus field.  K = Q(sqrt(D/4-normalized)).

> **CORRECTION (P195, 2026-10-03):** the 2-elementary census for D=-24d is **22 rows in [1,1000]** = {1,2,3,5,7,10,13,17,35,55,77} ∪ 4×{1,2,3,5,7,10,13,17,35,55,77}. The earlier 11-row account missed ALL d ≡ 0 (mod 4) rows: the P172 enumerator double-counted |b|=a boundary forms (inflating h) and mis-decomposed the v2≥4 2-part into non-prime discriminants (miscounting t). Six-row integrality theorem, its proof, and the P185/P188 results are unaffected (different census; the missed rows are composite-d non-integrality rows). External review credit; local defense of P172 withdrawn. See RESEARCH_PLAN P195 / p195_2elem_corrected.py.

## Lemma A (coprime representatives — the gap dissolves)

Every primitive binary quadratic form of any discriminant is SL2(Z)-
equivalent to a form whose leading coefficient is coprime to 6.

Proof.  Let [A,B,C] be primitive, F(x,y) = Ax^2+Bxy+Cy^2.  For p in
{2,3}: F is nonzero mod p as a form (primitivity), hence F(x,1) is a
nonzero poly of degree <= 2 over F_p, hence vanishes for at most 2
residues mod p while there are p >= 2 residues — pick x_p with
F(x_p,1) =/= 0 mod p (mod 2 both residues cannot vanish: that would
force A = B = C = 0 mod 2).  CRT gives x0 mod 6 with gcd(F(x0,1),6)=1.
Set (a,b) = (x0,1), choose (c,d) by x0*d - c = 1 (extended gcd), and
G = F(a*u+b*v, c*u+d*v).  Then G is a primitive form of the same
discriminant with leading coefficient F(x0,1), coprime to 6.  QED.

Consequence: every class of Pic(O) admits an ideal representative of
norm coprime to 6 (the ideal of G has norm G_A).  Therefore the
coprimality hypothesis of the Schertz-Thm-4 transport is satisfiable
for EVERY class of EVERY order in the locus — **there are no
"non-coprime classes"**.  The registered obstruction (P114: "the
generator class (2,0,9) for d=3 has all forms with even A") checked
only REDUCED forms; the explicit equivalence [2,0,9] ~ [11,18,9]
(A = 11, gcd = 1, same discriminant -72) is a counterexample, and the
lemma makes it general.  THE REGISTERED FORMAL GAP IS CLOSED.

Mechanical verification: p132_coprime_representatives.py — for all 10
locus discriminants, every class exhibits an explicit 6-coprime
representative with discriminant and primitiveness checked
(48 classes total, 48/48 pass).

## Prop O1 (genus containment) — PROVED

For 2-elementary d, every algebraic modular value at tau0 — in
particular P^12(tau0), W6(tau0), x6(tau0) — lies in H_gen.

Proof.  (i) CM theorem: a modular function with algebraic q-expansion
evaluated at the CM point of the order O lies in H.  (ii) Genus theory
of orders: H_gen = the fixed field of Pic(O)^2 inside H.
(iii) Pic(O) 2-elementary => Pic(O)^2 = {1} => H_gen = H.
Combining: the value lies in H = H_gen.  NO transport and NO
coprimality is used — the non-coprime classes are irrelevant to
containment.  QED.

Numerical confirmation: h(D) = 2^(t-1) on all 10 locus rows
(p132 table; also the closed forms' fields sit inside H_gen — the
prime-discriminant signs were re-derived: 2-pd is +8 iff
(D/8) = +1 mod 4 i.e. D/8 = 1 mod 4; the odd p-pd is (−1)^((p−1)/2)p;
e.g. d=7 has pds {-8,-3,-7}, so sqrt21 = sqrt(-3)sqrt(-7) IS in
H_gen, resolving an apparent contradiction).

## Prop O2 (stabilizer = support-character kernel) — CORRECTED, verified

The previous version identified the rationality-relevant character with
chi_2 = Kronecker(-3/.) on every row.  That identification is
ROW-DEPENDENT and fails on d in {7,13}.  The corrected statement:

Let the SUPPORT sqrt(s_d) be the single real genus coordinate carried
by P^12(tau0) (the P79 closed forms), i.e. the prime-discriminant
product whose sign flip sends P^12(tau0) to its algebraic conjugate:

    d=3:  s = 24  = (-8)(-3)   support char = chi(-3) (= chi(-8))
    d=5:  s = 40  = (8)(5)     support char = chi(8)chi(5) (= chi(-3))
    d=7:  s = 21  = (-3)(-7)   support char = chi(-3)chi(-7) (= chi(-8))
    d=13: s = 13  (generator)  support char = chi(13) (= chi(8)chi(-3))
    d=17: s = 136 = (8)(17)    support char = chi(8)chi(17) (= chi(-3))

(the parenthesized equalities are the product relation
chi(-8)chi(-3)chi(odd pds) = 1 on the genus group).  Then

    Stab_{Pic(O)}(P^12(tau0)) = ker(chi_support),

because Gal(H_gen/K) = Pic(O) acts on H_gen by the sign vector and
P^12(tau0) = a - b*sqrt(s_d) with b =/= 0 (P79).  Mechanically:
chi_support == chi_2 (= Kronecker(-3,.)) on 100% of classes for
d in {3,5,17} and on only 2/4 classes for d in {7,13} — exactly the
rows where the registered identification was wrong; for d=7/13 the
correct stabilizer kernel is ker(chi(-8)) / ker(chi(13)).

## Prop O3 — RETRACTED as stated; corrected criterion

RETRACTED: "chi_2 (Kronecker(-3,.)) trivial on Cl  <=>  x6 in Q".
Mechanically, chi_2 is NONTRIVIAL on the class group of EVERY locus
row (P132 table: values {+1,-1} on all ten) — the criterion never
fires, so it cannot be the separator.  (The previous version's
transport formula sigma(f) = chi_2(A) f(tau0) is also false as stated:
for d=3, sigma is the sqrt6-conjugate 49/64 + (5/16)sqrt6, not
-P^12.)

CORRECTED:  x6(tau0) in Q  <=>  2-elementary AND P^12(tau0) has
single-coordinate support AND the pair (P^12, W6) satisfies the
Pell-unit normalization 64 P^12 = eps_d^{±1} (P79/P82) — the last is
the deep content, carried by the CM-derivative cancellation chain
(P83-A/P84), not by genus theory alone.  Genus theory supplies the
FIELD (O1) and the ORBIT STRUCTURE (O2); the Pell chain supplies the
RATIONALITY.

## Status of the six-row theorem

- Census ground truth: P121, d in [1,300], 6 TP + 294 TN, 0 FP/FN.
- "<=" (six rows rational): PROVEN by the closed-form/Pell chain
  (P79-P84); now complemented by O1 (the values live in the right
  field) and O2-corrected (the orbit structure).
- "=>" (all other d irrational): census-proven; the character-theoretic
  explanation is the corrected support story above, with the
  composite-d multi-coordinate support measured (P89 step 1) and the
  d=10 case (t=3, h=4, still irrational) pinning the criterion on the
  Pell normalization rather than on h or t.

## What actually remains (paper-level)

1. The Schertz citation for the transport ON COPRIME CLASSES (now
   sufficient everywhere by Lemma A) — assembly, not discovery.
2. A conceptual explanation of WHY the support picks sqrt(s_d) and the
   Pell normalization holds for exactly {1,3,5,7,13,17} — the honest
   open question behind the six-row theorem (the census is complete;
   this is the "why" layer).
3. m_d = exp(Cl)/2 (P82) unification with the support-character
   picture.
