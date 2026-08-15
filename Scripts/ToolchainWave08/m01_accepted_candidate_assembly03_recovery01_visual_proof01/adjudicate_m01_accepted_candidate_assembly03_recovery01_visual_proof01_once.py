"""Bind the proven automatic D3D12 adjudicator to Assembly03 Recovery01."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01\adjudicate_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01_once.py"
)
EXPECTED_BYTES = 2513
EXPECTED_SHA256 = "9a163f864ff175867fd80b612b5d0cc4a7c0f95edfd2b4f9389eb5fe1af7a2f9"
OLD_PREFIX = "M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01_RECOVERY01"
NEW_PREFIX = "M01_ACCEPTED_CANDIDATE_ASSEMBLY03_RECOVERY01_VISUAL_PROOF01"
OLD_ID = "M01-COASTAL-CORRIDOR-C06R01-AXIS-RECOVERY01-VISUAL-PROOF01-RECOVERY01"
NEW_ID = "M01-ACCEPTED-CANDIDATE-ASSEMBLY03-RECOVERY01-VISUAL-PROOF01"
OLD_MAP = "Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01"
NEW_MAP = "Lvl_M01_AcceptedCandidateAssembly03_Recovery01"
OLD_CSV = "M01CoastalCorridorC06R01AxisRecovery01VisualProof01Recovery01.csv"
NEW_CSV = "M01AcceptedCandidateAssembly03Recovery01VisualProof01.csv"
OLD_SLUG = "m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01"
NEW_SLUG = "m01_accepted_candidate_assembly03_recovery01_visual_proof01"
OLD_KEBAB = "coastal-corridor-c06r01-axis-recovery01-visual-proof01-recovery01"
NEW_KEBAB = "accepted-candidate-assembly03-recovery01-visual-proof01"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen corridor adjudicator binder changed")
    namespace = {"__name__": "corridor_adjudicator_binder_authority"}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    for old, new in (
        (OLD_PREFIX, NEW_PREFIX), (OLD_ID, NEW_ID), (OLD_MAP, NEW_MAP),
        (OLD_CSV, NEW_CSV), (OLD_SLUG, NEW_SLUG), (OLD_KEBAB, NEW_KEBAB),
    ):
        if old not in transformed:
            raise RuntimeError(f"Adjudicator binding token is absent: {old}")
        transformed = transformed.replace(old, new)
    for stale in (OLD_PREFIX, OLD_ID, OLD_MAP, OLD_CSV, OLD_SLUG, OLD_KEBAB):
        if stale in transformed:
            raise RuntimeError(f"Adjudicator retained stale token: {stale}")
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::assembly03-proof01", "exec"), globals(), globals())
