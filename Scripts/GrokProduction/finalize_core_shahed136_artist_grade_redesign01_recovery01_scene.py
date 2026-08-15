from __future__ import annotations

import hashlib
from pathlib import Path


BASE = Path(r"D:\Skyguard52\Scripts\GrokProduction\finalize_core_shahed136_artist_grade_redesign01_scene.py")
EXPECTED_BYTES = 19777
EXPECTED_SHA256 = "9833e4c02ab07cf09eccd14c4ea887ac82497d446b4d18abdb9a62e4bffb3fd4"

OLD_OUTPUT = r'D:\Skyguard52\Production\Attempts\core-shahed136-grok-mcp-redesign01\attempt_20260811T0830000000000Z\output'
NEW_OUTPUT = r'D:\Skyguard52\Production\Attempts\core-shahed136-grok-mcp-redesign01-recovery01\attempt_20260811T0845000000000Z\output'
OLD_BLEND = 'CORE_Shahed136_ArtistGrade_Redesign01.blend'
NEW_BLEND = 'CORE_Shahed136_ArtistGrade_Redesign01_Recovery01.blend'
OLD_GLB = 'CORE_Shahed136_ArtistGrade_Redesign01.glb'
NEW_GLB = 'CORE_Shahed136_ArtistGrade_Redesign01_Recovery01.glb'
OLD_SCHEMA = 'skyguard.core-shahed136.grok-mcp.artist-grade-redesign01.report.v1'
NEW_SCHEMA = 'skyguard.core-shahed136.grok-mcp.artist-grade-redesign01-recovery01.report.v1'


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if not BASE.is_file() or BASE.stat().st_size != EXPECTED_BYTES or sha256(BASE) != EXPECTED_SHA256:
    raise RuntimeError("Frozen Shahed Redesign01 finalizer authority mismatch")

source = BASE.read_text(encoding="utf-8")
replacements = (
    (OLD_OUTPUT, NEW_OUTPUT),
    (OLD_BLEND, NEW_BLEND),
    (OLD_GLB, NEW_GLB),
    (OLD_SCHEMA, NEW_SCHEMA),
)
for old, new in replacements:
    if source.count(old) != 1:
        raise RuntimeError(f"Expected one frozen finalizer token: {old}")
    source = source.replace(old, new, 1)

exec(compile(source, str(BASE) + "::Recovery01", "exec"), {"__file__": str(BASE), "__name__": "__main__"})
