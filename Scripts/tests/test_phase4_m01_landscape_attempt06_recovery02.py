from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
from phase4_m01_landscape_attempt06_contract import load_attempt06_contract
from phase4_m01_landscape_repair_contract import load_attempt05_contract
from verify_skyguard_phase4_m01_landscape_visible_gpu_gate import (
    analyze_csv,
    normalized_repaired_capture_thresholds,
)


CONTRACT = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT06_RECOVERY02_CONTRACT.json"
)
SUPERVISOR = (
    ROOT
    / "Scripts/"
    "supervise_skyguard_phase4_m01_landscape_visible_"
    "attempt06_recovery02.py"
)
READINESS = (
    ROOT
    / "Scripts/"
    "verify_skyguard_phase4_m01_landscape_attempt06_"
    "recovery02_readiness.py"
)
LAUNCHER = (
    ROOT
    / "Scripts/"
    "run_skyguard_phase4_m01_landscape_visible_attempt06_recovery02.ps1"
)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8-sig"))


def test_recovery02_root_cause_is_the_exact_attempt06_schema_mismatch():
    cause = contract()["root_cause"]
    assert cause["classification"] == (
        "ATTEMPT06_VISUAL_THRESHOLD_SCHEMA_ADAPTER_MISSING"
    )
    assert cause["failing_function"] == "analyze_attempt05_visuals"
    assert cause["caller"] == "analyze_attempt06_visuals"
    assert cause["exception"] == (
        "KeyError: minimum_landscape_pixel_fraction_by_camera"
    )
    assert cause["unreal_evidence_failure"] is False
    assert cause["capture_failure"] is False
    assert cause["profile_failure"] is False
    assert cause["offline_gate_implementation_failure"] is True


def test_recovery02_inventory_is_exhaustive_and_all_hashes_are_exact():
    spec = contract()["recovery01_evidence"]["inventory"]
    inventory_path = ROOT / spec["file"]
    assert sha256_file(inventory_path) == spec["sha256"]
    inventory = json.loads(
        inventory_path.read_text(encoding="utf-8-sig")
    )
    source_root = ROOT / inventory["source_root"]
    expected = {
        item["file"].replace("\\", "/") for item in inventory["files"]
    }
    actual = {
        path.relative_to(source_root).as_posix()
        for path in source_root.rglob("*")
        if path.is_file()
    }
    assert actual == expected
    for item in inventory["files"]:
        path = source_root / item["file"]
        assert path.stat().st_size == item["bytes"]
        assert sha256_file(path) == item["sha256"]
    for item in inventory["external_profile_csv_files"]:
        path = ROOT / item["file"]
        assert path.stat().st_size == item["bytes"]
        assert sha256_file(path) == item["sha256"]


def test_recovery02_normalizes_attempt05_and_attempt06_threshold_schemas():
    expected = contract()["threshold_normalization"][
        "normalized_camera_thresholds"
    ]
    legacy = normalized_repaired_capture_thresholds(
        load_attempt05_contract()
    )
    current = normalized_repaired_capture_thresholds(
        load_attempt06_contract()
    )
    assert legacy["minimum_landscape_pixel_fraction_by_camera"] == expected
    assert current["minimum_landscape_pixel_fraction_by_camera"] == expected
    assert legacy["readability_inside_coverage_mask"] == current[
        "readability_inside_coverage_mask"
    ]


def test_recovery02_normalizer_rejects_duplicate_and_invalid_thresholds():
    duplicate = load_attempt06_contract()
    duplicate["repair"]["capture_revision"]["cameras"].append(
        duplicate["repair"]["capture_revision"]["cameras"][0].copy()
    )
    with pytest.raises(ValueError):
        normalized_repaired_capture_thresholds(duplicate)
    invalid = load_attempt06_contract()
    invalid["repair"]["capture_revision"]["cameras"][0][
        "minimum_landscape_pixel_fraction"
    ] = 1.01
    with pytest.raises(ValueError):
        normalized_repaired_capture_thresholds(invalid)


def test_recovery02_uses_immutable_csv_memory_only_when_stage_peak_is_absent():
    spec = contract()
    inventory = json.loads(
        (
            ROOT / spec["recovery01_evidence"]["inventory"]["file"]
        ).read_text(encoding="utf-8-sig")
    )
    csv_metrics = [
        analyze_csv(ROOT / item["file"])
        for item in inventory["external_profile_csv_files"]
    ]
    assert all(item["parseable"] for item in csv_metrics)
    assert all(
        item["metrics"]["peak_physical_used_mib"] is not None
        for item in csv_metrics
    )
    gate_source = text(
        ROOT
        / spec["offline_gate_implementation"]["source"]
    )
    assert "supervisor_stage_peak_working_set_mib" in gate_source
    assert "immutable_csv_PhysicalUsedMB" in gate_source
    assert 're.compile(r"^PhysicalUsedMB$"' in gate_source
    assert "peak_working_set_source" in gate_source


def test_recovery02_supervisor_is_offline_only_and_refuses_overwrite():
    source = text(SUPERVISOR)
    ast.parse(source)
    assert "--authorize-offline-recovery-run" in source
    assert "verify_recovery01_inventory" in source
    assert "verify_recovery01_boundary" in source
    assert "Recovery02 root already exists" in source
    assert "UnrealEditor" not in source
    assert "Build.bat" not in source
    assert "capture_skyguard" not in source
    assert "ProfileWarmupSeconds" not in source
    assert '"unreal_launched": False' in source
    assert '"captures_rerun": False' in source
    assert '"profiles_rerun": False' in source
    assert '"promotion_allowed": False' in source


def test_recovery02_contract_and_launcher_require_one_offline_authorization():
    spec = contract()
    execution = spec["recovery_execution"]
    for field in (
        "unreal_launch_allowed",
        "blender_launch_allowed",
        "build_allowed",
        "authoring_allowed",
        "capture_allowed",
        "profile_allowed",
        "network_allowed",
        "automatic_retry_allowed",
        "source_recovery_mutation_allowed",
        "promotion_allowed",
        "duplicate_or_overwrite_allowed",
    ):
        assert execution[field] is False
    assert not (ROOT / execution["root"]).exists()
    launcher = text(LAUNCHER)
    assert "if (-not $AuthorizeOfflineRecoveryRun)" in launcher
    assert "--authorize-offline-recovery-run" in launcher
    ast.parse(text(READINESS))
