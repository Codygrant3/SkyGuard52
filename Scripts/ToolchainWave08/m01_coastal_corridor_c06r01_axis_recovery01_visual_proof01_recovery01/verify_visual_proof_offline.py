from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
PREFIX = "M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01_RECOVERY01"
CONTRACT_ID = "M01-COASTAL-CORRIDOR-C06R01-AXIS-RECOVERY01-VISUAL-PROOF01-RECOVERY01"
DIR = ROOT / r"Scripts\ToolchainWave08\m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01"
CAPTURE = DIR / "capture_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01.py"
ADJUDICATOR = DIR / "adjudicate_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01_once.py"
SUPERVISOR = DIR / "invoke_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01_once.ps1"
CONTRACT = ROOT / f"Docs/AAA_Review/{PREFIX}_CONTRACT.json"
CAMERAS = ROOT / f"Docs/AAA_Review/{PREFIX}_CAMERAS.json"
VISUAL_RUBRIC = ROOT / f"Docs/AAA_Review/{PREFIX}_VISUAL_RUBRIC.json"
PERFORMANCE_RUBRIC = ROOT / f"Docs/AAA_Review/{PREFIX}_PERFORMANCE_RUBRIC.json"
OFFLINE_FREEZE = ROOT / f"Docs/AAA_Review/{PREFIX}_OFFLINE_DESIGN_FREEZE.json"
BINDING_FREEZE = ROOT / f"Docs/AAA_Review/{PREFIX}_EXECUTION_PROMPT_BINDING_FREEZE.json"
FAILED_FREEZE = ROOT / "Docs/AAA_Review/M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01_ATTEMPT01_TERMINAL_FREEZE.json"
MAP = ISOLATED / r"Content\M01\Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01.umap"
ATTEMPT = ROOT / f"Saved/BuildAttempts/{PREFIX}/attempt_01"
LAUNCHER = ROOT / f"Saved/BuildAttempts/{PREFIX}/launcher_attempt_01"
TERMINAL = ROOT / f"Saved/Reports/{PREFIX}_TERMINAL_SUPERVISOR.json"
CSV = ISOLATED / "Saved/Profiling/CSV/M01CoastalCorridorC06R01AxisRecovery01VisualProof01Recovery01.csv"
EXPECTED_CLASSIFICATION = f"PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_{PREFIX}_EXECUTION"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def record_path(record: dict) -> Path:
    if "absolute_path" in record:
        return Path(record["absolute_path"])
    if "file" in record:
        return ROOT / record["file"]
    return Path(record["path"])


def verify_record(record: dict) -> None:
    path = record_path(record)
    require(path.is_file(), f"Frozen member is missing: {path}")
    require(path.stat().st_size == int(record["bytes"]), f"Frozen member byte count changed: {path}")
    require(sha256(path) == record["sha256"], f"Frozen member hash changed: {path}")


def load_binder(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    require(specification is not None and specification.loader is not None, f"Cannot load binder: {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pre-freeze", action="store_true")
    args = parser.parse_args()

    for path in (CAPTURE, ADJUDICATOR, SUPERVISOR, CONTRACT, CAMERAS, VISUAL_RUBRIC, PERFORMANCE_RUBRIC):
        require(path.is_file(), f"Recovery01 authority is missing: {path}")
    for path in (CAPTURE, ADJUDICATOR):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    capture_runtime = load_binder(CAPTURE, "corridor_recovery01_capture").transform_source()
    adjudicator_runtime = load_binder(ADJUDICATOR, "corridor_recovery01_adjudicator").transform_source()
    ast.parse(capture_runtime, filename=str(CAPTURE) + "::runtime")
    ast.parse(adjudicator_runtime, filename=str(ADJUDICATOR) + "::runtime")
    for text, label in ((capture_runtime, "capture"), (adjudicator_runtime, "adjudicator")):
        require(CONTRACT_ID in text, f"{label} contract binding missing")
        require("VISUAL_PROOF01_RECOVERY01" in text, f"{label} Recovery01 namespace missing")
    for token in (
        'transient_pcg = corridor_by_label.get("PCGWorldActor0", [])',
        'transient_class != "/Script/PCG.PCGWorldActor"',
        'transient_transform["location_cm"] != [0.0, 0.0, 0.0]',
        'transient_transform["scale"] != [1.0, 1.0, 1.0]',
        "Corrected corridor positive-Y bounds failed",
        "Expected 39 frozen imported corridor assets",
    ):
        require(token in capture_runtime, f"Capture validation is missing: {token}")

    supervisor_text = SUPERVISOR.read_text(encoding="utf-8")
    require(supervisor_text.count("Start-Process -FilePath $editor") == 1, "Bound launch-path validation changed")
    require(supervisor_text.count("[ScriptBlock]::Create($transformed)") == 1, "Supervisor transform path changed")
    require("$timeoutSeconds = 1200" in supervisor_text, "Supervisor timeout binding check missing")
    require("AuthorizeSingleUnrealProof" not in supervisor_text, "Per-run authorization flag returned")

    contract = load_json(CONTRACT)
    require(contract["contract_id"] == CONTRACT_ID, "Contract identity mismatch")
    require(MAP.is_file() and MAP.stat().st_size == 707628, "Corrected map byte count changed")
    require(sha256(MAP) == "a2ccdbe88a77821acb3e601cc129af932f9061f8def90af452d620895ed6a1aa", "Corrected map hash changed")
    world = contract["world"]
    require(world["map_sha256"] == sha256(MAP), "Contract map hash mismatch")
    require(world["expected_total_governed_actor_count"] == 100, "Governed actor count mismatch")
    require(world["raw_full_editor_actor_count"] == 101, "Runtime actor count mismatch")
    require(world["maximum_ungoverned_editor_actors"] == 1, "Transient allowance mismatch")
    transient = world["allowed_transient_editor_actor"]
    require(transient == {
        "count": 1,
        "label": "PCGWorldActor0",
        "class": "/Script/PCG.PCGWorldActor",
        "location_cm": [0.0, 0.0, 0.0],
        "scale": [1.0, 1.0, 1.0],
    }, "Transient PCG contract changed")
    require(contract["runtime"]["supervisor_timeout_seconds"] == 1200, "Supervisor timeout mismatch")
    require(contract["runtime"]["minimum_frame_samples"] == 900, "Frame sample floor mismatch")
    for record in contract["locked_inputs"]:
        verify_record(record)

    failed = load_json(FAILED_FREEZE)
    require(failed["classification"] == "FAILED_WITH_EVIDENCE", "Prior failed proof classification changed")
    require(FAILED_FREEZE.stat().st_size == 4223, "Prior failed proof freeze byte count changed")
    require(sha256(FAILED_FREEZE) == "f74bd3e97fd59b5f3b427434af94f254a5b3daa4bfb3a9e37d53464863b5f766", "Prior failed proof freeze hash changed")

    for path in (ATTEMPT, LAUNCHER, TERMINAL, CSV):
        require(not path.exists(), f"Fresh Recovery01 namespace already exists: {path}")
    if not args.pre_freeze:
        for freeze in (OFFLINE_FREEZE, BINDING_FREEZE):
            require(freeze.is_file(), f"Required Recovery01 freeze is missing: {freeze}")
            value = load_json(freeze)
            require(value["classification"] == EXPECTED_CLASSIFICATION, f"Freeze classification mismatch: {freeze}")
            for record in value["members"]:
                verify_record(record)
    print("PASS")


if __name__ == "__main__":
    main()
