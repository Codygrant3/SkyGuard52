"""Offline readiness checks for the Unreal-ready environment consolidation."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
AUTHORITIES = {
    ROOT / r"Production\standing_heavy_process_authorization.json": "48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089",
    ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT02_ACCEPTANCE_FREEZE.json": "efc54d13040f45efbabcb9e55d99754be161c15fc80804e5ea30440deb368284",
    ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_IMPORT_PROBE01_ACCEPTANCE_FREEZE.json": "892a29460ca6e0872eca4bc58dbbd483bf619f0bf863a3ecad05b5e78e7a098a",
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_Checkpoint02\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT02.blend": "0ef89cd08cb224f1d21015cfb1c968c1b66d8916c29c4702e129766a215093eb",
    ROOT / r"Scripts\ToolchainWave08\environment_visible_kit_unreal_ready01\build_visible_environment_unreal_ready01.py": "9dc543d6443e35f12cb9d50e7d577f58d869447f7bdcdcd907389d94599eb21b",
    ROOT / r"Scripts\ToolchainWave08\environment_visible_kit_unreal_ready01\adjudicate_visible_environment_unreal_ready01.py": "8285d3e8640ed286618f2b37241e56445949b836c1d6dac9c5873e6269876262",
    ROOT / r"Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentUnrealReady01\execution_contract.json": "a1a792b0fc567ca6b6c38d224839840ef61d202f3ee204ee3c0bf4dc2cd713c5",
    Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"): "e27fbfea8564aa645d4463cb0949695fd85562b9de6df9561b06859a1074adf7",
}
FUTURE = (
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady01",
    ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_UNREAL_READY01\attempt_01",
    ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_UNREAL_READY01_TERMINAL_SUPERVISOR.json",
    ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_UNREAL_READY01_POSTFLIGHT.json",
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
        require(path.is_file(), f"Missing authority: {path}")
        require(sha256(path) == expected, f"Authority hash mismatch: {path}")
    for path in FUTURE:
        require(not path.exists(), f"Fresh namespace already exists: {path}")

    auth = json.loads((ROOT / r"Production\standing_heavy_process_authorization.json").read_text(encoding="utf-8"))
    require(auth["status"] == "ACTIVE", "Standing authorization is inactive")
    require(auth["execution_policy"]["per_run_user_authorization_required"] is False, "Per-run authorization unexpectedly required")
    contract = json.loads((ROOT / r"Docs\Toolchain\ToolchainWave08\M01VisibleEnvironmentUnrealReady01\execution_contract.json").read_text(encoding="utf-8"))
    require(contract["group_contract"]["total_render_groups"] == 14, "Render-group contract changed")
    require(contract["execution_policy"]["automatic_retries"] == 0, "Retry contract changed")

    generator = (ROOT / r"Scripts\ToolchainWave08\environment_visible_kit_unreal_ready01\build_visible_environment_unreal_ready01.py").read_text(encoding="utf-8")
    require("failed_geometry_read\": False" in generator, "Failed-geometry exclusion missing")
    require("total_groups == 14" in generator, "Fourteen-group assertion missing")
    require("EXCLUDED_TOKENS" in generator and "_WATER" in generator and "_LEAF_" in generator, "Runtime-system exclusions missing")
    require("bpy.ops.wm.open_mainfile" not in generator, "Generator may not redirect to an alternate blend")
    require(len(re.findall(r"bpy\.ops\.wm\.save_as_mainfile", generator)) == 1, "Expected one governed save path")
    require(len(re.findall(r"bpy\.ops\.export_scene\.gltf", generator)) == 1, "Expected one bounded export implementation")
    forbidden_map_apis = ("EditorLevelLibrary", "LevelEditorSubsystem", ".umap", "load_level(", "save_current_level")
    require(not any(token in generator for token in forbidden_map_apis), "Generator may not author or save an Unreal map")
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
