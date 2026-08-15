"""Bind the proven Stage06 adjudicator directly to the fresh Recovery01 proof."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage06_district_correction01_visual_proof01\adjudicate_m01_visible_environment_stage06_district_correction01_visual_proof01_once.py")
EXPECTED_BYTES = 2_561
EXPECTED_SHA256 = "13143174ff2dcf974bb3402a15822dcd32a3b05c4a5e329b9045d87620707abf"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Stage06 adjudicator binder changed")
    namespace = {"__name__": "stage06_adjudicator_authority", "__file__": str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    replacements = (
        ("M01_VISIBLE_ENVIRONMENT_STAGE06_DISTRICT_CORRECTION01_VISUAL_PROOF01", "M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_VISUAL_PROOF01_RECOVERY01"),
        ("M01-VISIBLE-ENVIRONMENT-STAGE06-DISTRICT-CORRECTION01-VISUAL-PROOF01", "M01-VISIBLE-ENVIRONMENT-STAGE07A-HERO-CORRIDOR01-CORRECTION01-VISUAL-PROOF01-RECOVERY01"),
        ("M01VisibleEnvironmentStage06DistrictCorrection01VisualProof01.csv", "M01VisibleEnvironmentStage07AHeroCorridor01Correction01VisualProof01Recovery01.csv"),
        ("m01_visible_environment_stage06_district_correction01_visual_proof01", "m01_visible_environment_stage07a_hero_corridor01_correction01_visual_proof01_recovery01"),
        ("visible-environment-stage06-district-correction01-visual-proof01", "visible-environment-stage07a-hero-corridor01-correction01-visual-proof01-recovery01"),
        ("Lvl_M01_VisibleEnvironmentStage06DistrictCorrection01", "Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01Correction01"),
    )
    optional = {replacements[3][0], replacements[4][0], replacements[5][0]}
    for old, new in replacements:
        if old not in transformed and old not in optional:
            raise RuntimeError(f"Recovery01 adjudicator token absent: {old}")
        if old in transformed:
            transformed = transformed.replace(old, new)
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::stage07a-correction01-recovery01", "exec"), globals(), globals())
