"""Offline verification for the Stage7A Mission 1 hero-corridor authoring gate."""

from __future__ import annotations

import ast
import json
import py_compile
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
HERE = ROOT / "Scripts/ToolchainWave08/m01_visible_environment_stage07a_hero_corridor01"


def require(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def assignments(source: str) -> dict[str, object]:
    tree = ast.parse(source)
    wanted = {"NEW_BUILDINGS", "VEGETATION_PLACEMENTS", "STREET_DETAILS"}
    result: dict[str, object] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in wanted:
                result[name] = ast.literal_eval(node.value)
    return result


def main() -> int:
    contract_path = HERE / "stage07a_hero_corridor01_contract.json"
    author = HERE / "author_m01_visible_environment_stage07a_hero_corridor01.py"
    supervisor = HERE / "invoke_stage07a_hero_corridor01_authoring_once.ps1"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    py_compile.compile(str(author), doraise=True)
    source = author.read_text(encoding="utf-8")
    power = supervisor.read_text(encoding="utf-8")
    values = assignments(source)

    require(contract["contract_id"] == "M01-VISIBLE-ENVIRONMENT-STAGE07A-HERO-CORRIDOR01-AUTHORING01", "Contract identity changed")
    require(len(values["NEW_BUILDINGS"]) * 3 == contract["corrections"]["new_building_actors"], "Building actor budget changed")
    require(len(values["VEGETATION_PLACEMENTS"]) == contract["corrections"]["new_vegetation_actors"], "Vegetation actor budget changed")
    require(len(values["STREET_DETAILS"]) == contract["corrections"]["new_street_detail_actors"], "Street-detail actor budget changed")
    require(contract["acceptance"]["actor_delta"] == contract["corrections"]["total_new_actors"], "Actor delta changed")
    require('runtime_promotion_performed": False' in source, "Runtime-promotion safety missing")
    require("levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET)" in source, "Fresh map clone missing")
    require("levels.save_current_level()" in source, "Fresh map save missing")
    require("preserve_hidden_rejected_contact" in source, "Rejected contact preservation missing")
    require(power.count("Start-Process -FilePath $Editor") == 1, "Supervisor must contain one Unreal launch")
    require("retry_count = 0" in power, "Zero-retry evidence missing")
    require("$TimeoutSeconds = 1800" in power, "Authoring timeout changed")
    for forbidden in ("Remove-Item", "Copy-Item -Recurse", "git reset", "git checkout"):
        require(forbidden not in power, f"Forbidden supervisor operation: {forbidden}")
    require(power.count("Start-Process") == 1, "Alternate heavy-process launch detected")
    require("$process = Start-Process -FilePath $Editor" in power, "Governed UnrealEditor launch missing")

    print("PASS_STAGE07A_HERO_CORRIDOR01_OFFLINE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
