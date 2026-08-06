import unreal
import math

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

def rebuild_ocean_material(name, deep=False):
    path = "/Game/Skyguard/Materials/" + name
    mel = unreal.MaterialEditingLibrary
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        mat = unreal.EditorAssetLibrary.load_asset(path)
    else:
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, "/Game/Skyguard/Materials", unreal.Material, unreal.MaterialFactoryNew())
    if not mat:
        return None
    try:
        mel.delete_all_material_expressions(mat)
        # translucent-ish look via base + roughness + slight emissive horizon
        base = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -500, -120)
        if deep:
            base.set_editor_property("constant", unreal.LinearColor(0.01, 0.05, 0.09, 1.0))
            rough_v = 0.12
        else:
            base.set_editor_property("constant", unreal.LinearColor(0.02, 0.14, 0.22, 1.0))
            rough_v = 0.08
        # noise variation
        try:
            noise = mel.create_material_expression(mat, unreal.MaterialExpressionNoise, -500, 20)
            noise.set_editor_property("scale", 0.015)
            scale = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -320, 80)
            scale.set_editor_property("r", 0.08)
            mul = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -180, 20)
            mel.connect_material_expressions(noise, "", mul, "A")
            mel.connect_material_expressions(scale, "", mul, "B")
            add = mel.create_material_expression(mat, unreal.MaterialExpressionAdd, -40, -40)
            one = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -320, 140)
            one.set_editor_property("r", 1.0)
            mel.connect_material_expressions(one, "", add, "A")
            mel.connect_material_expressions(mul, "", add, "B")
            base_mul = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, 80, -80)
            mel.connect_material_expressions(base, "", base_mul, "A")
            mel.connect_material_expressions(add, "", base_mul, "B")
            mel.connect_material_property(base_mul, "", unreal.MaterialProperty.MP_BASE_COLOR)
        except Exception:
            mel.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
        rough = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -500, 180)
        rough.set_editor_property("r", rough_v)
        mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
        metal = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -500, 240)
        metal.set_editor_property("r", 0.05)
        mel.connect_material_property(metal, "", unreal.MaterialProperty.MP_METALLIC)
        spec = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -500, 300)
        spec.set_editor_property("r", 0.9)
        mel.connect_material_property(spec, "", unreal.MaterialProperty.MP_SPECULAR)
        # subtle horizon glint
        em = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -500, 360)
        em.set_editor_property("constant", unreal.LinearColor(0.01, 0.03, 0.05, 1.0))
        mel.connect_material_property(em, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        mel.recompile_material(mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mat)
        log("rebuilt ocean mat " + name)
    except Exception as e:
        log("ocean mat fail " + str(e))
    return mat

def try_spawn_water_body():
    # Prefer Water plugin body if class available
    candidates = [
        "/Script/Water.WaterBodyOcean",
        "/Script/Water.WaterBodyLake",
        "/Script/Water.WaterBodyCustom",
    ]
    for path in candidates:
        try:
            cls = unreal.load_class(None, path)
            if not cls:
                continue
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(1200, 0, 0), unreal.Rotator())
            if a:
                a.set_actor_label("AAA_L14_WaterBodyOcean")
                try:
                    a.set_actor_scale3d(unreal.Vector(40, 40, 1))
                except Exception:
                    pass
                log("spawned water body class " + path)
                return a
        except Exception as e:
            log("water class " + path + " " + str(e))
    return None

