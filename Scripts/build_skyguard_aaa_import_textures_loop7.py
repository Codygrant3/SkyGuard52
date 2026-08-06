import unreal

def log(m):
    unreal.log("[SkyguardAAA] " + str(m))

def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)

def import_texture(src_path, dest_path, dest_name):
    full = dest_path + "/" + dest_name
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.EditorAssetLibrary.load_asset(full)
    task = unreal.AssetImportTask()
    task.filename = src_path
    task.destination_path = dest_path
    task.destination_name = dest_name
    task.automated = True
    task.save = True
    task.replace_existing = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.EditorAssetLibrary.load_asset(full)
    for a in unreal.EditorAssetLibrary.list_assets(dest_path, False, False):
        if dest_name.lower() in a.lower():
            return unreal.EditorAssetLibrary.load_asset(a)
    log("import failed " + src_path)
    return None

def build_textured_material(name, albedo, normal=None, rough=None, metallic_const=0.0):
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
        tex = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -500, -120)
        if albedo:
            tex.set_editor_property("texture", albedo)
        mel.connect_material_property(tex, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
        if normal:
            n = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -500, 40)
            n.set_editor_property("texture", normal)
            try:
                n.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
            except Exception:
                pass
            mel.connect_material_property(n, "RGB", unreal.MaterialProperty.MP_NORMAL)
        if rough:
            r = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -500, 200)
            r.set_editor_property("texture", rough)
            mel.connect_material_property(r, "R", unreal.MaterialProperty.MP_ROUGHNESS)
        mc = mel.create_material_expression(m, unreal.MaterialExpressionConstant, -500, 280)
        mc.set_editor_property("r", float(metallic_const))
        mel.connect_material_property(mc, "", unreal.MaterialProperty.MP_METALLIC)
        mel.recompile_material(m)
    except Exception as e:
        log("build " + name + " " + str(e))
    unreal.EditorAssetLibrary.save_loaded_asset(m)
    return m

def apply_mat(substr, material):
    count = 0
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            label = a.get_actor_label() or ""
            if substr in label and isinstance(a, unreal.StaticMeshActor):
                a.static_mesh_component.set_material(0, material)
                count += 1
        except Exception:
            pass
    log("applied " + (material.get_name() if material else "None") + " => " + str(count) + " " + substr)

def main():
    log("loop7 texture import start")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    ensure_dir("/Game/Skyguard/Textures/Imported")
    proj = unreal.Paths.project_content_dir()
    base = proj + "Skyguard/Textures/PolyHaven/"
    sets = {
        "plaster2": (base + "painted_plaster_wall/painted_plaster_wall_diff_2k.jpg", base + "painted_plaster_wall/painted_plaster_wall_nor_gl_2k.jpg", base + "painted_plaster_wall/painted_plaster_wall_rough_2k.jpg", 0.0),
        "beach2": (base + "aerial_beach_01/aerial_beach_01_diff_2k.jpg", base + "aerial_beach_01/aerial_beach_01_nor_gl_2k.jpg", base + "aerial_beach_01/aerial_beach_01_rough_2k.jpg", 0.0),
        "corrugated": (base + "corrugated_iron_02/corrugated_iron_02_diff_2k.jpg", base + "corrugated_iron_02/corrugated_iron_02_nor_gl_2k.jpg", base + "corrugated_iron_02/corrugated_iron_02_rough_2k.jpg", 0.7),
        "floorworn": (base + "concrete_floor_worn_001/concrete_floor_worn_001_diff_2k.jpg", base + "concrete_floor_worn_001/concrete_floor_worn_001_nor_gl_2k.jpg", base + "concrete_floor_worn_001/concrete_floor_worn_001_rough_2k.jpg", 0.05),
    }
    mats = {}
    for key, (a,n,r,met) in sets.items():
        ta = import_texture(a, "/Game/Skyguard/Textures/Imported", "T_L7_" + key + "_A")
        tn = import_texture(n, "/Game/Skyguard/Textures/Imported", "T_L7_" + key + "_N")
        tr = import_texture(r, "/Game/Skyguard/Textures/Imported", "T_L7_" + key + "_R")
        mats[key] = build_textured_material("M_Tex_L7_" + key, ta, tn, tr, met)
    apply_mat("CoastBlock", mats.get("plaster2"))
    apply_mat("Apt_", mats.get("plaster2"))
    apply_mat("Beach", mats.get("beach2"))
    apply_mat("Crane", mats.get("corrugated"))
    apply_mat("Ship", mats.get("corrugated"))
    apply_mat("Radar", mats.get("corrugated"))
    apply_mat("Rubble", mats.get("floorworn"))
    apply_mat("CockpitTub", mats.get("floorworn"))
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("loop7 texture import complete")

if __name__ == "__main__":
    main()
