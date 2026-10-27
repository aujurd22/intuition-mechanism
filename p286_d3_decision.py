# -*- coding: utf-8 -*-
"""d3 decision adapter for FastUse — vllm-sr/d3-flash (Decision 3.0).
Working interface (verified live): model.system_one(state, questions) with
  choice questions -> {"type": "choice", "criteria": {opt: desc}, ...}
  noul questions   -> {"type": "noul", "criteria": {"true":..., "false":...}}
Returns calibrated probabilities per option.
"""
import os
import json

MODEL_DIR = "D:/models/d3-flash"
_MODEL = None


def get_model(device="cuda"):
    global _MODEL
    if _MODEL is None:
        from transformers import AutoModel
        _MODEL = AutoModel.from_pretrained(
            MODEL_DIR, trust_remote_code=True).to(device).eval()
    return _MODEL


def decide(state_lines, subgoal, image=None):
    """One decision: compact state + sub-goal -> next action with calibrated
    probability + feasibility.  Returns dict with choice/probabilities."""
    model = get_model()
    state_obj = {"elements": state_lines, "subgoal": subgoal}
    kwargs = {}
    if image:
        kwargs["images"] = [image]
    result = model.system_one(
        state=state_obj,
        questions={
            "next_action": {
                "type": "choice",
                "criteria": {ln.split("]")[0][1:]: ln
                             for ln in state_lines},
                "instructions": ("pick the element ref whose action best "
                                 "advances the sub-goal")},
            "subgoal_feasible": {
                "type": "noul",
                "criteria": {"true": "the sub-goal can be completed from "
                                     "this page",
                             "false": "it cannot"},
                "instructions": "judge feasibility on this page"}},
        **kwargs)
    answers = result.get("answers", {})
    na = answers.get("next_action", {})
    feas = answers.get("subgoal_feasible", {})
    return {"choice": na.get("choice"),
            "probabilities": na.get("probabilities", {}),
            "confidence": na.get("confidence"),
            "feasible": feas.get("noul"),
            "usage": result.get("usage", {}),
            "raw": result}


if __name__ == "__main__":
    d = get_model()
    state = ['[e1] input id=username "用户名" value=""',
             '[e2] input id=password "密码" value=""',
             '[e3] button "登录"']
    r = decide(state, "用 admin/admin123 登录")
    print(json.dumps({k: v for k, v in r.items() if k != "raw"},
                     ensure_ascii=False, indent=1, default=str))
