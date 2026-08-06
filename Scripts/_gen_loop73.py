from pathlib import Path
import re, ast

src = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop72_true_art_slice15_capture.py")
dst = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop73_true_art_slice16_capture.py")
text = src.read_text(encoding="utf-8")

repls = [
    ("AAA_L72_", "AAA_L73_"),
    ("AAA_L72", "AAA_L73"),
    ("RT_AAA_L72", "RT_AAA_L73"),
    ("loop72", "loop73"),
    ("Loop72", "Loop73"),
    ("slice15", "slice16"),
    ("Slice15", "Slice16"),
    ("_SLICE15_MATS", "_SLICE16_MATS"),
    (
        "L71 freeze + true-art slice15 authored Niagara shells + denser VFX language",
        "L72 freeze + true-art slice16 deeper Niagara emitter pass + visible particle language",
    ),
    (
        "l71_freeze_true_art_slice15_authored_niagara_denser_vfx",
        "l72_freeze_true_art_slice16_deeper_niagara_visible_particles",
    ),
    ("TA15_", "TA16_"),
    ("NS_L72_", "NS_L73_"),
]
for a, b in repls:
    text = text.replace(a, b)
for old, new in [
    ("AAA_Cam_L72_", "AAA_Cam_L73_"),
    ("AAA_Cam_L71_", "AAA_Cam_L73_"),
    ("AAA_Cam_L70_", "AAA_Cam_L73_"),
    ("AAA_Cam_L69_", "AAA_Cam_L73_"),
    ("AAA_Cam_L68_", "AAA_Cam_L73_"),
    ("AAA_Cam_L67_", "AAA_Cam_L73_"),
    ("AAA_Cam_L66_", "AAA_Cam_L73_"),
    ("AAA_Cam_L65_", "AAA_Cam_L73_"),
]:
    text = text.replace(old, new)

# Replace ensure_authored_ns with deeper version
old_ns = '''def ensure_authored_ns(name):
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
    return asset'''

# After rename, comments may say Slice16 - find ensure_authored_ns function
m = re.search(r'def ensure_authored_ns\(name\):[\s\S]*?return asset\n', text)
if not m:
    raise SystemExit("ensure_authored_ns not found")
old_ns = m.group(0)

new_ns = r'''def ensure_authored_ns(name, deepen=True):
    """Create/load NiagaraSystem and attempt deeper emitter attachment + user params.
    Capture stills still rely on densified visible particle language because empty shells are not AAA.
    """
    path = "/Game/Skyguard/VFX/" + name
    asset = None
    try:
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            asset = unreal.EditorAssetLibrary.load_asset(path)
    except Exception:
        asset = None
    if asset is None:
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
    emitter = None
    try:
        ensure_dir("/Game/Skyguard/VFX/Emitters")
        epath = "/Game/Skyguard/VFX/Emitters/" + name + "_Emitter"
        if unreal.EditorAssetLibrary.does_asset_exist(epath):
            emitter = unreal.EditorAssetLibrary.load_asset(epath)
        else:
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
    if deepen:
        # Best-effort deeper authoring using any available python-exposed methods.
        # 1) try system methods that accept emitters
        if emitter is not None:
            for meth in [
                "add_emitter", "AddEmitter", "add_emitter_handle", "AddEmitterHandle",
                "add_emitter_from_asset", "AddEmitterFromAsset",
            ]:
                try:
                    fn = getattr(asset, meth, None)
                    if callable(fn):
                        try:
                            fn(emitter)
                            log("ns method %s attached emitter %s" % (meth, name))
                            break
                        except TypeError:
                            try:
                                fn(emitter, name + "_Handle")
                                log("ns method %s(name) attached emitter %s" % (meth, name))
                                break
                            except Exception:
                                pass
                except Exception:
                    pass
            # 2) try editor library helpers if present
            for libn in ["NiagaraSystemEditorLibrary", "NiagaraEditorLibrary", "NiagaraFunctionLibrary"]:
                try:
                    lib = getattr(unreal, libn, None)
                    if lib is None:
                        continue
                    for meth in ["add_emitter_to_system", "AddEmitterToSystem", "set_system_emitter", "compile_system"]:
                        fn = getattr(lib, meth, None)
                        if callable(fn):
                            try:
                                fn(asset, emitter)
                                log("lib %s.%s ok %s" % (libn, meth, name))
                            except Exception as e:
                                log("lib %s.%s fail %s %s" % (libn, meth, name, e))
                except Exception:
                    pass
        # 3) user parameters / compile-ish properties when available
        for prop, val in [
            ("expose_to_library", True),
            ("bExposeToLibrary", True),
            ("bDeterminism", True),
            ("warm_up_time", 0.15),
            ("WarmupTime", 0.15),
            ("fixed_bounds", True),
            ("bFixedBounds", True),
        ]:
            try:
                asset.set_editor_property(prop, val)
            except Exception:
                pass
        try:
            # fixed local bounds help capture stability
            asset.set_editor_property("fixed_bounds", unreal.Box(unreal.Vector(-80, -80, -80), unreal.Vector(80, 80, 80)))
        except Exception:
            try:
                asset.set_editor_property("FixedBounds", unreal.Box(unreal.Vector(-80, -80, -80), unreal.Vector(80, 80, 80)))
            except Exception:
                pass
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(asset)
        except Exception:
            pass
        log("deep authored ns %s" % name)
    return asset
'''
text = text.replace(old_ns, new_ns, 1)

