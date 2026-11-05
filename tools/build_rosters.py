# -*- coding: utf-8 -*-
"""为《列子》《述异记》两套新素材生成本站所需的名录与分类表。

输入：列子\\_extract.md、述异记\\_extract.md（【篇/卷·篇名】名目（类别）＋原文＋评）
      列子\\出品\\NN-名目.png、述异记\\出品\\NN-名目.png
输出：列子\\_roster.json、述异记\\_roster.json
      tools\\taxonomy_lzl.json、tools\\taxonomy_syj.json

归并原则：原编类别照列为 label（保留在数据里），站点 4 类由编者合并，见 CATS。
生境同样逐条判定；basis 取原文首句（必为 quote 子串，可回检）。
用法：python -X utf8 tools\\build_rosters.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)

HEAD = re.compile(r"^【(.+?)·(.+?)】(.*)$")
TAIL = re.compile(r"^(.+?)（(.+?)）\s*$")


def read_extract(path, work):
    """→ [{juan,pian,name,label,quote,comment}, …]"""
    items, cur = [], None
    for line in open(path, encoding="utf-8").read().splitlines():
        line = line.strip()
        m = HEAD.match(line)
        if m:
            rest = m.group(3).strip()
            if rest.startswith("（") and rest.endswith("）"):
                name, label = m.group(2), rest[1:-1]
            else:
                t = TAIL.match(rest)
                if not t:
                    raise SystemExit("%s：标题无法解析：%s" % (work, line))
                name, label = t.group(1), t.group(2)
            cur = {"juan": m.group(1).strip(), "pian": m.group(2).strip(),
                   "name": name.strip(), "label": label.strip(),
                   "quote": "", "comment": ""}
            items.append(cur)
            continue
        if cur is None or not line:
            continue
        if line.startswith("评："):
            cur["comment"] = line[2:].strip()
        elif not cur["comment"]:
            cur["quote"] += line
    return items


def basis_of(label, quote):
    """类别：原文首句（≤26 字，取到第一个停顿），必须是 quote 子串。"""
    seg = re.split(r"[，。；：]", quote)[0].strip()
    if len(seg) > 26:
        seg = seg[:26]
    return "%s：%s" % (label, seg)


def numbered(imgdir, work):
    """出品/NN-名目.png → {名目: 编号}；重号、重名即报错。"""
    out, seen = {}, {}
    for f in sorted(os.listdir(imgdir)):
        m = re.match(r"^(\d{2})-(.+)\.png$", f)
        if not m:
            continue
        num, name = int(m.group(1)), m.group(2)
        if num in seen:
            raise SystemExit("%s：编号重复 %d（%s / %s）" % (work, num, seen[num], name))
        if name in out:
            raise SystemExit("%s：图名重复 %s" % (work, name))
        seen[num] = name
        out[name] = num
    return out


def build(work, md, imgdir, cats, habs, expect, juan_expect, tax_out):
    items = read_extract(os.path.join(PROJECT, work, md), work)
    if len(items) != expect:
        raise SystemExit("%s：摘抄条目 %d 条，应为 %d" % (work, len(items), expect))
    num_of = numbered(os.path.join(PROJECT, work, imgdir), work)
    if len(num_of) != expect:
        raise SystemExit("%s：出品图 %d 张，应为 %d" % (work, len(num_of), expect))

    seen_juan = {}
    for e in items:
        seen_juan[e["juan"]] = seen_juan.get(e["juan"], 0) + 1
    if seen_juan != juan_expect:
        raise SystemExit("%s：卷/篇分布 %s，应为 %s" % (work, seen_juan, juan_expect))

    names = [e["name"] for e in items]
    if len(set(names)) != len(names):
        raise SystemExit("%s：名目重复" % work)

    def num_for(name):
        """摘抄名目可带括注别名（鬼母（鬼姑神）），出品文件名只取正名。"""
        if name in num_of:
            return num_of[name]
        base = re.sub(r"（.+?）$", "", name)
        if base in num_of:
            return num_of[base]
        raise SystemExit("%s：出品缺图 %s" % (work, name))

    extra = [n for n in num_of
             if n not in {re.sub(r"（.+?）$", "", x) for x in names}]
    if extra:
        raise SystemExit("%s：图无对应条目 %s" % (work, "、".join(extra)))
    uncat = [n for n in names if n not in cats]
    if uncat:
        raise SystemExit("%s：未归类 %s" % (work, "、".join(uncat)))
    unhab = [n for n in names if n not in habs]
    if unhab:
        raise SystemExit("%s：未定生境 %s" % (work, "、".join(unhab)))

    rows, tax = [], {}
    for e in items:
        n = num_for(e["name"])
        if not e["quote"] or not e["comment"]:
            raise SystemExit("%s：%s 缺原文或评语" % (work, e["name"]))
        basis = basis_of(e["label"], e["quote"])
        if basis.split("：", 1)[1] not in e["quote"]:
            raise SystemExit("%s：%s 依据非原文子串" % (work, e["name"]))
        rows.append({"id": "%02d" % n, "num": n, "juan": e["juan"], "pian": e["pian"],
                     "name": e["name"], "label": e["label"],
                     "quote": e["quote"], "comment": e["comment"],
                     "cat": cats[e["name"]], "hab": habs[e["name"]], "basis": basis})
        tax["%02d" % n] = {"cat": cats[e["name"]], "hab": habs[e["name"]], "basis": basis}

    rows.sort(key=lambda r: r["num"])
    with open(os.path.join(PROJECT, work, "_roster.json"), "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=1)
    with open(tax_out, "w", encoding="utf-8") as fh:
        json.dump({"items": tax}, fh, ensure_ascii=False, indent=1)

    print("%s：%d 条 → %s\\_roster.json、%s" % (work, len(rows), work,
                                              os.path.basename(tax_out)))
    for k in sorted({r["cat"] for r in rows}):
        print("   %s %d" % (k, sum(1 for r in rows if r["cat"] == k)))
    for k in sorted({r["hab"] for r in rows}):
        print("   境 %s %d" % (k, sum(1 for r in rows if r["hab"] == k)))


# ---------------------------------------------------------------- 列子
LZL_CATS = {
    # 神异：神人、异人、鬼物、操蛇之神——形在神而近人者
    "姑射神人": "shen", "上古四圣王": "shen", "化人": "shen",
    "石壁中人": "shen", "操蛇之神": "shen",
    # 巨兽：巨鳌、鲲、鹏与五山禽兽——以尺寸定形者
    "五山禽兽": "ju", "巨鳌": "ju", "鲲": "ju", "鹏": "ju",
    # 大小人：龙伯国之巨人，僬侥、诤人之小人
    "龙伯国大人": "ren", "僬侥国人": "ren", "诤人": "ren",
    # 微巧：焦螟之微、偃师之机巧
    "焦螟": "wei", "偃师倡者": "wei",
}
LZL_HABS = {
    "姑射神人": "shan", "石壁中人": "shan", "五山禽兽": "shan", "操蛇之神": "shan",
    "上古四圣王": "tian", "化人": "tian", "鹏": "tian",
    "巨鳌": "shui", "鲲": "shui", "焦螟": "shui",
    "龙伯国大人": "ye", "僬侥国人": "ye", "诤人": "ye",
    "偃师倡者": "zhai",
}

# ---------------------------------------------------------------- 述异记
SYJ_CATS = {
    # 神祇：古神、仙者、远方异人、卵生之人
    "盘古氏": "shen", "鬼母（鬼姑神）": "shen", "防风氏": "shen",
    "蚩尤": "shen", "蚩尤神": "shen", "驱石神人": "shen",
    "山神俞儿": "shen", "金鱼神": "shen", "哀牢龙": "shen",
    "驾鹤仙者": "shen", "鹄国人": "shen", "徐君卵": "shen",
    # 精魅：物老成精，已具人形或器形者
    "泉先（鲛人）": "jing", "梓树精青羊": "jing", "黄衣人": "jing",
    "白水素女": "jing", "青衣童子": "jing", "枝上小儿": "jing",
    "青牛": "jing", "木鹤": "jing", "藻兼": "jing", "三老人": "jing",
    "鹿娘": "jing", "赤鲤": "jing", "山精": "jing", "青鸟童子": "jing",
    "五色石女": "jing", "鲛人": "jing",
    # 化形：一身两状，由物而人、由人而物
    "黄能": "hua", "精卫": "hua", "蛟妾": "hua", "懒妇鱼": "hua",
    "水虺化龙": "hua", "玄鹿": "hua", "封使君": "hua", "横公鱼": "hua",
    "猿化老人": "hua", "化蛾宫人": "hua",
    # 物怪：兽、禽、虫、蛇与征兆之异
    "獍": "guai", "猰㺄": "guai", "风生兽": "guai", "怒毛兽": "guai",
    "獬豸": "guai", "蛟羊": "guai", "牛鱼": "guai", "格": "guai",
    "吐绶乌": "guai", "金翅黑鸟": "guai", "胡髯燕": "guai",
    "鳛鳛鱼": "guai", "木客鸟": "guai", "白蝙蝠": "guai",
    "肥遗": "guai", "蝹": "guai", "鳞角蚕": "guai",
    "龟毛兔角": "guai", "雨鱼": "guai",
}
SYJ_HABS = {
    "盘古氏": "tian", "驾鹤仙者": "tian", "雨鱼": "tian",
    "鬼母（鬼姑神）": "shan", "防风氏": "shan", "玄鹿": "shan",
    "梓树精青羊": "shan", "封使君": "shan", "吐绶乌": "shan",
    "金翅黑鸟": "shan", "山神俞儿": "shan", "青衣童子": "shan",
    "怒毛兽": "shan", "青牛": "shan", "猿化老人": "shan",
    "木鹤": "shan", "肥遗": "shan", "鹿娘": "shan",
    "木客鸟": "shan", "山精": "shan", "白蝙蝠": "shan",
    "黄能": "shui", "泉先（鲛人）": "shui", "精卫": "shui",
    "懒妇鱼": "shui", "水虺化龙": "shui", "黄衣人": "shui",
    "风生兽": "shui", "驱石神人": "shui", "白水素女": "shui",
    "横公鱼": "shui", "金鱼神": "shui", "牛鱼": "shui",
    "赤鲤": "zhai", "鳛鳛鱼": "shui", "哀牢龙": "shui", "鲛人": "shui",
    "蚩尤": "ye", "獍": "ye", "鹄国人": "ye", "猰㺄": "ye",
    "鳞角蚕": "ye", "枝上小儿": "ye", "獬豸": "ye", "蛟羊": "ye",
    "龟毛兔角": "ye", "蝹": "ye", "格": "ye", "三老人": "ye",
    "青鸟童子": "ye",
    "蚩尤神": "zhai", "蛟妾": "zhai", "胡髯燕": "zhai",
    "化蛾宫人": "zhai", "藻兼": "zhai", "徐君卵": "zhai",
    "五色石女": "zhai",
}


def main():
    build("列子", "_extract.md", "出品", LZL_CATS, LZL_HABS,
          expect=14, juan_expect={"黄帝": 3, "周穆王": 1, "汤问": 10},
          tax_out=os.path.join(HERE, "taxonomy_lzl.json"))
    build("述异记", "_extract.md", "出品", SYJ_CATS, SYJ_HABS,
          expect=57, juan_expect={"卷上": 36, "卷下": 21},
          tax_out=os.path.join(HERE, "taxonomy_syj.json"))


if __name__ == "__main__":
    main()
