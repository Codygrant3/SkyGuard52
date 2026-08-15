"""Offline checks for the consolidated UE 5.8 import re-probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
AUTHORITIES = {
    ROOT / r"Scripts\ToolchainWave08\environment_visible_kit_import_probe01\probe_visible_kit_import01.py": "20cf9b0fd2a2d8a9b60939b5b63a29527d66569d695b01c6dc9620b04d3d1955",
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady01_MetadataNormalized01\exports\SM_M01_Apartment_Production_A_UNREAL_READY.glb": "c1ecb14007710c4aaa4dd0c363177cba6ea4411eeeae495b56ca2e89a0f5e09a",
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady01_MetadataNormalized01\metadata_normalization_receipt.json": "2f057979659d29d5b83fa0fd4540d61433f8de0c805a536a630807ba72dec44a",
    ROOT / r"Production\standing_heavy_process_authorization.json": "48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089",
    Path(r"D:\SG52T08_ENV01\Skyguard52.uproject"): "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a",
    Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack03.umap"): "c68de75000c25569f38b9307fd8760cce85236e2f3166785350ea0c641de81e8",
    Path(r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"): "0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0",
}
FUTURE = (
    ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE01\attempt_01",
    ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_REPROBE01_TERMINAL_SUPERVISOR.json",
    Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\VisibleKitImportReprobe01"),
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
    source = (ROOT / r"Scripts\ToolchainWave08\environment_visible_kit_import_reprobe01\probe_visible_kit_import_reprobe01.py").read_text(encoding="utf-8")
    require("2 <= static_mesh_count <= 4" in source, "StaticMesh budget missing")
    require("EditorLevelLibrary" not in source and "save_current_level" not in source, "Map authoring API forbidden")
    contract = json.loads((ROOT / r"Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentKitImportReprobe01\execution_contract.json").read_text(encoding="utf-8"))
    require(contract["execution"]["map_load"] is False and contract["execution"]["map_save"] is False, "Map boundary changed")
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
