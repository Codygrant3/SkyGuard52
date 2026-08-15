from __future__ import annotations

import hashlib
import json
import py_compile
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
ORIGINAL = ROOT / "Scripts/ToolchainWave08/m01_photoreal_foundation_wave01_environment_composition_correction05/author_environment_composition_correction05.py"
BINDER = ROOT / "Scripts/ToolchainWave08/m01_photoreal_foundation_wave01_environment_composition_correction05_recovery01/author_environment_composition_correction05_recovery01.py"
CONTRACT = ROOT / "Docs/Toolchain/ToolchainWave08/M01PhotorealFoundationEnvironmentCompositionCorrection05Recovery01/quality_contract.json"
FAILED_FREEZE = ROOT / "Docs/AAA_Review/M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_AUTHORING_ATTEMPT01_TERMINAL_FREEZE.json"
OUTPUT = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_EnvironmentCompositionCorrection05Recovery01.umap"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY01_AUTHORING/attempt_01"
TERMINAL = ROOT / "Saved/Reports/M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY01_AUTHORING_TERMINAL_MANIFEST.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


require(ORIGINAL.is_file() and ORIGINAL.stat().st_size == 22628, "Frozen original author missing or changed")
require(digest(ORIGINAL) == "250c91c8facdea46ce1e5602eeb47e90cefd609c6b9f908f9f19c67eb5e2c294", "Frozen original author hash changed")
require(FAILED_FREEZE.is_file() and FAILED_FREEZE.stat().st_size == 4119, "Failed-attempt freeze missing or changed")
require(digest(FAILED_FREEZE) == "57d5f609719f47089a779af59e670c249cf408d2b45a903e4a4b64bd5c04494f", "Failed-attempt freeze hash changed")
require(BINDER.is_file() and CONTRACT.is_file(), "Recovery01 binder or contract missing")
py_compile.compile(str(BINDER), doraise=True)
contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
require(contract["classification"] == "PASSED_READY_FOR_OFFLINE_VALIDATION", "Recovery01 contract classification changed")

source = BINDER.read_text(encoding="utf-8")
required = (
    '"EnvironmentCompositionCorrection05", "EnvironmentCompositionCorrection05Recovery01", 6',
    '"ENVIRONMENT_COMPOSITION_CORRECTION05", "ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY01", 2',
    "ocean_waves_asset.get_editor_property",
    'ocean.set_water_waves(ocean_waves)',
    "EXPECTED_FAILED_FREEZE_SHA256",
)
for token in required:
    require(token in source, f"Recovery01 token missing: {token}")
require("destroy_actor" not in source and "set_actor_scale3d" not in source, "Recovery binder contains independent geometry behavior")
require(source.count("exec(compiled, scope, scope)") == 1, "Recovery binder execution count changed")

bound = ORIGINAL.read_text(encoding="utf-8")
replacements = (
    ("EnvironmentCompositionCorrection05", "EnvironmentCompositionCorrection05Recovery01", 6),
    ("ENVIRONMENT_COMPOSITION_CORRECTION05", "ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY01", 2),
    ("environment-composition-correction05", "environment-composition-correction05-recovery01", 1),
    (
        "    ocean_waves = unreal.load_asset(OCEAN_WAVES_PATH)\n    require(ocean_waves is not None, f\"Ocean waves unavailable: {OCEAN_WAVES_PATH}\")",
        "    ocean_waves_asset = unreal.load_asset(OCEAN_WAVES_PATH)\n"
        "    require(ocean_waves_asset is not None, f\"Ocean waves asset unavailable: {OCEAN_WAVES_PATH}\")\n"
        "    ocean_waves = ocean_waves_asset.get_editor_property(\"water_waves\")\n"
        "    require(ocean_waves is not None, f\"Contained ocean waves source unavailable: {OCEAN_WAVES_PATH}\")",
        1,
    ),
)
for old, new, expected_count in replacements:
    require(bound.count(old) == expected_count, f"Bound-source token count changed: {old!r}")
    bound = bound.replace(old, new)
compile(bound, "bound_authoring_source.py", "exec")
require("EnvironmentCompositionCorrection05.umap" not in bound, "Failed map remains in compiled bound source")
require("ENVIRONMENT_COMPOSITION_CORRECTION05_AUTHORING" not in bound, "Failed attempt remains in compiled bound source")
require(bound.count('get_editor_property("water_waves")') == 3, "Bound contained-wave access count changed")
require(bound.count("ocean.set_water_waves(ocean_waves)") == 1, "Bound water-wave assignment count changed")

for future in (OUTPUT, ATTEMPT, TERMINAL):
    require(not future.exists(), f"Fresh Recovery01 namespace already exists: {future}")

print("PASS")
sys.exit(0)
