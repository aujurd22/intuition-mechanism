"""Provenance audit: every artifact filename cited in docs/RESEARCH_PLAN.md
must exist in the repo (or be explicitly marked as inline/absent).

Extracts .json/.npy/.txt/.png/.md filenames from the registry rows and
checks existence at the repo root and under docs/.  Reports missing ones
with the P-number that cites them.
"""
import re, os

text = open("docs/RESEARCH_PLAN.md", encoding="utf-8").read()
rows = re.findall(r"^\| (P\d+[a-z]?(?:-[a-z0-9]+)?) \|", text, re.M)
# map row-id -> row text
entries = {}
for m in re.finditer(r"^\| (P\d+[a-z]?(?:-[a-z0-9]+)?) \|(.*?)\|$",
                     text, re.M | re.S):
    entries[m.group(1)] = m.group(2)

cited = {}
for pid, body in entries.items():
    for f in re.findall(r"[\w/\\-]+\.(?:json|npy|txt|png|csv|npz)", body):
        f = f.strip().split()[-1]
        m = re.match(r"(.*batch)(\d+)-(\d+)(\.\w+)$", f)
        if m:  # range shorthand "batch1-10.json" expands to per-batch files
            for i in range(int(m.group(2)), int(m.group(3)) + 1):
                cited.setdefault(f"{m.group(1)}{i}{m.group(4)}", set()).add(pid)
            continue
        cited.setdefault(f, set()).add(pid)

missing, present = [], 0
for f, pids in sorted(cited.items()):
    base = os.path.basename(f)
    if os.path.exists(f) or os.path.exists(base) or os.path.exists("docs/" + base):
        present += 1
    else:
        missing.append((base, sorted(pids)))

print(f"cited files: {len(cited)}, present: {present}, MISSING: {len(missing)}")
for f, pids in missing:
    print(f"  MISSING {f}   cited by {','.join(pids)}")
