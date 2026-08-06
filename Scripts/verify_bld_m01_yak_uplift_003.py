"""Strict source and artifact verifier for BLD-M01-YAK-UPLIFT-003.

The default mode is source-only and is safe to run without Blender.  Pass
``--artifacts`` only after the governed offline Blender command has completed.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from collections import Counter
from pathlib import Path


BUILD_ID = "BLD-M01-YAK-UPLIFT-003"
EXPECTED_STAGE_ORDER = [
    "camera_and_clearance",
    "component_ledger_tags",
    "selective_002_donors",
    "matched_comparison_setup",
    "isolated_save_export_and_comparison",
]
ALLOWED_CLASSIFICATIONS = {
    "provisional_inherited",
    "rebuild_candidate",
    "donor_from_002",
    "hold",
}


class ValidationError(RuntimeError):
    """A deterministic governance failure."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise ValidationError(f"Missing JSON file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"Invalid JSON file: {path}: {exc}") from exc


def verify_file_record(root: Path, record: dict, label: str) -> None:
    path = root / record["path"]
    if not path.is_file():
        raise ValidationError(f"{label} missing: {record['path']}")
    if path.stat().st_size != record["bytes"]:
        raise ValidationError(f"{label} byte count mismatch: {record['path']}")
    if sha256_file(path) != record["sha256"]:
        raise ValidationError(f"{label} hash mismatch: {record['path']}")


def resolve_component_ledger(ledger: dict, runtime: dict) -> list[dict]:
    if ledger.get("build_id") != BUILD_ID:
        raise ValidationError("Component ledger build id mismatch")
    if set(ledger.get("allowed_classifications", [])) != ALLOWED_CLASSIFICATIONS:
        raise ValidationError("Allowed component classification set drifted")
    if ledger.get("silent_promotion_forbidden") is not True:
        raise ValidationError("Silent promotion must be forbidden")
    for classification in ALLOWED_CLASSIFICATIONS:
        policy = ledger.get("classification_policy", {}).get(classification)
        if not policy or policy.get("promotion_allowed") is not False:
            raise ValidationError(f"Classification can silently promote: {classification}")

    entries = runtime.get("entries")
    if not isinstance(entries, list):
        raise ValidationError("L88 runtime contract has no entries list")
    expected_count = ledger["source_contract"]["expected_component_count"]
    if len(entries) != expected_count:
        raise ValidationError(
            f"L88 component count mismatch: expected {expected_count}, found {len(entries)}"
        )
    names = [entry.get("name") for entry in entries]
    if len(set(names)) != len(names):
        raise ValidationError("Duplicate L88 component name")
    unknown_overrides = sorted(set(ledger["component_overrides"]) - set(names))
    if unknown_overrides:
        raise ValidationError(f"Unknown component overrides: {unknown_overrides}")

    defaults = ledger["bundle_defaults"]
    resolved = []
    for entry in entries:
        bundle = entry.get("bundle")
        name = entry.get("name")
        if bundle not in defaults:
            raise ValidationError(f"Unknown bundle for {name}: {bundle}")
        classification = ledger["component_overrides"].get(name, defaults[bundle])
        if classification not in ALLOWED_CLASSIFICATIONS:
            raise ValidationError(f"Forbidden classification for {name}: {classification}")
        resolved.append({**entry, "classification": classification})
    if set(item["classification"] for item in resolved) != ALLOWED_CLASSIFICATIONS:
        raise ValidationError("Ledger must exercise all four governed classifications")

    donor_targets = {
        item["name"] for item in resolved if item["classification"] == "donor_from_002"
    }
    missing_donor_mapping = sorted(
        donor_targets - set(ledger.get("donor_replacement_map", {}))
    )
    if missing_donor_mapping:
        raise ValidationError(
            f"donor_from_002 components lack replacement mapping: {missing_donor_mapping}"
        )
    return resolved


