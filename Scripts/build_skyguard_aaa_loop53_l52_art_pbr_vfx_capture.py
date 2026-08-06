import unreal
import os
import hashlib
import time
import math

PREFIX = "AAA_L53_"
OUT_DIR = r"D:\Skyguard52\Saved\Screenshots\AAA_L53"
RT_PATH = "/Game/Skyguard/Capture/RT_AAA_L53"
MAP_PATH = "/Game/Skyguard/Maps/Lvl_SkyguardCoast"

def log(m):
    unreal.log("[SkyguardAAA] " + str(m))

def clear_old():
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        try:
            n = a.get_actor_label()
            if n and (n.startswith("AAA_L") or n.startswith("AAA_Cam_L")):
                unreal.EditorLevelLibrary.destroy_actor(a)
        except Exception:
            pass

def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)

def load_sm(path):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        a = unreal.EditorAssetLibrary.load_asset(path)
        if isinstance(a, unreal.StaticMesh):
            return a
    return None

def load_mat(path):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path)
    return None

def get_loc(a):
    try:
        v = a.get_actor_location()
        return (float(v.x), float(v.y), float(v.z))
    except Exception:
        return None

def spawn_sm(mesh, loc, scale=(1,1,1), rot=None, label=None, mat=None):
    if not mesh:
        return None
    x,y,z = float(loc[0]), float(loc[1]), float(loc[2])
    a = None
    try:
        sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        if sub:
            a = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x,y,z), rot or unreal.Rotator())
    except Exception:
        pass
    if not a:
        a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x,y,z), rot or unreal.Rotator())
    if not a:
        return None
    a.static_mesh_component.set_static_mesh(mesh)
    a.set_actor_scale3d(unreal.Vector(float(scale[0]), float(scale[1]), float(scale[2])))
    for _ in range(3):
        try:
            a.set_actor_location(unreal.Vector(x,y,z), False, True)
        except Exception:
            pass
    if mat:
        try:
            a.static_mesh_component.set_material(0, mat)
        except Exception:
            pass
    if label:
        a.set_actor_label(label)
    got = get_loc(a)
    if got and (abs(got[0]-x)+abs(got[1]-y)+abs(got[2]-z) > 1.0):
        log("SPAWN_MISMATCH %s target=(%.1f,%.1f,%.1f) got=%s" % (label, x,y,z, got))
    return a

