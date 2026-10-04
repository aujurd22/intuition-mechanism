# -*- coding: utf-8 -*-
"""小红书宣传图：拉马努金瞪眼法 · 机制拆解（粉笔黑板风，手绘抖动线条）"""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1440
random.seed(42)

BG = (11, 15, 18)          # 黑板墨黑
CHALK = (235, 235, 225)    # 粉笔白
GOLD = (224, 184, 92)      # 金
GOLD_HI = (250, 214, 130)
RED = (178, 45, 38)        # 印章红
DIM = (120, 128, 122)

FONT_KAI = r"C:\Windows\Fonts\simkai.ttf"
FONT_XK = r"C:\Windows\Fonts\STXINGKA.TTF"
FONT_HEI = r"C:\Windows\Fonts\simhei.ttf"

img = Image.new("RGB", (W, H), BG)
# 底色微渐变（中心稍亮）
grad = Image.new("L", (1, H))
for y in range(H):
    grad.putpixel((0, y), int(26 * (1 - abs(y - H*0.42)/(H*0.58))**2))
img = Image.composite(Image.new("RGB", (W, H), (19, 26, 24)), img, grad.resize((W, H)))

draw = ImageDraw.Draw(img)

# ---------- 粉笔质感辅助 ----------
def jit_line(dr, p1, p2, seg=None, amp=1.6, width=2, fill=CHALK):
    """抖动线段：模拟手绘粉笔"""
    x1, y1 = p1; x2, y2 = p2
    L = math.hypot(x2-x1, y2-y1)
    n = seg or max(2, int(L/28))
    pts = []
    for i in range(n+1):
        t = i/n
        x = x1 + (x2-x1)*t + random.uniform(-amp, amp)
        y = y1 + (y2-y1)*t + random.uniform(-amp, amp)
        pts.append((x, y))
    dr.line(pts, fill=fill, width=width, joint="curve")

def jit_poly(dr, pts, close=False, amp=1.6, width=2, fill=CHALK):
    pp = list(pts)
    if close:
        pp = pp + [pp[0]]
    for a, b in zip(pp[:-1], pp[1:]):
        jit_line(dr, a, b, amp=amp, width=width, fill=fill)

def chalk_text(dr, xy, s, font, fill, anchor="la", amp=0.7):
    """手写感文字：同一文本多层微偏移"""
    x, y = xy
    dr.text((x+amp, y-amp), s, font=font, fill=fill, anchor=anchor)

# ---------- 背景纹理：粉笔灰 + 淡公式 ----------
for _ in range(900):
    x, y = random.uniform(0, W), random.uniform(0, H)
    a = random.randint(4, 26)
    draw.ellipse([int(x), int(y), int(x+random.uniform(0.5, 2)), int(y+random.uniform(0.5, 2))],
                 fill=(210, 214, 205, a))

f_formula = ImageFont.truetype(FONT_KAI, 30)
f_formula_s = ImageFont.truetype(FONT_KAI, 22)
ghost = [(60, 130, "1/π = (√8/9801) Σ …", 38),
         (760, 1168, "1729 = 1³+12³ = 9³+10³", 30),
         (880, 90, "e^(π√163)", 32),
         (60, 700, "d | 1,3,5,7,13,17", 26)]
for x, y, s, size in ghost:
    ft = ImageFont.truetype(FONT_KAI, size)
    timg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tdr = ImageDraw.Draw(timg)
    tdr.text((x, y), s, font=ft, fill=CHALK)
    timg = timg.filter(ImageFilter.GaussianBlur(0.6))
    img = Image.blend(img, Image.alpha_composite(img.convert("RGBA"), timg).convert("RGB"), 0.10)
    img.convert("RGB")
draw = ImageDraw.Draw(img)

# ---------- 拉马努金剪影（右侧，面朝左） ----------
# 剪影外框（比例坐标，框 x0=640 y0=430 w=400 h=560）
x0, y0, w0, h0 = 648, 430, 396, 560
def P(px, py):
    return (x0 + px*w0, y0 + py*h0)

glow = Image.new("RGB", (W, H), (0, 0, 0))
gdr = ImageDraw.Draw(glow)

