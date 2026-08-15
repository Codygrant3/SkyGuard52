"""Bind the proven automatic postflight adjudicator to the Stage06 proof."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage05_composition01_recovery01_visual_proof01\adjudicate_m01_visible_environment_stage05_composition01_recovery01_visual_proof01_once.py"
)
EXPECTED_BYTES = 2_532
EXPECTED_SHA256 = "981559191a2613a391cc644e3f0b3af13a9ada288119c9b8ffd81d67de69d2c1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Stage05 adjudicator binder changed")
    namespace = {"__name__": "stage05_adjudicator_authority", "__file__": str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    replacements = (
        ("M01_VISIBLE_ENVIRONMENT_STAGE05_COMPOSITION01_RECOVERY01_VISUAL_PROOF01", "M01_VISIBLE_ENVIRONMENT_STAGE06_DISTRICT_CORRECTION01_VISUAL_PROOF01"),
        ("M01-VISIBLE-ENVIRONMENT-STAGE05-COMPOSITION01-RECOVERY01-VISUAL-PROOF01", "M01-VISIBLE-ENVIRONMENT-STAGE06-DISTRICT-CORRECTION01-VISUAL-PROOF01"),
        ("M01VisibleEnvironmentStage05Composition01Recovery01VisualProof01.csv", "M01VisibleEnvironmentStage06DistrictCorrection01VisualProof01.csv"),
        ("m01_visible_environment_stage05_composition01_recovery01_visual_proof01", "m01_visible_environment_stage06_district_correction01_visual_proof01"),
        ("visible-environment-stage05-composition01-recovery01-visual-proof01", "visible-environment-stage06-district-correction01-visual-proof01"),
        ("Lvl_M01_VisibleEnvironmentStage05Composition01Recovery01", "Lvl_M01_VisibleEnvironmentStage06DistrictCorrection01"),
    )
    optional = {
        "m01_visible_environment_stage05_composition01_recovery01_visual_proof01",
        "visible-environment-stage05-composition01-recovery01-visual-proof01",
    }
    for old, new in replacements:
        if old not in transformed and old not in optional:
            raise RuntimeError(f"Stage06 adjudicator token absent: {old}")
        if old in transformed:
            transformed = transformed.replace(old, new)
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::stage06-district-correction01", "exec"), globals(), globals())
