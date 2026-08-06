from pathlib import Path
import re, ast

src = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop67_true_art_slice10_capture.py")
dst = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop68_true_art_slice11_capture.py")
text = src.read_text(encoding="utf-8")
repls = [
    ("AAA_L67_", "AAA_L68_"),
    ("AAA_L67", "AAA_L68"),
    ("RT_AAA_L67", "RT_AAA_L68"),
    ("loop67", "loop68"),
    ("Loop67", "Loop68"),
    ("slice10", "slice11"),
    ("Slice10", "Slice11"),
    ("_SLICE10_MATS", "_SLICE11_MATS"),
    (
        "L65 freeze + true-art slice10 thin emissive accents + bounded Niagara (no FOV light stacks)",
        "L67 freeze + true-art slice11 stronger ANR materials + thin emissive (no FOV light stacks)",
    ),
    (
        "l65_freeze_true_art_slice10_thin_emissive_bounded_niagara",
        "l67_freeze_true_art_slice11_stronger_anr_thin_emissive",
    ),
    ("TA10_", "TA11_"),
]
for a,b in repls:
    text = text.replace(a,b)
text = text.replace("AAA_Cam_L67_", "AAA_Cam_L68_")
text = text.replace("AAA_Cam_L66_", "AAA_Cam_L68_")
text = text.replace("AAA_Cam_L65_", "AAA_Cam_L68_")

# strengthen create_textured_material usage by extending ensure_slice11_materials with real Imported textures
old = '''    _SLICE11_MATS = mats
    log("slice11 materials cached count=%d" % len([k for k,v in mats.items() if v]))
    return mats'''
if old not in text:
    # try exact from renamed ensure
    m = re.search(r'    _SLICE11_MATS = mats\n    log\("slice11 materials cached count=%d".*?\n    return mats', text)
    raise SystemExit('old ensure ret missing')
new = '''    # Slice11: stronger once-authored A/N/R materials from Imported textures (load-existing preferred)
    anr_specs = [
        ("M_L68_AirframeANR", "/Game/Skyguard/Textures/Imported/T_airframe_metal_A", "/Game/Skyguard/Textures/Imported/T_airframe_metal_N", "/Game/Skyguard/Textures/Imported/T_airframe_metal_R", 0.62, 0.0, 1.18, 2.2, -0.03),
        ("M_L68_PlateANR", "/Game/Skyguard/Textures/Imported/T_L8_plate2_A", "/Game/Skyguard/Textures/Imported/T_L8_plate2_N", "/Game/Skyguard/Textures/Imported/T_L8_plate2_R", 0.48, 0.0, 1.15, 2.6, -0.01),
        ("M_L68_BrickANR", "/Game/Skyguard/Textures/Imported/T_brick_A", "/Game/Skyguard/Textures/Imported/T_brick_N", "/Game/Skyguard/Textures/Imported/T_brick_R", 0.08, 0.0, 1.12, 2.8, 0.02),
        ("M_L68_ConcreteANR", "/Game/Skyguard/Textures/Imported/T_concrete_A", "/Game/Skyguard/Textures/Imported/T_concrete_N", "/Game/Skyguard/Textures/Imported/T_concrete_R", 0.05, 0.0, 1.1, 2.4, 0.03),
        ("M_L68_RustANR", "/Game/Skyguard/Textures/Imported/T_L4_rust_A", "/Game/Skyguard/Textures/Imported/T_L4_rust_N", "/Game/Skyguard/Textures/Imported/T_L4_rust_R", 0.22, 0.0, 1.14, 2.7, 0.02),
    ]
    for name, a, n, r, metal, emi, bright, uvs, rb in anr_specs:
        mats[name] = create_textured_material(name, a, n, r, metal, emi, bright, uvs, rb)
        if not mats[name]:
            # fallback chain
            for fb in ["M_L63_AirframeHF","M_L62_AirframeANR","M_L63_PlateHF","M_L62_PlateANR","M_L63_BrickHF","M_L62_BrickANR","M_L63_ConcreteHF","M_L62_ConcreteANR","M_L63_RustHF","M_L62_RustANR"]:
                p = "/Game/Skyguard/Materials/Generated/" + fb
                if unreal.EditorAssetLibrary.does_asset_exist(p):
                    mats[name] = unreal.EditorAssetLibrary.load_asset(p)
                    break
    _SLICE11_MATS = mats
    log("slice11 materials cached count=%d" % len([k for k,v in mats.items() if v]))
    return mats'''
text = text.replace(old, new, 1)

done = 'log("loop68 true-art slice11 densify done")'
if done not in text:
    m = re.search(r'log\("loop68.*?densify done"\)', text)
    raise SystemExit('done missing ' + str(m.group(0) if m else None))

