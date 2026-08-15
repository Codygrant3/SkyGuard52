"""Blender 5.2 compatibility binding for the immutable window-bay source.

Recovery02 supplies the supported Eevee enum and the one missing orientation
helper proven by Recovery01.  It changes no geometry, materials, cameras,
dimensions, receipts or acceptance thresholds.
"""

from __future__ import annotations

import sys
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.Workers import worker_m01_hero_prewar_window_bay_a01 as implementation


ASSET_ID = "m01-hero-prewar-window-bay-a01-recovery02"
implementation.ASSET_ID = ASSET_ID
implementation.GATE = "M01_HERO_PREWAR_WINDOW_BAY_A01_RECOVERY02"
implementation.base.ASSET_ID = ASSET_ID


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def configure_scene_blender52(scene: bpy.types.Scene) -> None:
    implementation.base.configure_scene(scene)
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.color_mode = "RGBA"


implementation.base.look_at = look_at
implementation.configure_scene = configure_scene_blender52


if __name__ == "__main__":
    raise SystemExit(implementation.main())
