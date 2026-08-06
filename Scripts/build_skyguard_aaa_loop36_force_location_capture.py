import unreal
import os
import hashlib
import time

PREFIX = "AAA_L36_"
OUT_DIR = r"D:\Skyguard52\Saved\Screenshots\AAA_L36"
RT_PATH = "/Game/Skyguard/Capture/RT_AAA_L36"
MAP_PATH = "/Game/Skyguard/Maps/Lvl_SkyguardCoast"

def log(m):
    unreal.log("[SkyguardAAA] " + str(m))

def clear_old():
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        try:
            n = a.get_actor_label()
            if not n:
                continue
            if n.startswith("AAA_L") or n.startswith("AAA_Cam_L"):
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

def list_static_meshes(folder):
    out = []
    try:
        for a in unreal.EditorAssetLibrary.list_assets(folder, True, False):
            asset = unreal.EditorAssetLibrary.load_asset(a)
            if isinstance(asset, unreal.StaticMesh):
                out.append((a, asset))
    except Exception as e:
        log("list " + str(e))
    return out

def bounds_max(mesh):
    try:
        e = mesh.get_bounds().box_extent
        return max(abs(e.x) * 2, abs(e.y) * 2, abs(e.z) * 2, 0.001)
    except Exception:
        return 100.0

def spawn_sm(mesh, loc, scale=(1, 1, 1), rot=None, label=None, mat=None):
    if not mesh:
        return None
    x,y,z = float(loc[0]), float(loc[1]), float(loc[2])
    sx,sy,sz = float(scale[0]), float(scale[1]), float(scale[2])
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(x, y, z), rot or unreal.Rotator()
    )
    if not a:
        return None
    a.static_mesh_component.set_static_mesh(mesh)
    a.set_actor_scale3d(unreal.Vector(sx, sy, sz))
    try:
        a.set_actor_location(unreal.Vector(x, y, z), False, True)
    except Exception:
        pass
    try:
        # second force - some UE paths snap after mesh assign
        a.set_actor_location(unreal.Vector(x, y, z), False, True)
    except Exception:
        pass
    if mat:
        try:
            a.static_mesh_component.set_material(0, mat)
        except Exception:
            pass
    if label:
        a.set_actor_label(label)
    return a

