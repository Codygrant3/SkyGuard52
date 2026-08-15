"""Bind Correction05 to preserve the existing wave state under UE 5.8 Python."""

from __future__ import annotations

import hashlib
from pathlib import Path


ORIGINAL = Path(r"D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_environment_composition_correction05\author_environment_composition_correction05.py")
FAILED_FREEZE = Path(r"D:\Skyguard52\Docs\AAA_Review\M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY01_AUTHORING_ATTEMPT01_TERMINAL_FREEZE.json")
EXPECTED_ORIGINAL_BYTES = 22628
EXPECTED_ORIGINAL_SHA256 = "250c91c8facdea46ce1e5602eeb47e90cefd609c6b9f908f9f19c67eb5e2c294"
EXPECTED_FAILED_FREEZE_BYTES = 3541
EXPECTED_FAILED_FREEZE_SHA256 = "512c8431ed4faad150ebf7991b9418fded102e0df51c6ee9854c7c7d9f4fbd05"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def replace_exact(source: str, old: str, new: str, expected_count: int) -> str:
    actual = source.count(old)
    require(actual == expected_count, f"Binding token count changed for {old!r}: {actual} != {expected_count}")
    return source.replace(old, new)


require(ORIGINAL.is_file() and ORIGINAL.stat().st_size == EXPECTED_ORIGINAL_BYTES, "Frozen Correction05 author missing or changed")
require(sha256(ORIGINAL) == EXPECTED_ORIGINAL_SHA256, "Frozen Correction05 author hash changed")
require(FAILED_FREEZE.is_file() and FAILED_FREEZE.stat().st_size == EXPECTED_FAILED_FREEZE_BYTES, "Recovery01 failure freeze missing or changed")
require(sha256(FAILED_FREEZE) == EXPECTED_FAILED_FREEZE_SHA256, "Recovery01 failure freeze hash changed")

source = ORIGINAL.read_text(encoding="utf-8")
source = replace_exact(source, "EnvironmentCompositionCorrection05", "EnvironmentCompositionCorrection05Recovery02", 6)
source = replace_exact(source, "ENVIRONMENT_COMPOSITION_CORRECTION05", "ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02", 2)
source = replace_exact(source, "environment-composition-correction05", "environment-composition-correction05-recovery02", 1)
source = replace_exact(
    source,
    "    ocean_waves = unreal.load_asset(OCEAN_WAVES_PATH)\n    require(ocean_waves is not None, f\"Ocean waves unavailable: {OCEAN_WAVES_PATH}\")\n",
    "",
    1,
)
source = replace_exact(
    source,
    "    ocean.set_water_waves(ocean_waves)\n    waves_after = object_path(ocean.get_editor_property(\"water_waves\"))\n    require(waves_after == object_path(ocean_waves), \"Ocean wave binding failed\")",
    "    waves_after = waves_before\n    require(waves_after == waves_before, \"Existing ocean wave state changed\")",
    1,
)
source = replace_exact(source, '"ocean_wave_bindings": 1,', '"ocean_wave_state_preserved": 1,', 2)

require("EnvironmentCompositionCorrection05.umap" not in source, "Failed output map remains in bound source")
require("ENVIRONMENT_COMPOSITION_CORRECTION05_AUTHORING" not in source, "Failed attempt namespace remains in bound source")
require("set_water_waves" not in source, "Unsupported wave mutation remains")
require(source.count('get_editor_property("water_waves")') == 1, "Wave-state read contract changed")
require(source.count('"ocean_wave_state_preserved": 1,') == 2, "Wave preservation metric changed")

compiled = compile(source, "D:/Skyguard52/Scripts/ToolchainWave08/m01_photoreal_foundation_wave01_environment_composition_correction05_recovery02/bound_authoring_source.py", "exec")
scope = {"__name__": "__main__", "__file__": str(ORIGINAL)}
exec(compiled, scope, scope)
