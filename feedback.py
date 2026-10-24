#!/usr/bin/env python3
"""讀 GitHub not-important issues -> not_interested.json（冪等，以作品名去重）"""
import json, re, subprocess, os
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = "1234yyyyyy/manga-radar"
OUT = os.path.join(HERE, "not_interested.json")
js = json.loads(subprocess.check_output(["gh","issue","list","-R",REPO,"--label","not-important","--state","all","--limit","500","--json","number,body,createdAt,state"]))
rows = {r["title"]: r for r in json.load(open(OUT, encoding="utf-8"))} if os.path.exists(OUT) else {}
for iss in js:
    for line in (iss.get("body") or "").splitlines():
        m = re.match(r"\s*-\s*\[([^\]]*)\]\s*(.+?)\s*$", line)
        if m: rows.setdefault(m.group(2), {"title": m.group(2), "genres": [g for g in re.split(r"[、,/]\s*", m.group(1)) if g], "date": iss["createdAt"][:10], "issue": iss["number"]})
json.dump(sorted(rows.values(), key=lambda r: r["date"]), open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(rows)} not-interested titles -> {OUT}; open issues: {[i['number'] for i in js if i['state']=='OPEN']}")
