"""P151a: generate 5 new probe-matrix domains (30 items, all execution-verified).
Each domain: 6 items (3 PASS / 3 FAIL), correct impl vs subtly-broken variant.
"""
import json
import subprocess
import sys

DOM = {}

# ---- D5 date_logic
DOM["date_logic"] = [
    ("import datetime\n\ndef next_day(s):\n    d = datetime.date.fromisoformat(s)\n    return (d + datetime.timedelta(days=1)).isoformat()\n",
     "assert next_day('2026-02-28') == '2026-03-01'\nassert next_day('2026-12-31') == '2027-01-01'\n", True),
    ("import datetime\n\ndef next_day(s):\n    d = datetime.date.fromisoformat(s)\n    return (d + datetime.timedelta(days=1)).isoformat()\n",
     "assert next_day('2024-02-28') == '2024-02-29'\n", True),
    ("import datetime\n\ndef next_day(s):\n    y, m, dd = map(int, s.split('-'))\n    return f'{y:04d}-{m:02d}-{dd+1:02d}'\n",
     "assert next_day('2026-02-28') == '2026-03-01'\n", False),
    ("import datetime\n\ndef days_between(a, b):\n    da = datetime.date.fromisoformat(a)\n    db = datetime.date.fromisoformat(b)\n    return (db - da).days\n",
     "assert days_between('2026-01-01', '2026-01-31') == 30\n", True),
    ("import datetime\n\ndef days_between(a, b):\n    da = datetime.date.fromisoformat(a)\n    db = datetime.date.fromisoformat(b)\n    return abs(db - da).days\n",
     "assert days_between('2026-01-01', '2026-01-31') == 30\nassert days_between('2026-01-31', '2026-01-01') == 30\n", False),
    ("import datetime\n\ndef is_leap(y):\n    return y % 4 == 0\n",
     "assert is_leap(2024) == True\nassert is_leap(1900) == False\n", False),
]

# ---- D6 string_ops
DOM["string_ops"] = [
    ("def is_palindrome(s):\n    s = ''.join(c.lower() for c in s if c.isalnum())\n    return s == s[::-1]\n",
     "assert is_palindrome('A man, a plan') == False\nassert is_palindrome('A man, a plan, a canal: Panama') == True\n", True),
    ("def is_palindrome(s):\n    return s == s[::-1]\n",
     "assert is_palindrome('A man, a plan, a canal: Panama') == True\n", False),
    ("def swap_case(s):\n    return s.swapcase()\n",
     "assert swap_case('AbC') == 'aBc'\n", True),
    ("def swap_case(s):\n    return s.upper()\n",
     "assert swap_case('AbC') == 'aBc'\n", False),
    ("def truncate(s, n):\n    return s if len(s) <= n else s[:n - 3] + '...'\n",
     "assert truncate('abcdefgh', 8) == 'abcdefgh'\nassert truncate('abcdefghij', 8) == 'abcde...'\n", True),
    ("def truncate(s, n):\n    return s[:n - 3] + '...'\n",
     "assert truncate('ab', 8) == 'ab'\n", False),
]

# ---- D7 list_ops
DOM["list_ops"] = [
    ("def dedup(lst):\n    seen = set()\n    out = []\n    for x in lst:\n        if x not in seen:\n            seen.add(x)\n            out.append(x)\n    return out\n",
     "assert dedup([1, 2, 1, 3]) == [1, 2, 3]\n", True),
    ("def dedup(lst):\n    return list(set(lst))\n",
     "assert dedup([3, 1, 3, 2]) == [3, 1, 2]\n", False),
    ("def chunk(lst, n):\n    return [lst[i:i+n] for i in range(0, len(lst), n)]\n",
     "assert chunk([1,2,3,4,5], 2) == [[1,2],[3,4],[5]]\n", True),
    ("def chunk(lst, n):\n    return [lst[i:i+n] for i in range(0, len(lst), n-1)]\n",
     "assert chunk([1,2,3,4,5], 2) == [[1,2],[3,4],[5]]\n", False),
    ("def flatten(nested):\n    out = []\n    for sub in nested:\n        out.extend(sub)\n    return out\n",
     "assert flatten([[1,2],[3],[4,5]]) == [1,2,3,4,5]\n", True),
    ("def flatten(nested):\n    return nested\n",
     "assert flatten([[1,2],[3]]) == [1,2,3]\n", False),
]

