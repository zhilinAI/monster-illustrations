# -*- coding: utf-8 -*-
"""把 _roster_150_raw.json 整理成站点用的 data/xyj_roster150.json，
并同步把补录条目并入 tools/taxonomy.json。

用法：python tools/finalize_roster150.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
RAW = os.path.join(PROJECT, "data", "xyj_roster150_raw.json")
OUT = os.path.join(PROJECT, "data", "xyj_roster150.json")
TAX = os.path.join(HERE, "taxonomy.json")


def main():
    rows = json.load(open(RAW, encoding="utf-8"))
    if len(rows) < 140:
        raise SystemExit("条目过少：%d" % len(rows))
    out = []
    for r in rows:
        d = {
            "id": r["id"], "num": r["num"], "name": r["name"],
            "chapter": r["chapter"], "chapterShort": r["chapterShort"],
            "desc": "形貌装束" if r.get("verse") else "行止言谈",
            "quote": r["quote"], "qsrc": r.get("src", "原著"),
            "cat": r["cat"], "hab": r["hab"], "basis": r["basis"],
            "shape": "tall", "imgw": 1600, "imgh": 2400,
        }
        out.append(d)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=1)

    tax = json.load(open(TAX, encoding="utf-8"))
    for d in out:
        tax["items"][d["id"]] = {"cat": d["cat"], "hab": d["hab"], "basis": d["basis"]}
    json.dump(tax, open(TAX, "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=1)
    print("名录 %d 条 → %s；分类表合计 %d 条" % (len(out), OUT, len(tax["items"])))


if __name__ == "__main__":
    sys.exit(main())
