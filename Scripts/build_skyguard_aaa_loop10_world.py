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

def mat(path):
    return unreal.EditorAssetLibrary.load_asset(path)

def load_any(paths):
    for p in paths:
        if unreal.EditorAssetLibrary.does_asset_exist(p):
            return unreal.EditorAssetLibrary.load_asset(p)
        # try without extension variants
    # search parent folder
    for p in paths:
        folder = "/".join(p.split("/")[:-1])
        name = p.split("/")[-1].lower()
        try:
            for a in unreal.EditorAssetLibrary.list_assets(folder, True, False):
                if name in a.lower():
                    return unreal.EditorAssetLibrary.load_asset(a)
        except Exception:
            pass
    return None

def spawn_sm(mesh_asset, loc, scale=None, rot=None, label=None, material=None):
    if not mesh_asset:
        return None
    # if skeletal? skip; static only
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc), rot or unreal.Rotator())
    if not a:
        return None
    c = a.static_mesh_component
    try:
        if isinstance(mesh_asset, unreal.StaticMesh):
            c.set_static_mesh(mesh_asset)
        else:
            # maybe Interchange imported as different type - try get editor property
            log("non-static mesh asset for " + str(label) + " type=" + str(type(mesh_asset)))
            return a
    except Exception as e:
        log("set mesh fail " + str(e))
        return a
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

def first_static_in_folder(folder):
    try:
        for a in unreal.EditorAssetLibrary.list_assets(folder, True, False):
            asset = unreal.EditorAssetLibrary.load_asset(a)
            if isinstance(asset, unreal.StaticMesh):
                return asset
    except Exception:
        pass
    return None

