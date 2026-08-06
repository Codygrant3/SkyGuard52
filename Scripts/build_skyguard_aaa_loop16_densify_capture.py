import unreal
import os
import hashlib
import time

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

def create_textured_mi(name, albedo_path, normal_path=None, rough_path=None, metallic=0.0, roughness=0.6):
    ensure_dir("/Game/Skyguard/Materials/Generated")
    mi_path = "/Game/Skyguard/Materials/Generated/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(mi_path):
        return unreal.EditorAssetLibrary.load_asset(mi_path)
    # Build a simple master-like material instance via full material when needed
    mel = unreal.MaterialEditingLibrary
    mat_path = "/Game/Skyguard/Materials/Generated/M_" + name
    if unreal.EditorAssetLibrary.does_asset_exist(mat_path):
        mat = unreal.EditorAssetLibrary.load_asset(mat_path)
    else:
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "M_" + name, "/Game/Skyguard/Materials/Generated", unreal.Material, unreal.MaterialFactoryNew()
        )
    if not mat:
        return load_mat("/Game/Skyguard/Materials/M_Metal")
    try:
        mel.delete_all_material_expressions(mat)
        tex = None
        if albedo_path and unreal.EditorAssetLibrary.does_asset_exist(albedo_path):
            tex_sample = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -500, -100)
            tex_obj = unreal.EditorAssetLibrary.load_asset(albedo_path)
            tex_sample.set_editor_property("texture", tex_obj)
            mel.connect_material_property(tex_sample, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
        else:
            c = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -500, -100)
            c.set_editor_property("constant", unreal.LinearColor(0.3, 0.3, 0.32, 1))
            mel.connect_material_property(c, "", unreal.MaterialProperty.MP_BASE_COLOR)
        if normal_path and unreal.EditorAssetLibrary.does_asset_exist(normal_path):
            n = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -500, 80)
            n.set_editor_property("texture", unreal.EditorAssetLibrary.load_asset(normal_path))
            try:
                n.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
            except Exception:
                pass
            mel.connect_material_property(n, "RGB", unreal.MaterialProperty.MP_NORMAL)
        r = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -500, 220)
        r.set_editor_property("r", float(roughness))
        mel.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS)
        m = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -500, 280)
        m.set_editor_property("r", float(metallic))
        mel.connect_material_property(m, "", unreal.MaterialProperty.MP_METALLIC)
        mel.recompile_material(mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mat)
        log("created textured mat M_" + name)
        return mat
    except Exception as e:
        log("tex mat fail " + name + " " + str(e))
        return load_mat("/Game/Skyguard/Materials/M_Metal")

