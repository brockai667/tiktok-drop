# -*- coding: utf-8 -*-
"""Vygeneruje TikTok Drop board (tiktok_drop.html) z tiktok_drop.json.
Re-runnable: ked pribudnu nove videa, len znova spusti."""
import html, json, re

DATA = json.load(open("tiktok_drop.json", encoding="utf-8"))
ACCENT = {"coldcasedaily667": "#ff4d5e", "UnexplainedDaily": "#a988ff", "MotivationFactory": "#ffb03a"}
SONGS = {
    "coldcasedaily667": [("E85", "Don Toliver", "temný trap ambient"),
                          ("Raindance", "Dave ft. Tems", "napäté, atmosferické")],
    "UnexplainedDaily": [("E85", "Don Toliver", "mysteriózny ambient"),
                          ("Fate of Ophelia", "Taylor Swift", "trending background")],
    "MotivationFactory": [("I Just Might", "Bruno Mars", "uplift, lifestyle"),
                           ("PRESSURE!", "Nyck Caution", "tvrdá motivácia")],
}
HANDLES = {"coldcasedaily667": "coldcasedaily667", "UnexplainedDaily": "unexplained_daily",
           "MotivationFactory": "disciplinedaily667"}
# QC „ocko" — nacitaj metriky (jas/ostrost/dlzka) a urob verdikt
try:
    QC = {r.get("file"): r for r in json.load(open("qc_raw.json", encoding="utf-8"))}
except Exception:
    QC = {}
def verdict(fname):
    m = QC.get(fname)
    if not m or "err" in m:
        return ("na", "", "")
    d, ba, bmin, sa = m["dur"], m["b_avg"], m["b_min"], m["s_avg"]
    tip = f"jas {ba} · ostrosť {sa} · {d}s"
    flags = []
    if d < 12: flags.append(f"krátke {d}s")
    if d > 60: flags.append(f"dlhé {d}s")
    if bmin < 4: flags.append("čierny frame")
    if ba < 20: flags.append("veľmi tmavé")
    if sa < 95: flags.append("mäkký obraz")
    if flags:
        return ("warn", "Pozri: " + ", ".join(flags), tip)
    if sa >= 200 and 15 <= d <= 28 and bmin >= 8:
        return ("star", "Silný vizuál", tip)
    return ("ok", "OK", tip)
def esc(s): return html.escape(str(s or ""))
def clean(d):
    d = str(d or "")
    if d.startswith("\U0001F4CD") and "N/A" in d.split(".")[0]:
        d = d.split(". ", 1)[1] if ". " in d else d
    return d.strip()

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0c0d11; --surf:#14161d; --surf2:#1a1d27; --line:#282c38;
  --tx:#edeff5; --mut:#98a0b3; --mut2:#5c6377; --accent:#35d3e0;
  --r:14px; --maxw:1180px;
}
html{scroll-behavior:smooth}
body{background:radial-gradient(1200px 600px at 50% -10%,#161a26 0%,var(--bg) 55%);
  color:var(--tx);font-family:"SF Pro Text",-apple-system,"Segoe UI",system-ui,sans-serif;
  line-height:1.5;-webkit-font-smoothing:antialiased;padding:0 20px 80px}
.wrap{max-width:var(--maxw);margin:0 auto}
.disp{font-family:"SF Pro Display",-apple-system,"Segoe UI",system-ui,sans-serif;font-weight:800;letter-spacing:-.02em;text-wrap:balance}
.eyebrow{font-size:11px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--mut2)}

