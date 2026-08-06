from pathlib import Path
import re, ast

src = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop71_true_art_slice14_capture.py")
dst = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop72_true_art_slice15_capture.py")
text = src.read_text(encoding="utf-8")

repls = [
    ("AAA_L71_", "AAA_L72_"),
    ("AAA_L71", "AAA_L72"),
    ("RT_AAA_L71", "RT_AAA_L72"),
    ("loop71", "loop72"),
    ("Loop71", "Loop72"),
    ("slice14", "slice15"),
    ("Slice14", "Slice15"),
    ("_SLICE14_MATS", "_SLICE15_MATS"),
    (
        "L70 freeze + true-art slice14 authored VFX look + prop PBR motion disc",
        "L71 freeze + true-art slice15 authored Niagara shells + denser VFX language",
    ),
    (
        "l70_freeze_true_art_slice15_authored_vfx_prop_pbr_motion",
        "l71_freeze_true_art_slice15_authored_niagara_denser_vfx",
    ),
    (
        "l70_freeze_true_art_slice14_authored_vfx_prop_pbr_motion",
        "l71_freeze_true_art_slice15_authored_niagara_denser_vfx",
    ),
    ("TA14_", "TA15_"),
]
for a, b in repls:
    text = text.replace(a, b)
for old, new in [
    ("AAA_Cam_L71_", "AAA_Cam_L72_"),
    ("AAA_Cam_L70_", "AAA_Cam_L72_"),
    ("AAA_Cam_L69_", "AAA_Cam_L72_"),
    ("AAA_Cam_L68_", "AAA_Cam_L72_"),
    ("AAA_Cam_L67_", "AAA_Cam_L72_"),
    ("AAA_Cam_L66_", "AAA_Cam_L72_"),
    ("AAA_Cam_L65_", "AAA_Cam_L72_"),
]:
    text = text.replace(old, new)

# Insert Niagara author helper after create_emissive_unlit / before _SLICE15_MATS
ni_helper = r'''

def ensure_authored_ns(name):
    """Create or load a NiagaraSystem shell and attempt basic emitter authoring via available Python APIs.
    Empty shells are not AAA, but this is the formal Slice15 step toward real emitter graphs.
    """
    path = "/Game/Skyguard/VFX/" + name
    try:
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            return unreal.EditorAssetLibrary.load_asset(path)
    except Exception:
        pass
    asset = None
    try:
        factory = unreal.NiagaraSystemFactoryNew()
        asset = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, "/Game/Skyguard/VFX", unreal.NiagaraSystem, factory
        )
    except Exception as e:
        log("ns create fail %s %s" % (name, e))
        return None
    if not asset:
        return None
    # Best-effort emitter graph authoring depending on engine Python bindings.
    try:
        # Prefer editor libraries if present
        for lib_name in ["NiagaraSystemEditorData", "NiagaraEditorUtilities", "NiagaraSystemFactoryNew"]:
            pass
        # Try creating an emitter asset and adding it
        emitter = None
        try:
            ef = unreal.NiagaraEmitterFactoryNew()
            emitter = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
                name + "_Emitter", "/Game/Skyguard/VFX/Emitters", unreal.NiagaraEmitter, ef
            )
            if emitter:
                try:
                    unreal.EditorAssetLibrary.save_loaded_asset(emitter)
                except Exception:
                    pass
                log("created emitter shell " + name + "_Emitter")
        except Exception as e:
            log("emitter factory limited %s %s" % (name, e))
        # Try system-level user parameters for bounded defaults
        for prop, val in [
            ("expose_to_library", True),
            ("bExposeToLibrary", True),
        ]:
            try:
                asset.set_editor_property(prop, val)
            except Exception:
                pass
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(asset)
        except Exception:
            pass
        log("authored ns shell " + name)
    except Exception as e:
        log("ns author limited %s %s" % (name, e))
    return asset


def ensure_slice15_vfx_library():
    ensure_dir("/Game/Skyguard/VFX")
    ensure_dir("/Game/Skyguard/VFX/Emitters")
    names = [
        "NS_MuzzleFlash", "NS_GunSmoke", "NS_HitSparks", "NS_TracerBurst", "NS_ShellCasings",
        "NS_DroneExplosion", "NS_FlakBurst", "NS_MissileTrail", "NS_IglaLaunch", "NS_DroneTrail",
        "NS_OceanSpray", "NS_WaterSplash", "NS_PropWash", "NS_ContrailRibbon", "NS_CityFire",
        "NS_CloudWisps",
        # Slice15 named variants (new shells for formal author pass)
        "NS_L72_MuzzleAuth", "NS_L72_SparkAuth", "NS_L72_ExplAuth", "NS_L72_SprayAuth", "NS_L72_PropWashAuth",
    ]
    out = {}
    for n in names:
        out[n] = ensure_authored_ns(n)
    log("slice15 vfx library count=%d" % len([k for k, v in out.items() if v]))
    return out

'''

