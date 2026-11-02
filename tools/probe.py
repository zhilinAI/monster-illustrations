# -*- coding: utf-8 -*-
"""生成临时探针副本，用于截取分类页、图录页、灯箱、检索四态。
用法：python tools/probe.py   （截图后删除 _probe_*.html）
"""
import os

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT, "西游记妖精灵怪图志.html")

PROBES = {
    "_probe_cats.html": 'location.hash="#/w/xyj";',
    "_probe_legacy.html": 'location.hash="#/x/gui/14";',
    "_probe_shj_cats.html": 'location.hash="#/w/shj";',
    "_probe_shj_shen.html": 'location.hash="#/w/shj/x/shen";',
    "_probe_shj_lb.html": ('location.hash="#/w/shj/x/shen/09";'
                           'document.querySelector("main").style.display="none";'
                           'document.querySelector("footer").style.display="none";'),
    "_probe_gal_jing.html": 'location.hash="#/w/xyj/x/jing";',
    "_probe_search.html": ('var el=document.getElementById("q");'
                           'el.value="九尾狐";'
                           'el.dispatchEvent(new Event("input"));'),
}

html = open(SRC, encoding="utf-8").read()
for name, js in PROBES.items():
    out = html.replace("</body>", "<script>%s</script>\n</body>" % js)
    with open(os.path.join(PROJECT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    print("写出 " + name + "  " + js)
