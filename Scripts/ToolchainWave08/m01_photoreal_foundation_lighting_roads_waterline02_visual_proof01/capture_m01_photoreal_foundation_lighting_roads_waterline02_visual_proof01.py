"""Bind the accepted eight-camera proof executor to LightingRoadsWaterline02."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_nonvegetation01_visual_proof01\capture_m01_photoreal_foundation_nonvegetation01_visual_proof01.py"
)
EXPECTED_BYTES = 2243
EXPECTED_SHA256 = "1fe0148e47bc37f3e17cd4e735ca0e5cdebc8997e1f0ed174d773f06d27cefc2"

OLD_PREFIX = "M01_PHOTOREAL_FOUNDATION_WAVE01_NONVEGETATION01_"
NEW_PREFIX = "M01_PHOTOREAL_FOUNDATION_WAVE01_LIGHTING_ROADS_WATERLINE02_"
OLD_ID = "M01-PHOTOREAL-FOUNDATION-WAVE01-NONVEGETATION01-VISUAL-PROOF01"
NEW_ID = "M01-PHOTOREAL-FOUNDATION-WAVE01-LIGHTING-ROADS-WATERLINE02-VISUAL-PROOF01"
OLD_MAP = "Lvl_M01_PhotorealFoundation_NonVegetation01"
NEW_MAP = "Lvl_M01_PhotorealFoundation_LightingRoadsWaterline02"
OLD_CSV = "M01PhotorealFoundationWave01NonVegetation01VisualProof01.csv"
NEW_CSV = "M01PhotorealFoundationWave01LightingRoadsWaterline02VisualProof01.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen NonVegetation01 proof executor changed")
    namespace = {"__name__": "nonvegetation01_proof_executor_authority"}
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
    exec(compile(transform_source(), str(SOURCE) + "::lighting-roads-waterline02-proof01", "exec"), globals(), globals())
