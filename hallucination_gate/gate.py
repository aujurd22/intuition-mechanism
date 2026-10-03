"""hallucination-gate v1 — the output toll booth (幻觉拦截器).

外部评审的幻觉解剖（四区）与处置：
  zone 1 验证器可得域  -> 执行机械验证器：VERIFIED / REFUTED
  zone 2 长尾事实      -> 无验证器：ABSTAIN（引用策略 v2 接入点）
  zone 3 影子规则      -> 规则类主张：影子邻域对比（v2 接入点，P-LAW1 区）
  zone 4 洞见前沿      -> SPECULATION 标签（不可消灭，只分拣）

任何 LLM 主张必须以四态之一出厂：
  VERIFIED (附验证轨迹) / REFUTED (默认拦截) / ABSTAIN / SPECULATION
设计原则（评审原文）：消灭幻觉 = 消灭洞见（④区），终局是分拣系统，
不是零幻觉。
"""
import json
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from intuition_pack.verifiers import run_verifier  # noqa: E402

AUDIT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit_log.jsonl")

STATUSES = ("VERIFIED", "REFUTED", "ABSTAIN", "SPECULATION")


def gate_claim(claim: str, kind: str = "auto", payload: dict | None = None) -> dict:
    """Route a claim through the toll booth. Returns a receipt."""
    receipt = {"claim": claim, "kind": kind, "ts": time.time()}

    if kind in ("auto", "sixrow") and payload and "d" in payload:
        receipt["zone"] = 1
        v = run_verifier("lambert_sixrow", {"d": int(payload["d"])})
        receipt["verifier"] = "lambert_sixrow"
        receipt["evidence"] = {k: v[k] for k in ("verdict", "confidence", "in_band", "value")
                               if k in v}
        verdict = v["verdict"]
        claimed = (payload or {}).get("claimed")   # model's claimed direction
        if verdict == "NEAR_INTEGER":
            # P142 three-band: machine itself is ambiguous -> downgrade to ABSTAIN
            receipt["status"] = "ABSTAIN"
            receipt["note"] = ("near-integer trap (Ramanujan shadow): machine "
                               "confidence 0.5 — claim downgraded, do not ship as fact")
        elif claimed and claimed != verdict:
            # model claim contradicts the machine -> REFUTED regardless of direction
            receipt["status"] = "REFUTED"
            receipt["note"] = (f"model claimed {claimed}, machine verdict {verdict} "
                               f"(1/x6 = {v.get('value')}) — intercepted")
        else:
            # machine verdict reached with no contradicting claim (or claim agrees)
            receipt["status"] = "VERIFIED"
            receipt["note"] = f"machine verdict {verdict}, claim consistent"
    elif kind == "fact":
        receipt["zone"] = 2
        receipt["status"] = "ABSTAIN"
        receipt["note"] = "long-tail factual claim with no registered verifier — " \
                          "ship only with citation (citation policy v2 pending)"
    elif kind == "rule":
        receipt["zone"] = 3
        receipt["status"] = "ABSTAIN"
        receipt["note"] = "rule-type claim: shadow-neighborhood contrast required " \
                          "(P-LAW1 zone; contrast tests v2 pending)"
    elif kind == "novel":
        receipt["zone"] = 4
        receipt["status"] = "SPECULATION"
        receipt["note"] = "novel claim ships with the SPECULATION label — " \
                          "indistinguishable from hallucination at generation time"
    else:
        receipt["zone"] = 2
        receipt["status"] = "ABSTAIN"
        receipt["note"] = "unknown claim kind — default abstain"

    receipt["intercepted"] = receipt["status"] == "REFUTED"
    audit(receipt)
    return receipt


def audit(receipt):
    with open(AUDIT_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(receipt, ensure_ascii=False) + "\n")


def audit_tail(n=10):
    if not os.path.exists(AUDIT_PATH):
        return []
    lines = open(AUDIT_PATH, encoding="utf-8").readlines()
    return [json.loads(l) for l in lines[-n:]]