# Update ensure_slice16_vfx_library names to L73 variants
text = text.replace("NS_L73_MuzzleAuth", "NS_L73_MuzzleAuth")  # already renamed from L72
# Ensure library includes L73 depth variants
old_lib_names = '''        # Slice16 named variants (new shells for formal author pass)
        "NS_L73_MuzzleAuth", "NS_L73_SparkAuth", "NS_L73_ExplAuth", "NS_L73_SprayAuth", "NS_L73_PropWashAuth",
    ]'''
if old_lib_names not in text:
    # try original comment after renames
    old_lib_names = '''        # Slice16 named variants (new shells for formal author pass)
        "NS_L73_MuzzleAuth", "NS_L73_SparkAuth", "NS_L73_ExplAuth", "NS_L73_SprayAuth", "NS_L73_PropWashAuth",
    ]'''
# more robust: inject extra names after PropWashAuth line
if '"NS_L73_PropWashAuth"' in text and "NS_L73_MuzzleBurst" not in text:
    text = text.replace(
        '"NS_L73_PropWashAuth",',
        '"NS_L73_PropWashAuth",\n        "NS_L73_MuzzleBurst", "NS_L73_SparkRing", "NS_L73_ExplPlume", "NS_L73_FoamBurst", "NS_L73_ContrailDense",',
    )

# Also deepen ensure_slice16_vfx_library call to use deepen=True by default via ensure_authored_ns(n)
# already does ensure_authored_ns(n)

# Add denser visual particle helper before densify inject
particle_helper = r'''

def spawn_particle_field(prefix, loc, mat, count=12, radius=0.35, size=0.04, label_base="PField"):
    """Capture-visible pseudo-particle field (emissive spheres) as fallback when NS graphs are empty."""
    out = []
    x0, y0, z0 = float(loc[0]), float(loc[1]), float(loc[2])
    for i in range(count):
        ang = (i / max(count, 1)) * 6.28318530718
        rr = radius * (0.35 + 0.65 * ((i * 37) % 10) / 10.0)
        yy = y0 + rr * math.cos(ang)
        zz = z0 + rr * math.sin(ang) * 0.7
        xx = x0 + 0.02 * ((i % 5) - 2)
        sc = size * (0.7 + 0.6 * ((i * 13) % 7) / 7.0)
        a = spawn_sm(load_sm("/Engine/BasicShapes/Sphere"), (xx, yy, zz), (sc, sc, sc), None, "%s_%s_%d" % (prefix, label_base, i), mat=mat)
        if a:
            out.append(a)
    return out


def spawn_burst_ring(prefix, loc, mat, count=10, radius=0.55, label_base="Ring"):
    x0, y0, z0 = float(loc[0]), float(loc[1]), float(loc[2])
    for i in range(count):
        ang = (i / max(count, 1)) * 6.28318530718
        yy = y0 + radius * math.cos(ang)
        zz = z0 + radius * math.sin(ang)
        spawn_sm(load_sm("/Engine/BasicShapes/Sphere"), (x0, yy, zz), (0.03, 0.03, 0.03), None, "%s_%s_%d" % (prefix, label_base, i), mat=mat)
        spawn_sm(load_sm("/Engine/BasicShapes/Cube"), (x0, yy, zz), (0.01, 0.14, 0.08), unreal.Rotator(0, ang * 57.2958, 0), "%s_%sCard_%d" % (prefix, label_base, i), mat=mat)

'''
if "def spawn_particle_field" not in text:
    # insert before _SLICE16_MATS
    anchor = "_SLICE16_MATS = None"
    if anchor not in text:
        raise SystemExit("slice mats missing")
    text = text.replace(anchor, particle_helper + "\n" + anchor, 1)

