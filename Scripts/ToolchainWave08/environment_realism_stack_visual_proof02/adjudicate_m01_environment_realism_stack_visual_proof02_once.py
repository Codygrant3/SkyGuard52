"""Bind the accepted mapped-proof adjudicator to RealismStack03 Visual Proof02."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\ToolchainWave08\environment_realism_stack_visual_proof01\adjudicate_m01_environment_realism_stack_visual_proof01_once.py")
EXPECTED_BYTES = 2650
EXPECTED_SHA256 = "e34800b161f0c1c7bca16e0139af1eb914549cbe01539fad8a7c1b7548c1294b"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Visual Proof01 adjudicator wrapper changed")
    namespace = {"__name__": "m01_visual_proof01_adjudicator_authority"}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    replacements = (
        ("M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF01", "M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF02"),
        ("M01-ENVIRONMENT-REALISM-STACK-VISUAL-PROOF01", "M01-ENVIRONMENT-REALISM-STACK-VISUAL-PROOF02"),
        ("Lvl_M01_T08_EnvironmentRealismStack01_Recovery02", "Lvl_M01_T08_EnvironmentRealismStack03"),
        ("M01EnvironmentRealismStackVisualProof01.csv", "M01EnvironmentRealismStackVisualProof02.csv"),
        ("m01_environment_realism_stack_visual_proof01", "m01_environment_realism_stack_visual_proof02"),
        ("visual-proof01", "visual-proof02"),
    )
    for old, new in replacements:
        if old in transformed:
            transformed = transformed.replace(old, new)
    for stale, _ in replacements:
        if stale in transformed:
            raise RuntimeError(f"Visual Proof02 adjudicator retained stale token: {stale}")
    for required in ("M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF02", "M01-ENVIRONMENT-REALISM-STACK-VISUAL-PROOF02", "Lvl_M01_T08_EnvironmentRealismStack03", "M01EnvironmentRealismStackVisualProof02.csv"):
        if required not in transformed:
            raise RuntimeError(f"Visual Proof02 adjudicator output binding is missing: {required}")
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::visual-proof02", "exec"), globals(), globals())
