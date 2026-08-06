import unreal
import os

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

def capture_cam(label_prefix, out_dir):
    # Find camera actors and take highres screenshots if subsystem available
    cams = []
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        try:
            n = a.get_actor_label() or ""
            if n.startswith(label_prefix) or n.startswith("AAA_Cam_L14_") or n.startswith("AAA_Cam_L13_"):
                if isinstance(a, unreal.CameraActor):
                    cams.append((n, a))
        except Exception:
            pass
    log("cams found=" + str(len(cams)))
    os.makedirs(out_dir, exist_ok=True)
    # Set viewport to camera and screenshot
    try:
        eisl = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    except Exception:
        eisl = None
    taken = 0
    for name, cam in cams[:12]:
        try:
            # Pilot level editor camera to this camera transform
            loc = cam.get_actor_location()
            rot = cam.get_actor_rotation()
            try:
                unreal.EditorLevelLibrary.set_level_viewport_camera_info(loc, rot)
            except Exception:
                pass
            shot = os.path.join(out_dir, name + ".png")
            # Automation screenshot
            try:
                unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, shot, cam)
                log("screenshot " + shot)
                taken += 1
            except Exception as e:
                # fallback filename only note
                log("screenshot fail " + name + " " + str(e))
        except Exception as e:
            log("cam " + name + " " + str(e))
    return taken

def densify_prop_and_rivets():
    prop = load_sm("/Game/Skyguard/Meshes/Hero/propeller_proxy")
    prop_mat = load_mat("/Game/Skyguard/Materials/M_PropDisc")
    metal = load_mat("/Game/Skyguard/Materials/M_Tex_airframe_metal") or load_mat("/Game/Skyguard/Materials/M_Metal")
    sphere = load_sm("/Engine/BasicShapes/Sphere")
    cube = load_sm("/Engine/BasicShapes/Cube")
    # spinning-looking multi-blade disc stack
    for i in range(8):
        ang = i * 22.5
        spawn_sm(prop or cube, (-190, 40, 330), (0.4, 0.4, 0.05), unreal.Rotator(0, ang, 90), "AAA_L15_PropBlade_%d" % i, prop_mat or metal)
    # prop blur disc
    spawn_sm(sphere, (-195, 40, 330), (1.8, 1.8, 0.08), None, "AAA_L15_PropBlur", prop_mat)
    # rivet lines on fuselage vicinity
    for i in range(40):
        x = -80 + i * 8
        spawn_sm(sphere, (x, 20, 325), (0.04, 0.04, 0.04), None, "AAA_L15_RivetL_%d" % i, metal)
        spawn_sm(sphere, (x, 60, 325), (0.04, 0.04, 0.04), None, "AAA_L15_RivetR_%d" % i, metal)
    log("prop/rivet densify done")

def densify_harbor():
    cube = load_sm("/Engine/BasicShapes/Cube")
    cyl = load_sm("/Engine/BasicShapes/Cylinder")
    metal = load_mat("/Game/Skyguard/Materials/M_Tex_metal") or load_mat("/Game/Skyguard/Materials/M_Metal")
    wood = load_mat("/Game/Skyguard/Materials/M_PierWood") or load_mat("/Game/Skyguard/Materials/M_Tex_L3_wood2")
    rust = load_mat("/Game/Skyguard/Materials/M_MetalRust") or metal
    # cranes
    for i, y in enumerate([-1200, -400, 400, 1200]):
        spawn_sm(cube, (-900, y, 80), (1.2, 1.2, 8.0), None, "AAA_L15_CraneMast_%d" % i, rust)
        spawn_sm(cube, (-820, y, 250), (8.0, 0.4, 0.4), None, "AAA_L15_CraneBoom_%d" % i, metal)
        spawn_sm(cyl, (-700, y, 40), (0.2, 0.2, 3.0), None, "AAA_L15_CraneCable_%d" % i, metal)
    # containers
    colors = [metal, rust, wood]
    for i in range(36):
        x = -1000 - (i % 4) * 50
        y = -1400 + (i // 4) * 90
        spawn_sm(cube, (x, y, 40 + (i % 3) * 28), (1.8, 0.9, 0.9), None, "AAA_L15_Container_%d" % i, colors[i % 3])
    # ships
    for i, y in enumerate([-2000, 0, 2000]):
        spawn_sm(cube, (-400, y, 20), (18, 4, 2.5), None, "AAA_L15_ShipHull_%d" % i, rust)
        spawn_sm(cube, (-300, y, 70), (6, 3, 2), None, "AAA_L15_ShipSuper_%d" % i, metal)
    log("harbor densify done")

def main():
    log("loop15 critic capture + densify start")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L15_")
    densify_prop_and_rivets()
    densify_harbor()

    # more critic cams
    for name, loc, rot in [
        ("AAA_Cam_L15_YakBeauty", (650, -1100, 540), (-12, 145, 0)),
        ("AAA_Cam_L15_Cockpit", (28, 112, 370), (-6, 8, 0)),
        ("AAA_Cam_L15_ADS", (16, 138, 365), (-1, 8, 0)),
        ("AAA_Cam_L15_OceanWide", (1800, -900, 520), (-12, 170, 0)),
        ("AAA_Cam_L15_Harbor", (-700, -1500, 260), (-8, 40, 0)),
        ("AAA_Cam_L15_City", (-1200, -800, 420), (-10, 25, 0)),
        ("AAA_Cam_L15_CombatLane", (1000, 100, 450), (-8, 185, 0)),
    ]:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)

    out_dir = r"D:\Skyguard52\Saved\Screenshots\AAA_L15"
    taken = capture_cam("AAA_Cam_L15_", out_dir)

    # reseed combat
    try:
        gunner_cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardGunner")
        spawner_cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardDroneSpawner")
        if gunner_cls:
            g = unreal.EditorLevelLibrary.spawn_actor_from_class(gunner_cls, unreal.Vector(20, 105, 360), unreal.Rotator())
            if g: g.set_actor_label("AAA_L15_CPP_Gunner")
        if spawner_cls:
            s = unreal.EditorLevelLibrary.spawn_actor_from_class(spawner_cls, unreal.Vector(2800, 0, 520), unreal.Rotator())
            if s: s.set_actor_label("AAA_L15_CPP_Spawner")
    except Exception as e:
        log("cpp " + str(e))

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop15 densify+capture complete screenshots=%d" % taken)
    log("CRITIC: still FAIL vs AAA; harbor/prop densify help partial pillars only")

if __name__ == "__main__":
    main()
