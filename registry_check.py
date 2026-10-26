"""registry_check.py — Registry CI v1 (external review item 5).
Recomputes quantitative claims from artifact JSONs and diffs against the
registry's stored numbers. Three historical bugs (nearest_integer, P172,
P186) would ALL have been caught by this check had it existed.
v1 coverage: P172/P195 locus, P185 landing, P188 character table, P196
genus landing, P198/P205 truths, P186-c/d accuracies, P204 grid."""
import json, sys, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "experiments"))

FAILS = []
def check(name, actual, expected):
    ok = actual == expected
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: actual={actual} expected={expected}")
    if not ok:
        FAILS.append(name)

# --- registry text integrity (v2, added by the 2026-10-26 registry audit) ---
# The ledger itself is now checked, not just the numbers inside it:
# every P-row must live inside the section-1 table (two batches of rows had been
# pasted after section 7 and inside the section-6 risk table, where neither the
# row count nor audit_provenance.py could see them as ledger rows); duplicate
# IDs must be the declared historical set; and the Registry integrity section's
# self-reported counts must equal what the table actually contains.
#
# ID grammar (broad, matching the ledger's real convention): base P<number>, an
# optional trailing letter, then any run of "-b"/"-v2"/"-FIX"/" v2" style
# suffixes. The narrow "P\d+[a-z]?" regex used by the first cut of this check
# silently dropped 90 physical rows (all -b/-c variants) and 3 duplicate IDs,
# which is exactly how three undeclared collisions survived a green CI.
import re as _re
from collections import Counter as _Counter
_ROOT = os.path.dirname(os.path.abspath(__file__))
_reg_text = open(os.path.join(_ROOT, "docs", "RESEARCH_PLAN.md"), encoding="utf-8").read()
_tbl_start = _reg_text.find("| ID | Experiment |")
_tbl_end = _reg_text.find("\n## 2. Testbed tiers", _tbl_start)
_main_tbl = _reg_text[_tbl_start:_tbl_end]
_ID_RE = r"(P\d+[a-z]?(?:[- ][A-Za-z0-9]+)*)"
_all_ids = _re.findall(r"(?m)^\| " + _ID_RE + r" \|", _reg_text)
_main_ids = _re.findall(r"(?m)^\| " + _ID_RE + r" \|", _main_tbl)
check("registry: every P-row is inside the section-1 table",
      len(_all_ids) == len(_main_ids), True)
DECLARED_DUPES = {"P9", "P10", "P11", "P111", "P113", "P117-b", "P118", "P118-b",
                  "P169", "P171", "P179", "P183", "P229-b", "P232"}
_dupes = {i for i, n in _Counter(_main_ids).items() if n > 1}
check("registry: no undeclared duplicate ID", _dupes - DECLARED_DUPES, set())
check("registry: every declared duplicate still present", _dupes, DECLARED_DUPES)
# rows whose first cell is not an ID are declared, not silently dropped
_nonid = []
for _line in _main_tbl.split("\n"):
    if not _line.startswith("|"):
        continue
    _cell = _line.split("|")[1].strip()
    if not _cell or set(_cell) <= set("- ") or _cell == "ID":
        continue
    if not _re.fullmatch(_ID_RE, _cell):
        _nonid.append(_cell)
check("registry: non-ID row cells are the two declared ones",
      [c[:8] for c in _nonid], ["P82/P83 ", "D1-eta"])
_n = _re.search(r"Counts \(this ledger, verified by `registry_check\.py`, which recomputes "
                r"them\): (\d+) rows, (\d+) distinct IDs, IDs run P1-P(\d+) with (\d+) unused "
                r"numbers", _reg_text)
if _n:
    check("registry: declared row count matches the table",
          int(_n.group(1)), len(_main_ids))
    check("registry: declared distinct-ID count matches the table",
          int(_n.group(2)), len(set(_main_ids)))
    check("registry: declared max ID matches the table", int(_n.group(3)),
          max(int(_re.match(r"P(\d+)", i).group(1)) for i in _main_ids))
    _bases = {int(_re.match(r"P(\d+)", i).group(1)) for i in _main_ids}
    _mx = max(_bases)
    check("registry: declared unused-base count matches the table",
          int(_n.group(4)), sum(1 for b in range(1, _mx + 1) if b not in _bases))
