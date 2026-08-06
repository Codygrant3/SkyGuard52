from pathlib import Path
import re, ast

src = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop69_true_art_slice12_capture.py")
dst = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop70_true_art_slice13_capture.py")
text = src.read_text(encoding="utf-8")

repls = [
    ("AAA_L69_", "AAA_L70_"),
    ("AAA_L69", "AAA_L70"),
    ("RT_AAA_L69", "RT_AAA_L70"),
    ("loop69", "loop70"),
    ("Loop69", "Loop70"),
    ("slice12", "slice13"),
    ("Slice12", "Slice13"),
    ("_SLICE12_MATS", "_SLICE13_MATS"),
    (
        "L68 freeze + true-art slice12 bounded Niagara quality + prop disc fidelity",
        "L69 freeze + true-art slice13 VFX core language + airframe material response",
    ),
    (
        "l68_freeze_true_art_slice12_bounded_niagara_prop_disc",
        "l69_freeze_true_art_slice13_vfx_core_airframe_response",
    ),
    ("TA12_", "TA13_"),
]
for a, b in repls:
    text = text.replace(a, b)
text = text.replace("AAA_Cam_L69_", "AAA_Cam_L70_")
text = text.replace("AAA_Cam_L68_", "AAA_Cam_L70_")
text = text.replace("AAA_Cam_L67_", "AAA_Cam_L70_")
text = text.replace("AAA_Cam_L66_", "AAA_Cam_L70_")
text = text.replace("AAA_Cam_L65_", "AAA_Cam_L70_")

# Extend ensure_slice13_materials with response mats that load existing L68 textures/mats
old_ret = '''    _SLICE13_MATS = mats
    log("slice13 materials cached count=%d" % len([k for k,v in mats.items() if v]))
    return mats'''
if old_ret not in text:
    # may still say slice12 if rename of ensure body incomplete
    m = re.search(r'    _SLICE13_MATS = mats\n    log\("slice13 materials cached count=%d".*?\n    return mats', text)
    if not m:
        # try after rename of function but ret still old
        raise SystemExit('ensure ret missing')
    old_ret = m.group(0)

new_ret = '''    # Slice13: once-authored higher-response ANR variants (load-existing preferred)
    # Prefer existing M_L68_*ANR; add slightly brighter UV-scaled response mats if textures exist.
    resp_specs = [
        ("M_L70_AirframeResp", "/Game/Skyguard/Textures/Imported/T_airframe_metal_A", "/Game/Skyguard/Textures/Imported/T_airframe_metal_N", "/Game/Skyguard/Textures/Imported/T_airframe_metal_R", 0.66, 0.02, 1.22, 2.6, -0.04),
        ("M_L70_PlateResp", "/Game/Skyguard/Textures/Imported/T_L8_plate2_A", "/Game/Skyguard/Textures/Imported/T_L8_plate2_N", "/Game/Skyguard/Textures/Imported/T_L8_plate2_R", 0.5, 0.0, 1.18, 3.0, -0.02),
        ("M_L70_BrickResp", "/Game/Skyguard/Textures/Imported/T_brick_A", "/Game/Skyguard/Textures/Imported/T_brick_N", "/Game/Skyguard/Textures/Imported/T_brick_R", 0.08, 0.0, 1.14, 3.2, 0.02),
        ("M_L70_ConcreteResp", "/Game/Skyguard/Textures/Imported/T_concrete_A", "/Game/Skyguard/Textures/Imported/T_concrete_N", "/Game/Skyguard/Textures/Imported/T_concrete_R", 0.05, 0.0, 1.12, 2.8, 0.03),
        ("M_L70_RustResp", "/Game/Skyguard/Textures/Imported/T_L4_rust_A", "/Game/Skyguard/Textures/Imported/T_L4_rust_N", "/Game/Skyguard/Textures/Imported/T_L4_rust_R", 0.24, 0.02, 1.16, 3.0, 0.02),
        ("M_L70_MuzzleResp", "/Game/Skyguard/Textures/Imported/T_L8_plate2_A", None, None, 0.12, 2.8, 1.35, 1.0, -0.15),
    ]
    for name, a, n, r, metal, emi, bright, uvs, rb in resp_specs:
        path = "/Game/Skyguard/Materials/Generated/" + name
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            mats[name] = unreal.EditorAssetLibrary.load_asset(path)
            continue
        mats[name] = create_textured_material(name, a, n if n else None, r if r else None, metal, emi, bright, uvs, rb)
        if not mats[name]:
            for fb in [
                "M_L68_AirframeANR", "M_L63_AirframeHF", "M_L68_PlateANR", "M_L63_PlateHF",
                "M_L68_BrickANR", "M_L63_BrickHF", "M_L68_ConcreteANR", "M_L63_ConcreteHF",
                "M_L68_RustANR", "M_L63_RustHF", "M_L61_MuzzleHot", "M_L66_MuzzleHot",
            ]:
                p = "/Game/Skyguard/Materials/Generated/" + fb
                if unreal.EditorAssetLibrary.does_asset_exist(p):
                    mats[name] = unreal.EditorAssetLibrary.load_asset(p)
                    break
    # always prefer existing L68 mats as well
    for k in ["M_L68_AirframeANR","M_L68_PlateANR","M_L68_BrickANR","M_L68_ConcreteANR","M_L68_RustANR","M_L61_MuzzleHot"]:
        p = "/Game/Skyguard/Materials/Generated/" + k
        if unreal.EditorAssetLibrary.does_asset_exist(p):
            mats[k] = unreal.EditorAssetLibrary.load_asset(p)
    _SLICE13_MATS = mats
    log("slice13 materials cached count=%d" % len([k for k,v in mats.items() if v]))
    return mats'''
