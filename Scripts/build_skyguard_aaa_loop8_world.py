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
    clear_prefix("AAA_L8_")
    ensure_dir("/Game/Skyguard/Meshes/Hero")
    proj = unreal.Paths.project_content_dir()
    src = proj + "Skyguard/Meshes/Source/procedural/"
    names = [
        "gunner_station_proxy", "glove_arm_proxy", "shahed_heavy_proxy",
        "ruined_tower_proxy", "pier_section_proxy",
        "yak52_hd_proxy", "rifle_ads_proxy", "igla_proxy", "propeller_proxy",
        "coast_block_proxy", "apartment_midrise_proxy", "city_car_proxy",
        "harbor_crane_proxy", "container_ship_proxy", "submarine_proxy",
        "radar_truck_proxy", "rubble_cluster_proxy", "shahed_proxy",
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
    sand = mat("/Game/Skyguard/Materials/M_Tex_L7_beach2") or mat("/Game/Skyguard/Materials/M_Tex_L3_sand")
    canopy = mat("/Game/Skyguard/Materials/M_CockpitGlass")
    exhaust = mat("/Game/Skyguard/Materials/M_ExhaustGlow")
    wood = mat("/Game/Skyguard/Materials/M_Tex_L3_wood2") or plate
    plaster = mat("/Game/Skyguard/Materials/M_Tex_L7_plaster2") or brick
    floorworn = mat("/Game/Skyguard/Materials/M_Tex_L7_floorworn") or concrete

    spawn_sm(meshes.get("yak52_hd_proxy"), (0, 40, 300), (92, 92, 92), None, "AAA_L8_YakHD", air)
    spawn_sm(meshes.get("propeller_proxy"), (0, -580, 320), (100, 100, 100), None, "AAA_L8_Prop", plate)
    spawn_sm(meshes.get("gunner_station_proxy"), (0, 75, 348), (55, 55, 55), None, "AAA_L8_GunnerStation", leather)
    spawn_sm(meshes.get("rifle_ads_proxy"), (18, 120, 358), (32, 32, 32), unreal.Rotator(0, 10, 0), "AAA_L8_RifleADS", rifle_m)
    spawn_sm(meshes.get("glove_arm_proxy"), (22, 98, 352), (20, 20, 20), unreal.Rotator(10, 15, 5), "AAA_L8_GloveArm", leather)
    spawn_sm(meshes.get("igla_proxy"), (-34, 98, 350), (24, 24, 24), unreal.Rotator(0, -8, 5), "AAA_L8_Igla", rust)
    spawn_sm(unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere"), (0, -90, 376), (1.22, 1.62, 0.85), None, "AAA_L8_Canopy", canopy)

    for i in range(20):
        y = -2800 + i * 280
        spawn_sm(meshes.get("coast_block_proxy"), (-2250, y, 20), (20, 20, 17 + (i % 6)), None, "AAA_L8_CoastBlock_%d" % i, plaster if i % 2 == 0 else concrete)
        spawn_sm(meshes.get("apartment_midrise_proxy"), (-2500, y + 60, 20), (17, 17, 18 + (i % 4) * 2), None, "AAA_L8_Apt_%d" % i, concrete)
        if i % 4 == 0:
            spawn_sm(meshes.get("ruined_tower_proxy"), (-2050, y - 30, 20), (22, 22, 20 + (i % 3) * 3), None, "AAA_L8_Ruin_%d" % i, floorworn)
            spawn_sm(meshes.get("rubble_cluster_proxy"), (-1980, y, 28), (20, 20, 18), None, "AAA_L8_Rubble_%d" % i, concrete)
        spawn_sm(meshes.get("city_car_proxy"), (-1890, y + 20, 34), (17, 17, 17), unreal.Rotator(0, 90 if i % 2 else 5, 0), "AAA_L8_Car_%d" % i, plate)

    for i, y in enumerate([-1800, -900, 0, 900, 1800, 2500]):
        spawn_sm(meshes.get("pier_section_proxy"), (-560, y, 18), (28, 28, 28), None, "AAA_L8_Pier_%d" % i, wood)
        spawn_sm(meshes.get("harbor_crane_proxy"), (-340, y + 80, 18), (42, 42, 42), None, "AAA_L8_Crane_%d" % i, rust)
    spawn_sm(meshes.get("container_ship_proxy"), (980, -2000, 0), (58, 58, 58), unreal.Rotator(0, 10, 0), "AAA_L8_Ship", plate)
    spawn_sm(meshes.get("submarine_proxy"), (1850, 800, 0), (82, 82, 82), unreal.Rotator(0, 90, 0), "AAA_L8_Sub", plate)

    for i, y in enumerate([-1700, -500, 700, 1700]):
        spawn_sm(meshes.get("radar_truck_proxy"), (-1480, y, 30), (24, 24, 24), unreal.Rotator(0, 25 * i, 0), "AAA_L8_Radar_%d" % i, rust)

    cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    for i, y in enumerate(range(-3200, 3201, 150)):
        spawn_sm(cube, (-1020, y, 14), (9.5, 7.2, 0.22), None, "AAA_L8_Beach_%d" % i, sand)
        spawn_sm(cube, (-1890, y, 34.1), (4.5, 7.2, 0.03), None, "AAA_L8_WetRoad_%d" % i, wet)

    for lane, y in enumerate([-2400, -1200, 0, 1200, 2400]):
        for n in range(8):
            x = 2480 + n * 420 + (lane % 2) * 160
            z = 360 + (n % 5) * 50
            heavy = (n % 3 == 0)
            mesh = meshes.get("shahed_heavy_proxy") if heavy else meshes.get("shahed_proxy")
            sc = 42 if heavy else 32
            spawn_sm(mesh, (x, y, z), (sc, sc, sc), unreal.Rotator(0, 180, 0), "AAA_L8_Drone_%d_%d" % (lane, n), plate)
            spawn_sm(unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere"), (x + 95, y, z), (0.3, 0.3, 0.3), None, "AAA_L8_DroneEx_%d_%d" % (lane, n), exhaust)

    for name, loc, rot in [
        ("AAA_Cam_L8_Cockpit", (30, 112, 372), (-7, 8, 0)),
        ("AAA_Cam_L8_ADS", (18, 138, 366), (-1, 8, 0)),
        ("AAA_Cam_L8_GunnerStation", (8, 70, 360), (-8, 5, 0)),
        ("AAA_Cam_L8_Glove", (26, 105, 356), (-4, 22, 0)),
        ("AAA_Cam_L8_CityRuin", (-2000, 0, 140), (-8, 0, 0)),
        ("AAA_Cam_L8_HarborPier", (-500, -1000, 120), (-6, 40, 0)),
        ("AAA_Cam_L8_Swarm", (3400, 0, 760), (-16, -180, 0)),
        ("AAA_Cam_L8_YakBeauty", (650, -1150, 540), (-12, 145, 0)),
        ("AAA_Cam_L8_Ocean", (1300, -1600, 280), (-10, 45, 0)),
    ]:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)

    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(20, 105, 360), unreal.Rotator())
    if ps:
        ps.set_actor_label("AAA_L8_PlayerStart")

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop8 world densification complete")
    log("CRITIC EXPECTED: still FAIL vs AAA")

if __name__ == "__main__":
    main()