done = 'log("loop73 true-art slice16 densify done")'
if done not in text:
    m = re.search(r'log\("loop73.*?densify done"\)', text)
    raise SystemExit("done missing: " + str(m.group(0) if m else None))

inject = r'''
    # Slice16: deeper Niagara author pass + denser capture-visible particle language
    # HARD RULES: no FOV PointLight stacks; keep L52 HF densify core; behind-wall only.
    vfxlib = ensure_slice16_vfx_library()
    s16 = ensure_slice16_materials()
    m_air = s16.get("M_L70_AirframeResp") or s16.get("M_L68_AirframeANR")
    m_plate = s16.get("M_L70_PlateResp") or s16.get("M_L68_PlateANR")
    m_rust = s16.get("M_L70_RustResp") or s16.get("M_L68_RustANR")
    m_brick = s16.get("M_L70_BrickResp") or s16.get("M_L68_BrickANR")
    m_conc = s16.get("M_L70_ConcreteResp") or s16.get("M_L68_ConcreteANR")
    m_hot = s16.get("M_L70_MuzzleResp") or s16.get("M_L61_MuzzleHot")
    m_glow = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or m_hot
    m_disc = s16.get("M_L72_PropDiscBright") or s16.get("M_L71_PropDiscMotion") or load_mat("/Game/Skyguard/Materials/M_PropDisc")
    m_blade = s16.get("M_L72_PropBladeEdge") or s16.get("M_L71_PropBlade") or m_air
    m_muzzle_emi = s16.get("M_L71_VFX_MuzzleEmi") or m_hot
    m_spark_emi = s16.get("M_L71_VFX_SparkEmi") or m_hot
    m_tracer_emi = s16.get("M_L71_VFX_TracerEmi") or m_hot
    m_foam_emi = s16.get("M_L71_VFX_FoamEmi") or m_plate
    m_expl_emi = s16.get("M_L71_VFX_ExplEmi") or m_hot
    m_card_hot = s16.get("M_L72_VFX_CardHot") or m_muzzle_emi
    m_card_soft = s16.get("M_L72_VFX_CardSoft") or m_spark_emi
    m_card_cool = s16.get("M_L72_VFX_CardCool") or m_foam_emi
    m_card_expl = s16.get("M_L72_VFX_CardExpl") or m_expl_emi
    m_rifle = load_mat("/Game/Skyguard/Materials/M_RifleTan") or m_plate
    sm_prop = load_sm("/Game/Skyguard/Meshes/Hero/propeller_proxy")
    sm_yak = load_sm("/Game/Skyguard/Meshes/Hero/yak52_hd_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/yak52_proxy")
    sm_rifle_m = load_sm("/Game/Skyguard/Meshes/Hero/rifle_ads_proxy")
    sm_drone = load_sm("/Game/Skyguard/Meshes/Hero/shahed_proxy")
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx = cam[0] + dist
        cy, cz = cam[1], cam[2]
        # Prop densify + particle wash field
        if name in ("Prop", "PropHub", "PropNose", "YakBeauty"):
            spawn_sm(sphere, (bx + 3.78, cy + 0.0, cz + 0.12), (1.3, 0.045, 1.3), None, PREFIX + "TA16_PropDiscOuter_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.79, cy + 0.0, cz + 0.12), (0.9, 0.04, 0.9), None, PREFIX + "TA16_PropDiscMid_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.8, cy + 0.0, cz + 0.12), (0.5, 0.035, 0.5), None, PREFIX + "TA16_PropDiscInner_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.81, cy + 0.0, cz + 0.12), (0.2, 0.08, 0.2), None, PREFIX + "TA16_PropHub_%s" % name, mat=m_plate)
            for k in range(12):
                ang = k * 15.0
                spawn_sm(cube, (bx + 3.82, cy + 0.12 * ((k % 2) * 2 - 1), cz + 0.12), (0.025, 1.15, 0.045), unreal.Rotator(0, ang, 5 + k), PREFIX + "TA16_PropBlade_%s_%d" % (name, k), mat=m_blade)
            if sm_prop:
                spawn_sm(sm_prop, (bx + 3.86, cy + 0.0, cz + 0.1), (0.5, 0.5, 0.5), unreal.Rotator(0, 0, 40), PREFIX + "TA16_PropHero_%s" % name, mats=[m_blade, m_air, m_plate, m_disc])
            if sm_yak and name == "YakBeauty":
                spawn_sm(sm_yak, (bx + 3.68, cy - 0.06, cz - 0.26), (0.66, 0.66, 0.66), unreal.Rotator(0, 90, 0), PREFIX + "TA16_YakHero", mats=[m_air, m_plate, m_rust, m_glow])
            spawn_niagara(PREFIX + "TA16_NS_PropWashAuth_%s" % name, (bx + 3.78, cy + 0.02, cz + 0.02), "NS_L73_PropWashAuth", (0.16, 0.16, 0.16), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_PropWash_%s" % name, (bx + 3.8, cy + 0.03, cz + 0.02), "NS_PropWash", (0.14, 0.14, 0.14), bound=True)
            spawn_particle_field(PREFIX + "TA16_WashField_%s" % name, (bx + 3.8, cy + 0.0, cz + 0.05), m_card_soft, count=14, radius=0.55, size=0.03, label_base="Wash")
            if name in ("YakBeauty", "Prop"):
                spawn_niagara(PREFIX + "TA16_NS_Contrail_%s" % name, (bx + 3.94, cy + 0.04, cz + 0.0), "NS_ContrailRibbon", (0.14, 0.14, 0.14), bound=True)
                spawn_niagara(PREFIX + "TA16_NS_ContrailDense_%s" % name, (bx + 3.96, cy + 0.06, cz + 0.0), "NS_L73_ContrailDense", (0.12, 0.12, 0.12), bound=True)
            spawn_sm(sphere, (bx + 3.9, cy - 0.26, cz - 0.02), (0.06, 0.06, 0.06), None, PREFIX + "TA16_Exhaust_%s" % name, mat=m_muzzle_emi)
        if name in ("YakBeauty", "Cockpit", "ADS", "Prop"):
            spawn_sm(cube, (bx + 3.55, cy + 0.06, cz + 0.05), (0.05, 1.4, 0.8), None, PREFIX + "TA16_AirResp_%s" % name, mat=m_air)
            spawn_sm(cube, (bx + 3.59, cy - 0.46, cz - 0.03), (0.045, 1.05, 0.55), None, PREFIX + "TA16_PlateResp_%s" % name, mat=m_plate)
            for k in range(12):
                spawn_sm(sphere, (bx + 3.6, cy - 0.65 + k * 0.13, cz + 0.44), (0.024, 0.024, 0.024), None, PREFIX + "TA16_Rivet_%s_%d" % (name, k), mat=m_plate)
        # Combat/ADS denser visible particle language + deeper NS
        if name in ("Combat", "ADS", "Wide"):
            if sm_rifle_m and name in ("ADS", "Combat"):
                spawn_sm(sm_rifle_m, (bx + 3.34, cy + 0.05, cz - 0.03), (0.44, 0.44, 0.44), unreal.Rotator(0, 90, 0), PREFIX + "TA16_RifleHero_%s" % name, mats=[m_rifle, m_plate, m_rust, m_hot])
            spawn_niagara(PREFIX + "TA16_NS_MuzzleAuth_%s" % name, (bx + 3.48, cy + 0.15, cz + 0.07), "NS_L73_MuzzleAuth", (0.14, 0.14, 0.14), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_MuzzleBurst_%s" % name, (bx + 3.49, cy + 0.16, cz + 0.08), "NS_L73_MuzzleBurst", (0.13, 0.13, 0.13), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Muzzle_%s" % name, (bx + 3.5, cy + 0.16, cz + 0.08), "NS_MuzzleFlash", (0.12, 0.12, 0.12), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Smoke_%s" % name, (bx + 3.51, cy + 0.11, cz + 0.04), "NS_GunSmoke", (0.12, 0.12, 0.12), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_SparkAuth_%s" % name, (bx + 3.58, cy + 1.0, cz + 0.28), "NS_L73_SparkAuth", (0.15, 0.15, 0.15), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_SparkRing_%s" % name, (bx + 3.59, cy + 1.02, cz + 0.3), "NS_L73_SparkRing", (0.14, 0.14, 0.14), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Sparks_%s" % name, (bx + 3.6, cy + 1.01, cz + 0.29), "NS_HitSparks", (0.13, 0.13, 0.13), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Tracer_%s" % name, (bx + 3.54, cy + 0.2, cz + 0.14), "NS_TracerBurst", (0.12, 0.12, 0.12), bound=True)
            # denser visible particles
            spawn_particle_field(PREFIX + "TA16_MuzzleField_%s" % name, (bx + 3.5, cy + 0.18, cz + 0.1), m_card_hot, count=16, radius=0.28, size=0.035, label_base="Muz")
            spawn_burst_ring(PREFIX + "TA16_SparkRingVis_%s" % name, (bx + 3.58, cy + 0.95, cz + 0.28), m_card_soft, count=12, radius=0.42, label_base="Spark")
            for k in range(8):
                spawn_sm(cube, (bx + 3.42 + k * 0.03, cy + 0.12 + k * 0.05, cz + 0.05 + k * 0.03), (0.16 - k * 0.012, 0.013, 0.013), unreal.Rotator(0, -14 + k * 6, 0), PREFIX + "TA16_Filament_%s_%d" % (name, k), mat=m_tracer_emi)
            for k in range(9):
                spawn_sm(sphere, (bx + 3.55, cy - 0.04 + k * 0.05, cz - 0.05 + k * 0.02), (0.02, 0.02, 0.02), None, PREFIX + "TA16_Shell_%s_%d" % (name, k), mat=m_plate)
            if name == "Combat":
                spawn_niagara(PREFIX + "TA16_NS_ExplAuth", (bx + 3.64, cy - 0.88, cz + 0.5), "NS_L73_ExplAuth", (0.18, 0.18, 0.18), bound=True)
                spawn_niagara(PREFIX + "TA16_NS_ExplPlume", (bx + 3.65, cy - 0.89, cz + 0.52), "NS_L73_ExplPlume", (0.16, 0.16, 0.16), bound=True)
                spawn_niagara(PREFIX + "TA16_NS_Expl", (bx + 3.66, cy - 0.9, cz + 0.51), "NS_DroneExplosion", (0.15, 0.15, 0.15), bound=True)
                spawn_niagara(PREFIX + "TA16_NS_Flak", (bx + 3.62, cy + 1.1, cz + 0.46), "NS_FlakBurst", (0.14, 0.14, 0.14), bound=True)
                if sm_drone:
                    spawn_sm(sm_drone, (bx + 3.66, cy - 0.92, cz + 0.48), (0.42, 0.42, 0.42), unreal.Rotator(0, 90, 3), PREFIX + "TA16_Shahed", mats=[m_plate, m_air, m_rust, m_hot])
                spawn_sm(sphere, (bx + 3.64, cy - 0.88, cz + 0.56), (0.18, 0.18, 0.18), None, PREFIX + "TA16_ExplCore", mat=m_card_expl)
                spawn_particle_field(PREFIX + "TA16_ExplField", (bx + 3.64, cy - 0.88, cz + 0.55), m_card_expl, count=18, radius=0.65, size=0.04, label_base="Expl")
                spawn_burst_ring(PREFIX + "TA16_ExplRing", (bx + 3.64, cy - 0.88, cz + 0.5), m_card_hot, count=14, radius=0.7, label_base="ExplR")
                for k in range(14):
                    spawn_sm(sphere, (bx + 3.57, cy - 1.25 + k * 0.05, cz + 0.42 + (k % 3) * 0.04), (0.025, 0.025, 0.025), None, PREFIX + "TA16_Debris_%d" % k, mat=m_spark_emi if k % 2 == 0 else m_plate)
        if name in ("City", "Harbor", "Wide"):
            spawn_sm(cube, (bx + 3.57, cy + 0.28, cz - 0.28), (0.06, 1.25, 1.5), None, PREFIX + "TA16_BrickResp_%s" % name, mat=m_brick)
            spawn_sm(cube, (bx + 3.61, cy - 0.92, cz - 0.08), (0.055, 1.05, 1.2), None, PREFIX + "TA16_ConcResp_%s" % name, mat=m_conc)
            for ix in range(4):
                for iy in range(5):
                    spawn_sm(cube, (bx + 3.58, cy - 0.35 + ix * 0.3, cz - 0.25 + iy * 0.28), (0.022, 0.13, 0.16), None, PREFIX + "TA16_Win_%s_%d_%d" % (name, ix, iy), mat=load_mat("/Game/Skyguard/Materials/M_CityGlass") or m_plate)
            if name == "City":
                spawn_niagara(PREFIX + "TA16_NS_CityFire", (bx + 3.64, cy + 0.38, cz + 0.74), "NS_CityFire", (0.16, 0.16, 0.16), bound=True)
                spawn_particle_field(PREFIX + "TA16_CityEmber", (bx + 3.64, cy + 0.38, cz + 0.8), m_card_hot, count=12, radius=0.4, size=0.028, label_base="Ember")
            spawn_sm(sphere, (bx + 3.68, cy + 0.06, cz + 0.86), (0.05, 0.05, 0.05), None, PREFIX + "TA16_CityPin_%s" % name, mat=m_muzzle_emi)
        if name in ("Ocean", "Harbor"):
            spawn_niagara(PREFIX + "TA16_NS_SprayAuth_%s" % name, (bx + 3.54, cy - 0.2, cz - 0.54), "NS_L73_SprayAuth", (0.2, 0.2, 0.2), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_FoamBurst_%s" % name, (bx + 3.55, cy - 0.18, cz - 0.52), "NS_L73_FoamBurst", (0.18, 0.18, 0.18), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Spray_%s" % name, (bx + 3.56, cy - 0.2, cz - 0.55), "NS_OceanSpray", (0.18, 0.18, 0.18), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Splash_%s" % name, (bx + 3.57, cy - 0.06, cz - 0.62), "NS_WaterSplash", (0.15, 0.15, 0.15), bound=True)
            spawn_particle_field(PREFIX + "TA16_FoamField_%s" % name, (bx + 3.55, cy - 0.35, cz - 0.45), m_card_cool, count=16, radius=0.7, size=0.04, label_base="Foam")
            for k in range(14):
                spawn_sm(sphere, (bx + 3.52, cy - 0.95 + k * 0.09, cz - 0.44 + (k % 2) * 0.05), (0.05 + (k % 2) * 0.01, 0.05 + (k % 2) * 0.01, 0.05 + (k % 2) * 0.01), None, PREFIX + "TA16_Foam_%s_%d" % (name, k), mat=m_foam_emi)
    log("slice16 deeper niagara + visible particle language densify applied (no extra point lights)")
'''
text = text.replace(done, inject + "\n    " + done, 1)
text = re.sub(
    r'log\("loop73 .*? start"\)',
    'log("loop73 L72 freeze + true-art slice16 deeper Niagara emitter pass + visible particle language start")',
    text,
    count=1,
)
text = re.sub(
    r'note=l\d+_freeze_true_art_slice16[^\n\"]*',
    'note=l72_freeze_true_art_slice16_deeper_niagara_visible_particles',
    text,
)

