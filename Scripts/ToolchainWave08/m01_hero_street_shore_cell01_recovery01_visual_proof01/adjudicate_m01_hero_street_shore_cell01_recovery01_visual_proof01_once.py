"""Bind the proven automatic adjudicator to Hero Street/Shore Cell01 R01."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_accepted_candidate_assembly03_recovery01_visual_proof01\adjudicate_m01_accepted_candidate_assembly03_recovery01_visual_proof01_once.py"
)
EXPECTED_BYTES = 2_588
EXPECTED_SHA256 = "cf1f3f1f5ad37c22ad84acbf21f28023dcf192a0cfce5fdfac2ddfad2fd6e744"
OLD_PREFIX = "M01_ACCEPTED_CANDIDATE_ASSEMBLY03_RECOVERY01_VISUAL_PROOF01"
NEW_PREFIX = "M01_HERO_STREET_SHORE_CELL01_RECOVERY01_VISUAL_PROOF01"
OLD_ID = "M01-ACCEPTED-CANDIDATE-ASSEMBLY03-RECOVERY01-VISUAL-PROOF01"
NEW_ID = "M01-HERO-STREET-SHORE-CELL01-RECOVERY01-VISUAL-PROOF01"
OLD_MAP = "Lvl_M01_AcceptedCandidateAssembly03_Recovery01"
NEW_MAP = "Lvl_M01_HeroStreetShoreCell01_Recovery01"
OLD_CSV = "M01AcceptedCandidateAssembly03Recovery01VisualProof01.csv"
NEW_CSV = "M01HeroStreetShoreCell01Recovery01VisualProof01.csv"
OLD_SLUG = "m01_accepted_candidate_assembly03_recovery01_visual_proof01"
NEW_SLUG = "m01_hero_street_shore_cell01_recovery01_visual_proof01"
OLD_KEBAB = "accepted-candidate-assembly03-recovery01-visual-proof01"
NEW_KEBAB = "hero-street-shore-cell01-recovery01-visual-proof01"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Frozen Assembly03 adjudicator binder changed")
    namespace = {"__name__": "assembly03_adjudicator_binder_authority", "__file__": str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace, namespace)
    transformed = namespace["transform_source"]()
    for old, new in (
        (OLD_PREFIX, NEW_PREFIX), (OLD_ID, NEW_ID), (OLD_MAP, NEW_MAP),
        (OLD_CSV, NEW_CSV), (OLD_SLUG, NEW_SLUG), (OLD_KEBAB, NEW_KEBAB),
    ):
        if old not in transformed:
            raise RuntimeError(f"Cell adjudicator token absent: {old}")
        transformed = transformed.replace(old, new)
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::hero-cell-proof01", "exec"), globals(), globals())
