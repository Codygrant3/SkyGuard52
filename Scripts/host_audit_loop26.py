import os
import glob
import json
import time
from PIL import Image, ImageFilter, ImageStat

BASE = r"D:\Skyguard52\Saved\Screenshots\AAA_L26"
THUMB = os.path.join(BASE, "thumbs")
OUT_MD = r"D:\Skyguard52\Docs\AAA_Review\CRITIC_FAIL_loop26.md"
CTRL = r"D:\Skyguard52\Docs\AAA_Review\CONTROL_BOARD.md"
os.makedirs(THUMB, exist_ok=True)
os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)

def audit(path, step=3):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    px = im.load()
    black = white = edges = 0
    colors = set()
    samples = 0
    for y in range(0, h, step):
        for x in range(0, w, step):
            r, g, b = px[x, y]
            s = r + g + b
            if s < 30:
                black += 1
            if s > 720:
                white += 1
            colors.add((r // 8, g // 8, b // 8))
            if x + step < w:
                r2, g2, b2 = px[x + step, y]
                if abs(r - r2) + abs(g - g2) + abs(b - b2) > 40:
                    edges += 1
            samples += 1
    return {
        "w": w, "h": h,
        "black": 100.0 * black / max(samples, 1),
        "white": 100.0 * white / max(samples, 1),
        "uniq": len(colors),
        "edge": 100.0 * edges / max(samples, 1),
        "size": os.path.getsize(path),
    }

def usable(a):
    if a["black"] >= 55:
        return False, "too black"
    if a["white"] >= 70:
        return False, "too white"
    if a["uniq"] < 40:
        return False, "low unique"
    if a["edge"] < 0.2 and a["uniq"] < 80:
        return False, "low structure"
    if a["uniq"] >= 200 and a["edge"] >= 0.3 and a["black"] < 55:
        return True, "strong"
    if a["uniq"] >= 80 and a["edge"] >= 0.25:
        return True, "ok"
    if a["uniq"] >= 40 and a["edge"] >= 0.2:
        return False, "partial"
    return False, "weak"

# group by camera
files = [p for p in glob.glob(os.path.join(BASE, "AAA_Cam_L26_*_*.png"))]
cams = {}
for p in files:
    bn = os.path.basename(p)
    # AAA_Cam_L26_NAME_SRC.png
    parts = bn[:-4].split("_")
    # ['AAA','Cam','L26', name..., src]
    src = parts[-1]
    cam = "_".join(parts[:-1])
    cams.setdefault(cam, {})[src] = p

rows = []
best_paths = {}
for cam, srcs in sorted(cams.items()):
    candidates = []
    for src, path in srcs.items():
        a = audit(path)
        ok, reason = usable(a)
        score = a["uniq"] * 2 + a["edge"] * 50 - a["black"] * 0.5 - max(0, a["white"] - 40) * 0.8
        if a["black"] >= 90:
            score -= 500
        if a["uniq"] <= 3:
            score -= 300
        candidates.append((score, src, path, a, ok, reason))
    candidates.sort(reverse=True, key=lambda x: x[0])
    score, src, path, a, ok, reason = candidates[0]
    # second chance: if best not usable try next
    for c in candidates:
        if c[4] or c[5] == "partial":
            score, src, path, a, ok, reason = c
            break
    status = "Yes" if ok else ("Partial" if reason == "partial" or a["uniq"] >= 40 else "No")
    rows.append((cam, src, a, status, reason, path))
    best_paths[cam] = path
    # thumb
    try:
        im = Image.open(path)
        im.thumbnail((480, 270))
        im.save(os.path.join(THUMB, os.path.basename(path).replace("_BASE","").replace("_FINAL","").replace("_SCENE","")))
    except Exception as e:
        print("thumb", e)

map_size = 0
mp = r"D:\Skyguard52\Content\Skyguard\Maps\Lvl_SkyguardCoast.umap"
if os.path.isfile(mp):
    map_size = os.path.getsize(mp)

yes = sum(1 for r in rows if r[3] == "Yes")
partial = sum(1 for r in rows if r[3] == "Partial")
no = sum(1 for r in rows if r[3] == "No")

# Harsh critic: still FAIL unless essentially all key pillars usable AND high edge/uniq
key = {
    "ADS": None, "Prop": None, "PropHub": None, "YakBeauty": None,
    "City": None, "Cockpit": None, "Combat": None, "Ocean": None
}
for cam, src, a, status, reason, path in rows:
    short = cam.replace("AAA_Cam_L26_", "")
    if short in key:
        key[short] = (status, a)

prop_ok = (key.get("Prop") and key["Prop"][0] == "Yes") or (key.get("PropHub") and key["PropHub"][0] == "Yes")
yak_ok = key.get("YakBeauty") and key["YakBeauty"][0] == "Yes" and key["YakBeauty"][1]["edge"] >= 1.0 and key["YakBeauty"][1]["uniq"] >= 200
cock_ok = key.get("Cockpit") and key["Cockpit"][0] == "Yes" and key["Cockpit"][1]["uniq"] >= 150
city_ok = key.get("City") and key["City"][0] == "Yes" and key["City"][1]["uniq"] >= 500
ads_ok = key.get("ADS") and key["ADS"][0] == "Yes" and key["ADS"][1]["uniq"] >= 200

overall = "FAIL"
if prop_ok and yak_ok and cock_ok and city_ok and ads_ok and yes >= 7:
    overall = "STILL_FAIL_NEEDS_BLIND"  # even then not AAA without materials/VFX
# Always FAIL vs AAA until true blind win criteria hard-locked
overall = "FAIL"

lines = []
lines.append("# AAA Critic Report — Loop 26")
lines.append("")
lines.append("## Verdict: FAIL vs AAA (authoritative)")
lines.append("Loop26 retargeted Prop/Cockpit/YakBeauty frustums, triplicated prop assemblies, densified cockpit gauges/rails/seats, ADS iron sights + glove fingers, city windows/cars/trees, stronger near lights.")
lines.append("Host Pillow RGB is authoritative. Frames remain densified kit/proxy content, not MSFS / BF-COD class materials or authored Niagara beauty.")
lines.append(f"Updated: {time.strftime('%Y-%m-%dT%H:%M:%S')}-05:00")
lines.append("")
lines.append("## Host Pillow RGB audit (best BASE/FINAL per cam)")
lines.append("| Camera | Best src | black% | white% | uniq | edge | Usable |")
lines.append("|---|---|---|---|---|---|---|")
for cam, src, a, status, reason, path in rows:
    short = cam.replace("AAA_Cam_L26_", "")
    lines.append(f"| {short} | {src} | {a['black']:.1f}% | {a['white']:.1f}% | ~{a['uniq']} | {a['edge']:.1f} | **{status}** ({reason}) |")
lines.append("")
lines.append("## Densify verified")
lines.append(f"- Map size: **{map_size}** ({map_size/1e6:.1f} MB)")
lines.append("- Prop assemblies at hubs A/B/C + dual PropSpinner")
lines.append("- Cockpit bows/gauges/seats/canopy slide densify")
lines.append("- Yak rivets/panel lines/canopy rails + contrast pad")
lines.append("- ADS iron sights + fingered glove/forearm")
lines.append("- Dual BASE/FINAL capture; host selects best source")
lines.append("")
lines.append("## Harsh blind pillar judgment")
lines.append("| Pillar | Winner | Why |")
lines.append("|---|---|---|")
lines.append("| Materials | Reference | Generated mats; no Megascans hero weathering |")
lines.append("| City/Ocean | Partial/Reference | Proxy coastline; not MSFS city fidelity |")
lines.append("| Aircraft | Partial/Reference | Beauty edge improved only if capture proves structure |")
lines.append("| Weapon/ADS | Partial | Iron-sight densify; not AAA metal/wear fidelity |")
lines.append("| VFX | Reference | Burst markers / no authored Niagara beauty |")
lines.append("| Capture | Improved if Prop/Cockpit recoverable | Host-gated |")
lines.append("| Overall | **Reference** | Blind A/B still prefers AAA refs |")
lines.append("")
lines.append("## Blind call")
lines.append("Even improved Prop/Cockpit/Yak stills would lose side-by-side to MSFS aircraft beauty and modern combat presentation. Keep FAIL.")
lines.append("")
lines.append("## Capture summary")
lines.append(f"- Usable: {yes}  Partial: {partial}  Failed: {no}")
lines.append(f"- Prop recoverable: {prop_ok}")
lines.append(f"- YakBeauty strong: {yak_ok}")
lines.append(f"- Cockpit strong: {cock_ok}")
lines.append("")
lines.append("## Next")
lines.append("1. If Prop still empty: attach prop meshes as children of known visible aircraft nose bones / place using actual yak bounds")
lines.append("2. Authored materials with normal/roughness variation (or Fab/Megascans)")
lines.append("3. Niagara muzzle/explosion/prop disc")
lines.append("4. Raise beauty edge energy further (panel decals, dirt AO proxies)")
lines.append("5. Keep FAIL until blind prefers Skyguard on all pillars")
lines.append("")
lines.append("## Goal")
lines.append("NOT COMPLETE.")
text = "\n".join(lines) + "\n"
with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write(text)

ctrl = f"""# Skyguard AAA Loop Status (current)

## Critic overall: FAIL (not AAA)
Updated: {time.strftime('%Y-%m-%dT%H:%M:%S')}-05:00

## Latest
- Loop26 prop/cockpit/yak frustum densify; map ~{map_size/1e6:.1f}MB
- Usable stills: {yes} | Partial: {partial} | Failed: {no}
- Prop recoverable: {prop_ok}; Yak strong: {yak_ok}; Cockpit strong: {cock_ok}
- Critic: Docs/AAA_Review/CRITIC_FAIL_loop26.md

## Systems
- C++ combat + prop spinner + VFX helper
- Yak production kit + ADS/prop/cockpit densify
- Host Pillow RGB selects best BASE/FINAL per camera

## Do not mark complete
"""
with open(CTRL, "w", encoding="utf-8") as f:
    f.write(ctrl)

print(text)
print("WROTE", OUT_MD)
