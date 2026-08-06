"""Fail-closed offline verifier for acquired M01 Fab kit evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

import build_m01_fab_staging_inventory as inventory_builder
import verify_m01_fab_quarantine_intake as intake_verifier


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = (
    ROOT / "Docs/AAA_Review/M01_FAB_TECHNICAL_EVALUATION_TEMPLATE.json"
)
SCHEMA_PATH = (
    ROOT / "Docs/AAA_Review/M01_FAB_TECHNICAL_EVALUATION_SCHEMA.json"
)
EVIDENCE_PREFIX = "Saved/FabQuarantine/M01_FAB_QUARANTINE_INTAKE_001/"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DESTINATIONS = {
    "CITY_KIT": "/Game/Skyguard/Quarantine/M01/CityKit",
    "BEACH_COAST_KIT": "/Game/Skyguard/Quarantine/M01/BeachCoastKit",
}
NAME_TOKENS = {
    "CITY_KIT": "M01Q_CITY",
    "BEACH_COAST_KIT": "M01Q_COAST",
}
ALLOWED_DEPENDENCY_ROOTS = (
    "/Engine/",
    "/Game/Skyguard/Quarantine/M01/",
    "/Game/Skyguard/Shared/Materials/",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def issue(issues: list[dict], path: str, code: str, detail: str) -> None:
    issues.append({"path": path, "code": code, "detail": detail})


def safe_relative(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    path = PurePosixPath(value.replace("\\", "/"))
    return not path.is_absolute() and ".." not in path.parts


def validate_evidence(
    evidence: object,
    field: str,
    issues: list[dict],
    root: Path,
) -> Path | None:
    if not isinstance(evidence, dict):
        issue(issues, field, "MISSING_EVIDENCE", "Expected path, bytes and sha256.")
        return None
    relative = evidence.get("path")
    size = evidence.get("bytes")
    digest = evidence.get("sha256")
    if not safe_relative(relative):
        issue(issues, field + ".path", "INVALID_EVIDENCE_PATH", str(relative))
        return None
    normalized = str(relative).replace("\\", "/")
    if not normalized.startswith(EVIDENCE_PREFIX):
        issue(issues, field + ".path", "OUTSIDE_M01_QUARANTINE", normalized)
    path = root / normalized
    if not path.is_file():
        issue(issues, field + ".path", "EVIDENCE_FILE_MISSING", normalized)
        return None
    if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
        issue(issues, field + ".bytes", "INVALID_BYTE_COUNT", str(size))
    elif path.stat().st_size != size:
        issue(issues, field + ".bytes", "BYTE_COUNT_MISMATCH", normalized)
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        issue(issues, field + ".sha256", "INVALID_SHA256", str(digest))
    elif sha256_file(path) != digest:
        issue(issues, field + ".sha256", "HASH_MISMATCH", normalized)
    return path


def validate_intake(record: dict, issues: list[dict], root: Path) -> dict | None:
    path = validate_evidence(
        record.get("intake_record"), "intake_record", issues, root
    )
    if not path:
        return None
    try:
        intake = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        issue(issues, "intake_record", "INVALID_INTAKE_JSON", str(error))
        return None
    result = intake_verifier.evaluate(intake, root)
    if result.get("gate_status") != "PASS" or result.get("disposition") != (
        "READY_FOR_MANUAL_QUARANTINE_INSPECTION"
    ):
        issue(
            issues,
            "intake_record",
            "INTAKE_NOT_PROVENANCE_READY",
            f"{result.get('gate_status')} / {result.get('disposition')}",
        )
    return intake


def validate_staging(
    slot_record: dict,
    base: str,
    issues: list[dict],
    root: Path,
) -> None:
    slot = slot_record.get("slot")
    expected_root = inventory_builder.SLOT_ROOTS.get(slot)
    staging = slot_record.get("staging")
    if not isinstance(staging, dict):
        issue(issues, base + ".staging", "MISSING_STAGING", "Staging contract required.")
        return
    expected_text = expected_root.as_posix() if expected_root else ""
    if staging.get("payload_root") != expected_text:
        issue(issues, base + ".staging.payload_root", "WRONG_STAGING_ROOT", expected_text)
    manifest_path = validate_evidence(
        staging.get("inventory_manifest"),
        base + ".staging.inventory_manifest",
        issues,
        root,
    )
    if not manifest_path or slot not in inventory_builder.SLOT_ROOTS:
        return
    try:
        recorded = json.loads(manifest_path.read_text(encoding="utf-8"))
        actual = inventory_builder.build_inventory(root, slot)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        issue(issues, base + ".staging", "STAGING_INVENTORY_UNREADABLE", str(error))
        return
    for key in (
        "schema", "slot", "staging_root", "file_count", "total_bytes",
        "tree_sha256", "files", "symlink_files",
        "unexpected_executable_files",
    ):
        if recorded.get(key) != actual.get(key):
            issue(issues, base + ".staging.inventory_manifest",
                  "STAGING_TREE_MISMATCH", key)
    if recorded.get("symlink_files"):
        issue(issues, base + ".staging", "SYMLINK_PAYLOAD_REJECTED",
              str(recorded["symlink_files"]))
    if recorded.get("unexpected_executable_files"):
        issue(issues, base + ".staging", "EXECUTABLE_PAYLOAD_REJECTED",
              str(recorded["unexpected_executable_files"]))


def validate_dependencies(
    slot_record: dict,
    base: str,
    issues: list[dict],
    root: Path,
) -> None:
    dependencies = slot_record.get("dependencies")
    if not isinstance(dependencies, dict):
        issue(issues, base + ".dependencies", "MISSING_DEPENDENCY_INVENTORY",
              "Explicit dependency inventory required.")
        return
    validate_evidence(
        dependencies.get("evidence"),
        base + ".dependencies.evidence",
        issues,
        root,
    )
    items = dependencies.get("items")
    if not isinstance(items, list):
        issue(issues, base + ".dependencies.items", "INVALID_DEPENDENCY_LIST",
              "Use [] only when evidence explicitly confirms none.")
        return
    seen: set[str] = set()
    for index, item in enumerate(items):
        item_base = f"{base}.dependencies.items[{index}]"
        if not isinstance(item, dict):
            issue(issues, item_base, "INVALID_DEPENDENCY", "Expected object.")
            continue
        object_path = item.get("object_path")
        if not isinstance(object_path, str) or not object_path.startswith("/"):
            issue(issues, item_base + ".object_path", "INVALID_OBJECT_PATH",
                  str(object_path))
            continue
        if object_path in seen:
            issue(issues, item_base + ".object_path", "DUPLICATE_DEPENDENCY",
                  object_path)
        seen.add(object_path)
        if not object_path.startswith(ALLOWED_DEPENDENCY_ROOTS):
            issue(issues, item_base + ".object_path",
                  "DEPENDENCY_OUTSIDE_ALLOWLIST", object_path)
        if item.get("approved") is not True:
            issue(issues, item_base + ".approved",
                  "DEPENDENCY_NOT_APPROVED", object_path)
        if not isinstance(item.get("kind"), str) or not item["kind"].strip():
            issue(issues, item_base + ".kind", "MISSING_DEPENDENCY_KIND",
                  object_path)


def valid_named_object(
    value: object,
    destination: str,
    prefix: str,
) -> bool:
    if not isinstance(value, str):
        return False
    if not value.startswith(destination + "/"):
        return False
    return value.rsplit("/", 1)[-1].startswith(prefix)


def validate_unreal_contract(
    slot_record: dict,
    base: str,
    issues: list[dict],
    root: Path,
    *,
    require_results: bool,
) -> None:
    slot = slot_record.get("slot")
    contract = slot_record.get("unreal_contract")
    if not isinstance(contract, dict) or slot not in DESTINATIONS:
        issue(issues, base + ".unreal_contract", "MISSING_UNREAL_CONTRACT",
              "Exact quarantine destination and validation policy required.")
        return
    destination = DESTINATIONS[slot]
    token = NAME_TOKENS[slot]
    expected_prefixes = {
        "static_mesh": f"SM_{token}_",
        "master_material": f"M_{token}_",
        "material_instance": f"MI_{token}_",
        "texture": f"T_{token}_",
        "blueprint": f"BP_{token}_",
    }
    if contract.get("destination_root") != destination:
        issue(issues, base + ".unreal_contract.destination_root",
              "WRONG_UNREAL_DESTINATION", destination)
    if contract.get("required_name_prefixes") != expected_prefixes:
        issue(issues, base + ".unreal_contract.required_name_prefixes",
              "WRONG_NAMING_CONTRACT", str(expected_prefixes))
    if contract.get("production_reference_allowed") is not False:
        issue(issues, base + ".unreal_contract.production_reference_allowed",
              "PRODUCTION_REFERENCE_FORBIDDEN", "Must remain false.")
    if contract.get("nanite_or_authored_lods_required") is not True:
        issue(issues, base + ".unreal_contract.nanite_or_authored_lods_required",
              "MISSING_GEOMETRY_SCALABILITY_RULE", "Must be true.")
    if contract.get("collision_required") is not True:
        issue(issues, base + ".unreal_contract.collision_required",
              "MISSING_COLLISION_RULE", "Must be true.")
    if contract.get("material_instances_required_for_variants") is not True:
        issue(issues, base + ".unreal_contract.material_instances_required_for_variants",
              "MISSING_MATERIAL_INSTANCE_RULE", "Must be true.")

    import_status = contract.get("import_status")
    if not require_results:
        if import_status != "NOT_IMPORTED":
            issue(issues, base + ".unreal_contract.import_status",
                  "PREIMPORT_STATUS_DRIFT", "Expected NOT_IMPORTED.")
        if contract.get("meshes") or contract.get("materials"):
            issue(issues, base + ".unreal_contract",
                  "PREIMPORT_RESULTS_NOT_ALLOWED",
                  "Technical results require a separately authorized import.")
        return
    if import_status != "QUARANTINE_IMPORTED":
        issue(issues, base + ".unreal_contract.import_status",
              "IMPORT_RESULTS_REQUIRED", "Expected QUARANTINE_IMPORTED.")
    validate_evidence(
        contract.get("asset_registry_evidence"),
        base + ".unreal_contract.asset_registry_evidence",
        issues,
        root,
    )
    meshes = contract.get("meshes")
    if not isinstance(meshes, list) or not meshes:
        issue(issues, base + ".unreal_contract.meshes",
              "MISSING_MESH_RESULTS", "At least one mesh is required.")
        meshes = []
    for index, mesh in enumerate(meshes):
        item = f"{base}.unreal_contract.meshes[{index}]"
        if not isinstance(mesh, dict):
            issue(issues, item, "INVALID_MESH_RESULT", "Expected object.")
            continue
        if not valid_named_object(
            mesh.get("object_path"), destination,
            expected_prefixes["static_mesh"],
        ):
            issue(issues, item + ".object_path",
                  "MESH_DESTINATION_OR_NAME_INVALID",
                  str(mesh.get("object_path")))
        triangles = mesh.get("triangle_count")
        if not isinstance(triangles, int) or isinstance(triangles, bool) or triangles <= 0:
            issue(issues, item + ".triangle_count",
                  "INVALID_TRIANGLE_COUNT", str(triangles))
        nanite = mesh.get("nanite_enabled")
        lod_count = mesh.get("lod_count")
        if not isinstance(nanite, bool):
            issue(issues, item + ".nanite_enabled",
                  "INVALID_NANITE_RESULT", str(nanite))
        if not isinstance(lod_count, int) or isinstance(lod_count, bool) or lod_count < 1:
            issue(issues, item + ".lod_count", "INVALID_LOD_COUNT",
                  str(lod_count))
        elif nanite is False and lod_count < 2:
            issue(issues, item, "NO_NANITE_OR_AUTHORED_LODS",
                  "Each mesh needs Nanite or at least two LODs.")
        collision = mesh.get("collision")
        if collision not in {"SIMPLE", "COMPLEX_AS_SIMPLE", "CUSTOM_UCX"}:
            issue(issues, item + ".collision", "MISSING_COLLISION",
                  str(collision))
        if mesh.get("foreground") is True and collision == "COMPLEX_AS_SIMPLE":
            issue(issues, item + ".collision",
                  "FOREGROUND_COMPLEX_COLLISION_REJECTED",
                  "Foreground meshes require simple or custom UCX collision.")
        slots = mesh.get("material_slots")
        if not isinstance(slots, list) or not slots:
            issue(issues, item + ".material_slots",
                  "MISSING_MATERIAL_ASSIGNMENT", "At least one slot required.")
    materials = contract.get("materials")
    if not isinstance(materials, list) or not materials:
        issue(issues, base + ".unreal_contract.materials",
              "MISSING_MATERIAL_RESULTS", "Material inventory required.")
        materials = []
    material_paths = {
        material.get("object_path")
        for material in materials
        if isinstance(material, dict) and isinstance(
            material.get("object_path"), str
        )
    }
    if materials and not any(
        isinstance(material, dict) and material.get("kind") == "INSTANCE"
        for material in materials
    ):
        issue(issues, base + ".unreal_contract.materials",
              "NO_MATERIAL_INSTANCES",
              "At least one governed material instance is required.")
    for index, material in enumerate(materials):
        item = f"{base}.unreal_contract.materials[{index}]"
        if not isinstance(material, dict):
            issue(issues, item, "INVALID_MATERIAL_RESULT", "Expected object.")
            continue
        kind = material.get("kind")
        prefix = (
            expected_prefixes["master_material"]
            if kind == "MASTER"
            else expected_prefixes["material_instance"]
            if kind == "INSTANCE"
            else ""
        )
        if not prefix or not valid_named_object(
            material.get("object_path"), destination, prefix
        ):
            issue(issues, item + ".object_path",
                  "MATERIAL_DESTINATION_OR_NAME_INVALID",
                  str(material.get("object_path")))
        if kind == "INSTANCE" and not isinstance(
            material.get("parent_material"), str
        ):
            issue(issues, item + ".parent_material",
                  "MISSING_INSTANCE_PARENT", "Material instance parent required.")
        elif kind == "INSTANCE":
            parent = material.get("parent_material")
            if parent not in material_paths and not str(parent).startswith(
                "/Game/Skyguard/Shared/Materials/"
            ):
                issue(issues, item + ".parent_material",
                      "INSTANCE_PARENT_OUTSIDE_INVENTORY", str(parent))
        elif kind == "MASTER" and material.get("parent_material") is not None:
            issue(issues, item + ".parent_material",
                  "MASTER_MATERIAL_HAS_PARENT",
                  str(material.get("parent_material")))
        if material.get("blend_mode") not in {
            "OPAQUE", "MASKED", "TRANSLUCENT"
        }:
            issue(issues, item + ".blend_mode", "INVALID_BLEND_MODE",
                  str(material.get("blend_mode")))
        if material.get("shader_complexity") not in {"LOW", "MEDIUM"}:
            issue(issues, item + ".shader_complexity",
                  "SHADER_COMPLEXITY_NOT_ACCEPTED",
                  str(material.get("shader_complexity")))
        texture_refs = material.get("texture_references")
        if not isinstance(texture_refs, list) or not texture_refs:
            issue(issues, item + ".texture_references",
                  "MISSING_TEXTURE_REFERENCES", "At least one texture required.")
        elif not all(
            isinstance(ref, str) and (
                valid_named_object(
                    ref, destination, expected_prefixes["texture"]
                ) or
                ref.startswith("/Game/Skyguard/Shared/Materials/")
            )
            for ref in texture_refs
        ):
            issue(issues, item + ".texture_references",
                  "TEXTURE_REFERENCE_OUTSIDE_ALLOWLIST",
                  str(texture_refs))
    for index, mesh in enumerate(meshes):
        if not isinstance(mesh, dict):
            continue
        slots = mesh.get("material_slots")
        if isinstance(slots, list):
            for material_path in slots:
                if material_path not in material_paths:
                    issue(
                        issues,
                        f"{base}.unreal_contract.meshes[{index}].material_slots",
                        "MESH_MATERIAL_OUTSIDE_INVENTORY",
                        str(material_path),
                    )


def evaluate(record: dict, root: Path = ROOT) -> dict:
    issues: list[dict] = []
    if record.get("schema") != "skyguard.m01.fab-technical-evaluation.v1":
        issue(issues, "schema", "WRONG_SCHEMA", str(record.get("schema")))
    if record.get("evaluation_id") != "M01-FAB-TECH-EVAL-001":
        issue(issues, "evaluation_id", "WRONG_EVALUATION_ID",
              str(record.get("evaluation_id")))
    policy = record.get("policy")
    expected_policy = {
        "manual_acquisition_required": True,
        "automatic_download_allowed": False,
        "automatic_import_allowed": False,
        "quarantine_only": True,
        "runtime_promotion_allowed": False,
        "city_kit_limit": 1,
        "coast_kit_limit": 1,
    }
    if not isinstance(policy, dict):
        issue(issues, "policy", "MISSING_POLICY", "Fail-closed policy required.")
    else:
        for key, value in expected_policy.items():
            if policy.get(key) != value:
                issue(issues, f"policy.{key}", "UNSAFE_POLICY_DRIFT",
                      f"Must equal {value!r}.")

    intake = validate_intake(record, issues, root)
    slots = record.get("slots")
    if not isinstance(slots, list) or len(slots) != 2:
        issue(issues, "slots", "WRONG_SLOT_COUNT",
              "Exactly one city and one coast slot required.")
        slots = slots if isinstance(slots, list) else []
    slot_names = [
        item.get("slot") for item in slots if isinstance(item, dict)
    ]
    if slot_names.count("CITY_KIT") != 1 or (
        slot_names.count("BEACH_COAST_KIT") != 1
    ):
        issue(issues, "slots", "WRONG_SLOT_CARDINALITY",
              "Exactly one CITY_KIT and one BEACH_COAST_KIT required.")
    intake_products = {}
    if isinstance(intake, dict):
        intake_products = {
            asset.get("slot"): asset.get("catalog", {}).get("product_id")
            for asset in intake.get("assets", [])
            if isinstance(asset, dict)
        }
    status = record.get("status")
    require_results = status == "TECHNICAL_EVALUATION_COMPLETE"
    for index, slot_record in enumerate(slots):
        base = f"slots[{index}]"
        if not isinstance(slot_record, dict):
            issue(issues, base, "INVALID_SLOT_RECORD", "Expected object.")
            continue
        slot = slot_record.get("slot")
        if slot not in DESTINATIONS:
            issue(issues, base + ".slot", "INVALID_SLOT", str(slot))
            continue
        if slot_record.get("product_id") != intake_products.get(slot):
            issue(issues, base + ".product_id", "INTAKE_PRODUCT_MISMATCH",
                  str(intake_products.get(slot)))
        validate_staging(slot_record, base, issues, root)
        validate_dependencies(slot_record, base, issues, root)
        validate_unreal_contract(
            slot_record, base, issues, root,
            require_results=require_results,
        )

    if status not in {
        "ACQUIRED_READY_FOR_MANUAL_QUARANTINE_IMPORT",
        "TECHNICAL_EVALUATION_COMPLETE",
    }:
        issue(issues, "status", "FAIL_CLOSED_STATUS",
              "Acquired/import-ready or technical-complete required.")
    gate = "PASS" if not issues else "FAIL_CLOSED"
    disposition = (
        "READY_FOR_VISUAL_REVIEW"
        if gate == "PASS" and require_results
        else "READY_FOR_MANUAL_QUARANTINE_IMPORT"
        if gate == "PASS"
        else "HOLD_NO_IMPORT_NO_PROMOTION"
    )
    return {
        "schema": "skyguard.m01.fab-technical-audit.v1",
        "evaluation_id": record.get("evaluation_id"),
        "gate_status": gate,
        "disposition": disposition,
        "automatic_import_allowed": False,
        "runtime_promotion_allowed": False,
        "issue_count": len(issues),
        "issues": issues,
    }


def validate_schema_source() -> list[str]:
    errors: list[str] = []
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [str(error)]
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("Schema must declare JSON Schema draft 2020-12.")
    text = SCHEMA_PATH.read_text(encoding="utf-8")
    for marker in (
        "payload_root", "inventory_manifest", "dependencies",
        "destination_root", "required_name_prefixes", "nanite_enabled",
        "lod_count", "collision", "materials", "texture_references",
        "runtime_promotion_allowed",
    ):
        if marker not in text:
            errors.append(f"Schema missing marker: {marker}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", type=Path, default=TEMPLATE_PATH)
    parser.add_argument("--require-visual-ready", action="store_true")
    args = parser.parse_args()
    record = json.loads(args.record.read_text(encoding="utf-8"))
    result = evaluate(record)
    for error in validate_schema_source():
        result["issues"].append({
            "path": "schema_source",
            "code": "SCHEMA_SOURCE_INVALID",
            "detail": error,
        })
    if result["issues"]:
        result["gate_status"] = "FAIL_CLOSED"
        result["disposition"] = "HOLD_NO_IMPORT_NO_PROMOTION"
        result["issue_count"] = len(result["issues"])
    print(json.dumps(result, indent=2))
    if result["gate_status"] != "PASS":
        return 3
    if args.require_visual_ready and (
        result["disposition"] != "READY_FOR_VISUAL_REVIEW"
    ):
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
