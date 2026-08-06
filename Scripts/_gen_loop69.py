from pathlib import Path
import re, ast

src = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop68_true_art_slice11_capture.py")
dst = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop69_true_art_slice12_capture.py")
text = src.read_text(encoding="utf-8")

repls = [
    ("AAA_L68_", "AAA_L69_"),
    ("AAA_L68", "AAA_L69"),
    ("RT_AAA_L68", "RT_AAA_L69"),
    ("loop68", "loop69"),
    ("Loop68", "Loop69"),
    ("slice11", "slice12"),
    ("Slice11", "Slice12"),
    ("_SLICE11_MATS", "_SLICE12_MATS"),
    (
        "L67 freeze + true-art slice11 stronger ANR materials + thin emissive (no FOV light stacks)",
        "L68 freeze + true-art slice12 bounded Niagara quality + prop disc fidelity (no FOV light stacks)",
    ),
    (
        "l67_freeze_true_art_slice11_stronger_anr_thin_emissive",
        "l68_freeze_true_art_slice12_bounded_niagara_prop_disc",
    ),
    ("TA11_", "TA12_"),
    ("M_L68_", "M_L69_"),  # careful: may rename mat load paths incorrectly for existing L68 mats
]
# Do NOT blind-replace M_L68_ in whole file because we want to LOAD L68 mats, not reauthor as L69 only.
# So apply name renames carefully without the M_L68_ replace.
repls = [r for r in repls if r[0] != "M_L68_"]
for a, b in repls:
    text = text.replace(a, b)
text = text.replace("AAA_Cam_L68_", "AAA_Cam_L69_")
text = text.replace("AAA_Cam_L67_", "AAA_Cam_L69_")
text = text.replace("AAA_Cam_L66_", "AAA_Cam_L69_")
text = text.replace("AAA_Cam_L65_", "AAA_Cam_L69_")

# Upgrade spawn_niagara to bounded activation
old_ni = '''def spawn_niagara(label, loc, asset_name, scale=(1,1,1)):
    try:
        a = None
        try:
            sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
            if sub:
                a = sub.spawn_actor_from_class(unreal.NiagaraActor, unreal.Vector(float(loc[0]), float(loc[1]), float(loc[2])), unreal.Rotator())
        except Exception:
            pass
        if not a:
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.NiagaraActor, unreal.Vector(float(loc[0]), float(loc[1]), float(loc[2])), unreal.Rotator()
            )
        if not a:
            return None
        a.set_actor_label(label)
        try:
            a.set_actor_scale3d(unreal.Vector(float(scale[0]), float(scale[1]), float(scale[2])))
        except Exception:
            pass
        asset = None
        path = "/Game/Skyguard/VFX/" + asset_name
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            asset = unreal.EditorAssetLibrary.load_asset(path)
        try:
            comp = a.niagara_component
            if comp and asset:
                comp.set_asset(asset)
                try:
                    comp.activate(True)
                except Exception:
                    pass
        except Exception as e:
            log("niagara set_asset fail %s %s" % (asset_name, e))
        return a
    except Exception as e:
        log("niagara spawn fail %s %s" % (asset_name, e))
        return None'''

