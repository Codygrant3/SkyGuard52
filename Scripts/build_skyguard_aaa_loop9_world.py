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
    clear_prefix("AAA_L9_")
    ensure_dir("/Game/Skyguard/Meshes/Hero")
    proj = unreal.Paths.project_content_dir()
    src = proj + "Skyguard/Meshes/Source/procedural/"
    names = [
        "gunner_pov_kit", "street_lamp_proxy", "coast_tree_proxy", "freighter_proxy", "flak_emplacement_proxy",
        "yak52_hd_proxy", "rifle_ads_proxy", "glove_arm_proxy", "gunner_station_proxy", "igla_proxy", "propeller_proxy",
        "coast_block_proxy", "apartment_midrise_proxy", "city_car_proxy", "ruined_tower_proxy", "rubble_cluster_proxy",
        "pier_section_proxy", "harbor_crane_proxy", "container_ship_proxy", "submarine_proxy", "radar_truck_proxy",
        "shahed_proxy", "shahed_heavy_proxy",
    ]
    meshes = {}
    for n in names:
        meshes[n] = import_obj(src + n + ".obj", "/Game/Skyguard/Meshes/Hero", n)
        log("mesh " + n + " => " + str(bool(meshes[n])))

    air = mat("/Game/Skyguard/Materials/M_Tex_L8_plate2") or mat("/Game/Skyguard/Materials/M_Tex_airframe_metal")
    plate = mat("/Game/Skyguard/Materials/M_Tex_L8_plate2") or mat("/Game/Skyguard/Materials/M_Tex_L3_plate")
    rust = mat("/Game/Skyguard/Materials/M_Tex_L8_corrugated") or mat("/Game/Skyguard/Materials/M_Tex_L4_rust")
    concrete = mat("/Game/Skyguard/Materials/M_Tex_L4_concrete8")
    plaster = mat("/Game/Skyguard/Materials/M_Tex_L8_plaster2") or mat("/Game/Skyguard/Materials/M_Tex_L7_plaster2")
    leather = mat("/Game/Skyguard/Materials/M_Tex_leather")
    rifle_m = mat("/Game/Skyguard/Materials/M_RifleTan") or plate
    wet = mat("/Game/Skyguard/Materials/M_L5_WetAsphalt")
    sand = mat("/Game/Skyguard/Materials/M_Tex_L8_beach2") or mat("/Game/Skyguard/Materials/M_Tex_L7_beach2")
    floorworn = mat("/Game/Skyguard/Materials/M_Tex_L8_floorworn") or mat("/Game/Skyguard/Materials/M_Tex_L7_floorworn")
    canopy = mat("/Game/Skyguard/Materials/M_CockpitGlass")
    exhaust = mat("/Game/Skyguard/Materials/M_ExhaustGlow")
    wood = mat("/Game/Skyguard/Materials/M_Tex_L3_wood2")
    foliage = mat("/Game/Skyguard/Materials/M_Foliage")

    # Cockpit / aircraft fidelity centerpiece
    spawn_sm(meshes.get("yak52_hd_proxy"), (0, 40, 300), (95, 95, 95), None, "AAA_L9_YakHD", air)
    spawn_sm(meshes.get("propeller_proxy"), (0, -585, 320), (105, 105, 105), None, "AAA_L9_Prop", plate)
    spawn_sm(meshes.get("gunner_pov_kit"), (0, 78, 348), (52, 52, 52), None, "AAA_L9_GunnerPOV", leather)
    spawn_sm(meshes.get("rifle_ads_proxy"), (18, 122, 358), (34, 34, 34), unreal.Rotator(0, 10, 0), "AAA_L9_RifleADS", rifle_m)
    spawn_sm(meshes.get("glove_arm_proxy"), (22, 100, 352), (22, 22, 22), unreal.Rotator(8, 16, 4), "AAA_L9_GloveArm", leather)
    spawn_sm(meshes.get("igla_proxy"), (-34, 100, 350), (25, 25, 25), unreal.Rotator(0, -8, 5), "AAA_L9_Igla", rust)
    spawn_sm(unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere"), (0, -92, 376), (1.25, 1.65, 0.88), None, "AAA_L9_Canopy", canopy)

    # City densify with street furniture
    for i in range(22):
        y = -3000 + i * 270
        spawn_sm(meshes.get("coast_block_proxy"), (-2280, y, 20), (21, 21, 16 + (i % 7)), None, "AAA_L9_CoastBlock_%d" % i, plaster if i % 2 == 0 else concrete)
        spawn_sm(meshes.get("apartment_midrise_proxy"), (-2550, y + 50, 20), (18, 18, 18 + (i % 5) * 2), None, "AAA_L9_Apt_%d" % i, concrete)
        if i % 3 == 0:
            spawn_sm(meshes.get("ruined_tower_proxy"), (-2080, y - 40, 20), (23, 23, 20 + (i % 4) * 2), None, "AAA_L9_Ruin_%d" % i, floorworn)
            spawn_sm(meshes.get("rubble_cluster_proxy"), (-2000, y, 28), (20, 20, 18), None, "AAA_L9_Rubble_%d" % i, concrete)
        spawn_sm(meshes.get("city_car_proxy"), (-1890, y + 15, 34), (17, 17, 17), unreal.Rotator(0, 90 if i % 2 else 0, 0), "AAA_L9_Car_%d" % i, plate)
        spawn_sm(meshes.get("street_lamp_proxy"), (-1855, y + 60, 34), (20, 20, 20), None, "AAA_L9_Lamp_%d" % i, plate)
        if i % 2 == 0:
            spawn_sm(meshes.get("coast_tree_proxy"), (-1960, y - 50, 34), (18, 18, 18), None, "AAA_L9_Tree_%d" % i, foliage)

    # Harbor / ocean military set dressing
    for i, y in enumerate([-2000, -1000, 0, 1000, 2000, 2800]):
        spawn_sm(meshes.get("pier_section_proxy"), (-560, y, 18), (30, 30, 30), None, "AAA_L9_Pier_%d" % i, wood)
        spawn_sm(meshes.get("harbor_crane_proxy"), (-320, y + 90, 18), (44, 44, 44), None, "AAA_L9_Crane_%d" % i, rust)
        if i % 2 == 0:
            spawn_sm(meshes.get("flak_emplacement_proxy"), (-1200, y, 32), (18, 18, 18), unreal.Rotator(0, 15 * i, 0), "AAA_L9_Flak_%d" % i, rust)
    spawn_sm(meshes.get("freighter_proxy"), (1100, -2100, 0), (45, 45, 45), unreal.Rotator(0, 12, 0), "AAA_L9_Freighter", plate)
    spawn_sm(meshes.get("container_ship_proxy"), (900, -1400, 0), (50, 50, 50), unreal.Rotator(0, -8, 0), "AAA_L9_Ship", plate)
    spawn_sm(meshes.get("submarine_proxy"), (1900, 850, 0), (85, 85, 85), unreal.Rotator(0, 90, 0), "AAA_L9_Sub", plate)
    for i, y in enumerate([-1600, -400, 800, 1800]):
        spawn_sm(meshes.get("radar_truck_proxy"), (-1500, y, 30), (24, 24, 24), unreal.Rotator(0, 20 * i, 0), "AAA_L9_Radar_%d" % i, rust)

    # Beach / wet road continuous
    cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    for i, y in enumerate(range(-3400, 3401, 140)):
        spawn_sm(cube, (-1020, y, 14), (10, 6.8, 0.22), None, "AAA_L9_Beach_%d" % i, sand)
        spawn_sm(cube, (-1890, y, 34.08), (4.6, 6.8, 0.03), None, "AAA_L9_WetRoad_%d" % i, wet)

    # Drone swarm heavy/light denser
    for lane, y in enumerate([-2500, -1250, 0, 1250, 2500]):
        for n in range(9):
            x = 2450 + n * 400 + (lane % 2) * 170
            z = 355 + (n % 5) * 52
            heavy = (n % 3 == 0)
            mesh = meshes.get("shahed_heavy_proxy") if heavy else meshes.get("shahed_proxy")
            sc = 44 if heavy else 33
            spawn_sm(mesh, (x, y, z), (sc, sc, sc), unreal.Rotator(0, 180, 0), "AAA_L9_Drone_%d_%d" % (lane, n), plate)
            spawn_sm(unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere"), (x + 100, y, z), (0.32, 0.32, 0.32), None, "AAA_L9_DroneEx_%d_%d" % (lane, n), exhaust)

    # Ensure C++ combat seed actors present
    try:
        gunner_cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardGunner")
        spawner_cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardDroneSpawner")
        drone_cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardDrone")
        if gunner_cls:
            g = unreal.EditorLevelLibrary.spawn_actor_from_class(gunner_cls, unreal.Vector(20, 105, 360), unreal.Rotator())
            if g:
                g.set_actor_label("AAA_L9_CPP_Gunner")
                log("spawned cpp gunner")
        if spawner_cls:
            s = unreal.EditorLevelLibrary.spawn_actor_from_class(spawner_cls, unreal.Vector(2600, 0, 500), unreal.Rotator())
            if s:
                s.set_actor_label("AAA_L9_CPP_Spawner")
                log("spawned cpp spawner")
        if drone_cls:
            for i, y in enumerate([-600, 0, 600]):
                d = unreal.EditorLevelLibrary.spawn_actor_from_class(drone_cls, unreal.Vector(3000, y, 420 + i * 20), unreal.Rotator(0, 180, 0))
                if d:
                    d.set_actor_label("AAA_L9_CPP_Drone_%d" % i)
    except Exception as e:
        log("cpp spawn note " + str(e))

    # Critic cameras
    for name, loc, rot in [
        ("AAA_Cam_L9_Cockpit", (30, 115, 372), (-7, 8, 0)),
        ("AAA_Cam_L9_ADS", (18, 140, 366), (-1, 8, 0)),
        ("AAA_Cam_L9_Glove", (26, 108, 356), (-4, 22, 0)),
        ("AAA_Cam_L9_CityStreet", (-1950, 0, 90), (-6, 0, 0)),
        ("AAA_Cam_L9_Ruin", (-2050, -200, 160), (-10, 10, 0)),
        ("AAA_Cam_L9_Harbor", (-400, -1200, 180), (-8, 35, 0)),
        ("AAA_Cam_L9_Freighter", (900, -1800, 220), (-10, 30, 0)),
        ("AAA_Cam_L9_Swarm", (3500, 0, 780), (-16, -180, 0)),
        ("AAA_Cam_L9_YakBeauty", (700, -1200, 560), (-12, 145, 0)),
        ("AAA_Cam_L9_OceanGolden", (1500, -1700, 300), (-12, 48, 0)),
    ]:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)

    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(20, 105, 360), unreal.Rotator())
    if ps:
        ps.set_actor_label("AAA_L9_PlayerStart")

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop9 world densification complete")
    log("CRITIC EXPECTED: still FAIL vs AAA (no Fab hero kits; Niagara still thin)")

if __name__ == "__main__":
    main()
