import unreal
import os
import hashlib
import time
import struct
import zlib

def log(m):
    unreal.log("[SkyguardAAA] " + str(m))

def clear_prefix(prefix):
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        try:
            n = a.get_actor_label()
            if n and n.startswith(prefix):
                unreal.EditorLevelLibrary.destroy_actor(a)
        except Exception:
            pass

def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)

def load_mat(path):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path)
    return None

def load_sm(path):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        a = unreal.EditorAssetLibrary.load_asset(path)
        if isinstance(a, unreal.StaticMesh):
            return a
    return None

def spawn_sm(mesh, loc, scale=(1,1,1), rot=None, label=None, mat=None):
    if not mesh:
        return None
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc), rot or unreal.Rotator())
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

def spawn_actor(cls_path, loc, rot=(0,0,0), label=None):
    try:
        cls = unreal.load_class(None, cls_path)
        if not cls:
            return None
        a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator(*rot))
        if a and label:
            a.set_actor_label(label)
        return a
    except Exception as e:
        log("spawn " + cls_path + " " + str(e))
        return None

def densify_atmosphere():
    # Remove old L17 lights first handled by clear_prefix
    sun = spawn_actor("/Script/Engine.DirectionalLight", (0,0,2500), (-35, 50, 0), "AAA_L17_Sun")
    try:
        if sun:
            # boost intensity if possible
            comp = sun.get_component_by_class(unreal.DirectionalLightComponent)
            if comp:
                try:
                    comp.set_editor_property("intensity", 12.0)
                    comp.set_editor_property("atmosphere_sun_light", True)
                except Exception:
                    pass
    except Exception as e:
        log("sun props " + str(e))

    sky = spawn_actor("/Script/Engine.SkyLight", (0,0,900), (0,0,0), "AAA_L17_SkyLight")
    try:
        if sky:
            comp = sky.get_component_by_class(unreal.SkyLightComponent)
            if comp:
                try:
                    comp.set_editor_property("intensity", 1.5)
                    comp.set_editor_property("real_time_capture", True)
                except Exception:
                    pass
    except Exception as e:
        log("skylight " + str(e))

    # Sky atmosphere
    spawn_actor("/Script/Engine.SkyAtmosphere", (0,0,0), (0,0,0), "AAA_L17_SkyAtmosphere")
    # Volumetric clouds if available
    spawn_actor("/Script/Engine.VolumetricCloud", (0,0,0), (0,0,0), "AAA_L17_VolCloud")
    # Exponential fog
    fog = spawn_actor("/Script/Engine.ExponentialHeightFog", (0,0,0), (0,0,0), "AAA_L17_Fog")
    try:
        if fog:
            comp = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
            if comp:
                try:
                    comp.set_editor_property("fog_density", 0.015)
                    comp.set_editor_property("fog_height_falloff", 0.15)
                except Exception:
                    pass
    except Exception as e:
        log("fog " + str(e))

    # Sky sphere / BP sky if exists
    spawn_actor("/Script/Engine.SkyAtmosphere", (0,0,100), (0,0,0), "AAA_L17_SkyAtmosphere2")

    pp = spawn_actor("/Script/Engine.PostProcessVolume", (0,0,300), (0,0,0), "AAA_L17_PP")
    try:
        if pp:
            pp.set_editor_property("unbound", True)
            settings = pp.get_editor_property("settings")
            # enable some look
            try:
                settings.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
            except Exception:
                pass
    except Exception as e:
        log("pp " + str(e))

    # fill light
    spawn_actor("/Script/Engine.DirectionalLight", (0,0,2000), (-20, -130, 0), "AAA_L17_FillSun")
    log("atmosphere densify done")

