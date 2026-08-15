"""Offline prevention checks for the material-slot import re-probe."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
PROBE = ROOT / r"Scripts\ToolchainWave08\environment_visible_kit_import_reprobe03\probe_visible_kit_import_reprobe03.py"
CONTRACT = ROOT / r"Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentKitImportReprobe03\execution_contract.json"
AUTHORITIES = {
    PROBE: "31cc367550e26054908bb45435145efde80c989201ae7bd7a8ad4dc580d68bc9",
    CONTRACT: "ea35e1db00a1c84d48681a3c9c921040c8fe4831e6a949b448cdf3edb9f3805f",
    ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_UNREAL_READY02_ACCEPTANCE_FREEZE.json": "9f0bce85b5011ca8b002e52fdb651fffe6adcb10f541c74583cc13599199dc20",
    ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE02_ACCEPTANCE_FREEZE.json": "88b2ac171f48bca55b0643599c7e17137f740b3db15d4c708c42b7838916b202",
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02\exports\SM_M01_Apartment_Production_A_CONSOLIDATED.glb": "77b04f21f75f97b337eb89d142b5d672d9be5eaaa79184ee9f44421d35e51080",
    ROOT / r"Production\standing_heavy_process_authorization.json": "48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089",
    Path(r"D:\SG52T08_ENV01\Skyguard52.uproject"): "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a",
    Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack03.umap"): "c68de75000c25569f38b9307fd8760cce85236e2f3166785350ea0c641de81e8",
    Path(r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"): "0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0",
}
FUTURE = (
    ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE03\attempt_01",
    ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE03_TERMINAL_SUPERVISOR.json",
    Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\VisibleKitImportReprobe03"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    for path, expected in AUTHORITIES.items():
        require(path.is_file() and sha256(path) == expected, f"Authority mismatch: {path}")
    for path in FUTURE:
        require(not path.exists(), f"Fresh namespace exists: {path}")
    result = subprocess.run(
        [sys.executable, str(PROBE), "--offline-contract-test"],
        check=False,
        capture_output=True,
        text=True,
    )
    require(
        result.returncode == 0 and "PASS_GLTF_MATERIAL_CONTRACT" in result.stdout,
        f"GLB material contract failed: {result.stdout} {result.stderr}",
    )
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(contract["acceptance"]["static_mesh_count"] == 3, "StaticMesh count contract changed")
    require(contract["acceptance"]["material_slot_total"] == 13, "Material-slot total changed")
    require(sum(contract["expected_static_meshes"].values()) == 13, "Per-mesh slot contract changed")
    require(contract["execution"]["automatic_retries"] == 0, "Retry contract changed")
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
