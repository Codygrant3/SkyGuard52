from __future__ import annotations

"""Blender 5.2 compatibility binding for the frozen hero street/shore proof.

The immutable production worker is compiled in memory after exactly three
bounded substitutions: fresh asset identity, fresh gate identity, and the
installed Blender 5.2 Eevee enum. Geometry and visual behavior are otherwise
byte-derived from the frozen source.
"""

import hashlib
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\Workers\worker_m01_environment_hero_streetshore_proof01.py")
EXPECTED_SOURCE_SHA256 = "94a831f9c0c70c67741e2b1bb7448796f8da70cc875e84c8d5c925583f933866"
RECOVERY_ASSET_ID = "m01-environment-hero-streetshore-proof01-recovery01"
RECOVERY_GATE_ID = "M01_ENVIRONMENT_PRODUCTION_RESET01_HERO_STREETSHORE_PROOF01_RECOVERY01"
REPLACEMENTS = (
    (
        'ASSET_ID = "m01-environment-hero-streetshore-proof01"',
        f'ASSET_ID = "{RECOVERY_ASSET_ID}"',
        "asset identity",
    ),
    (
        'GATE = "M01_ENVIRONMENT_PRODUCTION_RESET01_HERO_STREETSHORE_PROOF01"',
        f'GATE = "{RECOVERY_GATE_ID}"',
        "gate identity",
    ),
    (
        'scene.render.engine = "BLENDER_EEVEE_NEXT"',
        'scene.render.engine = "BLENDER_EEVEE"',
        "Blender 5.2 Eevee enum",
    ),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if not SOURCE.is_file():
    raise RuntimeError(f"Missing immutable source worker: {SOURCE}")
if sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
    raise RuntimeError("Immutable source worker hash mismatch")

recovery_text = SOURCE.read_text(encoding="utf-8")
for old_value, new_value, label in REPLACEMENTS:
    if recovery_text.count(old_value) != 1:
        raise RuntimeError(f"Immutable source {label} was not found exactly once")
    recovery_text = recovery_text.replace(old_value, new_value, 1)

compiled = compile(recovery_text, str(SOURCE) + "::Recovery01", "exec")
exec(compiled, {"__name__": "__main__", "__file__": str(SOURCE)})
