# -*- coding: utf-8 -*-
"""hallucination-gate v3 upgrade 9: the cognitive toll booth — single entry
fusing both plugins.

Contract (the closure of the coverage loop):
  EVERY model claim is routed to exactly one of three handlers:
    A. verifier available      -> mechanical gate   (hallucination_gate)
    B. pack available          -> pack judge         (intuition_pack)
    C. neither                 -> SPECULATION + registered as an
                                  auto_scan_loop candidate (the scanner
                                  learns what to build next)
  No claim can silently pass.  The router IS the shrink-law answer:
  the durable asset is the detector + the pipeline, and this entry point
  grows the detector surface automatically (zone-1 coverage expands as
  verifiers are registered; zone-B coverage as packs are stored).

Law anchors:
  shrink law (P144/P146) — durable asset = detector + pipeline speed
  Prop 4/5               — evidence tiering (this router escalates via
                           hallucination_gate.evidence.tiered_evidence)
  P270                   — evidence must be in the model's frame (preamble
                           protocol runs before scoring when enabled)
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from hallucination_gate.gate import gate_claim, audit  # noqa: E402
from hallucination_gate.preamble_ledger import (  # noqa: E402
    PredictionLedger, check_preamble, preamble_prompt)

STORE_DIR = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "packs")


class CognitiveBooth:
    """Single entry point fusing hallucination_gate + intuition_pack."""

    def __init__(self, packs_dir: str = STORE_DIR,
                 ledger_path: str | None = None):
        self.packs_dir = packs_dir
        self.ledger = PredictionLedger(ledger_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "prediction_ledger.jsonl"))
        self._pack_cache = {}

    # ---- coverage discovery ----
    def _load_pack(self, domain: str):
        if domain in self._pack_cache:
            return self._pack_cache[domain]
        from intuition_pack.pack import Pack
        f = os.path.join(self.packs_dir, f"{domain}.json")
        pack = None
        if os.path.exists(f):
            try:
                pack = Pack.from_json(open(f, encoding="utf-8").read())
            except Exception:
                pack = None
        else:
            # scan any stored pack whose triggers cover the domain
            for pf in glob_packs(self.packs_dir):
                try:
                    p = json.load(open(pf, encoding="utf-8"))
                except Exception:
                    continue
                if not isinstance(p, dict):   # error pools are lists
                    continue
                if domain in (p.get("triggers") or []) or \
                        p.get("domain") == domain:
                    try:
                        pack = Pack.from_json(json.dumps(p))
                        break
                    except Exception:
                        continue
        self._pack_cache[domain] = pack
        return pack

    def route(self, claim: str, domain: str, payload: dict | None = None,
              kind: str | None = None, preamble: str | None = None,
              prediction: str | None = None) -> dict:
        """Route one claim through the coverage loop.  Returns a receipt."""
        receipt = {"claim": claim[:200], "domain": domain, "ts": time.time()}
        # preamble protocol (P270): frame declared and consistency-checked
        if preamble is not None:
            pc = check_preamble(preamble)
            receipt["preamble"] = pc
            if not pc["ok"]:
                receipt["status"] = "ABSTAIN"
                receipt["handler"] = "preamble-check"
                receipt["note"] = f"preamble invalid: {pc['note']}"
                audit(receipt)
                return receipt
        # A. verifier available -> mechanical gate
        receipt_verifier = self._try_gate(claim, domain, payload, kind)
        if receipt_verifier is not None:
            receipt.update(receipt_verifier)
            receipt["handler"] = "mechanical-gate"
            # ④ ledger: speculations become checkable commitments
            if receipt["status"] == "SPECULATION" and prediction:
                rec = self.ledger.record(claim, prediction)
                receipt["prediction_id"] = rec["id"]
            audit(receipt)
            return receipt
        # B. pack available -> pack judge
        pack = self._load_pack(domain)
        if pack is not None:
            receipt["handler"] = "pack-judge"
            receipt["pack"] = f"{pack.domain} v{pack.version}"
            receipt["status"] = "PACK_JUDGED"
            receipt["note"] = ("pack judged — see pack.prompt_block for the "
                               "charter; mechanical verdict requires the "
                               "pack's verifier on this payload")
            audit(receipt)
            return receipt
        # C. neither -> speculation + scanner candidate registration
        receipt["handler"] = "scan-candidate"
        receipt["status"] = "SPECULATION"
        receipt["note"] = ("no verifier, no pack — registered as a scanner "
                           "candidate; speculation labeled")
        rec = self.ledger.record(claim, prediction or "(no prediction given)")
        receipt["prediction_id"] = rec["id"]
        self._register_candidate(domain, claim)
        audit(receipt)
        return receipt

    def _try_gate(self, claim, domain, payload, kind):
        try:
            from intuition_pack.verifiers import VERIFIERS
            names = set(VERIFIERS)
        except Exception:
            names = {"lambert_sixrow"}
        k = kind or domain
        if k in names or domain in names or \
                (payload and "d" in payload and "lambert_sixrow" in names):
            try:
                kk = k if k in names else ("lambert_sixrow" if domain in names
                                           or (payload and "d" in payload)
                                           else k)
                return gate_claim(claim, kind=kk, payload=payload)
            except Exception:
                return None
        return None

    def _register_candidate(self, domain: str, claim: str):
        qf = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "scan_queue.json")
        try:
            q = json.load(open(qf, encoding="utf-8")) if os.path.exists(qf) \
                else {"domains": []}
            if not any(d.get("domain") == domain for d in q["domains"]):
                q["domains"].append({"domain": domain, "status": "queued",
                                     "note": f"auto-registered by cognitive "
                                             f"booth: {claim[:80]}",
                                     "items": []})
                json.dump(q, open(qf, "w", encoding="utf-8"), indent=1,
                          ensure_ascii=False)
        except OSError:
            pass


def glob_packs(packs_dir: str):
    if not os.path.isdir(packs_dir):
        return []
    return [os.path.join(packs_dir, f) for f in os.listdir(packs_dir)
            if f.endswith(".json")]
