from __future__ import annotations

import hashlib
import json
import py_compile
import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
AUTHOR = ROOT / "Scripts/ToolchainWave08/m01_photoreal_foundation_wave01_environment_composition_correction05/author_environment_composition_correction05.py"
CONTRACT = ROOT / "Docs/Toolchain/ToolchainWave08/M01PhotorealFoundationEnvironmentCompositionCorrection05/quality_contract.json"
INPUT = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_GroundLightingCorrection04Recovery01.umap"
OUTPUT = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_EnvironmentCompositionCorrection05.umap"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_AUTHORING/attempt_01"
TERMINAL = ROOT / "Saved/Reports/M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_AUTHORING_TERMINAL_MANIFEST.json"
AUTHORIZATION = ROOT / "Production/standing_heavy_process_authorization.json"

AUTHORITIES = (
    (INPUT, 743809, "97902b7dd39556d4409adcdd87a8c995cfef1322a8e827c52cae7a84020093cf"),
    (ISOLATED / "Content/Skyguard/Meshes/Mission01/Wave1Refinement/m01_wave1_aaa_refinement/StaticMeshes/SM_M01_Coast_Beach_Detailed_A.uasset", 86515, "13358d6fc16ae1b648275d8bb5f7cbe8c4af92948d20dc2059a598e6b16a2ffe"),
    (ISOLATED / "Content/Skyguard/Meshes/Mission01/Wave1Refinement/m01_wave1_aaa_refinement/StaticMeshes/SM_M01_Road_CoastalTransition_Detailed_A.uasset", 94244, "fa87e9c9cc93d2612c5a461f854234c47cfd91242905e93931a81e103779b144"),
    (ISOLATED / "Content/M01/GroundLightingCorrection04Recovery01/Materials/MI_M01_BeachSand_Tiled.uasset", 75315, "6c99656214d6a827b083156ea9913d9e55c4d4a177bcd891b614509ede83e4e8"),
    (Path(r"D:\UE_5.8\Engine\Plugins\Experimental\Water\Content\Materials\WaterSurface\Water_Material_Ocean.uasset"), 90080, "ee16c08c99c9a8b2b1d24241d37455ae50ba01c877d4f9a77dc1588da2ca7ec6"),
    (Path(r"D:\UE_5.8\Engine\Plugins\Experimental\Water\Content\Materials\WaterSurface\Water_FarMesh.uasset"), 12296, "ccfcf0df2bd5bf9db9cc1e9b7d2394dff546e8faad78f7e999e69102aaf77d6d"),
    (Path(r"D:\UE_5.8\Engine\Plugins\Experimental\Water\Content\Waves\GerstnerWaves_Ocean.uasset"), 7962, "1f76d0c540daff4af14277b34af7f92184a2b0ee76574c51995233bb39edfb2f"),
    (AUTHORIZATION, 2146, "48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089"),
    (ROOT / "Docs/AAA_Review/M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_VISUAL_PROOF01_ATTEMPT01_TERMINAL_FREEZE.json", 4728, "0260193ab363d6c913e346bc561d0b7a65f93fc196f6b9532ebe55cbd8f13068"),
    (ROOT / "Docs/AAA_Review/M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_VISUAL_PROOF01_ATTEMPT01_DIRECT_VISUAL_REVIEW.json", 6899, "c8384f95a850c3c1f231eb0bdc05b2d7aa344f279c282b29d6882d97c7a8d346"),
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


for path, size, expected in AUTHORITIES:
    require(path.is_file(), f"Authority missing: {path}")
    require(path.stat().st_size == size, f"Authority byte mismatch: {path}")
    require(digest(path) == expected, f"Authority hash mismatch: {path}")

require(AUTHOR.is_file() and CONTRACT.is_file(), "Author or contract is missing")
py_compile.compile(str(AUTHOR), doraise=True)
contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
require(contract["classification"] == "PASSED_READY_FOR_OFFLINE_VALIDATION", "Contract classification changed")
authorization = json.loads(AUTHORIZATION.read_text(encoding="utf-8"))
require(authorization["status"] == "ACTIVE", "Standing authorization is inactive")
require(not authorization["execution_policy"]["per_run_user_authorization_required"], "Standing authorization requires per-run dialogue")

source = AUTHOR.read_text(encoding="utf-8")
required_tokens = (
    "EXPECTED_ACTOR_COUNT = 120",
    "EXPECTED_FINAL_ACTOR_COUNT = 140",
    "EXPECTED_BEACH_MODULES = 24",
    "TARGET_ROAD_Z_SCALE = 0.12",
    "set_water_material(ocean_material)",
    "set_water_waves(ocean_waves)",
    "far_distance_material",
    "TARGET_FILM_TOE = 0.40",
    "levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET)",
    "levels.save_current_level()",
)
for token in required_tokens:
    require(token in source, f"Required authoring token missing: {token}")
require(source.count("levels.save_current_level()") == 1, "Author must save exactly one fresh map")
require("save_all_dirty" not in source.lower(), "Author contains broad save path")
require("retry" not in source.lower(), "Author contains retry path")
require(re.search(r"EXPECTED_PREVIOUS_OCEAN_MATERIAL\s*=", source) is not None, "Near-water precondition missing")
require(re.search(r"EXPECTED_PREVIOUS_FAR_MATERIAL\s*=", source) is not None, "Far-water precondition missing")

for future in (OUTPUT, ATTEMPT, TERMINAL):
    require(not future.exists(), f"Future namespace already exists: {future}")

print("PASS")
sys.exit(0)
