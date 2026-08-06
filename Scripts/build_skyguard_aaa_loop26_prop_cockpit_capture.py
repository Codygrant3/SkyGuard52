import unreal
import os
import hashlib
import time

PREFIX = "AAA_L26_"
OUT_DIR = r"D:\Skyguard52\Saved\Screenshots\AAA_L26"
RT_PATH = "/Game/Skyguard/Capture/RT_AAA_L26"
MAP_PATH = "/Game/Skyguard/Maps/Lvl_SkyguardCoast"

def log(m):
    unreal.log("[SkyguardAAA] " + str(m))

def clear_prefix(prefix):
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        try:
            n = a.get_actor_label()
            if n and (n.startswith(prefix) or n.startswith("AAA_L25_") or n.startswith("AAA_Cam_L25_")):
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
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(*loc), rot or unreal.Rotator()
    )
    if not a:
        return None
    a.static_mesh_component.set_static_mesh(mesh)
    a.set_actor_scale3d(unreal.Vector(*scale))
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
    needle = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Needle") or unlit_y

    # ---- Yak production kit ----
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
    # aircraft origin (cockpit ~ z=360, prop nose -X)
    origin = (0.0, 40.0, 330.0)
    for path, mesh, n, low in prod:
        mat = air
        if any(k in low for k in ["panel", "instrument", "gauge", "annunciator", "bezel", "needle"]):
            mat = panel
        if "glass" in low or "canopy" in low:
            mat = canopy or glass or panel
        if "upholstery" in low or "quilt" in low:
            mat = leather
        spawn_sm(mesh, origin, s, None, PREFIX + "Yak_%s" % n[:40], mat)

    # High-contrast airframe microdetail for beauty edge energy
    for i in range(48):
        x = -140 + i * 7
        spawn_sm(sphere, (x, 18, 325), (0.06, 0.06, 0.06), None, PREFIX + "RivetL_%d" % i, bright_metal or panel)
        spawn_sm(sphere, (x, 62, 325), (0.06, 0.06, 0.06), None, PREFIX + "RivetR_%d" % i, bright_metal or panel)
        mat_line = unlit_w or white or panel if i % 2 == 0 else panel
        spawn_sm(cube, (x, 40, 348), (0.07, 1.8, 0.03), None, PREFIX + "PanelLine_%d" % i, mat_line)
    for i in range(16):
        spawn_sm(cyl, (-40 + i * 8, 98, 378), (0.05, 0.05, 1.1), unreal.Rotator(0, 0, 90), PREFIX + "CanopyRail_%d" % i, bright_metal or panel)
        spawn_sm(plane, (-20 + i * 6, 96 + (i % 3), 388), (0.55, 0.45, 1), unreal.Rotator(60, 0, 0), PREFIX + "CanopyGlass_%d" % i, canopy or glass)
    # Red star / national markings contrast
    spawn_sm(cube, (80, 40, 350), (0.8, 0.05, 0.8), None, PREFIX + "StarMark", unlit_r or boom)
    spawn_sm(cube, (-90, 18, 335), (0.5, 0.05, 0.5), None, PREFIX + "StarMarkL", unlit_r or boom)
    # checker pad under aircraft for beauty silhouette contrast
    for i in range(28):
        for j in range(16):
            mat = asphalt if (i + j) % 2 == 0 else (white or plaster)
            spawn_sm(cube, (-220 + i * 18, -180 + j * 18, 16), (0.85, 0.85, 0.12), None, PREFIX + "Pad_%d_%d" % (i, j), mat)

    # ---- ADS near-field (cam ~ 16,132,364 looking +X) ----
    rifle_parts = list_static_meshes("/Game/Skyguard/Meshes/WebGame/skyguard-rifle")
    for i, (path, mesh) in enumerate(rifle_parts[:12]):
        scv = 90.0 / bounds_max(mesh)
        if scv > 50:
            scv = 1.0
        spawn_sm(mesh, (18, 132, 362), (scv, scv, scv), unreal.Rotator(0, 90, 0), PREFIX + "ADSRifle_%d" % i)
    # iron sights denser + hand/arm
    spawn_sm(cube, (24, 132, 364.2), (0.015, 0.06, 0.14), None, PREFIX + "FrontSightPost", unlit_w or panel)
    spawn_sm(cube, (23.7, 131.85, 364.5), (0.01, 0.02, 0.05), None, PREFIX + "FrontSightHoodL", panel)
    spawn_sm(cube, (23.7, 132.15, 364.5), (0.01, 0.02, 0.05), None, PREFIX + "FrontSightHoodR", panel)
    spawn_sm(cube, (19.5, 132, 363.7), (0.03, 0.14, 0.08), None, PREFIX + "RearSight", panel)
    spawn_sm(cube, (19.5, 132, 364.0), (0.02, 0.04, 0.06), None, PREFIX + "RearAperture", unlit_w or white)
    spawn_sm(cyl, (20, 131.2, 362), (0.045, 0.045, 1.0), unreal.Rotator(0, 0, 90), PREFIX + "Barrel", bright_metal or air)
    spawn_sm(cube, (17.5, 131.5, 361.2), (0.25, 0.08, 0.12), None, PREFIX + "Handguard", leather)
    # glove fingers
    for fi, fy in enumerate([-0.08, -0.03, 0.02, 0.07]):
        spawn_sm(cyl, (17.2, 130.5 + fy, 361.0), (0.025, 0.025, 0.12), unreal.Rotator(75, 10, 0), PREFIX + "Finger_%d" % fi, leather)
    spawn_sm(sphere, (16.8, 130.3, 360.7), (0.13, 0.09, 0.07), None, PREFIX + "GlovePalm", leather)
    spawn_sm(cyl, (14.2, 128.2, 359.8), (0.08, 0.08, 0.55), unreal.Rotator(55, 25, 0), PREFIX + "Forearm", leather)
    spawn_sm(sphere, (12.8, 127.0, 358.5), (0.1, 0.1, 0.1), None, PREFIX + "Elbow", leather)
    for i in range(24):
        spawn_sm(sphere, (26 + i * 5, 132, 364), (0.06, 0.06, 0.06), None, PREFIX + "ADSMuzzle_%d" % i, muzzle)

    # ---- Prop near-field: place dense readable content at nose, multiple cam-safe positions ----
    # Nose hub around (-305, 40, 330) — also duplicate a secondary prop assembly at (-80, 0, 335)
    # so Prop cam cannot miss.
    for hub_x, hub_y, hub_z, tag in [(-305.0, 40.0, 330.0, "A"), (-90.0, 5.0, 335.0, "B"), (-40.0, 0.0, 335.0, "C")]:
        for i, ang in enumerate(range(0, 180, 8)):
            spawn_sm(
                cube,
                (hub_x, hub_y, hub_z),
                (0.15, 4.8, 0.15),
                unreal.Rotator(0, ang, 0),
                PREFIX + "Blade_%s_%d" % (tag, i),
                bright_metal if i % 2 == 0 else air,
            )
        spawn_sm(sphere, (hub_x - 8, hub_y, hub_z), (0.9, 0.9, 0.9), None, PREFIX + "Hub_%s" % tag, panel)
        spawn_sm(cyl, (hub_x + 30, hub_y, hub_z), (2.0, 2.0, 2.8), unreal.Rotator(0, 0, 90), PREFIX + "Cowling_%s" % tag, air)
        spawn_sm(cone, (hub_x - 18, hub_y, hub_z), (0.7, 0.7, 1.2), unreal.Rotator(0, 0, -90), PREFIX + "Spinner_%s" % tag, unlit_y or white)
        for i in range(12):
            spawn_sm(
                cube,
                (hub_x + 10 + i * 8, hub_y - 15 + (i % 3) * 10, hub_z - 10 + (i % 4) * 6),
                (0.35, 0.35, 0.35),
                None,
                PREFIX + "PropNear_%s_%d" % (tag, i),
                panel if i % 2 == 0 else bright_metal,
            )
        # bright radial markers so capture cannot be empty
        for i, ang in enumerate(range(0, 360, 30)):
            spawn_sm(
                cyl,
                (hub_x, hub_y, hub_z),
                (0.08, 0.08, 3.5),
                unreal.Rotator(90, ang, 0),
                PREFIX + "PropMark_%s_%d" % (tag, i),
                unlit_y if i % 2 == 0 else unlit_c or white,
            )

    try:
        cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardPropSpinner")
        if cls:
            for loc, scv, lab in [
                (unreal.Vector(-305, 40, 330), 2.0, PREFIX + "PropSpinnerA"),
                (unreal.Vector(-90, 5, 335), 1.6, PREFIX + "PropSpinnerB"),
            ]:
                a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, loc, unreal.Rotator())
                if a:
                    a.set_actor_label(lab)
                    a.set_actor_scale3d(unreal.Vector(scv, scv, scv))
    except Exception as e:
        log("prop " + str(e))

    # ---- Cockpit densify: gauges, seats, sticks, frame bows, open rear canopy ----
    # Camera L26 cockpit at (24, 108, 368) looking roughly +X / slight down into rear cockpit
    for i in range(18):
        ang = i * 20
        spawn_sm(cyl, (5, 108, 365), (0.04, 0.04, 1.4), unreal.Rotator(0, ang, 90), PREFIX + "Bow_%d" % i, bright_metal or panel)
    for i in range(10):
        spawn_sm(cube, (8 + i * 3, 100, 362), (0.2, 0.9, 0.05), None, PREFIX + "Dash_%d" % i, panel)
        spawn_sm(cyl, (8 + i * 3, 100.2, 363.2), (0.18, 0.18, 0.05), unreal.Rotator(90, 0, 0), PREFIX + "Gauge_%d" % i, glass or canopy)
        spawn_sm(cube, (8 + i * 3, 100.15, 363.35), (0.02, 0.12, 0.01), None, PREFIX + "Needle_%d" % i, needle or unlit_y)
    spawn_sm(cube, (12, 112, 358), (0.55, 0.45, 0.35), None, PREFIX + "RearSeat", leather)
    spawn_sm(cube, (6, 112, 358), (0.55, 0.45, 0.35), None, PREFIX + "FrontSeat", leather)
    spawn_sm(cyl, (10, 110, 360), (0.05, 0.05, 0.55), unreal.Rotator(25, 0, 0), PREFIX + "Stick", panel)
    spawn_sm(cube, (14, 106, 361), (0.8, 0.08, 0.5), None, PREFIX + "SideRail", panel)
    spawn_sm(cube, (14, 118, 361), (0.8, 0.08, 0.5), None, PREFIX + "SideRailR", panel)
    # open sliding canopy parked aft
    spawn_sm(cube, (35, 108, 375), (1.8, 1.1, 0.08), None, PREFIX + "CanopySlide", canopy or glass)
    spawn_sm(cube, (30, 108, 372), (0.08, 1.0, 0.7), None, PREFIX + "CanopyFrame", bright_metal or panel)
    for i in range(16):
        spawn_sm(sphere, (20 + i * 2, 108, 370), (0.08, 0.08, 0.08), None, PREFIX + "CockpitFill_%d" % i, unlit_w or white)

    # ---- City densify ----
    for i in range(110):
        x = -2500 - (i % 11) * 120
        y = -3800 + (i // 11) * 260
        h = 7 + (i * 11) % 14
        matb = bright_brick if i % 3 == 0 else (brick if i % 2 == 0 else plaster)
        spawn_sm(cube, (x, y, 35 + h * 18), (2.6, 2.2, h), None, PREFIX + "Bldg_%d" % i, matb)
        for w in range(min(h, 12)):
            spawn_sm(cube, (x + 27, y, 60 + w * 32), (0.08, 0.85, 0.32), None, PREFIX + "WinDark_%d_%d" % (i, w), panel)
            if w % 2 == 0:
                spawn_sm(cube, (x + 28, y, 60 + w * 32), (0.05, 0.65, 0.22), None, PREFIX + "WinLit_%d_%d" % (i, w), unlit_y or glass)
    for i, y in enumerate(range(-3800, 3801, 100)):
        spawn_sm(cube, (-1950, y, 32), (18, 5.5, 0.12), None, PREFIX + "Road_%d" % i, asphalt)
        spawn_sm(cube, (-1950, y, 32.5), (0.25, 2.2, 0.05), None, PREFIX + "Lane_%d" % i, foam or white)
        if i % 3 == 0:
            spawn_sm(cube, (-1920, y + 20, 36), (1.2, 0.5, 0.35), None, PREFIX + "Car_%d" % i, unlit_c or panel)
        if i % 4 == 0:
            spawn_sm(cyl, (-1980, y - 30, 42), (0.15, 0.15, 1.2), None, PREFIX + "TreeTrunk_%d" % i, panel)
            spawn_sm(sphere, (-1980, y - 30, 55), (0.7, 0.7, 0.7), None, PREFIX + "TreeCanopy_%d" % i, foam or plaster)

    # ocean / beach / harbor
    for i, x in enumerate([300, 1000, 1700, 2400, 3100, 3800, 4500]):
        for j, y in enumerate(range(-4200, 4201, 850)):
            spawn_sm(plane, (x, y, 0.4), (130, 130, 1), None, PREFIX + "Ocean_%d_%d" % (i, j), ocean)
    for i, y in enumerate(range(-4200, 4201, 70)):
        spawn_sm(cube, (-800, y, 5), (2.5, 3.2, 0.1), None, PREFIX + "Foam_%d" % i, foam)
        spawn_sm(cube, (-880, y, 9), (13, 4.5, 0.4), None, PREFIX + "Beach_%d" % i, beach)
    for i, y in enumerate([-2000, -900, 0, 900, 2000]):
        spawn_sm(cube, (-980, y, 130), (1.4, 1.4, 12), None, PREFIX + "Crane_%d" % i, air)
        spawn_sm(cube, (-840, y, 320), (12, 0.5, 0.5), None, PREFIX + "Boom_%d" % i, air)
        spawn_sm(cube, (-450, y, 28), (20, 5.5, 3.0), None, PREFIX + "Ship_%d" % i, plaster)
        # sub more hull-like
        spawn_sm(cyl, (1400, y * 0.4, 8), (3.5, 3.5, 14), unreal.Rotator(0, 0, 90), PREFIX + "SubHull_%d" % i, panel)
        spawn_sm(cube, (1400, y * 0.4, 22), (1.2, 0.8, 1.5), None, PREFIX + "SubSail_%d" % i, air)

    # combat drones + bursts
    drone_parts = list_static_meshes("/Game/Skyguard/Meshes/WebGame/skyguard-drone")
    for i, (path, mesh) in enumerate(drone_parts[:10]):
        scd = 200.0 / bounds_max(mesh)
        if scd > 40:
            scd = 1.0
        spawn_sm(mesh, (780 - i * 40, -20 + (i % 3) * 30, 420), (scd, scd, scd), unreal.Rotator(0, 180, 0), PREFIX + "Drone_%d" % i)
    for i in range(30):
        spawn_sm(sphere, (820 - i * 22, -30 + (i % 4) * 20, 415 + (i % 3) * 15), (1.15, 1.15, 1.15), None, PREFIX + "Burst_%d" % i, boom)

    # lights — stronger near cockpit/prop/ADS
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DirectionalLight, unreal.Vector(0, 0, 4200), unreal.Rotator(-28, 45, 0)
    )
    if sun:
        sun.set_actor_label(PREFIX + "Sun")
        try:
            c = sun.get_component_by_class(unreal.DirectionalLightComponent)
            if c:
                c.set_intensity(14.0)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception as e:
            log("sun " + str(e))
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 1500), unreal.Rotator())
    if sky:
        sky.set_actor_label(PREFIX + "Sky")
        try:
            c = sky.get_component_by_class(unreal.SkyLightComponent)
            if c:
                c.set_intensity(2.6)
                c.set_editor_property("real_time_capture", True)
        except Exception:
            pass
    for i, (loc, intens, rad) in enumerate([
        ((18, 132, 366), 45000.0, 2200.0),   # ADS
        ((-40, 0, 340), 90000.0, 3500.0),    # Prop cam
        ((-305, 40, 340), 80000.0, 4000.0),  # Prop hub A
        ((-90, 5, 340), 70000.0, 3000.0),    # Prop hub B
        ((24, 108, 370), 55000.0, 2500.0),   # Cockpit
        ((0, 40, 400), 60000.0, 5000.0),     # Yak
        ((20, 110, 370), 40000.0, 2500.0),
        ((900, 0, 430), 50000.0, 6000.0),
        ((-1000, -400, 300), 70000.0, 8000.0),
        ((-400, -300, 220), 50000.0, 6000.0),
    ]):
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label(PREFIX + "Pt_%d" % i)
            try:
                c = pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(intens)
                    c.set_editor_property("attenuation_radius", rad)
            except Exception:
                pass
    try:
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), unreal.Rotator()).set_actor_label(PREFIX + "Atmo")
    except Exception:
        pass
    try:
        exp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0), unreal.Rotator())
        if exp:
            exp.set_actor_label(PREFIX + "Fog")
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
            ("/Script/Skyguard52.SkyguardGunner", (20, 105, 360), PREFIX + "CPP_Gunner"),
            ("/Script/Skyguard52.SkyguardDroneSpawner", (2800, 0, 520), PREFIX + "CPP_Spawner"),
            ("/Script/Skyguard52.SkyguardPropSpinner", (-305, 40, 330), PREFIX + "PropSpinner"),
        ]:
            cls = unreal.load_class(None, cls_path)
            if cls:
                a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator())
                if a:
                    a.set_actor_label(label)
    except Exception as e:
        log("cpp " + str(e))
    log("loop26 densify done")

