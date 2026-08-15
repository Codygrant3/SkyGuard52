"""Freeze the completed Stage02 authoring output without inventing supervisor evidence."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_POLYHAVEN_VEGETATION_STAGING02/attempt_01"
ASSET_ROOT = ISOLATED / "Content/M01/SourceBacked/VegetationStaging02"
OUTPUT_MAP = ISOLATED / "Content/M01/Lvl_M01_PolyHavenVegetationStaging02.umap"
INPUT_MAP = ISOLATED / "Content/M01/Lvl_M01_HeroStreetShoreCell03Recovery01.umap"
INVENTORY = ROOT / "Saved/Reports/M01_POLYHAVEN_VEGETATION_STAGING02_ATTEMPT01_ARTIFACT_INVENTORY.json"
FREEZE = ROOT / "Docs/AAA_Review/M01_POLYHAVEN_VEGETATION_STAGING02_ATTEMPT01_TERMINAL_FREEZE.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise RuntimeError(f"Required file is absent: {path}")
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_new_json(path: Path, value: object) -> None:
    if path.exists():
        raise RuntimeError(f"Immutable artifact already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    if temporary.exists():
        raise RuntimeError(f"Temporary artifact already exists: {temporary}")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    receipt_path = ATTEMPT / "authoring_receipt.json"
    log_path = ATTEMPT / "unreal_engine_project_log_copy.log"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("classification") != "PASSED_AUTOMATIC_AWAITING_D3D12_VISUAL_AND_PERFORMANCE_PROOF":
        raise RuntimeError("Stage02 worker receipt classification changed")
    if receipt.get("runtime_promotion") is not False:
        raise RuntimeError("Stage02 promotion guard changed")
    if receipt.get("accepted_map_mutated") is not False:
        raise RuntimeError("Accepted input map mutation guard changed")
    if receipt.get("actor_count_before") != 164 or receipt.get("actor_count_after") != 192:
        raise RuntimeError("Stage02 governed actor counts changed")
    if len(receipt.get("asset_records", [])) != 5 or len(receipt.get("placements", [])) != 28:
        raise RuntimeError("Stage02 asset or placement count changed")

    if record(INPUT_MAP)["sha256"] != "c236e6f6b8a811b4cd2562be7598653464b8b30ff917418849e027ae174fc60b":
        raise RuntimeError("Accepted Cell03 input map changed")
    output_record = record(OUTPUT_MAP)
    if output_record["bytes"] != 906770 or output_record["sha256"] != "183a05414ed5f3c4ccfe70e9b92cbce4bfb60812f5662a0c539a0c42385cab5e":
        raise RuntimeError("Stage02 output map changed")

    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    required_log_lines = (
        "Map check complete: 0 Error(s), 0 Warning(s)",
        "Python script executed successfully",
        "PythonScriptCommandlet_0 finished execution (result 0)",
        "Success - 0 error(s), 13 warning(s)",
    )
    for fragment in required_log_lines:
        if fragment not in log_text:
            raise RuntimeError(f"Engine-log success evidence is absent: {fragment}")
    forbidden_log_lines = ("Invalid input AlphaMode", "SpecularColorFactor")
    for fragment in forbidden_log_lines:
        if fragment in log_text:
            raise RuntimeError(f"Rejected generic-material error survived Stage02: {fragment}")

    asset_records = [record(path) for path in sorted(ASSET_ROOT.rglob("*")) if path.is_file()]
    if len(asset_records) != 38:
        raise RuntimeError(f"Expected 38 Stage02 asset files, found {len(asset_records)}")

    members = [
        record(ATTEMPT / "author_m01_polyhaven_vegetation_staging02.py"),
        record(ATTEMPT / "preflight.json"),
        record(receipt_path),
        record(log_path),
        record(ROOT / "Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging02/vegetation_staging02_contract.json"),
        record(ROOT / "Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging02/author_m01_polyhaven_vegetation_staging02.py"),
        record(ROOT / "Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging02/invoke_m01_polyhaven_vegetation_staging02_once.ps1"),
        record(ROOT / "Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging02/verify_m01_polyhaven_vegetation_staging02_offline.py"),
        record(ROOT / "Docs/AAA_Review/M01_POLYHAVEN_VEGETATION_STAGING02_OFFLINE_DESIGN_FREEZE.json"),
        record(ROOT / "Docs/AAA_Review/M01_POLYHAVEN_VEGETATION_QUARANTINE01_BLENDER_REVIEW01_RECOVERY01_ACCEPTANCE_FREEZE.json"),
        record(ROOT / "Saved/SourceQuarantine/M01_POLYHAVEN_VEGETATION_MATERIAL_SOURCE01/material_source_manifest.json"),
        record(INPUT_MAP),
        output_record,
    ]
    created = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    inventory = {
        "schema": "skyguard.m01-polyhaven-vegetation-staging02.attempt01-artifact-inventory.v1",
        "created_utc": created,
        "classification": "COMPLETE_STAGE02_OUTPUT_INVENTORY",
        "attempt_members": members,
        "staged_asset_root": str(ASSET_ROOT),
        "staged_asset_file_count": len(asset_records),
        "staged_asset_total_bytes": sum(int(item["bytes"]) for item in asset_records),
        "staged_assets": asset_records,
    }
    write_new_json(INVENTORY, inventory)

    missing_supervisor_evidence = [
        str(ROOT / "Saved/Reports/M01_POLYHAVEN_VEGETATION_STAGING02_TERMINAL_SUPERVISOR.json"),
        str(ATTEMPT / "stdout.log"),
        str(ATTEMPT / "stderr.log"),
        str(ATTEMPT / "process_tree_samples.jsonl"),
    ]
    if any(Path(path).exists() for path in missing_supervisor_evidence):
        raise RuntimeError("Previously absent supervisor evidence unexpectedly appeared")

    freeze = {
        "schema": "skyguard.m01-polyhaven-vegetation-staging02.attempt01-terminal-freeze.v1",
        "created_utc": created,
        "classification": "PASSED_AUTOMATIC_AUTHORING_EVIDENCE_INCOMPLETE_AWAITING_D3D12_PROOF",
        "runtime_promotion": False,
        "heavy_process_attempts": 1,
        "automatic_retries": 0,
        "observed_unreal_pid": 48088,
        "worker_result": {
            "engine_commandlet_result": 0,
            "engine_log_success": True,
            "map_check_errors": 0,
            "map_check_warnings": 0,
            "governed_actor_count_before": 164,
            "governed_actor_count_after": 192,
            "source_backed_asset_count": 5,
            "explicit_material_count": 7,
            "grounded_placement_count": 28,
            "accepted_input_map_unchanged": True,
            "output_map": output_record,
        },
        "supervisor_result": {
            "classification": "EVIDENCE_LIFECYCLE_INTERRUPTED_AFTER_WORKER_COMPLETION",
            "numeric_supervisor_exit_code_available": False,
            "terminal_supervisor_manifest_present": False,
            "stdout_stderr_present": False,
            "process_tree_evidence_present": False,
            "reason": "The orchestration host interrupted the wrapper after Unreal completed; no second authoring run is permitted.",
            "missing_expected_evidence": missing_supervisor_evidence,
        },
        "authorities": members,
        "inventory": record(INVENTORY),
        "next_gate": "FRESH_SINGLE_D3D12_SM6_VISUAL_AND_PERFORMANCE_PROOF_OF_STAGE02_MAP",
        "prohibitions": ["NO_AUTHORING_RETRY", "NO_RUNTIME_PROMOTION", "NO_FAILED_NAMESPACE_REUSE"],
    }
    write_new_json(FREEZE, freeze)
    print(json.dumps({"classification": freeze["classification"], "inventory": record(INVENTORY), "freeze": record(FREEZE)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
