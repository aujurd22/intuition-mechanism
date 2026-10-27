# -*- coding: utf-8 -*-
"""P287 daemon: d3-flash decision layer + this session's computer-use tools
operating the REAL desktop (Notepad task: type text, save as file).

The conversation model (this session's LLM) drives everything through
computer-use MCP tools; d3-flash supplies calibrated per-action decisions.
"""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p286_d3_decision import decide as d3_decide

if __name__ == "__main__":
    print(__doc__)
    print("run via the session's computer-use tools; d3 decisions are taken "
          "in-loop by the operator")