def verify_contract(root: Path, contract: dict, ledger: dict, runtime: dict) -> list[dict]:
    if contract.get("schema") != "skyguard.blender-uplift-source-contract.v1":
        raise ValidationError("Uplift source contract schema mismatch")
    if contract.get("build_id") != BUILD_ID:
        raise ValidationError("Uplift source contract build id mismatch")
    if contract.get("status") != "source_only_not_run":
        raise ValidationError("Source contract status must remain source_only_not_run")
    promotion = str(contract.get("promotion", "")).lower()
    if "final" in promotion or promotion in {"accepted", "production"}:
        raise ValidationError("Source contract makes a final or production claim")
    if contract.get("required_stage_order") != EXPECTED_STAGE_ORDER:
        raise ValidationError("Required stage order mismatch")
    inheritance = contract.get("inheritance_policy", {})
    if inheritance.get("promotion_allowed_value") is not False:
        raise ValidationError("Inheritance policy allows silent promotion")
    if inheritance.get("no_aaa_or_final_claim") is not True:
        raise ValidationError("No-final/no-AAA guard is absent")

    outputs = contract["outputs"]
    for key in ("blend", "glb", "manifest"):
        path = outputs[key].replace("\\", "/")
        if "Uplift_003" not in path and "UPLIFT_003" not in path:
            raise ValidationError(f"Output is not isolated to Uplift 003: {path}")
        if any(token in path for token in ("L88/", "Production_001/", "Production_002/")):
            raise ValidationError(f"Output overlaps immutable source namespace: {path}")

    sources = contract["immutable_sources"]
    for key in ("l88_blend", "l88_runtime_contract", "donor_002_source", "visual_review"):
        verify_file_record(root, sources[key], key)
    if sources["l88_blend"].get("must_remain_unchanged") is not True:
        raise ValidationError("L88 source preservation guard is missing")
    if ledger["source_contract"]["sha256"] != sources["l88_runtime_contract"]["sha256"]:
        raise ValidationError("Ledger/runtime-contract lineage mismatch")

    slots = contract.get("matched_comparison_slots", [])
    if len(slots) != 5:
        raise ValidationError("Exactly five matched comparison slots are required")
    if len({slot["slot"] for slot in slots}) != 5:
        raise ValidationError("Matched comparison slot names must be unique")
    if len({slot["candidate"] for slot in slots}) != 5:
        raise ValidationError("Matched comparison candidate paths must be unique")
    for slot in slots:
        verify_file_record(root, slot["baseline"], f"{slot['slot']} baseline")

    required_volumes = contract.get("required_safety_and_clearance_volumes", {})
    if set(required_volumes) != {
        "VOL_UPLIFT003_CameraClearance",
        "VOL_UPLIFT003_PilotSafety",
        "VOL_UPLIFT003_RifleMuzzleClearance",
        "VOL_UPLIFT003_IglaBackblastClearance",
    }:
        raise ValidationError("Required camera/safety/weapon volumes drifted")
    if (
        contract.get("first_stage_camera", {}).get("required_clearance_volume")
        not in required_volumes
    ):
        raise ValidationError("Rear-gunner camera lacks its clearance volume")
    return resolve_component_ledger(ledger, runtime)


def verify_generator_source(root: Path) -> None:
    path = root / "Scripts" / "blender_bld_m01_yak_uplift_003.py"
    if not path.is_file():
        raise ValidationError("Uplift generator source is missing")
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        raise ValidationError(f"Uplift generator syntax error: {exc}") from exc
    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    required_functions = {
        "isolated_copy_and_open",
        "stage_camera_and_clearance",
        "stage_component_ledger_tags",
        "stage_selective_002_donors",
        "stage_matched_comparison_setup",
        "save_export_and_render",
        "write_manifest",
        "main",
    }
    missing = sorted(required_functions - set(functions))
    if missing:
        raise ValidationError(f"Generator required functions missing: {missing}")

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
        raise ValidationError(f"Generator contains forbidden asset import calls: {forbidden_calls}")
    if len(open_calls) != 1:
        raise ValidationError("Generator must contain exactly one Blender main-file open")
    open_text = ast.unparse(open_calls[0])
    if "BLEND_PATH" not in open_text or "L88_BLEND_PATH" in open_text:
        raise ValidationError("Generator must open only the isolated copied blend")
    if "shutil.copy2(L88_BLEND_PATH, BLEND_PATH)" not in source:
        raise ValidationError("Generator does not byte-copy L88 to isolated output")
    if "bpy.ops.wm.open_mainfile(filepath=str(BLEND_PATH))" not in source:
        raise ValidationError("Generator open-mainfile target is not the isolated output")
    if "Scripts/blender_bld_m01_yak_prod_002.py" in source.replace("\\", "/"):
        # This would be a hard-coded non-governed path instead of DONOR_SOURCE_PATH.
        raise ValidationError("Generator hard-codes the 002 donor source path")

    main_source = ast.get_source_segment(source, functions["main"]) or ""
    required_calls = [
        "stage_camera_and_clearance",
        "stage_component_ledger_tags",
        "stage_selective_002_donors",
        "stage_matched_comparison_setup",
        "save_export_and_render",
    ]
    positions = [main_source.find(name + "(") for name in required_calls]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        raise ValidationError("Generator main does not enforce governed stage call order")
    if "refuse_overwrite()" not in main_source:
        raise ValidationError("Generator lacks immutable-output overwrite refusal")


