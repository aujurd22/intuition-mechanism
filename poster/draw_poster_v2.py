# -*- coding: utf-8 -*-
"""小红书封面 · 金墨博物馆风 v2：真实肖像金色双色调 + 高级排版"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H = 1080, 1440
random.seed(7)
np.random.seed(7)

INK = (7, 9, 13)            # 底色近黑
GOLD_L = (248, 226, 176)    # 亮金
GOLD = (222, 186, 110)      # 金
GOLD_D = (150, 116, 58)     # 暗金
CHALK = (238, 236, 226)
DIM = (128, 134, 130)
RED = (176, 44, 38)

FONT_XK = r"C:\Windows\Fonts\STXINGKA.TTF"
FONT_KAI = r"C:\Windows\Fonts\simkai.ttf"
FONT_HEI = r"C:\Windows\Fonts\simhei.ttf"

# ---------- 1. 底：近黑 + 暗角 + 细噪点 ----------
yy, xx = np.mgrid[0:H, 0:W].astype(float)
cx, cy = W*0.68, H*0.38   # 暗角中心偏向肖像
r2 = ((xx-cx)/(W*0.85))**2 + ((yy-cy)/(H*0.85))**2
vig = np.clip(1 - 0.55*r2, 0, 1)
base = np.zeros((H, W, 3))
for c in range(3):
    base[..., c] = INK[c] * (0.75 + 0.25*vig)
noise = np.random.normal(0, 3.2, (H, W, 1))
base = np.clip(base + noise, 0, 255).astype(np.uint8)
img = Image.fromarray(base)

# ---------- 2. 肖像：裁剪 → 灰度 → 金色双色调 → 左缘渐隐 ----------
photo = Image.open("rama_wiki.jpg").convert("L")
photo = ImageOps.autocontrast(photo, cutoff=1)
pw, ph = photo.size
# 裁剪：脸部+上身（脸在照片中部偏上）
crop = photo.crop((int(pw*0.16), 0, pw, int(ph*0.99)))
cw, ch = crop.size
target_h = H
target_w = int(cw * target_h / ch)
crop = crop.resize((target_w, target_h), Image.LANCZOS)

# 金色双色调：暗部→墨黑，中间→暗金，亮部→暖金白
lo = np.array([8, 10, 16]); mid = np.array([168, 128, 62]); hi = np.array([246, 224, 178])
g = np.asarray(crop).astype(float) / 255.0
duo = np.zeros((*g.shape, 3))
m_lo = g < 0.55
t = g[m_lo] / 0.55
duo[m_lo] = lo + (mid - lo) * t[:, None]
m_hi = ~m_lo
t2 = (g[m_hi] - 0.55) / 0.45
duo[m_hi] = mid + (hi - mid) * t2[:, None]
duo = np.clip(duo + np.random.normal(0, 2.5, duo.shape), 0, 255).astype(np.uint8)
duo_img = Image.fromarray(duo)

# 左缘 + 顶部 + 底部 渐隐蒙版
px_w = duo_img.size[0]
mask = np.full((target_h, px_w), 255, dtype=float)
fade_x = int(px_w * 0.42)
ramp = np.linspace(0, 1, fade_x) ** 1.5
mask[:, :fade_x] *= ramp[None, :]
mask[:60, :] *= np.linspace(0, 1, 60)[:, None]
mask[-140:, :] *= np.linspace(1, 0, 140)[:, None] ** 1.2
mask_img = Image.fromarray(mask.astype(np.uint8))

pos_x = W - px_w   # 右对齐
# 头后金色微光晕
halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
hd = ImageDraw.Draw(halo)
hx, hy, hr = pos_x + int(px_w*0.52), int(H*0.30), int(H*0.34)
hd.ellipse([hx-hr, hy-int(hr*1.1), hx+hr, hy+int(hr*0.9)], fill=(120, 92, 38, 70))
halo = halo.filter(ImageFilter.GaussianBlur(90))
img = Image.alpha_composite(img.convert("RGBA"), halo).convert("RGB")
img.paste(duo_img, (pos_x, 0), mask_img)

# ---------- 3. 金色渐变字辅助 ----------
def gold_gradient_text(img, xy, s, font, anchor="la", light=GOLD_L, dark=GOLD_D):
    timg = Image.new("L", img.size, 0)
    td = ImageDraw.Draw(timg)
    td.text(xy, s, font=font, fill=255, anchor=anchor)
    bbox = timg.getbbox()
    if not bbox:
        return
    x0, y0, x1, y1 = bbox
    grad = Image.new("RGB", img.size, dark)
    gd = ImageDraw.Draw(grad)
    for i, y in enumerate(range(y0, y1)):
        tt = (y - y0) / max(1, y1 - y0)
        c = tuple(int(light[k] + (dark[k] - light[k]) * tt) for k in range(3))
        gd.line([(x0, y), (x1, y)], fill=c)
    img.paste(grad, (0, 0), timg)

draw = ImageDraw.Draw(img)

# ---------- 4. 排版（左列） ----------
# kicker（加字距）
kick = "预 注 册 · 268 个 实 验 · 机 器 可 复 验"
f_kick = ImageFont.truetype(FONT_HEI, 26)
draw.text((74, 96), kick, font=f_kick, fill=GOLD)

# 大标题（金色渐变）
gold_gradient_text(img, (66, 150), "拉马努金", ImageFont.truetype(FONT_XK, 138))
gold_gradient_text(img, (60, 318), "瞪眼法", ImageFont.truetype(FONT_XK, 176))
# 细金线 + 副标
draw.line([(72, 540), (470, 536)], fill=GOLD_D, width=2)
f_sub = ImageFont.truetype(FONT_KAI, 46)
draw.text((70, 562), "把直觉拆开给你看", font=f_sub, fill=CHALK)
f_en = ImageFont.truetype(FONT_HEI, 20)
draw.text((72, 632), "M E C H A N I S M   O F   I N T U I T I O N", font=f_en, fill=(150, 120, 66))

# 红印「机制拆解」
seal = Image.new("RGBA", (216, 216), (0, 0, 0, 0))
sdr = ImageDraw.Draw(seal)
sdr.rounded_rectangle([8, 8, 208, 208], radius=18, outline=RED, width=8)
f_seal = ImageFont.truetype(FONT_KAI, 68)
for gx, gy, ch in [(60, 60, "机"), (158, 60, "制"), (60, 158, "拆"), (158, 158, "解")]:
    sdr.text((gx, gy), ch, font=f_seal, fill=RED, anchor="mm")
seal = seal.rotate(-7, expand=True, resample=Image.BICUBIC)
img.paste(seal, (330, 700), seal)

# ---------- 5. 六数星座（中下，连线+光点） ----------
nodes = [(118, 812, "1"), (208, 868, "3"), (300, 826, "5"),
         (168, 948, "7"), (262, 992, "13"), (368, 940, "17")]
f_n = ImageFont.truetype(FONT_HEI, 30)
pts = [(x, y) for x, y, _ in nodes]
for i in range(len(pts) - 1):
    draw.line([pts[i], pts[i+1]], fill=(150, 116, 58), width=1)
for x, y, s in nodes:
    halo_n = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(halo_n)
    nd.ellipse([x-13, y-13, x+13, y+13], fill=(140, 108, 44, 110))
    halo_n = halo_n.filter(ImageFilter.GaussianBlur(6))
    base_rgba = img.convert("RGBA")
    img = Image.alpha_composite(base_rgba, halo_n).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.ellipse([x-7, y-7, x+7, y+7], outline=GOLD, width=2)
    draw.text((x+16, y-16), s, font=f_n, fill=GOLD_L)

# 微光公式（背景星尘）
f_g = ImageFont.truetype(FONT_KAI, 24)
for x, y, s in [(600, 700, "1/π"), (560, 900, "1729"), (96, 1105, "e^(π√163) ≈ 整数")]:
    draw.text((x, y), s, font=f_g, fill=(96, 82, 52))

# ---------- 6. 底部钩子 ----------
f_hook = ImageFont.truetype(FONT_KAI, 42)
hooks = ["他瞪一眼，就知道答案",
         "AI 猜了 268 次 · 全程预注册",
         "AI 自创算法，赢了 50 年经典"]
hy = 1170
for s in hooks:
    cx, cy = 92, hy + 27
    draw.polygon([(cx, cy-13), (cx+10, cy), (cx, cy+13), (cx-10, cy)],
                 outline=GOLD, width=3)
    draw.text((132, hy), s, font=f_hook, fill=CHALK)
    hy += 72

# ---------- 7. 边框 + 底栏 ----------
draw.rectangle([16, 16, W-17, H-17], outline=(120, 94, 46), width=2)
draw.rectangle([24, 24, W-25, H-25], outline=(70, 56, 30), width=1)
draw.rectangle([0, H-64, W, H], fill=(5, 6, 9))
f_bot = ImageFont.truetype(FONT_HEI, 28)
draw.text((W//2, H-32), "github.com/aujurd22/intuition-mechanism", font=f_bot,
          fill=(120, 128, 130), anchor="mm")

# ---------- 8. 细噪点收尾 ----------
arr = np.asarray(img).astype(np.int16)
arr = np.clip(arr + np.random.normal(0, 2.0, arr.shape), 0, 255).astype(np.uint8)
img = Image.fromarray(arr)

img.save("小红书封面_金墨版.png")
print("saved 小红书封面_金墨版.png")
