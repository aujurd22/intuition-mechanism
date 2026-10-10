# -*- coding: utf-8 -*-
"""hallucination-gate v3 upgrade 1+2: coordinate-adaptive evidence + tiered
evidence ladder.

Law anchors:
  P270  — evidence must live in the MODEL's coordinate system, or name the
          mismatch (27/27 zero-precision predictions were coordinate-mismatched)
  P240  — scalar feedback <= 0 flow; row labels ~2 calls; numeric evidence
          transfers.  Labels are the active ingredient, NOT quantity.
  P248  — numeric evidence buys transfer; labels only patch.
  Prop4 — history non-accumulation for scalars; cache realizability.

Public API:
  coordinate_adaptive_feedback(claim_cells, actual_cells) -> str
      Builds feedback anchored in the MODEL's own claimed coordinates,
      naming the mismatch class when detected.
  tiered_evidence(round_no, claim_cells, actual_cells, mode) -> (level, text)
      Ladder: rich3 (labels) -> rich5 (labels + model-anchor) ->
      rich10 (numeric values).  Escalates only on repeated failure.
"""
import json

# ---------- coordinate-mismatch detection (P270 lesson mechanized) ----------

def _detect_mismatch(claim_cells, actual_cells):
    """Heuristics for the P270 coordinate-mismatch classes.

    claim_cells / actual_cells: [(row, col, after), ...]
    Returns (mismatch_class, hint) or (None, "").
    """
    if not claim_cells or not actual_cells:
        return None, ""
    # class 1: transposed indices — claimed (r,c) matches actual (c,r)
    actual_t = {(c, r) for r, c, _ in actual_cells}
    hits_t = sum(1 for r, c, _ in claim_cells if (r, c) in actual_t)
    # class 2: off-by-one (1-based rows)
    actual_o = {(r + 1, c) for r, c, _ in actual_cells}
    actual_o2 = {(r, c + 1) for r, c, _ in actual_cells}
    hits_o = sum(1 for r, c, _ in claim_cells if (r + 1, c) in actual_o or
                 (r, c + 1) in actual_o2)
    n = min(len(claim_cells), 8)
    if hits_t >= max(2, n // 3):
        return "TRANSPOSED", ("your (row, col) look TRANSPOSED vs the frame's "
                              "array indexing — swap row and column")
    if hits_o >= max(2, n // 3):
        return "OFF_BY_ONE", ("your indices look 1-BASED while the frame is "
                              "0-BASED — subtract 1 from row and column")
    # class 3: row-col swapped region anchor (claimed block far from actual block)
    ar = sum(r for r, _, _ in actual_cells) / len(actual_cells)
    ac = sum(c for _, c, _ in actual_cells) / len(actual_cells)
    cr = sum(r for r, _, _ in claim_cells) / len(claim_cells)
    cc = sum(c for _, c, _ in claim_cells) / len(claim_cells)
    if math_hypot(ar - cr, ac - cc) > 10:
        return "REGION_MISMATCH", ("your predicted region is far from where the "
                                   "frame actually changed — re-locate the "
                                   "active region first")
    return None, ""


def math_hypot(a, b):
    return (a * a + b * b) ** 0.5


def coordinate_adaptive_feedback(claim_cells, actual_cells):
    """P270 lesson, mechanized: anchor the feedback in the model's own
    claimed coordinates AND name the mismatch class when detected."""
    cls, hint = _detect_mismatch(claim_cells, actual_cells)
    parts = []
    if cls:
        parts.append(f"COORDINATE MISMATCH DETECTED ({cls}): {hint}")
    if claim_cells:
        mine = "; ".join(f"you claimed ({r},{c})->{v}" for r, c, v in claim_cells[:5])
        parts.append(f"Your claims, in YOUR coordinates: {mine}")
    if actual_cells:
        real = "; ".join(f"({r},{c})->{v}" for r, c, v in actual_cells[:8])
        parts.append(f"Frame-true changes (array coords, row 0 = top): {real}")
    return " ".join(parts) if parts else "no cell changes occurred at all"


# ---------- tiered evidence ladder (P240/P248 mechanized) ----------

LEVELS = ("rich3", "rich5", "rich10")


def tiered_evidence(round_no, claim_cells, actual_cells, grid_fn=None):
    """Escalating evidence per P240/P248:
      round 1     -> rich3  (which cells changed — labels only)
      round 2     -> rich5  (labels + model-anchored coordinate repair)
      round >=3   -> rich10 (labels + anchor + numeric values via grid_fn)
    Returns (level_name, evidence_text).
    """
    lvl = LEVELS[min(max(round_no - 1, 0), 2)]
    base = coordinate_adaptive_feedback(claim_cells, actual_cells)
    if lvl == "rich3":
        actual = "; ".join(f"({r},{c})->{v}" for r, c, v in actual_cells[:8]) \
            if actual_cells else "none"
        return lvl, f"changed cells: {actual}"
    if lvl == "rich5":
        return lvl, base
    # rich10: numeric evidence (P248: the transfer tier)
    extra = ""
    if grid_fn and actual_cells:
        vals = "; ".join(f"({r},{c}) g={grid_fn(r, c)}->{v}"
                         for r, c, v in actual_cells[:8])
        extra = f" Numeric grid values: {vals}."
    return lvl, base + extra
