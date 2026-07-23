# -*- coding: utf-8 -*-
"""Video QC „ocko": stiahne kazde video, vzorkuje ~8 framov cez cely timeline,
zmeria jas + ostrost (Laplacian) + dlzku -> verdikt ok/warn + dovod. Kalibracne
prints (b_avg/b_min/s_avg) nech nastavim prahy tak, aby normalne presli."""
import cv2, numpy as np, json, os, tempfile, urllib.request
DATA = json.load(open("tiktok_drop.json", encoding="utf-8"))

def measure(url):
    tmp = tempfile.mktemp(suffix=".mp4")
    try:
        urllib.request.urlretrieve(url, tmp)
    except Exception as e:
        return {"err": str(e)[:60]}
    cap = cv2.VideoCapture(tmp)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    dur = n / fps if fps else 0
    idxs = [int(n * p) for p in (0.05, 0.15, 0.28, 0.42, 0.55, 0.68, 0.82, 0.94)] if n > 0 else []
    br, sh = [], []
    for i in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, fr = cap.read()
        if not ok:
            continue
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        br.append(float(g.mean()))
        sh.append(float(cv2.Laplacian(g, cv2.CV_64F).var()))
    cap.release()
    try: os.remove(tmp)
    except Exception: pass
    if not br:
        return {"err": "no frames"}
    return {"dur": round(dur), "b_avg": round(float(np.mean(br))), "b_min": round(float(min(br))),
            "s_avg": round(float(np.mean(sh))), "s_min": round(float(min(sh)))}

rows = []
for repo, blk in DATA.items():
    for v in blk["videos"]:
        m = measure(v["url"])
        m["title"] = v["title"][:36]; m["repo"] = repo; m["file"] = v["file"]
        rows.append(m)
        print(f"{repo[:13]:13} {str(m.get('dur','?')):>4}s  b{str(m.get('b_avg','?')):>4}/{str(m.get('b_min','?')):>4}  "
              f"s{str(m.get('s_avg','?')):>6}/{str(m.get('s_min','?')):>5}  {m.get('err','') or m['title']}")
json.dump(rows, open("qc_raw.json", "w"), indent=1)
print("-> qc_raw.json (", len(rows), "videi )")
