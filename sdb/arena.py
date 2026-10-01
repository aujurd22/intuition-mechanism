"""Insight Arena (P152): the cross-domain insight benchmark — formalizing
SDB v0 into the user's Discovery Score.

    Discovery Score = mean( Compression, Novelty, Verification, Transfer )

  Compression   bits(observations) / bits(stated rule), capped at the
                domain reference ratio                             [MDL, P35]
  Novelty       hidden-structure detection / rule stated unprompted
                (the charter omits it)
  Verification  mechanical verifier agreement with the judge's probe
                verdicts (the P138 "verify executed, not read" layer)
  Transfer      probe accuracy in a different carrier/regime than discovery

THE INSIGHT-vs-HALLUCINATION BOUNDARY (P152 formalization of direction 4):
a stated rule is an INSIGHT iff Verification == Transfer == 1 at nonzero
Compression.  A stated rule with Verification < 1 is a HALLUCINATION
(compressed hypothesis that failed verification pressure).  The boundary
is exactly the V component — mechanical, not judged.
"""
import json


def normalized_compression(observations, rule_text):
    s_obs = json.dumps(observations, separators=(",", ":"),
                       ensure_ascii=False).encode("utf-8")
    s_rule = rule_text.encode("utf-8")
    return round(len(s_obs) / max(len(s_rule), 1), 2)


def cap01(x):
    return max(0.0, min(1.0, float(x)))


def discovery_score(compression, novelty, verification, transfer, ref=None):
    """compression = mdl_ratio achieved; ref = the domain reference ratio.
    Component c = cap01(mdl/ref): a rule compressing at the reference
    ratio scores 1.0; below reference scales linearly; no compression
    (<=1) scores 0."""
    c = cap01((compression or 0) / ref) if ref else cap01((compression or 0) - 1)
    return {
        "compression": round(c, 3),
        "novelty": round(cap01(novelty), 3),
        "verification": round(cap01(verification), 3),
        "transfer": round(cap01(transfer), 3),
        "discovery_score": round((c + cap01(novelty) + cap01(verification)
                                  + cap01(transfer)) / 4, 3),
        "insight_vs_hallucination": (
            "INSIGHT" if cap01(verification) >= 1.0
            and cap01(transfer) >= 1.0 and c > 0 else
            "HALLUCINATION (verification failed)" if cap01(verification) < 1.0
            else "NO-COMPRESSION (fits discovery set only)"),
    }