inject = r'''
    # Slice11: stronger ANR material accents behind wall only; keep thin emissive/Niagara; NO extra point lights.
    s11 = ensure_slice11_materials()
    m_air = s11.get("M_L68_AirframeANR") or s11.get("M_L63_AirframeHF") or s11.get("M_L64_AirframeAO")
    m_plate = s11.get("M_L68_PlateANR") or s11.get("M_L63_PlateHF") or s11.get("M_L64_PlateAO")
    m_rust = s11.get("M_L68_RustANR") or s11.get("M_L63_RustHF") or s11.get("M_L64_RustDetail")
    m_brick = s11.get("M_L68_BrickANR") or s11.get("M_L63_BrickHF") or s11.get("M_L64_BrickDetail")
    m_conc = s11.get("M_L68_ConcreteANR") or s11.get("M_L63_ConcreteHF") or s11.get("M_L64_ConcreteAO")
    m_hot = s11.get("M_L61_MuzzleHot") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Muzzle")
    m_glow = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or m_hot
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx = cam[0] + dist
        cy, cz = cam[1], cam[2]
        if name in ("YakBeauty", "Prop", "PropHub", "PropNose", "Cockpit", "ADS"):
            spawn_sm(cube, (bx + 3.5, cy + 0.1, cz + 0.1), (0.06, 1.2, 0.7), None, PREFIX + "TA11_AirANR_%s" % name, mat=m_air)
            spawn_sm(cube, (bx + 3.54, cy - 0.55, cz - 0.08), (0.05, 0.85, 0.45), None, PREFIX + "TA11_PlateANR_%s" % name, mat=m_plate)
            spawn_sm(cube, (bx + 3.52, cy + 0.6, cz - 0.2), (0.04, 0.4, 0.14), None, PREFIX + "TA11_RustANR_%s" % name, mat=m_rust)
            # multi-slot hero panels
            spawn_sm(cube, (bx + 3.56, cy + 0.2, cz + 0.25), (0.05, 0.9, 0.5), None, PREFIX + "TA11_HeroPanel_%s" % name, mats=[m_air, m_plate, m_rust])
            spawn_sm(sphere, (bx + 3.58, cy + 0.0, cz + 0.4), (0.05, 0.05, 0.05), None, PREFIX + "TA11_EmiPin_%s" % name, mat=m_glow)
        if name in ("City", "Harbor", "Wide"):
            spawn_sm(cube, (bx + 3.52, cy + 0.4, cz - 0.4), (0.07, 1.05, 1.35), None, PREFIX + "TA11_BrickANR_%s" % name, mat=m_brick)
            spawn_sm(cube, (bx + 3.56, cy - 0.9, cz - 0.2), (0.06, 0.9, 1.0), None, PREFIX + "TA11_ConcANR_%s" % name, mat=m_conc)
            spawn_sm(cube, (bx + 3.54, cy + 0.1, cz + 0.3), (0.05, 0.7, 0.8), None, PREFIX + "TA11_CityHero_%s" % name, mats=[m_brick, m_conc, m_rust])
            spawn_sm(sphere, (bx + 3.6, cy + 0.15, cz + 0.9), (0.045, 0.045, 0.045), None, PREFIX + "TA11_CityPin_%s" % name, mat=m_glow)
        if name in ("Combat", "ADS"):
            spawn_niagara(PREFIX + "TA11_VFX_Muzzle_%s" % name, (bx + 3.38, cy + 0.22, cz + 0.12), "NS_MuzzleFlash", (0.26, 0.26, 0.26))
            spawn_niagara(PREFIX + "TA11_VFX_Sparks_%s" % name, (bx + 3.48, cy + 0.9, cz + 0.32), "NS_HitSparks", (0.3, 0.3, 0.3))
            spawn_sm(sphere, (bx + 3.4, cy + 0.25, cz + 0.15), (0.06, 0.06, 0.06), None, PREFIX + "TA11_MuzzleCore_%s" % name, mat=m_hot)
        if name in ("Ocean", "Harbor"):
            spawn_niagara(PREFIX + "TA11_VFX_Spray_%s" % name, (bx + 3.42, cy - 0.32, cz - 0.62), "NS_OceanSpray", (0.38, 0.38, 0.38))
        if name in ("Prop", "PropHub", "YakBeauty"):
            spawn_niagara(PREFIX + "TA11_VFX_Wash_%s" % name, (bx + 3.62, cy + 0.0, cz + 0.04), "NS_PropWash", (0.28, 0.28, 0.28))
    log("slice11 stronger ANR + thin emissive densify applied (no extra point lights)")
'''
# remove previous slice10 inject marker text if present by replacing densify done only once with inject after any existing thin inject
# If slice10 inject still exists under new names, keep it and add slice11 after
if 'slice10 thin emissive+bounded niagara densify applied' in text or 'slice11 thin emissive+bounded niagara densify applied' in text:
    # already renamed inject exists; append slice11 before densify done
    text = text.replace(done, inject + "\n    " + done, 1)
else:
    text = text.replace(done, inject + "\n    " + done, 1)

dst.write_text(text, encoding='utf-8')
ast.parse(text)
print('WROTE', dst, dst.stat().st_size)
print('cam68', 'AAA_Cam_L68_' in text)
print('anr', 'M_L68_AirframeANR' in text)
print('pointlight', 'spawn_point_light' in text)

ha = Path(r'D:\Skyguard52\Scripts\host_audit_loop67.py').read_text(encoding='utf-8')
ha2 = ha.replace('AAA_L67','AAA_L68').replace('loop67','loop68').replace('Loop 67','Loop 68').replace('Loop67','Loop68').replace('AAA_Cam_L67_','AAA_Cam_L68_')
Path(r'D:\Skyguard52\Scripts\host_audit_loop68.py').write_text(ha2, encoding='utf-8')
ast.parse(ha2)
print('AUDIT_OK')
