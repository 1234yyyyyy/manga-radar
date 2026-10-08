"""單頁漫畫卡片目錄。改自 /workspace/ai-tools/build.py，資料在 data.json。"""
import base64, html, io, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/workspace/manga-cards")
DATA = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
assert len(DATA) == 25

def thumb(item):
    src = ROOT / "img" / f"{item['id']}.jpg"
    if src.exists() and src.stat().st_size > 1500:
        im = Image.open(src).convert("RGB")
        w = 480
        h = max(1, round(im.height * w / im.width))
        im = im.resize((w, h), Image.Resampling.LANCZOS)
        real = True
    else:
        im = Image.new("RGB", (480, 680), (40, 36, 32))
        d = ImageDraw.Draw(im)
        font = ImageFont.load_default()
        d.text((24, 300), item["title"], fill=(245, 166, 35), font=font)
        real = False
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82)
    uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    return uri, real

def meta_line(it):
    score = f"漫畫櫃 {it['score']} 分" if it.get("score") else "漫畫櫃評分未確認"
    return f"{it['meta_genre']}・{it['status']}・{score}"

e = html.escape
cards = []
cover_ok = 0
for i, it in enumerate(DATA, 1):
    uri, real = thumb(it)
    cover_ok += int(real)
    tags = ["#" + g for g in it["genres"]] + ["#" + it["tier"], "#" + it["status"]]
    tagtxt = " ".join(tags) + " " + it.get("kw", "") + " " + it["author"]
    cards.append(
        f'<a class="c" href="{e(it["url"])}" target="_blank" rel="noopener">'
        f'<img src="{uri}" alt="{e(it["title"])}" loading="lazy">'
        f'<div class="t"><div class="n">{i}. {e(it["title"])}</div>'
        f'<div class="m">{e(meta_line(it))}</div>'
        f'<p>{e(it["hook"])}</p>'
        f'<span class="k">{e(tagtxt)}</span></div></a>'
    )

cats = [
    ("全部", ""),
    ("奇幻冒險", "#奇幻冒險"),
    ("懸疑推理/驚悚", "#懸疑推理"),
    ("日常家庭", "#日常家庭"),
    ("運動競技", "#運動競技"),
    ("歷史", "#歷史"),
    ("戀愛喜劇", "#戀愛喜劇"),
    ("熱血動作", "#熱血動作"),
]
row2 = [
    ("全部", ""),
    ("小眾未動畫化", "#小眾未動畫化"),
    ("人氣名作", "#人氣名作"),
    ("已完結", "#已完結"),
    ("連載中", "#連載中"),
]
cb = "".join(
    f'<button data-k="{e(k)}"{" class=on" if not k else ""}>{e(n)}</button>'
    for n, k in cats
)
pb = "".join(
    f'<button data-p="{e(k)}"{" class=on" if not k else ""}>{e(n)}</button>'
    for n, k in row2
)
CSS = '''body{margin:0;font-family:-apple-system,"PingFang TC","Noto Sans TC",sans-serif;background:#111;color:#eee}h1{font-size:22px;padding:20px 16px 4px;margin:0}.s{color:#999;padding:0 16px 12px;font-size:13px}
.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;padding:0 16px 24px}.c{background:#1c1c1c;border-radius:12px;overflow:hidden;text-decoration:none;color:inherit;display:block}
.c img{width:100%;height:200px;object-fit:cover;display:block;background:#000}.t{padding:10px 12px 14px}.n{font-weight:700;font-size:16px}.m{color:#f5a623;font-size:12px;margin:4px 0}p{margin:6px 0 0;font-size:14px;line-height:1.5;color:#ccc}.k{display:none}.f{position:sticky;top:0;z-index:5;background:#111;display:flex;flex-wrap:wrap;gap:8px;padding:10px 16px 12px;border-bottom:1px solid #222;margin-bottom:12px}.f button{background:#1c1c1c;color:#ddd;border:1px solid #333;border-radius:999px;padding:6px 14px;font-size:14px;cursor:pointer;font-family:inherit}.f button:hover{border-color:#666}.f button.on{background:#f5a623;color:#111;border-color:#f5a623;font-weight:700}.f .pr{flex-basis:100%;display:flex;flex-wrap:wrap;gap:8px}.f .pr button.on{background:#3a8f5c;border-color:#3a8f5c;color:#fff}.f .cnt{color:#888;font-size:13px;align-self:center;margin-left:4px}.c.h{display:none}.sb{flex-basis:100%;display:flex;gap:8px;margin-bottom:2px}.sb input{flex:1;min-width:0;background:#1c1c1c;color:#eee;border:1px solid #333;border-radius:10px;padding:9px 12px;font-size:16px;font-family:inherit}.sb input:focus{outline:none;border-color:#f5a623}.sb button{flex:none}#em{display:none;color:#888;text-align:center;padding:30px 16px}'''
JS = r'''(function(){var bs=document.querySelectorAll('#f button[data-k]'),ps=document.querySelectorAll('#f button[data-p]'),cs=document.querySelectorAll('.c'),cnt=document.getElementById('cnt'),q=document.getElementById('q'),em=document.getElementById('em'),cat='',pri='';
function run(){var re=cat?new RegExp(cat,'i'):null,rp=pri?new RegExp(pri,'i'):null,ts=q.value.trim().toLowerCase().split(/\s+/).filter(Boolean),n=0;
cs.forEach(function(c){var tags=c.querySelector('.k').textContent;var all=(c.querySelector('.t').textContent+' '+c.href).toLowerCase();var ok=(!re||re.test(tags))&&(!rp||rp.test(tags))&&ts.every(function(w){return all.indexOf(w)>=0});c.classList.toggle('h',!ok);if(ok)n++});
cnt.textContent=n+' 部';em.style.display=n?'none':'block';}
bs.forEach(function(b){b.addEventListener('click',function(){bs.forEach(function(x){x.classList.remove('on')});b.classList.add('on');cat=b.dataset.k;run();});});
ps.forEach(function(b){b.addEventListener('click',function(){ps.forEach(function(x){x.classList.remove('on')});b.classList.add('on');pri=b.dataset.p;run();});});
q.addEventListener('input',run);document.getElementById('qc').addEventListener('click',function(){q.value='';run();q.focus();});})();'''
H = f'''<!DOCTYPE html><html lang="zh-Hant-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>漫畫雷達推薦清單</title><style>
{CSS}</style></head>
<body><h1>漫畫雷達推薦清單</h1><div class="s">共 25 部・2026-10-09 更新・點卡片前往漫畫櫃・人氣名作與尚未動畫化的小眾作品</div><div class="f" id="f"><div class="sb"><input id="q" type="search" placeholder="搜尋作品、作者、關鍵字（例：棒球、推理、手塚）" autocomplete="off"><button id="qc" type="button">清除</button></div>{cb}<div class="pr">{pb}<span class="cnt" id="cnt">25 部</span></div></div><div id="em">找不到符合的項目</div><div class="g">{"".join(cards)}</div><script>
{JS}
</script></body></html>'''
out = ROOT / "index.html"
out.write_text(H, encoding="utf-8")
print("bytes", len(H.encode()), "covers", cover_ok, "/", len(DATA))
