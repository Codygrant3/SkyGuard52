import unreal
from pathlib import Path

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

def import_obj(src_abs, dest_path, dest_name):
    full = dest_path + "/" + dest_name
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.EditorAssetLibrary.load_asset(full)
    task = unreal.AssetImportTask()
    task.filename = src_abs
    task.destination_path = dest_path
    task.destination_name = dest_name
    task.automated = True
    task.save = True
    task.replace_existing = True
    # Static mesh import data
    try:
        options = unreal.FbxImportUI()
        # For OBJ, Interchange/automator may ignore; still set automated
        task.options = options
    except Exception:
        pass
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.EditorAssetLibrary.load_asset(full)
    # search imported
    for a in unreal.EditorAssetLibrary.list_assets(dest_path, True, False):
        if dest_name.lower() in a.lower() or Path(src_abs).stem.lower() in a.lower():
            return unreal.EditorAssetLibrary.load_asset(a)
    log("import failed " + src_abs)
    return None

def mat(path):
    return unreal.EditorAssetLibrary.load_asset(path)

def spawn_sm(mesh_asset, loc, scale=None, rot=None, label=None, material=None):
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc), rot or unreal.Rotator())
    if not a:
        return None
    c = a.static_mesh_component
    c.set_static_mesh(mesh_asset)
    if scale:
        a.set_actor_scale3d(unreal.Vector(*scale))
    if label:
        a.set_actor_label(label)
    if material:
        try:
            c.set_material(0, material)
        except Exception:
            pass
    return a

def main():
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L5_")
    ensure_dir("/Game/Skyguard/Meshes/Hero")
    proj = unreal.Paths.project_content_dir()
    src_dir = proj + "Skyguard/Meshes/Source/procedural/"
    names = [
        "yak52_proxy",
        "shahed_proxy",
        "rifle_irons_proxy",
        "igla_proxy",
        "facade_tower_proxy",
        "harbor_crane_proxy",
        "submarine_proxy",
    ]
    meshes = {}
    for n in names:
        src = src_dir + n + ".obj"
        meshes[n] = import_obj(src, "/Game/Skyguard/Meshes/Hero", n)
        log("mesh " + n + " => " + str(meshes[n]))

    air = mat("/Game/Skyguard/Materials/M_Tex_airframe_metal") or mat("/Game/Skyguard/Materials/M_Tex_L3_plate")
    plate = mat("/Game/Skyguard/Materials/M_Tex_L3_plate") or air
    rust = mat("/Game/Skyguard/Materials/M_Tex_L4_rust") or plate
    concrete = mat("/Game/Skyguard/Materials/M_Tex_L4_concrete8") or mat("/Game/Skyguard/Materials/M_Tex_concrete")
    rifle_m = mat("/Game/Skyguard/Materials/M_RifleTan") or plate
    leather = mat("/Game/Skyguard/Materials/M_Tex_leather")
    canopy = mat("/Game/Skyguard/Materials/M_CockpitGlass")
    exhaust = mat("/Game/Skyguard/Materials/M_ExhaustGlow")

    # Place hero Yak centered at existing flight path
    if meshes.get("yak52_proxy"):
        spawn_sm(meshes["yak52_proxy"], (0, 40, 300), (80, 80, 80), unreal.Rotator(0, 0, 0), "AAA_L5_HeroYak", air)
    # Rifle near gunner seat
    if meshes.get("rifle_irons_proxy"):
        spawn_sm(meshes["rifle_irons_proxy"], (18, 110, 358), (25, 25, 25), unreal.Rotator(0, 10, 0), "AAA_L5_HeroRifle", rifle_m)
    if meshes.get("igla_proxy"):
        spawn_sm(meshes["igla_proxy"], (-32, 90, 350), (20, 20, 20), unreal.Rotator(0, -8, 5), "AAA_L5_HeroIgla", rust)
    # Harbor cranes
    if meshes.get("harbor_crane_proxy"):
        for i, y in enumerate([-1200, -400, 400, 1200, 2000]):
            spawn_sm(meshes["harbor_crane_proxy"], (-420, y, 20), (35, 35, 35), None, "AAA_L5_HeroCrane_%d" % i, rust)
    # Sub
    if meshes.get("submarine_proxy"):
        spawn_sm(meshes["submarine_proxy"], (1750, 650, 0), (70, 70, 70), unreal.Rotator(0, 90, 0), "AAA_L5_HeroSub", plate)
    # Facade towers replace some graybox reads
    if meshes.get("facade_tower_proxy"):
        idx = 0
        for i in range(10):
            for j in range(4):
                x = -2300 - j * 120
                y = -2000 + i * 400
                spawn_sm(meshes["facade_tower_proxy"], (x, y, 20), (25, 25, 25 + (i+j)%3 * 5), None, "AAA_L5_HeroFacade_%d" % idx, concrete)
                idx += 1
    # Shahed swarm using imported mesh
    if meshes.get("shahed_proxy"):
        for lane, y in enumerate([-2000, -1000, 0, 1000, 2000]):
            for n in range(6):
                x = 2600 + n * 450 + (lane % 2) * 120
                z = 380 + (n % 4) * 50
                sc = 35 if n % 4 == 0 else 28
                spawn_sm(meshes["shahed_proxy"], (x, y, z), (sc, sc, sc), unreal.Rotator(0, 180, 0), "AAA_L5_HeroDrone_%d_%d" % (lane, n), plate)

    # Leather hand near rifle
    cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere")
    spawn_sm(cube, (22, 95, 352), (0.14, 0.16, 0.1), None, "AAA_L5_HandPalm", leather)
    # canopy glass bubble
    spawn_sm(unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere"), (0, -80, 375), (1.1, 1.5, 0.75), None, "AAA_L5_CanopyGlass", canopy)
    # muzzle / exhaust accents
    for i in range(12):
        spawn_sm(cube, (30 + i * 10, 150, 365), (0.1, 0.1, 0.1), None, "AAA_L5_MuzzleProxy_%d" % i, exhaust)

    # critic cameras
    for name, loc, rot in [
        ("AAA_Cam_L5_Cockpit", (28, 105, 372), (-8, 8, 0)),
        ("AAA_Cam_L5_ADS", (18, 130, 366), (-1, 8, 0)),
        ("AAA_Cam_L5_HeroYakExt", (500, -900, 480), (-10, 145, 0)),
        ("AAA_Cam_L5_City", (-2100, 0, 220), (-8, 0, 0)),
        ("AAA_Cam_L5_Harbor", (-350, -900, 250), (-10, 30, 0)),
        ("AAA_Cam_L5_Swarm", (3100, 100, 700), (-14, -180, 0)),
    ]:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop5 hero proxy import/place complete")
    log("CRITIC EXPECTED: still FAIL vs AAA until true Fab hero assets and authored Niagara")

if __name__ == "__main__":
    main()
