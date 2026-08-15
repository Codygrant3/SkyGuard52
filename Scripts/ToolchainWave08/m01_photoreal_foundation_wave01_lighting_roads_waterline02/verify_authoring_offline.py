from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SCRIPT = ROOT / r"Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_lighting_roads_waterline02\author_lighting_roads_waterline02.py"
CONTRACT = ROOT / r"Docs\Toolchain\ToolchainWave08\M01PhotorealFoundationLightingRoadsWaterline02\quality_contract.json"
INPUT = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_NonVegetation01.umap")
OUTPUT = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_LightingRoadsWaterline02.umap")
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_LIGHTING_ROADS_WATERLINE02_AUTHORING\attempt_01"
TERMINAL = ROOT / r"Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_LIGHTING_ROADS_WATERLINE02_AUTHORING_TERMINAL_MANIFEST.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
source = SCRIPT.read_text(encoding="utf-8")
compile(source, str(SCRIPT), "exec")
require(contract["contract_id"] == "M01-PHOTOREAL-FOUNDATION-WAVE01-LIGHTING-ROADS-WATERLINE02", "Contract identity changed")
require(INPUT.stat().st_size == 736476, "Input byte count changed")
require(sha256(INPUT) == "618a260a905680cf5b17c1ac82a114a69f93f947334f45701cd1a8daa2b1f2a1", "Input hash changed")
require(not OUTPUT.exists(), "Fresh output map already exists")
require(not ATTEMPT.exists(), "Fresh attempt namespace already exists")
require(not TERMINAL.exists(), "Fresh terminal namespace already exists")
for token in (
    "M_M01_ConcreteDark",
    "TARGET_FILL_INTENSITY = 4.25",
    "TARGET_SKYLIGHT_INTENSITY = 4.75",
    "TARGET_EXPOSURE_BIAS = 0.85",
    "TARGET_FILM_TOE = 0.42",
    "TARGET_OCEAN_Z_CM = -80.0",
    "TARGET_FAR_WATER_EXTENT_CM = 4_000_000.0",
    "far_distance_material",
    "far_distance_mesh_extent",
    "lower_hemisphere_is_black",
    "levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET)",
):
    require(token in source, f"Required authoring token missing: {token}")
require("destroy_actor" not in source, "Authoring must not delete actors")
require("spawn_actor" not in source, "Authoring must not spawn actors")
print("PASS")