def main():
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L10_")

    plate = mat("/Game/Skyguard/Materials/M_Tex_L8_plate2") or mat("/Game/Skyguard/Materials/M_Tex_L3_plate")
    rust = mat("/Game/Skyguard/Materials/M_Tex_L8_corrugated")
    plaster = mat("/Game/Skyguard/Materials/M_Tex_L8_plaster2")
    concrete = mat("/Game/Skyguard/Materials/M_Tex_L4_concrete8")
    leather = mat("/Game/Skyguard/Materials/M_Tex_leather")
    rifle_m = mat("/Game/Skyguard/Materials/M_RifleTan") or plate
    sand = mat("/Game/Skyguard/Materials/M_Tex_L8_beach2")
    wet = mat("/Game/Skyguard/Materials/M_L5_WetAsphalt")
    floorworn = mat("/Game/Skyguard/Materials/M_Tex_L8_floorworn")
    canopy = mat("/Game/Skyguard/Materials/M_CockpitGlass")
    exhaust = mat("/Game/Skyguard/Materials/M_ExhaustGlow")
    wood = mat("/Game/Skyguard/Materials/M_Tex_L3_wood2")
    foliage = mat("/Game/Skyguard/Materials/M_Foliage")

    # Prefer webgame imported meshes
    yak = load_any([
        "/Game/Skyguard/Meshes/WebGame/yak52-detail-kit",
        "/Game/Skyguard/Meshes/WebGame/yak52_detail_kit",
    ]) or load_any(["/Game/Skyguard/Meshes/Hero/yak52_hd_proxy"])
    rifle = load_any([
        "/Game/Skyguard/Meshes/WebGame/skyguard-rifle",
        "/Game/Skyguard/Meshes/WebGame/skyguard_rifle",
    ]) or load_any(["/Game/Skyguard/Meshes/Hero/rifle_ads_proxy"])
    drone = load_any([
        "/Game/Skyguard/Meshes/WebGame/skyguard-drone",
        "/Game/Skyguard/Meshes/WebGame/skyguard_drone",
    ]) or load_any(["/Game/Skyguard/Meshes/Hero/shahed_proxy"])
    interceptor = load_any([
        "/Game/Skyguard/Meshes/WebGame/skyguard-interceptor",
    ]) or yak
    occupant = load_any([
        "/Game/Skyguard/Meshes/WebGame/skyguard-occupant",
    ])
    # if folder has multiple static meshes from glb, grab first statics
    if not isinstance(yak, unreal.StaticMesh):
        yak = first_static_in_folder("/Game/Skyguard/Meshes/WebGame") or load_any(["/Game/Skyguard/Meshes/Hero/yak52_hd_proxy"])
    log("yak mesh=" + str(yak))
    log("rifle mesh=" + str(rifle))
    log("drone mesh=" + str(drone))

    # hero placements
    spawn_sm(yak, (0, 40, 300), (1, 1, 1) if yak and 'WebGame' in str(getattr(yak, 'get_path_name', lambda: '')()) else (95, 95, 95), None, "AAA_L10_HeroYak", None)
    # scale heuristic: webgame models may already be world-sized; use modest scale and also spawn proxy companions
    spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/yak52_hd_proxy"]), (0, 40, 300), (90, 90, 90), None, "AAA_L10_YakProxyBackup", plate)
    spawn_sm(rifle, (18, 120, 358), (1, 1, 1), unreal.Rotator(0, 10, 0), "AAA_L10_HeroRifle", None)
    spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/rifle_ads_proxy"]), (18, 120, 358), (32, 32, 32), unreal.Rotator(0, 10, 0), "AAA_L10_RifleProxyBackup", rifle_m)
    spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/glove_arm_proxy"]), (22, 100, 352), (22, 22, 22), unreal.Rotator(8, 16, 4), "AAA_L10_GloveArm", leather)
    spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/gunner_pov_kit"]), (0, 78, 348), (52, 52, 52), None, "AAA_L10_GunnerPOV", leather)
    spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/instrument_cluster_proxy"]), (0, -20, 365), (45, 45, 45), None, "AAA_L10_Instruments", plate)
    spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/igla_proxy"]), (-34, 100, 350), (25, 25, 25), unreal.Rotator(0, -8, 5), "AAA_L10_Igla", rust)
    spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/propeller_proxy"]), (0, -585, 320), (100, 100, 100), None, "AAA_L10_Prop", plate)
    if occupant:
        spawn_sm(occupant, (0, 60, 355), (1, 1, 1), None, "AAA_L10_Occupant", None)
    spawn_sm(unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere"), (0, -92, 376), (1.25, 1.65, 0.88), None, "AAA_L10_Canopy", canopy)

    # city densify
    for i in range(24):
        y = -3200 + i * 260
        spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/coast_block_proxy"]), (-2300, y, 20), (22, 22, 16 + (i % 8)), None, "AAA_L10_CoastBlock_%d" % i, plaster if i % 2 == 0 else concrete)
        spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/apartment_midrise_proxy"]), (-2580, y + 40, 20), (18, 18, 18 + (i % 5) * 2), None, "AAA_L10_Apt_%d" % i, concrete)
        if i % 3 == 0:
            spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/ruined_tower_proxy"]), (-2100, y - 30, 20), (24, 24, 20), None, "AAA_L10_Ruin_%d" % i, floorworn)
            spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/rubble_cluster_proxy"]), (-2020, y, 28), (20, 20, 18), None, "AAA_L10_Rubble_%d" % i, concrete)
        spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/city_car_proxy"]), (-1890, y + 10, 34), (17, 17, 17), unreal.Rotator(0, 90 if i % 2 else 0, 0), "AAA_L10_Car_%d" % i, plate)
        if i % 4 == 0:
            spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/city_bus_proxy"]), (-1870, y - 80, 34), (14, 14, 14), unreal.Rotator(0, 90, 0), "AAA_L10_Bus_%d" % i, plate)
        spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/street_lamp_proxy"]), (-1850, y + 50, 34), (20, 20, 20), None, "AAA_L10_Lamp_%d" % i, plate)
        if i % 2 == 0:
            spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/coast_tree_proxy"]), (-1970, y - 40, 34), (18, 18, 18), None, "AAA_L10_Tree_%d" % i, foliage)

    # harbor/ocean
    for i, y in enumerate([-2200, -1100, 0, 1100, 2200, 3000]):
        spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/pier_section_proxy"]), (-560, y, 18), (30, 30, 30), None, "AAA_L10_Pier_%d" % i, wood)
        spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/harbor_crane_proxy"]), (-300, y + 80, 18), (45, 45, 45), None, "AAA_L10_Crane_%d" % i, rust)
        spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/seawall_proxy"]), (-820, y, 10), (20, 12, 12), None, "AAA_L10_Seawall_%d" % i, concrete)
        if i % 2 == 0:
            spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/flak_emplacement_proxy"]), (-1250, y, 32), (18, 18, 18), None, "AAA_L10_Flak_%d" % i, rust)
    spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/freighter_proxy"]), (1150, -2200, 0), (45, 45, 45), unreal.Rotator(0, 12, 0), "AAA_L10_Freighter", plate)
    spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/container_ship_proxy"]), (900, -1500, 0), (50, 50, 50), unreal.Rotator(0, -8, 0), "AAA_L10_Ship", plate)
    spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/submarine_proxy"]), (1950, 900, 0), (85, 85, 85), unreal.Rotator(0, 90, 0), "AAA_L10_Sub", plate)

    # beach/road
    cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    for i, y in enumerate(range(-3600, 3601, 130)):
        spawn_sm(cube, (-1020, y, 14), (10, 6.5, 0.22), None, "AAA_L10_Beach_%d" % i, sand)
        spawn_sm(cube, (-1890, y, 34.06), (4.7, 6.5, 0.03), None, "AAA_L10_WetRoad_%d" % i, wet)

    # drones using webgame mesh if available
    for lane, y in enumerate([-2600, -1300, 0, 1300, 2600]):
        for n in range(10):
            x = 2400 + n * 390 + (lane % 2) * 160
            z = 350 + (n % 5) * 55
            heavy = (n % 3 == 0)
            mesh = drone if drone else load_any(["/Game/Skyguard/Meshes/Hero/shahed_heavy_proxy" if heavy else "/Game/Skyguard/Meshes/Hero/shahed_proxy"])
            # dual place: web mesh + proxy backup for scale certainty
            sc = 1.0
            spawn_sm(mesh, (x, y, z), (sc, sc, sc), unreal.Rotator(0, 180, 0), "AAA_L10_Drone_%d_%d" % (lane, n), None)
            spawn_sm(load_any(["/Game/Skyguard/Meshes/Hero/shahed_heavy_proxy" if heavy else "/Game/Skyguard/Meshes/Hero/shahed_proxy"]), (x, y, z), (42 if heavy else 32, 42 if heavy else 32, 42 if heavy else 32), unreal.Rotator(0, 180, 0), "AAA_L10_DroneProxy_%d_%d" % (lane, n), plate)
            spawn_sm(unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere"), (x + 100, y, z), (0.3, 0.3, 0.3), None, "AAA_L10_DroneEx_%d_%d" % (lane, n), exhaust)

    # C++ combat seed
    try:
        gunner_cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardGunner")
        spawner_cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardDroneSpawner")
        drone_cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardDrone")
        if gunner_cls:
            g = unreal.EditorLevelLibrary.spawn_actor_from_class(gunner_cls, unreal.Vector(20, 105, 360), unreal.Rotator())
            if g:
                g.set_actor_label("AAA_L10_CPP_Gunner")
                log("spawned cpp gunner")
        if spawner_cls:
            s = unreal.EditorLevelLibrary.spawn_actor_from_class(spawner_cls, unreal.Vector(2700, 0, 520), unreal.Rotator())
            if s:
                s.set_actor_label("AAA_L10_CPP_Spawner")
        if drone_cls:
            for i, y in enumerate([-500, 0, 500, 1000]):
                d = unreal.EditorLevelLibrary.spawn_actor_from_class(drone_cls, unreal.Vector(3100, y, 430), unreal.Rotator(0, 180, 0))
                if d:
                    d.set_actor_label("AAA_L10_CPP_Drone_%d" % i)
    except Exception as e:
        log("cpp " + str(e))

    for name, loc, rot in [
        ("AAA_Cam_L10_Cockpit", (30, 115, 372), (-7, 8, 0)),
        ("AAA_Cam_L10_ADS", (18, 140, 366), (-1, 8, 0)),
        ("AAA_Cam_L10_HeroRifle", (22, 125, 360), (-3, 12, 0)),
        ("AAA_Cam_L10_City", (-2000, 0, 120), (-8, 0, 0)),
        ("AAA_Cam_L10_Harbor", (-400, -1200, 180), (-8, 35, 0)),
        ("AAA_Cam_L10_Swarm", (3600, 0, 800), (-16, -180, 0)),
        ("AAA_Cam_L10_YakBeauty", (700, -1200, 560), (-12, 145, 0)),
        ("AAA_Cam_L10_Ocean", (1500, -1800, 280), (-12, 45, 0)),
    ]:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)

    ps = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(20, 105, 360), unreal.Rotator())
    if ps:
        ps.set_actor_label("AAA_L10_PlayerStart")

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop10 world complete with webgame hero assets staged")
    log("CRITIC: still FAIL vs AAA until materials/VFX/audio fully authored and playable feel matches refs")

if __name__ == "__main__":
    main()
