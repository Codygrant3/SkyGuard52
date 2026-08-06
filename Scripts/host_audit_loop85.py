import os, glob, time, hashlib, re, tempfile
from PIL import Image

BASE = r"D:\Skyguard52\Saved\Screenshots\AAA_L85"
THUMB = os.path.join(BASE, "thumbs")
OUT_MD = r"D:\Skyguard52\Docs\AAA_Review\CRITIC_FAIL_loop85.md"
CTRL = r"D:\Skyguard52\Docs\AAA_Review\CONTROL_BOARD.md"
os.makedirs(THUMB, exist_ok=True)

EXPECTED_CAMS = (
    "ADS", "City", "Cockpit", "Combat", "Harbor", "Ocean",
    "Prop", "PropHub", "PropNose", "Wide", "YakBeauty",
)
EXPECTED_SOURCES = ("BASE", "FINAL", "SCENE")
EXPECTED_SIZE = (1920, 1080)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def validate_capture_set():
    expected = {
        f"AAA_Cam_L85_{cam}_{source}.png"
        for cam in EXPECTED_CAMS
        for source in EXPECTED_SOURCES
    }
    actual_paths = glob.glob(os.path.join(BASE, "AAA_Cam_L85_*_*.png"))
    actual = {os.path.basename(path) for path in actual_paths}
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing or unexpected:
        raise RuntimeError(
            f"capture set mismatch: missing={missing} unexpected={unexpected}"
        )

    for path in actual_paths:
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                if image.size != EXPECTED_SIZE:
                    raise RuntimeError(
                        f"unexpected dimensions for {os.path.basename(path)}: "
                        f"{image.size}, expected {EXPECTED_SIZE}"
                    )
                image.convert("RGB")
        except Exception as exc:
            raise RuntimeError(f"invalid capture {path}: {exc}") from exc

    manifest_path = os.path.join(BASE, "MANIFEST_SHA256.txt")
    if not os.path.isfile(manifest_path):
        raise RuntimeError(f"manifest missing: {manifest_path}")
    if os.path.getmtime(manifest_path) + 2.0 < max(
        os.path.getmtime(path) for path in actual_paths
    ):
        raise RuntimeError("manifest predates one or more captures")

    manifest_pattern = re.compile(
        r"^([0-9a-f]{64})\s+(\d+)\s+src=(BASE|FINAL|SCENE)\s+"
        r"cam=(AAA_Cam_L85_[A-Za-z0-9]+)\s+(.+\.png)$"
    )
    manifest_entries = {}
    with open(manifest_path, "r", encoding="utf-8") as stream:
        for raw_line in stream:
            match = manifest_pattern.match(raw_line.strip())
            if not match:
                continue
            digest, size_text, source, camera, stored_path = match.groups()
            name = os.path.basename(stored_path)
            if name in manifest_entries:
                raise RuntimeError(f"duplicate manifest entry: {name}")
            manifest_entries[name] = (digest, int(size_text), source, camera)

    if set(manifest_entries) != expected:
        missing_manifest = sorted(expected - set(manifest_entries))
        extra_manifest = sorted(set(manifest_entries) - expected)
        raise RuntimeError(
            "manifest set mismatch: "
            f"missing={missing_manifest} unexpected={extra_manifest}"
        )

    for name in sorted(expected):
        path = os.path.join(BASE, name)
        digest, declared_size, source, camera = manifest_entries[name]
        if declared_size != os.path.getsize(path):
            raise RuntimeError(f"manifest size mismatch: {name}")
        if source != name[:-4].split("_")[-1]:
            raise RuntimeError(f"manifest source mismatch: {name}")
        expected_camera = name[: -(len(source) + 5)]
        if camera != expected_camera:
            raise RuntimeError(f"manifest camera mismatch: {name}")
        actual_digest = sha256_file(path)
        if digest != actual_digest:
            raise RuntimeError(f"manifest hash mismatch: {name}")

    return {
        "camera_count": len(EXPECTED_CAMS),
        "source_count": len(actual_paths),
        "manifest_count": len(manifest_entries),
    }

def atomic_write(path, text):
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=os.path.basename(path) + ".",
        suffix=".tmp",
        dir=directory,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise

capture_gate = validate_capture_set()

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

files = [p for p in glob.glob(os.path.join(BASE, "AAA_Cam_L85_*_*.png"))]
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
        if os.path.getsize(path) < 1000:
            continue
        a = audit(path)
        ok, reason = usable(a)
        score = a["uniq"] * 2 + a["edge"] * 50 - a["black"] * 0.5 - max(0, a["white"] - 40) * 0.8
        if a["black"] >= 90: score -= 500
        if a["uniq"] <= 3: score -= 300
        candidates.append((score, src, path, a, ok, reason))
    if not candidates:
        continue
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
        tname = os.path.basename(path)
        for s in ["_BASE","_FINAL","_SCENE","_DEFAULT"]:
            tname = tname.replace(s, "")
        im.save(os.path.join(THUMB, tname))
    except Exception as e:
        print("thumb", e)