def densify_city_ocean():
    cube = load_sm("/Engine/BasicShapes/Cube")
    sphere = load_sm("/Engine/BasicShapes/Sphere")
    plane = load_sm("/Engine/BasicShapes/Plane")
    cyl = load_sm("/Engine/BasicShapes/Cylinder")
    brick = load_mat("/Game/Skyguard/Materials/Generated/M_BrickFacade") or load_mat("/Game/Skyguard/Materials/M_Tex_brick")
    concrete = load_mat("/Game/Skyguard/Materials/Generated/M_ConcreteWall") or load_mat("/Game/Skyguard/Materials/M_CityConcrete")
    asphalt = load_mat("/Game/Skyguard/Materials/Generated/M_AsphaltRoad") or load_mat("/Game/Skyguard/Materials/M_Asphalt")
    metal = load_mat("/Game/Skyguard/Materials/Generated/M_AirframeMetal") or load_mat("/Game/Skyguard/Materials/M_Metal")
    glass = load_mat("/Game/Skyguard/Materials/M_CityGlass")
    ocean = load_mat("/Game/Skyguard/Materials/M_Ocean")
    deep = load_mat("/Game/Skyguard/Materials/M_OceanDeep")
    beach = load_mat("/Game/Skyguard/Materials/M_Beach")
    foam = load_mat("/Game/Skyguard/Materials/M_L5_SeaFoam")
    exhaust = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or load_mat("/Game/Skyguard/Materials/Generated/MI_MuzzleFlash_Hot")

    # landmark towers
    for i, y in enumerate([-2400, -800, 800, 2400]):
        h = 18 + i * 3
        spawn_sm(cube, (-2600, y, 40 + h*25), (4.5, 4.5, h), None, "AAA_L17_Landmark_%d" % i, concrete if i%2==0 else brick)
        spawn_sm(cube, (-2555, y, 80 + h*20), (0.1, 3.5, h*0.7), None, "AAA_L17_LandmarkGlass_%d" % i, glass)
        spawn_sm(cyl, (-2600, y, 80 + h*50), (0.3, 0.3, 2.0), None, "AAA_L17_Antenna_%d" % i, metal)

    # dense window emissive scatter
    for i in range(160):
        x = -2400 - (i % 10) * 120
        y = -3500 + (i * 53) % 7000
        z = 120 + (i * 41) % 900
        spawn_sm(cube, (x, y, z), (0.06, 0.7, 0.45), None, "AAA_L17_Window_%d" % i, glass)

    # ocean large planes both sides
    for i, x in enumerate([0, 1200, 2600, 4200]):
        for j, y in enumerate(range(-4800, 4801, 2000)):
            m = deep if x > 1500 else ocean
            spawn_sm(plane, (x, y, -1.5), (110, 110, 1), None, "AAA_L17_Ocean_%d_%d" % (i, j), m)

    # beach + foam
    for i, y in enumerate(range(-4500, 4501, 100)):
        spawn_sm(cube, (-840, y, 7), (12, 4.5, 0.35), None, "AAA_L17_Beach_%d" % i, beach)
        spawn_sm(cube, (-760, y, 3), (2.0, 4.0, 0.05), None, "AAA_L17_Foam_%d" % i, foam)

    # combat VFX readable still markers near gunner + drone lane
    for i in range(20):
        spawn_sm(sphere, (50 + i*15, 150, 365), (0.08,0.08,0.08), None, "AAA_L17_Muzzle_%d" % i, exhaust)
    for i in range(25):
        spawn_sm(sphere, (1800 - i*40, (i%5)*80, 420), (0.5,0.5,0.5), None, "AAA_L17_Burst_%d" % i, exhaust)

    # reseed prop spinner
    try:
        cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardPropSpinner")
        if cls:
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(-190,40,330), unreal.Rotator())
            if a:
                a.set_actor_label("AAA_L17_PropSpinner")
                a.set_actor_scale3d(unreal.Vector(1.3,1.3,1.3))
    except Exception as e:
        log("prop " + str(e))

    # combat
    try:
        gcls = unreal.load_class(None, "/Script/Skyguard52.SkyguardGunner")
        scls = unreal.load_class(None, "/Script/Skyguard52.SkyguardDroneSpawner")
        if gcls:
            g = unreal.EditorLevelLibrary.spawn_actor_from_class(gcls, unreal.Vector(20,105,360), unreal.Rotator())
            if g: g.set_actor_label("AAA_L17_CPP_Gunner")
        if scls:
            s = unreal.EditorLevelLibrary.spawn_actor_from_class(scls, unreal.Vector(2800,0,520), unreal.Rotator())
            if s: s.set_actor_label("AAA_L17_CPP_Spawner")
    except Exception as e:
        log("cpp " + str(e))
    log("city/ocean densify done")

