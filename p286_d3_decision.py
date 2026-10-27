# -*- coding: utf-8 -*-
"""d3 decision adapter for FastUse — loads vllm-sr/d3-flash locally and turns
compact state + sub-goal into action decisions with calibrated probabilities.

The d3 model's native interface is model.system_one(state, questions) —
state in (text/JSON/images), typed questions out with probabilities.
FastUse's decision layer needs exactly this: given the compact element list,
pick the next action (typed choice) with a probability.

Usage (once weights are downloaded to D:/models/d3-flash):
  from p286_d3_decision import D3Decision
  d = D3Decision()
  d.decide(state_lines, subgoal, available_actions) -> {action, ref, ...,
      probability, raw}
"""
import os
import json

MODEL_DIR = "D:/models/d3-flash"

class D3Decision:
    def __init__(self, model_dir=MODEL_DIR, device="cuda"):
        from transformers import AutoModel
        self.model = AutoModel.from_pretrained(
            model_dir, trust_remote_code=True).to(device).eval()
        self.device = device

    def decide(self, state_lines, subgoal, actions, image=None):
        """state_lines: compact element list; actions: allowed action names
        for the next step (click/fill/select/check/done); image optional."""
        state = "\n".join(state_lines)
        q_choice = {"question": ("Which single action best advances the "
                                 "sub-goal?"),
                    "options": actions}
        q_conf = {"question": ("How confident are you in this action? "
                               "Rate 0-100."), "type": "score"}
        result = self.model.system_one(
            state={"elements": state_lines, "subgoal": subgoal},
            images=[image] if image else [],
            questions={"next_action": q_choice, "confidence": q_conf})
        return result
