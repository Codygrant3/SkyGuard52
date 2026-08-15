import ast
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(r"D:\\Skyguard52")
SOURCE = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery05\author_m01_environment_authoring01_recovery05.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery05\invoke_environment_authoring01_recovery05_once.ps1"
TESTS = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery05\test_environment_authoring01_recovery05_offline.py"
INPUT_MAP = Path(r"D:\\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap")
OUTPUT_MAP = Path(r"D:\\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery05.umap")
ATTEMPT = ROOT / r"Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY05\attempt_01"
TERMINAL = ROOT / r"Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY05_TERMINAL_SUPERVISOR_MANIFEST.json"
EMERGENCY = ROOT / r"Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY05_EMERGENCY_RECEIPT.jsonl"
FAILURE_FREEZE = ROOT / r"Docs\AAA_Review\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY04_ATTEMPT01_TERMINAL_FREEZE.json"

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()

def require(value,message):
    if not value: raise RuntimeError(message)

require(digest(SOURCE)=="dc9811dd891412738b3245a0731a7deac0de9088d3d2546ac504f0f355a61a07","source hash mismatch")
require(digest(SUPERVISOR)=="ca12858a48e9a5dba1d1fe4097cb9ef6d53524aae01940ef06abb18d3eacffae","supervisor hash mismatch")
require(digest(TESTS)=="ecfad2038874dd7d5a04fd99aaedf837f09662e0441fa713dbb5e965521d50ae","tests hash mismatch")
require(INPUT_MAP.stat().st_size==8681 and digest(INPUT_MAP)=="5c8b7c6b0c6024767fa8a671523b5626213bd029d591270654080aed5fc7ced4","input map mismatch")
require(digest(FAILURE_FREEZE)=="18f5b8a77e4b48b1a324ba007b7280449d4c417a3e2c458e59b0df2128f3162a","Recovery04 failure freeze mismatch")
freeze=json.loads(FAILURE_FREEZE.read_text(encoding="utf-8-sig"))
require(freeze["classification"]=="FAILED_WITH_EVIDENCE","Recovery04 classification mismatch")
for member in freeze["members"]:
    p=Path(member["path"])
    require(p.stat().st_size==member["bytes"] and digest(p)==member["sha256"],f"member mismatch: {p}")

source=SOURCE.read_text(encoding="utf-8")
ast.parse(source,filename=str(SOURCE))
required=(
    'require(len(directors) <= 1',
    'SPAWNED_DETERMINISTICALLY_IN_FRESH_OUTPUT',
    'REUSED_SINGLE_EXISTING_OUTPUT_DIRECTOR',
    'result["director_acquisition"] = {',
    'scan_pcg_registry(registry)',
    'validate_pcg_tree_dependency(registry, path)',
    'EditorAssetLibrary.duplicate_asset(INPUT_ASSET, OUTPUT_ASSET)',
)
for token in required: require(token in source,f"missing token: {token}")
require(source.index('result["director_acquisition"] = {') < source.index('author_governed_landscape_with_existing_graph('),"acquisition ordering failed")
require(source.count("EditorAssetLibrary.duplicate_asset(INPUT_ASSET, OUTPUT_ASSET)")==1,"duplication count changed")
require("coast_tree_proxy" not in source,"proxy substitution introduced")

supervisor=SUPERVISOR.read_text(encoding="utf-8")
require(supervisor.count("$run=Invoke-CapturedProcess -FilePath $Editor")==1,"Unreal launch count is not one")
require("retry_count=0" in supervisor,"zero retry evidence missing")
require(not re.search(r"(?i)(for|while)\s*\([^\n]*retry",supervisor),"retry loop exists")
require("Environment director acquisition evidence failed" in supervisor,"director postflight missing")
for p in (OUTPUT_MAP,ATTEMPT,TERMINAL,EMERGENCY): require(not p.exists(),f"future namespace exists: {p}")
print("PASS")