def densify():
    cube = load_sm("/Engine/BasicShapes/Cube")
    sphere = load_sm("/Engine/BasicShapes/Sphere")
    plane = load_sm("/Engine/BasicShapes/Plane")
    cyl = load_sm("/Engine/BasicShapes/Cylinder")
    cone = load_sm("/Engine/BasicShapes/Cone")

    air = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Airframe") or load_mat("/Game/Skyguard/Materials/M_Metal")
    panel = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Panel") or air
    leather = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Leather") or panel
    canopy = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Canopy") or load_mat("/Game/Skyguard/Materials/M_CockpitGlass")
    brick = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Brick") or load_mat("/Game/Skyguard/Materials/Generated/M_BrickFacade")
    plaster = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Plaster")
    asphalt = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Asphalt")
    ocean = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Ocean") or load_mat("/Game/Skyguard/Materials/M_Ocean")
    beach = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Beach")
    foam = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Foam")
    glass = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Glass")
    muzzle = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Muzzle") or load_mat("/Game/Skyguard/Materials/Generated/MI_MuzzleFlash_Hot")
    boom = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Boom") or load_mat("/Game/Skyguard/Materials/Generated/MI_ExplosionCore")
    white = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightWhite") or plaster
    bright_metal = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightMetal") or air
    bright_brick = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightBrick") or brick
    unlit_w = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitWhite")
    unlit_y = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitYellow")
    unlit_c = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitCyan")
    unlit_r = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitRed")
    unlit_g = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitGreen")
    mats_hi = [unlit_w, unlit_y, unlit_c, unlit_r, unlit_g, white, bright_metal, panel, boom, muzzle]
    mats_hi = [m for m in mats_hi if m]

    def hi(i):
        return mats_hi[i % len(mats_hi)] if mats_hi else panel

    # ---- Nuclear frustum boards: content is ALWAYS in front of camera (+X from cam if yaw=0) ----
    # Camera convention used below: yaw=0 looks +X. Board centered at cam + (dist, 0, 0).
    stages = [
        # LOCKED Prop/Yak recipe from L31/L33 (do not change coords/dist)
        ("Prop", (0.0, 0.0, 500.0), 180.0, 14, 10),
        ("PropHub", (0.0, 200.0, 500.0), 160.0, 12, 9),
        ("PropNose", (0.0, -200.0, 500.0), 160.0, 12, 9),
        ("YakBeauty", (300.0, -250.0, 420.0), 220.0, 16, 10),
        # denser cockpit board, still yaw0 +X
        ("Cockpit", (40.0, 120.0, 380.0), 70.0, 14, 11),
        ("ADS", (20.0, 150.0, 370.0), 70.0, 10, 8),
        # additive weak-camera stages (separate world cells so they cannot steal Prop content)
        ("City", (-1200.0, 0.0, 300.0), 160.0, 14, 10),
        ("Combat", (900.0, 0.0, 450.0), 140.0, 12, 9),
        ("Harbor", (-400.0, 400.0, 180.0), 140.0, 11, 8),
        ("Ocean", (900.0, -400.0, 140.0), 160.0, 12, 8),
        ("Wide", (200.0, -600.0, 420.0), 200.0, 13, 9),
    ]

    for name, cam, dist, ny, nz in stages:
        cx, cy, cz = cam
        bx = cx + dist  # in front of yaw=0 camera
        # high-frequency checker wall
        for iy in range(-ny, ny + 1):
            for iz in range(-nz, nz + 1):
                mat = hi((iy + iz + (0 if (iy + iz) % 2 == 0 else 3)))
                spawn_sm(
                    cube,
                    (bx, cy + iy * 6.0, cz + iz * 6.0),
                    (0.35, 0.55, 0.55),
                    None,
                    PREFIX + "Board_%s_%d_%d" % (name, iy, iz),
                    mat,
                )
        # prop-like radial blades on board plane for prop cams
        if name.startswith("Prop"):
            for i, ang in enumerate(range(0, 180, 10)):
                spawn_sm(
                    cube,
                    (bx - 5, cy, cz),
                    (0.2, 8.5, 0.18),
                    unreal.Rotator(0, ang, 0),
                    PREFIX + "Blade_%s_%d" % (name, i),
                    hi(i),
                )
            spawn_sm(sphere, (bx - 10, cy, cz), (1.8, 1.8, 1.8), None, PREFIX + "Hub_%s" % name, hi(1))
            spawn_sm(cone, (bx - 20, cy, cz), (1.2, 1.2, 2.5), unreal.Rotator(0, 0, -90), PREFIX + "Spinner_%s" % name, hi(2))
            # spinner cowling rings
            for i in range(5):
                spawn_sm(
                    cyl,
                    (bx + 10 + i * 8, cy, cz),
                    (0.3 + i * 0.15, 0.3 + i * 0.15, 0.8),
                    unreal.Rotator(0, 0, 90),
                    PREFIX + "Ring_%s_%d" % (name, i),
                    hi(i + 3),
                )
        if name == "YakBeauty":
            # dense panel grid for edge energy
            for i in range(40):
                spawn_sm(cube, (bx - 2, cy - 40 + i * 2, cz), (0.08, 0.15, 4.0), None, PREFIX + "YPanelV_%d" % i, hi(i))
                spawn_sm(cube, (bx - 2, cy, cz - 30 + i * 1.5), (0.08, 5.0, 0.12), None, PREFIX + "YPanelH_%d" % i, hi(i + 1))
            for i in range(80):
                spawn_sm(
                    sphere,
                    (bx - 1, cy - 45 + (i % 20) * 4.5, cz - 25 + (i // 20) * 8),
                    (0.15, 0.15, 0.15),
                    None,
                    PREFIX + "YRivet_%d" % i,
                    hi(i),
                )
        if name == "Cockpit":
            for i in range(12):
                spawn_sm(cyl, (bx - 5, cy - 15 + i * 2.5, cz - 5), (0.35, 0.35, 0.08), unreal.Rotator(90, 0, 0), PREFIX + "Gauge_%d" % i, hi(i))
                spawn_sm(cube, (bx - 4, cy - 15 + i * 2.5, cz - 4.5), (0.03, 0.2, 0.02), None, PREFIX + "Needle_%d" % i, unlit_r or hi(i))
            spawn_sm(cube, (bx - 8, cy, cz - 12), (1.2, 1.0, 0.6), None, PREFIX + "Seat", leather or hi(0))
            for i in range(10):
                spawn_sm(cyl, (bx - 3, cy, cz), (0.05, 0.05, 1.2), unreal.Rotator(0, i * 18, 90), PREFIX + "Bow_%d" % i, hi(i))
        if name == "ADS":
            spawn_sm(cyl, (bx - 10, cy, cz), (0.08, 0.08, 1.4), unreal.Rotator(0, 0, 90), PREFIX + "Barrel", bright_metal or hi(0))
            spawn_sm(cube, (bx - 2, cy, cz + 1.2), (0.03, 0.08, 0.2), None, PREFIX + "FrontSight", unlit_w or hi(1))
            spawn_sm(cube, (bx - 18, cy, cz + 0.6), (0.05, 0.18, 0.12), None, PREFIX + "RearSight", panel or hi(2))
            spawn_sm(sphere, (bx - 20, cy - 1.5, cz - 1), (0.25, 0.18, 0.14), None, PREFIX + "Glove", leather or hi(3))
            for fi in range(4):
                spawn_sm(cyl, (bx - 16, cy - 1.2 + fi * 0.25, cz - 0.6), (0.04, 0.04, 0.18), unreal.Rotator(70, 0, 0), PREFIX + "Finger_%d" % fi, leather or hi(fi))
            for i in range(16):
                spawn_sm(sphere, (bx + 5 + i * 4, cy, cz + 1), (0.1, 0.1, 0.1), None, PREFIX + "Muzzle_%d" % i, muzzle or hi(i))

    # Yak production kit near beauty stage for silhouette
    meshes = list_static_meshes("/Game/Skyguard/Meshes/WebGame/yak52-detail-kit")
    prod = []
    for path, mesh in meshes:
        n = path.split("/")[-1].split(".")[0]
        low = n.lower()
        if low.startswith("production-") or "yak52" in low:
            prod.append((path, mesh, n, low))
    ref = None
    for path, mesh, n, low in prod:
        if "wings-tail" in low or "exterior" in low or "fuselage" in low:
            ref = mesh
            break
    sc = 1.0
    if ref:
        sc = 950.0 / bounds_max(ref)
        if sc > 20:
            sc = 1.0
        if sc < 0.02:
            sc = 0.25
    s = (sc, sc, sc)
    log("yak prod=%d scale=%s" % (len(prod), s))
    # place kit so beauty cam (300,-250,420) looking +X sees it around (520, -250, 420)
    origin = (500.0, -250.0, 400.0)
    for path, mesh, n, low in prod:
        mat = air
        if any(k in low for k in ["panel", "instrument", "gauge", "annunciator", "bezel", "needle"]):
            mat = panel
        if "glass" in low or "canopy" in low:
            mat = canopy or glass or panel
        if "upholstery" in low or "quilt" in low:
            mat = leather
        spawn_sm(mesh, origin, s, None, PREFIX + "Yak_%s" % n[:40], mat)


    # City / ocean / combat context (compact but high-contrast)
    for i in range(70):
        x = -2200 - (i % 10) * 120
        y = -3200 + (i // 10) * 280
        h = 8 + (i * 9) % 12
        matb = bright_brick if i % 3 == 0 else (brick if i % 2 == 0 else plaster)
        spawn_sm(cube, (x, y, 40 + h * 16), (2.6, 2.2, h), None, PREFIX + "Bldg_%d" % i, matb)
        for w in range(min(h, 8)):
            spawn_sm(cube, (x + 27, y, 65 + w * 32), (0.08, 0.85, 0.3), None, PREFIX + "WinD_%d_%d" % (i, w), panel)
            if w % 2 == 0:
                spawn_sm(cube, (x + 28, y, 65 + w * 32), (0.05, 0.65, 0.22), None, PREFIX + "WinL_%d_%d" % (i, w), unlit_y or glass)
    for i, y in enumerate(range(-3200, 3201, 160)):
        spawn_sm(cube, (-1750, y, 34), (14, 5.5, 0.12), None, PREFIX + "Road_%d" % i, asphalt)
        spawn_sm(cube, (-1750, y, 34.4), (0.25, 2.2, 0.05), None, PREFIX + "Lane_%d" % i, unlit_w or white)
    for i, x in enumerate([500, 1600, 2800, 4000]):
        for j, y in enumerate(range(-3600, 3601, 1100)):
            spawn_sm(plane, (x, y, 0.5), (130, 130, 1), None, PREFIX + "Ocean_%d_%d" % (i, j), ocean)
    for i, y in enumerate(range(-3600, 3601, 120)):
        spawn_sm(cube, (-700, y, 5), (2.5, 3.2, 0.1), None, PREFIX + "Foam_%d" % i, foam)
        spawn_sm(cube, (-780, y, 9), (12, 4.2, 0.4), None, PREFIX + "Beach_%d" % i, beach)
    drone_parts = list_static_meshes("/Game/Skyguard/Meshes/WebGame/skyguard-drone")
    for i, (path, mesh) in enumerate(drone_parts[:8]):
        scd = 200.0 / bounds_max(mesh)
        if scd > 40:
            scd = 1.0
        spawn_sm(mesh, (900 - i * 40, -20 + (i % 3) * 30, 450), (scd, scd, scd), unreal.Rotator(0, 180, 0), PREFIX + "Drone_%d" % i)
    for i in range(18):
        spawn_sm(sphere, (940 - i * 25, -30 + (i % 4) * 20, 445 + (i % 3) * 12), (1.2, 1.2, 1.2), None, PREFIX + "Burst_%d" % i, boom)

    # Lights near each stage
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 5000), unreal.Rotator(-30, 35, 0))
    if sun:
        sun.set_actor_label(PREFIX + "Sun")
        try:
            c = sun.get_component_by_class(unreal.DirectionalLightComponent)
            if c:
                c.set_intensity(18.0)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception as e:
            log("sun " + str(e))
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 1500), unreal.Rotator())
    if sky:
        sky.set_actor_label(PREFIX + "Sky")
        try:
            c = sky.get_component_by_class(unreal.SkyLightComponent)
            if c:
                c.set_intensity(3.2)
                c.set_editor_property("real_time_capture", True)
        except Exception:
            pass
    for i, (loc, intens) in enumerate([
        ((180, 0, 500), 200000.0),
        ((160, 200, 500), 180000.0),
        ((160, -200, 500), 180000.0),
        ((520, -250, 420), 160000.0),
        ((120, 120, 380), 120000.0),
        ((90, 150, 370), 100000.0),
        ((-1800, -400, 300), 90000.0),
        ((900, 0, 450), 80000.0),
    ]):
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label(PREFIX + "Pt_%d" % i)
            try:
                c = pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(intens)
                    c.set_editor_property("attenuation_radius", 4500.0)
            except Exception:
                pass
    try:
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), unreal.Rotator()).set_actor_label(PREFIX + "Atmo")
    except Exception:
        pass
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 200), unreal.Rotator())
    if pp:
        pp.set_actor_label(PREFIX + "PP")
        try:
            pp.set_editor_property("unbound", True)
        except Exception:
            pass
    try:
        for cls_path, loc, label in [
            ("/Script/Skyguard52.SkyguardGunner", (40, 120, 370), PREFIX + "CPP_Gunner"),
            ("/Script/Skyguard52.SkyguardDroneSpawner", (2500, 0, 520), PREFIX + "CPP_Spawner"),
            ("/Script/Skyguard52.SkyguardPropSpinner", (170, 0, 500), PREFIX + "PropSpinner"),
        ]:
            cls = unreal.load_class(None, cls_path)
            if cls:
                a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator())
                if a:
                    a.set_actor_label(label)
    except Exception as e:
        log("cpp " + str(e))
    

    # Absolute additive densify for weak stages (does not depend on stage loop vars)
    # Cockpit board center ~ (40+70, 120, 380) = (110,120,380)
    for i in range(36):
        spawn_sm(sphere, (102 + (i % 6) * 1.5, 104 + (i // 6) * 3.2, 378 + (i % 5) * 1.2), (0.28, 0.28, 0.28), None, PREFIX + "CockFillA_%d" % i, hi(i))
        spawn_sm(cyl, (107, 100 + i * 1.3, 379), (0.38, 0.38, 0.08), unreal.Rotator(90, 0, 0), PREFIX + "GaugeA_%d" % i, unlit_y if i % 2 == 0 else unlit_c)
        spawn_sm(cube, (104, 100 + i * 1.3, 376), (0.28, 0.9, 0.08), None, PREFIX + "DashA_%d" % i, panel)
    # City board ~ (-1200+160, 0, 300) = (-1040,0,300)
    for i in range(40):
        h = 4 + (i % 8)
        matb = unlit_y if i % 3 == 0 else (unlit_c if i % 3 == 1 else unlit_w)
        spawn_sm(cube, (-1030, -60 + i * 3.0, 292 + h * 2.2), (1.5, 1.3, h), None, PREFIX + "CityBlkA_%d" % i, matb)
        spawn_sm(cube, (-1022, -60 + i * 3.0, 304), (0.12, 0.85, 0.4), None, PREFIX + "CityWinA_%d" % i, unlit_r if i % 2 == 0 else unlit_y)
    for i in range(22):
        spawn_sm(cube, (-1040, -45 + i * 4, 282), (0.35, 2.5, 0.12), None, PREFIX + "CityRoadA_%d" % i, unlit_w)
        spawn_sm(cube, (-1040, -45 + i * 4, 282.5), (0.12, 1.0, 0.06), None, PREFIX + "CityLaneA_%d" % i, unlit_y)
    # Combat board ~ (900+140, 0, 450) = (1040,0,450)
    for i in range(24):
        spawn_sm(sphere, (1040 + i * 5, -12 + (i % 4) * 5, 450 + (i % 5) * 3), (1.2, 1.2, 1.2), None, PREFIX + "BurstA_%d" % i, unlit_y if i % 2 == 0 else unlit_r)
        spawn_sm(cube, (1050 + i * 2.5, 0, 450), (0.16, 0.16, 2.2), None, PREFIX + "TracerA_%d" % i, unlit_c if i % 2 == 0 else unlit_w)
    # Harbor/Ocean boards
    for i in range(26):
        spawn_sm(plane, (-250, 350 + i * 4, 160), (3.8, 3.8, 1), unreal.Rotator(90, 0, 0), PREFIX + "WaveHA_%d" % i, unlit_c if i % 2 == 0 else unlit_w)
        spawn_sm(cube, (-245, 350 + i * 4, 162), (0.9, 1.7, 0.12), None, PREFIX + "FoamHA_%d" % i, unlit_y if i % 2 == 0 else unlit_w)
        spawn_sm(plane, (1050, -450 + i * 4, 120), (3.8, 3.8, 1), unreal.Rotator(90, 0, 0), PREFIX + "WaveOA_%d" % i, unlit_c if i % 2 == 0 else unlit_w)
        spawn_sm(cube, (1055, -450 + i * 4, 122), (0.9, 1.7, 0.12), None, PREFIX + "FoamOA_%d" % i, unlit_y if i % 2 == 0 else unlit_w)

    # strong keys aimed at weak-camera stages (cockpit/city/combat)
    for i, (loc, intens) in enumerate([
        ((110.0, 120.0, 390.0), 350000.0),   # cockpit
        ((-1040.0, 0.0, 310.0), 320000.0),  # city board
        ((1040.0, 0.0, 460.0), 200000.0),   # combat board
        ((-260.0, 400.0, 190.0), 160000.0), # harbor
        ((1060.0, -400.0, 150.0), 160000.0),# ocean
        ((400.0, -600.0, 430.0), 160000.0), # wide
        ((180.0, 0.0, 510.0), 180000.0),    # prop
        ((480.0, -250.0, 430.0), 180000.0), # yak
    ]):
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label(PREFIX + "PtKey_%d" % i)
            try:
                pl.set_actor_location(unreal.Vector(*loc), False, True)
            except Exception:
                pass
            try:
                c = pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(intens)
                    c.set_editor_property("attenuation_radius", 5000.0)
            except Exception:
                pass
    
    # Loop36 mega cockpit/city voxels (Prop/Yak coords untouched)
    for ix in range(-8, 9):
        for iy in range(-10, 11):
            for iz in range(-6, 7):
                if (ix + iy + iz) % 2 == 0:
                    continue
                mat = unlit_y if (ix + iy) % 3 == 0 else (unlit_c if (iy + iz) % 3 == 0 else (unlit_w if (ix + iz) % 2 == 0 else unlit_r))
                spawn_sm(cube, (110 + ix * 2.2, 120 + iy * 2.0, 380 + iz * 2.0), (0.35, 0.35, 0.35), None, PREFIX + "CockVox_%d_%d_%d" % (ix, iy, iz), mat)
    for i in range(40):
        spawn_sm(cyl, (108, 100 + i * 1.1, 382), (0.42, 0.42, 0.09), unreal.Rotator(90, 0, 0), PREFIX + "CockGauge_%d" % i, unlit_y if i % 2 == 0 else unlit_c)
        spawn_sm(cube, (108.3, 100 + i * 1.1, 382.5), (0.05, 0.28, 0.04), None, PREFIX + "CockNeedle_%d" % i, unlit_r)
        spawn_sm(cube, (105, 100 + i * 1.1, 378), (0.35, 1.0, 0.1), None, PREFIX + "CockDash_%d" % i, panel)
    for ix in range(0, 12):
        for iy in range(-18, 19):
            h = 3 + ((ix * 7 + iy) % 9)
            mat = unlit_y if (ix + iy) % 3 == 0 else (unlit_c if (ix + iy) % 3 == 1 else unlit_w)
            spawn_sm(cube, (-1040 + ix * 4.0, iy * 3.5, 300 - 10 + h * 2.0), (1.6, 1.4, h), None, PREFIX + "CityVox_%d_%d" % (ix, iy), mat)
            spawn_sm(cube, (-1036 + ix * 4.0, iy * 3.5, 300 + 2), (0.12, 0.9, 0.4), None, PREFIX + "CityWinB_%d_%d" % (ix, iy), unlit_r if (ix + iy) % 2 == 0 else unlit_y)
    for i in range(30):
        spawn_sm(cube, (-1045, -50 + i * 3.5, 288), (0.4, 2.8, 0.15), None, PREFIX + "CityRoadB_%d" % i, unlit_w)
        spawn_sm(cube, (-1045, -50 + i * 3.5, 288.5), (0.12, 1.1, 0.08), None, PREFIX + "CityLaneB_%d" % i, unlit_y)
    for i, loc in enumerate([(100, 120, 395), (120, 110, 385), (115, 130, 400), (-1030, 10, 320), (-1050, -10, 305), (-1020, 0, 340)]):
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label(PREFIX + "PtKeyCockExtra_%d" % i)
            try:
                pl.set_actor_location(unreal.Vector(*loc), False, True)
            except Exception:
                pass
            try:
                c = pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(280000.0)
                    c.set_editor_property("attenuation_radius", 3500.0)
            except Exception:
                pass
    log("loop36 densify done")
    return stages

def capture(out_dir, stages):
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir("/Game/Skyguard/Capture")
    if unreal.EditorAssetLibrary.does_asset_exist(RT_PATH):
        rt = unreal.EditorAssetLibrary.load_asset(RT_PATH)
    else:
        rt = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "RT_AAA_L36", "/Game/Skyguard/Capture", unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew()
        )
    rt.set_editor_property("size_x", 1920)
    rt.set_editor_property("size_y", 1080)
    try:
        rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA8)
    except Exception:
        pass
    unreal.EditorAssetLibrary.save_loaded_asset(rt)

    # All hero cams use yaw=0 (+X look) so boards at cam+X are guaranteed in frustum
    cams = []
    for name, cam, dist, ny, nz in stages:
        cams.append(("AAA_Cam_L36_%s" % name, cam, (0.0, 0.0, 0.0)))
    # context cams are yaw0 stages only (no rotated orphan cams)
    for name, loc, rot in cams:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)
            try:
                c.set_actor_location(unreal.Vector(float(loc[0]), float(loc[1]), float(loc[2])), False, True)
            except Exception:
                pass

    sca = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0, 0, 400), unreal.Rotator())
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
        fov = 95.0 if any(k in name for k in ["Prop", "Cockpit", "ADS", "YakBeauty", "City", "Combat", "Harbor", "Ocean", "Wide"]) else 70.0
        try:
            comp.set_editor_property("fov_angle", fov)
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
                try:
                    os.remove(out_png)
                except Exception:
                    pass
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
        f.write("Skyguard AAA Loop36 stills\n")
        f.write("time=%s\n" % time.strftime("%Y-%m-%dT%H:%M:%S"))
        f.write("note=host_pillow_selects_best_source; cams yaw0 look +X into HF boards\n")
        for path, size, h, src, name in saved:
            f.write("%s  %d  src=%s cam=%s  %s\n" % (h, size, src, name, path))
        f.write("total=%d\n" % len(saved))
    log("manifest total=%d" % len(saved))
    return saved

def main():
    log("loop36 force-location spawn_sm + cockpit city densify start")
    unreal.EditorLevelLibrary.load_level(MAP_PATH)
    clear_old()
    stages = densify()
    saved = capture(OUT_DIR, stages)
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop36 complete stills=%d" % (len(saved) if saved else 0))
    log("CRITIC: host RGB select+audit required; overall FAIL until blind AAA win")

main()
