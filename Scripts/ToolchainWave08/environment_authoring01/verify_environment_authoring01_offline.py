import ast
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
DOCS = ROOT / r"Docs\Toolchain\ToolchainWave08\EnvironmentAuthoring01"
SCRIPT = ROOT / r"Scripts\ToolchainWave08\environment_authoring01\author_m01_environment_authoring01.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\environment_authoring01\invoke_environment_authoring01_once.ps1"
TESTS = ROOT / r"Scripts\ToolchainWave08\environment_authoring01\test_environment_authoring01_offline.py"
INPUT_MAP = ISOLATED / r"Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap"
OUTPUT_MAP = ISOLATED / r"Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01.umap"
ATTEMPT = ROOT / r"Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01\attempt_01"
EXTERNAL_TERMINAL = ROOT / r"Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_TERMINAL_SUPERVISOR_MANIFEST.json"
EMERGENCY = ROOT / r"Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_EMERGENCY_RECEIPT.jsonl"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def require(value, message):
    if not value:
        raise AssertionError(message)


def verify_record(record):
    path = Path(record["path"])
    require(path.is_file(), f"missing record: {path}")
    require(path.stat().st_size == int(record["bytes"]), f"byte mismatch: {path}")
    require(digest(path) == record["sha256"], f"hash mismatch: {path}")


freeze_records = (
    (ROOT / r"Docs\AAA_Review\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE_RECOVERY02_CAPABILITY_ACCEPTANCE_FREEZE.json", 2124, "19ffa2ec415b5f12b33964f1c2893c99f2fb8dca46473e57f4b6d29b307b3d6c", "PASSED_ENVIRONMENT_CAPABILITY_EVIDENCE_ACCEPTED"),
    (ROOT / r"Docs\AAA_Review\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE_RECOVERY02_OFFLINE_DESIGN_FREEZE.json", 3927, "419ddfc5b07da8053a0e654528e2d81f138fe4d131d012b871ecea9a89f2c25e", "PASSED_RECOVERY02_ENVIRONMENT_CAPABILITY_EVIDENCE_ACCEPTED_AND_SUPERVISOR_CORRECTED"),
)
for path, size, sha, classification in freeze_records:
    require(path.is_file() and path.stat().st_size == size and digest(path) == sha, f"freeze mismatch: {path}")
    freeze = json.loads(path.read_text(encoding="utf-8-sig"))
    require(freeze["classification"] == classification, f"freeze classification mismatch: {path}")
    for member in freeze["members"]:
        verify_record(member)

require(INPUT_MAP.is_file(), "accepted input clone missing")
require(INPUT_MAP.stat().st_size == 8681, "accepted input clone byte mismatch")
require(digest(INPUT_MAP) == "5c8b7c6b0c6024767fa8a671523b5626213bd029d591270654080aed5fc7ced4", "accepted input clone hash mismatch")

required_json = (
    "accepted_input_reconciliation.json",
    "existing_asset_dependency_inventory.json",
    "environment_spatial_layout_contract.json",
    "shoreline_grounding_contract.json",
    "water_landmass_pcg_usage_contract.json",
    "deterministic_authoring_contract.json",
    "save_mutation_allowlist.json",
    "review_camera_contract.json",
    "visual_acceptance_rubric.json",
    "readiness.json",
)
for name in required_json:
    path = DOCS / name
    require(path.is_file(), f"required JSON missing: {path}")
    json.loads(path.read_text(encoding="utf-8-sig"))

inventory = json.loads((DOCS / "existing_asset_dependency_inventory.json").read_text(encoding="utf-8-sig"))
require(len(inventory["accepted_records"]) == inventory["accepted_record_count"] == 25, "asset record count mismatch")
for record in inventory["accepted_records"]:
    verify_record(record)
require(inventory["downloads"] == 0 and inventory["generated_substitutes"] == 0, "external/generated dependency introduced")

source = SCRIPT.read_text(encoding="utf-8")
ast.parse(source, filename=str(SCRIPT))
require(source.count("EditorAssetLibrary.duplicate_asset(INPUT_ASSET, OUTPUT_ASSET)") == 1, "duplication call count is not one")
require("shutil.copy" not in source and "copyfile(" not in source, "filesystem duplication exists")
require("PCG_SEED = 520801" in source, "fixed PCG seed missing")
require("DISABLED_FIXED_DIRECT_PLACEMENT_ONLY" in source, "PCG generation is not fail-closed")
require("DEFERRED_NO_EFFECTFUL_BRUSH_API_AUTHORITY" in source, "Landmass deferral evidence missing")
require("len([label for label in labels if label.startswith(\"M01_A01_Tree_\")]) == 15" in source, "bounded vegetation assertion missing")
require("align_actor_bottom" in source and "Grounding tolerance exceeded" in source, "measured grounding validation missing")
require("shore_contact_checks" in source and "Water/shore vertical relationship failed" in source, "shore-contact validation missing")
require("EditorAssetLibrary.save_asset(OUTPUT_ASSET" in source, "exact output save missing")
require("save_asset(INPUT_ASSET" not in source, "input save path exists")

supervisor = SUPERVISOR.read_text(encoding="utf-8")
require("__AUTHORING_SCRIPT_SHA256__" not in supervisor and "__ASSET_MANIFEST_SHA256__" not in supervisor, "supervisor placeholder remains")
require(supervisor.count("$run=Invoke-CapturedProcess -FilePath $Editor") == 1, "future Unreal launch count is not one")
require("retry_count=0" in supervisor, "zero-retry evidence missing")
require(not re.search(r"(?i)(for|while)\s*\([^\n]*retry", supervisor), "retry loop exists")
require("ReadToEndAsync" in supervisor and "WaitForExit(1000)" in supervisor, "asynchronous process draining missing")
require("Authoring01 output already exists" in supervisor, "output-absence preflight missing")
require("Authoring01 output map is missing" in supervisor, "output-existence postflight missing")
require("Output map hash differs from receipt" in supervisor, "receipt/hash parity missing")
require("Write-JsonAtomic $ExternalTerminal" in supervisor and "$EmergencyReceipt" in supervisor, "terminal lifecycle incomplete")
require("-NullRHI" in supervisor and "-run=pythonscript" in supervisor, "governed Unreal arguments missing")

allowlist = json.loads((DOCS / "save_mutation_allowlist.json").read_text(encoding="utf-8-sig"))
require(allowlist["save_allowlist"] == ["/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentAuthoring01"], "save allowlist is not exact")
require(all("Prototype01" not in path for path in allowlist["save_allowlist"]), "input clone entered save allowlist")
require(all("/Game/Skyguard/Maps" not in path for path in allowlist["save_allowlist"]), "canonical map entered save allowlist")

for path in (SCRIPT, SUPERVISOR, TESTS):
    require(path.is_file() and path.stat().st_size > 0, f"source missing or empty: {path}")

require(not OUTPUT_MAP.exists(), "future Authoring01 output exists during offline gate")
require(not ATTEMPT.exists(), "future Authoring01 attempt exists during offline gate")
require(not EXTERNAL_TERMINAL.exists(), "future Authoring01 terminal exists during offline gate")
require(not EMERGENCY.exists(), "future Authoring01 emergency receipt exists during offline gate")
print("PASS")
