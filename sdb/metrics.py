"""SDB metrics: compression, transfer, surprise — computed, not asserted."""
import json
import math


def bits_of(obj):
    """Crude but consistent description length in bits: compact JSON,
    utf-8, per-character 4.7 bits (~log2(26))."""
    s = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    return len(s.encode("utf-8")) * 4.7


def mdl_ratio(observations, rule_reference: str) -> float:
    """bits(observations) / bits(rule).  The Jev-style compression ratio:
    how much data one sentence-style rule replaces."""
    d_bits = bits_of(observations)
    r_bits = bits_of(rule_reference)
    return round(d_bits / max(r_bits, 1.0), 2)


def transfer_acc(predictions: list, truths: list) -> float:
    assert len(predictions) == len(truths)
    return round(100 * sum(int(p == t) for p, t in
                           zip(predictions, truths)) / len(truths), 1)


def surprise_detected(anomaly_calls: list, truths: list) -> bool:
    """SURPRISE = the mechanism flags the hidden anomaly class at better
    than the base rate, without the charter naming it."""
    if not truths:
        return False
    base = max(sum(truths), len(truths) - sum(truths)) / len(truths)
    hits = sum(int(c == t) for c, t in zip(anomaly_calls, truths))
    acc = hits / len(truths)
    return acc > base + 0.15          # 15pp above the majority prior
