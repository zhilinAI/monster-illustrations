# -*- coding: utf-8 -*-
"""按 data/xyj150_table.tsv 的编者定稿，抽取各条名目的回目与原文段。

用法：python tools/build_roster150.py
产出：data/xyj_roster150_raw.json（含 cat/hab/basis/chapter/chapterShort/quote）
"""
import json
import os
import re
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FULL = r"E:\西游记-00\西游记-原著(1).txt"
A001 = r"E:\西游记-00\建模\A001【西游精怪妖图志】.txt"
NAMES = os.path.join(PROJECT, "data", "xyj150_names.txt")
TSV = os.path.join(PROJECT, "data", "xyj150_table.tsv")
OUT = os.path.join(PROJECT, "data", "xyj_roster150_raw.json")
TABLE = os.path.join(PROJECT, "data", "xyj_roster150_table.txt")

ALIAS = {
    "白骨精": ["白骨夫人", "白骨精", "白骨"],
    "白鹿精": ["白鹿精", "白鹿"],
    "百花羞公主": ["百花羞"],
    "宝象国国王": ["宝象国国王", "宝象国王"],
    "豹子精": ["南山大王", "艾叶花皮豹子精", "豹子精"],
    "比丘国国王": ["比丘国王", "比丘昏主"],
    "陈光蕊": ["陈光蕊", "光蕊"],
    "崔判官": ["崔判官", "崔珏"],
    "东海龙王": ["东海龙王", "敖广"],
    "观音菩萨": ["观音菩萨", "观音尊者", "菩萨"],
    "黑水河神": ["黑水河神"],
    "黑熊精": ["黑熊精", "黑熊", "熊罴", "黑汉"],
    "虎力大仙": ["虎力大仙", "虎力"],
    "黄风怪": ["黄风怪", "黄风大王"],
    "黄眉怪": ["黄眉怪", "黄眉大王", "黄眉"],
    "黄狮精": ["黄狮精", "黄狮"],
    "金角大王": ["金角大王", "金角"],
    "迦叶": ["伽叶", "迦叶"],
    "金圣娘娘": ["金圣娘娘", "金圣宫"],
    "劲节十八公": ["十八公"],
    "九头虫": ["九头虫", "九头怪", "九头驸马"],
    "寇员外": ["寇员外", "寇洪", "员外"],
    "奎木狼": ["奎木狼", "黄袍怪"],
    "老鼋": ["老鼋", "白鼋"],
    "刘伯钦": ["刘伯钦", "伯钦"],
    "鹿力大仙": ["鹿力大仙", "鹿力"],
    "昴日星官": ["昴日星官"],
    "摩昂太子": ["摩昂"],
    "木叉": ["木叉", "惠岸"],
    "牛头马面": ["牛头", "马面"],
    "女儿国国王": ["女儿国国王", "女王"],
    "毗蓝婆菩萨": ["毗蓝婆"],
    "辟尘大王": ["辟尘"],
    "辟寒大王": ["辟寒"],
    "辟暑大王": ["辟暑"],
    "普贤菩萨": ["普贤"],
    "青牛精": ["独角兕大王", "兕大王", "青牛", "老怪"],
    "如来佛祖": ["如来"],
    "三位小王子": ["小王子", "三位王子"],
    "四老猴": ["四老猴", "四猴"],
    "太白金星": ["太白金星", "金星"],
    "太上老君": ["太上老君", "老君"],
    "太阴星君": ["太阴星君", "太阴"],
    "唐太宗": ["唐太宗", "太宗"],
    "天竺国王": ["天竺国王", "天竺国主"],
    "通背猿猴": ["通背猿猴", "通臂猿猴"],
    "鼍龙怪": ["鼍龙"],
    "万圣龙王": ["万圣龙王", "万圣老龙", "万圣"],
    "尉迟恭": ["尉迟恭"],
    "魏徵": ["魏徵", "魏征"],
    "文殊菩萨": ["文殊"],
    "乌鸡国王": ["乌鸡国王"],
    "蜈蚣精": ["蜈蚣精", "百眼魔君", "蜈蚣"],
    "西海龙王": ["西海龙王", "敖闰"],
    "蝎子精": ["蝎子精", "蝎子"],
    "须菩提祖师": ["须菩提祖师", "菩提祖师", "祖师"],
    "徐茂公": ["徐茂公"],
    "许旌阳真人": ["许旌阳"],
    "羊力大仙": ["羊力大仙", "羊力"],
    "殷温娇": ["殷温娇", "温娇"],
    "银角大王": ["银角大王", "银角"],
    "玉帝": ["玉帝", "玉皇大帝", "玉皇"],
    "玉面公主": ["玉面公主", "玉面狐狸"],
    "玉兔精": ["玉兔"],
    "镇元大仙": ["镇元大仙", "镇元子", "大仙"],
    "蜘蛛精": ["蜘蛛精", "蜘蛛"],
    "七狮精": ["七狮", "狻猊狮"],
    "黑白无常": ["勾死人", "无常"],
    "降龙罗汉": ["罗汉"],
    "龙王夫人": ["万圣龙王", "龙王"],
    "千里眼": ["千里眼"],
    "太子": ["太子"],
    "太师": ["太师"],
    "刺史": ["刺史"],
    "苍头": ["苍头"],
}

