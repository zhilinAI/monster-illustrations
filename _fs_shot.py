# -*- coding: utf-8 -*-
"""截取封神探针四态到 _shots\\。临时脚本，用后删除。"""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

proj = Path(r"E:\西游记-00\建模\西游记")
shots = proj / "_shots"
shots.mkdir(exist_ok=True)
targets = [
    ("_probe_fs_cats.html", "fs_cats_desktop.png"),
    ("_probe_fs_yao.html", "fs_yao_desktop.png"),
    ("_probe_fs_lb.html", "fs_lb_desktop.png"),
    ("_probe_fs_search.html", "fs_search_desktop.png"),
]
with sync_playwright() as p:
    browser = p.chromium.launch()
    for name, out in targets:
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto((proj / name).resolve().as_uri())
        page.wait_for_timeout(1400)
        if name.endswith("_lb.html"):
            page.screenshot(path=str(shots / out))
        else:
            page.screenshot(path=str(shots / out), full_page=True)
        page.close()
        print("shot", out)
    browser.close()