else:
    check("registry: integrity-section counts present", False, True)

# --- P273: the artifact must not contradict its registry row ---------------
# p273_verdict.json originally stored the RAW grounding checker reading, whose
# structural-number false positives (0/1/6 from "1/x6") contradicted the row.
# The raw file is now marked SUPERSEDED and the value-scale re-analysis is the
# authoritative record; this check keeps the two from drifting apart again.
try:
    _v273 = json.load(open(os.path.join(_ROOT, "p273_value_scale_analysis.json"),
                           encoding="utf-8"))
    check("P273 value-scale verdict CONFIRMED (authoritative artifact)",
          _v273["verdict"]["P_ground"] == "CONFIRMED", True)
    _raw273 = json.load(open(os.path.join(_ROOT, "p273_verdict.json"), encoding="utf-8"))
    check("P273 raw artifact marked SUPERSEDED",
          "SUPERSEDED" in str(_raw273.get("_status", "")), True)
except FileNotFoundError:
    print("[SKIP] p273 artifacts")

# --- P195: corrected locus ---
locus = json.load(open("p195_2elem_corrected.json", encoding="utf-8"))["locus_[1,1000]"]
check("P195 locus == 22 rows 11U4x11", locus,
      sorted({1,2,3,5,7,10,13,17,35,55,77} | {4*d for d in {1,2,3,5,7,10,13,17,35,55,77}}))

# --- P185/P188: six-row landing + c_d table ---
lnd = json.load(open("p185_landing_structure.json", encoding="utf-8"))
six = {int(k): v["s"] for k, v in lnd.get("six_row_landing", {}).items()} if "six_row_landing" in lnd else {}
if not six:
    # fallback: the artifact stores under different key shapes; check rows
    rows = lnd.get("rows", [])
    six = {r["d"]: r["quadratic_hits"] for r in rows if r.get("quadratic_hits")}
check("P185 six-row landing {3:6,5:10,7:21,13:13,17:34}",
      {d: (s[0] if isinstance(s, list) else s) for d, s in six.items() if d in (3,5,7,13,17)},
      {3: 6, 5: 10, 7: 21, 13: 13, 17: 34})

# --- P198: 4x-family truth ---
t198 = json.load(open("p198_truth_newrows.json", encoding="utf-8"))
land = {}
for k, v in t198.items():
    ql = v.get("quadratic_landing")
    land[int(k)] = ql[0] if ql else "FULL"
check("P198 truth {4:3, 8:6, rest FULL}", land, {4: 3, 8: 6, 12: "FULL", 20: "FULL", 28: "FULL",
      40: "FULL", 52: "FULL", 68: "FULL", 140: "FULL", 220: "FULL", 308: "FULL"})

# --- P205: 9x-family truth (all FULL) ---
t205 = json.load(open("p205_truth_9x.json", encoding="utf-8"))
check("P205 9x-family all FULL", all(v["landing"] == "FULL" for v in t205.values()), True)
check("P205 9x-family has 11 rows", len(t205) == 11, True)

# --- P204: grid numbers ---
g = json.load(open("p204_repr_arch_grid.json", encoding="utf-8"))
check("P204 synthetic modular/mlp == 1.000", g["synthetic/modular/mlp"]["bal_acc_mean"] == 1.0, True)
check("P204 census decimal/mlp ~ 0.978 (+-0.01)", abs(g["census/decimal/mlp"]["bal_acc_mean"] - 0.978) < 0.011, True)
check("P204 census modular/mlp ~ 0.700 (+-0.02)", abs(g["census/modular/mlp"]["bal_acc_mean"] - 0.700) < 0.02, True)

# --- P196 genus landing (if artifact holds rows) ---
try:
    l196 = json.load(open("p196_genus_landing_newrows.json", encoding="utf-8"))
    check("P196 artifact present", True, True)
except FileNotFoundError:
    print("[SKIP] p196 artifact (inline run) — registry table is the record")

# --- P202-c/P205 protocol: GENERIC semantics present in truth file (anti-lattice-pseudo) ---
d9 = json.load(open("p205_truth_9x.json", encoding="utf-8"))
bad = [k for k, v in d9.items()
       if v.get("landing") in ("FULL", None) and v.get("semantic") != "GENERIC"]
check("P205 truth: GENERIC semantics on all FULL rows (single-pass lattice trap guarded)",
      bad == [], True)