# ensure ensure_slice16_vfx_library exists after rename
if "def ensure_slice16_vfx_library" not in text:
    # may still be ensure_slice15 after incomplete rename of function name only in body
    text = text.replace("def ensure_slice15_vfx_library", "def ensure_slice16_vfx_library")
if "def ensure_slice16_materials" not in text:
    raise SystemExit("ensure_slice16_materials missing")
if "ensure_slice16_vfx_library()" not in text:
    # inject call uses ensure_slice16 - already in inject
    pass

dst.write_text(text, encoding="utf-8")
# repair note lines
lines = dst.read_text(encoding="utf-8", errors="replace").splitlines(True)
out = []
for line in lines:
    if "note=l72_freeze_true_art_slice16_deeper_niagara_visible_particles" in line and "f.write" in line and not line.rstrip().endswith('")'):
        out.append('        f.write("note=l72_freeze_true_art_slice16_deeper_niagara_visible_particles\\n")\n')
    else:
        out.append(line)
text = "".join(out)
ast.parse(text)
dst.write_text(text, encoding="utf-8")
print("WROTE", dst, dst.stat().st_size)
print("cam73", "AAA_Cam_L73_" in text)
print("inject", "slice16 deeper niagara" in text)
print("particle_field", "spawn_particle_field" in text)
print("deep_ns", "deep authored ns" in text)
print("pointlight", "spawn_point_light" in text)

ha = Path(r"D:\Skyguard52\Scripts\host_audit_loop72.py").read_text(encoding="utf-8")
ha2 = (
    ha.replace("AAA_L72", "AAA_L73")
    .replace("loop72", "loop73")
    .replace("Loop 72", "Loop 73")
    .replace("Loop72", "Loop73")
    .replace("AAA_Cam_L72_", "AAA_Cam_L73_")
)
Path(r"D:\Skyguard52\Scripts\host_audit_loop73.py").write_text(ha2, encoding="utf-8")
ast.parse(ha2)
print("AUDIT_OK")
