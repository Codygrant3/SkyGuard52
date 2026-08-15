"""Bind the corridor automatic D3D12 adjudicator to the exact transient-PCG recovery."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01\adjudicate_m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_once.py"
)
EXPECTED_BYTES = 2871
EXPECTED_SHA256 = "4181f7af13ad54da8c1519029bc94069ef9c14f20442d2026820710c8de3a4ba"

OLD_PREFIX = "M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01"
NEW_PREFIX = "M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_VISUAL_PROOF01_RECOVERY01"
OLD_ID = "M01-COASTAL-CORRIDOR-C06R01-AXIS-RECOVERY01-VISUAL-PROOF01"
NEW_ID = "M01-COASTAL-CORRIDOR-C06R01-AXIS-RECOVERY01-VISUAL-PROOF01-RECOVERY01"
OLD_CSV = "M01CoastalCorridorC06R01AxisRecovery01VisualProof01.csv"
NEW_CSV = "M01CoastalCorridorC06R01AxisRecovery01VisualProof01Recovery01.csv"
OLD_SLUG = "m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01"
NEW_SLUG = "m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01_recovery01"
OLD_KEBAB = "coastal-corridor-c06r01-axis-recovery01-visual-proof01"
NEW_KEBAB = "coastal-corridor-c06r01-axis-recovery01-visual-proof01-recovery01"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen corridor Axis Recovery01 proof adjudicator changed")
    namespace = {"__name__": "corridor_axis_recovery01_proof_adjudicator_authority"}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    replacements = (
        (OLD_PREFIX, NEW_PREFIX),
        (OLD_ID, NEW_ID),
        (OLD_CSV, NEW_CSV),
        (OLD_SLUG, NEW_SLUG),
        (OLD_KEBAB, NEW_KEBAB),
    )
    for old, new in replacements:
        if old not in transformed:
            raise RuntimeError(f"Adjudicator Recovery01 binding token is absent: {old}")
        transformed = transformed.replace(old, new)
    for old, _ in replacements:
        if f'"{old}"' in transformed:
            raise RuntimeError(f"Adjudicator Recovery01 retained stale token: {old}")
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::corridor-axis-recovery01-proof01-recovery01", "exec"), globals(), globals())
