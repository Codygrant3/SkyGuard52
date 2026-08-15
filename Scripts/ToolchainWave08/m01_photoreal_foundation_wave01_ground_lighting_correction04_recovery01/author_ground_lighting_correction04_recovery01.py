from __future__ import annotations

import hashlib
from pathlib import Path


ORIGINAL = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_ground_lighting_correction04\author_ground_lighting_correction04.py"
)
EXPECTED_BYTES = 20684
EXPECTED_SHA256 = "eba032612dd1ee9de55560b1fef1ec8f88fdf608d96121ef3d1c08132ce818b3"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


require(ORIGINAL.is_file(), f"Frozen Correction04 source missing: {ORIGINAL}")
require(ORIGINAL.stat().st_size == EXPECTED_BYTES, "Frozen Correction04 source byte count changed")
require(sha256(ORIGINAL) == EXPECTED_SHA256, "Frozen Correction04 source hash changed")

source = ORIGINAL.read_text(encoding="utf-8")
replacements = (
    ("GroundLightingCorrection04", "GroundLightingCorrection04Recovery01", 6),
    ("GROUND_LIGHTING_CORRECTION04", "GROUND_LIGHTING_CORRECTION04_RECOVERY01", 4),
    ("ground-lighting-correction04", "ground-lighting-correction04-recovery01", 1),
    (
        '    require(bool(success), f"Failed to set {parameter} on {instance.get_path_name()}")',
        "    _known_ue58_false_return = success  # Installed UE 5.8 always returns false; verify_vector is authoritative.",
        1,
    ),
)

for old, new, expected_count in replacements:
    actual_count = source.count(old)
    require(actual_count == expected_count, f"Compatibility-binding token count changed: {old!r} -> {actual_count}")
    source = source.replace(old, new)

require("require(bool(success)" not in source, "Invalid UE 5.8 setter-return requirement remains")
require(source.count("verify_vector(sand, parameter, TARGET_SAND_TILING)") == 1, "Sand readback validation changed")
require(source.count("verify_vector(pavers, parameter, TARGET_URBAN_TILING)") == 1, "Urban readback validation changed")
require(source.count('verify_vector(far_water, "Water Albedo", TARGET_FAR_ALBEDO)') == 1, "Far-water readback changed")
require(source.count('verify_vector(window, "BaseColorFactor", TARGET_WINDOW_COLOR)') == 1, "Window readback changed")
require(source.count('verify_vector(glass, "BaseColorFactor", TARGET_GLASS_COLOR)') == 1, "Glass readback changed")
require("GroundLightingCorrection04/Materials" not in source, "Failed material namespace remains in bound source")
require("GROUND_LIGHTING_CORRECTION04_AUTHORING" not in source, "Failed attempt namespace remains in bound source")

compiled = compile(
    source,
    "D:/Skyguard52/Scripts/ToolchainWave08/m01_photoreal_foundation_wave01_ground_lighting_correction04_recovery01/bound_authoring_source.py",
    "exec",
)
scope = {"__name__": "__main__", "__file__": str(ORIGINAL)}
exec(compiled, scope, scope)