new_ni = '''def spawn_niagara(label, loc, asset_name, scale=(1,1,1), bound=True):
    """Spawn Niagara with capture-safe bounded activation (auto-activate, no full-screen veil)."""
    try:
        a = None
        try:
            sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
            if sub:
                a = sub.spawn_actor_from_class(unreal.NiagaraActor, unreal.Vector(float(loc[0]), float(loc[1]), float(loc[2])), unreal.Rotator())
        except Exception:
            pass
        if not a:
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.NiagaraActor, unreal.Vector(float(loc[0]), float(loc[1]), float(loc[2])), unreal.Rotator()
            )
        if not a:
            return None
        a.set_actor_label(label)
        try:
            a.set_actor_scale3d(unreal.Vector(float(scale[0]), float(scale[1]), float(scale[2])))
        except Exception:
            pass
        asset = None
        path = "/Game/Skyguard/VFX/" + asset_name
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            asset = unreal.EditorAssetLibrary.load_asset(path)
        try:
            comp = a.niagara_component
            if comp and asset:
                comp.set_asset(asset)
                # bounded / capture-safe activation preferences
                if bound:
                    for prop, val in [
                        ("auto_activate", True),
                        ("bAutoActivate", True),
                        ("bAllowScalability", True),
                    ]:
                        try:
                            comp.set_editor_property(prop, val)
                        except Exception:
                            pass
                    # keep systems local/small
                    try:
                        # re-assert small scale on component owner
                        a.set_actor_scale3d(unreal.Vector(float(scale[0]), float(scale[1]), float(scale[2])))
                    except Exception:
                        pass
                try:
                    comp.activate(True)
                except Exception:
                    try:
                        comp.set_active(True, True)
                    except Exception:
                        pass
                try:
                    # force a reinit so stills see particles
                    comp.reinitialize_system()
                except Exception:
                    pass
        except Exception as e:
            log("niagara set_asset fail %s %s" % (asset_name, e))
        return a
    except Exception as e:
        log("niagara spawn fail %s %s" % (asset_name, e))
        return None'''

if old_ni not in text:
    raise SystemExit('spawn_niagara block not found for replace')
text = text.replace(old_ni, new_ni, 1)

done = 'log("loop69 true-art slice12 densify done")'
if done not in text:
    m = re.search(r'log\("loop69.*?densify done"\)', text)
    raise SystemExit('done marker missing: ' + str(m.group(0) if m else None))

