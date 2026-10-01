"""Structure Discovery Benchmark (SDB) v0 — P148.

The benchmark formalizes "insight" as three computable metrics over a
domain (observations D, hidden structure S, held-out probes P):

  1. COMPRESSION  mdl_ratio = bits(D) / bits(rule)
                  (rule = the discovered compressed description)
  2. TRANSFER     accuracy of the discovered rule on probes drawn from a
                  DIFFERENT carrier than the discovery set (the P32
                  cross-family line: integers -> matrices; here: regime A
                  -> regime B)
  3. SURPRISE     detection rate of the structure class NOT mentioned in
                  the task charter (the hidden/anomaly class)

A mechanism "passes" a domain if it discovers S (surprise), compresses
it (mdl_ratio >> 1), and the compression TRANSFERS (probe accuracy).
The same harness runs over every domain — that is the generalization
claim being tested.
"""
from dataclasses import dataclass, field


@dataclass
class SDBDomain:
    name: str
    observations: list      # the discovery set (with ground truth attached)
    probes: list            # transfer probes (same structure, new carrier)
    rule_reference: str     # the reference compressed rule (for MDL numerator)
    charter: str            # what the judge is TOLD (deliberately incomplete:
                            #   the hidden structure is not named)


@dataclass
class SDBResult:
    domain: str
    discovery_acc: float = None     # did the mechanism find S on D?
    transfer_acc: float = None      # does S hold on P?
    mdl_ratio: float = None         # compression
    surprise_found: bool = None     # was the hidden class detected?
    notes: str = ""
