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

def get_comp(actor, *class_names):
    if not actor:
        return None
    for cn in class_names:
        try:
            cls = getattr(unreal, cn, None)
            if cls:
                c = actor.get_component_by_class(cls)
                if c:
                    return c
        except Exception:
            pass
    # try common properties
    for prop in ["light_component", "directional_light_component", "point_light_component", "sky_light_component", "root_component"]:
        try:
            c = actor.get_editor_property(prop)
            if c:
                return c
        except Exception:
            pass
    return None

def set_intensity(comp, value):
    if not comp:
        return
    for meth in ["set_intensity", "set_editor_property"]:
        try:
            if meth == "set_intensity":
                comp.set_intensity(value)
                return
            else:
                comp.set_editor_property("intensity", value)
                return
        except Exception:
            continue

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

def densify_lit_world():
    cube = load_sm("/Engine/BasicShapes/Cube")
    sphere = load_sm("/Engine/BasicShapes/Sphere")
    plane = load_sm("/Engine/BasicShapes/Plane")
    cyl = load_sm("/Engine/BasicShapes/Cylinder")

    air = load_mat("/Game/Skyguard/Materials/Generated/M_AirframeMetal") or load_mat("/Game/Skyguard/Materials/M_Tex_airframe_metal") or load_mat("/Game/Skyguard/Materials/M_Metal")
    brick = load_mat("/Game/Skyguard/Materials/Generated/M_BrickFacade") or load_mat("/Game/Skyguard/Materials/M_Tex_brick")
    concrete = load_mat("/Game/Skyguard/Materials/Generated/M_ConcreteWall") or load_mat("/Game/Skyguard/Materials/M_CityConcrete")
    asphalt = load_mat("/Game/Skyguard/Materials/Generated/M_AsphaltRoad") or load_mat("/Game/Skyguard/Materials/M_Asphalt")
    ocean = load_mat("/Game/Skyguard/Materials/M_Ocean")
    deep = load_mat("/Game/Skyguard/Materials/M_OceanDeep")
    beach = load_mat("/Game/Skyguard/Materials/M_Beach")
    glass = load_mat("/Game/Skyguard/Materials/M_CityGlass")
    propmat = load_mat("/Game/Skyguard/Materials/M_PropDisc") or air

    # Giant continuous Yak proxy silhouette at aircraft origin for beauty cam readability
    # Fuselage
    spawn_sm(cyl, (0, 40, 330), (1.2, 1.2, 8.0), unreal.Rotator(0, 0, 90), "AAA_L19_YakFuselage", air)
    # Wings
    spawn_sm(cube, (0, 40, 325), (10.0, 1.6, 0.15), None, "AAA_L19_YakWing", air)
    # Tail
    spawn_sm(cube, (280, 40, 360), (0.15, 1.2, 1.8), None, "AAA_L19_YakTail", air)
    spawn_sm(cube, (280, 40, 330), (1.8, 0.8, 0.12), None, "AAA_L19_YakElev", air)
    # Cowling
    spawn_sm(sphere, (-220, 40, 330), (1.6, 1.6, 1.6), None, "AAA_L19_YakNose", air)
    # Prop blades static readable + spinner actor
    for i, ang in enumerate([0, 60, 120]):
        spawn_sm(cube, (-250, 40, 330), (0.15, 3.2, 0.08), unreal.Rotator(0, ang, 0), "AAA_L19_PropBlade_%d" % i, propmat)
    try:
        cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardPropSpinner")
        if cls:
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(-250, 40, 330), unreal.Rotator())
            if a:
                a.set_actor_label("AAA_L19_PropSpinner")
                a.set_actor_scale3d(unreal.Vector(1.4, 1.4, 1.4))
    except Exception as e:
        log("prop " + str(e))

    # City skyline continuous wall of buildings with texture mats
    for i in range(60):
        x = -2500 - (i % 10) * 140
        y = -3600 + (i // 10) * 300
        h = 5 + (i * 13) % 16
        spawn_sm(cube, (x, y, 40 + h * 22), (3.0, 2.6, h), None, "AAA_L19_Bldg_%d" % i, brick if i % 3 else concrete)
        spawn_sm(cube, (x + 28, y, 100 + (i % 8) * 40), (0.08, 1.8, 0.5), None, "AAA_L19_Win_%d" % i, glass)

    # Roads
    for i, y in enumerate(range(-3800, 3801, 180)):
        spawn_sm(cube, (-1950, y, 34), (16, 7, 0.1), None, "AAA_L19_Road_%d" % i, asphalt)

    # Ocean planes + beach
    for i, x in enumerate([200, 1400, 2800, 4200]):
        for j, y in enumerate(range(-5000, 5001, 2200)):
            spawn_sm(plane, (x, y, -1), (120, 120, 1), None, "AAA_L19_Ocean_%d_%d" % (i, j), deep if x > 1500 else ocean)
    for i, y in enumerate(range(-4500, 4501, 120)):
        spawn_sm(cube, (-850, y, 8), (12, 5, 0.4), None, "AAA_L19_Beach_%d" % i, beach)

    # Harbor cranes/ships simple
    for i, y in enumerate([-1600, 0, 1600]):
        spawn_sm(cube, (-950, y, 120), (1.0, 1.0, 8.0), None, "AAA_L19_Crane_%d" % i, air)
        spawn_sm(cube, (-850, y, 280), (7.0, 0.4, 0.4), None, "AAA_L19_Boom_%d" % i, air)
        spawn_sm(cube, (-400, y, 25), (16, 4, 2.2), None, "AAA_L19_Ship_%d" % i, concrete)

    # combat markers
    try:
        g = unreal.load_class(None, "/Script/Skyguard52.SkyguardGunner")
        s = unreal.load_class(None, "/Script/Skyguard52.SkyguardDroneSpawner")
        if g:
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(g, unreal.Vector(20, 105, 360), unreal.Rotator())
            if a: a.set_actor_label("AAA_L19_CPP_Gunner")
        if s:
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(s, unreal.Vector(2800, 0, 520), unreal.Rotator())
            if a: a.set_actor_label("AAA_L19_CPP_Spawner")
    except Exception as e:
        log("cpp " + str(e))
    log("lit world densify done")

def densify_lights():
    # Key
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 3200), unreal.Rotator(-38, 40, 0))
    if sun:
        sun.set_actor_label("AAA_L19_KeySun")
        c = get_comp(sun, "DirectionalLightComponent", "LightComponent")
        set_intensity(c, 15.0)
        try:
            if c:
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
                c.set_editor_property("atmosphere_sun_light", True)
        except Exception:
            pass
    fill = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 2800), unreal.Rotator(-20, -150, 0))
    if fill:
        fill.set_actor_label("AAA_L19_FillSun")
        c = get_comp(fill, "DirectionalLightComponent", "LightComponent")
        set_intensity(c, 6.0)
        try:
            if c: c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception:
            pass
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 1200), unreal.Rotator())
    if sky:
        sky.set_actor_label("AAA_L19_SkyLight")
        c = get_comp(sky, "SkyLightComponent", "LightComponent")
        set_intensity(c, 2.5)
        try:
            if c:
                c.set_editor_property("real_time_capture", True)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception:
            pass
    # local point lights on aircraft and city
    for i, loc in enumerate([(-50, 40, 400), (50, 120, 380), (0, -20, 370), (-1800, 0, 200), (-900, -800, 150)]):
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label("AAA_L19_Point_%d" % i)
            c = get_comp(pl, "PointLightComponent", "LightComponent")
            set_intensity(c, 80000.0)
            try:
                if c:
                    c.set_editor_property("attenuation_radius", 4000.0)
                    c.set_mobility(unreal.ComponentMobility.MOVABLE)
            except Exception:
                pass
    try:
        a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), unreal.Rotator())
        if a: a.set_actor_label("AAA_L19_Atmosphere")
    except Exception:
        pass
    try:
        a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0), unreal.Rotator())
        if a: a.set_actor_label("AAA_L19_Fog")
    except Exception:
        pass
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 200), unreal.Rotator())
    if pp:
        pp.set_actor_label("AAA_L19_PP")
        try:
            pp.set_editor_property("unbound", True)
        except Exception:
            pass
    log("lights densify done")