/* header */
header{padding:56px 0 30px;text-align:center;border-bottom:1px solid var(--line);margin-bottom:34px}
header h1{font-size:clamp(38px,7vw,68px);line-height:.98;background:linear-gradient(180deg,#fff, #b8bece);
  -webkit-background-clip:text;background-clip:text;color:transparent}
header .sub{color:var(--mut);margin-top:14px;font-size:16px;max-width:56ch;margin-left:auto;margin-right:auto}
.pill{display:inline-flex;gap:8px;align-items:center;background:var(--surf);border:1px solid var(--line);
  border-radius:999px;padding:6px 14px;font-size:12.5px;color:var(--mut);margin-top:20px}
.pill b{color:var(--accent);font-weight:700}

/* how-to steps */
.how{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin:0 0 20px}
.step{background:var(--surf);border:1px solid var(--line);border-radius:var(--r);padding:16px 18px;position:relative}
.step .n{font-family:"SF Pro Display",system-ui;font-weight:800;font-size:13px;color:var(--accent);letter-spacing:.02em}
.step h3{font-size:14.5px;font-weight:700;margin:6px 0 3px}
.step p{font-size:13px;color:var(--mut)}
.note{background:linear-gradient(180deg,var(--surf),var(--surf2));border:1px solid var(--line);border-left:3px solid var(--accent);
  border-radius:12px;padding:15px 18px;font-size:13.5px;color:var(--mut);margin-bottom:44px}
.note b{color:var(--tx)}
.legend{display:flex;flex-wrap:wrap;align-items:center;gap:8px;font-size:12.5px;color:var(--mut);
  background:var(--surf);border:1px solid var(--line);border-radius:12px;padding:12px 16px;margin-bottom:44px}
.legend .eye{font-size:10.5px;padding:2px 8px}

/* section */
section{margin-bottom:52px;scroll-margin-top:20px}
.shead{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;padding-bottom:16px;margin-bottom:22px;
  border-bottom:1px solid var(--line)}
.dot{width:11px;height:11px;border-radius:3px;flex:none;transform:translateY(1px)}
.shead h2{font-size:26px}
.shead .cnt{color:var(--mut2);font-size:13px;font-variant-numeric:tabular-nums}
.acct{font-size:13px;color:var(--tx);background:color-mix(in srgb,var(--acc) 14%,transparent);
  border:1px solid color-mix(in srgb,var(--acc) 45%,transparent);border-radius:999px;padding:4px 12px}
.acct b{color:var(--acc);font-weight:700}
.songs{display:flex;gap:10px;flex-wrap:wrap;margin-left:auto}
.song{display:flex;flex-direction:column;background:var(--surf);border:1px solid var(--line);border-radius:10px;
  padding:8px 13px;min-width:0}
.song .t{font-size:13px;font-weight:600}.song .a{font-size:11.5px;color:var(--mut2)}
.song .v{font-size:10.5px;color:var(--acc);letter-spacing:.02em;margin-top:2px}

/* cards */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:18px}
.card{background:var(--surf);border:1px solid var(--line);border-radius:var(--r);padding:18px;display:flex;flex-direction:column;gap:13px;
  transition:border-color .18s,transform .18s}
