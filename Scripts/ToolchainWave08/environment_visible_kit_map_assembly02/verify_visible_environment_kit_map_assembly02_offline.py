"""Offline contract validation for the reversible Mission 1 map assembly."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
AUTHOR = ROOT / "Scripts/ToolchainWave08/environment_visible_kit_map_assembly02/author_visible_environment_kit_map_assembly02.py"
CONTRACT = ROOT / "Docs/Toolchain/ToolchainWave08/M01VisibleEnvironmentKitMapAssembly02/execution_contract.json"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    source = AUTHOR.read_text(encoding="utf-8")
    ast.parse(source, filename=str(AUTHOR))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    required_tokens = (
        'OUTPUT_ASSET = "/Game/M01/Lvl_M01_VisibleEnvironmentKit02"',
        "new_level_from_template(OUTPUT_ASSET, INPUT_ASSET)",
        "EXPECTED_REMOVED_COUNT = 99",
        "EXPECTED_CREATED_COUNT = 92",
        "EXPECTED_FINAL_COUNT = 179",
        "district_centers_x = [3000.0, 17000.0, 31000.0, 45000.0]",
        "sample_landscape_footprint",
        "unreal.ComponentMobility.STATIC",
        "levels.save_current_level()",
        "PASSED_M01_VISIBLE_ENVIRONMENT_KIT_MAP_ASSEMBLY02_AUTOMATIC",
    )
    require(all(token in source for token in required_tokens), "Assembly source is missing a required contract token")
    forbidden = (
        "save_loaded_asset",
        "save_directory",
        "delete_asset",
        "rename_asset",
        "M01_RS01_CrossStreet_",
        "M01_RS01_Tree_",
        "M01_RS01_Radar_Hero",
    )
    require(not any(token in source for token in forbidden), "Assembly source contains a forbidden mutation token")
    require(contract["classification"] == "PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_UNREAL_MAP_ASSEMBLY", "Contract classification changed")
    require(contract["actor_contract"] == {"before": 186, "removed": 99, "created": 92, "after": 179}, "Actor contract changed")
    require(contract["heavy_process_policy"]["maximum_concurrent_heavy_processes"] == 1, "Heavy-process policy changed")
    require(contract["heavy_process_policy"]["automatic_retries"] == 0, "Retry policy changed")
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
