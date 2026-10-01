"""pack_probe: the compression-domain detector (P144 protocol mechanized).

Question answered: is THIS domain worth building a pack for?
Method: few-shot learning curve on the domain's own items with ground
truth — accuracy at k = 0, 2, 8 in-context exemplars.  Verdict:
  gain(k=8) - acc(k=0) >= 15pp  -> COMPRESSION domain (build the pack;
      discriminative information concentrates in few exemplars)
  gain < 5pp                    -> DISTRIBUTIONAL domain (zero-shot is at
      the pack's ceiling; do not build — P144's IMDB/AG News finding)
  in between                    -> BORDERLINE (build only with more
      exemplars; report the curve)
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_client import ask_chat


def _fmt_example(item):
    code = item["code"]
    test = item["test"]
    label = "PASS" if item["passes"] else "FAIL"
    return f"CODE:\n{code}\nTESTS:\n{test}\nVERDICT: {label}"


def probe_prompt(items, exemplars, k):
    lines = []
    if k:
        lines.append("Calibration exemplars (execution-verified):")
        for e in exemplars[:k]:
            lines.append(_fmt_example(e))
        lines.append("")
    lines.append("For each candidate, judge whether the CODE passes the "
                 "TESTS. Judge only the code's structure against the tests.")
    for i, item in enumerate(items, 1):
        lines.append(f"--- Candidate {i} ---")
        lines.append(f"CODE:\n{item['code']}")
        lines.append(f"TESTS:\n{item['test']}")
    lines.append("\nAnswer exactly one line per candidate, in order: "
                 "'<i>: PASS' or '<i>: FAIL'.")
    return "\n".join(lines)


def parse_batch(ans, n):
    out = {}
    for m in re.finditer(r"(\d+)\s*[:\-]\s*(PASS|FAIL)", ans, re.I):
        out[int(m.group(1))] = m.group(2).upper() == "PASS"
    return [out.get(i) for i in range(1, n + 1)]


def probe(domain_items, exemplar_pool, model=None, ks=(0, 2, 8),
          max_batch=11, seed=20261001):
    """NOTE (P145, the positive-only poisoning rule): exemplar_pool MUST
    mix labels and the prompt must carry the contrast declaration —
    a positive-only pack pulled the census probe from 86.4 to 27.3
    (the all-RATIONAL prior).  Pools with a single label are rejected."""
    """Run the learning curve.  domain_items: list with ground truth
    ('passes'); exemplar_pool: separate items for in-context examples."""
    import importlib
    import llm_client
    if model:
        os.environ["ARK_MODEL"] = model
        importlib.reload(llm_client)
    truth = [it["passes"] for it in domain_items]
    labels = {it["passes"] for it in exemplar_pool}
    if len(labels) < 2 and exemplar_pool:
        return {"error": "POISONOUS-POOL: exemplar pool has a single label "
                "(P145 positive-only rule); mix in boundary negatives"}
    rng = __import__("random").Random(seed)

    curve = {}
    for k in ks:
        # rotate the exemplar pool per run so the pack isn't tuned to items
        pool = exemplar_pool[:] if k else []
        rng.shuffle(pool)
        preds = None
        # batch all items in ONE call (they are small) for cost control
        for attempt in range(3):
            ans = ask_chat(probe_prompt(domain_items, pool, k), max_tokens=2048)
            preds = parse_batch(ans, len(domain_items))
            if all(p is not None for p in preds):
                break
        if preds is None or any(p is None for p in preds):
            curve[k] = {"acc": None, "error": "unparseable"}
            continue
        correct = sum(int(p == t) for p, t in zip(preds, truth))
        curve[k] = {"acc": round(100 * correct / len(truth), 1)}
    g = (curve.get(8, {}).get("acc") or 0) - (curve.get(0, {}).get("acc") or 0)
    a8 = curve.get(8, {}).get("acc") or 0
    a0 = curve.get(0, {}).get("acc") or 0
    # P145 three-layer verdict + the form-sensitivity caveat:
    # batch probes CANNOT predict single-turn deployment gains (measured:
    # census batch k=0 = 95.5 vs single-turn A = 59.1, P138).  The probe
    # reliably detects TOXICITY (pack crashes accuracy) and SATURATION
    # (zero-shot ceiling); a compression-gain claim requires the
    # single-turn protocol.
    if a8 < a0 - 5:
        verdict = "TOXIC (pack hurts — do not build; check for "                   "positive-only exemplar bias)"
    elif g >= 15 and a8 >= 95:
        # P147: a strong gain to a saturated ceiling is a compression
        # signal even when zero-shot is decent — the pack closes the
        # remaining gap (constrained-set: 78.6 -> 100, gain 21.4)
        verdict = "COMPRESSION SIGNAL (confirm with single-turn protocol)"
    elif a0 >= 95 and a8 >= 95:
        verdict = "SATURATED-IN-BATCH (zero-shot already at ceiling; "                   "pack redundant in this form)"
    elif g >= 15:
        verdict = "COMPRESSION SIGNAL (confirm with single-turn protocol)"
    else:
        verdict = "NO BATCH SIGNAL (single-turn re-probe required)"
    return {"curve": curve, "gain_k8": round(g, 1), "verdict": verdict,
            "form_caveat": "batch-probe; single-turn may differ (P145)"}