text = text.replace(old_ret, new_ret, 1)

done = 'log("loop70 true-art slice13 densify done")'
if done not in text:
    m = re.search(r'log\("loop70.*?densify done"\)', text)
    raise SystemExit("done missing: " + str(m.group(0) if m else None))

inject = r'''
    # Slice13: VFX core language + stronger airframe/city material response (capture-safe)
    # HARD RULES: no extra PointLight FOV stacks; keep L52 HF densify core; behind-wall only.
    s13 = ensure_slice13_materials()
    m_air = s13.get("M_L70_AirframeResp") or s13.get("M_L68_AirframeANR") or s13.get("M_L63_AirframeHF")
    m_plate = s13.get("M_L70_PlateResp") or s13.get("M_L68_PlateANR") or s13.get("M_L63_PlateHF")
    m_rust = s13.get("M_L70_RustResp") or s13.get("M_L68_RustANR") or s13.get("M_L63_RustHF")
    m_brick = s13.get("M_L70_BrickResp") or s13.get("M_L68_BrickANR") or s13.get("M_L63_BrickHF")
    m_conc = s13.get("M_L70_ConcreteResp") or s13.get("M_L68_ConcreteANR") or s13.get("M_L63_ConcreteHF")
    m_hot = s13.get("M_L70_MuzzleResp") or s13.get("M_L61_MuzzleHot") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Muzzle")
    m_glow = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or m_hot
    m_disc = load_mat("/Game/Skyguard/Materials/M_PropDisc") or m_plate
    m_rifle = load_mat("/Game/Skyguard/Materials/M_RifleTan") or m_plate
    sm_prop = load_sm("/Game/Skyguard/Meshes/Hero/propeller_proxy")
    sm_yak = load_sm("/Game/Skyguard/Meshes/Hero/yak52_hd_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/yak52_proxy")
    sm_rifle_m = load_sm("/Game/Skyguard/Meshes/Hero/rifle_ads_proxy")
    sm_drone = load_sm("/Game/Skyguard/Meshes/Hero/shahed_proxy")
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx = cam[0] + dist
        cy, cz = cam[1], cam[2]
        # Airframe response panels + denser rivet/seam language (x>=bx+3.5)
        if name in ("YakBeauty", "Prop", "PropHub", "PropNose", "Cockpit", "ADS"):
            spawn_sm(cube, (bx + 3.52, cy + 0.12, cz + 0.1), (0.055, 1.25, 0.72), None, PREFIX + "TA13_AirResp_%s" % name, mat=m_air)
            spawn_sm(cube, (bx + 3.56, cy - 0.52, cz - 0.06), (0.05, 0.9, 0.48), None, PREFIX + "TA13_PlateResp_%s" % name, mat=m_plate)
            spawn_sm(cube, (bx + 3.54, cy + 0.58, cz - 0.16), (0.04, 0.42, 0.14), None, PREFIX + "TA13_RustResp_%s" % name, mat=m_rust)
            spawn_sm(cube, (bx + 3.58, cy + 0.18, cz + 0.22), (0.045, 0.95, 0.55), None, PREFIX + "TA13_HeroPanel_%s" % name, mats=[m_air, m_plate, m_rust, m_glow])
            for k in range(7):
                spawn_sm(sphere, (bx + 3.57, cy - 0.5 + k * 0.16, cz + 0.38), (0.028, 0.028, 0.028), None, PREFIX + "TA13_Rivet_%s_%d" % (name, k), mat=m_plate)
            for k in range(4):
                spawn_sm(cube, (bx + 3.53, cy - 0.35 + k * 0.25, cz + 0.02), (0.03, 0.06, 0.28), None, PREFIX + "TA13_Seam_%s_%d" % (name, k), mat=m_rust)
            spawn_sm(sphere, (bx + 3.62, cy + 0.0, cz + 0.42), (0.045, 0.045, 0.045), None, PREFIX + "TA13_EmiPin_%s" % name, mat=m_glow)
        # Prop disc fidelity + bounded wash
        if name in ("Prop", "PropHub", "PropNose", "YakBeauty"):
            spawn_sm(sphere, (bx + 3.74, cy + 0.0, cz + 0.12), (1.05, 0.07, 1.05), None, PREFIX + "TA13_PropDisc_%s" % name, mat=m_disc)
            for k in range(6):
                ang = k * 30.0
                spawn_sm(cube, (bx + 3.76, cy + 0.4 * ((k % 2) * 2 - 1), cz + 0.12), (0.035, 0.95, 0.07), unreal.Rotator(0, ang, 10), PREFIX + "TA13_PropBlade_%s_%d" % (name, k), mat=m_plate)
            if sm_prop:
                spawn_sm(sm_prop, (bx + 3.8, cy + 0.0, cz + 0.1), (0.44, 0.44, 0.44), unreal.Rotator(0, 0, 25), PREFIX + "TA13_PropHero_%s" % name, mats=[m_plate, m_air, m_rust, m_disc])
            if sm_yak and name == "YakBeauty":
                spawn_sm(sm_yak, (bx + 3.62, cy - 0.12, cz - 0.32), (0.6, 0.6, 0.6), unreal.Rotator(0, 90, 0), PREFIX + "TA13_YakHero", mats=[m_air, m_plate, m_rust, m_glow])
            spawn_niagara(PREFIX + "TA13_NS_PropWash_%s" % name, (bx + 3.72, cy + 0.04, cz + 0.04), "NS_PropWash", (0.22, 0.22, 0.22), bound=True)
            if name in ("YakBeauty", "Prop"):
                spawn_niagara(PREFIX + "TA13_NS_Contrail_%s" % name, (bx + 3.88, cy + 0.08, cz + 0.0), "NS_ContrailRibbon", (0.2, 0.2, 0.2), bound=True)
            spawn_sm(sphere, (bx + 3.82, cy - 0.32, cz - 0.04), (0.05, 0.05, 0.05), None, PREFIX + "TA13_Exhaust_%s" % name, mat=m_glow)
        # Authored-looking VFX core language (mesh cores + single bounded Niagara)
        if name in ("Combat", "ADS", "Wide"):
            if sm_rifle_m and name in ("ADS", "Combat"):
                spawn_sm(sm_rifle_m, (bx + 3.28, cy + 0.1, cz - 0.06), (0.38, 0.38, 0.38), unreal.Rotator(0, 90, 0), PREFIX + "TA13_RifleHero_%s" % name, mats=[m_rifle, m_plate, m_rust, m_hot])
            spawn_niagara(PREFIX + "TA13_NS_Muzzle_%s" % name, (bx + 3.42, cy + 0.2, cz + 0.12), "NS_MuzzleFlash", (0.2, 0.2, 0.2), bound=True)
            spawn_niagara(PREFIX + "TA13_NS_Smoke_%s" % name, (bx + 3.44, cy + 0.16, cz + 0.08), "NS_GunSmoke", (0.18, 0.18, 0.18), bound=True)
            spawn_niagara(PREFIX + "TA13_NS_Sparks_%s" % name, (bx + 3.52, cy + 0.92, cz + 0.34), "NS_HitSparks", (0.24, 0.24, 0.24), bound=True)
            # VFX cores / filaments / shells (proxy language that stills can read)
            spawn_sm(sphere, (bx + 3.43, cy + 0.22, cz + 0.14), (0.07, 0.07, 0.07), None, PREFIX + "TA13_MuzzleCore_%s" % name, mat=m_hot)
            spawn_sm(sphere, (bx + 3.46, cy + 0.3, cz + 0.2), (0.045, 0.045, 0.045), None, PREFIX + "TA13_MuzzleHalo_%s" % name, mat=m_glow)
            for k in range(6):
                spawn_sm(cube, (bx + 3.36 + k * 0.025, cy + 0.18 + k * 0.04, cz + 0.1 + k * 0.02), (0.14 - k * 0.015, 0.018, 0.018), unreal.Rotator(0, -12 + k * 5, 0), PREFIX + "TA13_Filament_%s_%d" % (name, k), mat=m_hot)
            for k in range(5):
                spawn_sm(sphere, (bx + 3.5, cy + 0.02 + k * 0.05, cz - 0.02 + k * 0.02), (0.025, 0.025, 0.025), None, PREFIX + "TA13_Shell_%s_%d" % (name, k), mat=m_plate)
            if name == "Combat":
                spawn_niagara(PREFIX + "TA13_NS_Expl", (bx + 3.58, cy - 0.95, cz + 0.58), "NS_DroneExplosion", (0.26, 0.26, 0.26), bound=True)
                spawn_niagara(PREFIX + "TA13_NS_Flak", (bx + 3.55, cy + 1.05, cz + 0.52), "NS_FlakBurst", (0.22, 0.22, 0.22), bound=True)
                if sm_drone:
                    spawn_sm(sm_drone, (bx + 3.6, cy - 1.0, cz + 0.55), (0.36, 0.36, 0.36), unreal.Rotator(0, 90, 8), PREFIX + "TA13_Shahed", mats=[m_plate, m_air, m_rust, m_hot])
                spawn_sm(sphere, (bx + 3.58, cy - 0.95, cz + 0.62), (0.12, 0.12, 0.12), None, PREFIX + "TA13_ExplCore", mat=m_hot)
                for k in range(8):
                    spawn_sm(sphere, (bx + 3.5, cy - 1.15 + k * 0.06, cz + 0.5 + (k % 2) * 0.05), (0.03, 0.03, 0.03), None, PREFIX + "TA13_Debris_%d" % k, mat=m_plate)
        # City/ocean response
        if name in ("City", "Harbor", "Wide"):
            spawn_sm(cube, (bx + 3.54, cy + 0.35, cz - 0.35), (0.065, 1.1, 1.35), None, PREFIX + "TA13_BrickResp_%s" % name, mat=m_brick)
            spawn_sm(cube, (bx + 3.58, cy - 0.9, cz - 0.15), (0.06, 0.95, 1.05), None, PREFIX + "TA13_ConcResp_%s" % name, mat=m_conc)
            spawn_sm(cube, (bx + 3.56, cy + 0.05, cz + 0.28), (0.05, 0.75, 0.85), None, PREFIX + "TA13_CityHero_%s" % name, mats=[m_brick, m_conc, m_rust])
            for ix in range(3):
                for iy in range(3):
                    spawn_sm(cube, (bx + 3.55, cy + 0.0 + ix * 0.35, cz + 0.0 + iy * 0.35), (0.03, 0.16, 0.22), None, PREFIX + "TA13_Win_%s_%d_%d" % (name, ix, iy), mat=load_mat("/Game/Skyguard/Materials/M_CityGlass") or m_plate)
            if name == "City":
                spawn_niagara(PREFIX + "TA13_NS_CityFire", (bx + 3.58, cy + 0.45, cz + 0.8), "NS_CityFire", (0.24, 0.24, 0.24), bound=True)
            spawn_sm(sphere, (bx + 3.62, cy + 0.12, cz + 0.92), (0.04, 0.04, 0.04), None, PREFIX + "TA13_CityPin_%s" % name, mat=m_glow)
        if name in ("Ocean", "Harbor"):
            spawn_niagara(PREFIX + "TA13_NS_Spray_%s" % name, (bx + 3.48, cy - 0.28, cz - 0.6), "NS_OceanSpray", (0.32, 0.32, 0.32), bound=True)
            spawn_niagara(PREFIX + "TA13_NS_Splash_%s" % name, (bx + 3.5, cy - 0.12, cz - 0.68), "NS_WaterSplash", (0.26, 0.26, 0.26), bound=True)
            for k in range(8):
                spawn_sm(sphere, (bx + 3.46, cy - 0.8 + k * 0.12, cz - 0.5 + (k % 2) * 0.06), (0.04 + (k % 2) * 0.01, 0.04 + (k % 2) * 0.01, 0.04 + (k % 2) * 0.01), None, PREFIX + "TA13_Foam_%s_%d" % (name, k), mat=load_mat("/Game/Skyguard/Materials/Generated/M_L61_FoamLit") or m_plate)
    log("slice13 vfx core language + airframe material response densify applied (no extra point lights)")
'''
text = text.replace(done, inject + "\n    " + done, 1)