inject = r'''
    # Slice12: bounded Niagara quality + prop disc fidelity + stronger multi-slot hero accents
    # HARD RULE: no extra PointLight FOV stacks (L66 reject). Keep HF densify core intact.
    s12 = ensure_slice12_materials()
    m_air = s12.get("M_L68_AirframeANR") or s12.get("M_L69_AirframeANR") or s12.get("M_L63_AirframeHF") or s12.get("M_L64_AirframeAO")
    m_plate = s12.get("M_L68_PlateANR") or s12.get("M_L69_PlateANR") or s12.get("M_L63_PlateHF") or s12.get("M_L64_PlateAO")
    m_rust = s12.get("M_L68_RustANR") or s12.get("M_L69_RustANR") or s12.get("M_L63_RustHF") or s12.get("M_L64_RustDetail")
    m_brick = s12.get("M_L68_BrickANR") or s12.get("M_L69_BrickANR") or s12.get("M_L63_BrickHF")
    m_conc = s12.get("M_L68_ConcreteANR") or s12.get("M_L69_ConcreteANR") or s12.get("M_L63_ConcreteHF")
    m_hot = s12.get("M_L61_MuzzleHot") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Muzzle")
    m_glow = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or m_hot
    m_disc = load_mat("/Game/Skyguard/Materials/M_PropDisc") or m_plate
    m_rifle = load_mat("/Game/Skyguard/Materials/M_RifleTan") or m_plate
    sm_prop = load_sm("/Game/Skyguard/Meshes/Hero/propeller_proxy")
    sm_yak = load_sm("/Game/Skyguard/Meshes/Hero/yak52_hd_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/yak52_proxy")
    sm_rifle_m = load_sm("/Game/Skyguard/Meshes/Hero/rifle_ads_proxy")
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx = cam[0] + dist
        cy, cz = cam[1], cam[2]
        # Prop fidelity: motion disc + blade accents behind wall only
        if name in ("Prop", "PropHub", "PropNose", "YakBeauty"):
            # translucent-ish disc proxy via flat cylinder of cubes + prop disc mat
            spawn_sm(sphere, (bx + 3.72, cy + 0.0, cz + 0.12), (0.95, 0.08, 0.95), None, PREFIX + "TA12_PropDisc_%s" % name, mat=m_disc)
            for k in range(4):
                ang = k * 45.0
                spawn_sm(cube, (bx + 3.74, cy + 0.35 * (1 if k % 2 == 0 else -1), cz + 0.12 + (0.15 if k > 1 else -0.15)), (0.04, 0.85, 0.08), unreal.Rotator(0, ang, 12), PREFIX + "TA12_PropBlade_%s_%d" % (name, k), mat=m_plate)
            if sm_prop:
                spawn_sm(sm_prop, (bx + 3.78, cy + 0.0, cz + 0.1), (0.42, 0.42, 0.42), unreal.Rotator(0, 0, 20), PREFIX + "TA12_PropHero_%s" % name, mats=[m_plate, m_air, m_rust, m_disc])
            # single bounded prop wash / contrail only
            spawn_niagara(PREFIX + "TA12_NS_PropWash_%s" % name, (bx + 3.7, cy + 0.05, cz + 0.05), "NS_PropWash", (0.24, 0.24, 0.24), bound=True)
            if name in ("YakBeauty", "Prop"):
                spawn_niagara(PREFIX + "TA12_NS_Contrail_%s" % name, (bx + 3.85, cy + 0.1, cz + 0.0), "NS_ContrailRibbon", (0.22, 0.22, 0.22), bound=True)
            if sm_yak and name == "YakBeauty":
                spawn_sm(sm_yak, (bx + 3.6, cy - 0.15, cz - 0.35), (0.58, 0.58, 0.58), unreal.Rotator(0, 90, 0), PREFIX + "TA12_YakHero", mats=[m_air, m_plate, m_rust, m_glow])
            # tiny emissive exhaust pin
            spawn_sm(sphere, (bx + 3.8, cy - 0.35, cz - 0.05), (0.05, 0.05, 0.05), None, PREFIX + "TA12_ExhaustPin_%s" % name, mat=m_glow)
        # Aircraft / cockpit multi-slot ANR seams (thin)
        if name in ("YakBeauty", "Cockpit", "ADS"):
            spawn_sm(cube, (bx + 3.5, cy + 0.15, cz + 0.12), (0.05, 1.15, 0.65), None, PREFIX + "TA12_AirANR_%s" % name, mat=m_air)
            spawn_sm(cube, (bx + 3.54, cy - 0.5, cz - 0.05), (0.045, 0.8, 0.4), None, PREFIX + "TA12_PlateANR_%s" % name, mat=m_plate)
            spawn_sm(cube, (bx + 3.52, cy + 0.55, cz - 0.18), (0.04, 0.35, 0.12), None, PREFIX + "TA12_RustANR_%s" % name, mat=m_rust)
            for k in range(5):
                spawn_sm(sphere, (bx + 3.55, cy - 0.4 + k * 0.18, cz + 0.35), (0.03, 0.03, 0.03), None, PREFIX + "TA12_Rivet_%s_%d" % (name, k), mat=m_plate)
        # Weapon/combat: single bounded muzzle/sparks + rifle multi-slot
        if name in ("Combat", "ADS"):
            if sm_rifle_m and name == "ADS":
                spawn_sm(sm_rifle_m, (bx + 3.25, cy + 0.12, cz - 0.08), (0.36, 0.36, 0.36), unreal.Rotator(0, 90, 0), PREFIX + "TA12_RifleHero", mats=[m_rifle, m_plate, m_rust, m_hot])
            spawn_niagara(PREFIX + "TA12_NS_Muzzle_%s" % name, (bx + 3.4, cy + 0.22, cz + 0.14), "NS_MuzzleFlash", (0.22, 0.22, 0.22), bound=True)
            spawn_niagara(PREFIX + "TA12_NS_GunSmoke_%s" % name, (bx + 3.42, cy + 0.18, cz + 0.1), "NS_GunSmoke", (0.2, 0.2, 0.2), bound=True)
            spawn_niagara(PREFIX + "TA12_NS_Sparks_%s" % name, (bx + 3.5, cy + 0.9, cz + 0.35), "NS_HitSparks", (0.26, 0.26, 0.26), bound=True)
            spawn_sm(sphere, (bx + 3.41, cy + 0.24, cz + 0.16), (0.055, 0.055, 0.055), None, PREFIX + "TA12_MuzzleCore_%s" % name, mat=m_hot)
            if name == "Combat":
                spawn_niagara(PREFIX + "TA12_NS_Expl_%s" % name, (bx + 3.55, cy - 0.95, cz + 0.55), "NS_DroneExplosion", (0.28, 0.28, 0.28), bound=True)
                spawn_niagara(PREFIX + "TA12_NS_Flak_%s" % name, (bx + 3.52, cy + 1.0, cz + 0.5), "NS_FlakBurst", (0.24, 0.24, 0.24), bound=True)
        # City/ocean bounded VFX + ANR facade accents
        if name in ("City", "Harbor", "Wide"):
            spawn_sm(cube, (bx + 3.52, cy + 0.35, cz - 0.35), (0.06, 1.0, 1.25), None, PREFIX + "TA12_BrickANR_%s" % name, mat=m_brick)
            spawn_sm(cube, (bx + 3.56, cy - 0.85, cz - 0.15), (0.055, 0.85, 0.95), None, PREFIX + "TA12_ConcANR_%s" % name, mat=m_conc)
            spawn_sm(cube, (bx + 3.54, cy + 0.05, cz + 0.25), (0.05, 0.65, 0.75), None, PREFIX + "TA12_CityHero_%s" % name, mats=[m_brick, m_conc, m_rust])
            if name == "City":
                spawn_niagara(PREFIX + "TA12_NS_CityFire", (bx + 3.55, cy + 0.45, cz + 0.75), "NS_CityFire", (0.26, 0.26, 0.26), bound=True)
            spawn_sm(sphere, (bx + 3.6, cy + 0.12, cz + 0.88), (0.04, 0.04, 0.04), None, PREFIX + "TA12_CityPin_%s" % name, mat=m_glow)
        if name in ("Ocean", "Harbor"):
            spawn_niagara(PREFIX + "TA12_NS_Spray_%s" % name, (bx + 3.45, cy - 0.3, cz - 0.62), "NS_OceanSpray", (0.34, 0.34, 0.34), bound=True)
            spawn_niagara(PREFIX + "TA12_NS_Splash_%s" % name, (bx + 3.48, cy - 0.15, cz - 0.7), "NS_WaterSplash", (0.28, 0.28, 0.28), bound=True)
    log("slice12 bounded niagara + prop disc fidelity densify applied (no extra point lights)")
'''

