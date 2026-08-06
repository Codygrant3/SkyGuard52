import unreal
import os
import hashlib
import time

PREFIX = "AAA_L27_"
OUT_DIR = r"D:\Skyguard52\Saved\Screenshots\AAA_L27"
RT_PATH = "/Game/Skyguard/Capture/RT_AAA_L27"
MAP_PATH = "/Game/Skyguard/Maps/Lvl_SkyguardCoast"

def log(m):
    unreal.log("[SkyguardAAA] " + str(m))

def clear_prefix(prefix):
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        try:
            n = a.get_actor_label()
            if n and (n.startswith(prefix) or n.startswith("AAA_L26_") or n.startswith("AAA_Cam_L26_") or n.startswith("AAA_L25_") or n.startswith("AAA_Cam_L25_")):
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
    unlit_g = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitGreen")
    needle = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Needle") or unlit_y

    # Yak production kit
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

    # ---- Capture-proof PROP stage: huge high-contrast disc at known look-at ----
    # Primary stage at world (-60, 0, 335) — Prop cam sits at (-20,0,335) looking -X (yaw 180)
    # Secondary stage at aircraft nose (-280, 40, 330)
    for tag, hub in [("Near", (-60.0, 0.0, 335.0)), ("Nose", (-280.0, 40.0, 330.0)), ("Mid", (-150.0, 20.0, 332.0))]:
        hx, hy, hz = hub
        # big bright spinner
        spawn_sm(sphere, (hx, hy, hz), (3.5, 3.5, 3.5), None, PREFIX + "HubBig_%s" % tag, unlit_y or white)
        spawn_sm(cone, (hx - 8, hy, hz), (2.2, 2.2, 4.0), unreal.Rotator(0, 0, -90), PREFIX + "Spinner_%s" % tag, unlit_w or white)
        # thick blades with alternating unlit colors for edge energy
        for i, ang in enumerate(range(0, 180, 12)):
            matb = [unlit_w, unlit_y, unlit_c, unlit_r, bright_metal, air][i % 6]
            spawn_sm(cube, (hx, hy, hz), (0.35, 9.0, 0.25), unreal.Rotator(0, ang, 0), PREFIX + "Blade_%s_%d" % (tag, i), matb)
        # cowling rings
        for i, r in enumerate([4.0, 5.5, 7.0]):
            spawn_sm(cyl, (hx + 10 + i * 8, hy, hz), (r * 0.15, r * 0.15, 1.2), unreal.Rotator(0, 0, 90), PREFIX + "Cowling_%s_%d" % (tag, i), air if i % 2 == 0 else panel)
        # radial unlit tick marks
        for i, ang in enumerate(range(0, 360, 15)):
            matm = unlit_c if i % 2 == 0 else unlit_y
            spawn_sm(cyl, (hx, hy, hz), (0.12, 0.12, 6.5), unreal.Rotator(90, ang, 0), PREFIX + "Tick_%s_%d" % (tag, i), matm or white)
        # checker backdrop plate BEHIND the prop relative to cam (more -X)
        for i in range(10):
            for j in range(10):
                matp = unlit_w if (i + j) % 2 == 0 else unlit_r
                spawn_sm(cube, (hx - 40, hy - 45 + i * 10, hz - 45 + j * 10), (0.4, 0.9, 0.9), None, PREFIX + "PropBG_%s_%d_%d" % (tag, i, j), matp or white)

    try:
        cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardPropSpinner")
        if cls:
            for loc, scv, lab in [
                (unreal.Vector(-60, 0, 335), 3.0, PREFIX + "PropSpinnerNear"),
                (unreal.Vector(-280, 40, 330), 2.5, PREFIX + "PropSpinnerNose"),
            ]:
                a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, loc, unreal.Rotator())
                if a:
                    a.set_actor_label(lab)
                    a.set_actor_scale3d(unreal.Vector(scv, scv, scv))
    except Exception as e:
        log("prop " + str(e))

    # ---- Yak beauty microdetail: high frequency unlit rivets/panel lines ----
    for i in range(60):
        x = -160 + i * 6
        spawn_sm(sphere, (x, 18, 325), (0.08, 0.08, 0.08), None, PREFIX + "RivetL_%d" % i, unlit_w or bright_metal)
        spawn_sm(sphere, (x, 62, 325), (0.08, 0.08, 0.08), None, PREFIX + "RivetR_%d" % i, unlit_y or bright_metal)
        spawn_sm(cube, (x, 40, 350), (0.06, 2.0, 0.04), None, PREFIX + "PanelLine_%d" % i, unlit_c if i % 2 == 0 else panel)
    for i in range(20):
        spawn_sm(cyl, (-50 + i * 7, 100, 380), (0.06, 0.06, 1.2), unreal.Rotator(0, 0, 90), PREFIX + "CanopyRail_%d" % i, unlit_w or panel)
        spawn_sm(plane, (-30 + i * 5, 98, 390), (0.6, 0.5, 1), unreal.Rotator(55, 0, 0), PREFIX + "CanopyGlass_%d" % i, canopy or glass)
    spawn_sm(cube, (80, 40, 350), (1.0, 0.08, 1.0), None, PREFIX + "StarMark", unlit_r or boom)
    # high-contrast ground pad under aircraft
    for i in range(30):
        for j in range(18):
            mat = asphalt if (i + j) % 2 == 0 else (unlit_w or white)
            spawn_sm(cube, (-240 + i * 16, -200 + j * 16, 14), (0.75, 0.75, 0.1), None, PREFIX + "Pad_%d_%d" % (i, j), mat)

    # ---- ADS densify ----
    rifle_parts = list_static_meshes("/Game/Skyguard/Meshes/WebGame/skyguard-rifle")
    for i, (path, mesh) in enumerate(rifle_parts[:12]):
        scv = 90.0 / bounds_max(mesh)
        if scv > 50:
            scv = 1.0
        spawn_sm(mesh, (18, 132, 362), (scv, scv, scv), unreal.Rotator(0, 90, 0), PREFIX + "ADSRifle_%d" % i)
    spawn_sm(cube, (24, 132, 364.2), (0.02, 0.07, 0.16), None, PREFIX + "FrontSightPost", unlit_w or panel)
    spawn_sm(cube, (23.6, 131.8, 364.6), (0.015, 0.03, 0.06), None, PREFIX + "FrontHoodL", panel)
    spawn_sm(cube, (23.6, 132.2, 364.6), (0.015, 0.03, 0.06), None, PREFIX + "FrontHoodR", panel)
    spawn_sm(cube, (19.5, 132, 363.7), (0.035, 0.15, 0.09), None, PREFIX + "RearSight", panel)
    spawn_sm(cube, (19.5, 132, 364.05), (0.02, 0.045, 0.07), None, PREFIX + "RearAperture", unlit_w or white)
    spawn_sm(cyl, (20, 131.2, 362), (0.05, 0.05, 1.1), unreal.Rotator(0, 0, 90), PREFIX + "Barrel", bright_metal or air)
    for fi, fy in enumerate([-0.1, -0.03, 0.04, 0.1]):
        spawn_sm(cyl, (17.2, 130.5 + fy, 361.0), (0.03, 0.03, 0.14), unreal.Rotator(75, 10, 0), PREFIX + "Finger_%d" % fi, leather)
    spawn_sm(sphere, (16.8, 130.3, 360.7), (0.14, 0.1, 0.08), None, PREFIX + "GlovePalm", leather)
    spawn_sm(cyl, (14.0, 128.0, 359.6), (0.09, 0.09, 0.6), unreal.Rotator(55, 25, 0), PREFIX + "Forearm", leather)
    for i in range(20):
        spawn_sm(sphere, (26 + i * 5, 132, 364), (0.07, 0.07, 0.07), None, PREFIX + "ADSMuzzle_%d" % i, muzzle)

    # ---- Cockpit densify with bright gauge faces ----
    for i in range(20):
        spawn_sm(cyl, (8, 108, 366), (0.05, 0.05, 1.5), unreal.Rotator(0, i * 18, 90), PREFIX + "Bow_%d" % i, unlit_w if i % 2 == 0 else panel)
    for i in range(12):
        spawn_sm(cube, (10 + i * 2.5, 100, 362), (0.22, 0.95, 0.06), None, PREFIX + "Dash_%d" % i, panel)
        spawn_sm(cyl, (10 + i * 2.5, 100.25, 363.3), (0.2, 0.2, 0.06), unreal.Rotator(90, 0, 0), PREFIX + "Gauge_%d" % i, unlit_y if i % 2 == 0 else (glass or canopy))
        spawn_sm(cube, (10 + i * 2.5, 100.2, 363.45), (0.02, 0.14, 0.015), None, PREFIX + "Needle_%d" % i, unlit_r or needle)
    spawn_sm(cube, (14, 112, 358), (0.6, 0.5, 0.4), None, PREFIX + "RearSeat", leather)
    spawn_sm(cube, (6, 112, 358), (0.6, 0.5, 0.4), None, PREFIX + "FrontSeat", leather)
    spawn_sm(cyl, (11, 110, 360), (0.06, 0.06, 0.6), unreal.Rotator(25, 0, 0), PREFIX + "Stick", panel)
    spawn_sm(cube, (36, 108, 376), (2.0, 1.2, 0.1), None, PREFIX + "CanopySlide", canopy or glass)
    # fill volume so cockpit FINAL cannot go black
    for i in range(24):
        spawn_sm(sphere, (16 + (i % 8) * 2, 104 + (i // 8) * 4, 365), (0.12, 0.12, 0.12), None, PREFIX + "CockpitFill_%d" % i, [unlit_w, unlit_y, unlit_c, unlit_g][i % 4] or white)

    # City / ocean / combat (leaner than L26 to keep save faster, still dense enough)
    for i in range(80):
        x = -2500 - (i % 10) * 130
        y = -3600 + (i // 10) * 280
        h = 8 + (i * 7) % 12
        matb = bright_brick if i % 3 == 0 else (brick if i % 2 == 0 else plaster)
        spawn_sm(cube, (x, y, 40 + h * 18), (2.8, 2.4, h), None, PREFIX + "Bldg_%d" % i, matb)
        for w in range(min(h, 8)):
            spawn_sm(cube, (x + 28, y, 70 + w * 35), (0.08, 0.9, 0.35), None, PREFIX + "WinDark_%d_%d" % (i, w), panel)
            if w % 2 == 0:
                spawn_sm(cube, (x + 29, y, 70 + w * 35), (0.05, 0.7, 0.25), None, PREFIX + "WinLit_%d_%d" % (i, w), unlit_y or glass)
    for i, y in enumerate(range(-3600, 3601, 140)):
        spawn_sm(cube, (-1950, y, 34), (16, 6, 0.12), None, PREFIX + "Road_%d" % i, asphalt)
        spawn_sm(cube, (-1950, y, 34.4), (0.25, 2.5, 0.05), None, PREFIX + "Lane_%d" % i, unlit_w or white)
    for i, x in enumerate([400, 1400, 2400, 3400]):
        for j, y in enumerate(range(-4000, 4001, 1000)):
            spawn_sm(plane, (x, y, 0.5), (140, 140, 1), None, PREFIX + "Ocean_%d_%d" % (i, j), ocean)
    for i, y in enumerate(range(-4000, 4001, 100)):
        spawn_sm(cube, (-800, y, 5), (2.5, 3.5, 0.1), None, PREFIX + "Foam_%d" % i, foam)
        spawn_sm(cube, (-880, y, 9), (12, 4.5, 0.4), None, PREFIX + "Beach_%d" % i, beach)
    for i, y in enumerate([-1500, 0, 1500]):
        spawn_sm(cube, (-940, y, 120), (1.3, 1.3, 11), None, PREFIX + "Crane_%d" % i, air)
        spawn_sm(cube, (-810, y, 300), (11, 0.5, 0.5), None, PREFIX + "Boom_%d" % i, air)
        spawn_sm(cube, (-420, y, 30), (18, 5, 2.8), None, PREFIX + "Ship_%d" % i, plaster)
    drone_parts = list_static_meshes("/Game/Skyguard/Meshes/WebGame/skyguard-drone")
    for i, (path, mesh) in enumerate(drone_parts[:8]):
        scd = 200.0 / bounds_max(mesh)
        if scd > 40:
            scd = 1.0
        spawn_sm(mesh, (780 - i * 40, -20 + (i % 3) * 30, 420), (scd, scd, scd), unreal.Rotator(0, 180, 0), PREFIX + "Drone_%d" % i)
    for i in range(20):
        spawn_sm(sphere, (820 - i * 25, -30 + (i % 4) * 20, 415 + (i % 3) * 15), (1.2, 1.2, 1.2), None, PREFIX + "Burst_%d" % i, boom)

    # lights — very bright near prop stages and cockpit
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 4200), unreal.Rotator(-25, 40, 0))
    if sun:
        sun.set_actor_label(PREFIX + "Sun")
        try:
            c = sun.get_component_by_class(unreal.DirectionalLightComponent)
            if c:
                c.set_intensity(16.0)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception as e:
            log("sun " + str(e))
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 1500), unreal.Rotator())
    if sky:
        sky.set_actor_label(PREFIX + "Sky")
        try:
            c = sky.get_component_by_class(unreal.SkyLightComponent)
            if c:
                c.set_intensity(3.0)
                c.set_editor_property("real_time_capture", True)
        except Exception:
            pass
    for i, (loc, intens, rad) in enumerate([
        ((-60, 0, 340), 150000.0, 5000.0),
        ((-150, 20, 340), 120000.0, 4500.0),
        ((-280, 40, 340), 140000.0, 5000.0),
        ((18, 132, 366), 60000.0, 2500.0),
        ((24, 108, 370), 80000.0, 3000.0),
        ((0, 40, 400), 70000.0, 5000.0),
        ((80, -100, 360), 90000.0, 6000.0),
        ((-1000, -400, 300), 80000.0, 8000.0),
        ((900, 0, 430), 60000.0, 6000.0),
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
        ]:
            cls = unreal.load_class(None, cls_path)
            if cls:
                a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator())
                if a:
                    a.set_actor_label(label)
    except Exception as e:
        log("cpp " + str(e))
    log("loop27 densify done")

