from __future__ import annotations

"""Blender 5.2 compatibility binding for Coastal Vegetation01 Recovery01."""

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_photoreal_foundation_wave01"
    r"\worker_m01_coastal_vegetation01.py"
)
EXPECTED_SOURCE_BYTES = 26824
EXPECTED_SOURCE_SHA256 = "dd623a698979b6740f4e9ecbd08caab0d43f8552102253e753d774899b923b60"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if not SOURCE.is_file():
    raise RuntimeError(f"Missing immutable source: {SOURCE}")
if SOURCE.stat().st_size != EXPECTED_SOURCE_BYTES or sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
    raise RuntimeError("Immutable Coastal Vegetation01 worker authority changed")

source = SOURCE.read_text(encoding="utf-8")
if source.count('scene.render.engine = "BLENDER_EEVEE_NEXT"') != 1:
    raise RuntimeError("Expected exactly one Blender 5.2-incompatible Eevee token")
source = source.replace(
    'scene.render.engine = "BLENDER_EEVEE_NEXT"',
    'scene.render.engine = "BLENDER_EEVEE"',
    1,
)
if "BLENDER_EEVEE_NEXT" in source:
    raise RuntimeError("Recovery01 retains an incompatible Eevee token")

exec(compile(source, str(SOURCE) + "::Recovery01", "exec"), {"__name__": "__main__", "__file__": str(SOURCE)})
