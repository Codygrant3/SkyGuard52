"""Offline prevention checks for the Unreal-safe full-kit import Recovery01."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
IMPORTER = ROOT / r"Scripts\ToolchainWave08\environment_visible_kit_full_import01_recovery01\import_visible_environment_kit01_recovery01.py"
CONTRACT = ROOT / r"Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentKitFullImport01Recovery01\execution_contract.json"
AUTHORITIES = {
    IMPORTER: "a1a7e6d301ce01b540462c8f15dcbb2036c18f566fe1e6c122a72d4f5aee3636",
    ROOT / r"Scripts\ToolchainWave08\environment_visible_kit_full_import01\import_visible_environment_kit01.py": "5db48b5f2862a6406b12534e85137f2a98021058816976f1f2e1f94d5191e3df",
    CONTRACT: "bc0fa66bcdf9c3b0f7750f96ccebfd8a8467c3ed303d2de64c7568bd83e25429",
    ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_METADATA_NORMALIZATION02_ACCEPTANCE_FREEZE.json": "f0e6880f7a628960bdf02ef16026b4226d2ed5a78b81933ce10246d51990edbb",
    ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_ATTEMPT01_TERMINAL_FREEZE.json": "ac9f4cdc6bcb75bfd93c0ea2b1dd9484543c63ca6d194d9a1a4258b37ad62712",
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02_MetadataNormalized01\exports\M01_APARTMENT_A.glb": "62f117c58a9cbe02e57ffe7ebcdc4d1b7ad7401635ecc5ef0ad1f2f07281b33a",
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02_MetadataNormalized01\exports\M01_COASTAL_DISTRICT_A.glb": "7c42cd930495aa39ef58a4e7f80b02b2b3af7f345f5477bff3130fd0bd6d7b34",
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02_MetadataNormalized01\exports\M01_CORNER_RESIDENCE_C.glb": "809aeb6e36256279320ed7688e81f9f14eb4553b027a711c277309cda6e24702",
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02_MetadataNormalized01\exports\M01_LIGHTHOUSE_A.glb": "e0502f12494a031a1187ea85defa11ac8038910301cd0bb4bf743dca17f7ba0a",
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady02_MetadataNormalized01\exports\M01_MIDRISE_B.glb": "5d93c46206631953b8affacee6bb757ef7bab674476276df08b61ff684cbc794",
    ROOT / r"Production\standing_heavy_process_authorization.json": "48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089",
    Path(r"D:\SG52T08_ENV01\Skyguard52.uproject"): "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a",
    Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack03.umap"): "c68de75000c25569f38b9307fd8760cce85236e2f3166785350ea0c641de81e8",
    Path(r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"): "0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0",
}
FUTURE = (
    ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_RECOVERY01\attempt_01",
    ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_FULL_IMPORT01_RECOVERY01_TERMINAL_SUPERVISOR.json",
    Path(r"D:\SG52T08_ENV01\Content\M01\EnvKit02"),
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
    require(result.returncode == 0 and "PASS_FULL_KIT_GLTF_CONTRACT" in result.stdout, f"Recovery01 transformed GLB contract failed: {result.stdout} {result.stderr}")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(contract["fresh_destination"] == "/Game/M01/EnvKit02", "Short destination changed")
    require(contract["acceptance"]["static_mesh_count"] == 14, "StaticMesh count changed")
    require(contract["acceptance"]["material_slot_total"] == 54, "Material-slot total changed")
    require(contract["acceptance"]["maximum_governed_object_name_length"] == 40, "Object-name ceiling changed")
    require(contract["execution"]["automatic_retries"] == 0, "Retry contract changed")
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
