# -*- coding: utf-8 -*-
"""由原文摘录 + 人工分类表生成多作品图志页面。

用法：python tools/build_site.py
输入：data/原文摘录.txt、shj/异兽描述96条.txt、liaozai/liaozai_entries.json、tools/taxonomy*.json、tools/template.html
输出：index.html、data/characters.json、data/shanhaijing.json、data/liaozhai.json
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
TEMPLATE = os.path.join(HERE, "template.html")
OUT_HTML = os.path.join(PROJECT, "index.html")

# ---------------------------------------------------------------- 作品配置

WORKS = [
    {
        "id": "xyj",
        "title": "西游记",
        "author": "明 · 吴承恩（旧题）",
        "seal": "西游记图",
        "color": "zhu",
        "alias": "西游 西游释厄传 西游证道书",
        "src": os.path.join(PROJECT, "data", "原文摘录.txt"),
        "roster": os.path.join(PROJECT, "data", "xyj_roster150.json"),
        "tax": os.path.join(HERE, "taxonomy.json"),
        "img": ("assets/characters", "webp"),
        "json": os.path.join(PROJECT, "data", "characters.json"),
        "cats": [("yao", "妖", "zhu"), ("jing", "精", "cui"),
                 ("gui", "鬼", "hun"), ("guai", "怪", "liu"),
                 ("shen", "神", "qing"), ("fo", "佛", "jin"), ("ren", "人", "dai")],
        "blurb": {
            "yao": "占山踞洞、统率妖众的魔头，多以人形示人。",
            "jing": "兽、禽、鱼虫、草木成精，本相可指认者。",
            "gui": "尸骸、骷髅、僵尸与幽冥鬼卒一类。",
            "guai": "本相难归一类、书中始终以「怪」称之者。",
            "shen": "天界神真、星宿雷将、四海龙王与天门守将。",
            "fo": "如来、菩萨、尊者、罗汉与灵山隨行圣众。",
            "ren": "帝王将相、僧道吏民、后妃宫人与取经沿途凡人。",
        },
        "habs": [("hai", "海", "江河水府", "龙宫、潭渊与河底水宅"),
                 ("lu", "陆", "山岭城郭", "山道、城郭与荒野"),
                 ("kong", "空", "云端天际", "天界、飞行与腾云之属"),
                 ("di", "地（穴）", "洞府幽穴", "洞府、穴居与地宫")],
        "intro": "取经路上所遇妖魔精怪、神佛人主的形象谱录：前六十幅为妖精灵怪摘抄四视图，后一百四十九幅为配角神人立绘，合按妖、精、鬼、怪、神、佛、人七类划分，以海、陆、空、地（穴）安置，逐条附回目与原文。",
        "unit": "段原文",
        "note": "「妖 · 精 · 鬼 · 怪 · 神 · 佛 · 人」与「海 · 陆 · 空 · 地（穴）」两层分类由编者依原文所载判定，用于检索与编排，并非原著官方分类。前六十条取自精怪摘抄（16:9 四视图），后一百四十九条取自国漫风人物立绘（2:3 竖图），两套图幅并存，按各自原比例排版。原著不载「黑白无常」「降龙罗汉」「龙王夫人」之名，此三条据民间俗称与相邻情节列目，按语已注明；「裴虚己」今本无此人，未收。条目若与本相、居所记载有出入，以原文为准，可在 <span style=\"font-family:var(--mono);font-size:11.5px\">tools/taxonomy.json</span> 中改写后重新生成。",
        "catintro": "七类之分，取原文对本相、身份、职司与居所的写法：",
    },
    {
        "id": "shj",
        "title": "山海经",
        "author": "先秦 · 佚名（旧题）",
        "seal": "山海经图",
        "color": "cui",
        "alias": "山海 山经 海经 山海经异兽",
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
    {
        "id": "lz",
        "title": "聊斋志异",
        "author": "清 · 蒲松龄",
        "seal": "聊斋图志",
        "color": "liu",
        "alias": "聊斋 聊斋志异 狐鬼 志异",
        "src": os.path.join(PROJECT, "liaozai", "liaozai_entries.json"),
        "tax": os.path.join(HERE, "taxonomy_lz.json"),
        "img": ("assets/liaozhai", "webp"),
        "json": os.path.join(PROJECT, "data", "liaozhai.json"),
        "cats": [("hu", "狐", "liu"), ("gui", "鬼", "hun"),
                 ("yao", "妖", "cui"), ("shen", "神", "zhu")],
        "blurb": {
            "hu": "狐族与狐女，绥绥之属，多以人形往来人间。",
            "gui": "鬼魂、僵尸、厉鬼与冥途之人，来去无迹。",
            "yao": "山魈、宅妖、纸人木偶、蛇龙水族之属，本相可指认。",
            "shen": "神祇与冥司：雹神、城隍、判官、灵官及地府轮回。",
        },
        "habs": [("zhai", "宅", "第宅官署", "第宅、官署与寺观"),
                 ("ye", "野", "山野坟冢", "山野、道路与坟冢"),
                 ("shui", "水", "江河湖海", "江河、湖海与井泉"),
                 ("ming", "冥", "地府阴司", "地府、阴司与梦魂所至"),
                 ("tian", "天", "云端神祇", "云端、雷雹与神祇所居")],
        "intro": "灯窗之下的狐鬼妖神，按狐、鬼、妖、神分类，以宅、野、水、冥、天安置，逐条附篇名与原文摘句。",
        "unit": "段摘抄",
        "note": "《聊斋志异》原书以篇为单位，并无「狐 · 鬼 · 妖 · 神」之别；本图志为检索方便，由编者依摘抄原文判定归类，以宅、野、水、冥、天安置，非原著分类。「神」兼收冥司判官、城隍与轮回诸篇，凡神职、冥职者归之。条目若与原文记载有出入，以原文为准，可在 <span style=\"font-family:var(--mono);font-size:11.5px\">tools/taxonomy_lz.json</span> 中改写后重新生成。",
        "catintro": "四类之分，取摘抄原文对本相、神职与所处之地的写法：",
    },
    {
        "id": "zby",
        "title": "子不语",
        "author": "清 · 袁枚",
        "seal": "子不语图",
        "color": "qing",
        "alias": "子不语 新齐谐 袁枚 续齐谐",
        "src": os.path.join(PROJECT, "子不语", "_extract.md"),
        "srcimg": os.path.join(PROJECT, "子不语", "出品"),
        "tax": os.path.join(HERE, "taxonomy_zby.json"),
        "img": ("assets/zibuyu", "webp"),
        "json": os.path.join(PROJECT, "data", "zibuyu.json"),
        "descLabel": "按语",
        "quoteLabel": "形貌摘抄",
        "cats": [("gui", "鬼", "hun"), ("shou", "兽", "cui"),
                 ("shen", "神", "zhu"), ("guai", "怪", "liu")],
        "blurb": {
            "gui": "鬼魅、骷髅、僵尸与旱魃，来去随夜与坟土。",
            "shou": "兽形精怪：毛人、人熊、龙蛇龟鼠与草木鸟兽之异。",
            "shen": "神祇与异人：黑面丈余、牛头大王、金将军及三头、鸡脚之人。",
            "guai": "器物与草木之怪：太岁、匾上人面、白瓷礅、柳树精之属。",
        },
        "habs": [("zhai", "宅", "第宅官署", "第宅、官署、祠堂与庙塑"),
                 ("ye", "野", "山野坟冢", "山野、道路、坟冢与田土"),
                 ("shui", "水", "江河湖海", "江河、湖海与水面"),
                 ("ming", "冥", "幽冥阴间", "阴间、地府与冥所畜养"),
                 ("tian", "天", "云端空际", "云端、空中与神祇所在")],
        "intro": "随笔记闻的精妖鬼怪，按鬼、兽、神、怪分类，以宅、野、水、冥、天安置，逐条附卷次篇名与形貌摘抄。",
        "unit": "条摘抄",
        "note": "《子不语》（一名《新齐谐》）原书二十四卷、六百八十五则，随笔体例并无类目；本图志为检索方便，由编者依形貌摘抄判定归类，以宅、野、水、冥、天安置，非原著分类。原编所标「鬼魅骷髅」「僵尸」「旱魃」并入「鬼」，「器物之怪」「树精」「草木怪」并入「怪」，「神」兼收神祇与异人。条目若与原文记载有出入，以原文为准，可在 <span style=\"font-family:var(--mono);font-size:11.5px\">tools/taxonomy_zby.json</span> 中改写后重新生成。",
        "catintro": "四类之分，取摘抄原文对本相、身份与所处之地的写法：",
    },
    {
        "id": "sjs",
        "title": "三教搜神大全",
        "author": "元 · 佚名（旧题）",
        "seal": "搜神图志",
        "color": "jin",
        "alias": "三教搜神 搜神大全 搜神记 三教源流搜神大全",
        "src": os.path.join(PROJECT, "三教搜神大全", "_roster.json"),
        "tax": os.path.join(HERE, "taxonomy_sjs.json"),
        "img": ("assets/sanjiao", "webp"),
        "json": os.path.join(PROJECT, "data", "sanjiao.json"),
        "descLabel": "生图要点",
        "quoteLabel": "原文依据",
        "cats": [("tianjie", "天界", "zhu"), ("shimen", "释门", "cui"),
                 ("shanchuan", "山川", "qing"), ("renshen", "人神", "liu"),
                 ("wuguai", "物怪", "hun"), ("hufa", "护法", "zhu")],
        "blurb": {
            "tianjie": "卷一、卷二：三教教主、玉皇帝君、三元五岳与修真真人。",
            "shimen": "卷三释氏圣众：观音、地藏、明王、罗汉与历代高僧。",
            "shanchuan": "卷三山川湖海之神：二郎、湘君、洞庭君与四渎岳神之属。",
            "renshen": "卷四忠烈城隍冥官，兼卷六门神、灶神、钟馗诸家宅之神。",
            "wuguai": "卷五地方神灵与物怪：石神、钟神、金火之精、盘瓠之属。",
            "hufa": "卷七：天妃与十二位护法元帅，雷部、瘟部与灵官诸将。",
        },
        "habs": [("tian", "天", "云阙星宫", "天界、云端与星宫神座"),
                 ("shan", "山", "岳渎名山", "五岳、名山与洞天石室"),
                 ("shui", "水", "江海潭泉", "江河、湖海、潭渊与水府"),
                 ("di", "地", "城隍冥府", "城隍、冥司、土神与地脉"),
                 ("zhai", "宅", "家室门户", "门神、灶神、寺观与家祠")],
        "intro": "三教源流所祀的天界帝君、释门圣众、山川岳渎、忠烈人神、地方物怪与护法元帅，按天界、释门、山川、人神、物怪、护法分类，以天、山、水、地、宅安置，逐条附原文依据与法相。",
        "unit": "位神祇",
        "note": "《三教搜神大全》（全称《三教源流搜神大全》）七卷，共收一百五十位神仙佛圣，原书并无类目；本图志为检索方便，由编者依卷次与职司判定归入「天界 · 释门 · 山川 · 人神 · 物怪 · 护法」六类，以天、山、水、地、宅安置，非原书分类。卷五「地方神灵与物怪」一体收录，原书小传多残缺，法相依据多取自存世篇目。条目若与原文记载有出入，以原文为准，可在 <span style=\"font-family:var(--mono);font-size:11.5px\">tools/taxonomy_sjs.json</span> 中改写后重新生成。",
        "catintro": "六类之分，取原书卷次与本相、职司的写法：",
    },
    {
        "id": "lzl",
        "title": "列子",
        "author": "战国 · 列御寇（旧题，今本或魏晋人辑）",
        "seal": "列子图志",
        "color": "cang",
        "alias": "列子 冲虚真经 冲虚至德真经 列御寇 列子寓言",
        "src": os.path.join(PROJECT, "列子", "_roster.json"),
        "tax": os.path.join(HERE, "taxonomy_lzl.json"),
        "img": ("assets/liezi", "webp"),
        "imgw": 1600, "imgh": 2114,
        "json": os.path.join(PROJECT, "data", "liezi.json"),
        "descLabel": "按语",
        "quoteLabel": "形貌摘抄",
        "cats": [("shen", "神异", "zhu"), ("ju", "巨兽", "cui"),
                 ("ren", "大小人", "liu"), ("wei", "微巧", "hun")],
        "blurb": {
            "shen": "姑射之山的神人、蛇身人面的上古圣王、乘虚不坠的化人。",
            "ju": "巨鳌、鲲、鹏与五山禽兽——以尺寸定形，形由数目承担。",
            "ren": "龙伯国之巨人，僬侥、诤人之小人，一头一尾的两极。",
            "wei": "焦螟集于蚊睫之微，偃师所造倡者之机巧。",
        },
        "habs": [("tian", "天", "云虚仙境", "乘虚、降霄与神人所居"),
                 ("shan", "山", "山岳崖穴", "姑射、五山与石壁崖穴"),
                 ("shui", "水", "江海渊泉", "归墟、江浦与巨鳌所戴"),
                 ("ye", "野", "荒服远国", "龙伯、僬侥与东北极之野"),
                 ("zhai", "宅", "王庭机巧", "王庭、机巧与人间器用")],
        "intro": "诸子寓言中的神人、巨兽、大小人与微巧之形，按神异、巨兽、大小人、微巧分类，以天、山、水、野、宅安置，逐条附篇次与原文。",
        "unit": "条摘抄",
        "note": "《列子》八篇旧题周列御寇撰，今本多谓魏晋人辑录，为诸子寓言而非志怪结集，原书并无类目；本图志为检索方便，由编者依形语判定归入「神异 · 巨兽 · 大小人 · 微巧」四类，以天、山、水、野、宅安置，非原书分类。天瑞、仲尼、力命、杨朱、说符五篇无可摘之精怪形貌，故十四幅仅出黄帝三、周穆王篇一、汤问十。原编所标「神人」「鬼物」「异人」「神」并入「神异」，「巨兽」「异兽」并入「巨兽」，「巨人」「小人」并入「大小人」，「微虫」「傀儡」并入「微巧」。条目若与原文记载有出入，以原文为准，可在 <span style=\"font-family:var(--mono);font-size:11.5px\">tools/taxonomy_lzl.json</span> 中改写后重新生成。",
        "catintro": "四类之分，取原文以量定形、以能代形的写法：",
    },
    {
        "id": "syj",
        "title": "述异记",
        "author": "南朝梁 · 任昉（旧题）",
        "seal": "述异图志",
        "color": "zhe",
        "alias": "述异记 任昉 述异 精妖鬼怪",
        "src": os.path.join(PROJECT, "述异记", "_roster.json"),
        "tax": os.path.join(HERE, "taxonomy_syj.json"),
        "img": ("assets/shuyiji", "webp"),
        "imgw": 1536, "imgh": 2048,
        "json": os.path.join(PROJECT, "data", "shuyiji.json"),
        "descLabel": "按语",
        "quoteLabel": "形貌摘抄",
        "cats": [("shen", "神祇", "zhu"), ("jing", "精魅", "cui"),
                 ("hua", "化形", "qing"), ("guai", "物怪", "liu")],
        "blurb": {
            "shen": "开天的盘古、产鬼的鬼母、铜头铁额的蚩尤与驱石、立祠之神。",
            "jing": "物老成精者：梓树青羊、白水素女、枝上小儿、梁上藻兼之属。",
            "hua": "一身两状者：鲧化黄能、女化精卫、虺蛟龙应龙五百年一进阶。",
            "guai": "兽、禽、虫、蛇与征兆：猰㺄、獬豸、鳛鳛十翼、龟毛兔角。",
        },
        "habs": [("tian", "天", "霄汉天兆", "开天、升天与天降之兆"),
                 ("shan", "山", "山岳崖穴", "名山、崖穴与山中草木之精"),
                 ("shui", "水", "江海潭泉", "江海、石湖、井泉与水居之属"),
                 ("ye", "野", "荒外道路", "荒外异国、道路与地中所得"),
                 ("zhai", "宅", "宫庙村舍", "宫室、祠庙、村舍与家池")],
        "intro": "上下二卷所记的古神、精魅、化形与物怪，按神祇、精魅、化形、物怪分类，以天、山、水、野、宅安置，逐条附卷次与形貌摘抄。",
        "unit": "条摘抄",
        "note": "《述异记》二卷旧题南朝梁任昉撰，四库馆臣已疑其或后人依托；原书一条记一物，并无类目。本图志为检索方便，由编者依形语判定归入「神祇 · 精魅 · 化形 · 物怪」四类，以天、山、水、野、宅安置，非原书分类。原编所标「神」「仙」「异人」「巨人」并入「神祇」，「兽怪」「禽怪」「虫怪」「蛇怪」「物怪」「妖征」并入「物怪」。原书每写完一怪常补「今某地有之」，形貌每有两版，本图志并存不裁。条目若与原文记载有出入，以原文为准，可在 <span style=\"font-family:var(--mono);font-size:11.5px\">tools/taxonomy_syj.json</span> 中改写后重新生成。",
        "catintro": "四类之分，取摘抄原文对本相、变状与所在的写法：",
    },
    {
        "id": "tpg",
        "title": "太平广记",
        "author": "宋 · 李昉 等（奉敕编纂）",
        "seal": "太平广记图",
        "color": "zi",
        "alias": "太平广记 广记 李昉 精妖鬼怪 志怪",
        "src": os.path.join(PROJECT, "太平广记", "_roster.json"),
        "tax": os.path.join(HERE, "taxonomy_tpg.json"),
        "img": ("assets/tpgj", "webp"),
        "imgw": 768, "imgh": 1024,
        "json": os.path.join(PROJECT, "data", "tpg.json"),
        "descLabel": "按语",
        "quoteLabel": "形貌摘抄",
        "cats": [("yao", "妖", "zhu"), ("jing", "精", "cui"),
                 ("cha", "夜叉", "liu"), ("hu", "狐", "qing"), ("gui", "鬼", "hun")],
        "blurb": {
            "yao": "凶兆、物怪与拼装的形体——九头狗、遍体毛的人、驴形人手、无首足的白物。先给熟悉的底子，再错装一处，怪就成立。",
            "jing": "器物、明器与家宅之魅——木偶、盟器婢、方相、铁杵、破甑、皮袋、钟。不是长出獠牙，而是学会读书。",
            "cha": "异域之怖的形体——赤发、青身、黄毛、兽爪、豹皮裤、带短兵。不伪装、不隐身，直接以本体出现。",
            "hu": "媚、破、本性——先是完美人形，再有一处破绽（尾、无毛、疥癞、醉后失形），最后由犬或道士一句喝破。",
            "gui": "四卷样本——气味（异香满院）、物证（骷髅赤发）、散场（若烟雾状）。写的是它退场的方式。",
        },
        "habs": [("shan", "山", "山岭", "两山之间与崖谷中现形的妖物。"),
                 ("shui", "水", "江湖陂泽", "池沼、江湖与岸畔的水族妖异。"),
                 ("ye", "野", "山林原野", "道途、田野、林莽中出没之怪。"),
                 ("zhai", "宅", "第宅宫室", "家宅、宫室、庭廊、灶梁间现形之物。"),
                 ("tian", "天", "天星", "天行之怪。"),
                 ("di", "地", "地中·墓圹", "地中、土下与古墓圹中的明器鬼物。"),
                 ("xue", "穴", "穴中", "土穴、窟穴中的藏匿之物。")],
        "intro": "《太平广记》五百卷所辑的精妖鬼怪，按妖、精、夜叉、狐、鬼分类，以山、水、野、宅、天、地、穴安置，逐条附所出书目与形貌摘抄。",
        "unit": "条摘抄",
        "note": "《太平广记》为北宋初李昉等奉敕编纂的类书，原书按部类编排，并无「妖 · 精 · 夜叉 · 狐 · 鬼」之别；本图志直接沿用原页所分部类与名目，逐条附所出书目与形貌摘抄，另按引文所见居所判以山、水、野、宅、天、地、穴七境。名目与部类如需改写，可在 <span style=\"font-family:var(--mono);font-size:11.5px\">tools/taxonomy_tpg.json</span> 中编辑后重新生成。",
        "catintro": "五类之分，沿用原页所标部类：",
    },
    {
        "id": "ssj",
        "title": "搜神记",
        "author": "东晋 · 干宝",
        "seal": "搜神记图",
        "color": "fei",
        "alias": "搜神记 干宝 精妖鬼怪 志怪 狐鬼兽鳞",
        "src": os.path.join(PROJECT, "搜神记", "_roster.json"),
        "tax": os.path.join(HERE, "taxonomy_ssj.json"),
        "img": ("assets/ssj", "webp"),
        "imgw": 1000, "imgh": 1500,
        "json": os.path.join(PROJECT, "data", "ssj.json"),
        "descLabel": "小标题",
        "quoteLabel": "原文摘抄",
        "cats": [("hu", "狐", "zhu"), ("gui", "鬼", "hun"), ("shou", "兽", "cang"),
                 ("lin", "鳞", "qing"), ("jing", "精魅", "cui"), ("hua", "化形", "liu")],
        "blurb": {
            "hu": "狐与狸——白狐、斑狐、老狸、阿紫，善化人形，迷媚于宅。",
            "gui": "鬼魅亡魂——恶鬼、三疫鬼、无头鬼、亡魂，出没于宅冢、山中与江湖。",
            "shou": "兽与水族——羊、鹿、獭、豕、鼠、犀犬、大鳀、马皮蚕女，走兽成精。",
            "lin": "蛇龙龟鼍——巨蛇、华亭大蛇、蛇翁、月下鼍、龟鼍化人，鳞介之异。",
            "jing": "草木山川禽虫星神与器宅之魅——彭侯、树神、山都、冶鸟、度朔君、饭臿、宅妖。",
            "hua": "人形化妖——皓首书生、偶人、冢中美人、女鬼、落头民，人形而藏妖。",
        },
        "habs": [("zhai", "宅", "居室·冢·庙", "家宅、冢墓、宫室、亭庙中现形的精怪鬼魅。"),
                 ("ye", "野", "山林原野", "道途、田野、竹木之间出没的精怪。"),
                 ("shui", "水", "江湖陂泽", "江、湖、陂、泽、渊中的鳞介水族。"),
                 ("shan", "山", "山岭", "两山之间与山中现形的山精、山都、冶鸟、雷兽。"),
                 ("shu", "树", "木中", "树断见物的木之精——彭侯、树神、树心青牛。"),
                 ("di", "地", "地中·穴", "地中、穴中、阴司地下之物。"),
                 ("tian", "天", "天星", "月与荧惑星之精。")],
        "intro": "《搜神记》所记的精妖鬼怪，按狐、鬼、兽、鳞、精魅、化形分类，以宅、野、水、山、树、地、天安置，逐条附章节小标题与原文摘句。",
        "unit": "条摘抄",
        "note": "《搜神记》为东晋干宝所撰志怪，本图志依皮克斯3D版 83 幅设定图整理；六类与七境由编者依原文判定，鬼类五条重名者以所出章节消歧。分类与生境如需改写，可在 <span style=\"font-family:var(--mono);font-size:11.5px\">tools/taxonomy_ssj.json</span> 中编辑后重新生成。",
        "catintro": "六类之分，依原文所记精怪本相与出处判定：",
    },
    {
        "id": "yw",
        "title": "阅微草堂笔记",
        "author": "清 · 纪昀",
        "seal": "阅微草堂",
        "color": "dai",
        "alias": "阅微草堂笔记 纪昀 鬼狐物怪 志怪",
        "src": os.path.join(PROJECT, "阅微草堂笔记", "_roster.json"),
        "tax": os.path.join(HERE, "taxonomy_yw.json"),
        "img": ("assets/yw", "webp"),
        "imgw": 1600, "imgh": 904,
        "json": os.path.join(PROJECT, "data", "yw.json"),
        "descLabel": "纪评",
        "quoteLabel": "原文摘抄",
        "cats": [("gui", "鬼", "hun"), ("hu", "狐", "zhu"), ("wu", "物怪", "cang"),
                 ("jing", "精魅", "cui"), ("long", "龙蛇", "qing"), ("shen", "神", "liu")],
        "blurb": {
            "gui": "鬼魅亡魂——含罗刹、夜叉、山魈与尸变，纪昀以一句成象，靠残缺与错位写鬼。",
            "hu": "狐——鲜写原形，多给不合常理的人间细节：红鞋、捧书人立、顶上出小人。",
            "wu": "物怪与巨物——似人非人的山兽、蓑衣黑物、巨如车轮之蝠，以及墓上、屋上、山间的巨人。",
            "jing": "精魅——白发黑媪、白发佝偻妇、美妇与边地男女，美丑对照，破幻即见。",
            "long": "龙蛇——晴昼之龙、龙爪、锦绣巨蛇，头角如画，只取局部。",
            "shen": "神——红衣树神磬折拱揖，社公衣冠文雅如书生。",
        },
        "habs": [("zhai", "宅", "居室·冢·庙", "门隙灯前、牛栏屋上、墓冢祠庙中现形的鬼狐物怪。"),
                 ("ye", "野", "山林原野", "道左、墟墓、旋风中与巨人出没的山野。"),
                 ("shan", "山", "山岭", "幽谷、高岗、涧畔之怪与山灵巨人。"),
                 ("shu", "树", "木中", "树杪红衣与斜柯垂足之形。"),
                 ("tian", "天", "天星", "晴昼之龙自西而东。")],
        "intro": "《阅微草堂笔记》所记的鬼狐物怪，按鬼、狐、物怪、精魅、龙蛇、神分类，以宅、野、山、树、天安置，逐条附纪评与原文摘句。",
        "unit": "条摘抄",
        "note": "《阅微草堂笔记》为清纪昀所撰志怪，本图志依五书分卷摘出 54 条形貌描写，一条一幅，纪评为编者所附、引文已回检。十二张同题材备选图未收录。分类与生境如需改写，可在 <span style=\"font-family:var(--mono);font-size:11.5px\">tools/taxonomy_yw.json</span> 中编辑后重新生成。",
        "catintro": "六类之分，依原文所记精怪本相与出处判定：",
    },
    {
        "id": "fs",
        "title": "封神演义",
        "author": "明 · 许仲琳",
        "seal": "封神演义",
        "color": "cheng",
        "alias": "封神演义 许仲琳 妖异神怪 神魔 精怪",
        "src": os.path.join(PROJECT, "封神", "_roster.json"),
        "tax": os.path.join(HERE, "taxonomy_fs.json"),
        "img": ("assets/fs", "webp"),
        "imgw": 1600, "imgh": 900,
        "json": os.path.join(PROJECT, "data", "fs.json"),
        "descLabel": "编者评",
        "quoteLabel": "原文摘抄",
        "cats": [("yao", "妖", "zhu"), ("jing", "精怪", "jin"), ("shen", "神", "liu"), ("yi", "异人", "dai")],
        "blurb": {
            "yao": "妖——兽禽虫蛇狐之化形：五妖、狐群、瘟部四使、梅山畜怪与三妖，多以五行配色写面。",
            "jing": "精怪——顽石、龙须虎、泽中怪物、灯头马善与桃柳之精，物老成怪，只给形体。",
            "shen": "神——孔宣五色光华、文殊普贤慈航三大士法身与二十八宿，法相反倒更像妖怪。",
            "yi": "异人——雷震子、辛环、土行孙、余化余元与哪吒诸相，青面朱发、四尺地行、三头八臂。",
        },
        "habs": [("tian", "天", "天界·空中", "法身、雷部先锋与起在空中飞腾的神魔。"),
                 ("shan", "山", "山岭洞府", "截教洞府、万仙阵与梅山群怪所居之岭。"),
                 ("ye", "野", "战场原野", "汜水关、泽畔与两军阵前现形的物怪妖兽。"),
                 ("zhai", "宅", "宫闱", "轩辕坟狐群与妲己三妖潜身的宫闱。"),
                 ("shui", "水", "水泽", "水底生威的龟灵圣母。")],
        "intro": "《封神演义》所记的精妖鬼怪，按妖、精怪、神、异人四类划分，以天、山、野、宅、水五境安置，逐条附编者评与原文摘句。",
        "unit": "条摘抄",
        "note": "《封神演义》为明许仲琳所撰神魔小说，本图志自第十三回至第九十七回摘出 47 条形貌描写，一条一幅；四视图为编者依既有版式补绘（普贤法身、高明、高觉、常昊、三妖、龙须虎六图后补）。拆“高明高觉”一条为桃精柳鬼两条。编者评与生境为编者所立，分类与生境如需改写，可在 <span style=\"font-family:var(--mono);font-size:11.5px\">tools/taxonomy_fs.json</span> 中编辑后重新生成。",
        "catintro": "四类之分，依原文所记精怪本相与出处判定：",
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


def parse_xyj_roster(path):
    """data/xyj_roster150.json → 补录条目（编号 061 起，2:3 竖图立绘）。"""
    data = json.load(open(path, encoding="utf-8"))
    entries = []
    for e in data:
        entries.append({
            "id": e["id"], "num": int(e["num"]), "name": e["name"],
            "chapter": e["chapter"], "chapterShort": e["chapterShort"],
            "desc": e.get("desc", ""), "para": None, "quote": e["quote"],
            "pinyin": "", "shape": e.get("shape", "tall"),
            "imgw": e.get("imgw", 1600), "imgh": e.get("imgh", 2400),
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


def parse_lz(path):
    """[{"no":1,"title":"《遵化署狐》｜群狐据楼为家","raw":"…"}, …] → 记录"""
    data = json.load(open(path, encoding="utf-8-sig"))
    entries = []
    for e in data:
        num = int(e["no"])
        title = e["title"]
        m = re.match(r"^《(.+?)》\s*[｜|]\s*(.+)$", title)
        chapter, scene = (m.group(1), m.group(2)) if m else (title, "")
        entries.append({
            "id": "%02d" % num, "num": num,
            "name": "%s（%s）" % (chapter, scene) if scene else chapter,
            "chapter": "《%s》" % chapter, "chapterShort": "第 %02d 则" % num,
            "desc": scene.strip(), "para": None,
            "quote": "\n".join(l.strip() for l in (e.get("raw") or "").splitlines() if l.strip()),
            "pinyin": "",
        })
    return entries


def parse_zby(path, imgdir):
    """_extract.md 按行扫描：【卷N·篇名】名称（类别） / 形貌摘抄 / 评：…；
    编号按 出品/NN-名称.png 的名称对位（图文顺序不同，不能按序对齐）。"""
    head = re.compile(r"^【卷(.+?)·(.+?)】(.+?)（(.+?)）\s*$")
    items, cur = [], None
    for line in open(path, encoding="utf-8").read().splitlines():
        line = line.strip()
        m = head.match(line)
        if m:
            cur = {"juan": "卷" + m.group(1).strip(), "pian": m.group(2).strip(),
                   "name": m.group(3).strip(), "label": m.group(4).strip(),
                   "quote": "", "comment": ""}
            items.append(cur)
            continue
        if cur is None or not line:
            continue
        if line.startswith("评："):
            cur["comment"] = line[2:].strip()
        elif not cur["comment"]:
            cur["quote"] = cur["quote"] + line
    num_of = {}
    for f in os.listdir(imgdir):
        mm = re.match(r"^(\d{2})-(.+)\.(png|jpg|jpeg)$", f)
        if mm:
            num_of[mm.group(2)] = int(mm.group(1))
    missing = [e["name"] for e in items if e["name"] not in num_of]
    if missing:
        raise SystemExit("子不语：出品目录缺图 %s" % "、".join(missing))
    dup = len(items) - len({num_of[e["name"]] for e in items})
    if dup:
        raise SystemExit("子不语：条目与图片编号重复 %d 条" % dup)
    out = []
    for e in items:
        n = num_of[e["name"]]
        out.append({
            "id": "%02d" % n, "num": n, "name": e["name"],
            "chapter": "《子不语》%s · %s" % (e["juan"], e["pian"]),
            "chapterShort": e["juan"],
            "desc": e["comment"], "para": None, "quote": e["quote"],
            "pinyin": "",
        })
    return out


def parse_sjs(path):
    """_roster.json（由三教搜神大全/_roster_build.py 从提示词库抽出）→ 记录；
    编号即出品文件名前缀，三位数。"""
    data = json.load(open(path, encoding="utf-8"))
    if len(data) != 150:
        raise SystemExit("三教搜神大全：条目 %d 条，应为 150" % len(data))
    entries = []
    for e in data:
        num = int(e["num"])
        entries.append({
            "id": e["id"], "num": num, "name": e["name"],
            "chapter": "《三教搜神大全》%s · 第 %d 位" % (e["juan"], num),
            "chapterShort": e["juan"],
            "desc": e["prompt"], "para": None,
            "quote": e["quote"], "pinyin": "",
        })
    return entries


def parse_lzl(path):
    """列子/_roster.json（由 tools/build_rosters.py 生成）→ 记录；编号两位。"""
    data = json.load(open(path, encoding="utf-8"))
    if len(data) != 14:
        raise SystemExit("列子：条目 %d 条，应为 14" % len(data))
    entries = []
    for e in data:
        entries.append({
            "id": e["id"], "num": int(e["num"]), "name": e["name"],
            "chapter": "《列子》%s" % e["pian"],
            "chapterShort": "%s篇" % e["juan"],
            "desc": e["comment"], "para": None,
            "quote": e["quote"], "pinyin": "",
        })
    return entries


def parse_syj(path):
    """述异记/_roster.json（同源生成）→ 记录；卷上/卷下分卷，编号两位。"""
    data = json.load(open(path, encoding="utf-8"))
    if len(data) != 57:
        raise SystemExit("述异记：条目 %d 条，应为 57" % len(data))
    entries = []
    for e in data:
        num = int(e["num"])
        entries.append({
            "id": e["id"], "num": num, "name": e["name"],
            "chapter": "《述异记》%s · 第 %d 则" % (e["juan"], num),
            "chapterShort": e["juan"],
            "desc": e["comment"], "para": None,
            "quote": e["quote"], "pinyin": "",
        })
    return entries


def parse_tpg(path):
    """太平广记/_roster.json（由 tpgy_index.html 解析生成）→ 记录；编号两位。"""
    data = json.load(open(path, encoding="utf-8"))
    if len(data) != 74:
        raise SystemExit("太平广记：条目 %d 条，应为 74" % len(data))
    entries = []
    for e in data:
        num = int(e["num"])
        src = e["source"] if e["source"] and e["source"] != "无出处" else "太平广记"
        entries.append({
            "id": e["id"], "num": num, "name": e["name"],
            "chapter": e["chapter"], "chapterShort": src,
            "desc": e["desc"], "para": None,
            "quote": e["quote"], "pinyin": "",
        })
    return entries


def parse_ssj(path):
    """搜神记/_roster.json → 记录；编号三位。"""
    data = json.load(open(path, encoding="utf-8"))
    if len(data) != 83:
        raise SystemExit("搜神记：条目 %d 条，应为 83" % len(data))
    entries = []
    for e in data:
        entries.append({
            "id": e["id"], "num": int(e["num"]), "name": e["name"],
            "chapter": e["chapter"], "chapterShort": e["chapterShort"],
            "desc": e["desc"], "para": None,
            "quote": e["quote"], "pinyin": "",
        })
    return entries


def parse_yw(path):
    """阅微草堂笔记/_roster.json → 记录；编号三位。"""
    data = json.load(open(path, encoding="utf-8"))
    if len(data) != 54:
        raise SystemExit("阅微草堂笔记：条目 %d 条，应为 54" % len(data))
    entries = []
    for e in data:
        entries.append({
            "id": e["id"], "num": int(e["num"]), "name": e["name"],
            "chapter": e["chapter"], "chapterShort": e["chapterShort"],
            "desc": e["desc"], "para": None,
            "quote": e["quote"], "pinyin": "",
        })
    return entries


def parse_fs(path):
    """封神演义/_roster.json → 记录；编号三位。"""
    data = json.load(open(path, encoding="utf-8"))
    if len(data) != 47:
        raise SystemExit("封神演义：条目 %d 条，应为 47" % len(data))
    entries = []
    for e in data:
        entries.append({
            "id": e["id"], "num": int(e["num"]), "name": e["name"],
            "chapter": e["chapter"], "chapterShort": e["chapterShort"],
            "desc": e["desc"], "para": None,
            "quote": e["quote"], "pinyin": "",
        })
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
    if w["id"] == "xyj":
        entries = parse_xyj(w["src"]) + parse_xyj_roster(w["roster"])
    elif w["id"] == "shj":
        entries = parse_shj(w["src"])
    elif w["id"] == "lz":
        entries = parse_lz(w["src"])
    elif w["id"] == "zby":
        entries = parse_zby(w["src"], w["srcimg"])
    elif w["id"] == "sjs":
        entries = parse_sjs(w["src"])
    elif w["id"] == "lzl":
        entries = parse_lzl(w["src"])
    elif w["id"] == "syj":
        entries = parse_syj(w["src"])
    elif w["id"] == "tpg":
        entries = parse_tpg(w["src"])
    elif w["id"] == "ssj":
        entries = parse_ssj(w["src"])
    elif w["id"] == "yw":
        entries = parse_yw(w["src"])
    elif w["id"] == "fs":
        entries = parse_fs(w["src"])
    else:
        raise SystemExit("未知作品解析器：%s" % w["id"])
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
    hero_items = []
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
                ' data-shape="{shape}" data-id="{id}" data-name="{name}" data-chapter="{chap}"'
                ' style="--cat:var(--{color})">\n'
                '  <a class="plate-fig" href="#/w/{work}/x/{cat}/{id}" aria-label="打开 {name} 的设定与原文">'
                '<img src="{img}" alt="{name} 设定图" width="{iw}" height="{ih}" loading="lazy" decoding="async">'
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
                shape=e.get("shape", "wide"),
                chap=esc(e["chapterShort"]), color=cat_color[e["cat"]], num="%02d" % e["num"],
                main=esc(main), subhtml=sub_html, catlabel=cat_name[e["cat"]],
                hablabel=hab_label[e["hab"]], basis=esc(e["basis"]), chapter=esc(e["chapter"]),
                desc=esc(e["desc"]), quote=esc(e["quote"]), img=e["img"],
                iw=e.get("imgw", w.get("imgw", 1600)), ih=e.get("imgh", w.get("imgh", 903)),
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
            % (w["id"], "var(--%s)" % w["color"], seal,
               esc(w["title"]), esc(w["author"]), esc(w["intro"]),
               len(rows), len(cats), len(habs), len(rows), w["unit"],
               wbars(), w["id"], len(rows))
        )

        # ---------- JS 元数据 ----------
        meta_js[w["id"]] = {
            "title": w["title"],
            "alias": w["alias"],
            "cats": dict((c[0], {"name": c[1], "color": c[2]}) for c in cats),
            "habs": dict((h[0], {"name": h[1], "short": h[2]}) for h in habs),
            "habOrder": [h[0] for h in habs],
            "descLabel": w.get("descLabel", "描写内容"),
            "quoteLabel": w.get("quoteLabel", "原文"),
        }
        for r in rows:
            hero_items.append({
                "img": r["img"], "name": r["name"],
                "shape": r.get("shape", "wide"),
                "sub": "%s · %s" % (w["title"], r["chapterShort"] or r["chapter"]),
            })

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
    ncats = sum(len(w["cats"]) for w in WORKS)
    nhabs = sum(len(w["habs"]) for w in WORKS)
    out = (tpl.replace("{{WORKCARDS}}", "\n".join(cards))
              .replace("{{CATVIEWS}}", "\n".join(catviews))
              .replace("{{GALLERIES}}", "\n".join(galleries))
              .replace("{{WORKMETA_JS}}", json.dumps(meta_js, ensure_ascii=False, indent=2))
              .replace("{{HERO_ITEMS_JS}}", json.dumps(hero_items, ensure_ascii=False))
              .replace("{{TOPMETA}}", "%d 幅 · %d 部 · %d 类" % (total, len(WORKS), ncats))
              .replace("{{N_ITEMS}}", str(total))
              .replace("{{N_WORKS}}", str(len(WORKS)))
              .replace("{{N_CATS}}", str(ncats))
              .replace("{{N_HABS}}", str(nhabs)))
    for token in ("{{WORKCARDS}}", "{{CATVIEWS}}", "{{GALLERIES}}", "{{WORKMETA_JS}}"):
        if token in out:
            raise SystemExit("模板占位未替换：%s" % token)
    open(OUT_HTML, "w", encoding="utf-8", newline="\n").write(out)
    print("生成 %s（%.0f KB），合计 %d 幅" %
          (os.path.basename(OUT_HTML), os.path.getsize(OUT_HTML) / 1024.0, total))


if __name__ == "__main__":
    sys.exit(build())
