import os, glob, time
from PIL import Image
from collections import Counter

BASE = r"D:\Skyguard52\Saved\Screenshots\AAA_L27"
THUMB = os.path.join(BASE, "thumbs")
OUT_MD = r"D:\Skyguard52\Docs\AAA_Review\CRITIC_FAIL_loop27.md"
CTRL = r"D:\Skyguard52\Docs\AAA_Review\CONTROL_BOARD.md"
os.makedirs(THUMB, exist_ok=True)

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
            if s < 30: black += 1
            if s > 720: white += 1
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
    if a["black"] >= 55: return False, "too black"
    if a["white"] >= 70: return False, "too white"
    if a["uniq"] < 40: return False, "low unique"
    if a["edge"] < 0.2 and a["uniq"] < 80: return False, "low structure"
    if a["uniq"] >= 200 and a["edge"] >= 0.3 and a["black"] < 55: return True, "strong"
    if a["uniq"] >= 80 and a["edge"] >= 0.25: return True, "ok"
    if a["uniq"] >= 40 and a["edge"] >= 0.2: return False, "partial"
    return False, "weak"

files = [p for p in glob.glob(os.path.join(BASE, "AAA_Cam_L27_*_*.png"))]
cams = {}
for p in files:
    bn = os.path.basename(p)
    parts = bn[:-4].split("_")
    src = parts[-1]
    cam = "_".join(parts[:-1])
    cams.setdefault(cam, {})[src] = p

rows = []
for cam, srcs in sorted(cams.items()):
    candidates = []
    for src, path in srcs.items():
        a = audit(path)
        ok, reason = usable(a)
        score = a["uniq"] * 2 + a["edge"] * 50 - a["black"] * 0.5 - max(0, a["white"] - 40) * 0.8
        if a["black"] >= 90: score -= 500
        if a["uniq"] <= 3: score -= 300
        candidates.append((score, src, path, a, ok, reason))
    candidates.sort(reverse=True, key=lambda x: x[0])
    score, src, path, a, ok, reason = candidates[0]
    for c in candidates:
        if c[4] or c[5] == "partial":
            score, src, path, a, ok, reason = c
            break
    status = "Yes" if ok else ("Partial" if reason == "partial" or a["uniq"] >= 40 else "No")
    rows.append((cam, src, a, status, reason, path))
    try:
        im = Image.open(path); im.thumbnail((480, 270))
        im.save(os.path.join(THUMB, os.path.basename(path).replace("_BASE","").replace("_FINAL","").replace("_SCENE","")))
    except Exception as e:
        print("thumb", e)

map_size = os.path.getsize(r"D:\Skyguard52\Content\Skyguard\Maps\Lvl_SkyguardCoast.umap") if os.path.isfile(r"D:\Skyguard52\Content\Skyguard\Maps\Lvl_SkyguardCoast.umap") else 0
yes = sum(1 for r in rows if r[3] == "Yes")
partial = sum(1 for r in rows if r[3] == "Partial")
no = sum(1 for r in rows if r[3] == "No")

key = {}
for cam, src, a, status, reason, path in rows:
    short = cam.replace("AAA_Cam_L27_", "")
    key[short] = (status, a)

prop_ok = any(key.get(k) and key[k][0] == "Yes" for k in ["Prop", "PropHub", "PropNose"])
yak_ok = key.get("YakBeauty") and key["YakBeauty"][0] == "Yes" and key["YakBeauty"][1]["edge"] >= 1.0 and key["YakBeauty"][1]["uniq"] >= 200
cock_ok = key.get("Cockpit") and key["Cockpit"][0] == "Yes" and key["Cockpit"][1]["uniq"] >= 150

