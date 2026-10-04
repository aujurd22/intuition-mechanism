# -*- coding: utf-8 -*-
"""G2B learnable domain ("星语" plural morphology) — generator + mechanical truth.

Design goals (review round-6, P235 redesign path (a)):
  1. Human-learnable from the SAME example set given to LLMs, within ~25 min.
  2. Programmatic truth: plural(stem) is a pure function — no ambiguity.
  3. Preserves the two-axis structure behind P234's predictions:
     - surface forms (stems) support memorization ("d-binding" analogue)
     - a compact structural rule over TWO stem features supports transfer
  4. Masking exam (exam2) preserves information but breaks surface binding
     (cipher alphabet + legend) — memorizers collapse, rule-users transfer.

Domain: stems are CVC pseudowords.
  initials: {b, d, g, k, p, t}   (IRRELEVANT feature — must be discovered;
                                  "trap" items have initial class != final class)
  vowels:   {a, i, u}            (feature B: a = 开口; i,u = 闭口)
  finals:   {b, d, g, k, p, t}   (feature A: b,d,g = 浊; k,p,t = 清)

Plural rule (the domain's "landing rule", a function of the FEATURE PAIR):
  (final 浊, vowel a)     -> -um
  (final 浊, vowel i/u)   -> -is
  (final 清, vowel a)     -> -is
  (final 清, vowel i/u)   -> -ok
Note the two -is cells sit on the anti-diagonal: any single-feature rule caps
at 0.5; only the feature PAIR reaches 1.0. Chance = 1/3 (three suffixes).

Item sets (fixed, registered — identical for humans and LLMs):
  train 16 (4 per cell, 3 initial-traps), exam1 12 (transfer + self-report),
  exam2 8 (cipher-masked, legend given).
"""
import json, os

VOICED = set("bdg")
OPEN_V = set("a")        # 开口
CLOSE_V = set("iu")      # 闭口

def truth(stem):
    """Mechanical plural rule — the domain's ground truth."""
    v, f = stem[1], stem[2]
    voiced, open_v = f in VOICED, v in OPEN_V
    if voiced and open_v:
        return "um"
    if voiced:
        return "is"
    if open_v:
        return "is"
    return "ok"

# cipher for exam2 (legend provided — information kept, surface binding broken)
CIPHER = {"b": "◆", "d": "★", "g": "●", "k": "▲", "p": "■", "t": "▼",
          "a": "1", "i": "2", "u": "3"}

def enc(stem):
    return "".join(CIPHER[c] for c in stem)

TRAIN = ["bab", "kad", "pag", "dab",   # 浊+开
         "big", "pid", "gub", "bud",   # 浊+闭 (pid = initial trap)
         "kap", "tap", "bap", "pak",   # 清+开 (bap = initial trap)
         "buk", "dup", "dik", "tup"]   # 清+闭 (dik = initial trap)
EXAM1 = ["bad", "gad", "pad",          # 浊+开 (pad trap)
         "dig", "pud", "bid",          # 浊+闭
         "bat", "tak", "dat",          # 清+开 (bat/dat traps)
         "bik", "dip", "kit"]          # 清+闭 (bik/dip traps)
EXAM2 = ["gab", "dag",                 # 浊+开
         "kud", "gid",                 # 浊+闭
         "dap", "pat",                 # 清+开 (dap trap)
         "pik", "bit"]                 # 清+闭 (bit trap)

def cell(stem):
    return ("voiced" if stem[2] in VOICED else "voiceless",
            "open" if stem[1] in OPEN_V else "closed")

if __name__ == "__main__":
    sets = {"train": TRAIN, "exam1": EXAM1, "exam2": EXAM2}
    for name, items in sets.items():
        assert len(items) == len(set(items)) == {"train": 16, "exam1": 12,
                                                 "exam2": 8}[name], name
        from collections import Counter
        bal = Counter(cell(s) for s in items)
        assert set(bal.values()) == {4 if name == "train" else
                                     (3 if name == "exam1" else 2)}, (name, bal)
        assert all(len(s) == 3 and s[0] in "bdgkpt" and s[1] in "aiu"
                   and s[2] in "bdgkpt" for s in items), name
    assert not (set(EXAM1) | set(EXAM2)) & set(TRAIN)
    key = {
        "rule": "voiced&a->um | voiced&{i,u}->is | voiceless&a->is | voiceless&{i,u}->ok",
        "chance": round(1 / 3, 4),
        "cipher_legend": CIPHER,
        "train": [{"stem": s, "plural": s + truth(s)} for s in TRAIN],
        "exam1": [{"stem": s, "plural": s + truth(s),
                   "final_class": cell(s)[0], "vowel_class": cell(s)[1]}
                  for s in EXAM1],
        "exam2": [{"stem": s, "cipher": enc(s), "plural": s + truth(s)}
                  for s in EXAM2],
    }
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "answer_key.json")
    json.dump(key, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for name in sets:
        print(name + ":", " ".join(f"{s}->{truth(s)}" for s in sets[name]))
    print("saved", out)
