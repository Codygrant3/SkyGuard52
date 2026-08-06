from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT
    / "Docs"
    / "AAA_Review"
    / "GATE7_COMBAT_ART_PRODUCTION_ACCEPTANCE_CONTRACT_2026-08-04.json"
)
AUDIT_PATH = (
    ROOT
    / "Saved"
    / "Reports"
    / "GATE7_COMBAT_ART_CURRENT_STATE_AUDIT_2026-08-04.json"
)

EXPECTED_LANES = {f"G7.{index}" for index in range(1, 9)}
EXPECTED_CLASSIFICATION = "AWAITING_GATE6_AND_EXPLICIT_PRODUCTION_AUTHORIZATION"
REQUIRED_FORBIDDEN_FRAGMENTS = {
    "/Game/Skyguard/Meshes/WebGame",
    "/Game/Skyguard/Meshes/Hero",
    "/Game/Skyguard/Meshes/L88/yak52_l88_silhouette_blockout",
    "/Engine/BasicShapes",
}
SOURCE_MARKERS = {
    ROOT / "Source" / "Skyguard52" / "SkyguardGunner.cpp": (
        "Meshes/WebGame/skyguard-rifle",
        "rifle_ads_proxy",
        "igla_proxy",
        "glove_hand_proxy",
        "glove_arm_proxy",
        "/Engine/BasicShapes",
    ),
    ROOT / "Source" / "Skyguard52" / "SkyguardDrone.cpp": (
        "Meshes/WebGame/skyguard-drone",
        "shahed_proxy",
        "shahed_heavy_proxy",
        "/Engine/BasicShapes",
    ),
    ROOT / "Source" / "Skyguard52" / "SkyguardIglaMissile.cpp": (
        "/Engine/BasicShapes/Cylinder",
    ),
    ROOT / "Source" / "Skyguard52" / "SkyguardPropSpinner.cpp": (
        "propeller_proxy",
        "/Engine/BasicShapes",
    ),
    ROOT / "Source" / "Skyguard52" / "SkyguardYak52Aircraft.cpp": (
        "yak52_l88_silhouette_blockout",
    ),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def verify_record(record: dict[str, Any], failures: list[str]) -> None:
    path = Path(record["path"])
    if not path.is_file():
        failures.append(f"missing authority: {path}")
        return
    actual_bytes = path.stat().st_size
    actual_sha = sha256_file(path)
    if actual_bytes != record["bytes"]:
        failures.append(
            f"byte mismatch: {path}: expected {record['bytes']}, got {actual_bytes}"
        )
    if actual_sha != record["sha256"]:
        failures.append(
            f"hash mismatch: {path}: expected {record['sha256']}, got {actual_sha}"
        )


def run_verification() -> dict[str, Any]:
    failures: list[str] = []
    checks: dict[str, Any] = {}

    contract = load_json(CONTRACT_PATH)
    audit = load_json(AUDIT_PATH)

    checks["contract_schema"] = contract.get("schema")
    checks["audit_schema"] = audit.get("schema")
    checks["classification"] = audit.get("classification")
    checks["lane_ids"] = sorted(lane.get("id") for lane in contract.get("lanes", []))

    if contract.get("current_classification") != EXPECTED_CLASSIFICATION:
        failures.append("contract current classification is not the governed waiting state")
    if audit.get("classification") != EXPECTED_CLASSIFICATION:
        failures.append("audit classification is not the governed waiting state")

    lane_ids = {lane.get("id") for lane in contract.get("lanes", [])}
    if lane_ids != EXPECTED_LANES:
        failures.append(f"lane set mismatch: expected {sorted(EXPECTED_LANES)}, got {sorted(lane_ids)}")

    forbidden = set(
        contract.get("disallowed_as_production_authority", {}).get(
            "path_fragments", []
        )
    )
    if not REQUIRED_FORBIDDEN_FRAGMENTS.issubset(forbidden):
        failures.append("production disallowlist is missing required proxy/WebGame/L88/primitive roots")

    next_gate = contract.get("next_executable_gate", {})
    if next_gate.get("authorization_state") != "NOT_AUTHORIZED_IN_THIS_OFFLINE_GATE":
        failures.append("next heavy gate must remain explicitly unauthorized")

    if audit.get("conclusion", {}).get("gate7_complete") is not False:
        failures.append("audit must not claim Gate 7 completion")
    if audit.get("conclusion", {}).get("production_asset_count_accepted") != 0:
        failures.append("audit must report zero accepted production Gate 7 assets")
    if audit.get("heavy_process_launched") is not False:
        failures.append("offline audit must not claim a heavy process launch")
    if audit.get("project_mutation_performed") is not False:
        failures.append("offline audit must not claim project runtime mutation")

    for record in audit.get("authority_files", []):
        verify_record(record, failures)
    for record in audit.get("source_authorities", []):
        verify_record(record, failures)

    marker_results: dict[str, dict[str, bool]] = {}
    for path, markers in SOURCE_MARKERS.items():
        if not path.is_file():
            failures.append(f"missing source marker authority: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        marker_results[str(path)] = {}
        for marker in markers:
            present = marker in text
            marker_results[str(path)][marker] = present
            if not present:
                failures.append(f"expected current-state marker absent: {path}: {marker}")
    checks["current_source_markers"] = marker_results

    required_performance = {
        "three accepted 1920x1080 input-driven combat captures",
        "one accepted 20-minute input-driven combat soak",
        "contextual first-use shader and PSO review",
        "trace, GPU telemetry and Windows machine-event artifacts",
    }
    observed_performance = set(
        audit.get("performance_state", {}).get("required_missing_evidence", [])
    )
    if not required_performance.issubset(observed_performance):
        failures.append("audit is missing one or more required combat-performance gaps")

    checks["authority_record_count"] = len(audit.get("authority_files", []))
    checks["source_authority_record_count"] = len(
        audit.get("source_authorities", [])
    )
    checks["failure_count"] = len(failures)

    return {
        "schema": "skyguard.aaa.gate7-combat-art-offline-control-verification.v1",
        "gate": "PASS" if not failures else "FAIL",
        "classification": (
            "PASSED_OFFLINE_CONTROL_PACKAGE_AWAITING_GATE6_AND_EXPLICIT_PRODUCTION_AUTHORIZATION"
            if not failures
            else "FAILED_WITH_EVIDENCE"
        ),
        "checks": checks,
        "failures": failures,
    }


def main() -> int:
    try:
        result = run_verification()
    except Exception as exc:
        result = {
            "schema": "skyguard.aaa.gate7-combat-art-offline-control-verification.v1",
            "gate": "FAIL",
            "classification": "FAILED_WITH_EVIDENCE",
            "checks": {},
            "failures": [f"{type(exc).__name__}: {exc}"],
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["gate"] == "PASS" else 3


if __name__ == "__main__":
    sys.exit(main())