def densify_ocean_surface(ocean_mat, deep_mat, foam_mat):
    plane = load_sm("/Engine/BasicShapes/Plane")
    cube = load_sm("/Engine/BasicShapes/Cube")
    sphere = load_sm("/Engine/BasicShapes/Sphere")
    # Large ocean tiles seaward (positive X from coast assumptions vary; project historically city negative X)
    # Place broad water sheets both sides for robustness
    for i, x in enumerate([-400, 200, 900, 1800, 2800, 4000]):
        for j, y in enumerate(range(-5000, 5001, 1800)):
            mat = deep_mat if x > 1000 else ocean_mat
            spawn_sm(plane, (x, y, -2.0), (90, 90, 1), unreal.Rotator(0, 0, 0), "AAA_L14_OceanTile_%d_%d" % (i, j), mat)
    # Shore foam lace near beach/city transition ~ x=-740 historically
    for i, y in enumerate(range(-4200, 4201, 90)):
        spawn_sm(cube, (-760, y, 2.5), (2.2, 4.2, 0.05), None, "AAA_L14_Foam_%d" % i, foam_mat)
        if i % 3 == 0:
            spawn_sm(sphere, (-720, y + 20, 4.0), (1.4, 2.0, 0.12), None, "AAA_L14_FoamCap_%d" % i, foam_mat)
    # Secondary deeper foam lines
    for i, y in enumerate(range(-4000, 4001, 160)):
        spawn_sm(cube, (-640, y, 1.5), (1.4, 5.5, 0.04), None, "AAA_L14_FoamLine2_%d" % i, foam_mat)
    # Whitecap flecks offshore
    for i in range(80):
        x = 400 + (i * 97) % 3200
        y = -3600 + (i * 173) % 7200
        spawn_sm(sphere, (x, y, 3.0 + (i % 5) * 0.4), (0.6, 0.9, 0.08), None, "AAA_L14_Whitecap_%d" % i, foam_mat)
    log("ocean surface densified")

def cockpit_integration():
    # Place occupant + open rear canopy feel + glass around gunner station
    occupant_parts = []
    for p in [
        "/Game/Skyguard/Meshes/WebGame/skyguard-occupant/StaticMeshes/occupant-leather",
        "/Game/Skyguard/Meshes/WebGame/skyguard-occupant/StaticMeshes/occupant-olive",
        "/Game/Skyguard/Meshes/WebGame/skyguard-occupant/StaticMeshes/occupant-oliveDark",
        "/Game/Skyguard/Meshes/WebGame/skyguard-occupant/StaticMeshes/occupant-seat",
        "/Game/Skyguard/Meshes/WebGame/skyguard-occupant/StaticMeshes/occupant-webbing",
        "/Game/Skyguard/Meshes/WebGame/skyguard-occupant/StaticMeshes/occupant-matteBlack",
    ]:
        m = load_sm(p)
        if m:
            occupant_parts.append((p.split("/")[-1], m))
    glass = load_mat("/Game/Skyguard/Materials/M_CockpitGlass")
    interior = load_mat("/Game/Skyguard/Materials/M_CockpitInterior")
    gauge = load_mat("/Game/Skyguard/Materials/M_GaugeGlass")
    airframe = load_mat("/Game/Skyguard/Materials/M_Tex_airframe_metal") or load_mat("/Game/Skyguard/Materials/M_YakAirframe")
    cube = load_sm("/Engine/BasicShapes/Cube")
    cyl = load_sm("/Engine/BasicShapes/Cylinder")
    plane = load_sm("/Engine/BasicShapes/Plane")

    # Occupant in rear seat near gunner
    for i, (name, mesh) in enumerate(occupant_parts):
        spawn_sm(mesh, (10, 95, 350), (0.9, 0.9, 0.9), unreal.Rotator(0, 90, 0), "AAA_L14_Occupant_%s" % name[:28])

    # Sliding rear canopy open: side rails + glass panels open to starboard/port
    # Rails
    for side, y in [("L", 70), ("R", 130)]:
        spawn_sm(cyl, (5, y, 375), (0.04, 0.04, 1.8), unreal.Rotator(0, 0, 90), "AAA_L14_CanopyRail_%s" % side, airframe)
    # Open canopy glass panels (slid aft/open)
    spawn_sm(plane, (25, 55, 385), (1.2, 0.9, 0.9), unreal.Rotator(70, 0, -25), "AAA_L14_CanopyGlass_OpenL", glass)
    spawn_sm(plane, (25, 145, 385), (1.2, 0.9, 0.9), unreal.Rotator(70, 0, 25), "AAA_L14_CanopyGlass_OpenR", glass)
    # Forward pilot windscreen (protect pilot - solid-ish glass wall)
    spawn_sm(plane, (-35, 100, 372), (0.05, 1.1, 0.9), unreal.Rotator(0, 0, 0), "AAA_L14_PilotShield", glass)
    spawn_sm(cube, (-38, 100, 360), (0.08, 1.0, 0.7), None, "AAA_L14_PilotBulkhead", interior)
    # Rear bow / last frame completion
    for i, x in enumerate([-5, 15, 35, 55]):
        spawn_sm(cyl, (x, 100, 390), (0.05, 0.05, 1.3), unreal.Rotator(0, 0, 90), "AAA_L14_CanopyBow_%d" % i, airframe)
        spawn_sm(plane, (x, 100, 400), (0.7, 0.9, 0.9), unreal.Rotator(90, 0, 0), "AAA_L14_CanopyTop_%d" % i, glass)
    # Instrument panel shelf
    spawn_sm(cube, (-10, 100, 355), (0.35, 0.9, 0.08), None, "AAA_L14_RearPanel", interior)
    for i in range(6):
        spawn_sm(cyl, (-5, 70 + i * 12, 362), (0.08, 0.08, 0.02), unreal.Rotator(90, 0, 0), "AAA_L14_Gauge_%d" % i, gauge)
    log("cockpit integration placed occupants=%d" % len(occupant_parts))

