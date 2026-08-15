"""Bind the proven D3D12 mapped-proof executor to VisibleEnvironmentKit02."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\ToolchainWave08\environment_realism_stack_visual_proof02\capture_m01_environment_realism_stack_visual_proof02.py")
EXPECTED_BYTES = 2225
EXPECTED_SHA256 = "cd1826d42b2631349109eb39e0f9407830d09c21054aacc7c93f02993b0b13b7"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Visual Proof02 capture wrapper changed")
    namespace = {"__name__": "m01_visual_proof02_capture_authority"}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    replacements = (
        ("M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF02", "M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_PROOF01"),
        ("M01_ENVIRONMENT_REALISM_STACK_", "M01_VISIBLE_ENVIRONMENT_KIT_MAP_"),
        ("VISUAL_PROOF02", "VISUAL_PROOF01"),
        ("M01-ENVIRONMENT-REALISM-STACK-VISUAL-PROOF02", "M01-VISIBLE-ENVIRONMENT-KIT-MAP-VISUAL-PROOF01"),
        ("Lvl_M01_T08_EnvironmentRealismStack03", "Lvl_M01_VisibleEnvironmentKit02_Recovery02"),
        ("Content/ToolchainWave08/Environment/", "Content/M01/"),
        ("/Game/ToolchainWave08/Environment/", "/Game/M01/"),
        ("M01EnvironmentRealismStackVisualProof02.csv", "M01VisibleEnvironmentKitMapVisualProof01.csv"),
        ("m01_environment_realism_stack_visual_proof02", "m01_visible_environment_kit_map_visual_proof01"),
        ("visual-proof02", "visible-environment-kit-map-visual-proof01"),
        ('("M01_A01_", "M01_RS01_")', '("M01_A01_", "M01_RS01_", "M01_VEK02_")'),
    )
    for old, new in replacements:
        if old in transformed:
            transformed = transformed.replace(old, new)
    for stale, _ in replacements[:-1]:
        if stale in transformed:
            raise RuntimeError(f"Visible-kit proof retained stale token: {stale}")
    required = (
        "M01_VISIBLE_ENVIRONMENT_KIT_MAP_",
        "VISUAL_PROOF01",
        "M01-VISIBLE-ENVIRONMENT-KIT-MAP-VISUAL-PROOF01",
        "Lvl_M01_VisibleEnvironmentKit02_Recovery02",
        "Content/M01/",
        "M01VisibleEnvironmentKitMapVisualProof01.csv",
        '"M01_VEK02_"',
    )
    for token in required:
        if token not in transformed:
            raise RuntimeError(f"Visible-kit proof output binding is missing: {token}")
    if transformed.count('("M01_A01_", "M01_RS01_", "M01_VEK02_")') < 2:
        raise RuntimeError("Visible-kit actors are not covered by restoration governance")
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::visible-kit-map-proof01", "exec"), globals(), globals())