anchor = "_SLICE15_MATS = None"
if anchor not in text:
    m = re.search(r'_SLICE\d+_MATS = None', text)
    raise SystemExit("mats anchor missing: " + str(m.group(0) if m else None))
text = text.replace(anchor, ni_helper + "\n" + anchor, 1)

# Extend ensure_slice15_materials with more VFX/prop mats
old_ret_m = re.search(
    r'    _SLICE15_MATS = mats\n    log\("slice15 materials cached count=%d" % len\(\[k for k,v in mats\.items\(\) if v\]\)\)\n    return mats',
    text,
)
if not old_ret_m:
    m = re.search(r'    _SLICE15_MATS = mats\n    log\("slice15 materials cached count=%d".*?\n    return mats', text, re.S)
    if not m:
        raise SystemExit("ensure ret missing")
    old_ret = m.group(0)
else:
    old_ret = old_ret_m.group(0)

new_ret = '''    # Slice15: denser prop motion + additional VFX emissive cards (once, load-existing preferred)
    mats["M_L72_PropDiscBright"] = create_textured_material(
        "M_L72_PropDiscBright",
        "/Game/Skyguard/Textures/Imported/T_L8_plate2_A",
        "/Game/Skyguard/Textures/Imported/T_L8_plate2_N",
        "/Game/Skyguard/Textures/Imported/T_L8_plate2_R",
        0.6, 0.55, 1.3, 5.0, -0.1,
    ) or mats.get("M_L71_PropDiscMotion") or load_mat("/Game/Skyguard/Materials/M_PropDisc")
    mats["M_L72_PropBladeEdge"] = create_textured_material(
        "M_L72_PropBladeEdge",
        "/Game/Skyguard/Textures/Imported/T_airframe_metal_A",
        "/Game/Skyguard/Textures/Imported/T_airframe_metal_N",
        "/Game/Skyguard/Textures/Imported/T_airframe_metal_R",
        0.75, 0.05, 1.2, 2.4, -0.06,
    ) or mats.get("M_L71_PropBlade") or mats.get("M_L70_AirframeResp")
    mats["M_L72_VFX_CardHot"] = create_emissive_unlit("M_L72_VFX_CardHot", (1.0, 0.65, 0.18), 18.0)
    mats["M_L72_VFX_CardSoft"] = create_emissive_unlit("M_L72_VFX_CardSoft", (1.0, 0.85, 0.45), 8.0)
    mats["M_L72_VFX_CardCool"] = create_emissive_unlit("M_L72_VFX_CardCool", (0.55, 0.8, 1.0), 5.0)
    mats["M_L72_VFX_CardExpl"] = create_emissive_unlit("M_L72_VFX_CardExpl", (1.0, 0.4, 0.05), 20.0)
    # keep prior L71/L70 mats
    for k in [
        "M_L71_PropDiscMotion", "M_L71_PropBlade",
        "M_L71_VFX_MuzzleEmi", "M_L71_VFX_SparkEmi", "M_L71_VFX_TracerEmi", "M_L71_VFX_FoamEmi", "M_L71_VFX_ExplEmi",
        "M_L70_AirframeResp", "M_L70_PlateResp", "M_L70_BrickResp", "M_L70_ConcreteResp", "M_L70_RustResp", "M_L70_MuzzleResp",
        "M_L68_AirframeANR", "M_L68_PlateANR", "M_L68_BrickANR", "M_L68_ConcreteANR", "M_L68_RustANR", "M_L61_MuzzleHot",
    ]:
        p = "/Game/Skyguard/Materials/Generated/" + k
        if unreal.EditorAssetLibrary.does_asset_exist(p):
            mats[k] = unreal.EditorAssetLibrary.load_asset(p)
    _SLICE15_MATS = mats
    log("slice15 materials cached count=%d" % len([k for k,v in mats.items() if v]))
    return mats'''
text = text.replace(old_ret, new_ret, 1)

