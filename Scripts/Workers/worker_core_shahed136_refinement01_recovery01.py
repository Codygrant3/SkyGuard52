from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Any


ORIGINAL = Path(__file__).with_name("worker_core_shahed136_refinement01.py")
EXPECTED_BYTES = 31801
EXPECTED_SHA256 = "7a845f941788c47cb2baab863bc17ce6606f626d7257170eb802f1f4a40c283b"

LEGACY_ACTION_BLOCK = '''    if rig.animation_data and rig.animation_data.action:
        rig.animation_data.action.name = "ANIM_PropellerPreview_1s"
        for curve in rig.animation_data.action.fcurves:
            for point in curve.keyframe_points:
                point.interpolation = "LINEAR"
'''

BLENDER52_ACTION_BLOCK = '''    if rig.animation_data and rig.animation_data.action:
        rig.animation_data.action.name = "ANIM_PropellerPreview_1s"
'''


class CompatibilityError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_patched_namespace() -> dict[str, Any]:
    if not ORIGINAL.is_file():
        raise CompatibilityError(f"Missing frozen Refinement01 worker: {ORIGINAL}")
    if ORIGINAL.stat().st_size != EXPECTED_BYTES or sha256(ORIGINAL) != EXPECTED_SHA256:
        raise CompatibilityError("Frozen Refinement01 worker authority mismatch.")
    source = ORIGINAL.read_text(encoding="utf-8")
    if source.count(LEGACY_ACTION_BLOCK) != 1:
        raise CompatibilityError("Expected exactly one Blender pre-5.x direct Action.fcurves block.")
    patched = source.replace(LEGACY_ACTION_BLOCK, BLENDER52_ACTION_BLOCK, 1)
    if "rig.animation_data.action.fcurves" in patched:
        raise CompatibilityError("Direct Action.fcurves access remains after compatibility binding.")
    ast.parse(patched, filename=str(ORIGINAL) + "::Recovery01")
    namespace: dict[str, Any] = {
        "__file__": str(ORIGINAL),
        "__name__": "skyguard_shahed136_refinement01_recovery01",
        "__package__": None,
    }
    exec(compile(patched, str(ORIGINAL) + "::Recovery01", "exec"), namespace)
    return namespace


def main() -> int:
    namespace = load_patched_namespace()
    entrypoint = namespace.get("main")
    if not callable(entrypoint):
        raise CompatibilityError("Patched worker exposes no callable main entrypoint.")
    return int(entrypoint())


if __name__ == "__main__":
    raise SystemExit(main())
