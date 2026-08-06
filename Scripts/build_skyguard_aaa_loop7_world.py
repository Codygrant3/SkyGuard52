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
    clear_prefix("AAA_L7_")
    ensure_dir("/Game/Skyguard/Meshes/Hero")
    proj = unreal.Paths.project_content_dir()
    src = proj + "Skyguard/Meshes/Source/procedural/"
    names = [
        "yak52_hd_proxy", "rifle_ads_proxy", "coast_block_proxy",
        "radar_truck_proxy", "rubble_cluster_proxy",
        "glove_hand_proxy", "cockpit_tub_proxy", "propeller_proxy",
        "city_car_proxy", "apartment_midrise_proxy", "container_ship_proxy",
        "harbor_crane_proxy", "submarine_proxy", "shahed_proxy", "igla_proxy",
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
    sand = mat("/Game/Skyguard/Materials/M_Tex_L3_sand")
    canopy = mat("/Game/Skyguard/Materials/M_CockpitGlass")
    exhaust = mat("/Game/Skyguard/Materials/M_ExhaustGlow")
    roof = mat("/Game/Skyguard/Materials/M_Tex_L3_roof")

    # HD Yak + prop + cockpit + ADS rifle + glove
    spawn_sm(meshes.get("yak52_hd_proxy"), (0, 40, 300), (90, 90, 90), None, "AAA_L7_HeroYakHD", air)
    spawn_sm(meshes.get("propeller_proxy"), (0, -575, 320), (95, 95, 95), None, "AAA_L7_Prop", plate)
    spawn_sm(meshes.get("cockpit_tub_proxy"), (0, 72, 348), (58, 58, 58), None, "AAA_L7_CockpitTub", leather)
    spawn_sm(meshes.get("rifle_ads_proxy"), (18, 118, 358), (30, 30, 30), unreal.Rotator(0, 10, 0), "AAA_L7_RifleADS", rifle_m)
    spawn_sm(meshes.get("glove_hand_proxy"), (22, 96, 352), (20, 20, 20), unreal.Rotator(0, 18, 8), "AAA_L7_Glove", leather)
    spawn_sm(meshes.get("igla_proxy"), (-34, 96, 350), (24, 24, 24), unreal.Rotator(0, -8, 5), "AAA_L7_Igla", rust)
    spawn_sm(unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere"), (0, -88, 376), (1.2, 1.6, 0.82), None, "AAA_L7_Canopy", canopy)

    # Coastal blocks denser
    for i in range(18):
        y = -2600 + i * 300
        spawn_sm(meshes.get("coast_block_proxy"), (-2200, y, 20), (20, 20, 18 + (i % 5)), None, "AAA_L7_CoastBlock_%d" % i, concrete if i % 2 == 0 else brick)
        spawn_sm(meshes.get("apartment_midrise_proxy"), (-2450, y + 80, 20), (18, 18, 20 + (i % 3) * 2), None, "AAA_L7_Apt_%d" % i, concrete)
        spawn_sm(meshes.get("city_car_proxy"), (-1890, y + 30, 34), (17, 17, 17), unreal.Rotator(0, 90 if i % 2 else 0, 0), "AAA_L7_Car_%d" % i, plate)
        if i % 3 == 0:
            spawn_sm(meshes.get("rubble_cluster_proxy"), (-2000, y - 40, 30), (18, 18, 18), None, "AAA_L7_Rubble_%d" % i, concrete)

    # AAA radar sites / SAM-ish ground props
    for i, y in enumerate([-1600, -400, 800, 1800]):
        spawn_sm(meshes.get("radar_truck_proxy"), (-1500, y, 30), (22, 22, 22), unreal.Rotator(0, 20 * i, 0), "AAA_L7_Radar_%d" % i, rust)

    # Harbor
    for i, y in enumerate([-1500, -600, 300, 1200, 2000]):
        spawn_sm(meshes.get("harbor_crane_proxy"), (-360, y, 18), (40, 40, 40), None, "AAA_L7_Crane_%d" % i, rust)
    spawn_sm(meshes.get("container_ship_proxy"), (950, -1900, 0), (55, 55, 55), unreal.Rotator(0, 12, 0), "AAA_L7_Ship", plate)
    spawn_sm(meshes.get("submarine_proxy"), (1800, 750, 0), (80, 80, 80), unreal.Rotator(0, 90, 0), "AAA_L7_Sub", plate)

    # Beach sand cards
    cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    for i, y in enumerate(range(-3000, 3001, 160)):
        spawn_sm(cube, (-1020, y, 14), (9, 7.5, 0.22), None, "AAA_L7_Beach_%d" % i, sand)
        spawn_sm(cube, (-1890, y, 34.12), (4.4, 7.5, 0.03), None, "AAA_L7_WetRoad_%d" % i, wet)

    # Swarm
    for lane, y in enumerate([-2300, -1150, 0, 1150, 2300]):
        for n in range(8):
            x = 2500 + n * 430 + (lane % 2) * 150
            z = 365 + (n % 5) * 48
            sc = 40 if n % 4 == 0 else 31
            spawn_sm(meshes.get("shahed_proxy"), (x, y, z), (sc, sc, sc), unreal.Rotator(0, 180, 0), "AAA_L7_Drone_%d_%d" % (lane, n), plate)
            spawn_sm(unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere"), (x + 90, y, z), (0.28, 0.28, 0.28), None, "AAA_L7_DroneEx_%d_%d" % (lane, n), exhaust)

    # Critic cameras
    for name, loc, rot in [
        ("AAA_Cam_L7_Cockpit", (30, 110, 372), (-7, 8, 0)),
        ("AAA_Cam_L7_ADS", (18, 135, 366), (-1, 8, 0)),
        ("AAA_Cam_L7_GloveRifle", (25, 105, 356), (-4, 20, 0)),
        ("AAA_Cam_L7_CityStreet", (-1960, 50, 85), (-5, 0, 0)),
        ("AAA_Cam_L7_Harbor", (-300, -1200, 240), (-10, 35, 0)),
        ("AAA_Cam_L7_Swarm", (3300, 0, 740), (-15, -180, 0)),
        ("AAA_Cam_L7_YakBeauty", (600, -1100, 520), (-11, 142, 0)),
        ("AAA_Cam_L7_RadarSite", (-1400, -400, 120), (-8, -10, 0)),
    ]:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)

    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(20, 102, 360), unreal.Rotator())
    if ps:
        ps.set_actor_label("AAA_L7_PlayerStart")

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop7 world HD densification complete")
    log("CRITIC EXPECTED: still FAIL vs AAA (proxies not Fab hero kits; Niagara unauthored)")

if __name__ == "__main__":
    main()