def png_stats(path):
    try:
        data = open(path, "rb").read()
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            return 1.0, 0, len(data)
        pos = 8
        idat = b""
        while pos + 8 <= len(data):
            ln = struct.unpack(">I", data[pos:pos+4])[0]
            ct = data[pos+4:pos+8]
            ch = data[pos+8:pos+8+ln]
            if ct == b"IDAT":
                idat += ch
            if ct == b"IEND":
                break
            pos += 12 + ln
        raw = zlib.decompress(idat)
        step = max(1, len(raw)//50000)
        sample = raw[::step]
        black = sum(1 for b in sample if b < 8) / float(len(sample))
        uniq = len(set(sample[:8000]))
        return black, uniq, len(data)
    except Exception:
        sz = os.path.getsize(path) if os.path.isfile(path) else 0
        return 1.0, 0, sz

def capture(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir("/Game/Skyguard/Capture")
    # two RTs
    def make_rt(name):
        path = "/Game/Skyguard/Capture/" + name
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            rt = unreal.EditorAssetLibrary.load_asset(path)
        else:
            rt = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, "/Game/Skyguard/Capture", unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew())
        rt.set_editor_property("size_x", 1920)
        rt.set_editor_property("size_y", 1080)
        try:
            rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA8)
        except Exception:
            pass
        unreal.EditorAssetLibrary.save_loaded_asset(rt)
        return rt

    rt_final = make_rt("RT_AAA_L19_Final")
    rt_base = make_rt("RT_AAA_L19_Base")

    cams = [
        ("AAA_Cam_L19_YakBeauty", (650, -1100, 520), (-10, 140, 0)),
        ("AAA_Cam_L19_Cockpit", (30, 115, 372), (-6, 8, 0)),
        ("AAA_Cam_L19_ADS", (18, 140, 366), (-1, 8, 0)),
        ("AAA_Cam_L19_Ocean", (1700, -900, 480), (-10, 165, 0)),
        ("AAA_Cam_L19_Harbor", (-700, -1400, 280), (-8, 35, 0)),
        ("AAA_Cam_L19_City", (-1300, -700, 420), (-9, 25, 0)),
        ("AAA_Cam_L19_Combat", (1100, -100, 460), (-10, 180, 0)),
        ("AAA_Cam_L19_Prop", (-100, -200, 340), (-5, 20, 0)),
        ("AAA_Cam_L19_Wide", (400, -1600, 700), (-15, 120, 0)),
    ]
    for name, loc, rot in cams:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)

    sca = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0, 0, 400), unreal.Rotator())
    sca.set_actor_label("AAA_L19_SceneCapture")
    comp = sca.get_editor_property("capture_component2d")
    comp.set_editor_property("capture_every_frame", True)
    try:
        comp.set_editor_property("fov_angle", 80.0)
    except Exception:
        pass

    try:
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    except Exception:
        world = unreal.EditorLevelLibrary.get_editor_world()

    sources = []
    # prefer base color then final
    for src_name, rt in [
        ("BASE", rt_base),
        ("FINAL", rt_final),
    ]:
        enum = None
        try:
            if src_name == "BASE":
                enum = unreal.SceneCaptureSource.SCS_BASE_COLOR
            else:
                enum = unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR
        except Exception:
            try:
                enum = unreal.SceneCaptureSource.SCS_SCENE_COLOR_HDR
            except Exception:
                enum = None
        sources.append((src_name, rt, enum))

    saved = []
    for name, loc, rot in cams:
        best = None
        for src_name, rt, enum in sources:
            try:
                comp.set_editor_property("texture_target", rt)
                if enum is not None:
                    comp.set_editor_property("capture_source", enum)
            except Exception as e:
                log("set source " + str(e))
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
                black, uniq, size = png_stats(out_png)
                h = hashlib.sha256(open(out_png, "rb").read()).hexdigest()
                valid = (black < 0.55 and uniq > 80 and size > 30000) or (uniq > 250 and size > 50000 and black < 0.75)
                log("still %s black=%.3f uniq=%d size=%d valid=%s" % (out_name, black, uniq, size, valid))
                rec = (out_png, size, h, black, uniq, valid, src_name)
                saved.append(rec)
                if valid and (best is None or uniq > best[4]):
                    best = rec
        # also copy best as canonical name if found
        if best and best[5]:
            canon = os.path.join(out_dir, name + ".png")
            try:
                import shutil
                shutil.copyfile(best[0], canon)
                log("canonical " + name + " from " + best[6])
            except Exception as e:
                log("copy canon " + str(e))

    try:
        comp.set_editor_property("capture_every_frame", False)
    except Exception:
        pass

    man = os.path.join(out_dir, "MANIFEST_SHA256.txt")
    with open(man, "w", encoding="utf-8") as f:
        f.write("Skyguard AAA Loop19 stills\n")
        f.write("time=%s\n" % time.strftime("%Y-%m-%dT%H:%M:%S"))
        vc = 0
        for path, size, h, black, uniq, valid, src in saved:
            f.write("%s  %d  black=%.3f uniq=%d valid=%s src=%s  %s\n" % (h, size, black, uniq, valid, src, path))
            if valid:
                vc += 1
        f.write("valid_count=%d total=%d\n" % (vc, len(saved)))
    log("manifest valid=%d/%d" % (sum(1 for s in saved if s[5]), len(saved)))
    return saved

def main():
    log("loop19 lit densify + dual capture start")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L19_")
    densify_lights()
    densify_lit_world()
    saved = capture(r"D:\Skyguard52\Saved\Screenshots\AAA_L19")
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    vc = sum(1 for s in saved if s[5]) if saved else 0
    log("Loop19 complete stills=%d valid=%d" % (len(saved) if saved else 0, vc))
    if vc == 0:
        log("CRITIC: still FAIL capture usability; overall FAIL vs AAA")
    else:
        log("CRITIC: valid stills present; harsh blind still required before any AAA win claim")

if __name__ == "__main__":
    main()
