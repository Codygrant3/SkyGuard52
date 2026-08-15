"""Recovery01 binder: tolerate optional lowercase tokens while preserving the proof."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage07a_hero_corridor01_correction01_visual_proof01\capture_m01_visible_environment_stage07a_hero_corridor01_correction01_visual_proof01.py")
EXPECTED_BYTES = 4_872
EXPECTED_SHA256 = "e155ed161e5f43e16c22fc60ab7573843c61dfcb5cccea234e74ced6ce791683"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen failed-attempt capture binder changed")
    source = SOURCE.read_text(encoding="utf-8")
    old = '''    for old, new in replacements:
        if old not in transformed:
            raise RuntimeError(f"Correction01 capture token absent: {old}")
        transformed = transformed.replace(old, new)'''
    new = '''    optional = {
        "m01_visible_environment_stage07a_hero_corridor01_visual_proof01",
        "visible-environment-stage07a-hero-corridor01-visual-proof01",
    }
    for old, new in replacements:
        if old not in transformed and old not in optional:
            raise RuntimeError(f"Correction01 capture token absent: {old}")
        if old in transformed:
            transformed = transformed.replace(old, new)'''
    if source.count(old) != 1:
        raise RuntimeError("Recovery01 optional-token patch anchor changed")
    namespace = {"__name__": "correction01_recovery01_capture", "__file__": str(SOURCE)}
    exec(compile(source.replace(old, new, 1), str(SOURCE) + "::recovery01", "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    replacements = (
        ("M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_VISUAL_PROOF01", "M01_VISIBLE_ENVIRONMENT_STAGE07A_HERO_CORRIDOR01_CORRECTION01_VISUAL_PROOF01_RECOVERY01"),
        ("M01-VISIBLE-ENVIRONMENT-STAGE07A-HERO-CORRIDOR01-CORRECTION01-VISUAL-PROOF01", "M01-VISIBLE-ENVIRONMENT-STAGE07A-HERO-CORRIDOR01-CORRECTION01-VISUAL-PROOF01-RECOVERY01"),
        ("M01VisibleEnvironmentStage07AHeroCorridor01Correction01VisualProof01.csv", "M01VisibleEnvironmentStage07AHeroCorridor01Correction01VisualProof01Recovery01.csv"),
        ("m01_visible_environment_stage07a_hero_corridor01_correction01_visual_proof01", "m01_visible_environment_stage07a_hero_corridor01_correction01_visual_proof01_recovery01"),
        ("visible-environment-stage07a-hero-corridor01-correction01-visual-proof01", "visible-environment-stage07a-hero-corridor01-correction01-visual-proof01-recovery01"),
    )
    optional = {replacements[3][0], replacements[4][0]}
    for old, new in replacements:
        if old not in transformed and old not in optional:
            raise RuntimeError(f"Recovery01 token absent: {old}")
        if old in transformed:
            transformed = transformed.replace(old, new)
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::recovery01-final", "exec"), globals(), globals())
