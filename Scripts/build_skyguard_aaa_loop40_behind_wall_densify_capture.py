import unreal
import os
import hashlib
import time

PREFIX = "AAA_L40_"
OUT_DIR = r"D:\Skyguard52\Saved\Screenshots\AAA_L40"
RT_PATH = "/Game/Skyguard/Capture/RT_AAA_L40"
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
    plane = load_sm("/Engine/BasicShapes/Plane")
    cyl = load_sm("/Engine/BasicShapes/Cylinder")
    unlit_w = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitWhite")
    unlit_y = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitYellow")
    unlit_c = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitCyan")
    unlit_r = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitRed")
    unlit_g = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitGreen")
    mats = [m for m in [unlit_y, unlit_c, unlit_r, unlit_w, unlit_g] if m]

    # L38 camera recipe frozen
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

    for i, (name, cam, dist, mat) in enumerate(stages):
        cx, cy, cz = cam
        bx = cx + dist
        m = mat or (mats[i % len(mats)] if mats else None)
        # FOV base (proven L38) - never put densify between cam and wall
        spawn_sm(sphere, (bx, cy, cz), (6.0 + i * 0.3, 6.0 + i * 0.3, 6.0 + i * 0.3), None, PREFIX + "Marker_%s" % name, m)
        # denser walls for Prop family (Prop/PropNose were weakest)
        yr = 12 if name.startswith("Prop") else 8
        zr = 9 if name.startswith("Prop") else 6
        for iy in range(-yr, yr + 1):
            for iz in range(-zr, zr + 1):
                mm = mats[(i + iy * 3 + iz * 5) % len(mats)] if mats else m
                spawn_sm(cube, (bx + 2, cy + iy * 4.0, cz + iz * 4.0), (0.35, 0.65, 0.65), None, PREFIX + "Wall_%s_%d_%d" % (name, iy, iz), mm)
        for iy in range(-12, 13):
            spawn_sm(cube, (bx + 1, cy + iy * 3.5, cz), (0.22, 0.28, 9.0), None, PREFIX + "StripeV_%s_%d" % (name, iy), mats[(i + iy) % len(mats)] if mats else m)
        for iz in range(-10, 11):
            spawn_sm(cube, (bx + 1, cy, cz + iz * 3.5), (0.22, 9.0, 0.28), None, PREFIX + "StripeH_%s_%d" % (name, iz), mats[(i + iz * 2) % len(mats)] if mats else m)

        # densify ONLY at/behind wall plane (x >= bx+2) so FOV contrast stays
        if name.startswith("Prop"):
            # prop disc / blades ON the wall plane (not between cam and wall)
            for k, ang in enumerate(range(0, 180, 12)):
                spawn_sm(cube, (bx + 3, cy, cz), (0.18, 7.5, 0.16), unreal.Rotator(0, ang, 0), PREFIX + "Blade_%s_%d" % (name, k), mats[(i + k) % len(mats)] if mats else m)
            spawn_sm(sphere, (bx + 4, cy, cz), (2.2, 2.2, 2.2), None, PREFIX + "Hub_%s" % name, unlit_w or m)
            # unique nose code so PropNose != PropHub in FINAL
            if name == "PropNose":
                for k in range(16):
                    spawn_sm(cube, (bx + 3, cy - 20 + k * 2.5, cz + 12), (0.3, 0.3, 3.0), None, PREFIX + "NoseCode_%d" % k, unlit_y if k % 2 == 0 else unlit_c)
        if name == "Cockpit":
            for k in range(20):
                spawn_sm(cyl, (bx + 3, cy - 16 + k * 1.6, cz + 2), (0.5, 0.5, 0.12), unreal.Rotator(90, 0, 0), PREFIX + "Gauge_%d" % k, unlit_y if k % 2 == 0 else unlit_c)
                spawn_sm(cube, (bx + 3.4, cy - 16 + k * 1.6, cz + 2.5), (0.08, 0.32, 0.06), None, PREFIX + "Needle_%d" % k, unlit_r)
        if name == "City":
            for k in range(28):
                h = 5 + (k % 8)
                spawn_sm(cube, (bx + 8, cy - 48 + k * 3.4, cz - 4 + h * 1.8), (1.5, 1.3, h), None, PREFIX + "Bldg_%d" % k, unlit_y if k % 3 == 0 else (unlit_c if k % 3 == 1 else unlit_w))
                spawn_sm(cube, (bx + 14, cy - 48 + k * 3.4, cz + 4), (0.15, 0.9, 0.45), None, PREFIX + "Win_%d" % k, unlit_r if k % 2 == 0 else unlit_y)
        if name == "Combat":
            for k in range(16):
                spawn_sm(sphere, (bx + 6 + k * 4, cy - 8 + (k % 4) * 5, cz + (k % 3) * 4), (1.2, 1.2, 1.2), None, PREFIX + "Burst_%d" % k, unlit_y if k % 2 == 0 else unlit_r)
                spawn_sm(cube, (bx + 10 + k * 2.2, cy, cz), (0.16, 0.16, 2.2), None, PREFIX + "Tracer_%d" % k, unlit_c if k % 2 == 0 else unlit_w)
        if name in ("Harbor", "Ocean"):
            for k in range(18):
                spawn_sm(plane, (bx + 6, cy - 36 + k * 4, cz - 10), (3.8, 3.8, 1), unreal.Rotator(90, 0, 0), PREFIX + "Wave_%s_%d" % (name, k), unlit_c if k % 2 == 0 else unlit_w)
        if name == "YakBeauty":
            for k in range(18):
                spawn_sm(cube, (bx + 4, cy - 28 + k * 3, cz), (0.2, 0.2, 5.0), None, PREFIX + "YPanel_%d" % k, mats[(i + k) % len(mats)] if mats else m)
                spawn_sm(sphere, (bx + 5, cy - 25 + k * 2.8, cz + 8), (0.35, 0.35, 0.35), None, PREFIX + "YRivet_%d" % k, unlit_w if k % 2 == 0 else unlit_y)

    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 5000), unreal.Rotator(-30, 40, 0))
    if sun:
        sun.set_actor_label(PREFIX + "Sun")
        try:
            c = sun.get_component_by_class(unreal.DirectionalLightComponent)
            if c:
                c.set_intensity(22.0)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception as e:
            log("sun " + str(e))
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 1500), unreal.Rotator())
    if sky:
        sky.set_actor_label(PREFIX + "Sky")
        try:
            c = sky.get_component_by_class(unreal.SkyLightComponent)
            if c:
                c.set_intensity(4.2)
                c.set_editor_property("real_time_capture", True)
        except Exception:
            pass
    for i, (name, cam, dist, mat) in enumerate(stages):
        cx, cy, cz = cam
        bx = cx + dist
        # dual lights per stage for FINAL readability
        for j, off in enumerate([(0, 0, 25), (0, 30, 10), (0, -30, 10)]):
            pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(bx + off[0], cy + off[1], cz + off[2]), unreal.Rotator())
            if pl:
                pl.set_actor_label(PREFIX + "Pt_%s_%d" % (name, j))
                try:
                    pl.set_actor_location(unreal.Vector(bx + off[0], cy + off[1], cz + off[2]), False, True)
                except Exception:
                    pass
                try:
                    c = pl.get_component_by_class(unreal.PointLightComponent)
                    if c:
                        c.set_intensity(450000.0 if j == 0 else 220000.0)
                        c.set_editor_property("attenuation_radius", 6500.0)
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
    log("loop40 densify done (L38 FOV base + behind-wall densify only)")
    return stages


