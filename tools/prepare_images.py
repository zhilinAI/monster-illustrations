# -*- coding: utf-8 -*-
"""把源图转成站点使用的 assets/<work>/NN.webp。

用法：python tools/prepare_images.py            # 全部作品
      python tools/prepare_images.py xyj        # 只处理指定作品

西游记：根目录 01-xx.webp → assets/characters/NN.webp
山海经：shj/shjcp/01-xx.png → assets/shanhaijing/NN.webp
聊斋志异：liaozai/聊斋图志/01-xx.jpg → assets/liaozhai/NN.webp
子不语：子不语/出品/01-xx.png → assets/zibuyu/NN.webp
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
    "lz": {"src": os.path.join(PROJECT, "liaozai", "聊斋图志"), "ext": ".jpg",
           "out": os.path.join(PROJECT, "assets", "liaozhai")},
    "zby": {"src": os.path.join(PROJECT, "子不语", "出品"), "ext": ".png",
            "out": os.path.join(PROJECT, "assets", "zibuyu")},
    "sjs": {"src": os.path.join(PROJECT, "三教搜神大全", "出品-四视图"), "ext": ".png",
            "out": os.path.join(PROJECT, "assets", "sanjiao")},
    "lzl": {"src": os.path.join(PROJECT, "列子", "出品"), "ext": ".png",
            "out": os.path.join(PROJECT, "assets", "liezi")},
    "syj": {"src": os.path.join(PROJECT, "述异记", "出品"), "ext": ".png",
            "out": os.path.join(PROJECT, "assets", "shuyiji")},
    "tpg": {"src": os.path.join(PROJECT, "太平广记", "出品"), "ext": ".webp",
            "out": os.path.join(PROJECT, "assets", "tpgj")},
    "ssj": {"src": os.path.join(PROJECT, "搜神记", "搜神记图志-皮克斯3D风格"), "ext": ".png",
            "out": os.path.join(PROJECT, "assets", "ssj"), "pad": 2 / 3},
    "yw": {"src": os.path.join(PROJECT, "阅微草堂笔记", "阅微草堂笔记-图"), "ext": ".png",
           "out": os.path.join(PROJECT, "assets", "yw"),
           "roster": os.path.join(PROJECT, "阅微草堂笔记", "_roster.json")},
    "fs": {"src": os.path.join(PROJECT, "封神", "输出"), "ext": ".png",
           "out": os.path.join(PROJECT, "assets", "fs"),
           "roster": os.path.join(PROJECT, "封神", "_roster.json")},
}
TARGET_W = 1600
QUALITY = 82
PAD_COLOR = (13, 17, 16)  # 与图卡底色相近的深色衬边（#0D1110）


def export(cfg):
    src, out = cfg["src"], cfg["out"]
    os.makedirs(out, exist_ok=True)
    count = 0
    name2id = {}
    if "roster" in cfg and os.path.exists(cfg["roster"]):
        import json as _json
        for e in _json.load(open(cfg["roster"], encoding="utf-8")):
            name2id[e.get("src", e["name"])] = e["id"]
    for name in sorted(os.listdir(src)):
        if not name.lower().endswith(cfg["ext"]):
            continue
        m = re.match(r"^(\d{2,3})-", name)
        if m:
            out_id = m.group(1)
        elif name2id:
            base = os.path.splitext(name)[0]
            if base in name2id:
                out_id = name2id[base]
            else:
                continue
        else:
            continue
        dst = os.path.join(out, out_id + ".webp")
        with Image.open(os.path.join(src, name)) as im:
            im = im.convert("RGB")
            if "pad" in cfg:
                target = cfg["pad"]
                cur = im.width / im.height
                if cur < target:
                    nh = round(im.width / target)
                    canvas = Image.new("RGB", (im.width, nh), PAD_COLOR)
                    canvas.paste(im, (0, (nh - im.height) // 2))
                    im = canvas
                elif cur > target:
                    nw = round(im.height * target)
                    canvas = Image.new("RGB", (nw, im.height), PAD_COLOR)
                    canvas.paste(im, ((nw - im.width) // 2, 0))
                    im = canvas
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
