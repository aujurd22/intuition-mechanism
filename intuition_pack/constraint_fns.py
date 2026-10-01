"""Persistent constraint-function registry (loaded by verifiers at import;
runtime register_constraint adds domain-specific ones on top)."""
from sympy import isprime

BUILT_IN = {
    "sum_is_100": lambda o: sum(o) == 100,
    "len_is_7": lambda o: len(o) == 7,
    "all_prime": lambda o: all(isprime(x) for x in o),
    "all_even": lambda o: all(x % 2 == 0 for x in o),
    "all_odd": lambda o: all(x % 2 == 1 for x in o),
    "strictly_increasing": lambda o: all(o[i] < o[i+1] for i in range(len(o)-1)),
    "no_duplicates": lambda o: len(set(o)) == len(o),
    "max_min_diff_30": lambda o: max(o) - min(o) == 30,
    "contains_20": lambda o: 20 in o,
}
