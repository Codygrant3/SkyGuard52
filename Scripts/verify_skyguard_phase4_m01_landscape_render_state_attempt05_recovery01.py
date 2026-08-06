"""D3D12 SM6 render-state acceptance for the immutable attempt05 candidate.

Run only in a normal Unreal Editor process through -ExecutePythonScript.
This script is read-only with respect to packages and never generates PCG.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
import verify_skyguard_phase4_m01_landscape_material_assets as verifier
from phase4_m01_landscape_repair_contract import load_attempt05_contract


RECOVERY_CONTRACT = (
    ROOT
    / "Docs/AAA_Review"
    / "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT05_RECOVERY_CONTRACT_01.json"
)
REPORT_PATH = (
    ROOT
    / "Saved/Reports"
    / "PHASE4_M01_LANDSCAPE_RENDER_STATE_ACCEPTANCE_ATTEMPT05_RECOVERY01.json"
)
EXPECTED_RHI = "D3D12|SM6"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def locked_package_hashes(contract: dict) -> dict[str, str]:
    hashes = {}
    for name, spec in contract["immutable_packages"].items():
        path = ROOT / spec["file"]
        if not path.is_file():
            raise RuntimeError(f"Missing immutable recovery package: {path}")
        actual = sha256_file(path)
        if actual != spec["sha256"]:
            raise RuntimeError(
                f"Immutable recovery package hash failed for {name}: {actual}"
            )
        hashes[name] = actual
    return hashes


def main() -> None:
    recovery = json.loads(RECOVERY_CONTRACT.read_text(encoding="utf-8-sig"))
    hashes_before = locked_package_hashes(recovery)
    rhi = (
        unreal.SkyguardMission01EnvironmentAuthoringLibrary
        .get_active_rhi_and_feature_level()
        .strip()
        .upper()
    )
    if rhi != EXPECTED_RHI:
        raise RuntimeError(
            f"Recovery verifier requires {EXPECTED_RHI}; Unreal reported {rhi}"
        )
    unreal.log("[SkyguardP45Recovery][RHI_VALIDATED] " + rhi)

    if REPORT_PATH.exists():
        raise RuntimeError(
            "Recovery render-state receipt already exists; never overwrite it"
        )
    verifier.REPORT_PATH = REPORT_PATH
    verifier.load_effective_contract = load_attempt05_contract
    verifier.main()

    report = json.loads(REPORT_PATH.read_text(encoding="utf-8-sig"))
    hashes_after = locked_package_hashes(recovery)
    package_hashes_unchanged = hashes_after == hashes_before
    report["schema"] = (
        "skyguard.phase4.m01-landscape-render-state-acceptance-recovery.v1"
    )
    report["recovery_id"] = recovery["recovery_id"]
    report["execution_mode"] = "normal-editor-render-offscreen"
    report["rhi_validation"] = rhi
    report["immutable_package_hashes_before"] = hashes_before
    report["immutable_package_hashes_after"] = hashes_after
    report["world_saved"] = False
    report["pcg_generation_invoked"] = False
    report["checks"]["d3d12_sm6_exact"] = rhi == EXPECTED_RHI
    report["checks"]["recovery_package_hashes_unchanged"] = (
        package_hashes_unchanged
    )
    report["gate"] = (
        "PASS" if all(report["checks"].values()) else "FAIL"
    )
    report["limitations"] = [
        "This proves fresh normal-editor D3D12 SM6 render readiness before captures.",
        "No package was saved and PCG generation was never invoked.",
        "Visible image and measured performance acceptance remain separate gates.",
    ]
    REPORT_PATH.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    unreal.log("[SkyguardP45RecoveryAcceptance] " + json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("Attempt05 recovery render-state acceptance failed")


if __name__ == "__main__":
    main()