def verify_artifacts(
    root: Path, contract: dict, ledger: dict, expected_resolved: list[dict]
) -> None:
    manifest_path = root / contract["outputs"]["manifest"]
    manifest = load_json(manifest_path)
    if manifest.get("build_id") != BUILD_ID:
        raise ValidationError("Artifact manifest build id mismatch")
    if manifest.get("stage_order") != EXPECTED_STAGE_ORDER:
        raise ValidationError("Artifact stage order mismatch")
    status = str(manifest.get("status", "")).lower()
    if status in {"accepted", "production", "final", "aaa"}:
        raise ValidationError("Artifact manifest makes a final/AAA/production claim")
    if manifest.get("promotion_allowed") is not False:
        raise ValidationError("Artifact manifest allows silent promotion")
    claims = manifest.get("claims", {})
    if any(claims.get(key) is not False for key in (
        "final", "aaa", "unreal_accepted", "matched_visual_review_accepted"
    )):
        raise ValidationError("Artifact claims acceptance, final, AAA, or Unreal approval")

    for key in ("blend", "glb"):
        verify_file_record(root, manifest["outputs"][key], f"artifact {key}")
    verify_file_record(
        root,
        contract["immutable_sources"]["l88_blend"],
        "immutable L88 blend after artifact run",
    )
    if manifest.get("original_l88_unchanged") is not True:
        raise ValidationError("Manifest does not attest unchanged original L88 source")

    resolved = manifest.get("resolved_component_ledger")
    if resolved != expected_resolved:
        raise ValidationError("Artifact resolved component ledger differs from source ledger")
    expected_counts = dict(
        sorted(Counter(item["classification"] for item in expected_resolved).items())
    )
    if manifest.get("classification_counts") != expected_counts:
        raise ValidationError("Artifact classification counts mismatch")

    records = {record["name"]: record for record in manifest.get("object_records", [])}
    for item in expected_resolved:
        record = records.get(item["name"])
        if not record:
            raise ValidationError(f"Inherited L88 object record missing: {item['name']}")
        if record.get("uplift_class") != item["classification"]:
            raise ValidationError(f"Uplift class mismatch: {item['name']}")
        if record.get("promotion_allowed") is not False:
            raise ValidationError(f"Silent promotion detected: {item['name']}")
        if record.get("inherited_from") != "L88":
            raise ValidationError(f"Inherited lineage missing: {item['name']}")

    for name in contract["required_donor_objects"]:
        record = records.get(name)
        if not record or record.get("uplift_class") != "donor_from_002":
            raise ValidationError(f"Selective donor record missing or unclassified: {name}")
        if record.get("promotion_allowed") is not False:
            raise ValidationError(f"Selective donor silently promoted: {name}")
    for name, spec in contract["required_safety_and_clearance_volumes"].items():
        record = records.get(name)
        if not record or record.get("governance_role") != spec["role"]:
            raise ValidationError(f"Governed clearance/safety volume missing: {name}")
        if record.get("promotion_allowed") is not False:
            raise ValidationError(f"Governed volume silently promoted: {name}")
    camera = records.get(contract["first_stage_camera"]["name"])
    if not camera or camera.get("promotion_allowed") is not False:
        raise ValidationError("Corrected rear-gunner camera record is missing")

    comparisons = manifest.get("matched_comparisons", [])
    if len(comparisons) != 5:
        raise ValidationError("Artifact must contain all five matched comparison records")
    by_slot = {item["slot"]: item for item in comparisons}
    for slot in contract["matched_comparison_slots"]:
        item = by_slot.get(slot["slot"])
        if not item or item.get("baseline") != slot["baseline"]:
            raise ValidationError(f"Matched baseline record drifted: {slot['slot']}")
        candidate = item.get("candidate")
        if not candidate or candidate.get("path") != slot["candidate"]:
            raise ValidationError(f"Matched candidate record missing: {slot['slot']}")
        verify_file_record(root, candidate, f"{slot['slot']} candidate")


def verify(root: Path, *, artifacts: bool = False) -> dict:
    contract_path = root / "Docs" / "AAA_Review" / "BLD_M01_YAK_UPLIFT_003_CONTRACT.json"
    ledger_path = (
        root / "Docs" / "AAA_Review" / "BLD_M01_YAK_UPLIFT_003_COMPONENT_LEDGER.json"
    )
    contract = load_json(contract_path)
    ledger = load_json(ledger_path)
    runtime = load_json(root / ledger["source_contract"]["path"])
    resolved = verify_contract(root, contract, ledger, runtime)
    verify_generator_source(root)
    if artifacts:
        verify_artifacts(root, contract, ledger, resolved)
    return {
        "build_id": BUILD_ID,
        "mode": "artifacts" if artifacts else "source_only",
        "component_count": len(resolved),
        "classification_counts": dict(
            sorted(Counter(item["classification"] for item in resolved).items())
        ),
        "matched_comparison_slots": len(contract["matched_comparison_slots"]),
        "result": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Skyguard52 repository root",
    )
    parser.add_argument(
        "--artifacts",
        action="store_true",
        help="Also verify the emitted blend, GLB, manifest, and five matched images",
    )
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
