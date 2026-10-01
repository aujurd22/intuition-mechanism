"""SDB domain 2: code DESIGN-PATTERN discovery (P148 second key experiment).

Hidden structure S: the team design rule "functions must not mutate their
input arguments" (pure vs input-mutating).  ALL functions pass their unit
tests — the tests only check return values, so pass/fail carries ZERO
information about S.  Discovery = inferring the rule from labeled
examples; Transfer = new function shapes (dict, list, nested).

Verifier: mechanical purity check — deepcopy the inputs, run, compare.
"""
import copy
import json

ITEMS = [
    {"id": "dp01", "passes": True, "label": "PURE",
     "code": "def normalize(nums):\n    return [n / max(nums) for n in nums]\n",
     "test": "from copy import deepcopy\ninp = [2, 4, 8]\nsnap = deepcopy(inp)\nassert normalize(inp) == [0.25, 0.5, 1.0]\nassert inp == snap\n"},
    {"id": "dp02", "passes": True, "label": "PURE",
     "code": "def top_scores(scores, k):\n    return sorted(scores, reverse=True)[:k]\n",
     "test": "from copy import deepcopy\ninp = [3, 9, 1]\nsnap = deepcopy(inp)\nassert top_scores(inp, 2) == [9, 3]\nassert inp == snap\n"},
    {"id": "dp03", "passes": True, "label": "PURE",
     "code": "def merge_dicts(a, b):\n    out = dict(a)\n    out.update(b)\n    return out\n",
     "test": "from copy import deepcopy\nx = {'k': 1}\nsnap = deepcopy(x)\nassert merge_dicts(x, {'m': 2}) == {'k': 1, 'm': 2}\nassert x == snap\n"},
    {"id": "dp04", "passes": True, "label": "PURE",
     "code": "def moving_avg(xs, w):\n    return [sum(xs[i:i+w])/w for i in range(len(xs)-w+1)]\n",
     "test": "from copy import deepcopy\ninp = [1, 2, 3, 4]\nsnap = deepcopy(inp)\nassert moving_avg(inp, 2) == [1.5, 2.5, 3.5]\nassert inp == snap\n"},
    {"id": "dp05", "passes": True, "label": "IMPURE",
     "code": "def add_defaults(cfg):\n    cfg.setdefault('retries', 3)\n    cfg.setdefault('timeout', 30)\n    return cfg\n",
     "test": "from copy import deepcopy\ninp = {'host': 'db'}\nsnap = deepcopy(inp)\nassert add_defaults(inp)['retries'] == 3\nassert inp == snap\n",
     "trap": "setdefault MUTATES the input dict in place"},
    {"id": "dp06", "passes": True, "label": "IMPURE",
     "code": "def sort_records(records):\n    records.sort(key=lambda r: r['ts'])\n    return records\n",
     "test": "from copy import deepcopy\ninp = [{'ts': 3}, {'ts': 1}]\nsnap = deepcopy(inp)\nassert [r['ts'] for r in sort_records(inp)] == [1, 3]\nassert inp == snap\n",
     "trap": "list.sort() mutates in place (should be sorted())"},
    {"id": "dp07", "passes": True, "label": "IMPURE",
     "code": "def saturate(values, cap):\n    for i, v in enumerate(values):\n        if v > cap:\n            values[i] = cap\n    return values\n",
     "test": "from copy import deepcopy\ninp = [5, 20, 7]\nsnap = deepcopy(inp)\nassert saturate(inp, 10) == [5, 10, 7]\nassert inp == snap\n",
     "trap": "writes through the list reference"},
    {"id": "dp08", "passes": True, "label": "PURE",
     "code": "def saturate(values, cap):\n    return [min(v, cap) for v in values]\n",
     "test": "from copy import deepcopy\ninp = [5, 20, 7]\nsnap = deepcopy(inp)\nassert saturate(inp, 10) == [5, 10, 7]\nassert inp == snap\n"},
    {"id": "dp09", "passes": True, "label": "IMPURE",
     "code": "def with_discounts(cart):\n    for item in cart:\n        item['price'] *= 0.9\n    return cart\n",
     "test": "from copy import deepcopy\ninp = [{'price': 100}]\nsnap = deepcopy(inp)\nassert with_discounts(inp)[0]['price'] == 90.0\nassert inp == snap\n",
     "trap": "mutates nested dicts through references"},
    {"id": "dp10", "passes": True, "label": "PURE",
     "code": "def with_discounts(cart):\n    return [{**item, 'price': item['price'] * 0.9} for item in cart]\n",
     "test": "from copy import deepcopy\ninp = [{'price': 100}]\nsnap = deepcopy(inp)\nassert with_discounts(inp)[0]['price'] == 90.0\nassert inp == snap\n"},
]


def purity_check(code: str, test: str, timeout: int = 10) -> dict:
    """Mechanical design-rule verifier: deepcopy inputs, run code+test,
    compare.  PASS == PURE (input unmodified)."""
    import subprocess, sys
    harness = (
        "from copy import deepcopy\n"
        "import json\n"
        "code = '''" + code.replace("'''", "''\\'\\''") + "'''\n"
        "exec(compile(code, 'candidate', 'exec'))\n"
    )
    # simpler & robust: run code + test as-is; the test ALREADY snapshots and
    # compares — but only if the test asserts it.  Our tests do assert it.
    prog = code + "\n" + test
    try:
        r = subprocess.run([sys.executable, "-c", prog],
                           capture_output=True, timeout=timeout, text=True)
        passed = (r.returncode == 0)
        trail = (r.stderr or "")[-250:]
    except subprocess.TimeoutExpired:
        passed, trail = False, "timeout"
    return {"verdict": "PURE" if passed else "IMPURE",
            "confidence": 1.0 - 1e-9,
            "typed": {"kind": "choice",
                      "options": {"PURE": 1.0 - 1e-9 if passed else 1e-9,
                                  "IMPURE": 1e-9 if passed else 1.0 - 1e-9}},
            "confidence_basis": "direct_execution",
            "exec_trail": trail}


if __name__ == "__main__":
    bad = []
    for it in ITEMS:
        out = purity_check(it["code"], it["test"])
        got = out["verdict"]
        if got != it["label"]:
            bad.append((it["id"], it["label"], got, out["exec_trail"][:100]))
    print(f"purity verifier vs labels: {'ALL ' + str(len(ITEMS)) + ' OK' if not bad else bad}")
    assert not bad
    json.dump(ITEMS, open("sdb_codepattern_items.json", "w"), indent=1)
    print("saved sdb_codepattern_items.json")
