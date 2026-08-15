"""Recovery01 compatibility binding for the frozen Attempt01 finalizer.

The Blender 5.2 installation exposes Eevee as ``BLENDER_EEVEE``.  This wrapper
changes only that installed-version token and the fresh governed output root.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


BASE = Path(r"D:\Skyguard52\Scripts\GrokProduction\finalize_m01_promenade_prop_kit_scene.py")
BASE_BYTES = 15395
BASE_SHA256 = "2abc1290fb7501f272f770f9385843b369b2481654e05137dd125055bb642d42"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if not BASE.is_file() or BASE.stat().st_size != BASE_BYTES or sha256(BASE) != BASE_SHA256:
    raise RuntimeError("Frozen Attempt01 finalizer is missing or changed")

source = BASE.read_text(encoding="utf-8")
old_root = r"D:\Skyguard52\Production\Attempts\m01-promenade-prop-kit-grok-mcp\attempt_20260811T061500000000Z\output"
new_root = r"D:\Skyguard52\Production\Attempts\m01-promenade-prop-kit-grok-mcp-recovery01\attempt_20260811T063000000000Z\output"

if source.count(old_root) != 1:
    raise RuntimeError("Frozen Attempt01 output-root binding changed")
if source.count('scene.render.engine = "BLENDER_EEVEE_NEXT"') != 1:
    raise RuntimeError("Frozen Attempt01 Eevee token binding changed")

source = source.replace(old_root, new_root)
source = source.replace('scene.render.engine = "BLENDER_EEVEE_NEXT"', 'scene.render.engine = "BLENDER_EEVEE"')

compile(source, str(BASE), "exec")
exec(source, globals(), globals())
