from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
from typing import Any


BUILD_ID = "BLD-M01-YAK-PROD-002"
CONTRACT_SCHEMA = "skyguard.blender-source-contract.v1"
ARTIFACT_SCHEMA = "skyguard.bld-m01-yak-prod-002.artifact-manifest.v1"
REQUIRED_FUNCTIONS = {
    "verify_source_lineage",
    "require_blender_52",
    "reset_factory_scene",
    "create_refined_fuselage",
    "create_radial_cowling",
    "create_propeller",
    "create_wings_and_tail",
    "create_vertical_tail",
    "create_canopy",
    "create_rear_cockpit",
    "create_landing_gear",
    "create_datums",
    "apply_decal_metadata",
    "reject_forbidden_names",
    "validate_contract",
    "save_and_export",
    "write_manifest",
}
FORBIDDEN_CALLS = {
    "bpy.ops.import_scene.gltf",
    "bpy.ops.wm.open_mainfile",
    "bpy.ops.wm.append",
    "bpy.ops.wm.link",
    "bpy.data.libraries.load",
    "base.create_aircraft",
    "base.create_fuselage",
    "base.create_propeller",
    "base.create_rear_cockpit",
    "base.create_datums",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve(root: Path, raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else root / path


def _call_name(node: ast.Call) -> str:
    parts: list[str] = []
    target: ast.AST = node.func
    while isinstance(target, ast.Attribute):
        parts.append(target.attr)
        target = target.value
    if isinstance(target, ast.Name):
        parts.append(target.id)
    return ".".join(reversed(parts))


def _bound_file_ok(root: Path, record: Any) -> bool:
    if not isinstance(record, dict):
        return False
    path = _resolve(root, str(record.get("path", "")))
    return (
        path.is_file()
        and path.stat().st_size == record.get("bytes")
        and sha256_file(path) == str(record.get("sha256", "")).lower()
    )


def evaluate_source(
    contract: dict[str, Any], generator_path: Path, root: Path
) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    errors: list[str] = []
    checks["contract_schema"] = contract.get("schema") == CONTRACT_SCHEMA
    checks["build_id"] = contract.get("build_id") == BUILD_ID
    checks["source_only_status"] = contract.get("status") == "source_only_not_run"
    version = contract.get("blender_version", {})
    checks["blender_52_contract"] = (
        isinstance(version, dict)
        and version.get("major") == 5
        and version.get("minor") == 2
    )
    checks["generator_exists"] = generator_path.is_file()
    if not generator_path.is_file():
        return {
            "schema": "skyguard.bld-m01-yak-prod-002.source-audit.v1",
            "gate": "FAIL",
            "artifact_gate": "NOT_RUN",
            "checks": checks,
            "errors": [f"generator missing: {generator_path}"],
        }
    source = generator_path.read_text(encoding="utf-8-sig")
    try:
        tree = ast.parse(source, filename=str(generator_path))
        checks["generator_python_syntax"] = True
    except SyntaxError as exc:
        tree = ast.Module(body=[], type_ignores=[])
        checks["generator_python_syntax"] = False
        errors.append(f"generator syntax error: {exc}")

    functions = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }
    calls = {
        _call_name(node) for node in ast.walk(tree) if isinstance(node, ast.Call)
    }
    strings = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    checks["required_functions"] = REQUIRED_FUNCTIONS.issubset(functions)
    forbidden_used = sorted(FORBIDDEN_CALLS & calls)
    checks["no_001_or_l88_geometry_import"] = not forbidden_used
    if forbidden_used:
        errors.append(f"forbidden geometry promotion calls: {forbidden_used}")
    checks["clean_factory_scene"] = "bpy.ops.wm.read_factory_settings" in calls
    checks["blend_save"] = "bpy.ops.wm.save_as_mainfile" in calls
    checks["glb_export"] = "bpy.ops.export_scene.gltf" in calls

    required_meshes = set(contract.get("required_mesh_objects", []))
    required_sockets = set(contract.get("required_socket_objects", []))
    required_datums = set(contract.get("required_datum_objects", []))
    required_materials = set(contract.get("required_materials", []))
    checks["required_mesh_names_authored"] = required_meshes.issubset(strings)
    checks["required_socket_names_authored"] = required_sockets.issubset(strings)
    checks["required_datum_names_authored"] = required_datums.issubset(strings)
    checks["required_material_names_authored"] = required_materials.issubset(strings)

    base_record = contract.get("base_source_reference", {})
    l88_record = contract.get("l88_reference", {})
    checks["base_source_hash"] = (
        _resolve(root, str(base_record.get("path", ""))).is_file()
        and sha256_file(_resolve(root, str(base_record.get("path", ""))))
        == str(base_record.get("sha256", "")).lower()
    )
    checks["l88_reference_hash"] = (
        _resolve(root, str(l88_record.get("path", ""))).is_file()
        and sha256_file(_resolve(root, str(l88_record.get("path", ""))))
        == str(l88_record.get("sha256", "")).lower()
    )
    review_records = contract.get("review_evidence", [])
    checks["three_review_renders"] = (
        isinstance(review_records, list) and len(review_records) == 3
    )
    checks["review_render_integrity"] = checks["three_review_renders"] and all(
        _bound_file_ok(root, record) for record in review_records
    )
    checks["review_findings_present"] = checks["three_review_renders"] and all(
        isinstance(record.get("finding"), str) and bool(record["finding"].strip())
        for record in review_records
    )

    dimensions = contract.get("reference_dimensions_m", {})
    tolerances = contract.get("dimension_tolerance_m", {})
    checks["dimension_contract"] = (
        isinstance(dimensions, dict)
        and len(dimensions) == 6
        and all(isinstance(value, (int, float)) and value > 0 for value in dimensions.values())
        and isinstance(tolerances, dict)
        and set(tolerances) == set(dimensions)
    )
    checks["movable_parts_contract"] = (
        isinstance(contract.get("movable_parts"), dict)
        and len(contract["movable_parts"]) >= 20
        and set(contract["movable_parts"]).issubset(required_meshes)
        and isinstance(contract.get("movable_pivot_positions_m"), dict)
        and set(contract["movable_pivot_positions_m"])
        == set(contract["movable_parts"])
        and all(
            isinstance(position, list)
            and len(position) == 3
            and all(isinstance(value, (int, float)) for value in position)
            for position in contract["movable_pivot_positions_m"].values()
        )
    )
    checks["decal_contract"] = (
        isinstance(contract.get("decal_ready_objects"), list)
        and bool(contract["decal_ready_objects"])
        and set(contract["decal_ready_objects"]).issubset(required_meshes)
        and contract.get("material_id_contract", {}).get("panel_line_decal") == 100
        and contract.get("material_id_contract", {}).get("rivet_decal") == 101
    )
    checks["minimum_vertex_contract"] = set(
        contract.get("minimum_mesh_vertices", {})
    ).issubset(required_meshes)
    checks["output_isolation"] = all(
        "002" in value for value in contract.get("outputs", {}).values()
    )
    checks["candidate_promotion_only"] = (
        "candidate" in str(contract.get("promotion", ""))
        and "unreal" in str(contract.get("promotion", "")).lower()
        and "final" not in str(contract.get("promotion", "")).lower()
    )

    for name, passed in checks.items():
        if not passed:
            errors.append(f"source check failed: {name}")
    return {
        "schema": "skyguard.bld-m01-yak-prod-002.source-audit.v1",
        "build_id": BUILD_ID,
        "gate": "PASS" if not errors else "FAIL",
        "artifact_gate": "NOT_RUN",
        "generator": str(generator_path),
        "generator_sha256": sha256_file(generator_path),
        "checks": checks,
        "errors": errors,
    }


def evaluate_artifacts(
    contract: dict[str, Any], manifest: dict[str, Any], root: Path
) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    errors: list[str] = []
    checks["artifact_schema"] = manifest.get("schema") == ARTIFACT_SCHEMA
    checks["build_id"] = manifest.get("build_id") == BUILD_ID
    checks["blender_52"] = str(manifest.get("blender_version", "")).startswith("5.2.")
    checks["base_source_helpers_only"] = (
        manifest.get("base_source_reference", {}).get("sha256")
        == contract.get("base_source_reference", {}).get("sha256")
        and manifest.get("base_source_reference", {}).get("use")
        == "python_helpers_only_no_001_artifact_or_datablock_import"
    )
    checks["l88_datum_only"] = (
        manifest.get("l88_reference", {}).get("sha256")
        == contract.get("l88_reference", {}).get("sha256")
        and manifest.get("l88_reference", {}).get("use")
        == "datum_reference_only_not_imported"
    )
    checks["blend_integrity"] = _bound_file_ok(root, manifest.get("outputs", {}).get("blend"))
    checks["glb_integrity"] = _bound_file_ok(root, manifest.get("outputs", {}).get("glb"))

    objects = manifest.get("objects", [])
    if not isinstance(objects, list):
        objects = []
    object_names = [
        item.get("name") for item in objects if isinstance(item, dict)
    ]
    object_map = {
        item["name"]: item
        for item in objects
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    checks["unique_object_names"] = len(object_names) == len(set(object_names))
    checks["required_meshes"] = set(contract["required_mesh_objects"]).issubset(object_map)
    checks["required_sockets"] = set(contract["required_socket_objects"]).issubset(object_map)
    checks["required_datums"] = set(contract["required_datum_objects"]).issubset(object_map)
    checks["mesh_types"] = all(
        object_map.get(name, {}).get("type") == "MESH"
        for name in contract["required_mesh_objects"]
    )
    checks["empty_types"] = all(
        object_map.get(name, {}).get("type") == "EMPTY"
        for name in contract["required_socket_objects"] + contract["required_datum_objects"]
    )
    checks["uv_complete"] = all(
        contract["required_uv_layer"] in object_map.get(name, {}).get("uv_layers", [])
        for name in contract["required_mesh_objects"]
    )
    checks["material_slots_complete"] = all(
        bool(object_map.get(name, {}).get("material_slots"))
        for name in contract["required_mesh_objects"]
    )
    checks["minimum_vertices"] = all(
        object_map.get(name, {}).get("vertices", -1) >= minimum
        for name, minimum in contract["minimum_mesh_vertices"].items()
    )

    forbidden = [token.lower() for token in contract["forbidden_name_tokens"]]
    violations = [
        name
        for name in object_names
        if isinstance(name, str)
        and any(token in name.lower() for token in forbidden)
    ]
    checks["forbidden_names"] = (
        not violations and not manifest.get("forbidden_name_violations")
    )

    movable_failures = []
    pivot_position_failures = []
    for name, pivot in contract["movable_parts"].items():
        record = object_map.get(name, {})
        custom = record.get("custom_properties", {})
        if custom.get("SKG_Movable") is not True or custom.get("SKG_PivotRole") != pivot:
            movable_failures.append(name)
        actual_location = record.get("location_m")
        expected_location = contract["movable_pivot_positions_m"][name]
        if (
            not isinstance(actual_location, list)
            or len(actual_location) != 3
            or any(
                not isinstance(value, (int, float))
                for value in actual_location
            )
            or any(
                abs(float(actual) - float(expected)) > 0.005
                for actual, expected in zip(actual_location, expected_location)
            )
        ):
            pivot_position_failures.append(name)
    checks["movable_parts"] = not movable_failures
    checks["movable_pivot_positions"] = not pivot_position_failures

    decal_failures = []
    for name in contract["decal_ready_objects"]:
        record = object_map.get(name, {})
        custom = record.get("custom_properties", {})
        slots = set(record.get("material_slots", []))
        if (
            custom.get("SKG_DecalReady") is not True
            or custom.get("SKG_MaterialID_PanelLine") != 100
            or custom.get("SKG_MaterialID_Rivet") != 101
            or "MAT002_PanelLine" not in slots
            or "MAT002_Rivet" not in slots
        ):
            decal_failures.append(name)
    checks["decal_metadata"] = not decal_failures

    measured = manifest.get("measured_dimensions_m", {})
    dimension_results = {}
    for key, expected in contract["reference_dimensions_m"].items():
        actual = measured.get(key)
        dimension_results[key] = (
            isinstance(actual, (int, float))
            and abs(float(actual) - float(expected))
            <= float(contract["dimension_tolerance_m"][key])
        )
    checks["dimensions"] = all(dimension_results.values())
    validation = manifest.get("validation", {})
    checks["generator_validation"] = (
        isinstance(validation, dict)
        and validation.get("pass") is True
        and not any(
            validation.get(key)
            for key in (
                "missing_meshes",
                "missing_sockets",
                "missing_datums",
                "uv_failures",
                "material_failures",
                "minimum_vertex_failures",
                "movable_failures",
                "pivot_position_failures",
                "decal_failures",
            )
        )
    )
    checks["candidate_not_final"] = (
        manifest.get("promotion") == contract.get("promotion")
        and "candidate" in str(manifest.get("promotion", ""))
        and "final" not in str(manifest.get("promotion", "")).lower()
    )
    for name, passed in checks.items():
        if not passed:
            errors.append(f"artifact check failed: {name}")
    return {
        "schema": "skyguard.bld-m01-yak-prod-002.artifact-audit.v1",
        "build_id": BUILD_ID,
        "gate": "PASS" if not errors else "FAIL",
        "artifact_gate": "PASS" if not errors else "FAIL",
        "checks": checks,
        "dimension_results": dimension_results,
        "forbidden_name_violations": violations,
        "movable_failures": movable_failures,
        "pivot_position_failures": pivot_position_failures,
        "decal_failures": decal_failures,
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Offline source/artifact verifier for BLD-M01-YAK-PROD-002."
    )
    parser.add_argument(
        "--contract",
        type=Path,
        default=root / "Docs" / "AAA_Review" / "BLD_M01_YAK_PROD_002_CONTRACT.json",
    )
    parser.add_argument(
        "--generator",
        type=Path,
        default=root / "Scripts" / "blender_bld_m01_yak_prod_002.py",
    )
    parser.add_argument("--artifact-manifest", type=Path)
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8-sig"))
    source_report = evaluate_source(contract, args.generator, root)
    if source_report["gate"] != "PASS" or args.artifact_manifest is None:
        print(json.dumps(source_report, indent=2, sort_keys=True))
        return 0 if source_report["gate"] == "PASS" else 1
    manifest = json.loads(args.artifact_manifest.read_text(encoding="utf-8-sig"))
    artifact_report = evaluate_artifacts(contract, manifest, root)
    artifact_report["source_audit"] = source_report
    print(json.dumps(artifact_report, indent=2, sort_keys=True))
    return 0 if artifact_report["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