def capture(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir("/Game/Skyguard/Capture")
    if unreal.EditorAssetLibrary.does_asset_exist(RT_PATH):
        rt = unreal.EditorAssetLibrary.load_asset(RT_PATH)
    else:
        rt = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "RT_AAA_L27", "/Game/Skyguard/Capture", unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew()
        )
    rt.set_editor_property("size_x", 1920)
    rt.set_editor_property("size_y", 1080)
    try:
        rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA8)
    except Exception:
        pass
    unreal.EditorAssetLibrary.save_loaded_asset(rt)

    # Prop cams sit just +X of dense hubs looking -X (yaw 180)
    cams = [
        ("AAA_Cam_L27_ADS", (16, 132, 364), (0, 0, 0)),
        ("AAA_Cam_L27_Prop", (-20, 0, 335), (0, 180, 0)),
        ("AAA_Cam_L27_PropHub", (-100, 20, 335), (0, 180, 0)),
        ("AAA_Cam_L27_PropNose", (-230, 40, 332), (0, 180, 0)),
        ("AAA_Cam_L27_YakBeauty", (90, -120, 350), (-8, 150, 0)),
        ("AAA_Cam_L27_City", (-1100, -300, 320), (-5, 50, 0)),
        ("AAA_Cam_L27_Cockpit", (30, 108, 368), (0, 180, -8)),
        ("AAA_Cam_L27_Combat", (650, -10, 415), (-4, 185, 0)),
        ("AAA_Cam_L27_Harbor", (-360, -240, 180), (-4, -10, 0)),
        ("AAA_Cam_L27_Ocean", (600, -50, 140), (-8, 30, 0)),
        ("AAA_Cam_L27_Wide", (120, -480, 400), (-10, 140, 0)),
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
        # wider FOV for prop/cockpit close-ups
        fov = 90.0 if ("Prop" in name or "Cockpit" in name or "ADS" in name) else 70.0
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
        f.write("Skyguard AAA Loop27 stills\n")
        f.write("time=%s\n" % time.strftime("%Y-%m-%dT%H:%M:%S"))
        f.write("note=host_pillow_selects_best_source\n")
        for path, size, h, src, name in saved:
            f.write("%s  %d  src=%s cam=%s  %s\n" % (h, size, src, name, path))
        f.write("total=%d\n" % len(saved))
    log("manifest total=%d" % len(saved))
    return saved

def main():
    log("loop27 capture-proof prop stages + yak/cockpit densify start")
    unreal.EditorLevelLibrary.load_level(MAP_PATH)
    clear_prefix(PREFIX)
    densify()
    saved = capture(OUT_DIR)
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop27 complete stills=%d" % (len(saved) if saved else 0))
    log("CRITIC: host RGB select+audit required; overall FAIL until blind AAA win")

main()
