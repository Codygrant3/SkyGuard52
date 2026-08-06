from pathlib import Path
import re

src = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop65_true_art_slice08_capture.py")
dst = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop66_true_art_slice09_capture.py")
text = src.read_text(encoding="utf-8")
repls = [
    ("AAA_L65_", "AAA_L66_"),
    ("AAA_L65", "AAA_L66"),
    ("RT_AAA_L65", "RT_AAA_L66"),
    ("loop65", "loop66"),
    ("Loop65", "Loop66"),
    ("slice08", "slice09"),
    ("Slice08", "Slice09"),
    ("_SLICE08_MATS", "_SLICE09_MATS"),
    (
        "L64 freeze + true-art slice08 multi-slot hero materials + multi-niagara",
        "L65 freeze + true-art slice09 lighting response + layered Niagara language",
    ),
    (
        "l64_freeze_true_art_slice08_multislot_hero_multiniagara",
        "l65_freeze_true_art_slice09_lighting_layered_niagara",
    ),
    ("TA8_", "TA9_"),
]
for a, b in repls:
    text = text.replace(a, b)

helper = r'''

def spawn_point_light(label, loc, intensity=120000.0, radius=1800.0, color=(1.0, 0.92, 0.82)):
    try:
        a = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.PointLight, unreal.Vector(float(loc[0]), float(loc[1]), float(loc[2])), unreal.Rotator()
        )
        if not a:
            return None
        a.set_actor_label(label)
        try:
            c = a.get_component_by_class(unreal.PointLightComponent)
            if c:
                c.set_intensity(float(intensity))
                c.set_editor_property("attenuation_radius", float(radius))
                try:
                    c.set_light_color(unreal.LinearColor(float(color[0]), float(color[1]), float(color[2]), 1.0))
                except Exception:
                    pass
                try:
                    c.set_editor_property("cast_shadows", False)
                except Exception:
                    pass
        except Exception as e:
            log("pointlight configure fail %s %s" % (label, e))
        return a
    except Exception as e:
        log("pointlight spawn fail %s %s" % (label, e))
        return None


def spawn_layered_niagara(prefix, loc, asset_name, layers=3):
    """Layered multi-spawn of existing systems with intentional offsets/scales (capture-safe)."""
    out = []
    offsets = [
        (0.0, 0.0, 0.0, 1.0),
        (0.12, 0.08, 0.05, 0.72),
        (-0.1, -0.06, 0.08, 0.55),
        (0.05, -0.12, 0.12, 0.42),
    ]
    for i in range(min(layers, len(offsets))):
        ox, oy, oz, sc = offsets[i]
        a = spawn_niagara(
            "%s_%s_L%d" % (prefix, asset_name, i),
            (loc[0] + ox, loc[1] + oy, loc[2] + oz),
            asset_name,
            (sc, sc, sc),
        )
        if a:
            out.append(a)
    return out

'''

anchor = "_SLICE09_MATS = None"
if anchor not in text:
    raise SystemExit("anchor missing")
text = text.replace(anchor, helper + "\n" + anchor, 1)

old_ret = '''    _SLICE09_MATS = mats
    log("slice09 materials cached count=%d" % len([k for k,v in mats.items() if v]))
    return mats'''
