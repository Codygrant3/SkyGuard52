"""Bind the accepted automatic postflight adjudicator to the remediated map proof."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\environment_visible_kit_map_visual_proof01\adjudicate_m01_visible_environment_kit_map_visual_proof01_once.py"
)
EXPECTED_BYTES = 2628
EXPECTED_SHA256 = "c8a04d150c651e43c4f016f4e911b11491b6a1df542279640db7cf4f7ff3095f"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen visible-kit mapped-proof adjudicator changed")
    namespace = {"__name__": "m01_visible_kit_map_visual_proof01_adjudicator_authority"}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    replacements = (
        (
            "M01_VISIBLE_ENVIRONMENT_KIT_MAP_",
            "M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_RECOVERY01_",
        ),
        (
            "M01-VISIBLE-ENVIRONMENT-KIT-MAP-VISUAL-PROOF01",
            "M01-VISIBLE-ENVIRONMENT-KIT-MAP-VISUAL-REMEDIATION01-RECOVERY01-VISUAL-PROOF01",
        ),
        (
            "Lvl_M01_VisibleEnvironmentKit02_Recovery02",
            "Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01_Recovery01",
        ),
        (
            "M01VisibleEnvironmentKitMapVisualProof01.csv",
            "M01VisibleEnvironmentKitMapVisualRemediation01Recovery01VisualProof01.csv",
        ),
        (
            "m01_visible_environment_kit_map_visual_proof01",
            "m01_visible_environment_kit_map_visual_remediation01_recovery01_visual_proof01",
        ),
        (
            "visible-environment-kit-map-visual-proof01",
            "visible-environment-kit-map-visual-remediation01-recovery01-visual-proof01",
        ),
    )
    for old, new in replacements:
        if old not in transformed:
            raise RuntimeError(f"Mapped-proof adjudicator binding token is absent: {old}")
        transformed = transformed.replace(old, new)
    for old, _ in replacements:
        if old == "M01_VISIBLE_ENVIRONMENT_KIT_MAP_":
            continue
        if old in transformed:
            raise RuntimeError(f"Mapped-proof adjudicator retained stale token: {old}")
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::visual-remediation01-recovery01-proof01", "exec"), globals(), globals())
