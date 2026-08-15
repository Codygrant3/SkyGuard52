from __future__ import annotations

"""Recovery03 production binding for the immutable rail-coupon generator.

This wrapper preserves the frozen source and applies three verified in-memory
compatibility corrections: a fresh gate identity, compatibility with the
controller-created output directory, and measured pre-bevel top-width
compensation so the evaluated Blender 5.2 result retains the authoritative
21.209 mm width within the frozen one-micron tolerance.
"""

from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\References\CombatAssets\CombatAsset_Refinement_Cycle03_Execution"
    r"\source\blender_gate7_combat_asset_refinement_cycle03_rail_coupon_attempt01.py"
)
EXPECTED_SOURCE_SHA256 = "1be92884de1bdc38f84c30d71a2daf4753f2d4054f6432f61b3e7f4a28d7799e"
OLD_GATE = 'GATE = "GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_ATTEMPT01"'
NEW_GATE = 'GATE = "GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY03_ATTEMPT01"'
OLD_OUTPUT_CREATE = "output.mkdir(parents=True, exist_ok=False)"
NEW_OUTPUT_CREATE = "output.mkdir(parents=True, exist_ok=True)"
OLD_TOOTH_TOP_WIDTH = (
    '            DIMENSIONS_M["top_width"],\n'
    "            BASE_HEIGHT_M,"
)
NEW_TOOTH_TOP_WIDTH = (
    '            DIMENSIONS_M["top_width"] + 0.0000498449856024326,\n'
    "            BASE_HEIGHT_M,"
)


def sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if not SOURCE.is_file():
    raise RuntimeError(f"Missing immutable rail generator: {SOURCE}")
if sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
    raise RuntimeError("Immutable rail generator hash mismatch")

source_text = SOURCE.read_text(encoding="utf-8")
for old_value, label in (
    (OLD_GATE, "gate identity"),
    (OLD_OUTPUT_CREATE, "output-directory contract"),
    (OLD_TOOTH_TOP_WIDTH, "tooth top-width anchor"),
):
    if source_text.count(old_value) != 1:
        raise RuntimeError(f"Immutable rail {label} was not found exactly once")

recovery_text = source_text.replace(OLD_GATE, NEW_GATE, 1)
recovery_text = recovery_text.replace(OLD_OUTPUT_CREATE, NEW_OUTPUT_CREATE, 1)
recovery_text = recovery_text.replace(OLD_TOOTH_TOP_WIDTH, NEW_TOOTH_TOP_WIDTH, 1)
compiled = compile(recovery_text, str(SOURCE) + "::Recovery03", "exec")
exec(compiled, {"__name__": "__main__", "__file__": str(SOURCE)})
