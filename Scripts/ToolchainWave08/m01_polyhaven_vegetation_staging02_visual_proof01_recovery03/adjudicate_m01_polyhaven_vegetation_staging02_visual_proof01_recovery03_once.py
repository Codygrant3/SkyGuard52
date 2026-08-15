"""Bind the frozen Stage02 adjudicator to fresh Recovery03 evidence paths."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\ToolchainWave08\m01_polyhaven_vegetation_staging02_visual_proof01\adjudicate_m01_polyhaven_vegetation_staging02_visual_proof01_once.py")
EXPECTED_BYTES = 2_041
EXPECTED_SHA256 = "7437136494396f93c956bd7a2d729ba5470fc87dfebf767a0f64024c07593c33"
REPLACEMENTS = (
    ("M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01", "M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY03"),
    ("M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01", "M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01-RECOVERY03"),
    ("M01PolyHavenVegetationStaging02VisualProof01.csv", "M01PolyHavenVegetationStaging02VisualProof01Recovery03.csv"),
    ("m01_polyhaven_vegetation_staging02_visual_proof01", "m01_polyhaven_vegetation_staging02_visual_proof01_recovery03"),
    ("polyhaven-vegetation-staging02-visual-proof01", "polyhaven-vegetation-staging02-visual-proof01-recovery03"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Stage02 adjudicator binder changed")
    namespace = {"__name__": "stage02_adjudicator_binder_authority", "__file__": str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    for old, new in REPLACEMENTS:
        if old not in transformed:
            raise RuntimeError(f"Recovery03 adjudicator token absent: {old}")
        transformed = transformed.replace(old, new)
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::stage02-proof01-recovery03", "exec"), globals(), globals())
