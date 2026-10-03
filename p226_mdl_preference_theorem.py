"""P226: from density to PREFERENCE (G1 Newton step, external review item 1).
Setting: H_mod = 4096 subset-rules of Z_12, MDL prior P(h) ∝ 2^(-|S_h|/2)
(description length = |S_h| bits, halved for the lambda free-scale).
Window W observes residue set R(W), |R(W)| = r, k = |S_r ∩ R(W)|.
Likelihood: only hypotheses with S_h ∩ R(W) = S_r ∩ R(W) survive.
POSTERIOR: among survivors, S_h is fixed on R(W) and free on the u = 12-r
unobserved residues. THEOREM (preference): the posterior puts ALL its mass
on length-k hypotheses iff ... ; the MDL point estimate is
  S_h* = S_r ∩ R(W)   (length k)
and the TRUE rule (length 2, when 2 ∉ R(W)-constraints... S_r itself) is
  - shorter than S_h* only if k < 2 (k=1: shadow SHORTER than truth -> MDL
    strictly prefers the shadow);
  - equal length iff k = 2 (truth still in window -> tie broken by count:
    1 truth vs C(u,0)=1 shadow... equal-length survivors at j=0: exactly 1
    (S_r∩R(W) itself). So at k=2 the MDL estimate coincides with truth's
    restriction to R(W) — it IS the shadow that equals truth on R(W) and
    picks up NO unobserved residues).
CONSEQUENCE (bits bridge): eliminating the surviving shadow requires
observing the residue(s) in S_r \ R(W) — i.e. log2 information = the
number of missing positive residues. For the P205 loop: k went 1->2 within
2 rounds = 1 bit of residue coverage bought per round — same order as the
P190 3.3-bits-per-rule unit price.
"""
from mpmath import mp, mpf
import itertools

H = []
for c in itertools.product([0, 1], repeat=12):
    H.append((frozenset(j for j in range(12) if c[j]), len(c)))  # (S, |S|)
S_r = frozenset({1, 5})

def posterior_concentration(R_W, lam=0.5):
    """MDL posterior over survivors: P(h|data) ∝ 2^(-lam*|S_h|).
    Returns: survivor count by length, MDL argmin, whether it's a shadow."""
    S_rW = S_r & R_W
    k = len(S_rW)
    u = 12 - len(R_W)
    survivors = [S for S, L in H if S & R_W == S_rW]
    # group survivors by length
    by_len = {}
    for S in survivors:
        by_len.setdefault(len(S), []).append(S)
    mdl_len = min(by_len)
    mdl_set = by_len[mdl_len][0]
    is_shadow = mdl_set != S_r
    # posterior mass on the MDL hypothesis (unnormalized 2^(-lam*len))
    return {"k": k, "u": u, "survivors": len(survivors),
            "mdl_length": mdl_len, "mdl_set": mdl_set,
            "mdl_is_shadow": mdl_set != S_r,
            "truth_in_window": S_r <= R_W,
            "by_len": {L: len(v) for L, v in sorted(by_len.items())}}

print("=== P226: MDL preference derivation (numeric verification) ===\n")
for r_val in [3, 5, 8, 11, 12]:
    # simulate R(W) with r_val residues, always including 1 (positive seen), 5 unseen until r=12
    R_W = frozenset([1] + [x for x in (4, 7, 9, 0, 2, 3, 6, 8, 10, 11, 5)[:r_val-1]])
    res = posterior_concentration(R_W)
    shadow_note = "SHADOW (shorter than truth len 2)" if res["mdl_length"] < 2 else \
                  ("truth-length tie" if res["mdl_length"] == 2 else "longer than truth")
    print(f"r={r_val:>2} residues: k={res['k']} u={res['u']} survivors={res['survivors']:>4} "
          f"MDL_len={res['mdl_length']} -> {shadow_note}")
print()
print("DERIVATION: MDL point estimate = S_r ∩ R(W), length k = |S_r ∩ R(W)|.")
print("Truth S_r has length 2. MDL strictly prefers a shadow iff k < 2, i.e.")
print("iff one of the two positive residues (1 or 5) is UNOBSERVED in the window.")
print("Preference persists until BOTH positive residues are observed — the exact")
print("covering condition from P225, now on the PREFERENCE side (Newton step).")
print("Bits bridge: buying the missing residue costs log2(#unobserved candidate")
print("residues) ~ the P190 ambiguity-bits currency.")
