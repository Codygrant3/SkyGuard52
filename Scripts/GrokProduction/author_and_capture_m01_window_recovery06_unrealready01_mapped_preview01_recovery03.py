"""Recovery03 mapped preview with a local deterministic look-at rotator."""

from __future__ import annotations

import hashlib
from pathlib import Path


BASE = Path(r"D:\Skyguard52\Scripts\GrokProduction\author_and_capture_m01_window_recovery06_unrealready01_mapped_preview01_recovery02.py")
BASE_SHA256 = "73d0bfcc45f287c27e0f79f04c3f92fe69be1384bbfec80fe6f8faf7cae0e943"
PRIOR_FREEZE = Path(r"D:\Skyguard52\Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY02_ATTEMPT01_TERMINAL_FREEZE.json")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if not BASE.is_file() or sha256(BASE) != BASE_SHA256:
    raise RuntimeError("Frozen mapped-preview Recovery02 executor changed")
if not PRIOR_FREEZE.is_file():
    raise RuntimeError("Mapped-preview Recovery02 failure freeze is absent")

wrapper = BASE.read_text(encoding="utf-8")
wrapper = wrapper.replace("RECOVERY02", "RECOVERY03").replace("Recovery02", "Recovery03").replace("recovery02", "recovery03")
wrapper = wrapper.replace("GW02PreviewR02", "GW02PreviewR03")
wrapper = wrapper.replace(
    r'M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json',
    r'M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY02_ATTEMPT01_TERMINAL_FREEZE.json',
)

look_at_patch = '''\n+source = source.replace("import hashlib\\nimport json", "import hashlib\\nimport json\\nimport math")\n+old_look_at = "def look_at(unreal: object, location: tuple[float, float, float], target: tuple[float, float, float]) -> object:\\n    return unreal.KismetMathLibrary.find_look_at_rotation(unreal.Vector(*location), unreal.Vector(*target))"\n+new_look_at = "def look_at(unreal: object, location: tuple[float, float, float], target: tuple[float, float, float]) -> object:\\n    dx = target[0] - location[0]\\n    dy = target[1] - location[1]\\n    dz = target[2] - location[2]\\n    horizontal = math.sqrt(dx * dx + dy * dy)\\n    yaw = math.degrees(math.atan2(dy, dx))\\n    pitch = math.degrees(math.atan2(dz, horizontal))\\n    return unreal.Rotator(pitch=pitch, yaw=yaw, roll=0.0)"\n+if source.count(old_look_at) != 1:\n+    raise RuntimeError("Recovery03 look-at marker changed")\n+source = source.replace(old_look_at, new_look_at)\n+'''
marker = '\nfor forbidden in ("sun.directional_light_component", "fill.directional_light_component", "sky.light_component", "light.point_light_component"):'
if wrapper.count(marker) != 1:
    raise RuntimeError("Recovery02 wrapper insertion marker changed")
wrapper = wrapper.replace(marker, look_at_patch + marker)
wrapper = wrapper.replace(
    'if source.count("require_actor_component(") != 5:',
    'if "KismetMathLibrary" in source:\n    raise RuntimeError("Recovery03 retains unavailable KismetMathLibrary")\nif source.count("require_actor_component(") != 5:',
)

for required in ("GW02PreviewR03", "RECOVERY03", "new_look_at"):
    if required not in wrapper:
        raise RuntimeError(f"Recovery03 wrapper correction missing: {required}")

compiled = compile(wrapper, str(Path(__file__)), "exec")
exec(compiled, globals(), globals())