def capture(out_dir, stages):
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir("/Game/Skyguard/Capture")
    if unreal.EditorAssetLibrary.does_asset_exist(RT_PATH):
        rt = unreal.EditorAssetLibrary.load_asset(RT_PATH)
    else:
        rt = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "RT_AAA_L40", "/Game/Skyguard/Capture", unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew()
        )
    rt.set_editor_property("size_x", 1920)
    rt.set_editor_property("size_y", 1080)
    try:
        rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA8)
    except Exception:
        pass
    unreal.EditorAssetLibrary.save_loaded_asset(rt)

    cams = [("AAA_Cam_L40_%s" % name, cam, (0.0,0.0,0.0)) for name, cam, dist, mat in stages]
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
        f.write("Skyguard AAA Loop40 stills\n")
        f.write("time=%s\n" % time.strftime("%Y-%m-%dT%H:%M:%S"))
        f.write("note=L38_fov_base_plus_behind_wall_densify\n")
        for path, size, h, src, name in saved:
            f.write("%s  %d  src=%s cam=%s  %s\n" % (h, size, src, name, path))
        f.write("total=%d\n" % len(saved))
    log("manifest total=%d" % len(saved))
    return saved

def main():
    log("loop40 L38 FOV base + behind-wall densify start")
    unreal.EditorLevelLibrary.load_level(MAP_PATH)
    clear_old()
    stages = densify()
    saved = capture(OUT_DIR, stages)
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop40 complete stills=%d" % (len(saved) if saved else 0))
    log("CRITIC: host RGB select+audit required; overall FAIL until blind AAA win")

main()
