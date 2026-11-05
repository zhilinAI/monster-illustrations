# -*- coding: utf-8 -*-
"""生成临时探针副本，用于截取分类页、图录页、灯箱、检索四态。
用法：python tools/probe.py   （截图后删除 _probe_*.html）
"""
import os

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT, "index.html")

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
    "_probe_lz_cats.html": 'location.hash="#/w/lz";',
    "_probe_lz_all.html": 'location.hash="#/w/lz/x/all";',
    "_probe_lz_hu.html": 'location.hash="#/w/lz/x/hu";',
    "_probe_lz_lb.html": ('location.hash="#/w/lz/x/gui/21";'
                          'document.querySelector("main").style.display="none";'
                          'document.querySelector("footer").style.display="none";'),
    "_probe_lz_search.html": ('var el=document.getElementById("q");'
                              'el.value="聂小倩";'
                              'el.dispatchEvent(new Event("input"));'),
    "_probe_zby_cats.html": 'location.hash="#/w/zby";',
    "_probe_zby_all.html": 'location.hash="#/w/zby/x/all";',
    "_probe_zby_gui.html": 'location.hash="#/w/zby/x/gui";',
    "_probe_zby_shou.html": 'location.hash="#/w/zby/x/shou";',
    "_probe_zby_lb.html": ('location.hash="#/w/zby/x/shou/19";'
                           'document.querySelector("main").style.display="none";'
                           'document.querySelector("footer").style.display="none";'),
    "_probe_zby_search.html": ('var el=document.getElementById("q");'
                               'el.value="簸箕龟";'
                               'el.dispatchEvent(new Event("input"));'),
    "_probe_sjs_cats.html": 'location.hash="#/w/sjs";',
    "_probe_sjs_all.html": 'location.hash="#/w/sjs/x/all";',
    "_probe_sjs_hufa.html": 'location.hash="#/w/sjs/x/hufa";',
    "_probe_sjs_lb.html": ('location.hash="#/w/sjs/x/hufa/150";'
                           'document.querySelector("main").style.display="none";'
                           'document.querySelector("footer").style.display="none";'),
    "_probe_sjs_search.html": ('var el=document.getElementById("q");'
                               'el.value="哪吒太子";'
                               'el.dispatchEvent(new Event("input"));'),
    "_probe_lzl_cats.html": 'location.hash="#/w/lzl";',
    "_probe_lzl_all.html": 'location.hash="#/w/lzl/x/all";',
    "_probe_lzl_lb.html": ('location.hash="#/w/lzl/x/ju/11";'
                           'document.querySelector("main").style.display="none";'
                           'document.querySelector("footer").style.display="none";'),
    "_probe_syj_cats.html": 'location.hash="#/w/syj";',
    "_probe_syj_jing.html": 'location.hash="#/w/syj/x/jing";',
    "_probe_syj_lb.html": ('location.hash="#/w/syj/x/shen/01";'
                           'document.querySelector("main").style.display="none";'
                           'document.querySelector("footer").style.display="none";'),
    "_probe_all_search.html": ('var el=document.getElementById("q");'
                               'el.value="鲛人";'
                               'el.dispatchEvent(new Event("input"));'),
    "_probe_tpg_cats.html": 'location.hash="#/w/tpg";',
    "_probe_tpg_yao.html": 'location.hash="#/w/tpg/x/yao";',
    "_probe_tpg_hu.html": 'location.hash="#/w/tpg/x/hu";',
    "_probe_tpg_lb.html": ('location.hash="#/w/tpg/x/yao/01";'
                           'document.querySelector("main").style.display="none";'
                           'document.querySelector("footer").style.display="none";'),
    "_probe_tpg_search.html": ('var el=document.getElementById("q");'
                               'el.value="四足牛怪";'
                               'el.dispatchEvent(new Event("input"));'),
    "_probe_ssj_cats.html": 'location.hash="#/w/ssj";',
    "_probe_ssj_hu.html": 'location.hash="#/w/ssj/x/hu";',
    "_probe_ssj_lb.html": ('location.hash="#/w/ssj/x/gui/019";'
                           'document.querySelector("main").style.display="none";'
                           'document.querySelector("footer").style.display="none";'),
    "_probe_ssj_search.html": ('var el=document.getElementById("q");'
                               'el.value="白狐精";'
                               'el.dispatchEvent(new Event("input"));'),
    "_probe_yw_cats.html": 'location.hash="#/w/yw";',
    "_probe_yw_gui.html": 'location.hash="#/w/yw/x/gui";',
    "_probe_yw_lb.html": ('location.hash="#/w/yw/x/gui/023";'
                          'document.querySelector("main").style.display="none";'
                          'document.querySelector("footer").style.display="none";'),
    "_probe_yw_search.html": ('var el=document.getElementById("q");'
                              'el.value="惨绿衫女鬼";'
                              'el.dispatchEvent(new Event("input"));'),
    "_probe_fs_cats.html": 'location.hash="#/w/fs";',
    "_probe_fs_yao.html": 'location.hash="#/w/fs/x/yao";',
    "_probe_fs_lb.html": ('location.hash="#/w/fs/x/yao/046";'
                          'document.querySelector("main").style.display="none";'
                          'document.querySelector("footer").style.display="none";'),
    "_probe_fs_search.html": ('var el=document.getElementById("q");'
                              'el.value="龙须虎";'
                              'el.dispatchEvent(new Event("input"));'),
}

html = open(SRC, encoding="utf-8").read()
for name, js in PROBES.items():
    out = html.replace("</body>", "<script>%s</script>\n</body>" % js)
    with open(os.path.join(PROJECT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    print("写出 " + name + "  " + js)
