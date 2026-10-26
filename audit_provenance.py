"""Provenance audit v2 (2026-10-26): every artifact cited by a registry row must
exist in the repo, or the row must say so with an ARTIFACT-NOTE.

v1 (kept below as history) was falsely clean:
  - it scanned only json|npy|txt|png|csv|npz, so scripts (.py), jsonl logs (.jsonl)
    and docs (.md) were never checked;
  - a shorthand citation like "p232_four_model_probe.py/.json" reduced to
    basename ".json", and the existence test was `fn.endswith(".json")`, which
    matches ANY json in a directory — 27 shorthand citations passed vacuously;
  - duplicate-ID rows were collapsed into a dict, so the first row of every
    duplicated ID was never audited.

v2: recursive file index, exact basename / relative-path matching, compound
citations expanded, duplicate rows kept, and a non-zero exit when a citation is
missing without an ARTIFACT-NOTE.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.join(ROOT, "docs", "RESEARCH_PLAN.md")
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules"}

# --- file index ----------------------------------------------------------
basenames, relpaths = set(), set()
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        basenames.add(fn)
        rel = os.path.relpath(os.path.join(dirpath, fn), ROOT).replace("\\", "/")
        relpaths.add(rel)

# --- registry rows (duplicates kept) ------------------------------------
ID_RE = re.compile(r"^P\d+[a-z]?(?:[- ][A-Za-z0-9]+)*$")
rows = []  # (row_id, body)
with open(PLAN, encoding="utf-8") as f:
    for line in f:
        if not line.startswith("| "):
            continue
        cells = line.rstrip("\n").split("|")
        if len(cells) < 3:
            continue
        rid = cells[1].strip()
        if ID_RE.match(rid):
            rows.append((rid, line))

CITE_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.\-/]*\.(?:json|npy|txt|png|csv|npz|py|jsonl|md)\b")


def expand(tok):
    """'a.py/.json' -> ['a.py', 'a.json'];  '/.json' -> [];  'out/p275/x.json' -> itself."""
    tok = tok.strip("/")
    if not tok:
        return []
    if "/." in tok:
        head, tail = tok.split("/.", 1)
        base, _, ext = head.rpartition(".")
        out = [head]
        if base:
            out.append(base + "." + tail)
        return out
    return [tok]


cited = {}  # filename -> set(row ids)
for rid, body in rows:
    for m in CITE_RE.finditer(body):
        for f in expand(m.group(0)):
            cited.setdefault(f, set()).add(rid)

# Two known citation shapes are expanded, not reported:
#  (a) batch ranges: "p32f_batch1-10_answers.json" means batch1 .. batch10
#  (b) fragments: a token that is a SUFFIX of a citation that does exist is a
#      piece of that citation (the P172 row even quotes "1-lite.json" as the
#      false positive the old audit produced); it is reported, not counted.
_BATCH = re.compile(r"^(.*batch)(\d+)-(\d+)(_\w+)?\.json$")
for f in [k for k in cited if _BATCH.match(k)]:
    m = _BATCH.match(f)
    pre, lo, hi, suf = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4) or ""
    rids = cited.pop(f)
    for i in range(lo, hi + 1):
        cited.setdefault(f"{pre}{i}{suf}.json", set()).update(rids)

def exists(f):
    return f in relpaths or os.path.basename(f) in basenames

present, missing, acknowledged, fragments = [], [], [], []
present_names = [f for f in cited if exists(f)]
for f, rids in sorted(cited.items()):
    if exists(f):
        present.append(f)
        continue
    if any(p.endswith(f) and len(p) > len(f) for p in present_names):
        fragments.append((f, sorted(rids)))
        continue
    if all("ARTIFACT-NOTE" in b for r, b in rows if r in rids):
        acknowledged.append((f, sorted(rids)))
    else:
        missing.append((f, sorted(rids)))

print(f"cited files: {len(cited)}, present: {len(present)}, "
      f"acknowledged-absent: {len(acknowledged)}, fragment-of-present: {len(fragments)}, "
      f"MISSING: {len(missing)}")
for f, rids in fragments:
    print(f"  FRAGMENT-OF-PRESENT {f}   cited by {','.join(rids)}")
for f, rids in acknowledged:
    print(f"  ABSENT-ACKNOWLEDGED {f}   cited by {','.join(rids)}")
for f, rids in missing:
    print(f"  MISSING {f}   cited by {','.join(rids)}")
sys.exit(1 if missing else 0)
