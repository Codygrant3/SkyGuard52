import ast
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(r"D:\Skyguard52")
SOURCE07 = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery07\author_m01_environment_authoring01_recovery07.py"
SUPERVISOR07 = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery07\invoke_environment_authoring01_recovery07_once.ps1"
TESTS07 = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery07\test_environment_authoring01_recovery07_offline.py"
SOURCE06 = ROOT / r"Scripts\ToolchainWave08\environment_authoring01_recovery06\author_m01_environment_authoring01_recovery06.py"
TERMINAL06 = ROOT / r"Docs\AAA_Review\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_ATTEMPT01_TERMINAL_FREEZE.json"
INPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap")
OUTPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery07.umap")
FUTURE = (
    ROOT / r"Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07\attempt_01",
    ROOT / r"Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_TERMINAL_SUPERVISOR_MANIFEST.json",
    ROOT / r"Saved\Reports\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_EMERGENCY_RECEIPT.jsonl",
    OUTPUT_MAP,
)

EXPECTED = {
    SOURCE07: (22741, "faf3120733e9fcd3a8c10244a1cf72a9018944422b7a0588689ad892531bb6a1"),
    SUPERVISOR07: (18935, "48985d6c578a8f48ee7db0856297bf9b70a22066201e9ce8b3d7ba11abefbd1a"),
    TESTS07: (3911, "debc08368099498651d72ac006cda742bf81ea5e03900c6ab9bfd951b96bb2d9"),
    SOURCE06: (22652, "d077cba756dc59149bc0411c46051aa5ff20acb86ac0f489a53fc1557f8d27c0"),
    TERMINAL06: (5044, "65413962002d1c1ecc5c2760882a12e2186cdd4a20eb42246a34e6b1a9b2aea9"),
    INPUT_MAP: (8681, "5c8b7c6b0c6024767fa8a671523b5626213bd029d591270654080aed5fc7ced4"),
}

INSTALLED_AUTHORITIES = {
    Path(r"D:\UE_5.8\Engine\Source\Editor\LevelEditor\Private\LevelEditorSubsystem.cpp"):
        (35090, "9b4af00e4ce54a41115cd6bbf419dc0de8a8e40ae73dd47351e3efc63fa53949"),
    Path(r"D:\UE_5.8\Engine\Source\Editor\UnrealEd\Private\EditorServer.cpp"):
        (248072, "ff2a331b732b23610f0dbf43d7ce92fa3a362c8656f13f73d52b5ebdb6f1abc6"),
    Path(r"D:\UE_5.8\Engine\Source\Editor\UnrealEd\Private\Subsystems\EditorAssetSubsystem.cpp"):
        (64485, "f6c9fa0e4e8ec16ecab95b4d07651def70b71425fcc240bb3dc2dfcf7384939a"),
}

OLD_BLOCK = """    output_world = unreal.EditorAssetLibrary.duplicate_asset(INPUT_ASSET, OUTPUT_ASSET)
    require(output_world is not None, "Unreal API duplication failed")
    require(unreal.EditorLevelLibrary.load_level(OUTPUT_ASSET), "Fresh Authoring01 world failed to load")"""
NEW_BLOCK = """    level_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(level_editor_subsystem is not None, "LevelEditorSubsystem is unavailable")
    require(
        level_editor_subsystem.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET),
        "Fresh Authoring01 world failed to create from the accepted template",
    )"""


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def require(value, message):
    if not value:
        raise RuntimeError(message)


for path, (expected_bytes, expected_hash) in {**EXPECTED, **INSTALLED_AUTHORITIES}.items():
    require(path.is_file(), f"required file missing: {path}")
    require(path.stat().st_size == expected_bytes, f"byte-count mismatch: {path}")
    require(digest(path) == expected_hash, f"hash mismatch: {path}")

freeze = json.loads(TERMINAL06.read_text(encoding="utf-8"))
require(freeze["classification"] == "FAILED_WITH_EVIDENCE", "Recovery06 terminal classification changed")
require(freeze["member_count"] == 17 and len(freeze["members"]) == 17, "Recovery06 member count changed")
for record in freeze["members"]:
    member = Path(record["path"])
    require(member.is_file(), f"Recovery06 member missing: {member}")
    require(member.stat().st_size == int(record["bytes"]), f"Recovery06 member byte mismatch: {member}")
    require(digest(member) == record["sha256"], f"Recovery06 member hash mismatch: {member}")

source07 = SOURCE07.read_text(encoding="utf-8")
source06 = SOURCE06.read_text(encoding="utf-8")
supervisor07 = SUPERVISOR07.read_text(encoding="utf-8")
ast.parse(source07, filename=str(SOURCE07))

normalized = (
    source07
    .replace("RECOVERY07", "RECOVERY06")
    .replace("Recovery07", "Recovery06")
    .replace("recovery07", "recovery06")
    .replace(NEW_BLOCK, OLD_BLOCK)
)
require(normalized == source06, "Recovery07 source exceeds namespace and lifecycle allowlist")
require(source07.count("new_level_from_template(OUTPUT_ASSET, INPUT_ASSET)") == 1, "one-step template lifecycle count is not one")
require("duplicate_asset(INPUT_ASSET, OUTPUT_ASSET)" not in source07, "unsafe duplicate lifecycle remains")
require("load_level(OUTPUT_ASSET)" not in source07, "unsafe reload lifecycle remains")
require("output_world =" not in source07, "retained Python world wrapper remains")
for token in (
    "/Script/Water.WaterBodyOcean",
    "/Script/Water.WaterZone",
    "scan_pcg_registry(registry)",
    "director_acquisition",
    "grounding_records",
    "shore_contact_checks",
    "save_asset(OUTPUT_ASSET, only_if_is_dirty=False)",
):
    require(token in source07, f"environment contract token missing: {token}")

require(supervisor07.count("$run=Invoke-CapturedProcess -FilePath $Editor") == 1, "Unreal launch count is not one")
require('"-ExecutePythonScript=$AttemptAuthoring"' in supervisor07, "regular-editor Python mode missing")
require("'-ScriptErrorsAreFatal'" in supervisor07, "fatal Python errors switch missing")
require("-run=pythonscript" not in supervisor07, "commandlet mode remains")
require(not re.search(r"(?i)(for|while)\s*\([^\n]*retry", supervisor07), "retry loop exists")
require("retry_count=0" in supervisor07, "zero-retry evidence missing")
require("Remove-Item -LiteralPath $OutputMap" not in supervisor07, "failed partial output would be deleted")
require("65413962002d1c1ecc5c2760882a12e2186cdd4a20eb42246a34e6b1a9b2aea9" in supervisor07, "Recovery06 authority missing")
for path in FUTURE:
    require(not path.exists(), f"future governed namespace exists: {path}")

print("PASS")
