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

def sm(mesh, loc, scale=None, rot=None, label=None, material=None):
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc), rot or unreal.Rotator())
    if not a:
        return None
    c = a.static_mesh_component
    c.set_static_mesh(mesh)
    if scale:
        a.set_actor_scale3d(unreal.Vector(*scale))
    if label:
        a.set_actor_label(label)
    if material:
        c.set_material(0, material)
    return a

def build_wet_material(name, base_color=(0.05,0.08,0.1), rough=0.15, metal=0.05):
    path = "/Game/Skyguard/Materials/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        m = unreal.EditorAssetLibrary.load_asset(path)
    else:
        m = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, "/Game/Skyguard/Materials", unreal.Material, unreal.MaterialFactoryNew())
    if not m:
        return None
    mel = unreal.MaterialEditingLibrary
    try:
        mel.delete_all_material_expressions(m)
        bc = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -400, -100)
        bc.set_editor_property("constant", unreal.LinearColor(base_color[0], base_color[1], base_color[2], 1))
        mel.connect_material_property(bc, "", unreal.MaterialProperty.MP_BASE_COLOR)
        r = mel.create_material_expression(m, unreal.MaterialExpressionConstant, -400, 40)
        r.set_editor_property("r", rough)
        mel.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS)
        mt = mel.create_material_expression(m, unreal.MaterialExpressionConstant, -400, 100)
        mt.set_editor_property("r", metal)
        mel.connect_material_property(mt, "", unreal.MaterialProperty.MP_METALLIC)
        sp = mel.create_material_expression(m, unreal.MaterialExpressionConstant, -400, 160)
        sp.set_editor_property("r", 0.85)
        mel.connect_material_property(sp, "", unreal.MaterialProperty.MP_SPECULAR)
        mel.recompile_material(m)
        unreal.EditorAssetLibrary.save_loaded_asset(m)
    except Exception as e:
        log("wet mat " + str(e))
    return m

def main():
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L5W_")
    wet_road = build_wet_material("M_L5_WetAsphalt", (0.03,0.03,0.035), 0.22, 0.02)
    wet_metal = build_wet_material("M_L5_WetMetal", (0.25,0.27,0.3), 0.18, 0.75)
    sea_foam = build_wet_material("M_L5_SeaFoam", (0.55,0.62,0.65), 0.35, 0.0)
    cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    sphere = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere")
    plane = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
    # wet road patches in city
    for i, y in enumerate(range(-2400, 2401, 220)):
        sm(cube, (-1890, y, 34.2), (4.2, 4.0, 0.04), None, "AAA_L5W_WetRoad_%d" % i, wet_road)
    # puddles
    for i, y in enumerate(range(-2000, 2001, 350)):
        sm(sphere, (-1820, y, 33.8), (1.2, 1.8, 0.05), None, "AAA_L5W_Puddle_%d" % i, wet_metal)
    # shoreline foam lace
    for i, y in enumerate(range(-3000, 3001, 120)):
        sm(cube, (-740, y, 3), (1.5, 5.5, 0.06), None, "AAA_L5W_Foam_%d" % i, sea_foam)
    # rain streak cards near cockpit for wet-air read
    glass = mat("/Game/Skyguard/Materials/M_CockpitGlass")
    for i in range(16):
        sm(plane, (10 + (i%4)*3, 70 + i*2, 380), (0.05, 0.4, 0.4), unreal.Rotator(0, 10, 15), "AAA_L5W_RainCard_%d" % i, glass)
    # directional sun re-key
    try:
        sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,1200), unreal.Rotator(-28, 55, 0))
        if sun:
            sun.set_actor_label("AAA_L5W_Sun")
    except Exception as e:
        log("sun " + str(e))
    # skylight intensity proxy via another skylight
    try:
        sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,600), unreal.Rotator())
        if sky:
            sky.set_actor_label("AAA_L5W_SkyLight")
    except Exception as e:
        log("skylight " + str(e))
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop5 weather/wetness pass complete")
    log("CRITIC: materials/ocean still FAIL vs AAA refs")

if __name__ == "__main__":
    main()
