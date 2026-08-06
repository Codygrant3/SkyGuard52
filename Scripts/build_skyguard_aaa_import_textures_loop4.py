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
        mat = unreal.EditorAssetLibrary.load_asset(path)
    else:
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, "/Game/Skyguard/Materials", unreal.Material, unreal.MaterialFactoryNew())
    if not mat:
        return None
    mel = unreal.MaterialEditingLibrary
    try:
        mel.delete_all_material_expressions(mat)
    except Exception:
        pass
    try:
        tex = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -500, -120)
        if albedo:
            tex.set_editor_property("texture", albedo)
        mel.connect_material_property(tex, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
        if normal:
            n = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -500, 40)
            n.set_editor_property("texture", normal)
            try:
                n.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
            except Exception:
                pass
            mel.connect_material_property(n, "RGB", unreal.MaterialProperty.MP_NORMAL)
        if rough:
            r = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -500, 200)
            r.set_editor_property("texture", rough)
            mel.connect_material_property(r, "R", unreal.MaterialProperty.MP_ROUGHNESS)
        mc = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -500, 280)
        mc.set_editor_property("r", float(metallic_const))
        mel.connect_material_property(mc, "", unreal.MaterialProperty.MP_METALLIC)
        mel.recompile_material(mat)
    except Exception as e:
        log("build mat " + name + ": " + str(e))
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat

def apply_mat_to_label_contains(substr, material):
    count = 0
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            label = a.get_actor_label() or ""
            if substr in label and isinstance(a, unreal.StaticMeshActor):
                a.static_mesh_component.set_material(0, material)
                count += 1
        except Exception:
            pass
    log("applied " + (material.get_name() if material else "None") + " to " + str(count) + " actors matching " + substr)

def main():
    log("loop4 texture import start")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    ensure_dir("/Game/Skyguard/Textures/Imported")
    proj = unreal.Paths.project_content_dir()
    base = proj + "Skyguard/Textures/PolyHaven/"
    sets = {
        "rust": (base + "rusty_metal_02/rusty_metal_02_diff_2k.jpg", base + "rusty_metal_02/rusty_metal_02_nor_gl_2k.jpg", base + "rusty_metal_02/rusty_metal_02_rough_2k.jpg", 0.7),
        "concrete8": (base + "concrete_wall_008/concrete_wall_008_diff_2k.jpg", base + "concrete_wall_008/concrete_wall_008_nor_gl_2k.jpg", base + "concrete_wall_008/concrete_wall_008_rough_2k.jpg", 0.05),
        "grassrock": (base + "aerial_grass_rock/aerial_grass_rock_diff_2k.jpg", base + "aerial_grass_rock/aerial_grass_rock_nor_gl_2k.jpg", base + "aerial_grass_rock/aerial_grass_rock_rough_2k.jpg", 0.0),
    }
    mats = {}
    for key, (a,n,r,met) in sets.items():
        ta = import_texture(a, "/Game/Skyguard/Textures/Imported", "T_L4_" + key + "_A")
        tn = import_texture(n, "/Game/Skyguard/Textures/Imported", "T_L4_" + key + "_N")
        tr = import_texture(r, "/Game/Skyguard/Textures/Imported", "T_L4_" + key + "_R")
        mats[key] = build_textured_material("M_Tex_L4_" + key, ta, tn, tr, met)
    apply_mat_to_label_contains("Crane", mats.get("rust"))
    apply_mat_to_label_contains("Container", mats.get("rust"))
    apply_mat_to_label_contains("Sub", mats.get("rust"))
    apply_mat_to_label_contains("Tower", mats.get("concrete8"))
    apply_mat_to_label_contains("Terrain", mats.get("grassrock"))
    apply_mat_to_label_contains("Landmark_Stacks", mats.get("rust"))
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("loop4 texture import complete")

if __name__ == "__main__":
    main()
