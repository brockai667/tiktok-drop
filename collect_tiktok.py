# -*- coding: utf-8 -*-
"""Pozbiera najnovsie hotove videa (GitHub Release 'media') + ich popis/hashtagy
(z committed scripts/auto_<slug>.json) pre 3 TikTok niky -> JSON pre download-page."""
import base64, json, os, subprocess, urllib.request, urllib.error
OWNER="brockai667"
NICHES={"coldcasedaily667":"True Crime","UnexplainedDaily":"Unsolved Mysteries","MotivationFactory":"Motivation"}
def tok():
    t=(os.environ.get("GITHUB_TOKEN") or "").strip()   # GitHub Action
    if t: return t
    p=subprocess.run(["git","credential","fill"],input="protocol=https\nhost=github.com\n\n",
        capture_output=True,text=True)                  # lokalny fallback
    for l in p.stdout.splitlines():
        if l.startswith("password="): return l[9:]
    return ""
TOK=tok()
def api(path):
    req=urllib.request.Request("https://api.github.com"+path,
        headers={"Authorization":"Bearer "+TOK,"Accept":"application/vnd.github+json","User-Agent":"a"})
    try: return json.loads(urllib.request.urlopen(req,timeout=40).read())
    except urllib.error.HTTPError as e: return {"__error__":e.code}
def spec(repo,slug):
    c=api(f"/repos/{OWNER}/{repo}/contents/scripts/auto_{slug}.json")
    if isinstance(c,dict) and c.get("content"):
        try: return json.loads(base64.b64decode(c["content"]).decode("utf-8","replace"))
        except Exception: return {}
    return {}
def cfg(repo):
    c=api(f"/repos/{OWNER}/{repo}/contents/config.example.json")
    if isinstance(c,dict) and c.get("content"):
        try: return json.loads(base64.b64decode(c["content"]).decode("utf-8","replace"))
        except Exception: return {}
    return {}
out={}
for repo,label in NICHES.items():
    rel=api(f"/repos/{OWNER}/{repo}/releases/tags/media")
    assets=rel.get("assets",[]) if isinstance(rel,dict) else []
    assets=[a for a in assets if a["name"].endswith(".mp4")]
    assets.sort(key=lambda a:a.get("created_at",""),reverse=True)
    c=cfg(repo); bh=c.get("brand_hashtags",[]); cta=c.get("brand_cta","")
    vids=[]
    for a in assets[:8]:   # headroom — build vyfiltruje technicky zlé, zobrazí max 6
        slug=a["name"][:-4]
        sp=spec(repo,slug)
        title=sp.get("title") or slug.replace("_"," ").title()
        desc=sp.get("description","")
        htags=sp.get("hashtags",[]) or bh
        vids.append({"title":title,"file":a["name"],"url":a["browser_download_url"],
                     "size_mb":round(a.get("size",0)/1048576,1),"desc":desc,
                     "hashtags":htags,"created":a.get("created_at","")[:10]})
    out[repo]={"label":label,"cta":cta,"brand_hashtags":bh,"videos":vids}
    print(f"{repo} ({label}): {len(vids)} videi, najnovsie {vids[0]['created'] if vids else '-'}")
json.dump(out,open("tiktok_drop.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
print("-> tiktok_drop.json")
# ukazka prveho
if out:
    r0=list(out)[0]; v0=out[r0]["videos"][0] if out[r0]["videos"] else None
    if v0: print("\nUKAZKA:",v0["title"],"\n ",v0["url"],"\n ",v0["desc"][:120],"\n ",v0["hashtags"][:6])
