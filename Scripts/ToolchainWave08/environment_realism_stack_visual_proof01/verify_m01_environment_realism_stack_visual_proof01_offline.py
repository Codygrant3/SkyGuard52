"""Offline validation for the realism-stack mapped proof sources and contract."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
PREFIX = "M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF01"
SCRIPT_ROOT = ROOT / "Scripts/ToolchainWave08/environment_realism_stack_visual_proof01"
CONTRACT = ROOT / f"Docs/AAA_Review/{PREFIX}_CONTRACT.json"
CAMERAS = ROOT / f"Docs/AAA_Review/{PREFIX}_CAMERAS.json"
VISUAL = ROOT / f"Docs/AAA_Review/{PREFIX}_VISUAL_RUBRIC.json"
PERFORMANCE = ROOT / f"Docs/AAA_Review/{PREFIX}_PERFORMANCE_RUBRIC.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"JSON root must be an object: {path}")
    return value


def main() -> int:
    capture_path = SCRIPT_ROOT / "capture_m01_environment_realism_stack_visual_proof01.py"
    adjudicator_path = SCRIPT_ROOT / "adjudicate_m01_environment_realism_stack_visual_proof01_once.py"
    for path in (capture_path, adjudicator_path, CONTRACT, CAMERAS, VISUAL, PERFORMANCE):
        require(path.is_file(), f"Missing offline authority: {path}")
    capture = load_module("m01_rs_capture_wrapper", capture_path)
    adjudicator = load_module("m01_rs_adjudicator_wrapper", adjudicator_path)
    capture_text = capture.transform_source()
    adjudicator_text = adjudicator.transform_source()
    ast.parse(capture_text)
    ast.parse(adjudicator_text)
    require("M01_ENVIRONMENT_REALISM_STACK_" in capture_text and "VISUAL_PROOF01" in capture_text, "Capture prefix")
    require("M01_RS01_" in capture_text, "Realism actor governance")
    require("Lvl_M01_T08_EnvironmentRealismStack01_Recovery02" in capture_text, "Capture map")
    require("M01EnvironmentRealismStackVisualProof01.csv" in adjudicator_text, "Profile binding")

    contract = load_json(CONTRACT)
    cameras = load_json(CAMERAS)
    visual = load_json(VISUAL)
    performance = load_json(PERFORMANCE)
    require(contract["contract_id"] == "M01-ENVIRONMENT-REALISM-STACK-VISUAL-PROOF01", "Contract ID")
    require(contract["world"]["expected_total_governed_actor_count"] == 186, "Governed count")
    require(contract["world"]["map_sha256"] == "46a8ad9187c836329554d29716bd61ca4a2bc0f8bad7d64f66addc108e93e9d2", "Map hash")
    require(len(cameras["static_cameras"]) == 5 and len(cameras["temporal_cameras"]) == 3, "Camera count")
    require(cameras["resolution"] == [2560, 1440], "Camera resolution")
    require(performance["measurement"]["minimum_samples"] == 900, "Performance sample count")
    require("visible placeholder repetition" in visual["human_rejects"], "Repetition reject")
    for record in contract["locked_inputs"]:
        path = Path(record["absolute_path"]) if "absolute_path" in record else ROOT / record["file"]
        require(path.is_file(), f"Missing locked input: {path}")
        require(path.stat().st_size == int(record["bytes"]), f"Byte mismatch: {path}")
        require(sha256(path) == record["sha256"], f"Hash mismatch: {path}")
    future = [
        ROOT / f"Saved/BuildAttempts/{PREFIX}/attempt_01",
        ROOT / f"Saved/BuildAttempts/{PREFIX}/launcher_attempt_01",
        ROOT / f"Saved/Reports/{PREFIX}_EXECUTION_PREFLIGHT.json",
        ROOT / f"Saved/Reports/{PREFIX}_TERMINAL_SUPERVISOR.json",
        ROOT / f"Saved/Reports/{PREFIX}_POSTFLIGHT.json",
        Path(r"D:\SG52T08_ENV01\Saved\Profiling\CSV\M01EnvironmentRealismStackVisualProof01.csv"),
    ]
    require(not any(path.exists() for path in future), "A future proof namespace already exists")
    print(json.dumps({"classification": "PASS", "locked_inputs": len(contract["locked_inputs"]), "cameras": 8}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
