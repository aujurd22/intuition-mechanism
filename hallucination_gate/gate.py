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
        if verdict == "RATIONAL":
            receipt["status"] = "VERIFIED"
            receipt["note"] = "machine-verified integer row"
        elif verdict == "NEAR_INTEGER":
            # P142 three-band: machine itself is ambiguous -> downgrade to ABSTAIN
            receipt["status"] = "ABSTAIN"
            receipt["note"] = ("near-integer trap (Ramanujan shadow): machine "
                               "confidence 0.5 — claim downgraded, do not ship as fact")
        else:
            receipt["status"] = "REFUTED"
            receipt["note"] = "verifier says NOT integer — intercepted"
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
