# -*- coding: utf-8 -*-
"""P289: three borrowed improvements to FastUse (P288 survey integration).

B1  set-of-marks fallback (OSWorld som observation): overlay numbered
    marks on a screenshot for element grounding when DOM/UIA is unavailable.
B2  claims hard gate (browser-use replay-detection analogue): an action
    WITHOUT claims is rejected before execution - fail-closed.
B3  structured action schema (browser-use 31-action analogue): explicit
    enum with per-action validation instead of free-form JSON.

Library part: enforce_claims / validate_action / set_of_marks.
Tests run only via CLI: python p289_borrowed.py   (exit 0 = pass)
"""
import io as _io
import json


def set_of_marks(png_bytes, detections):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.open(_io.BytesIO(png_bytes)).convert("RGB")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 16)
    except Exception:
        font = ImageFont.load_default()
    mark_map = {}
    for i, det in enumerate(detections, 1):
        x, y, w, h = int(det["x"]), int(det["y"]), int(det["w"]), int(det["h"])
        mid = "m%d" % i
        draw.rectangle([x, y, x + w, y + h], outline=(255, 60, 60), width=3)
        draw.rectangle([x, y - 18, x + 26, y], fill=(255, 60, 60))
        draw.text((x + 4, y - 16), str(i), font=font, fill=(255, 255, 255))
        mark_map[mid] = {"bbox": [x, y, w, h], "desc": det.get("desc", "")}
    buf = _io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue(), mark_map


def enforce_claims(action, ref_exists=True):
    if not ref_exists:
        return False, "ELEMENT_UNAVAILABLE"
    claims = action.get("claims") or []
    if not claims:
        return False, "NO_CLAIMS - every action must predict its outcome"
    if action.get("action") == "done":
        return True, "done"
    return True, "ok"


ACTION_SCHEMA = {
    "click":   {"required": ["ref"], "optional": ["click_count"]},
    "fill":    {"required": ["ref", "text"], "optional": []},
    "select":  {"required": ["ref", "value"], "optional": []},
    "check":   {"required": ["ref"], "optional": []},
    "uncheck": {"required": ["ref"], "optional": []},
    "scroll":  {"required": ["direction"], "optional": ["pages"]},
    "go_back": {"required": [], "optional": []},
    "done":    {"required": [], "optional": []},
}


def validate_action(a):
    if not isinstance(a, dict):
        return False, "not a dict"
    k = a.get("action")
    if k not in ACTION_SCHEMA:
        return False, "unknown action %r" % k
    for req_key in ACTION_SCHEMA[k]["required"]:
        if req_key not in a or a[req_key] in ("", None):
            return False, "missing required field %r" % req_key
    return True, "ok"


def run_tests():
    from PIL import Image
    results = []
    buf = _io.BytesIO()
    Image.new("RGB", (400, 300), (20, 24, 28)).save(buf, "PNG")
    _, mmap = set_of_marks(buf.getvalue(), [
        {"x": 50, "y": 40, "w": 120, "h": 30, "desc": "username input"},
        {"x": 50, "y": 90, "w": 120, "h": 30, "desc": "password input"},
        {"x": 50, "y": 140, "w": 80, "h": 32, "desc": "submit button"},
    ])
    results.append(("B1 som", len(mmap) == 3))
    results.append(("B2 claims-present", enforce_claims(
        {"action": "click", "ref": "e3",
         "claims": ["CHECKS PASS"]})[0]))
    results.append(("B2 claims-absent", not enforce_claims(
        {"action": "click", "ref": "e3"})[0]))
    results.append(("B3 click", validate_action(
        {"action": "click", "ref": "e1"})[0]))
    results.append(("B3 fill", validate_action(
        {"action": "fill", "ref": "e1", "text": "x"})[0]))
    results.append(("B3 bad-action rejected", not validate_action(
        {"action": "jump", "ref": "e1"})[0]))
    results.append(("B3 missing-text rejected", not validate_action(
        {"action": "fill", "ref": "e1"})[0]))
    for name, ok in results:
        print("[%s] %s" % ("PASS" if ok else "FAIL", name))
    all_ok = all(ok for _, ok in results)
    print("%s (%d tests)" % ("ALL PASS" if all_ok else "FAILURES", len(results)))
    return all_ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if run_tests() else 1)