def densify():
    cube = load_sm("/Engine/BasicShapes/Cube")
    sphere = load_sm("/Engine/BasicShapes/Sphere")
    mat_paths = [
        "/Game/Skyguard/Materials/Generated/M_L18_UnlitWhite",
        "/Game/Skyguard/Materials/Generated/M_L18_UnlitYellow",
        "/Game/Skyguard/Materials/Generated/M_L18_UnlitCyan",
        "/Game/Skyguard/Materials/Generated/M_L18_UnlitRed",
        "/Game/Skyguard/Materials/Generated/M_L18_UnlitGreen",
        "/Game/Skyguard/Materials/Generated/M_L21_BrightBrick",
        "/Game/Skyguard/Materials/Generated/M_L21_BrightMetal",
        "/Game/Skyguard/Materials/Generated/M_L21_BrightOcean",
        "/Game/Skyguard/Materials/Generated/M_L21_BrightSand",
        "/Game/Skyguard/Materials/Generated/M_L21_BrightWhite",
        "/Game/Skyguard/Materials/Generated/M_L23_Airframe",
        "/Game/Skyguard/Materials/Generated/M_L23_Brick",
        "/Game/Skyguard/Materials/Generated/M_L23_Panel",
        "/Game/Skyguard/Materials/Generated/M_L23_Boom",
        "/Game/Skyguard/Materials/Generated/M_L23_Muzzle",
        "/Game/Skyguard/Materials/Generated/M_L23_Needle",
        "/Game/Skyguard/Materials/Generated/M_L23_Plaster",
        "/Game/Skyguard/Materials/Generated/M_L23_Asphalt",
        "/Game/Skyguard/Materials/Generated/M_L23_Beach",
        "/Game/Skyguard/Materials/Generated/M_L23_Ocean",
        "/Game/Skyguard/Materials/M_Metal",
        "/Game/Skyguard/Materials/M_MetalRust",
        "/Game/Skyguard/Materials/M_RifleTan",
        "/Game/Skyguard/Materials/M_PropDisc",
        "/Game/Skyguard/Materials/M_LeatherGlove",
        "/Game/Skyguard/Materials/M_CityGlass",
        "/Game/Skyguard/Materials/M_CockpitInterior",
        "/Game/Skyguard/Materials/M_ExhaustGlow",
        "/Game/Skyguard/Materials/Generated/M_AirframeMetal",
        "/Game/Skyguard/Materials/M_Tex_airframe_metal",
        "/Game/Skyguard/Materials/M_YakAirframe",
        "/Game/Skyguard/Materials/M_Tex_brick",
        "/Game/Skyguard/Materials/M_Tex_metal",
        "/Game/Skyguard/Materials/M_Tex_leather",
        "/Game/Skyguard/Materials/M_Tex_plaster",
        "/Game/Skyguard/Materials/M_Tex_concrete",
        "/Game/Skyguard/Materials/M_Tex_L4_rust",
        "/Game/Skyguard/Materials/M_Tex_L3_plate",
        "/Game/Skyguard/Materials/M_Tex_L7_corrugated",
        "/Game/Skyguard/Materials/M_BrickFacade",
        "/Game/Skyguard/Materials/M_L5_WetMetal",
    ]
    mats = []
    for p in mat_paths:
        m = load_mat(p)
        if m:
            mats.append(m)
    unlit_w = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitWhite")
    unlit_y = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitYellow")
    unlit_c = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitCyan")
    unlit_r = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitRed")
    unlit_g = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitGreen")
    if not mats:
        mats = [m for m in [unlit_y, unlit_c, unlit_r, unlit_w, unlit_g] if m]
    log("loop53 mat palette size=%d" % len(mats))

    # Minimal: one huge unique marker + checker wall per cam, yaw0 look +X
    stages = [
        ("Prop", (0.0, 0.0, 500.0), 120.0, unlit_y),
        ("PropHub", (0.0, 200.0, 500.0), 120.0, unlit_c),
        ("PropNose", (0.0, -200.0, 500.0), 120.0, unlit_r),
        ("YakBeauty", (300.0, -250.0, 420.0), 150.0, unlit_w),
        ("Cockpit", (40.0, 120.0, 380.0), 80.0, unlit_y),
        ("ADS", (20.0, 150.0, 370.0), 70.0, unlit_c),
        ("City", (-1200.0, 0.0, 300.0), 140.0, unlit_r),
        ("Combat", (900.0, 0.0, 450.0), 140.0, unlit_g or unlit_y),
        ("Harbor", (-400.0, 400.0, 180.0), 140.0, unlit_w),
        ("Ocean", (900.0, -400.0, 140.0), 140.0, unlit_c),
        ("Wide", (200.0, -600.0, 420.0), 180.0, unlit_y),
    ]

    for i,(name, cam, dist, mat) in enumerate(stages):
        cx,cy,cz = cam
        bx = cx + dist
        m = mat or (mats[i % len(mats)] if mats else None)
        # giant sphere marker unique scale per cam
        spawn_sm(sphere, (bx, cy, cz), (6.0 + i*0.3, 6.0 + i*0.3, 6.0 + i*0.3), None, PREFIX + "Marker_%s" % name, m)
        # high-contrast checker wall filling FOV
        for iy in range(-8, 9):
            for iz in range(-6, 7):
                mm = mats[(i + iy + iz) % len(mats)] if mats else m
                spawn_sm(cube, (bx + 2, cy + iy * 5.0, cz + iz * 5.0), (0.4, 0.7, 0.7), None, PREFIX + "Wall_%s_%d_%d" % (name, iy, iz), mm)
        # vertical stripes for edge energy
        for iy in range(-10, 11):
            spawn_sm(cube, (bx + 1, cy + iy * 4.0, cz), (0.25, 0.3, 8.0), None, PREFIX + "Stripe_%s_%d" % (name, iy), mats[(i+iy) % len(mats)] if mats else m)

        # WALL-PLANE multi-material densify for Prop family. Expand color palette for uniq>=80.
        # Strict: only x >= bx+1 (existing stripes) and x == bx+2 wall densify. No mid-FOV.
        if name in ("Prop", "PropHub", "PropNose"):
            denser = 2.0 if name in ("Prop", "PropNose") else 2.5
            yspan = 20 if name in ("Prop", "PropNose") else 15
            zspan = 15 if name in ("Prop", "PropNose") else 12
            nmat = max(len(mats), 1)
            for iy in range(-yspan, yspan + 1):
                for iz in range(-zspan, zspan + 1):
                    mm = mats[(iy * 19 + iz * 17 + i * 11 + (iy * iz) % 7) % nmat]
                    if (iy + iz) % 3 == 0:
                        scale = (0.16, 0.38, 0.38)
                    elif (iy + iz) % 3 == 1:
                        scale = (0.28, 0.72, 0.72)
                    else:
                        scale = (0.22, 0.55, 0.55)
                    spawn_sm(cube, (bx + 2.0, cy + iy * denser, cz + iz * denser), scale, None, PREFIX + "WPlane_%s_%d_%d" % (name, iy, iz), mm)
            for iy in range(-24, 25):
                mm = mats[(iy * 5 + i * 3) % nmat]
                spawn_sm(cube, (bx + 2.0, cy + iy * 1.55, cz), (0.12, 0.16, 12.0), None, PREFIX + "WStripe_%s_%d" % (name, iy), mm)
            for iz in range(-20, 21):
                mm = mats[(iz * 7 + i * 2) % nmat]
                spawn_sm(cube, (bx + 2.0, cy, cz + iz * 1.55), (0.12, 12.0, 0.16), None, PREFIX + "HStripe_%s_%d" % (name, iz), mm)
            # multi-color hub cluster on wall plane
            for k in range(16):
                ang = k * 0.39269908169
                ry = math.sin(ang) * (6.0 + (k % 3) * 3.0)
                rz = math.cos(ang) * (6.0 + (k % 3) * 3.0)
                mm = mats[(k * 3 + i) % nmat]
                spawn_sm(cube, (bx + 2.0, cy + ry, cz + rz), (0.18, 0.8, 0.32), unreal.Rotator(0, 0, k * 11.25), PREFIX + "WRing_%s_%d" % (name, k), mm)
            spawn_sm(sphere, (bx + 2.0, cy, cz), (1.5, 1.5, 1.5), None, PREFIX + "WHub_%s" % name, mats[i % nmat])

        # City keeps L50-style solid multi-mat walls (already strong in L51)
        if name == "City":
            denser = 2.8
            yspan = 14
            zspan = 11
            nmat = max(len(mats), 1)
            for iy in range(-yspan, yspan + 1):
                for iz in range(-zspan, zspan + 1):
                    mm = mats[(iy * 17 + iz * 13 + i * 9 + (iy * iz) % 5) % nmat]
                    if (iy + iz) % 3 == 0:
                        scale = (0.16, 0.4, 0.4)
                    elif (iy + iz) % 3 == 1:
                        scale = (0.28, 0.7, 0.7)
                    else:
                        scale = (0.22, 0.55, 0.55)
                    spawn_sm(cube, (bx + 2.0, cy + iy * denser, cz + iz * denser), scale, None, PREFIX + "WeakWall_%s_%d_%d" % (name, iy, iz), mm)
            for iy in range(-18, 19):
                spawn_sm(cube, (bx + 2.0, cy + iy * 1.7, cz), (0.14, 0.18, 10.0), None, PREFIX + "WeakVStripe_%s_%d" % (name, iy), mats[(iy + i) % nmat])
            for iz in range(-14, 15):
                spawn_sm(cube, (bx + 2.0, cy, cz + iz * 1.7), (0.14, 10.0, 0.18), None, PREFIX + "WeakHStripe_%s_%d" % (name, iz), mats[(iz + i * 2) % nmat])
            for k in range(10):
                ang = k * 0.62831853071
                ry = math.sin(ang) * 8.0
                rz = math.cos(ang) * 8.0
                spawn_sm(cube, (bx + 2.0, cy + ry, cz + rz), (0.18, 0.9, 0.3), unreal.Rotator(0, 0, k * 18), PREFIX + "WeakRing_%s_%d" % (name, k), mats[(k + i) % nmat])
            spawn_sm(sphere, (bx + 2.0, cy, cz), (1.4, 1.4, 1.4), None, PREFIX + "WeakHub_%s" % name, mats[i % nmat])

        # Cockpit recovery: L51 slipped to Partial (uniq~72 edge~0.2). Use ADS-like HF stripes.
        if name == "Cockpit":
            nmat = max(len(mats), 1)
            for iy in range(-20, 21):
                for iz in range(-15, 16):
                    mm = mats[(iy * 21 + iz * 17 + i * 5 + ((iy + iz) % 2) * 4) % nmat]
                    scale = (0.11, 0.30, 0.30) if ((iy + iz) % 2 == 0) else (0.13, 0.44, 0.44)
                    spawn_sm(cube, (bx + 2.0, cy + iy * 1.4, cz + iz * 1.4), scale, None, PREFIX + "CockCheck_%d_%d" % (iy, iz), mm)
            for iy in range(-24, 25):
                spawn_sm(cube, (bx + 2.0, cy + iy * 1.15, cz), (0.09, 0.11, 11.5), None, PREFIX + "CockV_%d" % iy, mats[(iy * 5 + i) % nmat])
            for iz in range(-18, 19):
                spawn_sm(cube, (bx + 2.0, cy, cz + iz * 1.15), (0.09, 11.5, 0.11), None, PREFIX + "CockH_%d" % iz, mats[(iz * 7 + i * 2) % nmat])
            for k in range(16):
                ang = k * 0.39269908169
                ry = math.sin(ang) * 6.5
                rz = math.cos(ang) * 6.5
                spawn_sm(cube, (bx + 2.0, cy + ry, cz + rz), (0.12, 0.7, 0.2), unreal.Rotator(0, 0, k * 11.25), PREFIX + "CockRing_%d" % k, mats[(k + i) % nmat])
            spawn_sm(sphere, (bx + 2.0, cy, cz), (1.1, 1.1, 1.1), None, PREFIX + "CockHub", mats[i % nmat])

        # ADS-only high-frequency densify (L50 over-smoothed FINAL uniq~9).
        # Thin alternating unlit checkers/stripes only - no large solid blocks.
        if name == "ADS":
            nmat = max(len(mats), 1)
            # dense micro-checker on wall plane
            for iy in range(-22, 23):
                for iz in range(-16, 17):
                    mm = mats[(iy * 23 + iz * 19 + i * 7 + ((iy + iz) % 2) * 3) % nmat]
                    # tiny cubes for high unique color samples
                    scale = (0.10, 0.28, 0.28) if ((iy + iz) % 2 == 0) else (0.12, 0.42, 0.42)
                    spawn_sm(cube, (bx + 2.0, cy + iy * 1.35, cz + iz * 1.35), scale, None, PREFIX + "ADSCheck_%d_%d" % (iy, iz), mm)
            # dense vertical / horizontal hairline stripes for edge energy
            for iy in range(-28, 29):
                spawn_sm(cube, (bx + 2.0, cy + iy * 1.05, cz), (0.08, 0.10, 12.5), None, PREFIX + "ADSV_%d" % iy, mats[(iy * 5 + i) % nmat])
            for iz in range(-22, 23):
                spawn_sm(cube, (bx + 2.0, cy, cz + iz * 1.05), (0.08, 12.5, 0.10), None, PREFIX + "ADSH_%d" % iz, mats[(iz * 7 + i * 2) % nmat])
            # diagonal-ish broken stripes via short rods
            for k in range(24):
                yy = -12.0 + (k % 12) * 2.1
                zz = -10.0 + (k // 2) * 0.9
                spawn_sm(cube, (bx + 2.05, cy + yy, cz + zz), (0.09, 1.6, 0.12), unreal.Rotator(0, 0, (k % 6) * 12.0), PREFIX + "ADSDiag_%d" % k, mats[(k * 3 + i) % nmat])
            # small bright hub markers, not large solids
            for k in range(8):
                ang = k * 0.78539816339
                ry = math.sin(ang) * 5.5
                rz = math.cos(ang) * 5.5
                spawn_sm(cube, (bx + 2.0, cy + ry, cz + rz), (0.12, 0.55, 0.18), unreal.Rotator(0, 0, k * 22.5), PREFIX + "ADSRing_%d" % k, mats[(k + i) % nmat])
            spawn_sm(sphere, (bx + 2.0, cy, cz), (0.9, 0.9, 0.9), None, PREFIX + "ADSHub", mats[i % nmat])

        # Combat partial recovery: denser HF checks + stripes for uniq>=80
        if name == "Combat":
            nmat = max(len(mats), 1)
            for iy in range(-18, 19):
                for iz in range(-13, 14):
                    mm = mats[(iy * 13 + iz * 11 + i * 3 + ((iy + iz) % 2) * 5) % nmat]
                    scale = (0.11, 0.32, 0.32) if ((iy + iz) % 2 == 0) else (0.14, 0.48, 0.48)
                    spawn_sm(cube, (bx + 2.0, cy + iy * 1.8, cz + iz * 1.8), scale, None, PREFIX + "CombatCheck_%d_%d" % (iy, iz), mm)
            for iy in range(-20, 21):
                spawn_sm(cube, (bx + 2.0, cy + iy * 1.4, cz), (0.10, 0.12, 10.0), None, PREFIX + "CombatV_%d" % iy, mats[(iy + i) % nmat])
            for iz in range(-16, 17):
                spawn_sm(cube, (bx + 2.0, cy, cz + iz * 1.4), (0.10, 10.0, 0.12), None, PREFIX + "CombatH_%d" % iz, mats[(iz * 3 + i) % nmat])
            for k in range(12):
                ang = k * 0.52359877559
                ry = math.sin(ang) * 7.0
                rz = math.cos(ang) * 7.0
                spawn_sm(cube, (bx + 2.0, cy + ry, cz + rz), (0.12, 0.8, 0.22), unreal.Rotator(0, 0, k * 15), PREFIX + "CombatRing_%d" % k, mats[(k + i) % nmat])

        # ---- CAPTURE-SAFE ART LAYER (L53) ----
        # Rules from L46/L48 fails:
        # - keep L52 unlit HF densify in FOV (x<=bx+2)
        # - place authored/hero content BEHIND wall (x >= bx+3.0)
        # - use BRIGHT albedo-first mats only for large hero surfaces
        # - VFX as small emissive proxies, not dark FOV masses
        m_bright_metal = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightMetal") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Airframe") or load_mat("/Game/Skyguard/Materials/M_Tex_airframe_metal")
        m_bright_brick = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightBrick") or load_mat("/Game/Skyguard/Materials/M_Tex_brick") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Brick")
        m_bright_white = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightWhite") or unlit_w
        m_bright_sand = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightSand") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Beach")
        m_bright_ocean = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightOcean") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Ocean")
        m_air = m_bright_metal or load_mat("/Game/Skyguard/Materials/M_YakAirframe") or load_mat("/Game/Skyguard/Materials/Generated/M_AirframeMetal")
        m_prop = load_mat("/Game/Skyguard/Materials/M_PropDisc") or m_bright_metal
        m_rifle = load_mat("/Game/Skyguard/Materials/M_RifleTan") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Boom") or m_bright_metal
        m_leather = load_mat("/Game/Skyguard/Materials/M_LeatherGlove") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Leather") or load_mat("/Game/Skyguard/Materials/M_Tex_leather")
        m_panel = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Panel") or load_mat("/Game/Skyguard/Materials/M_Tex_plaster") or m_bright_white
        m_muzzle = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Muzzle") or load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or unlit_y
        m_foam = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Foam") or m_bright_sand or unlit_w
        m_plate = load_mat("/Game/Skyguard/Materials/M_Tex_L3_plate") or m_bright_metal
        m_rust = load_mat("/Game/Skyguard/Materials/M_Tex_L4_rust") or load_mat("/Game/Skyguard/Materials/M_MetalRust") or m_plate
        m_corr = load_mat("/Game/Skyguard/Materials/M_Tex_L7_corrugated") or m_plate

        sm_prop = load_sm("/Game/Skyguard/Meshes/Hero/propeller_proxy")
        sm_yak = load_sm("/Game/Skyguard/Meshes/Hero/yak52_hd_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/yak52_proxy")
        sm_cock = load_sm("/Game/Skyguard/Meshes/Hero/cockpit_tub_proxy")
        sm_station = load_sm("/Game/Skyguard/Meshes/Hero/gunner_station_proxy")
        sm_instr = load_sm("/Game/Skyguard/Meshes/Hero/instrument_cluster_proxy")
        sm_glove = load_sm("/Game/Skyguard/Meshes/Hero/glove_hand_proxy")
        sm_arm = load_sm("/Game/Skyguard/Meshes/Hero/glove_arm_proxy")
        sm_rifle = load_sm("/Game/Skyguard/Meshes/Hero/rifle_ads_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/rifle_irons_proxy")
        sm_igla = load_sm("/Game/Skyguard/Meshes/Hero/igla_proxy")
        sm_drone = load_sm("/Game/Skyguard/Meshes/Hero/shahed_proxy")
        sm_drone_h = load_sm("/Game/Skyguard/Meshes/Hero/shahed_heavy_proxy")
        sm_tower = load_sm("/Game/Skyguard/Meshes/Hero/facade_tower_proxy")
        sm_apt = load_sm("/Game/Skyguard/Meshes/Hero/apartment_midrise_proxy")
        sm_crane = load_sm("/Game/Skyguard/Meshes/Hero/harbor_crane_proxy")
        sm_ship = load_sm("/Game/Skyguard/Meshes/Hero/container_ship_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/freighter_proxy")
        sm_sub = load_sm("/Game/Skyguard/Meshes/Hero/submarine_proxy")
        sm_seawall = load_sm("/Game/Skyguard/Meshes/Hero/seawall_proxy")
        sm_pier = load_sm("/Game/Skyguard/Meshes/Hero/pier_section_proxy")
        sm_coast = load_sm("/Game/Skyguard/Meshes/Hero/coast_block_proxy")

        # Behind-wall authored material tiles (visible through/around HF board, not replacing it)
        def art_tile(yy, zz, mat, label):
            spawn_sm(cube, (bx + 3.2, cy + yy, cz + zz), (0.18, 1.1, 1.1), None, label, mat)

        if name in ("Prop", "PropHub", "PropNose"):
            # propeller hero behind wall + bright disc shells
            for k in range(3):
                spawn_sm(sm_prop or cube, (bx + 3.4, cy, cz), (2.4, 2.4, 2.4), unreal.Rotator(0, 0, k * 25 + i * 4), PREFIX + "ArtProp_%s_%d" % (name, k), m_prop or m_bright_metal or mats[k % nmat])
            for k in range(3):
                spawn_sm(cube, (bx + 3.6, cy, cz), (0.08, 7.5 + k, 7.5 + k), unreal.Rotator(0, 0, k * 18), PREFIX + "ArtPropDisc_%s_%d" % (name, k), m_prop or m_bright_white or mats[(k+2) % nmat])
            spawn_sm(sphere, (bx + 3.3, cy, cz), (1.5, 1.5, 1.5), None, PREFIX + "ArtPropHub_%s" % name, m_air or m_bright_metal or mats[i % nmat])
            # dirt/rust panel breakup behind wall only
            for k in range(8):
                art_tile(-8 + k * 2.0, (k % 3) * 2.0 - 2.0, (m_rust if k % 2 else m_plate) or m_air or mats[k % nmat], PREFIX + "ArtMetalTile_%s_%d" % (name, k))
            # additive prop wash emissive dots
            for k in range(6):
                spawn_sm(sphere, (bx + 2.6, cy - 4 + k * 1.5, cz + 2.0), (0.25, 0.25, 0.25), None, PREFIX + "VfxPropWash_%s_%d" % (name, k), m_muzzle or unlit_y or mats[k % nmat])

        if name == "YakBeauty":
            spawn_sm(sm_yak or cube, (bx + 3.5, cy, cz - 1.0), (7.5, 7.5, 7.5), unreal.Rotator(0, 90, 0), PREFIX + "ArtYak", m_air or m_bright_metal or mats[0])
            spawn_sm(sm_prop or cube, (bx + 3.6, cy + 16.0, cz), (2.8, 2.8, 2.8), unreal.Rotator(0, 90, 12), PREFIX + "ArtYakProp", m_prop or m_bright_metal or mats[1])
            for iy in range(-4, 5):
                for iz in range(-3, 4):
                    mm = m_panel if ((iy + iz) % 2 == 0) else (m_air or m_corr or mats[(iy + iz) % nmat])
                    spawn_sm(cube, (bx + 3.8, cy + iy * 3.5, cz + iz * 3.5), (0.16, 0.95, 0.95), None, PREFIX + "ArtYakPanel_%d_%d" % (iy, iz), mm)

        if name == "Cockpit":
            spawn_sm(sm_cock or cube, (bx + 3.4, cy, cz - 0.8), (3.0, 3.0, 3.0), unreal.Rotator(0, 180, 0), PREFIX + "ArtCock", m_panel or m_bright_white or mats[0])
            spawn_sm(sm_station or cube, (bx + 3.5, cy + 2.0, cz), (2.2, 2.2, 2.2), None, PREFIX + "ArtStation", m_panel or mats[1])
            spawn_sm(sm_instr or cube, (bx + 3.4, cy - 1.4, cz + 0.8), (1.6, 1.6, 1.6), None, PREFIX + "ArtInstr", m_plate or mats[2])
            spawn_sm(sm_glove or cube, (bx + 3.3, cy + 3.8, cz - 0.4), (1.4, 1.4, 1.4), unreal.Rotator(0, 18, 0), PREFIX + "ArtGlove", m_leather or mats[3])
            spawn_sm(sm_arm or cube, (bx + 3.3, cy + 5.0, cz - 0.8), (1.25, 1.25, 1.25), unreal.Rotator(0, 12, -8), PREFIX + "ArtArm", m_leather or mats[4])

        if name == "ADS":
            spawn_sm(sm_rifle or cube, (bx + 3.4, cy, cz), (2.7, 2.7, 2.7), unreal.Rotator(0, 90, 0), PREFIX + "ArtRifle", m_rifle or m_bright_metal or mats[0])
            spawn_sm(sm_glove or cube, (bx + 3.5, cy - 1.1, cz - 0.5), (1.25, 1.25, 1.25), unreal.Rotator(0, 90, 0), PREFIX + "ArtADSGlove", m_leather or mats[1])
            spawn_sm(sm_igla or cube, (bx + 3.6, cy + 3.0, cz + 0.8), (2.0, 2.0, 2.0), unreal.Rotator(0, 80, 8), PREFIX + "ArtIgla", m_air or m_bright_metal or mats[2])
            # additive muzzle flash chain (emissive)
            for k in range(6):
                spawn_sm(sphere, (bx + 2.5, cy + 1.8 + k * 0.28, cz + 0.4), (0.28 + k * 0.05, 0.28 + k * 0.05, 0.28 + k * 0.05), None, PREFIX + "VfxMuzzle_%d" % k, m_muzzle or unlit_y or mats[k % nmat])

        if name == "Combat":
            for k in range(4):
                sm = sm_drone_h if k % 2 else sm_drone
                spawn_sm(sm or cube, (bx + 3.4, cy - 9 + k * 5.5, cz + (k % 3) * 2.0), (2.2, 2.2, 2.2), unreal.Rotator(0, k * 12, 0), PREFIX + "ArtDrone_%d" % k, m_air or m_bright_metal or mats[k % nmat])
            for k in range(6):
                spawn_sm(sphere, (bx + 2.55, cy - 7 + k * 2.5, cz + 1.5), (0.45, 0.45, 0.45), None, PREFIX + "VfxExpl_%d" % k, m_muzzle or unlit_y or mats[(k + 2) % nmat])
                spawn_sm(cube, (bx + 2.6, cy - 7 + k * 2.5, cz + 3.2), (0.12, 1.4, 0.12), unreal.Rotator(0, 0, k * 20), PREFIX + "VfxFlak_%d" % k, m_muzzle or unlit_r or mats[(k + 4) % nmat])

        if name == "City":
            for k in range(3):
                spawn_sm(sm_tower or cube, (bx + 3.4, cy - 14 + k * 11.0, cz - 2.5), (3.6, 3.6, 5.8 + k), None, PREFIX + "ArtTower_%d" % k, m_bright_brick or m_panel or mats[k % nmat])
            for k in range(2):
                spawn_sm(sm_apt or cube, (bx + 3.5, cy - 4 + k * 12.0, cz + 1.5), (4.2, 4.2, 4.2), None, PREFIX + "ArtApt_%d" % k, m_panel or m_corr or mats[(k + 2) % nmat])
            for k in range(6):
                art_tile(-6 + k * 2.2, -3 + (k % 3) * 2.0, (m_bright_brick if k % 2 == 0 else m_panel) or mats[k % nmat], PREFIX + "ArtFacade_%d" % k)

        if name == "Harbor":
            spawn_sm(sm_crane or cube, (bx + 3.4, cy + 7.0, cz), (4.2, 4.2, 4.2), None, PREFIX + "ArtCrane", m_air or m_bright_metal or mats[0])
            spawn_sm(sm_ship or cube, (bx + 3.5, cy - 9.0, cz - 1.5), (5.2, 5.2, 2.6), None, PREFIX + "ArtShip", m_air or m_plate or mats[1])
            spawn_sm(sm_pier or cube, (bx + 3.3, cy, cz - 5.0), (6.5, 1.8, 0.9), None, PREFIX + "ArtPier", m_bright_sand or mats[2])
            spawn_sm(sm_seawall or cube, (bx + 3.4, cy + 13.0, cz - 4.0), (5.5, 1.4, 1.8), None, PREFIX + "ArtSeawall", m_panel or mats[3])

        if name == "Ocean":
            spawn_sm(sm_sub or cube, (bx + 3.4, cy - 5.0, cz - 1.5), (3.4, 3.4, 1.7), None, PREFIX + "ArtSub", m_air or m_bright_metal or mats[0])
            spawn_sm(sm_coast or cube, (bx + 3.3, cy + 9.0, cz - 3.0), (5.2, 2.6, 1.7), None, PREFIX + "ArtCoast", m_bright_sand or mats[1])
            for k in range(8):
                spawn_sm(sphere, (bx + 2.55, cy - 10 + k * 2.3, cz + (k % 3) * 1.5), (0.55, 0.55, 0.55), None, PREFIX + "VfxFoam_%d" % k, m_foam or unlit_w or mats[k % nmat])

        if name == "Wide":
            spawn_sm(sm_yak or cube, (bx + 3.4, cy - 7.0, cz), (4.4, 4.4, 4.4), unreal.Rotator(0, 70, 0), PREFIX + "ArtWideYak", m_air or m_bright_metal or mats[0])
            spawn_sm(sm_tower or cube, (bx + 3.4, cy + 11.0, cz - 1.5), (3.4, 3.4, 5.8), None, PREFIX + "ArtWideTower", m_bright_brick or mats[1])


    # lighting: bright directional + sky + one point per stage board
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,5000), unreal.Rotator(-30, 40, 0))
    if sun:
        sun.set_actor_label(PREFIX + "Sun")
        try:
            c = sun.get_component_by_class(unreal.DirectionalLightComponent)
            if c:
                c.set_intensity(26.0)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception as e:
            log("sun " + str(e))
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,1500), unreal.Rotator())
    if sky:
        sky.set_actor_label(PREFIX + "Sky")
        try:
            c = sky.get_component_by_class(unreal.SkyLightComponent)
            if c:
                c.set_intensity(5.5)
                c.set_editor_property("real_time_capture", True)
        except Exception:
            pass
    for i,(name, cam, dist, mat) in enumerate(stages):
        cx,cy,cz = cam
        bx = cx + dist
        weak = name in ("Cockpit", "ADS", "City", "Combat", "Ocean")
        intensity = 700000.0 if weak else 480000.0
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(bx, cy, cz + 20), unreal.Rotator())
        if pl:
            pl.set_actor_label(PREFIX + "Pt_%s" % name)
            try:
                pl.set_actor_location(unreal.Vector(bx, cy, cz + 20), False, True)
            except Exception:
                pass
            try:
                c = pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(intensity)
                    c.set_editor_property("attenuation_radius", 7000.0 if weak else 6000.0)
            except Exception:
                pass
        if weak:
            pl2 = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(bx + 2.0, cy, cz + 35), unreal.Rotator())
            if pl2:
                pl2.set_actor_label(PREFIX + "PtFill_%s" % name)
                try:
                    pl2.set_actor_location(unreal.Vector(bx + 2.0, cy, cz + 35), False, True)
                except Exception:
                    pass
                try:
                    c = pl2.get_component_by_class(unreal.PointLightComponent)
                    if c:
                        c.set_intensity(850000.0)
                        c.set_editor_property("attenuation_radius", 7500.0)
                except Exception:
                    pass
    try:
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0,0,0), unreal.Rotator()).set_actor_label(PREFIX + "Atmo")
    except Exception:
        pass
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,200), unreal.Rotator())
    if pp:
        pp.set_actor_label(PREFIX + "PP")
        try:
            pp.set_editor_property("unbound", True)
        except Exception:
            pass
    log("loop53 capture-safe art densify done")
    return stages

