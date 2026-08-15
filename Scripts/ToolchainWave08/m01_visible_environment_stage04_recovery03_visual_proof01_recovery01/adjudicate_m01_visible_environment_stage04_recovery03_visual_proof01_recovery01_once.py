"""Bind the frozen Stage04 adjudicator to the fresh Recovery01 namespace."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage04_recovery03_visual_proof01\adjudicate_m01_visible_environment_stage04_recovery03_visual_proof01_once.py"
)
EXPECTED_BYTES = 2_130
EXPECTED_SHA256 = "e6bca13fd9fa37f7599d186e1103d6609f45dd8ba5455f381105caf0c91968c7"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Stage04 adjudicator binder changed")
    namespace = {"__name__": "stage04_adjudicator_authority", "__file__": str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    replacements = (
        ("M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY03_VISUAL_PROOF01", "M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY03_VISUAL_PROOF01_RECOVERY01"),
        ("M01-VISIBLE-ENVIRONMENT-STAGE04-RECOVERY03-VISUAL-PROOF01", "M01-VISIBLE-ENVIRONMENT-STAGE04-RECOVERY03-VISUAL-PROOF01-RECOVERY01"),
        ("M01VisibleEnvironmentStage04Recovery03VisualProof01.csv", "M01VisibleEnvironmentStage04Recovery03VisualProof01Recovery01.csv"),
        ("m01_visible_environment_stage04_recovery03_visual_proof01", "m01_visible_environment_stage04_recovery03_visual_proof01_recovery01"),
        ("visible-environment-stage04-recovery03-visual-proof01", "visible-environment-stage04-recovery03-visual-proof01-recovery01"),
    )
    optional_tokens = {
        "m01_visible_environment_stage04_recovery03_visual_proof01",
        "visible-environment-stage04-recovery03-visual-proof01",
    }
    for old, new in replacements:
        if old not in transformed and old not in optional_tokens:
            raise RuntimeError(f"Recovery01 adjudicator token absent: {old}")
        if old in transformed:
            transformed = transformed.replace(old, new)
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::recovery01", "exec"), globals(), globals())
