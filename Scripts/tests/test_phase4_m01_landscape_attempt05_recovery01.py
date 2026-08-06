from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review"
    / "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT05_RECOVERY_CONTRACT_01.json"
)
VERIFIER = (
    ROOT
    / "Scripts"
    / "verify_skyguard_phase4_m01_landscape_render_state_attempt05_recovery01.py"
)
SUPERVISOR = (
    ROOT
    / "Scripts"
    / "run_skyguard_phase4_m01_landscape_visible_attempt05_recovery01.ps1"
)
READINESS = (
    ROOT
    / "Scripts"
    / "verify_skyguard_phase4_m01_landscape_attempt05_recovery01_readiness.py"
)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))


def test_recovery_contract_locks_every_predecessor_and_package():
    spec = contract()
    assert spec["recovery_id"].endswith("RECOVERY-01")
    assert spec["recovery_execution"]["authoring_stage_forbidden"] is True
    assert spec["recovery_execution"]["nullrhi_forbidden"] is True
    assert spec["idempotency"]["automatic_retry_allowed"] is False
    assert len(spec["immutable_packages"]) == 5
    for section in (
        "immutable_predecessor_evidence",
        "immutable_packages",
    ):
        for item in spec[section].values():
            path = ROOT / item["file"]
            assert path.is_file()
            assert sha256_file(path) == item["sha256"]


def test_recovery_contract_records_the_exact_nullrhi_fault():
    spec = contract()
    author = json.loads(
        (
            ROOT
            / spec["immutable_predecessor_evidence"]["authoring_report"][
                "file"
            ]
        ).read_text(encoding="utf-8-sig")
    )
    failed = json.loads(
        (
            ROOT
            / spec["immutable_predecessor_evidence"][
                "failed_nullrhi_acceptance"
            ]["file"]
        ).read_text(encoding="utf-8-sig")
    )
    assert author["landscape_visible_audit"][
        "render_state_created_component_count"
    ] == 16
    assert failed["landscape_visible_audit"][
        "render_state_created_component_count"
    ] == 0
    assert failed["landscape_visible_audit"][
        "contract_camera_frustum_intersection_count"
    ] == 5


def test_recovery_verifier_requires_d3d12_sm6_before_audit():
    source = text(VERIFIER)
    rhi = source.index("if rhi != EXPECTED_RHI:")
    audit = source.index("verifier.main()")
    assert rhi < audit
    assert 'EXPECTED_RHI = "D3D12|SM6"' in source
    assert "locked_package_hashes(recovery)" in source
    assert '"world_saved"] = False' in source
    assert '"pcg_generation_invoked"] = False' in source
    assert "save_asset" not in source
    assert "generate_pcg" not in source.lower()


def test_recovery_supervisor_never_authors_and_gates_before_capture():
    source = text(SUPERVISOR)
    assert (
        "build_skyguard_phase4_m01_landscape_material_validation"
        not in source
    )
    assert "author_immutable_candidate" not in source
    assert "-NullRHI" not in source
    verifier_stage = source.index(
        '-Name "verify_candidate_render_state_d3d12_sm6"'
    )
    capture_stage = source.index('-Name "$($spec.mode)_capture"')
    assert verifier_stage < capture_stage
    assert "render_state_created_component_count -ne 16" in source
    assert "Get-FileHash" not in source
    assert "[System.Security.Cryptography.SHA256]::Create()" in source


def test_recovery_supervisor_persists_and_hashes_fail_closed():
    source = text(SUPERVISOR)
    start = source.index(
        '-Name "verify_candidate_render_state_d3d12_sm6"'
    )
    persist = source.index("$manifest.stages += $stage", start)
    save = source.index(
        "Save-Json -Value $manifest -Path $ManifestPath", persist
    )
    assert_stage = source.index("Assert-StagePassed -Stage $stage", save)
    assert persist < save < assert_stage
    assert (
        "immutable_package_hashes_after = Get-LockedPackageSnapshot"
        not in source
    )
    assert "Get-LockedPackageSnapshotSafe" in source
    assert "immutable_package_lock_error = $lockResult.error" in source
    assert (
        "Immutable package lock failed after stage" in source
    )
    assert (
        "Recovery root already exists; refuse duplicate or overwrite"
        in source
    )
    assert "-csvCaptureFrames" not in source
    assert "-SkyguardP45ProfileWarmupSeconds=30" in source
    assert "-SkyguardP45ProfileMeasuredSeconds=60" in source


def test_recovery_readiness_is_offline_only():
    source = text(READINESS)
    assert "unreal_launched" in source
    assert "candidate_mutated" in source
    assert (
        "PASS_RECOVERY_OFFLINE_READY_PENDING_EXCLUSIVE_UNREAL_AUTHORIZATION"
        in source
    )
