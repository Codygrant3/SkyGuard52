"""Build and bind governed Mission 1 refinement materials without duplicating PolyHaven sources."""

import hashlib
import json
import os
import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
HERO_SOURCE = ROOT / "Content/Skyguard/Textures/Source/Mission01/HeroPBR_v1"
HERO_MANIFEST_PATH = ROOT / "Saved/Reports/M01_HERO_PBR_BAKE_MANIFEST.json"
HERO_REPORT_PATH = ROOT / "Saved/Reports/M01_HERO_PBR_BAKE_REPORT.json"
REFINEMENT_MANIFEST_PATH = ROOT / "Saved/Reports/M01_WAVE1_AAA_REFINEMENT_MANIFEST.json"
GEOMETRY_BUILDER_PATH = ROOT / "Scripts/build_skyguard_m01_wave1_refinement_validation.py"
MAP_PATH = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Material_Validation"
HERO_TEXTURE_ROOT = "/Game/Skyguard/Textures/Mission01/HeroPBR_v1"
MATERIAL_ROOT = "/Game/Skyguard/Materials/Mission01/MaterialValidation_v1"
REPORT_PATH = ROOT / "Saved/Reports/M01_REFINEMENT_MATERIAL_UNREAL_AUDIT.json"
BUDGET_PATH = ROOT / "Saved/Reports/M01_REFINEMENT_TEXTURE_BUDGET.json"
PREFIX = "M01_W1R_"


POLYHAVEN = {
    "Sand": {
        "slug": "coast_sand_01",
        "page": "https://polyhaven.com/a/coast_sand_01",
        "source": {
            "BaseColor": ROOT / "Content/Skyguard/Textures/PolyHaven/coast_sand_01/coast_sand_01_diff_2k.jpg",
            "Normal": ROOT / "Content/Skyguard/Textures/PolyHaven/coast_sand_01/coast_sand_01_nor_gl_2k.jpg",
            "Roughness": ROOT / "Content/Skyguard/Textures/PolyHaven/coast_sand_01/coast_sand_01_rough_2k.jpg",
        },
        "asset": {
            "BaseColor": "/Game/Skyguard/Textures/Imported/T_L3_sand_A",
            "Normal": "/Game/Skyguard/Textures/Imported/T_L3_sand_N",
            "Roughness": "/Game/Skyguard/Textures/Imported/T_L3_sand_R",
        },
        "tiling": 6.0,
        "metallic": 0.0,
    },
    "Asphalt": {
        "slug": "asphalt_02",
        "page": "https://polyhaven.com/a/asphalt_02",
        "source": {
            "BaseColor": ROOT / "Content/Skyguard/Textures/PolyHaven/asphalt_02/asphalt_02_diff_2k.jpg",
            "Normal": ROOT / "Content/Skyguard/Textures/PolyHaven/asphalt_02/asphalt_02_nor_gl_2k.jpg",
            "Roughness": ROOT / "Content/Skyguard/Textures/PolyHaven/asphalt_02/asphalt_02_rough_2k.jpg",
        },
        "asset": {
            "BaseColor": "/Game/Skyguard/Textures/Imported/T_L3_asphalt2_A",
            "Normal": "/Game/Skyguard/Textures/Imported/T_L3_asphalt2_N",
            "Roughness": "/Game/Skyguard/Textures/Imported/T_L3_asphalt2_R",
        },
        "tiling": 6.0,
        "metallic": 0.0,
    },
    "Concrete": {
        "slug": "concrete_wall_008",
        "page": "https://polyhaven.com/a/concrete_wall_008",
        "source": {
            "BaseColor": ROOT / "Content/Skyguard/Textures/PolyHaven/concrete_wall_008/concrete_wall_008_diff_2k.jpg",
            "Normal": ROOT / "Content/Skyguard/Textures/PolyHaven/concrete_wall_008/concrete_wall_008_nor_gl_2k.jpg",
            "Roughness": ROOT / "Content/Skyguard/Textures/PolyHaven/concrete_wall_008/concrete_wall_008_rough_2k.jpg",
        },
        "asset": {
            "BaseColor": "/Game/Skyguard/Textures/Imported/T_L4_concrete8_A",
            "Normal": "/Game/Skyguard/Textures/Imported/T_L4_concrete8_N",
            "Roughness": "/Game/Skyguard/Textures/Imported/T_L4_concrete8_R",
        },
        "tiling": 4.0,
        "metallic": 0.0,
    },
    "Plaster": {
        "slug": "painted_plaster_wall",
        "page": "https://polyhaven.com/a/painted_plaster_wall",
        "source": {
            "BaseColor": ROOT / "Content/Skyguard/Textures/PolyHaven/painted_plaster_wall/painted_plaster_wall_diff_2k.jpg",
            "Normal": ROOT / "Content/Skyguard/Textures/PolyHaven/painted_plaster_wall/painted_plaster_wall_nor_gl_2k.jpg",
            "Roughness": ROOT / "Content/Skyguard/Textures/PolyHaven/painted_plaster_wall/painted_plaster_wall_rough_2k.jpg",
        },
        "asset": {
            "BaseColor": "/Game/Skyguard/Textures/Imported/T_L7_plaster2_A",
            "Normal": "/Game/Skyguard/Textures/Imported/T_L7_plaster2_N",
            "Roughness": "/Game/Skyguard/Textures/Imported/T_L7_plaster2_R",
        },
        "tiling": 3.0,
        "metallic": 0.0,
    },
}


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path):
    with open(path, "r", encoding="utf-8") as stream:
        return json.load(stream)


