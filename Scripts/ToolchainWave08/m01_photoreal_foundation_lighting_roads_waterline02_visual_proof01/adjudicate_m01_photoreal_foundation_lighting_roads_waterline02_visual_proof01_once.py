"""Bind the accepted automatic adjudicator to LightingRoadsWaterline02."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_nonvegetation01_visual_proof01\adjudicate_m01_photoreal_foundation_nonvegetation01_visual_proof01_once.py"
)
EXPECTED_BYTES = 2643
EXPECTED_SHA256 = "e5b6823f2619028e314b2bca551ffd90c5ee5748761239e631397b24240a00ac"

OLD_PREFIX = "M01_PHOTOREAL_FOUNDATION_WAVE01_NONVEGETATION01_"
NEW_PREFIX = "M01_PHOTOREAL_FOUNDATION_WAVE01_LIGHTING_ROADS_WATERLINE02_"
OLD_ID = "M01-PHOTOREAL-FOUNDATION-WAVE01-NONVEGETATION01-VISUAL-PROOF01"
NEW_ID = "M01-PHOTOREAL-FOUNDATION-WAVE01-LIGHTING-ROADS-WATERLINE02-VISUAL-PROOF01"
OLD_MAP = "Lvl_M01_PhotorealFoundation_NonVegetation01"
NEW_MAP = "Lvl_M01_PhotorealFoundation_LightingRoadsWaterline02"
OLD_CSV = "M01PhotorealFoundationWave01NonVegetation01VisualProof01.csv"
NEW_CSV = "M01PhotorealFoundationWave01LightingRoadsWaterline02VisualProof01.csv"
OLD_SLUG = "m01_photoreal_foundation_wave01_nonvegetation01_visual_proof01"
NEW_SLUG = "m01_photoreal_foundation_wave01_lighting_roads_waterline02_visual_proof01"
OLD_KEBAB = "photoreal-foundation-wave01-nonvegetation01-visual-proof01"
NEW_KEBAB = "photoreal-foundation-wave01-lighting-roads-waterline02-visual-proof01"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen NonVegetation01 proof adjudicator changed")
    namespace = {"__name__": "nonvegetation01_proof_adjudicator_authority"}
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
    exec(compile(transform_source(), str(SOURCE) + "::lighting-roads-waterline02-proof01", "exec"), globals(), globals())
