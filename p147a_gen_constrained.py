"""P147a: generate the constrained-set domain programmatically.

Task shape (real-agent高频): an object + a claimed constraint list; decide
whether the object satisfies ALL claimed constraints.  LLM known weakness:
missing one constraint out of several.  Verifier: mechanical per-constraint
evaluation with a structured violation report (the auditability payload).

12 items: 6 fully-satisfying, 6 violating exactly one constraint
(which constraint is violated varies across items).
"""
import json
import random
from sympy import isprime

rng = random.Random(20261001)


def gen_satisfying(checks, keys, tries=4000):
    """Construct, not rejection-sample: pre-filter the candidate pool by
    attribute constraints (prime/even), sample from it, then retry on the
    relational constraints (sum/diff)."""
    attr_pools = {
        "all_prime": [p for p in range(2, 90) if isprime(p)],
        "all_even": list(range(2, 91, 2)),
    }
    base = list(range(2, 91))
    for k in keys:
        if k in attr_pools:
            base = attr_pools[k]
    n = 7 if "len_is_7" in keys else 6
    for _ in range(tries):
        obj = sorted(rng.sample(base, min(n, len(base))))
        if len(obj) < 4:
            continue
        if "sum_is_100" in keys:
            # repair sum: adjust the largest element to close the gap
            gap = 100 - sum(obj[:-1])
            if gap in base and gap not in obj[:-1]:
                obj[-1] = gap
                obj = sorted(obj)
        if "max_min_diff_30" in keys and obj:
            target_hi = obj[0] + 30
            if target_hi in base and target_hi not in obj[1:]:
                obj[-1] = target_hi
                obj = sorted(obj)
        if all(c(obj) for c in checks):
            return obj
    return None


CONSTRAINT_BANK = {
    "sum_is_100": (lambda o: sum(o) == 100, "the elements sum to exactly 100"),
    "len_is_7": (lambda o: len(o) == 7, "the list has exactly 7 elements"),
    "all_prime": (lambda o: all(isprime(x) for x in o), "every element is a prime number"),
    "all_even": (lambda o: all(x % 2 == 0 for x in o), "every element is even"),
    "strictly_increasing": (lambda o: all(o[i] < o[i+1] for i in range(len(o)-1)),
                            "the elements are strictly increasing"),
    "no_duplicates": (lambda o: len(set(o)) == len(o), "the elements are pairwise distinct"),
    "max_min_diff_30": (lambda o: max(o) - min(o) == 30, "max - min == 30"),
    "contains_20": (lambda o: 20 in o, "the value 20 is present"),
}

SETS = [
    ["len_is_7", "all_prime", "strictly_increasing"],
    ["sum_is_100", "all_even", "no_duplicates"],
    ["len_is_7", "all_even", "max_min_diff_30", "no_duplicates"],
    ["sum_is_100", "no_duplicates", "strictly_increasing"],
    ["all_prime", "no_duplicates", "max_min_diff_30"],
    ["len_is_7", "all_even", "contains_20"],
]

items = []
for si, keys in enumerate(SETS):
    cons = [{"name": k, "text": CONSTRAINT_BANK[k][1]} for k in keys]
    checks = [CONSTRAINT_BANK[k][0] for k in keys]
    obj = gen_satisfying(checks, keys)
    assert obj is not None, keys
    items.append({"id": f"cs{si*2+1:02d}", "object": obj,
                  "constraints": cons, "passes": True})
    # violating twin: break exactly one constraint (rotate which)
    vi = si % len(keys)
    for _ in range(500):
        bad = obj[:]
        idx = rng.randrange(len(bad))
        old = bad[idx]
        new = rng.randint(2, 90)
        if new == old:
            continue
        bad[idx] = new
        bad_sorted_ok = all(c(bad) for j, c in enumerate(checks) if j != vi)
        if (not checks[vi](bad)) and bad_sorted_ok:
            items.append({"id": f"cs{si*2+2:02d}", "object": bad,
                          "constraints": cons, "passes": False,
                          "violated": keys[vi]})
            break
    else:
        items.append({"id": f"cs{si*2+2:02d}", "object": obj,
                      "constraints": cons, "passes": True,
                      "note": "generator fallback"})

# final execution-verified truth pass
bad = []
for it in items:
    checks = [CONSTRAINT_BANK[c["name"]][0] for c in it["constraints"]]
    actual = all(c(it["object"]) for c in checks)
    if actual != it["passes"]:
        bad.append((it["id"], it["passes"], actual))
    it["passes"] = actual
print(f"{len(items)} items; truth mismatches after re-execution: {bad or 'none'}")
assert not bad
json.dump(items, open("constrained_items.json", "w"), indent=1)
print("saved constrained_items.json:",
      sum(1 for i in items if i["passes"]), "pass /",
      sum(1 for i in items if not i["passes"]), "violate")
