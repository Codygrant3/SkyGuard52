"""Offline validation for corrected RealismStack03 Visual Proof02."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
PREFIX = "M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF02"
DIR = ROOT / "Scripts/ToolchainWave08/environment_realism_stack_visual_proof02"
CONTRACT = ROOT / f"Docs/AAA_Review/{PREFIX}_CONTRACT.json"
CAMERAS = ROOT / f"Docs/AAA_Review/{PREFIX}_CAMERAS.json"
VISUAL = ROOT / f"Docs/AAA_Review/{PREFIX}_VISUAL_RUBRIC.json"
PERFORMANCE = ROOT / f"Docs/AAA_Review/{PREFIX}_PERFORMANCE_RUBRIC.json"
SUPERVISOR = DIR / "invoke_m01_environment_realism_stack_visual_proof02_once.ps1"


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"JSON root must be an object: {path}")
    return value


def main() -> int:
    capture_path = DIR / "capture_m01_environment_realism_stack_visual_proof02.py"
    adjudicator_path = DIR / "adjudicate_m01_environment_realism_stack_visual_proof02_once.py"
    for path in (capture_path, adjudicator_path, SUPERVISOR, CONTRACT, CAMERAS, VISUAL, PERFORMANCE):
        require(path.is_file(), f"Missing authority: {path}")
    capture_text = load_module("m01_rs_vp02_capture", capture_path).transform_source()
    adjudicator_text = load_module("m01_rs_vp02_adjudicator", adjudicator_path).transform_source()
    ast.parse(capture_text)
    ast.parse(adjudicator_text)
    for text, label in ((capture_text, "capture"), (adjudicator_text, "adjudicator")):
        require("M01-ENVIRONMENT-REALISM-STACK-VISUAL-PROOF02" in text, f"{label} contract ID")
        require("Lvl_M01_T08_EnvironmentRealismStack03" in text, f"{label} map")
        require("M01EnvironmentRealismStackVisualProof02.csv" in text, f"{label} profile")
        require("VISUAL_PROOF01" not in text and "Stack01_Recovery02" not in text, f"{label} stale binding")
    require("M01_RS01_" in capture_text, "Realism actor governance is missing")

    contract = load_json(CONTRACT)
    cameras = load_json(CAMERAS)
    visual = load_json(VISUAL)
    performance = load_json(PERFORMANCE)
    require(contract["contract_id"] == "M01-ENVIRONMENT-REALISM-STACK-VISUAL-PROOF02", "Contract ID")
    require(contract["world"]["map_sha256"] == "c68de75000c25569f38b9307fd8760cce85236e2f3166785350ea0c641de81e8", "Map hash")
    require(contract["world"]["expected_total_governed_actor_count"] == 186, "Actor count")
    require(len(cameras["static_cameras"]) == 5 and len(cameras["temporal_cameras"]) == 3, "Camera count")
    require(cameras["resolution"] == [2560, 1440], "Resolution")
    require(performance["measurement"]["minimum_samples"] == 900, "Sample count")
    require("visible placeholder repetition" in visual["human_rejects"], "Visual rubric was relaxed")
    for record in contract["locked_inputs"]:
        path = Path(record["absolute_path"]) if "absolute_path" in record else ROOT / record["file"]
        require(path.is_file(), f"Missing locked input: {path}")
        require(path.stat().st_size == int(record["bytes"]), f"Byte mismatch: {path}")
        require(sha256(path) == record["sha256"], f"Hash mismatch: {path}")

    ps = SUPERVISOR.read_text(encoding="utf-8-sig")
    require(ps.count("Start-Process -FilePath $editor") == 1, "Wrapper's transformed-source launch assertion changed")
    require(".atomic-backup" in ps, "Explicit atomic backup is missing")
    require("Known null-backup atomic writer target is missing" in ps, "Bounded atomic-writer correction guard is missing")
    require("Visual Proof01 supervisor wrapper changed" in ps, "Frozen parent binding is missing")
    future = (
        ROOT / f"Saved/BuildAttempts/{PREFIX}/attempt_01",
        ROOT / f"Saved/BuildAttempts/{PREFIX}/launcher_attempt_01",
        ROOT / f"Saved/Reports/{PREFIX}_EXECUTION_PREFLIGHT.json",
        ROOT / f"Saved/Reports/{PREFIX}_TERMINAL_SUPERVISOR.json",
        ROOT / f"Saved/Reports/{PREFIX}_POSTFLIGHT.json",
        Path(r"D:\SG52T08_ENV01\Saved\Profiling\CSV\M01EnvironmentRealismStackVisualProof02.csv"),
    )
    require(not any(path.exists() for path in future), "A future proof namespace exists")
    print(json.dumps({
        "schema": "skyguard.m01-environment-realism-stack.visual-proof02-offline-verifier.v1",
        "classification": "PASS",
        "locked_inputs": len(contract["locked_inputs"]),
        "cameras": 8,
        "atomic_writer_corrected": True,
        "future_namespaces_absent": True,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