DESC_KW = ("貌", "身", "穿", "戴", "执", "面", "头", "眼", "眉", "口", "牙", "手",
           "袍", "甲", "冠", "衣", "裙", "髻", "靴", "须", "发", "坐", "骑", "驾",
           "威", "凛", "堂堂", "庄严", "祥云", "瑞气", "神通", "打扮", "形容", "模样")
WEAPON_KW = ("棒", "钯", "杖", "枪", "刀", "剑", "叉", "杵", "锤", "斧", "鞭", "弓",
             "索", "扇", "瓶", "葫芦", "铃", "戟", "锏", "钺", "轮", "珠", "镜")


def load_chapters(text):
    pat = re.compile(r"第([一二三四五六七八九十百]+)回\s+(\S+)")
    return [(m.start(), "第%s回" % m.group(1), "第%s回 %s" % (m.group(1), m.group(2)),
            m.group(2)) for m in pat.finditer(text)]


def paragraphs(text, marks):
    out = []
    for i, (pos, short, full, title) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        body = text[pos:end]
        body = body.split("\n", 1)[1] if "\n" in body else ""
        for j, p in enumerate(re.split(r"\n{2,}", body)):
            p = re.sub(r"\s*\n\s*", "\n", p).strip()
            if len(p) >= 12:
                out.append({"short": short, "chapter": full, "title": title,
                            "idx": j, "text": p})
    return out


def is_verse(t):
    lines = [l.strip() for l in t.split("\n") if l.strip()]
    return len(lines) >= 3 and sum(1 for l in lines if 4 <= len(l) <= 12) >= len(lines) - 1


def score(p, al):
    t = p["text"]
    s = min(14, sum(1.6 for kw in DESC_KW if kw in t))
    if is_verse(t):
        s += 7
    if any(w in t for w in WEAPON_KW):
        s += 2
    if "道：" in t:
        s -= 5
    if len(t) > 320:
        s -= 3
    for a in al:
        i = t.find(a)
        if i > 0 and t[:i].count("“") > t[:i].count("”"):
            s -= 6
    return s


def clip(t, limit=210):
    t = t.strip()
    if len(t) <= limit:
        return t
    cut = t[:limit]
    for mark in ("。", "！", "；", "”"):
        m = cut.rfind(mark)
        if m > 70:
            return cut[:m + 1]
    return cut


def load_a001():
    text = open(A001, encoding="utf-8").read()
    chapters = [(m.start(), m.group(0).strip()) for m in
                re.finditer(r"第[一二三四五六七八九十百]+回\s+\S+", text)]
    out = {}
    for m in re.finditer(r"〔\d{2}〕妖怪：(.+?)\n(.*?)(?=\n〔|\n━|\Z)", text, re.S):
        name, body = m.group(1).strip(), m.group(2)
        chap = ""
        for pos, t in chapters:
            if pos <= m.start():
                chap = t
        q = re.search(r"原文：\n(.*)", body, re.S)
        quote = "\n".join(l.strip() for l in (q.group(1) if q else "").splitlines() if l.strip())
        target = A001_MAP.get(name)
        if target and target not in out:
            out[target] = {"chapter": chap, "chapterShort": chap.split(" ")[0],
                           "quote": quote, "from": "A001"}
    return out


A001_MAP = {
    "混世魔王": "混世魔王",
    "黑熊精（黑风山黑风王）": "黑熊精",
    "虎先锋": "虎先锋",
    "黄风怪": "黄风怪",
    "白骨精（一变·月貌花容）": "白骨精",
    "黄袍怪（奎木狼）": "奎木狼",
    "银角大王": "银角大王",
    "金角大王": "金角大王",
    "玉面狐狸": "玉面公主",
    "九头虫": "九头虫",
    "杏仙": "杏仙",
    "黄眉大王": "黄眉怪",
    "赛太岁（金毛犼）": "赛太岁",
    "蜘蛛精": "蜘蛛精",
    "南山大王（豹子精）": "豹子精",
    "独角兕大王": "青牛精",
    "玉兔精（本相）": "玉兔精",
}


