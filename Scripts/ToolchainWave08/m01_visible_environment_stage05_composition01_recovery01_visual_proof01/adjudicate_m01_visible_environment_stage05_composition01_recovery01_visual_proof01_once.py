"""Bind the proven automatic postflight adjudicator to the Stage05 proof."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage04_recovery03_visual_proof01_recovery01\adjudicate_m01_visible_environment_stage04_recovery03_visual_proof01_recovery01_once.py"
)
EXPECTED_BYTES = 2_307
EXPECTED_SHA256 = "a8386224b07ce81d412a96dfa57a37e9c39eca881e92043fbe897790bec49341"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Stage04 Recovery01 adjudicator binder changed")
    namespace = {"__name__": "stage04_recovery01_adjudicator_authority", "__file__": str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    optional = {
        "m01_visible_environment_stage04_recovery03_visual_proof01_recovery01",
        "visible-environment-stage04-recovery03-visual-proof01-recovery01",
    }
    for old, new in (
        ("M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY03_VISUAL_PROOF01_RECOVERY01", "M01_VISIBLE_ENVIRONMENT_STAGE05_COMPOSITION01_RECOVERY01_VISUAL_PROOF01"),
        ("M01-VISIBLE-ENVIRONMENT-STAGE04-RECOVERY03-VISUAL-PROOF01-RECOVERY01", "M01-VISIBLE-ENVIRONMENT-STAGE05-COMPOSITION01-RECOVERY01-VISUAL-PROOF01"),
        ("M01VisibleEnvironmentStage04Recovery03VisualProof01Recovery01.csv", "M01VisibleEnvironmentStage05Composition01Recovery01VisualProof01.csv"),
        ("m01_visible_environment_stage04_recovery03_visual_proof01_recovery01", "m01_visible_environment_stage05_composition01_recovery01_visual_proof01"),
        ("visible-environment-stage04-recovery03-visual-proof01-recovery01", "visible-environment-stage05-composition01-recovery01-visual-proof01"),
        ("Lvl_M01_VisibleEnvironmentStage04Recovery03", "Lvl_M01_VisibleEnvironmentStage05Composition01Recovery01"),
    ):
        if old not in transformed and old not in optional:
            raise RuntimeError(f"Stage05 adjudicator token absent: {old}")
        if old in transformed:
            transformed = transformed.replace(old, new)
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::stage05-composition01-recovery01", "exec"), globals(), globals())