done = 'log("loop72 true-art slice15 densify done")'
if done not in text:
    m = re.search(r'log\("loop72.*?densify done"\)', text)
    raise SystemExit("done missing: " + str(m.group(0) if m else None))

inject = r'''
    # Slice15: formal Niagara shell author pass + denser capture-safe VFX language
    # HARD RULES: no extra PointLight FOV stacks; keep L52 HF densify core; behind-wall only.
    vfxlib = ensure_slice15_vfx_library()
    s15 = ensure_slice15_materials()
    m_air = s15.get("M_L70_AirframeResp") or s15.get("M_L68_AirframeANR")
    m_plate = s15.get("M_L70_PlateResp") or s15.get("M_L68_PlateANR")
    m_rust = s15.get("M_L70_RustResp") or s15.get("M_L68_RustANR")
    m_brick = s15.get("M_L70_BrickResp") or s15.get("M_L68_BrickANR")
    m_conc = s15.get("M_L70_ConcreteResp") or s15.get("M_L68_ConcreteANR")
    m_hot = s15.get("M_L70_MuzzleResp") or s15.get("M_L61_MuzzleHot")
    m_glow = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or m_hot
    m_disc = s15.get("M_L72_PropDiscBright") or s15.get("M_L71_PropDiscMotion") or load_mat("/Game/Skyguard/Materials/M_PropDisc")
    m_blade = s15.get("M_L72_PropBladeEdge") or s15.get("M_L71_PropBlade") or m_air
    m_muzzle_emi = s15.get("M_L71_VFX_MuzzleEmi") or m_hot
    m_spark_emi = s15.get("M_L71_VFX_SparkEmi") or m_hot
    m_tracer_emi = s15.get("M_L71_VFX_TracerEmi") or m_hot
    m_foam_emi = s15.get("M_L71_VFX_FoamEmi") or m_plate
    m_expl_emi = s15.get("M_L71_VFX_ExplEmi") or m_hot
    m_card_hot = s15.get("M_L72_VFX_CardHot") or m_muzzle_emi
    m_card_soft = s15.get("M_L72_VFX_CardSoft") or m_spark_emi
    m_card_cool = s15.get("M_L72_VFX_CardCool") or m_foam_emi
    m_card_expl = s15.get("M_L72_VFX_CardExpl") or m_expl_emi
    m_rifle = load_mat("/Game/Skyguard/Materials/M_RifleTan") or m_plate
    sm_prop = load_sm("/Game/Skyguard/Meshes/Hero/propeller_proxy")
    sm_yak = load_sm("/Game/Skyguard/Meshes/Hero/yak52_hd_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/yak52_proxy")
    sm_rifle_m = load_sm("/Game/Skyguard/Meshes/Hero/rifle_ads_proxy")
    sm_drone = load_sm("/Game/Skyguard/Meshes/Hero/shahed_proxy")
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx = cam[0] + dist
        cy, cz = cam[1], cam[2]
        # Prop PBR motion densify (behind wall)
        if name in ("Prop", "PropHub", "PropNose", "YakBeauty"):
            spawn_sm(sphere, (bx + 3.76, cy + 0.0, cz + 0.12), (1.25, 0.05, 1.25), None, PREFIX + "TA15_PropDiscOuter_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.77, cy + 0.0, cz + 0.12), (0.85, 0.045, 0.85), None, PREFIX + "TA15_PropDiscMid_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.78, cy + 0.0, cz + 0.12), (0.45, 0.04, 0.45), None, PREFIX + "TA15_PropDiscInner_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.79, cy + 0.0, cz + 0.12), (0.22, 0.08, 0.22), None, PREFIX + "TA15_PropHub_%s" % name, mat=m_plate)
            for k in range(10):
                ang = k * 18.0
                spawn_sm(cube, (bx + 3.8, cy + 0.15 * ((k % 2) * 2 - 1), cz + 0.12), (0.028, 1.1, 0.05), unreal.Rotator(0, ang, 6 + k), PREFIX + "TA15_PropBlade_%s_%d" % (name, k), mat=m_blade)
            for k in range(8):
                spawn_sm(cube, (bx + 3.75, cy + 0.18 * (k - 3.5), cz + 0.12), (0.018, 0.95, 0.03), unreal.Rotator(0, k * 12, 0), PREFIX + "TA15_PropStreak_%s_%d" % (name, k), mat=m_disc)
            if sm_prop:
                spawn_sm(sm_prop, (bx + 3.84, cy + 0.0, cz + 0.1), (0.48, 0.48, 0.48), unreal.Rotator(0, 0, 35), PREFIX + "TA15_PropHero_%s" % name, mats=[m_blade, m_air, m_plate, m_disc])
            if sm_yak and name == "YakBeauty":
                spawn_sm(sm_yak, (bx + 3.66, cy - 0.08, cz - 0.28), (0.64, 0.64, 0.64), unreal.Rotator(0, 90, 0), PREFIX + "TA15_YakHero", mats=[m_air, m_plate, m_rust, m_glow])
            # single bounded authored NS variants + legacy systems
            spawn_niagara(PREFIX + "TA15_NS_PropWashAuth_%s" % name, (bx + 3.76, cy + 0.02, cz + 0.02), "NS_L72_PropWashAuth", (0.18, 0.18, 0.18), bound=True)
            spawn_niagara(PREFIX + "TA15_NS_PropWash_%s" % name, (bx + 3.78, cy + 0.04, cz + 0.03), "NS_PropWash", (0.16, 0.16, 0.16), bound=True)
            if name in ("YakBeauty", "Prop"):
                spawn_niagara(PREFIX + "TA15_NS_Contrail_%s" % name, (bx + 3.92, cy + 0.05, cz + 0.0), "NS_ContrailRibbon", (0.16, 0.16, 0.16), bound=True)
            spawn_sm(sphere, (bx + 3.88, cy - 0.28, cz - 0.02), (0.06, 0.06, 0.06), None, PREFIX + "TA15_Exhaust_%s" % name, mat=m_muzzle_emi)
        # Airframe densify
        if name in ("YakBeauty", "Cockpit", "ADS", "Prop"):
            spawn_sm(cube, (bx + 3.54, cy + 0.08, cz + 0.06), (0.05, 1.35, 0.78), None, PREFIX + "TA15_AirResp_%s" % name, mat=m_air)
            spawn_sm(cube, (bx + 3.58, cy - 0.48, cz - 0.04), (0.045, 1.0, 0.52), None, PREFIX + "TA15_PlateResp_%s" % name, mat=m_plate)
            spawn_sm(cube, (bx + 3.56, cy + 0.62, cz - 0.14), (0.04, 0.48, 0.16), None, PREFIX + "TA15_RustResp_%s" % name, mat=m_rust)
            for k in range(10):
                spawn_sm(sphere, (bx + 3.59, cy - 0.6 + k * 0.14, cz + 0.42), (0.025, 0.025, 0.025), None, PREFIX + "TA15_Rivet_%s_%d" % (name, k), mat=m_plate)
        # Authored VFX language: emissive cards (thin quads) + cores + single bounded NS
        if name in ("Combat", "ADS", "Wide"):
            if sm_rifle_m and name in ("ADS", "Combat"):
                spawn_sm(sm_rifle_m, (bx + 3.32, cy + 0.06, cz - 0.04), (0.42, 0.42, 0.42), unreal.Rotator(0, 90, 0), PREFIX + "TA15_RifleHero_%s" % name, mats=[m_rifle, m_plate, m_rust, m_hot])
            # authored NS shells (new) + existing systems, all small/bounded
            spawn_niagara(PREFIX + "TA15_NS_MuzzleAuth_%s" % name, (bx + 3.46, cy + 0.16, cz + 0.08), "NS_L72_MuzzleAuth", (0.16, 0.16, 0.16), bound=True)
            spawn_niagara(PREFIX + "TA15_NS_Muzzle_%s" % name, (bx + 3.47, cy + 0.17, cz + 0.09), "NS_MuzzleFlash", (0.15, 0.15, 0.15), bound=True)
            spawn_niagara(PREFIX + "TA15_NS_Smoke_%s" % name, (bx + 3.49, cy + 0.12, cz + 0.05), "NS_GunSmoke", (0.14, 0.14, 0.14), bound=True)
            spawn_niagara(PREFIX + "TA15_NS_SparkAuth_%s" % name, (bx + 3.56, cy + 0.98, cz + 0.3), "NS_L72_SparkAuth", (0.18, 0.18, 0.18), bound=True)
            spawn_niagara(PREFIX + "TA15_NS_Sparks_%s" % name, (bx + 3.57, cy + 0.99, cz + 0.31), "NS_HitSparks", (0.17, 0.17, 0.17), bound=True)
            spawn_niagara(PREFIX + "TA15_NS_Tracer_%s" % name, (bx + 3.52, cy + 0.22, cz + 0.16), "NS_TracerBurst", (0.14, 0.14, 0.14), bound=True)
            # soft sprite cards (thin cubes as billboards)
            for k in range(5):
                spawn_sm(cube, (bx + 3.45 + k * 0.02, cy + 0.18 + k * 0.03, cz + 0.1 + k * 0.02), (0.01, 0.22 - k * 0.02, 0.18 - k * 0.015), unreal.Rotator(0, -10 + k * 8, 0), PREFIX + "TA15_MuzzleCard_%s_%d" % (name, k), mat=m_card_hot)
            for k in range(6):
                spawn_sm(cube, (bx + 3.54, cy + 0.75 + k * 0.05, cz + 0.22 + (k % 2) * 0.04), (0.01, 0.12, 0.1), unreal.Rotator(0, k * 20, 15), PREFIX + "TA15_SparkCard_%s_%d" % (name, k), mat=m_card_soft)
            spawn_sm(sphere, (bx + 3.47, cy + 0.18, cz + 0.1), (0.09, 0.09, 0.09), None, PREFIX + "TA15_MuzzleCore_%s" % name, mat=m_muzzle_emi)
            for k in range(8):
                spawn_sm(cube, (bx + 3.4 + k * 0.03, cy + 0.14 + k * 0.045, cz + 0.06 + k * 0.025), (0.15 - k * 0.012, 0.014, 0.014), unreal.Rotator(0, -12 + k * 5, 0), PREFIX + "TA15_Filament_%s_%d" % (name, k), mat=m_tracer_emi)
            for k in range(7):
                spawn_sm(sphere, (bx + 3.53, cy - 0.02 + k * 0.05, cz - 0.04 + k * 0.02), (0.022, 0.022, 0.022), None, PREFIX + "TA15_Shell_%s_%d" % (name, k), mat=m_plate)
            if name == "Combat":
                spawn_niagara(PREFIX + "TA15_NS_ExplAuth", (bx + 3.62, cy - 0.9, cz + 0.52), "NS_L72_ExplAuth", (0.2, 0.2, 0.2), bound=True)
                spawn_niagara(PREFIX + "TA15_NS_Expl", (bx + 3.63, cy - 0.91, cz + 0.53), "NS_DroneExplosion", (0.18, 0.18, 0.18), bound=True)
                spawn_niagara(PREFIX + "TA15_NS_Flak", (bx + 3.6, cy + 1.08, cz + 0.48), "NS_FlakBurst", (0.16, 0.16, 0.16), bound=True)
                if sm_drone:
                    spawn_sm(sm_drone, (bx + 3.64, cy - 0.95, cz + 0.5), (0.4, 0.4, 0.4), unreal.Rotator(0, 90, 4), PREFIX + "TA15_Shahed", mats=[m_plate, m_air, m_rust, m_hot])
                spawn_sm(sphere, (bx + 3.62, cy - 0.9, cz + 0.58), (0.16, 0.16, 0.16), None, PREFIX + "TA15_ExplCore", mat=m_card_expl)
                for k in range(6):
                    spawn_sm(cube, (bx + 3.58, cy - 1.0 + k * 0.06, cz + 0.45 + (k % 2) * 0.05), (0.01, 0.18, 0.14), unreal.Rotator(0, k * 25, 10), PREFIX + "TA15_ExplCard_%d" % k, mat=m_card_expl)
                for k in range(12):
                    spawn_sm(sphere, (bx + 3.55, cy - 1.2 + k * 0.05, cz + 0.45 + (k % 3) * 0.04), (0.026, 0.026, 0.026), None, PREFIX + "TA15_Debris_%d" % k, mat=m_spark_emi if k % 2 == 0 else m_plate)
        # City/ocean densify
        if name in ("City", "Harbor", "Wide"):
            spawn_sm(cube, (bx + 3.56, cy + 0.3, cz - 0.3), (0.06, 1.2, 1.45), None, PREFIX + "TA15_BrickResp_%s" % name, mat=m_brick)
            spawn_sm(cube, (bx + 3.6, cy - 0.9, cz - 0.1), (0.055, 1.02, 1.15), None, PREFIX + "TA15_ConcResp_%s" % name, mat=m_conc)
            spawn_sm(cube, (bx + 3.58, cy + 0.0, cz + 0.24), (0.05, 0.85, 0.95), None, PREFIX + "TA15_CityHero_%s" % name, mats=[m_brick, m_conc, m_rust])
            for ix in range(4):
                for iy in range(4):
                    spawn_sm(cube, (bx + 3.57, cy - 0.3 + ix * 0.32, cz - 0.2 + iy * 0.3), (0.025, 0.14, 0.18), None, PREFIX + "TA15_Win_%s_%d_%d" % (name, ix, iy), mat=load_mat("/Game/Skyguard/Materials/M_CityGlass") or m_plate)
            if name == "City":
                spawn_niagara(PREFIX + "TA15_NS_CityFire", (bx + 3.62, cy + 0.4, cz + 0.76), "NS_CityFire", (0.18, 0.18, 0.18), bound=True)
            spawn_sm(sphere, (bx + 3.66, cy + 0.08, cz + 0.88), (0.05, 0.05, 0.05), None, PREFIX + "TA15_CityPin_%s" % name, mat=m_muzzle_emi)
        if name in ("Ocean", "Harbor"):
            spawn_niagara(PREFIX + "TA15_NS_SprayAuth_%s" % name, (bx + 3.52, cy - 0.22, cz - 0.56), "NS_L72_SprayAuth", (0.24, 0.24, 0.24), bound=True)
            spawn_niagara(PREFIX + "TA15_NS_Spray_%s" % name, (bx + 3.53, cy - 0.23, cz - 0.57), "NS_OceanSpray", (0.22, 0.22, 0.22), bound=True)
            spawn_niagara(PREFIX + "TA15_NS_Splash_%s" % name, (bx + 3.55, cy - 0.08, cz - 0.64), "NS_WaterSplash", (0.18, 0.18, 0.18), bound=True)
            for k in range(12):
                spawn_sm(sphere, (bx + 3.5, cy - 0.9 + k * 0.1, cz - 0.46 + (k % 2) * 0.05), (0.05 + (k % 2) * 0.012, 0.05 + (k % 2) * 0.012, 0.05 + (k % 2) * 0.012), None, PREFIX + "TA15_Foam_%s_%d" % (name, k), mat=m_foam_emi)
            for k in range(5):
                spawn_sm(cube, (bx + 3.51, cy - 0.5 + k * 0.12, cz - 0.4), (0.01, 0.2, 0.12), unreal.Rotator(0, k * 18, 0), PREFIX + "TA15_FoamCard_%s_%d" % (name, k), mat=m_card_cool)
    log("slice15 authored niagara shells + denser vfx language densify applied (no extra point lights)")
'''
text = text.replace(done, inject + "\n    " + done, 1)
text = re.sub(
    r'log\("loop72 .*? start"\)',
    'log("loop72 L71 freeze + true-art slice15 authored Niagara shells + denser VFX language start")',
    text,
    count=1,
)
text = re.sub(
    r'note=l\d+_freeze_true_art_slice15[^\n\"]*',
    'note=l71_freeze_true_art_slice15_authored_niagara_denser_vfx',
    text,
)