ANCHOR = {
    "苍头": "提著一把秤",
    "七狮精": "杂毛狮子",
    "降龙罗汉": "降龙、伏虎",
    "龙王夫人": "万圣",
    "黑白无常": "套上绳",
    "牛头马面": "摆牛头",
    "八大金刚": "八大金刚",
    "白鹿精": "国丈",
    "宝象国国王": "宝象国王",
    "百花羞公主": "三公主",
    "拂云叟": "拂云叟",
    "孤直公": "孤直公",
    "凌空子": "凌空子",
    "劲节十八公": "十八公",
    "观音菩萨": "落伽",
    "黑水河神": "河神",
    "虎力大仙": "虎力大仙",
    "金圣娘娘": "金圣宫",
    "泾河龙王": "泾河龙王",
    "精细鬼": "精细鬼",
    "伶俐虫": "伶俐虫",
    "迦叶": "人事",
    "金池长老": "金池",
    "寇员外": "寇员外",
    "大力鬼王": "大力鬼王",
    "昴日星官": "昴日星官",
    "明月": "明月",
    "辟寒大王": "辟寒",
    "辟尘大王": "辟尘",
    "辟暑大王": "辟暑",
    "普贤菩萨": "普贤",
    "文殊菩萨": "文殊",
    "千里眼": "千里眼",
    "秦叔宝": "秦叔宝",
    "魏徵": "魏徵",
    "如来佛祖": "如来",
    "水德星君": "水德星君",
    "通背猿猴": "通背猿猴",
    "赤尻马猴": "赤尻马猴",
    "太师": "太师",
    "太阴星君": "太阴星君",
    "天竺国王": "天竺国王",
    "万圣龙王": "万圣",
    "王母": "王母",
    "乌巢禅师": "乌巢",
    "乌鸡国王": "乌鸡国王",
    "蜈蚣精": "百眼魔君",
    "武曲星君": "武曲星君",
    "蝎子精": "蝎子精",
    "小钻风": "小钻风",
    "许旌阳真人": "许旌阳",
    "雪狮精": "雪狮",
    "羊力大仙": "羊力",
    "玉帝": "玉帝",
    "玉华王": "玉华王",
    "赵寡妇": "赵寡妇",
    "李天王": "李天王",
}

SKIP = {"裴虚己"}


def main():
    text = open(FULL, encoding="utf-8", errors="replace").read()
    marks = load_chapters(text)
    paras = paragraphs(text, marks)
    a001 = load_a001()
    names = [l.strip() for l in open(NAMES, encoding="utf-8") if l.strip()]
    table = {}
    for line in open(TSV, encoding="utf-8"):
        if not line.strip():
            continue
        name, chap, cat, hab, basis = line.rstrip("\n").split("\t")
        table[name] = {"chap": chap, "cat": cat, "hab": hab, "basis": basis}
    rows, miss, weak, bad_anchor = [], [], [], []
    num = 60
    for name in names:
        t = table.get(name)
        if name in SKIP or not t:
            miss.append(name)
            continue
        num += 1
        al = ALIAS.get(name, [name])
        anchor = ANCHOR.get(name)
        pool = [p for p in paras if p["short"] == t["chap"]]
        cands = [p for p in pool if any(a in p["text"] for a in al)]
        if anchor:
            hit = [p for p in pool if anchor in p["text"]]
            if hit:
                cands = hit
            else:
                bad_anchor.append(name)
        best = None
        # A001 摘抄里的形貌段优先（编者已校订，且逐字可回检）
        if name in a001 and a001[name]["quote"] and name not in ANCHOR:
            a = a001[name]
            best = {"chapter": a["chapter"], "chapterShort": a["chapterShort"],
                    "chapterTitle": a["chapter"].split(" ")[-1], "text": a["quote"],
                    "src": "A001"}
        if best is None and cands:
            best = max(cands, key=lambda p: score(p, al))
            best["src"] = "原著"
        elif best is None and name in a001 and a001[name]["quote"]:
            a = a001[name]
            best = {"chapter": a["chapter"], "chapterShort": a["chapterShort"],
                    "chapterTitle": a["chapter"].split(" ")[-1], "text": a["quote"],
                    "src": "A001"}
        if best is None:
            cands = [p for p in paras if any(a in p["text"] for a in al)]
            if not cands:
                miss.append(name)
                continue
            weak.append(name)
            best = max(cands, key=lambda p: score(p, al))
            best["src"] = "原著"
        rows.append({"id": "%03d" % num, "num": num, "name": name,
                     "chapter": best["chapter"],
                     "chapterShort": best.get("chapterShort") or best["short"],
                     "chapterTitle": best.get("chapterTitle") or best.get("title", ""),
                     "quote": clip(best["text"]), "src": best["src"],
                     "cat": t["cat"], "hab": t["hab"], "basis": t["basis"],
                     "verse": is_verse(best["text"])})
    json.dump(rows, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log = ["%-3s %-8s %-9s %s %s %s %s | %s" % (r["id"], r["name"], r["chapterShort"],
                                                r["cat"], r["hab"], r["src"],
                                                "韵" if r["verse"] else "散",
                                                r["quote"].replace("\n", "/")[:70]) for r in rows]
    open(TABLE, "w", encoding="utf-8").write(
        "\n".join(log) + "\n\n缺表：%s\n错回：%s\n落空锚点：%s\n"
        % ("、".join(miss), "、".join(weak), "、".join(bad_anchor)))
    print("\n".join(log[:8]))
    print("共 %d 条 | 缺表 %d：%s | 回次无命中 %d：%s | 落空锚点 %d：%s"
          % (len(rows), len(miss), "、".join(miss), len(weak), "、".join(weak),
             len(bad_anchor), "、".join(bad_anchor)))


if __name__ == "__main__":
    sys.exit(main())
