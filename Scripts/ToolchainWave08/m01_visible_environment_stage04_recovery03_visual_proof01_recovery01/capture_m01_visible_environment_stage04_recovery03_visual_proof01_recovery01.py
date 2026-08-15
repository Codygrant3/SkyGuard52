"""Bind the frozen Stage04 proof to a fresh Recovery01 evidence namespace."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage04_recovery03_visual_proof01\capture_m01_visible_environment_stage04_recovery03_visual_proof01.py"
)
EXPECTED_BYTES = 13_279
EXPECTED_SHA256 = "1c1e8999594af4897f442692038333a4bd442520ad6a7f6ba68e2b23b29cea1e"
OLD_PREFIX = "M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY03_VISUAL_PROOF01"
NEW_PREFIX = "M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY03_VISUAL_PROOF01_RECOVERY01"
OLD_ID = "M01-VISIBLE-ENVIRONMENT-STAGE04-RECOVERY03-VISUAL-PROOF01"
NEW_ID = "M01-VISIBLE-ENVIRONMENT-STAGE04-RECOVERY03-VISUAL-PROOF01-RECOVERY01"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Stage04 proof binder changed")
    namespace = {"__name__": "stage04_proof_binder_authority", "__file__": str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    replacements = (
        (OLD_PREFIX, NEW_PREFIX),
        (OLD_ID, NEW_ID),
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
            raise RuntimeError(f"Recovery01 proof token absent: {old}")
        if old in transformed:
            transformed = transformed.replace(old, new)
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::recovery01", "exec"), globals(), globals())