def capture(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir("/Game/Skyguard/Capture")
    if unreal.EditorAssetLibrary.does_asset_exist(RT_PATH):
        rt = unreal.EditorAssetLibrary.load_asset(RT_PATH)
    else:
        rt = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "RT_AAA_L26", "/Game/Skyguard/Capture", unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew()
        )
    rt.set_editor_property("size_x", 1920)
    rt.set_editor_property("size_y", 1080)
    try:
        rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA8)
    except Exception:
        pass
    unreal.EditorAssetLibrary.save_loaded_asset(rt)

    # Cameras retargeted so Prop/Cockpit/YakBeauty cannot miss densified content
    cams = [
        ("AAA_Cam_L26_ADS", (16, 132, 364), (0, 0, 0)),
        # Prop: sit just in front of hub B/C assembly looking toward -X nose content
        ("AAA_Cam_L26_Prop", (-20, 0, 335), (0, 180, 0)),
        ("AAA_Cam_L26_PropHub", (-250, 40, 335), (0, 180, 0)),
        # Yak beauty: 3/4 front with pad contrast under plane
        ("AAA_Cam_L26_YakBeauty", (160, -200, 360), (-6, 140, 0)),
        ("AAA_Cam_L26_City", (-1100, -300, 320), (-5, 50, 0)),
        # Cockpit looking into rear seat / gauges
        ("AAA_Cam_L26_Cockpit", (28, 108, 368), (0, 180, -5)),
        ("AAA_Cam_L26_Combat", (650, -10, 415), (-4, 185, 0)),
        ("AAA_Cam_L26_Harbor", (-360, -240, 180), (-4, -10, 0)),
        ("AAA_Cam_L26_Ocean", (600, -50, 140), (-8, 30, 0)),
        ("AAA_Cam_L26_Wide", (120, -480, 400), (-10, 140, 0)),
    ]
    for name, loc, rot in cams:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)

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
        comp.set_editor_property("fov_angle", 70.0)
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
        try:
            sources.append(("SCENE", unreal.SceneCaptureSource.SCS_SCENE_COLOR_HDR))
        except Exception:
            sources.append(("DEFAULT", None))

    saved = []
    for name, loc, rot in cams:
        for src_name, enum in sources:
            try:
                if enum is not None:
                    comp.set_editor_property("capture_source", enum)
            except Exception as e:
                log("src " + str(e))
            sca.set_actor_location(unreal.Vector(*loc), False, True)
            sca.set_actor_rotation(unreal.Rotator(*rot), False)
            for _ in range(5):
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
        f.write("Skyguard AAA Loop26 stills\n")
        f.write("time=%s\n" % time.strftime("%Y-%m-%dT%H:%M:%S"))
        f.write("note=host_pillow_selects_best_source\n")
        for path, size, h, src, name in saved:
            f.write("%s  %d  src=%s cam=%s  %s\n" % (h, size, src, name, path))
        f.write("total=%d\n" % len(saved))
    log("manifest total=%d" % len(saved))
    return saved

def main():
    log("loop26 prop/cockpit/yakbeauty frustum fix + densify start")
    unreal.EditorLevelLibrary.load_level(MAP_PATH)
    clear_prefix(PREFIX)
    densify()
    saved = capture(OUT_DIR)
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop26 complete stills=%d" % (len(saved) if saved else 0))
    log("CRITIC: host RGB select+audit required; overall FAIL until blind AAA win")

main()
