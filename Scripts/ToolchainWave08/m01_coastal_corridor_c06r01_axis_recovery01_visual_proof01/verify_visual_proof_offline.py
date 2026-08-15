from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
DIR = ROOT / r"Scripts\ToolchainWave08\m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01"
CAPTURE = DIR / "capture_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01.py"
ADJUDICATOR = DIR / "adjudicate_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_once.py"
SUPERVISOR = DIR / "invoke_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_once.ps1"
MAP = ISOLATED / r"Content\M01\Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01.umap"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01\attempt_01"
LAUNCHER_ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01\launcher_attempt_01"
TERMINAL = ROOT / r"Saved\Reports\M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01_TERMINAL_SUPERVISOR.json"
CSV = ISOLATED / r"Saved\Profiling\CSV\M01CoastalCorridorC06R01AxisRecovery01VisualProof01.csv"
PREFIX = "M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01"
CONTRACT = ROOT / f"Docs/AAA_Review/{PREFIX}_CONTRACT.json"
CAMERAS = ROOT / f"Docs/AAA_Review/{PREFIX}_CAMERAS.json"
VISUAL_RUBRIC = ROOT / f"Docs/AAA_Review/{PREFIX}_VISUAL_RUBRIC.json"
PERFORMANCE_RUBRIC = ROOT / f"Docs/AAA_Review/{PREFIX}_PERFORMANCE_RUBRIC.json"
OFFLINE_FREEZE = ROOT / f"Docs/AAA_Review/{PREFIX}_OFFLINE_DESIGN_FREEZE.json"
BINDING_FREEZE = ROOT / f"Docs/AAA_Review/{PREFIX}_EXECUTION_PROMPT_BINDING_FREEZE.json"
AXIS_TERMINAL = ROOT / "Saved/Reports/M01_COASTAL_CORRIDOR_C06R01_UNREAL_INTEGRATION01_RECOVERY01_TERMINAL_SUPERVISOR.json"
PRIOR_CONTRACT = ROOT / "Docs/AAA_Review/M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_VISUAL_PROOF01_CONTRACT.json"
CONTRACT_ID = "M01-COASTAL-CORRIDOR-C06R01-AXIS-RECOVERY01-VISUAL-PROOF01"
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


def load_binder(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    require(specification is not None and specification.loader is not None, f"Cannot load binder: {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def verify_record(record: dict) -> None:
    if "absolute_path" in record:
        path = Path(record["absolute_path"])
    elif "file" in record:
        path = ROOT / record["file"]
    else:
        path = Path(record["path"])
    require(path.is_file(), f"Frozen member is missing: {path}")
    require(path.stat().st_size == int(record["bytes"]), f"Frozen member byte count changed: {path}")
    require(sha256(path) == record["sha256"], f"Frozen member hash changed: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pre-freeze", action="store_true")
    args = parser.parse_args()

    capture_text = CAPTURE.read_text(encoding="utf-8")
    adjudicator_text = ADJUDICATOR.read_text(encoding="utf-8")
    supervisor_text = SUPERVISOR.read_text(encoding="utf-8")
    ast.parse(capture_text, filename=str(CAPTURE))
    ast.parse(adjudicator_text, filename=str(ADJUDICATOR))
    capture_runtime = load_binder(CAPTURE, "corridor_axis_capture_binder").transform_source()
    adjudicator_runtime = load_binder(ADJUDICATOR, "corridor_axis_adjudicator_binder").transform_source()
    ast.parse(capture_runtime, filename=str(CAPTURE) + "::runtime")
    ast.parse(adjudicator_runtime, filename=str(ADJUDICATOR) + "::runtime")

    require(MAP.is_file() and MAP.stat().st_size == 707628, "Corrected corridor map byte count changed")
    require(sha256(MAP) == "a2ccdbe88a77821acb3e601cc129af932f9061f8def90af452d620895ed6a1aa", "Corrected corridor map hash changed")
    for text, label in ((capture_runtime, "capture"), (adjudicator_runtime, "adjudicator")):
        require(CONTRACT_ID in text, f"{label} contract binding missing")
        require("Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01" in text, f"{label} map binding missing")
        require("Lvl_M01_PhotorealFoundation_EnvironmentCompositionCorrection05Recovery02" not in text, f"{label} retained stale map namespace")
    for token in (
        "corridor_expected_y",
        "Expected 39 frozen imported corridor assets",
        "Corrected corridor positive-Y bounds failed",
        "M01_C06R01_Corridor_TERRAIN",
    ):
        require(token in capture_runtime, f"Capture corridor validation missing: {token}")
    require("MI_M01_UrbanGround_Tiled" in capture_runtime, "Capture terrain-material binding missing")
    require(supervisor_text.count("Start-Process -FilePath $editor") == 1, "Bound launch-path validation changed")
    require("$timeoutSeconds = 1200" in supervisor_text, "Twenty-minute Unreal timeout contract missing")
    require("AuthorizeSingleUnrealProof" not in supervisor_text, "Redundant per-run authorization returned")
    for path in (ATTEMPT, LAUNCHER_ATTEMPT, TERMINAL, CSV):
        require(not path.exists(), f"Fresh proof namespace exists: {path}")

    for document in (CONTRACT, CAMERAS, VISUAL_RUBRIC, PERFORMANCE_RUBRIC):
        require(document.is_file(), f"Required proof authority is missing: {document}")
        load_json(document)
    contract = load_json(CONTRACT)
    require(contract["contract_id"] == CONTRACT_ID, "Contract identity mismatch")
    require(contract["world"]["map_sha256"] == sha256(MAP), "Contract map hash mismatch")
    require(contract["world"]["expected_total_governed_actor_count"] == 100, "Governed actor count mismatch")
    require(contract["world"]["maximum_ungoverned_editor_actors"] == 0, "Ungoverned actor allowance changed")
    for prefix in ("M01_ECC05_Beach_", "M01_RS01_CrossStreet_", "M01_VEK02_District_"):
        require(contract["world"]["expected_prefix_counts"][prefix] == 0, f"Obsolete prefix count changed: {prefix}")
    for label in ("M01_C06R01_Corridor_TERRAIN", "M01_C06R01_Corridor_HARDSCAPE", "M01_C06R01_Corridor_DETAILS"):
        require(label in contract["world"]["expected_labels"], f"Corrected corridor actor missing: {label}")
    require(contract["runtime"]["supervisor_timeout_seconds"] == 1200, "Contract timeout mismatch")
    require(contract["runtime"]["minimum_frame_samples"] == 900, "Contract sample floor mismatch")
    for record in contract["locked_inputs"]:
        verify_record(record)

    axis_terminal = load_json(AXIS_TERMINAL)
    require(axis_terminal["classification"] == "PASSED_M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_READY_FOR_D3D12_VISUAL_PROOF", "Axis terminal classification changed")
    require(axis_terminal["imported_assets_unchanged"] is True, "Imported-asset preservation evidence changed")
    require(len(axis_terminal["imported_assets_after"]) == 39, "Imported corridor inventory count changed")
    for record in axis_terminal["imported_assets_after"]:
        verify_record(record)
    for record in load_json(PRIOR_CONTRACT)["locked_inputs"]:
        verify_record(record)

    if not args.pre_freeze:
        for freeze in (OFFLINE_FREEZE, BINDING_FREEZE):
            require(freeze.is_file(), f"Required proof freeze is missing: {freeze}")
            value = load_json(freeze)
            require(value["classification"] == EXPECTED_CLASSIFICATION, f"Freeze classification mismatch: {freeze}")
            for record in value["members"]:
                verify_record(record)
    print("PASS")


if __name__ == "__main__":
    main()
