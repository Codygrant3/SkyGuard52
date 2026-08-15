"""Offline verifier for the bounded corridor Y-axis Recovery01 map correction."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SCRIPT_DIR = ROOT / "Scripts/ToolchainWave08/m01_coastal_corridor_c06r01_unreal_integration01_recovery01"
AUTHOR = SCRIPT_DIR / "author_corridor_axis_recovery01.py"
SUPERVISOR = SCRIPT_DIR / "invoke_corridor_axis_recovery01_once.ps1"
CONTRACT = ROOT / "Docs/Toolchain/ToolchainWave08/M01CoastalCorridorC06R01UnrealIntegration01Recovery01/execution_contract.json"
INPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01.umap")
OUTPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01.umap")
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_COASTAL_CORRIDOR_C06R01_UNREAL_INTEGRATION01_RECOVERY01/attempt_01"
TERMINAL = ROOT / "Saved/Reports/M01_COASTAL_CORRIDOR_C06R01_UNREAL_INTEGRATION01_RECOVERY01_TERMINAL_SUPERVISOR.json"
EXPECTED_INPUT_SHA256 = "1e8164704968153e59c69f463ce1b76d03c9deafb32c8d6b239574b1406ae5db"
EXPECTED_INPUT_BYTES = 705_359


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (AUTHOR, SUPERVISOR, CONTRACT, INPUT_MAP):
        require(path.is_file(), f"Missing required file: {path}")
    require(INPUT_MAP.stat().st_size == EXPECTED_INPUT_BYTES, "Input map byte count changed")
    require(sha256(INPUT_MAP) == EXPECTED_INPUT_SHA256, "Input map hash changed")
    require(not OUTPUT_MAP.exists(), "Fresh output map already exists")
    require(not ATTEMPT.exists(), "Fresh attempt namespace already exists")
    require(not TERMINAL.exists(), "Fresh terminal namespace already exists")

    author_text = AUTHOR.read_text(encoding="utf-8")
    ast.parse(author_text)
    required_author_tokens = (
        "new_level_from_template(OUTPUT_ASSET, INPUT_ASSET)",
        "set_actor_scale3d(unreal.Vector(1.0, -1.0, 1.0))",
        "EXPECTED_ACTOR_COUNT = 100",
        "unchanged_non_corridor_actor_count",
        "levels.save_current_level()",
        "PASSED_M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_READY_FOR_D3D12_VISUAL_PROOF",
    )
    for token in required_author_tokens:
        require(token in author_text, f"Authoring contract token missing: {token}")
    forbidden_author_tokens = ("import_asset_tasks", "destroy_actor(", "spawn_actor_from_class(")
    for token in forbidden_author_tokens:
        require(token not in author_text, f"Out-of-scope authoring behavior found: {token}")

    supervisor_text = SUPERVISOR.read_text(encoding="utf-8")
    require(supervisor_text.count("Start-Process -FilePath $Editor") == 1, "Supervisor must contain exactly one Unreal launch")
    require("-nullrhi" in supervisor_text.lower(), "NullRHI contract is missing")
    require("standing_heavy_process_authorization.json" in supervisor_text, "Standing authorization authority is missing")
    require("retry_count=0" in supervisor_text, "Zero-retry evidence is missing")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(contract["classification_on_success"] == "PASSED_M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_READY_FOR_D3D12_VISUAL_PROOF", "Contract classification changed")
    require(contract["correction"]["actor_scale"] == [1.0, -1.0, 1.0], "Contract Y-axis correction changed")
    require(contract["correction"]["governed_actor_count"] == 3, "Governed actor count changed")
    print("PASS_M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_OFFLINE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
