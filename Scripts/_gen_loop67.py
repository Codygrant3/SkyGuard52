from pathlib import Path
import re

src = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop65_true_art_slice08_capture.py")
dst = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop67_true_art_slice10_capture.py")
text = src.read_text(encoding="utf-8")

repls = [
    ("AAA_L65_", "AAA_L67_"),
    ("AAA_L65", "AAA_L67"),
    ("RT_AAA_L65", "RT_AAA_L67"),
    ("loop65", "loop67"),
    ("Loop65", "Loop67"),
    ("slice08", "slice10"),
    ("Slice08", "Slice10"),
    ("_SLICE08_MATS", "_SLICE10_MATS"),
    (
        "L64 freeze + true-art slice08 multi-slot hero materials + multi-niagara",
        "L65 freeze + true-art slice10 thin emissive accents + bounded Niagara (no FOV light stacks)",
    ),
    (
        "l64_freeze_true_art_slice08_multislot_hero_multiniagara",
        "l65_freeze_true_art_slice10_thin_emissive_bounded_niagara",
    ),
    ("TA8_", "TA10_"),
    # camera labels were hardcoded AAA_Cam_L65_ in capture(); after AAA_L65->AAA_L67 renames they may still be wrong if pattern was AAA_Cam_L65
]
for a, b in repls:
    text = text.replace(a, b)

# force camera label format to AAA_Cam_L67_
text = text.replace('("AAA_Cam_L67_%s" % name', '("AAA_Cam_L67_%s" % name')
# if leftover L65 cam names
text = text.replace("AAA_Cam_L65_", "AAA_Cam_L67_")
text = text.replace("AAA_Cam_L66_", "AAA_Cam_L67_")

done_marker = 'log("loop67 true-art slice10 densify done")'
if done_marker not in text:
    m = re.search(r'log\("loop67.*?densify done"\)', text)
    raise SystemExit("done marker missing: " + (m.group(0) if m else "none"))

inject = r'''
    # Slice10 (thin / capture-safe): tiny emissive accents + single bounded Niagara only.
    # HARD RULE from L66 reject: no extra point-light FOV stacks, no layered multi-Niagara near boards.
    s10 = ensure_slice10_materials()
    m_air = s10.get("M_L63_AirframeHF") or s10.get("M_L64_AirframeAO") or s10.get("M_L61_AirframeBright")
    m_plate = s10.get("M_L63_PlateHF") or s10.get("M_L64_PlateAO") or s10.get("M_L61_PlateBright")
    m_rust = s10.get("M_L63_RustHF") or s10.get("M_L64_RustDetail") or s10.get("M_L61_RustWarm")
    m_brick = s10.get("M_L63_BrickHF") or s10.get("M_L64_BrickDetail") or s10.get("M_L61_BrickWarm")
    m_conc = s10.get("M_L63_ConcreteHF") or s10.get("M_L64_ConcreteAO") or s10.get("M_L61_ConcreteLit")
    m_hot = s10.get("M_L61_MuzzleHot") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Muzzle")
    m_glow = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or m_hot
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx = cam[0] + dist
        cy, cz = cam[1], cam[2]
        # Behind-wall thin material accents only (x >= bx+3.4), small scales
        if name in ("YakBeauty", "Prop", "PropHub", "PropNose", "Cockpit"):
            spawn_sm(cube, (bx + 3.48, cy + 0.15, cz + 0.12), (0.05, 1.05, 0.55), None, PREFIX + "TA10_AirAccentA_%s" % name, mat=m_air)
            spawn_sm(cube, (bx + 3.52, cy - 0.45, cz - 0.05), (0.04, 0.7, 0.35), None, PREFIX + "TA10_PlateAccent_%s" % name, mat=m_plate)
            spawn_sm(cube, (bx + 3.5, cy + 0.55, cz - 0.18), (0.035, 0.35, 0.12), None, PREFIX + "TA10_RustSeam_%s" % name, mat=m_rust)
            # tiny emissive pin only (not a light actor)
            spawn_sm(sphere, (bx + 3.55, cy + 0.05, cz + 0.35), (0.06, 0.06, 0.06), None, PREFIX + "TA10_EmiPin_%s" % name, mat=m_glow)
        if name in ("City", "Harbor", "Wide"):
            spawn_sm(cube, (bx + 3.5, cy + 0.35, cz - 0.35), (0.06, 0.95, 1.2), None, PREFIX + "TA10_BrickAccent_%s" % name, mat=m_brick)
            spawn_sm(cube, (bx + 3.54, cy - 0.8, cz - 0.15), (0.05, 0.8, 0.9), None, PREFIX + "TA10_ConcAccent_%s" % name, mat=m_conc)
            spawn_sm(sphere, (bx + 3.58, cy + 0.1, cz + 0.85), (0.05, 0.05, 0.05), None, PREFIX + "TA10_CityPin_%s" % name, mat=m_glow)
        if name in ("Combat", "ADS"):
            # single small Niagara only (not layered), plus tiny hot core meshes
            spawn_niagara(PREFIX + "TA10_VFX_Muzzle_%s" % name, (bx + 3.35, cy + 0.25, cz + 0.15), "NS_MuzzleFlash", (0.28, 0.28, 0.28))
            spawn_niagara(PREFIX + "TA10_VFX_Sparks_%s" % name, (bx + 3.45, cy + 0.85, cz + 0.35), "NS_HitSparks", (0.32, 0.32, 0.32))
            spawn_sm(sphere, (bx + 3.38, cy + 0.28, cz + 0.18), (0.07, 0.07, 0.07), None, PREFIX + "TA10_MuzzleCore_%s" % name, mat=m_hot)
        if name in ("Ocean", "Harbor"):
            spawn_niagara(PREFIX + "TA10_VFX_Spray_%s" % name, (bx + 3.4, cy - 0.35, cz - 0.65), "NS_OceanSpray", (0.4, 0.4, 0.4))
        if name in ("Prop", "PropHub", "YakBeauty"):
            spawn_niagara(PREFIX + "TA10_VFX_Wash_%s" % name, (bx + 3.6, cy + 0.0, cz + 0.05), "NS_PropWash", (0.3, 0.3, 0.3))
    log("slice10 thin emissive+bounded niagara densify applied (no extra point lights)")
'''

text = text.replace(done_marker, inject + "\n    " + done_marker, 1)
dst.write_text(text, encoding="utf-8")
print("WROTE", dst, dst.stat().st_size)

# host audit from L65 with L67 names
ha = Path(r"D:\Skyguard52\Scripts\host_audit_loop65.py").read_text(encoding="utf-8")
ha2 = (
    ha.replace("AAA_L65", "AAA_L67")
    .replace("loop65", "loop67")
    .replace("Loop 65", "Loop 67")
    .replace("Loop65", "Loop67")
)
# ensure cam prefix AAA_Cam_L67_
ha2 = ha2.replace("AAA_Cam_L65_", "AAA_Cam_L67_")
Path(r"D:\Skyguard52\Scripts\host_audit_loop67.py").write_text(ha2, encoding="utf-8")
print("WROTE host_audit_loop67.py")

import ast
ast.parse(dst.read_text(encoding="utf-8"))
ast.parse(ha2)
print("AST_OK")
# sanity: no spawn_point_light in slice10 inject path; cam labels
t2 = dst.read_text(encoding="utf-8")
print("cam67", "AAA_Cam_L67_" in t2)
print("cam65 leftover", "AAA_Cam_L65_" in t2)
print("slice10 inject", "slice10 thin emissive" in t2)
print("extra pointlight fn", "def spawn_point_light" in t2)
