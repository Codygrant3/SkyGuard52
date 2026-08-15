from __future__ import annotations

"""Recovery02 production binding for the immutable rail-coupon generator.

The production controller creates the governed output directory before Blender
starts.  The frozen generator expected that directory to be absent.  This
wrapper verifies the immutable source, changes only the gate identity and the
output-directory compatibility flag in memory, then executes the result.
"""

from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\References\CombatAssets\CombatAsset_Refinement_Cycle03_Execution"
    r"\source\blender_gate7_combat_asset_refinement_cycle03_rail_coupon_attempt01.py"
)
EXPECTED_SOURCE_SHA256 = "1be92884de1bdc38f84c30d71a2daf4753f2d4054f6432f61b3e7f4a28d7799e"
OLD_GATE = 'GATE = "GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_ATTEMPT01"'
NEW_GATE = 'GATE = "GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_RECOVERY02_ATTEMPT01"'
OLD_OUTPUT_CREATE = "output.mkdir(parents=True, exist_ok=False)"
NEW_OUTPUT_CREATE = "output.mkdir(parents=True, exist_ok=True)"


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
if source_text.count(OLD_GATE) != 1:
    raise RuntimeError("Original rail gate identity was not found exactly once")
if source_text.count(OLD_OUTPUT_CREATE) != 1:
    raise RuntimeError("Original output-directory contract was not found exactly once")
if NEW_GATE in source_text or NEW_OUTPUT_CREATE in source_text:
    raise RuntimeError("Immutable rail source unexpectedly contains Recovery02 changes")

recovery_text = source_text.replace(OLD_GATE, NEW_GATE, 1)
recovery_text = recovery_text.replace(OLD_OUTPUT_CREATE, NEW_OUTPUT_CREATE, 1)
compiled = compile(recovery_text, str(SOURCE) + "::Recovery02", "exec")
exec(compiled, {"__name__": "__main__", "__file__": str(SOURCE)})
