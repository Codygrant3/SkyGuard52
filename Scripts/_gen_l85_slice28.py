from pathlib import Path
src = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop84_true_art_slice27_capture.py")
dst = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop85_true_art_slice28_capture.py")
text = src.read_text(encoding="utf-8")

text = text.replace('PREFIX = "AAA_L84_"', 'PREFIX = "AAA_L85_"')
text = text.replace(r'OUT_DIR = r"D:\Skyguard52\Saved\Screenshots\AAA_L84"', r'OUT_DIR = r"D:\Skyguard52\Saved\Screenshots\AAA_L85"')
text = text.replace('RT_PATH = "/Game/Skyguard/Capture/RT_AAA_L84"', 'RT_PATH = "/Game/Skyguard/Capture/RT_AAA_L85"')
text = text.replace('AAA_Cam_L84_', 'AAA_Cam_L85_')
text = text.replace('RT_AAA_L84', 'RT_AAA_L85')
text = text.replace('Skyguard AAA Loop84 stills', 'Skyguard AAA Loop85 stills')
text = text.replace('note=l83_freeze_true_art_slice27_niagara_material_push', 'note=l84_freeze_true_art_slice28_niagara_material_push')
text = text.replace('loop84 L83 freeze + true-art slice27 niagara + material push start', 'loop85 L84 freeze + true-art slice28 niagara + material push start')
text = text.replace('Loop84 complete stills=', 'Loop85 complete stills=')
text = text.replace('loop84 true-art slice27 densify done', 'loop85 true-art slice28 densify done')
text = text.replace('log("loop84 mat palette size=', 'log("loop85 mat palette size=')

slice28_fn = '''

def ensure_slice28_vfx_library():
    """Slice28: deepen VFX library with more capture-visible Auth systems on L84 freeze."""
    ensure_dir("/Game/Skyguard/VFX")
    ensure_dir("/Game/Skyguard/VFX/Emitters")
    base = ensure_slice27_vfx_library()
    names = [
        "NS_L85_MuzzleCoreHot", "NS_L85_SparkChain", "NS_L85_ExplBloomLite",
        "NS_L85_PropWashCore", "NS_L85_FoamCrestLite", "NS_L85_TracerCoreHot",
        "NS_L85_GunSmokeCoreLite", "NS_L85_FlakBloomLite", "NS_L85_CitySparkHot",
        "NS_L85_ContrailCoreLite", "NS_L85_ShellBurstLite", "NS_L85_HitFlashLite",
        "NS_L85_DebrisCoreLite", "NS_L85_ExhaustCoreLite", "NS_L85_MuzzleSmokeLite",
        "NS_L85_OceanFoamLite",
    ]
    out = dict(base)
    for n in names:
        out[n] = ensure_authored_ns(n, deepen=True)
    log("slice28 vfx library count=%d" % len([k for k, v in out.items() if v]))
    return out
'''

if 'def ensure_slice28_vfx_library' not in text:
    marker = 'def ensure_slice27_vfx_library():'
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit('ensure_slice27 not found')
    next_def = text.find('\ndef ', idx + len(marker))
    if next_def < 0:
        raise SystemExit('next def after slice27 not found')
    text = text[:next_def] + slice28_fn + text[next_def:]

