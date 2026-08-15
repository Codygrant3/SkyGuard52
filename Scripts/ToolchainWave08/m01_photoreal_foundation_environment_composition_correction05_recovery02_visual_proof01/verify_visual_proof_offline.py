from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
DIR = ROOT / r"Scripts\ToolchainWave08\m01_photoreal_foundation_environment_composition_correction05_recovery02_visual_proof01"
CAPTURE = DIR / "capture_m01_photoreal_foundation_environment_composition_correction05_recovery02_visual_proof01.py"
ADJUDICATOR = DIR / "adjudicate_m01_photoreal_foundation_environment_composition_correction05_recovery02_visual_proof01_once.py"
SUPERVISOR = DIR / "invoke_m01_photoreal_foundation_environment_composition_correction05_recovery02_visual_proof01_once.ps1"
MAP = ISOLATED / r"Content\M01\Lvl_M01_PhotorealFoundation_EnvironmentCompositionCorrection05Recovery02.umap"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_VISUAL_PROOF01\attempt_01"
LAUNCHER_ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_VISUAL_PROOF01\launcher_attempt_01"
TERMINAL = ROOT / r"Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_VISUAL_PROOF01_TERMINAL_SUPERVISOR.json"
CSV = ISOLATED / r"Saved\Profiling\CSV\M01PhotorealFoundationWave01EnvironmentCompositionCorrection05Recovery02VisualProof01.csv"
PREFIX = "M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_VISUAL_PROOF01"
CONTRACT = ROOT / f"Docs/AAA_Review/{PREFIX}_CONTRACT.json"
CAMERAS = ROOT / f"Docs/AAA_Review/{PREFIX}_CAMERAS.json"
VISUAL_RUBRIC = ROOT / f"Docs/AAA_Review/{PREFIX}_VISUAL_RUBRIC.json"
PERFORMANCE_RUBRIC = ROOT / f"Docs/AAA_Review/{PREFIX}_PERFORMANCE_RUBRIC.json"
OFFLINE_FREEZE = ROOT / f"Docs/AAA_Review/{PREFIX}_OFFLINE_DESIGN_FREEZE.json"
BINDING_FREEZE = ROOT / f"Docs/AAA_Review/{PREFIX}_EXECUTION_PROMPT_BINDING_FREEZE.json"
CONTRACT_ID = "M01-PHOTOREAL-FOUNDATION-WAVE01-ENVIRONMENT-COMPOSITION-CORRECTION05-RECOVERY02-VISUAL-PROOF01"
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
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_binder(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    require(specification is not None and specification.loader is not None, f"Cannot load binder: {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def verify_record(record: dict) -> None:
    path = Path(record["absolute_path"]) if "absolute_path" in record else ROOT / record["file"]
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

    capture_runtime = load_binder(CAPTURE, "environment_composition_capture_binder").transform_source()
    adjudicator_runtime = load_binder(ADJUDICATOR, "environment_composition_adjudicator_binder").transform_source()
    ast.parse(capture_runtime, filename=str(CAPTURE) + "::runtime")
    ast.parse(adjudicator_runtime, filename=str(ADJUDICATOR) + "::runtime")

    require(MAP.is_file() and MAP.stat().st_size == 781174, "Accepted Recovery02 map byte count changed")
    require(sha256(MAP) == "d868fc50959eda83e3e4d9dc495e95ea0fd9d83e34ebdd191a6cd43a5b0c04cd", "Accepted Recovery02 map hash changed")
    for text, label in ((capture_runtime, "capture"), (adjudicator_runtime, "adjudicator")):
        require(CONTRACT_ID in text, f"{label} contract binding missing")
        require("Lvl_M01_PhotorealFoundation_EnvironmentCompositionCorrection05Recovery02" in text, f"{label} map binding missing")
        require(
            "Lvl_M01_PhotorealFoundation_GroundLightingCorrection04Recovery01" not in text,
            f"{label} retained stale map namespace",
        )
    require("MI_M01_UrbanGround_Tiled" in capture_runtime, "Capture terrain-material binding missing")
    require("Start-Process -FilePath $editor" in supervisor_text, "Bound launch-path validation missing")
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
    require(contract["world"]["expected_total_governed_actor_count"] == 140, "Governed actor count mismatch")
    require(contract["world"]["expected_prefix_counts"]["M01_ECC05_Beach_"] == 24, "Beach prefix count mismatch")
    require(contract["world"]["expected_prefix_counts"]["M01_VEK02_District_"] == 4, "District prefix count mismatch")
    require(contract["runtime"]["supervisor_timeout_seconds"] == 1200, "Contract timeout mismatch")
    require(contract["runtime"]["minimum_frame_samples"] == 900, "Contract sample floor mismatch")
    for record in contract["locked_inputs"]:
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
