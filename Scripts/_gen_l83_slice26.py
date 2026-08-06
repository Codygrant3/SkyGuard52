from pathlib import Path
src = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop82_true_art_slice25_capture.py")
dst = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop83_true_art_slice26_capture.py")
text = src.read_text(encoding="utf-8")

# Identity retarget capture paths / labels only
text = text.replace('PREFIX = "AAA_L82_"', 'PREFIX = "AAA_L83_"')
text = text.replace(r'OUT_DIR = r"D:\Skyguard52\Saved\Screenshots\AAA_L82"', r'OUT_DIR = r"D:\Skyguard52\Saved\Screenshots\AAA_L83"')
text = text.replace('RT_PATH = "/Game/Skyguard/Capture/RT_AAA_L82"', 'RT_PATH = "/Game/Skyguard/Capture/RT_AAA_L83"')
text = text.replace('AAA_Cam_L82_', 'AAA_Cam_L83_')
text = text.replace('RT_AAA_L82', 'RT_AAA_L83')
text = text.replace('Skyguard AAA Loop82 stills', 'Skyguard AAA Loop83 stills')
text = text.replace('note=l81_freeze_true_art_slice25_niagara_material_push', 'note=l82_freeze_true_art_slice26_niagara_material_push')
text = text.replace('loop82 L81 freeze + true-art slice25 niagara + material push start', 'loop83 L82 freeze + true-art slice26 niagara + material push start')
text = text.replace('Loop82 complete stills=', 'Loop83 complete stills=')
text = text.replace('loop82 true-art slice25 densify done', 'loop83 true-art slice26 densify done')
text = text.replace('log("loop82 mat palette size=', 'log("loop83 mat palette size=')

slice26_fn = '''

def ensure_slice26_vfx_library():
    """Slice26: deepen VFX library with more capture-visible Auth systems on L82 freeze."""
    ensure_dir("/Game/Skyguard/VFX")
    ensure_dir("/Game/Skyguard/VFX/Emitters")
    base = ensure_slice25_vfx_library()
    names = [
        "NS_L83_MuzzlePetal", "NS_L83_SparkArc", "NS_L83_ExplShock",
        "NS_L83_PropWashDisc", "NS_L83_FoamRibbon", "NS_L83_TracerCoreLite",
        "NS_L83_GunSmokeRibbon", "NS_L83_FlakPetal", "NS_L83_CitySparkLite",
        "NS_L83_ContrailSoft", "NS_L83_ShellSpark", "NS_L83_HitFlash",
        "NS_L83_DebrisSpark", "NS_L83_ExhaustSoft", "NS_L83_MuzzleHalo",
        "NS_L83_OceanRibbon",
    ]
    out = dict(base)
    for n in names:
        out[n] = ensure_authored_ns(n, deepen=True)
    log("slice26 vfx library count=%d" % len([k for k, v in out.items() if v]))
    return out
'''

if 'def ensure_slice26_vfx_library' not in text:
    marker = 'def ensure_slice25_vfx_library():'
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit('ensure_slice25 not found')
    next_def = text.find('\ndef ', idx + len(marker))
    if next_def < 0:
        raise SystemExit('next def after slice25 not found')
    text = text[:next_def] + slice26_fn + text[next_def:]