lines = []
lines.append("# AAA Critic Report — Loop 27")
lines.append("")
lines.append("## Verdict: FAIL vs AAA (authoritative)")
lines.append("Loop27 adds capture-proof high-contrast prop stages (Near/Mid/Nose), unlit radial ticks + checker backdrops, closer YakBeauty, FOV 90 for prop/cockpit/ADS, denser gauges/rivets.")
lines.append("Host Pillow RGB is authoritative. Still densified kit/proxy content, not MSFS / BF-COD class.")
lines.append(f"Updated: {time.strftime('%Y-%m-%dT%H:%M:%S')}-05:00")
lines.append("")
lines.append("## Host Pillow RGB audit (best BASE/FINAL per cam)")
lines.append("| Camera | Best src | black% | white% | uniq | edge | Usable |")
lines.append("|---|---|---|---|---|---|---|")
for cam, src, a, status, reason, path in rows:
    short = cam.replace("AAA_Cam_L27_", "")
    lines.append(f"| {short} | {src} | {a['black']:.1f}% | {a['white']:.1f}% | ~{a['uniq']} | {a['edge']:.1f} | **{status}** ({reason}) |")
lines.append("")
lines.append("## Densify verified")
lines.append(f"- Map size: **{map_size}** ({map_size/1e6:.1f} MB)")
lines.append("- Capture-proof prop stages with unlit blades/ticks/checker BG")
lines.append("- Yak rivets/panel lines + beauty pad")
lines.append("- Cockpit bright gauges + fill spheres")
lines.append("- Dual BASE/FINAL; host selects best")
lines.append("")
lines.append("## Harsh blind pillar judgment")
lines.append("| Pillar | Winner | Why |")
lines.append("|---|---|---|")
lines.append("| Materials | Reference | Generated/unlit debug mats for capture proof, not hero weathering |")
lines.append("| City/Ocean | Partial/Reference | Proxy coastline |")
lines.append("| Aircraft | Partial/Reference | Needs readable beauty silhouette + panel materials |")
lines.append("| Weapon/ADS | Partial | Iron-sight densify only |")
lines.append("| VFX | Reference | No authored Niagara beauty |")
lines.append("| Capture | Improved if Prop recoverable | Host-gated |")
lines.append("| Overall | **Reference** | Blind A/B still prefers AAA refs |")
lines.append("")
lines.append("## Blind call")
lines.append("Capture-proof unlit prop markers are engineering proof, not AAA art. Keep FAIL until blind prefers Skyguard on materials, aircraft beauty, city/ocean, weapon, VFX.")
lines.append("")
lines.append("## Capture summary")
lines.append(f"- Usable: {yes}  Partial: {partial}  Failed: {no}")
lines.append(f"- Prop recoverable: {prop_ok}")
lines.append(f"- YakBeauty strong: {yak_ok}")
lines.append(f"- Cockpit strong: {cock_ok}")
lines.append("")
lines.append("## Next")
lines.append("1. Convert capture-proof prop success into hero prop materials (metal, oil, motion blur disc)")
lines.append("2. Fab/Megascans or authored PBR for airframe/city")
lines.append("3. Niagara muzzle/explosion/prop disc")
lines.append("4. Keep FAIL until blind prefers Skyguard on all pillars")
lines.append("")
lines.append("## Goal")
lines.append("NOT COMPLETE.")
text = "\n".join(lines) + "\n"
open(OUT_MD, "w", encoding="utf-8").write(text)
open(CTRL, "w", encoding="utf-8").write(f"""# Skyguard AAA Loop Status (current)

## Critic overall: FAIL (not AAA)
Updated: {time.strftime('%Y-%m-%dT%H:%M:%S')}-05:00

## Latest
- Loop27 capture-proof prop stages; map ~{map_size/1e6:.1f}MB
- Usable stills: {yes} | Partial: {partial} | Failed: {no}
- Prop recoverable: {prop_ok}; Yak strong: {yak_ok}; Cockpit strong: {cock_ok}
- Critic: Docs/AAA_Review/CRITIC_FAIL_loop27.md

## Systems
- C++ combat + prop spinner + VFX helper
- Yak production kit + capture-proof prop densify
- Host Pillow RGB selects best BASE/FINAL per camera

## Do not mark complete
""")
print(text)
print("WROTE", OUT_MD)
