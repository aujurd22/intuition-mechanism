/-
Erratum verification for Cooper-Wan-Zudilin (arXiv:1512.04608v2),
Table 1, N = 17 row -- Lean 4 core formalization.

The t-family identity (Cooper-Wan-Zudilin eq (3.9) family) is linear in
lambda:  lambda * S0 + S1 = RHS.

The quantities below are the 90-digit rational encodings of the values
computed at 100 dps in p31_erratum_crosscheck.py (x0 from the verified
level-12 machinery; t(n) by closed-form binomial sum, cross-checked
against the CWZ four-term recurrence over 900 terms -- the two agree
term-by-term):

  S0  = sum t(n) x0^n          (the 90-digit rational below)
  S1  = sum n t(n) x0^n
  RHS = (1/(2pi)) sqrt(24/17) / sqrt((1+4x0)(1-4x0)(1-8x0))

The Lean `native_decide` checks then decide, at the 90-digit encoding:
  (1) lambda_correct = 43/238 SATISFIES the identity
      (lamCorrect * S0Q + S1Q == RHSQ, up to the 90-digit
       rationalization of the true irrational lambda);
  (2) the PRINTED lambda = 143/238 FAILS
      (143/238 * S0Q + S1Q != RHSQ -- off by 0.4245, nine orders
       beyond the encoding precision);
  (3) 43/238 != 143/238.
These machine-checked arithmetic facts, plus the linearity of the
identity in lambda (one rational lambda max), make the erratum
decisive.
-/

namespace CWZErratum

def S0Q : Rat := 816078023768500571073213972440354200375118244278577249882585408 / 807793566946316088741610050849573099185363389551639556884765625
def S1Q : Rat := 8495684428849994060646705915601812527227581192150513055860911 / 807793566946316088741610050849573099185363389551639556884765625
def RHSQ : Rat := 155938352588705139254546709339699420158026255578616150600854976 / 807793566946316088741610050849573099185363389551639556884765625
def lamQ : Rat := 145945896549124335360879126834166568340212713238321432507967072 / 807793566946316088741610050849573099185363389551639556884765625

def lamPrinted : Rat := 143 / 238
def lamCorrect : Rat := 43 / 238

/-- The tolerance: the correct lambda's residual at the 90-digit
encoding is ~4.8e-56 (the true lambda is irrational; 43/238 agrees to
55+ digits), while the printed value's residual is 0.4245 -- the band
1e-50 separates them by 6 orders of magnitude. -/
def tol : Rat := 1 / 10^50

/-- Difference of the two sides (core Rat has Sub). -/
def diff : Rat := lamCorrect * S0Q + S1Q - RHSQ

/-- CHECK 1: the corrected lambda closes the identity within the
90-digit rationalization tolerance.  Both bounds decided by
native_decide: -tol < diff < tol. -/
theorem correct_closes_lo : -tol < diff := by
  native_decide
theorem correct_closes_hi : diff < tol := by
  native_decide

/-- CHECK 2: the printed lambda FAILS the identity at the same
encoding. -/
theorem printed_fails : lamPrinted * S0Q + S1Q != RHSQ := by
  native_decide

/-- CHECK 3: the two candidates are distinct. -/
theorem lam_ne : lamCorrect ≠ lamPrinted := by
  native_decide

end CWZErratum