def ensure_directory(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def configure_texture(texture, role, open_gl_normal=False):
    texture.set_editor_property("srgb", role == "BaseColor")
    if role == "Normal":
        texture.set_editor_property(
            "compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP
        )
        texture.set_editor_property("flip_green_channel", bool(open_gl_normal))
    elif role in {"Roughness", "ORM", "MaterialID"}:
        texture.set_editor_property(
            "compression_settings", unreal.TextureCompressionSettings.TC_MASKS
        )
    unreal.EditorAssetLibrary.save_loaded_asset(texture, False)


def import_texture(source, destination, name, role, open_gl_normal=False):
    asset_path = destination + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        texture = unreal.EditorAssetLibrary.load_asset(asset_path)
        status = "reused_governed_asset"
    else:
        ensure_directory(destination)
        task = unreal.AssetImportTask()
        task.filename = str(source)
        task.destination_path = destination
        task.destination_name = name
        task.automated = True
        task.replace_existing = False
        task.save = True
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        texture = unreal.EditorAssetLibrary.load_asset(asset_path)
        status = "imported_new_governed_asset"
    if not isinstance(texture, unreal.Texture2D):
        raise RuntimeError("Texture unavailable: " + asset_path)
    configure_texture(texture, role, open_gl_normal)
    return texture, asset_path, status


def create_material(name):
    path = MATERIAL_ROOT + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        material = unreal.EditorAssetLibrary.load_asset(path)
    else:
        ensure_directory(MATERIAL_ROOT)
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, MATERIAL_ROOT, unreal.Material, unreal.MaterialFactoryNew()
        )
    if material is None:
        raise RuntimeError("Cannot create material " + path)
    unreal.MaterialEditingLibrary.delete_all_material_expressions(material)
    return material, path


def texture_sample(material, texture, x, y, normal=False, uv=None):
    mel = unreal.MaterialEditingLibrary
    sample = mel.create_material_expression(
        material, unreal.MaterialExpressionTextureSample, x, y
    )
    sample.set_editor_property("texture", texture)
    if normal:
        sample.set_editor_property(
            "sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL
        )
    if uv is not None:
        mel.connect_material_expressions(uv, "", sample, "Coordinates")
    return sample