def densify_environment():
    cube = load_sm("/Engine/BasicShapes/Cube")
    cyl = load_sm("/Engine/BasicShapes/Cylinder")
    sphere = load_sm("/Engine/BasicShapes/Sphere")
    plane = load_sm("/Engine/BasicShapes/Plane")

    brick = create_textured_mi("BrickFacade", "/Game/Skyguard/Textures/Imported/T_brick_A", "/Game/Skyguard/Textures/Imported/T_brick_N", roughness=0.85)
    concrete = create_textured_mi("ConcreteWall", "/Game/Skyguard/Textures/Imported/T_concrete_A", "/Game/Skyguard/Textures/Imported/T_concrete_N", roughness=0.8)
    asphalt = create_textured_mi("AsphaltRoad", "/Game/Skyguard/Textures/Imported/T_L3_asphalt2_A", "/Game/Skyguard/Textures/Imported/T_L3_asphalt2_N", roughness=0.9)
    metal = create_textured_mi("AirframeMetal", "/Game/Skyguard/Textures/Imported/T_airframe_metal_A", "/Game/Skyguard/Textures/Imported/T_airframe_metal_N", metallic=0.7, roughness=0.35)
    plate = load_mat("/Game/Skyguard/Materials/M_Tex_L8_plate2") or metal
    plaster = load_mat("/Game/Skyguard/Materials/M_Tex_L8_plaster2") or concrete
    roof = load_mat("/Game/Skyguard/Materials/M_Tex_L3_roof") or plate
    sand = load_mat("/Game/Skyguard/Materials/M_Tex_L7_beach2") or load_mat("/Game/Skyguard/Materials/M_Beach")
    ocean = load_mat("/Game/Skyguard/Materials/M_Ocean")
    glass = load_mat("/Game/Skyguard/Materials/M_CityGlass")
    foliage = load_mat("/Game/Skyguard/Materials/M_Foliage") or plaster

    # Dense midrise city blocks with window grids
    for i in range(48):
        x = -2300 - (i % 8) * 180
        y = -3600 + (i // 8) * 220
        h = 6 + (i * 17) % 14
        spawn_sm(cube, (x, y, 40 + h * 20), (3.2, 2.4, h), None, "AAA_L16_Midrise_%d" % i, brick if i % 2 == 0 else plaster)
        # window strips
        for w in range(min(h, 10)):
            spawn_sm(cube, (x + 32, y, 60 + w * 38), (0.08, 1.8, 0.35), None, "AAA_L16_Win_%d_%d" % (i, w), glass)
        spawn_sm(cube, (x, y, 40 + h * 40 + 8), (3.4, 2.6, 0.25), None, "AAA_L16_Roof_%d" % i, roof)

    # Trees / greenery cards
    tree = load_sm("/Game/Skyguard/Meshes/Hero/coast_tree_proxy")
    for i in range(60):
        x = -1600 - (i % 5) * 70
        y = -3000 + i * 95
        if tree:
            spawn_sm(tree, (x, y, 40), (18, 18, 18), None, "AAA_L16_Tree_%d" % i, foliage)
        else:
            spawn_sm(cyl, (x, y, 70), (0.15, 0.15, 1.2), None, "AAA_L16_TreeTrunk_%d" % i, plate)
            spawn_sm(sphere, (x, y, 120), (0.9, 0.9, 0.7), None, "AAA_L16_TreeCanopy_%d" % i, foliage)

    # Coastal rocks / breakwater
    rock = load_mat("/Game/Skyguard/Materials/M_Tex_L3_rock") or concrete
    for i in range(40):
        y = -3500 + i * 170
        spawn_sm(sphere, (-700, y, 12), (2.5 + (i % 3), 1.8, 1.2), None, "AAA_L16_Rock_%d" % i, rock)

    # Seawall
    seawall = load_sm("/Game/Skyguard/Meshes/Hero/seawall_proxy")
    for i, y in enumerate(range(-3600, 3601, 240)):
        if seawall:
            spawn_sm(seawall, (-780, y, 20), (25, 25, 25), None, "AAA_L16_Seawall_%d" % i, concrete)
        else:
            spawn_sm(cube, (-780, y, 18), (2.0, 10.0, 1.5), None, "AAA_L16_Seawall_%d" % i, concrete)

    # Extra freighters / cranes using proxies
    crane = load_sm("/Game/Skyguard/Meshes/Hero/harbor_crane_proxy")
    freighter = load_sm("/Game/Skyguard/Meshes/Hero/freighter_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/container_ship_proxy")
    for i, y in enumerate([-1800, -600, 600, 1800]):
        if crane:
            spawn_sm(crane, (-950, y, 40), (30, 30, 30), None, "AAA_L16_CraneProxy_%d" % i, metal)
        if freighter:
            spawn_sm(freighter, (-350, y + 100, 10), (35, 35, 35), unreal.Rotator(0, 90, 0), "AAA_L16_Freighter_%d" % i, plate)

    # Road network bands
    for i, y in enumerate(range(-3800, 3801, 160)):
        spawn_sm(cube, (-1950, y, 33.5), (14.0, 6.5, 0.08), None, "AAA_L16_Road_%d" % i, asphalt)

    # Beach reinforcement
    for i, y in enumerate(range(-4000, 4001, 120)):
        spawn_sm(cube, (-860, y, 6), (10.0, 5.5, 0.4), None, "AAA_L16_Beach_%d" % i, sand)

    # Ocean glint cards
    for i in range(30):
        x = 600 + (i * 110) % 2800
        y = -3200 + (i * 211) % 6400
        spawn_sm(plane, (x, y, 1.0), (12, 8, 1), unreal.Rotator(0, (i * 17) % 360, 0), "AAA_L16_OceanGlint_%d" % i, ocean)

    log("environment densify done")

def place_prop_spinner():
    try:
        cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardPropSpinner")
        if cls:
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(-190, 40, 330), unreal.Rotator(0, 0, 0))
            if a:
                a.set_actor_label("AAA_L16_PropSpinner")
                a.set_actor_scale3d(unreal.Vector(1.2, 1.2, 1.2))
                log("spawned prop spinner")
                return True
    except Exception as e:
        log("prop spinner " + str(e))
    # fallback static prop disc
    prop = load_sm("/Game/Skyguard/Meshes/Hero/propeller_proxy")
    matp = load_mat("/Game/Skyguard/Materials/M_PropDisc")
    spawn_sm(prop, (-190, 40, 330), (0.6, 0.6, 0.6), unreal.Rotator(0, 0, 90), "AAA_L16_PropFallback", matp)
    return False

