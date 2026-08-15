"""Offline prevention checks for the five-GLB visible-environment kit import."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
IMPORTER = ROOT / r"Scripts\ToolchainWave08\environment_visible_kit_full_import01\import_visible_environment_kit01.py"
CONTRACT = ROOT / r"Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentKitFullImport01\execution_contract.json"
AUTHORITIES = {
    IMPORTER: "5db48b5f2862a6406b12534e85137f2a98021058816976f1f2e1f94d5191e3df",
    CONTRACT: "783ca2f4196a7b41153f1403590f2c3b0ce776ef88e2745544e6ae10ac0c001d",
    ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE03_ACCEPTANCE_FREEZE.json": "ce332b3648c848eaead2c898e27dd215c949758bf46350d15574daa889f29184",
    ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_UNREAL_READY02_ACCEPTANCE_FREEZE.json": "9f0bce85b5011ca8b002e52fdb651fffe6adcb10f541c74583cc13599199dc20",
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02\exports\SM_M01_Apartment_Production_A_CONSOLIDATED.glb": "77b04f21f75f97b337eb89d142b5d672d9be5eaaa79184ee9f44421d35e51080",
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02\exports\SM_M01_CoastalDistrict_Production_A_CONSOLIDATED.glb": "7c76f069a0f72592b4cdf0928529c1fc35405fa175cea27f5697124313f85c0a",
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02\exports\SM_M01_CornerResidence_Production_C_CONSOLIDATED.glb": "6c5fe2a8ce70a4dbf0d0bec910261e7eef68183ca6103f3b756c4f0f0065cdb8",
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02\exports\SM_M01_Lighthouse_Production_A_CONSOLIDATED.glb": "50e38c728d2497a6689bd352dcc8c4cb3de0e9ab8f2dfb50b5d518680d608301",
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02\exports\SM_M01_Midrise_Production_B_CONSOLIDATED.glb": "6c4b22ab84b79510345215772da2649b0cb101089d87336b4604944a74ca3155",
    ROOT / r"Production\standing_heavy_process_authorization.json": "48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089",
    Path(r"D:\SG52T08_ENV01\Skyguard52.uproject"): "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a",
    Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack03.umap"): "c68de75000c25569f38b9307fd8760cce85236e2f3166785350ea0c641de81e8",
    Path(r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"): "0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0",
}
FUTURE = (
    ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01\attempt_01",
    ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_TERMINAL_SUPERVISOR.json",
    Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\VisibleEnvironmentKit01"),
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
    result = subprocess.run([sys.executable, str(IMPORTER), "--offline-contract-test"], check=False, capture_output=True, text=True)
    require(result.returncode == 0 and "PASS_FULL_KIT_GLTF_CONTRACT" in result.stdout, f"Full-kit GLB contract failed: {result.stdout} {result.stderr}")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(contract["acceptance"]["static_mesh_count"] == 14, "StaticMesh count changed")
    require(contract["acceptance"]["material_slot_total"] == 54, "Material-slot total changed")
    require(contract["execution"]["automatic_retries"] == 0, "Retry contract changed")
    require(contract["scope_boundary"]["map_assembly"] is False, "Map-assembly boundary changed")
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
