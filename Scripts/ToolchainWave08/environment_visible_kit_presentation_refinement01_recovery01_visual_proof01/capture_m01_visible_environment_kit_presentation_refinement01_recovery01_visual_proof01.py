"""Bind the accepted mapped-proof executor to PresentationRefinement01 Recovery01."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\environment_visible_kit_map_visual_remediation01_recovery01_visual_proof01\capture_m01_visible_environment_kit_map_visual_remediation01_recovery01_visual_proof01.py"
)
EXPECTED_BYTES = 2705
EXPECTED_SHA256 = "4c9caa4a501bbddff0465455506b9f7d6824870844579b9188789da47ff6a5ed"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen remediated-map proof executor changed")
    namespace = {"__name__": "m01_visible_environment_remediated_proof_executor_authority"}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    replacements = (
        (
            "M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_RECOVERY01_",
            "M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_RECOVERY01_",
        ),
        (
            "M01-VISIBLE-ENVIRONMENT-KIT-MAP-VISUAL-REMEDIATION01-RECOVERY01-VISUAL-PROOF01",
            "M01-VISIBLE-ENVIRONMENT-PRESENTATION-REFINEMENT01-RECOVERY01-VISUAL-PROOF01",
        ),
        (
            "Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01_Recovery01",
            "Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01_Recovery01",
        ),
        (
            "M01VisibleEnvironmentKitMapVisualRemediation01Recovery01VisualProof01.csv",
            "M01VisibleEnvironmentPresentationRefinement01Recovery01VisualProof01.csv",
        ),
    )
    for old, new in replacements:
        if old not in transformed:
            raise RuntimeError(f"Presentation-proof executor binding token is absent: {old}")
        transformed = transformed.replace(old, new)
    for old, _ in replacements:
        if old in transformed:
            raise RuntimeError(f"Presentation-proof executor retained stale token: {old}")
    return transformed


if __name__ == "__main__":
    exec(
        compile(
            transform_source(),
            str(SOURCE) + "::presentation-refinement01-recovery01-proof01",
            "exec",
        ),
        globals(),
        globals(),
    )
