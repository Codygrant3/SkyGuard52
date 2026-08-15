"""Offline contract verifier for the M01 Realism Stack Authoring02 correction."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
DIR = ROOT / "Scripts/ToolchainWave08/environment_realism_stack_authoring02"
AUTHORING = DIR / "author_environment_realism_stack02.py"
SUPERVISOR = DIR / "invoke_environment_realism_stack_authoring02_once.ps1"
INPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack01_Recovery02.umap")
OUTPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack02.umap")
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_ENVIRONMENT_REALISM_STACK_AUTHORING02/attempt_01"
TERMINAL = ROOT / "Saved/Reports/M01_ENVIRONMENT_REALISM_STACK_AUTHORING02_TERMINAL_MANIFEST.json"
EMERGENCY = ROOT / "Saved/Reports/M01_ENVIRONMENT_REALISM_STACK_AUTHORING02_EMERGENCY_RECEIPT.jsonl"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    require(AUTHORING.is_file(), f"Missing {AUTHORING}")
    require(SUPERVISOR.is_file(), f"Missing {SUPERVISOR}")
    require(INPUT_MAP.is_file(), f"Missing {INPUT_MAP}")
    require(INPUT_MAP.stat().st_size == 860203, "Input map byte authority changed")
    require(sha256(INPUT_MAP) == "46a8ad9187c836329554d29716bd61ca4a2bc0f8bad7d64f66addc108e93e9d2", "Input map hash authority changed")
    require(AUTHORING.stat().st_size == 11473, "Authoring source byte authority changed")
    require(sha256(AUTHORING) == "116adb907c97d125ed349f2aa2d5b703ec6df6418df77a5b81bbe8622c9016fb", "Authoring source hash authority changed")

    py = AUTHORING.read_text(encoding="utf-8")
    ps = SUPERVISOR.read_text(encoding="utf-8-sig")
    required_python = (
        'OUTPUT_ASSET = "/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentRealismStack02"',
        "TARGET_LANDSCAPE_SCALE = (100.0, 150.0, 100.0)",
        "TARGET_SUN_ROTATION = (-35.0, 75.0, 0.0)",
        "TARGET_SUN_INTENSITY = 10.0",
        "TARGET_SKYLIGHT_INTENSITY = 2.0",
        'require(len(actors) == 186',
        'require(len(result["regrounding_records"]) == 165',
        'require(len(result["waterline_records"]) == 10',
        'unreal.SystemLibrary.quit_editor()',
    )
    for token in required_python:
        require(token in py, f"Missing Python contract token: {token}")
    require("def rotator(value):" in py and "value.pitch" in py and "value.yaw" in py and "value.roll" in py, "Rotator compatibility helper is missing")
    require("save_current_level" in py, "Output map save is missing")
    require("save_asset(INPUT_ASSET" not in py, "Input map save is prohibited")

    require(ps.count("Start-Process") == 1, "Supervisor must contain exactly one Start-Process")
    for forbidden in ("AutomationTool.exe", "RunUAT.bat", "blender.exe"):
        require(forbidden not in ps, f"Forbidden execution path found: {forbidden}")
    require("retry_count = 0" in ps, "Zero-retry evidence is missing")
    require("standing_heavy_process_authorization.json" in ps, "Standing authorization check is missing")
    require("M01_ENVIRONMENT_REALISM_STACK_AUTHORING02" in ps, "Fresh namespace binding is missing")
    require("Lvl_M01_T08_EnvironmentRealismStack02.umap" in ps, "Fresh output map binding is missing")
    require("-NullRHI" in ps and "-NoSaveOnExit" in ps, "Bounded authoring switches are missing")
    require("$TimeoutSeconds = 600" in ps, "Expected timeout is missing")
    require("PASSED_M01_ENVIRONMENT_REALISM_STACK_AUTHORING02_AUTOMATIC" in ps, "Terminal classification is missing")
    require(not re.search(r"\b(rm|del|erase)\b", ps, re.IGNORECASE), "Destructive command detected")

    for path in (OUTPUT_MAP, ATTEMPT, TERMINAL, EMERGENCY):
        require(not path.exists(), f"Future governed namespace already exists: {path}")

    result = {
        "schema": "skyguard.m01-environment-realism-stack-authoring02-offline-verifier.v1",
        "classification": "PASS",
        "authoring": {"bytes": AUTHORING.stat().st_size, "sha256": sha256(AUTHORING)},
        "supervisor": {"bytes": SUPERVISOR.stat().st_size, "sha256": sha256(SUPERVISOR)},
        "input_map": {"bytes": INPUT_MAP.stat().st_size, "sha256": sha256(INPUT_MAP)},
        "future_namespaces_absent": True,
        "one_launch": True,
        "zero_retry": True,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
