"""Blender 5.2 compatibility binding for the immutable failed A01 bay source.

The original source remains frozen.  This fresh namespace changes only the
Eevee engine enum from the obsolete BLENDER_EEVEE_NEXT token to Blender 5.2's
supported BLENDER_EEVEE token, then executes the original geometry contract.
"""

from __future__ import annotations

import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.Workers import worker_m01_hero_prewar_window_bay_a01 as implementation


ASSET_ID = "m01-hero-prewar-window-bay-a01-recovery01"
implementation.ASSET_ID = ASSET_ID
implementation.GATE = "M01_HERO_PREWAR_WINDOW_BAY_A01_RECOVERY01"
implementation.base.ASSET_ID = ASSET_ID


def configure_scene_blender52(scene: bpy.types.Scene) -> None:
    implementation.base.configure_scene(scene)
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.color_mode = "RGBA"


implementation.configure_scene = configure_scene_blender52


if __name__ == "__main__":
    raise SystemExit(implementation.main())
