"""Repair M_Tex_FacadeAtlas from lossless PNG transcodes of the original WebP set.

Run inside UnrealEditor-Cmd. The script is deliberately fail-closed: it never
deletes the existing graph unless all three textures have imported and loaded.
"""

from __future__ import annotations

import unreal


DESTINATION = "/Game/Skyguard/Textures/Imported"
MATERIAL_PATH = "/Game/Skyguard/Materials/M_Tex_FacadeAtlas"


def log(message: str) -> None:
    unreal.log(f"[SkyguardFacadeRepair] {message}")


def import_texture(source: str, name: str) -> unreal.Texture:
    object_path = f"{DESTINATION}/{name}"
    task = unreal.AssetImportTask()
    task.filename = source
    task.destination_path = DESTINATION
    task.destination_name = name
    task.automated = True
    task.save = True
    task.replace_existing = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    texture = unreal.EditorAssetLibrary.load_asset(object_path)
    if not texture:
        raise RuntimeError(f"Texture import failed: {source} -> {object_path}")
    return texture


def main() -> None:
    content = unreal.Paths.project_content_dir()
    source_root = content + "Skyguard/Textures/WebPBR/"
    textures = {
        "albedo": import_texture(source_root + "city-facade-atlas-albedo.png", "T_Facade_A"),
        "normal": import_texture(source_root + "city-facade-atlas-normal.png", "T_Facade_N"),
        "roughness": import_texture(
            source_root + "city-facade-atlas-roughness.png", "T_Facade_R"
        ),
    }

    material = unreal.EditorAssetLibrary.load_asset(MATERIAL_PATH)
    if not material:
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "M_Tex_FacadeAtlas",
            "/Game/Skyguard/Materials",
            unreal.Material,
            unreal.MaterialFactoryNew(),
        )
    if not material:
        raise RuntimeError(f"Unable to load or create {MATERIAL_PATH}")

    editing = unreal.MaterialEditingLibrary
    editing.delete_all_material_expressions(material)

    albedo = editing.create_material_expression(
        material, unreal.MaterialExpressionTextureSample, -560, -140
    )
    albedo.set_editor_property("texture", textures["albedo"])
    editing.connect_material_property(
        albedo, "RGB", unreal.MaterialProperty.MP_BASE_COLOR
    )

    normal = editing.create_material_expression(
        material, unreal.MaterialExpressionTextureSample, -560, 40
    )
    normal.set_editor_property("texture", textures["normal"])
    normal.set_editor_property(
        "sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL
    )
    editing.connect_material_property(normal, "RGB", unreal.MaterialProperty.MP_NORMAL)

    roughness = editing.create_material_expression(
        material, unreal.MaterialExpressionTextureSample, -560, 220
    )
    roughness.set_editor_property("texture", textures["roughness"])
    editing.connect_material_property(
        roughness, "R", unreal.MaterialProperty.MP_ROUGHNESS
    )

    metallic = editing.create_material_expression(
        material, unreal.MaterialExpressionConstant, -560, 320
    )
    metallic.set_editor_property("r", 0.05)
    editing.connect_material_property(
        metallic, "", unreal.MaterialProperty.MP_METALLIC
    )

    editing.recompile_material(material)
    if not unreal.EditorAssetLibrary.save_loaded_asset(material, only_if_is_dirty=False):
        raise RuntimeError(f"Failed to save {MATERIAL_PATH}")
    unreal.EditorAssetLibrary.save_directory(DESTINATION, only_if_is_dirty=False, recursive=True)
    log("PASS: facade textures imported, material graph rebuilt, assets saved")


if __name__ == "__main__":
    main()