# main/start note cleanup
text = text.replace(
    'log("loop70 L68 freeze + true-art slice13 VFX core language + airframe material response start")',
    'log("loop70 L69 freeze + true-art slice13 VFX core language + airframe material response start")',
)
# if previous replace didn't catch because string still had L68 from partial rename
text = re.sub(
    r'log\("loop70 .*? start"\)',
    'log("loop70 L69 freeze + true-art slice13 VFX core language + airframe material response start")',
    text,
    count=1,
)
text = text.replace(
    "note=l68_freeze_true_art_slice13_vfx_core_airframe_response",
    "note=l69_freeze_true_art_slice13_vfx_core_airframe_response",
)
text = text.replace(
    "note=l69_freeze_true_art_slice13_vfx_core_airframe_response",
    "note=l69_freeze_true_art_slice13_vfx_core_airframe_response",
)
# fix note if still old
text = re.sub(r'note=l\d+_freeze_true_art_slice13[^\n]*', 'note=l69_freeze_true_art_slice13_vfx_core_airframe_response', text)

if "def ensure_slice13_materials" not in text:
    raise SystemExit("ensure_slice13_materials missing")

dst.write_text(text, encoding="utf-8")
ast.parse(text)
print("WROTE", dst, dst.stat().st_size)
print("cam70", "AAA_Cam_L70_" in text)
print("inject", "slice13 vfx core language" in text)
print("pointlight", "spawn_point_light" in text)
print("M_L70", "M_L70_AirframeResp" in text)

ha = Path(r"D:\Skyguard52\Scripts\host_audit_loop69.py").read_text(encoding="utf-8")
ha2 = (
    ha.replace("AAA_L69", "AAA_L70")
    .replace("loop69", "loop70")
    .replace("Loop 69", "Loop 70")
    .replace("Loop69", "Loop70")
    .replace("AAA_Cam_L69_", "AAA_Cam_L70_")
)
Path(r"D:\Skyguard52\Scripts\host_audit_loop70.py").write_text(ha2, encoding="utf-8")
ast.parse(ha2)
print("AUDIT_OK")
