"""Bind the proven automatic adjudicator to Stage02 vegetation."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_hero_street_shore_cell03_recovery01_visual_proof01\adjudicate_m01_hero_street_shore_cell03_recovery01_visual_proof01_once.py"
)
EXPECTED_BYTES = 2_177
EXPECTED_SHA256 = "3f086e34f527838e808fafbf145b874182a9e7065a32bc1e7233f83a38759318"
REPLACEMENTS = (
    ("M01_HERO_STREET_SHORE_CELL03_RECOVERY01_VISUAL_PROOF01", "M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01"),
    ("M01-HERO-STREET-SHORE-CELL03-RECOVERY01-VISUAL-PROOF01", "M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01"),
    ("Lvl_M01_HeroStreetShoreCell03Recovery01", "Lvl_M01_PolyHavenVegetationStaging02"),
    ("M01HeroStreetShoreCell03Recovery01VisualProof01.csv", "M01PolyHavenVegetationStaging02VisualProof01.csv"),
    ("m01_hero_street_shore_cell03_recovery01_visual_proof01", "m01_polyhaven_vegetation_staging02_visual_proof01"),
    ("hero-street-shore-cell03-recovery01-visual-proof01", "polyhaven-vegetation-staging02-visual-proof01"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Cell03 adjudicator binder changed")
    namespace = {"__name__": "cell03_adjudicator_binder_authority", "__file__": str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    for old, new in REPLACEMENTS:
        if old not in transformed:
            raise RuntimeError(f"Stage02 adjudicator token absent: {old}")
        transformed = transformed.replace(old, new)
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::polyhaven-vegetation-stage02-proof01", "exec"), globals(), globals())
