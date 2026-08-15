"""Offline verification for the explicit-Rotator M01 Authoring03 recovery."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
DIR = ROOT / "Scripts/ToolchainWave08/environment_realism_stack_authoring03"
SOURCE = DIR / "author_environment_realism_stack03.py"
SUPERVISOR = DIR / "invoke_environment_realism_stack_authoring03_once.ps1"
INPUT = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack01_Recovery02.umap")
OUTPUT = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack03.umap")
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_ENVIRONMENT_REALISM_STACK_AUTHORING03/attempt_01"
TERMINAL = ROOT / "Saved/Reports/M01_ENVIRONMENT_REALISM_STACK_AUTHORING03_TERMINAL_MANIFEST.json"
EMERGENCY = ROOT / "Saved/Reports/M01_ENVIRONMENT_REALISM_STACK_AUTHORING03_EMERGENCY_RECEIPT.jsonl"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def main() -> int:
    require(SOURCE.is_file() and SUPERVISOR.is_file(), "Recovery03 sources are missing")
    require(SOURCE.stat().st_size == 3454 and digest(SOURCE) == "e42106e12648fbeac033def9c72298d3f0392be088dc8dd1d08cfda24ca8ea28", "Recovery03 source authority changed")
    require(INPUT.is_file() and INPUT.stat().st_size == 860203 and digest(INPUT) == "46a8ad9187c836329554d29716bd61ca4a2bc0f8bad7d64f66addc108e93e9d2", "Input authority changed")
    py = SOURCE.read_text(encoding="utf-8")
    ps = SUPERVISOR.read_text(encoding="utf-8-sig")
    for token in (
        "unreal.Rotator(roll=TARGET_SUN_ROTATION[2], pitch=TARGET_SUN_ROTATION[0], yaw=TARGET_SUN_ROTATION[1])",
        "Sun rotation mismatch",
        "EnvironmentRealismStack03",
        "PASSED_M01_ENVIRONMENT_REALISM_STACK_AUTHORING03_AUTOMATIC",
    ):
        require(token in py, f"Missing bounded transformation: {token}")
    require(py.count("transformed = transformed.replace(old, new, 1)") == 1, "Bounded transformation loop changed")
    require(ps.count("Start-Process") == 1, "Exactly one Unreal launch path is required")
    require("retry_count=0" in ps, "Zero-retry evidence is missing")
    require("Test-Near $State.actual_sun_rotation[0] -35.0" in ps, "Pitch postflight assertion is missing")
    require("Test-Near $State.actual_sun_rotation[1] 75.0" in ps, "Yaw postflight assertion is missing")
    require("Test-Near $State.actual_sun_rotation[2] 0.0" in ps, "Roll postflight assertion is missing")
    require("-NullRHI" in ps and "-NoSaveOnExit" in ps, "Bounded authoring switches are missing")
    for forbidden in ("AutomationTool.exe", "RunUAT.bat", "blender.exe"):
        require(forbidden not in ps, f"Forbidden execution path: {forbidden}")
    for future in (OUTPUT, ATTEMPT, TERMINAL, EMERGENCY):
        require(not future.exists(), f"Future namespace exists: {future}")
    print(json.dumps({
        "schema": "skyguard.m01-environment-realism-stack-authoring03-offline-verifier.v1",
        "classification": "PASS",
        "source": {"bytes": SOURCE.stat().st_size, "sha256": digest(SOURCE)},
        "supervisor": {"bytes": SUPERVISOR.stat().st_size, "sha256": digest(SUPERVISOR)},
        "future_namespaces_absent": True,
        "explicit_rotator_binding": True,
        "rotation_postflight": True,
        "one_launch": True,
        "zero_retry": True,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