new_ret = '''    # Slice09: stronger lighting-response variants (once-authored, load-existing preferred)
    light_specs = [
        ("M_L66_AirframeLit", "/Game/Skyguard/Textures/Generated/T_Airframe_A", "/Game/Skyguard/Textures/Generated/T_Airframe_N", "/Game/Skyguard/Textures/Generated/T_Airframe_R", 0.55, 0.08, 1.28, 2.4, -0.04),
        ("M_L66_PlateLit", "/Game/Skyguard/Textures/Generated/T_Plate_A", "/Game/Skyguard/Textures/Generated/T_Plate_N", "/Game/Skyguard/Textures/Generated/T_Plate_R", 0.45, 0.05, 1.22, 2.8, -0.02),
        ("M_L66_BrickLit", "/Game/Skyguard/Textures/Generated/T_Brick_A", "/Game/Skyguard/Textures/Generated/T_Brick_N", "/Game/Skyguard/Textures/Generated/T_Brick_R", 0.08, 0.0, 1.18, 3.2, 0.02),
        ("M_L66_ConcreteLit", "/Game/Skyguard/Textures/Generated/T_Concrete_A", "/Game/Skyguard/Textures/Generated/T_Concrete_N", "/Game/Skyguard/Textures/Generated/T_Concrete_R", 0.05, 0.0, 1.15, 2.6, 0.04),
        ("M_L66_RustLit", "/Game/Skyguard/Textures/Generated/T_Rust_A", "/Game/Skyguard/Textures/Generated/T_Rust_N", "/Game/Skyguard/Textures/Generated/T_Rust_R", 0.25, 0.04, 1.2, 3.0, 0.03),
        ("M_L66_MuzzleHot", "/Game/Skyguard/Textures/Generated/T_Plate_A", None, None, 0.1, 2.4, 1.4, 1.0, -0.2),
    ]
    for name, a, n, r, metal, emi, bright, uvs, rb in light_specs:
        if not load_tex(a):
            for alt in [
                a.replace("/Generated/", "/"),
                a.replace("T_Airframe_A", "T_L62_Airframe_A"),
                a.replace("T_Plate_A", "T_L62_Plate_A"),
                a.replace("T_Brick_A", "T_L62_Brick_A"),
                a.replace("T_Concrete_A", "T_L62_Concrete_A"),
                a.replace("T_Rust_A", "T_L62_Rust_A"),
            ]:
                if load_tex(alt):
                    a = alt
                    break
        mats[name] = create_textured_material(
            name,
            a,
            n if (n and load_tex(n)) else None,
            r if (r and load_tex(r)) else None,
            metal,
            emi,
            bright,
            uvs,
            rb,
        )
        if not mats[name]:
            for fb in [
                "M_L63_AirframeHF",
                "M_L64_AirframeAO",
                "M_L63_PlateHF",
                "M_L64_PlateAO",
                "M_L63_BrickHF",
                "M_L64_BrickDetail",
                "M_L63_ConcreteHF",
                "M_L64_ConcreteAO",
                "M_L63_RustHF",
                "M_L64_RustDetail",
                "M_L61_MuzzleHot",
            ]:
                p = "/Game/Skyguard/Materials/Generated/" + fb
                if unreal.EditorAssetLibrary.does_asset_exist(p):
                    mats[name] = unreal.EditorAssetLibrary.load_asset(p)
                    break
    _SLICE09_MATS = mats
    log("slice09 materials cached count=%d" % len([k for k,v in mats.items() if v]))
    return mats'''
if old_ret not in text:
    raise SystemExit("old_ret not found")
text = text.replace(old_ret, new_ret, 1)

done_marker = 'log("loop66 true-art slice09 densify done")'
if done_marker not in text:
    m = re.search(r'log\("loop66.*?densify done"\)', text)
    raise SystemExit("done marker missing; found=" + (m.group(0) if m else "none"))

