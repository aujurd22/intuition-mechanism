# -*- coding: utf-8 -*-
"""hallucination-gate middleware — 自动中间件层
Every llm_client.ask() call goes through the gate automatically.
REFUTED claims are regenerated with evidence. VERIFIED ships with proof.
ABSTAIN ships honestly labeled.

Usage:
    from hallucination_gate.middleware import gated_ask
    answer = gated_ask("is d=5 RATIONAL?", domain="sixrow", payload={"d": 5})
"""
import json, os, sys, re, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from hallucination_gate.gate import gate_claim, audit  # noqa: E402

MAX_ROUNDS = 3


def gated_ask(question: str, ask_fn=None, domain: str = "sixrow",
              payload: dict | None = None, max_rounds: int = MAX_ROUNDS) -> dict:
    """Ask the LLM, gate the output, regenerate on REFUTED.
    Returns a receipt with: answer (verified or abstain), status, evidence, trace.

    This is the HARNESS middleware — every LLM output passes through here
    before reaching the user.  A refuted claim NEVER ships.
    """
    if ask_fn is None:
        import llm_client
        ask_fn = llm_client.ask
    pl = dict(payload or {})
    prompt = question
    trace = []

    for rnd in range(1, max_rounds + 1):
        text = ask_fn(prompt)
        claim_word = _extract(text)
        pl["claimed"] = claim_word if claim_word in ("RATIONAL", "NOT") else None

        r = gate_claim(f"{question} [model claim: {claim_word}]",
                       kind=domain, payload=pl)

        trace.append({"round": rnd, "claim": claim_word,
                      "gate_status": r["status"],
                      "model_text_snippet": text[:150]})

        if r["status"] == "VERIFIED":
            audit({"middleware": "closed", "rounds": rnd,
                   "status": "VERIFIED", "question": question[:80]})
            return {"answer": text.strip(), "ship_status": "VERIFIED",
                    "evidence": r.get("evidence"),
                    "rounds_used": rnd, "trace": trace}

        if r["status"] in ("ABSTAIN", "SPECULATION"):
            audit({"middleware": "closed", "rounds": rnd,
                   "status": r["status"], "question": question[:80]})
            return {"answer": f"(abstain: machine confidence insufficient — "
                              f"no reliable answer shipped. evidence: "
                              f"{json.dumps(r.get('evidence', r.get('note','')))})",
                    "ship_status": r["status"],
                    "evidence": r.get("note"), "rounds_used": rnd,
                    "trace": trace}

        # REFUTED: feed back to the model with the evidence
        prompt = (f"{question}\n\n"
                  f"Your previous answer '{claim_word}' was REFUTED by a mechanical "
                  f"verifier ({r.get('note','')}). "
                  "Re-examine and answer again with exactly one word: RATIONAL or NOT.")

    # exhausted — honest abstain, never the refuted claim
    audit({"middleware": "exhausted", "rounds": max_rounds,
           "question": question[:80]})
    return {"answer": "(abstain: could not verify within round budget)",
            "ship_status": "ABSTAIN", "evidence": None,
            "rounds_used": max_rounds, "trace": trace}


def _extract(text: str) -> str:
    upper = text.upper()[:80]
    if "RATIONAL" in upper:
        return "RATIONAL"
    if "NOT" in upper:
        return "NOT"
    return "?"


def wrap_llm_client(domain: str = "sixrow", max_rounds: int = 3):
    """Decorator/factory: returns a gated version of llm_client.ask()"""
    def gated(prompt: str, **kwargs) -> str:
        r = gated_ask(prompt, ask_fn=lambda q: _raw_ask(q, **kwargs),
                      domain=domain, max_rounds=max_rounds)
        return r["answer"]
    return gated


def _raw_ask(prompt: str, **kwargs) -> str:
    import llm_client
    return llm_client.ask(prompt, **kwargs)