def reseed_combat():
    try:
        gunner_cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardGunner")
        spawner_cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardDroneSpawner")
        if gunner_cls:
            g = unreal.EditorLevelLibrary.spawn_actor_from_class(gunner_cls, unreal.Vector(20, 105, 360), unreal.Rotator())
            if g: g.set_actor_label("AAA_L16_CPP_Gunner")
        if spawner_cls:
            s = unreal.EditorLevelLibrary.spawn_actor_from_class(spawner_cls, unreal.Vector(2800, 0, 520), unreal.Rotator())
            if s: s.set_actor_label("AAA_L16_CPP_Spawner")
    except Exception as e:
        log("cpp " + str(e))

def capture_with_scene_capture(out_dir):
    """Durable stills via SceneCaptureComponent2D + render target export."""
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir("/Game/Skyguard/Capture")
    rt_path = "/Game/Skyguard/Capture/RT_AAA_L16"
    if unreal.EditorAssetLibrary.does_asset_exist(rt_path):
        rt = unreal.EditorAssetLibrary.load_asset(rt_path)
    else:
        rt = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "RT_AAA_L16", "/Game/Skyguard/Capture", unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew()
        )
    if not rt:
        log("no render target")
        return 0, []
    try:
        rt.set_editor_property("size_x", 1920)
        rt.set_editor_property("size_y", 1080)
        rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA8)
    except Exception as e:
        log("rt props " + str(e))
    unreal.EditorAssetLibrary.save_loaded_asset(rt)

    cams = []
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        try:
            n = a.get_actor_label() or ""
            if n.startswith("AAA_Cam_L16_") or n.startswith("AAA_Cam_L15_") or n.startswith("AAA_Cam_L14_"):
                if isinstance(a, unreal.CameraActor):
                    cams.append((n, a))
        except Exception:
            pass
    # ensure own cams
    own = [
        ("AAA_Cam_L16_YakBeauty", (700, -1200, 560), (-12, 145, 0)),
        ("AAA_Cam_L16_Cockpit", (30, 115, 372), (-7, 8, 0)),
        ("AAA_Cam_L16_ADS", (18, 140, 366), (-1, 8, 0)),
        ("AAA_Cam_L16_Ocean", (1600, -800, 480), (-10, 165, 0)),
        ("AAA_Cam_L16_Harbor", (-700, -1400, 280), (-8, 35, 0)),
        ("AAA_Cam_L16_City", (-1200, -700, 400), (-9, 25, 0)),
        ("AAA_Cam_L16_Combat", (1100, -100, 460), (-10, 180, 0)),
        ("AAA_Cam_L16_Prop", (-120, -200, 340), (-5, 20, 0)),
    ]
    for name, loc, rot in own:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)
            cams.append((name, c))

    # Scene capture actor
    sca = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0, 0, 400), unreal.Rotator())
    if not sca:
        log("no scenecapture actor")
        return 0, []
    sca.set_actor_label("AAA_L16_SceneCapture")
    comp = None
    try:
        comp = sca.get_editor_property("capture_component2d")
    except Exception:
        try:
            comp = sca.capture_component2d
        except Exception:
            comp = None
    if not comp:
        log("no capture component")
        return 0, []
    try:
        comp.set_editor_property("texture_target", rt)
        comp.set_editor_property("capture_every_frame", False)
        comp.set_editor_property("capture_on_movement", False)
    except Exception as e:
        log("capture props " + str(e))

    saved = []
    # Prefer unique L16 cams first
    ordered = [c for c in cams if c[0].startswith("AAA_Cam_L16_")] + [c for c in cams if not c[0].startswith("AAA_Cam_L16_")]
    seen = set()
    for name, cam in ordered:
        if name in seen:
            continue
        seen.add(name)
        if len(saved) >= 10:
            break
        try:
            loc = cam.get_actor_location()
            rot = cam.get_actor_rotation()
            sca.set_actor_location(loc, False, True)
            sca.set_actor_rotation(rot, False)
            try:
                comp.set_editor_property("fov_angle", 75.0)
            except Exception:
                pass
            # capture
            try:
                comp.capture_scene()
            except Exception:
                try:
                    # some versions
                    unreal.RenderingLibrary = getattr(unreal, "RenderingLibrary", None)
                except Exception:
                    pass
            # export RT to PNG
            out_png = os.path.join(out_dir, name + ".png")
            ok = False
            try:
                ok = unreal.RenderingLibrary.export_render_target(unreal.EditorLevelLibrary.get_editor_world(), rt, out_dir, name + ".png")
            except Exception as e1:
                try:
                    # alternate API
                    ok = bool(unreal.TextureCompressionSettings)  # noop touch
                    unreal.EditorAssetLibrary.save_asset(rt_path)
                    # fallback: write a tiny proof marker if export API unavailable
                    log("export_render_target fail " + str(e1))
                except Exception as e2:
                    log("export alt fail " + str(e2))
            if os.path.isfile(out_png) and os.path.getsize(out_png) > 1000:
                h = hashlib.sha256(open(out_png, "rb").read()).hexdigest()
                saved.append((out_png, os.path.getsize(out_png), h))
                log("saved still " + out_png + " sha256=" + h[:16])
            else:
                log("missing/empty still " + out_png)
        except Exception as e:
            log("capture cam " + name + " " + str(e))
    return len(saved), saved