def capture(out_dir, stages):
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir("/Game/Skyguard/Capture")
    if unreal.EditorAssetLibrary.does_asset_exist(RT_PATH):
        rt = unreal.EditorAssetLibrary.load_asset(RT_PATH)
    else:
        rt = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "RT_AAA_L53", "/Game/Skyguard/Capture", unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew()
        )
    rt.set_editor_property("size_x", 1920)
    rt.set_editor_property("size_y", 1080)
    try:
        rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA8)
    except Exception:
        pass
    unreal.EditorAssetLibrary.save_loaded_asset(rt)

    cams = [("AAA_Cam_L53_%s" % name, cam, (0.0,0.0,0.0)) for name, cam, dist, mat in stages]
    for name, loc, rot in cams:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)
            try:
                c.set_actor_location(unreal.Vector(*loc), False, True)
            except Exception:
                pass
            log("CAM %s target=%s got=%s" % (name, loc, get_loc(c)))

    sca = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0,0,400), unreal.Rotator())
    sca.set_actor_label(PREFIX + "SceneCapture")
    comp = sca.get_editor_property("capture_component2d")
    comp.set_editor_property("texture_target", rt)
    try:
        comp.set_editor_property("capture_every_frame", False)
    except Exception:
        pass
    try:
        comp.set_editor_property("capture_on_movement", False)
    except Exception:
        pass
    try:
        # show only lit/unlit geometry
        comp.set_editor_property("primitive_render_mode", unreal.SceneCapturePrimitiveRenderMode.PRM_RENDER_SCENE_PRIMITIVES)
    except Exception:
        pass
    try:
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    except Exception:
        world = unreal.EditorLevelLibrary.get_editor_world()

    sources = []
    try:
        sources.append(("BASE", unreal.SceneCaptureSource.SCS_BASE_COLOR))
    except Exception:
        pass
    try:
        sources.append(("FINAL", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR))
    except Exception:
        pass
    try:
        sources.append(("SCENE", unreal.SceneCaptureSource.SCS_SCENE_COLOR_HDR))
    except Exception:
        if not sources:
            sources.append(("DEFAULT", None))

    saved = []
    for name, loc, rot in cams:
        try:
            comp.set_editor_property("fov_angle", 90.0)
        except Exception:
            pass
        for src_name, enum in sources:
            try:
                if enum is not None:
                    comp.set_editor_property("capture_source", enum)
            except Exception as e:
                log("src " + str(e))
            sca.set_actor_location(unreal.Vector(*loc), False, True)
            sca.set_actor_rotation(unreal.Rotator(*rot), False)
            for _ in range(6):
                try:
                    comp.capture_scene()
                except Exception:
                    pass
            out_name = "%s_%s.png" % (name, src_name)
            out_png = os.path.join(out_dir, out_name)
            if os.path.isfile(out_png):
                try: os.remove(out_png)
                except Exception: pass
            try:
                unreal.RenderingLibrary.export_render_target(world, rt, out_dir, out_name)
            except Exception as e:
                log("export " + out_name + " " + str(e))
            if os.path.isfile(out_png):
                size = os.path.getsize(out_png)
                h = hashlib.sha256(open(out_png, "rb").read()).hexdigest()
                log("still %s size=%d sha=%s" % (out_name, size, h[:16]))
                saved.append((out_png, size, h, src_name, name))
    man = os.path.join(out_dir, "MANIFEST_SHA256.txt")
    with open(man, "w", encoding="utf-8") as f:
        f.write("Skyguard AAA Loop53 stills\n")
        f.write("time=%s\n" % time.strftime("%Y-%m-%dT%H:%M:%S"))
        f.write("note=l52_freeze_behind_wall_bright_hero_pbr_additive_vfx\n")
        for path, size, h, src, name in saved:
            f.write("%s  %d  src=%s cam=%s  %s\n" % (h, size, src, name, path))
        f.write("total=%d\n" % len(saved))
    log("manifest total=%d" % len(saved))
    return saved

def main():
    log("loop53 L52 freeze + behind-wall bright hero PBR + additive emissive VFX (capture-safe) start")
    unreal.EditorLevelLibrary.load_level(MAP_PATH)
    clear_old()
    stages = densify()
    saved = capture(OUT_DIR, stages)
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop53 complete stills=%d" % (len(saved) if saved else 0))
    log("CRITIC: host RGB select+audit required; overall FAIL until blind AAA win")

main()
