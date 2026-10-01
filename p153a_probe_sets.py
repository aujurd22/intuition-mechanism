"""P153a: enlarged probe sets for the Insight Arena (v2).

Track MATH:  32 probes — 6 rows re-shown (consistency) + 26 non-rows
             (20 in-band [18,300] + 6 out-of-band [301,1000]); ground
             truth = P142a census (zero errors on [1,1000]).
Track SCI:   30 series across regimes B/C/D (15 normal, 15 phase-inverted).
Track CODE:  20 functions — 10 PURE + 10 IMPURE across 10 mutation types,
             all tests-passing (pass/fail carries no signal).
"""
import json
import math
import random
import subprocess
import sys


def build_math_probes(seed=20261001):
    census = json.load(open("p142a_census_1000.json", encoding="utf-8"))
    hits = {d for d, _, _ in census["hits"]}
    from p33_n20 import params_for
    rng = random.Random(seed)
    non = [d for d in range(18, 1001) if d not in hits]
    rng.shuffle(non)
    probes = []
    for d in (1, 3, 5, 7, 13, 17):
        x0, lam = params_for(d)
        probes.append({"d": d, "x0": f"{x0:.6f}", "lam": f"{lam:.6f}",
                       "truth": "RATIONAL", "kind": "row_consistency"})
    for d in non[:20]:
        x0, lam = params_for(d)
        probes.append({"d": d, "x0": f"{x0:.6f}", "lam": f"{lam:.6f}",
                       "truth": "NOT", "kind": "in_band"})
    for d in non[20:26]:
        x0, lam = params_for(d)
        probes.append({"d": d, "x0": f"{x0:.6f}", "lam": f"{lam:.6f}",
                       "truth": "NOT", "kind": "out_of_band"})
    rng.shuffle(probes)
    return probes


