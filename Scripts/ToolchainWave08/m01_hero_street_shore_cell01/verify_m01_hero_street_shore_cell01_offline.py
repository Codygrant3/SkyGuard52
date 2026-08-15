"""Offline verifier for the frozen Hero Street/Shore Cell01 authoring gate."""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT = ROOT / "Docs/AAA_Review/M01_HERO_STREET_SHORE_CELL01_AUTHORING_CONTRACT.json"
AUTHOR = ROOT / "Scripts/ToolchainWave08/m01_hero_street_shore_cell01/author_m01_hero_street_shore_cell01.py"
SUPERVISOR = ROOT / "Scripts/ToolchainWave08/m01_hero_street_shore_cell01/invoke_m01_hero_street_shore_cell01_once.py"
OUTPUT = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_HeroStreetShoreCell01.umap")
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_HERO_STREET_SHORE_CELL01/attempt_01"
TERMINAL = ROOT / "Saved/Reports/M01_HERO_STREET_SHORE_CELL01_TERMINAL_SUPERVISOR.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(contract["classification"] == "PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_HERO_STREET_SHORE_CELL01_AUTHORING", "Contract classification changed")
    for row in contract["authorities"]:
        path = Path(row["path"])
        require(path.is_file(), f"Authority missing: {path}")
        require(path.stat().st_size == row["bytes"], f"Authority bytes changed: {path}")
        require(sha256(path) == row["sha256"], f"Authority hash changed: {path}")

    for path in (AUTHOR, SUPERVISOR):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    author_source = AUTHOR.read_text(encoding="utf-8")
    supervisor_source = SUPERVISOR.read_text(encoding="utf-8")

    required_author_tokens = (
        "WINDOW_COLUMNS_CM = (10_600.0, 11_020.0, 11_440.0)",
        "EXPECTED_ACTORS_AFTER = 120",
        "len(result[\"window_modules\"]) == 12",
        "len(result[\"prop_copies\"]) == 11",
        "runtime_promotion\": False",
        "levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET)",
    )
    for token in required_author_tokens:
        require(token in author_source, f"Required author token absent: {token}")
    for token in ("import_asset_tasks", "AssetImportTask", "WaterWavesAsset", "set_water_waves"):
        require(token not in author_source, f"Forbidden author token present: {token}")

    require(supervisor_source.count("exec(compile(") == 1, "Supervisor binding execution count changed")
    require("TIMEOUT_SECONDS = 1_800" in (ROOT / "Scripts/ToolchainWave08/m01_accepted_candidate_assembly03/invoke_m01_accepted_candidate_assembly03_once.py").read_text(encoding="utf-8"), "Proven lifecycle timeout changed")
    require("M01_HERO_STREET_SHORE_CELL01/attempt_01" in supervisor_source, "Fresh attempt namespace absent")
    require("Lvl_M01_HeroStreetShoreCell01.umap" in supervisor_source, "Fresh map namespace absent")
    require('ATTEMPT = ROOT / "Saved/BuildAttempts/M01_HERO_STREET_SHORE_CELL01/attempt_01"' in supervisor_source, "Fresh executable attempt binding absent")

    require(not OUTPUT.exists(), "Fresh output map exists")
    require(not ATTEMPT.exists(), "Fresh attempt exists")
    require(not TERMINAL.exists(), "Fresh terminal exists")

    for program, marker in (
        (AUTHOR, "PASS_M01_HERO_STREET_SHORE_CELL01_AUTHORING_CONTRACT"),
        (SUPERVISOR, "PASS_M01_HERO_STREET_SHORE_CELL01_SUPERVISOR_OFFLINE_CONTRACT"),
    ):
        result = subprocess.run(
            [sys.executable, str(program), "--offline-contract-test"],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )
        require(result.returncode == 0, f"Offline contract failed: {program}: {result.stdout} {result.stderr}")
        require(marker in result.stdout, f"Offline marker absent: {marker}")

    print("PASS_M01_HERO_STREET_SHORE_CELL01_OFFLINE_VERIFIER")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
