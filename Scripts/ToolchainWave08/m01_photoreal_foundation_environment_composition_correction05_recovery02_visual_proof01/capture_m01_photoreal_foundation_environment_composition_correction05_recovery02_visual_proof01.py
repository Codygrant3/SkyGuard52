"""Bind the proven eight-camera D3D12 executor to EnvironmentCompositionCorrection05 Recovery02."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_ground_lighting_correction04_recovery01_visual_proof01\capture_m01_photoreal_foundation_ground_lighting_correction04_recovery01_visual_proof01.py"
)
EXPECTED_BYTES = 2520
EXPECTED_SHA256 = "3e92ed21fdc892b71634e8460600e2a35a78f1146da856de7d8648ad5d7abbe9"

OLD_PREFIX = "M01_PHOTOREAL_FOUNDATION_WAVE01_GROUND_LIGHTING_CORRECTION04_RECOVERY01_"
NEW_PREFIX = "M01_PHOTOREAL_FOUNDATION_WAVE01_ENVIRONMENT_COMPOSITION_CORRECTION05_RECOVERY02_"
OLD_ID = "M01-PHOTOREAL-FOUNDATION-WAVE01-GROUND-LIGHTING-CORRECTION04-RECOVERY01-VISUAL-PROOF01"
NEW_ID = "M01-PHOTOREAL-FOUNDATION-WAVE01-ENVIRONMENT-COMPOSITION-CORRECTION05-RECOVERY02-VISUAL-PROOF01"
OLD_MAP = "Lvl_M01_PhotorealFoundation_GroundLightingCorrection04Recovery01"
NEW_MAP = "Lvl_M01_PhotorealFoundation_EnvironmentCompositionCorrection05Recovery02"
OLD_CSV = "M01PhotorealFoundationWave01GroundLightingCorrection04Recovery01VisualProof01.csv"
NEW_CSV = "M01PhotorealFoundationWave01EnvironmentCompositionCorrection05Recovery02VisualProof01.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen GroundLightingCorrection04 Recovery01 proof executor changed")
    namespace = {"__name__": "ground_lighting_proof_executor_authority"}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    replacements = (
        (OLD_PREFIX, NEW_PREFIX),
        (OLD_ID, NEW_ID),
        (OLD_MAP, NEW_MAP),
        (OLD_CSV, NEW_CSV),
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
    exec(compile(transform_source(), str(SOURCE) + "::environment-composition-correction05-recovery02-proof01", "exec"), globals(), globals())
