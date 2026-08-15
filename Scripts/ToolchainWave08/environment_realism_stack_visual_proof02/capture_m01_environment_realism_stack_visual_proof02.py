"""Bind the accepted mapped-proof executor to the corrected RealismStack03 map."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\ToolchainWave08\environment_realism_stack_visual_proof01\capture_m01_environment_realism_stack_visual_proof01.py")
EXPECTED_BYTES = 4267
EXPECTED_SHA256 = "5576b29c28724d34f55009a6206dd6c50d9c831d3489dac189bcaace210576aa"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Visual Proof01 capture wrapper changed")
    namespace = {"__name__": "m01_visual_proof01_capture_authority"}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    replacements = (
        ("VISUAL_PROOF01", "VISUAL_PROOF02"),
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
            raise RuntimeError(f"Visual Proof02 transformation retained stale token: {stale}")
    for required in ("VISUAL_PROOF02", "M01-ENVIRONMENT-REALISM-STACK-VISUAL-PROOF02", "Lvl_M01_T08_EnvironmentRealismStack03", "M01EnvironmentRealismStackVisualProof02.csv"):
        if required not in transformed:
            raise RuntimeError(f"Visual Proof02 output binding is missing: {required}")
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::visual-proof02", "exec"), globals(), globals())
