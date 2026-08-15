"""Offline verifier for the bounded Stage 7A Correction01 authoring gate."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
HERE = ROOT / "Scripts/ToolchainWave08/m01_visible_environment_stage07a_hero_corridor01_correction01"
CONTRACT = HERE / "stage07a_hero_corridor01_correction01_contract.json"
AUTHOR = HERE / "author_m01_visible_environment_stage07a_hero_corridor01_correction01.py"
SUPERVISOR = HERE / "invoke_stage07a_hero_corridor01_correction01_authoring_once.ps1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    ast.parse(AUTHOR.read_text(encoding="utf-8"), str(AUTHOR))
    supervisor = SUPERVISOR.read_text(encoding="utf-8")
    author = AUTHOR.read_text(encoding="utf-8")
    assert supervisor.count("Start-Process -FilePath $Editor") == 1
    assert "retry" in supervisor.lower() and "retry_count = 0" in supervisor
    assert "Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01Correction01" in author
    assert "M01_HSSC02_CoastalA_TERRAIN" in contract["correction"]["terrain_actor"]
    for spec in [contract["input"], *contract["authorities"]]:
        path = Path(spec.get("path", spec.get("file")))
        assert path.is_file() and path.stat().st_size == int(spec["bytes"]) and sha256(path) == spec["sha256"]
    assert not Path(contract["output"]["file"]).exists()
    assert not Path(contract["output"]["attempt"]).exists()
    print("PASS_STAGE07A_HERO_CORRIDOR01_CORRECTION01_OFFLINE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
