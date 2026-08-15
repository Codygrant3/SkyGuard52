from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
PREFIX = "M01_PHOTOREAL_FOUNDATION_WAVE01_STRUCTURAL_CLEANUP03_VISUAL_PROOF01"
HERE = ROOT / r"Scripts\ToolchainWave08\m01_photoreal_foundation_structural_cleanup03_visual_proof01"
CONTRACT = ROOT / f"Docs/AAA_Review/{PREFIX}_CONTRACT.json"
CAMERAS = ROOT / f"Docs/AAA_Review/{PREFIX}_CAMERAS.json"
VISUAL = ROOT / f"Docs/AAA_Review/{PREFIX}_VISUAL_RUBRIC.json"
PERFORMANCE = ROOT / f"Docs/AAA_Review/{PREFIX}_PERFORMANCE_RUBRIC.json"
MAP = ISOLATED / r"Content\M01\Lvl_M01_PhotorealFoundation_StructuralCleanup03.umap"
CAPTURE = HERE / "capture_m01_photoreal_foundation_structural_cleanup03_visual_proof01.py"
ADJUDICATOR = HERE / "adjudicate_m01_photoreal_foundation_structural_cleanup03_visual_proof01_once.py"
SUPERVISOR = HERE / "invoke_m01_photoreal_foundation_structural_cleanup03_visual_proof01_once.ps1"
ATTEMPT = ROOT / f"Saved/BuildAttempts/{PREFIX}/attempt_01"
LAUNCHER = ROOT / f"Saved/BuildAttempts/{PREFIX}/launcher_attempt_01"
PROFILE = ISOLATED / r"Saved\Profiling\CSV\M01PhotorealFoundationWave01StructuralCleanup03VisualProof01.csv"
TERMINAL = ROOT / f"Saved/Reports/{PREFIX}_TERMINAL_SUPERVISOR.json"
POSTFLIGHT = ROOT / f"Saved/Reports/{PREFIX}_POSTFLIGHT.json"
STANDING = ROOT / r"Production\standing_heavy_process_authorization.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


for path in (CONTRACT, CAMERAS, VISUAL, PERFORMANCE, STANDING):
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root is not an object: {path}")

contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
cameras = json.loads(CAMERAS.read_text(encoding="utf-8"))
standing = json.loads(STANDING.read_text(encoding="utf-8"))
require(contract["contract_id"] == "M01-PHOTOREAL-FOUNDATION-WAVE01-STRUCTURAL-CLEANUP03-VISUAL-PROOF01", "Contract identity changed")
require(contract["world"]["expected_total_governed_actor_count"] == 120, "Governed actor count changed")
require(contract["world"]["expected_prefix_counts"]["M01_RS01_Tree_"] == 0, "Rejected tree count is not zero")
require(sum(contract["world"]["expected_prefix_counts"].values()) + len(contract["world"]["expected_labels"]) == 120, "World-count contract does not reconcile")
require(contract["capture"] == {"count": 8, "width": 2560, "height": 1440}, "Capture contract changed")
require(len(cameras["static_cameras"]) == 5 and len(cameras["temporal_cameras"]) == 3, "Camera count changed")
require(MAP.stat().st_size == 738931 and sha256(MAP) == "142222c49c2ac232c301d14717a61c7a49c104df94ffeaa0e8ad21194184e08d", "Accepted StructuralCleanup03 map changed")
require(standing["status"] == "ACTIVE" and standing["execution_policy"]["per_run_user_authorization_required"] is False, "Standing heavy-process authorization is inactive")

assertions = contract["presentation_assertions"]
require(assertions["crossstreet_roadmark_material_count"] == 0, "Road-mark slab acceptance changed")
require(assertions["crossstreet_local_asphalt_slot2_count"] == 15, "Corrected road-top count changed")
require(assertions["district_urban_paver_material_count"] == 4, "Urban terrain count changed")
require(assertions["water_zone_extent_cm"] == 800000.0, "WaterZone extent changed")

for record in contract["locked_inputs"]:
    path = Path(record.get("absolute_path") or (ROOT / record["file"]))
    require(path.is_file(), f"Locked input missing: {path}")
    require(path.stat().st_size == int(record["bytes"]), f"Locked input byte mismatch: {path}")
    require(sha256(path) == record["sha256"], f"Locked input hash mismatch: {path}")

capture_source = load_module(CAPTURE, "structural_cleanup03_capture").transform_source()
adjudicator_source = load_module(ADJUDICATOR, "structural_cleanup03_adjudicator").transform_source()
for source in (capture_source, adjudicator_source):
    compile(source, "<transformed-proof-source>", "exec")
    require("Lvl_M01_PhotorealFoundation_StructuralCleanup03" in source, "Transformed source lacks output map")
    require("M01_PHOTOREAL_FOUNDATION_WAVE01_LIGHTING_ROADS_WATERLINE02" not in source, "Transformed source retained prior namespace")

supervisor = SUPERVISOR.read_text(encoding="utf-8")
require("$authorizationMatches.Count -ne 1" in supervisor, "Standing-authorization dispatch correction is missing")
require("Start-Process -FilePath $editor" in supervisor, "Wrapper does not validate the single Unreal launch path")
require("retry_count" not in supervisor, "Wrapper introduced a retry path")
for path in (ATTEMPT, LAUNCHER, PROFILE, TERMINAL, POSTFLIGHT):
    require(not path.exists(), f"Future visual-proof namespace exists: {path}")

print("PASS")
