"""Recovery01 compatibility wrapper for the frozen lighthouse production builder.

The only functional correction is luminance sampling from the already-written
PNG, because Blender 5.2 background mode may not retain Render Result pixels.
All authored geometry, materials, cameras, output validation, and export rules
remain inherited from the frozen original builder.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import bpy


FROZEN_BUILDER = Path(
    r"D:\Skyguard52\Scripts\Production\m01_lighthouse_production_refinement01\build_m01_lighthouse_production_refinement01.py"
)


def load_frozen_builder():
    specification = importlib.util.spec_from_file_location("skyguard_m01_lighthouse_refinement01_frozen", FROZEN_BUILDER)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"Unable to load frozen builder: {FROZEN_BUILDER}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def png_mean_luminance(path: Path) -> float:
    if not path.is_file():
        raise RuntimeError(f"Rendered PNG missing before luminance sampling: {path}")
    image = bpy.data.images.load(str(path), check_existing=False)
    try:
        if not image.has_data:
            raise RuntimeError(f"Rendered PNG has no pixel data: {path}")
        pixels = image.pixels[:]
        count = len(pixels) // 4
        if count <= 0:
            raise RuntimeError(f"Rendered PNG contains no pixels: {path}")
        stride = max(count // 16384, 1)
        total = 0.0
        samples = 0
        for index in range(0, count, stride):
            r, g, b = pixels[index * 4 : index * 4 + 3]
            total += 0.2126 * r + 0.7152 * g + 0.0722 * b
            samples += 1
        return total / samples
    finally:
        bpy.data.images.remove(image)


def main() -> int:
    frozen = load_frozen_builder()

    def render_view(output: Path, filename: str, location, target, lens: float, mode: str, materials):
        frozen.stage(mode, materials)
        scene = bpy.context.scene
        scene.camera = frozen.review_camera(location, target, lens)
        path = output / filename
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        luminance = png_mean_luminance(path)
        if luminance < 0.08:
            scene.view_settings.exposure += 1.25
            bpy.ops.render.render(write_still=True)
            luminance = png_mean_luminance(path)
        elif luminance > 0.72:
            scene.view_settings.exposure -= 0.85
            bpy.ops.render.render(write_still=True)
            luminance = png_mean_luminance(path)
        frozen.require(path.is_file(), f"Render missing: {path}")
        width, height = frozen.png_dimensions(path)
        frozen.require((width, height) == (2048, 1152), f"Wrong render dimensions: {path} {width}x{height}")
        return {
            **frozen.record(path),
            "mode": mode,
            "mean_luminance": luminance,
            "width": width,
            "height": height,
            "luminance_source": "saved_png",
        }

    frozen.render_view = render_view
    return int(frozen.main())


if __name__ == "__main__":
    raise SystemExit(main())
