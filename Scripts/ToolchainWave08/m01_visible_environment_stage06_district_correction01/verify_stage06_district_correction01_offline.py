"""Offline verification for the Stage06 Mission 1 district correction gate."""

from __future__ import annotations

import json
import py_compile
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
HERE = ROOT / "Scripts/ToolchainWave08/m01_visible_environment_stage06_district_correction01"


def require(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def main() -> int:
    contract = json.loads((HERE / "stage06_district_correction01_contract.json").read_text(encoding="utf-8"))
    author = HERE / "author_m01_visible_environment_stage06_district_correction01.py"
    supervisor = HERE / "invoke_stage06_district_correction01_authoring_once.ps1"
    py_compile.compile(str(author), doraise=True)
    source = author.read_text(encoding="utf-8")
    power = supervisor.read_text(encoding="utf-8")
    require(contract["acceptance"]["expected_actor_count"] == 225, "Stage06 actor contract changed")
    require(source.count("OUTPUT_ASSET =") == 1, "Output asset declaration changed")
    require('runtime_promotion_performed": False' in source, "Runtime promotion safety missing")
    require("levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET)" in source, "Fresh map clone missing")
    require("levels.save_current_level()" in source, "Fresh map save missing")
    require(power.count("Start-Process -FilePath $Editor") == 1, "Supervisor must contain one Unreal launch")
    require("retry_count = 0" in power, "Zero-retry evidence missing")
    for forbidden in ("Remove-Item", "Copy-Item -Recurse", "git reset", "git checkout"):
        require(forbidden not in power, f"Forbidden supervisor operation: {forbidden}")
    print("PASS_STAGE06_DISTRICT_CORRECTION01_OFFLINE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