def ensure_rt(name="RT_AAA_L17", w=1920, h=1080):
    ensure_dir("/Game/Skyguard/Capture")
    path = "/Game/Skyguard/Capture/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        rt = unreal.EditorAssetLibrary.load_asset(path)
    else:
        rt = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, "/Game/Skyguard/Capture", unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew()
        )
    if not rt:
        return None, path
    try:
        rt.set_editor_property("size_x", w)
        rt.set_editor_property("size_y", h)
        try:
            rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA8)
        except Exception:
            pass
        try:
            # clear color non-black so failed capture is obvious orange
            rt.set_editor_property("clear_color", unreal.LinearColor(0.15, 0.35, 0.8, 1.0))
        except Exception:
            pass
    except Exception as e:
        log("rt props " + str(e))
    unreal.EditorAssetLibrary.save_loaded_asset(rt)
    return rt, path

def png_black_ratio(path):
    """Return (black_ratio, unique_approx, size). Uses raw inflate best-effort; on fail use size heuristic."""
    try:
        data = open(path, "rb").read()
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            return 1.0, 0, len(data)
        # collect IDAT
        pos = 8
        idat = b""
        w = h = 0
        while pos + 8 <= len(data):
            length = struct.unpack(">I", data[pos:pos+4])[0]
            ctype = data[pos+4:pos+8]
            chunk = data[pos+8:pos+8+length]
            if ctype == b"IHDR":
                w, h = struct.unpack(">II", chunk[:8])
            elif ctype == b"IDAT":
                idat += chunk
            elif ctype == b"IEND":
                break
            pos += 12 + length
        raw = zlib.decompress(idat)
        # filter decode simple: assume filter 0 rows for approx, else sample bytes
        # Many UE exports are filter-type rows; count near-zero bytes as black proxy
        if not raw:
            return 1.0, 0, len(data)
        # sample
        step = max(1, len(raw)//50000)
        sample = raw[::step]
        black = sum(1 for b in sample if b < 8) / float(len(sample))
        uniq = len(set(sample[:5000]))
        return black, uniq, len(data)
    except Exception as e:
        log("png audit fail " + str(e))
        # heuristic: tiny files ~black compressed
        sz = os.path.getsize(path) if os.path.isfile(path) else 0
        return (1.0 if sz < 60000 else 0.5), 0, sz

def capture_stills(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    rt, rt_path = ensure_rt()
    if not rt:
        log("no RT")
        return []

    cams_spec = [
        ("AAA_Cam_L17_YakBeauty", (750, -1250, 580), (-12, 145, 0)),
        ("AAA_Cam_L17_Cockpit", (30, 115, 372), (-7, 8, 0)),
        ("AAA_Cam_L17_ADS", (18, 140, 366), (-1, 8, 0)),
        ("AAA_Cam_L17_Ocean", (1800, -900, 500), (-10, 165, 0)),
        ("AAA_Cam_L17_Harbor", (-700, -1400, 300), (-8, 35, 0)),
        ("AAA_Cam_L17_City", (-1300, -700, 420), (-9, 25, 0)),
        ("AAA_Cam_L17_Combat", (1200, -100, 470), (-10, 180, 0)),
        ("AAA_Cam_L17_Prop", (-100, -220, 340), (-5, 25, 0)),
    ]
    cams = []
    for name, loc, rot in cams_spec:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)
            cams.append((name, c, loc, rot))

    sca = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0,0,400), unreal.Rotator())
    if not sca:
        log("no scenecapture")
        return []
    sca.set_actor_label("AAA_L17_SceneCapture")
    comp = None
    try:
        comp = sca.get_editor_property("capture_component2d")
    except Exception:
        try:
            comp = sca.capture_component2d
        except Exception:
            comp = None
    if not comp:
        log("no capture comp")
        return []

    # Configure capture for lit final color
    try:
        comp.set_editor_property("texture_target", rt)
        comp.set_editor_property("capture_every_frame", True)
        comp.set_editor_property("capture_on_movement", True)
        try:
            comp.set_editor_property("primitive_render_mode", unreal.SceneCapturePrimitiveRenderMode.PRM_RENDER_SCENE_PRIMITIVES)
        except Exception:
            pass
        try:
            # CaptureSource FinalColorLDR if available
            comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
        except Exception:
            try:
                comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_SCENE_COLOR_HDR)
            except Exception:
                pass
        try:
            comp.set_editor_property("fov_angle", 80.0)
        except Exception:
            pass
        # show flags
        try:
            sf = comp.get_editor_property("show_flag_settings")
        except Exception:
            pass
    except Exception as e:
        log("capture configure " + str(e))

    world = None
    try:
        world = unreal.UnrealEditorSubsystem().get_editor_world()
    except Exception:
        try:
            world = unreal.EditorLevelLibrary.get_editor_world()
        except Exception:
            world = None

    saved = []
    for name, cam, loc, rot in cams:
        try:
            sca.set_actor_location(unreal.Vector(*loc), False, True)
            sca.set_actor_rotation(unreal.Rotator(*rot), False)
            # multiple captures to warm RT
            for _ in range(5):
                try:
                    comp.capture_scene()
                except Exception:
                    pass
            out_png = os.path.join(out_dir, name + ".png")
            if os.path.isfile(out_png):
                try:
                    os.remove(out_png)
                except Exception:
                    pass
            ok = False
            try:
                if world is not None:
                    ok = unreal.RenderingLibrary.export_render_target(world, rt, out_dir, name + ".png")
                else:
                    ok = unreal.RenderingLibrary.export_render_target(None, rt, out_dir, name + ".png")
            except Exception as e:
                log("export fail " + name + " " + str(e))
                ok = False

            # Fallback: HighResShot console (may async; still try)
            if (not os.path.isfile(out_png)) or os.path.getsize(out_png) < 2000:
                try:
                    unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(*loc), unreal.Rotator(*rot))
                except Exception:
                    pass
                try:
                    unreal.SystemLibrary.execute_console_command(world, "HighResShot 1920x1080")
                    log("HighResShot issued for " + name)
                except Exception as e:
                    log("highresshot " + str(e))

            if os.path.isfile(out_png):
                black, uniq, size = png_black_ratio(out_png)
                h = hashlib.sha256(open(out_png, "rb").read()).hexdigest()
                valid = (black < 0.45 and size > 20000) or (uniq > 80 and size > 30000)
                log("still %s black=%.3f uniq~%d size=%d valid=%s sha=%s" % (name, black, uniq, size, valid, h[:16]))
                saved.append((out_png, size, h, black, uniq, valid))
            else:
                log("missing still " + name)
        except Exception as e:
            log("cam " + name + " " + str(e))

    # stop continuous capture
    try:
        comp.set_editor_property("capture_every_frame", False)
    except Exception:
        pass
    return saved

