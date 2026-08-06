"""Strict source/artifact verifier for BLD-M01-YAK-UPLIFT-003-R2."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path


BUILD_ID = "BLD-M01-YAK-UPLIFT-003-R2"
EXPECTED_STAGE_ORDER = [
    "source_inventory_exception_gate",
    "camera_and_clearance",
    "component_ledger_tags",
    "selective_002_donors",
    "matched_comparison_setup",
    "isolated_save_export_and_comparison",
]
BASE_CLASSIFICATIONS = {
    "provisional_inherited",
    "rebuild_candidate",
    "donor_from_002",
    "hold",
}
R2_CLASSIFICATIONS = BASE_CLASSIFICATIONS | {"source_absent_hold"}


class ValidationError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise ValidationError(f"Missing JSON: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"Invalid JSON: {path}: {exc}") from exc


def verify_record(root: Path, record: dict, label: str) -> None:
    path = root / record["path"]
    if not path.is_file():
        raise ValidationError(f"{label} missing: {record['path']}")
    if path.stat().st_size != record["bytes"]:
        raise ValidationError(f"{label} byte count mismatch: {record['path']}")
    if sha256_file(path) != record["sha256"]:
        raise ValidationError(f"{label} hash mismatch: {record['path']}")


def parse_glb_mesh_node_names(path: Path) -> list[str]:
    payload = path.read_bytes()
    if payload[:4] != b"glTF":
        raise ValidationError("L88 GLB magic mismatch")
    offset = 12
    document = None
    while offset < len(payload):
        length, chunk_type = struct.unpack_from("<II", payload, offset)
        offset += 8
        chunk = payload[offset : offset + length]
        offset += length
        if chunk_type == 0x4E4F534A:
            document = json.loads(chunk.rstrip(b" \t\r\n\0"))
            break
    if document is None:
        raise ValidationError("L88 GLB JSON chunk missing")
    return sorted(
        node["name"]
        for node in document.get("nodes", [])
        if node.get("mesh") is not None and node.get("name")
    )


def resolve_ledger(overlay: dict, base: dict, runtime: dict) -> list[dict]:
    if overlay.get("build_id") != BUILD_ID:
        raise ValidationError("R2 ledger build id mismatch")
    if set(overlay.get("allowed_classifications", [])) != R2_CLASSIFICATIONS:
        raise ValidationError("R2 allowed classifications drifted")
    policy = overlay.get("source_absent_hold_policy", {})
    if (
        policy.get("promotion_allowed") is not False
        or policy.get("required_as_blender_object") is not False
        or policy.get("synthesis_allowed") is not False
        or policy.get("counts_toward_governed_component_total") is not True
    ):
        raise ValidationError("R2 source_absent_hold policy is unsafe")
    entries = runtime.get("entries", [])
    if len(entries) != 240 or len({item["name"] for item in entries}) != 240:
        raise ValidationError("R2 runtime inventory is not 240 unique components")
    runtime_names = {item["name"] for item in entries}
    exceptions = overlay.get("classification_overrides", {})
    if len(exceptions) != 8 or set(exceptions.values()) != {"source_absent_hold"}:
        raise ValidationError("R2 must have exactly eight source_absent_hold overrides")
    if set(exceptions) - runtime_names:
        raise ValidationError("R2 exception references unknown runtime name")
    observations = overlay.get("actual_source_observations", {})
    if set(observations) != set(exceptions) or len(set(observations.values())) != 8:
        raise ValidationError("R2 actual-source observations do not match exceptions")

    resolved = []
    for entry in entries:
        name = entry["name"]
        bundle = entry["bundle"]
        if bundle not in base["bundle_defaults"]:
            raise ValidationError(f"R2 unknown bundle: {bundle}")
        classification = exceptions.get(
            name,
            base["component_overrides"].get(name, base["bundle_defaults"][bundle]),
        )
        if classification not in R2_CLASSIFICATIONS:
            raise ValidationError(f"R2 forbidden classification: {classification}")
        resolved.append({**entry, "classification": classification})
    counts = Counter(item["classification"] for item in resolved)
    if counts["source_absent_hold"] != 8 or len(resolved) - counts["source_absent_hold"] != 232:
        raise ValidationError("R2 232 + 8 = 240 accounting failed")
    if set(counts) != R2_CLASSIFICATIONS:
        raise ValidationError("R2 must retain all component-by-component classes")
    donor_targets = {
        item["name"] for item in resolved if item["classification"] == "donor_from_002"
    }
    if donor_targets - set(base["donor_replacement_map"]):
        raise ValidationError("R2 donor component lacks replacement mapping")
    return resolved


def verify_source_audit(
    root: Path, audit: dict, overlay: dict, runtime: dict
) -> list[str]:
    if audit.get("build_id") != BUILD_ID:
        raise ValidationError("R2 source audit build id mismatch")
    if audit.get("status") != "source_inventory_reconciled_no_blender_run":
        raise ValidationError("R2 source audit status mismatch")
    if audit.get("audit_method", {}).get("blender_launch_used") is not False:
        raise ValidationError("R2 source audit must remain source-only")
    policy = audit.get("exception_policy", {})
    if (
        policy.get("exceptions_are_required_blender_objects") is not False
        or policy.get("exceptions_may_be_synthesized") is not False
        or policy.get("exceptions_count_toward_governed_240_total") is not True
        or policy.get("future_reconciliation_requires_new_versioned_contract") is not True
    ):
        raise ValidationError("R2 source audit exception policy is unsafe")

    inventory_record = audit["evidence"]["l88_glb_mesh_inventory"]
    names = parse_glb_mesh_node_names(root / inventory_record["path"])
    normalized = ("\n".join(names) + "\n").encode("utf-8")
    if len(names) != 240:
        raise ValidationError("Actual L88 source inventory is not 240 mesh nodes")
    if len(normalized) != inventory_record["normalized_sorted_names_bytes"]:
        raise ValidationError("Actual L88 normalized inventory byte count drifted")
    if hashlib.sha256(normalized).hexdigest() != inventory_record[
        "normalized_sorted_names_sha256"
    ]:
        raise ValidationError("Actual L88 normalized inventory hash drifted")
    runtime_names = {item["name"] for item in runtime["entries"]}
    actual_names = set(names)
    absent = runtime_names - actual_names
    extras = actual_names - runtime_names
    if absent != set(overlay["classification_overrides"]):
        raise ValidationError("Actual governed-name absences differ from eight R2 exceptions")
    if extras != set(overlay["actual_source_observations"].values()):
        raise ValidationError("Actual dotted source names differ from R2 observations")
    exception_rows = audit.get("source_absent_hold_exceptions", [])
    if len(exception_rows) != 8:
        raise ValidationError("R2 source audit must enumerate eight exception rows")
    by_name = {row["governed_name"]: row for row in exception_rows}
    for governed, observed in overlay["actual_source_observations"].items():
        row = by_name.get(governed)
        if (
            not row
            or row.get("classification") != "source_absent_hold"
            or row.get("actual_source_name_observed") != observed
        ):
            raise ValidationError(f"R2 source audit row mismatch: {governed}")
    return names


def verify_contract(root: Path) -> tuple[dict, dict, dict, list[dict]]:
    contract = load_json(
        root / "Docs" / "AAA_Review" / "BLD_M01_YAK_UPLIFT_003_R2_CONTRACT.json"
    )
    overlay = load_json(
        root
        / "Docs"
        / "AAA_Review"
        / "BLD_M01_YAK_UPLIFT_003_R2_COMPONENT_LEDGER.json"
    )
    audit = load_json(
        root / "Docs" / "AAA_Review" / "BLD_M01_YAK_UPLIFT_003_R2_SOURCE_AUDIT.json"
    )
    base = load_json(root / overlay["base_ledger"]["path"])
    runtime = load_json(root / "Saved" / "Reports" / "L88_RUNTIME_ASSEMBLY_CONTRACT.json")
    if contract.get("schema") != "skyguard.blender-uplift-source-contract.v2":
        raise ValidationError("R2 source contract schema mismatch")
    if contract.get("build_id") != BUILD_ID:
        raise ValidationError("R2 source contract build id mismatch")
    if contract.get("status") != "source_only_not_run":
        raise ValidationError("R2 source contract must remain source_only_not_run")
    if contract.get("does_not_modify_or_invalidate_prior_evidence") is not True:
        raise ValidationError("R2 does not preserve prior attempt evidence")
    if contract.get("required_stage_order") != EXPECTED_STAGE_ORDER:
        raise ValidationError("R2 required stage order drifted")
    for key, record in contract.get("immutable_sources", {}).items():
        verify_record(root, record, key)
    verify_record(root, overlay["base_ledger"], "R2 base ledger")
    verify_record(root, overlay["source_audit"], "R2 source audit")
    verify_source_audit(root, audit, overlay, runtime)
    resolved = resolve_ledger(overlay, base, runtime)
    accounting = contract.get("component_accounting", {})
    if (
        accounting.get("governed_total") != 240
        or accounting.get("exact_object_required") != 232
        or accounting.get("source_absent_hold") != 8
        or accounting.get("source_absent_hold_required_as_object") is not False
        or accounting.get("source_absent_hold_synthesis_allowed") is not False
    ):
        raise ValidationError("R2 contract component accounting is unsafe")
    outputs = contract["outputs"]
    for key in ("directory", "blend", "glb", "manifest", "comparison_directory"):
        path = outputs[key].replace("\\", "/")
        if "UPLIFT_003_R2" not in path.upper():
            raise ValidationError(f"R2 output not isolated: {path}")
        if "Yak52_Uplift_003/" in path or "BLD_M01_YAK_UPLIFT_003_MANIFEST" in path:
            raise ValidationError(f"R2 output overlaps R1 namespace: {path}")
    if len(contract.get("matched_comparison_slots", [])) != 5:
        raise ValidationError("R2 requires five matched comparisons")
    if len({slot["candidate"] for slot in contract["matched_comparison_slots"]}) != 5:
        raise ValidationError("R2 comparison candidate paths are not unique")
    for slot in contract["matched_comparison_slots"]:
        verify_record(root, slot["baseline"], f"{slot['slot']} baseline")
    inheritance = contract.get("inheritance_policy", {})
    if (
        inheritance.get("promotion_allowed_value") is not False
        or inheritance.get("source_absent_hold_never_synthesized") is not True
        or inheritance.get("no_aaa_or_final_claim") is not True
    ):
        raise ValidationError("R2 inheritance/promotion guard drifted")
    return contract, overlay, audit, resolved


def verify_generator_source(root: Path, overlay: dict) -> None:
    path = root / "Scripts" / "blender_bld_m01_yak_uplift_003_r2.py"
    if not path.is_file():
        raise ValidationError("R2 generator missing")
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        raise ValidationError(f"R2 generator syntax error: {exc}") from exc
    functions = {
        node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)
    }
    required = {
        "parse_glb_mesh_node_names",
        "resolve_ledger",
        "stage_source_inventory_exception_gate",
        "stage_component_ledger_tags",
        "stage_camera_and_clearance",
        "stage_selective_002_donors",
        "stage_matched_comparison_setup",
        "save_export_and_render",
        "write_manifest",
        "main",
    }
    if required - set(functions):
        raise ValidationError(f"R2 generator functions missing: {sorted(required-set(functions))}")
    forbidden_calls = []
    open_calls = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        call_name = ast.unparse(node.func)
        if call_name.endswith(("libraries.load", "wm.append", "wm.link")):
            forbidden_calls.append(call_name)
        if call_name.endswith("wm.open_mainfile"):
            open_calls.append(node)
    if forbidden_calls:
        raise ValidationError(f"R2 generator has forbidden import calls: {forbidden_calls}")
    if len(open_calls) != 1 or "BLEND_PATH" not in ast.unparse(open_calls[0]):
        raise ValidationError("R2 generator must open exactly one isolated copied blend")
    if "shutil.copy2(L88_BLEND_PATH, BLEND_PATH)" not in source:
        raise ValidationError("R2 generator does not byte-copy L88 to R2 output")
    if ".main(" in source or "r1.main" in source:
        raise ValidationError("R2 generator must never invoke the R1 main function")
    if "source_absent_hold" not in source:
        raise ValidationError("R2 generator lacks source_absent_hold handling")
    tag_source = ast.get_source_segment(source, functions["stage_component_ledger_tags"]) or ""
    skip_position = tag_source.find('if entry["classification"] == "source_absent_hold"')
    lookup_position = tag_source.find("bpy.data.objects.get")
    if skip_position < 0 or lookup_position < 0 or skip_position > lookup_position:
        raise ValidationError("R2 generator may require a source_absent_hold Blender object")
    if "continue" not in tag_source[skip_position:lookup_position]:
        raise ValidationError("R2 generator does not skip source_absent_hold object lookup")
    exception_source = ast.get_source_segment(
        source, functions["stage_source_inventory_exception_gate"]
    ) or ""
    if "bpy.data.objects.new" in exception_source or "primitive_" in exception_source:
        raise ValidationError("R2 generator synthesizes source-absent objects")
    for governed_name in overlay["classification_overrides"]:
        if governed_name in source:
            raise ValidationError(
                f"R2 generator hard-codes absent governed object name: {governed_name}"
            )
    main_source = ast.get_source_segment(source, functions["main"]) or ""
    calls = [
        "stage_source_inventory_exception_gate",
        "stage_camera_and_clearance",
        "stage_component_ledger_tags",
        "stage_selective_002_donors",
        "stage_matched_comparison_setup",
        "save_export_and_render",
    ]
    positions = [main_source.find(name + "(") for name in calls]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        raise ValidationError("R2 generator main stage call order drifted")
    if "refuse_overwrite()" not in main_source:
        raise ValidationError("R2 generator lacks overwrite refusal")


def verify_artifacts(
    root: Path, contract: dict, overlay: dict, expected_resolved: list[dict]
) -> None:
    manifest = load_json(root / contract["outputs"]["manifest"])
    if manifest.get("build_id") != BUILD_ID:
        raise ValidationError("R2 artifact build id mismatch")
    if manifest.get("stage_order") != EXPECTED_STAGE_ORDER:
        raise ValidationError("R2 artifact stage order drifted")
    if manifest.get("promotion_allowed") is not False:
        raise ValidationError("R2 artifact silently promotes")
    claims = manifest.get("claims", {})
    if any(
        claims.get(key) is not False
        for key in (
            "final",
            "aaa",
            "unreal_accepted",
            "matched_visual_review_accepted",
        )
    ):
        raise ValidationError("R2 artifact makes an acceptance/final/AAA claim")
    for key in ("blend", "glb"):
        verify_record(root, manifest["outputs"][key], f"R2 artifact {key}")
    verify_record(root, contract["immutable_sources"]["l88_blend"], "immutable L88 after R2")
    if manifest.get("original_l88_unchanged") is not True:
        raise ValidationError("R2 manifest does not attest unchanged L88 source")
    if manifest.get("resolved_component_ledger") != expected_resolved:
        raise ValidationError("R2 artifact resolved ledger drifted")
    counts = Counter(item["classification"] for item in expected_resolved)
    if manifest.get("classification_counts") != dict(sorted(counts.items())):
        raise ValidationError("R2 artifact classification counts drifted")
    accounting = manifest.get("component_accounting", {})
    if accounting != {
        "governed_total": 240,
        "exact_object_required": 232,
        "source_absent_hold": 8,
        "equation_valid": True,
    }:
        raise ValidationError("R2 artifact 232 + 8 = 240 accounting failed")
    exception_records = manifest.get("source_absent_hold_records", [])
    if len(exception_records) != 8:
        raise ValidationError("R2 artifact exception record count is not eight")
    expected_exceptions = set(overlay["classification_overrides"])
    if {row.get("governed_name") for row in exception_records} != expected_exceptions:
        raise ValidationError("R2 artifact exception names drifted")
    for row in exception_records:
        if (
            row.get("classification") != "source_absent_hold"
            or row.get("required_as_object") is not False
            or row.get("synthesized") is not False
            or row.get("promotion_allowed") is not False
        ):
            raise ValidationError("R2 artifact source-absent exception is unsafe")
    object_records = {row["name"]: row for row in manifest.get("object_records", [])}
    if expected_exceptions & set(object_records):
        raise ValidationError("R2 source-absent governed name was synthesized as object")
    for item in expected_resolved:
        if item["classification"] == "source_absent_hold":
            continue
        row = object_records.get(item["name"])
        if not row:
            raise ValidationError(f"R2 exact object record missing: {item['name']}")
        if (
            row.get("uplift_class") != item["classification"]
            or row.get("promotion_allowed") is not False
            or row.get("inherited_from") != "L88"
        ):
            raise ValidationError(f"R2 exact object governance mismatch: {item['name']}")
    for name in contract["required_donor_objects"]:
        row = object_records.get(name)
        if (
            not row
            or row.get("uplift_class") != "donor_from_002"
            or row.get("promotion_allowed") is not False
        ):
            raise ValidationError(f"R2 selective donor governance mismatch: {name}")
    for name, spec in contract["required_safety_and_clearance_volumes"].items():
        row = object_records.get(name)
        if (
            not row
            or row.get("governance_role") != spec["role"]
            or row.get("promotion_allowed") is not False
        ):
            raise ValidationError(f"R2 clearance/safety volume mismatch: {name}")
    camera = object_records.get(contract["first_stage_camera"]["name"])
    if (
        not camera
        or camera.get("type") != "CAMERA"
        or camera.get("promotion_allowed") is not False
    ):
        raise ValidationError("R2 corrected rear-gunner camera record missing")
    comparisons = manifest.get("matched_comparisons", [])
    if len(comparisons) != 5:
        raise ValidationError("R2 artifact lacks five comparisons")
    by_slot = {item["slot"]: item for item in comparisons}
    for slot in contract["matched_comparison_slots"]:
        row = by_slot.get(slot["slot"])
        if not row or row.get("baseline") != slot["baseline"]:
            raise ValidationError(f"R2 matched baseline drifted: {slot['slot']}")
        candidate = row.get("candidate")
        if not candidate or candidate.get("path") != slot["candidate"]:
            raise ValidationError(f"R2 candidate record missing: {slot['slot']}")
        verify_record(root, candidate, f"R2 {slot['slot']} candidate")


def verify(root: Path, *, artifacts: bool = False) -> dict:
    contract, overlay, _audit, resolved = verify_contract(root)
    verify_generator_source(root, overlay)
    if artifacts:
        verify_artifacts(root, contract, overlay, resolved)
    counts = Counter(item["classification"] for item in resolved)
    return {
        "build_id": BUILD_ID,
        "mode": "artifacts" if artifacts else "source_only",
        "governed_component_count": len(resolved),
        "exact_object_requirement_count": len(resolved) - counts["source_absent_hold"],
        "source_absent_hold_count": counts["source_absent_hold"],
        "classification_counts": dict(sorted(counts.items())),
        "matched_comparison_slots": len(contract["matched_comparison_slots"]),
        "result": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--artifacts", action="store_true")
    args = parser.parse_args()
    try:
        result = verify(args.root.resolve(), artifacts=args.artifacts)
    except ValidationError as exc:
        print(f"[{BUILD_ID}] FAIL: {exc}")
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
