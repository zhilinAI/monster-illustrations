# -*- coding: utf-8 -*-
"""由原文摘录 + 人工分类表生成多作品图志页面。

用法：python tools/build_site.py
输入：data/原文摘录.txt、shj/异兽描述96条.txt、tools/taxonomy*.json、tools/template.html
输出：西游记妖精灵怪图志.html、data/characters.json、data/shanhaijing.json
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
TEMPLATE = os.path.join(HERE, "template.html")
OUT_HTML = os.path.join(PROJECT, "西游记妖精灵怪图志.html")

# ---------------------------------------------------------------- 作品配置

WORKS = [
    {
        "id": "xyj",
        "title": "西游记",
        "author": "明 · 吴承恩（旧题）",
        "seal": "西游记图",
        "src": os.path.join(PROJECT, "data", "原文摘录.txt"),
        "tax": os.path.join(HERE, "taxonomy.json"),
        "img": ("assets/characters", "webp"),
        "json": os.path.join(PROJECT, "data", "characters.json"),
        "cats": [("yao", "妖", "zhu"), ("jing", "精", "cui"),
                 ("gui", "鬼", "hun"), ("guai", "怪", "liu")],
        "blurb": {
            "yao": "占山踞洞、统率妖众的魔头，多以人形示人。",
            "jing": "兽、禽、鱼虫、草木成精，本相可指认者。",
            "gui": "尸骸、骷髅、僵尸一类，原著中仅此一例可归。",
            "guai": "本相难归一类、书中始终以「怪」称之者。",
        },
        "habs": [("hai", "海", "江河水府", "龙宫、潭渊与河底水宅"),
                 ("lu", "陆", "山岭城郭", "山道、城郭与荒野"),
                 ("kong", "空", "云端天际", "天界、飞行与腾云之属"),
                 ("di", "地（穴）", "洞府幽穴", "洞府、穴居与地宫")],
        "intro": "取经路上所遇妖魔精怪的形象谱录，按妖、精、鬼、怪分类，以海、陆、空、地（穴）安置，逐条附回目与原文。",
        "unit": "段原文",
        "note": "「妖 · 精 · 鬼 · 怪」与「海 · 陆 · 空 · 地（穴）」两层分类由编者依原文所载判定，用于检索与编排，并非原著官方分类。原著中可明确归入「鬼」的形象极少，本图志仅收白骨夫人本相一例；「怪」类亦只三例。条目若与本相、居所记载有出入，以原文为准，可在 <span style=\"font-family:var(--mono);font-size:11.5px\">tools/taxonomy.json</span> 中改写后重新生成。",
        "catintro": "四类之分，取原文对本相、称号与居所的写法：",
    },
    {
        "id": "shj",
        "title": "山海经",
        "author": "先秦 · 佚名（旧题）",
        "seal": "山海经图",
        "src": os.path.join(PROJECT, "shj", "异兽描述96条.txt"),
        "tax": os.path.join(HERE, "taxonomy_shj.json"),
        "img": ("assets/shanhaijing", "webp"),
        "json": os.path.join(PROJECT, "data", "shanhaijing.json"),
        "cats": [("shou", "兽", "cui"), ("qin", "禽", "hun"),
                 ("shen", "神", "liu"), ("min", "民", "zhu")],
        "blurb": {
            "shou": "走兽、水族、虫蛇一类，本相仍落在畜兽之间。",
            "qin": "飞禽一类，以鸟形为本相或有翼能飞者。",
            "shen": "神祇与司天、司雨、司雷者，多具人面而兼兽身。",
            "min": "异国异民，形体、居处异于常人者。",
        },
        "habs": [("shan", "山", "山经所载", "山丘、峡谷与崖穴"),
                 ("shui", "水", "河泽海滨", "河泽、海隅与水府"),
                 ("guo", "国", "异国异民", "邦国、部族与聚落"),
                 ("tian", "天", "天界神祇", "天界、司天与乘龙驾云者")],
        "intro": "山海荒服之内的异兽、异禽、神祇与异国异民，按兽、禽、神、民分类，以山、水、国、天安置，逐条附描述与判定依据。",
        "unit": "条描述",
        "note": "《山海经》原书按南、西、北、东、中诸经分卷，并无「兽 · 禽 · 神 · 民」之别；本图志为检索方便，由编者依描述文本判定归类，以山、水、国、天安置，非原著分类。所据描述文本共 96 条，均已收入，其中第 18 条（相柳）、第 25 条（雷神）两幅设定图为按同一版式补绘。条目若与原文记载有出入，以原文为准，可在 <span style=\"font-family:var(--mono);font-size:11.5px\">tools/taxonomy_shj.json</span> 中改写后重新生成。",
        "catintro": "四类之分，取描述文本对本相与居处的写法：",
    },
]

# ---------------------------------------------------------------- 解析

def parse_xyj(path):
    text = open(path, encoding="utf-8").read()
    chapters = [(m.start(), m.group(0).strip()) for m in
                re.finditer(r"第[一二三四五六七八九十百]+回\s+\S+", text)]
    entries = []
    for m in re.finditer(r"〔(\d{2})〕妖怪：(.+?)\n(.*?)(?=\n〔|\n━|\n====+|\Z)", text, re.S):
        num, name, body = m.group(1), m.group(2).strip(), m.group(3)
        chapter = ""
        for pos, title in chapters:
            if pos <= m.start():
                chapter = title
            else:
                break
        chap_short = chapter.split(" ")[0] if chapter else ""
        desc_m = re.search(r"描写内容：(.+?)　?｜　?原文第\s*(\d+)\s*段", body)
        desc = desc_m.group(1).strip() if desc_m else ""
        para = int(desc_m.group(2)) if desc_m else None
        q_m = re.search(r"原文：\n(.*)", body, re.S)
        quote = q_m.group(1) if q_m else ""
        quote = "\n".join(line.strip() for line in quote.splitlines() if line.strip())
        entries.append({
            "id": num, "num": int(num), "name": name, "chapter": chapter,
            "chapterShort": chap_short, "desc": desc, "para": para, "quote": quote,
            "pinyin": "",
        })
    return entries


def parse_shj(path):
    """01. 蠃鱼（luǒ yú） + 描述行 → 记录"""
    text = open(path, encoding="utf-8").read()
    entries, cur = [], None
    for line in text.splitlines():
        m = re.match(r"^(\d{2})\.\s*(.+?)（([^（）]*)）\s*$", line)
        if m:
            if cur:
                entries.append(cur)
            cur = {"id": m.group(1), "num": int(m.group(1)), "name": m.group(2),
                   "pinyin": m.group(3), "desc": ""}
        elif cur is not None and line.strip() and not line.startswith("="):
            cur["desc"] = (cur["desc"] + line.strip()) if cur["desc"] else line.strip()
    if cur:
        entries.append(cur)
    for e in entries:
        e["chapter"] = "《山海经》异兽 · 第 %02d 种" % e["num"]
        e["chapterShort"] = e["pinyin"]
        e["quote"] = ""
        e["para"] = None
    return entries


def split_name(name):
    """白骨精（一变·月貌花容）-> (白骨精, 一变·月貌花容)"""
    m = re.match(r"^(.+?)（(.+)）$", name)
    if m:
        return m.group(1), m.group(2)
    return name, ""


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- 构建

def load_work(w):
    entries = parse_xyj(w["src"]) if w["id"] == "xyj" else parse_shj(w["src"])
    tax = json.load(open(w["tax"], encoding="utf-8"))["items"]
    img_dir, ext = w["img"]
    rows = []
    skipped = []
    for e in entries:
        path = os.path.join(PROJECT, img_dir, e["id"] + "." + ext)
        if not os.path.exists(path):
            skipped.append(e["id"])
            continue
        t = tax.get(e["id"])
        if not t:
            raise SystemExit("%s 分类表缺少条目 %s" % (w["title"], e["id"]))
        e.update(cat=t["cat"], hab=t["hab"], basis=t["basis"], img="%s/%s.%s" % (img_dir, e["id"], ext))
        rows.append(e)
    if skipped:
        print("  跳过无图条目：%s" % ",".join(skipped))
    return rows


def build():
    tpl = open(TEMPLATE, encoding="utf-8").read()
    cards, catviews, galleries = [], [], []
    meta_js = {}
    total = 0

    for w in WORKS:
        rows = load_work(w)
        total += len(rows)
        cats, habs = w["cats"], w["habs"]
        cat_name = dict((c[0], c[1]) for c in cats)
        hab_label = dict((h[0], h[1]) for h in habs)
        cat_color = dict((c[0], c[2]) for c in cats)

        by_cat = dict((c, sum(1 for r in rows if r["cat"] == c)) for c, _, _ in cats)
        by_hab = dict((h, sum(1 for r in rows if r["hab"] == h)) for h, _, _, _ in habs)
        per = dict(((c, h), sum(1 for r in rows if r["cat"] == c and r["hab"] == h))
                   for c, _, _ in cats for h, _, _, _ in habs)

        # ---------- 图卡 ----------
        def card(e):
            main, sub = split_name(e["name"])
            sub_html = '<span class="psub">%s</span>' % esc(sub) if sub else ""
            return (
                '<figure class="plate" data-work="{work}" data-cat="{cat}" data-hab="{hab}"'
                ' data-id="{id}" data-name="{name}" data-chapter="{chap}" style="--cat:var(--{color})">\n'
                '  <a class="plate-fig" href="#/w/{work}/x/{cat}/{id}" aria-label="打开 {name} 的设定与原文">'
                '<img src="{img}" alt="{name} 设定图" width="1600" height="903" loading="lazy" decoding="async">'
                '</a>\n'
                '  <span class="moremark">{num}</span>\n'
                '  <figcaption>\n'
                '    <div class="pname">{main}{subhtml}</div>\n'
                '    <div class="pmeta"><span class="tag tag--cat">{catlabel}</span>'
                '<span class="tag">{hablabel}</span><span>{chap}</span></div>\n'
                '    <p class="pbasis">{basis}</p>\n'
                '  </figcaption>\n'
                '  <div class="plate-data" hidden>\n'
                '    <span data-k="num">第 {num} 幅</span>\n'
                '    <span data-k="chapter">{chapter}</span>\n'
                '    <span data-k="desc">{desc}</span>\n'
                '    <span data-k="quote">{quote}</span>\n'
                '    <span data-k="basis">{basis}</span>\n'
                '  </div>\n'
                '</figure>'
            ).format(
                work=w["id"], cat=e["cat"], hab=e["hab"], id=e["id"], name=esc(e["name"]),
                chap=esc(e["chapterShort"]), color=cat_color[e["cat"]], num="%02d" % e["num"],
                main=esc(main), subhtml=sub_html, catlabel=cat_name[e["cat"]],
                hablabel=hab_label[e["hab"]], basis=esc(e["basis"]), chapter=esc(e["chapter"]),
                desc=esc(e["desc"]), quote=esc(e["quote"]), img=e["img"],
            )

        # ---------- 卷三 生境分栏 ----------
        gal = ['<div class="workgal" data-work="%s">' % w["id"]]
        for key, label, shortname, desc in habs:
            group = [r for r in rows if r["hab"] == key]
            gal.append(
                '<section class="gsec" data-hab="%s">\n'
                '  <div class="gsechead">\n'
                '    <span class="gsecchar">%s</span>\n'
                '    <span class="gsecname">%s</span>\n'
                '    <span class="gseccount">%d 幅</span>\n'
                '    <span class="gsecdesc">%s</span>\n'
                '  </div>\n'
                '  <div class="grid">\n%s\n  </div>\n'
                '</section>' % (key, label[0], shortname, len(group), desc,
                                 "\n".join("    " + card(e) for e in group))
            )
        gal.append("</div>")
        galleries.append("\n".join(gal))

        # ---------- 卷二 分类行 ----------
        def bars(cat):
            mx = max(per[(cat, h)] for h, _, _, _ in habs) or 1
            out = []
            for h, label, _, _ in habs:
                n = per[(cat, h)]
                out.append('      <div class="habrow habrow--cat"><em>%s</em>'
                           '<span class="track"><span class="bar" style="width:%d%%"></span></span>'
                           '<b>%d</b></div>' % (label, round(n / mx * 100), n))
            return "\n".join(out)

        catrows = []
        for cat, label, color in cats:
            catrows.append(
                '<a class="catrow" href="#/w/%s/x/%s" data-cat="%s" style="--cat:var(--%s)">\n'
                '  <span class="catglyph">%s</span>\n'
                '  <div class="catmain"><h2>%s<b>%d 幅</b></h2><p>%s</p></div>\n'
                '  <div class="cathabs">\n%s\n  </div>\n'
                '  <span class="catcta">入图录 <span class="arrow">→</span></span>\n'
                '</a>' % (w["id"], cat, cat, color, label, label, by_cat[cat],
                          esc(w["blurb"][cat]), bars(cat))
            )

        catlabels = "、".join(
            '<span style="color:var(--%s)">%s</span>' % (c[2], c[1]) for c in cats)
        catviews.append(
            '<div class="workview" data-work="%s">\n'
            '  <div class="chead">\n'
            '    <p class="kicker">卷二　分类</p>\n'
            '    <h1>%s<em>%s</em></h1>\n'
            '    <p>%s%s。选一类，即入生境图录。</p>\n'
            '  </div>\n'
            '  <div class="catlist">\n%s\n  </div>\n'
            '  <div class="note"><b>分类口径</b>　%s</div>\n'
            '</div>' % (w["id"], esc(w["title"]),
                        " · ".join(c[1] for c in cats), esc(w["catintro"]), catlabels,
                        "\n".join(catrows), w["note"])
        )

        # ---------- 卷一 作品卡 ----------
        def wbars():
            mx = max(by_hab.values()) or 1
            out = []
            for h, label, _, _ in habs:
                out.append('        <div class="habrow"><em>%s</em>'
                           '<span class="track"><span class="bar" style="width:%d%%"></span></span>'
                           '<b>%s</b></div>' % (label, round(by_hab[h] / mx * 100), by_hab[h]))
            return "\n".join(out)

        seal = "".join("<i>%s</i>" % ch for ch in w["seal"])
        cards.append(
            '<a class="workcard" href="#/w/%s" style="--work:%s">\n'
            '  <span class="seal">%s</span>\n'
            '  <div class="wbody">\n'
            '    <h3>%s<small>%s</small></h3>\n'
            '    <p>%s</p>\n'
            '    <div class="wtags"><span>%d 幅设定</span><span>%d 类</span><span>%d 境</span>'
            '<span>%d %s</span></div>\n'
            '  </div>\n'
            '  <div class="whabs">\n%s\n  </div>\n'
            '  <span class="wcta">进入分类<span class="arrow">→</span></span>\n'
            '</a>\n'
            '<div class="wquick">或 <a href="#/w/%s/x/all">浏览全部 %d 幅，按生境排列</a></div>'
            % (w["id"], "var(--cui)" if w["id"] == "shj" else "var(--zhu)", seal,
               esc(w["title"]), esc(w["author"]), esc(w["intro"]),
               len(rows), len(cats), len(habs), len(rows), w["unit"],
               wbars(), w["id"], len(rows))
        )

        # ---------- JS 元数据 ----------
        meta_js[w["id"]] = {
            "title": w["title"],
            "cats": dict((c[0], {"name": c[1], "color": c[2]}) for c in cats),
            "habs": dict((h[0], {"name": h[1], "short": h[2]}) for h in habs),
            "habOrder": [h[0] for h in habs],
        }

        # ---------- 数据集 ----------
        data = {
            "project": "西游记妖精灵怪图志",
            "work": {"id": w["id"], "title": w["title"], "author": w["author"]},
            "taxonomy": {
                "categories": [{"id": c, "name": n, "count": by_cat[c]} for c, n, _ in cats],
                "habitats": [{"id": h, "name": n, "desc": d, "count": by_hab[h]} for h, n, _, d in habs],
            },
            "items": [{
                "id": r["id"], "num": r["num"], "name": r["name"], "pinyin": r["pinyin"],
                "category": r["cat"], "habitat": r["hab"], "basis": r["basis"],
                "chapter": r["chapter"], "chapterShort": r["chapterShort"],
                "desc": r["desc"], "paragraph": r["para"], "quote": r["quote"],
                "image": r["img"],
            } for r in rows],
        }
        os.makedirs(os.path.dirname(w["json"]), exist_ok=True)
        with open(w["json"], "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print("%s：%d 幅　" % (w["title"], len(rows)) +
              "  ".join("%s %d" % (n, by_cat[c]) for c, n, _ in cats) + "　｜　" +
              "  ".join("%s %d" % (n, by_hab[h]) for h, n, _, _ in habs))

    # ---------- 注入模板 ----------
    out = (tpl.replace("{{WORKCARDS}}", "\n".join(cards))
              .replace("{{CATVIEWS}}", "\n".join(catviews))
              .replace("{{GALLERIES}}", "\n".join(galleries))
              .replace("{{WORKMETA_JS}}", json.dumps(meta_js, ensure_ascii=False, indent=2))
              .replace("{{TOPMETA}}", "%d 幅 · %d 部 · 8 类" % (total, len(WORKS)))
              .replace("{{N_ITEMS}}", str(total))
              .replace("{{N_WORKS}}", str(len(WORKS)))
              .replace("{{N_CATS}}", "8")
              .replace("{{N_HABS}}", "8"))
    for token in ("{{WORKCARDS}}", "{{CATVIEWS}}", "{{GALLERIES}}", "{{WORKMETA_JS}}"):
        if token in out:
            raise SystemExit("模板占位未替换：%s" % token)
    open(OUT_HTML, "w", encoding="utf-8", newline="\n").write(out)
    print("生成 %s（%.0f KB），合计 %d 幅" %
          (os.path.basename(OUT_HTML), os.path.getsize(OUT_HTML) / 1024.0, total))


if __name__ == "__main__":
    sys.exit(build())