if "def ensure_slice15_materials" not in text:
    raise SystemExit("ensure_slice15_materials missing")
if "def ensure_slice15_vfx_library" not in text:
    raise SystemExit("ensure_slice15_vfx_library missing")

dst.write_text(text, encoding="utf-8")
# repair truncated note lines if any
lines = dst.read_text(encoding="utf-8", errors="replace").splitlines(True)
out = []
for line in lines:
    if "note=l71_freeze_true_art_slice15_authored_niagara_denser_vfx" in line and "f.write" in line and not line.rstrip().endswith('")'):
        out.append('        f.write("note=l71_freeze_true_art_slice15_authored_niagara_denser_vfx\\n")\n')
    else:
        out.append(line)
text = "".join(out)
ast.parse(text)
dst.write_text(text, encoding="utf-8")
print("WROTE", dst, dst.stat().st_size)
print("cam72", "AAA_Cam_L72_" in text)
print("inject", "slice15 authored niagara shells" in text)
print("vfxlib", "ensure_slice15_vfx_library" in text)
print("pointlight", "spawn_point_light" in text)

ha = Path(r"D:\Skyguard52\Scripts\host_audit_loop71.py").read_text(encoding="utf-8")
ha2 = (
    ha.replace("AAA_L71", "AAA_L72")
    .replace("loop71", "loop72")
    .replace("Loop 71", "Loop 72")
    .replace("Loop71", "Loop72")
    .replace("AAA_Cam_L71_", "AAA_Cam_L72_")
)
Path(r"D:\Skyguard52\Scripts\host_audit_loop72.py").write_text(ha2, encoding="utf-8")
ast.parse(ha2)
print("AUDIT_OK")