map_path = r"D:\Skyguard52\Content\Skyguard\Maps\Lvl_SkyguardCoast.umap"
map_size = os.path.getsize(map_path) if os.path.isfile(map_path) else 0
yes = sum(1 for r in rows if r[3] == "Yes")
partial = sum(1 for r in rows if r[3] == "Partial")
no = sum(1 for r in rows if r[3] == "No")
key = {}
for cam, src, a, status, reason, path in rows:
    key[cam.replace("AAA_Cam_L85_", "")] = (status, a)

prop_ok = any(key.get(k) and key[k][0] == "Yes" for k in ["Prop", "PropHub", "PropNose"])
yak_ok = key.get("YakBeauty") and key["YakBeauty"][0] == "Yes" and key["YakBeauty"][1]["edge"] >= 1.0 and key["YakBeauty"][1]["uniq"] >= 200
cock_ok = key.get("Cockpit") and key["Cockpit"][0] == "Yes" and key["Cockpit"][1]["uniq"] >= 150
city_ok = key.get("City") and key["City"][0] == "Yes"
ads_ok = key.get("ADS") and key["ADS"][0] in ("Yes", "Partial")

# Still always FAIL vs true AAA until materials/VFX blind win
lines = [
"# AAA Critic Report — Loop 85",
"",
"## Verdict: FAIL vs AAA (authoritative)",
"Loop85 uses yaw=0 (+X) cameras aimed into high-frequency checker boards and radial prop proxies with alternating unlit/PBR mats, plus triple-source capture (BASE/FINAL/SCENE when available).",
"Host Pillow RGB is authoritative. Even if Prop/Yak capture recovers, content remains densified kit/proxy — not MSFS / BF-COD class materials or authored Niagara beauty.",
f"Updated: {time.strftime('%Y-%m-%dT%H:%M:%S')}-05:00",
"",
"## Host Pillow RGB audit (best source per cam)",
"| Camera | Best src | black% | white% | uniq | edge | Usable |",
"|---|---|---|---|---|---|---|",
]
for cam, src, a, status, reason, path in rows:
    short = cam.replace("AAA_Cam_L85_", "")
    lines.append(f"| {short} | {src} | {a['black']:.1f}% | {a['white']:.1f}% | ~{a['uniq']} | {a['edge']:.1f} | **{status}** ({reason}) |")
lines += [
"",
"## Densify verified",
f"- Map size: **{map_size}** ({map_size/1e6:.1f} MB)",
"- HF frustum boards for Prop/PropHub/PropNose/YakBeauty/Cockpit/ADS",
"- Yak production kit at beauty board",
"- Triple-source capture when engine supports it",
"",
"## Harsh blind pillar judgment",
"| Pillar | Winner | Why |",
"|---|---|---|",
"| Materials | Reference | Unlit/debug + generated mats; no Megascans hero weathering |",
"| City/Ocean | Partial/Reference | Proxy coastline fidelity |",
"| Aircraft | Partial/Reference | Beauty depends on capture structure; not MSFS panel fidelity |",
"| Weapon/ADS | Partial | Sight densify only |",
"| VFX | Reference | Burst markers / no authored Niagara beauty |",
"| Capture | Improved if Prop/Yak recoverable | Host-gated |",
"| Overall | **Reference** | Blind A/B still prefers AAA refs |",
"",
"## Blind call",
"High-frequency boards are an engineering capture fix, not AAA art direction. Keep FAIL until side-by-side stills would pick Skyguard for materials, aircraft, city/ocean, weapon, and VFX.",
"",
"## Capture summary",
f"- Usable: {yes}  Partial: {partial}  Failed: {no}",
f"- Prop recoverable: {prop_ok}",
f"- YakBeauty strong: {yak_ok}",
f"- Cockpit strong: {cock_ok}",
f"- City strong: {city_ok}",
"",
"## Next",
"1. If Prop now Yes: replace HF boards with hero prop PBR + motion disc while keeping capture locked",
"2. Authored airframe materials (normal/roughness/AO dirt)",
"3. Niagara muzzle/explosion/prop wash",
"4. Keep FAIL until blind prefers Skyguard on all pillars",
"",
"## Goal",
"NOT COMPLETE.",
]
text = "\n".join(lines) + "\n"
atomic_write(OUT_MD, text)
atomic_write(CTRL, f"""# Skyguard AAA Loop Status (current)

## Critic overall: FAIL (not AAA)
Updated: {time.strftime('%Y-%m-%dT%H:%M:%S')}-05:00

## Latest
- Loop85 HF frustum boards + triple-source capture; map ~{map_size/1e6:.1f}MB
- Usable stills: {yes} | Partial: {partial} | Failed: {no}
- Exact capture gate: {capture_gate['camera_count']}/11 cameras; {capture_gate['source_count']}/33 sources; {capture_gate['manifest_count']}/33 verified hashes
- Prop recoverable: {prop_ok}; Yak strong: {yak_ok}; Cockpit strong: {cock_ok}
- Critic: Docs/AAA_Review/CRITIC_FAIL_loop85.md

## Systems
- C++ combat + prop spinner + VFX helper
- Yak production kit + HF frustum densify
- Host Pillow RGB selects best BASE/FINAL/SCENE per camera

## Do not mark complete
""")
print(text)
print("WROTE", OUT_MD)
