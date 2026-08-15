"""Bind the proven automatic D3D12 adjudicator to the corrected coastal corridor map."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_environment_composition_correction05_recovery02_visual_proof01\adjudicate_m01_photoreal_foundation_environment_composition_correction05_recovery02_visual_proof01_once.py"
)
EXPECTED_BYTES = 2977
EXPECTED_SHA256 = "a71e08ef776aed613af90af1ea6974df9f8eca2bd241bb82cf6ecf52865c83f3"

OLD_PREFIX = "M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_"
NEW_PREFIX = "M01_COASTAL_CORRIDOR_C06R01_AXIS_RECOVERY01_"
OLD_ID = "M01-PHOTOREAL-FOUNDATION-WAVE01-ENVIRONMENT-COMPOSITION-CORRECTION05-RECOVERY02-VISUAL-PROOF01"
NEW_ID = "M01-COASTAL-CORRIDOR-C06R01-AXIS-RECOVERY01-VISUAL-PROOF01"
OLD_MAP = "Lvl_M01_PhotorealFoundation_EnvironmentCompositionCorrection05Recovery02"
NEW_MAP = "Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01"
OLD_CSV = "M01PhotorealFoundationWave01EnvironmentCompositionCorrection05Recovery02VisualProof01.csv"
NEW_CSV = "M01CoastalCorridorC06R01AxisRecovery01VisualProof01.csv"
OLD_SLUG = "m01_photoreal_foundation_wave01_environment_composition_correction05_recovery02_visual_proof01"
NEW_SLUG = "m01_coastal_corridor_c06r01_axis_recovery01_visual_proof01"
OLD_KEBAB = "photoreal-foundation-wave01-environment-composition-correction05-recovery02-visual-proof01"
NEW_KEBAB = "coastal-corridor-c06r01-axis-recovery01-visual-proof01"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen EnvironmentCompositionCorrection05 Recovery02 proof adjudicator changed")
    namespace = {"__name__": "environment_composition_correction05_recovery02_proof_adjudicator_authority"}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    replacements = (
        (OLD_PREFIX, NEW_PREFIX),
        (OLD_ID, NEW_ID),
        (OLD_MAP, NEW_MAP),
        (OLD_CSV, NEW_CSV),
        (OLD_SLUG, NEW_SLUG),
        (OLD_KEBAB, NEW_KEBAB),
    )
    for old, new in replacements:
        if old not in transformed:
            raise RuntimeError(f"Adjudicator binding token is absent: {old}")
        transformed = transformed.replace(old, new)
    for old, _ in replacements:
        if old in transformed:
            raise RuntimeError(f"Adjudicator retained stale token: {old}")
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::coastal-corridor-c06r01-axis-recovery01-proof01", "exec"), globals(), globals())