slice28_block = '''
    # Slice28 (thin / capture-safe on L84 KEEP): Niagara + material push
    vfx28 = ensure_slice28_vfx_library()
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx, by, bz = cam[0] + dist, cam[1], cam[2]
        cy, cz = by, bz
        if name in ('Prop', 'PropHub', 'PropNose', 'YakBeauty'):
            spawn_niagara(PREFIX + "TA28_NS_PropWashCore_%s" % name, (bx + 4.16, cy + 0.02, cz + 0.02), "NS_L85_PropWashCore", (0.08, 0.08, 0.08), bound=True)
            spawn_niagara(PREFIX + "TA28_NS_ContrailCoreLite_%s" % name, (bx + 4.23, cy + 0.05, cz + 0.0), "NS_L85_ContrailCoreLite", (0.06, 0.06, 0.06), bound=True)
            spawn_niagara(PREFIX + "TA28_NS_ExhaustCoreLite_%s" % name, (bx + 4.19, cy - 0.1, cz - 0.01), "NS_L85_ExhaustCoreLite", (0.06, 0.06, 0.06), bound=True)
            spawn_particle_field(PREFIX + "TA28_PropField_%s" % name, (bx + 4.0, cy, cz), mat, count=8, radius=0.28, size=0.035, label_base="PropPF28")
        if name in ('Combat', 'ADS', 'Cockpit'):
            spawn_niagara(PREFIX + "TA28_NS_MuzzleHot_%s" % name, (bx + 3.64, cy + 0.07, cz + 0.05), "NS_L85_MuzzleCoreHot", (0.06, 0.06, 0.06), bound=True)
            spawn_niagara(PREFIX + "TA28_NS_MuzzleSmokeLite_%s" % name, (bx + 3.66, cy + 0.06, cz + 0.04), "NS_L85_MuzzleSmokeLite", (0.05, 0.05, 0.05), bound=True)
            spawn_niagara(PREFIX + "TA28_NS_SmokeCoreLite_%s" % name, (bx + 3.66, cy + 0.03, cz + 0.02), "NS_L85_GunSmokeCoreLite", (0.06, 0.06, 0.06), bound=True)
            spawn_niagara(PREFIX + "TA28_NS_SparkChain_%s" % name, (bx + 3.74, cy + 0.84, cz + 0.2), "NS_L85_SparkChain", (0.07, 0.07, 0.07), bound=True)
            spawn_niagara(PREFIX + "TA28_NS_TracerHot_%s" % name, (bx + 3.69, cy + 0.11, cz + 0.05), "NS_L85_TracerCoreHot", (0.04, 0.04, 0.04), bound=True)
            spawn_niagara(PREFIX + "TA28_NS_ShellBurstLite_%s" % name, (bx + 3.6, cy + 0.0, cz - 0.02), "NS_L85_ShellBurstLite", (0.05, 0.05, 0.05), bound=True)
            if name == 'Combat':
                spawn_niagara(PREFIX + "TA28_NS_ExplBloomLite", (bx + 3.8, cy - 0.72, cz + 0.44), "NS_L85_ExplBloomLite", (0.09, 0.09, 0.09), bound=True)
                spawn_niagara(PREFIX + "TA28_NS_FlakBloomLite", (bx + 3.78, cy + 0.94, cz + 0.39), "NS_L85_FlakBloomLite", (0.06, 0.06, 0.06), bound=True)
                spawn_niagara(PREFIX + "TA28_NS_DebrisCoreLite", (bx + 3.79, cy - 0.82, cz + 0.36), "NS_L85_DebrisCoreLite", (0.08, 0.08, 0.08), bound=True)
                spawn_burst_ring(PREFIX + "TA28_CombatRing", (bx + 3.85, cy - 0.2, cz + 0.2), mat, count=8, radius=0.5, label_base="CRing28")
            if name == 'ADS':
                spawn_niagara(PREFIX + "TA28_NS_HitFlashLite", (bx + 3.65, cy + 0.14, cz + 0.1), "NS_L85_HitFlashLite", (0.05, 0.05, 0.05), bound=True)
        if name == 'City':
            spawn_niagara(PREFIX + "TA28_NS_CitySparkHot", (bx + 3.94, cy + 0.22, cz + 0.58), "NS_L85_CitySparkHot", (0.07, 0.07, 0.07), bound=True)
            spawn_particle_field(PREFIX + "TA28_CityField", (bx + 3.9, cy + 0.1, cz + 0.3), mat, count=10, radius=0.4, size=0.03, label_base="CityPF28")
        if name in ('Ocean', 'Harbor'):
            spawn_niagara(PREFIX + "TA28_NS_FoamCrestLite_%s" % name, (bx + 3.82, cy - 0.04, cz - 0.38), "NS_L85_FoamCrestLite", (0.1, 0.1, 0.1), bound=True)
            spawn_niagara(PREFIX + "TA28_NS_OceanFoamLite_%s" % name, (bx + 3.83, cy - 0.04, cz - 0.4), "NS_L85_OceanFoamLite", (0.08, 0.08, 0.08), bound=True)
            spawn_burst_ring(PREFIX + "TA28_FoamRing_%s" % name, (bx + 3.8, cy, cz - 0.35), mat, count=8, radius=0.45, label_base="FoamR28")

    log("slice28 niagara + material push densify applied (no extra point lights)")

'''

needle = '    log("slice27 niagara + material push densify applied (no extra point lights)")\n'
if needle not in text:
    needle_alt = "    log('slice27 niagara + material push densify applied (no extra point lights)')\n"
    if needle_alt in text:
        needle = needle_alt
    else:
        raise SystemExit('slice27 densify applied log missing')

pos = text.find(needle)
insert_at = pos + len(needle)
rest = text[insert_at:]
rest = rest.replace('true-art slice27 densify done', 'true-art slice28 densify done')
rest = rest.replace('loop84 true-art', 'loop85 true-art')
text = text[:insert_at] + slice28_block + rest

assert 'PREFIX = "AAA_L85_"' in text
assert 'Screenshots\\AAA_L85' in text or 'Screenshots/AAA_L85' in text
assert 'def ensure_slice27_vfx_library' in text
assert 'def ensure_slice28_vfx_library' in text
assert 'NS_L84_MuzzleBloomLite' in text
assert 'NS_L85_MuzzleCoreHot' in text
assert 'AAA_Cam_L85_' in text
assert 'loop85 L84 freeze' in text
assert 'ensure_auth_niagara' not in text

dst.write_text(text, encoding='utf-8')
print('WROTE', dst, 'lines', len(text.splitlines()), 'size', dst.stat().st_size)

hs = Path(r'D:\Skyguard52\Scripts\host_audit_loop84.py').read_text(encoding='utf-8')
hs = hs.replace('AAA_L84', 'AAA_L85')
hs = hs.replace('AAA_Cam_L84_', 'AAA_Cam_L85_')
hs = hs.replace('loop84', 'loop85').replace('Loop 84', 'Loop 85').replace('Loop84', 'Loop85')
hs = hs.replace('CRITIC_FAIL_loop84.md', 'CRITIC_FAIL_loop85.md')
assert 'AAA_Cam_L84_' not in hs
assert 'AAA_Cam_L85_' in hs
assert 'AAA_L85' in hs
Path(r'D:\Skyguard52\Scripts\host_audit_loop85.py').write_text(hs, encoding='utf-8')
print('WROTE host_audit_loop85')
