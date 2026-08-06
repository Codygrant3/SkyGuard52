import unreal
import os
import hashlib
import time
import math

PREFIX = "AAA_L37_"
OUT_DIR = r"D:\Skyguard52\Saved\Screenshots\AAA_L37"
RT_PATH = "/Game/Skyguard/Capture/RT_AAA_L37"
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

def dist(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

SNAP_STATS = {"ok": 0, "bad": 0, "samples": []}

def spawn_sm(mesh, loc, scale=(1,1,1), rot=None, label=None, mat=None):
    """Multi-path placement with location probe."""
    if not mesh:
        return None
    x, y, z = float(loc[0]), float(loc[1]), float(loc[2])
    sx, sy, sz = float(scale[0]), float(scale[1]), float(scale[2])
    target = (x, y, z)
    a = None

    # Path A: EditorActorSubsystem
    try:
        sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        if sub:
            a = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z), rot or unreal.Rotator())
    except Exception as e:
        log("spawn pathA " + str(e))

    # Path B: EditorLevelLibrary
    if not a:
        try:
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.StaticMeshActor, unreal.Vector(x, y, z), rot or unreal.Rotator()
            )
        except Exception as e:
            log("spawn pathB " + str(e))
            return None
    if not a:
        return None

    try:
        a.static_mesh_component.set_static_mesh(mesh)
    except Exception:
        pass
    try:
        a.set_actor_scale3d(unreal.Vector(sx, sy, sz))
    except Exception:
        pass

    # Force location multiple ways
    for _ in range(3):
        try:
            a.set_actor_location(unreal.Vector(x, y, z), False, True)
        except Exception:
            pass
        try:
            root = a.root_component or a.get_editor_property("root_component")
            if root:
                root.set_world_location(unreal.Vector(x, y, z), False, True)
        except Exception:
            try:
                a.static_mesh_component.set_world_location(unreal.Vector(x, y, z), False, True)
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
    if got is not None:
        d = dist(got, target)
        if d < 5.0:
            SNAP_STATS["ok"] += 1
        else:
            SNAP_STATS["bad"] += 1
            if len(SNAP_STATS["samples"]) < 12:
                SNAP_STATS["samples"].append((label or "?", target, got, d))
                log("SNAP label=%s target=%s got=%s d=%.1f" % (label, target, got, d))
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
    canopy = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Canopy")
    brick = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Brick") or load_mat("/Game/Skyguard/Materials/Generated/M_BrickFacade")
    plaster = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Plaster")
    asphalt = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Asphalt")
    ocean = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Ocean")
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
    mats_hi = [m for m in [unlit_w, unlit_y, unlit_c, unlit_r, unlit_g, white, bright_metal, panel, boom, muzzle] if m]

    def hi(i):
        return mats_hi[i % len(mats_hi)] if mats_hi else panel

    # LOCKED Prop/Yak recipe + additive stages from L34
    stages = [
        ("Prop", (0.0, 0.0, 500.0), 180.0, 12, 9),
        ("PropHub", (0.0, 200.0, 500.0), 160.0, 10, 8),
        ("PropNose", (0.0, -200.0, 500.0), 160.0, 10, 8),
        ("YakBeauty", (300.0, -250.0, 420.0), 220.0, 12, 8),
        ("Cockpit", (40.0, 120.0, 380.0), 80.0, 14, 11),
        ("ADS", (20.0, 150.0, 370.0), 70.0, 10, 8),
        ("City", (-1200.0, 0.0, 300.0), 160.0, 14, 10),
        ("Combat", (900.0, 0.0, 450.0), 140.0, 11, 8),
        ("Harbor", (-400.0, 400.0, 180.0), 140.0, 10, 7),
        ("Ocean", (900.0, -400.0, 140.0), 160.0, 11, 7),
        ("Wide", (200.0, -600.0, 420.0), 200.0, 12, 8),
    ]

    # Unique giant probe markers first (max contrast) at each board center
    for name, cam, dist, ny, nz in stages:
        cx, cy, cz = cam
        bx = cx + dist
        spawn_sm(sphere, (bx, cy, cz), (4.0, 4.0, 4.0), None, PREFIX + "Probe_%s" % name, unlit_y or white)
        spawn_sm(cube, (bx, cy + 8, cz), (2.0, 2.0, 2.0), None, PREFIX + "Probe2_%s" % name, unlit_r or unlit_c)

    for name, cam, dist, ny, nz in stages:
        cx, cy, cz = cam
        bx = cx + dist
        for iy in range(-ny, ny + 1):
            for iz in range(-nz, nz + 1):
                mat = hi(iy + iz * 3)
                spawn_sm(cube, (bx, cy + iy * 4.5, cz + iz * 4.5), (0.3, 0.45, 0.45), None, PREFIX + "Board_%s_%d_%d" % (name, iy, iz), mat)
        if name.startswith("Prop"):
            for i, ang in enumerate(range(0, 180, 12)):
                spawn_sm(cube, (bx - 4, cy, cz), (0.18, 7.5, 0.16), unreal.Rotator(0, ang, 0), PREFIX + "Blade_%s_%d" % (name, i), hi(i))
            spawn_sm(sphere, (bx - 8, cy, cz), (1.6, 1.6, 1.6), None, PREFIX + "Hub_%s" % name, hi(1))
            spawn_sm(cone, (bx - 16, cy, cz), (1.1, 1.1, 2.2), unreal.Rotator(0, 0, -90), PREFIX + "Spinner_%s" % name, unlit_y or white)
        if name == "YakBeauty":
            for i in range(24):
                spawn_sm(cube, (bx - 2, cy - 30 + i * 2.2, cz), (0.07, 0.12, 3.2), None, PREFIX + "YPanelV_%d" % i, hi(i))
                spawn_sm(cube, (bx - 2, cy, cz - 22 + i * 1.5), (0.07, 4.0, 0.1), None, PREFIX + "YPanelH_%d" % i, hi(i + 1))
            for i in range(48):
                spawn_sm(sphere, (bx - 1, cy - 35 + (i % 12) * 5, cz - 18 + (i // 12) * 7), (0.14, 0.14, 0.14), None, PREFIX + "YRivet_%d" % i, unlit_w if i % 3 == 0 else bright_metal)
        if name == "Cockpit":
            for i in range(28):
                spawn_sm(cyl, (bx - 3, cy - 20 + i * 1.5, cz - 1), (0.4, 0.4, 0.09), unreal.Rotator(90, 0, 0), PREFIX + "Gauge_%d" % i, unlit_y if i % 2 == 0 else unlit_c)
                spawn_sm(cube, (bx - 2.2, cy - 20 + i * 1.5, cz - 0.5), (0.05, 0.25, 0.04), None, PREFIX + "Needle_%d" % i, unlit_r)
                spawn_sm(cube, (bx - 6, cy - 20 + i * 1.5, cz - 4), (0.3, 0.9, 0.1), None, PREFIX + "Dash_%d" % i, panel)
            for i in range(36):
                spawn_sm(sphere, (bx - 8 + (i % 6) * 1.5, cy - 16 + (i // 6) * 3.0, cz + (i % 5) * 1.2), (0.28, 0.28, 0.28), None, PREFIX + "CockFill_%d" % i, hi(i))
        if name == "City":
            for i in range(40):
                h = 4 + (i % 8)
                matb = unlit_y if i % 3 == 0 else (unlit_c if i % 3 == 1 else unlit_w)
                spawn_sm(cube, (bx + 10, cy - 60 + i * 3.0, cz - 8 + h * 2.2), (1.5, 1.3, h), None, PREFIX + "CityBlk_%d" % i, matb)
                spawn_sm(cube, (bx + 18, cy - 60 + i * 3.0, cz + 2), (0.12, 0.85, 0.4), None, PREFIX + "CityWin_%d" % i, unlit_r if i % 2 == 0 else unlit_y)
            for i in range(24):
                spawn_sm(cube, (bx + 2, cy - 45 + i * 4, cz - 18), (0.35, 2.5, 0.12), None, PREFIX + "CityRoad_%d" % i, unlit_w)
        if name == "Combat":
            for i in range(20):
                spawn_sm(sphere, (bx + i * 5, cy - 10 + (i % 4) * 5, cz + (i % 5) * 3), (1.2, 1.2, 1.2), None, PREFIX + "Burst_%d" % i, unlit_y if i % 2 == 0 else unlit_r)
                spawn_sm(cube, (bx + 12 + i * 2.5, cy, cz), (0.16, 0.16, 2.2), None, PREFIX + "Tracer_%d" % i, unlit_c if i % 2 == 0 else unlit_w)
        if name in ("Harbor", "Ocean"):
            for i in range(22):
                spawn_sm(plane, (bx + 4, cy - 45 + i * 4, cz - 18), (3.5, 3.5, 1), unreal.Rotator(90, 0, 0), PREFIX + "Wave_%s_%d" % (name, i), unlit_c if i % 2 == 0 else unlit_w)
                spawn_sm(cube, (bx + 8, cy - 45 + i * 4, cz - 16), (0.9, 1.6, 0.12), None, PREFIX + "Foam_%s_%d" % (name, i), unlit_y if i % 2 == 0 else unlit_w)

    # Yak kit at beauty
    meshes = []
    try:
        for a in unreal.EditorAssetLibrary.list_assets("/Game/Skyguard/Meshes/WebGame/yak52-detail-kit", True, False):
            asset = unreal.EditorAssetLibrary.load_asset(a)
            if isinstance(asset, unreal.StaticMesh):
                n = a.split("/")[-1].split(".")[0]
                low = n.lower()
                if low.startswith("production-") or "yak52" in low:
                    meshes.append((a, asset, n, low))
    except Exception as e:
        log("yak list " + str(e))
    ref = None
    for path, mesh, n, low in meshes:
        if "wings-tail" in low or "exterior" in low or "fuselage" in low:
            ref = mesh
            break
    sc = 1.0
    if ref:
        try:
            e = ref.get_bounds().box_extent
            bm = max(abs(e.x) * 2, abs(e.y) * 2, abs(e.z) * 2, 0.001)
            sc = 950.0 / bm
            if sc > 20:
                sc = 1.0
            if sc < 0.02:
                sc = 0.25
        except Exception:
            sc = 0.29
    s = (sc, sc, sc)
    log("yak prod=%d scale=%s" % (len(meshes), s))
    origin = (520.0, -250.0, 400.0)
    for path, mesh, n, low in meshes:
        mat = air
        if any(k in low for k in ["panel", "instrument", "gauge"]):
            mat = panel
        if "glass" in low or "canopy" in low:
            mat = canopy or glass or panel
        if "upholstery" in low or "quilt" in low:
            mat = leather
        spawn_sm(mesh, origin, s, None, PREFIX + "Yak_%s" % n[:40], mat)

    # lights
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 5200), unreal.Rotator(-26, 38, 0))
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
        ((180, 0, 510), 200000.0),
        ((160, 200, 510), 180000.0),
        ((160, -200, 510), 180000.0),
        ((520, -250, 430), 180000.0),
        ((120, 120, 390), 320000.0),  # cockpit strong
        ((90, 150, 375), 180000.0),
        ((-1040, 0, 310), 300000.0),  # city strong
        ((1040, 0, 460), 200000.0),
        ((-260, 400, 190), 160000.0),
        ((1060, -400, 150), 160000.0),
        ((400, -600, 430), 160000.0),
    ]):
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label(PREFIX + "Pt_%d" % i)
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

    log("SNAP_STATS ok=%d bad=%d samples=%s" % (SNAP_STATS["ok"], SNAP_STATS["bad"], SNAP_STATS["samples"][:6]))
    log("loop37 densify done")
    return stages

def capture(out_dir, stages):
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir("/Game/Skyguard/Capture")
    if unreal.EditorAssetLibrary.does_asset_exist(RT_PATH):
        rt = unreal.EditorAssetLibrary.load_asset(RT_PATH)
    else:
        rt = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "RT_AAA_L37", "/Game/Skyguard/Capture", unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew()
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
        cams.append(("AAA_Cam_L37_%s" % name, cam, (0.0, 0.0, 0.0)))
    for name, loc, rot in cams:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)
            try:
                c.set_actor_location(unreal.Vector(*loc), False, True)
            except Exception:
                pass
            got = get_loc(c)
            log("CAM %s target=%s got=%s" % (name, loc, got))

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
            comp.set_editor_property("fov_angle", 95.0)
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
        f.write("Skyguard AAA Loop37 stills\n")
        f.write("time=%s\n" % time.strftime("%Y-%m-%dT%H:%M:%S"))
        f.write("snap_ok=%d snap_bad=%d\n" % (SNAP_STATS["ok"], SNAP_STATS["bad"]))
        f.write("note=probe_spawn_location_assert; yaw0 multi-stage; host_pillow\n")
        for path, size, h, src, name in saved:
            f.write("%s  %d  src=%s cam=%s  %s\n" % (h, size, src, name, path))
        f.write("total=%d\n" % len(saved))
    log("manifest total=%d snap_ok=%d snap_bad=%d" % (len(saved), SNAP_STATS["ok"], SNAP_STATS["bad"]))
    return saved

def main():
    log("loop37 spawn-location probe + additive densify start")
    unreal.EditorLevelLibrary.load_level(MAP_PATH)
    clear_old()
    stages = densify()
    saved = capture(OUT_DIR, stages)
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop37 complete stills=%d snap_ok=%d snap_bad=%d" % (len(saved) if saved else 0, SNAP_STATS["ok"], SNAP_STATS["bad"]))
    log("CRITIC: host RGB select+audit required; overall FAIL until blind AAA win")

main()