.card:hover{border-color:var(--acc);transform:translateY(-2px)}
.card .top{display:flex;justify-content:space-between;align-items:center;gap:10px}
.card .top{align-items:center}
.card .meta{font-size:11px;color:var(--mut2);font-variant-numeric:tabular-nums;letter-spacing:.02em}
.eye{display:inline-flex;align-items:center;gap:5px;font-size:11.5px;font-weight:700;border-radius:999px;padding:3px 10px;white-space:nowrap}
.eye.star{background:rgba(255,209,102,.16);color:#ffd166;border:1px solid rgba(255,209,102,.42)}
.eye.ok{background:rgba(125,211,168,.13);color:#7dd3a8;border:1px solid rgba(125,211,168,.3)}
.eye.warn{background:rgba(255,138,76,.16);color:#ff9a52;border:1px solid rgba(255,138,76,.42)}
.card h4{font-size:17px;font-weight:700;line-height:1.25;letter-spacing:-.01em}
.cap{background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:12px;font-size:13px;color:var(--mut);
  max-height:132px;overflow:auto}
.cap .tags{color:var(--acc);margin-top:8px;display:block;font-weight:500}
.row{display:flex;gap:9px;margin-top:auto}
.btn{flex:1;display:inline-flex;align-items:center;justify-content:center;gap:7px;border-radius:10px;padding:11px 12px;
  font-size:13.5px;font-weight:700;cursor:pointer;border:1px solid transparent;text-decoration:none;transition:filter .15s,background .15s;font-family:inherit}
.btn.dl{background:var(--acc);color:#0b0c10}
.btn.dl:hover{filter:brightness(1.08)}
.btn.cp{background:transparent;border-color:var(--line);color:var(--tx);flex:0 0 auto;padding:11px 15px}
.btn.cp:hover{border-color:var(--acc);color:var(--acc)}
.btn.cp.done{color:var(--acc);border-color:var(--acc)}
a.btn:focus-visible,button.btn:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
footer{color:var(--mut2);font-size:12.5px;text-align:center;border-top:1px solid var(--line);padding-top:26px;max-width:64ch;margin:0 auto}
@media (prefers-reduced-motion:reduce){*{transition:none!important}html{scroll-behavior:auto}}
@media(max-width:560px){.songs{margin-left:0;width:100%}header{padding:40px 0 24px}}
"""

def card_html(v, acc):
    cap = clean(v["desc"])
    tags = " ".join(v.get("hashtags", [])[:8])
    full = cap + "\n\n" + tags
    return f"""
    <article class="card" style="--acc:{acc}">
      <div class="top"><span class="eyebrow">{esc(v['created'])}</span><span class="meta">{v['size_mb']} MB · 9:16</span></div>
      <h4>{esc(v['title'])}</h4>
      <div class="cap">{esc(cap)}<span class="tags">{esc(tags)}</span></div>
      <div class="row">
        <a class="btn dl" href="{esc(v['url'])}" download>&#8595; Stiahnuť</a>
        <button class="btn cp" data-cap="{esc(full)}" aria-label="Kopírovať popis">Kopírovať popis</button>
      </div>
    </article>"""

sections = []
navs = []
total = 0
for repo, blk in DATA.items():
    acc = ACCENT.get(repo, "#35d3e0")
    # auto-filter: vyhoď technicky zlé videá (čierny frame / mäkký obraz / zlá dĺžka), potom max 6
    vids = [v for v in blk["videos"] if verdict(v["file"])[0] != "warn"][:6]
    total += len(vids)
    songs = "".join(
        f'<div class="song" style="--acc:{acc}"><span class="t">&#9834; {esc(t)}</span><span class="a">{esc(a)}</span><span class="v">{esc(vibe)}</span></div>'
        for t, a, vibe in SONGS.get(repo, []))
    cards = "".join(card_html(v, acc) for v in vids)
    handle = HANDLES.get(repo, repo)
    sections.append(f"""
    <section id="{esc(repo)}" style="--acc:{acc}">
      <div class="shead">
        <span class="dot" style="background:{acc}"></span>
        <h2 class="disp">{esc(blk['label'])}</h2>
        <span class="acct" style="--acc:{acc}">postuj na &rarr; <b>@{esc(handle)}</b></span>
        <span class="cnt">{len(vids)} videí</span>
        <div class="songs">{songs}</div>
      </div>
      <div class="grid">{cards}</div>
    </section>""")
    navs.append(f'<a href="#{esc(repo)}" style="color:{acc}">{esc(blk["label"])}</a>')

HTML = f"""<style>{CSS}</style>
<div class="wrap">
<header>
  <span class="eyebrow">Native TikTok · denný drop</span>
  <h1 class="disp">TikTok Drop</h1>
  <p class="sub">Stiahni → nahraj natívne v TikTok appke → vlož popis → pridaj trending zvuk potichu. Natívny upload = oveľa väčší dosah než auto-post.</p>
  <div class="pill">Auto-post cez Buffer je <b>vypnutý</b> na týchto 3 účtoch — žiadne duplicity</div>
</header>

<div class="how">
  <div class="step"><div class="n">01</div><h3>Stiahni video</h3><p>Klikni „Stiahnuť" — MP4 9:16 pripravené na TikTok.</p></div>
  <div class="step"><div class="n">02</div><h3>Nahraj natívne</h3><p>V TikTok appke z telefónu (nie cez plánovač) — to je celý trik.</p></div>
  <div class="step"><div class="n">03</div><h3>Vlož popis</h3><p>„Kopírovať popis" → vlož do TikToku. Hotové hashtagy.</p></div>
  <div class="step"><div class="n">04</div><h3>Pridaj zvuk</h3><p>Add sound → trending pesnička (dole) na <b>~8–12 %</b> hlasitosti pod voiceover.</p></div>
</div>

<div class="note"><b>Prečo trending zvuk potichu:</b> voiceover musí ostať čitateľný, ale TikTok algoritmus boostuje videá čo používajú trending sound. Nastav zvuk na ~10 % hlasitosti. Nájdeš ich v appke: <b>Add sound → hľadaj názov nižšie</b>, alebo prezeraj <b>Trending</b> a ber tie so šípkou &#8599;. Pre komerčný obsah použi zvuky z TikTok <b>Commercial Music Library</b>.</div>

<div class="note" style="--accent:#7dd3a8;border-left-color:#7dd3a8"><b>Prihlásenie (bezpečne, raz):</b> každá sekcia nižšie hovorí <b>na ktorý účet</b> postovať. V TikTok appke sa <b>prihlás do všetkých 3 účtov raz</b> (Profil → meno hore → <b>Pridať účet</b>) a potom už len <b>prepínaj účty</b> — žiadne heslá kopírovať netreba. Prihlasovacie údaje si nechaj v správcovi hesiel telefónu (iCloud/Google), ten ich vyplní. <i>Heslá zámerne nedávam na túto stránku — plaintext heslá na webe = riziko úniku účtu.</i></div>

{''.join(sections)}

<footer>Toto sú tvoje živé videá (bežia aj na YouTube/IG). Board sa dá kedykoľvek pregenerovať s novými. Chceš iný niche alebo iné pesničky — povedz.</footer>
</div>
<script>
document.querySelectorAll('.btn.cp').forEach(function(b){{
  b.addEventListener('click',function(){{
    var t=b.getAttribute('data-cap');
    navigator.clipboard.writeText(t).then(function(){{
      var o=b.textContent;b.textContent='Skopírované \\u2713';b.classList.add('done');
      setTimeout(function(){{b.textContent=o;b.classList.remove('done');}},1600);
    }});
  }});
}});
</script>"""

open("tiktok_drop.html", "w", encoding="utf-8").write(HTML)
print(f"tiktok_drop.html hotovy: {total} videi, {len(DATA)} nikov")
