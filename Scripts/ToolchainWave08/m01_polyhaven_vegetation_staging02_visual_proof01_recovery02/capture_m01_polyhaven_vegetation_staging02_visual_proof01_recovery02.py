"""Bind the frozen Stage02 proof executor to fresh Recovery02 evidence paths."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\ToolchainWave08\m01_polyhaven_vegetation_staging02_visual_proof01\capture_m01_polyhaven_vegetation_staging02_visual_proof01.py")
EXPECTED_BYTES = 6_895
EXPECTED_SHA256 = "0b2f184a3937bf87c56127957bd36101ae633e3ab3f252beb916291bd6851f96"
REPLACEMENTS = (
    ("M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01", "M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY02"),
    ("M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01", "M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01-RECOVERY02"),
    ("M01PolyHavenVegetationStaging02VisualProof01.csv", "M01PolyHavenVegetationStaging02VisualProof01Recovery02.csv"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Stage02 executor binder changed")
    namespace = {"__name__": "stage02_executor_binder_authority", "__file__": str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    for old, new in REPLACEMENTS:
        if old not in transformed:
            raise RuntimeError(f"Recovery02 executor token absent: {old}")
        transformed = transformed.replace(old, new)
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::stage02-proof01-recovery02", "exec"), globals(), globals())
