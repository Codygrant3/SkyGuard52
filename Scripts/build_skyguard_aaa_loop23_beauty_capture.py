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

def make_mat(name, base, metallic=0.0, roughness=0.5, emissive=None):
    ensure_dir("/Game/Skyguard/Materials/Generated")
    path = "/Game/Skyguard/Materials/Generated/" + name
    mel = unreal.MaterialEditingLibrary
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        mat = unreal.EditorAssetLibrary.load_asset(path)
    else:
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, "/Game/Skyguard/Materials/Generated", unreal.Material, unreal.MaterialFactoryNew())
    if not mat:
        return None
    try:
        mel.delete_all_material_expressions(mat)
        bc = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -450, -100)
        bc.set_editor_property("constant", unreal.LinearColor(base[0], base[1], base[2], 1))
        # noise variation
        try:
            noise = mel.create_material_expression(mat, unreal.MaterialExpressionNoise, -450, 20)
            noise.set_editor_property("scale", 1.5)
            scale = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -280, 60)
            scale.set_editor_property("r", 0.12)
            mul = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -160, 20)
            mel.connect_material_expressions(noise, "", mul, "A")
            mel.connect_material_expressions(scale, "", mul, "B")
            one = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -280, 110)
            one.set_editor_property("r", 1.0)
            add = mel.create_material_expression(mat, unreal.MaterialExpressionAdd, -40, 0)
            mel.connect_material_expressions(one, "", add, "A")
            mel.connect_material_expressions(mul, "", add, "B")
            bm = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, 80, -60)
            mel.connect_material_expressions(bc, "", bm, "A")
            mel.connect_material_expressions(add, "", bm, "B")
            mel.connect_material_property(bm, "", unreal.MaterialProperty.MP_BASE_COLOR)
        except Exception:
            mel.connect_material_property(bc, "", unreal.MaterialProperty.MP_BASE_COLOR)
        r = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -450, 180)
        r.set_editor_property("r", float(roughness))
        mel.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS)
        m = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -450, 240)
        m.set_editor_property("r", float(metallic))
        mel.connect_material_property(m, "", unreal.MaterialProperty.MP_METALLIC)
        if emissive is not None:
            em = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -450, 300)
            em.set_editor_property("constant", unreal.LinearColor(emissive[0], emissive[1], emissive[2], 1))
            mel.connect_material_property(em, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        mel.recompile_material(mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mat)
        log("mat " + name)
    except Exception as e:
        log("mat fail " + name + " " + str(e))
    return mat

def densify_materials_and_world():
    cube = load_sm("/Engine/BasicShapes/Cube")
    sphere = load_sm("/Engine/BasicShapes/Sphere")
    plane = load_sm("/Engine/BasicShapes/Plane")
    cyl = load_sm("/Engine/BasicShapes/Cylinder")

    air = make_mat("M_L23_Airframe", (0.62, 0.64, 0.58), metallic=0.55, roughness=0.38)
    canopy = make_mat("M_L23_Canopy", (0.15, 0.22, 0.28), metallic=0.05, roughness=0.08, emissive=(0.02, 0.03, 0.04))
    leather = make_mat("M_L23_Leather", (0.12, 0.07, 0.04), metallic=0.0, roughness=0.75)
    panel = make_mat("M_L23_Panel", (0.18, 0.18, 0.17), metallic=0.2, roughness=0.55)
    ocean = make_mat("M_L23_Ocean", (0.05, 0.28, 0.42), metallic=0.15, roughness=0.12, emissive=(0.01, 0.04, 0.06))
    foam = make_mat("M_L23_Foam", (0.85, 0.9, 0.92), metallic=0.0, roughness=0.5)
    beach = make_mat("M_L23_Beach", (0.78, 0.66, 0.42), metallic=0.0, roughness=0.9)
    brick = make_mat("M_L23_Brick", (0.48, 0.26, 0.17), metallic=0.0, roughness=0.82)
    plaster = make_mat("M_L23_Plaster", (0.72, 0.7, 0.64), metallic=0.0, roughness=0.7)
    asphalt = make_mat("M_L23_Asphalt", (0.08, 0.08, 0.09), metallic=0.0, roughness=0.85)
    glass = make_mat("M_L23_Glass", (0.2, 0.3, 0.4), metallic=0.0, roughness=0.05, emissive=(0.25, 0.18, 0.06))
    muzzle = make_mat("M_L23_Muzzle", (1.0, 0.55, 0.1), metallic=0.0, roughness=0.3, emissive=(4.0, 1.5, 0.2))
    boom = make_mat("M_L23_Boom", (1.0, 0.35, 0.05), metallic=0.0, roughness=0.4, emissive=(3.0, 0.8, 0.1))

    # Yak hero production meshes + materials override
    meshes = list_static_meshes("/Game/Skyguard/Meshes/WebGame/yak52-detail-kit")
    prod = []
    for path, mesh in meshes:
        n = path.split("/")[-1].split(".")[0]
        low = n.lower()
        if low.startswith("production-") or low.startswith("batch_"):
            # skip pure needles if too tiny later
            prod.append((path, mesh, n, low))
    # scale using wings/fuselage
    ref = None
    for path, mesh, n, low in prod:
        if "wings-tail" in low or "exterior" in low or "fuselage" in low:
            ref = mesh
            break
    sc = 1.0
    if ref:
        sc = 950.0 / bounds_max(ref)
        if sc > 20: sc = 1.0
        if sc < 0.02: sc = 0.25
    s = (sc, sc, sc)
    log("yak parts=%d scale=%s" % (len(prod), s))
    origin = (0.0, 40.0, 330.0)
    for i, (path, mesh, n, low) in enumerate(prod):
        mat = air
        if "instrument" in low or "panel" in low or "gauge" in low or "annunciator" in low:
            mat = panel
        if "upholstery" in low or "quilt" in low:
            mat = leather
        if "glass" in low or "canopy" in low:
            mat = canopy
        spawn_sm(mesh, origin, s, None, "AAA_L23_Yak_%s" % n[:42], mat)

    # explicit cockpit set around rear seat for cockpit cam
    for i, (path, mesh, n, low) in enumerate(prod):
        if "rear" in low or "instrument" in low or "throttle" in low or "needle" in low:
            # place extra at cockpit-friendly scale near gunner
            sc2 = 2.5 * sc
            spawn_sm(mesh, (15, 100, 355), (sc2, sc2, sc2), unreal.Rotator(0, 0, 0), "AAA_L23_CockpitPart_%s" % n[:36], panel if "needle" not in low else make_mat("M_L23_Needle", (0.9,0.1,0.05), 0.3, 0.4, (1.0,0.2,0.05)))

    # continuous fuselage fill + canopy glass
    spawn_sm(cyl, (0, 40, 330), (1.6, 1.6, 10), unreal.Rotator(0, 0, 90), "AAA_L23_FuseFill", air)
    spawn_sm(cube, (0, 40, 325), (15, 2.4, 0.18), None, "AAA_L23_WingFill", air)
    spawn_sm(plane, (20, 100, 390), (1.6, 1.2, 1), unreal.Rotator(75, 0, 0), "AAA_L23_CanopyL", canopy)
    spawn_sm(plane, (20, 140, 390), (1.6, 1.2, 1), unreal.Rotator(75, 0, 0), "AAA_L23_CanopyR", canopy)
    spawn_sm(cube, (10, 110, 350), (0.5, 0.9, 0.08), None, "AAA_L23_SeatBase", leather)

    # prop
    for i, ang in enumerate(range(0, 180, 20)):
        spawn_sm(cube, (-300, 40, 330), (0.12, 3.8, 0.08), unreal.Rotator(0, ang, 0), "AAA_L23_Blade_%d" % i, air)
    try:
        cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardPropSpinner")
        if cls:
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(-300, 40, 330), unreal.Rotator())
            if a:
                a.set_actor_label("AAA_L23_PropSpinner")
                a.set_actor_scale3d(unreal.Vector(1.5, 1.5, 1.5))
    except Exception as e:
        log("prop " + str(e))

    # ocean beauty
    for i, x in enumerate([300, 900, 1500, 2100, 2700, 3300, 3900]):
        for j, y in enumerate(range(-3600, 3601, 900)):
            spawn_sm(plane, (x, y, 0.5), (100, 100, 1), None, "AAA_L23_Ocean_%d_%d" % (i, j), ocean)
    for i, y in enumerate(range(-3600, 3601, 80)):
        spawn_sm(cube, (-800, y, 5), (2.5, 3.5, 0.1), None, "AAA_L23_Foam_%d" % i, foam)
        spawn_sm(cube, (-880, y, 9), (12, 4.5, 0.4), None, "AAA_L23_Beach_%d" % i, beach)

    # city
    for i in range(70):
        x = -2400 - (i % 10) * 150
        y = -3400 + (i // 10) * 320
        h = 6 + (i * 11) % 15
        spawn_sm(cube, (x, y, 40 + h * 22), (3.2, 2.8, h), None, "AAA_L23_Bldg_%d" % i, brick if i % 2 == 0 else plaster)
        spawn_sm(cube, (x + 30, y, 120 + (i % 7) * 45), (0.08, 1.9, 0.55), None, "AAA_L23_Win_%d" % i, glass)
    for i, y in enumerate(range(-3600, 3601, 160)):
        spawn_sm(cube, (-1950, y, 34), (16, 7, 0.1), None, "AAA_L23_Road_%d" % i, asphalt)

    # harbor
    for i, y in enumerate([-1800, -600, 600, 1800]):
        spawn_sm(cube, (-940, y, 120), (1.2, 1.2, 10), None, "AAA_L23_Crane_%d" % i, air)
        spawn_sm(cube, (-820, y, 300), (10, 0.5, 0.5), None, "AAA_L23_Boom_%d" % i, air)
        spawn_sm(cube, (-420, y, 28), (18, 4.5, 2.6), None, "AAA_L23_Ship_%d" % i, plaster)

    # combat VFX readable still markers + drones
    for i in range(24):
        spawn_sm(sphere, (40 + i * 10, 150, 365), (0.12, 0.12, 0.12), None, "AAA_L23_Muzzle_%d" % i, muzzle)
    for i in range(20):
        spawn_sm(sphere, (850 - i * 35, -60 + (i % 4) * 40, 420 + (i % 3) * 20), (1.2, 1.2, 1.2), None, "AAA_L23_Burst_%d" % i, boom)
    drone_parts = list_static_meshes("/Game/Skyguard/Meshes/WebGame/skyguard-drone")
    for i, (path, mesh) in enumerate(drone_parts[:8]):
        sc = 200.0 / bounds_max(mesh)
        if sc > 40: sc = 1.0
        spawn_sm(mesh, (950 - i * 50, -40 + (i % 3) * 35, 430), (sc, sc, sc), unreal.Rotator(0, 180, 0), "AAA_L23_Drone_%d" % i)
    rifle_parts = list_static_meshes("/Game/Skyguard/Meshes/WebGame/skyguard-rifle")
    for i, (path, mesh) in enumerate(rifle_parts[:8]):
        sc = 110.0 / bounds_max(mesh)
        if sc > 40: sc = 1.0
        spawn_sm(mesh, (22, 125, 360), (sc, sc, sc), unreal.Rotator(0, 90, 0), "AAA_L23_Rifle_%d" % i)

    log("materials+world densify done")

def densify_lights():
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 4500), unreal.Rotator(-36, 40, 0))
    if sun:
        sun.set_actor_label("AAA_L23_Sun")
        try:
            c = sun.get_component_by_class(unreal.DirectionalLightComponent)
            if c:
                c.set_intensity(22.0)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
                c.set_editor_property("atmosphere_sun_light", True)
        except Exception as e:
            log("sun " + str(e))
    fill = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 3000), unreal.Rotator(-18, -130, 0))
    if fill:
        fill.set_actor_label("AAA_L23_Fill")
        try:
            c = fill.get_component_by_class(unreal.DirectionalLightComponent)
            if c:
                c.set_intensity(7.0)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception:
            pass
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 1600), unreal.Rotator())
    if sky:
        sky.set_actor_label("AAA_L23_Sky")
        try:
            c = sky.get_component_by_class(unreal.SkyLightComponent)
            if c:
                c.set_intensity(3.2)
                c.set_editor_property("real_time_capture", True)
        except Exception:
            pass
    for i, loc in enumerate([(0, 40, 420), (-250, 40, 380), (50, 130, 370), (900, 0, 450), (-800, -900, 220), (1600, -200, 240), (20, 110, 380)]):
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label("AAA_L23_Pt_%d" % i)
            try:
                c = pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(220000.0)
                    c.set_editor_property("attenuation_radius", 8000.0)
                    c.set_mobility(unreal.ComponentMobility.MOVABLE)
            except Exception:
                pass
    try:
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), unreal.Rotator()).set_actor_label("AAA_L23_Atmo")
    except Exception:
        pass
    try:
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0), unreal.Rotator()).set_actor_label("AAA_L23_Fog")
    except Exception:
        pass
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 200), unreal.Rotator())
    if pp:
        pp.set_actor_label("AAA_L23_PP")
        try:
            pp.set_editor_property("unbound", True)
        except Exception:
            pass
    log("lights done")

