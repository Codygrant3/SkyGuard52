from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
BINDER = ROOT / r"Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_ground_lighting_correction04_recovery01\author_ground_lighting_correction04_recovery01.py"
ORIGINAL = ROOT / r"Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_ground_lighting_correction04\author_ground_lighting_correction04.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_ground_lighting_correction04_recovery01\invoke_authoring_once.ps1"
ORIGINAL_SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_ground_lighting_correction04\invoke_authoring_once.ps1"
CONTRACT = ROOT / r"Docs\Toolchain\ToolchainWave08\M01PhotorealFoundationGroundLightingCorrection04Recovery01\quality_contract.json"
SOURCE_MAP = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_StructuralCleanup03.umap")
OUTPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_GroundLightingCorrection04Recovery01.umap")
MATERIAL_DIRECTORY = Path(r"D:\SG52T08_ENV01\Content\M01\GroundLightingCorrection04Recovery01")
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_AUTHORING\attempt_01"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


binder = BINDER.read_text(encoding="utf-8")
original = ORIGINAL.read_text(encoding="utf-8")
supervisor = SUPERVISOR.read_text(encoding="utf-8")
original_supervisor = ORIGINAL_SUPERVISOR.read_text(encoding="utf-8")
contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
ast.parse(binder, filename=str(BINDER))
ast.parse(original, filename=str(ORIGINAL))

require(ORIGINAL.stat().st_size == 20684, "Original source byte count changed")
require(sha256(ORIGINAL) == "eba032612dd1ee9de55560b1fef1ec8f88fdf608d96121ef3d1c08132ce818b3", "Original source hash changed")
require(contract["classification"] == "PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_UNREAL_AUTHORING", "Contract classification changed")
require("_known_ue58_false_return = success" in binder, "UE 5.8 compatibility correction missing")
require(binder.count("require(bool(success)") == 2, "Compatibility-binding source token changed")
require('("GroundLightingCorrection04", "GroundLightingCorrection04Recovery01", 6)' in binder, "Fresh namespace binding changed")
require('("GROUND_LIGHTING_CORRECTION04", "GROUND_LIGHTING_CORRECTION04_RECOVERY01", 4)' in binder, "Attempt binding changed")
require("verify_vector" in binder and "exec(compiled, scope, scope)" in binder, "Readback or execution boundary missing")
require(supervisor.count("Start-Process") == 0, "Compatibility wrapper must not add a launch path")
require(original_supervisor.count("Start-Process") == 1, "Frozen bound supervisor launch count changed")
require("[scriptblock]::Create($source)" in supervisor, "Bound supervisor execution missing")
require("retry_count = 0" in supervisor, "Zero-retry evidence missing")
require("standing_heavy_process_authorization.json" in original_supervisor, "Standing authorization missing from bound supervisor")
require(SOURCE_MAP.is_file() and SOURCE_MAP.stat().st_size == 738931, "Accepted source map changed")
require(not OUTPUT_MAP.exists(), "Fresh Recovery01 output exists")
require(not MATERIAL_DIRECTORY.exists(), "Fresh Recovery01 material namespace exists")
require(not ATTEMPT.exists(), "Fresh Recovery01 attempt exists")

print("PASS")