slice26_block = '''
    # Slice26 (thin / capture-safe on L82 KEEP): Niagara + material push
    vfx26 = ensure_slice26_vfx_library()
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx, by, bz = cam[0] + dist, cam[1], cam[2]
        cy, cz = by, bz
        if name in ('Prop', 'PropHub', 'PropNose', 'YakBeauty'):
            spawn_niagara(PREFIX + "TA26_NS_PropWashDisc_%s" % name, (bx + 4.16, cy + 0.02, cz + 0.02), "NS_L83_PropWashDisc", (0.08, 0.08, 0.08), bound=True)
            spawn_niagara(PREFIX + "TA26_NS_ContrailSoft_%s" % name, (bx + 4.23, cy + 0.05, cz + 0.0), "NS_L83_ContrailSoft", (0.06, 0.06, 0.06), bound=True)
            spawn_niagara(PREFIX + "TA26_NS_ExhaustSoft_%s" % name, (bx + 4.19, cy - 0.1, cz - 0.01), "NS_L83_ExhaustSoft", (0.06, 0.06, 0.06), bound=True)
            spawn_particle_field(PREFIX + "TA26_PropField_%s" % name, (bx + 4.0, cy, cz), mat, count=8, radius=0.28, size=0.035, label_base="PropPF26")
        if name in ('Combat', 'ADS', 'Cockpit'):
            spawn_niagara(PREFIX + "TA26_NS_MuzzlePetal_%s" % name, (bx + 3.64, cy + 0.07, cz + 0.05), "NS_L83_MuzzlePetal", (0.06, 0.06, 0.06), bound=True)
            spawn_niagara(PREFIX + "TA26_NS_MuzzleHalo_%s" % name, (bx + 3.66, cy + 0.06, cz + 0.04), "NS_L83_MuzzleHalo", (0.05, 0.05, 0.05), bound=True)
            spawn_niagara(PREFIX + "TA26_NS_SmokeRibbon_%s" % name, (bx + 3.66, cy + 0.03, cz + 0.02), "NS_L83_GunSmokeRibbon", (0.06, 0.06, 0.06), bound=True)
            spawn_niagara(PREFIX + "TA26_NS_SparkArc_%s" % name, (bx + 3.74, cy + 0.84, cz + 0.2), "NS_L83_SparkArc", (0.07, 0.07, 0.07), bound=True)
            spawn_niagara(PREFIX + "TA26_NS_TracerLite_%s" % name, (bx + 3.69, cy + 0.11, cz + 0.05), "NS_L83_TracerCoreLite", (0.04, 0.04, 0.04), bound=True)
            spawn_niagara(PREFIX + "TA26_NS_ShellSpark_%s" % name, (bx + 3.6, cy + 0.0, cz - 0.02), "NS_L83_ShellSpark", (0.05, 0.05, 0.05), bound=True)
            if name == 'Combat':
                spawn_niagara(PREFIX + "TA26_NS_ExplShock", (bx + 3.8, cy - 0.72, cz + 0.44), "NS_L83_ExplShock", (0.09, 0.09, 0.09), bound=True)
                spawn_niagara(PREFIX + "TA26_NS_FlakPetal", (bx + 3.78, cy + 0.94, cz + 0.39), "NS_L83_FlakPetal", (0.06, 0.06, 0.06), bound=True)
                spawn_niagara(PREFIX + "TA26_NS_DebrisSpark", (bx + 3.79, cy - 0.82, cz + 0.36), "NS_L83_DebrisSpark", (0.08, 0.08, 0.08), bound=True)
                spawn_burst_ring(PREFIX + "TA26_CombatRing", (bx + 3.85, cy - 0.2, cz + 0.2), mat, count=8, radius=0.5, label_base="CRing26")
            if name == 'ADS':
                spawn_niagara(PREFIX + "TA26_NS_HitFlash", (bx + 3.65, cy + 0.14, cz + 0.1), "NS_L83_HitFlash", (0.05, 0.05, 0.05), bound=True)
        if name == 'City':
            spawn_niagara(PREFIX + "TA26_NS_CitySparkLite", (bx + 3.94, cy + 0.22, cz + 0.58), "NS_L83_CitySparkLite", (0.07, 0.07, 0.07), bound=True)
            spawn_particle_field(PREFIX + "TA26_CityField", (bx + 3.9, cy + 0.1, cz + 0.3), mat, count=10, radius=0.4, size=0.03, label_base="CityPF26")
        if name in ('Ocean', 'Harbor'):
            spawn_niagara(PREFIX + "TA26_NS_FoamRibbon_%s" % name, (bx + 3.82, cy - 0.04, cz - 0.38), "NS_L83_FoamRibbon", (0.1, 0.1, 0.1), bound=True)
            spawn_niagara(PREFIX + "TA26_NS_OceanRibbon_%s" % name, (bx + 3.83, cy - 0.04, cz - 0.4), "NS_L83_OceanRibbon", (0.08, 0.08, 0.08), bound=True)
            spawn_burst_ring(PREFIX + "TA26_FoamRing_%s" % name, (bx + 3.8, cy, cz - 0.35), mat, count=8, radius=0.45, label_base="FoamR26")

    log("slice26 niagara + material push densify applied (no extra point lights)")

'''

needle = '    log("slice25 niagara + material push densify applied (no extra point lights)")\n'
# after identity retarget, slice25 applied log may still use single quotes if inserted earlier
if needle not in text:
    needle_alt = "    log('slice25 niagara + material push densify applied (no extra point lights)')\n"
    if needle_alt in text:
        needle = needle_alt
    else:
        raise SystemExit('slice25 densify applied log missing')

pos = text.find(needle)
insert_at = pos + len(needle)
rest = text[insert_at:]
rest = rest.replace('true-art slice25 densify done', 'true-art slice26 densify done')
rest = rest.replace('loop82 true-art', 'loop83 true-art')
text = text[:insert_at] + slice26_block + rest

# Safety
assert 'PREFIX = "AAA_L83_"' in text
assert 'Screenshots\\AAA_L83' in text or 'Screenshots/AAA_L83' in text
assert 'def ensure_slice25_vfx_library' in text
assert 'def ensure_slice26_vfx_library' in text
assert 'ensure_authored_ns(n, deepen=True)' in text
assert 'NS_L82_MuzzleCone' in text
assert 'NS_L83_MuzzlePetal' in text
assert 'AAA_Cam_L83_' in text
assert 'loop83 L82 freeze' in text
assert 'ensure_auth_niagara' not in text

dst.write_text(text, encoding='utf-8')
print('WROTE', dst, 'lines', len(text.splitlines()), 'size', dst.stat().st_size)

# host audit
hs = Path(r'D:\Skyguard52\Scripts\host_audit_loop82.py').read_text(encoding='utf-8')
hs = hs.replace('AAA_L82', 'AAA_L83').replace('loop82', 'loop83').replace('Loop 82', 'Loop 83').replace('Loop82', 'Loop83')
hs = hs.replace('CRITIC_FAIL_loop82.md', 'CRITIC_FAIL_loop83.md')
Path(r'D:\Skyguard52\Scripts\host_audit_loop83.py').write_text(hs, encoding='utf-8')
print('WROTE host_audit_loop83')
