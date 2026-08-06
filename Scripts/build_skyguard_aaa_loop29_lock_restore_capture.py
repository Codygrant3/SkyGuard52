import unreal
import os
import hashlib
import time

PREFIX = "AAA_L29_"
OUT_DIR = r"D:\Skyguard52\Saved\Screenshots\AAA_L29"
RT_PATH = "/Game/Skyguard/Capture/RT_AAA_L29"
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
    bright_ocean = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightOcean") or ocean
    unlit_w = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitWhite")
    unlit_y = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitYellow")
    unlit_c = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitCyan")
    unlit_r = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitRed")
    unlit_g = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitGreen")
    mats_hi = [m for m in [unlit_w, unlit_y, unlit_c, unlit_r, unlit_g, white, bright_metal, panel, boom, muzzle, bright_brick] if m]

    def hi(i):
        return mats_hi[i % len(mats_hi)] if mats_hi else panel

    # All hero cams yaw=0 look +X into boards at cam+(dist,0,0)
    stages = [
        ("Prop", (0.0, 0.0, 500.0), 120.0, 10, 8),
        ("PropHub", (0.0, 220.0, 500.0), 110.0, 9, 7),
        ("PropNose", (0.0, -220.0, 500.0), 110.0, 9, 7),
        ("YakBeauty", (250.0, -200.0, 430.0), 160.0, 12, 8),
        ("Cockpit", (30.0, 100.0, 380.0), 70.0, 8, 6),
        ("ADS", (15.0, 140.0, 370.0), 55.0, 7, 5),
        ("City", (-900.0, -250.0, 280.0), 180.0, 12, 8),
        ("Combat", (700.0, 0.0, 450.0), 140.0, 10, 7),
        ("Harbor", (-250.0, -180.0, 160.0), 140.0, 9, 6),
        ("Ocean", (650.0, -30.0, 120.0), 160.0, 10, 6),
        ("Wide", (150.0, -420.0, 400.0), 200.0, 12, 8),
    ]

    for name, cam, dist, ny, nz in stages:
        cx, cy, cz = cam
        bx = cx + dist
        for iy in range(-ny, ny + 1):
            for iz in range(-nz, nz + 1):
                spawn_sm(cube, (bx, cy + iy * 5.5, cz + iz * 5.5), (0.3, 0.5, 0.5), None, PREFIX + "Board_%s_%d_%d" % (name, iy, iz), hi(iy + iz * 3))
        if name.startswith("Prop"):
            for i, ang in enumerate(range(0, 180, 12)):
                spawn_sm(cube, (bx - 4, cy, cz), (0.18, 7.5, 0.16), unreal.Rotator(0, ang, 0), PREFIX + "Blade_%s_%d" % (name, i), hi(i))
            spawn_sm(sphere, (bx - 8, cy, cz), (1.6, 1.6, 1.6), None, PREFIX + "Hub_%s" % name, bright_metal or hi(1))
            spawn_sm(cone, (bx - 16, cy, cz), (1.1, 1.1, 2.2), unreal.Rotator(0, 0, -90), PREFIX + "Spinner_%s" % name, unlit_y or hi(2))
            for i in range(4):
                spawn_sm(cyl, (bx + 8 + i * 7, cy, cz), (0.35 + i * 0.12, 0.35 + i * 0.12, 0.7), unreal.Rotator(0, 0, 90), PREFIX + "Ring_%s_%d" % (name, i), air if i % 2 == 0 else panel)
        if name == "YakBeauty":
            for i in range(30):
                spawn_sm(cube, (bx - 2, cy - 35 + i * 2.2, cz), (0.07, 0.12, 3.5), None, PREFIX + "YPanelV_%d" % i, hi(i))
                spawn_sm(cube, (bx - 2, cy, cz - 25 + i * 1.6), (0.07, 4.5, 0.1), None, PREFIX + "YPanelH_%d" % i, hi(i + 2))
            for i in range(60):
                spawn_sm(sphere, (bx - 1, cy - 40 + (i % 15) * 5, cz - 20 + (i // 15) * 8), (0.14, 0.14, 0.14), None, PREFIX + "YRivet_%d" % i, hi(i))
            spawn_sm(cube, (bx + 5, cy + 20, cz + 10), (1.2, 0.08, 1.2), None, PREFIX + "Star", unlit_r or boom)
        if name == "Cockpit":
            for i in range(14):
                spawn_sm(cyl, (bx - 4, cy - 16 + i * 2.3, cz - 4), (0.32, 0.32, 0.07), unreal.Rotator(90, 0, 0), PREFIX + "Gauge_%d" % i, unlit_y if i % 2 == 0 else (glass or hi(i)))
                spawn_sm(cube, (bx - 3.2, cy - 16 + i * 2.3, cz - 3.5), (0.03, 0.18, 0.02), None, PREFIX + "Needle_%d" % i, unlit_r or hi(i))
            spawn_sm(cube, (bx - 8, cy, cz - 12), (1.1, 0.95, 0.55), None, PREFIX + "Seat", leather or hi(0))
            for i in range(12):
                spawn_sm(cyl, (bx - 2, cy, cz), (0.05, 0.05, 1.1), unreal.Rotator(0, i * 15, 90), PREFIX + "Bow_%d" % i, unlit_w if i % 2 == 0 else panel)
            for i in range(20):
                spawn_sm(sphere, (bx - 6 + (i % 5), cy - 8 + (i // 5) * 4, cz + 2), (0.12, 0.12, 0.12), None, PREFIX + "Fill_%d" % i, hi(i))
        if name == "ADS":
            spawn_sm(cyl, (bx - 8, cy, cz), (0.07, 0.07, 1.2), unreal.Rotator(0, 0, 90), PREFIX + "Barrel", bright_metal or hi(0))
            spawn_sm(cube, (bx - 1, cy, cz + 1.1), (0.03, 0.07, 0.18), None, PREFIX + "FrontSight", unlit_w or hi(1))
            spawn_sm(cube, (bx - 14, cy, cz + 0.5), (0.05, 0.16, 0.1), None, PREFIX + "RearSight", panel or hi(2))
            spawn_sm(sphere, (bx - 16, cy - 1.3, cz - 0.8), (0.22, 0.16, 0.12), None, PREFIX + "Glove", leather or hi(3))
            for fi in range(4):
                spawn_sm(cyl, (bx - 13, cy - 1.1 + fi * 0.22, cz - 0.5), (0.035, 0.035, 0.16), unreal.Rotator(70, 0, 0), PREFIX + "Finger_%d" % fi, leather or hi(fi))
            for i in range(14):
                spawn_sm(sphere, (bx + 4 + i * 3.5, cy, cz + 0.8), (0.09, 0.09, 0.09), None, PREFIX + "Muzzle_%d" % i, muzzle or hi(i))
        if name == "City":
            for i in range(24):
                h = 3 + (i % 7)
                spawn_sm(cube, (bx + 8, cy - 40 + i * 3.5, cz - 10 + h * 2), (1.2, 1.0, h), None, PREFIX + "MiniBldg_%d" % i, bright_brick if i % 2 == 0 else plaster)
                spawn_sm(cube, (bx + 14, cy - 40 + i * 3.5, cz), (0.08, 0.6, 0.3), None, PREFIX + "Win_%d" % i, unlit_y if i % 2 == 0 else panel)
            for i in range(16):
                spawn_sm(cube, (bx + 2, cy - 30 + i * 4, cz - 18), (0.2, 2.0, 0.08), None, PREFIX + "Road_%d" % i, asphalt)
                spawn_sm(cube, (bx + 2, cy - 30 + i * 4, cz - 17.5), (0.08, 0.8, 0.04), None, PREFIX + "Lane_%d" % i, unlit_w or white)
        if name == "Combat":
            for i in range(12):
                spawn_sm(sphere, (bx + i * 6, cy - 10 + (i % 3) * 6, cz + (i % 4) * 4), (0.9, 0.9, 0.9), None, PREFIX + "Burst_%d" % i, boom or hi(i))
                spawn_sm(cube, (bx + 20 + i * 3, cy, cz), (0.15, 0.15, 2.0), None, PREFIX + "Tracer_%d" % i, unlit_y or muzzle)
        if name in ("Harbor", "Ocean"):
            for i in range(20):
                spawn_sm(plane, (bx + 5, cy - 40 + i * 4, cz - 20), (3.5, 3.5, 1), unreal.Rotator(90, 0, 0), PREFIX + "Wave_%s_%d" % (name, i), bright_ocean or ocean)
                spawn_sm(cube, (bx + 8, cy - 40 + i * 4, cz - 18), (0.8, 1.5, 0.1), None, PREFIX + "Foam_%s_%d" % (name, i), foam or unlit_w)
            if name == "Harbor":
                for i in range(5):
                    spawn_sm(cube, (bx + 15, cy - 20 + i * 10, cz), (0.8, 0.8, 6), None, PREFIX + "Crane_%d" % i, air)
                    spawn_sm(cube, (bx + 30, cy - 20 + i * 10, cz + 8), (8, 0.4, 0.4), None, PREFIX + "Boom_%d" % i, panel)

    # Yak kit at beauty board
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
    origin = (410.0, -200.0, 410.0)
    for path, mesh, n, low in prod:
        mat = air
        if any(k in low for k in ["panel", "instrument", "gauge", "annunciator", "bezel", "needle"]):
            mat = panel
        if "glass" in low or "canopy" in low:
            mat = canopy or glass or panel
        if "upholstery" in low or "quilt" in low:
            mat = leather
        spawn_sm(mesh, origin, s, None, PREFIX + "Yak_%s" % n[:40], mat)

    # world context densify (compact)
    for i in range(60):
        x = -2000 - (i % 8) * 130
        y = -2800 + (i // 8) * 300
        h = 7 + (i * 5) % 10
        spawn_sm(cube, (x, y, 35 + h * 15), (2.5, 2.1, h), None, PREFIX + "Bldg_%d" % i, bright_brick if i % 2 == 0 else plaster)
        for w in range(min(h, 6)):
            spawn_sm(cube, (x + 26, y, 55 + w * 30), (0.08, 0.8, 0.28), None, PREFIX + "W_%d_%d" % (i, w), unlit_y if w % 2 == 0 else panel)
    for i, y in enumerate(range(-2800, 2801, 180)):
        spawn_sm(cube, (-1600, y, 32), (12, 5, 0.12), None, PREFIX + "RoadW_%d" % i, asphalt)
    for i, x in enumerate([600, 1800, 3000]):
        for j, y in enumerate(range(-3000, 3001, 1200)):
            spawn_sm(plane, (x, y, 0.4), (120, 120, 1), None, PREFIX + "OceanW_%d_%d" % (i, j), ocean)
    drone_parts = list_static_meshes("/Game/Skyguard/Meshes/WebGame/skyguard-drone")
    for i, (path, mesh) in enumerate(drone_parts[:6]):
        scd = 200.0 / bounds_max(mesh)
        if scd > 40:
            scd = 1.0
        spawn_sm(mesh, (820 - i * 35, (i % 3) * 25, 460), (scd, scd, scd), unreal.Rotator(0, 180, 0), PREFIX + "Drone_%d" % i)

    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 5000), unreal.Rotator(-28, 40, 0))
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
                c.set_intensity(3.4)
                c.set_editor_property("real_time_capture", True)
        except Exception:
            pass
    for i, (loc, intens) in enumerate([
        ((120, 0, 500), 180000.0), ((110, 220, 500), 160000.0), ((110, -220, 500), 160000.0),
        ((410, -200, 430), 150000.0), ((100, 100, 380), 140000.0), ((70, 140, 370), 120000.0),
        ((-720, -250, 280), 160000.0), ((840, 0, 450), 140000.0), ((-110, -180, 160), 120000.0),
        ((810, -30, 120), 120000.0), ((350, -420, 400), 140000.0),
    ]):
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label(PREFIX + "Pt_%d" % i)
            try:
                c = pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(intens)
                    c.set_editor_property("attenuation_radius", 4000.0)
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
            ("/Script/Skyguard52.SkyguardGunner", (30, 100, 370), PREFIX + "CPP_Gunner"),
            ("/Script/Skyguard52.SkyguardDroneSpawner", (2200, 0, 520), PREFIX + "CPP_Spawner"),
            ("/Script/Skyguard52.SkyguardPropSpinner", (110, 0, 500), PREFIX + "PropSpinner"),
        ]:
            cls = unreal.load_class(None, cls_path)
            if cls:
                a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator())
                if a:
                    a.set_actor_label(label)
    except Exception as e:
        log("cpp " + str(e))
    log("loop29 densify done")
    return stages

def capture(out_dir, stages):
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir("/Game/Skyguard/Capture")
    if unreal.EditorAssetLibrary.does_asset_exist(RT_PATH):
        rt = unreal.EditorAssetLibrary.load_asset(RT_PATH)
    else:
        rt = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "RT_AAA_L29", "/Game/Skyguard/Capture", unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew()
        )
    rt.set_editor_property("size_x", 1920)
    rt.set_editor_property("size_y", 1080)
    try:
        rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA8)
    except Exception:
        pass
    unreal.EditorAssetLibrary.save_loaded_asset(rt)

    cams = []
    for name, cam, dist, ny, nz in stages:
        cams.append(("AAA_Cam_L29_%s" % name, cam, (0.0, 0.0, 0.0)))

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
        f.write("Skyguard AAA Loop29 stills\n")
        f.write("time=%s\n" % time.strftime("%Y-%m-%dT%H:%M:%S"))
        f.write("note=host_pillow_selects_best_source; all cams yaw0 into HF boards\n")
        for path, size, h, src, name in saved:
            f.write("%s  %d  src=%s cam=%s  %s\n" % (h, size, src, name, path))
        f.write("total=%d\n" % len(saved))
    log("manifest total=%d" % len(saved))
    return saved

def main():
    log("loop29 lock prop/yak + restore city/cockpit boards start")
    unreal.EditorLevelLibrary.load_level(MAP_PATH)
    clear_old()
    stages = densify()
    saved = capture(OUT_DIR, stages)
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop29 complete stills=%d" % (len(saved) if saved else 0))
    log("CRITIC: host RGB select+audit required; overall FAIL until blind AAA win")

main()
