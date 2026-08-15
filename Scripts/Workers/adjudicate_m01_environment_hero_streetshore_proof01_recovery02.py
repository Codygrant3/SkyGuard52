from __future__ import annotations

"""Recovery02 identity binding for the frozen street/shore postflight."""

import hashlib
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\Workers\adjudicate_m01_environment_hero_streetshore_proof01.py")
EXPECTED_SOURCE_SHA256 = "59cff240704a40b68a70c71b6002391b14e06a9296b7fecbaaeaaecb539c6cac"
ORIGINAL_ID = 'ASSET_ID = "m01-environment-hero-streetshore-proof01"'
RECOVERY_ID = 'ASSET_ID = "m01-environment-hero-streetshore-proof01-recovery02"'


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if not SOURCE.is_file() or sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
    raise RuntimeError("Frozen postflight authority mismatch")
text = SOURCE.read_text(encoding="utf-8")
if text.count(ORIGINAL_ID) != 1:
    raise RuntimeError("Frozen postflight asset identity was not found exactly once")
text = text.replace(ORIGINAL_ID, RECOVERY_ID, 1)
exec(compile(text, str(SOURCE) + "::Recovery02", "exec"), {"__name__": "__main__", "__file__": str(SOURCE)})
