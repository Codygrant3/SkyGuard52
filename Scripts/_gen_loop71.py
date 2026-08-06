from pathlib import Path
import re, ast

src = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop70_true_art_slice13_capture.py")
dst = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop71_true_art_slice14_capture.py")
text = src.read_text(encoding="utf-8")

repls = [
    ("AAA_L70_", "AAA_L71_"),
    ("AAA_L70", "AAA_L71"),
    ("RT_AAA_L70", "RT_AAA_L71"),
    ("loop70", "loop71"),
    ("Loop70", "Loop71"),
    ("slice13", "slice14"),
    ("Slice13", "Slice14"),
    ("_SLICE13_MATS", "_SLICE14_MATS"),
    (
        "L69 freeze + true-art slice13 VFX core language + airframe material response",
        "L70 freeze + true-art slice14 authored VFX look + prop PBR motion disc",
    ),
    (
        "l69_freeze_true_art_slice13_vfx_core_airframe_response",
        "l70_freeze_true_art_slice14_authored_vfx_prop_pbr_motion",
    ),
    ("TA13_", "TA14_"),
]
for a, b in repls:
    text = text.replace(a, b)
for old, new in [
    ("AAA_Cam_L70_", "AAA_Cam_L71_"),
    ("AAA_Cam_L69_", "AAA_Cam_L71_"),
    ("AAA_Cam_L68_", "AAA_Cam_L71_"),
    ("AAA_Cam_L67_", "AAA_Cam_L71_"),
    ("AAA_Cam_L66_", "AAA_Cam_L71_"),
    ("AAA_Cam_L65_", "AAA_Cam_L71_"),
]:
    text = text.replace(old, new)

# Upgrade spawn_niagara with optional user param / fixed bounds and smaller defaults
old_ni_sig = "def spawn_niagara(label, loc, asset_name, scale=(1,1,1), bound=True):"
if old_ni_sig not in text:
    raise SystemExit("spawn_niagara missing")

# Insert helper after spawn_niagara block for emissive unlit material creation
helper = r'''

def create_emissive_unlit(name, color=(1.0, 0.75, 0.25), intensity=8.0, opacity=1.0):
    """Once-authored unlit emissive material for readable VFX cores in stills."""
    path = "/Game/Skyguard/Materials/Generated/" + name
    try:
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            mat = unreal.EditorAssetLibrary.load_asset(path)
            if mat:
                return mat
        factory = unreal.MaterialFactoryNew()
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, "/Game/Skyguard/Materials/Generated", unreal.Material, factory
        )
        if not mat:
            return None
        mel = unreal.MaterialEditingLibrary
        try:
            mel.delete_all_material_expressions(mat)
        except Exception:
            pass
        try:
            mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
        except Exception:
            try:
                mat.set_editor_property("BlendMode", unreal.BlendMode.BLEND_ADDITIVE)
            except Exception:
                pass
        try:
            mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
        except Exception:
            try:
                mat.set_editor_property("ShadingModel", unreal.MaterialShadingModel.MSM_UNLIT)
            except Exception:
                pass
        try:
            mat.set_editor_property("two_sided", True)
        except Exception:
            pass
        c = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
        try:
            c.set_editor_property("constant", unreal.LinearColor(float(color[0]), float(color[1]), float(color[2]), 1.0))
        except Exception:
            pass
        s = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 120)
        try:
            s.set_editor_property("r", float(intensity))
        except Exception:
            pass
        mul = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -200, 40)
        try:
            mel.connect_material_expressions(c, "", mul, "A")
            mel.connect_material_expressions(s, "", mul, "B")
        except Exception:
            pass
        try:
            mel.connect_material_property(mul, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        except Exception:
            try:
                mel.connect_material_property(mul, "", unreal.MaterialProperty.MP_BASE_COLOR)
            except Exception:
                pass
        try:
            mel.recompile_material(mat)
        except Exception:
            pass
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(mat)
        except Exception:
            pass
        log("slice14 emissive mat ready " + name)
        return mat
    except Exception as e:
        log("slice14 emissive mat fail %s %s" % (name, e))
        return None

'''
anchor = "_SLICE14_MATS = None"
if anchor not in text:
    # after rename from _SLICE13
    if "_SLICE14_MATS = None" not in text:
        # find any _SLICE mats
        m = re.search(r'_SLICE\d+_MATS = None', text)
        raise SystemExit("slice mats anchor missing: " + str(m.group(0) if m else None))
