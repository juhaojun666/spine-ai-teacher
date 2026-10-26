# -*- coding: utf-8 -*-
"""生成『方块小哥』练习素材：一套可直接导入 Spine 的分层 PNG 图片。

设计原则（学 Spine 很重要）：
  每个部件都是一张独立的透明 PNG，尺寸紧贴内容；
  肢体部件的“轴心”在图片的顶部中点/肩部，这样绑到骨骼上时关节就在骨点，
  不需要在 Spine 里反复调偏移。

运行： python make_parts.py
输出： ../01-方块小哥/parts/ 以及一张组装预览图
"""
from PIL import Image, ImageDraw
import os

SS = 4  # 超采样倍数，用大图绘制再缩小，边缘更平滑
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "01-方块小哥", "parts"))
PREVIEW = os.path.abspath(os.path.join(HERE, "..", "01-方块小哥", "组装效果预览.png"))

SKIN    = (243, 198, 160, 255)
SKIN_HI = (250, 216, 186, 255)
SHIRT   = (74, 124, 240, 255)
SHIRT_HI= (108, 152, 250, 255)
PANTS   = (51, 64, 92, 255)
PANTS_HI= (72, 88, 120, 255)
SHOE    = (59, 46, 46, 255)
LINE    = (30, 42, 56, 255)

os.makedirs(OUT, exist_ok=True)


def rr(d, box, radius, fill, outline=LINE, width=3):
    """在放大坐标系下画圆角矩形。"""
    x0, y0, x1, y1 = [v * SS for v in box]
    d.rounded_rectangle([x0, y0, x1 - 1, y1 - 1], radius=radius * SS,
                        fill=fill, outline=outline, width=int(width * SS))


def part(name, w, h, radius, fill, hi=None, outline_w=3):
    """画一个部件并保存。高清绘制 -> 缩小 -> 输出。"""
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rr(d, (0, 0, w, h), radius, fill, width=outline_w)
    if hi is not None:
        # 顶部一条浅色高光，让方块看起来有体积
        pad = max(3, int(w * 0.10))
        rr(d, (pad, pad, w - pad, int(h * 0.40)), max(2, radius * 0.55),
           hi, outline=(0, 0, 0, 0), width=0)
    img = img.resize((w, h), Image.LANCZOS)
    img.save(os.path.join(OUT, name))
    return img


def face(name, blink=False):
    """头部：同尺寸的睁眼 / 闭眼两张，方便以后讲『附件切换 = 眨眼』。"""
    w = h = 96
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rr(d, (0, 0, w, h), 24, SKIN, width=3)
    rr(d, (9, 8, w - 9, 40), 14, SKIN_HI, outline=(0, 0, 0, 0), width=0)

    if blink:
        # 闭眼：两条小弧线
        for cx in (34, 62):
            d.line([(cx - 7) * SS, 56 * SS, (cx + 7) * SS, 56 * SS],
                   fill=LINE, width=3 * SS)
            d.arc([(cx - 7) * SS, (50) * SS, (cx + 7) * SS, (58) * SS],
                  200, 340, fill=LINE, width=2 * SS)
    else:
        # 睁眼：两个深色小方块 + 高光点
        for cx in (34, 62):
            rr(d, (cx - 6, 45, cx + 6, 64), 5, LINE, outline=LINE, width=1)
            rr(d, (cx - 3, 48, cx - 1, 51), 1, (255, 255, 255, 255),
               outline=(0, 0, 0, 0), width=0)

    # 腮红
    for cx in (20, 76):
        rr(d, (cx - 7, 66, cx + 7, 74), 4, (240, 160, 150, 160),
           outline=(0, 0, 0, 0), width=0)
    # 嘴巴
    d.arc([40 * SS, 64 * SS, 56 * SS, 76 * SS], 20, 160, fill=LINE, width=2 * SS)

    img = img.resize((w, h), Image.LANCZOS)
    img.save(os.path.join(OUT, name))
    return img


imgs = {}
imgs["head"] = face("head.png", blink=False)
imgs["head_blink"] = face("head_blink.png", blink=True)
imgs["torso"] = part("torso.png", 88, 130, 18, SHIRT, SHIRT_HI)
imgs["upper_arm"] = part("upper_arm.png", 26, 74, 12, SHIRT, SHIRT_HI)
imgs["lower_arm"] = part("lower_arm.png", 24, 70, 11, SKIN, SKIN_HI)
imgs["hand"] = part("hand.png", 28, 28, 13, SKIN)
imgs["upper_leg"] = part("upper_leg.png", 30, 86, 13, PANTS, PANTS_HI)
imgs["lower_leg"] = part("lower_leg.png", 26, 80, 12, PANTS, PANTS_HI)
imgs["foot"] = part("foot.png", 44, 22, 9, SHOE)
imgs["sword"] = part("sword.png", 18, 104, 4, (200, 210, 225, 255), (235, 242, 250, 255))

# ---- 组装预览图（只是给你看效果，Spine 里不需要这张图）----
canvas = Image.new("RGBA", (800, 760), (250, 248, 244, 255))
pos = {
    "upper_arm": [(336, 316), (438, 316)],
    "lower_arm": [(339, 388), (437, 388)],
    "hand":      [(337, 456), (435, 456)],
    "upper_leg": [(368, 424), (402, 424)],
    "lower_leg": [(370, 506), (404, 506)],
    "foot":      [(356, 584), (400, 584)],
    "torso":     [(356, 300)],
    "head":      [(352, 212)],
}
# 先画四肢（在身体后面），再画身体和头
for key in ["upper_arm", "lower_arm", "hand", "upper_leg", "lower_leg", "foot", "torso", "head"]:
    for p in pos[key]:
        canvas.alpha_composite(imgs[key], p)
canvas.save(PREVIEW)

print("已生成：", OUT)
print("预览：", PREVIEW)
for f in sorted(os.listdir(OUT)):
    print("  -", f)