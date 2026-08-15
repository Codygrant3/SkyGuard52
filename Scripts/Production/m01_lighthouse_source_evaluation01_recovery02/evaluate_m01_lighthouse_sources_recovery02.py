"""Blender 5.2 compatibility and review-axis wrapper for the frozen evaluator."""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

from mathutils import Matrix


FROZEN = Path(r"D:\Skyguard52\Scripts\Production\m01_lighthouse_source_evaluation01\evaluate_m01_lighthouse_sources.py")
spec = importlib.util.spec_from_file_location("skyguard_lighthouse_eval01_frozen", FROZEN)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load frozen evaluator: {FROZEN}")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def make_material_compat(name: str, color: tuple[float, float, float, float], metallic: float, roughness: float):
    material = module.bpy.data.materials.new(name)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    module.require(principled is not None, "Principled BSDF unavailable")
    metallic_socket = principled.inputs.get("Metallic")
    if metallic_socket is None:
        metallic_socket = principled.inputs.get("Metallic IOR Level")
    module.require(metallic_socket is not None, "Blender 5.2 metallic input unavailable")
    principled.inputs["Base Color"].default_value = color
    metallic_socket.default_value = metallic
    principled.inputs["Roughness"].default_value = roughness
    return material


def render_views_axis_normalized(source_id: str, objects: list, output: Path):
    minimum, maximum = module.world_bounds(objects)
    center = (minimum + maximum) * 0.5
    size = maximum - minimum
    longest = max(range(3), key=lambda index: float(size[index]))
    if longest == 0:
        rotation = Matrix.Rotation(math.radians(-90.0), 4, "Y")
    elif longest == 1:
        rotation = Matrix.Rotation(math.radians(90.0), 4, "X")
    else:
        rotation = Matrix.Identity(4)
    if longest != 2:
        transform = Matrix.Translation(center) @ rotation @ Matrix.Translation(-center)
        for obj in objects:
            obj.matrix_world = transform @ obj.matrix_world
        module.bpy.context.view_layer.update()
    return module.render_views_original(source_id, objects, output)


module.make_material = make_material_compat
module.render_views_original = module.render_views
module.render_views = render_views_axis_normalized

if __name__ == "__main__":
    raise SystemExit(module.main())
