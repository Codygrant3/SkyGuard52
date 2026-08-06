from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(r"D:\Skyguard52")
OUTPUT_DIR = ROOT / "Saved" / "Screenshots" / "BLD_M01_COAST_PROD_001"


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
    size: float = 12.0,
) -> bpy.types.Object:
    data = bpy.data.lights.new(name=name, type=kind)
    data.energy = energy
    data.color = color
    if kind == "AREA":
        data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    point_at(obj, (0.0, 0.0, 0.0))
    return obj


def set_visible(layout: dict[str, tuple[float, float, float]]) -> None:
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH" and not obj.name.startswith("REVIEW"):
            obj.hide_render = obj.name not in layout
            if obj.name in layout:
                local_center = sum(
                    (Vector(corner) for corner in obj.bound_box),
                    Vector(),
                ) / 8.0
                obj.location = Vector(layout[obj.name]) - local_center


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

    world = scene.world or bpy.data.worlds.new("CoastReviewWorld")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.03, 0.055, 0.08, 1.0)
    background.inputs["Strength"].default_value = 0.45

    add_light("REVIEW_Key", "AREA", (-30.0, -65.0, 95.0), 2600.0, (1.0, 0.88, 0.72), 45.0)
    add_light("REVIEW_Fill", "AREA", (80.0, 45.0, 55.0), 1800.0, (0.55, 0.72, 1.0), 35.0)
    sun = add_light("REVIEW_Sun", "SUN", (0.0, 0.0, 80.0), 2.0, (1.0, 0.94, 0.82))
    sun.rotation_euler = (math.radians(32.0), math.radians(-20.0), math.radians(28.0))

    camera_data = bpy.data.cameras.new("REVIEW_Camera")
    camera = bpy.data.objects.new("REVIEW_Camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera

    set_visible(
        {
            "GEO_COAST001_Terrain_BeachDune_A_100m": (-150.0, 0.0, 0.0),
            "GEO_COAST001_Terrain_BeachDune_B_100m": (-50.0, 0.0, 0.0),
            "GEO_COAST001_Terrain_DuneSeawall_100m": (50.0, 0.0, 0.0),
            "GEO_COAST001_Terrain_SeawallRoad_100m": (150.0, 0.0, 0.0),
        }
    )
    render(camera, "coastal_tiles_sequence.png", (0.0, -185.0, 145.0), (0.0, 0.0, -0.5), 58.0)

    set_visible(
        {
            "GEO_COAST001_MidriseShell_Straight_5F": (-30.0, 0.0, 8.1),
            "GEO_COAST001_MidriseShell_Straight_7F": (-10.0, 0.0, 11.1),
            "GEO_COAST001_MidriseShell_Corner_7F": (12.0, 2.5, 11.1),
            "GEO_COAST001_MidriseShell_End_7F": (34.0, 0.0, 11.1),
            "GEO_COAST001_Roof_Flat_18x12": (-10.0, 0.0, 22.75),
            "GEO_COAST001_Roof_ServiceScreen_6x4": (-10.0, 0.0, 24.5),
        }
    )
    render(camera, "midrise_shell_variants.png", (10.0, -88.0, 47.0), (2.0, 0.0, 10.0), 62.0)

    detail_names = [
        "GEO_COAST001_Seawall_CornerInner_10m",
        "GEO_COAST001_Road_JunctionT_20m",
        "GEO_COAST001_Curb_DropKerb_3m",
        "GEO_COAST001_Sidewalk_Ramp_3m",
        "GEO_COAST001_Drain_Channel_10m",
        "GEO_COAST001_Drain_Grate_1m",
        "GEO_COAST001_Drain_Inlet",
        "GEO_COAST001_Drain_Outfall",
        "GEO_COAST001_WindowBay_A",
        "GEO_COAST001_WindowBay_B",
        "GEO_COAST001_WindowBay_Double",
        "GEO_COAST001_BalconyBay_A",
        "GEO_COAST001_BalconyBay_B",
        "GEO_COAST001_Facade_CornerBay",
        "GEO_COAST001_Facade_EndWallBay",
        "GEO_COAST001_Roof_Parapet_10m",
    ]
    layout = {}
    for index, name in enumerate(detail_names):
        column = index % 4
        row = index // 4
        layout[name] = ((column - 1.5) * 22.0, (row - 1.5) * 18.0, 2.0)
    set_visible(layout)
    render(camera, "coastal_detail_modules.png", (0.0, -105.0, 85.0), (0.0, 0.0, 2.0), 65.0)


if __name__ == "__main__":
    main()
