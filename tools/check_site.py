# -*- coding: utf-8 -*-
"""生成结果的静态校验：条目数、分类计数、图片存在、原文段落是否夹带下一回。

用法：python tools/check_site.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
PAGE = os.path.join(PROJECT, "index.html")
DATASETS = [os.path.join(PROJECT, "data", "characters.json"),
            os.path.join(PROJECT, "data", "shanhaijing.json"),
            os.path.join(PROJECT, "data", "liaozhai.json"),
            os.path.join(PROJECT, "data", "zibuyu.json"),
            os.path.join(PROJECT, "data", "sanjiao.json"),
            os.path.join(PROJECT, "data", "liezi.json"),
            os.path.join(PROJECT, "data", "shuyiji.json"),
            os.path.join(PROJECT, "data", "tpg.json"),
            os.path.join(PROJECT, "data", "ssj.json"),
            os.path.join(PROJECT, "data", "yw.json"),
            os.path.join(PROJECT, "data", "fs.json")]

problems = []
page = open(PAGE, encoding="utf-8").read()
total = 0

for path in DATASETS:
    data = json.load(open(path, encoding="utf-8"))
    items = data["items"]
    work = data["work"]["id"]
    total += len(items)

    ids = [it["id"] for it in items]
    if len(set(ids)) != len(ids):
        problems.append("%s id 重复" % work)

    # 《西游记》《聊斋志异》每条都应有原文；山海经无原文，跳过
    if work in ("xyj", "lz", "zby", "sjs", "lzl", "syj", "tpg", "ssj", "yw", "fs"):
        bad = [it["id"] for it in items if not re.search(r"[^\s]", it["quote"] or "")]
        if bad:
            problems.append("原文为空：%s" % ",".join(bad))
        leak = [it["id"] for it in items
                if "━" in it["quote"] or re.search(r"第[一二三四五六七八九十]+回", it["quote"])]
        if leak:
            problems.append("原文夹带章节头：%s" % ",".join(leak))
    else:
        empty = [it["id"] for it in items if len(it["desc"] or "") < 8]
        if empty:
            problems.append("%s 描述过短：%s" % (work, ",".join(empty)))

    # 子不语：卷次篇名须由摘抄标题解析出来，按语不可为空
    if work == "zby":
        bad = [it["id"] for it in items
               if not re.match(r"《子不语》卷[一二三四五六七八九十]+ · .+", it["chapter"])
               or not re.match(r"卷[一二三四五六七八九十]+$", it["chapterShort"])
               or len(it["desc"] or "") < 4]
        if bad:
            problems.append("子不语卷次/篇名/按语异常：%s" % ",".join(bad))
        dup = len(items) - len({it["name"] for it in items})
        if dup:
            problems.append("子不语名目重复 %d 条" % dup)
        if len(items) != 47:
            problems.append("子不语条目 %d 条，应为 47" % len(items))

    # 三教搜神大全：卷次须落在七卷内，名号不可重复，条数固定 150
    if work == "sjs":
        bad = [it["id"] for it in items
               if not re.match(r"《三教搜神大全》卷[一二三四五六七] · 第 \d+ 位", it["chapter"])
               or not re.match(r"卷[一二三四五六七]$", it["chapterShort"])
               or len(it["desc"] or "") < 12]
        if bad:
            problems.append("三教卷次/名号异常：%s" % ",".join(bad))
        dup = len(items) - len({it["name"] for it in items})
        if dup:
            problems.append("三教名号重复 %d 条" % dup)
        if len(items) != 150:
            problems.append("三教条目 %d 条，应为 150" % len(items))

    # 列子：篇次须落在黄帝、周穆王、汤问三篇内，名目不可重复，条数固定 14
    if work == "lzl":
        bad = [it["id"] for it in items
               if not re.match(r"《列子》[^·]+篇（[一二三四五六七八九十]+）", it["chapter"])
               or not re.match(r".+篇$", it["chapterShort"])
               or len(it["desc"] or "") < 8]
        if bad:
            problems.append("列子篇次/按语异常：%s" % ",".join(bad))
        dup = len(items) - len({it["name"] for it in items})
        if dup:
            problems.append("列子名目重复 %d 条" % dup)
        if len(items) != 14:
            problems.append("列子条目 %d 条，应为 14" % len(items))
        pian = {it["chapterShort"] for it in items}
        if pian != {"黄帝篇", "周穆王篇", "汤问篇"}:
            problems.append("列子篇次取值异常：%s" % "、".join(sorted(pian)))

    # 述异记：卷次只分上下，名目不可重复，条数固定 57
    if work == "syj":
        bad = [it["id"] for it in items
               if not re.match(r"《述异记》卷[上下] · 第 \d+ 则", it["chapter"])
               or not re.match(r"卷[上下]$", it["chapterShort"])
               or len(it["desc"] or "") < 8]
        if bad:
            problems.append("述异记卷次/按语异常：%s" % ",".join(bad))
        dup = len(items) - len({it["name"] for it in items})
        if dup:
            problems.append("述异记名目重复 %d 条" % dup)
        if len(items) != 57:
            problems.append("述异记条目 %d 条，应为 57" % len(items))
        for juan in ("卷上", "卷下"):
            n = sum(1 for it in items if it["chapterShort"] == juan)
            if n != {"卷上": 36, "卷下": 21}[juan]:
                problems.append("述异记%s 共 %d 条，应为 %d" % (juan, n, {"卷上": 36, "卷下": 21}[juan]))

    # 太平广记：出处书目解析，名目不可重复，条数固定 74，部类分布固定
    if work == "tpg":
        bad = [it["id"] for it in items
               if not re.match(r"《太平广记》·.+部", it["chapter"])
               or len(it["chapterShort"] or "") < 2
               or len(it["desc"] or "") < 2]
        if bad:
            problems.append("太平广记章节/按语异常：%s" % ",".join(bad))
        dup = len(items) - len({it["name"] for it in items})
        if dup:
            problems.append("太平广记名目重复 %d 条" % dup)
        if len(items) != 74:
            problems.append("太平广记条目 %d 条，应为 74" % len(items))
        for bu, n in (("妖怪部", 25), ("精怪部", 24), ("夜叉部", 8), ("狐部", 11), ("鬼部", 6)):
            c = sum(1 for it in items if bu in it["chapter"])
            if c != n:
                problems.append("太平广记%s 共 %d 条，应为 %d" % (bu, c, n))
        for hab, n in (("shan", 1), ("shui", 3), ("ye", 24), ("zhai", 32), ("tian", 0), ("di", 12), ("xue", 2)):
            c = sum(1 for it in items if it["habitat"] == hab)
            if c != n:
                problems.append("太平广记生境%s 共 %d 条，应为 %d" % (hab, c, n))

    # 搜神记：六类七境分布、名目不重、条数固定 83
    if work == "ssj":
        bad = [it["id"] for it in items
               if not re.match(r"《搜神记》·.+", it["chapter"])
               or len(it["chapterShort"] or "") < 2
               or len(it["desc"] or "") < 2]
        if bad:
            problems.append("搜神记章节/小标题异常：%s" % ",".join(bad))
        dup = len(items) - len({it["name"] for it in items})
        if dup:
            problems.append("搜神记名目重复 %d 条" % dup)
        if len(items) != 83:
            problems.append("搜神记条目 %d 条，应为 83" % len(items))
        for cat, n in (("hu", 9), ("gui", 13), ("shou", 17), ("lin", 9), ("jing", 27), ("hua", 8)):
            c = sum(1 for it in items if it["category"] == cat)
            if c != n:
                problems.append("搜神记%s 共 %d 条，应为 %d" % (cat, c, n))
        for hab, n in (("zhai", 35), ("ye", 18), ("shui", 9), ("shan", 9), ("shu", 6), ("di", 3), ("tian", 3)):
            c = sum(1 for it in items if it["habitat"] == hab)
            if c != n:
                problems.append("搜神记生境%s 共 %d 条，应为 %d" % (hab, c, n))

    # 阅微草堂笔记：六类五境分布、名目不重、条数固定 54
    if work == "yw":
        bad = [it["id"] for it in items
               if not re.match(r"《阅微草堂笔记》·.+", it["chapter"])
               or len(it["chapterShort"] or "") < 2
               or len(it["desc"] or "") < 2
               or len(it["quote"] or "") < 2]
        if bad:
            problems.append("阅微章节/纪评/引文异常：%s" % ",".join(bad))
        dup = len(items) - len({it["name"] for it in items})
        if dup:
            problems.append("阅微名目重复 %d 条" % dup)
        if len(items) != 54:
            problems.append("阅微条目 %d 条，应为 54" % len(items))
        for cat, n in (("gui", 26), ("hu", 7), ("wu", 12), ("jing", 4), ("long", 3), ("shen", 2)):
            c = sum(1 for it in items if it["category"] == cat)
            if c != n:
                problems.append("阅微%s 共 %d 条，应为 %d" % (cat, c, n))
        for hab, n in (("zhai", 29), ("ye", 16), ("shan", 6), ("shu", 2), ("tian", 1)):
            c = sum(1 for it in items if it["habitat"] == hab)
            if c != n:
                problems.append("阅微生境%s 共 %d 条，应为 %d" % (hab, c, n))

    # 封神演义：回次解析、名目不重、条数固定 47，四类五境分布固定
    if work == "fs":
        bad = [it["id"] for it in items
               if not re.match(r"第[0-9一二三四五六七八九十百]+回$", it["chapterShort"])
               or len(it["chapter"] or "") < 2
               or len(it["desc"] or "") < 2
               or len(it["quote"] or "") < 2]
        if bad:
            problems.append("封神回次/编者评/引文异常：%s" % ",".join(bad))
        dup = len(items) - len({it["name"] for it in items})
        if dup:
            problems.append("封神名目重复 %d 条" % dup)
        if len(items) != 47:
            problems.append("封神条目 %d 条，应为 47" % len(items))
        for cat, n in (("yao", 22), ("jing", 8), ("shen", 6), ("yi", 11)):
            c = sum(1 for it in items if it["category"] == cat)
            if c != n:
                problems.append("封神%s 共 %d 条，应为 %d" % (cat, c, n))
        for hab, n in (("tian", 14), ("shan", 18), ("ye", 9), ("zhai", 5), ("shui", 1)):
            c = sum(1 for it in items if it["habitat"] == hab)
            if c != n:
                problems.append("封神生境%s 共 %d 条，应为 %d" % (hab, c, n))

    # 聊斋：篇名须从摘抄标题解析出来，画面小标题不可为空
    if work == "lz":
        bad = [it["id"] for it in items
               if not re.match(r"《.+》", it["chapter"]) or len(it["desc"] or "") < 3]
        if bad:
            problems.append("聊斋篇名/小标题异常：%s" % ",".join(bad))

    for it in items:
        p = os.path.join(PROJECT, it["image"].replace("/", os.sep))
        if not os.path.exists(p):
            problems.append("缺图：%s" % it["image"])
            continue
        if os.path.getsize(p) < 20000:
            problems.append("图片过小：%s" % it["image"])

    for c in data["taxonomy"]["categories"]:
        n = sum(1 for it in items if it["category"] == c["id"])
        if n != c["count"]:
            problems.append("%s 分类计数不符：%s %d != %d" % (work, c["id"], n, c["count"]))
    for h in data["taxonomy"]["habitats"]:
        n = sum(1 for it in items if it["habitat"] == h["id"])
        if n != h["count"]:
            problems.append("%s 生境计数不符：%s %d != %d" % (work, h["id"], n, h["count"]))

    if 'data-work="%s"' % work not in page:
        problems.append("页面缺少作品块：%s" % work)
    for it in items:
        if 'src="%s"' % it["image"] not in page:
            problems.append("页面缺少图片引用：%s" % it["image"])

    card_attrs = re.findall(
        r'<figure class="plate" data-work="%s" data-cat="(\w+)" data-hab="(\w+)" data-id="(\d{2,3})"' % work, page)
    if len(card_attrs) != len(items):
        problems.append("%s 图卡 %d 张，应为 %d" % (work, len(card_attrs), len(items)))
    for cat, hab, cid in card_attrs:
        it = next((x for x in items if x["id"] == cid), None)
        if it and (cat, hab) != (it["category"], it["habitat"]):
            problems.append("%s 图卡 %s 类/境与数据集不一致" % (work, cid))

if "{{" in page:
    problems.append("页面残留模板占位")
cards = page.count('class="plate"')
if cards != total:
    problems.append("页面图卡 %d 张，应为 %d" % (cards, total))
imgs = page.count('src="assets/')
if imgs != total + 1:  # +1 为首页焦点图
    problems.append("页面 img 标签 %d，应为 %d" % (imgs, total + 1))

if problems:
    print("校验未通过：")
    for p in problems:
        print(" - " + p)
    sys.exit(1)
print("校验通过：%d 幅（%d 部）、各作品分类计数一致、%d 处图片引用均在位、页面无模板残留"
      % (total, len(DATASETS), total + 1))