inject = r'''
    # Slice09 true-art: stronger lighting response + layered Niagara language (capture-safe, behind wall)
    smats = ensure_slice09_materials()
    air_lit = smats.get("M_L66_AirframeLit") or smats.get("M_L63_AirframeHF") or smats.get("M_L64_AirframeAO")
    plate_lit = smats.get("M_L66_PlateLit") or smats.get("M_L63_PlateHF") or smats.get("M_L64_PlateAO")
    brick_lit = smats.get("M_L66_BrickLit") or smats.get("M_L63_BrickHF") or smats.get("M_L64_BrickDetail")
    conc_lit = smats.get("M_L66_ConcreteLit") or smats.get("M_L63_ConcreteHF") or smats.get("M_L64_ConcreteAO")
    rust_lit = smats.get("M_L66_RustLit") or smats.get("M_L63_RustHF") or smats.get("M_L64_RustDetail")
    muzzle_hot = smats.get("M_L66_MuzzleHot") or smats.get("M_L61_MuzzleHot")
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx = cam[0] + dist
        cy, cz = cam[1], cam[2]
        if name in ("YakBeauty", "Prop", "PropHub", "PropNose", "Cockpit", "ADS"):
            spawn_sm(cube, (bx + 3.45, cy + 0.2, cz + 0.15), (0.08, 1.8, 1.2), None, PREFIX + "TA9_LitPanelA_%s" % name, mat=air_lit)
            spawn_sm(cube, (bx + 3.5, cy - 0.6, cz - 0.1), (0.07, 1.4, 0.9), None, PREFIX + "TA9_LitPanelB_%s" % name, mat=plate_lit)
            spawn_sm(cube, (bx + 3.55, cy + 0.9, cz - 0.3), (0.06, 0.9, 0.55), None, PREFIX + "TA9_LitSeam_%s" % name, mat=rust_lit)
            spawn_point_light(PREFIX + "TA9_Rim_%s" % name, (bx + 2.9, cy + 1.4, cz + 0.8), intensity=160000.0, radius=2200.0, color=(1.0, 0.94, 0.85))
            spawn_point_light(PREFIX + "TA9_Fill_%s" % name, (bx + 2.7, cy - 1.2, cz + 0.3), intensity=90000.0, radius=1800.0, color=(0.75, 0.85, 1.0))
        if name in ("City", "Harbor", "Wide"):
            spawn_sm(cube, (bx + 3.5, cy + 0.4, cz - 0.5), (0.1, 1.6, 2.2), None, PREFIX + "TA9_CityLitA_%s" % name, mat=brick_lit)
            spawn_sm(cube, (bx + 3.55, cy - 1.1, cz - 0.2), (0.1, 1.3, 1.8), None, PREFIX + "TA9_CityLitB_%s" % name, mat=conc_lit)
            spawn_point_light(PREFIX + "TA9_CityLamp_%s" % name, (bx + 3.0, cy + 0.2, cz + 1.2), intensity=140000.0, radius=2500.0, color=(1.0, 0.9, 0.7))
        if name in ("Combat", "ADS", "Wide"):
            spawn_layered_niagara(PREFIX + "TA9_CombatMuzzle_%s" % name, (bx + 2.5, cy + 0.3, cz + 0.2), "NS_MuzzleFlash", layers=3)
            spawn_layered_niagara(PREFIX + "TA9_CombatSmoke_%s" % name, (bx + 2.55, cy + 0.2, cz + 0.15), "NS_GunSmoke", layers=2)
            spawn_layered_niagara(PREFIX + "TA9_CombatSparks_%s" % name, (bx + 3.2, cy + 1.0, cz + 0.4), "NS_HitSparks", layers=3)
            spawn_layered_niagara(PREFIX + "TA9_CombatExpl_%s" % name, (bx + 3.3, cy - 0.9, cz + 0.6), "NS_DroneExplosion", layers=2)
            if muzzle_hot:
                spawn_sm(sphere, (bx + 2.48, cy + 0.32, cz + 0.22), (0.22, 0.22, 0.22), None, PREFIX + "TA9_MuzzleCore_%s" % name, mat=muzzle_hot)
            spawn_point_light(PREFIX + "TA9_MuzzleLight_%s" % name, (bx + 2.5, cy + 0.3, cz + 0.25), intensity=220000.0, radius=900.0, color=(1.0, 0.72, 0.35))
        if name in ("Ocean", "Harbor", "Wide"):
            spawn_layered_niagara(PREFIX + "TA9_OceanSpray_%s" % name, (bx + 3.25, cy - 0.4, cz - 0.7), "NS_OceanSpray", layers=3)
            spawn_layered_niagara(PREFIX + "TA9_OceanMist_%s" % name, (bx + 3.4, cy + 0.2, cz - 0.4), "NS_CloudWisps", layers=2)
        if name in ("Prop", "PropHub", "PropNose", "YakBeauty"):
            spawn_layered_niagara(PREFIX + "TA9_PropWash_%s" % name, (bx + 3.6, cy + 0.0, cz + 0.05), "NS_PropWash", layers=2)
            spawn_layered_niagara(PREFIX + "TA9_Contrail_%s" % name, (bx + 3.75, cy + 0.1, cz + 0.0), "NS_ContrailRibbon", layers=2)
    log("slice09 lighting+layered niagara densify applied")
'''
text = text.replace(done_marker, inject + "\n    " + done_marker, 1)
dst.write_text(text, encoding="utf-8")
print("WROTE", dst, "bytes", dst.stat().st_size)

ha = Path(r"D:\Skyguard52\Scripts\host_audit_loop65.py").read_text(encoding="utf-8")
ha2 = (
    ha.replace("AAA_L65", "AAA_L66")
    .replace("loop65", "loop66")
    .replace("Loop 65", "Loop 66")
    .replace("Loop65", "Loop66")
)
# improve control board write to mention KEEP lineage
Path(r"D:\Skyguard52\Scripts\host_audit_loop66.py").write_text(ha2, encoding="utf-8")
print("WROTE host_audit_loop66.py")
