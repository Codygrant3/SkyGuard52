"""Bind the proven automatic D3D12 adjudicator to Stage04 Recovery03."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage03_visual_proof01\adjudicate_m01_visible_environment_stage03_visual_proof01_once.py"
)
EXPECTED_BYTES = 2_057
EXPECTED_SHA256 = "98abf8d22fdece1d004208391c15962e1e64530ea8abda53d891ae95e27fd09b"
REPLACEMENTS = (
    ("M01_VISIBLE_ENVIRONMENT_STAGE03_VISUAL_PROOF01", "M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY03_VISUAL_PROOF01"),
    ("M01-VISIBLE-ENVIRONMENT-STAGE03-VISUAL-PROOF01", "M01-VISIBLE-ENVIRONMENT-STAGE04-RECOVERY03-VISUAL-PROOF01"),
    ("Lvl_M01_VisibleEnvironmentStage03", "Lvl_M01_VisibleEnvironmentStage04Recovery03"),
    ("M01VisibleEnvironmentStage03VisualProof01.csv", "M01VisibleEnvironmentStage04Recovery03VisualProof01.csv"),
    ("m01_visible_environment_stage03_visual_proof01", "m01_visible_environment_stage04_recovery03_visual_proof01"),
    ("visible-environment-stage03-visual-proof01", "visible-environment-stage04-recovery03-visual-proof01"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if (
        not SOURCE.is_file()
        or SOURCE.stat().st_size != EXPECTED_BYTES
        or sha256(SOURCE) != EXPECTED_SHA256
    ):
        raise RuntimeError("Frozen Stage03 adjudicator binder changed")
    namespace = {"__name__": "stage03_adjudicator_authority", "__file__": str(SOURCE)}
    exec(
        compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"),
        namespace,
        namespace,
    )
    transformed = namespace["transform_source"]()
    for old, new in REPLACEMENTS:
        if old not in transformed:
            raise RuntimeError(f"Stage04 Recovery03 adjudicator token absent: {old}")
        transformed = transformed.replace(old, new)
    return transformed


if __name__ == "__main__":
    exec(
        compile(transform_source(), str(SOURCE) + "::stage04-recovery03-visual-proof01", "exec"),
        globals(),
        globals(),
    )