text = text.replace(anchor, helper + "\n" + anchor, 1)

# Extend ensure_slice14 materials return with prop disc / VFX mats
old_ret_pat = re.compile(
    r'    _SLICE14_MATS = mats\n    log\("slice14 materials cached count=%d" % len\(\[k for k,v in mats\.items\(\) if v\]\)\)\n    return mats'
)
if not old_ret_pat.search(text):
    # may still have slice14 from rename of slice13 ret that includes L70 resp block
    m = re.search(r'    _SLICE14_MATS = mats\n    log\("slice14 materials cached count=%d".*?\n    return mats', text, re.S)
    if not m:
        raise SystemExit("ensure ret missing")
    old_ret = m.group(0)
else:
    old_ret = old_ret_pat.search(text).group(0)

new_ret = '''    # Slice14: prop motion disc PBR + authored VFX look materials (once, load-existing preferred)
    # Keep L70 response mats; add emissive unlit VFX cores and brighter prop disc variants.
    mats["M_L71_PropDiscMotion"] = create_textured_material(
        "M_L71_PropDiscMotion",
        "/Game/Skyguard/Textures/Imported/T_L8_plate2_A",
        "/Game/Skyguard/Textures/Imported/T_L8_plate2_N",
        "/Game/Skyguard/Textures/Imported/T_L8_plate2_R",
        0.55, 0.35, 1.25, 4.0, -0.08,
    ) or load_mat("/Game/Skyguard/Materials/M_PropDisc") or mats.get("M_L70_PlateResp")
    mats["M_L71_PropBlade"] = create_textured_material(
        "M_L71_PropBlade",
        "/Game/Skyguard/Textures/Imported/T_airframe_metal_A",
        "/Game/Skyguard/Textures/Imported/T_airframe_metal_N",
        "/Game/Skyguard/Textures/Imported/T_airframe_metal_R",
        0.7, 0.0, 1.15, 2.2, -0.05,
    ) or mats.get("M_L70_AirframeResp") or mats.get("M_L68_AirframeANR")
    mats["M_L71_VFX_MuzzleEmi"] = create_emissive_unlit("M_L71_VFX_MuzzleEmi", (1.0, 0.72, 0.22), 12.0)
    mats["M_L71_VFX_SparkEmi"] = create_emissive_unlit("M_L71_VFX_SparkEmi", (1.0, 0.9, 0.55), 10.0)
    mats["M_L71_VFX_TracerEmi"] = create_emissive_unlit("M_L71_VFX_TracerEmi", (1.0, 0.35, 0.12), 14.0)
    mats["M_L71_VFX_FoamEmi"] = create_emissive_unlit("M_L71_VFX_FoamEmi", (0.75, 0.9, 1.0), 3.5)
    mats["M_L71_VFX_ExplEmi"] = create_emissive_unlit("M_L71_VFX_ExplEmi", (1.0, 0.45, 0.08), 16.0)
    # retain L70 response mats if present
    for k in [
        "M_L70_AirframeResp", "M_L70_PlateResp", "M_L70_BrickResp", "M_L70_ConcreteResp",
        "M_L70_RustResp", "M_L70_MuzzleResp", "M_L68_AirframeANR", "M_L68_PlateANR",
        "M_L68_BrickANR", "M_L68_ConcreteANR", "M_L68_RustANR", "M_L61_MuzzleHot",
    ]:
        p = "/Game/Skyguard/Materials/Generated/" + k
        if unreal.EditorAssetLibrary.does_asset_exist(p):
            mats[k] = unreal.EditorAssetLibrary.load_asset(p)
    _SLICE14_MATS = mats
    log("slice14 materials cached count=%d" % len([k for k,v in mats.items() if v]))
    return mats'''
