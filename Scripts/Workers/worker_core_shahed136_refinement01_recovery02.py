from __future__ import annotations

"""Blender 5.2 compatibility binding for the frozen Shahed refinement worker."""

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

LEGACY_LIGHT_ENERGY = (
    "    key.energy, fill.energy, rim.energy, world.color = settings[profile]\n"
)
BLENDER52_LIGHT_ENERGY = (
    "    key.data.energy, fill.data.energy, rim.data.energy, world.color = settings[profile]\n"
)


class CompatibilityError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_patched_source() -> str:
    if not ORIGINAL.is_file():
        raise CompatibilityError(f"Missing frozen Refinement01 worker: {ORIGINAL}")
    if ORIGINAL.stat().st_size != EXPECTED_BYTES or sha256(ORIGINAL) != EXPECTED_SHA256:
        raise CompatibilityError("Frozen Refinement01 worker authority mismatch.")
    source = ORIGINAL.read_text(encoding="utf-8")
    if source.count(LEGACY_ACTION_BLOCK) != 1:
        raise CompatibilityError("Expected one legacy Action.fcurves block.")
    if source.count(LEGACY_LIGHT_ENERGY) != 1:
        raise CompatibilityError("Expected one legacy object-level light-energy assignment.")
    patched = source.replace(LEGACY_ACTION_BLOCK, BLENDER52_ACTION_BLOCK, 1)
    patched = patched.replace(LEGACY_LIGHT_ENERGY, BLENDER52_LIGHT_ENERGY, 1)
    if "rig.animation_data.action.fcurves" in patched:
        raise CompatibilityError("Direct Action.fcurves access remains.")
    if LEGACY_LIGHT_ENERGY in patched:
        raise CompatibilityError("Object-level light-energy assignment remains.")
    if patched.count(BLENDER52_LIGHT_ENERGY) != 1:
        raise CompatibilityError("Blender 5.2 light-data correction is not unique.")
    ast.parse(patched, filename=str(ORIGINAL) + "::Recovery02")
    return patched


def load_patched_namespace() -> dict[str, Any]:
    patched = build_patched_source()
    namespace: dict[str, Any] = {
        "__file__": str(ORIGINAL),
        "__name__": "skyguard_shahed136_refinement01_recovery02",
        "__package__": None,
    }
    exec(compile(patched, str(ORIGINAL) + "::Recovery02", "exec"), namespace)
    return namespace


def main() -> int:
    namespace = load_patched_namespace()
    entrypoint = namespace.get("main")
    if not callable(entrypoint):
        raise CompatibilityError("Patched worker exposes no callable main entrypoint.")
    return int(entrypoint())


if __name__ == "__main__":
    raise SystemExit(main())
