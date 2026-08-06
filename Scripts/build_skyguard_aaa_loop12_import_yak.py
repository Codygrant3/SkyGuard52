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

def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)

def import_glb(src_abs, dest_path):
    if not os.path.isfile(src_abs):
        log("missing " + src_abs)
        return False
    task = unreal.AssetImportTask()
    task.filename = src_abs
    task.destination_path = dest_path
    task.automated = True
    task.save = True
    task.replace_existing = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    return True

def list_static_meshes(folder):
    out = []
    try:
        for a in unreal.EditorAssetLibrary.list_assets(folder, True, False):
            asset = unreal.EditorAssetLibrary.load_asset(a)
            if isinstance(asset, unreal.StaticMesh):
                out.append((a, asset))
    except Exception as e:
        log("list fail " + str(e))
    return out

def bounds_size(mesh):
    try:
        b = mesh.get_bounds()
        e = b.box_extent
        return (abs(e.x)*2, abs(e.y)*2, abs(e.z)*2)
    except Exception:
        return (100,100,100)

def scale_to_target(mesh, target_max_dim):
    sx,sy,sz = bounds_size(mesh)
    m = max(sx,sy,sz, 0.001)
    s = target_max_dim / m
    return (s,s,s)

def spawn_sm(mesh, loc, scale=(1,1,1), rot=None, label=None):
    if not mesh:
        return None
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc), rot or unreal.Rotator())
    if not a:
        return None
    a.static_mesh_component.set_static_mesh(mesh)
    a.set_actor_scale3d(unreal.Vector(*scale))
    if label:
        a.set_actor_label(label)
    return a

def main():
    log("loop12 yak import start")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L12_")
    ensure_dir("/Game/Skyguard/Meshes/WebGame/yak52-detail-kit")

    src = r"D:\Skyguard52\Content\Skyguard\Meshes\Source\webgame\yak52-detail-kit-blender.glb"
    log("importing " + src)
    import_glb(src, "/Game/Skyguard/Meshes/WebGame/yak52-detail-kit")
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard/Meshes/WebGame", False, True)

    meshes = list_static_meshes("/Game/Skyguard/Meshes/WebGame/yak52-detail-kit")
    log("yak static meshes=" + str(len(meshes)))
    for path, mesh in meshes[:50]:
        log(" mesh " + path + " bounds=" + str(bounds_size(mesh)))

    if not meshes:
        log("NO YAK MESHES IMPORTED")
        # keep proxy
        proxy = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Meshes/Hero/yak52_hd_proxy")
        spawn_sm(proxy, (0,40,300), (95,95,95), None, "AAA_L12_YakProxyFallback")
    else:
        # scale largest dimension of first mesh / or median
        s = scale_to_target(meshes[0][1], 950.0)
        if s[0] > 500: s = (100,100,100)
        if s[0] < 0.01: s = (1,1,1)
        log("yak auto scale=" + str(s))
        # Place all parts at aircraft origin
        for i, (path, mesh) in enumerate(meshes):
            name = path.split("/")[-1]
            spawn_sm(mesh, (0, 40, 320), s, None, "AAA_L12_YakPart_%03d_%s" % (i, name[:40]))

    # Critic cams focused on aircraft
    for name, loc, rot in [
        ("AAA_Cam_L12_YakBeauty", (700, -1200, 560), (-12, 145, 0)),
        ("AAA_Cam_L12_YakCockpitExt", (120, 200, 380), (-8, 200, 0)),
        ("AAA_Cam_L12_YakNose", (-200, -500, 340), (-5, 30, 0)),
        ("AAA_Cam_L12_Cockpit", (30, 115, 372), (-7, 8, 0)),
        ("AAA_Cam_L12_ADS", (18, 140, 366), (-1, 8, 0)),
    ]:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)

    # reseed cpp gunner
    try:
        gunner_cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardGunner")
        spawner_cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardDroneSpawner")
        if gunner_cls:
            g = unreal.EditorLevelLibrary.spawn_actor_from_class(gunner_cls, unreal.Vector(20,105,360), unreal.Rotator())
            if g: g.set_actor_label("AAA_L12_CPP_Gunner")
        if spawner_cls:
            s = unreal.EditorLevelLibrary.spawn_actor_from_class(spawner_cls, unreal.Vector(2800,0,520), unreal.Rotator())
            if s: s.set_actor_label("AAA_L12_CPP_Spawner")
    except Exception as e:
        log("cpp " + str(e))

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop12 yak import/place complete count=" + str(len(meshes)))
    log("CRITIC: aircraft pillar may improve if kit imported; overall still FAIL vs AAA")

if __name__ == "__main__":
    main()
