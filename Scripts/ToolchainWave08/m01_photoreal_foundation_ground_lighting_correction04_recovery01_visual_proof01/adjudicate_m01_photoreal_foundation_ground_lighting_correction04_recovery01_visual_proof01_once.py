"""Bind the accepted automatic adjudicator to GroundLightingCorrection04 Recovery01."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_structural_cleanup03_visual_proof01\adjudicate_m01_photoreal_foundation_structural_cleanup03_visual_proof01_once.py"
)
EXPECTED_BYTES = 2658
EXPECTED_SHA256 = "719f851024afc92eeace3f157f05c7a4e18a94c64a79720f4e381521c015e027"

OLD_PREFIX = "M01_PHOTOREAL_FOUNDATION_WAVE01_STRUCTURAL_CLEANUP03_"
NEW_PREFIX = "M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_"
OLD_ID = "M01-PHOTOREAL-FOUNDATION-WAVE01-STRUCTURAL-CLEANUP03-VISUAL-PROOF01"
NEW_ID = "M01-PHOTOREAL-FOUNDATION-WAVE01-GROUND-LIGHTING-CORRECTION04-RECOVERY01-VISUAL-PROOF01"
OLD_MAP = "Lvl_M01_PhotorealFoundation_StructuralCleanup03"
NEW_MAP = "Lvl_M01_PhotorealFoundation_GroundLightingCorrection04Recovery01"
OLD_CSV = "M01PhotorealFoundationWave01StructuralCleanup03VisualProof01.csv"
NEW_CSV = "M01PhotorealFoundationWave01GroundLightingCorrection04Recovery01VisualProof01.csv"
OLD_SLUG = "m01_photoreal_foundation_wave01_structural_cleanup03_visual_proof01"
NEW_SLUG = "m01_photoreal_foundation_wave01_ground_lighting_correction04_recovery01_visual_proof01"
OLD_KEBAB = "photoreal-foundation-wave01-structural-cleanup03-visual-proof01"
NEW_KEBAB = "photoreal-foundation-wave01-ground-lighting-correction04-recovery01-visual-proof01"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen StructuralCleanup03 proof adjudicator changed")
    namespace = {"__name__": "structural_cleanup03_proof_adjudicator_authority"}
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
    exec(compile(transform_source(), str(SOURCE) + "::ground-lighting-correction04-recovery01-proof01", "exec"), globals(), globals())