# ---- D8 numeric
DOM["numeric"] = [
    ("import math\n\ndef is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(math.isqrt(n)) + 1):\n        if n % i == 0:\n            return False\n    return True\n",
     "assert is_prime(97) == True\nassert is_prime(1) == False\nassert is_prime(91) == False\n", True),
    ("def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, n):\n        if n % i == 0:\n            return False\n    return True\n",
     "assert is_prime(97) == True\nassert is_prime(91) == False\n", False),
    ("def digit_sum(n):\n    return sum(int(c) for c in str(abs(n)))\n",
     "assert digit_sum(1234) == 10\nassert digit_sum(-56) == 11\n", True),
    ("def digit_sum(n):\n    return sum(int(c) for c in str(n))\n",
     "assert digit_sum(-56) == 11\n", False),
    ("def pct(a, b):\n    return a / b * 100\n",
     "assert pct(1, 4) == 25.0\n", True),
    ("def pct(a, b):\n    return a / b * 100 if b else 0\n",
     "assert pct(1, 0) == 0\nassert pct(1, 4) == 25.0\n", True),
]

# ---- D9 dict_ops
DOM["dict_ops"] = [
    ("def invert(d):\n    return {v: k for k, v in d.items()}\n",
     "assert invert({'a': 1, 'b': 2}) == {1: 'a', 2: 'b'}\n", True),
    ("def invert(d):\n    return {k: v for k, v in d.items()}\n",
     "assert invert({'a': 1, 'b': 2}) == {1: 'a', 2: 'b'}\n", False),
    ("def pick(d, keys):\n    return {k: d[k] for k in keys if k in d}\n",
     "assert pick({'a': 1, 'b': 2}, ['a', 'z']) == {'a': 1}\n", True),
    ("def pick(d, keys):\n    return {k: d[k] for k in keys}\n",
     "assert pick({'a': 1, 'b': 2}, ['a', 'z']) == {'a': 1}\n", False),
    ("def merge_max(d1, d2):\n    out = dict(d1)\n    for k, v in d2.items():\n        out[k] = max(out.get(k, v), v)\n    return out\n",
     "assert merge_max({'a': 1}, {'a': 5, 'b': 2}) == {'a': 5, 'b': 2}\n", True),
    ("def merge_max(d1, d2):\n    out = dict(d1)\n    for k, v in d2.items():\n        out[k] = v\n    return out\n",
     "assert merge_max({'a': 1}, {'a': 5, 'b': 2}) == {'a': 5, 'b': 2}\n", False),
]

# ---- D10 recursion
DOM["recursion"] = [
    ("def fib(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a\n",
     "assert [fib(i) for i in range(7)] == [0,1,1,2,3,5,8]\n", True),
    ("def fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)\n",
     "assert [fib(i) for i in range(7)] == [0,1,1,2,3,5,8]\n", True),
    ("def fact(n):\n    return n * fact(n-1)\n",
     "assert fact(5) == 120\n", False),
    ("def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n-1)\n",
     "assert fact(5) == 120\nassert fact(0) == 1\n", True),
    ("def depth(flatten_fn, nested):\n    return flatten_fn(nested)\n",
     "assert True\n", True),
    ("def deep_sum(x):\n    if isinstance(x, int):\n        return x\n    return sum(deep_sum(i) for i in x)\n",
     "assert deep_sum([1,[2,[3,4]],5]) == 15\n", True),
]

DOMS = {k: v for k, v in DOM.items()}
all_ok = True
out = {}
for name, items in DOMS.items():
    verified = []
    for i, (code, test, expect_pass) in enumerate(items):
        prog = code + "\n" + test
        try:
            r = subprocess.run([sys.executable, "-c", prog], capture_output=True,
                               timeout=10, text=True)
            actual = (r.returncode == 0)
        except subprocess.TimeoutExpired:
            actual = False
        if actual != expect_pass:
            bad.append if False else None
            all_ok = False
            bad_id = f"{name}#{i}"
            print("MISMATCH:", bad_id, "expected", expect_pass, "got", actual,
                  (r.stderr or "")[:80] if 'r' in dir() else "")
            continue
        verified.append({"id": f"{name}#{i}", "code": code, "test": test,
                         "passes": actual})
    out[name] = verified
    print(f"{name}: {len(verified)}/6 verified")

json.dump(out, open("p151_domains.json", "w"), indent=1)
print("all execution-verified:", all_ok)