def city_roof_and_street_detail():
    cube = load_sm("/Engine/BasicShapes/Cube")
    cyl = load_sm("/Engine/BasicShapes/Cylinder")
    sphere = load_sm("/Engine/BasicShapes/Sphere")
    concrete = load_mat("/Game/Skyguard/Materials/M_Tex_concrete") or load_mat("/Game/Skyguard/Materials/M_CityConcrete")
    asphalt = load_mat("/Game/Skyguard/Materials/M_Tex_L3_asphalt2") or load_mat("/Game/Skyguard/Materials/M_Asphalt")
    metal = load_mat("/Game/Skyguard/Materials/M_Tex_metal") or load_mat("/Game/Skyguard/Materials/M_Metal")
    plaster = load_mat("/Game/Skyguard/Materials/M_Tex_L8_plaster2") or concrete
    glass = load_mat("/Game/Skyguard/Materials/M_CityGlass")
    # Roof AC / water tanks / antennas across city band
    for i in range(90):
        x = -2100 - (i % 7) * 160
        y = -3200 + (i * 79) % 6400
        z = 280 + (i * 37) % 700
        spawn_sm(cube, (x, y, z), (0.7, 0.5, 0.35), None, "AAA_L14_RoofAC_%d" % i, metal)
        if i % 2 == 0:
            spawn_sm(cyl, (x + 40, y, z + 40), (0.35, 0.35, 0.5), None, "AAA_L14_WaterTank_%d" % i, plaster)
        if i % 3 == 0:
            spawn_sm(cyl, (x - 20, y + 20, z + 90), (0.04, 0.04, 1.3), None, "AAA_L14_Antenna_%d" % i, metal)
        if i % 4 == 0:
            spawn_sm(cube, (x + 10, y - 30, z - 20), (0.05, 0.8, 0.5), None, "AAA_L14_WindowLite_%d" % i, glass)
    # Street furniture
    for i, y in enumerate(range(-3000, 3001, 180)):
        spawn_sm(cyl, (-1900, y, 55), (0.08, 0.08, 1.4), None, "AAA_L14_StreetLamp_%d" % i, metal)
        spawn_sm(sphere, (-1900, y, 95), (0.15, 0.15, 0.15), None, "AAA_L14_LampHead_%d" % i, glass)
        if i % 2 == 0:
            spawn_sm(cube, (-1860, y + 40, 36), (0.8, 0.35, 0.25), None, "AAA_L14_Car_%d" % i, metal)
            spawn_sm(cube, (-1860, y + 40, 42), (0.5, 0.3, 0.18), None, "AAA_L14_CarCabin_%d" % i, glass)
    # Road markings
    for i, y in enumerate(range(-3200, 3201, 220)):
        spawn_sm(cube, (-1890, y, 34.5), (3.8, 0.15, 0.02), None, "AAA_L14_LaneMark_%d" % i, asphalt)
    log("city roof/street densify complete")

