import unreal
import os
import hashlib
import time
import math

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
        return max(abs(e.x)*2, abs(e.y)*2, abs(e.z)*2, 0.001)
    except Exception:
        return 100.0

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

def densify_yak_hero():
    # Prefer production yak meshes from imported kit
    meshes = list_static_meshes("/Game/Skyguard/Meshes/WebGame/yak52-detail-kit")
    production = []
    for path, mesh in meshes:
        name = path.split("/")[-1].split(".")[0].lower()
        if name.startswith("production-yak52") or "wings" in name or "fuselage" in name or "exterior" in name:
            production.append((path, mesh, name))
    log("yak production meshes=" + str(len(production)))
    # scale to ~9.5m
    if production:
        ref = None
        for path, mesh, name in production:
            if "wings" in name or "exterior" in name:
                ref = mesh
                break
        if ref is None:
            ref = production[0][1]
        sc = 950.0 / bounds_max(ref)
        if sc > 20: sc = 1.0
        if sc < 0.02: sc = 0.25
        s = (sc, sc, sc)
        log("yak scale=" + str(s))
        origin = (0.0, 40.0, 330.0)
        for i, (path, mesh, name) in enumerate(production[:30]):
            spawn_sm(mesh, origin, s, None, "AAA_L22_Yak_%s" % name[:40])
    else:
        # fallback continuous proxy
        air = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightMetal") or load_mat("/Game/Skyguard/Materials/M_Metal")
        cube = load_sm("/Engine/BasicShapes/Cube")
        cyl = load_sm("/Engine/BasicShapes/Cylinder")
        sphere = load_sm("/Engine/BasicShapes/Sphere")
        spawn_sm(cyl, (0,40,330), (1.5,1.5,10), unreal.Rotator(0,0,90), "AAA_L22_YakFuse", air)
        spawn_sm(cube, (0,40,325), (14,2.2,0.2), None, "AAA_L22_YakWing", air)
        spawn_sm(sphere, (-300,40,330), (2.2,2.2,2.2), None, "AAA_L22_YakNose", air)

    # rifle / drone hero parts near combat lane
    rifle_parts = list_static_meshes("/Game/Skyguard/Meshes/WebGame/skyguard-rifle")
    drone_parts = list_static_meshes("/Game/Skyguard/Meshes/WebGame/skyguard-drone")
    log("rifle meshes=%d drone meshes=%d" % (len(rifle_parts), len(drone_parts)))
    for i, (path, mesh) in enumerate(rifle_parts[:8]):
        sc = 120.0 / bounds_max(mesh)
        if sc > 50: sc = 1.0
        spawn_sm(mesh, (25, 130, 360), (sc,sc,sc), unreal.Rotator(0,90,0), "AAA_L22_Rifle_%d"%i)
    for i, (path, mesh) in enumerate(drone_parts[:8]):
        sc = 220.0 / bounds_max(mesh)
        if sc > 50: sc = 1.0
        spawn_sm(mesh, (900 - i*40, -50 + (i%3)*30, 430), (sc,sc,sc), unreal.Rotator(0,180,0), "AAA_L22_Drone_%d"%i)

def densify_ocean_city():
    plane = load_sm("/Engine/BasicShapes/Plane")
    cube = load_sm("/Engine/BasicShapes/Cube")
    ocean = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightOcean") or load_mat("/Game/Skyguard/Materials/M_Ocean")
    beach = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightSand") or load_mat("/Game/Skyguard/Materials/M_Beach")
    brick = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightBrick") or load_mat("/Game/Skyguard/Materials/Generated/M_BrickFacade")
    white = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightWhite")
    metal = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightMetal")
    # denser ocean grid in front of ocean cam
    for i,x in enumerate([400,1000,1600,2200,2800,3400]):
        for j,y in enumerate(range(-2400,2401,800)):
            spawn_sm(plane, (x,y,1.0), (90,90,1), None, "AAA_L22_Ocean_%d_%d"%(i,j), ocean)
            if i % 2 == 0:
                spawn_sm(cube, (x, y, 8), (6,6,0.3), None, "AAA_L22_Whitecap_%d_%d"%(i,j), white)
    for i,y in enumerate(range(-3000,3001,100)):
        spawn_sm(cube, (-820,y,8), (12,4.5,0.4), None, "AAA_L22_Beach_%d"%i, beach)
    # combat lane bright markers
    for i in range(30):
        spawn_sm(cube, (700+i*40, -100+(i%5)*40, 400+(i%4)*15), (2,2,2), None, "AAA_L22_CombatBlock_%d"%i, metal if i%2==0 else brick)

def densify_lights():
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,4200), unreal.Rotator(-40, 25, 0))
    if sun:
        sun.set_actor_label("AAA_L22_Sun")
        try:
            c = sun.get_component_by_class(unreal.DirectionalLightComponent)
            if c:
                c.set_intensity(18.0)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception:
            pass
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,1600), unreal.Rotator())
    if sky:
        sky.set_actor_label("AAA_L22_Sky")
        try:
            c = sky.get_component_by_class(unreal.SkyLightComponent)
            if c:
                c.set_intensity(2.8)
                c.set_editor_property("real_time_capture", True)
        except Exception:
            pass
    for i, loc in enumerate([(0,40,420),(-200,40,380),(200,100,360),(900,0,450),(-700,-800,220),(1800,-200,250)]):
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label("AAA_L22_Pt_%d"%i)
            try:
                c = pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(180000.0)
                    c.set_editor_property("attenuation_radius", 7000.0)
            except Exception:
                pass
    try:
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0,0,0), unreal.Rotator()).set_actor_label("AAA_L22_Atmo")
    except Exception:
        pass
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,200), unreal.Rotator())
    if pp:
        pp.set_actor_label("AAA_L22_PP")
        try: pp.set_editor_property("unbound", True)
        except Exception: pass

