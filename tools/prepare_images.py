# -*- coding: utf-8 -*-
"""把源图转成站点使用的 assets/<work>/NN.webp。

用法：python tools/prepare_images.py            # 全部作品
      python tools/prepare_images.py xyj        # 只处理指定作品

西游记：根目录 01-xx.webp → assets/characters/NN.webp
山海经：shj/shjcp/01-xx.png → assets/shanhaijing/NN.webp
"""
import os
import re
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)

WORKS = {
    "xyj": {"src": PROJECT, "ext": ".webp", "out": os.path.join(PROJECT, "assets", "characters")},
    "shj": {"src": os.path.join(PROJECT, "shj", "shjcp"), "ext": ".png",
            "out": os.path.join(PROJECT, "assets", "shanhaijing")},
}
TARGET_W = 1600
QUALITY = 82


def export(cfg):
    src, out = cfg["src"], cfg["out"]
    os.makedirs(out, exist_ok=True)
    count = 0
    for name in sorted(os.listdir(src)):
        if not name.lower().endswith(cfg["ext"]):
            continue
        m = re.match(r"^(\d{2})-", name)
        if not m:
            continue
        dst = os.path.join(out, m.group(1) + ".webp")
        with Image.open(os.path.join(src, name)) as im:
            im = im.convert("RGB")
            if im.width > TARGET_W:
                h = round(im.height * TARGET_W / im.width)
                im = im.resize((TARGET_W, h), Image.LANCZOS)
            im.save(dst, "WEBP", quality=QUALITY, method=6)
        count += 1
    total = sum(os.path.getsize(os.path.join(out, f)) for f in os.listdir(out))
    print("%-4s 导出 %d 张 -> %s（%.1f MB）" % (cfg["out"].split(os.sep)[-1], count, out, total / 1048576.0))


def main():
    only = sys.argv[1:] or list(WORKS)
    for k in only:
        if k in WORKS:
            export(WORKS[k])


if __name__ == "__main__":
    sys.exit(main())
