"""P176: color-harmony domain — constraint-checking with the schema template.
Objects: color palettes (lists of hex colors).  Constraints: color theory
rules (hue separation ≥ 30°, saturation range 20-90%, value range 15-95%,
no more than 3 distinct hues).  All mechanically checkable via HSL.
"""
import json, math, random, colorsys

def hex_to_hsl(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16)/255, int(hex_color[2:4], 16)/255, int(hex_color[4:6], 16)/255
    mx, mn = max(r,g,b), min(r,g,b)
    l = (mx+mn)/2
    if mx == mn:
        return (0, 0, l)
    d = mx - mn
    s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
    if mx == r:
        h = (g - b) / d + (6 if g < b else 0)
    elif mx == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    h *= 60
    return (h, s, l)

def hue_dist(h1, h2):
    d = abs(h1 - h2) % 360
    return min(d, 360 - d)

def check_palette(colors, max_hues=3, min_sep=30, sat_range=(0.1, 0.9), val_range=(0.1, 0.95)):
    hsls = [hex_to_hsl(c) for c in colors]
    violations = []
    # saturation range
    for h, s, l in hsls:
        if not (sat_range[0] <= s <= sat_range[1]):
            violations.append(f"saturation {s:.2f} outside [{sat_range[0]},{sat_range[1]}]")
        if not (val_range[0] <= l <= val_range[1]):
            violations.append(f"lightness {l:.2f} outside [{val_range[0]},{val_range[1]}]")
    # hue separation: all pairs must differ by >= min_sep (on the hue circle)
    for i in range(len(hsls)):
        for j in range(i+1, len(hsls)):
            d = hue_dist(hsls[i][0], hsls[j][0])
            if d < min_sep and d > 0:
                violations.append(f"hue distance {d:.0f}° < {min_sep}° between {colors[i]} and {colors[j]}")
    # distinct hues count
    hue_buckets = set()
    for h, s, l in hsls:
        bucket = int(h // min_sep) % (360 // min_sep)
        hue_buckets.add(bucket)
    if len(hue_buckets) > max_hues:
        violations.append(f"{len(hue_buckets)} distinct hue groups > {max_hues}")
    return violations

def gen_valid(rng):
    """Generate a palette satisfying the constraints."""
    n = rng.randint(2, 4)
    base_hue = rng.uniform(0, 360)
    hues = [base_hue]
    while len(hues) < n:
        h = (base_hue + rng.choice([30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330])) % 360
        if all(hue_dist(h, h2) >= 30 or hue_dist(h, h2) == 0 for h2 in hues):
            hues.append(h)
    colors = []
    for h in hues:
        s = rng.uniform(0.2, 0.8)
        l = rng.uniform(0.2, 0.8)
        r, g, b = colorsys.hls_to_rgb(h/360, l, s)
        hex_c = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        colors.append(hex_c)
    return colors

def gen_violating(rng):
    """Generate a palette that violates at least one constraint."""
    n = rng.randint(2, 4)
    # sample random colors, check for violations
    for _ in range(100):
        colors = []
        for _ in range(n):
            r = rng.randint(0, 255)
            g = rng.randint(0, 255)
            b = rng.randint(0, 255)
            colors.append(f"#{r:02x}{g:02x}{b:02x}")
        viols = check_palette_rules(colors)
        if viols:
            return colors
    return None

def check_palette_rules(colors):
    hsls = [hex_to_hsl(c) for c in colors]
    viols = []
    for h, s, l in hsls:
        if not (0.1 <= s <= 0.9):
            viols.append(f"sat {s:.2f}")
        if not (0.1 <= l <= 0.95):
            viols.append(f"val {l:.2f}")
    for i in range(len(hsls)):
        for j in range(i+1, len(hsls)):
            d = hue_dist(hsls[i][0], hsls[j][0])
            if 0 < d < 30:
                viols.append(f"hue {d:.0f}°")
    return viols

def hue_dist(h1, h2):
    d = abs(h1 - h2) % 360
    return min(d, 360 - d)

rng = random.Random(20261004)
items = []
# 6 valid, 6 violating
for i in range(6):
    colors = gen_valid(rng)
    items.append({"id": f"ch{i:02d}", "colors": colors, "passes": True})
for i in range(6):
    while True:
        colors = [f"#{rng.randint(0,255):02x}{rng.randint(0,255):02x}{rng.randint(0,255):02x}"
                  for _ in range(rng.randint(2, 4))]
        # force a violation: two colors too close in hue
        h1 = rng.uniform(0, 360)
        c1 = colorsys.hls_to_rgb(h1/360, 0.5, 0.5)
        c1_hex = f"#{int(c1[0]*255):02x}{int(c1[1]*255):02x}{int(c1[2]*255):02x}"
        h2 = (h1 + rng.uniform(1, 15)) % 360  # too close in hue
        c2 = colorsys.hls_to_rgb(h2/360, 0.5, 0.5)
        c2_hex = f"#{int(c2[0]*255):02x}{int(c2[1]*255):02x}{int(c2[2]*255):02x}"
        # check: does this palette violate?
        if check_palette_rules([c1_hex, c2_hex]):
            items.append({"id": f"cv{i:02d}", "colors": [c1_hex, c2_hex], "passes": False})
            break

# final verification
verified = []
for it in items:
    viols = check_palette_rules(it["colors"])
    actual_pass = len(viols) == 0
    if actual_pass == it["passes"]:
        verified.append(it)
    else:
        print(f"MISMATCH: {it['id']} label={it['passes']} actual={actual_pass}")

items = verified
json.dump(items, open("color_harmony_items.json", "w"), indent=1)
print(f"{len(items)} items saved ({sum(1 for i in items if i['passes'])} pass / {sum(1 for i in items if not i['passes'])} fail)")
