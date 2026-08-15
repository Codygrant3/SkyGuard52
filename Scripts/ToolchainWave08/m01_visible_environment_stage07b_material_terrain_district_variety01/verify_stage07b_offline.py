"""Offline verification for the Stage 7B material-terrain-district-variety authoring gate."""

from __future__ import annotations

import ast
import json
import py_compile
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
HERE = ROOT / "Scripts/ToolchainWave08/m01_visible_environment_stage07b_material_terrain_district_variety01"


def require(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def assignments(source: str) -> dict[str, object]:
    tree = ast.parse(source)
    wanted = {"NEW_BUILDINGS", "FACADE_BAYS", "VEGETATION_PLACEMENTS", "CHECKPOINT_CAMERAS"}
    result: dict[str, object] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in wanted:
                result[name] = ast.literal_eval(node.value)
    return result


def main() -> int:
    contract_path = HERE / "stage07b_contract.json"
    author = HERE / "author_m01_visible_environment_stage07b_material_terrain_district_variety01.py"
    supervisor = HERE / "invoke_stage07b_authoring_once.ps1"
    inventory = HERE / "material_asset_inventory.json"
    sources = HERE / "source_inventory.json"
    namespace = HERE / "namespace_plan.json"
    cameras = ROOT / "Docs/AAA_Review/M01_VISIBLE_ENVIRONMENT_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_CAMERAS.json"
    visual = ROOT / "Docs/AAA_Review/M01_VISIBLE_ENVIRONMENT_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_VISUAL_RUBRIC.json"
    performance = ROOT / "Docs/AAA_Review/M01_VISIBLE_ENVIRONMENT_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_PERFORMANCE_RUBRIC.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    py_compile.compile(str(author), doraise=True)
    source = author.read_text(encoding="utf-8")
    power = supervisor.read_text(encoding="utf-8")
    values = assignments(source)
    inventory_payload = json.loads(inventory.read_text(encoding="utf-8"))
    source_payload = json.loads(sources.read_text(encoding="utf-8"))
    namespace_payload = json.loads(namespace.read_text(encoding="utf-8"))
    cameras_payload = json.loads(cameras.read_text(encoding="utf-8"))
    visual_payload = json.loads(visual.read_text(encoding="utf-8"))
    performance_payload = json.loads(performance.read_text(encoding="utf-8"))

    require(contract["contract_id"] == "M01-VISIBLE-ENVIRONMENT-STAGE07B-MATERIAL-TERRAIN-DISTRICT-VARIETY01-AUTHORING01", "Contract identity changed")
    require(len(values["NEW_BUILDINGS"]) * 3 == contract["corrections"]["new_building_actors"], "Building actor budget changed")
    require(len(values["FACADE_BAYS"]) * 4 == contract["corrections"]["new_facade_bay_actors"], "Facade-bay actor budget changed")
    require(len(values["VEGETATION_PLACEMENTS"]) == contract["corrections"]["new_vegetation_actors"], "Vegetation actor budget changed")
    require(len({row[0] for row in values["VEGETATION_PLACEMENTS"]}) == 14, "Vegetation cluster count changed")
    require(len({row[1] for row in values["VEGETATION_PLACEMENTS"]}) == 5, "Vegetation species count changed")
    require(len(values["CHECKPOINT_CAMERAS"]) == 3, "Checkpoint camera count changed")
    require(contract["acceptance"]["actor_delta"] == contract["corrections"]["total_new_actors"], "Actor delta changed")
    require(namespace_payload["input_immutable"]["sha256"] == contract["input"]["sha256"], "Namespace input hash drifted")
    require(inventory_payload["coverage"]["acquisition_gap"] is False, "Inventory reports an acquisition gap")
    require(source_payload["new_blender_hero_assets"] is False, "New Blender hero assets are forbidden")
    require(source_payload["quarantined_vegetation_reimport"] is False, "Quarantine reimport is forbidden")
    require(source_payload["procedural_tree_substitutes"] is False, "Procedural tree substitutes are forbidden")
    require(len(cameras_payload["static_cameras"]) == 5 and len(cameras_payload["temporal_cameras"]) == 3, "Final camera set changed")
    require(performance_payload["thresholds"]["p95_frame_ms_max"] == 16.7, "P95 bound changed")
    require("blank white or untextured ground occupies no more than 10 percent" in visual_payload["required_pass_observations"][0], "Visual rubric changed")
    require('runtime_promotion_performed": False' in source, "Runtime-promotion safety missing")
    require("levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET)" in source, "Fresh map clone missing")
    require("levels.save_current_level()" in source, "Fresh map save missing")
    require("MI_M01_Stage07A_DistrictGround" in source, "Forbidden 7A slab guard missing")
    require("hide_line_vegetation" in source, "Line-vegetation hide missing")
    require("capture_checkpoints" in source, "Same-launch checkpoint capture missing")
    require(power.count("Start-Process -FilePath $Editor") == 1, "Supervisor must contain one Unreal launch")
    require("retry_count = 0" in power, "Zero-retry evidence missing")
    require("$TimeoutSeconds = 2400" in power, "Authoring timeout changed")
    require("-d3d12" in power.lower() or "-dx12" in power.lower() or "NullRHI" not in power, "D3D12 authoring launch missing")
    require("NullRHI" not in power, "NullRHI would prevent checkpoint captures")
    for forbidden in ("Remove-Item", "Copy-Item -Recurse", "git reset", "git checkout"):
        require(forbidden not in power, f"Forbidden supervisor operation: {forbidden}")
    require(power.count("Start-Process") == 1, "Alternate heavy-process launch detected")
    require("$process = Start-Process -FilePath $Editor" in power, "Governed UnrealEditor launch missing")
    print("PASS_STAGE07B_MATERIAL_TERRAIN_DISTRICT_VARIETY01_OFFLINE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
