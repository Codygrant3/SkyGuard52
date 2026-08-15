"""Bind the accepted mapped-proof executor to VisualRemediation01 Recovery01."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\environment_visible_kit_map_visual_proof01\capture_m01_visible_environment_kit_map_visual_proof01.py"
)
EXPECTED_BYTES = 2968
EXPECTED_SHA256 = "5b63324193897b52963e4efea839d64fee55f86bc6fe3b05a2000b9b5b1e4a7e"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen visible-kit mapped-proof executor changed")
    namespace = {"__name__": "m01_visible_kit_map_visual_proof01_authority"}
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
    )
    for old, new in replacements:
        if old not in transformed:
            raise RuntimeError(f"Mapped-proof executor binding token is absent: {old}")
        transformed = transformed.replace(old, new)
    for old, _ in replacements:
        if old == "M01_VISIBLE_ENVIRONMENT_KIT_MAP_":
            continue
        if old in transformed:
            raise RuntimeError(f"Mapped-proof executor retained stale token: {old}")
    for required in (
        "M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_RECOVERY01_",
        "VISUAL_PROOF01",
        "Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01_Recovery01",
        "M01VisibleEnvironmentKitMapVisualRemediation01Recovery01VisualProof01.csv",
        '"M01_VEK02_"',
    ):
        if required not in transformed:
            raise RuntimeError(f"Mapped-proof executor output binding is missing: {required}")
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::visual-remediation01-recovery01-proof01", "exec"), globals(), globals())
