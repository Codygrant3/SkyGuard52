from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
DIR = ROOT / r"Scripts\ToolchainWave08\m01_photoreal_foundation_ground_lighting_correction04_recovery01_visual_proof01"
CAPTURE = DIR / "capture_m01_photoreal_foundation_ground_lighting_correction04_recovery01_visual_proof01.py"
ADJUDICATOR = DIR / "adjudicate_m01_photoreal_foundation_ground_lighting_correction04_recovery01_visual_proof01_once.py"
SUPERVISOR = DIR / "invoke_m01_photoreal_foundation_ground_lighting_correction04_recovery01_visual_proof01_once.ps1"
MAP = ISOLATED / r"Content\M01\Lvl_M01_PhotorealFoundation_GroundLightingCorrection04Recovery01.umap"
AUTHORING_TERMINAL = ROOT / r"Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_AUTHORING_TERMINAL_MANIFEST.json"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_VISUAL_PROOF01\attempt_01"
TERMINAL = ROOT / r"Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_VISUAL_PROOF01_TERMINAL_SUPERVISOR.json"
CSV = ISOLATED / r"Saved\Profiling\CSV\M01PhotorealFoundationWave01GroundLightingCorrection04Recovery01VisualProof01.csv"
CONTRACT = ROOT / r"Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_VISUAL_PROOF01_CONTRACT.json"
CAMERAS = ROOT / r"Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_VISUAL_PROOF01_CAMERAS.json"
VISUAL_RUBRIC = ROOT / r"Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_VISUAL_PROOF01_VISUAL_RUBRIC.json"
PERFORMANCE_RUBRIC = ROOT / r"Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_VISUAL_PROOF01_PERFORMANCE_RUBRIC.json"
OFFLINE_FREEZE = ROOT / r"Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_VISUAL_PROOF01_OFFLINE_DESIGN_FREEZE.json"
BINDING_FREEZE = ROOT / r"Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_VISUAL_PROOF01_EXECUTION_PROMPT_BINDING_FREEZE.json"
EXPECTED_CLASSIFICATION = "PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_VISUAL_PROOF01_EXECUTION"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


capture = CAPTURE.read_text(encoding="utf-8")
adjudicator = ADJUDICATOR.read_text(encoding="utf-8")
supervisor = SUPERVISOR.read_text(encoding="utf-8")
ast.parse(capture, filename=str(CAPTURE))
ast.parse(adjudicator, filename=str(ADJUDICATOR))

require(MAP.is_file() and MAP.stat().st_size == 743809, "Accepted Recovery01 map byte count changed")
require(sha256(MAP) == "97902b7dd39556d4409adcdd87a8c995cfef1322a8e827c52cae7a84020093cf", "Accepted Recovery01 map hash changed")
require(AUTHORING_TERMINAL.is_file(), "Recovery01 authoring terminal is missing")
require("GroundLightingCorrection04Recovery01" in capture, "Capture map binding missing")
require("MI_M01_UrbanGround_Tiled" in capture, "Capture terrain-material binding missing")
require("GroundLightingCorrection04Recovery01" in adjudicator, "Adjudicator map binding missing")
require("Start-Process -FilePath $editor" in supervisor, "Bound launch-path validation missing")
require("$timeoutSeconds = 1200" in supervisor, "Twenty-minute Unreal timeout contract missing")
require("AuthorizeSingleUnrealProof" not in supervisor, "Redundant per-run authorization returned")
require(not ATTEMPT.exists(), "Fresh proof attempt exists")
require(not TERMINAL.exists(), "Fresh proof terminal exists")
require(not CSV.exists(), "Fresh CSV profile exists")

for document in (CONTRACT, CAMERAS, VISUAL_RUBRIC, PERFORMANCE_RUBRIC, OFFLINE_FREEZE, BINDING_FREEZE):
    require(document.is_file(), f"Required proof authority is missing: {document}")
    json.loads(document.read_text(encoding="utf-8-sig"))

contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
require(contract["contract_id"] == "M01-PHOTOREAL-FOUNDATION-WAVE01-GROUND-LIGHTING-CORRECTION04-RECOVERY01-VISUAL-PROOF01", "Contract identity mismatch")
require(contract["world"]["map_sha256"] == "97902b7dd39556d4409adcdd87a8c995cfef1322a8e827c52cae7a84020093cf", "Contract map hash mismatch")
require(contract["world"]["terrain_material"].endswith("MI_M01_UrbanGround_Tiled"), "Contract terrain material mismatch")
require(contract["runtime"]["supervisor_timeout_seconds"] == 1200, "Contract timeout mismatch")
require(contract["runtime"]["minimum_frame_samples"] == 900, "Contract sample floor mismatch")

for freeze in (OFFLINE_FREEZE, BINDING_FREEZE):
    value = json.loads(freeze.read_text(encoding="utf-8-sig"))
    require(value["classification"] == EXPECTED_CLASSIFICATION, f"Freeze classification mismatch: {freeze}")
    for record in value["members"]:
        path = Path(record["absolute_path"]) if "absolute_path" in record else ROOT / record["file"]
        require(path.is_file(), f"Frozen member is missing: {path}")
        require(path.stat().st_size == int(record["bytes"]), f"Frozen member byte count changed: {path}")
        require(sha256(path) == record["sha256"], f"Frozen member hash changed: {path}")

print("PASS")
