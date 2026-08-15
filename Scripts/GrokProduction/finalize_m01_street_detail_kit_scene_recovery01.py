"""Finalizer-only Recovery01 for the immutable street-detail checkpoint scene."""

from __future__ import annotations

import hashlib
from pathlib import Path


BASE = Path(r"D:\Skyguard52\Scripts\GrokProduction\finalize_m01_street_detail_kit_scene.py")
BASE_BYTES = 15934
BASE_SHA256 = "d69ed70bdc34ca2ef478355972559f763b61f086be5aba8febcc72efc982fe4f"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if not BASE.is_file() or BASE.stat().st_size != BASE_BYTES or sha256(BASE) != BASE_SHA256:
    raise RuntimeError("Frozen Attempt01 finalizer is missing or changed")

source = BASE.read_text(encoding="utf-8")
replacements = {
    r'D:\Skyguard52\Production\Attempts\m01-street-detail-kit-grok-mcp\attempt_20260811T070000000000Z\output':
        r'D:\Skyguard52\Production\Attempts\m01-street-detail-kit-finalizer-recovery01\attempt_20260811T071500000000Z\output',
    'scene.render.engine = "BLENDER_EEVEE_NEXT"':
        'scene.render.engine = "BLENDER_EEVEE"',
}

for old, new in replacements.items():
    if source.count(old) != 1:
        raise RuntimeError(f"Frozen finalizer binding changed: {old}")
    source = source.replace(old, new)

compile(source, str(BASE), "exec")
exec(source, globals(), globals())