# 头巾（大圆顶 + 褶皱）
turban = [P(0.02, 0.34), P(0.06, 0.18), P(0.20, 0.06), P(0.42, 0.00), P(0.66, 0.02),
          P(0.84, 0.12), P(0.94, 0.28), P(0.97, 0.40), P(0.90, 0.42), P(0.86, 0.33),
          P(0.72, 0.22), P(0.50, 0.16), P(0.30, 0.20), P(0.16, 0.30), P(0.12, 0.40)]
jit_poly(gdr, turban, close=True, amp=2.2, width=3, fill=GOLD)
# 头巾褶皱
jit_line(gdr, P(0.30, 0.19), P(0.26, 0.33), amp=1.2, width=1, fill=GOLD)
jit_line(gdr, P(0.55, 0.14), P(0.56, 0.30), amp=1.2, width=1, fill=GOLD)
jit_line(gdr, P(0.76, 0.20), P(0.82, 0.34), amp=1.2, width=1, fill=GOLD)
# 头巾下缘（额头带）
jit_line(gdr, P(0.12, 0.40), P(0.30, 0.365), amp=1.2, width=2, fill=GOLD_HI)

# 脸部侧影（面朝左：额→鼻→唇→下巴→颌）
face = [P(0.30, 0.365), P(0.245, 0.40), P(0.215, 0.455), P(0.225, 0.49),   # 额头→眉弓
        P(0.20, 0.52), P(0.135, 0.585), P(0.105, 0.635), P(0.145, 0.655),  # 鼻梁→鼻尖
        P(0.185, 0.665), P(0.175, 0.69), P(0.15, 0.71),                     # 鼻底→人中
        P(0.175, 0.725), P(0.16, 0.75), P(0.185, 0.775),                    # 上唇→口缝
        P(0.165, 0.80), P(0.19, 0.83), P(0.235, 0.875), P(0.30, 0.91),      # 下唇→下巴
        P(0.40, 0.945), P(0.52, 0.975)]                                      # 颌线
jit_poly(gdr, face, amp=1.8, width=3, fill=GOLD)
# 后脑/颈（头巾右侧下来）
back = [P(0.97, 0.40), P(0.99, 0.55), P(0.965, 0.72), P(0.92, 0.86), P(0.86, 0.98)]
jit_poly(gdr, back, amp=1.8, width=3, fill=GOLD)
# 胡须（短须暗示）
jit_line(gdr, P(0.185, 0.80), P(0.30, 0.845), amp=1.0, width=1, fill=GOLD)
jit_line(gdr, P(0.235, 0.865), P(0.36, 0.90), amp=1.0, width=1, fill=GOLD)
# 耳朵
ear = [P(0.60, 0.52), P(0.66, 0.50), P(0.685, 0.56), P(0.64, 0.615), P(0.585, 0.60)]
jit_poly(gdr, ear, amp=1.0, width=2, fill=GOLD)

# 眼睛（瞪眼：微大 + 发光）
eye_c = P(0.315, 0.525)
gdr.ellipse([eye_c[0]-14, eye_c[1]-7, eye_c[0]+14, eye_c[1]+7], outline=GOLD_HI, width=3)
gdr.ellipse([eye_c[0]-5, eye_c[1]-5, eye_c[0]+5, eye_c[1]+5], fill=GOLD_HI)

# 瞳孔光晕
glow_g = glow.filter(ImageFilter.GaussianBlur(3))
img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), 0.0)  # no-op keep
mask = glow.convert("L").point(lambda v: min(255, int(v*0.9)))
gold_layer = Image.new("RGB", (W, H), GOLD)
img = Image.composite(Image.blend(img, gold_layer, 0.35), img, mask.point(lambda v: min(255, int(v*1.4))))
draw = ImageDraw.Draw(img)

# ---------- 瞪眼光束（射向左侧公式区） ----------
beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bdr = ImageDraw.Draw(beam)
bx, by = eye_c
bdr.polygon([(bx-8, by-6), (bx-620, by-250), (bx-620, by+40), (bx-8, by+8)],
            fill=(224, 184, 92, 22))
bdr.polygon([(bx-8, by-4), (bx-620, by-180), (bx-620, by+20), (bx-8, by+6)],
            fill=(224, 184, 92, 18))
