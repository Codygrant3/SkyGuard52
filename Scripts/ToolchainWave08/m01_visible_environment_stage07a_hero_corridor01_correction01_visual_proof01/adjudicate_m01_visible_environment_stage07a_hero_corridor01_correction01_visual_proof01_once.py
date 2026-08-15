"""Bind the proven automatic adjudicator to the Stage07A Correction01 proof."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage07a_hero_corridor01_visual_proof01\adjudicate_m01_visible_environment_stage07a_hero_corridor01_visual_proof01_once.py")
EXPECTED_BYTES = 2_498
EXPECTED_SHA256 = "9823cc4267d3a8f188947997d774b26cbe1e418beb556317366549f511c1016e"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Stage07A adjudicator binder changed")
    namespace = {"__name__": "stage07a_adjudicator_authority", "__file__": str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    replacements = (
        ("M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_VISUAL_PROOF01", "M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_VISUAL_PROOF01"),
        ("M01-VISIBLE-ENVIRONMENT-STAGE07A-HERO-CORRIDOR01-VISUAL-PROOF01", "M01-VISIBLE-ENVIRONMENT-STAGE07A-HERO-CORRIDOR01-CORRECTION01-VISUAL-PROOF01"),
        ("M01VisibleEnvironmentStage07AHeroCorridor01VisualProof01.csv", "M01VisibleEnvironmentStage07AHeroCorridor01Correction01VisualProof01.csv"),
        ("m01_visible_environment_stage07a_hero_corridor01_visual_proof01", "m01_visible_environment_stage07a_hero_corridor01_correction01_visual_proof01"),
        ("visible-environment-stage07a-hero-corridor01-visual-proof01", "visible-environment-stage07a-hero-corridor01-correction01-visual-proof01"),
        ("Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01", "Lvl_M01_VisibleEnvironmentStage07AHeroCorridor01Correction01"),
    )
    for old, new in replacements:
        if old not in transformed:
            raise RuntimeError(f"Correction01 adjudicator token absent: {old}")
        transformed = transformed.replace(old, new)
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::stage07a-correction01", "exec"), globals(), globals())