def reseed():
    try:
        for cls_path, loc, label in [
            ("/Script/Skyguard52.SkyguardGunner", (20,105,360), "AAA_L22_CPP_Gunner"),
            ("/Script/Skyguard52.SkyguardDroneSpawner", (2800,0,520), "AAA_L22_CPP_Spawner"),
            ("/Script/Skyguard52.SkyguardPropSpinner", (-280,40,330), "AAA_L22_PropSpinner"),
        ]:
            cls = unreal.load_class(None, cls_path)
            if cls:
                a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator())
                if a: a.set_actor_label(label)
    except Exception as e:
        log("cpp " + str(e))

def capture(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir("/Game/Skyguard/Capture")
    path = "/Game/Skyguard/Capture/RT_AAA_L22"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        rt = unreal.EditorAssetLibrary.load_asset(path)
    else:
        rt = unreal.AssetToolsHelpers.get_asset_tools().create_asset("RT_AAA_L22", "/Game/Skyguard/Capture", unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew())
    rt.set_editor_property("size_x", 1920)
    rt.set_editor_property("size_y", 1080)
    try:
        rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA8)
    except Exception:
        pass
    unreal.EditorAssetLibrary.save_loaded_asset(rt)

    # closer cams that worked + combat restore
    cams = [
        ("AAA_Cam_L22_YakBeauty", (280, -350, 370), (-6, 150, 0)),
        ("AAA_Cam_L22_Ocean", (800, -150, 180), (-10, 15, 0)),
        ("AAA_Cam_L22_Harbor", (-450, -350, 210), (-7, -25, 0)),
        ("AAA_Cam_L22_Wide", (180, -700, 480), (-14, 125, 0)),
        ("AAA_Cam_L22_City", (-1100, -600, 380), (-8, 30, 0)),
        ("AAA_Cam_L22_Cockpit", (30, 115, 372), (-6, 8, 0)),
        ("AAA_Cam_L22_Combat", (750, -40, 420), (-7, 185, 0)),
        ("AAA_Cam_L22_Prop", (-40, -100, 335), (-4, 35, 0)),
    ]
    for name, loc, rot in cams:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c: c.set_actor_label(name)

    sca = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0,0,400), unreal.Rotator())
    sca.set_actor_label("AAA_L22_SceneCapture")
    comp = sca.get_editor_property("capture_component2d")
    comp.set_editor_property("texture_target", rt)
    comp.set_editor_property("capture_every_frame", True)
    # Prefer Final for lit beauty; fallback handled by host audit
    try:
        comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    except Exception:
        try:
            comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_BASE_COLOR)
        except Exception:
            pass
    try:
        comp.set_editor_property("fov_angle", 80.0)
    except Exception:
        pass
    try:
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    except Exception:
        world = unreal.EditorLevelLibrary.get_editor_world()

    saved = []
    for name, loc, rot in cams:
        sca.set_actor_location(unreal.Vector(*loc), False, True)
        sca.set_actor_rotation(unreal.Rotator(*rot), False)
        for _ in range(8):
            try: comp.capture_scene()
            except Exception: pass
        out_png = os.path.join(out_dir, name + ".png")
        if os.path.isfile(out_png):
            try: os.remove(out_png)
            except Exception: pass
        try:
            unreal.RenderingLibrary.export_render_target(world, rt, out_dir, name + ".png")
        except Exception as e:
            log("export " + name + " " + str(e))
        if os.path.isfile(out_png):
            size = os.path.getsize(out_png)
            h = hashlib.sha256(open(out_png, "rb").read()).hexdigest()
            # host will audit; mark provisional valid by size only
            provisional = size > 200000
            log("still %s size=%d provisional=%s sha=%s" % (name, size, provisional, h[:16]))
            saved.append((out_png, size, h, provisional))
        else:
            log("missing " + name)
    try:
        comp.set_editor_property("capture_every_frame", False)
    except Exception:
        pass
    man = os.path.join(out_dir, "MANIFEST_SHA256.txt")
    with open(man, "w", encoding="utf-8") as f:
        f.write("Skyguard AAA Loop22 stills\n")
        f.write("time=%s\n" % time.strftime("%Y-%m-%dT%H:%M:%S"))
        f.write("note=host_pillow_rgb_is_authoritative\n")
        for path, size, h, provisional in saved:
            f.write("%s  %d  provisional=%s  %s\n" % (h, size, provisional, path))
        f.write("total=%d\n" % len(saved))
    log("manifest total=" + str(len(saved)))
    return saved

def main():
    log("loop22 hero yak + ocean/combat densify capture start")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L22_")
    densify_lights()
    densify_yak_hero()
    densify_ocean_city()
    reseed()
    saved = capture(r"D:\Skyguard52\Saved\Screenshots\AAA_L22")
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop22 complete stills=%d" % (len(saved) if saved else 0))
    log("CRITIC: host RGB audit required; overall still FAIL until blind AAA win")

if __name__ == "__main__":
    main()
