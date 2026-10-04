# -*- coding: utf-8 -*-
"""P232 truth generator: 40+ rules, executed truth, JSON out.
Bodies are single-line python expressions building the list `s`."""
import json, random

NL = chr(10)

# (desc, body_lines, expect_good)
RULES = [
    ("sort descending, first five", "    s = sorted(lst, reverse=True)[:5]", True),
    ("closest to 100", "    s = sorted(lst, key=lambda x: abs(x - 100))[-5:]", True),
    ("farthest from mean", "    m = sum(lst)/len(lst)\n    s = sorted(lst, key=lambda x: -abs(x - m))[:5]", True),
    ("last digit descending", "    s = sorted(lst, key=lambda x: -(x % 10))[:5]", False),
    ("closest to mean", "    m = sum(lst)/len(lst)\n    s = sorted(lst, key=lambda x: abs(x - m))[:5]", False),
    ("ascending first five", "    s = sorted(lst)[:5]", False),
    ("above 50, five largest", "    f = [x for x in lst if x > 50]\n    s = sorted(f, reverse=True)[:5] if len(f) >= 5 else sorted(lst, reverse=True)[:5]", True),
    ("divisor count descending", "    s = sorted(lst, key=lambda x: -sum(1 for i in range(1, int(abs(x)) + 1) if abs(x) % i == 0))[:5]", False),
    ("square descending", "    s = sorted(lst, key=lambda x: -x*x)[:5]", True),
    ("five largest odds", "    o = [x for x in lst if x % 2 == 1]\n    s = sorted(o, reverse=True)[:5] if len(o) >= 5 else sorted(lst, reverse=True)[:5]", True),
    ("five largest evens", "    e = [x for x in lst if x % 2 == 0]\n    s = sorted(e, reverse=True)[:5] if len(e) >= 5 else sorted(lst, reverse=True)[:5]", True),
    ("farthest from 50", "    s = sorted(lst, key=lambda x: -abs(x - 50))[:5]", True),
    ("five largest primes", "    pr = [x for x in lst if all(x % i for i in range(2, int(abs(x)**0.5)+1)) and abs(x) > 1]\n    s = sorted(pr, reverse=True)[:5] if len(pr) >= 5 else sorted(lst, reverse=True)[:5]", True),
    ("five smallest", "    s = sorted(lst)[:5]", False),
    ("mod 7 descending", "    s = sorted(lst, key=lambda x: -(x % 7))[:5]", False),
    ("above median, five largest", "    med = sorted(lst)[len(lst)//2]\n    f = [x for x in lst if x > med]\n    s = sorted(f, reverse=True)[:5] if len(f) >= 5 else sorted(lst, reverse=True)[:5]", True),
    ("bit length descending", "    s = sorted(lst, key=lambda x: -x.bit_length())[:5]", True),
    ("largest digit sums", "    ds = lambda x: sum(int(c) for c in str(abs(x)))\n    s = sorted(lst, key=ds, reverse=True)[:5]", True),
    ("random shuffle five", "    import random as _r\n    s = _r.sample(lst, 5)", False),
    ("closest to 75", "    s = sorted(lst, key=lambda x: abs(x - 75))[:5]", False),
    ("largest squares", "    s = sorted(lst, key=lambda x: -x*x)[:5]", True),
    ("every other number", "    s = lst[::2][:5]", False),
    ("descending even positions", "    s = sorted(lst, reverse=True)[::2][:5]", False),
    ("divisible by 3, five largest", "    f = [x for x in lst if x % 3 == 0]\n    s = sorted(f, reverse=True)[:5] if len(f) >= 5 else sorted(lst, reverse=True)[:5]", True),
    ("mod 10 ascending", "    s = sorted(lst, key=lambda x: x % 10)[:5]", False),
    ("first five as-is", "    s = lst[:5]", False),
    ("closest to 30", "    s = sorted(lst, key=lambda x: abs(x - 30))[:5]", False),
    ("farthest from 60", "    s = sorted(lst, key=lambda x: -abs(x - 60))[:5]", True),
    ("closest mapping to 60..100", "    import random as _r2\n    cand = list(range(60, 101))\n    s = [min(lst, key=lambda x: abs(x - v)) for v in _r2.sample(cand, 5)]", False),
    ("five smallest dup", "    s = sorted(lst)[:5]", False),
    ("fewest digits first", "    s = sorted(lst, key=lambda x: len(str(abs(x))))[:5]", False),
    ("smallest digit sums", "    ds = lambda x: sum(int(c) for c in str(abs(x)))\n    s = sorted(lst, key=ds)[:5]", False),
    ("divisible by 5, first five", "    f = [x for x in lst if x % 5 == 0]\n    s = f[:5]", False),
    ("ascending by square", "    s = sorted(lst, key=lambda x: x*x)[:5]", False),
    ("closest to zero", "    s = sorted(lst, key=lambda x: abs(x))[:5]", False),
    ("every third number", "    s = lst[::3][:5]", False),
    ("five most frequent", "    from collections import Counter\n    s = [v for v, _ in Counter(lst).most_common(5)]", False),
    ("reverse digit sum sort", "    ds = lambda x: -sum(int(c) for c in str(abs(x)))\n    s = sorted(lst, key=ds)[:5]", False),
    ("most divisors", "    nd = lambda x: sum(1 for i in range(1, int(abs(x)) + 1) if abs(x) % i == 0)\n    s = sorted(lst, key=nd, reverse=True)[:5]", True),
    ("last five as-is", "    s = lst[-5:]", False),
    ("tens digit ascending", "    s = sorted(lst, key=lambda x: (x // 10) % 10)[:5]", False),
]

def main():
    random.seed(7)
    opt = 0.0
    for t in range(30):
        rng = random.Random(1000 + t)
        lst = [rng.randint(0, 100) for _ in range(20)]
        opt += sum(sorted(lst, reverse=True)[:5])
    opt /= 30

    labeled = []
    for desc, body, expect_good in RULES:
        ns = {"random": random}
        code = "def rule(lst):\n" + body + "\n    return sorted(s, reverse=True)[:5]\n"
        try:
            exec(code, ns)
        except Exception as ex:
            labeled.append({"desc": desc, "good": None, "error": str(ex)[:40]})
            continue
        rule_fn = ns["rule"]
        sc = 0.0
        ok = True
        for t in range(30):
            rng = random.Random(1000 + t)
            lst = [rng.randint(0, 100) for _ in range(20)]
            try:
                sc += sum(rule_fn(lst))
            except Exception as _ex:
                ok = False
                print(f"  RULE RUNTIME ERR: {desc[:30]}: {_ex}")
                break
        if not ok:
            labeled.append({"desc": desc, "good": None, "error": "runtime"})
            continue
        good = (sc / 30) >= 0.97 * opt
        labeled.append({"desc": desc, "good": good, "score_over_opt": sc / 30 / opt})
    n_good = sum(1 for r in labeled if r.get("good") is True)
    n_bad = sum(1 for r in labeled if r.get("good") is False)
    print(f"{len(labeled)} rules labeled: {n_good} GOOD / {n_bad} BAD / {sum(1 for r in labeled if r.get('good') is None)} ERR")
    json.dump({"opt": opt, "labeled": labeled}, open("p232_rules_truth.json", "w"), indent=1)

if __name__ == "__main__":
    main()