def build_poly_material(name, textures, tiling, metallic):
    material, path = create_material("M_M01_" + name)
    mel = unreal.MaterialEditingLibrary
    uv = mel.create_material_expression(
        material, unreal.MaterialExpressionTextureCoordinate, -700, 20
    )
    uv.set_editor_property("u_tiling", tiling)
    uv.set_editor_property("v_tiling", tiling)
    base = texture_sample(material, textures["BaseColor"], -450, -160, uv=uv)
    normal = texture_sample(material, textures["Normal"], -450, 20, True, uv)
    rough = texture_sample(material, textures["Roughness"], -450, 200, uv=uv)
    metal = mel.create_material_expression(
        material, unreal.MaterialExpressionConstant, -420, 360
    )
    metal.set_editor_property("r", float(metallic))
    mel.connect_material_property(base, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(normal, "RGB", unreal.MaterialProperty.MP_NORMAL)
    mel.connect_material_property(rough, "R", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(metal, "", unreal.MaterialProperty.MP_METALLIC)
    mel.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material, False)
    return material, path


def build_hero_material(hero, textures):
    material, path = create_material("M_M01_Hero_" + hero)
    mel = unreal.MaterialEditingLibrary
    base = texture_sample(material, textures["BaseColor"], -450, -180)
    normal = texture_sample(material, textures["Normal"], -450, 20, True)
    orm = texture_sample(material, textures["ORM"], -450, 220)
    mel.connect_material_property(base, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(normal, "RGB", unreal.MaterialProperty.MP_NORMAL)
    mel.connect_material_property(
        orm, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION
    )
    mel.connect_material_property(orm, "G", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(orm, "B", unreal.MaterialProperty.MP_METALLIC)
    mel.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material, False)
    return material, path


def assign_component_material(component, material):
    mesh = component.get_editor_property("static_mesh")
    if mesh is None:
        return 0
    slots = len(mesh.get_editor_property("static_materials"))
    for index in range(slots):
        component.set_material(index, material)
    return slots


def family_for_mesh(name):
    if name == "SM_M01_Coast_Beach_Detailed_A":
        return "Sand"
    if name == "SM_M01_Road_CoastalTransition_Detailed_A":
        return "Asphalt"
    if name in {
        "SM_M01_Coast_Seawall_Detailed_A",
        "SM_M01_Coast_Promenade_Detailed_A",
    }:
        return "Concrete"
    if name.startswith("SM_M01_Urban_"):
        return "Plaster"
    if name == "SM_M01_Landmark_Lighthouse_Hero_A":
        return "Lighthouse"
    if name == "SM_M01_Landmark_RadarPost_Hero_A":
        return "RadarPost"
    if name.startswith("SM_Boss_Pathfinder_"):
        return "Pathfinder"
    return None


def build_or_load_validation_map():
    """Create this revision directly; never duplicate/load a live World asset."""
    if unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        if not unreal.EditorLevelLibrary.load_level(MAP_PATH):
            raise RuntimeError("Failed to load existing material-validation map")
        return "reused_existing_material_validation_map"

    if not GEOMETRY_BUILDER_PATH.is_file():
        raise RuntimeError("Missing geometry builder dependency")
    scripts_path = str(ROOT / "Scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    import build_skyguard_m01_wave1_refinement_validation as geometry

    manifest = read_json(REFINEMENT_MANIFEST_PATH)
    meshes, _ = geometry.collect_meshes()
    expected = {entry["name"] for entry in manifest["assets"]}
    if set(meshes) != expected:
        raise RuntimeError("Refinement mesh set differs from governed manifest")
    if not unreal.EditorLevelLibrary.new_level(MAP_PATH):
        raise RuntimeError("Failed to create material-validation map")

    for index, spec in enumerate(manifest["placements"]):
        if str(spec["mission_role"]).startswith("boss_"):
            continue
        geometry.spawn_static(
            meshes[spec["asset"]],
            "%s%03d_%s" % (PREFIX, index, spec["asset"][:48]),
            spec["location_m"],
            spec["rotation_deg"],
            spec["scale"],
        )
    boss, bindings, required = geometry.spawn_and_bind_pathfinder(meshes)
    if boss is None or bindings != required:
        raise RuntimeError("Refined Pathfinder could not be staged")
    geometry.spawn_environment()
    unreal.EditorLevelLibrary.save_current_level()
    return "created_from_governed_refinement_manifest"


def main():
    hero_manifest = read_json(HERO_MANIFEST_PATH)
    hero_report = read_json(HERO_REPORT_PATH)
    provenance = []
    poly_materials = {}

    for family, spec in POLYHAVEN.items():
        textures = {}
        for role, source in spec["source"].items():
            if not source.is_file():
                raise RuntimeError("Missing local PolyHaven source: " + str(source))
            asset_path = spec["asset"][role]
            texture = unreal.EditorAssetLibrary.load_asset(asset_path)
            if not isinstance(texture, unreal.Texture2D):
                raise RuntimeError("Missing existing canonical texture: " + asset_path)
            configure_texture(texture, role, role == "Normal")
            textures[role] = texture
            provenance.append({
                "provider": "PolyHaven",
                "family": family,
                "asset_page": spec["page"],
                "role": role,
                "source_path": str(source),
                "source_bytes": source.stat().st_size,
                "source_sha256": sha256(source),
                "unreal_asset": asset_path,
                "import_action": "reused_existing_canonical_unreal_asset",
                "resolution": [2048, 2048],
            })
        poly_materials[family] = build_poly_material(
            family, textures, spec["tiling"], spec["metallic"]
        )[0]

    hero_materials = {}
    hero_texture_paths = {}
    for hero in ["Pathfinder", "Lighthouse", "RadarPost"]:
        destination = HERO_TEXTURE_ROOT + "/" + hero
        textures = {}
        hero_texture_paths[hero] = {}
        for role in ["BaseColor", "Normal", "ORM", "MaterialID"]:
            source = HERO_SOURCE / hero / ("T_M01_%s_%s.png" % (hero, role))
            texture, asset_path, status = import_texture(
                source,
                destination,
                "T_M01_%s_%s" % (hero, role),
                role,
                role == "Normal",
            )
            textures[role] = texture
            hero_texture_paths[hero][role] = asset_path
            provenance.append({
                "provider": "Skyguard52_BlenderBake",
                "family": hero,
                "asset_page": None,
                "role": role,
                "source_path": str(source),
                "source_bytes": source.stat().st_size,
                "source_sha256": sha256(source),
                "unreal_asset": asset_path,
                "import_action": status,
                "resolution": [1024, 1024],
            })
        hero_materials[hero] = build_hero_material(hero, textures)[0]

    map_action = build_or_load_validation_map()

    materials = dict(poly_materials)
    materials.update(hero_materials)
    bindings = []
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        components = actor.get_components_by_class(unreal.StaticMeshComponent)
        for component in components:
            mesh = component.get_editor_property("static_mesh")
            if mesh is None:
                continue
            family = family_for_mesh(mesh.get_name())
            material = materials.get(family)
            if material is None:
                continue
            slots = assign_component_material(component, material)
            bindings.append({
                "actor": actor.get_actor_label(),
                "component": component.get_name(),
                "mesh": mesh.get_name(),
                "family": family,
                "material": material.get_path_name(),
                "slot_count": slots,
            })

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory(HERO_TEXTURE_ROOT, False, True)
    unreal.EditorAssetLibrary.save_directory(MATERIAL_ROOT, False, True)

    expected_meshes = {
        "SM_M01_Coast_Beach_Detailed_A",
        "SM_M01_Coast_Promenade_Detailed_A",
        "SM_M01_Coast_Seawall_Detailed_A",
        "SM_M01_Landmark_Lighthouse_Hero_A",
        "SM_M01_Landmark_RadarPost_Hero_A",
        "SM_M01_Road_CoastalTransition_Detailed_A",
        "SM_M01_Urban_Apartment_Detailed_A",
        "SM_M01_Urban_Apartment_Detailed_B",
        "SM_M01_Urban_Midrise_Damaged_A",
        "SM_M01_Urban_Midrise_Detailed_A",
        "SM_Boss_Pathfinder_Body_AAA",
        "SM_Boss_Pathfinder_CommandAntenna_AAA",
        "SM_Boss_Pathfinder_NoseCamera_AAA",
        "SM_Boss_Pathfinder_Engine_AAA",
        "SM_Boss_Pathfinder_ControlLinkage_AAA",
        "SM_Boss_Pathfinder_BreakChunk_Wing_L_AAA",
        "SM_Boss_Pathfinder_BreakChunk_Wing_R_AAA",
        "SM_Boss_Pathfinder_BreakChunk_Engine_AAA",
    }
    bound_meshes = {entry["mesh"] for entry in bindings}
    checks = {
        "hero_bake_fingerprint_matches": (
            hero_report["package_fingerprint_sha256"]
            == "3950bc25a3fb6fa0b1827b0b94a129292141289313f754f3b78f6b6ccbf63687"
        ),
        "polyhaven_sources_reused_not_duplicated": all(
            entry["import_action"] == "reused_existing_canonical_unreal_asset"
            for entry in provenance
            if entry["provider"] == "PolyHaven"
        ),
        "hero_texture_count": sum(
            1 for entry in provenance if entry["provider"] == "Skyguard52_BlenderBake"
        ) == 12,
        "all_expected_refined_meshes_bound": expected_meshes.issubset(bound_meshes),
        "material_validation_map_saved": unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH),
    }
    report = {
        "schema": "skyguard.m01.refinement.material-unreal-audit.v1",
        "refinement_manifest": str(REFINEMENT_MANIFEST_PATH),
        "geometry_builder": str(GEOMETRY_BUILDER_PATH),
        "map": MAP_PATH,
        "map_action": map_action,
        "polyhaven_family_count": len(POLYHAVEN),
        "hero_family_count": len(hero_materials),
        "material_count": len(materials),
        "texture_source_count": len(provenance),
        "bindings": bindings,
        "bound_mesh_count": len(bound_meshes),
        "provenance": provenance,
        "hero_manifest": str(HERO_MANIFEST_PATH),
        "hero_package_fingerprint_sha256": hero_report["package_fingerprint_sha256"],
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "promotion": "material_candidate_requires_rendered_visual_and_gpu_profile_acceptance",
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)

    # BC estimates: Base/Normal 8 bpp; scalar/mask 4 bpp. Full mip chain = 4/3.
    top_mip_bytes = 0
    for entry in provenance:
        width, height = entry["resolution"]
        bits_per_pixel = 4 if entry["role"] in {"Roughness", "ORM", "MaterialID"} else 8
        top_mip_bytes += width * height * bits_per_pixel // 8
    budget_checks = {
        "source_count_bounded": len(provenance) == 24,
        "hero_textures_are_1k": all(
            entry["resolution"] == [1024, 1024]
            for entry in provenance
            if entry["provider"] == "Skyguard52_BlenderBake"
        ),
        "polyhaven_textures_are_2k": all(
            entry["resolution"] == [2048, 2048]
            for entry in provenance
            if entry["provider"] == "PolyHaven"
        ),
        "estimated_full_mips_under_80_mib": (
            top_mip_bytes * 4.0 / 3.0 < 80 * 1024 * 1024
        ),
    }
    budget = {
        "schema": "skyguard.m01.refinement.texture-budget.v1",
        "texture_count": len(provenance),
        "polyhaven_reused_texture_count": 12,
        "hero_imported_or_reused_texture_count": 12,
        "source_disk_bytes": sum(entry["source_bytes"] for entry in provenance),
        "estimated_compressed_top_mip_bytes": top_mip_bytes,
        "estimated_compressed_full_mip_chain_bytes": int(top_mip_bytes * 4.0 / 3.0),
        "estimate_basis": "BC-family estimate only; final RHI residency requires runtime profile.",
        "checks": budget_checks,
        "gate": "READY_FOR_RUNTIME_PROFILE" if all(budget_checks.values()) else "BLOCKED",
    }
    with open(BUDGET_PATH, "w", encoding="utf-8") as stream:
        json.dump(budget, stream, indent=2)
    unreal.log("[SkyguardM01Materials] " + json.dumps(report))
    unreal.log("[SkyguardM01TextureBudget] " + json.dumps(budget))
    if report["gate"] != "PASS":
        raise RuntimeError("Mission 1 material Unreal gate failed")


if __name__ == "__main__":
    main()