def write_manifest(out_dir, saved):
    man = os.path.join(out_dir, "MANIFEST_SHA256.txt")
    with open(man, "w", encoding="utf-8") as f:
        f.write("Skyguard AAA Loop17 stills\n")
        f.write("time=%s\n" % time.strftime("%Y-%m-%dT%H:%M:%S"))
        valid_n = 0
        for path, size, h, black, uniq, valid in saved:
            f.write("%s  %d  black=%.3f uniq=%d valid=%s  %s\n" % (h, size, black, uniq, valid, path))
            if valid:
                valid_n += 1
        f.write("valid_count=%d total=%d\n" % (valid_n, len(saved)))
    log("manifest " + man + " valid=" + str(sum(1 for s in saved if s[5])))

def main():
    log("loop17 atmosphere+fixed capture start")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L17_")

    densify_atmosphere()
    densify_city_ocean()

    out_dir = r"D:\Skyguard52\Saved\Screenshots\AAA_L17"
    saved = capture_stills(out_dir)
    if saved:
        write_manifest(out_dir, saved)
    valid_n = sum(1 for s in saved if s[5]) if saved else 0

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop17 complete stills=%d valid=%d" % (len(saved), valid_n))
    if valid_n == 0:
        log("CRITIC: FAIL capture still black/invalid; overall FAIL vs AAA")
    else:
        log("CRITIC: valid stills available for blind compare; densify improved but AAA win still required")

if __name__ == "__main__":
    main()
