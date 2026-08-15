"""Offline verification for the one-shot corridor import and map assembly."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
AUTHOR = ROOT / r"Scripts\ToolchainWave08\m01_coastal_corridor_c06r01_unreal_integration01\author_corridor_integration01.py"
NORMALIZER = ROOT / r"Scripts\ToolchainWave08\m01_coastal_corridor_c06r01_unreal_integration01\normalize_corridor_glb.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\m01_coastal_corridor_c06r01_unreal_integration01\invoke_corridor_integration01_once.ps1"
CONTRACT = ROOT / r"Docs\Toolchain\ToolchainWave08\M01CoastalCorridorC06R01UnrealIntegration01\execution_contract.json"
SOURCE = ROOT / r"Production\Derived\m01-coastal-corridor-correction06-recovery01-unrealready01-normalized01\M01_CoastalCorridor_C06R01_UNREAL_READY.glb"
NORMALIZATION_RECEIPT = SOURCE.parent / "metadata_normalization_receipt.json"
PROJECT = Path(r"D:\SG52T08_ENV01\Skyguard52.uproject")
INPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_EnvironmentCompositionCorrection05Recovery02.umap")
STANDING_AUTHORIZATION = ROOT / r"Production\standing_heavy_process_authorization.json"
EXPECTED = {
    AUTHOR: (21523, "e4860a91acafde03867597c154ac7093ac57b5a7b6e8b64ae7a762b3edd61887"),
    NORMALIZER: (7113, "5561066434af7f7a166cdcaf861289d5710e8d4126d438d574aa3be832d33280"),
    SOURCE: (48367620, "935ba333c18cc6b8da0083cbee069f35728155a1159fe276140a601d3b591e93"),
    NORMALIZATION_RECEIPT: (2072, "183e140104694f04b483a517ef9d744d9aec988a1d79c1ce7f1e9f5d7827595c"),
    PROJECT: (3703, "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"),
    INPUT_MAP: (781174, "d868fc50959eda83e3e4d9dc495e95ea0fd9d83e34ebdd191a6cd43a5b0c04cd"),
    STANDING_AUTHORIZATION: (2146, "48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089"),
}
FUTURE_PATHS = (
    Path(r"D:\SG52T08_ENV01\Content\M01\CoastalCorridorC06R01"),
    Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01.umap"),
    ROOT / r"Saved\BuildAttempts\M01_COASTAL_CORRIDOR_C06R01_UNREAL_INTEGRATION01\attempt_01",
    ROOT / r"Saved\Reports\M01_COASTAL_CORRIDOR_C06R01_UNREAL_INTEGRATION01_TERMINAL_SUPERVISOR.json",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


for path, (expected_bytes, expected_hash) in EXPECTED.items():
    require(path.is_file(), f"Authority missing: {path}")
    require(path.stat().st_size == expected_bytes, f"Authority byte mismatch: {path}")
    require(sha256(path) == expected_hash, f"Authority hash mismatch: {path}")

contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
require(contract["classification"] == "READY_FOR_SINGLE_GOVERNED_UNREAL_EXECUTION", "Contract classification changed")
require(contract["execution"]["unreal_launches"] == 1, "One-launch contract changed")
require(contract["execution"]["automatic_retries"] == 0, "Zero-retry contract changed")
require(contract["map_edit"]["expected_actor_count_after"] == 100, "Final actor-count contract changed")
normalization = json.loads(NORMALIZATION_RECEIPT.read_text(encoding="utf-8"))
require(normalization["classification"] == "PASSED_METADATA_NORMALIZATION_READY_FOR_UNREAL_IMPORT", "Normalization is not accepted")
require(normalization["geometry_modified"] is False and normalization["materials_modified"] is False, "Normalization exceeded metadata scope")

author = AUTHOR.read_text(encoding="utf-8")
compile(author, str(AUTHOR), "exec")
for token in (
    "AssetImportTask",
    "import_asset_tasks([task])",
    "new_level_from_template(OUTPUT_ASSET, INPUT_ASSET)",
    "levels.save_current_level()",
    "corridor_surface_z_cm",
    "contact_asset_imported_not_spawned",
    "EXPECTED_REMOVED = 43",
    "EXPECTED_ACTORS_AFTER = 100",
):
    require(token in author, f"Required authoring token missing: {token}")
require(author.count("import_asset_tasks([task])") == 1, "Import invocation count is not one")
require(author.count("new_level_from_template(OUTPUT_ASSET, INPUT_ASSET)") == 1, "Map clone invocation count is not one")
require(author.count("levels.save_current_level()") == 1, "Map save invocation count is not one")
for forbidden in (
    "replace_existing = True",
    "save_asset(INPUT_ASSET",
    "save_current_level(INPUT_ASSET",
    "M01_C06R01_Corridor_CONTACT",
):
    require(forbidden not in author, f"Forbidden authoring token present: {forbidden}")

require(SUPERVISOR.is_file(), f"Supervisor missing: {SUPERVISOR}")
supervisor = SUPERVISOR.read_text(encoding="utf-8")
require(supervisor.count("Start-Process") == 1, "Supervisor launch count is not one")
for token in ("-nullrhi", "AuthorizeSingleUnreal", "retry_count=0", "TimeoutSeconds=1800"):
    require(token in supervisor, f"Supervisor contract token missing: {token}")
require(
    "$Editor='D:\\UE_5.8\\Engine\\Binaries\\Win64\\UnrealEditor-Cmd.exe'" in supervisor,
    "Exact UnrealEditor-Cmd authority is not bound",
)

for path in FUTURE_PATHS:
    require(not path.exists(), f"Fresh future namespace exists: {path}")

print("PASS_M01_COASTAL_CORRIDOR_C06R01_UNREAL_INTEGRATION01_OFFLINE")
