"""Offline readiness gate for Yak-52 R4 Slice 01.

This verifier never imports bpy and never launches Blender or Unreal. It
validates the frozen authorities, deterministic authoring source, output
namespace, missing-reference truth boundary, and canonical-output absence.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BUILD_ID = "BLD-M01-YAK-FINAL-ART-R4-S01"
CONTRACT_REL = Path(
    "Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_OUTPUT_CONTRACT.json"
)
LEDGER_REL = Path(
    "Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_DIMENSION_LEDGER.json"
)
CAMERA_REL = Path(
    "Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_CAMERA_MANIFEST.json"
)
R4_REL = Path(
    "Docs/AAA_Review/PHASE2_YAK52_R4_OFFLINE_PRODUCTION_CONTRACT.json"
)
REPORT_ROOT_REL = Path("Saved/Reports/Phase2Yak52R4Slice01Readiness")

EXPECTED_DIMENSIONS = {
    "overall_length": (7.745, 0.08),
    "wingspan": (9.3, 0.08),
    "overall_height": (2.7, 0.08),
    "propeller_diameter": (2.4, 0.05),
    "rear_cockpit_clear_width": (0.72, 0.04),
    "rear_cockpit_rail_height": (1.34, 0.04),
}
EXPECTED_COLLECTIONS = {
    "R4_S01_ROOT",
    "R4_S01_GEOMETRY",
    "R4_S01_PRIMARY",
    "R4_S01_REFERENCE",
    "R4_S01_DATUMS",
    "R4_S01_CAMERAS",
    "R4_S01_LIGHTING",
}
EXPECTED_PRIMARY_OBJECTS = {
    "GEO_R4S01_FuselagePrimary",
    "GEO_R4S01_CowlingEnvelope",
    "GEO_R4S01_WingPrimary_L",
    "GEO_R4S01_WingPrimary_R",
    "GEO_R4S01_HorizontalTail_L",
    "GEO_R4S01_HorizontalTail_R",
    "GEO_R4S01_VerticalTail",
    "GEO_R4S01_CanopyEnvelope_Front",
    "GEO_R4S01_CanopyEnvelope_Rear",
    "GEO_R4S01_GearEnvelope_Main_L",
    "GEO_R4S01_GearEnvelope_Main_R",
    "GEO_R4S01_GearEnvelope_Nose",
    "GEO_R4S01_PropellerDisc",
}
EXPECTED_DATUMS = {
    "DATUM_R4S01_AircraftOrigin",
    "DATUM_R4S01_TailExtreme",
    "DATUM_R4S01_PropellerPlane",
    "DATUM_R4S01_WingReference",
}
EXPECTED_MATERIALS = {
    "MAT_R4S01_PrimaryNeutral",
    "MAT_R4S01_CanopyNeutral",
    "MAT_R4S01_GearNeutral",
}
EXPECTED_CAMERAS = [
    "R4_CAM_BEAUTY_PORT",
    "R4_CAM_SIDE_ORTHO",
    "R4_CAM_TOP_ORTHO",
    "R4_CAM_REAR_QUARTER",
    "R4_CAM_UNDERSIDE_ORTHO",
]
EXPECTED_RENDER_OUTPUTS = [
    "R4S01_BeautyPort.png",
    "R4S01_SideOrtho.png",
    "R4S01_TopOrtho.png",
    "R4S01_RearQuarter.png",
    "R4S01_UndersideOrtho.png",
]
REQUIRED_MISSING_REFERENCE_FIELDS = {
    "orthographic_or_dimensioned_drawing",
    "cleared_port_side_photo",
    "cleared_top_or_high_oblique_photo",
    "cleared_front_three_quarter_photo",
    "cleared_rear_three_quarter_photo",
    "cleared_underside_or_gear_photo",
    "primary_dimension_source",
}
FALSE_CLAIMS = {
    "blender_launched",
    "unreal_launched",
    "outputs_created",
    "reference_package_complete",
    "silhouette_locked",
    "slice01_human_accepted",
    "final",
    "aaa",
    "unreal_imported",
    "runtime_replaced",
    "promotion_allowed",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _same_number(left: Any, right: Any) -> bool:
    try:
        return abs(float(left) - float(right)) <= 1e-9
    except (TypeError, ValueError):
        return False


def _set_or_empty(value: Any) -> set[str]:
    return set(value) if isinstance(value, list) else set()


def validate_contract_data(
    contract: dict[str, Any],
    ledger: dict[str, Any],
    cameras: dict[str, Any],
    r4_contract: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    if contract.get("schema") != (
        "skyguard.phase2.yak52-r4-slice01-output-contract.v1"
    ):
        errors.append("output contract schema mismatch")
    if contract.get("contract_id") != (
        "PHASE2-YAK52-R4-S01-OUTPUTS-20260802-V1"
    ):
        errors.append("output contract id mismatch")
    if contract.get("build_id") != BUILD_ID:
        errors.append("build id mismatch")
    if contract.get("current_status") != "AUTHORING_SOURCE_READY_NOT_RUN":
        errors.append("readiness status must remain AUTHORING_SOURCE_READY_NOT_RUN")

    claims = contract.get("claims", {})
    for claim in sorted(FALSE_CLAIMS):
        if claims.get(claim) is not False:
            errors.append(f"claim must remain false: {claim}")

    source_policy = contract.get("source_policy", {})
    if source_policy.get("scene_origin") != "FACTORY_EMPTY_ONLY":
        errors.append("source scene must be FACTORY_EMPTY_ONLY")
    for field in (
        "accepted_blend_open_allowed",
        "accepted_blend_append_allowed",
        "accepted_blend_link_allowed",
        "r3_donor_geometry_allowed",
        "external_mesh_import_allowed",
        "network_access_allowed",
    ):
        if source_policy.get(field) is not False:
            errors.append(f"source policy must forbid {field}")
    if source_policy.get("diagnostic_materials_only") is not True:
        errors.append("Slice 01 must use diagnostic materials only")

    output_policy = contract.get("output_policy", {})
    for field in (
        "overwrite_allowed",
        "automatic_promotion_allowed",
        "unreal_import_allowed",
    ):
        if output_policy.get(field) is not False:
            errors.append(f"output policy must forbid {field}")
    for field in (
        "atomic_canonical_publication_required",
        "canonical_outputs_must_be_absent_before_run",
    ):
        if output_policy.get(field) is not True:
            errors.append(f"output policy must require {field}")

    namespace = contract.get("namespace_contract", {})
    if _set_or_empty(namespace.get("collections")) != EXPECTED_COLLECTIONS:
        errors.append("collection namespace mismatch")
    if _set_or_empty(namespace.get("primary_objects")) != EXPECTED_PRIMARY_OBJECTS:
        errors.append("primary object namespace mismatch")
    if _set_or_empty(namespace.get("datum_objects")) != EXPECTED_DATUMS:
        errors.append("datum namespace mismatch")
    if _set_or_empty(namespace.get("materials")) != EXPECTED_MATERIALS:
        errors.append("diagnostic material namespace mismatch")
    if namespace.get("camera_ids") != EXPECTED_CAMERAS:
        errors.append("Slice 01 camera namespace/order mismatch")

    topology = contract.get("topology_contract", {})
    expected_topology = {
        "primary_object_count": 13,
        "datum_object_count": 4,
        "primary_mesh_total_triangle_budget": 50000,
        "symmetry_tolerance_m": 0.001,
        "nonzero_bounds_required": True,
        "finite_vertices_required": True,
        "applied_scale_required": True,
        "duplicate_primary_names_allowed": False,
        "microdetail_geometry_allowed": False,
    }
    for field, expected in expected_topology.items():
        value = topology.get(field)
        if isinstance(expected, float):
            valid = _same_number(value, expected)
        else:
            valid = value == expected and type(value) is type(expected)
        if not valid:
            errors.append(f"topology contract mismatch: {field}")

    if ledger.get("schema") != (
        "skyguard.phase2.yak52-r4-slice01-dimension-ledger.v1"
    ):
        errors.append("dimension ledger schema mismatch")
    if ledger.get("ledger_id") != (
        "PHASE2-YAK52-R4-S01-DIMENSIONS-20260802-V1"
    ):
        errors.append("dimension ledger id mismatch")
    reference = ledger.get("reference_package_status", {})
    for field in sorted(REQUIRED_MISSING_REFERENCE_FIELDS):
        if reference.get(field) != "MISSING":
            errors.append(f"primary reference field must remain MISSING: {field}")
    if reference.get("silhouette_lock_allowed") is not False:
        errors.append("silhouette lock cannot be allowed without references")
    if reference.get("draft_authoring_allowed") is not True:
        errors.append("dimension ledger must explicitly allow draft authoring")

    dimension_entries = ledger.get("governed_dimensions_m", [])
    dimensions = {
        entry.get("id"): entry
        for entry in dimension_entries
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }
    if len(dimension_entries) != len(EXPECTED_DIMENSIONS):
        errors.append("governed dimension count mismatch")
    if set(dimensions) != set(EXPECTED_DIMENSIONS):
        errors.append("governed dimension ids mismatch")
    for dimension_id, (target, tolerance) in EXPECTED_DIMENSIONS.items():
        entry = dimensions.get(dimension_id, {})
        if not _same_number(entry.get("target"), target):
            errors.append(f"dimension target mismatch: {dimension_id}")
        if not _same_number(entry.get("tolerance"), tolerance):
            errors.append(f"dimension tolerance mismatch: {dimension_id}")
        if entry.get("primary_source_verified") is not False:
            errors.append(f"dimension cannot claim primary verification: {dimension_id}")

    stations = ledger.get("normalized_station_plan", [])
    fractions = [
        station.get("x_fraction_of_half_length")
        for station in stations
        if isinstance(station, dict)
    ]
    if len(stations) != 9:
        errors.append("normalized station count mismatch")
    try:
        if not all(
            float(fractions[index]) < float(fractions[index + 1])
            for index in range(len(fractions) - 1)
        ):
            errors.append("normalized station fractions are not strictly increasing")
    except (TypeError, ValueError):
        errors.append("normalized station fractions are invalid")

    checks = ledger.get("offline_checks", {})
    expected_checks = {
        "dimension_count": 6,
        "station_count": 9,
        "symmetry_tolerance_m": 0.001,
        "primary_mesh_total_triangle_budget": 50000,
        "silhouette_lock_requires_primary_reference_package": True,
    }
    for field, expected in expected_checks.items():
        value = checks.get(field)
        valid = (
            _same_number(value, expected)
            if isinstance(expected, float)
            else value == expected and type(value) is type(expected)
        )
        if not valid:
            errors.append(f"dimension offline check mismatch: {field}")

    if cameras.get("schema") != (
        "skyguard.phase2.yak52-r4-slice01-camera-manifest.v1"
    ):
        errors.append("camera manifest schema mismatch")
    if cameras.get("manifest_id") != (
        "PHASE2-YAK52-R4-S01-CAMERAS-20260802-V1"
    ):
        errors.append("camera manifest id mismatch")
    if cameras.get("required_camera_ids") != EXPECTED_CAMERAS:
        errors.append("required camera ids mismatch")
    camera_entries = cameras.get("cameras", [])
    if [camera.get("id") for camera in camera_entries] != EXPECTED_CAMERAS:
        errors.append("camera entry order/ids mismatch")
    if [camera.get("output_filename") for camera in camera_entries] != (
        EXPECTED_RENDER_OUTPUTS
    ):
        errors.append("camera output filenames mismatch")
    render = cameras.get("render_contract", {})
    expected_render = {
        "resolution_x": 1920,
        "resolution_y": 1080,
        "resolution_percentage": 100,
        "engine": "BLENDER_EEVEE_NEXT",
        "file_format": "PNG",
        "camera_mutation_allowed_after_authoring_start": False,
        "crop_or_reframe_allowed": False,
    }
    for field, expected in expected_render.items():
        if render.get(field) != expected:
            errors.append(f"render contract mismatch: {field}")

    if r4_contract.get("contract_id") != (
        "PHASE2-YAK52-R4-FINAL-ART-GAP-20260802-V1"
    ):
        errors.append("accepted R4 authority id mismatch")
    slices = r4_contract.get("ordered_asset_slices", [])
    slice01 = next(
        (
            entry
            for entry in slices
            if isinstance(entry, dict) and entry.get("slice_id") == "R4-S01"
        ),
        None,
    )
    if not slice01:
        errors.append("accepted R4 Slice 01 missing")
    elif slice01.get("acceptance_cameras") != EXPECTED_CAMERAS:
        errors.append("camera manifest does not match accepted R4 Slice 01")

    r4_cameras = {
        entry.get("id"): entry
        for entry in r4_contract.get("visual_acceptance_contract", {}).get(
            "required_cameras", []
        )
        if isinstance(entry, dict)
    }
    camera_fields = (
        "projection",
        "location_m",
        "target_m",
        "lens_mm",
        "ortho_scale_m",
    )
    for camera in camera_entries:
        authority = r4_cameras.get(camera.get("id"))
        if authority is None:
            errors.append(f"R4 authority camera missing: {camera.get('id')}")
            continue
        for field in camera_fields:
            if field in authority and camera.get(field) != authority.get(field):
                errors.append(f"camera authority mismatch: {camera.get('id')} {field}")

    dimension_contract = contract.get("dimension_contract", {})
    if dimension_contract.get("ledger_id") != ledger.get("ledger_id"):
        errors.append("output contract dimension ledger id mismatch")
    if dimension_contract.get("required_dimension_ids") != list(
        EXPECTED_DIMENSIONS
    ):
        errors.append("output contract required dimension ids mismatch")
    if dimension_contract.get("normalized_station_count") != 9:
        errors.append("output contract station count mismatch")
    for field in (
        "primary_reference_package_complete",
        "silhouette_lock_allowed",
    ):
        if dimension_contract.get(field) is not False:
            errors.append(f"dimension completion boundary must remain false: {field}")
    if dimension_contract.get("future_successful_run_is_draft_only") is not True:
        errors.append("future successful run must remain draft-only")

    visual = contract.get("visual_evidence_contract", {})
    if visual.get("camera_manifest_id") != cameras.get("manifest_id"):
        errors.append("output contract camera manifest id mismatch")
    if visual.get("required_render_count") != 5:
        errors.append("required render count mismatch")
    if visual.get("required_outputs") != EXPECTED_RENDER_OUTPUTS:
        errors.append("required visual outputs mismatch")
    for field in (
        "crop_reframe_or_camera_mutation_allowed",
        "rendered",
        "human_reviewed",
    ):
        if visual.get(field) is not False:
            errors.append(f"visual readiness boundary must remain false: {field}")

    return errors


def validate_authority_files(
    root: Path, contract: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    authorities = contract.get("authority_inputs", [])
    if len(authorities) != 8:
        errors.append("authority input count mismatch")
    for authority in authorities:
        rel = authority.get("path")
        if not isinstance(rel, str):
            errors.append("authority path is invalid")
            continue
        path = root / Path(rel)
        if not path.is_file():
            errors.append(f"authority missing: {rel}")
            continue
        if path.stat().st_size != authority.get("bytes"):
            errors.append(f"authority size drift: {rel}")
        if sha256_file(path) != authority.get("sha256"):
            errors.append(f"authority hash drift: {rel}")
    return errors


def _attribute_name(node: ast.AST) -> str:
    parts: list[str] = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))


def validate_authoring_script(
    root: Path, contract: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    script_contract = contract.get("authoring_script", {})
    rel = script_contract.get("path")
    if not isinstance(rel, str):
        return ["authoring script path is invalid"]
    path = root / Path(rel)
    if not path.is_file():
        return [f"authoring script missing: {rel}"]
    if path.stat().st_size != script_contract.get("bytes"):
        errors.append("authoring script size drift")
    if sha256_file(path) != script_contract.get("sha256"):
        errors.append("authoring script hash drift")

    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return errors + [f"authoring script syntax error: {exc}"]

    allowed_top_level = (
        ast.Expr,
        ast.Import,
        ast.ImportFrom,
        ast.Assign,
        ast.AnnAssign,
        ast.FunctionDef,
        ast.If,
    )
    for node in tree.body:
        if not isinstance(node, allowed_top_level):
            errors.append(f"unexpected top-level authoring node: {type(node).__name__}")
        if isinstance(node, ast.Expr) and not (
            isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            errors.append("top-level executable expression is forbidden")
        if isinstance(node, ast.If):
            is_main_guard = (
                isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name)
                and node.test.left.id == "__name__"
            )
            if not is_main_guard:
                errors.append("only the __main__ guard is allowed at top level")

    forbidden_imports = {
        "requests",
        "urllib",
        "http",
        "socket",
        "ftplib",
        "paramiko",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in forbidden_imports:
                    errors.append(f"network import forbidden: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in forbidden_imports:
                errors.append(f"network import forbidden: {node.module}")

    forbidden_calls = {
        "bpy.ops.wm.open_mainfile",
        "bpy.ops.wm.append",
        "bpy.ops.wm.link",
        "bpy.ops.import_scene.gltf",
        "bpy.ops.import_scene.fbx",
        "bpy.data.libraries.load",
    }
    call_names = {
        _attribute_name(node.func)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    }
    for call in sorted(forbidden_calls & call_names):
        errors.append(f"accepted/donor source operation forbidden: {call}")
    required_calls = {
        "bpy.ops.wm.read_factory_settings",
        "bpy.ops.wm.save_as_mainfile",
        "bpy.ops.export_scene.gltf",
        "bpy.ops.render.render",
    }
    for call in sorted(required_calls - call_names):
        errors.append(f"required deterministic authoring operation missing: {call}")

    required_literals = (
        [BUILD_ID, "DRAFT_REFERENCE_PACKAGE_MISSING"]
        + sorted(EXPECTED_COLLECTIONS)
        + sorted(EXPECTED_PRIMARY_OBJECTS)
        + sorted(EXPECTED_DATUMS)
        + sorted(EXPECTED_MATERIALS)
        + EXPECTED_CAMERAS
    )
    for literal in required_literals:
        if literal not in source:
            errors.append(f"authoring script literal missing: {literal}")

    if "RANDOM_SEED = 5201" not in source:
        errors.append("authoring random seed mismatch")
    if "bpy.app.version[:2] != (5, 2)" not in source:
        errors.append("Blender 5.2 version gate missing")
    if "use_empty=True" not in source:
        errors.append("factory-empty reset is not explicit")
    if "ensure_canonical_outputs_absent(contract)" not in source:
        errors.append("canonical overwrite refusal is missing")
    if source.count('if __name__ == "__main__":') != 1:
        errors.append("authoring script must have exactly one main guard")

    return errors


def validate_output_absence(root: Path, contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    paths = contract.get("output_policy", {}).get("paths", {})
    for key in ("blend", "glb", "manifest", "screenshot_directory"):
        rel = paths.get(key)
        if not isinstance(rel, str):
            errors.append(f"canonical output path missing: {key}")
            continue
        if (root / Path(rel)).exists():
            errors.append(f"canonical output must be absent before run: {rel}")
    return errors


def run_validation(root: Path) -> tuple[dict[str, Any], list[str]]:
    contract = read_json(root / CONTRACT_REL)
    ledger = read_json(root / LEDGER_REL)
    cameras = read_json(root / CAMERA_REL)
    r4_contract = read_json(root / R4_REL)
    errors = validate_contract_data(contract, ledger, cameras, r4_contract)
    errors.extend(validate_authority_files(root, contract))
    errors.extend(validate_authoring_script(root, contract))
    errors.extend(validate_output_absence(root, contract))
    return contract, errors


def write_immutable_report(
    root: Path, contract: dict[str, Any], errors: list[str]
) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    contract_hash = sha256_file(root / CONTRACT_REL)
    attempt = (
        root
        / REPORT_ROOT_REL
        / f"attempt_{timestamp}_{contract_hash[:8]}_{os.getpid():08x}"
    )
    attempt.mkdir(parents=True, exist_ok=False)
    report = {
        "schema": "skyguard.phase2.yak52-r4-slice01-readiness-report.v1",
        "build_id": BUILD_ID,
        "status": (
            "PASS_SLICE01_AUTHORING_READY_PRODUCTION_NOT_STARTED"
            if not errors
            else "FAIL_SLICE01_AUTHORING_NOT_READY"
        ),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "contract": {
            "path": CONTRACT_REL.as_posix(),
            "bytes": (root / CONTRACT_REL).stat().st_size,
            "sha256": contract_hash,
        },
        "authoring_script": copy.deepcopy(contract.get("authoring_script", {})),
        "canonical_outputs_absent": not any(
            error.startswith("canonical output must be absent") for error in errors
        ),
        "reference_package_complete": False,
        "silhouette_lock_allowed": False,
        "blender_launched_by_gate": False,
        "unreal_launched_by_gate": False,
        "production_started": False,
        "errors": errors,
    }
    report_path = attempt / "slice01_readiness_report.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (attempt / "SHA256SUMS.txt").write_text(
        f"{sha256_file(report_path)}  {report_path.name}\n",
        encoding="utf-8",
    )
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Validate without creating an immutable attempt receipt.",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    contract, errors = run_validation(root)
    status = (
        "PASS_SLICE01_AUTHORING_READY_PRODUCTION_NOT_STARTED"
        if not errors
        else "FAIL_SLICE01_AUTHORING_NOT_READY"
    )
    result: dict[str, Any] = {
        "build_id": BUILD_ID,
        "status": status,
        "error_count": len(errors),
        "errors": errors,
        "production_started": False,
        "blender_launched_by_gate": False,
        "unreal_launched_by_gate": False,
    }
    if not args.no_write:
        result["report_path"] = str(
            write_immutable_report(root, contract, errors).relative_to(root)
        ).replace("\\", "/")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
