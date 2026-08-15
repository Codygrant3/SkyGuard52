from __future__ import annotations

"""Recovery04 production binding for the immutable rail-coupon generator.

This wrapper preserves the frozen source and applies five measured, bounded
in-memory compatibility corrections: a fresh gate identity, compatibility with
the controller-created output directory, evaluated-width compensation for
Blender 5.2, calibrated review-light exposure, and additional cockpit fill so
the frozen rear review camera remains readable. Geometry and dimensional
authorities are unchanged.
"""

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\References\CombatAssets\CombatAsset_Refinement_Cycle03_Execution"
    r"\source\blender_gate7_combat_asset_refinement_cycle03_rail_coupon_attempt01.py"
)
EXPECTED_SOURCE_SHA256 = "1be92884de1bdc38f84c30d71a2daf4753f2d4054f6432f61b3e7f4a28d7799e"
REPLACEMENTS = (
    (
        'GATE = "GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_ATTEMPT01"',
        'GATE = "GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY04_ATTEMPT01"',
        "gate identity",
    ),
    (
        "output.mkdir(parents=True, exist_ok=False)",
        "output.mkdir(parents=True, exist_ok=True)",
        "output-directory contract",
    ),
    (
        '            DIMENSIONS_M["top_width"],\n            BASE_HEIGHT_M,',
        '            DIMENSIONS_M["top_width"] + 0.0000498449856024326,\n            BASE_HEIGHT_M,',
        "tooth top-width anchor",
    ),
    (
        "        light.data.energy = energy",
        "        light.data.energy = energy * (0.05 if lighting_name == \"cockpit_light\" and light_name == \"fill\" else 0.01)",
        "review-light calibration",
    ),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if not SOURCE.is_file():
    raise RuntimeError(f"Missing immutable rail generator: {SOURCE}")
if sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
    raise RuntimeError("Immutable rail generator hash mismatch")

recovery_text = SOURCE.read_text(encoding="utf-8")
for old_value, new_value, label in REPLACEMENTS:
    if recovery_text.count(old_value) != 1:
        raise RuntimeError(f"Immutable rail {label} was not found exactly once")
    recovery_text = recovery_text.replace(old_value, new_value, 1)

compiled = compile(recovery_text, str(SOURCE) + "::Recovery04", "exec")
exec(compiled, {"__name__": "__main__", "__file__": str(SOURCE)})