text = text.replace(old_ret, new_ret, 1)

done = 'log("loop71 true-art slice14 densify done")'
if done not in text:
    m = re.search(r'log\("loop71.*?densify done"\)', text)
    raise SystemExit("done missing: " + str(m.group(0) if m else None))

inject = r'''
    # Slice14: authored VFX look (emissive unlit cores) + prop PBR motion disc fidelity
    # HARD RULES: no extra PointLight FOV stacks; keep L52 HF densify core; behind-wall only.
    s14 = ensure_slice14_materials()
    m_air = s14.get("M_L70_AirframeResp") or s14.get("M_L68_AirframeANR") or s14.get("M_L63_AirframeHF")
    m_plate = s14.get("M_L70_PlateResp") or s14.get("M_L68_PlateANR") or s14.get("M_L63_PlateHF")
    m_rust = s14.get("M_L70_RustResp") or s14.get("M_L68_RustANR")
    m_brick = s14.get("M_L70_BrickResp") or s14.get("M_L68_BrickANR")
    m_conc = s14.get("M_L70_ConcreteResp") or s14.get("M_L68_ConcreteANR")
    m_hot = s14.get("M_L70_MuzzleResp") or s14.get("M_L61_MuzzleHot")
    m_glow = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or m_hot
    m_disc = s14.get("M_L71_PropDiscMotion") or load_mat("/Game/Skyguard/Materials/M_PropDisc") or m_plate
    m_blade = s14.get("M_L71_PropBlade") or m_air
    m_muzzle_emi = s14.get("M_L71_VFX_MuzzleEmi") or m_hot
    m_spark_emi = s14.get("M_L71_VFX_SparkEmi") or m_hot
    m_tracer_emi = s14.get("M_L71_VFX_TracerEmi") or m_hot
    m_foam_emi = s14.get("M_L71_VFX_FoamEmi") or m_plate
    m_expl_emi = s14.get("M_L71_VFX_ExplEmi") or m_hot
    m_rifle = load_mat("/Game/Skyguard/Materials/M_RifleTan") or m_plate
    sm_prop = load_sm("/Game/Skyguard/Meshes/Hero/propeller_proxy")
    sm_yak = load_sm("/Game/Skyguard/Meshes/Hero/yak52_hd_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/yak52_proxy")
    sm_rifle_m = load_sm("/Game/Skyguard/Meshes/Hero/rifle_ads_proxy")
    sm_drone = load_sm("/Game/Skyguard/Meshes/Hero/shahed_proxy")
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx = cam[0] + dist
        cy, cz = cam[1], cam[2]
        # Prop PBR motion disc: concentric rings + multi-blade motion language (behind wall)
        if name in ("Prop", "PropHub", "PropNose", "YakBeauty"):
            # outer disc + mid ring + hub
            spawn_sm(sphere, (bx + 3.74, cy + 0.0, cz + 0.12), (1.15, 0.06, 1.15), None, PREFIX + "TA14_PropDiscOuter_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.75, cy + 0.0, cz + 0.12), (0.75, 0.05, 0.75), None, PREFIX + "TA14_PropDiscMid_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.76, cy + 0.0, cz + 0.12), (0.28, 0.08, 0.28), None, PREFIX + "TA14_PropHub_%s" % name, mat=m_plate)
            for k in range(8):
                ang = k * 22.5
                spawn_sm(cube, (bx + 3.77, cy + 0.55 * ((k % 2) * 2 - 1) * 0.5, cz + 0.12), (0.03, 1.05, 0.06), unreal.Rotator(0, ang, 8 + k), PREFIX + "TA14_PropBlade_%s_%d" % (name, k), mat=m_blade)
            # motion blur streaks (thin emissive-ish plate strips)
            for k in range(6):
                spawn_sm(cube, (bx + 3.73, cy + 0.2 * (k - 2.5), cz + 0.12), (0.02, 0.9, 0.035), unreal.Rotator(0, k * 15, 0), PREFIX + "TA14_PropStreak_%s_%d" % (name, k), mat=m_disc)
            if sm_prop:
                spawn_sm(sm_prop, (bx + 3.82, cy + 0.0, cz + 0.1), (0.46, 0.46, 0.46), unreal.Rotator(0, 0, 30), PREFIX + "TA14_PropHero_%s" % name, mats=[m_blade, m_air, m_plate, m_disc])
            if sm_yak and name == "YakBeauty":
                spawn_sm(sm_yak, (bx + 3.64, cy - 0.1, cz - 0.3), (0.62, 0.62, 0.62), unreal.Rotator(0, 90, 0), PREFIX + "TA14_YakHero", mats=[m_air, m_plate, m_rust, m_glow])
            spawn_niagara(PREFIX + "TA14_NS_PropWash_%s" % name, (bx + 3.74, cy + 0.03, cz + 0.03), "NS_PropWash", (0.2, 0.2, 0.2), bound=True)
            if name in ("YakBeauty", "Prop"):
                spawn_niagara(PREFIX + "TA14_NS_Contrail_%s" % name, (bx + 3.9, cy + 0.06, cz + 0.0), "NS_ContrailRibbon", (0.18, 0.18, 0.18), bound=True)
            spawn_sm(sphere, (bx + 3.85, cy - 0.3, cz - 0.02), (0.055, 0.055, 0.055), None, PREFIX + "TA14_Exhaust_%s" % name, mat=m_muzzle_emi or m_glow)
        # Airframe response seams (compound L70)
        if name in ("YakBeauty", "Cockpit", "ADS", "Prop"):
            spawn_sm(cube, (bx + 3.53, cy + 0.1, cz + 0.08), (0.05, 1.3, 0.75), None, PREFIX + "TA14_AirResp_%s" % name, mat=m_air)
            spawn_sm(cube, (bx + 3.57, cy - 0.5, cz - 0.05), (0.045, 0.95, 0.5), None, PREFIX + "TA14_PlateResp_%s" % name, mat=m_plate)
            spawn_sm(cube, (bx + 3.55, cy + 0.6, cz - 0.15), (0.04, 0.45, 0.15), None, PREFIX + "TA14_RustResp_%s" % name, mat=m_rust)
            for k in range(8):
                spawn_sm(sphere, (bx + 3.58, cy - 0.55 + k * 0.15, cz + 0.4), (0.026, 0.026, 0.026), None, PREFIX + "TA14_Rivet_%s_%d" % (name, k), mat=m_plate)
        # Authored VFX look: emissive cores + bounded systems (still capture-safe sizes)
        if name in ("Combat", "ADS", "Wide"):
            if sm_rifle_m and name in ("ADS", "Combat"):
                spawn_sm(sm_rifle_m, (bx + 3.3, cy + 0.08, cz - 0.05), (0.4, 0.4, 0.4), unreal.Rotator(0, 90, 0), PREFIX + "TA14_RifleHero_%s" % name, mats=[m_rifle, m_plate, m_rust, m_hot])
            spawn_niagara(PREFIX + "TA14_NS_Muzzle_%s" % name, (bx + 3.44, cy + 0.18, cz + 0.1), "NS_MuzzleFlash", (0.18, 0.18, 0.18), bound=True)
            spawn_niagara(PREFIX + "TA14_NS_Smoke_%s" % name, (bx + 3.46, cy + 0.14, cz + 0.06), "NS_GunSmoke", (0.16, 0.16, 0.16), bound=True)
            spawn_niagara(PREFIX + "TA14_NS_Sparks_%s" % name, (bx + 3.54, cy + 0.95, cz + 0.32), "NS_HitSparks", (0.22, 0.22, 0.22), bound=True)
            spawn_niagara(PREFIX + "TA14_NS_Tracer_%s" % name, (bx + 3.5, cy + 0.25, cz + 0.18), "NS_TracerBurst", (0.16, 0.16, 0.16), bound=True)
            # emissive authored cores
            spawn_sm(sphere, (bx + 3.45, cy + 0.2, cz + 0.12), (0.08, 0.08, 0.08), None, PREFIX + "TA14_MuzzleCore_%s" % name, mat=m_muzzle_emi)
            spawn_sm(sphere, (bx + 3.48, cy + 0.28, cz + 0.18), (0.05, 0.05, 0.05), None, PREFIX + "TA14_MuzzleHalo_%s" % name, mat=m_spark_emi)
            for k in range(7):
                spawn_sm(cube, (bx + 3.38 + k * 0.03, cy + 0.16 + k * 0.045, cz + 0.08 + k * 0.025), (0.16 - k * 0.015, 0.016, 0.016), unreal.Rotator(0, -14 + k * 6, 0), PREFIX + "TA14_Filament_%s_%d" % (name, k), mat=m_tracer_emi)
            for k in range(6):
                spawn_sm(sphere, (bx + 3.52, cy + 0.0 + k * 0.05, cz - 0.03 + k * 0.02), (0.024, 0.024, 0.024), None, PREFIX + "TA14_Shell_%s_%d" % (name, k), mat=m_plate)
            for k in range(8):
                spawn_sm(sphere, (bx + 3.5, cy + 0.7 + k * 0.05, cz + 0.25 + (k % 2) * 0.04), (0.03, 0.03, 0.03), None, PREFIX + "TA14_Spark_%s_%d" % (name, k), mat=m_spark_emi)
            if name == "Combat":
                spawn_niagara(PREFIX + "TA14_NS_Expl", (bx + 3.6, cy - 0.92, cz + 0.55), "NS_DroneExplosion", (0.24, 0.24, 0.24), bound=True)
                spawn_niagara(PREFIX + "TA14_NS_Flak", (bx + 3.58, cy + 1.05, cz + 0.5), "NS_FlakBurst", (0.2, 0.2, 0.2), bound=True)
                if sm_drone:
                    spawn_sm(sm_drone, (bx + 3.62, cy - 0.98, cz + 0.52), (0.38, 0.38, 0.38), unreal.Rotator(0, 90, 6), PREFIX + "TA14_Shahed", mats=[m_plate, m_air, m_rust, m_hot])
                spawn_sm(sphere, (bx + 3.6, cy - 0.92, cz + 0.6), (0.14, 0.14, 0.14), None, PREFIX + "TA14_ExplCore", mat=m_expl_emi)
                for k in range(10):
                    spawn_sm(sphere, (bx + 3.52, cy - 1.15 + k * 0.05, cz + 0.48 + (k % 2) * 0.05), (0.028, 0.028, 0.028), None, PREFIX + "TA14_Debris_%d" % k, mat=m_spark_emi if k % 2 == 0 else m_plate)
        # City/ocean
        if name in ("City", "Harbor", "Wide"):
            spawn_sm(cube, (bx + 3.55, cy + 0.32, cz - 0.32), (0.06, 1.15, 1.4), None, PREFIX + "TA14_BrickResp_%s" % name, mat=m_brick)
            spawn_sm(cube, (bx + 3.59, cy - 0.88, cz - 0.12), (0.055, 0.98, 1.1), None, PREFIX + "TA14_ConcResp_%s" % name, mat=m_conc)
            spawn_sm(cube, (bx + 3.57, cy + 0.02, cz + 0.26), (0.05, 0.8, 0.9), None, PREFIX + "TA14_CityHero_%s" % name, mats=[m_brick, m_conc, m_rust])
            for ix in range(3):
                for iy in range(4):
                    spawn_sm(cube, (bx + 3.56, cy - 0.2 + ix * 0.35, cz - 0.15 + iy * 0.32), (0.028, 0.15, 0.2), None, PREFIX + "TA14_Win_%s_%d_%d" % (name, ix, iy), mat=load_mat("/Game/Skyguard/Materials/M_CityGlass") or m_plate)
            if name == "City":
                spawn_niagara(PREFIX + "TA14_NS_CityFire", (bx + 3.6, cy + 0.42, cz + 0.78), "NS_CityFire", (0.22, 0.22, 0.22), bound=True)
            spawn_sm(sphere, (bx + 3.64, cy + 0.1, cz + 0.9), (0.045, 0.045, 0.045), None, PREFIX + "TA14_CityPin_%s" % name, mat=m_muzzle_emi or m_glow)
        if name in ("Ocean", "Harbor"):
            spawn_niagara(PREFIX + "TA14_NS_Spray_%s" % name, (bx + 3.5, cy - 0.25, cz - 0.58), "NS_OceanSpray", (0.3, 0.3, 0.3), bound=True)
            spawn_niagara(PREFIX + "TA14_NS_Splash_%s" % name, (bx + 3.52, cy - 0.1, cz - 0.66), "NS_WaterSplash", (0.24, 0.24, 0.24), bound=True)
            for k in range(10):
                spawn_sm(sphere, (bx + 3.48, cy - 0.85 + k * 0.11, cz - 0.48 + (k % 2) * 0.06), (0.045 + (k % 2) * 0.012, 0.045 + (k % 2) * 0.012, 0.045 + (k % 2) * 0.012), None, PREFIX + "TA14_Foam_%s_%d" % (name, k), mat=m_foam_emi)
    log("slice14 authored vfx look + prop pbr motion densify applied (no extra point lights)")
'''
text = text.replace(done, inject + "\n    " + done, 1)
text = re.sub(
    r'log\("loop71 .*? start"\)',
    'log("loop71 L70 freeze + true-art slice14 authored VFX look + prop PBR motion disc start")',
    text,
    count=1,
)
text = re.sub(
    r'note=l\d+_freeze_true_art_slice14[^\n\"]*',
    'note=l70_freeze_true_art_slice14_authored_vfx_prop_pbr_motion',
    text,
)

