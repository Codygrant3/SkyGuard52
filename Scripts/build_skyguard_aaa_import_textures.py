"""Import PolyHaven + web PBR textures and build textured master materials, reapply to map actors by label prefix."""
import unreal

def log(m):
    unreal.log(f"[SkyguardAAA] {m}")

def ensure_dir(p):
    if not unreal.EditorAssetLibrary.does_directory_exist(p):
        unreal.EditorAssetLibrary.make_directory(p)

def import_texture(src_path, dest_path, dest_name):
    full = f"{dest_path}/{dest_name}"
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
    # imported name may differ
    assets = unreal.EditorAssetLibrary.list_assets(dest_path, False, False)
    for a in assets:
        if dest_name.lower() in a.lower():
            return unreal.EditorAssetLibrary.load_asset(a)
    log(f"import failed {src_path}")
    return None

def build_textured_material(name, albedo, normal=None, rough=None, metallic_const=0.0, emissive_scale=0.0):
    if not albedo:
        raise RuntimeError(f"{name}: a valid albedo texture is required; refusing to save an empty TextureSample")
    path = f"/Game/Skyguard/Materials/{name}"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        mat = unreal.EditorAssetLibrary.load_asset(path)
    else:
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, "/Game/Skyguard/Materials", unreal.Material, unreal.MaterialFactoryNew()
        )
    if not mat:
        return None
    mel = unreal.MaterialEditingLibrary
    try:
        mel.delete_all_material_expressions(mat)
    except Exception:
        pass
    try:
        # albedo sample
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
        else:
            rc = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -500, 200)
            rc.set_editor_property("r", 0.7)
            mel.connect_material_property(rc, "", unreal.MaterialProperty.MP_ROUGHNESS)
        mc = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -500, 280)
        mc.set_editor_property("r", float(metallic_const))
        mel.connect_material_property(mc, "", unreal.MaterialProperty.MP_METALLIC)
        if emissive_scale > 0 and albedo:
            em = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -200, 360)
            sc = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 400)
            sc.set_editor_property("r", float(emissive_scale))
            mel.connect_material_expressions(tex, "RGB", em, "A")
            mel.connect_material_expressions(sc, "", em, "B")
            mel.connect_material_property(em, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        mel.recompile_material(mat)
    except Exception as e:
        log(f"build mat {name}: {e}")
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
    log(f"applied {material.get_name() if material else None} to {count} actors matching {substr}")

def main():
    log("texture import + material apply pass start")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    ensure_dir("/Game/Skyguard/Textures/Imported")
    ensure_dir("/Game/Skyguard/Materials")

    # project content filesystem root for absolute paths
    # Unreal content path mapping: /Game/Skyguard/Textures/PolyHaven/...
    # Import from absolute disk path under project Content
    proj = unreal.Paths.project_content_dir()  # .../Content/
    base = proj + "Skyguard/Textures/PolyHaven/"
    web = proj + "Skyguard/Textures/WebPBR/"

    sets = {
        "concrete": (
            base + "concrete_wall_006/concrete_wall_006-diffuse-2k.jpg",
            base + "concrete_wall_006/concrete_wall_006-nor_gl-2k.jpg",
            base + "concrete_wall_006/concrete_wall_006-rough-2k.jpg",
            0.05,
        ),
        "brick": (
            base + "brick_wall_006/brick_wall_006-diffuse-2k.jpg",
            base + "brick_wall_006/brick_wall_006-nor_gl-2k.jpg",
            base + "brick_wall_006/brick_wall_006-rough-2k.jpg",
            0.02,
        ),
        "plaster": (
            base + "blue_plaster_weathered/blue_plaster_weathered-diffuse-2k.jpg",
            base + "blue_plaster_weathered/blue_plaster_weathered-nor_gl-2k.jpg",
            base + "blue_plaster_weathered/blue_plaster_weathered-rough-2k.jpg",
            0.0,
        ),
        "metal": (
            base + "green_metal_rust/green_metal_rust-diffuse-2k.jpg",
            base + "green_metal_rust/green_metal_rust-nor_gl-2k.jpg",
            base + "green_metal_rust/green_metal_rust-rough-2k.jpg",
            0.7,
        ),
        "airframe_metal": (
            base + "blue_metal_plate/blue_metal_plate-diffuse-2k.jpg",
            base + "blue_metal_plate/blue_metal_plate-nor_gl-2k.jpg",
            base + "blue_metal_plate/blue_metal_plate-rough-2k.jpg",
            0.85,
        ),
        "leather": (
            base + "fabric_leather_01/fabric_leather_01-diffuse-2k.jpg",
            base + "fabric_leather_01/fabric_leather_01-nor_gl-2k.jpg",
            base + "fabric_leather_01/fabric_leather_01-rough-2k.jpg",
            0.0,
        ),
    }

    built = {}
    for key, (a,n,r,m) in sets.items():
        ta = import_texture(a, "/Game/Skyguard/Textures/Imported", f"T_{key}_A")
        tn = import_texture(n, "/Game/Skyguard/Textures/Imported", f"T_{key}_N")
        tr = import_texture(r, "/Game/Skyguard/Textures/Imported", f"T_{key}_R")
        built[key] = build_textured_material(f"M_Tex_{key}", ta, tn, tr, metallic_const=m)
        log(f"built textured {key}")

    # web facade atlas
    # Unreal's unattended importer did not accept the original WebP sources.
    # The PNG files are lossless local transcodes of those same 3072px sources.
    fa = import_texture(web + "city-facade-atlas-albedo.png", "/Game/Skyguard/Textures/Imported", "T_Facade_A")
    fn = import_texture(web + "city-facade-atlas-normal.png", "/Game/Skyguard/Textures/Imported", "T_Facade_N")
    fr = import_texture(web + "city-facade-atlas-roughness.png", "/Game/Skyguard/Textures/Imported", "T_Facade_R")
    built["facade"] = build_textured_material("M_Tex_FacadeAtlas", fa, fn, fr, metallic_const=0.05)

    # apply
    apply_mat_to_label_contains("Bld_", built.get("facade") or built.get("concrete"))
    apply_mat_to_label_contains("CityDetail_Balcony", built.get("concrete"))
    apply_mat_to_label_contains("CityDetail_AC", built.get("metal"))
    apply_mat_to_label_contains("CityDetail_Antenna", built.get("metal"))
    apply_mat_to_label_contains("CityDetail_Window", built.get("plaster"))
    apply_mat_to_label_contains("Yak_", built.get("airframe_metal"))
    apply_mat_to_label_contains("Rifle", built.get("metal"))
    apply_mat_to_label_contains("Glove", built.get("leather"))
    apply_mat_to_label_contains("Drone_", built.get("metal"))
    apply_mat_to_label_contains("Pier_", built.get("concrete"))
    apply_mat_to_label_contains("Crane", built.get("metal"))
    apply_mat_to_label_contains("Container", built.get("metal"))
    apply_mat_to_label_contains("Ship", built.get("metal"))
    apply_mat_to_label_contains("Landmass", built.get("concrete"))
    apply_mat_to_label_contains("Promenade", built.get("concrete"))
    apply_mat_to_label_contains("Road", built.get("concrete"))

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("textured materials imported and applied")
    log("CRITIC: better, but still FAIL AAA until hero meshes + gameplay compile")

if __name__ == "__main__":
    main()