def reseed():
    try:
        for cls_path, loc, label in [
            ("/Script/Skyguard52.SkyguardGunner", (20, 105, 360), "AAA_L23_CPP_Gunner"),
            ("/Script/Skyguard52.SkyguardDroneSpawner", (2800, 0, 520), "AAA_L23_CPP_Spawner"),
            ("/Script/Skyguard52.SkyguardPropSpinner", (-300, 40, 330), "AAA_L23_PropSpinner"),
        ]:
            cls = unreal.load_class(None, cls_path)
            if cls:
                a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator())
                if a:
                    a.set_actor_label(label)
    except Exception as e:
        log("cpp " + str(e))

def capture(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir("/Game/Skyguard/Capture")
    path = "/Game/Skyguard/Capture/RT_AAA_L23"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        rt = unreal.EditorAssetLibrary.load_asset(path)
    else:
        rt = unreal.AssetToolsHelpers.get_asset_tools().create_asset("RT_AAA_L23", "/Game/Skyguard/Capture", unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew())
    rt.set_editor_property("size_x", 1920)
    rt.set_editor_property("size_y", 1080)
    try:
        rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA8)
    except Exception:
        pass
    unreal.EditorAssetLibrary.save_loaded_asset(rt)

    # proven closer cams
    cams = [
        ("AAA_Cam_L23_YakBeauty", (260, -320, 365), (-5, 148, 0)),
        ("AAA_Cam_L23_Cockpit", (28, 112, 370), (-5, 8, 0)),
        ("AAA_Cam_L23_ADS", (18, 135, 365), (-1, 8, 0)),
        ("AAA_Cam_L23_Ocean", (700, -120, 160), (-10, 20, 0)),
        ("AAA_Cam_L23_Harbor", (-420, -320, 200), (-6, -20, 0)),
        ("AAA_Cam_L23_City", (-1000, -500, 360), (-7, 35, 0)),
        ("AAA_Cam_L23_Combat", (700, -30, 420), (-6, 185, 0)),
        ("AAA_Cam_L23_Wide", (160, -650, 460), (-12, 130, 0)),
        ("AAA_Cam_L23_Prop", (-30, -90, 335), (-3, 40, 0)),
    ]
    for name, loc, rot in cams:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)

    sca = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0, 0, 400), unreal.Rotator())
    sca.set_actor_label("AAA_L23_SceneCapture")
    comp = sca.get_editor_property("capture_component2d")
    comp.set_editor_property("texture_target", rt)
    comp.set_editor_property("capture_every_frame", True)
    try:
        comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    except Exception:
        try:
            comp.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_BASE_COLOR)
        except Exception:
            pass
    try:
        comp.set_editor_property("fov_angle", 78.0)
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
        try:
            unreal.RenderingLibrary.export_render_target(world, rt, out_dir, name + ".png")
        except Exception as e:
            log("export " + name + " " + str(e))
        if os.path.isfile(out_png):
            size = os.path.getsize(out_png)
            h = hashlib.sha256(open(out_png, "rb").read()).hexdigest()
            log("still %s size=%d sha=%s" % (name, size, h[:16]))
            saved.append((out_png, size, h))
        else:
            log("missing " + name)
    try:
        comp.set_editor_property("capture_every_frame", False)
    except Exception:
        pass
    man = os.path.join(out_dir, "MANIFEST_SHA256.txt")
    with open(man, "w", encoding="utf-8") as f:
        f.write("Skyguard AAA Loop23 stills\n")
        f.write("time=%s\n" % time.strftime("%Y-%m-%dT%H:%M:%S"))
        f.write("note=host_pillow_rgb_authoritative\n")
        for path, size, h in saved:
            f.write("%s  %d  %s\n" % (h, size, path))
        f.write("total=%d\n" % len(saved))
    log("manifest total=%d" % len(saved))
    return saved

def main():
    log("loop23 beauty materials + hero densify capture start")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L23_")
    densify_lights()
    densify_materials_and_world()
    reseed()
    saved = capture(r"D:\Skyguard52\Saved\Screenshots\AAA_L23")
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop23 complete stills=%d" % (len(saved) if saved else 0))
    log("CRITIC: host RGB audit required; overall FAIL until blind AAA win on all pillars")

if __name__ == "__main__":
    main()
