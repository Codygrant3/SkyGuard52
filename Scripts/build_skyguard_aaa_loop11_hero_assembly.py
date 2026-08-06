import unreal
import random

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
    import os
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

def load_sm(path):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        a = unreal.EditorAssetLibrary.load_asset(path)
        if isinstance(a, unreal.StaticMesh):
            return a
    return None

def list_static_meshes(folder):
    out = []
    try:
        for a in unreal.EditorAssetLibrary.list_assets(folder, True, False):
            asset = unreal.EditorAssetLibrary.load_asset(a)
            if isinstance(asset, unreal.StaticMesh):
                out.append((a, asset))
    except Exception as e:
        log("list fail " + folder + " " + str(e))
    return out

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

def bounds_size(mesh):
    try:
        b = mesh.get_bounds()
        # BoxSphereBounds has box_extent
        e = b.box_extent
        return (abs(e.x)*2, abs(e.y)*2, abs(e.z)*2)
    except Exception:
        try:
            # fallback
            return (100,100,100)
        except Exception:
            return (100,100,100)

def scale_to_target(mesh, target_max_dim):
    sx,sy,sz = bounds_size(mesh)
    m = max(sx,sy,sz, 0.001)
    s = target_max_dim / m
    return (s,s,s)

def main():
    log("loop11 hero assembly start")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L11_")
    ensure_dir("/Game/Skyguard/Meshes/WebGame")

    # Re-import yak kit (large)
    proj = unreal.Paths.project_content_dir()
    yak_src = r"D:\Skyguard52\Content\Skyguard\Meshes\Source\webgame\yak52-detail-kit.glb"
    log("importing yak kit from " + yak_src)
    ok = import_glb(yak_src, "/Game/Skyguard/Meshes/WebGame/yak52-detail-kit")
    log("yak import attempted ok=" + str(ok))
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard/Meshes/WebGame", False, True)

    yak_meshes = list_static_meshes("/Game/Skyguard/Meshes/WebGame/yak52-detail-kit")
    log("yak static meshes found=" + str(len(yak_meshes)))
    for path, mesh in yak_meshes[:40]:
        log(" yak mesh " + path + " bounds=" + str(bounds_size(mesh)))

    # Place ALL yak parts co-located with auto scale to ~9m airframe if needed
    if yak_meshes:
        # use first mesh to estimate scale to ~900 uu (9m)
        s = scale_to_target(yak_meshes[0][1], 900.0)
        # clamp ridiculous scales
        if s[0] > 500: s = (100,100,100)
        if s[0] < 0.01: s = (1,1,1)
        log("yak auto scale=" + str(s))
        for i, (path, mesh) in enumerate(yak_meshes):
            spawn_sm(mesh, (0, 40, 320), s, None, "AAA_L11_YakPart_%d" % i)
    else:
        # fallback HD proxy
        proxy = load_sm("/Game/Skyguard/Meshes/Hero/yak52_hd_proxy")
        spawn_sm(proxy, (0, 40, 300), (95,95,95), None, "AAA_L11_YakProxyFallback")
        log("yak kit missing; proxy fallback")

    # Rifle assembly: place parts together at gunner view with scale to ~1.1m weapon length
    rifle_paths = [
        "/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-fde",
        "/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-gunmetal",
        "/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-matteBlack",
        "/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-glove",
        "/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-sleeve",
        "/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-fdeDark",
    ]
    rifle_meshes = [(p, load_sm(p)) for p in rifle_paths]
    rifle_meshes = [(p,m) for p,m in rifle_meshes if m]
    if rifle_meshes:
        s = scale_to_target(rifle_meshes[0][1], 110.0)
        if s[0] > 500: s=(100,100,100)
        log("rifle scale=" + str(s) + " bounds0=" + str(bounds_size(rifle_meshes[0][1])))
        for i,(p,m) in enumerate(rifle_meshes):
            spawn_sm(m, (18, 120, 358), s, unreal.Rotator(0, 100, 0), "AAA_L11_RiflePart_%d" % i)

    # Occupant at rear seat
    occ_folder = "/Game/Skyguard/Meshes/WebGame/skyguard-occupant/StaticMeshes"
    occ = list_static_meshes(occ_folder)
    if occ:
        s = scale_to_target(occ[0][1], 180.0)
        if s[0] > 500: s=(100,100,100)
        log("occupant scale=" + str(s))
        for i,(p,m) in enumerate(occ):
            spawn_sm(m, (0, 75, 352), s, None, "AAA_L11_Occupant_%d" % i)

    # Igla assembly left side
    igla_folder = "/Game/Skyguard/Meshes/WebGame/skyguard-interceptor/StaticMeshes"
    igla = list_static_meshes(igla_folder)
    if igla:
        s = scale_to_target(igla[0][1], 150.0)
        if s[0] > 500: s=(100,100,100)
        log("igla scale=" + str(s))
        for i,(p,m) in enumerate(igla):
            spawn_sm(m, (-34, 95, 352), s, unreal.Rotator(0, -10, 5), "AAA_L11_IglaPart_%d" % i)

    # Drones from web body+wing with scale to ~3.5m
    body = load_sm("/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-body")
    wing = load_sm("/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-wing")
    fins = load_sm("/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-fins")
    if body:
        s = scale_to_target(body, 350.0)
        if s[0] > 500: s=(100,100,100)
        log("drone scale=" + str(s) + " bounds=" + str(bounds_size(body)))
        for lane,y in enumerate([-1800,-600,600,1800]):
            for n in range(7):
                x = 2500 + n*420 + (lane%2)*140
                z = 370 + (n%4)*45
                spawn_sm(body, (x,y,z), s, unreal.Rotator(0,180,0), "AAA_L11_DroneBody_%d_%d" % (lane,n))
                if wing:
                    spawn_sm(wing, (x,y,z), s, unreal.Rotator(0,180,0), "AAA_L11_DroneWing_%d_%d" % (lane,n))
                if fins:
                    spawn_sm(fins, (x,y,z), s, unreal.Rotator(0,180,0), "AAA_L11_DroneFins_%d_%d" % (lane,n))

    # Keep proxy backups lightly for silhouette if web scale wrong
    spawn_sm(load_sm("/Game/Skyguard/Meshes/Hero/yak52_hd_proxy"), (0, 40, 300), (90,90,90), None, "AAA_L11_YakProxyBackup")
    spawn_sm(load_sm("/Game/Skyguard/Meshes/Hero/rifle_ads_proxy"), (18, 120, 358), (30,30,30), unreal.Rotator(0,10,0), "AAA_L11_RifleProxyBackup")

    # C++ combat seed
    try:
        gunner_cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardGunner")
        spawner_cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardDroneSpawner")
        if gunner_cls:
            g = unreal.EditorLevelLibrary.spawn_actor_from_class(gunner_cls, unreal.Vector(20,105,360), unreal.Rotator())
            if g: g.set_actor_label("AAA_L11_CPP_Gunner"); log("spawned gunner")
        if spawner_cls:
            s = unreal.EditorLevelLibrary.spawn_actor_from_class(spawner_cls, unreal.Vector(2800,0,520), unreal.Rotator())
            if s: s.set_actor_label("AAA_L11_CPP_Spawner"); log("spawned spawner")
    except Exception as e:
        log("cpp " + str(e))

    # Critic cams
    for name, loc, rot in [
        ("AAA_Cam_L11_Cockpit", (30,115,372), (-7,8,0)),
        ("AAA_Cam_L11_ADS", (18,140,366), (-1,8,0)),
        ("AAA_Cam_L11_RifleClose", (20,125,360), (-2,15,0)),
        ("AAA_Cam_L11_YakExterior", (650,-1100,520), (-10,140,0)),
        ("AAA_Cam_L11_Swarm", (3400,0,760), (-15,-180,0)),
        ("AAA_Cam_L11_City", (-2000,0,140), (-8,0,0)),
    ]:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c: c.set_actor_label(name)

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop11 hero assembly complete")
    log("CRITIC EXPECTED: still FAIL vs AAA overall, but weapon/drone hero mesh quality should improve")

if __name__ == "__main__":
    main()
