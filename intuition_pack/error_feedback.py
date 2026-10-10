# -*- coding: utf-8 -*-
"""intuition_pack v3 upgrade 7: error-pool feedback into pack building.

Law anchor: P138 (+41-50pp from discriminative exemplars) + the error-pool
mechanism wired into auto_scan_loop (every judged item joins
packs/<domain>_errors.json).  This module closes the loop: new packs are
built FROM the error pool first — the judge's own mistakes are the highest-
value contrast examples.

Public API:
  build_pack_with_errors(domain, charter, items, verifier, packs_dir,
                         source) -> (Pack, stats)
      items: fresh candidates (may be empty).  The error pool is merged in:
        pool items that the current pack/judge got wrong are the priors.
      stats: {"pool_size", "pool_reused", "fresh_added", "dedup_dropped"}
"""
import json
import os

from intuition_pack.pack import build_pack


def load_error_pool(packs_dir: str, domain: str) -> list:
    f = os.path.join(packs_dir, f"{domain}_errors.json")
    if os.path.exists(f):
        try:
            return json.load(open(f, encoding="utf-8"))
        except Exception:
            return []
    return []


def build_pack_with_errors(domain: str, charter: str, items: list,
                           verifier: dict, packs_dir: str,
                           source: str = "", max_exemplars: int = 12):
    pool = load_error_pool(packs_dir, domain)
    seen = set()
    exemplars = []
    pool_reused = 0
    # pool first: the judge's own mistakes are the contrast priors
    for it in pool:
        if len(exemplars) >= max_exemplars // 2:
            break
        if it["id"] in seen:
            continue
        exemplars.append({"d": it["id"],
                          "inputs": {"code": it.get("code", ""),
                                     "test": it.get("test", "")},
                          "label": "PASS" if it.get("passes") else "FAIL",
                          "note": "error-pool prior (judged by the loop)"})
        seen.add(it["id"])
        pool_reused += 1
    fresh_added = 0
    for it in items:
        if len(exemplars) >= max_exemplars:
            break
        if it.get("id") in seen:
            continue
        exemplars.append({"d": it["id"],
                          "inputs": {"code": it.get("code", ""),
                                     "test": it.get("test", "")},
                          "label": "PASS" if it.get("passes") else "FAIL",
                          "note": "fresh candidate"})
        seen.add(it["id"])
        fresh_added += 1
    pack = build_pack(domain, charter, exemplars, verifier, source=source)
    stats = {"pool_size": len(pool), "pool_reused": pool_reused,
             "fresh_added": fresh_added, "dedup_dropped": len(pool) + len(items)
             - pool_reused - fresh_added}
    return pack, stats
