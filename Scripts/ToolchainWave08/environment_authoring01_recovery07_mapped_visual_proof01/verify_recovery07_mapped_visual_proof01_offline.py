"""Offline verifier for Recovery07 mapped visual-proof design artifacts."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\Skyguard52")
ISOLATED_ROOT = Path(r"D:\SG52T08_ENV01")
PREFIX = "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01"
SCRIPT_ROOT = ROOT / "Scripts/ToolchainWave08/environment_authoring01_recovery07_mapped_visual_proof01"
DOC_ROOT = ROOT / "Docs/AAA_Review"
REPORT_ROOT = ROOT / "Saved/Reports"
CONTRACT_ID = "T08-M01-ENV-AUTH01-RECOVERY07-MAPPED-VISUAL-PROOF01"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"Missing JSON: {path}")
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def record_path(record: dict[str, Any]) -> Path:
    if "absolute_path" in record:
        return Path(record["absolute_path"])
    return ROOT / record["file"]


def verify_record(record: dict[str, Any]) -> None:
    path = record_path(record)
    require(path.is_file(), f"Missing frozen member: {path}")
    require(path.stat().st_size == int(record["bytes"]), f"Byte mismatch: {path}")
    require(sha256_file(path) == record["sha256"], f"Hash mismatch: {path}")


def heavy_processes() -> list[dict[str, Any]]:
    completed = subprocess.run(
        ["tasklist.exe", "/FO", "CSV", "/NH"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    require(completed.returncode == 0, "tasklist failed")
    names = {
        "unrealeditor.exe",
        "unrealeditor-cmd.exe",
        "shadercompileworker.exe",
        "blender.exe",
        "automationtool.exe",
        "unrealbuildtool.exe",
        "cl.exe",
        "link.exe",
        "msbuild.exe",
    }
    output = []
    for row in csv.reader(completed.stdout.splitlines()):
        if len(row) >= 2 and row[0].lower() in names:
            output.append({"name": row[0], "pid": row[1]})
    return output


def validate_python(path: Path) -> None:
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def verify_contract() -> dict[str, Any]:
    contract = load_json(DOC_ROOT / f"{PREFIX}_CONTRACT.json")
    require(contract["contract_id"] == CONTRACT_ID, "Contract ID")
    require(contract["classification"] == "OFFLINE_DESIGN", "Contract classification")
    runtime = contract["runtime"]
    require(runtime["warmup_seconds"] == 30, "Warmup")
    require(runtime["measurement_seconds"] == 30, "Measurement")
    require(runtime["minimum_frame_samples"] == 900, "Frame samples")
    require(runtime["stable_shader_polls"] == 2, "Stable shader polls")
    require(contract["capture"] == {"count": 8, "width": 2560, "height": 1440}, "Capture contract")
    require(contract["world"]["expected_total_actor_count"] == 59, "Actor count")
    require(contract["world"]["map_sha256"] == "401fb7a86321c05f977347185e41fd0ea0436ef7ec3d06d635935ad5f4ce702f", "Map authority")
    for record in contract["locked_inputs"]:
        verify_record(record)
    return contract


def verify_cameras() -> dict[str, Any]:
    cameras = load_json(DOC_ROOT / f"{PREFIX}_CAMERAS.json")
    static = cameras["static_cameras"]
    temporal = cameras["temporal_cameras"]
    require(len(static) == 5 and len(temporal) == 3, "Camera count")
    ids = [item["id"] for item in static + temporal]
    require(
        ids
        == [
            "C01_REAR_GUNNER_PORT",
            "C02_REAR_GUNNER_STARBOARD",
            "C03_SHORELINE_OBLIQUE",
            "C04_ROUTE_EXTERIOR",
            "C05_CITY_TO_COAST",
            "T01_ROUTE_ENTRY",
            "T02_ROUTE_MID",
            "T03_ROUTE_EXIT",
        ],
        "Camera identities/order",
    )
    require(all(item["fov_degrees"] == 90 for item in static + temporal), "FOV")
    require(cameras["resolution"] == [2560, 1440], "Camera resolution")
    return cameras


def verify_source_contracts() -> dict[str, Any]:
    executor = SCRIPT_ROOT / "capture_recovery07_mapped_visual_proof01.py"
    supervisor = SCRIPT_ROOT / "invoke_recovery07_mapped_visual_proof01_once.ps1"
    adjudicator = SCRIPT_ROOT / "adjudicate_recovery07_mapped_visual_proof01_once.py"
    test_file = SCRIPT_ROOT / "test_recovery07_mapped_visual_proof01.py"
    for path in (executor, adjudicator, test_file, Path(__file__)):
        validate_python(path)
    executor_text = executor.read_text(encoding="utf-8")
    supervisor_text = supervisor.read_text(encoding="utf-8")
    adjudicator_text = adjudicator.read_text(encoding="utf-8")
    require("register_slate_post_tick_callback" in executor_text, "Deferred tick callback")
    require("csvprofile start" in executor_text and "csvprofile stop" in executor_text, "CSV lifecycle")
    require("audit_landscape_material_compilation" in executor_text, "Shader readiness audit")
    require("save_loaded_asset" not in executor_text, "Forbidden save API")
    require("save_current_level" not in executor_text, "Forbidden level save")
    require(
        not re.search(r"(?i)pcg[^\n]{0,80}\.generate(?:_local)?\s*\(", executor_text),
        "Forbidden PCG generation call",
    )
    require(supervisor_text.count("Start-Process -FilePath $editor") == 1, "Exactly one Unreal Start-Process")
    require("-ExecCmds=py" in supervisor_text, "ExecCmds Python lifecycle")
    require("-ExecutePythonScript" not in supervisor_text, "Forbidden ExecutePythonScript")
    require("automatic_retry = $false" in supervisor_text, "Retry policy")
    require("retry_count = 0" in supervisor_text, "Retry count")
    require("PASSED_AUTOMATIC_AWAITING_HUMAN_VISUAL_REVIEW" in adjudicator_text, "Postflight classification")
    require("human_full_resolution_review_required" in adjudicator_text, "Human review requirement")
    bare_literals = re.findall(r"(?m)^\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*(?:true|false|null)\s*$", supervisor_text)
    require(not bare_literals, f"Bare PowerShell literals: {bare_literals}")
    return {
        "executor": str(executor),
        "supervisor": str(supervisor),
        "adjudicator": str(adjudicator),
        "single_unreal_start_process": True,
        "execute_python_script_absent": True,
        "world_save_api_absent": True,
    }


def verify_runtime_report() -> dict[str, Any]:
    report = load_json(DOC_ROOT / f"{PREFIX}_RUNTIME_COMPATIBILITY_REPORT.json")
    require(report["classification"] == "PASS", "Runtime compatibility report")
    require(report["selected_lifecycle"] == "FULL_EDITOR_EXECCMDS_PY_DEFERRED_TICK", "Selected lifecycle")
    require(report["rejected_lifecycle"] == "UNREALEDITOR_CMD_EXECUTE_PYTHON_SCRIPT_AUTO_QUIT", "Rejected lifecycle")
    for record in report["installed_engine_authorities"]:
        verify_record(record)
    return report


def verify_freezes() -> dict[str, Any]:
    offline = load_json(DOC_ROOT / f"{PREFIX}_OFFLINE_DESIGN_FREEZE.json")
    binding = load_json(DOC_ROOT / f"{PREFIX}_EXECUTION_PROMPT_BINDING_FREEZE.json")
    expected = "PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY07_MAPPED_VISUAL_PROOF_AUTHORIZATION"
    require(offline["classification"] == expected, "Offline freeze classification")
    require(binding["classification"] == expected, "Binding freeze classification")
    for record in offline["members"]:
        verify_record(record)
    for record in binding["members"]:
        verify_record(record)
    return {
        "offline_freeze_sha256": sha256_file(DOC_ROOT / f"{PREFIX}_OFFLINE_DESIGN_FREEZE.json"),
        "binding_freeze_sha256": sha256_file(DOC_ROOT / f"{PREFIX}_EXECUTION_PROMPT_BINDING_FREEZE.json"),
        "offline_members": len(offline["members"]),
        "binding_members": len(binding["members"]),
    }


def verify_future_namespaces_absent() -> list[str]:
    future = [
        ROOT / f"Saved/BuildAttempts/{PREFIX}/attempt_01",
        ROOT / f"Saved/BuildAttempts/{PREFIX}/launcher_attempt_01",
        REPORT_ROOT / f"{PREFIX}_EXECUTION_PREFLIGHT.json",
        REPORT_ROOT / f"{PREFIX}_TERMINAL_SUPERVISOR.json",
        REPORT_ROOT / f"{PREFIX}_EMERGENCY_RECEIPT.jsonl",
        REPORT_ROOT / f"{PREFIX}_POSTFLIGHT.json",
        ISOLATED_ROOT / "Saved/Profiling/CSV/Recovery07MappedVisualProof01.csv",
    ]
    for path in future:
        require(not path.exists(), f"Future namespace exists: {path}")
    return [str(path) for path in future]


def verify_all() -> dict[str, Any]:
    json_paths = list(DOC_ROOT.glob(f"{PREFIX}*.json")) + list(
        REPORT_ROOT.glob(f"{PREFIX}*.json")
    )
    for path in json_paths:
        load_json(path)
    heavy = heavy_processes()
    require(not heavy, f"Heavy processes active: {heavy}")
    result = {
        "schema": "skyguard.t08.m01.recovery07-mapped-proof01-offline-verification.v1",
        "classification": "PASS",
        "contract": verify_contract()["contract_id"],
        "cameras": verify_cameras()["resolution"],
        "source_contracts": verify_source_contracts(),
        "runtime": verify_runtime_report()["selected_lifecycle"],
        "freezes": verify_freezes(),
        "future_namespaces_absent": verify_future_namespaces_absent(),
        "heavy_processes": heavy,
        "unreal_launched": False,
        "blender_launched": False,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        result = verify_all()
        code = 0
    except Exception as exc:
        result = {
            "schema": "skyguard.t08.m01.recovery07-mapped-proof01-offline-verification.v1",
            "classification": "FAILED_WITH_EVIDENCE",
            "error": f"{type(exc).__name__}: {exc}",
        }
        code = 1
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
