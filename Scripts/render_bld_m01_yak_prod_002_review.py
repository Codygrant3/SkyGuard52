from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(r"D:\Skyguard52")
OUTPUT_DIR = ROOT / "Saved" / "Screenshots" / "BLD_M01_YAK_PROD_002"


def point_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (
        Vector(target) - obj.location
    ).to_track_quat("-Z", "Y").to_euler()


def add_light(
    name: str,
    kind: str,
    location: tuple[float, float, float],
    energy: float,
    color: tuple[float, float, float],
    size: float = 5.0,
) -> bpy.types.Object:
    data = bpy.data.lights.new(name=name, type=kind)
    data.energy = energy
    data.color = color
    if kind == "AREA":
        data.shape = "DISK"
        data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    point_at(obj, (0.0, 0.0, 0.7))
    return obj


def render(
    camera: bpy.types.Object,
    filename: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    lens: float,
) -> None:
    camera.location = location
    camera.data.lens = lens
    point_at(camera, target)
    bpy.context.scene.render.filepath = str(OUTPUT_DIR / filename)
    bpy.ops.render.render(write_still=True)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.look = "AgX - Medium High Contrast"

    world = scene.world or bpy.data.worlds.new("ReviewWorld002")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.025, 0.045, 0.075, 1.0)
    background.inputs["Strength"].default_value = 0.45

    bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0.0, 0.0, -0.62))
    ground = bpy.context.object
    ground.name = "REVIEW002_Ground"
    ground_mat = bpy.data.materials.new("REVIEW002_GroundMat")
    ground_mat.diffuse_color = (0.10, 0.12, 0.14, 1.0)
    ground.data.materials.append(ground_mat)

    add_light("REVIEW002_Key", "AREA", (6.0, -8.0, 10.0), 1750.0, (1.0, 0.88, 0.72), 6.0)
    add_light("REVIEW002_Fill", "AREA", (-5.0, 7.0, 6.0), 1250.0, (0.52, 0.70, 1.0), 5.0)
    add_light("REVIEW002_Rim", "AREA", (-6.0, -5.0, 7.0), 1450.0, (0.72, 0.84, 1.0), 4.0)
    sun = add_light("REVIEW002_Sun", "SUN", (0.0, 0.0, 8.0), 2.2, (1.0, 0.94, 0.82))
    sun.rotation_euler = (math.radians(28.0), math.radians(-18.0), math.radians(35.0))

    camera_data = bpy.data.cameras.new("REVIEW002_Camera")
    camera = bpy.data.objects.new("REVIEW002_Camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera

    render(camera, "yak52_three_quarter.png", (10.5, -12.5, 7.0), (0.45, 0.0, 0.55), 56.0)
    render(camera, "yak52_side.png", (0.5, -15.5, 2.6), (0.5, 0.0, 0.55), 62.0)
    render(camera, "yak52_top.png", (0.2, -0.2, 16.5), (0.2, 0.0, 0.25), 58.0)
    render(camera, "yak52_underside.png", (8.0, -11.0, -6.5), (0.35, 0.0, 0.0), 58.0)
    render(camera, "yak52_rear_cockpit_oblique.png", (-2.35, -3.25, 2.75), (-0.72, 0.0, 1.03), 60.0)
    render(camera, "yak52_rear_gunner_eye.png", (-0.88, 0.0, 1.52), (1.15, 0.0, 1.08), 62.0)


if __name__ == "__main__":
    main()
