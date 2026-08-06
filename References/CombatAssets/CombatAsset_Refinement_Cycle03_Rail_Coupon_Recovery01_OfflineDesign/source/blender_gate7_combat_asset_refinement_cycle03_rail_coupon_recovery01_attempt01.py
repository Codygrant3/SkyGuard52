from __future__ import annotations

"""Recovery01 execution binding for the immutable Attempt01 rail generator.

The original generator was never launched. This wrapper preserves it byte-for-byte,
changes only the governed gate identity in memory, and forwards the original CLI.
"""

from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\References\CombatAssets\CombatAsset_Refinement_Cycle03_Execution"
    r"\source\blender_gate7_combat_asset_refinement_cycle03_rail_coupon_attempt01.py"
)
EXPECTED_SOURCE_SHA256 = "1be92884de1bdc38f84c30d71a2daf4753f2d4054f6432f61b3e7f4a28d7799e"
OLD_GATE = 'GATE = "GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_ATTEMPT01"'
NEW_GATE = 'GATE = "GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY01_ATTEMPT01"'


def sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if not SOURCE.is_file():
    raise RuntimeError(f"Missing immutable Attempt01 generator: {SOURCE}")
if sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
    raise RuntimeError("Immutable Attempt01 generator hash mismatch")

source_text = SOURCE.read_text(encoding="utf-8")
if source_text.count(OLD_GATE) != 1:
    raise RuntimeError("Attempt01 gate identity was not found exactly once")
if NEW_GATE in source_text:
    raise RuntimeError("Attempt01 source unexpectedly already contains Recovery01 identity")

recovery_text = source_text.replace(OLD_GATE, NEW_GATE, 1)
compiled = compile(recovery_text, str(SOURCE) + "::Recovery01", "exec")
exec(compiled, {"__name__": "__main__", "__file__": str(SOURCE)})
