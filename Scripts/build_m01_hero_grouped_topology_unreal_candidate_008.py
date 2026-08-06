"""Build the isolated Build 008 Unreal candidate. Never run outside its supervisor."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import unreal


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Scripts"))
from audit_m01_hero_grouped_topology_unreal_acceptance_008 import (  # noqa: E402
    CONTRACT_PATH,
    audit_source,
    load_json,
)

BUILD_REPORT = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_CANDIDATE_008_BUILD.json"
CANDIDATE_ROOT = "/Game/Skyguard/Candidates/Mission01/HeroGroupedTopology_008"


def fail(message: str) -> None:
    raise RuntimeError("[M01Grouped008] " + message)


def ensure_dir(path: str) -> None:
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def asset_name(path: str) -> str:
    return path.rsplit("/", 1)[-1].split(".")[0]


def import_file(source: Path, destination: str, destination_name: str = "") -> list[str]:
    task = unreal.AssetImportTask()
    task.filename = str(source)
    task.destination_path = destination
    task.destination_name = destination_name
    task.automated = True
    task.replace_existing = False
    task.save = False
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    return list(task.imported_object_paths or [])


def texture_settings(texture, map_type: str) -> None:
    texture.set_editor_property("srgb", False)
    texture.set_editor_property("virtual_texture_streaming", False)
    if map_type == "Normal":
        texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
        texture.set_editor_property("flip_green_channel", True)
    else:
        texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
    unreal.EditorAssetLibrary.save_loaded_asset(texture, False)


def create_material(path: str, normal, ao):
    folder, name = path.rsplit("/", 1)
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        name, folder, unreal.Material, unreal.MaterialFactoryNew()
    )
    if material is None:
        fail("material creation failed: " + path)
    mel = unreal.MaterialEditingLibrary
    base = mel.create_material_expression(material, unreal.MaterialExpressionConstant3Vector, -500, -180)
    base.set_editor_property("constant", unreal.LinearColor(0.32, 0.34, 0.36, 1.0))
    normal_sample = mel.create_material_expression(material, unreal.MaterialExpressionTextureSample, -500, 20)
    normal_sample.set_editor_property("texture", normal)
    normal_sample.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    ao_sample = mel.create_material_expression(material, unreal.MaterialExpressionTextureSample, -500, 220)
    ao_sample.set_editor_property("texture", ao)
    mel.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(normal_sample, "RGB", unreal.MaterialProperty.MP_NORMAL)
    mel.connect_material_property(ao_sample, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
    mel.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material, False)
    return material


def bounds_cm(mesh) -> list[float]:
    extent = mesh.get_bounds().box_extent
    return [abs(float(extent.x)) * 2.0, abs(float(extent.y)) * 2.0, abs(float(extent.z)) * 2.0]


def simple_collision_count(mesh) -> int:
    body_setup = mesh.get_editor_property("body_setup")
    aggregate = body_setup.get_editor_property("agg_geom")
    total = 0
    for field in (
        "box_elems",
        "sphere_elems",
        "sphyl_elems",
        "convex_elems",
        "tapered_capsule_elems",
    ):
        try:
            total += len(aggregate.get_editor_property(field))
        except Exception:
            pass
    return total


def force_clear_simple_collision(mesh) -> None:
    """Clear imported primitive arrays even when the commandlet facade is stale."""
    body_setup = mesh.get_editor_property("body_setup")
    aggregate = body_setup.get_editor_property("agg_geom")
    for field in (
        "box_elems",
        "sphere_elems",
        "sphyl_elems",
        "convex_elems",
        "tapered_capsule_elems",
    ):
        try:
            aggregate.set_editor_property(field, [])
        except Exception:
            pass
    body_setup.set_editor_property("agg_geom", aggregate)


def configure_collision(mesh, mode: str) -> int:
    subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    if subsystem is not None:
        subsystem.remove_collisions(mesh)
        add_collision = subsystem.add_simple_collisions
    else:
        # PythonScriptCommandlet does not initialize EditorSubsystems in UE
        # 5.8. The deprecated static facade remains the commandlet-safe bridge
        # to the same StaticMeshEditor collision implementation.
        legacy = getattr(unreal, "EditorStaticMeshLibrary", None)
        if legacy is None:
            fail("no commandlet-safe static-mesh collision API is available")
        legacy.remove_collisions(mesh)
        add_collision = legacy.add_simple_collisions
    if mode == "NONE":
        force_clear_simple_collision(mesh)
        primitive_count = simple_collision_count(mesh)
        if primitive_count != 0:
            fail("NONE collision policy retained simple primitives")
        return primitive_count
    shape = {
        "BOX": unreal.ScriptingCollisionShapeType.BOX,
        "NDOP26": unreal.ScriptingCollisionShapeType.NDOP26,
    }[mode]
    result = add_collision(mesh, shape)
    # Commandlet collision generation is finalized asynchronously when the
    # mesh package is saved. The legacy facade can return -1 even when the
    # generated primitive persists. The fresh-process verifier is the sole
    # authority for positive primitive counts; only NONE is synchronous.
    return int(result)


def main() -> None:
    contract = load_json(CONTRACT_PATH)
    if contract["unreal"]["candidate_root"] != CANDIDATE_ROOT:
        fail("candidate root differs from source-audited builder")
    manifest = load_json(ROOT / contract["bound_sources"]["manifest"]["path"])
    audit = audit_source(write_report=False)
    if audit["gate"] != "PASS_OFFLINE_READY_AWAITING_SEPARATE_UNREAL_AUTHORIZATION":
        fail("offline readiness failed")
    candidate = contract["unreal"]["candidate_root"]
    if unreal.EditorAssetLibrary.does_directory_exist(candidate):
        existing = unreal.EditorAssetLibrary.list_assets(candidate, True, False)
        if existing:
            fail("candidate root is non-empty; preserve and review it, never overwrite")
    for path in (
        candidate,
        contract["unreal"]["mesh_root"],
        contract["unreal"]["texture_root"],
        contract["unreal"]["material_root"],
        candidate + "/Review",
    ):
        ensure_dir(path)

    import_file(ROOT / contract["bound_sources"]["low_glb"]["path"], contract["unreal"]["mesh_root"])
    mesh_assets = {}
    extras = []
    for path in unreal.EditorAssetLibrary.list_assets(contract["unreal"]["mesh_root"], True, False):
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if isinstance(asset, unreal.StaticMesh):
            mesh_assets[asset.get_name()] = path
        else:
            extras.append(path)
    for path in extras:
        if not unreal.EditorAssetLibrary.delete_asset(path):
            fail("could not remove imported support asset " + path)

    groups = [
        (asset["id"], group["id"], group)
        for asset in manifest["assets"]
        for group in asset["groups"]
    ]
    expected_sources = {group["low"]["object"] for _, _, group in groups}
    if set(mesh_assets) != expected_sources:
        fail("imported mesh set differs from the exact 12-object manifest")

    configured = []
    materials = {}
    texture_records = []
    for family, group_id, group in groups:
        key = f"{family}/{group_id}"
        source_path = mesh_assets[group["low"]["object"]]
        target_name = contract["mesh_targets"][key]
        target_path = contract["unreal"]["mesh_root"] + "/" + target_name
        if not unreal.EditorAssetLibrary.rename_asset(source_path, target_path):
            fail("mesh rename failed: " + key)
        mesh = unreal.EditorAssetLibrary.load_asset(target_path)
        if not isinstance(mesh, unreal.StaticMesh):
            fail("renamed asset is not StaticMesh: " + target_path)

        maps = {}
        for item in group["maps"]:
            map_type = item["type"]
            destination = f"{contract['unreal']['texture_root']}/{family}/{group_id}"
            ensure_dir(destination)
            name = f"T_M01C008_{family}_{group_id}_{map_type}"
            imported = import_file(Path(item["path"]), destination, name)
            texture_path = destination + "/" + name
            texture = unreal.EditorAssetLibrary.load_asset(texture_path)
            if not isinstance(texture, unreal.Texture2D):
                fail("texture import failed: " + texture_path)
            texture_settings(texture, map_type)
            maps[map_type] = texture
            texture_records.append({
                "key": f"{key}/{map_type}",
                "source": item["path"],
                "source_sha256": item["sha256"],
                "asset": texture_path,
                "imported_objects": imported,
            })

        material_path = contract["unreal"]["material_root"] + f"/M_M01C008_{family}_{group_id}"
        material = create_material(material_path, maps["Normal"], maps["AO"])
        materials[key] = material_path
        slots = len(mesh.get_editor_property("static_materials"))
        for index in range(slots):
            mesh.set_material(index, material)

        collision_primitives = configure_collision(mesh, contract["mesh_policy"]["collision"][key])
        settings = mesh.get_editor_property("nanite_settings")
        settings.enabled = key in contract["mesh_policy"]["nanite"]["enabled_groups"]
        mesh.set_editor_property("nanite_settings", settings)
        unreal.EditorAssetLibrary.set_metadata_tag(mesh, "Skyguard.BuildId", contract["build_id"])
        unreal.EditorAssetLibrary.set_metadata_tag(mesh, "Skyguard.SourceSha256", contract["bound_sources"]["low_glb"]["sha256"])
        unreal.EditorAssetLibrary.set_metadata_tag(mesh, "Skyguard.SemanticGroup", key)
        unreal.EditorAssetLibrary.set_metadata_tag(mesh, "Skyguard.PromotionAllowed", "false")
        unreal.EditorAssetLibrary.save_loaded_asset(mesh, False)

        actual = bounds_cm(mesh)
        expected = [float(value) * 100.0 for value in group["low"]["dimensions_m"]]
        errors = [
            abs(a - e) / max(e, 0.001)
            for a, e in zip(sorted(actual), sorted(expected))
        ]
        configured.append({
            "key": key,
            "asset": target_path,
            "triangles": group["low"]["triangles"],
            "expected_dimensions_cm": expected,
            "actual_dimensions_cm": actual,
            "maximum_dimension_relative_error": max(errors),
            "collision": contract["mesh_policy"]["collision"][key],
            "collision_primitives": collision_primitives,
            "nanite_enabled": bool(settings.enabled),
            "material": material_path,
            "material_slots": slots,
        })

    map_path = contract["unreal"]["review_map"]
    if unreal.EditorAssetLibrary.does_asset_exist(map_path):
        fail("candidate review map already exists")
    if not unreal.EditorLevelLibrary.new_level(map_path):
        fail("candidate review map creation failed")
    offsets = {"Pathfinder": (0.0, 0.0, 0.0), "Lighthouse": (3000.0, 0.0, 0.0), "RadarPost": (6000.0, 0.0, 0.0)}
    for entry in configured:
        family = entry["key"].split("/", 1)[0]
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.StaticMeshActor, unreal.Vector(*offsets[family]), unreal.Rotator()
        )
        actor.set_actor_label("M01C008_" + entry["key"].replace("/", "_"))
        actor.static_mesh_component.set_static_mesh(unreal.EditorAssetLibrary.load_asset(entry["asset"]))
    unreal.EditorLevelLibrary.save_current_level()
    if not unreal.EditorAssetLibrary.save_directory(candidate, False, True):
        fail("candidate directory save failed")

    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-candidate-build.v1",
        "gate": "PASS_CANDIDATE_BUILD_REQUIRES_FRESH_PROCESS_AUDIT",
        "build_id": contract["build_id"],
        "candidate_root": candidate,
        "source_glb_sha256": contract["bound_sources"]["low_glb"]["sha256"],
        "manifest_sha256": contract["bound_sources"]["manifest"]["sha256"],
        "meshes": configured,
        "textures": texture_records,
        "materials": materials,
        "review_map": map_path,
        "runtime_map_changed": False,
        "config_changed": False,
        "promotion_allowed": False,
        "p3_4_closed": False,
    }
    BUILD_REPORT.parent.mkdir(parents=True, exist_ok=True)
    BUILD_REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    unreal.log("[M01Grouped008] " + report["gate"])


if __name__ == "__main__":
    main()
