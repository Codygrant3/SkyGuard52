import unreal

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
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.EditorAssetLibrary.load_asset(full)
    for a in unreal.EditorAssetLibrary.list_assets(dest_path, True, False):
        if dest_name.lower() in a.lower():
            return unreal.EditorAssetLibrary.load_asset(a)
    log("import failed " + src_abs)
    return None

def mat(path):
    return unreal.EditorAssetLibrary.load_asset(path)

def spawn_sm(mesh_asset, loc, scale=None, rot=None, label=None, material=None):
    if not mesh_asset:
        return None
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
    clear_prefix("AAA_L6_")
    ensure_dir("/Game/Skyguard/Meshes/Hero")
    proj = unreal.Paths.project_content_dir()
    src = proj + "Skyguard/Meshes/Source/procedural/"
    names = [
        "glove_hand_proxy", "cockpit_tub_proxy", "city_car_proxy",
        "apartment_midrise_proxy", "propeller_proxy", "container_ship_proxy",
        "yak52_proxy", "rifle_irons_proxy", "igla_proxy", "shahed_proxy",
        "harbor_crane_proxy", "submarine_proxy", "facade_tower_proxy",
    ]
    meshes = {}
    for n in names:
        meshes[n] = import_obj(src + n + ".obj", "/Game/Skyguard/Meshes/Hero", n)
        log("mesh " + n + " => " + str(bool(meshes[n])))

    air = mat("/Game/Skyguard/Materials/M_Tex_airframe_metal") or mat("/Game/Skyguard/Materials/M_Tex_L3_plate")
    plate = mat("/Game/Skyguard/Materials/M_Tex_L3_plate")
    rust = mat("/Game/Skyguard/Materials/M_Tex_L4_rust") or plate
    concrete = mat("/Game/Skyguard/Materials/M_Tex_L4_concrete8") or mat("/Game/Skyguard/Materials/M_Tex_concrete")
    brick = mat("/Game/Skyguard/Materials/M_Tex_brick") or concrete
    leather = mat("/Game/Skyguard/Materials/M_Tex_leather")
    rifle_m = mat("/Game/Skyguard/Materials/M_RifleTan") or plate
    wet = mat("/Game/Skyguard/Materials/M_L5_WetAsphalt")
    canopy = mat("/Game/Skyguard/Materials/M_CockpitGlass")
    exhaust = mat("/Game/Skyguard/Materials/M_ExhaustGlow")

    # Hero yak + spinning prop + cockpit tub
    spawn_sm(meshes.get("yak52_proxy"), (0, 40, 300), (85, 85, 85), None, "AAA_L6_HeroYak", air)
    spawn_sm(meshes.get("propeller_proxy"), (0, -560, 320), (90, 90, 90), unreal.Rotator(0, 0, 0), "AAA_L6_Propeller", plate)
    spawn_sm(meshes.get("cockpit_tub_proxy"), (0, 70, 348), (55, 55, 55), None, "AAA_L6_CockpitTub", leather)
    spawn_sm(meshes.get("rifle_irons_proxy"), (18, 115, 358), (28, 28, 28), unreal.Rotator(0, 10, 0), "AAA_L6_Rifle", rifle_m)
    spawn_sm(meshes.get("glove_hand_proxy"), (22, 95, 352), (18, 18, 18), unreal.Rotator(0, 20, 10), "AAA_L6_GloveHand", leather)
    spawn_sm(meshes.get("igla_proxy"), (-34, 95, 350), (22, 22, 22), unreal.Rotator(0, -8, 5), "AAA_L6_Igla", rust)
    spawn_sm(unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere"), (0, -85, 376), (1.15, 1.55, 0.8), None, "AAA_L6_CanopyGlass", canopy)

    # City apartments + cars (replace pure cube street read)
    for i in range(16):
        y = -2400 + i * 300
        spawn_sm(meshes.get("apartment_midrise_proxy"), (-2150, y, 20), (22, 22, 22 + (i % 4) * 3), None, "AAA_L6_Apt_%d" % i, concrete if i % 2 == 0 else brick)
        spawn_sm(meshes.get("city_car_proxy"), (-1885, y + 40, 34), (18, 18, 18), unreal.Rotator(0, 90 if i % 2 else 0, 0), "AAA_L6_Car_%d" % i, plate)
        if i % 2 == 0:
            spawn_sm(meshes.get("city_car_proxy"), (-1870, y - 60, 34), (17, 17, 17), unreal.Rotator(0, -20, 0), "AAA_L6_CarB_%d" % i, rust)

    # Harbor cranes + container ship
    for i, y in enumerate([-1400, -500, 400, 1300, 2100]):
        spawn_sm(meshes.get("harbor_crane_proxy"), (-380, y, 18), (38, 38, 38), None, "AAA_L6_Crane_%d" % i, rust)
    spawn_sm(meshes.get("container_ship_proxy"), (900, -1800, 0), (50, 50, 50), unreal.Rotator(0, 15, 0), "AAA_L6_Ship", plate)
    spawn_sm(meshes.get("submarine_proxy"), (1750, 700, 0), (75, 75, 75), unreal.Rotator(0, 90, 0), "AAA_L6_Sub", plate)

    # Drone swarm
    for lane, y in enumerate([-2200, -1100, 0, 1100, 2200]):
        for n in range(7):
            x = 2550 + n * 460 + (lane % 2) * 140
            z = 370 + (n % 5) * 45
            sc = 38 if n % 4 == 0 else 30
            spawn_sm(meshes.get("shahed_proxy"), (x, y, z), (sc, sc, sc), unreal.Rotator(0, 180, 0), "AAA_L6_Drone_%d_%d" % (lane, n), plate)
            spawn_sm(unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere"), (x + 80, y, z), (0.25, 0.25, 0.25), None, "AAA_L6_DroneEx_%d_%d" % (lane, n), exhaust)

    # Wet road strip continuity
    cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    for i, y in enumerate(range(-2500, 2501, 180)):
        spawn_sm(cube, (-1890, y, 34.15), (4.3, 8.5, 0.035), None, "AAA_L6_WetRoad_%d" % i, wet)

    # Cinematic cameras for critic
    for name, loc, rot in [
        ("AAA_Cam_L6_Cockpit", (30, 108, 372), (-7, 8, 0)),
        ("AAA_Cam_L6_ADS", (18, 132, 366), (-1, 8, 0)),
        ("AAA_Cam_L6_Glove", (24, 100, 355), (-5, 25, 0)),
        ("AAA_Cam_L6_CityStreet", (-1950, 0, 90), (-6, 5, 0)),
        ("AAA_Cam_L6_HarborShip", (600, -1500, 220), (-8, 30, 0)),
        ("AAA_Cam_L6_Swarm", (3200, 0, 720), (-15, -180, 0)),
        ("AAA_Cam_L6_YakBeauty", (550, -1000, 500), (-10, 140, 0)),
    ]:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)

    # Player start at gunner
    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(20, 100, 360), unreal.Rotator())
    if ps:
        ps.set_actor_label("AAA_L6_PlayerStart")

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop6 world hero densification complete")
    log("CRITIC EXPECTED: still FAIL vs AAA (proxy heroes, empty Niagara, no Fab kits)")

if __name__ == "__main__":
    main()
