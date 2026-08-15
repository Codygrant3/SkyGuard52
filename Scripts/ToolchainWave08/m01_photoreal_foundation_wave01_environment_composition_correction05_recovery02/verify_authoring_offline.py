from __future__ import annotations

import hashlib
import json
import py_compile
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
ORIGINAL = ROOT / "Scripts/ToolchainWave08/m01_photoreal_foundation_wave01_environment_composition_correction05/author_environment_composition_correction05.py"
BINDER = ROOT / "Scripts/ToolchainWave08/m01_photoreal_foundation_wave01_environment_composition_correction05_recovery02/author_environment_composition_correction05_recovery02.py"
CONTRACT = ROOT / "Docs/Toolchain/ToolchainWave08/M01PhotorealFoundationEnvironmentCompositionCorrection05Recovery02/quality_contract.json"
FAILED_FREEZE = ROOT / "Docs/AAA_Review/M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY01_AUTHORING_ATTEMPT01_TERMINAL_FREEZE.json"
OUTPUT = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_EnvironmentCompositionCorrection05Recovery02.umap"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_AUTHORING/attempt_01"
TERMINAL = ROOT / "Saved/Reports/M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_AUTHORING_TERMINAL_MANIFEST.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


require(ORIGINAL.is_file() and ORIGINAL.stat().st_size == 22628, "Frozen original author missing or changed")
require(sha256(ORIGINAL) == "250c91c8facdea46ce1e5602eeb47e90cefd609c6b9f908f9f19c67eb5e2c294", "Frozen original author hash changed")
require(FAILED_FREEZE.is_file() and FAILED_FREEZE.stat().st_size == 3541, "Recovery01 failure freeze missing or changed")
require(sha256(FAILED_FREEZE) == "512c8431ed4faad150ebf7991b9418fded102e0df51c6ee9854c7c7d9f4fbd05", "Recovery01 failure freeze hash changed")
require(BINDER.is_file() and CONTRACT.is_file(), "Recovery02 binder or contract missing")
py_compile.compile(str(BINDER), doraise=True)
contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
require(contract["classification"] == "PASSED_READY_FOR_OFFLINE_VALIDATION", "Recovery02 contract classification changed")

source = BINDER.read_text(encoding="utf-8")
for token in ("Recovery02", '"ocean_wave_bindings": 1,', '"ocean_wave_state_preserved": 1,', '"set_water_waves" not in source, "Unsupported wave mutation remains"'):
    require(token in source, f"Recovery02 binder token missing: {token}")

bound = ORIGINAL.read_text(encoding="utf-8")
replacements = (
    ("EnvironmentCompositionCorrection05", "EnvironmentCompositionCorrection05Recovery02", 6),
    ("ENVIRONMENT_COMPOSITION_CORRECTION05", "ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02", 2),
    ("environment-composition-correction05", "environment-composition-correction05-recovery02", 1),
    ("    ocean_waves = unreal.load_asset(OCEAN_WAVES_PATH)\n    require(ocean_waves is not None, f\"Ocean waves unavailable: {OCEAN_WAVES_PATH}\")\n", "", 1),
    ("    ocean.set_water_waves(ocean_waves)\n    waves_after = object_path(ocean.get_editor_property(\"water_waves\"))\n    require(waves_after == object_path(ocean_waves), \"Ocean wave binding failed\")", "    waves_after = waves_before\n    require(waves_after == waves_before, \"Existing ocean wave state changed\")", 1),
    ('"ocean_wave_bindings": 1,', '"ocean_wave_state_preserved": 1,', 2),
)
for old, new, expected_count in replacements:
    require(bound.count(old) == expected_count, f"Bound-source token count changed: {old!r}")
    bound = bound.replace(old, new)
compile(bound, "bound_authoring_source.py", "exec")
require("set_water_waves" not in bound, "Bound source contains unsupported wave mutation")
require(bound.count('get_editor_property("water_waves")') == 1, "Bound wave-state read count changed")
require(bound.count('"ocean_wave_state_preserved": 1,') == 2, "Bound wave preservation metric changed")
require("EnvironmentCompositionCorrection05.umap" not in bound, "Failed output map remains in bound source")
require("ENVIRONMENT_COMPOSITION_CORRECTION05_AUTHORING" not in bound, "Failed attempt namespace remains in bound source")

for future in (OUTPUT, ATTEMPT, TERMINAL):
    require(not future.exists(), f"Fresh Recovery02 namespace already exists: {future}")

print("PASS")
sys.exit(0)
