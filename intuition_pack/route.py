"""Mechanical route: which registered pack (if any) does this input touch?

Zero-LLM trigger (the P142 answer to "can the model auto-trigger?"):
the reliability ranking measured earlier is mechanical-hook > resident
rules > model self-trigger — a model cannot see its own meta-task
(the P32-h blind-judge result: 4/20 at detecting "this is new"), so
triggering is a HOST-side pattern match, not a model decision.

Match rules per pack (all mechanical, any hit fires):
  T1  explicit domain/trigger word
  T2  stimulus shape: the pack's exemplar input keys appearing with
      numeric values (e.g. "x0=0.083, lambda=0.25" or "x0 0.0833")
  T3  the domain's judgment verbs co-occurring with a trigger key
Returns (domain, pack, matched_rule) or None.  False positives are
cheap (an injected prompt_block is a few hundred tokens and P138
showed injection is harmless-to-helpful); false negatives are the
cost to avoid.
"""
import json
import re


def _tokens(s):
    return set(re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", s.lower()))


def route(text: str, packs: list):
    """packs: list[Pack].  Returns (domain, matched_rule) or None."""
    if not text or len(text) < 4:
        return None
    low = text.lower()
    toks = _tokens(low)
    # numeric-pair shape: key +/- "= : #" followed by a number
    pair_hits = {}
    for key in ("x0", "lambda", "lam"):
        n = len(re.findall(key + r"\s*[=:：]?\s*-?\d+\.\d+", low))
        if n:
            pair_hits[key] = n

    best = None
    for pack in packs:
        trig = [t.lower() for t in (pack.triggers or [pack.domain])]
        # T1 explicit trigger word; whole-word for ASCII, substring for
        # CJK (\b is meaningless between CJK word chars — P147 catch:
        # "约束" never matched inside "满足约束：")
        def _hit(t):
            # alnum-lookaround boundary instead of \b: CJK chars are
            # unicode \w, so \b fails on both "满足约束：" (CJK-CJK) and
            # "constraints吗" (ASCII-CJK) — the lookarounds only reject
            # [a-zA-Z0-9] neighbors, which is the boundary we mean
            if t.isascii():
                return re.search(
                    r"(?<![a-zA-Z0-9])" + re.escape(t) + r"(?![a-zA-Z0-9])",
                    low) is not None
            return t in low
        t1 = any(_hit(t) for t in trig)
        # T2 stimulus shape: pack input keys present AND a numeric pair in text
        pack_keys = set()
        for e in pack.exemplars:
            pack_keys |= {k.lower() for k in e.inputs}
        shape = bool(pair_hits) and bool(pack_keys & set(pair_hits))
        # also bare d=NN + a judgment verb
        verb = any(v in low for v in
                   ("判断", "判定", "verify", "rational", "integer",
                    "是不是", "是否", "classify", "判别", "满足",
                    "satisfy", "satisfies", "检查", "check"))
        dnum = re.search(r"\bd\s*[=:：]\s*(\d{1,4})\b", low)
        t2 = shape or (dnum and verb and pack_keys & {"d"})
        # T3 trigger word + verb (e.g. "用直觉包判断")
        t3 = t1 and verb
        if t1 or t2 or t3:
            rule = "T1-explicit" if t1 else ("T2-shape" if t2 else "T3-verb")
            score = (2 if t1 else 0) + (2 if t2 else 0) + (1 if t3 else 0)
            if best is None or score > best[2]:
                best = (pack.domain, rule, score)
    if best is None:
        return None
    return best[0], best[1]