def reseed_combat_and_cams():
    for name, loc, rot in [
        ("AAA_Cam_L14_YakBeauty", (700, -1200, 560), (-12, 145, 0)),
        ("AAA_Cam_L14_Cockpit", (30, 115, 372), (-7, 8, 0)),
        ("AAA_Cam_L14_ADS", (18, 140, 366), (-1, 8, 0)),
        ("AAA_Cam_L14_Ocean", (1400, -800, 420), (-10, 160, 0)),
        ("AAA_Cam_L14_City", (-900, -900, 380), (-8, 30, 0)),
        ("AAA_Cam_L14_Combat", (900, -200, 480), (-12, 175, 0)),
        ("AAA_Cam_L14_Shore", (-500, -600, 120), (-5, 20, 0)),
    ]:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)
    try:
        gunner_cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardGunner")
        spawner_cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardDroneSpawner")
        if gunner_cls:
            g = unreal.EditorLevelLibrary.spawn_actor_from_class(gunner_cls, unreal.Vector(20, 105, 360), unreal.Rotator())
            if g:
                g.set_actor_label("AAA_L14_CPP_Gunner")
        if spawner_cls:
            s = unreal.EditorLevelLibrary.spawn_actor_from_class(spawner_cls, unreal.Vector(2800, 0, 520), unreal.Rotator())
            if s:
                s.set_actor_label("AAA_L14_CPP_Spawner")
    except Exception as e:
        log("cpp " + str(e))

def main():
    log("loop14 ocean+cockpit+vfx densify start")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    for p in ["AAA_L14_", "AAA_L5W_Foam", "AAA_L5W_Wet"]:
        clear_prefix(p)

    ensure_dir("/Game/Skyguard/Materials")
    ocean = rebuild_ocean_material("M_Ocean", deep=False)
    deep = rebuild_ocean_material("M_OceanDeep", deep=True)
    foam = load_mat("/Game/Skyguard/Materials/M_L5_SeaFoam") or load_mat("/Game/Skyguard/Materials/M_Beach")
    beach = load_mat("/Game/Skyguard/Materials/M_Tex_L7_beach2") or load_mat("/Game/Skyguard/Materials/M_Beach")

    water = try_spawn_water_body()
    densify_ocean_surface(ocean, deep, foam)
    # Beach strip reinforcement
    cube = load_sm("/Engine/BasicShapes/Cube")
    for i, y in enumerate(range(-4500, 4501, 140)):
        spawn_sm(cube, (-820, y, 8), (8.0, 6.5, 0.35), None, "AAA_L14_Beach_%d" % i, beach)

    cockpit_integration()
    city_roof_and_street_detail()
    reseed_combat_and_cams()

    # Lighting polish
    try:
        sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 1800), unreal.Rotator(-32, 40, 0))
        if sun:
            sun.set_actor_label("AAA_L14_Sun")
        sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 700), unreal.Rotator())
        if sky:
            sky.set_actor_label("AAA_L14_SkyLight")
        exp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 300), unreal.Rotator())
        if exp:
            exp.set_actor_label("AAA_L14_PP")
            try:
                exp.set_editor_property("unbound", True)
            except Exception:
                pass
    except Exception as e:
        log("lights " + str(e))

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop14 ocean+cockpit+city densify complete water=%s" % bool(water))
    log("CRITIC: VFX runtime helper in C++ this loop; Niagara graphs still empty shells; overall still FAIL vs AAA")

if __name__ == "__main__":
    main()
