"""Fresh D3D12|SM6 read-only render-state verifier for Recovery01."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
import verify_skyguard_phase4_m01_landscape_material_assets as verifier
from phase4_m01_landscape_attempt06_contract import load_attempt06_contract


RECOVERY_CONTRACT = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT06_RECOVERY01_CONTRACT.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def parse_switch(name: str) -> str:
    command_line = unreal.SystemLibrary.get_command_line()
    match = re.search(
        rf'(?:^|\s)-{re.escape(name)}=(?:"([^"]+)"|(\S+))',
        command_line,
        re.IGNORECASE,
    )
    if not match:
        raise RuntimeError("Missing required -" + name + " switch")
    return match.group(1) or match.group(2)


def main() -> None:
    recovery = json.loads(
        RECOVERY_CONTRACT.read_text(encoding="utf-8-sig")
    )
    output = Path(parse_switch("SkyguardAttempt06RecoveryReceipt"))
    if output.exists():
        raise RuntimeError("Recovery render-state receipt already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    rhi = (
        unreal.SkyguardMission01EnvironmentAuthoringLibrary
        .get_active_rhi_and_feature_level()
        .strip()
        .upper()
    )
    if rhi != "D3D12|SM6":
        raise RuntimeError(
            "Recovery01 render-state verification requires D3D12|SM6; "
            + "reported "
            + repr(rhi)
        )
    before = {}
    for name, item in recovery["immutable_packages"].items():
        path = ROOT / item["file"]
        if not path.is_file():
            raise RuntimeError("Missing immutable package: " + str(path))
        before[name] = sha256_file(path)
        if before[name] != item["sha256"]:
            raise RuntimeError("Immutable package hash failed: " + str(path))
    verifier.REPORT_PATH = output
    verifier.load_effective_contract = load_attempt06_contract
    verifier.main()
    report = json.loads(output.read_text(encoding="utf-8-sig"))
    after = {
        name: sha256_file(ROOT / item["file"])
        for name, item in recovery["immutable_packages"].items()
    }
    report.update(
        {
            "schema": (
                "skyguard.phase4.m01-landscape-attempt06-"
                "recovery01-render-state.v1"
            ),
            "recovery_id": recovery["recovery_id"],
            "rhi_validation": rhi,
            "package_hashes_before": before,
            "package_hashes_after": after,
            "package_hashes_unchanged": before == after,
            "world_saved": False,
            "pcg_generation_invoked": False,
        }
    )
    render_count = report["landscape_visible_audit"][
        "render_state_created_component_count"
    ]
    if not (
        report.get("gate") == "PASS"
        and rhi == "D3D12|SM6"
        and render_count == 16
        and before == after
    ):
        report["gate"] = "FAIL"
        output.write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        raise RuntimeError("Recovery01 D3D12 render-state gate failed")
    output.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    unreal.log(
        "[SkyguardP46Recovery01RenderState] " + json.dumps(report)
    )


if __name__ == "__main__":
    main()
