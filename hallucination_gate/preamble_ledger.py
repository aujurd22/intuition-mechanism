# -*- coding: utf-8 -*-
"""hallucination-gate v3 upgrade 3+4: preamble protocol + prediction ledger.

Law anchors:
  P270 — declaring the coordinate system up front catches frame errors
         before generation (cheaper than post-hoc repair)
  P198 — verification pressure converges to memorization; the fix is NOT
         to suppress speculation but to make it a checkable asset
  P265 — updates pointed at the correct function are the signal; the
         ledger turns speculations into directional, checkable commitments

Public API:
  preamble_prompt(domain_hint="")  -> str
      Inject into any agent prompt: forces the model to declare its
      coordinate system / assumptions before the claim.
  check_preamble(preamble: str) -> dict
      Mechanical consistency checks on the declared frame (naming classes
      from P270: 0- vs 1-based, transposed, missing).
  PredictionLedger(path)  — SPECULATION upgrade (zone 4):
      .record(claim, prediction) -> id   every speculation becomes a
          checkable commitment (never silently dropped)
      .resolve(id, observed)  -> verdict  mechanical check when the
          environment answers; hit-rate feeds back as direction signal
      .stats()  -> {open, resolved, hit_rate}  — the ledger's own
          calibration, auditable.
"""
import json
import os
import time

DEFAULT_LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "prediction_ledger.jsonl")


def preamble_prompt(domain_hint: str = "") -> str:
    base = ("Before answering, state a one-line PREAMBLE declaring: "
            "(1) your coordinate/indexing convention (e.g. 'row 0 = top, "
            "0-based'), (2) any assumption you are making about the input "
            "format. Then give your answer.")
    if domain_hint:
        base += f" Domain note: {domain_hint}"
    return base


def check_preamble(preamble: str) -> dict:
    """Mechanical consistency checks on a declared frame.
    Flags the P270 mismatch classes when the declaration contradicts itself
    or omits the required fields."""
    low = preamble.lower()
    checks = {
        "declares_indexing": any(k in low for k in
                                 ("0-based", "1-based", "row 0", "index 0",
                                  "1-indexed", "zero-based")),
        "declares_origin": ("top" in low or "bottom" in low or
                            "left" in low or "first" in low),
        "contradictory": (("0-based" in low and "1-based" in low) or
                          ("row 0" in low and "row 1 = first" in low)),
    }
    ok = checks["declares_indexing"] and checks["declares_origin"] \
        and not checks["contradictory"]
    return {"ok": ok, "checks": checks,
            "note": "" if ok else
            ("preamble contradicts itself" if checks["contradictory"]
             else "preamble missing indexing/origin declaration")}


class PredictionLedger:
    """Zone-4 upgrade: SPECULATION ships labeled AND recorded as a checkable
    commitment.  Resolution is mechanical when the environment answers."""

    def __init__(self, path: str = DEFAULT_LEDGER):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    def _append(self, obj):
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    def _rows(self):
        if not os.path.exists(self.path):
            return []
        return [json.loads(l) for l in open(self.path, encoding="utf-8")]

    def record(self, claim: str, prediction: str) -> dict:
        rec = {"id": f"pred-{int(time.time() * 1000)}", "claim": claim[:200],
               "prediction": prediction[:300], "status": "OPEN",
               "ts": time.time()}
        self._append(rec)
        return rec

    def resolve(self, pred_id: str, observed: str, hit: bool) -> dict:
        rows = self._rows()
        out = None
        for r in rows:
            if r.get("id") == pred_id:
                r["status"] = "RESOLVED"
                r["observed"] = observed[:200]
                r["hit"] = bool(hit)
                r["resolved_ts"] = time.time()
                out = r
        with open(self.path, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        return out or {}

    def stats(self) -> dict:
        rows = self._rows()
        resolved = [r for r in rows if r.get("status") == "RESOLVED"]
        hits = sum(1 for r in resolved if r.get("hit"))
        return {"open": sum(1 for r in rows if r.get("status") == "OPEN"),
                "resolved": len(resolved),
                "hit_rate": round(hits / len(resolved), 3) if resolved else None}
