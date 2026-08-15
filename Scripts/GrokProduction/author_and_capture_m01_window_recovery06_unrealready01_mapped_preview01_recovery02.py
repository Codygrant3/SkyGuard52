"""Recovery02 mapped-preview executor with UE 5.8 component access."""

from __future__ import annotations

import hashlib
from pathlib import Path


BASE = Path(r"D:\Skyguard52\Scripts\GrokProduction\author_and_capture_m01_window_recovery06_unrealready01_mapped_preview01.py")
BASE_SHA256 = "bf114b348475ff29bee80c7ec7c15e1c0d73a567422a38690639cb9df25ea893"
PRIOR_FREEZE = Path(r"D:\Skyguard52\Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if not BASE.is_file() or sha256(BASE) != BASE_SHA256:
    raise RuntimeError("Frozen mapped-preview base executor changed")
if not PRIOR_FREEZE.is_file():
    raise RuntimeError("Mapped-preview Recovery01 failure freeze is absent")

source = BASE.read_text(encoding="utf-8")
source = source.replace(
    'MAP_ASSET = "/Game/T08/GW02Preview/Lvl_GW02_WindowPreview01"',
    'MAP_ASSET = "/Game/T08/GW02PreviewR02/Lvl_GW02_WindowPreview01_Recovery02"',
)
source = source.replace(
    'MAP_FILE = ISOLATED / r"Content\\T08\\GW02Preview\\Lvl_GW02_WindowPreview01.umap"',
    'MAP_FILE = ISOLATED / r"Content\\T08\\GW02PreviewR02\\Lvl_GW02_WindowPreview01_Recovery02.umap"',
)
source = source.replace(
    'ATTEMPT = ROOT / r"Saved\\BuildAttempts\\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01\\attempt_01"',
    'ATTEMPT = ROOT / r"Saved\\BuildAttempts\\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY02\\attempt_01"',
)

old_handshake = '''    if ATTEMPT.exists() and any(ATTEMPT.iterdir()):\n        raise RuntimeError("Fresh mapped-preview attempt is not empty")'''
new_handshake = '''    allowed_launcher_files = {"unreal.stdout.log", "unreal.stderr.log", "unreal.engine.log", "process_tree_samples.jsonl"}\n    unexpected_launcher_files = []\n    if ATTEMPT.exists():\n        unexpected_launcher_files = sorted(path.name for path in ATTEMPT.iterdir() if path.name not in allowed_launcher_files)\n    if unexpected_launcher_files:\n        raise RuntimeError(f"Fresh Recovery02 attempt contains unexpected launcher files: {unexpected_launcher_files}")\n    if RECEIPT.exists() or PROOF.exists():\n        raise RuntimeError("Fresh Recovery02 executor output namespace already exists")'''
if source.count(old_handshake) != 1:
    raise RuntimeError("Frozen executor handshake marker changed")
source = source.replace(old_handshake, new_handshake)

component_helper = '''\n\ndef require_actor_component(actor: object, component_class: object) -> object:\n    component = actor.get_component_by_class(component_class)\n    if component is None:\n        raise RuntimeError(f\"Actor {actor.get_actor_label()} lacks component {component_class}\")\n    return component\n'''
component_marker = "\n\ndef spawn_mesh(unreal: object, mesh: object, label: str,"
if source.count(component_marker) != 1:
    raise RuntimeError("Frozen executor component-helper marker changed")
source = source.replace(component_marker, component_helper + component_marker)

source = source.replace(
    '    sun.set_actor_label("GW02_KeySun")\n    sun.directional_light_component.set_intensity(8.0)\n    sun.directional_light_component.set_mobility(unreal.ComponentMobility.MOVABLE)',
    '    sun.set_actor_label("GW02_KeySun")\n    sun_component = require_actor_component(sun, unreal.DirectionalLightComponent)\n    sun_component.set_intensity(8.0)\n    sun_component.set_mobility(unreal.ComponentMobility.MOVABLE)',
)
source = source.replace(
    '    fill.set_actor_label("GW02_FillSun")\n    fill.directional_light_component.set_intensity(2.5)\n    fill.directional_light_component.set_mobility(unreal.ComponentMobility.MOVABLE)',
    '    fill.set_actor_label("GW02_FillSun")\n    fill_component = require_actor_component(fill, unreal.DirectionalLightComponent)\n    fill_component.set_intensity(2.5)\n    fill_component.set_mobility(unreal.ComponentMobility.MOVABLE)',
)
source = source.replace(
    '    sky.set_actor_label("GW02_Sky")\n    sky.light_component.set_intensity(1.2)\n    sky.light_component.set_editor_property("real_time_capture", True)\n    sky.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)',
    '    sky.set_actor_label("GW02_Sky")\n    sky_component = require_actor_component(sky, unreal.SkyLightComponent)\n    sky_component.set_intensity(1.2)\n    sky_component.set_editor_property("real_time_capture", True)\n    sky_component.set_mobility(unreal.ComponentMobility.MOVABLE)',
)
source = source.replace(
    '        light.set_actor_label(f"GW02_Point_{index:02d}")\n        light.point_light_component.set_intensity(intensity)\n        light.point_light_component.set_editor_property("attenuation_radius", radius)\n        light.point_light_component.set_mobility(unreal.ComponentMobility.MOVABLE)',
    '        light.set_actor_label(f"GW02_Point_{index:02d}")\n        point_component = require_actor_component(light, unreal.PointLightComponent)\n        point_component.set_intensity(intensity)\n        point_component.set_editor_property("attenuation_radius", radius)\n        point_component.set_mobility(unreal.ComponentMobility.MOVABLE)',
)
source = source.replace("mapped-preview01.v1", "mapped-preview01-recovery02.v1")
source = source.replace("PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW", "PASSED_RECOVERY02_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW")

for forbidden in ("sun.directional_light_component", "fill.directional_light_component", "sky.light_component", "light.point_light_component"):
    if forbidden in source:
        raise RuntimeError(f"Recovery02 retains unsupported actor attribute: {forbidden}")
if source.count("require_actor_component(") != 5:
    raise RuntimeError("Recovery02 component access count changed")

compiled = compile(source, str(Path(__file__)), "exec")
exec(compiled, globals(), globals())