def gate_batch(claims: list) -> list:
    return [gate_claim(**c) if isinstance(c, dict) else gate_claim(c) for c in claims]


# ---------------- v2: enforce loop (harness semantics) ----------------
#
# ARCHITECTURE (answering: harness part or filter?):
#   The gate is a HARNESS COMPONENT sitting between model and user:
#
#     user question
#        │
#        ▼
#     model ──claim──► GATE ──VERIFIED──► user (+ evidence)
#        ▲              │
#        │ REFUTED +    ├──ABSTAIN──► user (labeled "machine unsure")
#        │ refutation   └──SPECULATION──► user (labeled, zone 4 only)
#        └───────────────┘  (regeneration loop, max_rounds)
#
# What reaches the user: a VERIFIED answer (with evidence) or an honestly
# labeled abstain/speculation.  A REFUTED claim NEVER ships — it loops back
# to the model with the refutation evidence until fixed or rounds exhausted.


def enforce(question: str, ask_fn, kind: str = "sixrow",
            payload: dict | None = None, max_rounds: int = 3,
            extract_claim=None) -> dict:
    """Regeneration loop: REFUTED claims go BACK to the model with the
    refutation evidence; the user only ever sees a verified answer or an
    honestly labeled abstain.

    ask_fn(prompt) -> str   : the model's text output
    extract_claim(text)->str: pull the claim word (e.g. RATIONAL/NOT) from output
    """
    extract = extract_claim or (lambda t: (
        "RATIONAL" if "RATIONAL" in t.upper()[:60] else
        ("NOT" if "NOT" in t.upper()[:60] else "?")))
    prompt = question
    trace = []
    for rnd in range(1, max_rounds + 1):
        text = ask_fn(prompt)
        claim_word = extract(text)
        # gate the claim the same way regardless of wording
        pl = dict(payload or {})
        pl["claimed"] = claim_word if claim_word in ("RATIONAL", "NOT") else None
        r = gate_claim(f"{question} [model claim: {claim_word}]", kind=kind,
                       payload=pl)
        trace.append({"round": rnd, "model_text": text[:200],
                      "claim": claim_word, "gate_status": r["status"],
                      "note": r.get("note", "")})
        if r["status"] == "VERIFIED":
            # ship immediately — continuing only risks a later round
            # overwriting a verified answer (the d=5 triple-VERIFIED loss)
            final = {"answer": text.strip(), "ship_status": "VERIFIED",
                     "evidence": r.get("evidence"), "rounds_used": rnd,
                     "trace": trace}
            audit({"enforce": "closed", "rounds": rnd, "status": "VERIFIED",
                   "question": question[:80]})
            return final
        if r["status"] in ("ABSTAIN", "SPECULATION"):
            # user-facing semantic: the MODEL TEXT DOES NOT SHIP on abstain —
            # the user gets the machine evidence + an honest label instead
            final = {"answer": f"(abstain: machine confidence 0.5 on this row — "
                               f"no reliable answer shipped. machine evidence: "
                               f"{json.dumps(r.get('evidence'))})",
                     "ship_status": r["status"], "evidence": r.get("evidence"),
                     "rounds_used": rnd, "trace": trace}
            audit({"enforce": "closed", "rounds": rnd, "status": r["status"],
                   "question": question[:80]})
            return final
            audit({"enforce": "closed", "rounds": rnd, "status": r["status"],
                   "question": question[:80]})
            return final
        # REFUTED: feed the refutation back
        prompt = (f"{question}\n\n"
                  f"Your previous answer was '{claim_word}', but a mechanical "
                  f"verifier REFUTED it: {r.get('note','')}. Re-examine and "
                  "answer again with exactly one word: RATIONAL or NOT.")
    # rounds exhausted — honest abstain ships, never the refuted claim
    final = {"answer": "(abstain: claim could not be verified within the "
                       "round budget)",
             "ship_status": "ABSTAIN", "evidence": None,
             "rounds_used": max_rounds, "trace": trace}
    audit({"enforce": "exhausted", "rounds": max_rounds,
           "question": question[:80]})
    return final
