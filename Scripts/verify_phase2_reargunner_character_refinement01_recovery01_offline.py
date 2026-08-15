from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\Skyguard52")
AUTHORITY = ROOT / "Saved/Reports/PHASE2_REARGUNNER_CHARACTER_REFINEMENT01_RECOVERY01_EXECUTION_AUTHORITY.json"
ORIGINAL_AUTHORITY = ROOT / "Saved/Reports/PHASE2_REARGUNNER_CHARACTER_REFINEMENT01_EXECUTION_AUTHORITY.json"
MANIFEST = ROOT / "Production/production_manifest.json"
SUPERVISOR = ROOT / "Scripts/invoke_phase2_reargunner_character_refinement01_recovery01_once.ps1"
WORKER = ROOT / "Scripts/Workers/worker_core_reargunner_character_refinement01.py"
FUTURE_ATTEMPT = ROOT / "Production/Attempts/core-reargunner-character-refinement01"


class VerificationError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise VerificationError(f"JSON root is not an object: {path}")
    return payload


def verify_record(record: dict[str, Any]) -> None:
    path = Path(str(record["path"]))
    if not path.is_file():
        raise VerificationError(f"Missing authority: {path}")
    if path.stat().st_size != int(record["bytes"]):
        raise VerificationError(f"Byte mismatch: {path}")
    if sha256(path) != str(record["sha256"]):
        raise VerificationError(f"Hash mismatch: {path}")


def verify_manifest_semantics(manifest: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    assets = [item for item in manifest.get("assets", []) if item.get("id") == contract["asset_id"]]
    if len(assets) != int(contract["asset_cardinality"]):
        raise VerificationError("Character asset cardinality mismatch")
    asset = assets[0]
    if asset.get("status") != contract["status"]:
        raise VerificationError("Character status mismatch")
    worker = asset.get("worker", {})
    if worker.get("script") != contract["worker_script"]:
        raise VerificationError("Character worker binding mismatch")
    if int(worker.get("minimum_renders", 0)) != int(contract["minimum_renders"]):
        raise VerificationError("Character minimum-render count mismatch")
    if list(worker.get("arguments", [])) != list(contract["worker_arguments"]):
        raise VerificationError("Character worker argument mismatch")
    legacy = [item for item in manifest.get("assets", []) if item.get("id") == contract["legacy_asset_id"]]
    if len(legacy) != int(contract["legacy_asset_cardinality"]):
        raise VerificationError("Legacy rear-gunner cardinality mismatch")
    if legacy[0].get("status") != contract["legacy_status"]:
        raise VerificationError("Legacy rear-gunner status mismatch")
    return {
        "asset_id": asset["id"],
        "status": asset["status"],
        "worker_script": worker["script"],
        "minimum_renders": worker["minimum_renders"],
        "worker_arguments": worker["arguments"],
        "legacy_status": legacy[0]["status"],
    }


def main() -> int:
    authority = load_json(AUTHORITY)
    expected = "PASSED_READY_FOR_EXPLICIT_SINGLE_REARGUNNER_CHARACTER_REFINEMENT01_RECOVERY01_BLENDER_AUTHORIZATION"
    if authority.get("classification") != expected:
        raise VerificationError("Recovery01 authority classification mismatch")
    records = list(authority.get("authorities", []))
    if not records:
        raise VerificationError("Recovery01 authority contains no records")
    if any(str(record["path"]).lower().endswith("production_manifest.json") for record in records):
        raise VerificationError("Mutable production manifest remains in immutable authority records")
    for record in records:
        verify_record(record)

    original = load_json(ORIGINAL_AUTHORITY)
    original_manifest_records = [
        record for record in original["authorities"] if str(record["path"]).lower().endswith("production_manifest.json")
    ]
    if len(original_manifest_records) != 1:
        raise VerificationError("Original stale-authority root cause is not singular")
    stale = original_manifest_records[0]
    if MANIFEST.stat().st_size == int(stale["bytes"]) or sha256(MANIFEST) == stale["sha256"]:
        raise VerificationError("Original manifest authority is unexpectedly current")

    manifest_result = verify_manifest_semantics(load_json(MANIFEST), authority["manifest_semantic_contract"])

    ast.parse(WORKER.read_text(encoding="utf-8"), filename=str(WORKER))
    worker_source = WORKER.read_text(encoding="utf-8")
    for forbidden in ("np.repeat", "np.tile", "empty_display_type = \"CROSS\"", "empty_display_type = 'CROSS'"):
        if forbidden in worker_source:
            raise VerificationError(f"Worker contains preventive-risk token: {forbidden}")

    supervisor_source = SUPERVISOR.read_text(encoding="utf-8")
    required_tokens = (
        "Assert-ManifestSemanticContract",
        "manifest_semantic_contract",
        "PASS_RECOVERY01_OFFLINE_CONTRACT_TEST",
        "& python $ControllerPath run $AssetId",
        "[Environment]::Exit([int]3)",
        "[Environment]::Exit([int]2)",
    )
    for token in required_tokens:
        if token not in supervisor_source:
            raise VerificationError(f"Recovery01 supervisor missing token: {token}")
    if supervisor_source.count("& python $ControllerPath run $AssetId") != 1:
        raise VerificationError("Recovery01 supervisor launch cardinality is not one")
    for forbidden in ("Start-Process", "while (", "for (;;", "Get-FileHash"):
        if forbidden.lower() in supervisor_source.lower():
            raise VerificationError(f"Recovery01 supervisor contains forbidden construct: {forbidden}")
    if FUTURE_ATTEMPT.exists():
        raise VerificationError(f"Future attempt namespace exists: {FUTURE_ATTEMPT}")

    print(
        json.dumps(
            {
                "schema": "skyguard.phase2.reargunner-character-refinement01-recovery01.offline-verification.v1",
                "classification": "PASS",
                "authority_records": len(records),
                "whole_manifest_hash_removed": True,
                "original_manifest_bytes": stale["bytes"],
                "current_manifest_bytes": MANIFEST.stat().st_size,
                "original_manifest_sha256": stale["sha256"],
                "current_manifest_sha256": sha256(MANIFEST),
                "manifest_semantics": manifest_result,
                "worker_bytes": WORKER.stat().st_size,
                "worker_sha256": sha256(WORKER),
                "supervisor_bytes": SUPERVISOR.stat().st_size,
                "supervisor_sha256": sha256(SUPERVISOR),
                "future_attempt_absent": True,
                "blender_launches": 0,
                "unreal_launches": 0,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"classification": "FAIL", "error": f"{type(exc).__name__}: {exc}"}, indent=2))
        raise SystemExit(1)
