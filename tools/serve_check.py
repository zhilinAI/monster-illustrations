import urllib.request, json

def probe(path):
    url = "http://127.0.0.1:8088/" + path
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            return r.status, r.headers.get("Content-Type"), len(r.read())
    except Exception as e:
        return "ERR", str(e), 0

for p in ["%E8%A5%BF%E6%B8%B8%E8%AE%B0%E5%A6%96%E7%B2%BE%E7%81%B5%E6%80%AA%E5%9B%BE%E5%BF%97.html",
          "assets/characters/02.webp",
          "assets/characters/60.webp",
          "data/characters.json",
          "README.md",
          "no-such-file.webp"]:
    s, c, n = probe(p)
    print("%-6s %-28s %-18s %s" % (s, p[-28:], c, n))
