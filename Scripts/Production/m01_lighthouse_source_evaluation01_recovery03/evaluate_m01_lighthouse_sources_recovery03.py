"""Blender 5.2 compatibility wrapper for the frozen read-only lighthouse evaluator.

This wrapper changes only temporary review-scene setup. Project-owned source files
are opened read-only, evaluated, and then hash-checked by the frozen evaluator.
"""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

from mathutils import Matrix, Vector


FROZEN = Path(
    r"D:\Skyguard52\Scripts\Production\m01_lighthouse_source_evaluation01"
    r"\evaluate_m01_lighthouse_sources.py"
)
spec = importlib.util.spec_from_file_location("skyguard_lighthouse_eval01_frozen_r03", FROZEN)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load frozen evaluator: {FROZEN}")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def make_material_compat(
    name: str,
    color: tuple[float, float, float, float],
    metallic: float,
    roughness: float,
):
    material = module.bpy.data.materials.new(name)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    module.require(principled is not None, "Principled BSDF unavailable")
    metallic_socket = principled.inputs.get("Metallic")
    if metallic_socket is None:
        metallic_socket = principled.inputs.get("Metallic IOR Level")
    module.require(metallic_socket is not None, "Supported metallic input unavailable")
    base_color_socket = principled.inputs.get("Base Color")
    roughness_socket = principled.inputs.get("Roughness")
    module.require(base_color_socket is not None, "Base Color input unavailable")
    module.require(roughness_socket is not None, "Roughness input unavailable")
    base_color_socket.default_value = color
    metallic_socket.default_value = metallic
    roughness_socket.default_value = roughness
    return material


def set_first_supported(target: object, attribute: str, candidates: tuple[str, ...]) -> str:
    failures: list[str] = []
    for candidate in candidates:
        try:
            setattr(target, attribute, candidate)
            return candidate
        except (TypeError, ValueError) as exc:
            failures.append(f"{candidate}: {exc}")
    raise RuntimeError(
        f"No supported value for {type(target).__name__}.{attribute}; "
        + " | ".join(failures)
    )


def prepare_review_scene_compat(objects: list, minimum: Vector, maximum: Vector):
    for obj in module.bpy.context.scene.objects:
        obj.hide_render = obj not in objects
    module.replace_with_clay(objects)
    center = (minimum + maximum) * 0.5
    size = maximum - minimum
    ground_material = module.make_material(
        "__EVAL_GROUND", (0.11, 0.12, 0.13, 1.0), 0.0, 0.82
    )
    module.bpy.ops.mesh.primitive_plane_add(
        size=max(size.x, size.y, 1.0) * 4.0,
        location=(center.x, center.y, minimum.z - 0.015),
    )
    ground = module.bpy.context.object
    ground.name = "__EVAL_GROUND"
    ground.data.materials.append(ground_material)

    camera_data = module.bpy.data.cameras.new("__EVAL_CAMERA")
    camera_data.type = "ORTHO"
    camera_data.lens = 55.0
    camera = module.bpy.data.objects.new("__EVAL_CAMERA", camera_data)
    module.bpy.context.scene.collection.objects.link(camera)
    module.bpy.context.scene.camera = camera

    span = max(size.x, size.y, size.z, 1.0)
    module.add_area(
        "__EVAL_KEY",
        center + Vector((-span * 0.9, -span * 1.1, span * 1.25)),
        1450.0,
        span * 0.85,
        center,
    )
    module.add_area(
        "__EVAL_FILL",
        center + Vector((span * 1.0, -span * 0.4, span * 0.55)),
        850.0,
        span * 0.7,
        center,
    )

    world = module.bpy.context.scene.world or module.bpy.data.worlds.new("__EVAL_WORLD")
    module.bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    module.require(background is not None, "World Background node unavailable")
    background.inputs["Color"].default_value = (0.045, 0.055, 0.075, 1.0)
    background.inputs["Strength"].default_value = 0.42

    scene = module.bpy.context.scene
    set_first_supported(
        scene.render,
        "engine",
        ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH"),
    )
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    set_first_supported(
        scene.view_settings,
        "look",
        (
            "AgX - Medium High Contrast",
            "AgX - Medium High Contrast Punchy",
            "Medium High Contrast",
            "None",
        ),
    )
    camera.data.ortho_scale = max(
        size.z * 1.22,
        max(size.x, size.y) * 1.22 / (1600.0 / 900.0),
        2.0,
    )
    return camera


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
module.prepare_review_scene = prepare_review_scene_compat
module.render_views_original = module.render_views
module.render_views = render_views_axis_normalized


if __name__ == "__main__":
    raise SystemExit(module.main())