def write_manifest(out_dir, saved):
    man = os.path.join(out_dir, "MANIFEST_SHA256.txt")
    with open(man, "w", encoding="utf-8") as f:
        f.write("Skyguard AAA Loop16 stills\n")
        f.write("time=%s\n" % time.strftime("%Y-%m-%dT%H:%M:%S"))
        for path, size, h in saved:
            f.write("%s  %d  %s\n" % (h, size, path))
    log("manifest " + man)

def main():
    log("loop16 densify+durable capture start")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L16_")

    densify_environment()
    prop_ok = place_prop_spinner()
    reseed_combat()

    # lighting
    try:
        sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 2000), unreal.Rotator(-30, 45, 0))
        if sun: sun.set_actor_label("AAA_L16_Sun")
        sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 800), unreal.Rotator())
        if sky: sky.set_actor_label("AAA_L16_Sky")
        exp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.ExponentialHeightFog, unreal.Vector(0, 0, 0), unreal.Rotator())
        if exp: exp.set_actor_label("AAA_L16_Fog")
        pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 300), unreal.Rotator())
        if pp:
            pp.set_actor_label("AAA_L16_PP")
            try: pp.set_editor_property("unbound", True)
            except Exception: pass
    except Exception as e:
        log("lights " + str(e))

    out_dir = r"D:\Skyguard52\Saved\Screenshots\AAA_L16"
    count, saved = capture_with_scene_capture(out_dir)
    if saved:
        write_manifest(out_dir, saved)

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop16 densify+capture complete prop=%s stills=%d" % (prop_ok, count))
    if count > 0:
        log("CRITIC: stills on disk for blind compare; overall still likely FAIL vs AAA refs")
    else:
        log("CRITIC: densify complete but durable stills missing; overall FAIL vs AAA")

if __name__ == "__main__":
    main()
