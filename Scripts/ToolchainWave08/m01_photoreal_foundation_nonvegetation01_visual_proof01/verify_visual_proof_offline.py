from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
PREFIX = "M01_PHOTOREAL_FOUNDATION_WAVE01_NONVEGETATION01_VISUAL_PROOF01"
HERE = ROOT / r"Scripts\ToolchainWave08\m01_photoreal_foundation_nonvegetation01_visual_proof01"
CONTRACT = ROOT / f"Docs/AAA_Review/{PREFIX}_CONTRACT.json"
CAMERAS = ROOT / f"Docs/AAA_Review/{PREFIX}_CAMERAS.json"
VISUAL = ROOT / f"Docs/AAA_Review/{PREFIX}_VISUAL_RUBRIC.json"
PERFORMANCE = ROOT / f"Docs/AAA_Review/{PREFIX}_PERFORMANCE_RUBRIC.json"
MAP = ISOLATED / r"Content\M01\Lvl_M01_PhotorealFoundation_NonVegetation01.umap"
CAPTURE = HERE / "capture_m01_photoreal_foundation_nonvegetation01_visual_proof01.py"
ADJUDICATOR = HERE / "adjudicate_m01_photoreal_foundation_nonvegetation01_visual_proof01_once.py"
SUPERVISOR = HERE / "invoke_m01_photoreal_foundation_nonvegetation01_visual_proof01_once.ps1"
ATTEMPT = ROOT / f"Saved/BuildAttempts/{PREFIX}/attempt_01"
LAUNCHER = ROOT / f"Saved/BuildAttempts/{PREFIX}/launcher_attempt_01"
PROFILE = ISOLATED / r"Saved\Profiling\CSV\M01PhotorealFoundationWave01NonVegetation01VisualProof01.csv"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


for path in (CONTRACT, CAMERAS, VISUAL, PERFORMANCE):
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root is not an object: {path}")

contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
cameras = json.loads(CAMERAS.read_text(encoding="utf-8"))
require(contract["contract_id"] == "M01-PHOTOREAL-FOUNDATION-WAVE01-NONVEGETATION01-VISUAL-PROOF01", "Contract identity changed")
require(contract["world"]["expected_total_governed_actor_count"] == 120, "Governed actor count changed")
require(contract["world"]["expected_prefix_counts"]["M01_RS01_Tree_"] == 0, "Rejected tree count is not zero")
require(sum(contract["world"]["expected_prefix_counts"].values()) + len(contract["world"]["expected_labels"]) == 120, "World-count contract does not reconcile")
require(contract["capture"] == {"count": 8, "width": 2560, "height": 1440}, "Capture contract changed")
require(len(cameras["static_cameras"]) == 5 and len(cameras["temporal_cameras"]) == 3, "Camera count changed")
require(MAP.stat().st_size == 736476 and sha256(MAP) == "618a260a905680cf5b17c1ac82a114a69f93f947334f45701cd1a8daa2b1f2a1", "Accepted output map changed")

capture_source = load_module(CAPTURE, "nonvegetation_capture").transform_source()
adjudicator_source = load_module(ADJUDICATOR, "nonvegetation_adjudicator").transform_source()
for source in (capture_source, adjudicator_source):
    require("Lvl_M01_PhotorealFoundation_NonVegetation01" in source, "Transformed source lacks output map")
    require("M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_RECOVERY01" not in source, "Transformed source retained prior namespace")

supervisor = SUPERVISOR.read_text(encoding="utf-8")
require("$arguments['AuthorizeSingleUnrealProof'] = $true" in supervisor, "Standing authorization binding is missing")
require("retry" not in supervisor.lower() or "automatic" not in supervisor.lower(), "Unexpected retry implementation in binding wrapper")
for path in (ATTEMPT, LAUNCHER, PROFILE):
    require(not path.exists(), f"Future visual-proof namespace exists: {path}")

print("PASS")
