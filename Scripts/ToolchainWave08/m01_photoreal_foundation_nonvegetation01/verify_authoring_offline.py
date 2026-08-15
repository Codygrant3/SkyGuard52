from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
HERE = ROOT / r"Scripts\ToolchainWave08\m01_photoreal_foundation_nonvegetation01"
AUTHOR = HERE / "author_nonvegetation01.py"
CONTRACT = ROOT / r"Docs\Toolchain\ToolchainWave08\M01PhotorealFoundationNonVegetation01\quality_contract.json"
OUTPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_NonVegetation01.umap")
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_NONVEGETATION01_AUTHORING\attempt_01"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


source = AUTHOR.read_text(encoding="utf-8")
ast.parse(source, filename=str(AUTHOR))
contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
require(contract["requirements"]["removed_rejected_pcg_tree_count"] == 60, "Tree-removal contract changed")
require(contract["requirements"]["city_group_count"] == 27, "City-group contract changed")
for token in (
    'startswith("M01_RS01_Tree_")',
    "M_M01_Window",
    "M_M01_Glass",
    "M_ENV_Road_Marking",
    "sample_landscape_footprint",
    "maximum_equal_spacing_repetition_per_row",
    "minimum_adjacent_building_aabb_gap_cm",
    "new_level_from_template",
    "save_current_level",
):
    require(token in source, f"Authoring contract token missing: {token}")
require("Source/M01" not in source and "Content/Skyguard/Candidates" not in source, "Forbidden source or candidate path detected")
require(not OUTPUT_MAP.exists(), "Future output map already exists")
require(not ATTEMPT.exists(), "Future authoring attempt already exists")
print("PASS")
