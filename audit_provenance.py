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
        m = re.match(r"(.*batch)(\d+)-(\d+)(_.*)?$", f)
        if m and int(m.group(3)) > int(m.group(2)):
            pre, lo, hi, suf = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4) or ""
            for i in range(lo, hi + 1):
                cited.setdefault(f"{pre}{i}{suf}", set()).add(pid)
            continue
        cited.setdefault(f, set()).add(pid)

missing, present = [], 0
for f, pids in sorted(cited.items()):
    base = os.path.basename(f)
    def exists_any(name):
        # exact, then suffix match (model-suffixed artifacts like
        # p144_doubao-seed-2.1-lite.json get mis-split by the citation
        # regex at "2." — P149 audit false positive fix)
        if os.path.exists(name) or os.path.exists("docs/" + name):
            return True
        try:
            candidates = [".", "experiments/data"] + [d for d in os.listdir(".")
                                  if os.path.isdir(d) and not d.startswith(".")]
            return any(fn.endswith(name)
                       for cand in candidates
                       for fn in os.listdir(cand))
        except OSError:
            return False
    if exists_any(base):
        present += 1
    else:
        missing.append((base, sorted(pids)))

# rows explicitly marked inline/absent (ARTIFACT-NOTE) are acknowledged
acknowledged = [(f, pids) for f, pids in missing
                if all("ARTIFACT-NOTE" in entries.get(p, "") for p in pids)]
missing = [(f, pids) for f, pids in missing if (f, pids) not in acknowledged]

print(f"cited files: {len(cited)}, present: {present}, "
      f"acknowledged-absent: {len(acknowledged)}, MISSING: {len(missing)}")
for f, pids in acknowledged:
    print(f"  ABSENT-ACKNOWLEDGED {f}   cited by {','.join(pids)}")
for f, pids in missing:
    print(f"  MISSING {f}   cited by {','.join(pids)}")
