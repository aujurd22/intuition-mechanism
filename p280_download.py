# -*- coding: utf-8 -*-
"""P280 step 1: download the three frozen 2006 pairs (view1/view5 @ Illum2/Exp1,
disp1, dmin) into out/p280/data/<scene>/.

Only the frozen scene list is downloaded; nothing is looked at beyond HTTP status.

Run:  python p280_download.py
"""
import json
import os
import sys
import urllib.request

BASE = "https://vision.middlebury.edu/stereo/data/scenes2006/FullSize"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "p280", "data")
SCENES = ["Baby2", "Cloth1", "Cloth2"]      # frozen in p280_preregistration.json
FILES = [("view1.png", "Illum2/Exp1/view1.png"),
         ("view5.png", "Illum2/Exp1/view5.png"),
         ("disp1.png", "disp1.png"),
         ("dmin.txt", "dmin.txt")]


def main():
    for scene in SCENES:
        d = os.path.join(OUT, scene)
        os.makedirs(d, exist_ok=True)
        for name, rel in FILES:
            dst = os.path.join(d, name)
            if os.path.exists(dst) and os.path.getsize(dst) > 0:
                print(f"skip {scene}/{name}")
                continue
            url = f"{BASE}/{scene}/{rel}"
            with urllib.request.urlopen(url, timeout=120) as r, open(dst, "wb") as f:
                f.write(r.read())
            print(f"got  {scene}/{name} ({os.path.getsize(dst)} bytes)")
    print(json.dumps({"scenes": SCENES, "root": OUT}, ensure_ascii=False))


if __name__ == "__main__":
    main()