bdr.line([(bx-8, by), (bx-620, by-120)], fill=(240, 214, 140, 50), width=2)
beam = beam.filter(ImageFilter.GaussianBlur(2))
img = Image.alpha_composite(img.convert("RGBA"), beam).convert("RGB")
draw = ImageDraw.Draw(img)
# 光束里的魔法数字
f_num = ImageFont.truetype(FONT_HEI, 34)
for (nx, ny, s) in [(240, by-215, "1"), (330, by-190, "3"), (415, by-160, "5"),
                    (250, by-90, "7"), (345, by-55, "13"), (438, by-28, "17")]:
    draw.text((nx, ny), s, font=f_num, fill=GOLD_HI)
    draw.ellipse([nx-8, ny+40, nx+40, ny+46], fill=None)

# ---------- 标题区（左上） ----------
f_title1 = ImageFont.truetype(FONT_XK, 132)
f_title2 = ImageFont.truetype(FONT_XK, 150)
f_sub = ImageFont.truetype(FONT_KAI, 44)
draw.text((66, 96), "拉马努金", font=f_title1, fill=GOLD_HI)
draw.text((70, 236), "瞪眼法", font=f_title2, fill=CHALK)
# 手绘下划线
jit_line(draw, (78, 425), (430, 418), amp=2.5, width=4, fill=GOLD)
draw.text((70, 448), "把直觉拆开给你看", font=f_sub, fill=CHALK)

# 红色印章「已复验」
seal = Image.new("RGBA", (230, 230), (0, 0, 0, 0))
sdr = ImageDraw.Draw(seal)
sdr.rounded_rectangle([8, 8, 222, 222], radius=20, outline=RED, width=9)
f_seal = ImageFont.truetype(FONT_KAI, 72)
grid = [(62, 62, "机"), (168, 62, "制"), (62, 168, "拆"), (168, 168, "解")]
for gx, gy, ch in grid:
    sdr.text((gx, gy), ch, font=f_seal, fill=RED, anchor="mm")
seal = seal.rotate(-7, expand=True, resample=Image.BICUBIC)
img.paste(seal, (548, 128), seal)
draw = ImageDraw.Draw(img)

# ---------- 中部：拆解流程（瞪眼→猜想→考试→修正） ----------
f_flow = ImageFont.truetype(FONT_KAI, 40)
fy = 1010
steps = ["瞪一眼", "猜规律", "代码考试", "错题喂回"]
sx = 66
for i, s in enumerate(steps):
    draw.rounded_rectangle([sx, fy, sx+210, fy+74], radius=10, outline=GOLD, width=3)
    draw.text((sx+105, fy+37), s, font=f_flow, fill=CHALK, anchor="mm")
    if i < 3:
        draw.text((sx+218, fy+30), "→", font=ImageFont.truetype(FONT_HEI, 40), fill=GOLD)
    sx += 258

# ---------- 底部钩子 ----------
f_hook = ImageFont.truetype(FONT_KAI, 42)
hooks = ["他瞪一眼就知道答案",
         "AI 猜了 268 次，全部预注册",
         "AI 自创算法，赢了 50 年老算法"]
hy = 1140
for i, s in enumerate(hooks):
    cx, cy = 88, hy + 26
    draw.polygon([(cx, cy-15), (cx+11, cy), (cx, cy+15), (cx-11, cy)],
                 outline=GOLD, width=3)
    draw.polygon([(cx, cy-5), (cx+4, cy), (cx, cy+5), (cx-4, cy)], fill=GOLD)
    draw.text((126, hy), s, font=f_hook, fill=CHALK)
    hy += 66

# ---------- 内边框（手绘卡片感） ----------
jit_poly(draw, [(26, 26), (W-26, 26), (W-26, H-96), (26, H-96)],
         close=True, amp=1.2, width=1, fill=(200, 205, 196))

# ---------- 脸部颧骨线 ----------
jit_line(draw, P(0.34, 0.60), P(0.50, 0.575), amp=0.8, width=1, fill=(190, 160, 95))

# ---------- 底栏 ----------
draw.rectangle([0, H-72, W, H], fill=(6, 8, 10))
f_bot = ImageFont.truetype(FONT_HEI, 30)
draw.text((W//2, H-36), "github.com/aujurd22/intuition-mechanism", font=f_bot,
          fill=DIM, anchor="mm")

img.save("小红书封面_v1.png")
print("saved 小红书封面_v1.png")
