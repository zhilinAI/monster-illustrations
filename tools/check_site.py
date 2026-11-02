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
PAGE = os.path.join(PROJECT, "西游记妖精灵怪图志.html")
DATASETS = [os.path.join(PROJECT, "data", "characters.json"),
            os.path.join(PROJECT, "data", "shanhaijing.json")]

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

    # 《西游记》每条都应有原文；山海经无原文，跳过
    if work == "xyj":
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
        r'<figure class="plate" data-work="%s" data-cat="(\w+)" data-hab="(\w+)" data-id="(\d{2})"' % work, page)
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
imgs = page.count('<img src="assets/')
if imgs != total + 1:  # +1 为首页焦点图
    problems.append("页面 img 标签 %d，应为 %d" % (imgs, total + 1))

if problems:
    print("校验未通过：")
    for p in problems:
        print(" - " + p)
    sys.exit(1)
print("校验通过：%d 幅（2 部）、两类分类计数一致、%d 处图片引用均在位、页面无模板残留"
      % (total, total + 1))