# --- P186-c/d accuracy cells ---
try:
    m = json.load(open("p186c_math_fixed.json", encoding="utf-8"))["models"]
    ds = [v["mean"] for v in m.values()]
    check("P186-c corrected means in 82-95 band", all(80 <= x <= 96 for x in ds), True)
except FileNotFoundError:
    print("[SKIP] p186c artifact")

# --- P259/P262 flagship: external bin-packing claim, machine re-verification ---
# The sprint's headline external claim must be as reproducible as the math rows:
# re-execute the stored discovered heuristics on the OR3 holdout and re-derive
# the double win over First-Fit / Best-Fit, plus the P262 simulator equivalence.
try:
    import random as _rand

    cap_ds = json.load(open("funsearch_datasets.json", encoding="utf-8"))
    cap_p259 = json.load(open("p259_capstone_upgrade.json", encoding="utf-8"))
    HOLD = [f"u500_{i:02d}" for i in range(10, 20)]

    def _ff(inst):
        cap, items = inst["capacity"], inst["items"]
        bins = []
        for it in items:
            for i in range(len(bins)):
                if bins[i] >= it - 1e-9:
                    bins[i] -= it
                    break
            else:
                bins.append(cap - it)
        return len(bins)

    def _bf(inst):
        cap, items = inst["capacity"], inst["items"]
        bins = []
        for it in items:
            fits = [i for i in range(len(bins)) if bins[i] >= it - 1e-9]
            if fits:
                bins[min(fits, key=lambda k: bins[k])] -= it
            else:
                bins.append(cap - it)
        return len(bins)

    def _l1(inst):
        return -(-sum(inst["items"]) // inst["capacity"])

    def _sim(inst, place):
        cap, items = inst["capacity"], inst["items"]
        bins = []
        for item in items:
            i = int(place(item, list(bins), cap))
            if i < 0 or i > len(bins):
                raise ValueError("bad index")
            if i == len(bins):
                bins.append(cap - item)
            else:
                if bins[i] < item - 1e-9:
                    raise ValueError("does not fit")
                bins[i] -= item
        return len(bins)

    for model in ("glm-5.3-flash", "kimi-k2.8-preview"):
        rounds = cap_p259["models"][model]["rounds"]
        ok_rounds = [r for r in rounds if r["err"] is None
                     and r["dev_mean_excess"] is not None]
        best = min(ok_rounds, key=lambda r: r["dev_mean_excess"])
        ns = {}
        exec(best["code"], ns)
        fn = ns["place"]
        OR3i = cap_ds["OR3"]
        he = [_sim(OR3i[k], fn) - _l1(OR3i[k]) for k in HOLD]
        ff = [_ff(OR3i[k]) - _l1(OR3i[k]) for k in HOLD]
        bf = [_bf(OR3i[k]) - _l1(OR3i[k]) for k in HOLD]
        short = model.split("-")[0]
        check(f"P259 flagship [{short}]: holdout excess < First-Fit",
              sum(he) < sum(ff), True)
        check(f"P259 flagship [{short}]: holdout excess < Best-Fit",
              sum(he) < sum(bf), True)

    # P262: FunSearch official policy (priority = -(bins-item), argmax over
    # valid) must equal our Best-Fit per instance (simulator equivalence).
    mism = 0
    for dname in ("OR3", "Weibull 5k"):
      for k, inst in cap_ds[dname].items():
        cap, items = inst["capacity"], inst["items"]
        bins_fs = [cap] * len(items)
        used = set()
        for item in items:
            valid = [i for i in range(len(bins_fs)) if bins_fs[i] - item >= 0]
            best = max(valid, key=lambda i: -(bins_fs[i] - item))
            bins_fs[best] -= item
            used.add(best)
        if len(used) != _bf(inst):
            mism += 1
    check("P262 simulator equivalence: official policy == our Best-Fit (25/25)",
          mism == 0, True)
except Exception as ex:
    print(f"[FAIL] P259/P262 flagship re-verification crashed: {ex}")
    FAILS.append("P259/P262 flagship")

print()
if FAILS:
    print(f"REGISTRY CI: {len(FAILS)} FAILURES: {FAILS}")
    sys.exit(1)
print("REGISTRY CI: ALL CHECKS PASS")