def gen_series(T, gamma, A=1.0, n=40, dt=0.25, anomaly=False):
    xs = []
    for i in range(n):
        t = i * dt
        v = A * math.exp(-gamma * t) * math.sin(2 * math.pi * t / T)
        if anomaly and (i // 5) % 2 == 1:
            v = -v
        xs.append(round(v, 4))
    return xs


def build_sci_probes(seed=20261002):
    rng = random.Random(seed)
    regimes = [(3.0, 0.20), (4.0, 0.05), (5.0, 0.30), (6.0, 0.15)]
    probes = []
    k = 0
    for T, g in regimes:
        for anom in (False, True):
            for rep in range(2):
                k += 1
                A = round(1.0 + 0.4 * ((k + rep) % 3), 2)
                xs = gen_series(T, g, A=A, anomaly=anom)
                probes.append({"series": xs, "anomalous": anom,
                               "regime": f"T{T}-g{g}"})
    rng.shuffle(probes)
    return probes


PAIRS = [
    ("def drop_tail(lst, k):\n    return lst[:-k] if k else lst[:]\n",
     "from copy import deepcopy\ninp=[1,2,3]\ns=deepcopy(inp)\nassert drop_tail(inp,1)==[1,2]\nassert inp==s\n",
     "def drop_tail(lst, k):\n    del lst[len(lst)-k:]\n    return lst\n",
     "from copy import deepcopy\ninp=[1,2,3]\ns=deepcopy(inp)\nassert drop_tail(inp,1)==[1,2]\nassert inp==s\n",
     "del on input reference"),
    ("def canon_keys(d):\n    return {k.strip().lower(): v for k, v in d.items()}\n",
     "from copy import deepcopy\ninp={'A ':1}\ns=deepcopy(inp)\nassert canon_keys(inp)=={'a':1}\nassert inp==s\n",
     "def canon_keys(d):\n    for k in list(d):\n        d[k.strip().lower()] = d.pop(k)\n    return d\n",
     "from copy import deepcopy\ninp={'A ':1}\ns=deepcopy(inp)\nassert canon_keys(inp)=={'a':1}\nassert inp==s\n",
     "pop-rewrite of input dict"),
    ("def filled(grid, val):\n    return [[val for _ in row] for row in grid]\n",
     "from copy import deepcopy\ninp=[[0],[0]]\ns=deepcopy(inp)\nassert filled(inp,7)==[[7],[7]]\nassert inp==s\n",
     "def filled(grid, val):\n    for row in grid:\n        row[0] = val\n    return grid\n",
     "from copy import deepcopy\ninp=[[0],[0]]\ns=deepcopy(inp)\nassert filled(inp,7)==[[7],[7]]\nassert inp==s\n",
     "writes through nested rows"),
    ("def tagged(items, tag):\n    return [dict(x, tag=tag) for x in items]\n",
     "from copy import deepcopy\ninp=[{'v':1}]\ns=deepcopy(inp)\nassert tagged(inp,'t')==[{'v':1,'tag':'t'}]\nassert inp==s\n",
     "def tagged(items, tag):\n    for x in items:\n        x['tag'] = tag\n    return items\n",
     "from copy import deepcopy\ninp=[{'v':1}]\ns=deepcopy(inp)\nassert tagged(inp,'t')==[{'v':1,'tag':'t'}]\nassert inp==s\n",
     "adds key to input dicts"),
    ("def shifted(xs):\n    return [x + 1 for x in xs]\n",
     "from copy import deepcopy\ninp=[1,2]\ns=deepcopy(inp)\nassert shifted(inp)==[2,3]\nassert inp==s\n",
     "def shifted(xs):\n    for i in range(len(xs)):\n        xs[i] += 1\n    return xs\n",
     "from copy import deepcopy\ninp=[1,2]\ns=deepcopy(inp)\nassert shifted(inp)==[2,3]\nassert inp==s\n",
     "in-place increment"),
    ("def ensure_header(rows, header):\n    return [header] + list(rows)\n",
     "from copy import deepcopy\ninp=[['a']]\ns=deepcopy(inp)\nassert ensure_header(inp,['h'])==[['h'],['a']]\nassert inp==s\n",
     "def ensure_header(rows, header):\n    rows.insert(0, header)\n    return rows\n",
     "from copy import deepcopy\ninp=[['a']]\ns=deepcopy(inp)\nassert ensure_header(inp,['h'])==[['h'],['a']]\nassert inp==s\n",
     "insert into input list"),
    ("def cleaned(s):\n    return ' '.join(s.split())\n",
     "assert cleaned(' a  b ') == 'a b'\n",
     "import re\n\ndef cleaned(s):\n    return re.sub(r'\\s+', ' ', s.strip())\n",
     "assert cleaned(' a  b ') == 'a b'\n",
     "NEGATIVE CONTROL: strings immutable — both variants PURE by nature"),
    ("def bounded(d, cap):\n    return {k: min(v, cap) for k, v in d.items()}\n",
     "from copy import deepcopy\ninp={'x':9}\ns=deepcopy(inp)\nassert bounded(inp,5)=={'x':5}\nassert inp==s\n",
     "def bounded(d, cap):\n    for k in d:\n        d[k] = min(d[k], cap)\n    return d\n",
     "from copy import deepcopy\ninp={'x':9}\ns=deepcopy(inp)\nassert bounded(inp,5)=={'x':5}\nassert inp==s\n",
     "in-place dict value clamp"),
    ("def zipped(a, b):\n    return list(zip(a, b))\n",
     "from copy import deepcopy\nx,y=[1,2],['a','b']\nsx,sy=deepcopy(x),deepcopy(y)\nassert zipped(x,y)==[(1,'a'),(2,'b')]\nassert x==sx and y==sy\n",
     "def zipped(a, b):\n    while len(b) < len(a):\n        b.append(None)\n    return list(zip(a, b))\n",
     "from copy import deepcopy\nx,y=[1,2],['a']\nsx,sy=deepcopy(x),deepcopy(y)\nassert zipped(x,y)==[(1,'a'),(2,None)]\nassert y==sy\n",
     "appends pad None into input b"),
    ("def clipped(d, cap):\n    return {k: (v if v <= cap else cap) for k, v in d.items()}\n",
     "from copy import deepcopy\ninp={'p':3}\ns=deepcopy(inp)\nassert clipped(inp,2)=={'p':2}\nassert inp==s\n",
     "def clipped(d, cap):\n    d.update({k: min(v, cap) for k, v in d.items()})\n    return d\n",
     "from copy import deepcopy\ninp={'p':3}\ns=deepcopy(inp)\nassert clipped(inp,2)=={'p':2}\nassert inp==s\n",
     "update() on input dict"),
]


def build_code_probes():
    import subprocess
    probes = []
    bad = []
    for i, (pure_code, pure_test, imp_code, imp_test, note) in enumerate(PAIRS):
        is_control = "NEGATIVE CONTROL" in note
        kinds = ("PURE", "PURE") if is_control else ("PURE", "IMPURE")
        for kind, code, test in zip(kinds, (pure_code, imp_code),
                                    (pure_test, imp_test)):
            prog = code + "\n" + test
            r = subprocess.run([sys.executable, "-c", prog],
                               capture_output=True, timeout=10, text=True)
            # PURE items must pass their tests; IMPURE items must FAIL
            # them (the test asserts input non-mutation — designed fail)
            expected_rc0 = (kind == "PURE")
            if (r.returncode == 0) != expected_rc0:
                bad.append((i, kind, r.stderr[-120:]))
                continue
            probes.append({"id": f"cp{i:02d}-{kind}", "code": code,
                           "test": test, "truth": kind, "trap": note})
    if bad:
        print("execution-check failures:", bad)
    return probes


if __name__ == "__main__":
    m = build_math_probes()
    s = build_sci_probes()
    c = build_code_probes()
    json.dump({"math": m, "sci": s, "code": c},
              open("p153a_probe_sets.json", "w"), indent=1)
    print(f"math probes: {len(m)}, sci probes: {len(s)}, code probes: {len(c)}")
