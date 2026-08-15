import ast
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(r"D:\\Skyguard52")
SOURCE = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery04_authoring\author_m01_environment_authoring01_recovery04.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery04_authoring\invoke_environment_authoring01_recovery04_once.ps1"
TESTS = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery04_authoring\test_environment_authoring01_recovery04_offline.py"
INPUT_MAP = Path(r"D:\\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap")
OUTPUT_MAP = Path(r"D:\\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery04.umap")
ATTEMPT = ROOT / r"Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY04\attempt_01"
TERMINAL = ROOT / r"Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY04_TERMINAL_SUPERVISOR_MANIFEST.json"
EMERGENCY = ROOT / r"Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY04_EMERGENCY_RECEIPT.jsonl"
DEPENDENCY_FREEZE = ROOT / r"Docs\AAA_Review\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY04_DEPENDENCY_PROBE_TERMINAL_FREEZE.json"


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require(value, message):
    if not value:
        raise RuntimeError(message)


require(digest(SOURCE) == "96ed0418079aa05e540b75e3db32b53dfeb3749131092525e18e830984f79f08", "corrected source hash mismatch")
require(digest(SUPERVISOR) == "72441beaebdb2e038ce71ca0f42f72348076b80fdb2021358f3716a08f3f1fed", "corrected supervisor hash mismatch")
require(digest(TESTS) == "2d2a56b866164d4631354acc2cadcb364be16d858a0007f9bb28564528e62f7e", "tests hash mismatch")
require(INPUT_MAP.stat().st_size == 8681 and digest(INPUT_MAP) == "5c8b7c6b0c6024767fa8a671523b5626213bd029d591270654080aed5fc7ced4", "accepted input map mismatch")
require(digest(DEPENDENCY_FREEZE) == "6531cf1a9a0c9f83b4f51981e3f52e6c2e65f45dcd99b9216b0c6ca95c1f72fd", "dependency-probe freeze mismatch")
freeze = json.loads(DEPENDENCY_FREEZE.read_text(encoding="utf-8-sig"))
require(freeze["classification"] == "PASSED_DEPENDENCY_PROBE_READY_FOR_RECOVERY04_FREEZE", "dependency classification mismatch")
for member in freeze["members"]:
    path = Path(member["path"])
    require(path.stat().st_size == member["bytes"] and digest(path) == member["sha256"], f"frozen member mismatch: {path}")

source = SOURCE.read_text(encoding="utf-8")
ast.parse(source, filename=str(SOURCE))
required = (
    'scan_paths_synchronous([PCG_SCAN_ROOT], True, False)',
    'registry.get_asset_by_object_path(record["object_path"])',
    'unreal.EditorAssetLibrary.does_asset_exist(package_path)',
    'unreal.load_asset(package_path)',
    'unreal.load_object(None, record["object_path"])',
    'record["class"] == "StaticMesh"',
    'record["valid_nonzero_bounds"]',
    'require(all(record["passed"] for record in result["pcg_tree_validation"])',
)
for token in required:
    require(token in source, f"registry contract token missing: {token}")
scan = source.index('result["pcg_registry_initialization"] = scan_pcg_registry(registry)')
validation = source.index('validate_pcg_tree_dependency(registry, path)')
loading = source.index('loaded = {path: load_required_asset(path) for path in dependencies}')
duplication = source.index('EditorAssetLibrary.duplicate_asset(INPUT_ASSET, OUTPUT_ASSET)')
require(scan < validation < loading < duplication, "registry-scan/load/duplicate ordering failed")
require(source.count("EditorAssetLibrary.duplicate_asset(INPUT_ASSET, OUTPUT_ASSET)") == 1, "duplicate call count changed")
require("SAVE_ALLOWLIST = (OUTPUT_ASSET,)" in source, "save allowlist changed")
require("coast_tree_proxy" not in source, "proxy substitution introduced")

supervisor = SUPERVISOR.read_text(encoding="utf-8")
require(supervisor.count("$run=Invoke-CapturedProcess -FilePath $Editor") == 1, "future Unreal launch count is not one")
require("retry_count=0" in supervisor, "zero-retry evidence missing")
require(not re.search(r"(?i)(for|while)\s*\([^\n]*retry", supervisor), "retry loop exists")
require("PCG registry initialization evidence failed" in supervisor and "PCG tree validation evidence failed" in supervisor, "postflight registry checks missing")
require("-NullRHI" in supervisor and "-run=pythonscript" in supervisor, "governed Unreal arguments missing")
for future in (ATTEMPT, OUTPUT_MAP, TERMINAL, EMERGENCY):
    require(not future.exists(), f"future governed namespace exists: {future}")

print("PASS")
