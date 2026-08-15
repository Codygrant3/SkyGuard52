"""Bind the accepted eight-camera D3D12 executor to GroundLightingCorrection04 Recovery01."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_structural_cleanup03_visual_proof01\capture_m01_photoreal_foundation_structural_cleanup03_visual_proof01.py"
)
EXPECTED_BYTES = 2252
EXPECTED_SHA256 = "acf3ac390a94f5dc0c7f0faebacd39ee6121780fbdf18675a1573c8726f19993"

OLD_PREFIX = "M01_PHOTOREAL_FOUNDATION_WAVE01_STRUCTURAL_CLEANUP03_"
NEW_PREFIX = "M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_"
OLD_ID = "M01-PHOTOREAL-FOUNDATION-WAVE01-STRUCTURAL-CLEANUP03-VISUAL-PROOF01"
NEW_ID = "M01-PHOTOREAL-FOUNDATION-WAVE01-GROUND-LIGHTING-CORRECTION04-RECOVERY01-VISUAL-PROOF01"
OLD_MAP = "Lvl_M01_PhotorealFoundation_StructuralCleanup03"
NEW_MAP = "Lvl_M01_PhotorealFoundation_GroundLightingCorrection04Recovery01"
OLD_CSV = "M01PhotorealFoundationWave01StructuralCleanup03VisualProof01.csv"
NEW_CSV = "M01PhotorealFoundationWave01GroundLightingCorrection04Recovery01VisualProof01.csv"
OLD_MATERIAL = "/Game/Skyguard/Materials/M_Terrain"
NEW_MATERIAL = (
    "/Game/M01/GroundLightingCorrection04Recovery01/Materials/"
    "MI_M01_UrbanGround_Tiled"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen StructuralCleanup03 proof executor changed")
    namespace = {"__name__": "structural_cleanup03_proof_executor_authority"}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    replacements = (
        (OLD_PREFIX, NEW_PREFIX),
        (OLD_ID, NEW_ID),
        (OLD_MAP, NEW_MAP),
        (OLD_CSV, NEW_CSV),
        (OLD_MATERIAL, NEW_MATERIAL),
    )
    for old, new in replacements:
        if old not in transformed:
            raise RuntimeError(f"Executor binding token is absent: {old}")
        transformed = transformed.replace(old, new)
    for old, _ in replacements:
        if old in transformed:
            raise RuntimeError(f"Executor retained stale token: {old}")
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::ground-lighting-correction04-recovery01-proof01", "exec"), globals(), globals())
