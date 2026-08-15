from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / r"Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_ground_lighting_correction04\author_ground_lighting_correction04.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_ground_lighting_correction04\invoke_authoring_once.ps1"
CONTRACT = ROOT / r"Docs\Toolchain\ToolchainWave08\M01PhotorealFoundationGroundLightingCorrection04\quality_contract.json"
SOURCE_MAP = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_StructuralCleanup03.umap")
OUTPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_GroundLightingCorrection04.umap")
MATERIAL_DIRECTORY = Path(r"D:\SG52T08_ENV01\Content\M01\GroundLightingCorrection04")
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_AUTHORING\attempt_01"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


source = SOURCE.read_text(encoding="utf-8")
supervisor = SUPERVISOR.read_text(encoding="utf-8")
contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
ast.parse(source, filename=str(SOURCE))

require(contract["classification"] == "PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_UNREAL_AUTHORING", "Contract classification changed")
require(contract["expected_actor_count"] == 120, "Actor-count contract changed")
require(contract["material_count"] == 5, "Material-count contract changed")
require(contract["glazing_actor_count"] == 27, "Glazing-count contract changed")
require(source.count("levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET)") == 1, "Map clone call count changed")
require(source.count("duplicate_material(") == 6, "Material duplication function/call count changed")
require("destroy_actor" not in source and "spawn_actor" not in source, "Actor creation or deletion is prohibited")
require("delete_asset" not in source and "rename_asset" not in source, "Asset deletion or rename is prohibited")
require("TARGET_SAND_TILING = (0.0, 0.0, 70.0, 18.0)" in source, "Sand tiling changed")
require("TARGET_URBAN_TILING = (0.0, 0.0, 126.0, 47.0)" in source, "Urban tiling changed")
require("TARGET_FAR_ALBEDO = (0.018, 0.055, 0.085, 0.5)" in source, "Far-water albedo changed")
require("TARGET_FILL_INTENSITY = 8.0" in source and "TARGET_SKYLIGHT_INTENSITY = 9.0" in source, "Shadow-floor lighting changed")
require("EXPECTED_GLAZING_COUNT = 27" in source, "Glazing expectation changed")
require(supervisor.count("Start-Process") == 1, "Supervisor must contain one Unreal launch")
require("retry_count = 0" in supervisor, "Zero-retry evidence missing")
require("standing_heavy_process_authorization.json" in supervisor, "Standing authorization missing")
require(SOURCE_MAP.is_file(), "Accepted StructuralCleanup03 map missing")
require(SOURCE_MAP.stat().st_size == 738931, "Accepted StructuralCleanup03 byte count changed")
require(not OUTPUT_MAP.exists(), "Fresh output map exists")
require(not MATERIAL_DIRECTORY.exists(), "Fresh material namespace exists")
require(not ATTEMPT.exists(), "Fresh attempt namespace exists")

print("PASS")