text = text.replace(done, inject + "\n    " + done, 1)
# ensure ensure_slice12 exists (renamed from 11). Keep L68 mat names inside anr specs if renamed incorrectly.
# After slice rename, ensure function may reference M_L68 in anr_specs still if we avoided M_L68 replace - good.
# But ensure function name should be ensure_slice12_materials from rename slice11->slice12.
if "def ensure_slice12_materials" not in text:
    raise SystemExit("ensure_slice12_materials missing")

# If anr specs still use M_L68 names that is fine (load existing). Also add aliases in inject via get.
# Fix main start string if still says L64 freeze
text = text.replace(
    'log("loop69 L64 freeze + true-art slice12 multi-slot hero materials + multi-niagara start")',
    'log("loop69 L68 freeze + true-art slice12 bounded Niagara quality + prop disc fidelity start")',
)
text = text.replace(
    "note=l64_freeze_true_art_slice12_multislot_hero_multiniagara",
    "note=l68_freeze_true_art_slice12_bounded_niagara_prop_disc",
)

dst.write_text(text, encoding="utf-8")
ast.parse(text)
print("WROTE", dst, dst.stat().st_size)
print("cam69", "AAA_Cam_L69_" in text)
print("spawn_bound", "bound=True" in text)
print("propdisc", "TA12_PropDisc" in text)
print("pointlight", "spawn_point_light" in text)
print("ensure12", "ensure_slice12_materials" in text)

ha = Path(r"D:\Skyguard52\Scripts\host_audit_loop68.py").read_text(encoding="utf-8")
ha2 = (
    ha.replace("AAA_L68", "AAA_L69")
    .replace("loop68", "loop69")
    .replace("Loop 68", "Loop 69")
    .replace("Loop68", "Loop69")
    .replace("AAA_Cam_L68_", "AAA_Cam_L69_")
)
Path(r"D:\Skyguard52\Scripts\host_audit_loop69.py").write_text(ha2, encoding="utf-8")
ast.parse(ha2)
print("AUDIT_OK")
