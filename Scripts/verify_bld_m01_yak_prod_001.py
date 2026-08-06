from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
from typing import Any


BUILD_ID = "BLD-M01-YAK-PROD-001"
CONTRACT_SCHEMA = "skyguard.blender-source-contract.v1"
ARTIFACT_SCHEMA = "skyguard.bld-m01-yak-prod-001.artifact-manifest.v1"
FORBIDDEN_IMPORT_CALLS = {
    "bpy.ops.import_scene.gltf",
    "bpy.ops.wm.link",
    "bpy.ops.wm.append",
    "bpy.data.libraries.load",
}
REQUIRED_GENERATOR_FUNCTIONS = {
    "require_blender_52",
    "verify_reference_only",
    "reset_factory_scene",
    "create_fuselage",
    "create_lifting_surface",
    "create_canopy_shell",
    "create_propeller",
    "create_rear_cockpit",
    "create_datums",
    "reject_forbidden_names",
    "validate_contract",
    "save_and_export",
    "write_manifest",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _call_name(node: ast.Call) -> str:
    parts: list[str] = []
    target: ast.AST = node.func
    while isinstance(target, ast.Attribute):
        parts.append(target.attr)
        target = target.value
    if isinstance(target, ast.Name):
        parts.append(target.id)
    return ".".join(reversed(parts))


def evaluate_source(contract: dict[str, Any], generator_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    checks: dict[str, bool] = {}
    checks["contract_schema"] = contract.get("schema") == CONTRACT_SCHEMA
    checks["build_id"] = contract.get("build_id") == BUILD_ID
    version = contract.get("blender_version", {})
    checks["blender_52_contract"] = (
        isinstance(version, dict)
        and version.get("major") == 5
        and version.get("minor") == 2
    )
    checks["generator_exists"] = generator_path.is_file()
    if not checks["generator_exists"]:
        errors.append(f"generator missing: {generator_path}")
        return {
            "gate": "FAIL",
            "artifact_gate": "NOT_RUN",
            "checks": checks,
            "errors": errors,
        }

    source = generator_path.read_text(encoding="utf-8-sig")
    try:
        tree = ast.parse(source, filename=str(generator_path))
        checks["generator_python_syntax"] = True
    except SyntaxError as exc:
        checks["generator_python_syntax"] = False
        errors.append(f"generator syntax error: {exc}")
        tree = ast.Module(body=[], type_ignores=[])

    functions = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }
    checks["required_generator_functions"] = REQUIRED_GENERATOR_FUNCTIONS.issubset(
        functions
    )

    calls = {
        _call_name(node) for node in ast.walk(tree) if isinstance(node, ast.Call)
    }
    forbidden_calls = sorted(FORBIDDEN_IMPORT_CALLS & calls)
    checks["no_external_geometry_import"] = not forbidden_calls
    if forbidden_calls:
        errors.append(f"forbidden geometry import/link calls: {forbidden_calls}")

    string_constants = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    required_meshes = set(contract.get("required_mesh_objects", []))
    required_sockets = set(contract.get("required_socket_objects", []))
    required_datums = set(contract.get("required_datum_objects", []))
    required_materials = set(contract.get("required_materials", []))
    checks["required_mesh_names_authored"] = required_meshes.issubset(
        string_constants
    )
    checks["required_socket_names_authored"] = required_sockets.issubset(
        string_constants
    )
    checks["required_datum_names_authored"] = required_datums.issubset(
        string_constants
    )
    checks["required_material_names_authored"] = required_materials.issubset(
        string_constants
    )
    checks["l88_hash_bound"] = (
        contract.get("l88_reference", {}).get("sha256") in string_constants
        or "verify_reference_only" in functions
    )
    reference_record = contract.get("l88_reference", {})
    reference_path = Path(str(reference_record.get("path", "")))
    if not reference_path.is_absolute():
        reference_path = generator_path.resolve().parents[1] / reference_path
    checks["l88_reference_exists"] = reference_path.is_file()
    checks["l88_reference_integrity"] = (
        checks["l88_reference_exists"]
        and sha256_file(reference_path)
        == str(reference_record.get("sha256", "")).lower()
    )
    checks["factory_scene_reset"] = "bpy.ops.wm.read_factory_settings" in calls
    checks["blend_save_present"] = "bpy.ops.wm.save_as_mainfile" in calls
    checks["glb_export_present"] = "bpy.ops.export_scene.gltf" in calls
    checks["manifest_write_present"] = "write_manifest" in functions

    dimensions = contract.get("reference_dimensions_m", {})
    tolerances = contract.get("dimension_tolerance_m", {})
    checks["dimension_contract"] = (
        isinstance(dimensions, dict)
        and set(dimensions)
        == {
            "overall_length",
            "wingspan",
            "overall_height",
            "propeller_diameter",
            "rear_cockpit_clear_width",
            "rear_cockpit_rail_height",
        }
        and all(isinstance(value, (int, float)) and value > 0 for value in dimensions.values())
        and isinstance(tolerances, dict)
        and set(tolerances) == set(dimensions)
    )
    checks["minimum_vertex_contract"] = set(
        contract.get("minimum_mesh_vertices", {})
    ).issubset(required_meshes)
    checks["forbidden_name_contract"] = {
        "blockout",
        "proxy",
        "placeholder",
        "temp",
        "default",
        "cube",
    }.issubset(set(contract.get("forbidden_name_tokens", [])))
    checks["outputs_are_new_production_paths"] = all(
        "Yak52_Production" in path or "BLD_M01_YAK_PROD_001" in path
        for path in contract.get("outputs", {}).values()
    )

    for name, passed in checks.items():
        if not passed and name not in {"generator_exists"}:
            errors.append(f"source check failed: {name}")
    return {
        "schema": "skyguard.bld-m01-yak-prod-001.source-audit.v1",
        "build_id": BUILD_ID,
        "gate": "PASS" if not errors else "FAIL",
        "artifact_gate": "NOT_RUN",
        "generator": str(generator_path),
        "generator_sha256": sha256_file(generator_path),
        "checks": checks,
        "errors": errors,
    }


def _validate_bound_file(record: Any) -> bool:
    if not isinstance(record, dict):
        return False
    path = Path(str(record.get("path", "")))
    return (
        path.is_file()
        and path.stat().st_size == record.get("bytes")
        and sha256_file(path) == str(record.get("sha256", "")).lower()
    )


def evaluate_artifacts(
    contract: dict[str, Any], manifest: dict[str, Any]
) -> dict[str, Any]:
    errors: list[str] = []
    checks: dict[str, bool] = {}
    checks["artifact_schema"] = manifest.get("schema") == ARTIFACT_SCHEMA
    checks["build_id"] = manifest.get("build_id") == BUILD_ID
    version = str(manifest.get("blender_version", ""))
    checks["blender_52"] = version.startswith("5.2.")
    checks["l88_reference_hash"] = (
        manifest.get("l88_reference", {}).get("sha256")
        == contract.get("l88_reference", {}).get("sha256")
        and manifest.get("l88_reference", {}).get("use")
        == "datum_reference_only_not_imported"
    )
    outputs = manifest.get("outputs", {})
    checks["blend_integrity"] = _validate_bound_file(outputs.get("blend"))
    checks["glb_integrity"] = _validate_bound_file(outputs.get("glb"))

    objects = manifest.get("objects")
    if not isinstance(objects, list):
        objects = []
    object_names = [
        item.get("name") for item in objects if isinstance(item, dict)
    ]
    object_map = {
        item.get("name"): item
        for item in objects
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    checks["unique_object_names"] = len(object_names) == len(set(object_names))
    checks["required_meshes"] = set(contract["required_mesh_objects"]).issubset(
        object_map
    )
    checks["required_sockets"] = set(contract["required_socket_objects"]).issubset(
        object_map
    )
    checks["required_datums"] = set(contract["required_datum_objects"]).issubset(
        object_map
    )
    checks["mesh_types"] = all(
        object_map.get(name, {}).get("type") == "MESH"
        for name in contract["required_mesh_objects"]
    )
    checks["socket_types"] = all(
        object_map.get(name, {}).get("type") == "EMPTY"
        for name in contract["required_socket_objects"]
    )
    checks["datum_types"] = all(
        object_map.get(name, {}).get("type") == "EMPTY"
        for name in contract["required_datum_objects"]
    )
    required_uv = contract["required_uv_layer"]
    checks["uv_complete"] = all(
        required_uv in object_map.get(name, {}).get("uv_layers", [])
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

    forbidden_tokens = [
        token.lower() for token in contract.get("forbidden_name_tokens", [])
    ]
    violations = [
        name
        for name in object_names
        if isinstance(name, str)
        and any(token in name.lower() for token in forbidden_tokens)
    ]
    checks["blockout_name_rejection"] = (
        not violations and not manifest.get("forbidden_name_violations")
    )

    reference = contract["reference_dimensions_m"]
    tolerance = contract["dimension_tolerance_m"]
    measured = manifest.get("measured_dimensions_m", {})
    dimension_results = {}
    for key, expected in reference.items():
        actual = measured.get(key)
        dimension_results[key] = (
            isinstance(actual, (int, float))
            and abs(float(actual) - float(expected)) <= float(tolerance[key])
        )
    checks["dimensions"] = all(dimension_results.values())
    validation = manifest.get("validation", {})
    checks["generator_validation"] = (
        isinstance(validation, dict)
        and validation.get("pass") is True
        and not validation.get("missing_meshes")
        and not validation.get("missing_sockets")
        and not validation.get("missing_datums")
        and not validation.get("uv_failures")
        and not validation.get("material_failures")
        and not validation.get("minimum_vertex_failures")
    )
    checks["candidate_not_final_promotion"] = (
        manifest.get("promotion") == contract.get("promotion")
        and "candidate" in str(manifest.get("promotion", ""))
        and "unreal" in str(manifest.get("promotion", "")).lower()
    )

    for name, passed in checks.items():
        if not passed:
            errors.append(f"artifact check failed: {name}")
    return {
        "schema": "skyguard.bld-m01-yak-prod-001.artifact-audit.v1",
        "build_id": BUILD_ID,
        "gate": "PASS" if not errors else "FAIL",
        "artifact_gate": "PASS" if not errors else "FAIL",
        "checks": checks,
        "dimension_results": dimension_results,
        "forbidden_name_violations": violations,
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Offline verifier for BLD-M01-YAK-PROD-001."
    )
    parser.add_argument(
        "--contract",
        type=Path,
        default=root
        / "Docs"
        / "AAA_Review"
        / "BLD_M01_YAK_PROD_001_CONTRACT.json",
    )
    parser.add_argument(
        "--generator",
        type=Path,
        default=root / "Scripts" / "blender_bld_m01_yak_prod_001.py",
    )
    parser.add_argument(
        "--artifact-manifest",
        type=Path,
        help="Optional Blender-produced manifest. Omit for source-only audit.",
    )
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8-sig"))
    source_report = evaluate_source(contract, args.generator)
    if source_report["gate"] != "PASS" or args.artifact_manifest is None:
        print(json.dumps(source_report, indent=2, sort_keys=True))
        return 0 if source_report["gate"] == "PASS" else 1
    manifest = json.loads(
        args.artifact_manifest.read_text(encoding="utf-8-sig")
    )
    artifact_report = evaluate_artifacts(contract, manifest)
    artifact_report["source_audit"] = source_report
    print(json.dumps(artifact_report, indent=2, sort_keys=True))
    return 0 if artifact_report["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