# fix possible broken note lines later
if "def ensure_slice14_materials" not in text:
    raise SystemExit("ensure_slice14_materials missing")

dst.write_text(text, encoding="utf-8")
# repair any truncated note write lines
lines = dst.read_text(encoding="utf-8", errors="replace").splitlines(True)
out = []
for line in lines:
    if "note=l70_freeze_true_art_slice14_authored_vfx_prop_pbr_motion" in line and "f.write" in line and not line.rstrip().endswith('")'):
        out.append('        f.write("note=l70_freeze_true_art_slice14_authored_vfx_prop_pbr_motion\\n")\n')
    else:
        out.append(line)
text = "".join(out)
ast.parse(text)
dst.write_text(text, encoding="utf-8")
print("WROTE", dst, dst.stat().st_size)
print("cam71", "AAA_Cam_L71_" in text)
print("inject", "slice14 authored vfx look" in text)
print("emissive", "create_emissive_unlit" in text)
print("pointlight", "spawn_point_light" in text)

ha = Path(r"D:\Skyguard52\Scripts\host_audit_loop70.py").read_text(encoding="utf-8")
ha2 = (
    ha.replace("AAA_L70", "AAA_L71")
    .replace("loop70", "loop71")
    .replace("Loop 70", "Loop 71")
    .replace("Loop70", "Loop71")
    .replace("AAA_Cam_L70_", "AAA_Cam_L71_")
)
Path(r"D:\Skyguard52\Scripts\host_audit_loop71.py").write_text(ha2, encoding="utf-8")
ast.parse(ha2)
print("AUDIT_OK")
